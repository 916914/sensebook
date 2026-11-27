"""SenseBook v4 tri-grip: full parametric 3D model (CadQuery).

Every part is its own body, built from sb_params.py. Run from design/cad:

    ..\\.venv\\Scripts\\python.exe build_model.py            # build, check, export everything
    ..\\.venv\\Scripts\\python.exe build_model.py --quick    # build + checks only (no STEP/STL)

Writes design/cad/out/ (STEP, STL, DXF, model_report.json) and design/cad/build/ (meshes for
the renderer and the web viewer; not committed).

Frames (same as sb_params): UNIT frame for everything inside the unit, BOOK frame for the
stick, hub and legs. sb_params is left-handed (+x = reader's right, +y toward the reader, z up),
so the exported CAD is mirrored once: X_cad = -x (see add()). The default pose is the textbook pose from analysis.py: stick 90 mm,
unit tipped 10.5 deg, hub centred on the page plane, hardcover on a table.

Honesty note: part sizes for bought parts are typical datasheet / breakout sizes (EST).
Nothing here has been built or measured.
"""
from __future__ import annotations

import json
import math
import os
import sys

import cadquery as cq
import numpy as np

import sb_params as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
BUILD = os.path.join(HERE, "build")
S2 = math.sqrt(2.0)
FA = math.radians(P.FACET_ANGLE)
N_OUT = (math.sin(FA), -math.cos(FA))            # facet outward normal (y, z)
T_UP = (math.cos(FA), math.sin(FA))              # in-facet "up" direction (y, z)
TIP0 = 10.5                                      # default tip: best textbook pose from analysis.py
STICK0 = P.STICK_COLLAPSED


# ------------------------------------------------------------------ small helpers
def W(solid):
    return cq.Workplane("XY").add(solid)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(p0, axis, r, h):
    return W(cq.Solid.makeCylinder(r, h, cq.Vector(*p0), cq.Vector(*axis)))


def cyl_x(x0, x1, y, z, r):
    return cyl((x0, y, z), (1, 0, 0), r, x1 - x0)


def cyl_y(y0, y1, x, z, r):
    return cyl((x, y0, z), (0, 1, 0), r, y1 - y0)


def cyl_z(z0, z1, x, y, r):
    return cyl((x, y, z0), (0, 0, 1), r, z1 - z0)


def tube_z(z0, z1, x, y, ro, ri):
    return cyl_z(z0, z1, x, y, ro).cut(cyl_z(z0 - 1, z1 + 1, x, y, ri))


def shape_of(wp):
    objs = [o for o in wp.vals() if isinstance(o, cq.Shape)]
    return objs[0] if len(objs) == 1 else cq.Compound.makeCompound(objs)


def fuse(items):
    out = items[0]
    for it in items[1:]:
        out = out.union(it)
    return out


def group(items):
    """Several solids as one body without fusing them (they do not overlap)."""
    return W(cq.Compound.makeCompound([shape_of(i) for i in items]))


def mirror_x(wp):
    return wp.mirror("YZ")


def to_facet(wp):
    """Local (u = x, v = up the facet, a = depth into the unit) -> unit frame."""
    return wp.rotate((0, 0, 0), (1, 0, 0), P.FACET_ANGLE).translate((0, P.LENS_Y, P.LENS_Z))


def fpt(a, u=0.0, v=0.0):
    """Facet-local point -> unit frame (x, y, z)."""
    return (u, P.LENS_Y - a * N_OUT[0] + v * T_UP[0], P.LENS_Z - a * N_OUT[1] + v * T_UP[1])


def facet_floor(y, inner=True):
    """Lowest z inside the cavity (or the shell) at a given y, set by the lens facet."""
    return y + P.FACET_TOP_Z + (P.WALL * S2 if inner else 0.0)


def wire(points, r=0.55):
    """Round wire bundle along a polyline (cylinders + spheres at the bends)."""
    parts = []
    for a, b in zip(points[:-1], points[1:]):
        d = [b[i] - a[i] for i in range(3)]
        L = math.sqrt(sum(c * c for c in d))
        if L < 1e-6:
            continue
        parts.append(cyl(a, d, r, L))
    for p in points[1:-1]:
        parts.append(W(cq.Solid.makeSphere(r, cq.Vector(0, 0, 0)).translate(cq.Vector(*p))))
    return fuse(parts)


def slot_xy(length, width, z0, z1, x, y, angle=0.0):
    s = cq.Workplane("XY").slot2D(length, width).extrude(z1 - z0)
    return s.rotate((0, 0, 0), (0, 0, 1), angle).translate((x, y, z0))


def slot_yz(length_y, width_z, x0, x1, y, z):
    """Capsule hole through a side wall: long axis along y."""
    s = cq.Workplane("YZ").slot2D(length_y, width_z).extrude(x1 - x0)
    return s.translate((x0, y, z))


def rot_x(wp, deg, y, z):
    """Rotate about an axis parallel to x through (y, z). Positive: y -> z."""
    return wp.rotate((0, y, z), (1, y, z), deg)


# ------------------------------------------------------------------ registry
BODIES: list[dict] = []


def add(name, wp, group_, mat, *, budget, label, mass=None, rho=None, printed=False, frame="unit",
        variant=None, explode=(0, 0, 0)):
    """mass (g) for bought parts, or rho (key of P.RHO) for made parts (mass from volume)."""
    shp = shape_of(wp) if isinstance(wp, cq.Workplane) else wp
    # sb_params uses +x = reader's right with +y toward the reader and z up, which is a left-handed
    # frame. CAD files, meshes and renders are right-handed, so every body is mirrored once here:
    # X_cad = -x. "Left" and "right" in part names always mean the reader's left and right.
    shp = shp.mirror("YZ")
    BODIES.append(dict(name=name, shape=shp, group=group_, mat=mat, budget=budget, label=label,
                       mass=mass, rho=rho, printed=printed, frame=frame, variant=variant,
                       explode=(-explode[0], explode[1], explode[2])))
    return wp


# =====================================================================================
#  UNIT (unit frame)
# =====================================================================================
def unit_solid(i=0.0):
    """Outer envelope inset by i (i = WALL gives the cavity)."""
    b = cq.Workplane("XY").box(P.UNIT_W - 2 * i, P.UNIT_D - 2 * i, P.UNIT_H - 2 * i,
                               centered=(True, False, False)).translate((0, -P.UNIT_D + i, i))
    b = b.edges("|Y").fillet(P.R_FRONT - i)
    b = b.faces(">Y").edges().fillet(P.R_EDGE - i)
    b = b.faces("<Y").edges().fillet(P.R_EDGE - i)
    c = P.FACET_TOP_Z + i * S2
    cutter = cq.Workplane("YZ").polyline([(-90, -90 + c), (50, 50 + c), (50, -200), (-90, -200)]).close() \
        .extrude(100, both=True)
    return b.cut(cutter)


