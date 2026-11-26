"""Final hardware: pin map, lens undistortion, jack detect + amp enable, hub attach/detach guidance, battery,
volume/speed buttons, small-print capture."""
import time

import cv2
import numpy as np
import pytest

from sensebook.battery import BatteryMonitor, FakeGauge, MAX17048Gauge
from sensebook.camera import ScriptedCamera
from sensebook.config import I2C_PINS, I2S_PINS, PINS, RESERVED_PINS, load_config
from sensebook.lens import Undistorter
from sensebook.providers.mock import MockVision
from sensebook.audio import NullBackend


def wait(pred, t=3.0):
    end = time.time() + t
    while time.time() < end:
        if pred():
            return True
        time.sleep(0.01)
    return False


def said(app):
    return [t for r, t in app.speech_log if r == "explainer"]


@pytest.fixture(autouse=True)
def reset_mock():
    MockVision.registry, MockVision.upside_down = [], False
    yield
    MockVision.registry, MockVision.upside_down = [], False


# ---------------------------------------------------------------- pin map / config
def test_final_pin_map_and_reserved_lines():
    assert PINS == {"ask": 5, "play_pause": 6, "back": 13, "forward": 26, "vol_up": 23, "vol_down": 24, "mic_mute": 16,
                    "dot_ready": 17, "dot_listening": 27, "dot_sending": 22, "dot_warn": 4, "light": 12,
                    "amp_enable": 25, "jack_detect": 7, "haptic": 11, "hub_attached": 8}
    assert I2S_PINS == {"bclk": 18, "lrclk": 19, "din": 20, "dout": 21} and I2C_PINS == {"sda": 2, "scl": 3}
    assert not set(PINS.values()) & RESERVED_PINS and len(set(PINS.values())) == len(PINS)
    assert not {"enc_a", "enc_b", "enc_push", "ask_remote"} & set(PINS)       # old encoder / remote removed


def test_config_defaults_and_example_load(tmp_path):
    cfg = load_config("nonexistent.yaml", {"data_dir": str(tmp_path)})
    assert cfg["webapp"]["host"] == "127.0.0.1" and cfg["camera"]["lens"]["model"] == "none"
    assert cfg["battery"]["warn_levels"] == [20, 10] and cfg["audio"]["hat"] == "i2s"
    ex = load_config("config.example.yaml", {"data_dir": str(tmp_path)})
    assert ex["camera"]["lens"]["model"] == "none" and ex["flip"]["preload"]["enabled"] and ex["camera"]["full_res"][0] == 4608
    cfg = load_config("nonexistent.yaml", {"data_dir": str(tmp_path), "camera": {"lens": {"model": "fisheye", "K": [1] * 9}}})
    assert cfg["camera"]["lens"]["model"] == "fisheye" and cfg["camera"]["lens"]["balance"] == 0.3     # merged, not replaced


# ---------------------------------------------------------------- undistortion
def fisheye_distort(pix, K, D):
    f, c = K[0], np.array([K[2], K[5]])
    n = (pix - c) / f
    r = np.linalg.norm(n, axis=1, keepdims=True)
    th = np.arctan(r)
    td = th * (1 + D[0] * th ** 2 + D[1] * th ** 4 + D[2] * th ** 6 + D[3] * th ** 8)
    return n * np.where(r > 1e-9, td / np.maximum(r, 1e-9), 1) * f + c


def standard_distort(pix, K, D):
    f, c = K[0], np.array([K[2], K[5]])
    n = (pix - c) / f
    r2 = (n ** 2).sum(1, keepdims=True)
    return n * (1 + D[0] * r2 + D[1] * r2 ** 2) * f + c


W, H = 1280, 720
K = [500.0, 0, 640, 0, 500.0, 360, 0, 0, 1]


@pytest.mark.parametrize("model,D,fn", [("fisheye", [0.2, -0.05, 0.0, 0.0], fisheye_distort),
                                        ("standard", [-0.3, 0.1, 0, 0, 0], standard_distort)])
def test_undistort_straightens_a_distorted_grid_line(model, D, fn):
    u = Undistorter({"model": model, "K": K, "D": D, "size": [W, H], "balance": 0.3})
    xs = np.linspace(120, 1160, 900)
    ideal = np.stack([xs, np.full_like(xs, 140.0)], 1)          # a straight world line, far from the centre
    dist = fn(ideal, K, D)
    assert dist[:, 1].std() > 3.0                                # clearly curved before
    out = u.map_points(dist, (W, H))
    assert out[:, 1].std() < 0.05                                # point-level: straight again
    img = np.full((H, W, 3), 255, np.uint8)
    cv2.polylines(img, [dist.astype(np.int32).reshape(-1, 1, 2)], False, (0, 0, 0), 3)
    res = u.undistort(img)
    ys = []
    for x in range(300, 1000, 20):                               # image-level: dark pixels near the expected row
        col = res[:, x, 0]
        band = np.where(col[int(out[:, 1].mean()) - 25:int(out[:, 1].mean()) + 25] < 128)[0]
        if band.size:
            ys.append(band.mean())
    assert len(ys) > 20 and np.std(ys) < 1.5


