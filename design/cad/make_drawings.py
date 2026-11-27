"""Dimensioned drawings (PDF) for every part and for the assembly, made from the same model as the STEP files.

Run after build_model.py, from design/cad:
    ..\\.venv\\Scripts\\python.exe make_drawings.py            # everything
    ..\\.venv\\Scripts\\python.exe make_drawings.py hub_body   # parts whose name starts with this

Writes design/drawings/SenseBook_drawings.pdf (all sheets) and design/drawings/parts/<part>.pdf.

Each part sheet has three views in third-angle projection (hidden-line removed, straight from the solid),
the overall sizes, the key dimensions, how to make the part (material, print placement, finish), a table of
every round hole and shaft found in the solid, tolerances and notes. Long lists run on to a second sheet.
Numbers come from the model, from sb_params.py or from the layout worked out in build_model.py.
Bought parts get a reference sheet with their published sizes and the source; estimates are marked [EST].

Status: prototype drawings. Nothing has been made from them yet.
"""
import datetime
import math
import os
import sys

import cadquery as cq
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface  # noqa: E402
from OCP.BRepLib import BRepLib  # noqa: E402
from OCP.GeomAbs import GeomAbs_Cylinder  # noqa: E402
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt  # noqa: E402
from OCP.HLRAlgo import HLRAlgo_Projector  # noqa: E402
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape  # noqa: E402

import build_model as B  # noqa: E402
import check_model as C  # noqa: E402
import sb_params as P  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(os.path.join(HERE, "..", "drawings"))
INK, GREY, ACC = "#1D2A2E", "#8A979B", "#B0600F"
SHEET_W, SHEET_H = 297.0, 210.0                      # A4 landscape, mm
DATE = datetime.date.today().strftime("%d %b %Y")

# view name -> (direction toward the viewer, screen-right direction), CAD frame (+x = reader's left)
VIEWS = {"front": ((0, 1, 0), (-1, 0, 0)), "top": ((0, 0, 1), (-1, 0, 0)), "right": ((-1, 0, 0), (0, -1, 0)),
         "iso": ((-0.55, 0.62, 0.56), (-0.75, -0.66, 0.0))}


# ------------------------------------------------------------------ projection
def project(shape, view, hidden=True):
    """Hidden-line projection. Returns (visible polylines, hidden polylines) in view coordinates (mm)."""
    n, xdir = VIEWS[view]
    hlr = HLRBRep_Algo()
    hlr.Add(shape.wrapped)
    hlr.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*n), gp_Dir(*xdir))))
    hlr.Update()
    hlr.Hide()
    hs = HLRBRep_HLRToShape(hlr)

    def lines(compounds):
        out = []
        for c in compounds:
            if c is None or c.IsNull():
                continue
            BRepLib.BuildCurves3d_s(c, 1e-6)
            for e in cq.Shape(c).Edges():
                try:
                    cu = BRepAdaptor_Curve(e.wrapped)
                    u0, u1 = cu.FirstParameter(), cu.LastParameter()
                    k = 2 if e.geomType() == "LINE" else 24
                    pts = [cu.Value(u0 + (u1 - u0) * i / (k - 1)) for i in range(k)]
                except Exception:
                    continue
                out.append(np.array([(p.X(), p.Y()) for p in pts]))
        return out

    vis = lines([hs.VCompound(), hs.Rg1LineVCompound(), hs.OutLineVCompound()])
    hid = lines([hs.HCompound(), hs.OutLineHCompound()]) if hidden else []
    return vis, hid


def extent(polys):
    if not polys:
        return 0.0, 0.0, 0.0, 0.0
    a = np.vstack(polys)
    return float(a[:, 0].min()), float(a[:, 0].max()), float(a[:, 1].min()), float(a[:, 1].max())


# ------------------------------------------------------------------ round features
def round_features(shape):
    """Every round hole and shaft in the solid: diameter, axis, a point on the axis. Fillets are left out.
    Hole or shaft is decided by testing on which side of the surface the material is."""
    solids = shape.Solids()

    def in_material(pt):
        v = cq.Vector(float(pt[0]), float(pt[1]), float(pt[2]))
        return any(so.isInside(v, 1e-7) for so in solids)

    rows = {}
    for f in shape.Faces():
        s = BRepAdaptor_Surface(f.wrapped)
        if s.GetType() != GeomAbs_Cylinder:
            continue
        cyl = s.Cylinder()
        d = 2 * cyl.Radius()
        if d > 40 or d < 0.5:
            continue
        u0, u1, v0, v1 = f._uvBounds()
        if (u1 - u0) < 2.6:                                   # under about 150 degrees of arc: an edge round, not a hole
            continue
        ax = cyl.Axis().Direction()
        loc = cyl.Location()
        a = np.array([ax.X(), ax.Y(), ax.Z()])
        p = np.array([loc.X(), loc.Y(), loc.Z()])
        q = s.Value((u0 + u1) / 2, (v0 + v1) / 2)
        q = np.array([q.X(), q.Y(), q.Z()])
        radial = (q - p) - a * float(np.dot(q - p, a))
        radial = radial / max(np.linalg.norm(radial), 1e-9)
        inside, outside = in_material(q - radial * 0.06), in_material(q + radial * 0.06)
        if inside == outside:
            continue
        p = p - a * float(np.dot(p, a))                       # the point of the axis nearest the origin
        k = int(np.argmax(np.abs(a)))
        along = "XYZ"[k] if abs(a[k]) > 0.999 else "skew"
        key = (round(d, 2), outside, along)
        rows.setdefault(key, set()).add(tuple(round(float(v), 1) + 0.0 for v in p))
    out = []
    for (d, hole, along), pts in sorted(rows.items(), key=lambda kv: (not kv[0][1], kv[0][0])):
        out.append(dict(d=d, kind="hole" if hole else "shaft", axis=along, n=len(pts), at=sorted(pts)))
    return out