def build_unit():
    wall = P.WALL
    outer, inner = unit_solid(0.0), unit_solid(wall)
    shell = outer.cut(inner)
    tub = shell.intersect(box(-60, 60, P.SEAM_Y, 20, -30, 60))
    cover = shell.intersect(box(-60, 60, -60, P.SEAM_Y, -30, 60))

    # ---- tilt lugs under the flat bottom (pivot axis along x)
    py, pz = P.PIVOT_Y, P.PIVOT_Z
    lug2d = (cq.Workplane("YZ").polyline([(py - 6, 0.6), (py + 2.9, 0.6), (py + 3.4, pz), (py - 4.3, pz)]).close()
             .extrude(P.LUG_T).union(cq.Workplane("YZ").circle(4.3).extrude(P.LUG_T).translate((0, py, pz))))
    lug = lug2d.translate((P.LUG_GAP / 2, 0, 0))
    lugs = lug.union(mirror_x(lug)).cut(cyl_x(-20, 20, py, pz, P.PIVOT_PIN_D / 2 + 0.1))
    tub = tub.union(lugs)

    # ---- cover screw bosses (M2 self-tapping from the back)
    boss_pts = [(40.0, 22.0), (-40.0, 22.0), (9.0, 36.0), (-9.0, 36.0)]
    boss_keep = []
    for (bx, bz) in boss_pts:
        b = cyl_y(P.SEAM_Y, P.SEAM_Y + 7.0, bx, bz, 2.0)
        if abs(bx) > 30:
            web = box(min(bx, bx + math.copysign(2.4, bx)), max(bx, bx + math.copysign(2.4, bx)),
                      P.SEAM_Y, P.SEAM_Y + 7.0, bz - 2.0, bz + 2.0)
        else:
            web = box(bx - 2.0, bx + 2.0, P.SEAM_Y, P.SEAM_Y + 6.5, bz, bz + 2.4)
        b = b.union(web).intersect(unit_solid(wall - 0.2))
        tub = tub.union(b)
        boss_keep.append(box(bx - 2.4, bx + 2.4, P.SEAM_Y - 1, P.SEAM_Y + 8, bz - 2.4, bz + 2.8))
        tub = tub.cut(cyl_y(P.SEAM_Y - 1, P.SEAM_Y + 6.5, bx, bz, 0.8))
        cover = cover.cut(cyl_y(-40, P.SEAM_Y + 1, bx, bz, 1.15))
        cover = cover.cut(cyl_y(-40, -P.UNIT_D + 1.0, bx, bz, 2.1))

    # ---- cover tongue (locates the cover in the tub)
    g, t = P.TONGUE_GAP, P.TONGUE_T
    tongue = unit_solid(wall + g).cut(unit_solid(wall + g + t)).intersect(
        box(-60, 60, P.SEAM_Y - 0.5, P.SEAM_Y + P.TONGUE_H, -30, 60))
    tongue = tongue.cut(box(-29, 29, -60, 20, 0, P.PI_Z0 + 0.3))          # Pi connector edge
    for k in boss_keep:
        tongue = tongue.cut(k)
    cover = cover.union(tongue)

    # ---- Pi standoffs on the cover (M2.5)
    pi_holes = [(sx * (P.PI_L / 2 - 3.5), P.PI_Z0 + zz) for sx in (-1, 1) for zz in (3.5, P.PI_Wd - 3.5)]
    pi_top_y = P.PI_PCB_Y - P.PI_TH                                       # component-side face of the PCB
    for (hx, hz) in pi_holes:
        post = cyl_y(-P.UNIT_D + wall - 0.2, pi_top_y, hx, hz, 2.3).union(cyl_y(pi_top_y, P.PI_PCB_Y + 0.4, hx, hz, 1.25))
        cover = cover.union(post)

    # ---- lens opening, camera posts
    tub = tub.cut(to_facet(cq.Workplane("XY").circle(P.RING_OD / 2 + 0.1).extrude(6).translate((0, 0, -2))))
    cam_face = P.CAM_LENS_RECESS + P.CAM_STACK                            # depth of the board front face
    for su in (-1, 1):
        for v in P.CAM_POST_V:
            p = cq.Workplane("XY").circle(1.6).extrude(cam_face - wall + 0.3).translate((su * P.CAM_POST_U, v, wall - 0.3))
            p = p.cut(cq.Workplane("XY").circle(0.75).extrude(6).translate((su * P.CAM_POST_U, v, cam_face - 6)))
            tub = tub.union(to_facet(p))
        web = cq.Workplane("XY").box(1.2, P.CAM_POST_V[1] - P.CAM_POST_V[0], cam_face - 7.0, centered=(True, False, False)) \
            .translate((su * P.CAM_POST_U, P.CAM_POST_V[0], 7.0))
        tub = tub.union(to_facet(web))

    # ---- openings in the tub
    for dx in P.DOT_X:                                                    # status dots
        tub = tub.cut(cyl_y(-4, 2, dx, P.DOT_Z, P.DOT_D / 2 + 0.05))
    sx, sz = P.SPK_XZ                                                     # speaker grille
    for i in range(7):
        for j in range(4):
            tub = tub.cut(cyl_y(-4, 2, sx + (i - 3) * 2.6, sz + (j - 1.5) * 2.6, 0.5))
    tub = tub.cut(cyl_z(36, 42, P.ASK_XY[0], P.ASK_XY[1], P.ASK_D / 2 + 0.15))
    tub = tub.cut(slot_xy(P.PLAY_SIZE[0] + 0.3, P.PLAY_SIZE[1] + 0.3, 36, 42, *P.PLAY_XY))
    for s in (-1, 1):
        tub = tub.cut(cyl_z(36, 42, s * P.NAV_X, P.NAV_Y, P.NAV_D / 2 + 0.15))
        tub = tub.cut(cyl_z(36, 42, s * P.MIC_X, P.MIC_Y, 0.5))           # mic ports
    for vz in P.VOL_Z:                                                    # left side: volume
        tub = tub.cut(slot_yz(P.VOL_SIZE[0] + 0.3, P.VOL_SIZE[1] + 0.3, -46, -40, P.VOL_Y, vz))
    tub = tub.cut(box(-46, -40, P.MUTE_Y - 3.6, P.MUTE_Y + 3.6, P.MUTE_Z - 1.5, P.MUTE_Z + 1.5))   # mute slot
    tub = tub.cut(box(40, 46, P.USB_Y - 1.85, P.USB_Y + 1.85, P.USB_Z - 4.7, P.USB_Z + 4.7))      # USB-C
    tub = tub.cut(cyl_x(40, 46, P.JACK_Y, P.JACK_Z, 3.1))                                         # 3.5 mm jack
    tub = tub.cut(cyl_z(-2, 3, -10.0, -21.0, 1.3))                                                # hub cord entry

    add("shell_front_tub", tub, "unit", "abs_teal", budget="unit_shells", rho="petg", printed=True,
        label="Front shell (tub): front face, lens facet, top, sides, tilt lugs", explode=(0, 34, 0))
    add("shell_back_cover", cover, "unit", "abs_teal", budget="unit_shells", rho="petg", printed=True,
        label="Back cover with Pi standoffs", explode=(0, -46, 0))
    for n, (bx, bz) in enumerate(boss_pts):
        s = cyl_y(-P.UNIT_D + 0.2, -P.UNIT_D + 0.2 + 8.0, bx, bz, 0.95).union(cyl_y(-P.UNIT_D + 0.2, -P.UNIT_D + 1.0, bx, bz, 1.9))
        add(f"cover_screw_{n + 1}", s, "unit", "screw_black", budget="spreader_wiring", mass=0.15,
            label="Cover screws, M2 x 8 self-tapping (4)", explode=(0, -60, 0))

    # ---- lens window, bezel, light-ring diffuser
    win = to_facet(cq.Workplane("XY").circle(P.LENS_WIN_D / 2).extrude(0.8).translate((0, 0, 0.3)))
    add("lens_window", win, "unit", "glass", budget="unit_shells", rho="pmma",
        label="Lens window, 14 mm clear disc", explode=(0, 30, -30))
    bez = cq.Workplane("XY").circle(P.RING_ID / 2).circle(6.3).extrude(0.3) \
        .union(cq.Workplane("XY").circle(P.RING_ID / 2).circle(P.LENS_WIN_D / 2 + 0.05).extrude(1.0).translate((0, 0, 0.3)))
    add("lens_bezel", to_facet(bez), "unit", "blue_ring", budget="unit_shells", rho="al",
        label="Lens bezel ring (pale blue)", explode=(0, 34, -34))
    dif = cq.Workplane("XY").circle(P.RING_OD / 2).circle(P.RING_ID / 2).extrude(wall + 0.6)   # plain ring, glued in
    add("light_ring_diffuser", to_facet(dif), "unit", "diffuser", budget="unit_shells", rho="petg", printed=True,
        label="Light-ring diffuser (print in natural/clear PETG)", explode=(0, 26, -26))

    # ---- light-ring LED board
    ring = cq.Workplane("XY").circle(10.0).circle(7.3).extrude(1.0).translate((0, 0, 3.6))
    add("light_ring_pcb", to_facet(ring), "unit", "pcb_white", budget="leds_buttons_motor", mass=0.5,
        label="Light-ring LED board (8 warm-white LEDs, PWM on GPIO 12)", explode=(0, 20, -20))
    leds = []
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        l = cq.Workplane("XY").box(3.0, 1.4, 0.8, centered=(True, True, False)).rotate((0, 0, 0), (0, 0, 1), math.degrees(a) + 90) \
            .translate((8.65 * math.cos(a), 8.65 * math.sin(a), 2.8))
        leds.append(to_facet(l))
    add("light_ring_leds", group(leds), "unit", "led_warm", budget="leds_buttons_motor", mass=0.2,
        label="Light-ring LEDs", explode=(0, 20, -20))

    # ---- camera: lens, holder, board, connector
    r0 = P.CAM_LENS_RECESS
    lens_len = P.CAM_STACK - P.CAM_HOLDER_H
    lens = cq.Workplane("XY").circle(P.CAM_LENS_D / 2).extrude(lens_len + 3.0).translate((0, 0, r0)) \
        .cut(cq.Workplane("XY").circle(5.0).extrude(0.6).translate((0, 0, r0 - 0.01)))
    add("camera_lens_m12", to_facet(lens), "unit", "lens_black", budget="camera_m12", mass=5.0,
        label="M12 ultra-wide lens (~120 deg, supplier part TBD)", explode=(0, 12, -12))
    glass = cq.Workplane("XY").circle(4.9).extrude(0.45).translate((0, 0, r0 + 0.1))
    add("camera_lens_glass", to_facet(glass), "unit", "lens_glass", budget="camera_m12", mass=0.2,
        label="Lens front element", explode=(0, 12, -12))
    hold = cq.Workplane("XY").rect(P.CAM_HOLDER, P.CAM_HOLDER).extrude(P.CAM_HOLDER_H).translate((0, 0, r0 + lens_len)) \
        .cut(cq.Workplane("XY").circle(P.CAM_LENS_D / 2 + 0.02).extrude(3.2).translate((0, 0, r0 + lens_len - 0.1)))
    add("camera_holder_m12", to_facet(hold), "unit", "plastic_black", budget="camera_m12", mass=1.8,
        label="M12 lens holder", explode=(0, 6, -6))
    v0, v1 = P.CAM_V_MIN, P.CAM_V_MIN + P.CAM_BOARD_T
    brd = box(-P.CAM_BOARD_X / 2, P.CAM_BOARD_X / 2, v0, v1, cam_face, cam_face + P.CAM_BOARD_TH)
    for su in (-1, 1):
        for v in P.CAM_POST_V:
            brd = brd.cut(cyl_z(cam_face - 1, cam_face + 3, su * P.CAM_POST_U, v, 1.1))
    add("camera_board_imx708", to_facet(brd), "unit", "pcb_black", budget="camera_m12", mass=1.6,
        label="Camera board, 12 MP IMX708 (25 x 24 mm class, EST)")
    back = cam_face + P.CAM_BOARD_TH
    conn = box(-8.5, 8.5, 2.0, 6.0, back, back + 1.8)
    passives = box(-7, 7, -6.5, -1.0, back, back + 0.6)
    add("camera_connector", group([to_facet(conn), to_facet(passives)]), "unit", "ic_black", budget="camera_m12", mass=0.4,
        label="Camera flex connector")
    scr = []
    for su in (-1, 1):
        for v in P.CAM_POST_V:
            scr.append(to_facet(cyl_z(back, back + 1.0, su * P.CAM_POST_U, v, 1.7).union(
                cyl_z(back - 5.5, back, su * P.CAM_POST_U, v, 0.74))))
    add("camera_screws", group(scr), "unit", "screw_black", budget="spreader_wiring", mass=0.3,
        label="Camera screws, M1.6 x 5 (4)", explode=(0, -8, 8))

    # ---- Pi Zero 2 W (components face the back cover)
    yb, yt = P.PI_PCB_Y, pi_top_y                 # underside (toward camera), component face (toward cover)
    z0 = P.PI_Z0

    def pb(bx0, bx1, by0, by1, h):                # board coords (from SD end, from connector edge) -> unit box
        return box(P.PI_L / 2 - bx1, P.PI_L / 2 - bx0, yt - h, yt, z0 + by0, z0 + by1)

    pcb = box(-P.PI_L / 2, P.PI_L / 2, yt, yb, z0, z0 + P.PI_Wd).edges("|Y").fillet(3.0)
    for (hx, hz) in pi_holes:
        pcb = pcb.cut(cyl_y(yt - 1, yb + 1, hx, hz, 1.35))
    add("pi_zero_2w_pcb", pcb, "unit", "pcb_green", budget="pi_zero_2w", mass=10.4,
        label="Raspberry Pi Zero 2 W", explode=(0, -22, 0))
    chips = group([pb(22, 37, 7.5, 22.5, 1.3), pb(44, 56, 11, 23, 1.5), pb(61, 65, 6.5, 23.5, 1.3)])
    add("pi_zero_2w_chips", chips, "unit", "ic_black", budget="pi_zero_2w", mass=0.0,
        label="Pi: RP3A0 SiP, radio can, camera connector", explode=(0, -22, 0))
    conns = group([pb(6.8, 18.0, -0.5, 7.1, 3.2), pb(37.65, 45.15, -0.6, 5.0, 2.6), pb(50.25, 57.75, -0.6, 5.0, 2.6),
                   pb(0.0, 12.0, 11.25, 22.75, 1.4)])
    add("pi_zero_2w_connectors", conns, "unit", "metal_tin", budget="pi_zero_2w", mass=0.0,
        label="Pi: mini-HDMI, 2 micro-USB, microSD slot (not used in normal use)", explode=(0, -22, 0))
    gpio = box(-P.PI_L / 2 + 7, P.PI_L / 2 - 7, yb, yb + 0.05, z0 + 24.2, z0 + 29.2)
    add("pi_gpio_pads", gpio, "unit", "gold", budget="pi_zero_2w", mass=0.0,
        label="Pi GPIO pads (wires soldered here)", explode=(0, -22, 0))
    sd = box(P.PI_L / 2 - 10.0, P.PI_L / 2 + 2.3, yt - 1.25, yt - 0.45, z0 + 11.5, z0 + 22.5)
    sd = sd.cut(box(P.PI_L / 2 - 12.0, P.PI_L / 2, yt - 1.4, yt, z0 + 11.25, z0 + 22.75).intersect(sd)) \
        if False else box(P.PI_L / 2, P.PI_L / 2 + 2.3, yt - 1.25, yt - 0.45, z0 + 11.5, z0 + 22.5)
    add("microsd_card", sd, "unit", "ic_black", budget="pi_zero_2w", mass=0.3,
        label="microSD card, 32 GB", explode=(14, -22, 0))
    # ---- heat spreader + thermal pad (SiP -> pad -> aluminium plate on the cover)
    sip_x0, sip_x1 = P.PI_L / 2 - 37, P.PI_L / 2 - 22
    spx = (sip_x0 + sip_x1) / 2 + 2.0
    spr = box(spx - P.SPREADER[0] / 2, spx + P.SPREADER[0] / 2, -P.UNIT_D + wall, -P.UNIT_D + wall + P.SPREADER[2],
              12.0, 12.0 + P.SPREADER[1])
    add("heat_spreader", spr, "unit", "aluminium", budget="spreader_wiring", rho="al",
        label="Aluminium heat spreader, 40 x 22 x 1 mm, bonded to the cover", explode=(0, -34, 0))
    pad = box(sip_x0, sip_x1, -P.UNIT_D + wall + P.SPREADER[2], yt - 1.3, z0 + 7.5, z0 + 22.5)
    add("thermal_pad", pad, "unit", "pad_grey", budget="spreader_wiring", mass=0.4,
        label="Thermal pad, 15 x 15 x 1 mm", explode=(0, -28, 0))

    # ---- cells
    cx0, cy1, cz0 = P.CELL_X0, P.CELL_Y1, P.CELL_Z0
    cell = box(cx0, cx0 + P.CELL[0], cy1 - P.CELL[1], cy1, cz0, cz0 + P.CELL[2]).edges().fillet(1.5)
    pcm = box(cx0 + 2.5, cx0 + 22.5, cy1, cy1 + 0.9, cz0 + 28.0, cz0 + 32.0)
    add("cell_right", cell, "unit", "pouch_silver", budget="lipo_2x102535", mass=17.0,
        label="LiPo cell 102535 (right)", explode=(30, 0, 0))
    add("cell_left", mirror_x(cell), "unit", "pouch_silver", budget="lipo_2x102535", mass=17.0,
        label="LiPo cell 102535 (left)", explode=(-30, 0, 0))
    add("cell_pcm_right", pcm, "unit", "kapton", budget="lipo_2x102535", mass=0.0,
        label="Cell protection board, folded onto the front face", explode=(30, 0, 0))
    add("cell_pcm_left", mirror_x(pcm), "unit", "kapton", budget="lipo_2x102535", mass=0.0,
        label="Cell protection board, folded onto the front face", explode=(-30, 0, 0))

    # ---- speaker
    spk = box(sx - P.SPK[0] / 2, sx + P.SPK[0] / 2, -wall - 0.1 - P.SPK[1], -wall - 0.1, sz - P.SPK[2] / 2, sz + P.SPK[2] / 2) \
        .edges("|Y").fillet(2.0)
    add("speaker", spk, "unit", "speaker", budget="speaker", mass=2.8,
        label="Micro speaker, 20 x 14 x 4 mm, 8 ohm 1 W", explode=(0, 18, 0))

    # ---- audio boards (left front): MAX98357A amp, I2S headphone DAC
    amp = box(-37, -19, -7.6, -6.6, 13.5, 31.5)
    amp_parts = group([box(-30, -26, -9.2, -7.6, 20, 24), box(-35, -32, -9.4, -7.6, 15, 19), box(-24, -21, -8.6, -7.6, 26, 29)])
    add("amp_board_max98357a", amp, "unit", "pcb_blue", budget="audio_boards", mass=1.4,
        label="MAX98357A I2S speaker amp breakout", explode=(-16, 12, 0))
    add("amp_board_parts", amp_parts, "unit", "ic_black", budget="audio_boards", mass=0.2,
        label="Amp parts", explode=(-16, 12, 0))
    dac = box(-37, -17, -12.6, -11.6, 10.5, 22.5)
    dac_parts = group([box(-31, -25, -14.0, -12.6, 14, 19), box(-22, -19, -14.2, -12.6, 12, 16)])
    add("dac_board_pcm5102", dac, "unit", "pcb_purple", budget="audio_boards", mass=1.8,
        label="I2S headphone DAC breakout (PCM5102-class)", explode=(-26, 4, -6))
    add("dac_board_parts", dac_parts, "unit", "ic_black", budget="audio_boards", mass=0.2,
        label="DAC parts", explode=(-26, 4, -6))

    # ---- microphones (under the top, ports up)
    mic = box(27.5, 36.5, -12, -4, 35.6, 36.4)
    mic_can = box(P.MIC_X - 1.9, P.MIC_X + 1.9, P.MIC_Y - 1.5, P.MIC_Y + 1.5, 36.4, 37.5)
    add("mic_right", group([mic, mic_can]), "unit", "pcb_blue", budget="audio_boards", mass=0.5,
        label="I2S MEMS microphone (right)", explode=(8, 8, 14))
    add("mic_left", mirror_x(group([mic, mic_can])), "unit", "pcb_blue", budget="audio_boards", mass=0.5,
        label="I2S MEMS microphone (left)", explode=(-8, 8, 14))

    # ---- power board (charger + 5 V boost) with USB-C, fuel gauge
    pwr = box(15, 41, -13.6, -12.6, 16.5, 32.5)
    pwr_parts = group([box(22, 27, -15.6, -13.6, 20, 25), box(30, 34, -15.0, -13.6, 26, 30), box(17, 20, -14.8, -13.6, 18, 22)])
    usb = box(34.9, 42.25, -12.6, -9.3, P.USB_Z - 4.47, P.USB_Z + 4.47).edges("|X").fillet(1.2)
    add("power_board", pwr, "unit", "pcb_blue", budget="power_boards", mass=2.2,
        label="Charger + 5 V boost board (1S LiPo, USB-C, <= 26 x 16 mm, EST)", explode=(22, 6, 0))
    add("power_board_parts", pwr_parts, "unit", "ic_black", budget="power_boards", mass=0.4,
        label="Charger / boost parts", explode=(22, 6, 0))
    add("usb_c_receptacle", usb, "unit", "metal_tin", budget="power_boards", mass=0.5,
        label="USB-C receptacle (charging, power-bank use)", explode=(22, 6, 0))
    gau = box(-6.5, 6.5, -27.6, -17.7, 2.3, 3.1)
    gau_ic = box(-1.5, 1.5, -23.5, -21.0, 3.1, 3.9)
    add("fuel_gauge_max17048", group([gau, gau_ic]), "unit", "pcb_red", budget="power_boards", mass=0.7,
        label="MAX17048 fuel gauge (I2C, optional)", explode=(0, 0, -22))

    # ---- status dots: LED strip board + four light pipes
    dots = box(-37, -13, -3.6, -2.6, 30.0, 35.0)
    dled = group([box(dx - 0.8, dx + 0.8, -2.6, -2.05, P.DOT_Z - 0.4, P.DOT_Z + 0.4) for dx in P.DOT_X])
    add("status_led_board", dots, "unit", "pcb_white", budget="leds_buttons_motor", mass=0.4,
        label="Status LED board (ready, listening, sending, battery)", explode=(-6, 14, 8))
    add("status_leds", dled, "unit", "led_warm", budget="leds_buttons_motor", mass=0.05,
        label="Status LEDs", explode=(-6, 14, 8))
    pipes = group([cyl_y(-2.0, 0.0, dx, P.DOT_Z, P.DOT_D / 2) for dx in P.DOT_X])
    add("status_dot_pipes", pipes, "unit", "dot_white", budget="unit_shells", rho="petg", printed=True,
        label="Four status-dot light pipes (clear)", explode=(-6, 44, 8))

    # ---- top buttons: caps, switches, boards
    top_in = P.UNIT_H - wall                       # inner top surface
    zc0 = top_in - 1.0                             # underside of the cap flanges

    def tact(x, y):
        return box(x - 2, x + 2, y - 2, y + 2, zc0 - 1.6, zc0)

    ax, ay = P.ASK_XY
    ask = cyl_z(zc0, P.UNIT_H + 0.6, ax, ay, P.ASK_D / 2).union(cyl_z(zc0, top_in, ax, ay, P.ASK_D / 2 + 1.0))
    dish = W(cq.Solid.makeSphere(16.0, cq.Vector(0, 0, 0)).translate(cq.Vector(ax, ay, P.UNIT_H + 0.6 + 16.0 - 1.1)))
    ask = ask.cut(dish).union(cyl_z(P.UNIT_H - 0.6, P.UNIT_H + 0.1, ax, ay, 1.0))
    add("button_ask", ask, "unit", "marigold", budget="unit_shells", rho="petg", printed=True,
        label="Ask button (concave, marigold, raised dot): hold to talk", explode=(0, 0, 26))
    px, pyy = P.PLAY_XY
    play = slot_xy(P.PLAY_SIZE[0], P.PLAY_SIZE[1], zc0, P.UNIT_H + 0.8, px, pyy) \
        .union(slot_xy(P.PLAY_SIZE[0] + 1.6, P.PLAY_SIZE[1] + 1.6, zc0, top_in, px, pyy)) \
        .union(box(px - 3.0, px + 3.0, pyy - 0.45, pyy + 0.45, P.UNIT_H + 0.8, P.UNIT_H + 1.3))
    add("button_play_pause", play, "unit", "abs_light", budget="unit_shells", rho="petg", printed=True,
        label="Play / Pause (bar with a ridge)", explode=(0, 0, 22))
    for s, nm, lab in ((-1, "back", "Back (arrow pointing left)"), (1, "forward", "Forward (arrow pointing right)")):
        nx = s * P.NAV_X
        cap = cyl_z(zc0, P.UNIT_H + 0.8, nx, P.NAV_Y, P.NAV_D / 2).union(cyl_z(zc0, top_in, nx, P.NAV_Y, P.NAV_D / 2 + 1.0))
        tri = cq.Workplane("XY").polyline([(s * 2.2, 0), (-s * 1.6, 2.4), (-s * 1.6, -2.4)]).close().extrude(0.6) \
            .translate((nx, P.NAV_Y, P.UNIT_H + 0.8))
        add(f"button_{nm}", cap.union(tri), "unit", "abs_light", budget="unit_shells", rho="petg", printed=True,
            label=lab, explode=(0, 0, 22))
    ask_pcb = box(-6, 6, -23, -3.5, zc0 - 2.4, zc0 - 1.6)
    add("top_button_board", ask_pcb, "unit", "pcb_green2", budget="leds_buttons_motor", mass=0.5,
        label="Button board: Ask + Play/Pause", explode=(0, 0, 14))
    add("top_button_switches", group([tact(ax, ay), tact(px, pyy)]), "unit", "ic_black", budget="leds_buttons_motor", mass=0.1,
        label="Tact switches: Ask, Play/Pause", explode=(0, 0, 14))
    for s, nm in ((-1, "back"), (1, "forward")):
        nx = s * P.NAV_X
        b = box(nx - 3.5, nx + 3.5, P.NAV_Y - 4, P.NAV_Y + 4, zc0 - 2.4, zc0 - 1.6)
        add(f"{nm}_button_board", group([b, tact(nx, P.NAV_Y)]), "unit", "pcb_green2", budget="leds_buttons_motor", mass=0.25,
            label=f"Button board: {nm.capitalize()}", explode=(0, 0, 14))

    # ---- left side: volume buttons, mic-mute slide switch
    xin = -P.UNIT_W / 2 + wall
    for vz, nm, lab in ((P.VOL_Z[0], "vol_up", "Volume + (raised dot)"), (P.VOL_Z[1], "vol_down", "Volume -")):
        cap = slot_yz(P.VOL_SIZE[0], P.VOL_SIZE[1], -P.UNIT_W / 2 - 0.7, xin + 1.0, P.VOL_Y, vz) \
            .union(slot_yz(P.VOL_SIZE[0] + 1.6, P.VOL_SIZE[1] + 1.6, xin, xin + 1.0, P.VOL_Y, vz))
        if nm == "vol_up":
            cap = cap.union(cyl_x(-P.UNIT_W / 2 - 1.2, -P.UNIT_W / 2 - 0.6, P.VOL_Y, vz, 0.8))
        add(f"button_{nm}", cap, "unit", "abs_light", budget="unit_shells", rho="petg", printed=True,
            label=lab, explode=(-22, 0, 0))
    vol_pcb = box(xin + 2.6, xin + 3.4, P.VOL_Y - 4, P.VOL_Y + 4, 16.5, 31.5)
    vol_sw = group([box(xin + 1.0, xin + 2.6, P.VOL_Y - 2, P.VOL_Y + 2, vz - 2, vz + 2) for vz in P.VOL_Z])
    add("volume_board", group([vol_pcb, vol_sw]), "unit", "pcb_green2", budget="leds_buttons_motor", mass=0.5,
        label="Volume switch board", explode=(-12, 0, 0))
    mute = box(xin, xin + 3.6, P.MUTE_Y - 3.4, P.MUTE_Y + 3.4, P.MUTE_Z - 1.4, P.MUTE_Z + 1.4)
    add("mic_mute_switch", mute, "unit", "metal_tin", budget="leds_buttons_motor", mass=0.4,
        label="Mic-mute slide switch (GPIO 16, low = muted)", explode=(-12, 0, 0))
    knob = box(-P.UNIT_W / 2 - 1.0, xin, P.MUTE_Y - 3.0, P.MUTE_Y - 0.2, P.MUTE_Z - 1.1, P.MUTE_Z + 1.1)
    add("mic_mute_slider", knob, "unit", "abs_light", budget="unit_shells", rho="petg", printed=True,
        label="Mic-mute slider cap", explode=(-22, 0, 0))
    flag = box(-P.UNIT_W / 2 + 0.25, -P.UNIT_W / 2 + 0.75, P.MUTE_Y + 0.4, P.MUTE_Y + 3.2, P.MUTE_Z - 1.1, P.MUTE_Z + 1.1)
    add("mic_mute_flag", flag, "unit", "orange_flag", budget="unit_shells", mass=0.02,
        label="Orange flag: shows when the mic is muted", explode=(-22, 0, 0))

    # ---- right side: headphone jack
    jack = box(30.0, P.UNIT_W / 2 - wall, P.JACK_Y - 3, P.JACK_Y + 3, P.JACK_Z - 2.5, P.JACK_Z + 2.5) \
        .union(cyl_x(P.UNIT_W / 2 - wall, P.UNIT_W / 2 - 0.2, P.JACK_Y, P.JACK_Z, 2.9)) \
        .cut(cyl_x(34, P.UNIT_W / 2 + 1, P.JACK_Y, P.JACK_Z, 1.8))
    add("headphone_jack", jack, "unit", "plastic_black", budget="leds_buttons_motor", mass=1.2,
        label="3.5 mm headphone jack with detect switch (GPIO 7)", explode=(20, 0, -6))

    # ---- haptic motor
    mot = cyl_y(-wall - 0.1 - 2.7, -wall - 0.1, -27.0, 24.0, 5.0)
    add("haptic_motor", mot, "unit", "metal_tin", budget="leds_buttons_motor", mass=0.9,
        label="Coin vibration motor, 10 x 2.7 mm (GPIO 11 via transistor)", explode=(-10, 20, -4))

    # ---- wiring routes (indicative: main bundles only)
    zt = P.PI_Z0 + P.PI_Wd                          # Pi top edge
    yh = -P.UNIT_D + wall + 1.3                     # channel behind the Pi's top edge, inside the cover
    for s_, nm, lab, tail in ((-1, "left", "Harness, left: I2S, buttons, LEDs, motor, mics",
                               [(-38.0, -15.0, 33.0), (-30.0, -10.5, 33.2), (-28.0, -8.6, 32.3)]),
                              (1, "right", "Harness, right: 5 V, I2C, jack detect, Forward",
                               [(39.5, -14.8, 31.5), (36.0, -14.5, 31.5)])):
        pts = [(s_ * 3, yb + 0.8, zt - 2.5), (s_ * 3, yb + 0.8, zt + 0.5), (s_ * 3, yh, zt + 0.45), (s_ * 36, yh, zt + 0.45),
               (s_ * 39.6, yh, 33.0), (s_ * 40.3, -29.0, 29.5), (s_ * 40.3, -17.5, 29.5)] + tail
        add(f"harness_{nm}", wire(pts, 0.7), "unit", "wire_multi", budget="spreader_wiring", mass=0.8,
            label=lab, explode=(s_ * 4, -4, 10))
    bat = wire([(-25.0, cy1 + 1.6, 33.6), (-13.5, cy1 + 1.6, 33.9), (13.5, cy1 + 1.6, 33.9), (25.0, cy1 + 1.6, 33.6),
                (25.0, cy1 + 1.6, 31.0), (25.0, -14.2, 31.0)], 0.5)
    add("battery_leads", bat, "unit", "wire_red", budget="spreader_wiring", mass=0.4,
        label="Battery leads to the power board", explode=(0, 0, 8))
    sp = wire([(-28.0, -6.0, 32.2), (-14.0, -3.0, 36.6), (14.0, -3.0, 36.6), (22.0, -4.0, 35.0), (26.0, -4.4, 34.6)], 0.45)
    add("speaker_leads", sp, "unit", "wire_black", budget="spreader_wiring", mass=0.2,
        label="Speaker leads from the amp", explode=(0, 6, 10))
    hp = wire([(-27.0, -14.8, 12.0), (-12.1, -15.6, 8.6), (-11.9, -22.6, 6.0), (11.9, -22.6, 6.0), (12.1, -15.6, 8.6),
               (29.4, -13.2, 12.2)], 0.4)
    add("headphone_leads", hp, "unit", "wire_black", budget="spreader_wiring", mass=0.2,
        label="Headphone leads from the DAC to the jack", explode=(0, 0, -10))
    hub_tail = wire([(-10.0, -21.0, 6.0), (-10.0, -21.0, -2.5), (-10.0, -25.0, -7.0), (-5.0, -27.5, -10.5), (-1.5, -25.5, -11.5)], 0.6)
    add("hub_cord_tail", hub_tail, "unit", "wire_black", budget="stick_tubes_cord", mass=0.3,
        label="Hub-sensor cord, tail into the unit", explode=(0, 0, -14))
    # camera flex: from the Pi camera connector, folded back along the Pi underside, then up to the camera board
    fz0, fz1 = z0 + 9.3, z0 + 20.8
    cb = cam_face + P.CAM_BOARD_TH + 1.0
    cy_, cz_ = fpt(cb, 0, 5.6)[1:]
    rib = cq.Workplane("YZ").polyline([(yb + 0.2, fz1 - 2.0), (yb + 0.35, fz1 - 2.2), (cy_ + 0.1, cz_ - 0.1), (cy_, cz_ + 0.1)]).close() \
        .extrude(5.75, both=True)
    fx = group([box(-P.PI_L / 2 - 2.6, -P.PI_L / 2 + 1.0, yt - 0.9, yt - 0.75, fz0, fz1),
                box(-P.PI_L / 2 - 2.6, -P.PI_L / 2 - 2.45, yt - 0.9, yb + 0.35, fz0, fz1),
                box(-P.PI_L / 2 - 2.6, 5.75, yb + 0.2, yb + 0.35, fz0, fz1), rib])
    add("camera_flex", fx, "unit", "flex_amber", budget="spreader_wiring", mass=0.5,
        label="Camera flex, 22-pin (Pi Zero cable), folded along the Pi", explode=(0, -14, 0))
    return tub, cover


