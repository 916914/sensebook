"""SenseBookApp: wires camera, providers, memory, reminders, audio and hardware into one event loop."""
from __future__ import annotations

import queue
import threading
from collections import OrderedDict
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from .audio import (AudioRouter, OfflineSpeech, Player, chime_wav, page_turn_wav, tone_wav)
from .captures import CaptureStore
from .camera import PageTurnDetector, assess_image, encode_jpeg
from .db import Database
from .discussion import Discussion
from .hardware import Hardware
from .memory import Memory
from .messages import msg
from .pages import UNCERTAIN_MARK, PageCache, PageContent, label_number, phash, reading_units
from .battery import BatteryMonitor, NullGauge
from .lens import Undistorter
from .perspective import page_framing
from .pipeline import halves_from_still
from .providers.base import AudioClip, ProviderError, ProviderUnavailable
from .quiz import ConceptTracker, QuizSession
from .reminders import ReminderError, ReminderScheduler, ReminderStore
from .tutor import TutorService


@dataclass
class Spread:
    pages: list[PageContent]
    units: list[tuple[int, int, str]] = field(default_factory=list)   # (page_idx, block_idx, sentence)
    preloaded: bool = False

    @property
    def key(self) -> tuple:
        return tuple(p.page_id for p in self.pages)

    def labels(self) -> list[int | None]:
        return [label_number(p.page_label) for p in self.pages]


ERROR_KEYS = {"cloud_error", "no_internet", "no_internet_new_page", "camera_blocked", "page_unclear", "low_confidence",
              "mic_off", "too_dark", "edge_not_visible", "book_upside_down", "reminder_bad"}


class AudioIO:
    """QuizSession I/O: speak() and listen() (listen waits for the next utterance from Ask)."""

    def __init__(self, app: "SenseBookApp"):
        self.app = app

    def speak(self, text, role="explainer"):
        self.app.say(text, role, chime=False)

    def listen(self, timeout=45.0):
        self.app.log("[quiz] waiting for your answer (hold Ask / say <text>)")
        try:
            return self.app.answer_q.get(timeout=timeout)
        except queue.Empty:
            return None


