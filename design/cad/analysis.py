"""SenseBook v4 tri-grip - geometry checks (coverage/dpi, page-turn clearance, grip, stability).

Run:  ..\.venv\Scripts\python.exe analysis.py
Writes design/cad/out/analysis_results.json and design/diagrams/*.png.
All results are ESTIMATES from geometry and assumed masses/lens model; nothing measured.

Lens model (ultra-wide M12 on IMX708, supplier part TBD): equidistant (f-theta)
projection r = f*phi with f chosen so the 4608 px width spans 120 deg H -> f = 2200 px
(eff. focal length ~3.08 mm at 1.4 um). This gives ~67.5 deg V and ~138 deg diagonal.
"""
import json
import math
import os

import numpy as np

import sb_params as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DIAG = os.path.join(HERE, "..", "diagrams")
os.makedirs(OUT, exist_ok=True)
os.makedirs(DIAG, exist_ok=True)

HALF_U, HALF_V = 2304.0, 1296.0
F_PX = HALF_U / math.radians(60.0)


# ------------------------------------------------------------------ camera model
def project(lens_y, lens_z, theta_deg, x, y, z=0.0):
    th = math.radians(theta_deg)
    rx, ry, rz = x, y - lens_y, z - lens_z
    zc = ry * math.sin(th) - rz * math.cos(th)
    yc = ry * math.cos(th) + rz * math.sin(th)
    xc = rx
    rho = math.hypot(xc, yc)
    phi = math.atan2(rho, zc)
    r = F_PX * phi
    if rho == 0:
        return 0.0, 0.0
    return r * xc / rho, r * yc / rho


def margin(lens_y, lens_z, theta, W, D):
    m = 9.0
    for x in np.linspace(-W / 2, W / 2, 41):
        for y in (0.0, D):
            u, v = project(lens_y, lens_z, theta, x, y)
            m = min(m, 1 - abs(u) / HALF_U, 1 - abs(v) / HALF_V)
    for y in np.linspace(0, D, 31):
        for x in (-W / 2, W / 2):
            u, v = project(lens_y, lens_z, theta, x, y)
            m = min(m, 1 - abs(u) / HALF_U, 1 - abs(v) / HALF_V)
    return m


def scales(lens_y, lens_z, theta, x, y, e=0.25):
    u0, v0 = project(lens_y, lens_z, theta, x, y)
    ux, vx = project(lens_y, lens_z, theta, x + e, y)
    uy, vy = project(lens_y, lens_z, theta, x, y + e)
    sx = math.hypot(ux - u0, vx - v0) / e * 25.4
    sy = math.hypot(uy - u0, vy - v0) / e * 25.4
    return sx, sy   # dots per inch along page-x and page-y


def best_pose(stick, W, D):
    best = None
    lo, hi = P.TIP_NOMINAL - P.TIP_RANGE, P.TIP_NOMINAL + P.TIP_RANGE
    for t10 in range(int(lo * 10), int(hi * 10) + 1, 5):
        tip = t10 / 10
        pose = P.unit_pose(stick, tip)
        ly, lz = pose["lens"]
        m = margin(ly, lz, pose["theta_from_vertical"], W, D)
        if best is None or m > best[0]:
            best = (m, tip, pose)
    return best


def dpi_report(pose, W, D):
    ly, lz = pose["lens"]
    th = pose["theta_from_vertical"]
    pts = {
        "near (top edge, centre)": (0, 0),
        "near corner (top edge, outer)": (W / 2, 0),
        "centre of spread": (0, D / 2),
        "far (reader edge, centre)": (0, D),
        "far corner (reader edge, outer)": (W / 2, D),
    }
    rep = {}
    for k, (x, y) in pts.items():
        sx, sy = scales(ly, lz, th, x, y)
        rep[k] = dict(dpi_across=round(sx), dpi_down=round(sy), dpi_min=round(min(sx, sy)),
                      squash=round(sy / sx, 2))
    return rep