# =====================================================================================
#  STICK, JOINT, HUB, BLADES, REAR LEG (book frame, default pose)
# =====================================================================================
def blade_shape(drop):
    """Right-hand blade (x > 0) for a given step height between the hub and the cover."""
    bx, hw, t = P.BLADE_X, P.BLADE_W / 2, P.BLADE_T
    zr = P.BLADE_ROOT_Z
    zf = zr - drop
    yv, R = -0.7, min(2.0, drop / 2 - 0.05)
    root = box(bx - hw, bx + hw, P.BLADE_ROOT_Y, yv - R, zr - t / 2, zr + t / 2)
    root = root.cut(cyl_z(zr - 2, zr + 2, bx, -31.2, 1.1))                         # clamp-screw hole
    # step: centre-line in (y, z), offset to a closed polygon, extruded across the blade width
    cl = []
    for k in range(9):
        a = math.radians(90 - 90 * k / 8)
        cl.append((yv - R + R * math.cos(a), zr - R + R * math.sin(a)))
    for k in range(9):
        a = math.radians(180 + 90 * k / 8)
        cl.append((yv + R + R * math.cos(a), zf + R + R * math.sin(a)))
    up, dn = [], []
    for i, (y, z) in enumerate(cl):
        y0, z0 = cl[max(i - 1, 0)]
        y1, z1 = cl[min(i + 1, len(cl) - 1)]
        dy, dz = y1 - y0, z1 - z0
        L = math.hypot(dy, dz)
        ny, nz = -dz / L, dy / L
        up.append((y + ny * t / 2, z + nz * t / 2))
        dn.append((y - ny * t / 2, z - nz * t / 2))
    step = cq.Workplane("YZ").polyline(up + dn[::-1]).close().extrude(2 * hw).translate((bx - hw, 0, 0))
    # flat run under the pages: in-plane dogleg (cut from sheet), rounded tip
    y_s, y_d = yv + R, 2.2
    sp = math.radians(P.BLADE_SPLAY)
    Lr = P.BLADE_REACH - y_d - hw
    dx, dy = math.sin(sp), math.cos(sp)
    nx, ny = dy, -dx                                                               # right-hand normal
    tipc = (bx + Lr * dx, y_d + Lr * dy)
    pts = [(bx + hw, y_s), (bx + hw, y_d + hw * math.tan(sp / 2))]
    # arc runs from the right edge (a = 0 is along the normal) over the tip to the left edge
    arc = [(tipc[0] + hw * (math.cos(th) * nx + math.sin(th) * dx), tipc[1] + hw * (math.cos(th) * ny + math.sin(th) * dy))
           for th in [math.pi * k / 12 for k in range(13)]]
    pts += arc
    pts += [(bx - hw, y_d - hw * math.tan(sp / 2)), (bx - hw, y_s)]
    flat = cq.Workplane("XY").polyline(pts).close().extrude(t).translate((0, 0, zf - t / 2))
    dot = cyl_z(zr + t / 2, zr + t / 2 + 0.5, bx, -17.0, 1.3)
    blade = root.union(step).union(flat).union(dot)
    coat = cq.Workplane("XY").polyline(pts).close().offset2D(0.45).extrude(t + 0.5).translate((0, 0, zf - t / 2 - 0.25)) \
        .intersect(box(-200, 200, 5.0, 200, -100, 100)).cut(flat)
    tip = (tipc[0] + hw * dx, tipc[1] + hw * dy, zf)
    return blade, coat, tip


