"""Lens undistortion for the M12 ultra-wide (~120 deg) lens on the IMX708, plus chessboard calibration.

Config block (written by scripts/calibrate_camera.py):
    camera.lens: {model: none|standard|fisheye, K: [9 numbers], D: [coeffs], size: [w, h], balance: 0..1}
Order in the pipeline: undistort -> keystone/homography (perspective.py) -> split. Maps are cached per image size and
K is rescaled when the image size differs from the calibration size (e.g. low-res vs full-res stills).
"""
from __future__ import annotations

import cv2
import numpy as np


class Undistorter:
    def __init__(self, lens_cfg: dict | None):
        c = lens_cfg or {}
        self.model = c.get("model", "none") if c.get("K") and c.get("D") else "none"
        self.K0 = np.array(c["K"], np.float64).reshape(3, 3) if self.model != "none" else None
        self.D = np.array(c["D"], np.float64).reshape(-1, 1) if self.model != "none" else None
        self.calib_size = tuple(c["size"]) if c.get("size") else None
        self.balance = float(c.get("balance", 0.3))
        self._maps: dict[tuple, tuple] = {}

    @property
    def enabled(self) -> bool:
        return self.model != "none"

    def _K(self, size: tuple[int, int]) -> np.ndarray:
        K = self.K0.copy()
        if self.calib_size and tuple(self.calib_size) != tuple(size):
            sx, sy = size[0] / self.calib_size[0], size[1] / self.calib_size[1]
            K[0] *= sx
            K[1] *= sy
        return K

    def _build(self, size: tuple[int, int]):
        if size in self._maps:
            return self._maps[size]
        K = self._K(size)
        if self.model == "fisheye":
            D = self.D.reshape(4, 1)
            newK = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, size, np.eye(3), balance=self.balance)
            m1, m2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), newK, size, cv2.CV_16SC2)
        else:
            newK, _ = cv2.getOptimalNewCameraMatrix(K, self.D, size, self.balance, size)
            m1, m2 = cv2.initUndistortRectifyMap(K, self.D, None, newK, size, cv2.CV_16SC2)
        self._maps[size] = (m1, m2, K, newK)
        return self._maps[size]

    def undistort(self, img: np.ndarray) -> np.ndarray:
        if not self.enabled:
            return img
        h, w = img.shape[:2]
        m1, m2, _, _ = self._build((w, h))
        return cv2.remap(img, m1, m2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    def map_points(self, pts: np.ndarray, size: tuple[int, int]) -> np.ndarray:
        """Distorted pixel coordinates -> coordinates in the undistorted output image (for tests / overlays)."""
        if not self.enabled:
            return np.asarray(pts, np.float64)
        _, _, K, newK = self._build(size)
        p = np.asarray(pts, np.float64).reshape(-1, 1, 2)
        if self.model == "fisheye":
            out = cv2.fisheye.undistortPoints(p, K, self.D.reshape(4, 1), R=np.eye(3), P=newK)
        else:
            out = cv2.undistortPoints(p, K, self.D, R=None, P=newK)
        return out.reshape(-1, 2)


# ---------------------------------------------------------------- calibration (used by scripts/calibrate_camera.py)
def calibrate(images: list[np.ndarray], board: tuple[int, int], square_mm: float, model: str = "fisheye") -> dict:
    """Chessboard calibration. `board` = inner corners (cols, rows). Returns the `camera.lens` config block."""
    objp = np.zeros((1, board[0] * board[1], 3), np.float64)
    objp[0, :, :2] = np.mgrid[0:board[0], 0:board[1]].T.reshape(-1, 2) * square_mm
    obj, img_pts, size = [], [], None
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)
    for im in images:
        g = im if im.ndim == 2 else cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        size = (g.shape[1], g.shape[0])
        ok, corners = cv2.findChessboardCorners(g, board, cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE)
        if ok:
            corners = cv2.cornerSubPix(g, corners, (7, 7), (-1, -1), crit)
            obj.append(objp.copy())
            img_pts.append(corners.reshape(1, -1, 2))
    if len(obj) < 8:
        raise ValueError(f"only {len(obj)} usable chessboard views; need at least 8 (use 15-25 at varied angles)")
    if model == "fisheye":
        K, D = np.zeros((3, 3)), np.zeros((4, 1))
        flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_FIX_SKEW
        rms, K, D, _, _ = cv2.fisheye.calibrate(obj, img_pts, size, K, D, None, None, flags, crit)
    else:
        rms, K, D, _, _ = cv2.calibrateCamera([o.reshape(-1, 3).astype(np.float32) for o in obj],
                                              [p.reshape(-1, 1, 2).astype(np.float32) for p in img_pts], size, None, None)
    return {"model": model, "K": [round(float(x), 6) for x in K.ravel()], "D": [round(float(x), 8) for x in np.ravel(D)],
            "size": [size[0], size[1]], "balance": 0.3, "rms_px": round(float(rms), 3), "views": len(obj)}
