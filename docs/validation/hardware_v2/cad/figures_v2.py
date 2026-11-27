"""Figures for the SenseBook hardware v2 proposal page, redrawn from the model's own outputs.

Reads out/model_report_v2.json (written by build_v2.py) and data/bom_v2_estimate.csv; writes web/figures/*.svg.
The maps are recomputed here from the saved camera and LED models, as a second, independent check of the numbers
build_v2.py prints. All figures are estimates from geometry and datasheet figures; nothing has been measured.

    python docs/validation/hardware_v2/cad/figures_v2.py
"""
import csv
import json
import math
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt                       # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "out", "model_report_v2.json")))
FIG = os.path.join(ROOT, "web", "figures")
os.makedirs(FIG, exist_ok=True)

INK, INK2, MUTED, LINE, SURF = "#1b2528", "#46555a", "#5b6b70", "#d9e1e2", "#ffffff"
plt.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": LINE, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlecolor": INK, "svg.fonttype": "none",
                     "axes.spines.top": False, "axes.spines.right": False, "text.parse_math": False})

SPX, SPY = R["page"]["spread_mm"][0] / 2, R["page"]["spread_mm"][1]
MG = R["page"]["text_margin_mm"]
WPX, HPX = R["page"]["sensor_px"]


# ---------------------------------------------------------------- camera models
def project(c, x, y):
    p, X, Y, Z = (np.array(c[k]) for k in ("p", "X", "Y", "Z"))
    v = np.stack([x - p[0], y - p[1], -p[2] * np.ones_like(x)], -1)
    xc, yc, zc = v @ X, v @ Y, v @ Z
    u, w = c["f_px"] * xc / yc, c["f_px"] * zc / yc
    k = 1 + c["distortion"] * (u * u + w * w) / ((WPX / 2) ** 2 + (HPX / 2) ** 2)     # radial lens distortion
    u, w = u * k, w * k
    ok = (yc > 0) & (np.abs(u) <= WPX / 2) & (np.abs(w) <= HPX / 2)
    return u, w, ok


def dpi(c, x, y, d=0.5):
    # central differences (symmetric, so mirrored cameras give mirrored numbers)
    ua, wa, oka = project(c, x - d / 2, y)
    ub, wb, okb = project(c, x + d / 2, y)
    uc, wc, okc = project(c, x, y - d / 2)
    ue, we, oke = project(c, x, y + d / 2)
    s = np.minimum(np.hypot(ub - ua, wb - wa), np.hypot(ue - uc, we - wc)) / d * 25.4
    return np.where(oka & okb & okc & oke, s, 0.0)


def v1_dpi(x, y, d=0.5):
    """v1: one 12 MP IMX708 (4608 px wide) behind a 120 deg M12 lens, modelled as f-theta (f = 2200 px), lens 116.2 mm
    above the page and 26.4 mm behind its top edge, axis 55.5 deg below horizontal (build chat's analysis [D1])."""
    pos = np.array([0.0, -26.4, 116.2])
    a = math.radians(55.5)
    fwd = np.array([0, math.cos(a), -math.sin(a)]); right = np.array([1.0, 0, 0]); up = np.cross(right, fwd)

    def proj(px, py):
        v = np.stack([px - pos[0], py - pos[1], -pos[2] * np.ones_like(px)], -1)
        vx, vy, vz = v @ right, v @ up, v @ fwd
        th = np.arccos(vz / np.linalg.norm(v, axis=-1)); ph = np.arctan2(vy, vx)
        return 2200.0 * th * np.cos(ph), 2200.0 * th * np.sin(ph)
    u0, w0 = proj(x, y); u1, w1 = proj(x + d, y); u2, w2 = proj(x, y + d)
    return np.minimum(np.hypot(u1 - u0, w1 - w0), np.hypot(u2 - u0, w2 - w0)) / d * 25.4


cams = R["cameras_model"]
names = list(cams)
xs = np.linspace(-SPX + 1, SPX - 1, 185)
ys = np.linspace(1, SPY - 1, 123)
GX, GY = np.meshgrid(xs, ys)
stack = np.stack([dpi(cams[n], GX.ravel(), GY.ravel()) for n in names])
V2 = stack.max(0).reshape(GX.shape)
OWN = stack.argmax(0).reshape(GX.shape)
V1 = v1_dpi(GX.ravel(), GY.ravel()).reshape(GX.shape)
in_text = ((np.abs(GX) >= MG["gutter"]) & (np.abs(GX) <= SPX - MG["outer"]) & (GY >= MG["top"]) & (GY <= SPY - MG["bottom"]))
# the text-area minimum on a fine grid that includes the text-area edges exactly
tx = np.r_[np.linspace(-SPX + MG["outer"], -MG["gutter"], 60), np.linspace(MG["gutter"], SPX - MG["outer"], 60)]
ty = np.linspace(MG["top"], SPY - MG["bottom"], 80)
TX, TY = [a.ravel() for a in np.meshgrid(tx, ty)]
v2_text_min = float(np.max(np.stack([dpi(cams[n], TX, TY) for n in names]), 0).min())
v1_text_min = float(v1_dpi(TX, TY).min())
v2_page_min = float(V2.min())
_left = TX < 0
v2_same_side_min = float(min(
    np.maximum(dpi(cams["far_left"], TX[_left], TY[_left]), dpi(cams["near_left"], TX[_left], TY[_left])).min(),
    np.maximum(dpi(cams["far_right"], TX[~_left], TY[~_left]), dpi(cams["near_right"], TX[~_left], TY[~_left])).min()))

