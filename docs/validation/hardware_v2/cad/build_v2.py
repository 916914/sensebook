"""SenseBook hardware v2 proposal: parametric 3D model, checks and exports (CadQuery).

Built on the build chat's v1 model (design/cad/build_model.py + sb_params.py), imported READ-ONLY:
the v1 shell, stick, hub, blades, rear leg, buttons, side controls, jack, USB-C, status dots, top
microphones, cover screws and heat spreader are reused exactly. v2 replaces the Pi Zero, the single
camera and light ring, the cells and the speaker, and adds Option B controls. New numbers live in
hw2_params.py.

Run from the repository root with the build chat's environment:
    design\\.venv\\Scripts\\python.exe docs\\validation\\hardware_v2\\cad\\build_v2.py

Writes docs/validation/hardware_v2/out/ (GLB, STEP, STL, model_report_v2.json). Never writes to design/.
Nothing here has been built or measured: bought-part sizes are datasheet or estimated sizes (see hw2_params).
"""
from __future__ import annotations

import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
# The v1 model is taken from a fixed git commit (the one checked in design/VALIDATION.md and shown on the hub's
# 3D viewer), not from the working copy, so work in progress in design/ cannot change this build.
V1_COMMIT = "598d0f3"
import subprocess                          # noqa: E402
import tempfile                            # noqa: E402
V1_DIR = os.path.join(tempfile.gettempdir(), f"sensebook_v1_{V1_COMMIT}")
os.makedirs(V1_DIR, exist_ok=True)
for _f in ("build_model.py", "sb_params.py"):
    _src = subprocess.check_output(["git", "-C", REPO, "show", f"{V1_COMMIT}:design/cad/{_f}"])
    with open(os.path.join(V1_DIR, _f), "wb") as _fh:
        _fh.write(_src)
sys.path.insert(0, V1_DIR)
sys.path.insert(0, HERE)

import cadquery as cq                      # noqa: E402
import build_model as bm                   # noqa: E402  (v1 model, read-only)
import sb_params as P                      # noqa: E402
import hw2_params as Q                     # noqa: E402

OUT = os.path.join(HERE, "..", "out")
QUICK = "--quick" in sys.argv
U0 = bm.unit_matrix(bm.STICK0, bm.TIP0)    # unit frame -> book frame (default textbook pose)
R0 = U0[:3, :3]
box, cyl, cyl_y, cyl_z, to_facet, fpt, wire, group = bm.box, bm.cyl, bm.cyl_y, bm.cyl_z, bm.to_facet, bm.fpt, bm.wire, bm.group


def add(name, wp, grp, mat, *, label, option=None, mass=None, rho=None, frame="unit", explode=(0, 0, 0), printed=False,
        budget="v2"):
    bm.add(name, wp, grp, mat, budget=budget, label=label, mass=mass, rho=rho, frame=frame, explode=explode, printed=printed)
    bm.BODIES[-1]["option"] = option
    bm.BODIES[-1]["v2"] = True


def M_from(X, Y, Z, p):
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = X, Y, Z, p
    return m


def W(shape):
    return cq.Workplane("XY").add(shape)


# =====================================================================================
#  1. v1 model (read-only reuse)
# =====================================================================================
tub1, cover1 = bm.build_unit()
info = bm.build_mechanics()
REMOVE = {"shell_front_tub", "lens_window", "lens_bezel", "light_ring_diffuser", "light_ring_pcb", "light_ring_leds",
          "camera_lens_m12", "camera_lens_glass", "camera_holder_m12", "camera_board_imx708", "camera_connector",
          "camera_screws", "pi_zero_2w_pcb", "pi_zero_2w_chips", "pi_zero_2w_connectors", "pi_gpio_pads", "microsd_card",
          "cell_right", "cell_left", "cell_pcm_right", "cell_pcm_left", "speaker", "amp_board_max98357a", "amp_board_parts",
          "dac_board_pcm5102", "dac_board_parts", "power_board", "power_board_parts", "fuel_gauge_max17048", "haptic_motor",
          "harness_left", "harness_right", "battery_leads", "speaker_leads", "headphone_leads", "camera_flex"}
OPTION_A_ONLY = {"button_ask", "button_play_pause", "button_back", "button_forward", "top_button_board",
                 "top_button_switches", "back_button_board", "forward_button_board"}
V1_HEAD_ENV = (lambda bs: [round(float(v), 1) for v in (np.max([bm.bbox(b["shape"])[3:] for b in bs], 0) - np.min([bm.bbox(b["shape"])[:3] for b in bs], 0))])(
    [b for b in bm.BODIES if b["group"] == "unit" and b["variant"] is None])
bm.BODIES[:] = [b for b in bm.BODIES if b["name"] not in REMOVE]
for b in bm.BODIES:
    b["option"] = "A" if b["name"] in OPTION_A_ONLY else None
    b["v2"] = False
    if b["name"] == "shell_back_cover":
        b["label"] = "Back cover (v1, unchanged): its four standoffs carry the v2 main board"
    if b["name"] == "thermal_pad":
        b["label"] = "Thermal pad: SoC to heat spreader (v1 part, now under the RK3576)"
    if b["name"] == "usb_c_receptacle":
        b["label"] = "USB-C receptacle (v1 position): charging with USB PD"


# =====================================================================================
#  2. camera aims: search for the highest worst-case dpi on the printed text, with full-page coverage
# =====================================================================================
SPX, SPY = Q.SPREAD[0] / 2, Q.SPREAD[1]
mg = Q.TEXT_MARGIN
TX = np.r_[np.linspace(-SPX + mg["outer"], -mg["gutter"], 14), np.linspace(mg["gutter"], SPX - mg["outer"], 14)]
TY = np.linspace(mg["top"], SPY - mg["bottom"], 16)
GX, GY = np.meshgrid(TX, TY)
GX, GY = GX.ravel(), GY.ravel()
CX = np.r_[np.linspace(-SPX, -1, 9), np.linspace(1, SPX, 9)]
CY = np.linspace(0, SPY, 9)
CGX, CGY = [a.ravel() for a in np.meshgrid(CX, CY)]


def cam_basis(down, yaw, side):
    d, y = math.radians(down), math.radians(yaw) * side
    fwd = np.array([math.sin(y) * math.cos(d), math.cos(y) * math.cos(d), -math.sin(d)])
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return right, fwd, up


def make_cam(pos_book, down, yaw, side, hfov, dist):
    Wp, Hp = Q.SENSOR_PX
    X, Y, Z = cam_basis(down, yaw, side)
    f = (Wp / 2) / math.tan(math.radians(hfov) / 2)
    vfov = 2 * math.degrees(math.atan((Hp / 2) / f))
    return dict(p=np.asarray(pos_book, float), X=X, Y=Y, Z=Z, f=f, hfov=hfov, vfov=vfov, down=down, yaw=yaw, side=side, D=dist)


R_CORNER = math.hypot(Q.SENSOR_PX[0] / 2, Q.SENSOR_PX[1] / 2)


def project(c, x, y):
    v = np.stack([x - c["p"][0], y - c["p"][1], -c["p"][2] * np.ones_like(x)], -1)
    xc, yc, zc = v @ c["X"], v @ c["Y"], v @ c["Z"]
    u, w = c["f"] * xc / yc, c["f"] * zc / yc
    k = 1 + c["D"] * (u * u + w * w) / R_CORNER ** 2          # radial lens distortion (barrel for D < 0)
    u, w = u * k, w * k
    ok = (yc > 0) & (np.abs(u) <= Q.SENSOR_PX[0] / 2) & (np.abs(w) <= Q.SENSOR_PX[1] / 2)
    return u, w, ok


