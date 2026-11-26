"""Seamless page flipping: hand handling, auto-continue, preload, back/skip, mid-sentence flips, keystone."""
import threading
import time

import cv2
import numpy as np
import pytest

from sensebook.audio import NullBackend, Player, page_turn_wav
from sensebook.camera import PageTurnDetector, ScriptedCamera, draw_hand, split_spread, synthetic_spread
from sensebook.pages import hamming, phash
from sensebook.perspective import find_page_quad, rectify_page
from sensebook.providers.mock import MockVision


def wait(pred, t=4.0):
    end = time.time() + t
    while time.time() < end:
        if pred():
            return True
        time.sleep(0.01)
    return False


@pytest.fixture(autouse=True)
def reset_registry():
    MockVision.registry = []
    yield
    MockVision.registry = []


@pytest.fixture
def fa(make_app):
    """App with the synthetic camera whose pages carry printed numbers (spread i = pages 2i+2, 2i+3)."""
    app = make_app()
    MockVision.registry = app.camera.labels()
    return app


def finished(app):
    return wait(lambda: not app._reading and app.read_idx >= len(app.spread.units))


def reader_texts(app):
    return [t for r, t in app.speech_log if r == "reader"]


def read_log(app):
    """Sentences actually played (from the app log; cached TTS is not re-synthesized so speech_log misses them)."""
    return [l[len("[reader] "):] for l in app.logs if l.startswith("[reader] ") and "end of spread" not in l]


def explainer_texts(app):
    return [t for r, t in app.speech_log if r == "explainer"]


# ---------------------------------------------------------------- 1. hand handling
def run_frames(det, cam, n, t0, dt=0.15):
    ev = []
    for k in range(n):
        ev.append((t0 + k * dt, det.feed_event(cam.low_res(), t0 + k * dt)))
    return ev


def test_hand_blocks_settling_and_same_page_does_not_recapture():
    cam, det = ScriptedCamera(), PageTurnDetector(stable_seconds=0.8)
    ev = run_frames(det, cam, 20, 0)
    assert [e for _, e in ev].count("settled_changed") == 1
    cam.toggle_hand()                                         # steady hand over the text
    ev = run_frames(det, cam, 60, 3.0)                        # 9 s of hand
    names = [e for _, e in ev if e]
    assert names[0] == "hand_in" and "settled_changed" not in names and "settled_same" not in names
    assert det.hand and det.hand_in_frame(cam.capture_still())
    cam.toggle_hand()                                         # hand leaves, page unchanged
    names = [e for _, e in run_frames(det, cam, 15, 12.0) if e]
    assert names == ["hand_out", "settled_same"]              # resume, but no re-capture


def test_simulated_flip_settles_once_and_never_with_hand_in_still():
    cam, det = ScriptedCamera(), PageTurnDetector(stable_seconds=0.8)
    run_frames(det, cam, 20, 0)
    cam.simulate_turn()
    events = []
    for k in range(40):
        t = 3.0 + k * 0.15
        e = det.feed_event(cam.low_res(), t)
        if e:
            events.append(e)
        if e == "settled_changed":
            assert not det.hand_in_frame(cam.capture_still())     # the page that gets captured has no hand
    assert events[0] == "hand_in" and events.count("settled_changed") == 1
    assert cam.idx == 1


def test_cream_paper_is_not_a_hand():
    cream = np.full((720, 1280, 3), (190, 222, 240), np.uint8)
    det = PageTurnDetector()
    assert not det.hand_in_frame(cream)
    for k in range(10):
        assert det.feed_event(cream, k * 0.15) != "hand_in"


def test_capture_guard_skips_hand_then_captures_when_clear(fa):
    MockVision.calls = 0
    fa.camera.toggle_hand()
    fa.on_page_settled()
    assert fa.spread is None and MockVision.calls == 0 and fa.detector.ref is None
    fa.camera.toggle_hand()
    fa.on_page_settled()
    assert fa.spread is not None and MockVision.calls == 2


def test_duck_and_unduck():
    seen = []

    class B(NullBackend):
        def write(self, pcm, rate):
            seen.append(int(np.abs(pcm).max()))
    from sensebook.audio import tone_wav
    p = Player(B(), volume=1.0)
    p.play(tone_wav(440, 0.2))
    full = max(seen)
    seen.clear()
    p.duck = 0.25
    p.play(tone_wav(440, 0.2))
    assert max(seen) < full * 0.3