def min_stick(W, D, target=0.03):
    for s in np.arange(40, 260, 2.0):
        m, tip, pose = best_pose(s, W, D)
        if m >= target:
            return float(s), tip, pose, m
    return None


# ------------------------------------------------------------------ page-turn clearance
def clearance(pose):
    hub_front = P.STICK_Y + P.HUB_D / 2
    stick_front = P.STICK_Y + P.STICK_OD_OUTER / 2
    return dict(unit_front_y=round(pose["front_y"], 1), stick_front_y=round(stick_front, 1),
                hub_front_y=round(hub_front, 1), blade_upright_y=-(P.BLADE_T + 0.1),
                unit_bottom_z=round(pose["low_z"], 1), unit_top_z=round(pose["top_z"], 1))


# ------------------------------------------------------------------ mass / stability
def com_and_masses(stick, tip):
    pose = P.unit_pose(stick, tip)
    piv_y, piv_z = pose["pivot"]
    # unit CoM ~ centroid of profile, slightly low/back because cells+Pi sit back (EST)
    uy = np.mean([p[0] for p in pose["outline"]]) - 1.5
    uz = np.mean([p[1] for p in pose["outline"]]) - 1.0
    items = [
        ("unit", P.unit_mass(), uy, uz),
        ("tilt joint", P.MASS["tilt_joint"], piv_y, piv_z),
        ("stick+cord", P.MASS["stick_tubes_cord"], P.STICK_Y, P.HUB_TOP_Z + stick / 2),
        ("hub+spring", P.MASS["hub_spring"], P.STICK_Y, P.HUB_TOP_Z - P.HUB_H / 2),
        ("blades", P.MASS["blades"], 20.0, -8.0),
        ("rear leg", P.MASS["rear_leg_pad"], P.STICK_Y - 25, -12.0),
    ]
    m = sum(i[1] for i in items)
    cy = sum(i[1] * i[2] for i in items) / m
    cz = sum(i[1] * i[3] for i in items) / m
    return items, m, cy, cz


def _support(foot_y):
    sp = math.radians(P.BLADE_SPLAY)
    xr, yr = P.BLADE_X, 0.0
    xt, yt = P.BLADE_X + P.BLADE_REACH * math.sin(sp), P.BLADE_REACH * math.cos(sp)
    fw = P.REAR_FOOT_W / 2
    return [(-fw, foot_y), (fw, foot_y), (xt, yt), (-xt, yt)], (xt, yt)


def _edge_dist(a, b, p):
    (x1, y1), (x2, y2) = a, b
    nx, ny = (y2 - y1), -(x2 - x1)
    L = math.hypot(nx, ny)
    return abs(nx * (p[0] - x1) + ny * (p[1] - y1)) / L


def tripod_nobook(stick, tip):
    """Free-standing on a table: blades swung down flat on the table (splayed),
    rear-leg T-pad behind. Table ~16 mm below the page-plane reference (EST)."""
    items, m, cy, cz = com_and_masses(stick, tip)
    z_t = -16.0
    poly, _ = _support(P.STICK_Y - 62.0)
    h = cz - z_t
    ds = [_edge_dist(poly[i], poly[(i + 1) % 4], (0.0, cy)) for i in range(4)]
    dmin = min(ds)
    unit_h = P.unit_pose(stick, tip)["top_z"] - 15 - z_t
    return dict(mass_g=round(m), com_height_mm=round(h), min_edge_dist_mm=round(dmin, 1),
                tip_angle_deg=round(math.degrees(math.atan2(dmin, h)), 1),
                push_to_tip_at_unit_N=round(m / 1000 * 9.81 * dmin / unit_h, 2),
                polygon=poly, com=(0.0, cy))