def test_undistort_scales_k_for_other_resolution_and_is_noop_when_unconfigured():
    img = np.random.default_rng(0).integers(0, 255, (360, 640, 3), dtype=np.uint8)
    assert Undistorter(None).undistort(img) is img
    u = Undistorter({"model": "fisheye", "K": K, "D": [0.2, -0.05, 0, 0], "size": [W, H]})
    out = u.undistort(img)                                       # half-size frame: K rescaled, no crash
    assert out.shape == img.shape and (out != img).any()


# ---------------------------------------------------------------- jack detect + amp enable
def test_jack_detect_switches_to_headphones_and_amp_follows(make_app):
    app = make_app(camera=False)
    app.cfg["audio"]["amp_idle_seconds"] = 0.0
    app.say("hello", "explainer", chime=False)
    assert app.hw.amp_on                                         # speaker mode: amp woken before sound
    app.hw.jack_in = True
    app.handle("headphones_in")
    assert app.router.effective_output() == "headphones" and not app.hw.amp_on and "Headphones." in said(app)
    app.say("private", "explainer", chime=False)
    assert not app.hw.amp_on                                     # never wakes the speaker amp while headphones are in
    app.handle("headphones_out")
    assert app.router.effective_output() == "speaker" and "Speaker." in said(app) and app.hw.amp_on
    time.sleep(0.05)
    app.amp_tick()
    assert not app.hw.amp_on                                     # idle: SD low to save power


# ---------------------------------------------------------------- hub attach / detach and guidance
def margin_app(make_app, margin=40):
    app = make_app()
    app.camera = ScriptedCamera(desk_margin=margin)
    MockVision.registry = app.camera.labels()
    return app


def test_attach_buzz_then_ready_pages_message(make_app):
    app = margin_app(make_app)
    app.handle("attached")
    assert "Attached." in said(app) and "attached" in app.hw.haptics and app.attach_pending
    app.on_page_settled()
    assert "Ready, I can see pages 2 and 3. Press play to listen." in said(app)
    assert not app.attach_pending and not app._reading


def test_attach_edge_not_visible_and_upside_down(make_app):
    app = margin_app(make_app, margin=0)                         # page fills the frame: edges cut off
    app.handle("attached")
    app.on_page_settled()
    assert "Page edge not visible, move the book a little away." in said(app)
    assert app.spread is None and app.attach_pending and "error" in app.hw.haptics
    app2 = margin_app(make_app)
    app2.handle("attached")
    MockVision.upside_down = True
    app2.on_page_settled()
    assert "Book upside down." in said(app2) and app2.spread is None and app2.cache.library() == []
    MockVision.upside_down = False
    app2.on_page_settled()
    assert "Ready, I can see pages 2 and 3. Press play to listen." in said(app2)


def test_detach_during_reading_pauses_and_speaks_idle_detach_is_silent(make_app):
    app = margin_app(make_app)
    app.player.backend = NullBackend(realtime=True)
    app.on_page_settled()
    app.start_reading()
    assert wait(lambda: app.player.playing)
    app.handle("detached")
    assert not app._reading and not app.read_mode and "Detached." in said(app)
    idx = app.read_idx
    time.sleep(0.2)
    assert app.read_idx == idx                                   # paused, position kept
    app2 = margin_app(make_app)
    app2.handle("detached")
    assert "Detached." not in said(app2)


# ---------------------------------------------------------------- battery
def test_battery_announcements_once_per_threshold_and_where_am_i(make_app):
    g = FakeGauge(50)
    got = []
    mon = BatteryMonitor(g, [20, 10], lambda pct, lv: got.append((round(pct), lv)))
    for lvl in (50, 25, 19, 18, 12, 9, 8, 30, 19):
        g.level = lvl
        mon.poll()
    assert got == [(19, 20), (9, 10), (19, 20)]                  # once per crossing, re-armed after recovering >25
    g.level = None
    assert mon.poll() is None

    app = margin_app(make_app)
    app.gauge = app.battery.gauge = FakeGauge(80)
    app.on_page_settled()
    app.handle("where_am_i")
    assert any(t.startswith("Pages 2 and 3, sentence 1 of") and t.endswith("Battery 80 percent.") for t in said(app))
    app.battery.gauge.level = 19
    app.poll_battery(force=True)
    assert "Battery low, 19 percent. Please charge soon." in said(app) and app.hw.dots["warn"]
    app.poll_battery(force=True)
    assert said(app).count("Battery low, 19 percent. Please charge soon.") == 1