def test_hand_action_duck_never_stops(fa):
    fa.flip["hand_action"] = "duck"
    fa.on_page_settled()
    fa._reading = True
    fa.handle("hand_in")
    assert fa.player.duck == fa.flip["duck_level"] and not fa._flip_hold
    fa.handle("scene_settled")
    assert fa.player.duck == 1.0
    fa._reading = False


# ---------------------------------------------------------------- 2. auto-continue + earcon
def test_auto_continue_across_page_turn_with_earcon_and_spoken_prompt(fa):
    fa.memory.set("accessibility_mode", "1")
    played = []
    orig = fa.player.play
    fa.player.play = lambda wav: (played.append(len(wav)), orig(wav))[1]
    fa.on_page_settled()
    fa.start_reading()
    assert finished(fa)
    assert len(page_turn_wav()) in played                                   # soft earcon at the end of the spread
    assert wait(lambda: "Turn the page." in explainer_texts(fa))           # accessibility mode
    first_heading_next = None
    fa.camera.turn_to(1)
    fa.on_page_settled()                                                    # no button press
    assert fa.spread.labels() == [4, 5]
    first_heading_next = fa.spread.units[0][2]
    assert wait(lambda: first_heading_next in reader_texts(fa))
    assert finished(fa)
    assert fa.read_mode


def test_no_auto_continue_after_user_pause(fa):
    fa.on_page_settled()
    fa.start_reading()
    assert finished(fa)
    fa.read_mode = False                                                    # user stopped
    n = len(reader_texts(fa))
    fa.camera.turn_to(1)
    fa.on_page_settled()
    time.sleep(0.2)
    assert len(reader_texts(fa)) == n and not fa._reading


# ---------------------------------------------------------------- 3. preload + latency metric
def test_predictive_preload_and_flip_latency(fa):
    fa.on_page_settled()
    fa.start_reading()
    assert finished(fa)
    fa.camera.turn_to(1)
    fa.on_page_settled()
    assert finished(fa)
    nxt_first = fa.spread.units[0][2]
    fa.camera.turn_to(0)                                                    # back: spread 1 is now "next"
    fa._tts_futs.clear()
    fa.speech_log.clear()
    fa.on_page_settled()
    assert wait(lambda: fa._tts_ready(nxt_first))                           # warmed while page N is being read
    assert reader_texts(fa).count(nxt_first) == 1                           # synthesized once, not twice
    assert finished(fa)
    n = len(fa.metrics["flip_to_audio"])
    fa.camera.turn_to(1)
    fa.on_page_settled(t_settle=time.monotonic())
    assert wait(lambda: len(fa.metrics["flip_to_audio"]) > n)
    m = fa.metrics["flip_to_audio"][-1]
    assert m["preloaded"] and m["seconds"] < 0.3, m
    assert reader_texts(fa).count(nxt_first) == 1                           # still no second cloud synthesis


# ---------------------------------------------------------------- 4. back-flip and skip
def test_back_flip_announces_and_resumes_at_last_sentence_and_skip_announces(fa):
    fa.on_page_settled()
    fa.start_reading()
    assert finished(fa)
    fa.camera.turn_to(1)
    fa.on_page_settled()
    assert finished(fa)
    fa.camera.turn_to(0)
    fa.on_page_settled()                                                    # back-flip
    assert "Back to page 2." in explainer_texts(fa)
    last = len(fa.spread.units) - 1
    assert fa.read_idx >= last or fa.positions[fa.history[-1]] == last      # last read sentence
    assert wait(lambda: fa.spread.units[last][2] in read_log(fa)[-3:])
    assert finished(fa)
    fa.camera.turn_to(3)                                                    # skipped ahead: pages 8-9
    fa.on_page_settled()
    assert "Page 8." in explainer_texts(fa)


# ---------------------------------------------------------------- 5. mid-sentence flip
@pytest.fixture
def slow(make_app):
    app = make_app()
    app.player.backend = NullBackend(realtime=True)
    MockVision.registry = app.camera.labels()
    return app


def test_mid_sentence_hand_holds_then_same_page_resumes(slow):
    app = slow
    app.on_page_settled()
    app.start_reading()
    assert wait(lambda: app.player.playing)
    app.handle("hand_in")
    assert app._flip_hold
    assert wait(lambda: not app.player.playing)
    i = app.read_idx
    time.sleep(0.4)
    assert app.read_idx == i and app._reading                               # held, position remembered
    app.handle("scene_settled")
    assert wait(lambda: app.read_idx > i)                                   # replays the sentence, moves on