bounds = [0, 150, 225, 300, 400, 600, 2000]
cmap = ListedColormap(["#c23b36", "#e57a72", "#f4c2bd", "#b7d3f6", "#5598e7", "#1c5cab"])
norm = BoundaryNorm(bounds, cmap.N)
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.1), constrained_layout=True)
for ax, M, title, lo in [(axs[0], V1, "v1: one 12 MP camera, 120° lens", v1_text_min),
                         (axs[1], V2, "v2: four 50 MP cameras on the lens facet", v2_text_min)]:
    im = ax.pcolormesh(xs / 10, ys / 10, M, cmap=cmap, norm=norm, shading="auto", rasterized=True)
    ax.contour(xs / 10, ys / 10, M, levels=[300], colors=INK, linewidths=1.0)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * MG["gutter"] / 10, sx * (SPX - MG["outer"]) / 10))
        ax.add_patch(plt.Rectangle((x0, MG["top"] / 10), x1 - x0, (SPY - MG["top"] - MG["bottom"]) / 10, fill=False,
                                   ec=INK, lw=0.8, ls=(0, (3, 2))))
    if M is V2:
        for k in range(len(names)):
            ax.contour(xs / 10, ys / 10, (OWN == k).astype(float), levels=[0.5], colors="white", linewidths=0.9)
    ax.set_title(title, loc="left", fontsize=10)
    ax.set_aspect("equal"); ax.invert_yaxis()
    ax.set_xlabel("across the open book (cm), spine at 0")
    ax.set_ylabel("down the page (cm), 0 = top edge (device side)")
    ax.axvline(0, color="white", lw=0.8)
    ax.text(-SPX / 10 + 0.4, SPY / 10 - 0.6, f"lowest on the printed text: {lo:.0f} dpi", fontsize=9, color=INK, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=LINE))
cb = fig.colorbar(im, ax=axs, shrink=0.9, ticks=bounds[:-1])
cb.set_label("dpi on the page, worst direction (300 = black line)")
cb.ax.tick_params(labelsize=8)
fig.savefig(os.path.join(FIG, "dpi_v1_v2.svg"), facecolor=SURF)
fig.savefig(os.path.join(FIG, "dpi_v1_v2.png"), facecolor=SURF, dpi=130)
plt.close(fig)

# ---------------------------------------------------------------- light
L = R["light_model"]
leds, aims, cd = np.array(L["leds_book_mm"]), np.array(L["aims"]), np.array(L["cd"])


def lux(px, py):
    E = np.zeros_like(px)
    for p, (tx_, ty_, half), I in zip(leds, aims, cd):
        a = np.array([tx_, ty_, 0.0]) - p; a /= np.linalg.norm(a)
        V = np.stack([px - p[0], py - p[1], -p[2] * np.ones_like(px)], -1)
        d = np.linalg.norm(V, axis=-1); U = V / d[..., None]
        m = math.log(0.5) / math.log(math.cos(math.radians(half)))
        E += I * np.clip(U @ a, 0, 1) ** m * (p[2] / d) / (d / 1000.0) ** 2
    return E


LX = lux(GX, GY)
lt = lux(TX, TY)
lb = [0, 150, 300, 450, 600, 750, 5000]
lcm = ListedColormap(["#f3f1ec", "#f6dcc0", "#f1b77e", "#e48b43", "#c2621d", "#8a4410"])
fig, ax = plt.subplots(figsize=(7.0, 4.0), constrained_layout=True)
im = ax.pcolormesh(xs / 10, ys / 10, LX, cmap=lcm, norm=BoundaryNorm(lb, lcm.N), shading="auto", rasterized=True)
for sx in (-1, 1):
    x0, x1 = sorted((sx * MG["gutter"] / 10, sx * (SPX - MG["outer"]) / 10))
    ax.add_patch(plt.Rectangle((x0, MG["top"] / 10), x1 - x0, (SPY - MG["top"] - MG["bottom"]) / 10, fill=False, ec=INK, lw=0.8,
                               ls=(0, (3, 2))))