def dpi(c, x, y, d=0.5):
    # central differences (symmetric, so mirrored cameras give mirrored numbers)
    ua, wa, oka = project(c, x - d / 2, y)
    ub, wb, okb = project(c, x + d / 2, y)
    uc, wc, okc = project(c, x, y - d / 2)
    ue, we, oke = project(c, x, y + d / 2)
    s = np.minimum(np.hypot(ub - ua, wb - wa), np.hypot(ue - uc, we - wc)) / d * 25.4
    return np.where(oka & okb & okc & oke, s, 0.0)


def best_of(cams, x, y):
    return np.max(np.stack([dpi(c, x, y) for c in cams]), 0)


near_lens_unit = {s: np.array(fpt(Q.NEAR_A, s * Q.NEAR_UV[0], Q.NEAR_UV[1])) for s in (-1, 1)}
far_lens_unit = {s: np.array(fpt(Q.FAR_A, s * Q.FAR_UV[0], Q.FAR_UV[1])) for s in (-1, 1)}
to_book = lambda p: (U0 @ np.append(p, 1.0))[:3]
near_pos = {s: to_book(p) for s, p in near_lens_unit.items()}
far_pos = {s: to_book(p) for s, p in far_lens_unit.items()}
FA = math.radians(P.FACET_ANGLE)
FACET_N_BOOK = R0 @ np.array([0.0, math.sin(FA), -math.cos(FA)])        # outward facet normal, book frame


def tilt_deg(down, yaw):
    _, f, _ = cam_basis(down, yaw, 1)
    return math.degrees(math.acos(float(np.clip(f @ FACET_N_BOOK, -1, 1))))


def pick(cands, max_tilt=None):
    """cands: (ok, score, tilt, down, yaw). The highest worst-case dpi reachable (within max_tilt); among aims within
    0.5 dpi of it, the one closest to the facet normal, so the module sits flattest behind the facet."""
    pool = [c for c in cands if c[0] and (max_tilt is None or c[2] <= max_tilt)] or cands
    top = max(c[1] for c in pool)
    return min((c for c in pool if c[1] >= top - 0.5), key=lambda c: (c[2], -c[1]))


def search(fixed, pos, hfov, dist, cap):
    """Aim one pair (mirrored) with the other pair fixed: every aim within the tilt cap that, with the fixed pair, sees
    the whole page; scored by the lowest dpi on the printed text."""
    cands = []
    for dn in Q.SEARCH_DOWN:
        for yw in Q.SEARCH_YAW:
            t = tilt_deg(dn, yw)
            if t > cap:
                continue
            cams = [make_cam(pos[s], dn, yw, s, hfov, dist) for s in (-1, 1)] + fixed
            ok = bool(np.all(best_of(cams, CGX, CGY) > 0))
            cands.append((ok, float(best_of(cams, GX, GY).min()), t, dn, yw))
    return pick(cands)


# alternate: far pair with a starting near aim, then the near pair, then the far pair again
near_aim = (Q.NEAR_START_AIM[0], Q.NEAR_START_AIM[1])
NEAR_CAMS = [make_cam(near_pos[s], near_aim[0], near_aim[1], s, Q.NEAR_HFOV, Q.NEAR_DISTORTION) for s in (-1, 1)]
for _ in range(2):
    bf = search(NEAR_CAMS, far_pos, Q.FAR_HFOV, Q.FAR_DISTORTION, Q.MAX_TILT)
    FAR_CAMS = [make_cam(far_pos[s], bf[3], bf[4], s, Q.FAR_HFOV, Q.FAR_DISTORTION) for s in (-1, 1)]
    bn = search(FAR_CAMS, near_pos, Q.NEAR_HFOV, Q.NEAR_DISTORTION, Q.MAX_TILT)
    NEAR_CAMS = [make_cam(near_pos[s], bn[3], bn[4], s, Q.NEAR_HFOV, Q.NEAR_DISTORTION) for s in (-1, 1)]
best_far = (bf[1], bf[3], bf[4])
best_near = (bn[1], bn[3], bn[4])
CAM_TILT = dict(near=round(bn[2], 1), far=round(bf[2], 1))
ALL_CAMS = NEAR_CAMS + FAR_CAMS
CAM_NAMES = ["near_left", "near_right", "far_left", "far_right"]
grid_dpi = best_of(ALL_CAMS, GX, GY)
cover_dpi = best_of(ALL_CAMS, CGX, CGY)
print(f"aims: near down {best_near[1]} yaw {best_near[2]} (tilt {CAM_TILT['near']}), far down {best_far[1]} yaw {best_far[2]} (tilt {CAM_TILT['far']}); "
      f"text min {grid_dpi.min():.0f} dpi, full-page covered {bool(np.all(cover_dpi > 0))}")


# =====================================================================================
#  3. head shell v2 (v1 tub with filled, removed and new openings)
# =====================================================================================
wall_solid = bm.unit_solid(0.0).cut(bm.unit_solid(P.WALL))
tub = tub1
tub = tub.union(wall_solid.intersect(box(17, 35, -2.5, 0.5, 22, 32)))                     # fill the v1 speaker grille
tub = tub.union(wall_solid.intersect(to_facet(cq.Workplane("XY").circle(10.4).extrude(4.0).translate((0, 0, -1)))))  # fill v1 lens/ring opening
tub = tub.cut(to_facet(box(-12.5, 12.5, -8.5, 10.5, P.WALL + 0.15, 17.5)))                 # remove v1 camera posts and webs


def cam_frames(cam, lens_unit):
    """Camera-local frame (X right, Y = optical axis, Z up) -> unit frame, as a 4x4 matrix."""
    Xu, Yu, Zu = R0.T @ cam["X"], R0.T @ cam["Y"], R0.T @ cam["Z"]
    return M_from(Xu, Yu, Zu, lens_unit)


