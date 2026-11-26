"""python -m sensebook --mode dev|device --provider gemini|mock"""
from __future__ import annotations

import argparse
import sys
import threading


def build(args):
    from .app import SenseBookApp
    from .audio import (AplayBackend, ArecordRecorder, NullBackend, OfflineSpeech, Player, ScriptedRecorder,
                        SoundDeviceBackend, SoundDeviceRecorder)
    from .camera import OpenCVCamera, PiCamera, ScriptedCamera
    from .battery import FakeGauge, make_gauge
    from .config import load_config
    from .hardware import DeviceHardware, KeyboardHardware, NullHardware
    from .providers import make_providers

    cfg = load_config(args.config)
    vision, tutor, speech = make_providers(args.provider, cfg)
    cam_cfg, a_cfg = cfg["camera"], cfg["audio"]
    camera = None
    if not args.no_camera:
        try:
            if args.mode == "device":
                camera = PiCamera(tuple(cam_cfg["low_res"]), tuple(cam_cfg["still_res"]), tuple(cam_cfg["full_res"]))
            elif args.provider == "mock" and args.fake_camera:
                camera = ScriptedCamera(desk_margin=40)
                from .providers.mock import MockVision
                MockVision.registry = camera.labels()      # synthetic pages carry printed page numbers
            else:
                camera = OpenCVCamera(cam_cfg["device_index"], tuple(cam_cfg["low_res"]))
        except Exception as e:
            print(f"[camera] unavailable ({e}); continuing without page following. "
                  "Use --fake-camera with --provider mock for a synthetic one.")
    if args.mode == "device":
        h = cfg["hardware"]
        hw = DeviceHardware(hold_seconds=h["hold_seconds"], jack_active_low=h["jack_active_low"],
                            hub_active_low=h["hub_active_low"], amp_owner=a_cfg["amp_enable_owner"])
        player = Player(AplayBackend(a_cfg["alsa_device"]))
        recorder = ArecordRecorder(a_cfg["alsa_capture_device"], a_cfg["sample_rate"], a_cfg["record_seconds_max"])
        gauge = make_gauge(cfg["battery"])
    else:
        hw = KeyboardHardware()
        gauge = hw.gauge = FakeGauge(80.0)          # `bat 18` on the console simulates a low battery
        if args.silent:
            player = Player(NullBackend())
        else:
            try:
                player = Player(SoundDeviceBackend())
            except Exception as e:
                print(f"[audio] no output device ({e}); playing silently")
                player = Player(NullBackend())
        try:
            if args.provider == "mock":
                raise RuntimeError("mock provider cannot hear audio: use `say <text>`")
            recorder = SoundDeviceRecorder(a_cfg["sample_rate"], a_cfg["record_seconds_max"])
        except Exception as e:
            print(f"[mic] {e}")
            recorder = ScriptedRecorder()
    app = SenseBookApp(cfg, vision, tutor, speech, camera, hw, recorder, player, offline=OfflineSpeech(), gauge=gauge)
    if args.mode == "device" and hw.hub_attached:
        app.attach_pending = True                    # booted on a book: give the framing guidance once
    return app, cfg


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    p = argparse.ArgumentParser(prog="sensebook")
    p.add_argument("--mode", choices=["dev", "device"], default="dev")
    p.add_argument("--provider", choices=["gemini", "mock"], default="mock")
    p.add_argument("--config", default=None)
    p.add_argument("--no-camera", action="store_true")
    p.add_argument("--fake-camera", action="store_true", help="mock provider only: synthetic page-turning camera")
    p.add_argument("--silent", action="store_true", help="do not open an audio device")
    p.add_argument("--no-web", action="store_true")
    p.add_argument("--purge-captures", action="store_true", help="delete saved page images/audio and exit")
    args = p.parse_args(argv)
    if args.purge_captures:
        from .config import load_config
        from .captures import CaptureStore
        n = CaptureStore(load_config(args.config)).purge()
        print(f"purged {n} capture file(s)")
        return
    app, cfg = build(args)
    if not args.no_web:
        from .webapp import create_app
        web = create_app(app)
        host = "0.0.0.0" if args.mode == "device" else cfg["webapp"]["host"]
        port = cfg["webapp"]["port"]
        threading.Thread(target=lambda: web.run(host=host, port=port, threaded=True),
                         daemon=True, name="web").start()
        print(f"[web] companion app on http://<this-device>:{port}  (PIN protected, bound to {host})")
    app.run()


if __name__ == "__main__":
    main()
