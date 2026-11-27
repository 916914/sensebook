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


def sphere(c, r):
    return cq.Workplane("XY").sphere(r).translate(tuple(c))


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
        parts.append(sphere(p, r))
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


CORD_EXIT_Z = 0.75     # the cord leaves the joint head this far above the top of the stick (mid-height of the 1.5 mm collar)
SOURCE_KEY = {}        # body name -> key in sb_params.PARTS (bought parts only)
LAY = {}               # where things ended up in the unit (filled by build_unit; read by make_drawings.py)
ROUTES = {}            # cable routes: points, bundle radius, length


def add(name, wp, group_, mat, *, budget, label, mass=None, rho=None, printed=False, frame="unit",
        variant=None, explode=(0, 0, 0), part=None):
    """mass (g) for bought parts, or rho (key of P.RHO) for made parts (mass from volume)."""
    shp = shape_of(wp) if isinstance(wp, cq.Workplane) else wp
    # sb_params uses +x = reader's right with +y toward the reader and z up, which is a left-handed
    # frame. CAD files, meshes and renders are right-handed, so every body is mirrored once here:
    # X_cad = -x. "Left" and "right" in part names always mean the reader's left and right.
    shp = shp.mirror("YZ")
    if part:
        SOURCE_KEY[name] = part
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


def layout():
    """Where the bought parts sit, worked out from their datasheet sizes (sb_params.PARTS). Unit frame, mm."""
    D, wall = P.PD, P.WALL
    L = {}
    L["xin"] = P.UNIT_W / 2 - wall
    L["ceil"] = P.UNIT_H - wall
    L["back_in"] = -P.UNIT_D + wall
    # camera, along the lens axis (a = depth behind the outer facet surface)
    L["a_apex"] = P.CAM_LENS_RECESS
    L["a_back"] = L["a_apex"] + D("cam", "back_to_apex")            # back face of the camera board
    L["a_front"] = L["a_back"] - D("cam", "pcb_t")                  # front face of the camera board
    L["a_rim"] = L["a_back"] - D("cam", "back_to_rim")
    L["a_holder"] = L["a_back"] - D("cam", "holder_top_from_back")
    L["v0"] = -D("cam", "axis_from_far_edge")                       # lower edge of the board
    L["v1"] = L["v0"] + D("cam", "board_h")                         # upper (connector) edge
    L["cam_hu"] = D("cam", "hole_pitch_w") / 2
    L["cam_hv"] = (L["v0"] + D("cam", "hole_edge"), L["v0"] + D("cam", "hole_edge") + D("cam", "hole_pitch_h"))
    # cells stand either side of the camera board, as far forward as the lens facet allows
    L["cell_x0"] = D("cam", "board_w") / 2 + P.CELL_GAP_X
    L["cell_y1"] = round(P.CELL_Z0 - facet_floor(0.0) - 0.05, 2)
    L["cell_yb"] = L["cell_y1"] - P.CELL_POCKET_T
    # Pi behind the cells, parts toward the cover
    L["pi_yu"] = L["cell_yb"] - 0.2                                 # flat underside of the Pi
    L["pi_yt"] = L["pi_yu"] - D("pi", "pcb_t")                      # component face
    L["pi_keep"] = L["pi_yt"] - (D("pi", "thick_total") - D("pi", "pcb_t"))
    return L