ax.set_aspect("equal"); ax.invert_yaxis(); ax.axvline(0, color="white", lw=0.8)
ax.set_title(f"v2 light bar: {len(leds)} LEDs, each aimed at its own patch of the page", loc="left", fontsize=10)
ax.set_xlabel("across the open book (cm), spine at 0"); ax.set_ylabel("down the page (cm)")
ax.text(-SPX / 10 + 0.4, SPY / 10 - 0.6, f"printed text: {lt.min():.0f} to {lt.max():.0f} lux", fontsize=9, color=INK, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=LINE))
cb = fig.colorbar(im, ax=ax, shrink=0.9, ticks=lb[:-1]); cb.set_label("lux on the page (target 300 to 750)")
fig.savefig(os.path.join(FIG, "light_v2.svg"), facecolor=SURF)
fig.savefig(os.path.join(FIG, "light_v2.png"), facecolor=SURF, dpi=130)
plt.close(fig)

# ---------------------------------------------------------------- battery
B = R["battery"]
chem = [("generic_lipo", "Standard Li-po\n460 Wh/L"), ("high_voltage_4v45", "4.45 V cell\n600 Wh/L"),
        ("silicon_carbon", "Silicon-carbon\n800 Wh/L")]
fig, axs = plt.subplots(1, 2, figsize=(9.6, 2.9), constrained_layout=True, sharey=True)
for ax, key, target, title in [(axs[0], "light_off", 10, "Light off: target 10 h"), (axs[1], "light_on", 8, "Light on: target 8 h")]:
    for i, (k, lab) in enumerate(chem):
        lo, hi = B["hours"][k][key]
        ax.barh(i, hi - lo, left=lo, height=0.42, color="#2a78d6" if lo >= target else "#86b6ef", edgecolor="none")
        ax.text(hi + 0.4, i, f"{lo:.1f} to {hi:.1f} h", va="center", fontsize=8.5, color=INK)
    ax.axvline(target, color=INK, lw=1.0, ls=(0, (3, 2)))
    ax.text(target + 0.25, -0.8, f"target {target} h", ha="left", va="center", fontsize=8, color=INK)
    ax.set_yticks(range(len(chem))); ax.set_yticklabels([c[1] for c in chem])
    ax.set_xlim(0, max(B["hours"]["silicon_carbon"][key][1] + 9, target + 10))
    ax.set_ylim(len(chem) - 0.5, -1.0)
    ax.set_title(title, loc="left", fontsize=10); ax.set_xlabel("hours of reading (worst to best estimate)")
    ax.grid(axis="x", color=LINE, lw=0.6); ax.set_axisbelow(True)
fig.suptitle(f"Battery: {B['cell_volume_cm3']:.1f} cm³ of cells in the same head (v1: {B['v1_cell_volume_cm3']} cm³). "
             "Dark bar = meets the target even in the worst case.", x=0.01, ha="left", fontsize=9, color=INK2)
fig.savefig(os.path.join(FIG, "battery_v2.svg"), facecolor=SURF)
fig.savefig(os.path.join(FIG, "battery_v2.png"), facecolor=SURF, dpi=130)
plt.close(fig)

# ---------------------------------------------------------------- cost
rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "bom_v2_estimate.csv"), encoding="utf-8")))
blk = {}
for r in rows:
    q = int(r["qty"]); lo_, hi_ = blk.get(r["block"], (0.0, 0.0))
    blk[r["block"]] = (lo_ + q * float(r["unit_low_usd"]), hi_ + q * float(r["unit_high_usd"]))
order = sorted(blk, key=lambda k: blk[k][1])
tot = (sum(v[0] for v in blk.values()), sum(v[1] for v in blk.values()))
fig, ax = plt.subplots(figsize=(7.6, 3.4), constrained_layout=True)
for i, k in enumerate(order):
    lo_, hi_ = blk[k]
    ax.barh(i, hi_ - lo_, left=lo_, height=0.5, color="#2a78d6", edgecolor="none")
    ax.text(hi_ + 1.2, i, f"${lo_:.0f} to ${hi_:.0f}", va="center", fontsize=8.5, color=INK)
ax.set_yticks(range(len(order))); ax.set_yticklabels(order)
ax.set_xlim(0, max(v[1] for v in blk.values()) + 22)
ax.grid(axis="x", color=LINE, lw=0.6); ax.set_axisbelow(True)
ax.set_xlabel("US$ per unit at about 1,000 units (estimate, low to high)")
ax.set_title(f"Parts cost estimate: ${tot[0]:.0f} to ${tot[1]:.0f} per unit", loc="left", fontsize=10)
fig.savefig(os.path.join(FIG, "cost_v2.svg"), facecolor=SURF)
fig.savefig(os.path.join(FIG, "cost_v2.png"), facecolor=SURF, dpi=130)
plt.close(fig)

summary = dict(v1_text_min_dpi=round(v1_text_min), v2_text_min_dpi=round(v2_text_min), v2_page_min_dpi=round(v2_page_min), v2_same_side_text_min_dpi=round(v2_same_side_min),
               v2_text_lux=[round(float(lt.min())), round(float(lt.max()))], cost_usd=[round(tot[0]), round(tot[1])],
               cost_by_block={k: [round(v[0], 1), round(v[1], 1)] for k, v in blk.items()})
json.dump(summary, open(os.path.join(ROOT, "out", "figures_summary.json"), "w"), indent=1)
print(json.dumps(summary))