class SenseBookApp:
    def __init__(self, cfg: dict, vision, tutor, speech, camera=None, hardware: Hardware | None = None,
                 recorder=None, player: Player | None = None, db: Database | None = None, clock=None,
                 log=print, offline: OfflineSpeech | None = None, gauge=None):
        self.cfg, self.log = cfg, log
        self.tz = ZoneInfo(cfg["timezone"])
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.db = db or Database(str(__import__("pathlib").Path(cfg["data_dir"]) / "sensebook.db"))
        self.memory = Memory(self.db, clock=lambda: self.clock().isoformat(timespec="seconds"))
        if self.db.one("SELECT 1 x FROM profile WHERE key='language'") is None:
            self.memory.set("language", cfg["language"])
        if self.db.one("SELECT 1 x FROM profile WHERE key='voice_speed'") is None:
            self.memory.set("voice_speed", cfg["voice_speed"])
        self.captures = CaptureStore(cfg)
        self.cache = PageCache(self.db, cfg["pages"]["phash_max_distance"])
        self.vision, self.tutor_p, self.speech = vision, tutor, speech
        self.camera, self.hw, self.recorder = camera, hardware or Hardware(log), recorder
        self.player = player or Player()
        self.router = AudioRouter(cfg)
        self.offline = offline or OfflineSpeech()
        self.reminders = ReminderStore(self.db, self.clock, self.tz)
        self.scheduler = ReminderScheduler(self.reminders, lambda r: self.hw.events.put(f"reminder:{r.id}"))
        self.tracker = ConceptTracker(self.db, self.memory, self.clock)
        self.tutor = TutorService(tutor, self.memory, self.tz, self.clock, self._handlers())
        self.detector = PageTurnDetector(**{k: cfg["camera"][k] for k in (
            "motion_threshold", "still_threshold", "stable_seconds", "change_threshold",
            "hand_skin_fraction", "hand_motion_fraction")})
        # state
        self.spread: Spread | None = None
        self.session_pages: list[PageContent] = []
        self.recording = False
        self.read_idx = 0
        self._reading = False
        self._read_lock = threading.Lock()
        self._read_thread: threading.Thread | None = None
        self._tts_futs: "OrderedDict[tuple, object]" = OrderedDict()     # (text, lang, speed) -> Future[wav]
        self.history: list[tuple] = []          # stack of spread keys visited (browser-style)
        self.positions: dict[tuple, int] = {}   # spread key -> sentence index where reading stopped
        self.read_mode = False                  # user started reading and has not stopped it: auto-continue on flips
        self._flip_hold = False                 # reading is held (hand in frame / flip in progress)
        self._settle_t: float | None = None
        self.metrics: dict[str, list] = {"flip_to_audio": []}
        self.flip = cfg["flip"]
        self._last_back = 0.0
        self.mode = "idle"      # idle | reading | discussion | quiz
        self.answer_q: queue.Queue = queue.Queue()
        self._disc: Discussion | None = None
        self._disc_resume = threading.Event()
        self._pending_confirm: tuple[str, float] | None = None
        self.undistorter = Undistorter(cfg["camera"].get("lens"))
        self.attach_pending = False             # set on attach / at boot (device): next good spread gets the guidance
        self._full_res = False                  # small-print mode: capture at full resolution until a page reads well
        self._sp_state: str | None = None       # None | wait_scene (stick being pulled up) | wait_play
        self._sp_since = 0.0
        self.gauge = gauge or NullGauge()
        self.battery = BatteryMonitor(self.gauge, cfg["battery"]["warn_levels"], self._battery_announce)
        self._last_battery_poll = -1e9
        self.player.pre_play = self._amp_up
        self.work = ThreadPoolExecutor(max_workers=2, thread_name_prefix="work")
        self.prefetch = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tts")
        self._stop = threading.Event()
        self._session_id = self.memory.start_session()
        self._t0 = time.time()
        self._last_review_check = 0.0
        self._last_reminder_fire = 0.0

    # ------------------------------------------------------------------ language / voice helpers
    @property
    def lang(self) -> str:
        return self.memory.get("language", "bn")

    @property
    def speed(self) -> float:
        return float(self.memory.get("voice_speed", "1.0"))

    def apply_settings(self):
        """Called after the web app changes settings."""
        self.router.output = self.memory.get("headphone_pref", "speaker")
        self.router.jack_in = self.hw.jack_in
        self.router.apply()
        if not self.router.amp_wanted():
            self.hw.set_amp(False)
        self.hw.set_light(float(self.memory.get("light_level", "0.4")))

    def say(self, text: str, role: str = "explainer", chime: bool = True, prefer_offline: bool = False) -> bool:
        """Speak text. role=explainer is the AI voice (preceded by a chime); role=reader is faithful reading."""
        if not text:
            return True
        wav = None
        if prefer_offline and self.offline.available():
            wav = self.offline.synthesize(text, self.lang, self.speed)
        if wav is None:
            try:
                with self.hw.cloud_activity():
                    wav = self.speech.synthesize(text, role, self.lang, self.speed)
            except ProviderError:
                wav = self.offline.synthesize(text, self.lang, self.speed) if self.offline.available() else None
        self.log(f"[{role}] {text}")
        if wav is None:
            return False
        if chime and role == "explainer":
            self.player.play(chime_wav())
        return self.player.play(wav)

    def notify(self, key: str, **kw):
        """System notice: offline voice first (instant, works without internet)."""
        if key in ERROR_KEYS:
            self.hw.haptic("error")
        self.say(msg(key, self.lang, **kw), "explainer", chime=False, prefer_offline=True)

    # ------------------------------------------------------------------ pages
    @property
    def spoken_prompt(self) -> bool:
        return bool(self.flip["spoken_prompt"]) or self.memory.get("accessibility_mode") == "1"

    def _fail_capture(self, key: str | None):
        """Capture unusable: re-arm the detector so the next settle tries again, release any held reading."""
        self.detector.invalidate()
        self.player.duck = 1.0
        if self._flip_hold:
            self.stop_reading()          # keep read_mode: reading resumes when a good page is captured
        if key:
            self.notify(key)

    def on_page_settled(self, t_settle: float | None = None):
        """A settled, changed scene: capture, rectify, split, read (cache first), then continue reading."""
        t0 = t_settle or self._settle_t or time.monotonic()
        if not self.camera:
            return
        self._sp_state = None                          # a settle (or Play) arrived: stop waiting
        img = self.camera.capture_still(full=self._full_res)
        if img is None:
            return self._fail_capture("camera_blocked")
        if self.detector.hand_in_frame(img):          # never capture a hand over the text
            self.log("[capture] hand over the page: skipped, waiting")
            return self._fail_capture(None)
        halves, info = halves_from_still(img, self.cfg["camera"], self.undistorter)     # undistort -> keystone -> split
        if self.attach_pending and self.cfg["camera"].get("attach_checks", True):
            if page_framing(info["undistorted"]) != "ok":
                return self._fail_capture("edge_not_visible")
        problem = assess_image(info["rectified"])
        if problem:
            return self._fail_capture({"blocked": "camera_blocked", "dark": "too_dark", "blurry": "page_unclear"}[problem])
        pages, offline_miss = [], False
        for half in halves:
            h = phash(half)
            pc = self.cache.lookup(h)
            if pc is None:
                try:
                    with self.hw.cloud_activity():      # LED on while the image is being sent
                        jpeg = encode_jpeg(half)
                        self.captures.save('page', jpeg, 'jpg')
                        pc = self.vision.read_page(jpeg, self.lang)
                except ProviderUnavailable:
                    offline_miss = True
                    continue
                except ProviderError as e:
                    self.log(f"[vision error] {e}")
                    return self._fail_capture("cloud_error")
                if pc.upside_down:
                    return self._fail_capture("book_upside_down")
                if pc.problem or not pc.blocks:
                    self.notify("page_unclear")
                    continue
                if pc.confidence < self.cfg["pages"]["min_confidence"]:
                    if not self._full_res:        # small print on a page not in the library
                        self._full_res = True
                        self.notify("small_print")
                        self._sp_state, self._sp_since = "wait_scene", time.monotonic()
                        self.detector.invalidate()    # the next settle (view changed as the stick extends) is captured
                        return self._fail_capture(None)
                    self.notify("low_confidence")
                    continue      # never cache or read a doubtful page
                self.cache.store(h, pc, self.memory.get("current_book"))
            pages.append(pc)
        if not pages:
            return self._fail_capture("no_internet_new_page" if offline_miss else None)
        if offline_miss:
            self.notify("no_internet")
        self._install_spread(pages, t0)

    # ---- spread bookkeeping -------------------------------------------------------------------------
    def _classify(self, spread: Spread) -> str:
        """first | same | back | skip | forward"""
        if not self.history or not self.spread:
            return "first"
        key = spread.key
        if key == self.history[-1]:
            return "same"
        if key in self.history:
            return "back"
        cur = [x for x in self.spread.labels() if x is not None]
        new = [x for x in spread.labels() if x is not None]
        if cur and new:
            if new[0] < cur[0]:
                return "back"
            if new[0] > cur[-1] + 1:
                return "skip"
        return "forward"

    def _page_label_text(self, spread: Spread) -> int | None:
        known = [x for x in spread.labels() if x is not None]
        return known[0] if known else None

    def _remember_position(self):
        if self.spread and self.history:
            # read_idx is the sentence being read (or the next one): the "unfinished sentence"
            self.positions[self.history[-1]] = min(self.read_idx, max(0, len(self.spread.units) - 1))

    def _install_spread(self, pages: list[PageContent], t0: float):
        new = Spread(pages, [(pi, bi, s) for pi, p in enumerate(pages) for bi, s in reading_units(p)])
        kind = self._classify(new)
        was_reading = self.read_mode
        self.stop_reading()
        self._flip_hold = False
        self.player.duck = 1.0
        if kind != "same":
            self._remember_position()
        self.spread = new
        for p in pages:
            if not any(p.page_id == q.page_id for q in self.session_pages):
                self.session_pages.append(p)
        start = 0
        if kind == "same":
            start = self.read_idx if self.read_idx < len(new.units) else 0
        elif new.key in self.positions and (kind == "back" or self.positions[new.key] < len(new.units) - 1):
            start = self.positions[new.key]            # back-flip: last read sentence; revisit: unfinished sentence
        if kind == "back" and new.key in self.history:
            del self.history[self.history.index(new.key) + 1:]      # browser-style: leaving the later pages
        elif kind != "same":
            self.history.append(new.key)
        self.read_idx = start
        self._full_res = False
        was_attach, self.attach_pending = self.attach_pending, False
        self.memory.update_session(self._session_id, len(self.session_pages), int(time.time() - self._t0))
        self.log(f"[page] {kind}: labels={new.labels()} sentences={len(new.units)} start={start} "
                 f"cached={[p.from_cache for p in pages]}")
        auto = was_reading and self.flip["auto_continue"] and new.units and not was_attach
        if auto:
            self._arm_latency(t0, kind, new, start)
        n = self._page_label_text(new)
        if was_attach:
            known = [x for x in new.labels() if x is not None]
            self.notify("ready_pages" if len(known) >= 2 else "ready_page" if known else "ready_book",
                        a=known[0] if known else "", b=known[1] if len(known) > 1 else "")
            return
        if kind == "back":
            self.notify("back_to_page" if n is not None else "back_to_prev", n=n)
        elif kind == "skip" and n is not None:
            self.notify("page_n", n=n)
        if auto:
            self.start_reading(start)
        elif kind != "same":
            self.notify("page_ready")

    def _arm_latency(self, t0: float, kind: str, spread: Spread, start: int):
        warm = self._tts_ready(self._unit_text(start, spread)) if spread.units else False

        def done():
            dt = time.monotonic() - t0
            self.metrics["flip_to_audio"].append({"seconds": round(dt, 3), "kind": kind, "preloaded": warm})
            self.log(f"[flip] settle->first audio {dt * 1000:.0f} ms ({kind}, tts {'preloaded' if warm else 'cold'})")
        self.player.on_start = done

    def go_previous_spread(self) -> bool:
        """Back button at the top of a spread: return to the unfinished sentence on the previous spread."""
        if len(self.history) < 2:
            return False
        prev_key = self.history[-2]
        pages = [self.cache.get(pid) for pid in prev_key if pid]
        if not pages or any(p is None for p in pages):
            return False
        self.stop_reading()
        self._remember_position()
        self.history.pop()
        self.spread = Spread(pages, [(pi, bi, s) for pi, p in enumerate(pages) for bi, s in reading_units(p)])
        self.read_idx = min(self.positions.get(prev_key, 0), max(0, len(self.spread.units) - 1))
        n = self._page_label_text(self.spread)
        self.notify("back_to_page" if n is not None else "back_to_prev", n=n)
        self.start_reading(self.read_idx)
        return True

    def page_text(self) -> str:
        return "\n".join(p.text for p in self.spread.pages) if self.spread else ""

    def session_text(self) -> str:
        return "\n\n".join(p.text for p in self.session_pages)

    # ------------------------------------------------------------------ faithful reading
    def _unit_text(self, i: int, spread: Spread | None = None) -> str:
        sp = spread or self.spread
        return sp.units[i][2].replace(UNCERTAIN_MARK, msg("unclear_word", self.lang))

    def _tts_text(self, text: str, lang: str | None = None):
        """One Future per (text, lang, speed): the reader, the prefetcher and the flip preloader all share it,
        so a sentence is synthesized once."""
        key = (text, self.lang, self.speed)
        with self._read_lock:
            fut = self._tts_futs.get(key)
            if fut is None:
                fut = self._tts_futs[key] = self.prefetch.submit(self._synth_text, text, lang)
                while len(self._tts_futs) > 64:
                    self._tts_futs.popitem(last=False)
            else:
                self._tts_futs.move_to_end(key)
        return fut

    def _tts_ready(self, text: str) -> bool:
        with self._read_lock:
            fut = self._tts_futs.get((text, self.lang, self.speed))
        return bool(fut and fut.done() and fut.result())

    def _synth_text(self, text: str, page_lang: str | None) -> bytes | None:
        try:
            with self.hw.cloud_activity():
                return self.speech.synthesize(text, "reader", self.lang, self.speed)
        except ProviderError:
            if self.offline.available():
                return self.offline.synthesize(text, page_lang or self.lang, self.speed)
        return None

    def _preload_next(self):
        """While spread N is read, warm the TTS for the first sentences of the predicted spread N+1."""
        pre = self.flip["preload"]
        if not pre["enabled"] or not self.spread or self.spread.preloaded:
            return
        self.spread.preloaded = True
        nxt = self.cache.successor(self.spread.pages)
        if not nxt:
            return
        texts = [s.replace(UNCERTAIN_MARK, msg("unclear_word", self.lang))
                 for p in nxt for _, s in reading_units(p)][: pre["sentences"]]
        for t in texts:
            self._tts_text(t)
        self.log(f"[preload] next spread known ({len(nxt)} page(s)); warming {len(texts)} sentence(s)")

    def start_reading(self, from_idx: int | None = None):
        if not self.spread or not self.spread.units:
            return self.notify("nothing_read")
        self.stop_reading()
        self._drop_discussion()
        if from_idx is not None:
            self.read_idx = from_idx
        if self.read_idx >= len(self.spread.units):
            self.read_idx = 0
        self._reading, self.mode, self.read_mode = True, "reading", True
        self.player.resume()
        self._read_thread = threading.Thread(target=self._read_loop, daemon=True, name="reader")
        self._read_thread.start()

    def _read_loop(self):
        spread = self.spread
        while self._reading:
            while self._flip_hold and self._reading:      # hand in frame / flip under way: hold position
                time.sleep(0.02)
            with self._read_lock:
                i = self.read_idx
            if not self._reading or i >= len(spread.units):
                break
            wav = self._tts_text(self._unit_text(i, spread), spread.pages[spread.units[i][0]].lang).result()
            for j in (i + 1, i + 2):          # prefetch next sentences while this one plays
                if j < len(spread.units):
                    self._tts_text(self._unit_text(j, spread), spread.pages[spread.units[j][0]].lang)
            self._preload_next()
            if wav is None:
                self.log("[reader] no audio available")
                break
            if self._flip_hold or not self._reading:
                continue
            self.log(f"[reader] {spread.units[i][2]}")
            ok = self.player.play(wav)
            with self._read_lock:
                if ok and self.read_idx == i:
                    self.read_idx += 1
        finished = self._reading and self.read_idx >= len(spread.units) and spread is self.spread
        self._reading = False
        if self.mode == "reading":
            self.mode = "idle"
        if finished:
            self._end_of_spread()

    def _end_of_spread(self):
        if self.read_mode and self.flip["auto_continue"]:
            if self.flip["earcon"]:
                self.player.play(page_turn_wav())
            if self.spoken_prompt:
                self.notify("turn_page")
            self.log("[reader] end of spread: waiting for the page turn")
        else:
            self.notify("end_of_page")

    def _drop_discussion(self):
        if self._disc:
            self._disc_resume.set()
            self._disc = None

    def stop_reading(self):
        self._reading = False
        self._flip_hold = False
        self.player.stop()
        if self._read_thread and self._read_thread is not threading.current_thread():
            self._read_thread.join(timeout=2)
        self._read_thread = None
        if self.mode == "reading":
            self.mode = "idle"

    def stop_all(self):
        """User-level stop: also ends 'read mode' so a page turn will not start reading by itself."""
        self.read_mode = False
        self.stop_reading()
        self._drop_discussion()
        self.player.stop()

    def jump(self, delta: int, paragraph: bool = False):
        if not self.spread:
            return
        with self._read_lock:
            if paragraph:
                u = self.spread.units
                starts = [k for k in range(len(u)) if k == 0 or u[k][:2] != u[k - 1][:2]]
                cur_start = max(k for k in starts if k <= self.read_idx)
                prev = [k for k in starts if k < cur_start]
                if delta < 0 and not prev and cur_start == 0 and self.read_idx == 0:
                    target = "prev_spread"
                else:
                    target = prev[-1] if prev else 0
            elif delta < 0 and self.read_idx == 0:
                target = "prev_spread"
            else:
                target = max(0, min(len(self.spread.units) - 1, self.read_idx + delta))
        if target == "prev_spread":
            if not self.go_previous_spread():
                self.start_reading(0)
            return
        with self._read_lock:
            self.read_idx = target
        if self._reading:
            self.player.stop()          # loop picks up the new index
        else:
            self.start_reading()

    # ------------------------------------------------------------------ hand / flip events
    def on_hand_in(self):
        act = self.flip["hand_action"]
        if act == "none":
            return
        self.player.duck = float(self.flip["duck_level"])
        if act == "stop" and self._reading and not self.player.paused:
            self._flip_hold = True                      # remember position: read_idx is the interrupted sentence
            if self.flip["stop_mode"] == "word":
                self.player.stop_soft(0.25)
            else:
                self.player.stop()
            self.log(f"[flip] hand in frame: holding at sentence {self.read_idx}")

    def on_scene_settled_same(self):
        """The hand left and the page did not change: carry on exactly where we were."""
        self.player.duck = 1.0
        if self._flip_hold:
            self._flip_hold = False
            self.log("[flip] same page: resuming")

    # ------------------------------------------------------------------ Ask
    def ask_start(self):
        if self.hw.mic_muted:
            return self.notify("mic_off")          # hard block: nothing is recorded
        if self.recording or not self.recorder:
            return
        self.player.stop()                          # stop whatever is playing; reading position is kept
        if self._reading:
            self._reading = False
            self.mode = "idle"
        self.read_mode = False                       # after an answer the user presses Play to continue
        self._flip_hold = False
        self.recorder.start()
        self.recording = True
        self.hw.set_dot("listening", True)
        self.log("[ask] recording...")

    def ask_stop(self):
        if not self.recording:
            return
        self.recording = False
        self.hw.set_dot("listening", False)
        wav = self.recorder.stop()
        if self.hw.mic_muted or not wav:      # switch flipped mid-recording: discard
            return self.notify("not_heard") if not self.hw.mic_muted else self.notify("mic_off")
        self.captures.save('ask', wav, 'wav')
        clip = AudioClip(wav, getattr(self.recorder, "last_transcript", None))
        self.work.submit(self.on_utterance, clip)

    def on_utterance(self, clip: AudioClip):
        if self.mode == "quiz":
            return self.answer_q.put(clip)
        if self.mode == "discussion" and self._disc:
            return self._discussion_interrupt(clip)
        try:
            with self.hw.cloud_activity():            # audio goes to the cloud
                text, confirmations = self.tutor.ask(clip, self.lang, self.page_text(),
                                                     [p.text for p in self.session_pages[-4:]])
        except ProviderUnavailable:
            return self.notify("no_internet")
        except ProviderError as e:
            self.log(f"[tutor error] {e}")
            return self.notify("cloud_error")
        if text:
            self.say(text, "explainer", chime=True)
        for c in confirmations:
            self.say(c, "explainer", chime=False, prefer_offline=True)
        if self.spread and self.read_idx > 0 and self.mode == "idle":
            self.notify("resume")

    # ------------------------------------------------------------------ tools (function calling targets)
    def _handlers(self):
        return {"set_reminder": self._t_reminder, "remember_note": self._t_note, "start_quiz": self._t_quiz,
                "start_discussion": self._t_discussion, "read_page": lambda a: self._later(self.start_reading),
                "bookmark": self._t_bookmark, "set_language": self._t_lang, "forget": self._t_forget}

    def _later(self, fn, *a):
        threading.Thread(target=fn, args=a, daemon=True).start()

    def _t_reminder(self, a):
        try:
            r = self.reminders.from_tool_args(a)
        except ReminderError as e:
            self.log(f"[reminder] {e}")
            return msg("reminder_bad", self.lang)
        when = r.next_fire.astimezone(self.tz).strftime("%a %d %b, %I:%M %p")
        return f"{msg('reminder_set', self.lang)} {r.message}. {when}" + ("" if r.repeat == "none" else f", {r.repeat}")

    def _t_note(self, a):
        if not self.memory.enabled:
            return msg("memory_off", self.lang)
        self.memory.add_note(a["text"])
        return msg("noted", self.lang)

    def _t_bookmark(self, a):
        if not self.memory.enabled:
            return msg("memory_off", self.lang)
        pid = self.spread.pages[0].page_id if self.spread else None
        self.memory.add_bookmark(self.memory.get("current_book"), pid, a.get("label") or "bookmark")
        return msg("bookmarked", self.lang)

    def _t_lang(self, a):
        if a.get("language") in ("bn", "en"):
            self.memory.set("language", a["language"])
        return None

    def _t_forget(self, a):
        if a.get("scope") == "note":
            n = self.memory.delete_note_matching(a.get("text", ""))
            return msg("forgot", self.lang) if n else None
        # Deleting everything needs a *physical* confirmation (knob press). The PIN protects the web path.
        self._pending_confirm = ("forget_all", time.time() + 10)
        return msg("confirm_delete", self.lang)

    def _t_quiz(self, a):
        self._later(self.start_quiz, a.get("num_questions"))
        return None

    def _t_discussion(self, a):
        self._later(self.start_discussion, a.get("minutes"))
        return None

    # ------------------------------------------------------------------ quiz
    def start_quiz(self, n=None):
        text = self.session_text()
        if not text:
            return self.notify("nothing_read")
        self.stop_all()
        self.mode = "quiz"
        try:
            while not self.answer_q.empty():
                self.answer_q.get_nowait()
            QuizSession(self.tutor_p, self.memory, self.tracker, AudioIO(self), self.lang,
                        self.memory.get("level")).run(text, source_page=self.session_pages[-1].page_label)
        except ProviderUnavailable:
            self.notify("no_internet")
        except ProviderError as e:
            self.log(f"[quiz error] {e}")
            self.notify("cloud_error")
        finally:
            self.mode = "idle"

    # ------------------------------------------------------------------ discussion
    def start_discussion(self, minutes=None):
        text = self.session_text()
        if not text:
            return self.notify("nothing_read")
        self.stop_all()
        d = Discussion(self.tutor_p, self.speech, self.player, self.lang, self.cfg["discussion"]["segment_lines"])
        try:
            with self.hw.cloud_activity():
                d.prepare(text, minutes or self.cfg["discussion"]["minutes"])
        except ProviderUnavailable:
            return self.notify("no_internet")
        except ProviderError as e:
            self.log(f"[discussion error] {e}")
            return self.notify("cloud_error")
        self._disc, self.mode = d, "discussion"
        self.say("Chapter talk." if self.lang == "en" else "অধ্যায় আলোচনা।", "explainer", chime=True, prefer_offline=True)
        self._disc_thread = threading.Thread(target=self._disc_loop, args=(d,), daemon=True, name="discussion")
        self._disc_thread.start()

    def _disc_loop(self, d: Discussion):
        while self._disc is d and not d.finished():
            if d.play():
                break
            self._disc_resume.wait()          # interrupted: wait for resume (Play) or cancel
            self._disc_resume.clear()
        if self._disc is d:
            self._disc, self.mode = None, "idle"

    def _discussion_interrupt(self, clip):
        d = self._disc
        try:
            with self.hw.cloud_activity():
                d.answer_interruption(clip)
        except ProviderError:
            self.notify("cloud_error")
        self.notify("resume")

    # ------------------------------------------------------------------ event handling
    def handle(self, ev: str):
        if self._pending_confirm and ev in ("forward", "back"):       # "forget everything": Forward confirms, Back cancels
            ok = time.time() < self._pending_confirm[1]
            self._pending_confirm = None
            if ev == "forward" and ok:
                self.memory.delete_everything()
                return self.notify("deleted")
            return self.notify("delete_cancelled")
        if ev == "ask_toggle":
            self.ask_start() if not self.recording else self.ask_stop()
        elif ev == "ask_down":
            self.ask_start()
        elif ev == "ask_up":
            self.ask_stop()
        elif ev.startswith("say:"):
            self.player.stop()
            self.work.submit(self.on_utterance, AudioClip(b"", ev[4:]))
        elif ev == "play_pause":
            self._play_pause()
        elif ev == "back":
            now = time.time()
            self.jump(-1, paragraph=(now - self._last_back < 1.0))     # double-tap = previous paragraph
            self._last_back = now
        elif ev == "forward":
            self.jump(+1)
        elif ev == "vol_up" or ev == "vol_down":
            self.player.volume = max(0.1, min(1.0, self.player.volume + (0.1 if ev == "vol_up" else -0.1)))
            self.log(f"[volume] {self.player.volume:.0%}")
            self.player.play(tone_wav(600 + 400 * self.player.volume, 0.08))
        elif ev == "repeat":
            if self.spread and self.spread.units:
                self.start_reading(max(0, self.read_idx - 1 if not self._reading else self.read_idx))   # hold Back
        elif ev == "where_am_i":
            self.where_am_i()
        elif ev in ("speed_up", "speed_down"):
            self.change_speed(+1 if ev == "speed_up" else -1)
        elif ev == "headphones_in" or ev == "headphones_out":
            self.on_jack(ev == "headphones_in")
        elif ev == "attached":
            self.on_attached()
        elif ev == "detached":
            self.on_detached()
        elif ev == "quiz":
            self._later(self.start_quiz)
        elif ev == "discussion":
            self._later(self.start_discussion)
        elif ev == "read_page":
            self._later(self.start_reading)
        elif ev == "page_settled":
            self.work.submit(self.on_page_settled, self._settle_t)
        elif ev == "hand_in":
            self.on_hand_in()
        elif ev == "scene_settled":
            self.on_scene_settled_same()
        elif ev in ("sim_hand", "sim_turn", "sim_back"):
            cam = self.camera
            fn = {"sim_hand": "toggle_hand", "sim_turn": "simulate_turn", "sim_back": "simulate_back"}[ev]
            if cam is not None and hasattr(cam, fn):
                getattr(cam, fn)()
                self.log(f"[sim] {fn}")
            else:
                self.log("[sim] needs --fake-camera (mock provider)")
        elif ev in ("mic_mute_on", "mic_mute_off"):
            if ev == "mic_mute_on" and self.recording:
                self.recording = False
                self.recorder.stop()
            self.notify("mic_off" if ev == "mic_mute_on" else "mic_on")
        elif ev.startswith("reminder:"):
            self._on_reminder(int(ev.split(":")[1]))
        elif ev == "review_due":
            self.notify("review_due")
        elif ev == "quit":
            self._stop.set()

    def _on_reminder(self, rid: int):
        r = self.reminders.get(rid)
        if not r:
            return
        self.player.stop()
        self._reading = False
        self.read_mode = False
        self._flip_hold = False
        self._last_reminder_fire = time.time()
        self.hw.haptic("reminder")
        self.say(f"Reminder: {r.message}" if self.lang == "en" else f"রিমাইন্ডার: {r.message}", "explainer", chime=True)

    def small_print_tick(self):
        """No scene change within camera.small_print_wait_s after "pull the stick up": ask for a Play press instead."""
        if self._sp_state == "wait_scene" and time.monotonic() - self._sp_since >= self.cfg["camera"]["small_print_wait_s"]:
            self._sp_state = "wait_play"
            self.notify("small_print_play")

    def _play_pause(self):
        if self._sp_state in ("wait_scene", "wait_play"):      # the stick is up: capture at full resolution now
            self._sp_state = None
            self.work.submit(self.on_page_settled)
            return
        if time.time() - self._last_reminder_fire < 60 and self.scheduler.last_fired:
            if self.scheduler.snooze_last(10):
                self._last_reminder_fire = 0
                return self.notify("snoozed")
        if self._disc:
            if self.player.playing:
                return self.player.toggle()
            self._disc_resume.set()           # resume after an interruption
            self.player.resume()
        elif self._reading:
            self.player.toggle()
            self.read_mode = not self.player.paused      # paused by the user: a page turn must not restart reading
        else:
            self.start_reading()

    # ---- speed, "where am I", jack, hub, battery, amp ----------------------------------------------
    def change_speed(self, direction: int):
        step = self.cfg["hardware"]["speed_step"]
        new = round(min(1.4, max(0.7, self.speed + direction * step)), 2)
        self.memory.set("voice_speed", new)
        self.log(f"[speed] {new}")
        self.player.play(tone_wav(700 if direction > 0 else 450, 0.08))
        return new

    def where_am_i(self):
        if not self.spread:
            text = msg("where_none", self.lang)
        else:
            known = [str(x) for x in self.spread.labels() if x is not None]
            pages = (" and " if self.lang == "en" else " ও ").join(known) or "?"
            text = msg("where", self.lang, pages=pages, i=min(self.read_idx + 1, len(self.spread.units)), n=len(self.spread.units))
        pct = self.battery.poll()
        if pct is not None:
            text += " " + msg("battery", self.lang, pct=round(pct))
        if self._reading:
            self.player.stop()
            self._reading = False
        self.say(text, "explainer", chime=False, prefer_offline=True)

    def on_jack(self, plugged: bool):
        """Jack-detect (GPIO 7): auto-switch to headphones (amp SD low) and back."""
        self.router.set_jack(plugged)
        self.hw.jack_in = plugged
        if plugged:
            self.hw.set_amp(False)              # speaker silent before the announcement: it goes to the headphones
        self.notify("headphones" if plugged else "speaker")

    def on_attached(self):
        self.attach_pending = True
        self._full_res, self._sp_state = False, None
        self.spread, self.history = None, []
        self.detector.reset()
        self.hw.haptic("attached")
        self.notify("attached")

    def on_detached(self):
        was_reading = self._reading or self.player.playing
        self.attach_pending = True
        if was_reading:
            self.read_mode = False
            self.stop_reading()                 # position kept in read_idx
            self.notify("detached")

    def _battery_announce(self, pct: float, level: int):
        self.hw.set_dot("warn", True)
        self.notify("battery_low", pct=round(pct))

    def poll_battery(self, force: bool = False):
        now = time.monotonic()
        if force or now - self._last_battery_poll >= self.cfg["battery"]["poll_seconds"]:
            self._last_battery_poll = now
            self.battery.poll()
            self.hw.set_dot("warn", self.battery.low)

    def _amp_up(self):
        """Called before every playback: wake the speaker amp unless headphones are in."""
        if self.router.amp_wanted() and not self.hw.amp_on:
            self.hw.set_amp(True)
            time.sleep(0.02)                    # MAX98357A turn-on time

    def amp_tick(self):
        """Amp SD low when idle (power saving). Headphones in: always low."""
        if self.hw.amp_on and (not self.router.amp_wanted() or
                               (not self.player.playing and time.monotonic() - self.player.last_active >
                                self.cfg["audio"]["amp_idle_seconds"])):
            self.hw.set_amp(False)

    def check_reviews(self):
        if self.memory.enabled and self.tracker.due():
            self.hw.events.put("review_due")

    # ------------------------------------------------------------------ main loop
    def _camera_loop(self):
        period = 1.0 / self.cfg["camera"]["fps"]
        while not self._stop.is_set():
            try:
                f = self.camera.low_res()
                if f is not None:
                    now = time.monotonic()
                    ev = self.detector.feed_event(f, now)
                    if ev == "hand_in":
                        self.hw.events.put("hand_in")
                    elif ev == "settled_changed":
                        self._settle_t = now
                        self.hw.events.put("page_settled")
                    elif ev == "settled_same":
                        self.hw.events.put("scene_settled")
            except Exception as e:  # camera hiccup must not kill the loop
                self.log(f"[camera] {e}")
            time.sleep(period)

    def run(self):
        self.apply_settings()
        self.hw.start()
        self.scheduler.start()
        if self.camera:
            threading.Thread(target=self._camera_loop, daemon=True, name="camera").start()
        else:
            self.log("[camera] none: running without page following")
        self.hw.set_dot("ready", True)
        self.notify("ready")
        self.check_reviews()
        try:
            while not self._stop.is_set():
                try:
                    ev = self.hw.events.get(timeout=0.25)
                except queue.Empty:
                    self.amp_tick()
                    self.small_print_tick()
                    self.poll_battery()
                    if time.time() - self._last_review_check > 3600:
                        self._last_review_check = time.time()
                        self.check_reviews()
                    continue
                try:
                    self.handle(ev)
                except Exception as e:
                    self.log(f"[error] {type(e).__name__}: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        self._stop.set()
        self._disc_resume.set()
        self.scheduler.stop()
        self.player.stop()
        self.memory.update_session(self._session_id, len(self.session_pages), int(time.time() - self._t0))
        for c in (self.camera, self.hw):
            try:
                c and c.close()
            except Exception:
                pass