def build_mechanics():
    sy = P.STICK_Y
    hub_top = P.HUB_TOP_Z
    # ---- hub body
    hw, hd = P.HUB_W / 2, P.HUB_D / 2
    ly, lz = P.LEG_PIVOT
    ro_bore = P.STICK_OD_OUTER / 2 + 0.08
    hub = box(-hw, hw, sy - hd, sy + hd, hub_top - P.HUB_H, hub_top).edges("|Z").fillet(3.0).faces(">Z").edges().fillet(1.2)
    rear = box(-12, 12, ly - 5.6, sy - hd + 1.0, lz - 5.6, -1.0).edges("|X").fillet(2.4)
    hub = hub.union(rear)
    hub = hub.cut(cyl_z(P.TUBE_OUT_Z[0], hub_top + 1, 0, sy, P.STICK_OD_OUTER / 2 + 0.08))        # stick bore
    hub = hub.cut(box(-4.6, 4.6, ly - 12, ly + 1.6, -30, 30))                                    # leg swing slot (back)
    hub = hub.cut(box(-4.6, 4.6, ly - 12, sy + hd + 1, -30, -7.6))                               # leg swing slot (underneath)
    hub = hub.cut(box(-4.6, 4.6, ly - 12, sy - ro_bore + 0.05, -30, lz + 1.6))                   # arm clearance next to the pivot
    hub = hub.cut(cyl_x(-10.6, 10.6, ly, lz, 3.1))                                               # barrel cavity
    hub = hub.cut(cyl_x(4.9, 10.6, ly, lz, 4.5))                                                 # spring cavity
    hub = hub.cut(cyl_x(-13.5, 13.5, ly, lz, 1.05))                                              # leg pin
    hub = hub.cut(box(-10.6, -5.3, ly - 2.2, ly + 4.2, lz + 2.4, lz + 6.8))                      # sensor pocket (opens into the barrel cavity)
    ky, kz = P.KNUCKLE_PIN
    for s in (-1, 1):
        x0, x1 = sorted((s * 6.3, s * 14.0))
        hub = hub.cut(box(x0, x1, ky - 3.7, sy + hd + 1, kz - 4.4, kz + 4.7))                    # knuckle notches
    hub = hub.cut(cyl_x(-16, 16, ky, kz, 0.85))                                                  # knuckle pin
    add("hub_body", hub, "hub", "abs_teal", budget="hub_spring", rho="petg", printed=True, frame="book",
        label="Tri-grip hub (stick socket, leg hinge, blade knuckle seats)", explode=(0, 0, -30))

    # ---- stick: outer and inner tube, collar, glide bush
    ro, ri, wl = P.STICK_OD_OUTER / 2, P.STICK_OD_INNER / 2, P.STICK_WALL
    add("stick_outer_tube", tube_z(P.TUBE_OUT_Z[0], P.TUBE_OUT_Z[1], 0, sy, ro, ro - wl), "stick_outer", "steel_brushed",
        budget="stick_tubes_cord", rho="steel", frame="book", label="Outer tube, 10 x 0.5 mm stainless", explode=(0, 0, -12))
    zi0, zi1 = P.TUBE_IN_Z0, P.TUBE_IN_Z0 + P.TUBE_IN_LEN
    add("stick_inner_tube", tube_z(zi0, zi1, 0, sy, ri, ri - wl), "stick_inner", "steel_brushed",
        budget="stick_tubes_cord", rho="steel", frame="book", label="Inner tube, 8 x 0.5 mm stainless (pulls up to 18 cm)",
        explode=(0, 0, 14))
    bush = tube_z(zi0, zi0 + 6.0, 0, sy, ro - wl - 0.04, ri)
    add("stick_glide_bush", bush, "stick_inner", "plastic_black", budget="stick_tubes_cord", mass=0.15, frame="book",
        label="Glide bush on the inner tube (friction fit)", explode=(0, 0, 4))
    oz, c0, c1 = P.COLLAR
    col = cyl_z(c0, c1, 0, sy, oz / 2).cut(cyl_z(c0 - 1, P.TUBE_OUT_Z[1], 0, sy, ro + 0.06)).cut(cyl_z(c0, c1 + 1, 0, sy, ri + 0.1))
    add("stick_collar", col, "stick_outer", "abs_teal", budget="stick_tubes_cord", rho="petg", printed=True, frame="book",
        label="Twist-lock collar", explode=(0, 0, 4))

    # ---- joint head (in the inner tube top), pivot screw and thumb nut
    zt = hub_top + STICK0                                                         # stick top = joint base
    pzb = zt + P.JOINT_ABOVE_STICK                                                # pivot height
    tw = P.LUG_GAP / 2 - 0.3
    head = cyl_z(zt - 8.0, zt, 0, sy, ri - wl - 0.05).union(cyl_z(zt, zt + 1.5, 0, sy, ri))
    tongue = box(-tw, tw, sy - 3.5, sy + 3.5, zt + 1.5, pzb).union(cyl_x(-tw, tw, sy, pzb, 3.5))
    head = head.union(tongue).cut(cyl_x(-10, 10, sy, pzb, P.PIVOT_PIN_D / 2 + 0.05))
    add("tilt_joint_head", head, "stick_inner", "abs_teal", budget="tilt_joint", rho="petg", printed=True, frame="book",
        label="Tilt-joint head (plugs into the inner tube)", explode=(0, 0, 26))
    xl = P.LUG_GAP / 2 + P.LUG_T
    screw = cyl_x(-xl, xl + 3.6, sy, pzb, P.PIVOT_PIN_D / 2).union(cyl_x(-xl - 2.0, -xl, sy, pzb, 2.8))
    add("tilt_pivot_screw", screw, "stick_inner", "screw_steel", budget="tilt_joint", rho="steel", frame="book",
        label="Tilt pivot, M3 x 18 screw", explode=(-24, 0, 26))
    nut = cyl_x(xl, xl + 3.6, sy, pzb, 3.5).cut(cyl_x(xl - 1, xl + 5, sy, pzb, P.PIVOT_PIN_D / 2))
    add("tilt_thumb_nut", nut, "stick_inner", "abs_light", budget="tilt_joint", rho="brass", frame="book",
        label="Tilt thumb nut (sets the friction)", explode=(24, 0, 26))

    # ---- hub-sensor cord (coiled inside the inner tube)
    def cord(z0, z1, turns=20):
        pitch = (z1 - z0) / turns
        helix = cq.Wire.makeHelix(pitch, z1 - z0, 2.3)
        c = cq.Workplane("XZ").center(2.3, 0).circle(0.45).sweep(cq.Workplane("XY").add(helix), isFrenet=True)
        return c.translate((0, sy, z0))
    add("hub_cord", cord(-3.0, zt - 9.0), "cord", "wire_black", budget="stick_tubes_cord", mass=1.2, frame="book",
        label="Coiled 2-wire cord to the hub sensor", explode=(0, -26, 0))
    add("hub_cord", cord(-3.0, zt - 9.0 + (P.STICK_EXTENDED - STICK0)), "cord", "wire_black", budget="stick_tubes_cord",
        mass=1.2, frame="book", variant="extended", label="Coiled cord, stretched", explode=(0, -26, 0))

    # ---- rear leg, TPU pad, pin, torsion spring, hub sensor
    a0 = math.degrees(math.asin(((lz - (-(P.COVER_HARD + P.BLOCK_HARD))) - P.PAD[2] - 1.3) / P.LEG_CHORD))   # table pose
    barrel = cyl_x(-10.3, 10.3, ly, lz, 2.8)
    arm = box(-4.0, 4.0, ly - (P.LEG_CHORD - 6.0), ly - 1.0, lz - 1.3, lz + 1.3)
    foot = box(-P.PAD[0] / 2, P.PAD[0] / 2, ly - P.LEG_CHORD - P.PAD[1] / 2, ly - P.LEG_CHORD + P.PAD[1] / 2, lz - 1.3, lz + 1.3) \
        .edges("|Z").fillet(3.0)
    foot = rot_x(foot, -a0, ly - P.LEG_CHORD, lz)
    leg = barrel.union(arm).union(foot).cut(cyl_x(-14, 14, ly, lz, 1.05))
    pad = box(-P.PAD[0] / 2, P.PAD[0] / 2, ly - P.LEG_CHORD - P.PAD[1] / 2, ly - P.LEG_CHORD + P.PAD[1] / 2,
              lz - 1.3 - P.PAD[2], lz - 1.3).edges("|Z").fillet(3.0)
    pad = rot_x(pad, -a0, ly - P.LEG_CHORD, lz)
    leg, pad = rot_x(leg, a0, ly, lz), rot_x(pad, a0, ly, lz)
    add("rear_leg", leg, "leg", "abs_teal", budget="rear_leg_pad", rho="petg", printed=True, frame="book",
        label="Rear leg with T-foot (presses on the spine, or rests on the table)", explode=(0, -34, -12))
    add("rear_leg_pad", pad, "leg", "tpu_dark", budget="rear_leg_pad", rho="tpu", printed=True, frame="book",
        label="Soft TPU pad", explode=(0, -40, -22))
    add("leg_pin", cyl_x(-12.8, 12.8, ly, lz, 1.0), "hub", "screw_steel", budget="hub_spring", rho="steel", frame="book",
        label="Leg hinge pin, 2 x 25 mm", explode=(-34, 0, -30))
    helix = cq.Wire.makeHelix(1.02, 4.6, 3.6)
    spring = cq.Workplane("XZ").center(3.6, 0).circle(0.5).sweep(cq.Workplane("XY").add(helix), isFrenet=True)
    spring = spring.rotate((0, 0, 0), (0, 1, 0), 90).translate((5.45, ly, lz))
    add("torsion_spring", spring, "hub", "spring_steel", budget="hub_spring", mass=0.8, frame="book",
        label="Torsion spring, 1.0 mm wire, 5 coils", explode=(30, 0, -30))
    sens = box(-10.4, -5.5, ly - 2.0, ly + 4.0, lz + 3.3, lz + 6.6)
    add("hub_sensor_switch", sens, "hub", "ic_black", budget="hub_spring", mass=0.3, frame="book",
        label="Hub sensor: detector switch (GPIO 8, low = leg deployed)", explode=(-30, 0, -22))

    # ---- blades (two drop variants), coats, knuckles, pin, clamp screws
    drops = {None: blade_drop("hard"), "soft": blade_drop("soft"), "deep": blade_drop("none"), "thick": blade_drop("thick")}
    tips = {}
    for var, drop in drops.items():
        bl, coat, tip = blade_shape(drop)
        tips[var or "default"] = tip
        add("blade_right", bl, "blade_r", "spring_steel", budget="blades", rho="steel", frame="book", variant=var,
            label="Blade, 0.4 x 8 mm 301 spring steel (right)", explode=(26, 22, -8))
        add("blade_left", mirror_x(bl), "blade_l", "spring_steel", budget="blades", rho="steel", frame="book", variant=var,
            label="Blade, 0.4 x 8 mm 301 spring steel (left)", explode=(-26, 22, -8))
        add("blade_coat_right", coat, "blade_r", "silicone", budget="blades", mass=0.25, frame="book", variant=var,
            label="Blade coating / sleeve (right)", explode=(26, 34, -8))
        add("blade_coat_left", mirror_x(coat), "blade_l", "silicone", budget="blades", mass=0.25, frame="book", variant=var,
            label="Blade coating / sleeve (left)", explode=(-26, 34, -8))
    zr, t = P.BLADE_ROOT_Z, P.BLADE_T
    kn = box(6.6, 15.4, ky - 3.5, ky + 4.5, kz - 4.2, kz + 2.6).edges("|X").fillet(1.0)
    kn = kn.cut(box(6.0, 16.0, P.BLADE_ROOT_Y - 0.2, ky + 5.0, zr - t / 2 - 0.03, zr + t / 2 + 0.03))
    kn = kn.cut(cyl_x(0, 20, ky, kz, 0.85)).cut(cyl_z(kz - 6, kz + 4, P.BLADE_X, -31.2, 1.05))
    add("blade_knuckle_right", kn, "blade_r", "abs_teal", budget="hub_spring", rho="petg", printed=True, frame="book",
        label="Blade knuckle (right): pivots to fold the blade up", explode=(26, 10, -8))
    add("blade_knuckle_left", mirror_x(kn), "blade_l", "abs_teal", budget="hub_spring", rho="petg", printed=True, frame="book",
        label="Blade knuckle (left)", explode=(-26, 10, -8))
    add("knuckle_pin", cyl_x(-15.4, 15.4, ky, kz, 0.8), "hub", "screw_steel", budget="hub_spring", rho="steel", frame="book",
        label="Knuckle pin, 1.6 x 31 mm", explode=(0, 14, -30))
    cs = cyl_z(kz - 4.2, kz + 2.6, P.BLADE_X, -31.2, 1.0).union(cyl_z(kz + 2.6, kz + 3.7, P.BLADE_X, -31.2, 1.9))
    add("blade_clamp_screw_right", cs, "blade_r", "screw_black", budget="hub_spring", mass=0.15, frame="book",
        label="Blade clamp screw, M2 x 6", explode=(26, 10, 4))
    add("blade_clamp_screw_left", mirror_x(cs), "blade_l", "screw_black", budget="hub_spring", mass=0.15, frame="book",
        label="Blade clamp screw, M2 x 6", explode=(-26, 10, 4))
    return dict(leg_table_deg=a0, blade_tips=tips, drops={k or "default": v for k, v in drops.items()})


