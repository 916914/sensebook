"""Check the 3D model: fit, clearances, walls, cable routes, mass and stability. Also writes the source table.

Run after build_model.py, from design/cad:
    ..\\.venv\\Scripts\\python.exe check_model.py

Reads out/model_report.json and out/stl/*.stl, re-uses the functions in analysis.py, and writes
    out/check_report.json     every number, for other scripts
    out/FIT_REPORT.md         tolerances, every touching pair, walls, cable routes, mass and stability
    out/PRINT_NOTES.md        how to print each part
    SOURCES.md                every bought part, every dimension, where it came from
plus two diagrams in design/diagrams/. Everything is worked out from the CAD and from published part sizes.
Nothing has been built or measured: a printed part is only proven by printing it.
"""
import json
import math
import os

import numpy as np

import analysis as A
import sb_params as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DIAG = os.path.join(HERE, "..", "diagrams")
TIP0, STICK0 = 10.5, P.STICK_COLLAPSED
TABLE_Z = -(P.COVER_HARD + P.BLOCK_HARD)


def edge_dists(poly, p):
    return [A._edge_dist(poly[i], poly[(i + 1) % len(poly)], p) for i in range(len(poly))]


def stability(mass_g, com_y, com_z, poly, push_z):
    h = com_z - TABLE_Z
    ds = edge_dists(poly, (0.0, com_y))
    names = ["rear (pad edge)", "side", "front (blade tips)", "side"]
    i = int(np.argmin(ds))
    dmin = ds[i]
    return dict(mass_g=round(mass_g, 1), com_y_mm=round(com_y, 1), com_height_mm=round(h, 1),
                min_edge_dist_mm=round(dmin, 1), weakest_edge=names[i],
                tip_angle_deg=round(math.degrees(math.atan2(dmin, h)), 1),
                push_to_tip_at_unit_N=round(mass_g / 1000 * 9.81 * dmin / (push_z - TABLE_Z), 2),
                edge_dists_mm=[round(d, 1) for d in ds])


def wall_thickness(path, n=6000, seed=1):
    import trimesh
    m = trimesh.load(path)
    pts, fid = trimesh.sample.sample_surface(m, n, seed=seed)
    nrm = m.face_normals[fid]
    t = trimesh.proximity.thickness(m, pts, exterior=False, normals=nrm, method="ray")
    t = np.asarray(t, dtype=float)
    t = t[np.isfinite(t) & (t > 0.05)]
    return dict(samples=int(len(t)), min_mm=round(float(t.min()), 2), p05_mm=round(float(np.percentile(t, 5)), 2),
                median_mm=round(float(np.median(t)), 2), share_below_1p2_pct=round(100 * float((t < 1.2).mean()), 1),
                share_below_0p8_pct=round(100 * float((t < 0.8).mean()), 1),
                share_at_nominal_pct=round(100 * float(((t > P.WALL - 0.15) & (t < P.WALL + 0.15)).mean()), 1),
                volume_cm3=round(float(m.volume) / 1000, 2), watertight=bool(m.is_watertight))