def test_max17048_register_decoding():
    class Bus:
        def read_word_data(self, addr, reg):
            assert (addr, reg) == (0x36, 0x04)
            return 0x804C                                        # bytes 4C 80 -> 76 + 128/256 %
    g = MAX17048Gauge.__new__(MAX17048Gauge)
    g.bus = Bus()
    assert g.percent() == 76.5


# ---------------------------------------------------------------- volume / speed
def test_volume_buttons_and_speed_steps(make_app):
    app = make_app(camera=False)
    v0 = app.player.volume
    app.handle("vol_down")
    app.handle("vol_down")
    assert app.player.volume == pytest.approx(v0 - 0.2)
    for _ in range(20):
        app.handle("vol_up")
    assert app.player.volume == 1.0
    for _ in range(20):
        app.handle("vol_down")
    assert app.player.volume == pytest.approx(0.1)
    assert app.speed == 1.0
    app.handle("speed_up")
    assert app.speed == pytest.approx(1.1)
    for _ in range(20):
        app.handle("speed_up")
    assert app.speed == 1.4
    for _ in range(20):
        app.handle("speed_down")
    assert app.speed == 0.7


# ---------------------------------------------------------------- small print
def small_print_app(make_app):
    app = make_app()
    app.camera = ScriptedCamera()
    real = app.vision.read_page
    calls = []

    def flaky(jpeg, lang):
        calls.append(1)
        pc = real(jpeg, lang)
        if len(calls) <= 1:
            pc.confidence = 0.2                                  # unreadable at normal resolution
        return pc
    app.vision.read_page = flaky
    return app


def test_small_print_waits_for_scene_change_then_captures_full_res(make_app):
    app = small_print_app(make_app)
    app.on_page_settled()
    assert "For small print, pull the stick up." in said(app)
    assert app.camera.full_calls == 0 and app.spread is None     # NOT an immediate re-capture
    assert app._sp_state == "wait_scene" and app.detector.ref is None
    app.small_print_tick()                                       # well inside the 20 s window: no Play prompt yet
    assert "Press play when the stick is up." not in said(app)
    app.camera.turn_to(1)                                        # the stick extends: view changes, then settles
    det, ev = app.detector, []
    for k in range(40):
        e = det.feed_event(app.camera.low_res(), 100 + k * 0.15)
        if e:
            ev.append(e)
    assert "settled_changed" in ev                               # the existing detector sees the change + settle
    app.on_page_settled()                                        # what the page_settled event triggers
    assert app.camera.full_calls == 1 and app.spread is not None and app._sp_state is None
    assert not app._full_res                                     # back to normal capture after a good read
    n = app.camera.full_calls
    app.camera.turn_to(2)
    app.on_page_settled()
    assert app.camera.full_calls == n


def test_small_print_no_change_asks_for_play_then_captures_full_res(make_app):
    app = small_print_app(make_app)
    app.cfg["camera"]["small_print_wait_s"] = 0.0
    app.on_page_settled()
    assert app.camera.full_calls == 0
    app.small_print_tick()
    assert "Press play when the stick is up." in said(app) and app._sp_state == "wait_play"
    assert app.camera.full_calls == 0                            # still waiting for the button
    app.handle("play_pause")
    assert wait(lambda: app.camera.full_calls == 1) and wait(lambda: app.spread is not None)
    assert said(app).count("Press play when the stick is up.") == 1


def test_amp_enable_owner_app_vs_driver():
    pytest.importorskip("gpiozero")
    from gpiozero.pins.mock import MockFactory, MockPWMPin
    from sensebook.hardware import DeviceHardware
    f = MockFactory(pin_class=MockPWMPin)
    hw = DeviceHardware(log=lambda *a: None, pin_factory=f)               # default owner: app
    hw.set_amp(True)
    assert f.pin(PINS["amp_enable"]).function == "output" and f.pin(PINS["amp_enable"]).state == 1
    hw.close()
    f2 = MockFactory(pin_class=MockPWMPin)
    hw2 = DeviceHardware(log=lambda *a: None, pin_factory=f2, amp_owner="driver")
    hw2.set_amp(True)                                                      # tracked in software only
    assert hw2.amp_on and f2.pin(PINS["amp_enable"]).function == "input"   # the app never claimed GPIO 25
    assert f2.pin(PINS["mic_mute"]).function == "input"
    hw2.close()
    assert load_config("nonexistent.yaml")["audio"]["amp_enable_owner"] == "app"