def test_word_stop_mode_fades_quickly(slow):
    slow.flip["stop_mode"] = "word"
    slow.on_page_settled()
    slow.start_reading()
    assert wait(lambda: slow.player.playing)
    t = time.monotonic()
    slow.handle("hand_in")
    assert wait(lambda: not slow.player.playing, 1.0) and time.monotonic() - t < 0.8


def test_flip_mid_sentence_then_back_returns_to_unfinished_sentence(slow):
    app = slow
    app.flip["auto_continue"] = False
    app.on_page_settled()
    key0 = app.spread.key
    app.start_reading()
    assert wait(lambda: app.read_idx >= 2 and app.player.playing)
    app.handle("hand_in")
    assert wait(lambda: not app.player.playing)
    interrupted = app.read_idx
    app.camera.turn_to(1)
    app.on_page_settled()
    assert app.positions[key0] == interrupted and app.read_idx == 0
    app.stop_all()
    app.jump(-1)                                                            # Back at the top of the new spread
    assert app.spread.key == key0
    assert wait(lambda: app.spread.units[interrupted][2] in read_log(app)[-2:])


# ---------------------------------------------------------------- 6. perspective
def warp(spread, quad_dst, size=(1280, 960)):
    h, w = spread.shape[:2]
    src = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    M = cv2.getPerspectiveTransform(src, np.array(quad_dst, np.float32))
    return cv2.warpPerspective(spread, M, size, borderValue=(25, 25, 25)), M


QUAD = [[300, 130], [980, 130], [1150, 840], [130, 840]]       # keystoned: far (top) edge shorter


def test_find_quad_and_rectify_matches_straight_view():
    sp = synthetic_spread(0)
    tilted, _ = warp(sp, QUAD)
    q = find_page_quad(tilted)
    assert q is not None and np.abs(q - np.array(QUAD)).max() < 15
    rect, how = rectify_page(tilted, {"rectify": True, "spread_aspect": 1280 / 720})
    assert how == "quad"
    left_t, right_t = split_spread(rect)
    left_o, right_o = split_spread(sp)
    assert hamming(phash(left_t), phash(left_o)) <= 14 and hamming(phash(right_t), phash(right_o)) <= 14
    assert hamming(phash(left_t), phash(right_o)) > 14                      # still distinguishes pages


def test_fixed_homography_fallback_and_full_frame_passthrough():
    sp = synthetic_spread(1)
    flat = np.full((600, 800, 3), 120, np.uint8)                            # no page quad to find
    H = [1, 0, 10, 0, 1, 5, 0, 0, 1]
    out, how = rectify_page(flat, {"homography": H})
    assert how == "fixed" and out.shape == flat.shape
    out, how = rectify_page(sp, {})
    assert how == "none" and out is sp


def test_app_pipeline_handles_tilted_view(make_app):
    app = make_app()
    app.camera.pages[0] = warp(synthetic_spread(0), QUAD)[0]
    app.cfg["camera"]["spread_aspect"] = 1280 / 720
    app.on_page_settled()
    assert app.spread is not None and len(app.spread.pages) == 2


# ---------------------------------------------------------------- full loop: hand, flip, auto-continue, latency
def test_full_camera_loop_flip_to_audio(make_app):
    app = make_app()
    app.cfg["camera"].update(fps=40)
    app.detector.stable_s = 0.35
    MockVision.registry = app.camera.labels()
    MockVision.calls = 0
    th = threading.Thread(target=app.run, daemon=True)
    th.start()
    assert wait(lambda: app.spread is not None, 6)
    app.hw.events.put("read_page")
    assert wait(lambda: app.read_mode and app.read_idx >= len(app.spread.units) and not app._reading, 6)
    calls = MockVision.calls
    app.hw.events.put("sim_turn")                                           # hand, flip, hand, hand leaves
    assert wait(lambda: app.metrics["flip_to_audio"], 8)
    m = app.metrics["flip_to_audio"][-1]
    print(f"\nFLIP-TO-AUDIO (mock, full camera loop): {m}")
    assert app.spread.labels() == [4, 5] and MockVision.calls == calls + 2   # exactly one capture of the new spread
    assert m["seconds"] < 0.5
    app.hw.events.put("quit")
    th.join(3)
