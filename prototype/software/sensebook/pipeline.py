"""Still image -> half pages: undistort (ultra-wide lens) -> keystone/homography -> split spread."""
from __future__ import annotations

import numpy as np

from .camera import split_spread
from .lens import Undistorter
from .perspective import rectify_page


def halves_from_still(img: np.ndarray, cam_cfg: dict, undistorter: Undistorter | None = None):
    """Returns (halves, info). info = {undistorted, rectified, method}."""
    und = undistorter.undistort(img) if undistorter and undistorter.enabled else img
    rect, method = rectify_page(und, cam_cfg)
    return split_spread(rect), {"undistorted": und, "rectified": rect, "method": method}