def blade_drop(kind):
    """Step from the blade root down to where the blade lies.
    hard: on the cover board of a hardcover, under the pages (hub centred on the page plane).
    soft: on the cover of a thin paperback (the whole device then sits higher, see poses).
    none: no book, blade flat on the table."""
    table = -(P.COVER_HARD + P.BLOCK_HARD)                     # table height under the hub in device coordinates
    if kind == "thick":                                        # hub stays centred on the page plane, table is lower
        table = -(P.COVER_THICK + P.BLOCK_THICK)
    cover = {"hard": P.COVER_HARD, "soft": P.COVER_SOFT, "none": 0.0, "thick": P.COVER_THICK}[kind]
    return P.BLADE_ROOT_Z - (table + cover + 0.5)


# =====================================================================================
#  POSES (book frame). Each group gets a 4x4 matrix per pose, relative to the default pose.
# =====================================================================================
def M_translate(x, y, z):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def M_rot_x(deg, y, z):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    r = np.eye(4)
    r[1, 1], r[1, 2], r[2, 1], r[2, 2] = c, -s, s, c
    return M_translate(0, y, z) @ r @ M_translate(0, -y, -z)


def unit_matrix(stick, tip):
    """Unit frame -> book frame."""
    piv = (0.0, P.STICK_Y, P.HUB_TOP_Z + stick + P.JOINT_ABOVE_STICK)
    return M_translate(*piv) @ M_rot_x(-tip, 0, 0) @ M_translate(0, -P.PIVOT_Y, -P.PIVOT_Z)


