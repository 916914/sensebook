"""Camera backends, page-turn detector, spread splitter and image-quality checks."""
from __future__ import annotations

import time
from dataclasses import dataclass

import cv2
import numpy as np


# ---------------------------------------------------------------- page-turn detector
def _touches_border(mask: np.ndarray, band: int = 4) -> bool:
    return bool(mask[:band].any() or mask[-band:].any() or mask[:, :band].any() or mask[:, -band:].any())


class PageTurnDetector:
    """Scene-state machine for page following.

    * Hand handling: a hand (skin-tone region entering from the outer edges, measured against a slowly
      tracked skin baseline so cream paper does not count) or a large motion blob touching the border sets
      `hand=True`. While a hand is present nothing can settle, so a frame with a hand over the text is never
      captured.
    * Page turn: motion, then ~`stable_seconds` of stillness => a settle event.
    * A settled scene that differs from the last captured one is `settled_changed` (capture it); one that
      matches is `settled_same` (a hand came and went: just resume).
    Time is passed in, so tests are deterministic.
    """

    def __init__(self, motion_threshold=0.035, still_threshold=0.012, stable_seconds=1.0, change_threshold=0.01,
                 hand_skin_fraction=0.04, hand_motion_fraction=0.2):
        self.motion_t, self.still_t = motion_threshold, still_threshold
        self.stable_s, self.change_t = stable_seconds, change_threshold
        self.hand_skin, self.hand_motion = hand_skin_fraction, hand_motion_fraction
        self.prev = None
        self.ref = None            # frame at last capture
        self.moving = False
        self.hand = False
        self.skin_base: float | None = None
        self.still_since = None
        self.armed_first = True    # first stable scene after start is captured too

    @staticmethod
    def _prep(frame: np.ndarray) -> np.ndarray:
        g = frame if frame.ndim == 2 else cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        g = cv2.resize(g, (64, 48), interpolation=cv2.INTER_AREA)
        return cv2.GaussianBlur(g, (5, 5), 0).astype(np.float32) / 255.0

    @staticmethod
    def skin_mask(frame: np.ndarray) -> np.ndarray | None:
        if frame.ndim != 3 or frame.shape[2] != 3:
            return None            # luma-only frame: motion blob is the only hand cue
        ycc = cv2.cvtColor(cv2.resize(frame, (80, 60), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2YCrCb)
        y, cr, cb = ycc[..., 0], ycc[..., 1], ycc[..., 2]
        return (cr >= 142) & (cr <= 180) & (cb >= 80) & (cb <= 128) & (y > 50)

    def hand_in_frame(self, frame: np.ndarray) -> bool:
        """Skin test for a single (e.g. high-res still) frame, relative to the tracked baseline."""
        m = self.skin_mask(frame)
        if m is None:
            return False
        return float(m.mean()) - (self.skin_base or 0.0) > self.hand_skin and _touches_border(m)

    def reset(self):
        """New book attached: forget the previous scene; the first stable scene is captured again."""
        self.ref, self.prev, self.moving, self.hand, self.armed_first, self.still_since = None, None, False, False, True, None

    def invalidate(self):
        """The last settled scene was not usable (hand, blur...): make the next settle capture again."""
        self.ref = None

    def feed_event(self, frame: np.ndarray, t: float) -> str | None:
        """Returns None | hand_in | hand_out | settled_changed | settled_same."""
        cur = self._prep(frame)
        skin = self.skin_mask(frame)
        frac = float(skin.mean()) if skin is not None else 0.0
        if self.skin_base is None:
            self.skin_base = frac
        if self.prev is None:
            self.prev, self.still_since = cur, t
            return None
        delta = np.abs(cur - self.prev)
        diff = float(delta.mean())
        self.prev = cur
        blob = delta > 0.12
        hand_now = bool(
            (skin is not None and frac - self.skin_base > self.hand_skin and _touches_border(skin))
            or (float(blob.mean()) > self.hand_motion and _touches_border(blob)))
        if not hand_now:
            self.skin_base = min(frac, self.skin_base + 0.0005)    # slow-rising baseline, drops instantly
        ev = "hand_in" if hand_now and not self.hand else "hand_out" if self.hand and not hand_now else None
        self.hand = hand_now
        if hand_now or diff > self.motion_t:
            self.moving, self.still_since = True, None
            return ev
        if diff > self.still_t:           # small wobble: not yet still
            self.still_since = None
            return ev
        if self.still_since is None:
            self.still_since = t
        if t - self.still_since < self.stable_s or not (self.moving or self.armed_first):
            return ev
        self.moving, self.armed_first = False, False
        changed = self.ref is None or float(np.mean(np.abs(cur - self.ref))) > self.change_t
        if changed:
            self.ref = cur
            return "settled_changed"
        return "settled_same"

    def feed(self, frame: np.ndarray, t: float) -> bool:
        return self.feed_event(frame, t) == "settled_changed"


# ---------------------------------------------------------------- image helpers
def split_spread(img: np.ndarray) -> list[np.ndarray]:
    """Return [left, right] pages of a two-page spread (gutter found near the middle, else midline).
    A portrait image is treated as a single page."""
    h, w = img.shape[:2]
    if w < h * 1.15:
        return [img]
    g = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lo, hi = int(w * 0.42), int(w * 0.58)
    cols = cv2.GaussianBlur(g[:, lo:hi].astype(np.float32).mean(axis=0).reshape(1, -1), (1, 0), sigmaX=max(2, w // 200))[0]
    mid = w // 2
    if cols.std() > 4:   # a visible shadow line, otherwise plain midline
        mid = lo + int(np.argmin(cols))
    return [img[:, :mid], img[:, mid:]]


def assess_image(img: np.ndarray) -> str | None:
    """Return None if usable, else a problem code: blocked | dark | blurry."""
    g = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (320, int(320 * g.shape[0] / g.shape[1])))
    if g.mean() < 25 and g.std() < 12:
        return "blocked"
    if g.mean() < 55:
        return "dark"
    if cv2.Laplacian(g, cv2.CV_64F).var() < 20:
        return "blurry"
    return None


def encode_jpeg(img: np.ndarray, max_side: int = 1800, quality: int = 85) -> bytes:
    h, w = img.shape[:2]
    s = max_side / max(h, w)
    if s < 1:
        img = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("jpeg encode failed")
    return buf.tobytes()


# ---------------------------------------------------------------- camera backends
class Camera:
    def low_res(self) -> np.ndarray | None: ...
    def capture_still(self, full: bool = False) -> np.ndarray | None: ...   # full=True: full sensor resolution (small print)
    def close(self): ...


class OpenCVCamera(Camera):
    def __init__(self, index=0, low=(160, 120), still=(1920, 1080)):
        self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) if hasattr(cv2, "CAP_DSHOW") and __import__("sys").platform == "win32" else cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError("no webcam")
        self.low = low
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, still[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, still[1])

    def _grab(self):
        ok, f = self.cap.read()
        return f if ok else None

    def low_res(self):
        f = self._grab()
        return None if f is None else cv2.resize(f, self.low, interpolation=cv2.INTER_AREA)

    def capture_still(self, full: bool = False):
        for _ in range(3):      # flush stale buffer / let autofocus settle
            self._grab()
        return self._grab()

    def close(self):
        self.cap.release()


class PiCamera(Camera):
    """Picamera2 + IMX708 (Camera Module 3). Imported lazily; install via apt."""

    def __init__(self, low=(160, 120), still=(2304, 1296), full=(4608, 2592)):
        from picamera2 import Picamera2  # type: ignore
        from libcamera import controls  # type: ignore
        self.cam = Picamera2()
        self.low = tuple(low)
        self._controls = controls
        cfg = self.cam.create_still_configuration(main={"size": tuple(still)}, lores={"size": tuple(low)},
                                                  display=None, buffer_count=2)
        self.full_cfg = self.cam.create_still_configuration(main={"size": tuple(full)}, display=None, buffer_count=1)
        self.cam.configure(cfg)
        self.cam.start()
        self.cam.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfRange": controls.AfRangeEnum.Normal,
                               "AfSpeed": controls.AfSpeedEnum.Normal})

    def low_res(self):
        yuv = self.cam.capture_array("lores")    # YUV420 (h*3/2 rows): convert to colour for skin detection
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420) if yuv.ndim == 2 else yuv

    def capture_still(self, full: bool = False):
        try:
            self.cam.autofocus_cycle()   # one explicit AF sweep before the high-res still
        except Exception:
            pass
        if full:                         # small print: switch to the full 12 MP mode for one frame, then back
            return cv2.cvtColor(self.cam.switch_mode_and_capture_array(self.full_cfg, "main"), cv2.COLOR_RGB2BGR)
        return cv2.cvtColor(self.cam.capture_array("main"), cv2.COLOR_RGB2BGR)

    def close(self):
        self.cam.stop()
        self.cam.close()


