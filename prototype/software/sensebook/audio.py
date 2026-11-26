"""WAV helpers, player/recorder backends, offline TTS fallback and output routing."""
from __future__ import annotations

import io
import math
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import wave

import numpy as np


# ------------------------------------------------------------------ WAV helpers
def pcm_to_wav(pcm: np.ndarray, rate: int) -> bytes:
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(np.asarray(pcm, dtype="<i2").tobytes())
    return b.getvalue()


def wav_to_pcm(wav: bytes) -> tuple[np.ndarray, int]:
    with wave.open(io.BytesIO(wav), "rb") as w:
        ch, rate = w.getnchannels(), w.getframerate()
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
        if ch > 1:
            pcm = pcm.reshape(-1, ch).mean(axis=1).astype("<i2")
    return pcm, rate


def tone_wav(freq: float, seconds: float, rate: int = 16000, volume: float = 0.25) -> bytes:
    n = int(rate * seconds)
    t = np.arange(n) / rate
    env = np.minimum(1, np.minimum(t, seconds - t) * 40)          # short fade in/out, no clicks
    return pcm_to_wav((np.sin(2 * math.pi * freq * t) * env * volume * 32767).astype("<i2"), rate)


def page_turn_wav(rate: int = 16000) -> bytes:
    """Soft 'page-turn' earcon: short filtered-noise swish plus a quiet falling note (not a chime: not AI speech)."""
    n = int(rate * 0.22)
    t = np.arange(n) / rate
    env = np.sin(np.pi * t / t[-1]) ** 2
    noise = np.random.default_rng(7).normal(0, 1, n)
    noise = np.convolve(noise, np.ones(8) / 8, mode="same")
    note = np.sin(2 * math.pi * (520 - 180 * t / t[-1]) * t)
    return pcm_to_wav(((0.5 * noise + 0.5 * note) * env * 0.18 * 32767).astype("<i2"), rate)


def silence_wav(seconds: float, rate: int = 16000) -> bytes:
    return pcm_to_wav(np.zeros(int(rate * seconds), "<i2"), rate)


def chime_wav(rate: int = 16000) -> bytes:
    """Two rising notes: the 'AI is about to explain' cue, never used for faithful reading."""
    a, _ = wav_to_pcm(tone_wav(660, 0.12, rate))
    b, _ = wav_to_pcm(tone_wav(880, 0.18, rate))
    return pcm_to_wav(np.concatenate([a, np.zeros(int(rate * .03), "<i2"), b]), rate)


def wav_seconds(wav: bytes) -> float:
    pcm, rate = wav_to_pcm(wav)
    return len(pcm) / rate