# ------------------------------------------------------------------ part data
MATERIAL = [  # name prefix -> (material and process, general tolerance, finish)
    ("shell_", ("PETG, FDM printed, 3 perimeters, slate-teal", "FDM", "as printed; visible faces sanded 400 grit")),
    ("button_ask", ("PETG, FDM printed, 100% infill, marigold", "FDM", "as printed")),
    ("button_", ("PETG, FDM printed, 100% infill, lighter teal", "FDM", "as printed")),
    ("mic_mute_slider", ("PETG, FDM printed, lighter teal", "FDM", "as printed; flag area painted orange")),
    ("mic_mute_flag", ("Orange paint or sticker on the slider cap", "REF", "-")),
    ("light_ring_diffuser", ("PETG natural (clear), FDM, 100% infill", "FDM", "as printed")),
    ("status_dot_pipes", (f"PETG natural (clear), or {P.DOT_D:g} mm clear rod", "FDM", "ends polished")),
    ("tilt_joint_head", ("PETG, FDM printed, 100% infill", "FDM", f"pivot hole drilled {P.PIVOT_PIN_D + 0.1:g}")),
    ("stick_collar", ("PETG, FDM printed", "FDM", "bore reamed to fit the tubes")),
    ("hub_body", ("PETG, FDM printed, 100% infill", "FDM", "bores drilled to size")),
    ("blade_knuckle", ("PETG, FDM printed, 100% infill", "FDM", "slit sawn to 0.45")),
    ("rear_leg_pad", ("TPU 95A, FDM printed", "FDM", "as printed")),
    ("rear_leg", ("PETG, FDM printed, 100% infill", "FDM", "barrel drilled 2.1")),
    ("blade_coat", ("Silicone sleeve or dip coating, 0.25 mm", "REF", "smooth, no seam on the page side")),
    ("blade_clamp_screw", ("M1.6 x 6 pan head screw, steel", "BOUGHT", "as supplied")),
    ("blade_", (f"Stainless spring shim, 300 series full hard, {P.BLADE_T:g} mm", "SHEET", "all edges rounded and deburred")),
    ("stick_outer_tube", (f"Stainless steel 304 tube {P.STICK_OD_OUTER:g} x {P.STICK_WALL:g}", "CUT", "ends square, deburred inside and out")),
    ("stick_inner_tube", (f"Stainless steel 304 tube {P.STICK_OD_INNER:g} x {P.STICK_WALL:g}", "CUT", "ends square, deburred inside and out")),
    ("stick_glide_bush", ("PTFE or acetal sleeve, or two turns of PTFE tape", "TURN", "slides freely in the 9.0 bore")),
    ("leg_pin", ("Stainless or hardened steel pin, 2.0 mm", "CUT", "ends chamfered")),
    ("knuckle_pin", ("Stainless or hardened steel pin, 1.6 mm", "CUT", "ends chamfered")),
    ("heat_spreader", ("Aluminium sheet 1.0 mm (1050 or 5052)", "SHEET", "deburred")),
    ("thermal_pad", ("Silicone thermal pad, soft, cut to size", "SHEET", "-")),
    ("cell_foam", ("Closed-cell foam tape, 0.7 mm", "SHEET", "-")),
    ("lens_bezel", ("Aluminium, turned; or PETG printed", "TURN", "pale blue anodise or paint")),
    ("tilt_thumb_nut", ("M3 knurled thumb nut, brass", "BOUGHT", "as supplied")),
    ("tilt_pivot_screw", ("M3 x 18 button head screw, steel (ISO 7380)", "BOUGHT", "as supplied")),
]
TOL_NOTE = {
    "FDM": f"General tolerance, printed: +/-{P.TOL['fdm']:.1f} mm. Holes print small: drill or ream to the size in the hole table.",
    "SHEET": f"General tolerance, cut sheet: +/-{P.TOL['sheet']:.1f} mm. Thickness as supplied.",
    "CUT": f"General tolerance, cut length: +/-{P.TOL['cut']:.1f} mm. Diameters as supplied.",
    "TURN": f"General tolerance, turned: +/-{P.TOL['turn']:.2f} mm.",
    "REF": "Reference only.",
    "BOUGHT": "Bought part: drawn at the sizes its maker publishes (listed here). Check a sample before building.",
}
WIRES = ("harness_", "battery_leads", "speaker_leads", "hub_cord", "hub_sensor_lead", "camera_flex")


def material_of(body):
    for pre, val in MATERIAL:
        if body["name"].startswith(pre):
            return val
    return (body["label"], "BOUGHT", "as supplied")


def fx(x):
    """x in the CAD files is mirrored against sb_params.py."""
    return -x + 0.0