# ------------------------------------------------------------------------------------------------ fits
SL, PIN, SEAT = P.TOL["slide"], P.TOL["pin"], P.TOL["seat"]
FITS = [  # name starts with, other name starts with, kind of fit, designed clearance per side (mm), what it is
    ("blade_clamp_screw", "blade_knuckle", "joined", 0.0, "clamp screw threaded into the knuckle"),
    ("blade_coat", "blade_", "bonded", 0.0, "coating on the blade"),
    ("blade_clamp_screw", "blade_", "pin", 0.10, "M1.6 clamp screw through the 1.8 mm hole in the blade"),
    ("blade_knuckle", "blade_", "clamped", 0.03, "blade in the knuckle slit, pinched by the clamp screw (saw the slit to 0.45 mm)"),
    ("tilt_pivot_screw", "tilt_joint_head", "pin", PIN, "M3 pivot through the joint tongue: drill to 3.1 mm"),
    ("tilt_pivot_screw", "shell_front_tub", "pin", 0.10, "M3 pivot through the two lugs: drill to 3.2 mm"),
    ("mic_mute_slider", "mic_mute_switch", "sliding", 0.10, "slider cap pocket over the switch lever"),
    ("camera_lens_m12", "camera_holder_m12", "thread", 0.02, "M12 lens thread in its holder (one bought assembly)"),
    ("camera_lens_glass", "camera_lens_m12", "bonded", 0.04, "front element in the lens barrel (one bought part)"),
    ("lens_bezel", "camera_lens", "sliding", 0.20, "lens rim inside the bezel opening"),
    ("harness_", "pi_", "bonded", 0.05, "wires soldered to the Pi's GPIO pads"),
    ("speaker_leads", "amp_board", "bonded", 0.05, "leads soldered to the amp board"),
    ("dac_jack", "shell_front_tub", "sliding", 0.20, "headphone jack nose in its hole in the side wall"),
    ("usb_c_receptacle", "shell_front_tub", "sliding", 0.20, "USB-C shell in its opening in the side wall"),
    ("microsd_card", "pi_", "bonded", 0.25, "card in its slot on the Pi"),
    ("hub_cord_tail", "pi_", "bonded", 0.10, "cord soldered to the Pi's GPIO pads"),
    ("hub_cord_tail", "shell_front_tub", "sliding", 0.55, "cord through its 2 mm hole in the bottom of the unit"),
    ("hub_cord_riser", "tilt_joint_head", "sliding", 0.30, "cord in the hole and slot of the joint head"),
    ("hub_cord_riser", "stick_inner_tube", "sliding", 0.30, "cord leaving the joint head just above the top of the tube"),
    ("hub_cord_tail", "tilt_joint_head", "sliding", 0.30, "cord leaving the slot at the back of the joint head"),
    ("hub_sensor_lead", "hub_body", "sliding", 0.15, "lead laid in its 1.2 mm groove in the hub"),
    ("hub_sensor_lead", "stick_outer_tube", "sliding", 0.15, "lead through the notch filed in the foot of the outer tube"),
    ("hub_sensor_lead", "stick_", "sliding", 0.15, "lead under the inner tube and its bush, inside the outer tube"),
    ("hub_sensor_lead", "hub_sensor_switch", "bonded", 0.0, "lead soldered to the sensor board"),
    ("button_", "shell_front_tub", "sliding", SL, "button cap in its opening, held in by its inner lip"),
    ("mic_mute_slider", "shell_front_tub", "sliding", SL, "slider cap in its slot"),
    ("mic_mute_flag", "shell_front_tub", "sliding", SL, "orange flag (paint or sticker on the slider) seen through the slot"),
    ("mic_mute_slider", "mic_mute_flag", "sliding", SL, "flag sits beside the cap, in the same slot"),
    ("shell_back_cover", "shell_front_tub", "sliding", P.TONGUE_GAP, "cover tongue inside the tub wall; the two shells meet at the seam"),
    ("status_dot_pipes", "shell_front_tub", "press", 0.05, "clear pins pushed into the dot holes, a drop of glue"),
    ("light_ring_diffuser", "shell_front_tub", "press", 0.10, "diffuser ring glued into the lens opening"),
    ("lens_bezel", "light_ring_diffuser", "press", 0.0, "bezel ring glued inside the diffuser"),
    ("leg_pin", "hub_body", "pin", PIN, "hinge pin: drill the printed hole to 2.0 mm"),
    ("leg_pin", "rear_leg", "pin", PIN, "hinge pin through the leg barrel: drill to 2.1 mm so the leg turns freely"),
    ("knuckle_pin", "hub_body", "pin", PIN, "knuckle pin: drill the printed hole to 1.6 mm"),
    ("knuckle_pin", "blade_knuckle", "pin", PIN, "knuckle turns on the pin: drill to 1.7 mm"),
    ("stick_outer_tube", "hub_body", "press", 0.08, "tube pushed into the hub bore and glued"),
    ("stick_outer_tube", "stick_collar", "press", 0.06, "collar pushed onto the outer tube"),
    ("stick_inner_tube", "stick_collar", "sliding", 0.10, "inner tube slides through the collar, which grips it when twisted"),
    ("stick_glide_bush", "stick_outer_tube", "sliding", 0.04, "glide bush on the inner tube runs in the outer tube"),
    ("stick_inner_tube", "stick_outer_tube", "sliding", 0.50, "telescope: 8 mm tube in the 9 mm bore, guided by the bush and collar"),
    ("tilt_joint_head", "shell_front_tub", "hinge", 0.20, "lugs swing over the joint collar (0.2) and beside its tongue (0.3)"),
    ("tilt_joint_head", "stick_inner_tube", "press", 0.05, "joint spigot pushed into the inner tube and glued"),
    ("rear_leg", "hub_body", "hinge", SEAT, "leg barrel and arm in the hub slot"),
    ("torsion_spring", "hub_body", "hinge", 0.10, "spring in its pocket, free to wind: 0.25 around it, 0.1 at its end face"),
    ("torsion_spring", "rear_leg", "hinge", 0.15, "spring rides on the leg barrel"),
    ("blade_knuckle", "hub_body", "hinge", 0.20, "knuckle in its notch, turns on the pin"),
    ("blade_clamp_screw", "hub_body", "hinge", 0.20, "clamp screw head swings past the hub"),
    ("blade_clamp_screw", "knuckle_pin", "hinge", 0.20, "clamp screw passes beside the pin"),
    ("blade_", "hub_body", "hinge", SEAT, "blade root swings with its knuckle"),
    ("speaker", "shell_front_tub", "bonded", 0.10, "speaker held on the front wall by a 0.1 mm glue or tape line"),
    ("haptic_motor", "shell_front_tub", "bonded", 0.10, "motor stuck to the front wall with its own adhesive pad"),
    ("status_leds", "status_dot_pipes", "bonded", 0.10, "LED faces the end of its light pipe"),
    ("light_ring_diffuser", "light_ring_leds", "bonded", 0.20, "LEDs face the back of the diffuser"),
    ("hub_sensor_switch", "stick_outer_tube", "bonded", 0.25, "sensor board glued in its pocket, beside the tube"),
    ("camera_flex", "pi_", "bonded", 0.15, "flex lies along the Pi, held by a strip of tape"),
    ("camera_flex", "cell_foam", "bonded", 0.15, "flex passes behind the foam pad"),
    ("camera_flex", "shell_front_tub", "bonded", 0.20, "flex passes under the top wall"),
]
NESTED_WHY = [
    ("cover_screw", "tapping screw in its printed boss"), ("camera_screws", "tapping screw through the camera board into its post"),
    ("blade_clamp_screw", "clamp screw in the knuckle"), ("knuckle_pin", "pin through the knuckle"), ("leg_pin", "pin through the leg barrel"),
    ("blade_coat", "coating on the blade"), ("blade_", "blade clamped in the knuckle slit"), ("stick_", "tube inside tube"),
    ("tilt_pivot_screw", "pivot screw through the lugs and the tongue"), ("tilt_", "pivot screw through the joint"),
    ("camera_flex", "flex plugged into its connector"), ("camera_lens", "lens screwed into its holder"),
    ("harness_", "wires soldered to the board"), ("battery_leads", "leads soldered to the board or leaving the pack"),
    ("speaker_leads", "leads soldered on"), ("hub_cord_tail", "cord joined to the next length of cord"),
    ("hub_cord_riser", "cord joined to the coil"), ("hub_sensor_lead", "lead joined to the coil or soldered to the sensor"),
    ("light_ring_leds", "LEDs soldered to the ring board"), ("usb_c_receptacle", "socket soldered to the charger board"),
    ("dac_jack", "jack soldered to the DAC board"), ("mic_mute_slider", "cap gripping the switch lever"),
    ("hub_sensor_switch", "switch plunger pressed by the leg"), ("torsion_spring", "spring on the leg barrel"),
    ("shell_back_cover", "Pi located on the cover pins"),
]


def fit_of(a, b, kind):
    for pa, pb, cls, des, why in FITS:
        if (a.startswith(pa) and b.startswith(pb)) or (b.startswith(pa) and a.startswith(pb)):
            return cls, des, why
    if kind == "nested":
        for p, why in NESTED_WHY:
            if a.startswith(p) or b.startswith(p):
                return "joined", None, why
        return "joined", None, "joined by design"
    if kind == "contact":
        return "seated", 0.0, "parts touch by design: seated, glued, taped or soldered"
    return "clearance", SEAT, "neighbours that must not touch"