# ------------------------------------------------------------------ playback
class Player:
    """Chunked, pausable, stoppable playback. `backend.write(pcm_chunk, rate)` blocks for the chunk's duration.

    play() blocks until finished/stopped and returns True if it played to the end.
    """

    def __init__(self, backend=None, volume: float = 0.8):
        self.backend = backend or NullBackend()
        self.volume = volume
        self._paused = threading.Event()
        self._stop = threading.Event()
        self.playing = False
        self.muted = False          # private mode: speaker muted
        self.duck = 1.0             # <1.0 while a hand is in frame (speech ducked, not cut)
        self.on_start = None        # one-shot callback fired right before the first audio chunk is written
        self.pre_play = None        # called before every play() (wakes the amp)
        self.last_active = 0.0      # monotonic time of the last chunk written (amp idle timer)
        self._fade_until = None

    def pause(self):
        self._paused.set()

    def resume(self):
        self._paused.clear()

    def toggle(self):
        self.resume() if self._paused.is_set() else self.pause()

    @property
    def paused(self):
        return self._paused.is_set()

    def stop(self):
        self._stop.set()
        self._paused.clear()

    def stop_soft(self, seconds: float = 0.25):
        """Fade out and stop (approximates 'stop at the end of the current word': TTS gives no word timings)."""
        self._fade_until = (time.monotonic(), seconds)

    def play(self, wav: bytes) -> bool:
        pcm, rate = wav_to_pcm(wav)
        if self.pre_play:
            self.pre_play()
        self._stop.clear()
        self._fade_until = None
        self.playing = True
        step = max(1, rate // 20)
        try:
            i = 0
            while i < len(pcm):
                if self._stop.is_set():
                    return False
                if self._paused.is_set():
                    time.sleep(0.02)
                    continue
                chunk = pcm[i:i + step]
                gain = self.volume * self.duck
                if self._fade_until:
                    t0, dur = self._fade_until
                    gain *= max(0.0, 1.0 - (time.monotonic() - t0) / dur)
                    if gain <= 0.0:
                        return False
                if self.muted:
                    gain = 0.0
                cb, self.on_start = self.on_start, None
                if cb:
                    cb()
                self.backend.write((chunk * gain).astype("<i2"), rate)
                self.last_active = time.monotonic()
                i += step
            return True
        finally:
            self.playing = False


class NullBackend:
    """Records what would have been played; does not sleep (fast tests)."""

    def __init__(self, realtime=False):
        self.realtime, self.samples, self.rate = realtime, 0, None

    def write(self, pcm, rate):
        self.samples += len(pcm)
        self.rate = rate
        if self.realtime:
            time.sleep(len(pcm) / rate)


class SoundDeviceBackend:
    def __init__(self, device=None):
        import sounddevice as sd
        self.sd, self.device, self.stream, self.rate = sd, device, None, None

    def write(self, pcm, rate):
        if self.stream is None or rate != self.rate:
            if self.stream:
                self.stream.close()
            self.stream = self.sd.OutputStream(samplerate=rate, channels=1, dtype="int16", device=self.device)
            self.stream.start()
            self.rate = rate
        self.stream.write(pcm.reshape(-1, 1))


class AplayBackend:
    """Pi: pipe raw PCM to aplay (ALSA) or pw-play/paplay. Device chosen by AudioRouter."""

    def __init__(self, device="default", runner=None):
        self.device, self.proc, self.rate = device, None, None

    def write(self, pcm, rate):
        if self.proc is None or rate != self.rate:
            self.close()
            self.proc = subprocess.Popen(["aplay", "-q", "-t", "raw", "-f", "S16_LE", "-r", str(rate), "-c", "1",
                                          "-D", self.device], stdin=subprocess.PIPE)
            self.rate = rate
        self.proc.stdin.write(pcm.tobytes())
        self.proc.stdin.flush()

    def close(self):
        if self.proc:
            try:
                self.proc.stdin.close()
                self.proc.wait(timeout=2)
            except Exception:
                self.proc.kill()
            self.proc = None


# ------------------------------------------------------------------ recording
class Recorder:
    """start() begins capturing; stop() returns WAV bytes (or None if nothing was captured)."""

    def start(self): ...
    def stop(self) -> bytes | None: ...


class SoundDeviceRecorder(Recorder):
    def __init__(self, rate=16000, max_seconds=30, device=None):
        import sounddevice as sd
        self.sd, self.rate, self.max, self.device = sd, rate, max_seconds, device
        self.frames: list[np.ndarray] = []
        self.stream = None

    def start(self):
        self.frames = []
        self.stream = self.sd.InputStream(samplerate=self.rate, channels=1, dtype="int16", device=self.device,
                                          callback=lambda d, f, t, s: self.frames.append(d.copy()))
        self.stream.start()

    def stop(self):
        if not self.stream:
            return None
        self.stream.stop()
        self.stream.close()
        self.stream = None
        if not self.frames:
            return None
        pcm = np.concatenate(self.frames).reshape(-1)[: self.rate * self.max]
        return pcm_to_wav(pcm, self.rate)


class ArecordRecorder(Recorder):
    def __init__(self, device="plughw:wm8960soundcard", rate=16000, max_seconds=30):
        self.device, self.rate, self.max, self.proc = device, rate, max_seconds, None
        self.path = None

    def start(self):
        self.path = tempfile.mktemp(suffix=".wav")
        self.proc = subprocess.Popen(["arecord", "-q", "-D", self.device, "-f", "S16_LE", "-r", str(self.rate),
                                      "-c", "1", "-d", str(self.max), self.path])

    def stop(self):
        if not self.proc:
            return None
        self.proc.terminate()
        self.proc.wait()
        self.proc = None
        try:
            with open(self.path, "rb") as f:
                return f.read()
        except OSError:
            return None
        finally:
            import os
            try:
                os.unlink(self.path)
            except OSError:
                pass


class ScriptedRecorder(Recorder):
    """Tests / mock-provider dev mode: each stop() yields the next queued utterance as a (silent) clip
    carrying a transcript that only the Mock provider reads."""

    def __init__(self):
        self.queue: list[str] = []
        self.active = False
        self.last_transcript: str | None = None

    def say(self, text: str):
        self.queue.append(text)

    def start(self):
        self.active = True

    def stop(self):
        self.active = False
        if not self.queue:
            return None
        self.last_transcript = self.queue.pop(0)
        return silence_wav(0.2)


# ------------------------------------------------------------------ offline TTS
class OfflineSpeech:
    """Cloud-less fallback voice. espeak-ng on the Pi (has `bn`), pyttsx3 on laptops."""
    sample_rate = 22050

    def available(self) -> bool:
        return bool(shutil.which("espeak-ng")) or _has_pyttsx3()

    def synthesize(self, text: str, lang: str = "en", speed: float = 1.0) -> bytes | None:
        path = tempfile.mktemp(suffix=".wav")
        try:
            if shutil.which("espeak-ng"):
                subprocess.run(["espeak-ng", "-v", "bn" if lang == "bn" else "en", "-s", str(int(160 * speed)),
                                "-w", path, text], check=True, timeout=30)
            elif _has_pyttsx3():
                import pyttsx3
                e = pyttsx3.init()
                e.setProperty("rate", int(170 * speed))
                e.save_to_file(text, path)
                e.runAndWait()
            else:
                return None
            data = open(path, "rb").read()
            return data or None
        except Exception:
            return None


def _has_pyttsx3():
    try:
        import pyttsx3  # noqa: F401
        return True
    except Exception:
        return False


# ------------------------------------------------------------------ routing
class AudioRouter:
    """Speaker (default) | headphones | Bluetooth earbuds, plus 'private mode'.

    Final hardware (`audio.hat: i2s`): speaker amp (MAX98357A) and the I2S headphone DAC share the I2S data-out line,
    so routing = the amp's SD pin (GPIO 25). Headphone jack detect (GPIO 7) forces `headphones`: amp low, speaker silent.
    Legacy WM8960 dev kit (`audio.hat: wm8960`): routing through amixer controls instead.
    Bluetooth is detected with bluetoothctl; if the earbuds are not connected the router falls back to the speaker.
    `run` is injectable so tests can capture commands.
    """

    def __init__(self, cfg: dict, run=None):
        self.cfg = cfg["audio"]
        self.run = run or self._run
        self.output = self.cfg["output"]
        self.private = bool(self.cfg["private_mode"])
        self.jack_in = False

    @staticmethod
    def _run(cmd: list[str]) -> str:
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout
        except Exception:
            return ""

    def bluetooth_connected(self) -> bool:
        return bool(self.run(["bluetoothctl", "devices", "Connected"]).strip())

    def effective_output(self) -> str:
        if self.jack_in:
            return "headphones"              # a plugged jack always wins (auto-switch)
        if self.output == "bluetooth" and not self.bluetooth_connected():
            return "speaker"        # fall back rather than going silent
        return self.output

    def amp_wanted(self) -> bool:
        """Should the speaker amp be powered when something plays?"""
        out = self.effective_output()
        return out == "speaker" or (out != "speaker" and not self.private)

    def plan(self) -> list[list[str]]:
        out = self.effective_output()
        cmds: list[list[str]] = []
        if self.cfg.get("hat") == "wm8960":
            card = self.cfg["mixer_card"]
            speaker_mute = (out != "speaker") and self.private
            cmds += [["amixer", "-c", card, "sset", "Speaker", "0%" if speaker_mute else "100%"],
                     ["amixer", "-c", card, "sset", "Headphone", "100%" if out == "headphones" else "0%"]]
        if out == "bluetooth" and self.cfg.get("bluetooth_sink"):
            cmds.append(["pactl", "set-default-sink", self.cfg["bluetooth_sink"]])
        return cmds

    def apply(self) -> list[list[str]]:
        cmds = self.plan()
        if sys.platform.startswith("linux"):
            for c in cmds:
                self.run(c)
        return cmds

    def set_output(self, output: str, private: bool | None = None):
        assert output in ("speaker", "headphones", "bluetooth")
        self.output = output
        if private is not None:
            self.private = private
        return self.apply()

    def set_jack(self, plugged: bool):
        self.jack_in = plugged
        return self.apply()

    def alsa_device(self) -> str:
        return "default" if self.effective_output() == "bluetooth" else self.cfg["alsa_device"]

    def speaker_muted(self) -> bool:
        return self.private and self.effective_output() != "speaker"