SKIN_BGR = (110, 150, 225)


def draw_hand(img: np.ndarray) -> np.ndarray:
    """Skin-coloured 'hand + wrist' entering from the bottom edge and covering text."""
    out = img.copy()
    h, w = out.shape[:2]
    cv2.rectangle(out, (int(w * .30), int(h * .40)), (int(w * .65), h), SKIN_BGR, -1)
    return out


class ScriptedCamera(Camera):
    """Deterministic camera for mock mode, tests and the --fake-camera demo.

    `turn_to(i)` plays a short burst of motion then a stable scene. `simulate_turn()` / `simulate_back()` play a
    realistic flip: hand arrives over the old page, the page moves, hand lingers on the new page, hand leaves.
    `toggle_hand()` puts a steady hand in the frame. capture_still() renders the *current* scene, hand included,
    so the 'never capture a hand' guard is testable.
    """

    def __init__(self, pages: list[np.ndarray] | None = None, low=(160, 120), n_spreads: int = 6, desk_margin: int = 0):
        self.pages = pages or [synthetic_spread(i, desk_margin) for i in range(n_spreads)]
        self.full_calls = 0
        self.idx, self.low, self.blocked, self.hand = 0, low, False, False
        self._timeline: list[tuple[str, int]] = []
        self._state: tuple[str, int] = ("page", 0)

    def _render(self, tag: str, idx: int) -> np.ndarray:
        if self.blocked:
            return np.zeros((720, 1280, 3), np.uint8)
        base = self.pages[idx]
        if tag == "noise":
            return (np.random.default_rng(len(self._timeline)).random(base.shape) * 255).astype(np.uint8)
        return draw_hand(base) if tag == "hand" else base

    def _advance(self):
        if self._timeline:
            self._state = self._timeline.pop(0)
            self.idx = self._state[1]
        else:
            self._state = ("hand" if self.hand else "page", self.idx)

    def turn_to(self, idx: int):
        self.idx = idx % len(self.pages)
        self._state = ("page", self.idx)
        self._timeline = [("noise", self.idx)] * 4

    def simulate_turn(self, step: int = 1, hand_frames: int = 4):
        old, new = self.idx, (self.idx + step) % len(self.pages)
        self._timeline = [("hand", old)] * hand_frames + [("noise", new)] * 3 + [("hand", new)] * 3

    def simulate_back(self):
        self.simulate_turn(-1)

    def toggle_hand(self):
        self.hand = not self.hand

    def low_res(self):
        self._advance()
        return cv2.resize(self._render(*self._state), self.low, interpolation=cv2.INTER_AREA)

    def capture_still(self, full: bool = False):
        self.full_calls += int(full)
        tag, idx = self._state
        return self._render("hand" if self.hand and tag == "page" else tag, idx)

    def labels(self) -> list[tuple[str, str]]:
        """(phash, printed page label) for every half-page, so the mock vision model can 'read' page numbers.
        Spread i carries pages 2i+2 and 2i+3, as in a real book."""
        from .pages import phash
        from .pipeline import halves_from_still
        out = []
        for i, sp in enumerate(self.pages):
            for j, half in enumerate(halves_from_still(sp, {})[0]):
                out.append((phash(half), str(2 * i + 2 + j)))
        return out

    def close(self):
        pass