def fit_rows(rep):
    printed = set(rep["printed"])
    rows = []
    for p in rep["pairs"]:
        a, b, kind = p["a"], p["b"], p["kind"]
        cls, des, why = fit_of(a, b, kind)
        gap = p.get("gap_mm")
        if kind == "nested":
            verdict = "by design"
        elif kind == "contact":
            verdict = "CHECK: touching" if cls == "clearance" else "by design"
        elif cls == "clearance":
            if gap >= SEAT - 0.006:
                verdict = "ok"
            elif (a in printed or b in printed) and gap < P.TOL["fdm"] - 0.006:
                verdict = "TIGHT: under the 0.2 mm print tolerance"
            else:
                verdict = "close: under 0.3 mm"
        else:
            verdict = "as designed" if gap >= des - 0.011 else "tighter than designed"
        rows.append(dict(a=a, b=b, kind=kind, gap_mm=gap, overlap_mm3=p.get("overlap_mm3"), fit=cls, designed_mm=des,
                         what=why, verdict=verdict, printed=[n for n in (a, b) if n in printed]))
    order = {"TIGHT: under the 0.2 mm print tolerance": 0, "CHECK: touching": 0, "tighter than designed": 1, "close: under 0.3 mm": 2,
             "as designed": 3, "ok": 4, "by design": 5}
    rows.sort(key=lambda r: (order[r["verdict"]], r["gap_mm"] if r["gap_mm"] is not None else 9, r["a"], r["b"]))
    return rows


def route_rows(rep):
    out = []
    stock = {"battery_leads": ("pack leads, 150 mm each (Akyga sheet)", 2 * P.PD("cell", "lead_len")),
             "camera_flex": ("stock cable, 150 mm (Raspberry Pi drawing)", P.PD("fpc", "len"))}
    for name, r in rep["routes"].items():
        gaps = [p["gap_mm"] for p in rep["pairs"] if p["kind"] == "gap" and name in (p["a"], p["b"])]
        near = sorted((p["gap_mm"], p["b"] if p["a"] == name else p["a"]) for p in rep["pairs"]
                      if p["kind"] == "gap" and name in (p["a"], p["b"]))
        hit = [h for h in rep["collisions"] if name in (h["a"], h["b"])]
        st = stock.get(name)
        out.append(dict(name=name, label=rep["labels"].get(name, name), diameter_mm=round(2 * r["radius"], 2), length_mm=r["length"],
                        bends=max(len(r["points"]) - 2, 0) if r["points"] else r.get("bends"),
                        stock=st[0] if st else "cut to length", stock_mm=st[1] if st else None,
                        spare_mm=round(st[1] - r["length"], 1) if st else None,
                        clashes=len(hit), least_clearance_mm=min(gaps) if gaps else None,
                        nearest=near[0][1] if near else None, extra={k: v for k, v in r.items() if k not in ("points", "radius", "length")}))
    return out


# ------------------------------------------------------------------------------------------------ printing
PRINT = [  # file stem, qty, material, how to place it on the bed, notes
    ("shell_front_tub", 1, "PETG, slate-teal", "Open back down on the bed (front face up).",
     "Supports inside for the top wall and under the lens facet; none on the visible front. 3 perimeters, 0.16 mm layers. "
     f"Clean the four dot holes with a {P.DOT_D:g} mm drill, the cover screw pilots with a 1.7 mm drill, and the lens opening with a blade."),
    ("shell_back_cover", 1, "PETG, slate-teal", "Outside face down on the bed.",
     f"No supports. The four Pi posts end in {2 * (P.PD('pi', 'hole_d') / 2 - P.TOL['pin'] - 0.05):.2f} mm locating pins: "
     f"check they pass the {P.PD('pi', 'hole_d'):g} mm Pi holes before fitting the board."),
    ("button_ask", 1, "PETG, marigold (or paint)", "Flange down.", "The dished top prints without support. 100% infill."),
    ("button_play_pause", 1, "PETG, lighter teal", "Flange down.", "100% infill."),
    ("button_back", 1, "PETG, lighter teal", "Flange down.", "The raised arrow points away from the Play button."),
    ("button_forward", 1, "PETG, lighter teal", "Flange down.", "Mirror of Back."),
    ("button_vol_up", 1, "PETG, lighter teal", "Flange down.", "Has the raised dot."),
    ("button_vol_down", 1, "PETG, lighter teal", "Flange down.", ""),
    ("mic_mute_slider", 1, "PETG, lighter teal", "Flat side down.", "Tiny part: print four and keep the best. Paint the flag area orange."),
    ("light_ring_diffuser", 1, "PETG, natural / clear", "Flat on the bed.", "0.12 mm layers, 100% infill so it glows evenly. Glue in with a drop of clear glue."),
    ("status_dot_pipes", 1, "PETG, natural / clear", "Standing on end.",
     f"Four {P.DOT_D:g} mm pins in one file. Or cut them from {P.DOT_D:g} mm clear filament or acrylic rod."),
    ("tilt_joint_head", 1, "PETG", "Spigot up, tongue on the bed with support, or split and glue.",
     f"Drill the pivot hole to {P.PIVOT_PIN_D:.1f} mm. 100% infill: this part carries the unit."),
    ("stick_collar", 1, "PETG", "Wide end down.", "Ream to push onto the 10 mm tube and grip the 8 mm tube lightly."),
    ("hub_body", 1, "PETG", "Top face down on the bed.",
     "Supports in the leg slot, the spring pockets and the knuckle seats. Drill: stick bore 10.1 mm, leg pin 2.0 mm, knuckle pin 1.6 mm. 100% infill."),
    ("blade_knuckle_right", 1, "PETG", "Slit vertical.", "Saw or file the blade slit to 0.45 mm if it closes up. Drill 1.7 mm (pin); clamp screw hole 1.7 mm above the slit, 1.3 mm pilot below it."),
    ("blade_knuckle_left", 1, "PETG", "Slit vertical.", "Mirror of the right knuckle."),
    ("rear_leg", 1, "PETG", "Flat on its side, barrel axis vertical.", "Layers then run along the arm, which is stronger. Drill the barrel 2.1 mm."),
    ("rear_leg_pad", 1, "TPU 95A", "Flat.", "Glue to the T-foot with flexible CA or contact glue."),
]