def build_unit():
    D, wall = P.PD, P.WALL
    L = layout()
    xin, ceil = L["xin"], L["ceil"]
    outer, inner = unit_solid(0.0), unit_solid(wall)
    shell = outer.cut(inner)
    tub = shell.intersect(box(-60, 60, P.SEAM_Y, 20, -30, 60))
    cover = shell.intersect(box(-60, 60, -60, P.SEAM_Y, -30, 60))

    # ---- tilt lugs under the flat bottom (pivot axis along x)
    py, pz = P.PIVOT_Y, P.PIVOT_Z
    lug2d = (cq.Workplane("YZ").polyline([(py - 6, 0.6), (py + 2.0, 0.6), (py + 3.4, pz), (py - 4.3, pz)]).close()
             .extrude(P.LUG_T).union(cq.Workplane("YZ").circle(4.3).extrude(P.LUG_T).translate((0, py, pz))))
    lug = lug2d.translate((P.LUG_GAP / 2, 0, 0))
    lugs = lug.union(mirror_x(lug)).cut(cyl_x(-20, 20, py, pz, P.PIVOT_PIN_D / 2 + 0.1))
    tub = tub.union(lugs)

    # ---- cover screw bosses (ST2.2 tapping screws from the back)
    st_d, st_hd, st_hh = D("st22", "thread_d"), D("st22", "head_d"), D("st22", "head_h")
    boss_pts = [(9.0, ceil - 2.3, 6.5), (-9.0, ceil - 2.3, 6.5), (30.0, wall + 2.1, 3.5), (-30.0, wall + 2.1, 3.5)]
    boss_keep = []
    for (bx, bz, blen) in boss_pts:
        b = cyl_y(P.SEAM_Y, P.SEAM_Y + blen, bx, bz, 2.0)
        web = box(bx - 2.0, bx + 2.0, P.SEAM_Y, P.SEAM_Y + blen, bz, bz + 2.4) if bz > 20 else \
            box(bx - 2.0, bx + 2.0, P.SEAM_Y, P.SEAM_Y + blen, bz - 2.2, bz)
        b = b.union(web).intersect(unit_solid(wall - 0.2))
        tub = tub.union(b)
        boss_keep.append(box(bx - 2.4, bx + 2.4, P.SEAM_Y - 1, P.SEAM_Y + blen + 1, bz - 2.6, bz + 2.8))
        tub = tub.cut(cyl_y(P.SEAM_Y - 1, P.SEAM_Y + blen, bx, bz, 0.85))            # 1.7 pilot
        cover = cover.cut(cyl_y(-60, P.SEAM_Y + 1, bx, bz, st_d / 2 + 0.1))
        cover = cover.cut(cyl_y(-60, -P.UNIT_D + 1.0, bx, bz, st_hd / 2 + 0.2))       # counterbore for the head

    # ---- cover tongue (locates the cover in the tub)
    g, t = P.TONGUE_GAP, P.TONGUE_T
    tongue = unit_solid(wall + g).cut(unit_solid(wall + g + t)).intersect(
        box(-60, 60, P.SEAM_Y - 0.05, P.SEAM_Y + P.TONGUE_H, -30, 60))
    for k in boss_keep:
        tongue = tongue.cut(k)
    # root of the tongue: a 1.0 mm band inside the cover, fused to the cover wall (the tongue itself stands TONGUE_GAP off the tub wall)
    root = unit_solid(wall - 0.05).cut(unit_solid(wall + g + t)).intersect(box(-60, 60, P.SEAM_Y - 1.0, P.SEAM_Y, -30, 60))
    cover = cover.union(root).union(tongue)
    for (bx, bz, blen) in boss_pts:                                                   # the screw holes pass through the root too
        cover = cover.cut(cyl_y(-60, P.SEAM_Y + 1, bx, bz, st_d / 2 + 0.1))

    # ---- Pi standoffs on the cover, each ending in a locating pin (no room for screw heads behind the cells)
    pl, pw = D("pi", "len"), D("pi", "wid")
    z0, yu, yt = P.PI_Z0, L["pi_yu"], L["pi_yt"]
    hi = D("pi", "hole_inset")
    pi_holes = [(sx * (pl / 2 - hi), z0 + zz) for sx in (-1, 1) for zz in (hi, pw - hi)]
    for (hx, hz) in pi_holes:
        post = cyl_y(L["back_in"] - 0.2, yt, hx, hz, 2.3).union(cyl_y(yt, yu + 0.4, hx, hz, D("pi", "hole_d") / 2 - P.TOL["pin"] - 0.05))
        cover = cover.union(post)

    # ---- lens opening, camera posts and lower cradle
    r_ring = P.RING_OD / 2
    tub = tub.cut(to_facet(cq.Workplane("XY").circle(r_ring + 0.1).extrude(6).translate((0, 0, -2))))
    af, ab = L["a_front"], L["a_back"]
    hu, (hv0, hv1) = L["cam_hu"], L["cam_hv"]
    for su in (-1, 1):
        p = cq.Workplane("XY").circle(1.6).extrude(af - wall + 0.3).translate((su * hu, hv1, wall - 0.3))
        rib = cq.Workplane("XY").box(1.2, 5.5, 7.0, centered=(True, False, False)).translate((su * hu, hv1, wall - 0.3))
        p = p.union(rib).cut(cq.Workplane("XY").circle(0.85).extrude(6.5).translate((su * hu, hv1, af - 6.0)))
        tub = tub.union(to_facet(p))
        cr = box(su * 11.5 - 0.9, su * 11.5 + 0.9, L["v0"] - 2.2, L["v0"] + 1.4, wall - 0.3, ab + 1.0)
        cr = cr.cut(box(-20, 20, L["v0"] - 0.15, L["v0"] + 5, af - 0.15, ab + 0.15))      # the board edge sits in this notch
        tub = tub.union(to_facet(cr))
    # keep the ring of LEDs clear of the posts and cradle
    tub = tub.cut(to_facet(cq.Workplane("XY").circle(r_ring + 0.3).extrude(5.0 - wall + 0.4).translate((0, 0, wall - 0.4))))

    # ---- openings in the tub
    for dx in P.DOT_X:                                                    # status dots
        tub = tub.cut(cyl_y(-4, 2, dx, P.DOT_Z, P.DOT_D / 2 + 0.05))
    sx = P.SPK_X
    sl, sw, sh = D("spk", "len"), D("spk", "wid"), D("spk", "h")
    for i in range(5):                                                    # speaker grille
        for j in range(8):
            tub = tub.cut(cyl_y(-4, 2, sx + (i - 2) * 2.4, P.SPK_Z0 + sl / 2 + (j - 3.5) * 2.2, 0.5))
    cl = P.TOL["slide"]
    tub = tub.cut(cyl_z(ceil - 2, P.UNIT_H + 2, P.ASK_XY[0], P.ASK_XY[1], P.ASK_D / 2 + cl))
    for bx in (-P.NAV_X, 0.0, P.NAV_X):
        tub = tub.cut(slot_xy(P.BAR_SIZE[0] + 2 * cl, P.BAR_SIZE[1] + 2 * cl, ceil - 2, P.UNIT_H + 2, bx, P.BAR_Y))
    ml, mw = D("mic", "len"), D("mic", "wid")
    mic_y1 = -10.4                                                        # front edge of the mic boards
    mic_port = (P.MIC_X0 + D("mic", "port_x"), mic_y1 - D("mic", "port_y"))
    for s in (-1, 1):
        tub = tub.cut(cyl_z(ceil - 2, P.UNIT_H + 2, s * mic_port[0], mic_port[1], 0.6))
    for vz in P.VOL_Z:                                                    # left side: volume
        tub = tub.cut(slot_yz(P.VOL_SIZE[0] + 2 * cl, P.VOL_SIZE[1] + 2 * cl, -P.UNIT_W / 2 - 2, -xin + 2, P.VOL_Y, vz))
    mute_y = -6.9
    tub = tub.cut(box(-P.UNIT_W / 2 - 2, -xin + 2, mute_y - 2.75, mute_y + 2.75, P.MUTE_Z - 1.3, P.MUTE_Z + 1.3))  # mute slot: cap 3.6 + 1.6 travel
    # DAC board (left) and charger board (right): their sockets pass through the side walls
    dl, dw, dh, dt = D("dac", "len"), D("dac", "wid"), D("dac", "h"), D("dac", "pcb_t")
    dac_yf = -11.5
    dac_z0 = round(facet_floor(dac_yf) + 0.45, 2)
    jack_y, jack_z = dac_yf - dt - (dh - dt) / 2, dac_z0 + D("dac", "jack_cy")
    tub = tub.cut(cyl_x(-P.UNIT_W / 2 - 2, -xin + 2, jack_y, jack_z, D("dac", "jack_barrel_d") / 2 + 0.2))
    gl, gw, gt_, ghh = D("chg", "len"), D("chg", "wid"), D("chg", "pcb_t"), D("chg", "h")
    chg_yf = -9.2
    chg_z0 = round(facet_floor(chg_yf) + 0.45, 2)
    uw, uh, ud = D("usbc", "w"), D("usbc", "h"), D("usbc", "d")
    usb_y, usb_z = chg_yf - gt_ - uh / 2, chg_z0 + D("chg", "usb_cy")
    tub = tub.cut(box(xin - 2, P.UNIT_W / 2 + 2, usb_y - uh / 2 - 0.2, usb_y + uh / 2 + 0.2, usb_z - uw / 2 - 0.25, usb_z + uw / 2 + 0.25))
    tub = tub.cut(cyl_z(-2, 3, P.CORD_ENTRY[0], P.CORD_ENTRY[1], P.CORD_D / 2 + 0.55))   # hub cord entry, between the tilt lugs

    add("shell_front_tub", tub, "unit", "abs_teal", budget="unit_shells", rho="petg", printed=True,
        label="Front shell (tub): front face, lens facet, top, sides, tilt lugs")
    add("shell_back_cover", cover, "unit", "abs_teal", budget="unit_shells", rho="petg", printed=True,
        label="Back cover with Pi standoffs")
    for n, (bx, bz, blen) in enumerate(boss_pts):
        s = cyl_y(-P.UNIT_D + 1.0, -P.UNIT_D + 1.0 + 6.5, bx, bz, st_d / 2).union(cyl_y(-P.UNIT_D + 1.0 - st_hh, -P.UNIT_D + 1.0, bx, bz, st_hd / 2))
        add(f"cover_screw_{n + 1}", s, "unit", "screw_black", budget="spreader_wiring", mass=0.15, part="st22",
            label="Cover screws, ST2.2 x 6.5 pan head tapping (4)")

    # ---- lens bezel and light-ring diffuser (no window: the lens front sits in the bezel)
    r_open = P.LENS_OPENING_D / 2
    bez = cq.Workplane("XY").circle(P.RING_ID / 2).circle(r_open).extrude(wall)
    bez = bez.faces("<Z").edges(cq.selectors.RadiusNthSelector(0)).chamfer(0.8)
    add("lens_bezel", to_facet(bez), "unit", "blue_ring", budget="unit_shells", rho="al",
        label="Lens bezel ring (pale blue), chamfered so it does not shade the lens")
    dif = cq.Workplane("XY").circle(r_ring).circle(P.RING_ID / 2).extrude(wall + 0.6)
    add("light_ring_diffuser", to_facet(dif), "unit", "diffuser", budget="unit_shells", rho="petg", printed=True,
        label="Light-ring diffuser (print in natural / clear PETG)")
    lw_, lh_, lt_ = D("led_ring", "len"), D("led_ring", "wid"), D("led_ring", "h")
    a_led = wall + 0.6 + 0.2
    ring = cq.Workplane("XY").circle(r_ring).circle(D("cam", "lens_head_d") / 2 + 0.4).extrude(1.0).translate((0, 0, a_led + lt_))
    add("light_ring_pcb", to_facet(ring), "unit", "pcb_white", budget="leds_buttons_motor", mass=0.6,
        label="Light-ring LED board (6 warm-white LEDs, PWM on GPIO 12)")
    leds = []
    r_led = (r_ring + D("cam", "lens_head_d") / 2 + 0.4) / 2
    for k in range(6):
        a = math.radians(60 * k)
        l = cq.Workplane("XY").box(lw_, lh_, lt_, centered=(True, True, False)).rotate((0, 0, 0), (0, 0, 1), math.degrees(a) + 90) \
            .translate((r_led * math.cos(a), r_led * math.sin(a), a_led))
        leds.append(to_facet(l))
    add("light_ring_leds", group(leds), "unit", "led_warm", budget="leds_buttons_motor", mass=0.2, part="led_ring",
        label="Light-ring LEDs: 6 x 2835, 2700 K, CRI 90")

    # ---- camera: lens, holder, board, connector (Arducam B0310)
    a0, ar, ah = L["a_apex"], L["a_rim"], L["a_holder"]
    r_rim, r_head, r_thr = D("cam", "lens_rim_d") / 2, D("cam", "lens_head_d") / 2, D("cam", "lens_thread_d") / 2
    a_head1 = ar + 0.6 + D("cam", "lens_head_len")
    lens = cq.Workplane("XY").circle(r_rim).extrude(0.6).translate((0, 0, ar)) \
        .union(cq.Workplane("XY").circle(r_head).extrude(a_head1 - ar - 0.6).translate((0, 0, ar + 0.6))) \
        .union(cq.Workplane("XY").circle(r_thr).extrude(af - 0.9 - a_head1).translate((0, 0, a_head1)))
    lens = lens.cut(cq.Workplane("XY").circle(r_rim - 1.1).extrude(0.5).translate((0, 0, ar - 0.01)))
    add("camera_lens_m12", to_facet(lens), "unit", "lens_black", budget="camera_m12", mass=5.0, part="cam",
        label="M12 ultra-wide lens, 120 degrees across (on the Arducam B0310)")
    rg = r_rim - 1.15
    hcap = ar - a0
    Rs = (hcap * hcap + rg * rg) / (2 * hcap)
    glass = cq.Workplane("XY").circle(rg).extrude(hcap + 0.45).translate((0, 0, a0)) \
        .intersect(sphere((0, 0, a0 + Rs), Rs))
    add("camera_lens_glass", to_facet(glass), "unit", "lens_glass", budget="camera_m12", mass=0.3,
        label="Lens front element")
    hw_, hd_ = D("cam", "holder_w"), D("cam", "holder_d")
    hold = cq.Workplane("XY").circle(hd_ / 2).extrude(af - ah).translate((0, 0, ah))
    ears = cq.Workplane("XY").box(D("cam", "holder_screw_pitch"), 4.0, 2.0, centered=(True, True, False)).translate((0, 0, af - 2.0))
    for su in (-1, 1):
        ears = ears.union(cq.Workplane("XY").circle(2.0).extrude(2.0).translate((su * D("cam", "holder_screw_pitch") / 2, 0, af - 2.0)))
    hold = hold.union(ears).cut(cq.Workplane("XY").circle(r_thr + 0.02).extrude(af - ah + 1).translate((0, 0, ah - 0.5)))
    add("camera_holder_m12", to_facet(hold), "unit", "plastic_black", budget="camera_m12", mass=1.6, part="cam",
        label="M12 lens holder (part of the camera)")
    bw_ = D("cam", "board_w")
    brd = box(-bw_ / 2, bw_ / 2, L["v0"], L["v1"], af, ab).edges("|Z").fillet(D("cam", "corner_r"))
    for su in (-1, 1):
        for v in (hv0, hv1):
            brd = brd.cut(cyl_z(af - 1, ab + 1, su * hu, v, D("cam", "hole_d") / 2))
    add("camera_board_imx708", to_facet(brd), "unit", "pcb_black", budget="camera_m12", mass=1.8, part="cam",
        label="Camera board, 12 MP IMX708 (Arducam B0310)")
    cw_, cd_, ch_ = D("cam", "conn_w"), D("cam", "conn_d"), D("cam", "conn_h")
    conn = box(-cw_ / 2, cw_ / 2, L["v1"] + D("cam", "conn_over") - cd_, L["v1"] + D("cam", "conn_over"), ab, ab + ch_)
    add("camera_connector", to_facet(conn), "unit", "ic_black", budget="camera_m12", mass=0.3, part="cam",
        label="Camera flex connector (15-pin)")
    scr = [to_facet(cyl_z(ab, ab + st_hh, su * hu, hv1, st_hd / 2).union(cyl_z(ab - 6.0, ab, su * hu, hv1, st_d / 2))) for su in (-1, 1)]
    add("camera_screws", group(scr), "unit", "screw_black", budget="spreader_wiring", mass=0.3, part="st22",
        label="Camera screws, ST2.2 x 6.5 (2)")

    # ---- Pi Zero 2 W (parts face the back cover); positions from the Raspberry Pi drawing
    def pb(bx0, bx1, by0, by1, h):                # drawing coordinates (X from the SD end, Y from the connector edge)
        return box(pl / 2 - bx1, pl / 2 - bx0, yt - h, yt, z0 + by0, z0 + by1)

    pcb = box(-pl / 2, pl / 2, yt, yu, z0, z0 + pw).edges("|Y").fillet(D("pi", "corner_r"))
    for (hx, hz) in pi_holes:
        pcb = pcb.cut(cyl_y(yt - 1, yu + 1, hx, hz, D("pi", "hole_d") / 2))
    add("pi_zero_2w_pcb", pcb, "unit", "pcb_green", budget="pi_zero_2w", mass=D("pi", "mass_g"), part="pi",
        label="Raspberry Pi Zero 2 W")
    sip, can = D("pi", "sip"), D("pi", "can")
    chips = group([pb(D("pi", "sip_cx") - sip / 2, D("pi", "sip_cx") + sip / 2, D("pi", "sip_cy") - sip / 2, D("pi", "sip_cy") + sip / 2, D("pi", "sip_h")),
                   pb(D("pi", "can_cx") - can / 2, D("pi", "can_cx") + can / 2, D("pi", "can_cy") - can / 2, D("pi", "can_cy") + can / 2, D("pi", "can_h")),
                   pb(pl - D("pi", "csi_d"), pl, D("pi", "csi_cy") - D("pi", "csi_w") / 2, D("pi", "csi_cy") + D("pi", "csi_w") / 2, D("pi", "csi_h"))])
    add("pi_zero_2w_chips", chips, "unit", "ic_black", budget="pi_zero_2w", mass=0.0, part="pi",
        label="Pi: RP3A0 SiP, radio can, camera connector")
    conns = group([pb(D("pi", "hdmi_cx") - D("pi", "hdmi_w") / 2, D("pi", "hdmi_cx") + D("pi", "hdmi_w") / 2, -D("pi", "hdmi_over"),
                      D("pi", "hdmi_d") - D("pi", "hdmi_over"), D("pi", "hdmi_h")),
                   pb(D("pi", "usb_cx1") - D("pi", "usb_w") / 2, D("pi", "usb_cx1") + D("pi", "usb_w") / 2, -D("pi", "usb_over"),
                      D("pi", "usb_d") - D("pi", "usb_over"), D("pi", "usb_h")),
                   pb(D("pi", "usb_cx2") - D("pi", "usb_w") / 2, D("pi", "usb_cx2") + D("pi", "usb_w") / 2, -D("pi", "usb_over"),
                      D("pi", "usb_d") - D("pi", "usb_over"), D("pi", "usb_h")),
                   pb(D("pi", "sd_x0"), D("pi", "sd_x1"), D("pi", "sd_cy") - D("pi", "sd_w") / 2, D("pi", "sd_cy") + D("pi", "sd_w") / 2, D("pi", "sd_h"))])
    add("pi_zero_2w_connectors", conns, "unit", "metal_tin", budget="pi_zero_2w", mass=0.0, part="pi",
        label="Pi: mini-HDMI, 2 micro-USB, microSD slot (not used in normal use)")
    gp = D("pi", "gpio_pitch")
    gpio = box(pl / 2 - D("pi", "gpio_cx") - 10 * gp, pl / 2 - D("pi", "gpio_cx") + 10 * gp, yu, yu + 0.05,
               z0 + D("pi", "gpio_cy") - gp, z0 + D("pi", "gpio_cy") + gp)
    add("pi_gpio_pads", gpio, "unit", "gold", budget="pi_zero_2w", mass=0.0, part="pi",
        label="Pi GPIO pads (wires soldered here)")
    sd_out = D("sd", "len") - D("pi", "sd_x1")
    sd = pb(-sd_out, 0.0, D("pi", "sd_cy") - D("sd", "wid") / 2, D("pi", "sd_cy") + D("sd", "wid") / 2, 1.25).intersect(
        box(-100, 100, yt - 1.25, yt - 0.25, -100, 100))
    add("microsd_card", sd, "unit", "ic_black", budget="pi_zero_2w", mass=0.3, part="sd",
        label="microSD card, 32 GB (the part that sticks out)")

    # ---- heat spreader + thermal pad (SiP -> pad -> aluminium plate on the cover)
    sx0, sx1 = pl / 2 - D("pi", "sip_cx") - sip / 2, pl / 2 - D("pi", "sip_cx") + sip / 2
    spx = (sx0 + sx1) / 2
    szc = z0 + D("pi", "sip_cy")
    spr = box(spx - P.SPREADER[0] / 2, spx + P.SPREADER[0] / 2, L["back_in"], L["back_in"] + P.SPREADER[2],
              szc - 6.0, szc - 6.0 + P.SPREADER[1])
    add("heat_spreader", spr, "unit", "aluminium", budget="spreader_wiring", rho="al",
        label="Aluminium heat spreader, 40 x 21 x 1 mm, bonded to the cover")
    pad = box(sx0, sx1, L["back_in"] + P.SPREADER[2], yt - D("pi", "sip_h"), szc - sip / 2, szc + sip / 2)
    add("thermal_pad", pad, "unit", "pad_grey", budget="spreader_wiring", mass=0.6,
        label="Thermal pad, 15 x 15 mm, fills the gap from the Pi's main chip to the spreader")

    # ---- cells (Akyga LP902535 packs: protection board at the top end, leads leave the top)
    ct, cwid, clen = D("cell", "t_max"), D("cell", "w_max"), D("cell", "len_max")
    cx0, cy1, cz0 = L["cell_x0"], L["cell_y1"], P.CELL_Z0
    pcm_h = clen - D("cell", "len_bare_max")
    cell = box(cx0, cx0 + cwid, cy1 - ct, cy1, cz0, cz0 + clen - pcm_h).edges().fillet(1.5)
    pcm = box(cx0 + 1.5, cx0 + cwid - 1.5, cy1 - ct + 1.0, cy1 - 1.0, cz0 + clen - pcm_h, cz0 + clen)
    foam = box(cx0 + 2.0, cx0 + 12.0, cy1 - ct - 0.7, cy1 - ct, cz0 + 4.0, cz0 + clen - 6.0)
    for s, nm in ((1, "right"), (-1, "left")):
        m = (lambda w: w) if s > 0 else mirror_x
        add(f"cell_{nm}", m(cell), "unit", "pouch_silver", budget="lipo_cells", mass=D("cell", "mass_g"), part="cell",
            label=f"LiPo cell pack LP902535, 800 mAh ({nm})")
        add(f"cell_pcm_{nm}", m(pcm), "unit", "kapton", budget="lipo_cells", mass=0.0, part="cell",
            label="Cell protection board (top end of the pack)")
        add(f"cell_foam_{nm}", m(foam), "unit", "foam", budget="spreader_wiring", mass=0.1,
            label="Foam pad, 0.7 mm, behind each cell")

    # ---- speaker (Same Sky CES-20134-088PM), standing behind the grille
    yf = -wall - 0.1
    spk = box(sx - sw / 2, sx + sw / 2, yf - sh, yf, P.SPK_Z0, P.SPK_Z0 + sl).edges("|Y").fillet(1.5)
    lz_ = P.SPK_Z0 + D("spk", "lug_from_end")
    for s in (-1, 1):
        lx = sx + s * D("spk", "lug_pitch") / 2
        lugp = cyl_y(yf - D("spk", "lug_t"), yf, lx, lz_, D("spk", "lug_d") / 2).union(
            box(min(lx, sx + s * sw / 2), max(lx, sx + s * sw / 2), yf - D("spk", "lug_t"), yf, lz_ - 2.5, lz_ + 2.5))
        spk = spk.union(lugp.cut(cyl_y(yf - 2, yf + 1, lx, lz_, D("spk", "lug_hole_d") / 2)))
    add("speaker", spk, "unit", "speaker", budget="speaker", mass=D("spk", "mass_g"), part="spk",
        label="Enclosed micro speaker, 20 x 13 x 4.9 mm, 8 ohm 0.8 W")

    # ---- left front: amp board, then the DAC board with its jack
    al_, aw_, ah_, at_ = D("amp", "len"), D("amp", "wid"), D("amp", "h"), D("amp", "pcb_t")
    amp_yf, amp_x1 = -6.2, -18.4
    amp_z0 = round(facet_floor(amp_yf) + 0.45, 2)
    amp = box(amp_x1 - al_, amp_x1, amp_yf - at_, amp_yf, amp_z0, amp_z0 + aw_)
    for hx in (2.54, 15.24):
        amp = amp.cut(cyl_y(amp_yf - 3, amp_yf + 1, amp_x1 - al_ + 16.51, amp_z0 + hx, D("amp", "hole_d") / 2))
    add("amp_board_max98357a", amp, "unit", "pcb_blue", budget="audio_boards", mass=D("amp", "mass_g"), part="amp",
        label="MAX98357A I2S speaker amp breakout (Adafruit 3006)")
    amp_parts = group([box(amp_x1 - al_ + 6.5, amp_x1 - al_ + 10.5, amp_yf - ah_, amp_yf - at_, amp_z0 + 6.5, amp_z0 + 10.5),
                       box(amp_x1 - al_ + 2.0, amp_x1 - al_ + 5.0, amp_yf - ah_, amp_yf - at_, amp_z0 + 11.5, amp_z0 + 14.5)])
    add("amp_board_parts", amp_parts, "unit", "ic_black", budget="audio_boards", mass=0.0, part="amp",
        label="Amp parts")
    dx0 = -xin + P.TOL["seat"]
    dac = box(dx0, dx0 + dl, dac_yf - dt, dac_yf, dac_z0, dac_z0 + dw)
    hi_d = D("dac", "hole_inset")
    for hx in (hi_d, dl - hi_d):
        for hz in (hi_d, dw - hi_d):
            dac = dac.cut(cyl_y(dac_yf - 3, dac_yf + 1, dx0 + hx, dac_z0 + hz, D("dac", "hole_d") / 2))
    add("dac_board_pcm5102", dac, "unit", "pcb_purple", budget="audio_boards", mass=D("dac", "mass_g"), part="dac",
        label="PCM5102 I2S DAC board with 3.5 mm jack (Adafruit 6250)")
    jl, jw = D("dac", "jack_len"), D("dac", "jack_w")
    jk = box(dx0, dx0 + jl, dac_yf - dh, dac_yf - dt, jack_z - jw / 2, jack_z + jw / 2).union(
        cyl_x(dx0 - (D("dac", "len_with_jack") - dl), dx0, jack_y, jack_z, D("dac", "jack_barrel_d") / 2)).cut(
        cyl_x(dx0 - 5, dx0 + 8, jack_y, jack_z, 1.8))
    dchip = box(dx0 + 17.0, dx0 + 23.5, dac_yf - dt - 1.2, dac_yf - dt, dac_z0 + 7.0, dac_z0 + 12.0)
    add("dac_jack", group([jk, dchip]), "unit", "plastic_black", budget="audio_boards", mass=0.0, part="dac",
        label="3.5 mm headphone jack (on the DAC board) and DAC chip")

    # ---- microphones: flat under the top, sound comes in through a hole in the board
    mt_, mh_ = D("mic", "pcb_t"), D("mic", "h")
    mic = box(P.MIC_X0, P.MIC_X0 + ml, mic_y1 - mw, mic_y1, ceil - mt_, ceil).cut(cyl_z(ceil - 2, ceil + 1, mic_port[0], mic_port[1], D("mic", "port_d") / 2))
    mic_can = box(mic_port[0] - 1.75, mic_port[0] + 1.75, mic_port[1] - 0.6, mic_port[1] + 2.05, ceil - mh_, ceil - mt_)
    for s, nm in ((1, "right"), (-1, "left")):
        m = (lambda w: w) if s > 0 else mirror_x
        add(f"mic_{nm}", m(group([mic, mic_can])), "unit", "pcb_blue", budget="audio_boards", mass=D("mic", "mass_g"), part="mic",
            label=f"I2S MEMS microphone breakout, SPH0645 ({nm})")

    # ---- right front: charger + boost board with USB-C, then the fuel gauge
    gx1 = xin - 0.3
    chg = box(gx1 - gl, gx1, chg_yf - gt_, chg_yf, chg_z0, chg_z0 + gw)
    hi_c = D("chg", "hole_inset")
    for hx in (hi_c, gl - hi_c):
        for hz in (hi_c, gw - hi_c):
            chg = chg.cut(cyl_y(chg_yf - 3, chg_yf + 1, gx1 - hx, chg_z0 + hz, D("chg", "hole_d") / 2))
    add("charger_board", chg, "unit", "pcb_blue", budget="power_boards", mass=D("chg", "mass_g"), part="chg",
        label="bq25185 USB-C charger with 5 V boost (Adafruit 6106)")
    chg_parts = group([box(gx1 - 18.0, gx1 - 13.0, chg_yf - ghh, chg_yf - gt_, chg_z0 + 4.0, chg_z0 + 9.0),
                       box(gx1 - 25.5, gx1 - 21.5, chg_yf - gt_ - 2.0, chg_yf - gt_, chg_z0 + 11.0, chg_z0 + 15.0)])
    add("charger_board_parts", chg_parts, "unit", "ic_black", budget="power_boards", mass=0.0, part="chg",
        label="Charger / boost parts (inductor, chip)")
    usb = box(P.UNIT_W / 2 - 0.25 - ud, P.UNIT_W / 2 - 0.25, usb_y - uh / 2, usb_y + uh / 2, usb_z - uw / 2, usb_z + uw / 2).edges("|X").fillet(1.2)
    add("usb_c_receptacle", usb, "unit", "metal_tin", budget="power_boards", mass=0.0, part="usbc",
        label="USB-C socket (on the charger board): charging and power-bank use")
    ggl, ggw, ggt, ggh = D("gauge", "len"), D("gauge", "wid"), D("gauge", "pcb_t"), D("gauge", "h_no_connectors")
    gau_yf = chg_yf - ghh - 0.6
    gau_z0 = round(facet_floor(gau_yf) + 0.45, 2)
    gau = box(15.0, 15.0 + ggl, gau_yf - ggt, gau_yf, gau_z0, gau_z0 + ggw)
    gau_ic = box(15.0 + 11.0, 15.0 + 14.0, gau_yf - ggh, gau_yf - ggt, gau_z0 + 8.5, gau_z0 + 11.5)
    add("fuel_gauge_max17048", group([gau, gau_ic]), "unit", "pcb_red", budget="power_boards", mass=D("gauge", "mass_g"), part="gauge",
        label="MAX17048 fuel gauge (Adafruit 5580, connectors removed)")

    # ---- status dots: LED strip board + four light pipes
    dlh = D("led_dot", "h")
    dots = box(-37, -13, -3.4, -2.6, P.DOT_Z - 2.3, P.DOT_Z + 2.3)
    dled = group([box(dx - D("led_dot", "len") / 2, dx + D("led_dot", "len") / 2, -2.6, -2.6 + dlh,
                      P.DOT_Z - D("led_dot", "wid") / 2, P.DOT_Z + D("led_dot", "wid") / 2) for dx in P.DOT_X])
    add("status_led_board", dots, "unit", "pcb_white", budget="leds_buttons_motor", mass=0.4,
        label="Status LED board (ready, listening, sending, battery)")
    add("status_leds", dled, "unit", "led_warm", budget="leds_buttons_motor", mass=0.05, part="led_dot",
        label="Status LEDs: 4 x white 0603")
    pipes = group([cyl_y(-2.6 + dlh + 0.1, 0.0, dx, P.DOT_Z, P.DOT_D / 2) for dx in P.DOT_X])
    add("status_dot_pipes", pipes, "unit", "dot_white", budget="unit_shells", rho="petg", printed=True,
        label="Four status-dot light pipes (clear)")

    # ---- top buttons: caps, switches, boards
    tw, th_ = D("tact", "w"), D("tact", "h")
    zc0 = ceil - 1.0                                # underside of the cap flanges
    zs0 = zc0 - th_                                 # top face of the switch boards

    def tact(x, y):
        return box(x - tw / 2, x + tw / 2, y - tw / 2, y + tw / 2, zs0, zc0)

    ax, ay = P.ASK_XY
    ask = cyl_z(zc0, P.UNIT_H + 0.6, ax, ay, P.ASK_D / 2).union(cyl_z(zc0, ceil, ax, ay, P.ASK_D / 2 + 1.0))
    dish = sphere((ax, ay, P.UNIT_H + 0.6 + 16.0 - 1.1), 16.0)
    ask = ask.cut(dish).union(cyl_z(P.UNIT_H - 0.6, P.UNIT_H + 0.1, ax, ay, 1.0))
    add("button_ask", ask, "unit", "marigold", budget="unit_shells", rho="petg", printed=True,
        label="Ask button (concave, marigold, raised dot): hold to talk")
    bl, bw2 = P.BAR_SIZE

    def bar(x):
        return slot_xy(bl, bw2, zc0, P.UNIT_H + 0.8, x, P.BAR_Y).union(slot_xy(bl + 1.6, bw2 + 1.6, zc0, ceil, x, P.BAR_Y))

    play = bar(0.0).union(cyl_z(P.UNIT_H + 0.8, P.UNIT_H + 1.3, 0.0, P.BAR_Y, 1.0))
    add("button_play_pause", play, "unit", "abs_light", budget="unit_shells", rho="petg", printed=True,
        label="Play / Pause (bar with a raised dot)")
    for s, nm, lab in ((-1, "back", "Back (bar with an arrow pointing left)"), (1, "forward", "Forward (bar with an arrow pointing right)")):
        nx = s * P.NAV_X
        tri = cq.Workplane("XY").polyline([(s * 2.6, 0), (-s * 1.4, 1.7), (-s * 1.4, -1.7)]).close().extrude(0.6) \
            .translate((nx, P.BAR_Y, P.UNIT_H + 0.8))
        add(f"button_{nm}", bar(nx).union(tri), "unit", "abs_light", budget="unit_shells", rho="petg", printed=True, label=lab)
    bar_pcb = box(-P.NAV_X - 6.5, P.NAV_X + 6.5, P.BAR_Y - 3.1, P.BAR_Y + 2.9, zs0 - 0.8, zs0)
    add("top_bar_board", bar_pcb, "unit", "pcb_green2", budget="leds_buttons_motor", mass=0.6,
        label="Button board: Back, Play/Pause, Forward")
    add("top_bar_switches", group([tact(-P.NAV_X, P.BAR_Y), tact(0.0, P.BAR_Y), tact(P.NAV_X, P.BAR_Y)]), "unit", "ic_black",
        budget="leds_buttons_motor", mass=0.1, part="tact", label="Tactile switches (3)")
    ask_pcb = box(ax - 6.5, ax + 6.5, ay - 6.5, ay + 6.5, zs0 - 0.8, zs0)
    add("ask_button_board", group([ask_pcb, tact(ax, ay)]), "unit", "pcb_green2", budget="leds_buttons_motor", mass=0.3, part="tact",
        label="Button board: Ask")

    # ---- left side: volume buttons, mic-mute slide switch
    xl = -xin
    for vz, nm, lab in ((P.VOL_Z[0], "vol_up", "Volume + (raised dot)"), (P.VOL_Z[1], "vol_down", "Volume -")):
        cap = slot_yz(P.VOL_SIZE[0], P.VOL_SIZE[1], -P.UNIT_W / 2 - 0.7, xl + 1.0, P.VOL_Y, vz) \
            .union(slot_yz(P.VOL_SIZE[0] + 1.2, P.VOL_SIZE[1] + 1.2, xl, xl + 1.0, P.VOL_Y, vz))   # 0.6 mm retaining lip
        if nm == "vol_up":
            cap = cap.union(cyl_x(-P.UNIT_W / 2 - 1.2, -P.UNIT_W / 2 - 0.6, P.VOL_Y, vz, 0.8))
        add(f"button_{nm}", cap, "unit", "abs_light", budget="unit_shells", rho="petg", printed=True, label=lab)
    vol_pcb = box(xl + 1.0 + th_, xl + 1.8 + th_, P.VOL_Y - 3.5, P.VOL_Y + 3.5, P.VOL_Z[1] - 3.5, P.VOL_Z[0] + 3.5)
    vol_sw = group([box(xl + 1.0, xl + 1.0 + th_, P.VOL_Y - tw / 2, P.VOL_Y + tw / 2, vz - tw / 2, vz + tw / 2) for vz in P.VOL_Z])
    add("volume_board", group([vol_pcb, vol_sw]), "unit", "pcb_green2", budget="leds_buttons_motor", mass=0.5, part="tact",
        label="Volume switch board (2 tactile switches)")
    sll, sld, slh, lev = D("slide", "len"), D("slide", "d"), D("slide", "h"), D("slide", "lever_len")
    msx = xl + 0.1 + lev                             # switch body starts here; the lever reaches the wall
    mute_pcb = box(msx - 0.3, msx + sld + 1.2, mute_y - sll / 2 - 0.2, mute_y + sll / 2 + 0.2, P.MUTE_Z - slh / 2 - 0.8, P.MUTE_Z - slh / 2)
    mute_body = box(msx, msx + sld, mute_y - sll / 2, mute_y + sll / 2, P.MUTE_Z - slh / 2, P.MUTE_Z + slh / 2)
    mute_lever = box(msx - lev, msx, mute_y - 0.8 - D("slide", "lever_w") / 2, mute_y - 0.8 + D("slide", "lever_w") / 2,
                     P.MUTE_Z - D("slide", "lever_t") / 2, P.MUTE_Z + D("slide", "lever_t") / 2)
    add("mic_mute_switch", group([mute_pcb, mute_body, mute_lever]), "unit", "metal_tin", budget="leds_buttons_motor", mass=0.4, part="slide",
        label="Mic-mute slide switch MSK12C02 on its small board (GPIO 16, low = muted)")
    knob = box(-P.UNIT_W / 2 - 1.0, xl - 0.05, mute_y - 2.6, mute_y + 1.0, P.MUTE_Z - 1.1, P.MUTE_Z + 1.1) \
        .cut(box(xl - 1.3, xl, mute_y - 0.8 - 0.75, mute_y - 0.8 + 0.75, P.MUTE_Z - 0.6, P.MUTE_Z + 0.6))
    add("mic_mute_slider", knob, "unit", "abs_light", budget="unit_shells", rho="petg", printed=True,
        label="Mic-mute slider cap (grips the switch lever)")
    flag = box(-P.UNIT_W / 2 + 0.25, -P.UNIT_W / 2 + 0.75, mute_y + 1.15, mute_y + 2.6, P.MUTE_Z - 1.1, P.MUTE_Z + 1.1)
    add("mic_mute_flag", flag, "unit", "orange_flag", budget="unit_shells", mass=0.02,
        label="Orange flag: shows when the mic is muted")

    # ---- haptic motor (Vybronics VC1026B002F) on the front wall
    mot = cyl_y(yf - D("motor", "t"), yf, -24.0, 27.5, D("motor", "d") / 2)
    add("haptic_motor", mot, "unit", "metal_tin", budget="leds_buttons_motor", mass=D("motor", "mass_g"), part="motor",
        label="Coin vibration motor, 10 x 2.7 mm (GPIO 11 via transistor)")

    # ---- wiring routes (main bundles; lengths and clearances are checked)
    zt = z0 + pw                                    # Pi top edge
    zg = z0 + D("pi", "gpio_cy")
    add_wire("harness_left", [(-10.5, yu + 0.8, zg), (-10.5, yu + 0.8, zt + 1.6), (-10.5, -12.5, zt + 1.7), (-20.0, -10.4, zt + 0.3),
                              (-28.0, -10.2, amp_z0 + aw_ + 2.0), (-28.0, -9.9, amp_z0 + aw_ + 0.9)], 0.7,
             "Harness, left: I2S to the amp and DAC, buttons, LEDs, motor", mass=0.9)
    add_wire("harness_right", [(10.5, yu + 0.8, zg), (10.5, yu + 0.8, zt + 1.6), (10.5, -12.5, zt + 1.7), (17.0, -12.6, chg_z0 + gw + 3.2),
                               (20.5, -12.6, chg_z0 + gw + 1.2)], 0.7,
             "Harness, right: 5 V, I2C to the fuel gauge", mass=0.7)
    zl = cz0 + clen + 0.8
    add_wire("battery_leads", [(-26.0, cy1 - ct / 2, zl), (-26.0, yt - 0.9, zt + 1.4), (26.0, yt - 0.9, zt + 1.4), (26.0, cy1 - ct / 2, zl),
                               (26.0, cy1 + 0.9, zl), (26.0, cy1 + 2.9, chg_z0 + gw + 5.0), (26.0, chg_yf - gt_ - 1.2, chg_z0 + gw + 0.8)], 0.7,
             "Battery leads: both packs in parallel to the charger board", mass=1.6)
    add_wire("speaker_leads", [(-28.0, amp_yf - 0.8, amp_z0 + aw_ + 0.5), (-12.5, -2.8, 35.4), (12.5, -2.8, 35.9), (13.7, -4.3, 35.6)], 0.45,
             "Speaker leads from the amp", mass=0.2)
    # hub-sensor cord: leaves the back of the joint head (see build_mechanics), enters the unit between the lugs,
    # runs up between the cells behind the camera and ends on the Pi's GPIO pads beside the left harness
    ex, ey = P.CORD_ENTRY
    c_, s_ = math.cos(math.radians(TIP0)), math.sin(math.radians(TIP0))
    dy_, dz_ = -(P.STICK_OD_INNER / 2 + 0.3), CORD_EXIT_Z - P.JOINT_ABOVE_STICK          # head exit, relative to the pivot (book frame)
    exit_u = (0.0, P.PIVOT_Y + c_ * dy_ - s_ * dz_, P.PIVOT_Z + s_ * dy_ + c_ * dz_)       # the same point in the unit frame
    add_wire("hub_cord_tail", [exit_u, (ex, ey + 0.3, exit_u[2] + 0.6), (ex, ey, -2.0), (ex, ey, 6.0), (-9.0, -27.6, 9.0),
                               (-9.0, -27.6, zg - 2.2), (-9.0, yu + 0.05 + P.CORD_D / 2 + 0.1, zg - 0.5)], P.CORD_D / 2,
             "Hub-sensor cord: from the joint head into the unit, up to the Pi (GPIO 8 and ground)", mass=0.3, budget="stick_tubes_cord")
    # camera flex: Pi connector -> folded back along the Pi underside -> up -> forward over the camera -> down into its connector
    w22, w15, ft = D("fpc", "w22"), D("fpc", "w15"), 0.15
    zc = z0 + D("pi", "csi_cy")
    cy_, cz_ = fpt(ab + ch_ / 2, 0, L["v1"] + D("cam", "conn_over") + 0.4)[1:]
    zf = zt + 0.95
    fx = group([box(-pl / 2 - 2.6, -pl / 2 + 1.0, yt - 0.9, yt - 0.9 + ft, zc - w22 / 2, zc + w22 / 2),
                box(-pl / 2 - 2.6, -pl / 2 - 2.6 + ft, yt - 0.9, yu + 0.2 + ft, zc - w22 / 2, zc + w22 / 2),
                box(-pl / 2 - 2.6, w15 / 2, yu + 0.2, yu + 0.2 + ft, zc - w22 / 2, zc + w22 / 2),
                box(-w15 / 2, w15 / 2, yu + 0.2, yu + 0.2 + ft, zc + w22 / 2, zf),
                box(-w15 / 2, w15 / 2, yu + 0.2, cy_ + ft, zf, zf + ft),
                box(-w15 / 2, w15 / 2, cy_, cy_ + ft, cz_, zf)])
    flex_len = 3.6 + (yu + 0.2 - (yt - 0.9)) + (pl / 2 + 2.6) + (zf - zc) + (cy_ - (yu + 0.2)) + (zf - cz_)
    ROUTES["camera_flex"] = dict(points=[], radius=ft / 2, length=round(flex_len, 1), stock_length=D("fpc", "len"), width=w15)
    add("camera_flex", fx, "unit", "flex_amber", budget="spreader_wiring", mass=0.8, part="fpc",
        label="Camera flex, 22-pin to 15-pin, folded along the Pi and over the camera")
    LAY.update(L)
    LAY.update(dict(jack=(jack_y, jack_z), usb=(usb_y, usb_z), usb_open=(uh + 0.4, uw + 0.5), mic_port=mic_port, mic_y1=mic_y1, mute_y=mute_y,
                    boss_pts=boss_pts, cam_post=(hu, hv1), dac=(dx0, dac_yf, dac_z0), chg=(gx1, chg_yf, chg_z0), amp=(amp_x1, amp_yf, amp_z0),
                    gauge=(15.0, gau_yf, gau_z0), pi_holes=pi_holes, pi_pin_d=2 * (D("pi", "hole_d") / 2 - P.TOL["pin"] - 0.05),
                    cap_seat_z=zc0, switch_board_z=zs0, cord_exit=exit_u))
    return tub, cover