def table_with_book(stick, tip, page_block_g=150.0):
    """Book open on table; blades pinned under the page blocks (each held by ~half the
    weight of the page block above it - EST), rear T-pad on the table behind."""
    items, m, cy, cz = com_and_masses(stick, tip)
    z_t = -16.0
    foot_y = P.STICK_Y - 50.0
    poly, (xt, yt) = _support(foot_y)
    Rb = (page_block_g / 2) / 1000 * 9.81
    h_push = P.unit_pose(stick, tip)["top_z"] - 15 - z_t
    W = m / 1000 * 9.81
    bc = (P.BLADE_X + 0.5 * (xt - P.BLADE_X), 0.5 * yt)          # blade centre of pressure
    M_back = W * (cy - foot_y) + 2 * Rb * (bc[1] - foot_y)
    line = ((P.REAR_FOOT_W / 2, foot_y), (xt, yt))               # roll toward +x
    M_lat = W * _edge_dist(*line, (0.0, cy)) + Rb * _edge_dist(*line, (-bc[0], bc[1]))
    return dict(F_back_N=round(M_back / h_push, 2), F_lateral_N=round(M_lat / h_push, 2),
                per_blade_hold_N=round(Rb, 2), push_height_mm=round(h_push))


def in_hand(stick, tip, beta_deg):
    """Book held with page plane tilted beta from horizontal (top edge up).
    Gravity moment of everything above the hub about the hub, tending to tip the stick
    toward the reader (over the pages). Load path: blades bear on the covers."""
    pose = P.unit_pose(stick, tip)
    m_up = (P.unit_mass() + P.MASS["tilt_joint"] + P.MASS["stick_tubes_cord"]) / 1000
    # lever: height of upper CoM above hub along stick
    items, m, cy, cz = com_and_masses(stick, tip)
    up = [i for i in items if i[0] in ("unit", "tilt joint", "stick+cord")]
    zc = sum(i[1] * i[3] for i in up) / sum(i[1] for i in up)
    yc = sum(i[1] * i[2] for i in up) / sum(i[1] for i in up)
    L = zc - (P.HUB_TOP_Z - P.HUB_H / 2)
    b = math.radians(beta_deg)
    M = m_up * 9.81 * (L * math.sin(b) + (yc - P.STICK_Y) * math.cos(b)) / 1000   # N*m
    # per-blade root stress and free-span rotation (0.4 x 8 spring steel, free span 12 mm)
    t, w = P.BLADE_T, P.BLADE_W
    Z = w * t * t / 6
    I = w * t ** 3 / 12
    E = 193000.0
    Mb = M * 1000 / 2
    sigma = Mb / Z
    free = 12.0
    rot = math.degrees(Mb * free / (E * I))
    return dict(beta=beta_deg, moment_Nm=round(M, 3), blade_root_stress_MPa=round(sigma),
                free_span_rotation_deg=round(rot, 1))


def spring_check():
    # torsion spring: 1.0 mm music wire, 5 coils, 6 mm ID; rear-leg pad lever 45 mm
    d, Dm, N, E = 1.0, 7.0, 5, 207000.0
    k_rad = E * d ** 4 / (64 * Dm * N)          # N*mm/rad
    k_deg = k_rad * math.pi / 180
    pre = 135.0                                  # N*mm preload at closed (thin book)
    lever = 45.0
    out = []
    for open_deg in (0, 20, 40, 60):
        T = pre + k_deg * open_deg
        out.append(dict(open_deg=open_deg, torque_Nmm=round(T), pad_force_N=round(T / lever, 1)))
    return dict(k_Nmm_per_deg=round(k_deg, 2), table=out,
                squeeze_force_at_pads_N=round((pre + k_deg * 40) / 18.0, 1))


