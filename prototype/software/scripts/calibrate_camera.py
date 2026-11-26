#!/usr/bin/env python
"""Chessboard calibration for the M12 ultra-wide lens. Writes the `camera.lens` block into config.yaml.

Print a chessboard (e.g. 9x6 inner corners, 25 mm squares) on a flat board. Then either

  python scripts/calibrate_camera.py --images calib/*.jpg --board 9x6 --square-mm 25 --model fisheye
  python scripts/calibrate_camera.py --live --camera 0 --board 9x6        # SPACE captures a view, q finishes (laptop webcam)
  (on the Pi: take 15-25 stills at varied tilts/distances with `rpicam-still -o calib/%04d.jpg --width 2304 --height 1296` first)

Take views covering the whole frame, especially the corners (the ultra-wide lens distorts most there).
A reprojection error under ~1 px is good. Use the same resolution/aspect as the device's still_res.
"""
import argparse
import glob
import sys
from pathlib import Path

import cv2
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sensebook.lens import calibrate  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", nargs="*", default=[])
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--board", default="9x6", help="inner corners, COLSxROWS")
    ap.add_argument("--square-mm", type=float, default=25.0)
    ap.add_argument("--model", choices=["fisheye", "standard"], default="fisheye")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--dry-run", action="store_true", help="print the block, do not write the config")
    a = ap.parse_args()
    board = tuple(int(x) for x in a.board.lower().split("x"))

    paths = [p for pat in a.images for p in glob.glob(pat)]
    imgs = [cv2.imread(p) for p in paths]
    if a.live:
        cap = cv2.VideoCapture(a.camera)
        while True:
            ok, f = cap.read()
            if not ok:
                break
            found, c = cv2.findChessboardCorners(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), board)
            view = f.copy()
            cv2.drawChessboardCorners(view, board, c, found)
            cv2.putText(view, f"views={len(imgs)}  SPACE=capture  q=done", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("calibrate", view)
            k = cv2.waitKey(30) & 0xFF
            if k == ord(" ") and found:
                imgs.append(f)
            elif k == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()
    imgs = [i for i in imgs if i is not None]
    block = calibrate(imgs, board, a.square_mm, a.model)
    print(f"views used: {block.pop('views')}, reprojection RMS: {block.pop('rms_px')} px")
    print(yaml.safe_dump({"camera": {"lens": block}}, sort_keys=False))
    if not a.dry_run:
        p = Path(a.config)
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
        cfg = cfg or {}
        cfg.setdefault("camera", {})["lens"] = block
        p.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(f"wrote camera.lens to {p}")


if __name__ == "__main__":
    main()