def add_wire(name, pts, r, label, mass=0.3, budget="spreader_wiring"):
    ROUTES[name] = dict(points=[list(p) for p in pts], radius=r,
                        length=round(sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:])), 1))
    mat = "wire_red" if name.startswith("battery") else "wire_black" if name.startswith(("speaker", "hub")) else "wire_multi"
    add(name, wire(pts, r), "unit", mat, budget=budget, mass=mass, label=label)


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
    root = root.cut(cyl_z(zr - 2, zr + 2, bx, P.CLAMP_Y, 0.9))                     # clamp-screw hole, dia 1.8
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
    sp_id, sp_wire, sp_len = P.PD("spring", "id"), P.PD("spring", "wire"), P.PD("spring", "body_len")
    sp_or = sp_id / 2 + sp_wire                                                                  # spring outer radius
    r_barrel = sp_id / 2 - 0.15                                                                  # the springs ride on the leg barrel
    x_sp0, x_sp1 = 4.9, 4.9 + sp_len                                                             # each spring, either side of the leg
    hub = box(-hw, hw, sy - hd, sy + hd, hub_top - P.HUB_H, hub_top).edges("|Z").fillet(3.0).faces(">Z").edges().fillet(1.2)
    rear = box(-hw, hw, ly - 5.6, sy - hd + 1.0, lz - 5.6, 0.5).edges("|X").fillet(2.4)
    hub = hub.union(rear)
    hub = hub.cut(cyl_z(P.TUBE_OUT_Z[0], hub_top + 1, 0, sy, ro_bore))                           # stick bore
    hub = hub.cut(box(-4.6, 4.6, ly - 12, ly + 1.6, -30, 30))                                    # leg swing slot (back)
    hub = hub.cut(box(-4.6, 4.6, ly - 12, sy + hd + 1, -30, P.TUBE_OUT_Z[0]))                    # leg swing slot (underneath), up to the foot of the tube
    hub = hub.cut(box(-4.6, 4.6, ly - 12, sy - ro_bore + 0.05, -30, lz + 1.6))                   # arm clearance next to the pivot
    hub = hub.cut(cyl_x(-x_sp1 - 0.3, x_sp1 + 0.3, ly, lz, r_barrel + 0.35))                     # barrel cavity
    for s in (-1, 1):
        x0, x1 = sorted((s * 4.6, s * (x_sp1 + 0.3)))
        hub = hub.cut(cyl_x(x0, x1, ly, lz, sp_or + 0.25))                                       # spring cavities
    hub = hub.cut(cyl_x(-hw - 1, hw + 1, ly, lz, 1.0 + P.TOL["pin"]))                            # leg pin
    hub = hub.cut(box(-2.0, 2.0, ly + 1.5, sy - 4.4, 1.3, 4.7))                                  # sensor pocket, behind the stick, open to the bore
    gx0, gx1 = 5.0, 6.2                                                                          # lead groove, 1.2 wide for the 0.9 mm lead
    hub = hub.cut(box(2.0, gx1, sy - 6.6, sy - 5.4, 2.4, 3.6))                                   # from the sensor board sideways
    hub = hub.cut(box(gx0, gx1, sy - 6.6, sy - 4.0, 2.4, 3.6))                                   # short jog forward
    hub = hub.cut(box(gx0, gx1, sy - 5.2, sy - 4.0, -7.5, 3.6))                                  # down beside the bore
    hub = hub.cut(box(gx0, gx1, sy - 5.2, sy - 0.7, -7.5, -6.3))                                 # forward at the foot
    hub = hub.cut(box(4.0, gx1, sy - 1.9, sy - 0.7, -7.5, -6.3))                                 # into the bore
    ky, kz = P.KNUCKLE_PIN
    for s in (-1, 1):
        x0, x1 = sorted((s * 6.3, s * (hw + 1.0)))
        hub = hub.cut(box(x0, x1, ky - 3.7, sy + hd + 1, kz - 4.4, kz + 4.7))                    # knuckle notches
    hub = hub.cut(cyl_x(-hw - 2, hw + 2, ky, kz, 0.8 + P.TOL["pin"]))                            # knuckle pin
    add("hub_body", hub, "hub", "abs_teal", budget="hub_spring", rho="petg", printed=True, frame="book",
        label="Tri-grip hub (stick socket, leg hinge, blade knuckle seats)")

    # ---- stick: outer and inner tube, collar, glide bush
    ro, ri, wl = P.STICK_OD_OUTER / 2, P.STICK_OD_INNER / 2, P.STICK_WALL
    outer = tube_z(P.TUBE_OUT_Z[0], P.TUBE_OUT_Z[1], 0, sy, ro, ro - wl) \
        .cut(box(3.8, 5.4, sy - 1.9, sy - 0.7, P.TUBE_OUT_Z[0] - 0.1, -6.3))                     # notch 1.2 x 1.2 filed in the foot: the lead comes in here
    add("stick_outer_tube", outer, "stick_outer", "steel_brushed",
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
    head = head.cut(cyl_z(zt - 9.0, zt + 1.5, 0, sy, 0.85))                                      # cord hole up the spigot
    head = head.cut(box(-0.85, 0.85, sy - ri - 1.0, sy, zt, zt + 1.5))                           # cord slot out through the back of the collar
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
    rc = P.CORD_D / 2
    riser = [(2.3, sy, zt - 9.0), (0.0, sy, zt - 8.8), (0.0, sy, zt + CORD_EXIT_Z), (0.0, sy - ri - 0.3, zt + CORD_EXIT_Z)]
    ROUTES["hub_cord_riser"] = dict(points=[list(p) for p in riser], radius=rc,
                                    length=round(sum(math.dist(a, b) for a, b in zip(riser[:-1], riser[1:])), 1))
    add("hub_cord_riser", wire(riser, rc), "stick_inner", "wire_black", budget="stick_tubes_cord", mass=0.05, frame="book",
        label="Hub-sensor cord: up through the joint head and out of its back", explode=(0, 0, 14))
    gxm = 5.6
    lead = [(2.0, sy - 6.0, 3.0), (gxm, sy - 6.0, 3.0), (gxm, sy - 4.6, 3.0), (gxm, sy - 4.6, -6.9), (gxm, sy - 1.3, -6.9),
            (3.0, sy - 1.3, -6.9), (2.3, sy, -6.9), (2.3, sy, -3.0)]
    ROUTES["hub_sensor_lead"] = dict(points=[list(p) for p in lead], radius=rc,
                                     length=round(sum(math.dist(a, b) for a, b in zip(lead[:-1], lead[1:])), 1))
    add("hub_sensor_lead", wire(lead, rc), "hub", "wire_black", budget="stick_tubes_cord", mass=0.1, frame="book",
        label="Hub-sensor lead: from the sensor, down a groove in the hub, into the foot of the stick")
    ROUTES["hub_cord"] = dict(points=[], radius=0.45, bends=None, coil_od=2 * (2.3 + 0.45), bore=2 * (ri - wl), turns=20,
                              length=round(math.hypot(2 * math.pi * 2.3 * 20, zt - 9.0 + 3.0), 0),
                              coil_len_collapsed=zt - 9.0 + 3.0, coil_len_extended=zt - 9.0 + 3.0 + (P.STICK_EXTENDED - STICK0))
    add("hub_cord", cord(-3.0, zt - 9.0), "cord", "wire_black", budget="stick_tubes_cord", mass=1.2, frame="book",
        label="Coiled 2-wire cord to the hub sensor", explode=(0, -26, 0))
    add("hub_cord", cord(-3.0, zt - 9.0 + (P.STICK_EXTENDED - STICK0)), "cord", "wire_black", budget="stick_tubes_cord",
        mass=1.2, frame="book", variant="extended", label="Coiled cord, stretched", explode=(0, -26, 0))

    # ---- rear leg, TPU pad, pin, two torsion springs, hub sensor
    a0 = math.degrees(math.asin(((lz - (-(P.COVER_HARD + P.BLOCK_HARD))) - P.PAD[2] - 1.3) / P.LEG_CHORD))   # table pose
    barrel = cyl_x(-x_sp1, x_sp1, ly, lz, r_barrel)
    arm = box(-4.0, 4.0, ly - (P.LEG_CHORD - 6.0), ly - 1.0, lz - 1.3, lz + 1.3)
    arm = arm.cut(box(-1.3, 1.3, ly - 12.4, ly - 9.6, lz + 0.4, lz + 2.0))                       # dimple that meets the sensor plunger
    foot = box(-P.PAD[0] / 2, P.PAD[0] / 2, ly - P.LEG_CHORD - P.PAD[1] / 2, ly - P.LEG_CHORD + P.PAD[1] / 2, lz - 1.3, lz + 1.3) \
        .edges("|Z").fillet(3.0)
    foot = rot_x(foot, -a0, ly - P.LEG_CHORD, lz)
    leg = barrel.union(arm).union(foot).cut(cyl_x(-hw - 1, hw + 1, ly, lz, 1.0 + P.TOL["pin"]))
    pad = box(-P.PAD[0] / 2, P.PAD[0] / 2, ly - P.LEG_CHORD - P.PAD[1] / 2, ly - P.LEG_CHORD + P.PAD[1] / 2,
              lz - 1.3 - P.PAD[2], lz - 1.3).edges("|Z").fillet(3.0)
    pad = rot_x(pad, -a0, ly - P.LEG_CHORD, lz)
    leg, pad = rot_x(leg, a0, ly, lz), rot_x(pad, a0, ly, lz)
    add("rear_leg", leg, "leg", "abs_teal", budget="rear_leg_pad", rho="petg", printed=True, frame="book",
        label="Rear leg with T-foot (presses on the spine, or rests on the table)")
    add("rear_leg_pad", pad, "leg", "tpu_dark", budget="rear_leg_pad", rho="tpu", printed=True, frame="book",
        label="Soft TPU pad")
    add("leg_pin", cyl_x(-hw + 0.2, hw - 0.2, ly, lz, 1.0), "hub", "screw_steel", budget="hub_spring", rho="steel", frame="book",
        label=f"Leg hinge pin, 2.0 x {2 * hw - 0.4:g} mm")
    coils = P.PD("spring", "coils")
    rm = sp_id / 2 + sp_wire / 2
    for s, nm in ((1, "right"), (-1, "left")):
        helix = cq.Wire.makeHelix(sp_wire, coils * sp_wire, rm)
        spring = cq.Workplane("XZ").center(rm, 0).circle(sp_wire / 2).sweep(cq.Workplane("XY").add(helix), isFrenet=True)
        spring = spring.rotate((0, 0, 0), (0, 1, 0), 90).translate((x_sp0 + sp_wire / 2, ly, lz))
        if s < 0:
            spring = spring.mirror("YZ")
        add(f"torsion_spring_{nm}", spring, "hub", "spring_steel", budget="hub_spring", mass=0.9, frame="book", part="spring",
            label=f"Torsion spring, 1.0 mm wire, 6.5 coils, stock part ({nm}); legs trimmed to fit")
    dl_, dw_, dh_ = P.PD("det", "len"), P.PD("det", "wid"), P.PD("det", "h")
    yb0 = sy - ro_bore - 0.25                                                                    # switch board, against the stick
    sens = group([box(-2.0, 2.0, yb0 - 0.6, yb0, 1.3, 4.7),
                  box(-dl_ / 2, dl_ / 2, yb0 - 0.6 - dh_, yb0 - 0.6, 3.0 - dw_ / 2, 3.0 + dw_ / 2),
                  box(-P.PD("det", "plunger_w") / 2, P.PD("det", "plunger_w") / 2, yb0 - 0.6 - P.PD("det", "plunger_free"), yb0 - 0.6 - dh_, 2.7, 3.3)])
    add("hub_sensor_switch", sens, "hub", "ic_black", budget="hub_spring", mass=0.2, frame="book", part="det",
        label="Hub sensor: detector switch SPVE110200, pressed when the rear leg is folded away (GPIO 8)")

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
    kn = box(6.6, 15.4, ky - 3.5, ky + 4.5, kz - 4.2, kz + 2.6).edges("|X").fillet(1.0)        # blade at BLADE_X = 11, 8.8 wide
    kn = kn.cut(box(6.0, 16.0, P.BLADE_ROOT_Y - 0.2, ky + 5.0, zr - t / 2 - 0.03, zr + t / 2 + 0.03))
    kn = kn.cut(cyl_x(0, 20, ky, kz, 0.85)).cut(cyl_z(zr, kz + 4, P.BLADE_X, P.CLAMP_Y, 0.85))      # pin bore; screw hole dia 1.7 above the slit
    kn = kn.cut(cyl_z(kz - 6, zr, P.BLADE_X, P.CLAMP_Y, 0.65))                                      # dia 1.3 pilot below the slit
    add("blade_knuckle_right", kn, "blade_r", "abs_teal", budget="hub_spring", rho="petg", printed=True, frame="book",
        label="Blade knuckle (right): pivots to fold the blade up", explode=(26, 10, -8))
    add("blade_knuckle_left", mirror_x(kn), "blade_l", "abs_teal", budget="hub_spring", rho="petg", printed=True, frame="book",
        label="Blade knuckle (left)", explode=(-26, 10, -8))
    add("knuckle_pin", cyl_x(-15.4, 15.4, ky, kz, 0.8), "hub", "screw_steel", budget="hub_spring", rho="steel", frame="book",
        label="Knuckle pin, 1.6 x 31 mm", explode=(0, 14, -30))
    cs = cyl_z(kz - 4.2, kz + 2.6, P.BLADE_X, P.CLAMP_Y, 0.8).union(cyl_z(kz + 2.6, kz + 3.6, P.BLADE_X, P.CLAMP_Y, 1.5))
    add("blade_clamp_screw_right", cs, "blade_r", "screw_black", budget="hub_spring", mass=0.15, frame="book",
        label="Blade clamp screw, M1.6 x 6", explode=(26, 10, 4))
    add("blade_clamp_screw_left", mirror_x(cs), "blade_l", "screw_black", budget="hub_spring", mass=0.15, frame="book",
        label="Blade clamp screw, M1.6 x 6", explode=(-26, 10, 4))
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
           ("camera_screws", "shell_front_tub"), ("blade_clamp_screw", "blade_knuckle"), ("hub_cord_tail", "tilt_joint_head"), ("hub_cord_tail", "hub_cord_riser"),
           ("hub_cord_tail", "stick_inner_tube"),      # the free 10 mm of cord at the joint bends as the unit tilts; it is drawn rigid
           ("hub_cord_riser", "hub_cord"), ("hub_sensor_lead", "hub_cord"), ("hub_sensor_lead", "hub_sensor_switch"),
           ("hub_cord_tail", "pi_gpio_pads"),
           ("tilt_pivot_screw", "shell_front_tub"), ("light_ring_leds", "light_ring_pcb"),
           ("camera_flex", "pi_zero_2w_chips"), ("camera_flex", "camera_connector"), ("camera_lens_m12", "camera_holder_m12"),
           ("camera_lens_glass", "camera_lens_m12"), ("harness_", "pi_gpio_pads"), ("harness_", "pi_zero_2w_pcb"),
           ("battery_leads", "cell_"), ("battery_leads", "charger_board"), ("harness_", "amp_board"), ("harness_", "charger_board"),
           ("speaker_leads", "amp_board"), ("speaker_leads", "speaker"),
           ("shell_back_cover", "pi_zero_2w_pcb"), ("mic_mute_slider", "mic_mute_switch"), ("hub_sensor_switch", "rear_leg"),
           ("torsion_spring", "rear_leg"), ("usb_c_receptacle", "charger_board"), ("dac_jack", "dac_board")]


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
    hits, close, contacts, pairs = [], [], [], []
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if boxes_gap(bb[a], bb[b]) > 0.6:
                continue
            ok = allowed(a, b)
            try:
                common = shp[a].intersect(shp[b])
                v = sum(s.Volume() for s in common.Solids()) if common is not None else 0.0
            except Exception:
                v = 0.0
            if v > 0.02:
                if ok:
                    pairs.append(dict(a=a, b=b, kind="nested", overlap_mm3=round(v, 2)))     # screw in its boss, lead on its pad
                else:
                    hits.append(dict(a=a, b=b, overlap_mm3=round(v, 2)))
                continue
            if boxes_gap(bb[a], bb[b]) > 0.5:
                continue
            try:
                d = BRepExtrema_DistShapeShape(shp[a].wrapped, shp[b].wrapped)
                d.Perform()
                dist = d.Value()
            except Exception:
                dist = None
            if dist is None or dist >= 0.5:
                continue
            if dist > 0.005:
                pairs.append(dict(a=a, b=b, kind="gap", gap_mm=round(dist, 3)))
                if not ok:
                    close.append(dict(a=a, b=b, gap_mm=round(dist, 2)))
            else:
                pairs.append(dict(a=a, b=b, kind="contact", gap_mm=0.0))
                if not ok:
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
    return dict(collisions=hits, tight_gaps=close, n_contacts=len(contacts), contacts=[list(c) for c in contacts], routes=ROUTES,
                pairs=pairs, printed=[b["name"] for b in base if b["printed"]], labels={b["name"]: b["label"] for b in base},
                source_key=SOURCE_KEY,
                n_bodies=len(base), masses=rows, budget=budget,
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
    "tpu_dark": (0.13, 0.14, 0.15), "foam": (0.20, 0.20, 0.21),
}