# ------------------------------------------------------------------ diagrams
def diagrams(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch

    teal, marigold, ink, grey = "#2E4A52", "#E8A317", "#1E2A2E", "#9AA5A8"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

    # ---- 1. side view: FOV + page-turn envelope + clearance
    fig, ax = plt.subplots(figsize=(13, 6.2), dpi=160)
    D = 245.0
    ax.add_patch(Rectangle((0, -12), D, 12, fc="#F3EBDD", ec="#B9A98C", lw=1))        # page block
    ax.add_patch(Rectangle((0, -15), D, 3, fc="#C9B999", ec="#B9A98C", lw=0.8))      # cover
    ax.plot([-140, 300], [-15, -15], color="#8A7A60", lw=1)                         # table
    # vertical page (worst case) + flexible page arc
    ax.add_patch(Rectangle((0, 0), D, 185, fc="#FFF6E5", ec="#C8B48A", lw=1, ls="--", alpha=0.6))
    ax.text(120, 175, "page standing upright mid-turn\n(37 cm spread: 185 mm tall)", ha="center",
            va="top", fontsize=9, color="#8A7350")
    ax.axvline(0, color="#C0392B", lw=1, ls=":")
    ax.text(2, 222, "top-edge plane (y = 0)\nturning pages stay at y >= 0", color="#C0392B", fontsize=8.5,
            va="top")
    ax.add_patch(Rectangle((-10, 0), 10, 215, fc="#F5B7B1", ec="none", alpha=0.35))
    ax.text(-11, 205, "finger\nmargin\n10 mm", ha="right", va="top", fontsize=8, color="#A93226")
    for stick, alpha, lab in ((P.STICK_COLLAPSED, 1.0, "9 cm"), (P.STICK_EXTENDED, 0.35, "18 cm")):
        tip = res["coverage"]["textbook_9cm" if stick == P.STICK_COLLAPSED else "large_18cm"]["tip_deg"]
        pose = P.unit_pose(stick, tip)
        ax.add_patch(Polygon(pose["outline"], closed=True, fc=teal, ec=ink, lw=1, alpha=alpha))
        ly, lz = pose["lens"]
        ax.plot([P.STICK_Y, P.STICK_Y], [P.HUB_TOP_Z, pose["pivot"][1]], color="#6B7B80", lw=4,
                alpha=alpha, solid_capstyle="round")
        ax.plot(*pose["pivot"], "o", color="#C9CED0", ms=5, alpha=alpha)
        th = pose["theta_from_vertical"]
        Dsp = 245.0 if stick == P.STICK_COLLAPSED else 300.0
        for edge in (th - 33.75, th + 33.75):
            a = math.radians(edge)
            t = (lz - 0) / math.cos(a)
            ax.plot([ly, ly + t * math.sin(a)], [lz, 0], color="#3E8EDE", lw=1.2, alpha=alpha)
        a0, a1 = math.radians(th - 33.75), math.radians(th + 33.75)
        ax.add_patch(Polygon([(ly, lz), (ly + lz * math.tan(a0), 0), (ly + lz * math.tan(a1), 0)],
                             fc="#3E8EDE", ec="none", alpha=0.10 * alpha))
        ax.annotate(f"lens {lz:.0f} mm above page\n({lab} stick, axis {pose['axis_below_h']:.0f}° below horiz.)",
                    xy=(ly, lz), xytext=(ly - 125, lz + 8), fontsize=8.5, alpha=max(alpha, 0.6),
                    arrowprops=dict(arrowstyle="-", color=grey, lw=0.8))
    # hub + legs (9 cm pose)
    ax.add_patch(Rectangle((P.STICK_Y - P.HUB_D / 2, P.HUB_TOP_Z - P.HUB_H), P.HUB_D, P.HUB_H,
                           fc="#3A5A63", ec=ink, lw=1))
    ax.plot([P.STICK_Y + P.HUB_D / 2, -1.0, -1.0, 70], [-4, -4, -12.5, -12.5], color="#555", lw=1.6)
    ax.text(40, -24, "blade (0.4 mm) under the pages, inside the cover", fontsize=8, ha="center")
    ax.plot([P.STICK_Y - P.HUB_D / 2, P.STICK_Y - 62], [-6, -15], color="#555", lw=2)
    ax.text(P.STICK_Y - 62, -27, "rear leg on table", fontsize=8, ha="center")
    cl = res["clearance"]["textbook_9cm"]
    ax.annotate("", xy=(cl["unit_front_y"], 60), xytext=(0, 60),
                arrowprops=dict(arrowstyle="<->", color="#C0392B", lw=1))
    ax.text(cl["unit_front_y"] / 2, 64, f"{-cl['unit_front_y']:.0f} mm", ha="center", fontsize=8.5,
            color="#C0392B")
    ax.set_xlim(-150, 300)
    ax.set_ylim(-35, 300)
    ax.set_aspect("equal")
    ax.set_xlabel("y: distance toward the reader from the book's top edge (mm)")
    ax.set_ylabel("height above page plane (mm)")
    ax.set_title("SenseBook v4 tri-grip - side view: camera cone, page-turn envelope and clearance (estimates)",
                 fontsize=11)
    ax.grid(alpha=0.15)
    fig.tight_layout()
    fig.savefig(os.path.join(DIAG, "side_geometry.png"))
    plt.close(fig)

    # ---- 2. coverage / dpi maps (top view)
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.0), dpi=160)
    for ax, key, (W, D) in ((axs[0], "textbook_9cm", (370, 245)), (axs[1], "large_18cm", (460, 300))):
        c = res["coverage"][key]
        pose = P.unit_pose(c["stick_mm"], c["tip_deg"])
        ly, lz = pose["lens"]
        th = pose["theta_from_vertical"]
        xs = np.linspace(-W / 2, W / 2, 93)
        ys = np.linspace(0, D, 62)
        Z = np.zeros((len(ys), len(xs)))
        for i, y in enumerate(ys):
            for j, x in enumerate(xs):
                sx, sy = scales(ly, lz, th, x, y)
                Z[i, j] = min(sx, sy)
        im = ax.imshow(Z, extent=(-W / 2, W / 2, D, 0), cmap="viridis", vmin=40, vmax=260, aspect="equal")
        # image boundary footprint on page plane
        bx, by = [], []
        for u, v in [(uu, -HALF_V) for uu in np.linspace(-HALF_U, HALF_U, 40)] + \
                    [(HALF_U, vv) for vv in np.linspace(-HALF_V, HALF_V, 30)] + \
                    [(uu, HALF_V) for uu in np.linspace(HALF_U, -HALF_U, 40)] + \
                    [(-HALF_U, vv) for vv in np.linspace(HALF_V, -HALF_V, 30)]:
            r = math.hypot(u, v); phi = r / F_PX
            xc, yc = (u / r * math.sin(phi), v / r * math.sin(phi)) if r else (0, 0)
            zc = math.cos(phi)
            t_ = math.radians(th)
            # camera -> world: axis a=(0,sin,-cos), yhat=(0,cos,sin)
            dx = xc
            dy = zc * math.sin(t_) + yc * math.cos(t_)
            dz = -zc * math.cos(t_) + yc * math.sin(t_)
            if dz < -1e-6:
                s = lz / -dz
                bx.append(dx * s); by.append(ly + dy * s)
        ax.plot(bx, by, color="#E74C3C", lw=1.2)
        ax.add_patch(Rectangle((-W / 2, 0), W, D, fill=False, ec="white", lw=1.5))
        ax.axvline(0, color="white", lw=0.6, ls=":")
        ax.set_xlim(-W / 2 - 60, W / 2 + 60); ax.set_ylim(D + 40, -60)
        ax.set_title(f"{W/10:.0f} x {D/10:.1f} cm spread, {c['stick_mm']/10:.0f} cm stick, lens {c['lens_height_mm']:.0f} mm\n"
                     f"margin {c['margin_pct']:.1f}% ; min dpi {c['dpi_min_overall']:.0f}", fontsize=10)
        ax.set_xlabel("x (mm)"); ax.set_ylabel("y from top edge (mm)")
        ax.plot(0, ly, "v", color=marigold, ms=8)
        fig.colorbar(im, ax=ax, shrink=0.8, label="dpi (lower of across/down)")
    fig.suptitle("Camera footprint (red) and sampling density on the page - ultra-wide f-theta model, ESTIMATE", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(DIAG, "coverage_dpi.png"))
    plt.close(fig)

    # ---- 3. stability polygons
    fig, ax = plt.subplots(figsize=(6.5, 6.5), dpi=160)
    tn = res["stability"]["tripod_no_book"]
    ax.add_patch(Polygon(tn["polygon"], closed=True, fc="#D6EAF8", ec="#2E86C1", lw=1.2))
    ax.plot(*tn["com"], "o", color="#C0392B")
    ax.text(tn["com"][0] + 3, tn["com"][1], " CoM (plan)", color="#C0392B", fontsize=9)
    ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_title(f"No-book tripod support polygon\nmin edge distance {tn['min_edge_dist_mm']} mm, "
                 f"tips at {tn['tip_angle_deg']} deg, push {tn['push_to_tip_at_unit_N']} N", fontsize=10)
    ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
    fig.tight_layout()
    fig.savefig(os.path.join(DIAG, "stability_tripod.png"))
    plt.close(fig)