def key_dims(name):
    """Key dimensions and fits for a made part, from sb_params.py and the layout worked out in build_model.py.
    Positions are (x, y, z) in the part's own file. A line ending in [EST ...] depends on a size nobody publishes."""
    T, w, D, L = P.TOL, P.WALL, P.PD, B.LAY
    cl = T["slide"]
    sy = P.STICK_Y
    sp_or = D("spring", "id") / 2 + D("spring", "wire")
    r_barrel = D("spring", "id") / 2 - 0.15
    x_sp1 = 4.9 + D("spring", "body_len")
    hi = D("pi", "hole_inset")
    K = {
        "shell_front_tub": [
            f"Outside {P.UNIT_W:g} wide x {P.UNIT_H:g} high; depth to the seam {-P.SEAM_Y:g} (whole unit {P.UNIT_D:g} deep)",
            f"Wall {w:g}; front-view corners R{P.R_FRONT:g}; front and back edges R{P.R_EDGE:g}",
            f"Lens facet at {P.FACET_ANGLE:g} deg, from z {P.FACET_TOP_Z:g} on the front face to y {P.FACET_BOT_Y:g} on the bottom",
            f"Lens opening dia {P.RING_OD + 0.2:g} square to the facet, centre y {P.LENS_Y:g}, z {P.LENS_Z:g}; "
            f"inside it a dia {P.RING_OD + 0.6:g} relief from 1.4 to 5.0 behind the facet for the LED ring",
            f"Tilt lugs: 2 x {P.LUG_T:g} thick, {P.LUG_GAP:g} apart; pivot dia {P.PIVOT_PIN_D + 0.2:g} at y {P.PIVOT_Y:g}, z {P.PIVOT_Z:g}",
            f"Top: Ask opening dia {P.ASK_D + 2 * cl:g} at ({fx(P.ASK_XY[0]):g}, {P.ASK_XY[1]:g}); three capsule openings "
            f"{P.BAR_SIZE[0] + 2 * cl:g} x {P.BAR_SIZE[1] + 2 * cl:g} at x {fx(-P.NAV_X):g}, 0, {fx(P.NAV_X):g}, y {P.BAR_Y:g}",
            f"Top: 2 microphone ports dia 1.2 at x +/-{L['mic_port'][0]:.2f}, y {L['mic_port'][1]:.2f}",
            f"Side at x = +{P.UNIT_W / 2:g}: two capsule openings {P.VOL_SIZE[0] + 2 * cl:g} x {P.VOL_SIZE[1] + 2 * cl:g} at y {P.VOL_Y:g}, "
            f"z {P.VOL_Z[0]:g} and {P.VOL_Z[1]:g}; mute slot 5.5 x 2.6 at y {L['mute_y']:g}, z {P.MUTE_Z:g}",
            f"Side at x = +{P.UNIT_W / 2:g}: headphone hole dia {D('dac', 'jack_barrel_d') + 0.4:g} at y {L['jack'][0]:.2f}, z {L['jack'][1]:.2f} "
            "[EST: jack size not published]",
            f"Side at x = -{P.UNIT_W / 2:g}: USB-C opening {L['usb_open'][1]:.2f} high x {L['usb_open'][0]:.2f}, centre y {L['usb'][0]:.2f}, z {L['usb'][1]:.2f}",
            f"Front: 4 dot holes dia {P.DOT_D + 0.1:g} at x " + ", ".join(f"{fx(x):g}" for x in P.DOT_X) + f", z {P.DOT_Z:g}; "
            f"speaker grille 5 x 8 holes dia 1.0 on 2.4 x 2.2 centres about x {fx(P.SPK_X):g}, z {P.SPK_Z0 + D('spk', 'len') / 2:g}",
            f"Bottom: cord hole dia {P.CORD_D + 1.1:g} at ({fx(P.CORD_ENTRY[0]):g}, {P.CORD_ENTRY[1]:g}), between the lugs",
            "Cover screw bosses: 4 x dia 4.0 with dia 1.7 pilot for ST2.2 tapping screws, at (x, z) "
            + ", ".join(f"({fx(bx):g}, {bz:.1f})" for bx, bz, _ in L["boss_pts"]),
            f"Camera posts: 2 x dia 3.2 with dia 1.7 pilot, {2 * L['cam_post'][0]:g} apart, {L['cam_post'][1]:.2f} up the facet from the lens axis; "
            f"the top faces are {L['a_front']:.2f} behind the facet; two cradle ribs hold the lower edge of the camera board",
            f"Button, slider and cover fits are sliding fits: {cl:g} clear per side",
        ],
        "shell_back_cover": [
            f"Outside {P.UNIT_W:g} x {P.UNIT_H:g}; {P.UNIT_D + P.SEAM_Y:g} from the seam to the back face",
            f"Wall {w:g}; locating tongue {P.TONGUE_T:g} thick, standing {P.TONGUE_H:g} past the seam, {P.TONGUE_GAP:g} clear of the tub wall",
            f"Pi posts: 4 x dia 4.6 on {D('pi', 'len') - 2 * hi:g} x {D('pi', 'wid') - 2 * hi:g} centres, lowest row at z {P.PI_Z0 + hi:g}; "
            f"post faces {L['pi_yt'] - L['back_in']:.2f} from the inside face; each ends in a dia {L['pi_pin_d']:.2f} pin, "
            f"{D('pi', 'pcb_t') + 0.4:g} long, for the dia {D('pi', 'hole_d'):g} holes in the Pi [EST: Pi board thickness]",
            f"Screw holes: 4 x dia {D('st22', 'thread_d') + 0.2:g} with dia {D('st22', 'head_d') + 0.4:g} counterbore, 1.0 deep, "
            "on the same centres as the tub bosses",
            f"Heat spreader ({P.SPREADER[0]:g} x {P.SPREADER[1]:g} x {P.SPREADER[2]:g}) is bonded flat on the inside face, behind the Pi's main chip",
        ],
        "hub_body": [
            f"Body {P.HUB_W:g} wide x {P.HUB_D:g} deep x {P.HUB_H:g} high, with the hinge block behind it",
            f"Stick bore dia {P.STICK_OD_OUTER + 0.16:g}, {P.HUB_TOP_Z - P.TUBE_OUT_Z[0]:g} deep from the top (drill 10.1, glue the tube in)",
            f"Leg hinge: dia 2.1 hole for a 2.0 pin, {sy - P.LEG_PIVOT[0]:g} behind the stick axis and {P.HUB_TOP_Z - P.LEG_PIVOT[1]:g} below the hub top",
            f"Leg slot 9.2 wide; barrel bore dia {2 * (r_barrel + 0.35):g}; two spring pockets dia {2 * (sp_or + 0.25):g} x "
            f"{D('spring', 'body_len') + 0.4:g} long, one each side of the slot",
            f"Knuckle pin: dia 1.7 hole for a 1.6 pin, {P.KNUCKLE_PIN[0] - sy:g} in front of the stick axis, {P.HUB_TOP_Z - P.KNUCKLE_PIN[1]:g} below the hub top; "
            f"blade centre lines {2 * P.BLADE_X:g} apart",
            "Sensor pocket 4.0 wide x 3.4 high, open to the bore, behind the stick, its floor 8.7 below the hub top",
            "Lead groove 1.2 x 1.2: from the sensor pocket sideways, down beside the bore, forward at the foot and into the bore",
        ],
        "tilt_joint_head": [
            f"Spigot dia {P.STICK_OD_INNER - 2 * P.STICK_WALL - 0.1:g} x 8 long (glue into the inner tube); collar dia {P.STICK_OD_INNER:g} x 1.5 "
            "[EST: inner tube size, supplier not confirmed]",
            f"Tongue {P.LUG_GAP - 0.6:g} thick (0.3 clear of each lug) x 7.0; pivot dia {P.PIVOT_PIN_D + 0.1:g}, {P.JOINT_ABOVE_STICK:g} above the top of the tube",
            "Cord hole dia 1.7 up the middle of the spigot; cord slot 1.7 wide x 1.5 high out through the back of the collar",
        ],
        "stick_collar": [f"Outside dia {P.COLLAR[0]:g}, length {P.COLLAR[2] - P.COLLAR[1]:g}",
                         f"Bores: dia {P.STICK_OD_OUTER + 0.12:g} (pushed onto the outer tube) and dia {P.STICK_OD_INNER + 0.2:g} (the inner tube slides)"],
        "rear_leg": [f"Pivot to pad centre {P.LEG_CHORD:g}; arm 8.0 wide x 2.6 thick",
                     f"Barrel dia {2 * r_barrel:g} x {2 * x_sp1:g} long, bore dia 2.1 (the two springs ride on the barrel)",
                     f"T-foot {P.PAD[0]:g} x {P.PAD[1]:g} x 2.6, corners R3; small pocket 2.6 x 2.8 on the arm meets the sensor plunger"],
        "rear_leg_pad": [f"{P.PAD[0]:g} x {P.PAD[1]:g} x {P.PAD[2]:g}, corners R3"],
        "stick_outer_tube": [f"Dia {P.STICK_OD_OUTER:g} x {P.STICK_WALL:g} wall, length {P.TUBE_OUT_Z[1] - P.TUBE_OUT_Z[0]:g}",
                             "Notch 1.2 wide x 1.2 high filed in the foot, for the sensor lead"],
        "stick_inner_tube": [f"Dia {P.STICK_OD_INNER:g} x {P.STICK_WALL:g} wall, length {P.TUBE_IN_LEN:g} [EST: supplier for this tube size not confirmed]"],
        "stick_glide_bush": [f"Outside dia {2 * (P.STICK_OD_OUTER / 2 - P.STICK_WALL - 0.04):g}, inside dia {P.STICK_OD_INNER:g}, length 6"],
        "leg_pin": [f"Dia 2.0 x {P.HUB_W - 0.4:g}"], "knuckle_pin": ["Dia 1.6 x 30.8"],
        "heat_spreader": [f"{P.SPREADER[0]:g} x {P.SPREADER[1]:g} x {P.SPREADER[2]:g}"],
        "thermal_pad": [f"{D('pi', 'sip'):g} x {D('pi', 'sip'):g} x {L['pi_yt'] - D('pi', 'sip_h') - L['back_in'] - P.SPREADER[2]:.2f} thick "
                        "[EST: the Pi chip height is not published; choose the pad after measuring]"],
        "cell_foam_right": ["10 x 27.5 x 0.7"], "cell_foam_left": ["10 x 27.5 x 0.7"],
        "lens_bezel": [f"Outside dia {P.RING_ID:g}, inside dia {P.LENS_OPENING_D:g}, {w:g} thick; 0.8 x 45 deg chamfer on the bore, outer face"],
        "light_ring_diffuser": [f"Outside dia {P.RING_OD:g}, inside dia {P.RING_ID:g}, {w + 0.6:g} long"],
        "button_ask": [f"Cap dia {P.ASK_D:g} (opening dia {P.ASK_D + 2 * cl:g}); retaining lip dia {P.ASK_D + 2:g} x 1.0",
                       "Top dished to R16, centre dot dia 2.0"],
        "button_play_pause": [f"Capsule cap {P.BAR_SIZE[0]:g} x {P.BAR_SIZE[1]:g}; retaining lip 0.8 all round x 1.0; raised dot dia 2.0 x 0.5"],
        "button_back": [f"Capsule cap {P.BAR_SIZE[0]:g} x {P.BAR_SIZE[1]:g}; retaining lip 0.8 all round x 1.0; raised arrow 0.6 high"],
        "button_forward": [f"Capsule cap {P.BAR_SIZE[0]:g} x {P.BAR_SIZE[1]:g}; retaining lip 0.8 all round x 1.0; raised arrow 0.6 high"],
        "button_vol_up": [f"Capsule cap {P.VOL_SIZE[0]:g} x {P.VOL_SIZE[1]:g}; retaining lip 0.6 all round x 1.0; raised dot dia 1.6"],
        "button_vol_down": [f"Capsule cap {P.VOL_SIZE[0]:g} x {P.VOL_SIZE[1]:g}; retaining lip 0.6 all round x 1.0"],
        "mic_mute_slider": [f"Cap 3.6 long x 2.2 high; pocket 1.5 x 1.2 grips the switch lever [EST: lever width {D('slide', 'lever_w'):g} not published]",
                            f"Travel {D('slide', 'travel'):g}"],
        "status_dot_pipes": [f"4 pins dia {P.DOT_D:g}, in the dot holes, flush with the front face"],
        "blade_knuckle_right": ["Body 8.8 x 8.0 x 6.8; blade slit 0.46; pin bore dia 1.7",
                                f"Clamp screw (M1.6) {P.CLAMP_Y - P.KNUCKLE_PIN[0]:g} in front of the pin: dia 1.7 above the slit, dia 1.3 pilot below it"],
        "blade_knuckle_left": ["Mirror of the right knuckle"],
        "blade_right": [f"Strip {P.BLADE_W:g} wide x {P.BLADE_T:g}; two bends, radius 2.0 on the centre line; flat run {P.BLADE_REACH:g} from the top edge of the book; "
                        f"splay {P.BLADE_SPLAY:g} deg", "Cut from the DXF flat pattern; clamp hole dia 1.8; raised dot dia 2.6 marks the top side"],
        "blade_left": ["Mirror of the right blade"],
    }
    return K.get(name, [])