# Exploded-view offsets (mm), in the sb_params frame (+x = reader's right). First match wins.
EXPLODE = [
    # the tub goes well forward and down, so the parts that sit on its front wall can be seen behind and above it
    ("shell_front_tub", (0, 100, -40)), ("status_dot_pipes", (0, 116, -40)), ("lens_bezel", (0, 124, -64)), ("light_ring_diffuser", (0, 113, -53)),
    ("button_ask", (0, 100, -10)), ("button_play_pause", (0, 100, -18)), ("button_back", (0, 100, -18)), ("button_forward", (0, 100, -18)),
    ("button_vol", (-24, 100, -40)), ("mic_mute_slider", (-24, 100, -40)), ("mic_mute_flag", (-24, 100, -40)),
    ("speaker_leads", (0, 30, 18)), ("speaker", (0, 38, 0)), ("status_led", (0, 38, 8)), ("haptic_motor", (0, 38, 0)),
    ("amp_board", (-8, 26, 0)), ("dac_", (-16, 14, -8)), ("charger_board", (14, 22, 0)), ("usb_c_receptacle", (14, 22, 0)),
    ("fuel_gauge", (20, 10, -10)), ("mic_right", (8, 14, 18)), ("mic_left", (-8, 14, 18)), ("top_bar", (0, 30, 16)),
    ("ask_button_board", (0, 6, 16)), ("volume_board", (-16, 30, 0)), ("mic_mute_switch", (-16, 30, 0)),
    ("light_ring_pcb", (0, 22, -22)), ("light_ring_leds", (0, 22, -22)), ("camera_lens", (0, 12, -12)),
    ("camera_holder_m12", (0, 5, -5)), ("camera_screws", (0, -7, 7)), ("camera_flex", (0, -20, 6)), ("camera_", (0, 0, 0)),
    ("cell_foam_right", (30, -6, 0)), ("cell_foam_left", (-30, -6, 0)), ("cell_right", (30, 0, 0)), ("cell_pcm_right", (30, 0, 0)),
    ("cell_left", (-30, 0, 0)), ("cell_pcm_left", (-30, 0, 0)), ("microsd_card", (10, -30, 0)), ("pi_", (0, -30, 0)),
    ("harness_", (0, -12, 18)), ("battery_leads", (0, -8, 22)), ("hub_cord_tail", (0, 0, -16)), ("thermal_pad", (0, -44, 0)),
    ("heat_spreader", (0, -54, 0)), ("shell_back_cover", (0, -70, 0)), ("cover_screw", (0, -90, 0)),
    # stick, joint, hub, legs (book frame)
    ("tilt_joint_head", (0, 0, 150)), ("tilt_pivot_screw", (-24, 0, 150)), ("tilt_thumb_nut", (24, 0, 150)),
    ("stick_inner_tube", (0, 0, 128)), ("stick_glide_bush", (0, 0, 116)), ("stick_collar", (0, 0, 14)), ("stick_outer_tube", (0, 0, 0)),
    ("hub_cord_riser", (0, 0, 128)), ("hub_sensor_lead", (0, -16, -14)), ("hub_cord", (-46, 0, 24)), ("hub_body", (0, 0, -34)), ("leg_pin", (-38, 0, -34)), ("torsion_spring_right", (30, -14, -34)),
    ("torsion_spring_left", (-30, -14, -34)), ("hub_sensor_switch", (0, -16, -14)), ("rear_leg_pad", (0, -52, -58)),
    ("rear_leg", (0, -44, -44)), ("blade_knuckle_right", (24, 16, -34)), ("blade_knuckle_left", (-24, 16, -34)),
    ("knuckle_pin", (0, 34, -20)), ("blade_clamp_screw_right", (24, 16, -14)), ("blade_clamp_screw_left", (-24, 16, -14)),
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
                        budget=b["budget"], printed=b["printed"], explode=explode_of(b["name"]), frame=b["frame"],
                        part=SOURCE_KEY.get(b["name"])))
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
            .cut(cq.Workplane("XY").circle(0.9).extrude(1).translate((0, -dev + (P.CLAMP_Y - P.BLADE_ROOT_Y), 0)))
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
