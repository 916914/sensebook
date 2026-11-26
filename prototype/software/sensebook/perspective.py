"""Keystone (perspective) correction for a camera above/behind the book's top edge, tilted 30-35 deg.

Strategy: find the page quadrilateral (bright paper vs darker desk) -> homography to a rectangle.
If no confident quad is found, fall back to a fixed homography from config (`camera.homography`, 3x3, calibrated
once for the stand), else leave the image alone. Lens distortion of the wide camera is NOT corrected here.
"""
from __future__ import annotations

import cv2
import numpy as np


def order_quad(pts: np.ndarray) -> np.ndarray:
    pts = np.asarray(pts, np.float32).reshape(4, 2)
    s, d = pts.sum(axis=1), np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)], pts[np.argmax(s)], pts[np.argmax(d)]], np.float32)  # TL TR BR BL


def find_page_quad(img: np.ndarray, min_area: float = 0.25) -> np.ndarray | None:
    h, w = img.shape[:2]
    scale = 480.0 / w
    g = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(cv2.resize(g, (480, int(h * scale)), interpolation=cv2.INTER_AREA), (9, 9), 0)
    _, th = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))     # text holes -> solid paper
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    c = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(c) < min_area * th.shape[0] * th.shape[1]:
        return None
    hull = cv2.convexHull(c)
    peri = cv2.arcLength(hull, True)
    for eps in (0.01, 0.02, 0.03, 0.05, 0.08):
        ap = cv2.approxPolyDP(hull, eps * peri, True)
        if len(ap) == 4:
            q = order_quad(ap.reshape(4, 2)) / scale
            return q if cv2.contourArea(q) > 0 else None
    return None


def _near_full_frame(q: np.ndarray, shape) -> bool:
    h, w = shape[:2]
    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    return bool(np.all(np.linalg.norm(q - corners, axis=1) < 0.03 * max(h, w)))


def rectify_page(img: np.ndarray, cam_cfg: dict | None = None) -> tuple[np.ndarray, str]:
    """Returns (rectified image, method) where method is quad | fixed | none."""
    cam_cfg = cam_cfg or {}
    if cam_cfg.get("rectify", True):
        q = find_page_quad(img, cam_cfg.get("quad_min_area", 0.25))
        if q is not None and not _near_full_frame(q, img.shape):
            tl, tr, br, bl = q
            W = int(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)))
            H = int(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr)))
            if cam_cfg.get("spread_aspect"):          # optional: foreshortening-proof output shape
                H = int(W / float(cam_cfg["spread_aspect"]))
            M = cv2.getPerspectiveTransform(q, np.array([[0, 0], [W, 0], [W, H], [0, H]], np.float32))
            return cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_CUBIC), "quad"
        if q is not None and not cam_cfg.get("homography"):
            return img, "none"                         # page already fills the frame
    hm = cam_cfg.get("homography")
    if hm:
        M = np.array(hm, np.float64).reshape(3, 3)
        return cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_CUBIC), "fixed"
    return img, "none"


def page_framing(img: np.ndarray, min_area: float = 0.12) -> str:
    """Attach guidance: 'ok' | 'no_page' (no bright page quadrilateral) | 'edge_cut' (page runs off the frame)."""
    q = find_page_quad(img, min_area)
    if q is None:
        return "no_page"
    h, w = img.shape[:2]
    m = 0.01 * max(h, w)
    if q[:, 0].min() < m or q[:, 1].min() < m or q[:, 0].max() > w - m or q[:, 1].max() > h - m:
        return "edge_cut"
    return "ok"