def bought_dims(key):
    """Published sizes of a bought part, with the EST ones marked."""
    if not key or key not in P.PARTS:
        return [], ""
    p = P.PARTS[key]
    lines, ids = [], []
    unit = {"mass_g": "g", "capacity_mah": "mAh", "max_discharge_a": "A", "out_a": "A", "coils": "turns", "max_torque_nmm": "N mm",
            "max_angle_deg": "deg", "yield_mpa": "MPa", "tensile_mpa": "MPa", "hfov_deg": "deg", "vfov_deg": "deg", "dfov_deg": "deg",
            "force_n": "N", "lead_awg": "AWG"}
    good = [f"{d} {v:g}{(' ' + unit[d]) if d in unit else ''}" for d, (v, sid, basis) in p["dims"].items() if basis != "EST"]
    est = [f"{d} {v:g}{(' ' + unit[d]) if d in unit else ''}" for d, (v, sid, basis) in p["dims"].items() if basis == "EST"]
    for d, (v, sid, basis) in p["dims"].items():
        if sid != "EST" and sid not in ids:
            ids.append(sid)
    lines.append(p["name"])
    lines.append("Published (mm unless marked): " + "; ".join(good))
    if est:
        lines.append("[EST: not published, to be measured] " + "; ".join(est))
    src = "; ".join(f"{P.SRC[i][0]} ({P.SRC[i][1]})" for i in ids)
    return lines, src