def poses(info):
    ly, lz = P.LEG_PIVOT
    ky, kz = P.KNUCKLE_PIN
    a0 = info["leg_table_deg"]
    U0 = unit_matrix(STICK0, TIP0)
    I = np.eye(4)
    rise = P.BLOCK_HARD + P.COVER_HARD - (P.BLOCK_SOFT + P.COVER_SOFT)      # device sits higher on a thin book

    def pose(stick=STICK0, tip=TIP0, leg=a0, blade=0.0, variant=None, lift=0.0, note=""):
        up = M_translate(0, 0, stick - STICK0)
        L = M_translate(0, 0, lift)
        return dict(
            groups={
                "unit": (L @ unit_matrix(stick, tip) @ np.linalg.inv(U0)).tolist(),
                "stick_inner": (L @ up).tolist(), "stick_outer": L.tolist(), "hub": L.tolist(), "cord": L.tolist(),
                "leg": (L @ M_rot_x(leg - a0, ly, lz)).tolist(),
                "blade_r": (L @ M_rot_x(blade, ky, kz)).tolist(), "blade_l": (L @ M_rot_x(blade, ky, kz)).tolist(),
            },
            variants=variant or {}, stick=stick, tip=tip, leg_deg=leg, lift=lift, note=note)

    return {
        "table_hardcover": pose(note="Open hardcover on a table: blades under the pages, rear leg on the table."),
        "table_paperback": pose(variant={"blade_right": "soft", "blade_left": "soft", "blade_coat_right": "soft",
                                         "blade_coat_left": "soft"}, lift=rise,
                                note="Thin paperback on a table: the device sits higher so the hub clears the table."),
        "tripod_no_book": pose(variant={"blade_right": "deep", "blade_left": "deep", "blade_coat_right": "deep",
                                        "blade_coat_left": "deep"},
                               note="No book: blades flat on the table, rear leg behind."),
        "in_hand": pose(leg=180 - math.degrees(math.asin((P.COVER_HARD + P.BLOCK_HARD + P.PAD[2] + 1.3 + lz) / P.LEG_CHORD)),
                        note="Book held in the hands: rear leg swung forward under the spine."),
        "extended": pose(stick=P.STICK_EXTENDED, tip=14.5,
                         leg=math.degrees(math.asin((P.COVER_THICK + P.BLOCK_THICK - P.PAD[2] - 1.3 + lz) / P.LEG_CHORD)),
                         variant={"hub_cord": "extended", "blade_right": "thick", "blade_left": "thick",
                                  "blade_coat_right": "thick", "blade_coat_left": "thick"},
                         note="Stick pulled up to 18 cm for small print, on a 33 mm thick book."),
        "stowed": pose(tip=0.0, leg=-90.0, blade=90.0, note="Legs folded up along the stick."),
    }


# =====================================================================================
#  CHECKS: collisions, clearances, wall thickness, mass and centre of mass
# =====================================================================================
def moved(shape, M):
    """Apply a rigid 4x4 matrix (rotation + translation) to a shape."""
    from OCP.gp import gp_Trsf
    t = gp_Trsf()
    m = np.asarray(M, dtype=float)
    t.SetValues(*[float(m[i, j]) for i in range(3) for j in range(4)])
    return shape.moved(cq.Location(t))