def print_notes(rep):
    import trimesh
    rho = {"PETG": P.RHO["petg"], "TPU": P.RHO["tpu"]}
    rows, total = [], 0.0
    for stem, qty, mat, place, note in PRINT:
        m = trimesh.load(os.path.join(OUT, "stl", stem + ".stl"))
        g = float(m.volume) / 1000 * rho["TPU" if mat.startswith("TPU") else "PETG"] * qty
        total += g
        ex = sorted((float(v) for v in m.extents), reverse=True)
        rows.append(f"| `stl/{stem}.stl` | {qty} | {mat} | {ex[0]:.1f} x {ex[1]:.1f} x {ex[2]:.1f} | {g:.1f} | {place} | {note} |")
    missing = sorted(set(rep["printed"]) - {p[0] for p in PRINT})
    assert not missing, f"printed parts without print notes: {missing}"
    zo = P.TUBE_OUT_Z[1] - P.TUBE_OUT_Z[0]
    out = ["# SenseBook prototype: 3D-print notes", "",
           "> **Not yet printed.** These files come straight from the parametric model (`build_model.py`). Sizes and masses below are "
           "read from the STL files. Expect one or two fit iterations on the first prints, mainly holes and the cover fit. "
           "Every part also has a dimensioned drawing in `design/drawings/`.", "",
           f"{len(PRINT)} printed parts, about **{total:.0f} g of filament** in total at 100% infill (estimate; supports not counted).", "",
           "## Settings that should work", "",
           "- 0.4 mm nozzle, 0.16 mm layers for the two shells and the buttons, 0.2 mm for the rest.",
           f"- PETG: 240 °C nozzle, 80 °C bed, 3 perimeters. Walls are {P.WALL:g} mm, so the shells print as solid walls.",
           "- TPU 95A for the pad: 225 °C, slow (25 mm/s), no retraction tricks needed for a flat pad.",
           f"- The model is drawn for a general print tolerance of ±{P.TOL['fdm']:g} mm, with {P.TOL['slide']:g} mm clearance per side on "
           "sliding fits (buttons, slider, cover tongue).",
           "- Holes print small. Drill them to size: 1.7 mm pilots for the ST2.2 tapping screws, 2.0 mm and 1.6 mm for the hinge pins, "
           f"{P.PIVOT_PIN_D:.1f} mm for the tilt pivot, 10.1 mm for the stick.", "",
           "## Parts", "", "| File | Qty | Material | Size (mm) | Mass (g, est.) | On the bed | Notes |", "|---|---|---|---|---|---|---|"] + rows + [
           "", "## Not printed", "",
           f"- **Blades:** cut from {P.BLADE_T:g} mm full-hard 300-series stainless spring shim with the `blade_flat_pattern_*.dxf` outlines "
           "(two bends each, see the assembly guide). `hardcover` has the shorter step, `thin_book` the longer one. Round and deburr every edge.",
           f"- **Stick:** {P.STICK_OD_OUTER:g} mm and {P.STICK_OD_INNER:g} mm stainless tube, {P.STICK_WALL:g} mm wall, cut to {zo:g} mm and "
           f"{P.TUBE_IN_LEN:g} mm (±{P.TOL['cut']:g}).",
           f"- **Lens bezel:** turned or printed ring, {P.RING_ID:g} mm outside, {P.LENS_OPENING_D:g} mm inside, {P.WALL:g} mm thick, "
           "chamfered on the outer face. There is no window: the lens front sits in the bezel.",
           f"- **Heat spreader:** {P.SPREADER[0]:g} x {P.SPREADER[1]:g} x {P.SPREADER[2]:g} mm aluminium sheet.",
           f"- **Pins:** leg hinge pin 2.0 x {P.HUB_W - 0.4:g} mm, knuckle pin 1.6 x 30.8 mm, steel.",
           "", "## Frames", "",
           "- Unit parts are in the unit frame from `sb_params.py` (mm): front face at y = 0, bottom at z = 0.",
           "- Stick, hub and leg parts are in the book frame: page surface z = 0, top edge of the book y = 0.",
           "- The CAD files are right-handed, so x is mirrored against `sb_params.py`: in the files, +x is the reader's left.",
           f"- `SenseBook_assembly.step` holds all {rep['n_bodies']} bodies in place (hardcover pose); `step/` has one STEP per body.", ""]
    with open(os.path.join(OUT, "PRINT_NOTES.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    return round(total, 1)


# ------------------------------------------------------------------------------------------------ source table
BASIS = {"drawing": "maker's drawing or datasheet, labelled", "design": "maker's published board file",
         "model": "measured on the maker's published 3D file", "scaled": "measured from the 1:1 artwork in the maker's drawing (about ±0.1)",
         "page": "maker's or seller's product page", "EST": "no source found: our estimate, to be measured on the real part"}
UNITS = {"mass_g": "g", "capacity_mah": "mAh", "max_discharge_a": "A", "out_a": "A", "lead_awg": "AWG", "coils": "turns",
         "max_torque_nmm": "N·mm", "max_angle_deg": "°", "yield_mpa": "MPa", "tensile_mpa": "MPa", "hfov_deg": "°", "vfov_deg": "°",
         "dfov_deg": "°", "force_n": "N"}


def sources_md(rep):
    used = {}
    for body, key in rep["source_key"].items():
        used.setdefault(key, []).append(body)
    n_dim = sum(len(p["dims"]) for p in P.PARTS.values())
    n_est = sum(1 for p in P.PARTS.values() for v in p["dims"].values() if v[2] == "EST")
    L = ["# SenseBook: where every part size comes from", "",
         f"Looked up on {P.SOURCE_DATE}. This table is written by `check_model.py` from `sb_params.py` (`PARTS`, `SRC`, `EST_WHY`), "
         "which is the single source of truth: the 3D model, the drawings and the bill of materials all read the same numbers.", "",
         f"**{len(P.PARTS)} bought parts, {n_dim} values, {n_est} of them estimates (marked EST).** "
         "An EST value is one no published source gives. It is listed at the end with the reason and how to measure it.", "",
         "How to read the *basis* column:", ""]
    L += [f"- **{k}**: {v}" for k, v in BASIS.items()]
    L += ["", "No third-party 3D file is stored in this repository. Each part is modelled from the published dimensions below, "
              "and the drawing or file they were read from is cited. (Raspberry Pi drawings are open, but their STEP files may not be "
              "redistributed; Arducam's STEP file carries no stated licence; KiCad library models are CC-BY-SA.)", ""]
    for key, p in P.PARTS.items():
        L += [f"## {p['name']}", "", f"Key in `sb_params.PARTS`: `{key}`. "
              + (f"Bodies in the model: {', '.join('`' + b + '`' for b in sorted(used[key]))}." if key in used else "Used for sizes only (no body of its own)."),
              "", "| Dimension | Value | Basis | Source |", "|---|---|---|---|"]
        for d, (val, sid, basis) in p["dims"].items():
            unit = UNITS.get(d, "mm")
            title, url = P.SRC[sid]
            src = f"[{title}]({url})" if url else title
            L.append(f"| `{d}` | {val:g} {unit} | {'**EST**' if basis == 'EST' else basis} | {src} |")
        L.append("")
    L += ["## Estimates: what to measure on the real parts", "",
          "| Part | Dimension | Value used | Why it is an estimate | How to measure |", "|---|---|---|---|---|"]
    for (k, d), (why, how) in P.EST_WHY.items():
        val = P.PARTS[k]["dims"][d][0]
        unit = UNITS.get(d, "mm")
        L.append(f"| {P.PARTS[k]['name']} | `{d}` | {val:g} {unit} | {why} | {how} |")
    L += ["", "## All sources", "", "| Id | Source | Link |", "|---|---|---|"]
    for sid, (title, url) in P.SRC.items():
        L.append(f"| {sid} | {title} | {url or 'none'} |")
    L.append("")
    with open(os.path.join(HERE, "SOURCES.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))
    return dict(parts=len(P.PARTS), values=n_dim, estimates=n_est)


# ------------------------------------------------------------------------------------------------ fit report
def fit_report_md(res, rep):
    f, mass = res["fit"], res["mass"]
    rows = res["fit_pairs"]
    cnt = {}
    for r in rows:
        cnt[r["verdict"]] = cnt.get(r["verdict"], 0) + 1
    n = lambda k: cnt.get(k, 0)
    lab = rep["labels"]
    nm = lambda x: f"`{x}`"
    L = ["# SenseBook: fit report", "",
         "> Worked out from the CAD by `build_model.py` and `check_model.py`. The bought parts are drawn at their published sizes "
         "(see `../SOURCES.md`). **Nothing here has been printed or measured.** CAD can prove that the drawn parts do not clash; "
         "only a print proves the real fit.", "",
         "## 1. Tolerances the model is drawn for", "",
         "| What | Value | Where it is used |", "|---|---|---|",
         f"| Printed PETG part, general | ±{P.TOL['fdm']:g} mm | every printed part |",
         f"| Sliding fit, printed | {P.TOL['slide']:g} mm clearance per side ({2 * P.TOL['slide']:g} mm on the width) | button caps, mute slider, cover tongue |",
         f"| Steel pin in a drilled hole | {P.TOL['pin']:g} mm per side | leg hinge pin, knuckle pin (holes are drilled to size after printing) |",
         f"| Bought part to anything it must not touch | at least {P.TOL['seat']:g} mm | boards, cells, speaker, camera |",
         f"| Cut sheet metal outline | ±{P.TOL['sheet']:g} mm | blades, heat spreader |",
         f"| Cut length of tube or pin | ±{P.TOL['cut']:g} mm | stick tubes, hinge pins |",
         f"| Turned part | ±{P.TOL['turn']:g} mm | lens bezel, thumb nut |", "",
         "## 2. Interference check", "",
         f"- Bodies checked: **{f['bodies']}**, every pair whose boxes come within 0.6 mm, by exact solid intersection.",
         f"- Clashes in the assembled pose: **{len(f['collisions'])}**.",
         "- Clashes between parts that move against each other, in each pose: "
         + ", ".join(f"{k.replace('_', ' ')} **{len(v)}**" for k, v in f["pose_collisions"].items()) + ".",
         f"- Pairs that overlap on purpose (a screw in its boss, a wire on its pad): {n('by design') and sum(1 for r in rows if r['kind'] == 'nested')}. "
         "They are listed in section 3 as *joined*.", ""]
    if f["collisions"]:
        L += ["**Clashes still open:**", ""] + [f"- {nm(h['a'])} and {nm(h['b'])}: {h['overlap_mm3']} mm³" for h in f["collisions"]] + [""]
    L += ["## 3. Clearance between every pair of parts that touch or come within 0.5 mm", "",
          f"{len(rows)} pairs. **{n('TIGHT: under the 0.2 mm print tolerance') + n('CHECK: touching')}** need a check on the first print because the gap is "
          f"smaller than the print tolerance, **{n('close: under 0.3 mm')}** are closer than our 0.3 mm rule, **{n('tighter than designed')}** are tighter "
          f"than the fit they were drawn for, {n('as designed')} are designed fits at their drawn clearance, {n('ok')} are clear, and "
          f"{n('by design')} touch or overlap on purpose.", "",
          "| Part A | Part B | Gap in CAD (mm) | Fit | Drawn clearance (mm) | What it is | Result |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        gap = "overlap" if r["kind"] == "nested" else "0 (touching)" if r["kind"] == "contact" else f"{r['gap_mm']:.2f}"
        des = "" if r["designed_mm"] is None else f"{r['designed_mm']:g}"
        L.append(f"| {nm(r['a'])} | {nm(r['b'])} | {gap} | {r['fit']} | {des} | {r['what']} | {r['verdict']} |")
    L += ["", "## 4. Wall thickness of the printed parts", "",
          "Measured on the STL files by casting rays inward from 6,000 points on each part. The minimum is usually a chamfer, a rib edge or "
          "the rim of a hole, so read the 5th percentile and the share under 0.8 mm as well. 0.8 mm is two passes of a 0.4 mm nozzle.", "",
          "| Part | Thinnest (mm) | 5th percentile (mm) | Median (mm) | Under 0.8 mm | Under 1.2 mm | Volume (cm³) | Watertight |", "|---|---|---|---|---|---|---|---|"]
    for k, w in res["walls"].items():
        L.append(f"| {nm(k)} | {w['min_mm']:.2f} | {w['p05_mm']:.2f} | {w['median_mm']:.2f} | {w['share_below_0p8_pct']:.1f}% | "
                 f"{w['share_below_1p2_pct']:.1f}% | {w['volume_cm3']:.2f} | {'yes' if w['watertight'] else '**NO**'} |")
    L += ["", "## 5. Cable routes", "",
          "Each bundle is drawn as a solid along its route and goes through the same clash check as every other part. "
          "Runs are drawn straight with sharp corners; real wire takes a radius, so allow the spare length shown.", "",
          "| Route | What it carries | Bundle (mm) | Length (mm) | Bends | Stock | Spare (mm) | Clashes | Least clearance (mm) |", "|---|---|---|---|---|---|---|---|---|"]
    for r in res["cable_routes"]:
        lc = "0.5 or more" if r["least_clearance_mm"] is None else f"{r['least_clearance_mm']:.2f} to `{r['nearest']}`"
        L.append(f"| {nm(r['name'])} | {r['label']} | {r['diameter_mm']:g} | {r['length_mm']:g} | {'' if r['bends'] is None else r['bends']} | "
                 f"{r['stock']} | {'' if r['spare_mm'] is None else r['spare_mm']} | {r['clashes']} | {lc} |")
    hc = rep["routes"].get("hub_cord", {})
    L += ["", f"- **Camera flex:** the route is {rep['routes']['camera_flex']['length']:g} mm, the stock cable is {P.PD('fpc', 'len'):g} mm. "
              "The spare length has to be folded flat behind the Pi; the model does not draw that fold. Do not crease the flex: fold it over a 1 mm rod.",
          f"- **Hub cord:** a coil of {hc.get('coil_od', 0):g} mm outside diameter inside the {hc.get('bore', 0):g} mm bore of the inner tube, "
          f"{hc.get('length', 0):g} mm of cord, stretching by {P.STICK_EXTENDED - P.STICK_COLLAPSED:g} mm when the stick is pulled out. "
          "Whether a hand-wound coil stretches that far without snagging is not proven: test it on the first build.",
          "- **Battery leads:** both packs are joined in parallel at the charger board. The packs come with 150 mm leads; cut them to the route length plus 15 mm.", "",
          "## 6. Mass and centre of mass", "",
          f"- Assembled mass in the model: **{mass['model_total_g']:.1f} g** (unit {mass['model_unit_g']:.1f} g). "
          "Printed parts are volume times density; bought parts use the published mass, or an EST where none is published.",
          f"- Centre of mass of the unit, in the unit frame: x {mass['com_unit_frame_mm'][0]:g}, y {mass['com_unit_frame_mm'][1]:g}, z {mass['com_unit_frame_mm'][2]:g} mm.", "",
          "| Group | Model (g) | `sb_params.MASS` (g) | Difference (g) |", "|---|---|---|---|"]
    for b in mass["by_group"]:
        L.append(f"| {b['key'].replace('_', ' ')} | {b['model_g']:.1f} | {b['params_g']:.1f} | {b['diff_g']:+.1f} |")
    s = res["stability_no_book_tripod"]
    L += ["", "## 7. Tripod stability (no book)", "",
          "| Case | Mass (g) | Centre of mass height (mm) | Nearest edge of the feet (mm) | Tips at | Sideways push at the unit that tips it (N) |", "|---|---|---|---|---|---|",
          f"| Model, stick 9 cm | {s['model']['mass_g']} | {s['model']['com_height_mm']} | {s['model']['min_edge_dist_mm']} ({s['model']['weakest_edge']}) | "
          f"{s['model']['tip_angle_deg']}° | {s['model']['push_to_tip_at_unit_N']} |",
          f"| Model, stick 18 cm | {s['model_stick_extended_18cm']['mass_g']} | {s['model_stick_extended_18cm']['com_height_mm']} | "
          f"{s['model_stick_extended_18cm']['min_edge_dist_mm']} ({s['model_stick_extended_18cm']['weakest_edge']}) | "
          f"{s['model_stick_extended_18cm']['tip_angle_deg']}° | {s['model_stick_extended_18cm']['push_to_tip_at_unit_N']} |",
          f"| `analysis.py` (point masses from `sb_params.MASS`) | {s['analysis_masses_on_model_feet']['mass_g']} | {s['analysis_masses_on_model_feet']['com_height_mm']} | "
          f"{s['analysis_masses_on_model_feet']['min_edge_dist_mm']} | {s['analysis_masses_on_model_feet']['tip_angle_deg']}° | "
          f"{s['analysis_masses_on_model_feet']['push_to_tip_at_unit_N']} |", "",
          f"Sizes in each pose (mm): " + "; ".join(f"{k.replace('_', ' ')} {v['size_mm'][0]:g} x {v['size_mm'][1]:g} x {v['size_mm'][2]:g}" for k, v in f["poses"].items()) + ".", ""]
    with open(os.path.join(OUT, "FIT_REPORT.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


def main():
    rep = json.load(open(os.path.join(OUT, "model_report.json")))
    old = json.load(open(os.path.join(OUT, "analysis_results.json")))
    res = {}

    # ---------------- lens position: model against the pose used in analysis.py
    pose = P.unit_pose(STICK0, TIP0)
    ly, lz = pose["lens"]
    t = math.radians(P.FACET_ANGLE + TIP0)
    back = P.CAM_LENS_RECESS                                    # physical lens front sits behind the facet plane
    my, mz = ly - back * math.cos(t), lz + back * math.sin(t)
    m_ref, _, _ = A.best_pose(STICK0, 370, 245)
    m_model = A.margin(my, mz, pose["theta_from_vertical"], 370, 245)
    # largest field angle needed to see the textbook corners, and what the lens opening lets through
    phis = []
    for x in (-185, 185):
        for y in (0, 245):
            u, v = A.project(my, mz, pose["theta_from_vertical"], x, y)
            phis.append(math.degrees(math.hypot(u, v) / A.F_PX))
    need = max(phis)
    bezel_r = P.LENS_OPENING_D / 2                              # lens bezel inner radius
    res["camera"] = dict(
        analysis_lens_point_mm=[round(ly, 1), round(lz, 1)], model_lens_front_mm=[round(my, 1), round(mz, 1)],
        coverage_margin_pct_analysis=round(100 * m_ref, 1), coverage_margin_pct_model=round(100 * m_model, 1),
        largest_field_angle_needed_deg=round(need, 1), bezel_inner_radius_mm=bezel_r, lens_rim_radius_mm=P.PD("cam", "lens_rim_d") / 2,
        lens_apex_behind_facet_mm=P.CAM_LENS_RECESS,
        lens_fov_deg=dict(h=P.PD("cam", "hfov_deg"), v=P.PD("cam", "vfov_deg"), d=P.PD("cam", "dfov_deg")),
        note="The lens dome sits 0.4 mm inside the facet, in a bezel that only clears its rim, so nothing stands in front of the glass. "
             "analysis.py models the lens as equidistant with 120 degrees across; the maker states 120 H / 66.7 V / 152.2 D. "
             "Real distortion and sharpness at the corners are unknown until a page is photographed.")

    # ---------------- mass and centre of mass
    pm = rep["poses"]
    info = rep["info"]
    tip = info["blade_tips"]["deep"]
    a0 = math.radians(info["leg_table_deg"])
    pad_y = P.LEG_PIVOT[0] - P.LEG_CHORD * math.cos(a0)
    fw = P.PAD[0] / 2
    poly = [(-fw, pad_y - P.PAD[1] / 2), (fw, pad_y - P.PAD[1] / 2), (abs(tip[0]), tip[1]), (-abs(tip[0]), tip[1])]
    push_z = pose["top_z"] - 15                                  # same push height as analysis.py
    d = pm["table_hardcover"]
    s_model = stability(d["mass_g"], d["com"][1], d["com"][2], poly, push_z)
    # same geometry, masses from the sb_params budget (to separate "heavier" from "different shape")
    items, m_a, cy_a, cz_a = A.com_and_masses(STICK0, TIP0)
    s_budget_on_model_feet = stability(m_a, cy_a, cz_a, poly, push_z)
    de = pm["extended"]
    pose_e = P.unit_pose(P.STICK_EXTENDED, 14.5)
    s_ext = stability(de["mass_g"], de["com"][1], de["com"][2], poly, pose_e["top_z"] - 15)
    res["stability_no_book_tripod"] = dict(
        analysis_py=old["stability"]["tripod_no_book"] | {"polygon": None, "com": None},
        model=s_model, analysis_masses_on_model_feet=s_budget_on_model_feet, model_stick_extended_18cm=s_ext,
        support_polygon_mm=[[round(a, 1), round(b, 1)] for a, b in poly], table_z_mm=TABLE_Z,
        note="Model feet: rear pad 14 mm deep centred %.0f mm behind the top edge, blade tips at (+-%.0f, %.0f)." % (-pad_y, abs(tip[0]), tip[1]))

    # table with a book: same formula as analysis.table_with_book, model mass / CoM / foot position
    page_block_g = 150.0
    Rb = (page_block_g / 2) / 1000 * 9.81
    Wt = d["mass_g"] / 1000 * 9.81
    xt, yt = abs(tip[0]), tip[1]
    bc = (P.BLADE_X + 0.5 * (xt - P.BLADE_X), 0.5 * yt)
    M_back = Wt * (d["com"][1] - pad_y) + 2 * Rb * (bc[1] - pad_y)
    line = ((fw, pad_y), (xt, yt))
    M_lat = Wt * A._edge_dist(*line, (0.0, d["com"][1])) + Rb * A._edge_dist(*line, (-bc[0], bc[1]))
    hp = push_z - TABLE_Z
    res["stability_table_with_book"] = dict(analysis_py=old["stability"]["table_with_book"],
                                            model=dict(F_back_N=round(M_back / hp, 2), F_lateral_N=round(M_lat / hp, 2),
                                                       per_blade_hold_N=round(Rb, 2), push_height_mm=round(hp)))

    # in the hand: moment of everything above the hub about the hub, and blade root stress (same formulas)
    up = [r for r in rep["masses"] if r["group"] in ("unit", "stick_inner", "stick_outer", "cord")]
    m_up = sum(r["mass_g"] for r in up) / 1000
    yc = sum(r["mass_g"] * r["com"][1] for r in up) / (m_up * 1000)
    zc = sum(r["mass_g"] * r["com"][2] for r in up) / (m_up * 1000)
    L = zc - (P.HUB_TOP_Z - P.HUB_H / 2)
    tt, w = P.BLADE_T, P.BLADE_W
    Z = w * tt * tt / 6
    rows = []
    for beta in (30, 45, 60, 90):
        b = math.radians(beta)
        M = m_up * 9.81 * (L * math.sin(b) + (yc - P.STICK_Y) * math.cos(b)) / 1000
        rows.append(dict(beta=beta, moment_Nm=round(M, 3), blade_root_stress_MPa=round(M * 1000 / 2 / Z)))
    res["in_hand"] = dict(analysis_py=[r for r in old["stability"]["in_hand"] if "stick" not in r], model=rows,
                          mass_above_hub_g=round(m_up * 1000, 1), shim_yield_MPa=P.PD("shim", "yield_mpa"),
                          note="Full-hard 300-series stainless shim: yield about 965 MPa (RS PRO datasheet). Check the stock actually bought.")

    res["springs"] = old["stability"]["spring"]                  # two stock springs, from analysis.spring_check()

    # ---------------- masses
    res["mass"] = dict(model_total_g=rep["mass_total_g"], params_total_g=rep["params_total_g"],
                       model_unit_g=rep["mass_unit_g"], params_unit_g=rep["params_unit_g"], by_group=rep["budget"],
                       spec_claim_g=90, com_unit_frame_mm=rep["com_unit_in_unit_frame"])
    tubes = {r["name"]: r for r in rep["masses"] if r["name"].startswith("stick_") and r["name"].endswith("_tube")}
    v = sum(r["volume_mm3"] for r in tubes.values())
    res["mass"]["tubes_stainless_g"] = round(v / 1000 * P.RHO["steel"], 1)
    res["mass"]["tubes_if_aluminium_g"] = round(v / 1000 * P.RHO["al"], 1)

    # ---------------- fit
    res["fit"] = dict(bodies=rep["n_bodies"], collisions=rep["collisions"], pose_collisions=rep["pose_collisions"],
                      clearances_below_0p5mm=len(rep["tight_gaps"]),
                      tightest=[g for g in rep["tight_gaps"] if g["gap_mm"] <= 0.2],
                      poses={k: dict(size_mm=v["size_mm"]) for k, v in pm.items()})
    over = P.TUBE_IN_Z0 + (P.STICK_EXTENDED - STICK0)
    res["fit"]["cell_top_clearance_mm"] = round(P.UNIT_H - P.WALL - (P.CELL_Z0 + P.PD("cell", "len_max")), 1)
    res["fit"]["cell_pocket_thickness_spare_mm"] = round(P.CELL_POCKET_T - P.PD("cell", "t_max"), 1)
    res["fit"]["telescope_overlap_at_18cm_mm"] = round(P.TUBE_OUT_Z[1] - over, 1)
    res["fit"]["stowed_size_mm"] = pm["stowed"]["size_mm"]
    res["fit"]["unit_envelope_mm"] = [P.UNIT_W, P.UNIT_H, P.UNIT_D]
    res["fit"]["readme_folded_claim_mm"] = [100, 40, 35]
    res["fit_pairs"] = fit_rows(rep)
    res["cable_routes"] = route_rows(rep)

    # ---------------- wall thickness of every printed part
    res["walls"] = {n: wall_thickness(os.path.join(OUT, "stl", n + ".stl")) for n in sorted(rep["printed"])}

    res["printed_parts_filament_g"] = print_notes(rep)
    res["sources"] = sources_md(rep)
    with open(os.path.join(OUT, "check_report.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    fit_report_md(res, rep)
    diagrams(res, rep, poly, d, (cy_a, cz_a))
    short = {k: v for k, v in res.items() if k not in ("fit_pairs",)}
    print(json.dumps(short, indent=1)[:5000])
    cnt = {}
    for r in res["fit_pairs"]:
        cnt[r["verdict"]] = cnt.get(r["verdict"], 0) + 1
    print("fit pairs:", cnt)
    for r in res["fit_pairs"]:
        if r["verdict"] not in ("by design", "ok", "as designed"):
            print("  ", r["verdict"], "|", r["a"], "/", r["b"], r["gap_mm"], r["fit"])


def diagrams(res, rep, poly, d, old_com):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

    teal, marigold, ink, grey = "#2E4A52", "#D9921C", "#1E2A2E", "#9AA5A8"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    os.makedirs(DIAG, exist_ok=True)

    # ---- mass: model against the sb_params budget
    b = res["mass"]["by_group"]
    labels = [x["key"].replace("_", " ") for x in b]
    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=160)
    y = np.arange(len(b))
    ax.barh(y + 0.2, [x["params_g"] for x in b], 0.38, color=grey, label="sb_params.MASS (used by analysis.py)")
    ax.barh(y - 0.2, [x["model_g"] for x in b], 0.38, color=teal, label="3D model (volume x density, or published part mass)")
    for i, x in enumerate(b):
        if abs(x["diff_g"]) >= 1.5:
            ax.text(max(x["model_g"], x["params_g"]) + 0.6, i - 0.05, f"{x['diff_g']:+.1f} g", va="center", fontsize=9,
                    color="#A93226" if x["diff_g"] > 0 else "#1E8449")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("grams")
    ax.set_title(f"Mass: 3D model {res['mass']['model_total_g']:.0f} g, sb_params.MASS {res['mass']['params_total_g']:.0f} g "
                 f"(the product spec says about 90 g). Not weighed: estimates.", fontsize=11)
    ax.legend(loc="lower right", frameon=False)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(DIAG, "model_mass_budget.png"))
    plt.close(fig)

    # ---- stability: support polygon and centre of mass, plan and side
    s = res["stability_no_book_tripod"]
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.6), dpi=160)
    ax = axs[0]
    ax.add_patch(Polygon(poly, closed=True, fc="#DCEBEE", ec=teal, lw=1.4))
    ax.plot(0, d["com"][1], "o", color="#C0392B", ms=7)
    ax.text(4, d["com"][1], f"model CoM  ({d['mass_g']:.0f} g)", color="#C0392B", va="center", fontsize=9)
    ax.plot(0, old_com[0], "o", mfc="none", color=grey, ms=7)
    ax.text(4, old_com[0] - 9, f"analysis.py CoM ({res['mass']['params_total_g']:.0f} g)", color="#6B7B80", va="center", fontsize=9)
    ax.axhline(0, color=marigold, lw=1, ls="--")
    ax.text(-58, 3, "top edge of the book", color=marigold, fontsize=8.5)
    ax.set_aspect("equal")
    ax.set_xlim(-65, 65)
    ax.set_ylim(-125, 80)
    ax.set_xlabel("x across (mm)")
    ax.set_ylabel("y toward the reader (mm)")
    ax.set_title(f"Plan: feet and centre of mass\nnearest edge {s['model']['min_edge_dist_mm']} mm ({s['model']['weakest_edge']})",
                 fontsize=10)
    ax.grid(alpha=0.15)
    ax = axs[1]
    names = ["analysis.py\n(point masses)", "3D model\n9 cm stick", "3D model\n18 cm stick"]
    vals = [s["analysis_masses_on_model_feet"]["tip_angle_deg"], s["model"]["tip_angle_deg"], s["model_stick_extended_18cm"]["tip_angle_deg"]]
    push = [s["analysis_masses_on_model_feet"]["push_to_tip_at_unit_N"], s["model"]["push_to_tip_at_unit_N"],
            s["model_stick_extended_18cm"]["push_to_tip_at_unit_N"]]
    bars = ax.bar(names, vals, color=[grey, teal, "#6F8F98"], width=0.55)
    for bar, v, p in zip(bars, vals, push):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.3, f"{v:.1f}\N{DEGREE SIGN}\npush {p:.2f} N", ha="center", fontsize=9.5)
    ax.set_ylabel("tilt before it tips, no book (degrees)")
    ax.set_ylim(0, max(vals) * 1.35)
    ax.set_title("Free-standing tripod: how far it can lean, and the sideways\npush at the unit that tips it (estimates)", fontsize=10)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(DIAG, "model_stability.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