# ------------------------------------------------------------------ drawing primitives
def new_sheet():
    fig = plt.figure(figsize=(SHEET_W / 25.4, SHEET_H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, SHEET_W)
    ax.set_ylim(0, SHEET_H)
    ax.axis("off")
    ax.add_patch(Rectangle((8, 8), SHEET_W - 16, SHEET_H - 16, fill=False, ec=INK, lw=0.8))
    return fig, ax


def title_block(ax, title, number, sheet, material="", finish="", qty="", mass="", scale="", tol="", status="PROTOTYPE - NOT YET MADE"):
    x0, y0, w, h = SHEET_W - 8 - 128, 8, 128, 34
    ax.add_patch(Rectangle((x0, y0), w, h, fill=False, ec=INK, lw=0.8))
    for yy in (y0 + 8, y0 + 16, y0 + 24):
        ax.plot([x0, x0 + w], [yy, yy], color=INK, lw=0.4)
    ax.plot([x0 + 78, x0 + 78], [y0, y0 + 24], color=INK, lw=0.4)
    f = dict(fontsize=5.6, color=INK, va="center")
    ax.text(x0 + 2, y0 + 29, title, fontsize=9, fontweight="bold", color=INK, va="center")
    ax.text(x0 + 2, y0 + 20, f"Material: {material}", **f)
    ax.text(x0 + 2, y0 + 12, f"Finish: {finish}", **f)
    ax.text(x0 + 2, y0 + 4, "SenseBook v4 tri-grip  |  CERN-OHL-W-2.0  |  third-angle projection  |  mm", **f)
    ax.text(x0 + 80, y0 + 20, f"Drawing {number}    Sheet {sheet}", **f)
    ax.text(x0 + 80, y0 + 12, f"Qty {qty}    Mass {mass}    Scale {scale}", **f)
    ax.text(x0 + 80, y0 + 4, f"{DATE}    {status}", fontsize=5.0, color=ACC, va="center")
    if tol:
        ax.text(10, 11, tol, fontsize=5.4, color=INK, va="center")


def draw_view(ax, polys, hidden, ox, oy, s, x0, y0):
    for p in hidden:
        ax.plot(ox + (p[:, 0] - x0) * s, oy + (p[:, 1] - y0) * s, color=GREY, lw=0.25, ls=(0, (3, 2)))
    for p in polys:
        ax.plot(ox + (p[:, 0] - x0) * s, oy + (p[:, 1] - y0) * s, color=INK, lw=0.45, solid_capstyle="round")


def dim_h(ax, xa, xb, y, text, below=True):
    yy = y - 6 if below else y + 6
    ax.plot([xa, xa], [y, yy - (1 if below else -1)], color=GREY, lw=0.25)
    ax.plot([xb, xb], [y, yy - (1 if below else -1)], color=GREY, lw=0.25)
    ax.annotate("", xy=(xa, yy), xytext=(xb, yy), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.4, shrinkA=0, shrinkB=0, mutation_scale=5))
    ax.text((xa + xb) / 2, yy + (-2.4 if below else 1.0), text, fontsize=6, ha="center", va="center" if below else "bottom", color=INK)


def dim_v(ax, ya, yb, x, text, left=True):
    xx = x - 6 if left else x + 6
    ax.plot([x, xx - (1 if left else -1)], [ya, ya], color=GREY, lw=0.25)
    ax.plot([x, xx - (1 if left else -1)], [yb, yb], color=GREY, lw=0.25)
    ax.annotate("", xy=(xx, ya), xytext=(xx, yb), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.4, shrinkA=0, shrinkB=0, mutation_scale=5))
    ax.text(xx + (-1.2 if left else 1.2), (ya + yb) / 2, text, fontsize=6, ha="right" if left else "left", va="center", color=INK, rotation=90)