def placed(body, U0):
    """Body shape in the book frame, default pose."""
    if body["frame"] == "book":
        return body["shape"]
    return moved(body["shape"], U0)


def vol_centroid(shape):
    solids = shape.Solids() if hasattr(shape, "Solids") else [shape]
    v = sum(s.Volume() for s in solids)
    c = np.zeros(3)
    for s in solids:
        cc = s.Center()
        c += s.Volume() * np.array([cc.x, cc.y, cc.z])
    return v, (c / v if v > 0 else c)


def bbox(shape):
    b = shape.BoundingBox()
    return (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)


def boxes_gap(a, b):
    return max(a[0] - b[3], b[0] - a[3], a[1] - b[4], b[1] - a[4], a[2] - b[5], b[2] - a[5])


# pairs that touch or nest by design (fits), not collisions
ALLOWED = [("blade_", "blade_knuckle"), ("blade_", "blade_clamp_screw"), ("knuckle_pin", "blade_knuckle"),
           ("blade_coat", "blade_"), ("leg_pin", "rear_leg"), ("stick_", "stick_"), ("tilt_", "tilt_"),
           ("tilt_joint_head", "stick_inner_tube"), ("cover_screw", "shell_"), ("camera_screws", "camera_"),
           ("camera_screws", "shell_front_tub"), 
           ("blade_clamp_screw", "blade_knuckle"), ("hub_cord_tail", "tilt_"), ("tilt_pivot_screw", "shell_front_tub"),
           ("light_ring_leds", "light_ring_pcb"), ("camera_flex", "pi_zero_2w_chips"), ("camera_flex", "camera_connector"),
           ("harness_", "pi_gpio_pads"), ("harness_", "pi_zero_2w_pcb"), ("battery_leads", "cell_pcm"),
           ("battery_leads", "power_board"), ("harness_", "amp_board"), ("harness_", "power_board"),
           ("speaker_leads", "amp_board"), ("speaker_leads", "speaker"), ("headphone_leads", "dac_board"),
           ("headphone_leads", "headphone_jack"), ("hub_cord_tail", "tilt_"), ("hub_cord_tail", "shell_front_tub"),
           ("shell_back_cover", "pi_zero_2w_pcb")]


def allowed(a, b):
    for p, q in ALLOWED:
        if (a.startswith(p) and b.startswith(q)) or (b.startswith(p) and a.startswith(q)):
            return True
    return False


def run_checks(info):
    U0 = unit_matrix(STICK0, TIP0)
    base = [b for b in BODIES if b["variant"] is None]
    shp = {b["name"]: placed(b, U0) for b in base}
    bb = {n: bbox(s) for n, s in shp.items()}
    names = list(shp)
    hits, close, contacts = [], [], []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if boxes_gap(bb[a], bb[b]) > 0.6:
                continue
            try:
                common = shp[a].intersect(shp[b])
                v = sum(s.Volume() for s in common.Solids()) if common is not None else 0.0
            except Exception:
                v = 0.0
            if v > 0.02:
                if not allowed(a, b):
                    hits.append(dict(a=a, b=b, overlap_mm3=round(v, 2)))
                continue
            if boxes_gap(bb[a], bb[b]) > 0.5 or allowed(a, b):
                continue
            try:
                from OCP.BRepExtrema import BRepExtrema_DistShapeShape
                d = BRepExtrema_DistShapeShape(shp[a].wrapped, shp[b].wrapped)
                d.Perform()
                dist = d.Value()
            except Exception:
                dist = None
            if dist is not None and 0.005 < dist < 0.5:
                close.append(dict(a=a, b=b, gap_mm=round(dist, 2)))
            elif dist is not None:
                contacts.append((a, b))
    close.sort(key=lambda r: r["gap_mm"])

    # ---- masses
    rows = []
    for b in base:
        v, c = vol_centroid(shp[b["name"]])
        m = b["mass"] if b["mass"] is not None else v / 1000.0 * P.RHO[b["rho"]]
        rows.append(dict(name=b["name"], group=b["group"], budget=b["budget"], mass_g=round(m, 2),
                         volume_mm3=round(v, 1), com=[round(float(x), 2) for x in c], source="est" if b["mass"] is not None else b["rho"]))
    by_budget = {}
    for r in rows:
        by_budget.setdefault(r["budget"], 0.0)
        by_budget[r["budget"]] += r["mass_g"]
    budget = [dict(key=k, model_g=round(by_budget.get(k, 0.0), 1), params_g=P.MASS[k],
                   diff_g=round(by_budget.get(k, 0.0) - P.MASS[k], 1)) for k in P.MASS]
    mtot = sum(r["mass_g"] for r in rows)
    com = sum(r["mass_g"] * np.array(r["com"]) for r in rows) / mtot
    unit_rows = [r for r in rows if r["group"] == "unit"]
    munit = sum(r["mass_g"] for r in unit_rows)
    com_unit = sum(r["mass_g"] * np.array(r["com"]) for r in unit_rows) / munit
    Uinv = np.linalg.inv(U0)
    com_unit_local = (Uinv @ np.append(com_unit, 1.0))[:3]
    return dict(collisions=hits, tight_gaps=close, n_contacts=len(contacts), n_bodies=len(base), masses=rows, budget=budget,
                mass_total_g=round(mtot, 1), mass_unit_g=round(munit, 1), params_total_g=P.total_mass(),
                params_unit_g=P.unit_mass(), com_book=[round(float(x), 1) for x in com],
                com_unit_book=[round(float(x), 1) for x in com_unit],
                com_unit_in_unit_frame=[round(float(x), 1) for x in com_unit_local])


def pose_collisions(pz):
    """Collisions between parts that move relative to each other, in every pose."""
    U0 = unit_matrix(STICK0, TIP0)
    out = {}
    for pname, p in pz.items():
        items = []
        for b in BODIES:
            if b["variant"] != p["variants"].get(b["name"]):
                continue
            s_ = moved(placed(b, U0), np.array(p["groups"][b["group"]]))
            items.append((b["name"], b["group"], s_, bbox(s_)))
        hits = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                (a, ga, sa, ba), (b, gb, sb, bb_) = items[i], items[j]
                if ga == gb or boxes_gap(ba, bb_) > 0 or allowed(a, b):
                    continue
                try:
                    v = sum(x.Volume() for x in sa.intersect(sb).Solids())
                except Exception:
                    v = 0.0
                if v > 0.02:
                    hits.append(dict(a=a, b=b, overlap_mm3=round(v, 2)))
        out[pname] = hits
    return out


def pose_coms(report, pz):
    """Centre of mass and bounding box for every pose (uses the default-pose body centroids)."""
    out = {}
    U0 = unit_matrix(STICK0, TIP0)
    rows = {r["name"]: r for r in report["masses"]}
    for pname, p in pz.items():
        tot, acc = 0.0, np.zeros(3)
        lo, hi = np.full(3, 1e9), np.full(3, -1e9)
        for b in BODIES:
            want = p["variants"].get(b["name"])
            if b["variant"] != want:
                continue
            M = np.array(p["groups"][b["group"]])
            r = rows[b["name"]]
            c = (M @ np.append(np.array(r["com"]), 1.0))[:3]
            acc += r["mass_g"] * c
            tot += r["mass_g"]
            s = moved(placed(b, U0), M)
            bx = bbox(s)
            lo, hi = np.minimum(lo, bx[:3]), np.maximum(hi, bx[3:])
        out[pname] = dict(com=[round(float(x), 1) for x in acc / tot], mass_g=round(tot, 1),
                          bbox_min=[round(float(x), 1) for x in lo], bbox_max=[round(float(x), 1) for x in hi],
                          size_mm=[round(float(x), 1) for x in hi - lo])
    return out


# =====================================================================================
#  EXPORT
# =====================================================================================
COLORS = {  # sRGB 0..1, used for STEP colours and as the base colours in the viewer
    "abs_teal": (0.180, 0.290, 0.322), "abs_light": (0.300, 0.420, 0.455), "marigold": (0.910, 0.639, 0.090),
    "glass": (0.55, 0.62, 0.66), "blue_ring": (0.62, 0.78, 0.88), "diffuser": (0.93, 0.93, 0.90),
    "dot_white": (0.96, 0.96, 0.94), "orange_flag": (0.93, 0.42, 0.10), "pcb_green": (0.05, 0.36, 0.20),
    "pcb_green2": (0.10, 0.42, 0.24), "pcb_black": (0.06, 0.07, 0.08), "pcb_blue": (0.07, 0.20, 0.52),
    "pcb_purple": (0.33, 0.14, 0.45), "pcb_red": (0.62, 0.10, 0.10), "pcb_white": (0.90, 0.90, 0.88),
    "ic_black": (0.07, 0.07, 0.08), "plastic_black": (0.09, 0.09, 0.10), "lens_black": (0.05, 0.05, 0.06),
    "lens_glass": (0.20, 0.24, 0.35), "metal_tin": (0.74, 0.75, 0.76), "gold": (0.83, 0.66, 0.26),
    "aluminium": (0.80, 0.81, 0.82), "pad_grey": (0.55, 0.60, 0.68), "pouch_silver": (0.70, 0.71, 0.73),
    "kapton": (0.78, 0.52, 0.12), "speaker": (0.12, 0.12, 0.13), "led_warm": (1.0, 0.93, 0.72),
    "wire_multi": (0.75, 0.30, 0.25), "wire_red": (0.75, 0.10, 0.10), "wire_black": (0.10, 0.10, 0.11),
    "flex_amber": (0.80, 0.55, 0.20), "screw_black": (0.12, 0.12, 0.13), "screw_steel": (0.70, 0.71, 0.72),
    "steel_brushed": (0.72, 0.73, 0.74), "spring_steel": (0.62, 0.64, 0.67), "silicone": (0.82, 0.84, 0.85),
    "tpu_dark": (0.13, 0.14, 0.15),
}