# ---------------------------------------------------------------- real gpiozero logic on mock pins
gz = pytest.importorskip("gpiozero")


@pytest.fixture
def dev():
    from gpiozero.pins.mock import MockFactory, MockPWMPin
    from sensebook.hardware import DeviceHardware
    f = MockFactory(pin_class=MockPWMPin)
    hw = DeviceHardware(log=lambda *a: None, pin_factory=f, hold_seconds=0.15)
    yield hw, f
    hw.close()


def drain(hw):
    out = []
    while not hw.events.empty():
        out.append(hw.events.get_nowait())
    return out


def press(f, pin, hold=0.0):
    f.pin(pin).drive_low()
    time.sleep(hold)
    f.pin(pin).drive_high()
    time.sleep(0.08)


def test_device_buttons_press_vs_hold(dev):
    hw, f = dev
    time.sleep(0.05)
    drain(hw)
    press(f, PINS["vol_up"])
    press(f, PINS["vol_down"])
    press(f, PINS["play_pause"])
    press(f, PINS["back"])
    press(f, PINS["forward"])
    assert drain(hw) == ["vol_up", "vol_down", "play_pause", "back", "forward"]
    press(f, PINS["vol_up"], hold=0.5)                           # hold Vol+ = faster reading speed (repeats), no volume step
    ev = drain(hw)
    assert ev and set(ev) == {"speed_up"}
    press(f, PINS["vol_down"], hold=0.3)
    assert "speed_down" in drain(hw)
    press(f, PINS["play_pause"], hold=0.3)                       # hold Play/Pause = where am I (not a toggle)
    assert drain(hw) == ["where_am_i"]
    press(f, PINS["back"], hold=0.3)
    assert drain(hw) == ["repeat"]
    f.pin(PINS["ask"]).drive_low()
    time.sleep(0.08)
    f.pin(PINS["ask"]).drive_high()
    time.sleep(0.08)
    assert drain(hw) == ["ask_down", "ask_up"]


def test_device_jack_hub_mute_and_outputs(dev):
    hw, f = dev
    time.sleep(0.05)
    drain(hw)
    assert hw.hub_attached is False and hw.jack_in is False
    f.pin(PINS["jack_detect"]).drive_low()
    f.pin(PINS["hub_attached"]).drive_low()
    f.pin(PINS["mic_mute"]).drive_low()
    time.sleep(0.15)
    assert set(drain(hw)) == {"headphones_in", "attached", "mic_mute_on"} and hw.mic_muted and hw.jack_in and hw.hub_attached
    f.pin(PINS["hub_attached"]).drive_high()
    time.sleep(0.15)
    assert drain(hw) == ["detached"]
    hw.set_amp(True)
    hw.set_dot("ready", True)
    hw.set_light(0.5)
    assert f.pin(PINS["amp_enable"]).state == 1 and f.pin(PINS["dot_ready"]).state == 1
    assert f.pin(PINS["light"]).state == pytest.approx(0.5)
    hw.set_amp(False)
    assert f.pin(PINS["amp_enable"]).state == 0
    with hw.cloud_activity():
        assert f.pin(PINS["dot_sending"]).state == 1
    assert f.pin(PINS["dot_sending"]).state == 0


def test_calibrate_returns_config_block_on_synthetic_chessboards():
    from sensebook.lens import calibrate
    sq = 40
    board = np.full((7 * sq + 80, 10 * sq + 80), 255, np.uint8)
    for r in range(7):
        for c in range(10):
            if (r + c) % 2 == 0:
                board[40 + r * sq:40 + (r + 1) * sq, 40 + c * sq:40 + (c + 1) * sq] = 0
    h, w = board.shape
    rng = np.random.default_rng(1)
    imgs = []
    for _ in range(12):
        dst = np.float32([[300, 200], [900, 200], [900, 560], [300, 560]]) + rng.uniform(-60, 60, (4, 2)).astype(np.float32)
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), dst)
        imgs.append(cv2.warpPerspective(board, M, (1280, 720), borderValue=255))
    blk = calibrate(imgs, (9, 6), 25.0, "standard")
    assert blk["model"] == "standard" and len(blk["K"]) == 9 and blk["size"] == [1280, 720] and blk["views"] == 12
    with pytest.raises(ValueError):
        calibrate(imgs[:3], (9, 6), 25.0)