SCALES = [(10, "10:1"), (5, "5:1"), (4, "4:1"), (2, "2:1"), (1, "1:1"), (0.5, "1:2"), (0.25, "1:4")]


def three_views(ax, shape, region, hidden=True):
    """Front, top, right in third-angle layout, plus a small pictorial view. Returns the scale label."""
    rx, ry, rw, rh = region
    pv = {v: project(shape, v, hidden and v != "iso") for v in ("front", "top", "right", "iso")}
    ex = {v: extent(pv[v][0] + pv[v][1]) for v in pv}
    W = ex["front"][1] - ex["front"][0]
    H = ex["front"][3] - ex["front"][2]
    D = ex["top"][3] - ex["top"][2]
    gap = 13.0
    iso_w = ex["iso"][1] - ex["iso"][0]
    s, label = SCALES[-1]
    for sc, lab in SCALES:
        if (W + D) * sc + gap + 20 <= rw and (H + D) * sc + gap + 18 <= rh:
            s, label = sc, lab
            break
    fx, fy = rx + 14, ry + 12                                   # front view origin (lower-left)
    draw_view(ax, *pv["front"], fx, fy, s, ex["front"][0], ex["front"][2])
    tx, ty = fx, fy + H * s + gap
    draw_view(ax, *pv["top"], tx, ty, s, ex["top"][0], ex["top"][2])
    sx, sy = fx + W * s + gap, fy
    draw_view(ax, *pv["right"], sx, sy, s, ex["right"][0], ex["right"][2])
    dim_h(ax, fx, fx + W * s, fy, f"{W:.1f}")
    dim_v(ax, fy, fy + H * s, fx, f"{H:.1f}")
    dim_h(ax, sx, sx + D * s, sy, f"{D:.1f}")
    for lab_, (lx, ly) in (("FRONT", (fx, fy + H * s + 2)), ("TOP", (tx, ty + D * s + 2)), ("RIGHT", (sx, sy + H * s + 2))):
        ax.text(lx, ly, lab_, fontsize=4.6, color=GREY)
    iso_h = ex["iso"][3] - ex["iso"][2]                         # pictorial view goes in the free corner above the right view
    free_w, free_h = rx + rw - sx - 4, ry + rh - ty - 8
    if free_w > 12 and free_h > 12 and iso_w > 0 and iso_h > 0:
        si = min(s, free_w / iso_w, free_h / iso_h)
        draw_view(ax, pv["iso"][0], [], sx, ty, si, ex["iso"][0], ex["iso"][2])
        ax.text(sx, ty - 3, "pictorial, not to scale", fontsize=4.6, color=GREY)
    return label, (W, H, D)


def hole_lines(feats, limit=14):
    out = []
    for f in feats[:limit]:
        at = "; ".join("(" + ", ".join(f"{v:g}" for v in p) + ")" for p in f["at"][:4]) + (" ..." if len(f["at"]) > 4 else "")
        out.append(f"{f['n']} x dia {f['d']:g} {f['kind']}, axis {f['axis']}, at {at}")
    if len(feats) > limit:
        out.append(f"... and {len(feats) - limit} more sizes (see the STEP file)")
    return out or ["none"]


# ------------------------------------------------------------------ sheets
def flow(ax, blocks, x, y, y_min, width, size=5.3):
    """Write titled blocks of lines down a column. Returns the blocks (or parts of blocks) that did not fit."""
    import textwrap
    left, full = [], False
    pitch = size * 0.48
    for title, lines in blocks:
        if full or y - 10 < y_min:
            full = True
            left.append((title, lines))
            continue
        ax.text(x, y, title, fontsize=6.3, fontweight="bold", color=INK, va="top")
        y -= 4.4
        for i, ln in enumerate(lines):
            parts = textwrap.wrap(ln, int(width / (size * 0.2))) or [""]
            if y - len(parts) * pitch < y_min:
                left.append((title + " (continued)", lines[i:]))
                full = True
                break
            col = ACC if "[EST" in ln else INK
            for part in parts:
                ax.text(x, y, part, fontsize=size, color=col, va="top")
                y -= pitch
            y -= 0.7
        y -= 2.4
    return left