def synthetic_page(seed: int, size=(720, 640)) -> np.ndarray:
    """A white 'page' with seed-dependent text-like bars; sharp enough to pass assess_image."""
    rng = np.random.default_rng(seed + 1000)
    h, w = size
    img = np.full((h, w, 3), 235, np.uint8)
    for y in range(40, h - 40, 28):
        x = 30
        while x < w - 40:
            L = int(rng.integers(20, 90))
            cv2.rectangle(img, (x, y), (min(x + L, w - 30), y + 12), (30, 30, 30), -1)
            x += L + 10
    cv2.putText(img, f"P{seed}", (w // 2 - 30, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    return img


def synthetic_spread(seed: int, desk_margin: int = 0) -> np.ndarray:
    """Two synthetic pages. desk_margin > 0 puts the spread on a dark desk (page edges visible)."""
    left, right = synthetic_page(seed * 2), synthetic_page(seed * 2 + 1)
    spread = np.concatenate([left, right], axis=1)
    spread[:, left.shape[1] - 3: left.shape[1] + 3] = 90   # gutter shadow
    if desk_margin:
        spread = cv2.copyMakeBorder(spread, desk_margin, desk_margin, desk_margin, desk_margin, cv2.BORDER_CONSTANT, value=(25, 25, 25))
    return spread
