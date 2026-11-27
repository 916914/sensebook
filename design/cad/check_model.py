"""Check the 3D model against the numbers in analysis.py.

Run after build_model.py, from design/cad:
    ..\\.venv\\Scripts\\python.exe check_model.py

Reads out/model_report.json and out/stl/*.stl, re-uses the functions in analysis.py, and writes
out/check_report.json plus two diagrams in design/diagrams/. Everything is an ESTIMATE from
geometry and assumed part masses. Nothing has been built or measured.
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
                share_at_nominal_pct=round(100 * float(((t > P.WALL - 0.15) & (t < P.WALL + 0.15)).mean()), 1),
                volume_cm3=round(float(m.volume) / 1000, 2), watertight=bool(m.is_watertight))


PRINT = [  # file stem, qty, material, how to place it on the bed, notes
    ("shell_front_tub", 1, "PETG, slate-teal", "Open back down on the bed (front face up).",
     "Supports inside for the top wall and under the lens facet; none on the visible front. 3 perimeters, 0.16 mm layers. "
     "Clean the four dot holes with a 2.4 mm drill and the lens opening with a blade."),
    ("shell_back_cover", 1, "PETG, slate-teal", "Outside face down on the bed.",
     "No supports. The four Pi posts end in 2.5 mm locating pins: check they pass the Pi holes before fitting the board."),
    ("button_ask", 1, "PETG, marigold (or paint)", "Flange down.", "The dished top prints without support. 100% infill."),
    ("button_play_pause", 1, "PETG, lighter teal", "Flange down.", "100% infill."),
    ("button_back", 1, "PETG, lighter teal", "Flange down.", "The raised arrow points away from the Ask button."),
    ("button_forward", 1, "PETG, lighter teal", "Flange down.", "Mirror of Back."),
    ("button_vol_up", 1, "PETG, lighter teal", "Flange down.", "Has the raised dot."),
    ("button_vol_down", 1, "PETG, lighter teal", "Flange down.", ""),
    ("mic_mute_slider", 1, "PETG, lighter teal", "Flat side down.", "Tiny part: print four and keep the best. Paint the flag area orange."),
    ("light_ring_diffuser", 1, "PETG, natural / clear", "Flat on the bed.", "0.12 mm layers, 100% infill so it glows evenly. Glue in with a drop of clear glue."),
    ("status_dot_pipes", 1, "PETG, natural / clear", "Standing on end.", "Four 2.4 mm pins in one file. Or cut them from 2.4 mm clear filament / acrylic rod."),
    ("tilt_joint_head", 1, "PETG", "Spigot up, tongue on the bed with support, or split and glue.", "Drill the pivot hole to 3.0 mm. 100% infill: this part carries the unit."),
    ("stick_collar", 1, "PETG", "Wide end down.", "Ream to slide on the 10 mm tube and grip the 8 mm tube lightly."),
    ("hub_body", 1, "PETG", "Top face down on the bed.", "Supports in the leg slot and the knuckle seats. Drill: stick bore 10.1 mm, leg pin 2.0 mm, knuckle pin 1.6 mm. 100% infill."),
    ("blade_knuckle_right", 1, "PETG", "Slit vertical.", "Saw or file the blade slit to 0.45 mm if it closes up. Drill 1.6 mm (pin) and 2.0 mm (clamp screw)."),
    ("blade_knuckle_left", 1, "PETG", "Slit vertical.", "Mirror of the right knuckle."),
    ("rear_leg", 1, "PETG", "Flat on its side, barrel axis vertical.", "Layers then run along the arm, which is stronger. Drill the barrel 2.0 mm."),
    ("rear_leg_pad", 1, "TPU 95A", "Flat.", "Glue to the T-foot with flexible CA or contact glue."),
]


def print_notes():
    import trimesh
    rho = {"PETG": P.RHO["petg"], "TPU": P.RHO["tpu"]}
    rows, total = [], 0.0
    for stem, qty, mat, place, note in PRINT:
        m = trimesh.load(os.path.join(OUT, "stl", stem + ".stl"))
        g = float(m.volume) / 1000 * rho["TPU" if mat.startswith("TPU") else "PETG"] * qty
        total += g
        ex = sorted((float(v) for v in m.extents), reverse=True)
        rows.append(f"| `stl/{stem}.stl` | {qty} | {mat} | {ex[0]:.0f} x {ex[1]:.0f} x {ex[2]:.0f} | {g:.1f} | {place} | {note} |")
    out = ["# SenseBook prototype: 3D-print notes", "",
           "> **Not yet printed.** These files come straight from the parametric model (`build_model.py`). Sizes and masses below are "
           "read from the STL files. Expect one or two fit iterations on the first prints, mainly holes and the cover fit.", "",
           f"Eighteen printed parts, about **{total:.0f} g of filament** in total at 100% infill (estimate; supports not counted).", "",
           "## Settings that should work", "",
           "- 0.4 mm nozzle, 0.16 mm layers for the two shells and the buttons, 0.2 mm for the rest.",
           "- PETG: 240 °C nozzle, 80 °C bed, 3 perimeters. Walls are 1.8 mm, so the shells print as solid walls.",
           "- TPU 95A for the pad: 225 °C, slow (25 mm/s), no retraction tricks needed for a flat pad.",
           "- Holes print small. Drill them to size: 1.6 mm for the M2 self-tapping screws, 2.0 mm and 1.6 mm for the hinge pins, "
           "3.0 mm for the tilt pivot, 10.1 mm for the stick.", "",
           "## Parts", "", "| File | Qty | Material | Size (mm) | Mass (g, est.) | On the bed | Notes |", "|---|---|---|---|---|---|---|"] + rows + [
           "", "## Not printed", "",
           "- **Blades:** cut from 0.4 mm 301 spring-steel shim with the `blade_flat_pattern_*.dxf` outlines (two bends each, see the "
           "assembly guide). `hardcover` has the shorter step, `thin_book` the longer one. Round and deburr every edge.",
           "- **Stick:** 10 mm and 8 mm tube, 0.5 mm wall, cut to 103.5 mm and 106.5 mm.",
           "- **Lens window:** 14 mm clear acrylic or glass disc, 0.8 to 1 mm thick. **Lens bezel:** turned or printed ring, 15 mm outside, 12.6 mm inside.",
           "- **Heat spreader:** 40 x 21 x 1 mm aluminium sheet.",
           "", "## Frames", "",
           "- Unit parts are in the unit frame from `sb_params.py` (mm): front face at y = 0, bottom at z = 0.",
           "- Stick, hub and leg parts are in the book frame: page surface z = 0, top edge of the book y = 0.",
           "- The CAD files are right-handed, so x is mirrored against `sb_params.py`: in the files, +x is the reader's left.",
           "- `SenseBook_assembly.step` holds all 88 bodies in place (hardcover pose); `step/` has one STEP per body.", ""]
    with open(os.path.join(OUT, "PRINT_NOTES.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    return round(total, 1)


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
    bezel_r = 6.3                                               # lens bezel inner radius (build_model.py)
    clear = {f"pupil_{d}mm_behind_lens_front": round(math.degrees(math.atan(bezel_r / (P.CAM_LENS_RECESS + d))), 1) for d in (1, 2, 3)}
    need_r = {f"pupil_{d}mm_behind_lens_front": round((P.CAM_LENS_RECESS + d) * math.tan(math.radians(need)), 1) for d in (1, 2, 3)}
    res["camera"] = dict(
        analysis_lens_point_mm=[round(ly, 1), round(lz, 1)], model_lens_front_mm=[round(my, 1), round(mz, 1)],
        coverage_margin_pct_analysis=round(100 * m_ref, 1), coverage_margin_pct_model=round(100 * m_model, 1),
        largest_field_angle_needed_deg=round(need, 1), bezel_inner_radius_mm=bezel_r,
        clear_half_angle_deg=clear, bezel_radius_needed_mm=need_r,
        note="Entrance-pupil depth of the M12 lens is unknown (EST 1-3 mm). If the clear half-angle is below the "
             "needed field angle the page corners are vignetted by the bezel: open the bezel or move the lens forward.")

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
    # same geometry, masses scaled to the sb_params budget (to separate "heavier" from "different shape")
    items, m_a, cy_a, cz_a = A.com_and_masses(STICK0, TIP0)
    s_budget_on_model_feet = stability(m_a, cy_a, cz_a, poly, push_z)
    de = pm["extended"]
    pose_e = P.unit_pose(P.STICK_EXTENDED, 14.5)
    s_ext = stability(de["mass_g"], de["com"][1], de["com"][2] , poly, pose_e["top_z"] - 15)
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
                          mass_above_hub_g=round(m_up * 1000, 1),
                          note="301 full-hard spring steel yields at roughly 1,000-1,200 MPa (EST, check the stock used).")

    # ---------------- masses
    res["mass"] = dict(model_total_g=rep["mass_total_g"], params_total_g=rep["params_total_g"],
                       model_unit_g=rep["mass_unit_g"], params_unit_g=rep["params_unit_g"], by_group=rep["budget"],
                       spec_claim_g=90, com_unit_frame_mm=rep["com_unit_in_unit_frame"],
                       analysis_unit_com_assumption="profile centroid shifted (-1.5, -1.0) mm")
    tubes = {r["name"]: r for r in rep["masses"] if r["name"].startswith("stick_") and r["name"].endswith("_tube")}
    v = sum(r["volume_mm3"] for r in tubes.values())
    res["mass"]["tubes_stainless_g"] = round(v / 1000 * P.RHO["steel"], 1)
    res["mass"]["tubes_if_aluminium_g"] = round(v / 1000 * P.RHO["al"], 1)

    # ---------------- fit
    res["fit"] = dict(bodies=rep["n_bodies"], collisions=rep["collisions"], pose_collisions=rep["pose_collisions"],
                      clearances_below_0p5mm=len(rep["tight_gaps"]),
                      tightest=[g for g in rep["tight_gaps"] if g["gap_mm"] <= 0.2],
                      poses={k: dict(size_mm=v["size_mm"]) for k, v in pm.items()})
    cell_len_room = P.UNIT_H - 2 * P.WALL - P.CELL[2]
    over = P.TUBE_IN_Z0 + (P.STICK_EXTENDED - STICK0)
    res["fit"]["cell_end_clearance_mm"] = round(cell_len_room, 1)
    res["fit"]["telescope_overlap_at_18cm_mm"] = round(P.TUBE_OUT_Z[1] - over, 1)
    res["fit"]["stowed_size_mm"] = pm["stowed"]["size_mm"]
    res["fit"]["readme_folded_claim_mm"] = [100, 40, 35]

    # ---------------- wall thickness of the printed shells
    res["walls"] = {n: wall_thickness(os.path.join(OUT, "stl", n + ".stl")) for n in
                    ("shell_front_tub", "shell_back_cover", "hub_body", "rear_leg")}

    res["printed_parts_filament_g"] = print_notes()
    with open(os.path.join(OUT, "check_report.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    diagrams(res, rep, poly, d, (cy_a, cz_a))
    print(json.dumps(res, indent=1)[:6000])


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
    ax.barh(y + 0.2, [x["params_g"] for x in b], 0.38, color=grey, label="sb_params budget (estimate)")
    ax.barh(y - 0.2, [x["model_g"] for x in b], 0.38, color=teal, label="3D model (volume x density, or typical part mass)")
    for i, x in enumerate(b):
        if abs(x["diff_g"]) >= 1.5:
            ax.text(max(x["model_g"], x["params_g"]) + 0.6, i - 0.05, f"{x['diff_g']:+.1f} g", va="center", fontsize=9,
                    color="#A93226" if x["diff_g"] > 0 else "#1E8449")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("grams")
    ax.set_title(f"Mass: 3D model {res['mass']['model_total_g']:.0f} g against the {res['mass']['params_total_g']:.0f} g budget "
                 f"(product spec says about 90 g). All figures are estimates.", fontsize=11)
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
    ax.text(4, old_com[0] - 9, "analysis.py CoM (137 g)", color="#6B7B80", va="center", fontsize=9)
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
    names = ["analysis.py\n(137 g budget)", "3D model\n9 cm stick", "3D model\n18 cm stick"]
    vals = [s["analysis_py"]["tip_angle_deg"], s["model"]["tip_angle_deg"], s["model_stick_extended_18cm"]["tip_angle_deg"]]
    push = [s["analysis_py"]["push_to_tip_at_unit_N"], s["model"]["push_to_tip_at_unit_N"],
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