def part_sheets(body, number, mass, source_key=None, qty=1):
    """One sheet with the views and the main text; a second sheet when the lists do not fit."""
    shape = body["shape"]
    mat, tolk, finish = material_of(body)
    bought = tolk == "BOUGHT"
    name = body["name"]
    fig, ax = new_sheet()
    label, (W, H, D) = three_views(ax, shape, (8, 44, 170, 156))
    feats = round_features(shape)
    env = f"Envelope {W:.2f} x {D:.2f} x {H:.2f} (width x depth x height in these views)"
    blocks = []
    if bought:
        lines, src = bought_dims(source_key)
        blocks.append(("Published sizes of this bought part", lines or [body["label"]]))
        blocks.append(("As drawn in the model", [env]))
        notes = [TOL_NOTE["BOUGHT"]]
        if src:
            notes.append("Source: " + src)
        notes.append(f"Looked up {P.SOURCE_DATE}. The full table is in design/cad/SOURCES.md.")
    else:
        blocks.append(("Key dimensions (mm)", (key_dims(name) or []) + [env]))
        make = [f"Material: {mat}", f"Finish: {finish}", f"Quantity: {qty}"]
        pr = next((p for p in C.PRINT if p[0] == name), None)
        if pr:
            make += [f"On the printer bed: {pr[3]}", pr[4]] if pr[4] else [f"On the printer bed: {pr[3]}"]
            make.append("0.4 mm nozzle; 0.16 mm layers for shells and buttons, 0.2 mm for the rest; PETG 240 / 80 deg C; TPU 225 deg C")
        blocks.append(("How to make it", make))
        notes = [TOL_NOTE[tolk]]
        if tolk == "FDM":
            notes.append(f"Sliding fits: {P.TOL['slide']:.2f} mm clear per side. Steel pins in drilled holes: {P.TOL['pin']:.2f} mm per side.")
        notes.append("Positions are (x, y, z) in the part's own file: " + ("unit frame, front face y = 0, bottom z = 0" if body["frame"] == "unit"
                     else "book frame, page surface z = 0, top edge of the book y = 0") + ". x in the files is mirrored against sb_params.py.")
        notes.append("A line marked [EST] depends on a size no maker publishes: measure the real part first (design/cad/SOURCES.md).")
    blocks.append(("Round holes and shafts: count x diameter, axis, position (x, y, z)", hole_lines(feats, limit=10 if bought else 60)))
    blocks.append(("Notes", notes))
    left = flow(ax, blocks, 184, 200, 46, 104)
    two = bool(left)
    status = "BOUGHT PART - REFERENCE" if bought else "PROTOTYPE - NOT YET MADE"
    files = f"File: step/{name}.step" + (f"   stl/{name}.stl" if body["printed"] else "") + ("   blade_flat_pattern_*.dxf" if name.startswith("blade_") and "knuckle" not in name and "coat" not in name and "clamp" not in name else "")
    title_block(ax, body["label"][:74], number, "1 of 2" if two else "1 of 1", material=mat[:70], finish=finish[:70], qty=qty, mass=f"{mass:.1f} g (est.)",
                scale=label, status=status)
    ax.text(10, 11, files, fontsize=5.4, color=INK, va="center")
    figs = [fig]
    if two:
        fig2, ax2 = new_sheet()
        ax2.text(12, 198, f"{number}  {name}: lists continued", fontsize=8, fontweight="bold", color=INK, va="top")
        left = flow(ax2, left, 12, 190, 46, 132)
        if left:
            left = flow(ax2, left, 152, 190, 46, 132)
        if left:
            ax2.text(152, 48, "... more in the STEP file", fontsize=5.3, color=INK)
        title_block(ax2, body["label"][:74], number, "2 of 2", material=mat[:70], finish=finish[:70], qty=qty, mass=f"{mass:.1f} g (est.)", scale="-", status=status)
        ax2.text(10, 11, files, fontsize=5.4, color=INK, va="center")
        figs.append(fig2)
    return figs


def assembly_sheets(bodies, rep, check):
    figs = []
    U0 = B.unit_matrix(B.STICK0, B.TIP0)
    total = rep["mass_total_g"]
    skip = WIRES + ("torsion_spring",)
    solids = [B.placed(b, U0) for b in bodies if b["variant"] is None and not b["name"].startswith(skip)]
    comp = cq.Compound.makeCompound(solids)
    fig, ax = new_sheet()
    label, (W, H, D) = three_views(ax, comp, (8, 44, 180, 156), hidden=False)
    pose = P.unit_pose(B.STICK0, B.TIP0)
    sizes = rep["poses"]
    st = sizes["stowed"]["size_mm"]
    ex = sizes["extended"]["size_mm"]
    blocks = [("General arrangement: key dimensions (mm)", [
        f"Pose drawn: open hardcover on a table, stick {P.STICK_COLLAPSED:g}, unit tipped {B.TIP0:g} deg (camera axis {pose['axis_below_h']:g} deg below horizontal)",
        f"Overall in this pose: {W:.1f} wide x {D:.1f} deep x {H:.1f} high",
        f"Folded for the bag: {st[0]:g} x {st[1]:g} x {st[2]:g}. Stick pulled up: {ex[2]:g} high",
        f"Unit {P.UNIT_W:g} x {P.UNIT_H:g} x {P.UNIT_D:g}; hub {P.HUB_W:g} x {P.HUB_D:g} x {P.HUB_H:g}",
        f"Stick axis {-P.STICK_Y:g} behind the top edge of the book; hub top {P.HUB_TOP_Z:g} above the page surface",
        f"Stick {P.STICK_COLLAPSED:g} closed, {P.STICK_EXTENDED:g} pulled up; tilt {P.TIP_NOMINAL - P.TIP_RANGE:g} to {P.TIP_NOMINAL + P.TIP_RANGE:g} deg",
        f"Lens {pose['lens'][1]:.1f} above the page and {-pose['lens'][0]:.1f} behind the top edge",
        f"Blades: {P.BLADE_W:g} x {P.BLADE_T:g}, centre lines {2 * P.BLADE_X:g} apart, reaching {P.BLADE_REACH:g} under the pages, splayed {P.BLADE_SPLAY:g} deg",
        f"Rear leg: pivot to pad centre {P.LEG_CHORD:g}; pad {P.PAD[0]:g} x {P.PAD[1]:g}",
    ]), ("Fit and tolerances", [
        f"Interference check: {rep['n_bodies']} bodies, {len(rep['collisions'])} clashes; {sum(len(v) for v in rep['pose_collisions'].values())} clashes "
        f"between moving parts over {len(rep['pose_collisions'])} poses",
        f"Printed parts +/-{P.TOL['fdm']:g}; sliding fits {P.TOL['slide']:g} clear per side; pins {P.TOL['pin']:g} per side; "
        f"bought parts at least {P.TOL['seat']:g} from anything they must not touch",
        f"Cut sheet +/-{P.TOL['sheet']:g}; cut tube and pin lengths +/-{P.TOL['cut']:g}; turned parts +/-{P.TOL['turn']:g}",
        "Every touching pair and its clearance: design/cad/out/FIT_REPORT.md",
    ]), ("Notes", [
        f"Mass of the model: {total:.0f} g (estimate, nothing weighed)",
        "Wiring, the coiled cord and the springs are left out of these views; they are in the STEP assembly",
        "Nothing has been built from these drawings yet. A first print is needed to prove the fits.",
    ])]
    flow(ax, blocks, 192, 200, 46, 96)
    title_block(ax, "SenseBook v4 tri-grip: general arrangement", "SB-000", "1", material="see parts list", finish="-", qty=1,
                mass=f"{total:.0f} g (est.)", scale=label, status="PROTOTYPE - NOT YET BUILT")
    ax.text(10, 11, "File: SenseBook_assembly.step", fontsize=5.4, color=INK, va="center")
    figs.append(fig)

    # the unit on its own, cover and screws left off, so the inside layout can be read
    inside = [b["shape"] for b in bodies if b["variant"] is None and b["group"] == "unit"
              and not b["name"].startswith(WIRES + ("shell_back_cover", "cover_screw", "heat_spreader", "thermal_pad"))]
    fig, ax = new_sheet()
    label, (W, H, D) = three_views(ax, cq.Compound.makeCompound(inside), (8, 44, 180, 156), hidden=True)
    L = B.LAY
    Dp = P.PD
    blocks = [("Inside the unit (back cover off): where the bought parts sit, unit frame, mm", [
        f"Camera: lens axis square to the {P.FACET_ANGLE:g} deg facet, lens front {P.CAM_LENS_RECESS:g} inside the facet surface; "
        f"board back face {L['a_back']:.2f} behind the facet",
        f"Cells: two packs {Dp('cell', 't_max'):g} x {Dp('cell', 'w_max'):g} x {Dp('cell', 'len_max'):g}, standing either side of the camera, "
        f"inner edges at x +/-{L['cell_x0']:g}, front faces at y {L['cell_y1']:g}, bottom at z {P.CELL_Z0:g}; pocket depth {P.CELL_POCKET_T:g}",
        f"Pi Zero 2 W: flat on the cover posts, underside at y {L['pi_yu']:g}, lower long edge at z {P.PI_Z0:g}, parts facing the cover",
        f"Speaker behind the front grille, centre x {fx(P.SPK_X):g}, lower end z {P.SPK_Z0:g}",
        f"DAC board with its jack against the wall at x = +{P.UNIT_W / 2:g}; charger board with USB-C against the wall at x = -{P.UNIT_W / 2:g}",
        f"Microphones flat under the top, ports at x +/-{L['mic_port'][0]:.2f}, y {L['mic_port'][1]:.2f}",
        f"Least clearance between a bought part and anything it must not touch: {P.TOL['seat']:g}",
    ])]
    flow(ax, blocks, 192, 200, 46, 96)
    title_block(ax, "SenseBook unit: inside layout", "SB-000", "2", material="see parts list", finish="-", qty=1,
                mass=f"{rep['mass_unit_g']:.0f} g (est.)", scale=label, status="PROTOTYPE - NOT YET BUILT")
    ax.text(10, 11, "File: SenseBook_assembly.step (unit bodies)", fontsize=5.4, color=INK, va="center")
    figs.append(fig)
    return figs