# Exploded-view offsets (mm), in the sb_params frame (+x = reader's right). First match wins.
EXPLODE = [
    ("shell_front_tub", (0, 50, 0)), ("status_dot_pipes", (0, 62, 0)), ("lens_window", (0, 62, -12)), ("lens_bezel", (0, 66, -16)),
    ("light_ring_diffuser", (0, 58, -8)), ("button_ask", (0, 50, 30)), ("button_play_pause", (0, 50, 22)),
    ("button_back", (0, 50, 22)), ("button_forward", (0, 50, 22)), ("button_vol", (-24, 50, 0)), ("mic_mute_slider", (-24, 50, 0)),
    ("mic_mute_flag", (-24, 50, 0)), ("speaker_leads", (0, 10, 18)), ("speaker", (0, 24, 0)), ("status_led", (0, 24, 8)),
    ("haptic_motor", (0, 24, 0)), ("amp_board", (-10, 14, 0)), ("dac_board", (-20, 8, -8)), ("power_board", (12, 12, 0)),
    ("usb_c_receptacle", (12, 12, 0)), ("headphone_jack", (24, 8, -10)), ("headphone_leads", (0, 0, -16)), ("mic_right", (6, 14, 16)),
    ("mic_left", (-6, 14, 16)), ("top_button", (0, 6, 16)), ("back_button_board", (0, 10, 16)), ("forward_button_board", (0, 10, 16)),
    ("volume_board", (-16, 12, 0)), ("mic_mute_switch", (-16, 12, 0)), ("light_ring_pcb", (0, 18, -18)), ("light_ring_leds", (0, 18, -18)),
    ("camera_lens", (0, 10, -10)), ("camera_holder_m12", (0, 5, -5)), ("camera_screws", (0, -7, 7)), ("camera_flex", (0, -18, 0)),
    ("camera_", (0, 0, 0)), ("cell_right", (28, 0, 0)), ("cell_pcm_right", (28, 0, 0)), ("cell_left", (-28, 0, 0)),
    ("cell_pcm_left", (-28, 0, 0)), ("fuel_gauge", (0, 0, -22)), ("microsd_card", (10, -28, 0)), ("pi_", (0, -28, 0)),
    ("harness_", (0, -14, 16)), ("battery_leads", (0, 0, 14)), ("hub_cord_tail", (0, 0, -16)), ("thermal_pad", (0, -42, 0)),
    ("heat_spreader", (0, -52, 0)), ("shell_back_cover", (0, -68, 0)), ("cover_screw", (0, -88, 0)),
    # stick, joint, hub, legs (book frame)
    ("tilt_joint_head", (0, 0, 150)), ("tilt_pivot_screw", (-24, 0, 150)), ("tilt_thumb_nut", (24, 0, 150)),
    ("stick_inner_tube", (0, 0, 128)), ("stick_glide_bush", (0, 0, 116)), ("stick_collar", (0, 0, 14)), ("stick_outer_tube", (0, 0, 0)),
    ("hub_cord", (-46, 0, 24)), ("hub_body", (0, 0, -34)), ("leg_pin", (-34, 0, -34)), ("torsion_spring", (30, -12, -34)),
    ("hub_sensor_switch", (-30, -12, -24)), ("rear_leg_pad", (0, -52, -58)), ("rear_leg", (0, -44, -44)),
    ("blade_knuckle_right", (24, 16, -34)), ("blade_knuckle_left", (-24, 16, -34)), ("knuckle_pin", (0, 34, -20)),
    ("blade_clamp_screw_right", (24, 16, -14)), ("blade_clamp_screw_left", (-24, 16, -14)),
    ("blade_coat_right", (40, 62, -34)), ("blade_coat_left", (-40, 62, -34)), ("blade_right", (32, 40, -34)), ("blade_left", (-32, 40, -34)),
]


def explode_of(name):
    for k, v in EXPLODE:
        if name.startswith(k):
            return [-v[0], v[1], v[2]]            # mirrored into the right-handed CAD frame
    return [0, 0, 0]


def mesh_of(shape, tol, ang):
    vs, fs = shape.tessellate(tol, ang)
    v = np.array([(p.x, p.y, p.z) for p in vs], dtype=np.float32)
    f = np.array(fs, dtype=np.int32)
    return v, f


def key_of(b):
    return b["name"] + ("__" + b["variant"] if b["variant"] else "")


def export_meshes(pz, info, report, keep=False):
    os.makedirs(os.path.join(BUILD, "mesh"), exist_ok=True)
    os.makedirs(os.path.join(BUILD, "mesh_web"), exist_ok=True)
    U0 = unit_matrix(STICK0, TIP0)
    man = []
    for b in BODIES:
        s = placed(b, U0)
        k = key_of(b)
        p1, p2 = os.path.join(BUILD, "mesh", k + ".npz"), os.path.join(BUILD, "mesh_web", k + ".npz")
        if not (keep and os.path.exists(p1) and os.path.exists(p2)):
            v, f = mesh_of(s, 0.02, 0.12)
            np.savez_compressed(p1, v=v, f=f)
            v2, f2 = mesh_of(s, 0.08, 0.35)
            if len(f2) > 40000:                          # the coiled cord and the spring: thin them for the web viewer
                import trimesh
                slim = trimesh.Trimesh(v2, f2, process=True).simplify_quadric_decimation(face_count=9000 if len(f2) > 150000 else 3000)
                v2, f2 = np.asarray(slim.vertices, dtype=np.float32), np.asarray(slim.faces, dtype=np.int32)
            np.savez_compressed(p2, v=v2, f=f2)
        man.append(dict(key=k, name=b["name"], variant=b["variant"], group=b["group"], mat=b["mat"], label=b["label"],
                        budget=b["budget"], printed=b["printed"], explode=explode_of(b["name"]), frame=b["frame"]))
    with open(os.path.join(BUILD, "manifest.json"), "w") as fh:
        json.dump(dict(bodies=man, poses=pz, colors=COLORS, unit_matrix=U0.tolist(), info=info,
                       params=dict(stick_y=P.STICK_Y, hub_top_z=P.HUB_TOP_Z, table_hard=-(P.COVER_HARD + P.BLOCK_HARD),
                                   cover_hard=P.COVER_HARD, block_hard=P.BLOCK_HARD, cover_soft=P.COVER_SOFT,
                                   block_soft=P.BLOCK_SOFT, pivot=[P.PIVOT_Y, P.PIVOT_Z], unit=[P.UNIT_W, P.UNIT_D, P.UNIT_H]),
                       report=dict(com_book=report["com_book"], mass_total_g=report["mass_total_g"])), fh, indent=1)
    print(f"meshes: {len(man)} bodies -> {BUILD}")


def export_cad(pz):
    os.makedirs(os.path.join(OUT, "step"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)
    U0 = unit_matrix(STICK0, TIP0)
    asm = cq.Assembly(name="SenseBook_v4_tri_grip")
    for b in BODIES:
        if b["variant"] is not None:
            continue
        s = placed(b, U0)
        asm.add(s, name=b["name"], color=cq.Color(*COLORS[b["mat"]], 1.0))
        cq.exporters.export(cq.Workplane("XY").add(b["shape"]), os.path.join(OUT, "step", b["name"] + ".step"))
    asm.save(os.path.join(OUT, "SenseBook_assembly.step"))
    n = 0
    for b in BODIES:
        if not b["printed"] or b["variant"] is not None:
            continue
        b["shape"].exportStl(os.path.join(OUT, "stl", b["name"] + ".stl"), tolerance=0.01, angularTolerance=0.1)
        n += 1
    # blade flat pattern (developed length along the centre-line), for laser cutting or snipping shim stock
    for var, kind in (("hardcover", "hard"), ("thin_book", "soft")):
        drop = blade_drop(kind)
        R = min(2.0, drop / 2 - 0.05)
        yv = -0.7
        dev = (yv - R - P.BLADE_ROOT_Y) + (math.pi * R) + (drop - 2 * R)          # root + two quarter bends + upright
        hw = P.BLADE_W / 2
        sp = math.radians(P.BLADE_SPLAY)
        y_d = 2.2 - (yv + R)
        Lr = P.BLADE_REACH - 2.2 - hw
        pts = [(hw, -dev), (hw, y_d + hw * math.tan(sp / 2))]
        tc = (Lr * math.sin(sp), y_d + Lr * math.cos(sp))
        nx, ny, dx, dy = math.cos(sp), -math.sin(sp), math.sin(sp), math.cos(sp)
        pts += [(tc[0] + hw * (math.cos(th) * nx + math.sin(th) * dx), tc[1] + hw * (math.cos(th) * ny + math.sin(th) * dy))
                for th in [math.pi * k / 12 for k in range(13)]]
        pts += [(-hw, y_d - hw * math.tan(sp / 2)), (-hw, -dev)]
        flat = cq.Workplane("XY").polyline(pts).close().extrude(P.BLADE_T) \
            .cut(cq.Workplane("XY").circle(1.1).extrude(1).translate((0, -dev + (-31.2 - P.BLADE_ROOT_Y), 0)))
        cq.exporters.export(flat.section(), os.path.join(OUT, f"blade_flat_pattern_{var}_right.dxf"))
        cq.exporters.export(mirror_x(flat).section(), os.path.join(OUT, f"blade_flat_pattern_{var}_left.dxf"))
    print(f"CAD: assembly STEP, {len([b for b in BODIES if b['variant'] is None])} part STEP, {n} STL, 4 DXF -> {OUT}")


def main():
    quick = "--quick" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    build_unit()
    info = build_mechanics()
    pz = poses(info)
    if "--manifest" in sys.argv:                      # fast path: only rewrite the manifest (poses, explode offsets)
        report = json.load(open(os.path.join(OUT, "model_report.json")))
        export_meshes(pz, info, report, keep=True)
        return
    report = run_checks(info)
    report["poses"] = pose_coms(report, pz)
    report["pose_collisions"] = pose_collisions(pz)
    report["info"] = info
    with open(os.path.join(OUT, "model_report.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    print(f"bodies {report['n_bodies']}  collisions {len(report['collisions'])}  tight gaps {len(report['tight_gaps'])}")
    for h in report["collisions"]:
        print("  COLLISION", h)
    for h in report["tight_gaps"]:
        print("  tight", h)
    print("mass total", report["mass_total_g"], "g (params", report["params_total_g"], ")  unit", report["mass_unit_g"],
          "(params", report["params_unit_g"], ")")
    for b in report["budget"]:
        print(f"  {b['key']:22s} model {b['model_g']:6.1f}  params {b['params_g']:5.1f}  diff {b['diff_g']:+.1f}")
    for k, v in report["pose_collisions"].items():
        print(f"  pose {k:16s} collisions between moving groups: {len(v)}", v[:6])
    print("CoM book", report["com_book"], " unit CoM in unit frame", report["com_unit_in_unit_frame"])
    for k, v in report["poses"].items():
        print(f"  pose {k:16s} size {v['size_mm']}  com {v['com']}")
    if "--no-mesh" not in sys.argv:
        export_meshes(pz, info, report)
    if not quick:
        export_cad(pz)


if __name__ == "__main__":
    main()
