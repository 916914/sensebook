import json

from sensebook.audio import AudioRouter, Player, NullBackend, tone_wav, wav_seconds
from sensebook.camera import ScriptedCamera
from sensebook.config import load_config
from sensebook.discussion import Discussion
from sensebook.hardware import KeyboardHardware, NullHardware
from sensebook.providers.mock import MockSpeech, MockTutor


def test_keyboard_events_and_mic_switch():
    hw = KeyboardHardware(log=lambda *a: None)
    for line, ev in [("a", "ask_toggle"), ("p", "play_pause"), ("w", "where_am_i"), ("[", "back"), ("]", "forward"),
                     ("k", "repeat"), ("+", "vol_up"), ("-", "vol_down"), (">", "speed_up"), ("<", "speed_down"),
                     ("t", "quiz"), ("d", "discussion"), ("r", "read_page"), ("q", "quit"),
                     ("say hi there", "say:hi there")]:
        hw.feed_line(line)
        assert hw.events.get_nowait() == ev
    hw.feed_line("m")
    assert hw.mic_muted and hw.events.get_nowait() == "mic_mute_on"


def test_capture_led_counts_nested_cloud_activity():
    hw = NullHardware()
    with hw.cloud_activity():
        with hw.cloud_activity():
            assert hw.led_on
        assert hw.led_on
    assert not hw.led_on


def test_audio_router_private_mode_and_bluetooth_fallback():
    cfg = load_config("nope.yaml", {"audio": {"hat": "wm8960"}})      # legacy WM8960 dev kit routes via amixer
    ran = []
    r = AudioRouter(cfg, run=lambda c: (ran.append(c), "")[1])
    plan = r.set_output("headphones", private=True)
    assert ["amixer", "-c", "wm8960soundcard", "sset", "Speaker", "0%"] in plan and r.speaker_muted()
    r.set_output("speaker")
    assert not r.speaker_muted()
    r.set_output("bluetooth")                      # nothing connected -> falls back to speaker rather than silence
    assert r.effective_output() == "speaker"
    r2 = AudioRouter(cfg, run=lambda c: "Device AA:BB Earbuds" if c[:2] == ["bluetoothctl", "devices"] else "")
    r2.set_output("bluetooth", private=True)
    assert r2.effective_output() == "bluetooth" and r2.speaker_muted() and r2.alsa_device() == "default"


def test_player_pause_stop_and_duration():
    wav = tone_wav(440, 0.5)
    assert abs(wav_seconds(wav) - 0.5) < 0.01
    p = Player(NullBackend())
    assert p.play(wav) is True
    p.pause()
    import threading, time
    res = []
    t = threading.Thread(target=lambda: res.append(p.play(wav)))
    t.start()
    time.sleep(0.1)
    assert t.is_alive()                             # paused
    p.stop()
    t.join(1)
    assert res == [False]


def test_discussion_segments_and_interrupt_replays_segment():
    class P(Player):
        def __init__(self):
            super().__init__(NullBackend())
            self.n = 0

        def play(self, wav):
            self.n += 1
            return self.n != 2                     # interrupt during 2nd call
    d = Discussion(MockTutor(), MockSpeech(), P(), "en", 2)
    d.prepare("A fact. Another fact. A third fact. Fourth fact.")
    assert d.play() is False and d.pos == 1 and d.interrupted
    assert d.play() is True and d.finished()


def test_scripted_camera_turns_pages():
    c = ScriptedCamera()
    c.turn_to(1)
    assert c.low_res().shape[:2] == (120, 160)
