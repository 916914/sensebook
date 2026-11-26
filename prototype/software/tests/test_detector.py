import numpy as np

from sensebook.camera import PageTurnDetector, assess_image, split_spread, synthetic_page, synthetic_spread


def frames_still(img, n, t0, dt=0.15):
    return [(img, t0 + i * dt) for i in range(n)]


def run(det, seq):
    return [det.feed(f, t) for f, t in seq]


def noise(seed):
    return (np.random.default_rng(seed).random((120, 160, 3)) * 255).astype(np.uint8)


def test_first_stable_scene_is_captured_once():
    det = PageTurnDetector()
    a = synthetic_spread(0)
    out = run(det, frames_still(a, 20, 0))
    assert out.count(True) == 1


def test_page_turn_motion_then_stability_fires_once_after_about_1s():
    det = PageTurnDetector()
    a, b = synthetic_spread(0), synthetic_spread(1)
    run(det, frames_still(a, 15, 0))
    t = 3.0
    seq = [(noise(i), t + i * 0.15) for i in range(4)]           # motion
    seq += frames_still(b, 15, t + 0.6)                           # new page, still
    out = run(det, seq)
    assert out.count(True) == 1
    fire_time = seq[out.index(True)][1]
    assert 1.0 <= fire_time - (t + 0.6) <= 1.5                    # ~1 s of stability first


def test_hand_wave_over_same_page_does_not_refire():
    det = PageTurnDetector()
    a = synthetic_spread(0)
    run(det, frames_still(a, 15, 0))
    seq = [(noise(i), 3 + i * 0.15) for i in range(3)] + frames_still(a, 15, 3.5)
    assert not any(run(det, seq))


def test_continuous_motion_never_fires():
    det = PageTurnDetector()
    assert not any(run(det, [(noise(i), i * 0.15) for i in range(40)]))


def test_split_and_quality():
    s = synthetic_spread(2)
    parts = split_spread(s)
    assert len(parts) == 2 and abs(parts[0].shape[1] - s.shape[1] // 2) < 40
    assert len(split_spread(synthetic_page(1))) == 1               # portrait = single page
    assert assess_image(s) is None
    assert assess_image(np.zeros((300, 400, 3), np.uint8)) == "blocked"
    assert assess_image(np.full((300, 400, 3), 100, np.uint8)) == "blurry"