def frustum(cam, r0, length=12.0, back=0.4):
    """Viewing pyramid (camera local) from just behind the lens front out to `length`, with margins."""
    hx = math.tan(math.radians(cam["hfov"] / 2 + Q.WINDOW_MARGIN_DEG))
    hz = math.tan(math.radians(cam["vfov"] / 2 + Q.WINDOW_MARGIN_DEG))
    w0 = [cq.Vector(sx * r0, -back, sz * r0) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    w1 = [cq.Vector(sx * (r0 + (length + back) * hx), length, sz * (r0 + (length + back) * hz)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return cq.Solid.makeLoft([cq.Wire.makePolygon(w0, close=True), cq.Wire.makePolygon(w1, close=True)], True)


def module(body, barrel):
    """Camera module in camera-local coordinates (optical axis +Y, lens front at the origin)."""
    w, h, d = body
    r, L = barrel
    b = cq.Solid.makeCylinder(r, L, cq.Vector(0, -L, 0), cq.Vector(0, 1, 0))
    m = cq.Solid.makeBox(w, d, h, cq.Vector(-w / 2, -L - d, -h / 2))
    s = cq.Solid.makeBox(w, Q.CAM_STIFF, h + 1.5, cq.Vector(-w / 2, -L - d - Q.CAM_STIFF, -h / 2 - 1.5))
    return b, m, s


CAM_PARTS = {}
facet_slab = to_facet(box(-60, 60, -60, 60, 0.2, 0.2 + Q.WINDOW_T))
for name, cam in zip(CAM_NAMES, ALL_CAMS):
    near = name.startswith("near")
    s = cam["side"]
    lens_u = near_lens_unit[s] if near else far_lens_unit[s]
    M = cam_frames(cam, lens_u)
    body, barrel = (Q.NEAR_BODY, Q.NEAR_BARREL) if near else (Q.FAR_BODY, Q.FAR_BARREL)
    fr = bm.moved(frustum(cam, barrel[0] + 0.4, back=barrel[1] + 0.3), M)       # clears the whole barrel through the wall
    tub = tub.cut(W(fr))
    pane = W(fr).intersect(facet_slab).intersect(wall_solid)
    CAM_PARTS[name] = dict(M=M, near=near, pane=pane, parts=[bm.moved(x, M) for x in module(body, barrel)])

# light-bar slots and the ToF window (facet)
LIGHT_SLOTS = [(u0, u1, Q.LIGHT_TOP["v"][0], Q.LIGHT_TOP["v"][1], "top") for u0, u1 in Q.LIGHT_TOP["u"]] + \
              [(u0, u1, Q.LIGHT_BOTTOM["v"][0], Q.LIGHT_BOTTOM["v"][1], "bottom_left" if u0 < 0 else "bottom_right") for u0, u1 in Q.LIGHT_BOTTOM["u"]]
for u0, u1, v0, v1, _ in LIGHT_SLOTS:
    tub = tub.cut(to_facet(box(u0, u1, v0, v1, -2, 4)))
tw, th = Q.TOF_WINDOW
tub = tub.cut(to_facet(box(-tw / 2, tw / 2, -th / 2, th / 2, -2, 4)))
# new speaker grille (front centre) and the third microphone port
g = Q.GRILLE
sx0, sz0 = Q.SPEAKER_XZ
for i in range(g["cols"]):
    for j in range(g["rows"]):
        tub = tub.cut(cyl_y(-4, 2, sx0 + (i - (g["cols"] - 1) / 2) * g["pitch"], sz0 + (j - (g["rows"] - 1) / 2) * g["pitch"], g["r"]))
tub = tub.cut(cyl_y(-4, 2, Q.MIC3_XZ[0], Q.MIC3_XZ[1], 0.5))

# Option B shell: the four top-button openings are closed (keys move to the hub wings)
plugB = wall_solid.intersect(bm.fuse([
    cyl_z(36, 42, P.ASK_XY[0], P.ASK_XY[1], P.ASK_D / 2 + 0.3),
    bm.slot_xy(P.PLAY_SIZE[0] + 0.6, P.PLAY_SIZE[1] + 0.6, 36, 42, *P.PLAY_XY),
    cyl_z(36, 42, -P.NAV_X, P.NAV_Y, P.NAV_D / 2 + 0.3), cyl_z(36, 42, P.NAV_X, P.NAV_Y, P.NAV_D / 2 + 0.3)]))
tubB = tub.union(plugB)
add("shell_front_tub", tub, "unit", "abs_teal", option="A", rho="petg", printed=True, explode=(0, 34, 0),
    label="Front shell v2 (Option A): v1 shell with 4 camera windows, light-bar slots, ToF window, new speaker grille")
add("shell_front_tub_b", tubB, "unit", "abs_teal", option="B", rho="petg", printed=True, explode=(0, 34, 0),
    label="Front shell v2 (Option B): top-button openings closed; keys are on the hub wings")


# =====================================================================================
#  4. head internals v2
# =====================================================================================
LBL = {"near_left": f"Near-left camera, 50 MP ultra-wide, ~{Q.NEAR_HFOV:.0f} deg (fills in the area near the device)",
       "near_right": f"Near-right camera, 50 MP ultra-wide, ~{Q.NEAR_HFOV:.0f} deg (fills in the area near the device)",
       "far_left": f"Left-page camera, 50 MP, ~{Q.FAR_HFOV:.0f} deg (reads most of the left page)",
       "far_right": f"Right-page camera, 50 MP, ~{Q.FAR_HFOV:.0f} deg (reads most of the right page)"}
for name, cp in CAM_PARTS.items():
    b, m, s = cp["parts"]
    add(f"camera_{name}_lens", W(b), "unit", "lens_black", mass=0.3, label=LBL[name] + ": lens", explode=(0, 10, -10))
    add(f"camera_{name}_module", W(m), "unit", "ic_black", mass=Q.CAM_MASS - 0.3, label=LBL[name] + ": module", explode=(0, 6, -6))
    add(f"camera_{name}_stiffener", W(s), "unit", "pcb_black", mass=0.1, label=LBL[name] + ": stiffener and flex tail")

# one clear window per side over the near and far camera (their openings meet), like a phone's camera glass;
# the window is printed black on the inside except over each camera's view
for side in ("left", "right"):
    add(f"window_{side}", CAM_PARTS[f"near_{side}"]["pane"].union(CAM_PARTS[f"far_{side}"]["pane"]), "unit", "glass", rho="pmma",
        label=f"Clear window over the near-{side} and far-{side} cameras (one piece)", explode=(0, 24, -12))

LED_UV = [(u, sum(Q.LIGHT_TOP["v"]) / 2) for u in Q.LED_TOP_U] + [(u, sum(Q.LIGHT_BOTTOM["v"]) / 2) for u in Q.LED_BOTTOM_U]
for u0, u1, v0, v1, nm in LIGHT_SLOTS:
    add(f"light_optic_{nm}", to_facet(box(u0 + 0.1, u1 - 0.1, v0 + 0.1, v1 - 0.1, 0.2, P.WALL)), "unit", "diffuser", rho="pmma",
        label=f"Light-bar optic ({nm.replace('_', ' ')}): moulded strip that aims each LED at its own band of the page", explode=(0, 22, -22))
    add(f"light_board_{nm}", to_facet(box(u0 - 0.5, u1 + 0.5, v0 - 0.5, v1 + 0.5, 2.6, 3.2)), "unit", "pcb_white", mass=0.3,
        label=f"Light-bar LED board ({nm.replace('_', ' ')})", explode=(0, 16, -16))
    leds = [to_facet(box(u - Q.LED_PKG[0] / 2, u + Q.LED_PKG[0] / 2, v - Q.LED_PKG[1] / 2, v + Q.LED_PKG[1] / 2, 2.6 - Q.LED_PKG[2], 2.6))
            for u, v in LED_UV if u0 < u < u1 and v0 < v < v1]
    add(f"light_leds_{nm}", group(leds), "unit", "led_warm", mass=0.05 * len(leds),
        label=f"High-CRI LEDs ({nm.replace('_', ' ')}), one driver channel each", explode=(0, 16, -16))
N_LEDS = len(LED_UV)

add("tof_window", to_facet(box(-tw / 2 + 0.1, tw / 2 - 0.1, -th / 2 + 0.1, th / 2 - 0.1, 0.2, 1.0)), "unit", "glass", rho="pmma",
    label="ToF sensor window", explode=(0, 22, -22))
add("tof_sensor", to_facet(box(-Q.TOF[0] / 2, Q.TOF[0] / 2, -Q.TOF[1] / 2, Q.TOF[1] / 2, 1.85, 1.85 + Q.TOF[2])), "unit", "ic_black",
    mass=0.1, label="Hand and page-turn sensor: ST VL53L8CX multizone ToF (lets the cameras sleep)", explode=(0, 14, -14))
add("tof_board", to_facet(box(-4.4, 4.4, -3.4, 3.4, 3.65, 4.25)), "unit", "pcb_green2", mass=0.15, label="ToF sensor board",
    explode=(0, 10, -10))

# main board: same outline and holes as the Pi Zero 2 W, so v1's standoffs and cover are unchanged
yb, yt = P.PI_PCB_Y, P.PI_PCB_Y - P.PI_TH
z0 = P.PI_Z0
pi_holes = [(sx * (P.PI_L / 2 - 3.5), z0 + zz) for sx in (-1, 1) for zz in (3.5, P.PI_Wd - 3.5)]
pcb = box(-P.PI_L / 2, P.PI_L / 2, yt, yb, z0, z0 + P.PI_Wd).edges("|Y").fillet(3.0)
for (hx, hz) in pi_holes:
    pcb = pcb.cut(cyl_y(yt - 1, yb + 1, hx, hz, 1.35))
add("main_board", pcb, "unit", "pcb_green", mass=6.0, label="v2 main board, 65 x 30 mm, 8-layer HDI (same outline and holes as the Pi Zero)",
    explode=(0, -22, 0))
for key, lab, x0, x1, zz0, zz1, h, ms in Q.BOARD_PARTS:
    mat = "metal_tin" if key in ("wifi_bt",) else ("ic_black" if not key.startswith("conn") else "plastic_black")
    add(f"mb_{key}", box(x0, x1, yt - h, yt, zz0, zz1), "unit", mat, mass=ms, label=lab, explode=(0, -22, 0))
add("antenna_flex", box(P.UNIT_W / 2 - P.WALL - 0.05 - Q.ANTENNA[2], P.UNIT_W / 2 - P.WALL - 0.05, -27.0, -27.0 + Q.ANTENNA[0], 26.0, 26.0 + Q.ANTENNA[1]), "unit", "flex_amber",
    mass=0.1, label="Flex antenna, Wi-Fi 6 + Bluetooth, on the right inner wall (away from the steel stick)", explode=(14, 0, 0))

# cells: stepped pouch cells in parallel, sized around the camera modules
cam_bb = np.array([bm.bbox(x) for cp in CAM_PARTS.values() for x in cp["parts"]])
z_step = float(cam_bb[:, 5].max()) + Q.CELL_GAP
y_back_cam = float(cam_bb[:, 1].min())
Y_DROP = y_back_cam - 0.6                                  # flex drop line, just behind the deepest module
y_low = Y_DROP - 0.6                                       # front face of the lower cells
cell_specs = []
for side, (x0, x1) in (("right", Q.CELL_SIDE_X), ("left", (-Q.CELL_SIDE_X[1], -Q.CELL_SIDE_X[0])), ("center", Q.CELL_CENTER_X)):
    zz0, zz1 = Q.CELL_Z["center" if side == "center" else "side"]
    cell_specs.append((f"cell_{side}_upper", x0, x1, Q.CELL_Y_BACK, Q.CELL_Y_FRONT, z_step, zz1))
    if z_step - Q.CELL_GAP - zz0 > 3.0 and y_low - Q.CELL_Y_BACK > 3.0:
        cell_specs.append((f"cell_{side}_lower", x0, x1, Q.CELL_Y_BACK, y_low, zz0, z_step - Q.CELL_GAP))
cell_vols = {}
for nm, x0, x1, y0, y1, zz0, zz1 in cell_specs:
    c = box(x0, x1, y0, y1, zz0, zz1).edges().fillet(Q.CELL_R)
    v = bm.shape_of(c).Volume() / 1000.0
    cell_vols[nm] = v
    sx_ = 30 if "right" in nm else (-30 if "left" in nm else 0)
    add(nm, c, "unit", "pouch_silver", mass=round(v * Q.CELL_DENSITY, 1), label=f"Pouch cell ({nm[5:].replace('_', ' ')}), {v:.1f} cm3 (EST)",
        explode=(sx_, 0, 24 if "upper" in nm else 0))
fx0, fx1 = Q.CELL_FRONT["x"]; fy0, fy1 = Q.CELL_FRONT["y"]
cf = box(fx0, fx1, fy0, fy1, z_step, Q.CELL_FRONT["z1"]).edges().fillet(Q.CELL_R)
cell_vols["cell_front"] = bm.shape_of(cf).Volume() / 1000.0
add("cell_front", cf, "unit", "pouch_silver", mass=round(cell_vols["cell_front"] * Q.CELL_DENSITY, 1),
    label=f"Pouch cell (front, above the cameras), {cell_vols['cell_front']:.1f} cm3 (EST)", explode=(0, 26, 20))
add("cell_bus", box(-36.0, 36.0, -27.65, -27.5, 18.0, 22.0).union(box(-36.0, -33.0, -31.0, -27.5, 18.0, 22.0))
    .union(box(-33.0, -27.1, -30.05, -29.9, 18.0, 22.0)), "unit", "kapton", mass=0.3,
    label="Cell bus flex: joins the cells in parallel and runs round the board edge to the charger", explode=(0, -8, 0))

# USB-C sub-board behind the v1 receptacle
add("usb_board", box(33.0, 41.5, -14.5, -13.6, 18.0, 29.0), "unit", "pcb_green2", mass=0.3,
    label="USB-C sub-board (connects to the charger via the board-to-board flex)", explode=(18, 0, 0))

# speaker, third mic, haptic (Option A)
sp_x, sp_z = Q.SPEAKER_XZ
spk = box(sp_x - Q.SPEAKER[0] / 2, sp_x + Q.SPEAKER[0] / 2, -P.WALL - 0.15 - Q.SPEAKER[2], -P.WALL - 0.15,
          sp_z - Q.SPEAKER[1] / 2, sp_z + Q.SPEAKER[1] / 2).edges("|Y").fillet(1.5)
add("speaker_box", spk, "unit", "speaker", mass=2.0, label="Sealed box speaker, Soberton 1511 class (15 x 11 mm, 90 dB at 0.6 W, 10 cm)",
    explode=(0, 20, 0))
mx, mz = Q.MIC3_XZ
add("mic_front", box(mx - 2.5, mx + 2.5, -P.WALL - 0.95, -P.WALL - 0.15, mz - 2.5, mz + 2.5)
    .union(box(mx - 1.5, mx + 1.5, -P.WALL - 1.95, -P.WALL - 0.95, mz - 1.3, mz + 1.3)), "unit", "pcb_blue", mass=0.3,
    label="Third MEMS microphone (front): echo cancellation and beamforming", explode=(0, 14, 8))
hx, hy, hz0, hr, ht = Q.HAPTIC_A
add("haptic_motor_head", cyl_z(hz0, hz0 + ht, hx, hy, hr), "unit", "metal_tin", option="A", mass=0.9,
    label="Coin vibration motor (Option A: in the head)", explode=(0, 0, 18))

# flex cables (indicative routes; collision-checked like every other body)
def cam_tail(name):
    M = CAM_PARTS[name]["M"]
    w, h, d = Q.NEAR_BODY if name.startswith("near") else Q.FAR_BODY
    L = (Q.NEAR_BARREL if name.startswith("near") else Q.FAR_BARREL)[1]
    return tuple((M @ np.array([0.0, -L - d - Q.CAM_STIFF - 0.2, -h / 2 - 1.0, 1.0]))[:3])


flex = []
fx = Q.FLEX_X
zf = max(2.6, Y_DROP + P.FACET_TOP_Z + P.WALL * math.sqrt(2) + 0.7)       # stay above the facet's inner floor
for nm in CAM_NAMES:
    s_ = -1 if nm.endswith("left") else 1
    p0 = cam_tail(nm)
    if nm.startswith("near"):
        xr = s_ * fx["near"]
        pts = [p0, (xr, Y_DROP, p0[2]), (xr, Y_DROP, zf), (xr, Y_DROP - 2.5, 2.6), (xr, -30.4, 2.6), (xr, -30.4, 5.6)]
    else:
        xd, xr = s_ * fx["far_drop"], s_ * fx["far"]
        pts = [p0, (xd, Y_DROP, p0[2]), (xd, Y_DROP, zf), (xd, Y_DROP - 2.5, 2.6), (xd, -27.4, 2.6), (xr, -27.4, 2.6),
               (xr, -30.4, 2.6), (xr, -30.4, 5.6)]
    flex.append((f"flex_{nm}", pts, f"Flex: {nm.replace('_', '-')} camera to the board"))
tb = np.array(fpt(4.9, 0.0, -2.0))
flex.append(("flex_tof", [tuple(tb), (0.0, Y_DROP, float(tb[2])), (0.0, Y_DROP, zf), (0.0, Y_DROP - 2.5, 2.6), (0.0, -30.4, 2.6), (0.0, -30.4, 5.6)],
             "Flex: ToF sensor to the board"))
flex.append(("flex_top", [(0.0, -5.5, 31.0), (0.0, -5.5, 34.4), (5.8, -8.0, 34.4), (5.8, -27.4, 34.4), (5.8, -30.0, 34.4), (3.2, -30.3, 32.4)],
             "Flex: speaker, front mic, status LEDs, top keys, haptic to the board"))
# light bars: two jumpers behind the facet and one flex to the far-left connector (LED driver on the main board)
vb = sum(Q.LIGHT_BOTTOM["v"]) / 2
vt = sum(Q.LIGHT_TOP["v"]) / 2
uj = fx["light_jumper_u"]
xin_b = Q.LIGHT_BOTTOM["u"][0][1] + 0.4                 # inner ends of the lower strips
ptl = tuple(fpt(3.4, -uj, vt))
flex.append(("flex_light_jumper_bottom", [tuple(fpt(3.4, xin_b, vb)), tuple(fpt(3.4, -xin_b, vb))],
             "Flex jumper: joins the two lower light strips across the middle"))
flex.append(("flex_light_jumper_left", [tuple(fpt(3.4, -uj, vb)), ptl], "Flex jumper: lower-left light strip to the top strip"))
# The light lines join the far-left camera flex where it drops (one two-in-one flex to the far-left connector):
# under the board there is no free path beside the camera flex (the back cover's lip and the camera flex fill it).
xl = -fx["light_drop"]
far_pts = dict((nm, pts) for nm, pts, _ in flex)["flex_far_left"]
zj = (far_pts[1][2] + far_pts[2][2]) / 2                 # halfway down the far-left flex's drop
flex.append(("flex_light_main", [ptl, (xl, ptl[1], ptl[2]), (xl, Y_DROP, ptl[2]), (xl, Y_DROP, zj), (far_pts[1][0] - 0.6, Y_DROP, zj)],
             "Flex: light bars; joins the far-left camera flex, which carries the LED lines to the driver on the main board"))
for nm, pts, lab in flex:
    add(nm, wire(pts, 0.4), "unit", "flex_amber", mass=0.3 if not nm.startswith("flex_light_jumper") else 0.1, label=lab, explode=(0, -6, 6))


# =====================================================================================
#  5. Option B controls (book frame): hub wings and a pocket clicker
# =====================================================================================
for s in (-1, 1):
    x0, x1 = sorted((s * Q.WING_X[0], s * Q.WING_X[1]))
    wing = box(x0, x1, Q.WING_Y[0], Q.WING_Y[1], Q.WING_Z[0], Q.WING_Z[1]).edges("|Z").fillet(3.0).faces(">Z").edges().fillet(1.2)
    side = "left" if s < 0 else "right"
    add(f"hub_wing_{side}", wing, "hub", "abs_teal", option="B", rho="petg", printed=True, frame="book", explode=(s * 30, 0, -30),
        label=f"Hub wing ({side}, Option B): carries the main keys at the book's top edge, braced by the book")
    add(f"hub_wing_board_{side}", box(x0 + 1.5, x1 - 1.5, Q.WING_Y[0] + 1.5, Q.WING_Y[1] - 1.5, 6.2, 7.0), "hub", "pcb_green2",
        option="B", mass=0.4, frame="book", label=f"Wing key board ({side})", explode=(s * 30, 0, -22))
yc = (Q.WING_Y[0] + Q.WING_Y[1]) / 2
for key, kx, r in Q.WING_KEYS:
    if key == "play_pause":
        cap = bm.slot_xy(8.0, 4.0, Q.WING_Z[1] - 0.5, Q.WING_Z[1] + 1.2, kx, yc, 90)
        mat, lab = "abs_light", "Play / Pause key (Option B, left wing)"
    else:
        cap = cyl_z(Q.WING_Z[1] - 0.5, Q.WING_Z[1] + (1.6 if key == "ask" else 1.2), kx, yc, r)
        if key == "ask":
            cap = cap.cut(cq.Workplane("XY").add(cq.Solid.makeSphere(14.0, cq.Vector(kx, yc, Q.WING_Z[1] + 1.6 + 14.0 - 0.9))))
        mat = "marigold" if key == "ask" else "abs_light"
        lab = {"ask": "Ask key (Option B, right wing): hold to talk", "forward": "Forward key (Option B, right wing)",
               "back": "Back key (Option B, left wing)"}[key]
    add(f"wing_key_{key}", cap, "hub", mat, option="B", rho="petg", printed=True, frame="book", label=lab,
        explode=(math.copysign(30, kx), 0, -14))
add("haptic_motor_wing", cyl_z(1.0, 3.7, 24.0, yc, 4.0), "hub", "metal_tin", option="B", mass=0.8, frame="book",
    label="Coin vibration motor (Option B: in the right wing, felt through the book)", explode=(30, 0, -38))
cx0, cx1, cy0, cy1, ch = Q.CLICKER
TABLE = -(P.COVER_HARD + P.BLOCK_HARD)
clk = box(cx0, cx1, cy0, cy1, TABLE, TABLE + ch).edges("|Z").fillet(5.0).faces(">Z").edges().fillet(1.5)
add("clicker_body", clk, "clicker", "abs_teal", option="B", mass=Q.CLICKER_MASS, frame="book", printed=True,
    label="Pocket clicker (Option B): Bluetooth LE keys for reading in the hands, in bed or on a bus; docks to charge (EST 36 x 28 x 9 mm)")
ky = (cy0 + cy1) / 2
ask_c = cyl_z(TABLE + ch - 0.3, TABLE + ch + 1.4, cx0 + 11, ky, 5.0).cut(
    cq.Workplane("XY").add(cq.Solid.makeSphere(12.0, cq.Vector(cx0 + 11, ky, TABLE + ch + 1.4 + 12.0 - 0.8))))
add("clicker_key_ask", ask_c, "clicker", "marigold", option="B", rho="petg", frame="book", label="Clicker: Ask key")
add("clicker_keys", group([cyl_z(TABLE + ch - 0.3, TABLE + ch + 1.0, cx0 + 24, ky - 6.5, 2.6), cyl_z(TABLE + ch - 0.3, TABLE + ch + 1.0, cx0 + 24, ky + 6.5, 2.6),
                           bm.slot_xy(6.0, 2.6, TABLE + ch - 0.3, TABLE + ch + 1.0, cx0 + 31, ky, 90)]),
    "clicker", "abs_light", option="B", rho="petg", frame="book", label="Clicker: Back, Forward, Play/Pause")

# =====================================================================================
#  6. context: the open textbook and the camera zones (not part of the device)
# =====================================================================================
add("book_cover_left", box(-SPX - 5, -0.8, -4, SPY + 4, TABLE, TABLE + P.COVER_HARD), "book", "book_cover", mass=0, frame="book",
    label="Open textbook (context): cover")
add("book_cover_right", box(0.8, SPX + 5, -4, SPY + 4, TABLE, TABLE + P.COVER_HARD), "book", "book_cover", mass=0, frame="book",
    label="Open textbook (context): cover")
add("book_pages_left", box(-SPX - 1, -1.5, 0, SPY, -10.6, 0), "book", "paper", mass=0, frame="book",
    label="Open textbook (context): left page, 18.5 x 24.5 cm")
add("book_pages_right", box(1.5, SPX + 1, 0, SPY, -10.6, 0), "book", "paper", mass=0, frame="book",
    label="Open textbook (context): right page, 18.5 x 24.5 cm")
# zones: which camera gives the sharpest view of each point of the page
ZX = np.linspace(-SPX + 2, SPX - 2, 74)
ZY = np.linspace(2, SPY - 2, 49)
ZGX, ZGY = [a.ravel() for a in np.meshgrid(ZX, ZY)]
own = np.argmax(np.stack([dpi(c, ZGX, ZGY) for c in ALL_CAMS]), 0)
zone_cols = {0: "zone_near", 1: "zone_near", 2: "zone_far", 3: "zone_far"}
for k, name in enumerate(CAM_NAMES):
    sel = own == k
    if not sel.any():
        continue
    xs_, ys_ = ZGX[sel], ZGY[sel]
    dx, dy = ZX[1] - ZX[0], ZY[1] - ZY[0]
    O = own.reshape(len(ZY), len(ZX))
    runs = []
    for iy, yv in enumerate(ZY):                       # one box per run of the same owner along a row
        ix = 0
        while ix < len(ZX):
            if O[iy, ix] != k:
                ix += 1
                continue
            jx = ix
            while jx + 1 < len(ZX) and O[iy, jx + 1] == k:
                jx += 1
            runs.append(box(ZX[ix] - dx / 2, ZX[jx] + dx / 2, yv - dy / 2, yv + dy / 2, 0.15, 0.45))
            ix = jx + 1
    zone = group(runs)
    add(f"zone_{name}", zone, "views", zone_cols[k], mass=0, frame="book",
        label=f"Page area read by the {name.replace('_', '-')} camera (sharpest view)")
    cam = ALL_CAMS[k]
    corners = [(xs_.min(), ys_.min()), (xs_.max(), ys_.min()), (xs_.max(), ys_.max()), (xs_.min(), ys_.max())]
    rays = [bm.cyl(tuple(cam["p"]), tuple(np.array([cx_, cy_, 0.3]) - cam["p"]), 0.45, float(np.linalg.norm(np.array([cx_, cy_, 0.3]) - cam["p"])))
            for cx_, cy_ in corners]
    add(f"view_{name}", group(rays), "views", zone_cols[k], mass=0, frame="book",
        label=f"View lines of the {name.replace('_', '-')} camera")


# =====================================================================================
#  7. checks
# =====================================================================================
ALLOWED = bm.ALLOWED + [("window_", "shell_"), ("light_optic", "shell_"), ("tof_window", "shell_"), ("camera_", "camera_"),
                        ("flex_", "mb_conn"), ("flex_", "camera_"), ("cell_bus", "mb_charger"), ("cell_bus", "cell_"),
                        ("light_leds", "light_board"), ("tof_sensor", "tof_board"), ("mb_", "main_board"), ("main_board", "shell_back_cover"),
                        ("hub_wing", "hub_body"), ("wing_key", "hub_wing"), ("hub_wing_board", "hub_wing"), ("haptic_motor_wing", "hub_wing"),
                        ("clicker_", "clicker_"), ("book_", "book_"), ("zone_", ""), ("view_", ""), ("thermal_pad", "mb_soc"),
                        ("usb_board", "usb_c"), ("flex_top", "speaker_box"), ("flex_light", "light_board"), ("flex_light", "flex_light"), ("flex_light_main", "flex_far_left")]


def allowed(a, b):
    for p, q in ALLOWED:
        if (a.startswith(p) and b.startswith(q)) or (b.startswith(p) and a.startswith(q)):
            return True
    return False


def config_bodies(opt, include_context=False):
    out = []
    for b in bm.BODIES:
        if b["variant"] is not None:
            continue
        if b.get("option") not in (None, opt):
            continue
        if not include_context and b["group"] in ("book", "views"):
            continue
        out.append(b)
    return out


def collisions(opt):
    bodies = config_bodies(opt, include_context=True)
    bodies = [b for b in bodies if b["group"] != "views"]
    shp = {b["name"]: bm.placed(b, U0) for b in bodies}
    bb = {n: bm.bbox(s) for n, s in shp.items()}
    names = list(shp)
    hits, tight = [], []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, c = names[i], names[j]
            if bm.boxes_gap(bb[a], bb[c]) > 0.3:
                continue
            if allowed(a, c):
                continue
            try:
                v = sum(s_.Volume() for s_ in shp[a].intersect(shp[c]).Solids())
            except Exception:
                v = 0.0
            if v > 0.02:
                ob = bm.bbox(shp[a].intersect(shp[c]))
                hits.append(dict(a=a, b=c, overlap_mm3=round(v, 3), where_book_mm=[round(float(q), 1) for q in ob]))
            elif bm.boxes_gap(bb[a], bb[c]) < 0.25:
                try:
                    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
                    d = BRepExtrema_DistShapeShape(shp[a].wrapped, shp[c].wrapped); d.Perform()
                    if 0.005 < d.Value() < 0.25:
                        tight.append(dict(a=a, b=c, gap_mm=round(d.Value(), 3)))
                except Exception:
                    pass
    return hits, sorted(tight, key=lambda r: r["gap_mm"])


def pose_hits(opt):
    pz = bm.poses(info)
    out = {}
    for pname, p in pz.items():
        items = []
        for b in bm.BODIES:
            if b.get("option") not in (None, opt) or b["group"] in ("book", "views", "clicker"):
                continue
            if b["variant"] != p["variants"].get(b["name"]):
                continue
            s_ = bm.moved(bm.placed(b, U0), np.array(p["groups"][b["group"]]))
            items.append((b["name"], b["group"], s_, bm.bbox(s_)))
        hits = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                (a, ga, sa, ba), (c, gc, sc, bc) = items[i], items[j]
                if ga == gc or bm.boxes_gap(ba, bc) > 0 or allowed(a, c) or bm.allowed(a, c):
                    continue
                try:
                    v = sum(x.Volume() for x in sa.intersect(sc).Solids())
                except Exception:
                    v = 0.0
                if v > 0.02:
                    hits.append(dict(a=a, b=c, overlap_mm3=round(v, 2)))
        out[pname] = hits
    return out


PARTS_MASS = {}


def mass_report(opt):
    rows = []
    for b in config_bodies(opt):
        if b["group"] == "clicker":
            continue
        s = bm.placed(b, U0)
        v, c = bm.vol_centroid(s)
        m = b["mass"] if b["mass"] is not None else v / 1000.0 * P.RHO[b["rho"]]
        rows.append(dict(name=b["name"], group=b["group"], mass_g=round(m, 2), com=[round(float(x), 2) for x in c]))
    PARTS_MASS[opt] = [dict(name=r["name"], group=r["group"], mass_g=r["mass_g"]) for r in rows]
    tot = sum(r["mass_g"] for r in rows)
    com = sum(r["mass_g"] * np.array(r["com"]) for r in rows) / tot
    unit = [r for r in rows if r["group"] == "unit"]
    mu = sum(r["mass_g"] for r in unit)
    return dict(total_g=round(tot, 1), head_g=round(mu, 1), com_book=[round(float(x), 1) for x in com])


def los_check(opt):
    """Rays from every camera to its page area must not hit any opaque part of the device."""
    import trimesh
    meshes = []
    for b in config_bodies(opt):
        if b["name"].startswith(("window_", "tof_window")) or b["mat"] == "glass":
            continue
        if b["name"].startswith(f"camera_"):
            continue
        s = bm.placed(b, U0)
        vs, fs = s.tessellate(0.1, 0.3)
        if not fs:
            continue
        meshes.append(trimesh.Trimesh(np.array([(p.x, p.y, p.z) for p in vs]), np.array(fs), process=False))
    scene = trimesh.util.concatenate(meshes)
    cast = trimesh.ray.ray_triangle.RayMeshIntersector(scene)
    res = {}
    for k, (name, cam) in enumerate(zip(CAM_NAMES, ALL_CAMS)):
        sel = own == k
        tx, ty = ZGX[sel], ZGY[sel]
        # the mirror in bm.add (X_cad = -x) applies to the meshes: mirror the camera and targets too
        o = cam["p"] * np.array([-1, 1, 1]) + (cam["Y"] * np.array([-1, 1, 1])) * 0.6
        tgt = np.stack([-tx, ty, np.full_like(tx, 0.3)], -1)
        d = tgt - o
        dist = np.linalg.norm(d, axis=1)
        d = d / dist[:, None]
        locs, idx_ray, _ = cast.intersects_location(np.repeat(o[None], len(d), 0), d, multiple_hits=False)
        blocked = 0
        for L_, r in zip(locs, idx_ray):
            if np.linalg.norm(L_ - o) < dist[r] - 0.5:
                blocked += 1
        res[name] = dict(rays=int(len(d)), blocked=int(blocked))
    return res


def light_check():
    """Zoned light: LED positions from the model, each LED aimed at its own band; least power for 300-750 lux."""
    from scipy.optimize import linprog
    X_, Y_ = np.meshgrid(np.linspace(-SPX + mg["outer"], SPX - mg["outer"], 41), np.linspace(mg["top"], SPY - mg["bottom"], 31))
    leds = [to_book(np.array(fpt(0.5, u, v))) for u, v in LED_UV]
    bands = [(25, 22), (75, 16), (130, 12), (185, 9), (228, 8)]
    cols = [-140, -50, 50, 140]
    aims = [(c_, b_[0], b_[1]) for b_ in bands for c_ in cols]
    assert len(aims) == len(leds), (len(aims), len(leds))
    # pair LEDs to aims: left-side LEDs to left columns first
    leds_sorted = sorted(leds, key=lambda p: p[0])
    aims_sorted = sorted(aims, key=lambda a: a[0])
    A_ = []
    for p, (tx, ty, half) in zip(leds_sorted, aims_sorted):
        a = np.array([tx, ty, 0.0]) - p; a /= np.linalg.norm(a)
        V = np.stack([X_ - p[0], Y_ - p[1], -p[2] * np.ones_like(X_)], -1)
        d = np.linalg.norm(V, axis=-1); U = V / d[..., None]
        m = math.log(0.5) / math.log(math.cos(math.radians(half)))
        A_.append((np.clip(U @ a, 0, 1) ** m * (p[2] / d) / (d / 1000.0) ** 2).ravel())
    A_ = np.stack(A_, 1)
    fw = np.array([2 * math.pi / (math.log(0.5) / math.log(math.cos(math.radians(h))) + 1) for _, _, h in aims_sorted])
    lo, hi = Q.LIGHT_TARGET_LUX
    r = linprog(fw, A_ub=np.vstack([A_, -A_]), b_ub=np.r_[hi * np.ones(len(A_)), -lo * np.ones(len(A_))], bounds=(0, None), method="highs")
    if r.status != 0:
        return dict(feasible=False, leds=len(leds))
    E = A_ @ r.x
    flux = float(fw @ r.x)
    watts = flux / 160.0 / 0.85 / 0.88          # ~160 lm/W CRI 90 LED (EST [R2]), optic 85%, driver 88%
    LIGHT_SOLUTION.update(leds_book_mm=[[round(float(v), 2) for v in p] for p in leds_sorted],
                          aims=[[float(a[0]), float(a[1]), float(a[2])] for a in aims_sorted],
                          cd=[round(float(v), 3) for v in r.x])
    return dict(feasible=True, leds=len(leds), min_lux=round(float(E.min())), max_lux=round(float(E.max())),
                uniformity=round(float(E.min() / E.max()), 2), flux_lm=round(flux), electrical_w=round(watts, 2),
                max_led_cd=round(float(r.x.max()), 1))


LIGHT_SOLUTION = {}


def head_envelope(opt):
    lo, hi = np.full(3, 1e9), np.full(3, -1e9)
    for b in config_bodies(opt):
        if b["group"] != "unit":
            continue
        bx = bm.bbox(b["shape"])                   # unit frame (mirrored x), not placed
        lo, hi = np.minimum(lo, bx[:3]), np.maximum(hi, bx[3:])
    return [round(float(v), 1) for v in hi - lo]


report = dict(cells=dict(step_z=round(z_step, 1), lower_front_y=round(y_low, 1), deepest_camera_y=round(y_back_cam, 1)), camera=dict(tilt_from_facet_deg=CAM_TILT, 
    aims=dict(near=dict(down_deg=best_near[1], yaw_deg=best_near[2], hfov=Q.NEAR_HFOV, vfov=round(NEAR_CAMS[0]["vfov"], 1)),
              far=dict(down_deg=best_far[1], yaw_deg=best_far[2], hfov=Q.FAR_HFOV, vfov=round(FAR_CAMS[0]["vfov"], 1))),
    positions_book_mm={n: [round(float(v), 1) for v in c["p"]] for n, c in zip(CAM_NAMES, ALL_CAMS)},
    text_area_min_dpi=round(float(grid_dpi.min())), text_area_median_dpi=round(float(np.median(grid_dpi))),
    share_text_area_at_or_above_300=round(float((grid_dpi >= 300).mean()), 3),
    full_page_covered=bool(np.all(cover_dpi > 0)),
    single_v1_camera_text_min_dpi=82))
total_cell = sum(cell_vols.values())
pw = Q.POWER_W
report["battery"] = dict(cell_volume_cm3=round(total_cell, 2), cells={k: round(v, 2) for k, v in cell_vols.items()},
                         v1_cell_volume_cm3=17.5,
                         wh={k: round(total_cell * v / 1000.0, 1) for k, v in Q.CELL_WH_PER_L.items()},
                         hours={k: dict(light_off=[round(total_cell * v / 1000.0 * Q.USABLE / pw["light_off"][1], 1),
                                                   round(total_cell * v / 1000.0 * Q.USABLE / pw["light_off"][0], 1)],
                                        light_on=[round(total_cell * v / 1000.0 * Q.USABLE / (pw["light_off"][1] + pw["light_on_extra"][1]), 1),
                                                  round(total_cell * v / 1000.0 * Q.USABLE / (pw["light_off"][0] + pw["light_on_extra"][0]), 1)])
                                for k, v in Q.CELL_WH_PER_L.items()},
                         power_w=pw)
report["light"] = light_check()
for opt in ("A", "B"):
    hits, tight = collisions(opt)
    report[f"option_{opt}"] = dict(collisions=hits, tight_gaps=tight[:20], mass=mass_report(opt), head_envelope_mm=head_envelope(opt),
                                   v1_head_envelope_mm=V1_HEAD_ENV)
    report[f"option_{opt}"]["parts_mass_g"] = PARTS_MASS[opt]
    print(f"Option {opt}: collisions {len(hits)}, tight {len(tight)}, mass {report[f'option_{opt}']['mass']}, head {report[f'option_{opt}']['head_envelope_mm']}")
    for h in hits:
        print("   HIT", h)
    if not QUICK:
        report[f"option_{opt}"]["pose_collisions"] = pose_hits(opt)
        report[f"option_{opt}"]["line_of_sight"] = los_check(opt)
        print("   poses:", {k: len(v) for k, v in report[f"option_{opt}"]["pose_collisions"].items()},
              " line of sight:", report[f"option_{opt}"]["line_of_sight"])
bb1, bb2 = bm.bbox(bm.shape_of(tub1)), bm.bbox(bm.shape_of(tub))
report["shell_size_mm"] = dict(v1=[round(bb1[i + 3] - bb1[i], 2) for i in range(3)], v2=[round(bb2[i + 3] - bb2[i], 2) for i in range(3)])
report["v1_reference"] = dict(mass_total_g=160.0, mass_head_g=108.8, cell_volume_cm3=17.5, model_commit=V1_COMMIT)
report["leds"] = N_LEDS
# everything the figures script needs to redraw the maps on its own (cameras as pinhole models, LEDs with their solved intensity)
report["cameras_model"] = {n: dict(p=[float(v) for v in c["p"]], X=[float(v) for v in c["X"]], Y=[float(v) for v in c["Y"]],
                                   Z=[float(v) for v in c["Z"]], f_px=float(c["f"]), hfov=c["hfov"], vfov=round(c["vfov"], 2), distortion=c["D"],
                                   text_min_dpi_own_zone=round(float(dpi(c, GX, GY)[np.argmax(np.stack([dpi(k, GX, GY) for k in ALL_CAMS]), 0) == i].min()))
                                   if np.any(np.argmax(np.stack([dpi(k, GX, GY) for k in ALL_CAMS]), 0) == i) else None)
                           for i, (n, c) in enumerate(zip(CAM_NAMES, ALL_CAMS))}
report["light_model"] = LIGHT_SOLUTION
report["page"] = dict(spread_mm=list(Q.SPREAD), text_margin_mm=Q.TEXT_MARGIN, sensor_px=list(Q.SENSOR_PX))
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "model_report_v2.json"), "w") as fh:
    json.dump(report, fh, indent=1)
print(json.dumps({k: report[k] for k in ("camera", "battery", "light")}, indent=1))

# =====================================================================================
#  8. exports: GLB (web viewer), STEP (A and B), STL (new printed parts)
# =====================================================================================
COLORS = dict(bm.COLORS)
COLORS.update({"book_cover": (0.30, 0.36, 0.42), "paper": (0.96, 0.94, 0.88), "zone_near": (0.12, 0.48, 0.52),
               "zone_far": (0.79, 0.54, 0.07)})
METAL = {"steel_brushed", "spring_steel", "screw_steel", "aluminium", "metal_tin", "gold", "pouch_silver"}


def srgb2lin(c):
    return [((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c]


def material(key):
    m = dict(name=key, doubleSided=True, pbrMetallicRoughness=dict(baseColorFactor=srgb2lin(COLORS[key]) + [1.0],
                                                                  metallicFactor=0.6 if key in METAL else 0.0,
                                                                  roughnessFactor=0.35 if key in METAL else 0.55))
    if key in ("glass", "lens_glass"):
        m["pbrMetallicRoughness"]["baseColorFactor"][3] = 0.3
        m["alphaMode"] = "BLEND"
        m["pbrMetallicRoughness"]["roughnessFactor"] = 0.05
    if key.startswith("zone_"):
        m["pbrMetallicRoughness"]["baseColorFactor"][3] = 0.35
        m["alphaMode"] = "BLEND"
    if key == "led_warm":
        m["emissiveFactor"] = [0.9, 0.8, 0.55]
    if key == "diffuser":
        m["pbrMetallicRoughness"]["baseColorFactor"][3] = 0.75
        m["alphaMode"] = "BLEND"
    return m


def export_glb(path):
    import trimesh
    nodes, meshes, accessors, views, mats, matidx = [], [], [], [], [], {}
    blob = bytearray()

    def push(arr, target, comp, typ):
        nonlocal blob
        while len(blob) % 4:
            blob += b"\0"
        off = len(blob)
        blob += arr.tobytes()
        views.append(dict(buffer=0, byteOffset=off, byteLength=arr.nbytes, **({"target": target} if target else {})))
        acc = dict(bufferView=len(views) - 1, componentType=comp, count=int(arr.shape[0]), type=typ)
        if typ == "VEC3" and target == 34962:
            acc["min"] = [float(v) for v in arr.min(0)]
            acc["max"] = [float(v) for v in arr.max(0)]
        accessors.append(acc)
        return len(accessors) - 1

    for b in bm.BODIES:
        if b["variant"] is not None:
            continue
        s = bm.placed(b, U0)
        tol = 0.6 if b["group"] in ("book",) else (0.08 if b["group"] != "views" else 0.2)
        vs, fs = s.tessellate(tol, 0.3)
        if not fs:
            continue
        V = np.array([(p.x, p.y, p.z) for p in vs], dtype=np.float64)
        F = np.array(fs, dtype=np.int64)
        tm = trimesh.Trimesh(V, F, process=True)
        try:
            tm = trimesh.graph.smooth_shade(tm, angle=math.radians(35))
        except Exception:
            pass
        V = np.asarray(tm.vertices)
        Vg = np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1).astype(np.float32) / 1000.0
        N = np.asarray(tm.vertex_normals)
        Ng = np.stack([N[:, 0], N[:, 2], -N[:, 1]], 1).astype(np.float32)
        I = np.asarray(tm.faces, dtype=np.uint32).ravel()
        ap = push(Vg, 34962, 5126, "VEC3")
        an = push(Ng, 34962, 5126, "VEC3")
        ai = push(I, 34963, 5125, "SCALAR")
        if b["mat"] not in matidx:
            matidx[b["mat"]] = len(mats)
            mats.append(material(b["mat"]))
        meshes.append(dict(name=b["name"], primitives=[dict(attributes=dict(POSITION=ap, NORMAL=an), indices=ai, material=matidx[b["mat"]])]))
        if not b.get("v2") and any(b["name"].startswith(k) for k, _ in bm.EXPLODE):
            e = bm.explode_of(b["name"])
        else:
            e = list(b["explode"])
        e = np.array(e, float)
        if b["frame"] == "unit":
            e = np.array([-1, 1, 1]) * (R0 @ (np.array([-1, 1, 1]) * e))   # explode offsets follow the tipped unit
        name = b["name"]
        nodes.append(dict(name=name, mesh=len(meshes) - 1, extras=dict(label=b["label"], group=b["group"], mat=b["mat"],
                                                                     explode=[float(v) / 1000.0 for v in e],
                                                                     option=b.get("option") or "", v2=bool(b.get("v2")))))
    gltf = dict(asset=dict(version="2.0", generator="SenseBook v2 build (CadQuery + trimesh)"), scene=0,
                scenes=[dict(name="SenseBook v2", nodes=list(range(len(nodes))))], nodes=nodes, meshes=meshes, materials=mats,
                accessors=accessors, bufferViews=views, buffers=[dict(byteLength=len(blob))])
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    while len(blob) % 4:
        blob += b"\0"
    with open(path, "wb") as fh:
        fh.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)))
        fh.write(struct.pack("<II", len(js), 0x4E4F534A)); fh.write(js)
        fh.write(struct.pack("<II", len(blob), 0x004E4942)); fh.write(bytes(blob))
    print("glb", path, round(os.path.getsize(path) / 1e6, 2), "MB,", len(nodes), "nodes")


if not QUICK:
    export_glb(os.path.join(OUT, "sensebook_v2.glb"))
    os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)
    for opt in ("A", "B"):
        asm = cq.Assembly(name=f"SenseBook_v2_option_{opt}")
        for b in config_bodies(opt):
            asm.add(bm.placed(b, U0), name=b["name"], color=cq.Color(*COLORS[b["mat"]], 1.0))
        asm.save(os.path.join(OUT, f"SenseBook_v2_option_{opt}.step"))
    for b in bm.BODIES:
        if b.get("v2") and b["printed"] and b["group"] not in ("book", "views"):
            b["shape"].exportStl(os.path.join(OUT, "stl", b["name"] + ".stl"), tolerance=0.01, angularTolerance=0.1)
    print("STEP A/B and STL written to", os.path.abspath(OUT))