def parts_list_sheets(rows, first_sheet=3):
    figs = []
    per = 34
    for k in range(0, len(rows), per):
        fig, ax = new_sheet()
        ax.text(12, 196, "Parts list", fontsize=10, fontweight="bold", color=INK)
        heads = [("No.", 12), ("Drawing", 22), ("Part", 44), ("Qty", 100), ("Material / what it is", 108), ("Mass g", 268)]
        for h, x in heads:
            ax.text(x, 188, h, fontsize=6, fontweight="bold", color=INK)
        ax.plot([10, SHEET_W - 10], [186, 186], color=INK, lw=0.5)
        for i, r in enumerate(rows[k:k + per]):
            y = 182 - i * 4.4
            for val, x in zip(r, [12, 22, 44, 100, 108, 268]):
                ax.text(x, y, str(val), fontsize=5.2, color=INK, va="center")
        title_block(ax, "SenseBook v4 tri-grip: parts list", "SB-000", f"{first_sheet + k // per}", material="-", finish="-", qty="-", mass="-", scale="-",
                    status="PROTOTYPE - NOT YET BUILT")
        figs.append(fig)
    return figs


def main():
    import json
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(os.path.join(OUTDIR, "parts"), exist_ok=True)
    B.build_unit()
    B.build_mechanics()
    bodies = [b for b in B.BODIES if b["variant"] is None]
    rep = json.load(open(os.path.join(HERE, "out", "model_report.json")))
    chk = json.load(open(os.path.join(HERE, "out", "check_report.json")))
    masses = {r["name"]: r["mass_g"] for r in rep["masses"]}
    rows, sheets, n_parts = [], [], 0
    for n, b in enumerate(bodies, 1):
        num = f"SB-{n:03d}"
        name = b["name"]
        mat, tolk, _ = material_of(b)
        what = mat if tolk != "BOUGHT" else b["label"]
        if name in rep["routes"]:
            what = f"{b['label']}: cut to {rep['routes'][name]['length']:g} mm"
        rows.append((n, num, name, 1, what[:112], f"{masses.get(name, 0):.1f}"))
        if want and not any(name.startswith(w) for w in want):
            continue
        if name.startswith(WIRES):
            continue
        figs = part_sheets(b, num, masses.get(name, 0.0), source_key=B.SOURCE_KEY.get(name))
        with PdfPages(os.path.join(OUTDIR, "parts", name + ".pdf")) as pdf:
            for f in figs:
                pdf.savefig(f)
        sheets += figs
        n_parts += 1
        print("drawn", num, name, len(figs), flush=True)
    if not want:
        with PdfPages(os.path.join(OUTDIR, "SenseBook_drawings.pdf")) as pdf:
            front = assembly_sheets(bodies, rep, chk) + parts_list_sheets(rows)
            for fig in front:
                pdf.savefig(fig)
                plt.close(fig)
            for fig in sheets:
                pdf.savefig(fig)
        print("written", os.path.join(OUTDIR, "SenseBook_drawings.pdf"), "with", n_parts, "parts on", len(sheets), "sheets, plus", len(front), "front sheets")
    for fig in sheets:
        plt.close(fig)


if __name__ == "__main__":
    main()
