"""Config loading: defaults <- config.yaml <- env (.env). Model IDs and voices live here, not in code."""
from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import yaml

DEFAULTS: dict[str, Any] = {
    "timezone": "Asia/Dhaka",
    "data_dir": "data",
    "language": "bn",
    "voice_speed": 1.0,
    "gemini": {
        "text_model": "gemini-3.5-flash-lite",
        "tts_model": "gemini-3.8-flash-tts",
        "tts_api": "interactions",
        "voices": {
            "reader": "Kore",
            "explainer": "Puck",
            "host_learner": "Leda",
            "host_teacher": "Charon",
        },
        "tts_sample_rate": 24000,
    },
    "camera": {
        "device_index": 0,
        "low_res": [160, 120],
        "still_res": [2304, 1296],         # normal capture; small print uses full_res
        "motion_threshold": 0.035,
        "still_threshold": 0.012,
        "stable_seconds": 0.8,           # page must be still this long (0.6-1.0) before capture
        "hand_skin_fraction": 0.04,      # extra skin-tone area (vs baseline) entering from an edge = hand
        "hand_motion_fraction": 0.2,     # or a motion blob this large touching an edge
        "rectify": True,                 # keystone-correct using the detected page quadrilateral
        "homography": None,              # fallback fixed 3x3 (row-major list of 9) calibrated for the stand
        "spread_aspect": None,           # optional spread width/height (e.g. 1.4) to undo foreshortening
        "quad_min_area": 0.25,
        # Lens model for the M12 ultra-wide (~120 deg) lens. model: none | standard | fisheye. K = 3x3 (list of 9),
        # D = distortion coefficients (4 for fisheye, 4/5/8 for standard), size = [w, h] used when calibrating.
        # Written by scripts/calibrate_camera.py. balance 0..1: 0 crops to valid pixels, 1 keeps the whole view.
        "lens": {"model": "none", "K": None, "D": None, "size": None, "balance": 0.3},
        "full_res": [4608, 2592],
        "small_print_wait_s": 20.0,      # after "pull the stick up": wait this long for the view to change, then ask for Play        # small-print capture
        "attach_checks": True,           # guidance messages after the stand is attached to a book
        "change_threshold": 0.01,
        "fps": 6,
    },
    "flip": {
        "hand_action": "stop",       # stop | duck | none: what to do to speech when a hand enters the frame
        "stop_mode": "immediate",    # immediate | word (fade-out ~0.25 s; TTS has no word timings)
        "duck_level": 0.25,
        "auto_continue": True,       # keep reading onto the new spread after a flip
        "earcon": True,
        "spoken_prompt": False,      # say "turn the page" (also on when the web app's accessibility mode is on)
        "preload": {"enabled": True, "sentences": 3},
    },
    "pages": {"phash_max_distance": 6, "min_confidence": 0.55},
    "audio": {
        "output": "speaker",
        "private_mode": True,
        "hat": "i2s",                    # i2s (final: I2S mics + MAX98357A + I2S headphone DAC) | wm8960 (legacy dev kit)
        "alsa_device": "default",        # playback PCM (see docs/AUDIO.md); legacy: plughw:wm8960soundcard
        "alsa_capture_device": "mic_in", # capture PCM; legacy: plughw:wm8960soundcard
        "amp_enable_owner": "app",       # app: SenseBook alone drives GPIO 25 | driver: kernel/overlay owns it, app never touches it
        "amp_idle_seconds": 3.0,         # amp SD goes low this long after the last sound
        "bluetooth_sink": "",
        "mixer_card": "wm8960soundcard",
        "record_seconds_max": 30,
        "sample_rate": 16000,
    },
    "battery": {"gauge": "auto", "warn_levels": [20, 10], "poll_seconds": 60},   # auto | none (MAX17048 over I2C)
    "hardware": {"hold_seconds": 0.8, "jack_active_low": True, "hub_active_low": True, "speed_step": 0.1},
    "discussion": {"minutes": 4, "segment_lines": 6},
    "webapp": {"host": "127.0.0.1", "port": 8080},   # device mode overrides host to 0.0.0.0 (LAN, PIN-protected)
    "storage": {"keep_captures": False},            # page images / audio are NOT kept unless enabled; local only
}

# FINAL BCM pin map (founder-approved hardware). Shared with the hardware team: do not change without them.
PINS = {
    "ask": 5, "play_pause": 6, "back": 13, "forward": 26,
    "vol_up": 23, "vol_down": 24,            # buttons; hold = reading speed
    "mic_mute": 16,                          # switch, active low = muted
    "dot_ready": 17, "dot_listening": 27, "dot_sending": 22, "dot_warn": 4,   # status dots (battery/warn on 4)
    "light": 12,                             # light ring, PWM
    "amp_enable": 25,                        # MAX98357A SD: low = off (headphones in / idle)
    "jack_detect": 7,                        # headphone jack switch
    "haptic": 11,                            # vibration motor
    "hub_attached": 8,                       # hub sensor: low = clamped on a book
}
I2S_PINS = {"bclk": 18, "lrclk": 19, "din": 20, "dout": 21}   # mics in on 20, amp + headphone DAC out on 21
I2C_PINS = {"sda": 2, "scl": 3}                               # optional MAX17048 fuel gauge (address 0x36)
RESERVED_PINS = set(I2S_PINS.values()) | set(I2C_PINS.values())
assert len(set(PINS.values())) == len(PINS) and not set(PINS.values()) & RESERVED_PINS


def _merge(base: dict, over: dict) -> dict:
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge(base[k], v)
        else:
            base[k] = v
    return base


def load_config(path: str | os.PathLike | None = None, overrides: dict | None = None) -> dict:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:  # dotenv optional
        pass
    cfg = copy.deepcopy(DEFAULTS)
    p = Path(path) if path else Path("config.yaml")
    if p.exists():
        _merge(cfg, yaml.safe_load(p.read_text(encoding="utf-8")) or {})
    _merge(cfg, overrides or {})
    Path(cfg["data_dir"]).mkdir(parents=True, exist_ok=True)
    return cfg