def main():
    res = {"lens_model": dict(type="equidistant f-theta", f_px=round(F_PX), hfov=120.0,
                              vfov=round(2 * math.degrees(HALF_V / F_PX), 1),
                              dfov=round(2 * math.degrees(math.hypot(HALF_U, HALF_V) / F_PX), 1))}
    cov = {}
    for key, stick, (W, D) in (("textbook_9cm", P.STICK_COLLAPSED, (370, 245)),
                               ("large_18cm", P.STICK_EXTENDED, (460, 300)),
                               ("large_at_9cm", P.STICK_COLLAPSED, (460, 300)),
                               ("textbook_18cm", P.STICK_EXTENDED, (370, 245))):
        m, tip, pose = best_pose(stick, W, D)
        rep = dpi_report(pose, W, D)
        cov[key] = dict(spread_mm=(W, D), stick_mm=stick, tip_deg=tip,
                        axis_below_horizontal=round(pose["axis_below_h"], 1),
                        lens_height_mm=round(pose["lens"][1], 1), lens_setback_mm=round(-pose["lens"][0], 1),
                        margin_pct=round(100 * m, 1), points=rep,
                        dpi_min_overall=min(v["dpi_min"] for v in rep.values()))
    res["coverage"] = cov
    mins = {}
    for key, (W, D) in (("textbook_370x245", (370, 245)), ("large_460x300", (460, 300))):
        r = min_stick(W, D, 0.0)
        r3 = min_stick(W, D, 0.03)
        mins[key] = dict(zero_margin_stick_mm=r[0], zero_margin_lens_mm=round(r[2]["lens"][1]),
                         margin3_stick_mm=r3[0], margin3_lens_mm=round(r3[2]["lens"][1]))
    res["min_stick"] = mins
    res["clearance"] = {k: clearance(P.unit_pose(v["stick_mm"], v["tip_deg"])) for k, v in cov.items()
                        if k in ("textbook_9cm", "large_18cm")}
    t9 = cov["textbook_9cm"]["tip_deg"]
    res["stability"] = dict(
        mass_total_g=round(P.total_mass()), mass_unit_g=round(P.unit_mass()),
        tripod_no_book=tripod_nobook(P.STICK_COLLAPSED, t9),
        table_with_book=table_with_book(P.STICK_COLLAPSED, t9),
        in_hand=[in_hand(P.STICK_COLLAPSED, t9, b) for b in (30, 45, 60, 90)] +
                [dict(in_hand(P.STICK_EXTENDED, cov["large_18cm"]["tip_deg"], b), stick="18cm") for b in (45, 90)],
        spring=spring_check())
    with open(os.path.join(OUT, "analysis_results.json"), "w") as f:
        json.dump(res, f, indent=1)
    diagrams(res)
    print(json.dumps({k: v for k, v in res.items()}, indent=1, default=str)[:9000])


if __name__ == "__main__":
    main()
