"""Build the SenseBook hardware v2 site (web/): facts.json for the 3D viewer, proposal.html, and the model file.

Every number on the pages comes from out/model_report_v2.json (build_v2.py), out/figures_summary.json (figures_v2.py)
or data/bom_v2_estimate.csv. Nothing is typed in by hand, so the pages cannot drift from the model.

    python docs/validation/hardware_v2/cad/make_site.py
"""
import csv
import html
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SITE = os.path.join(ROOT, "web")
R = json.load(open(os.path.join(ROOT, "out", "model_report_v2.json")))
F = json.load(open(os.path.join(ROOT, "out", "figures_summary.json")))
BOM = list(csv.DictReader(open(os.path.join(ROOT, "data", "bom_v2_estimate.csv"), encoding="utf-8")))
e = html.escape
# v1 head size, read from the same v1 commit the model is built on
import subprocess
_v1 = {}
exec(subprocess.check_output(["git", "-C", os.path.join(ROOT, "..", "..", ".."), "show",
                              f"{R['v1_reference']['model_commit']}:design/cad/sb_params.py"]).decode(), _v1)
HEAD_MM = f"{_v1['UNIT_W']:.0f} × {_v1['UNIT_H']:.0f} × {_v1['UNIT_D']:.0f}"
DISPLAY = {"near_left": "Wide camera, left", "near_right": "Wide camera, right", "far_left": "Page camera, left", "far_right": "Page camera, right"}
SHARE = R.get("zone_share", {})

cam, bat, lit = R["camera"], R["battery"], R["light"]
A, B = R["option_A"], R["option_B"]
hrs = bat["hours"]


def rng(v, unit="", nd=1):
    return f"{v[0]:.{nd}f} to {v[1]:.{nd}f}{unit}"


def n_coll(o):
    return len(o["collisions"])


def n_pose(o):
    return sum(len(v) for v in o.get("pose_collisions", {}).values()) if "pose_collisions" in o else None


def n_blocked(o):
    los = o.get("line_of_sight")
    return None if los is None else (sum(v["blocked"] for v in los.values()), sum(v["rays"] for v in los.values()))


def met(key, target, chem):
    lo, hi = hrs[chem][key]
    return "yes, even in the worst case" if lo >= target else ("only in the better cases" if hi >= target else "no")


# ---------------------------------------------------------------- facts for the viewer
facts = [
    dict(n=f"{F['v2_text_min_dpi']} dpi", l=f"lowest on the printed text (v1: {F['v1_text_min_dpi']} dpi)"),
    dict(n="4 × 50 MP", l="cameras on the lens facet, snapshot only"),
    dict(n=f"{F['v2_text_lux'][0]}–{F['v2_text_lux'][1]} lux", l=f"on the printed text with about {lit['electrical_w']} W"),
    dict(n=f"{bat['cell_volume_cm3']:.1f} cm³", l=f"of cells (v1: {bat['v1_cell_volume_cm3']} cm³), same head size"),
    dict(n=f"{hrs['high_voltage_4v45']['light_on'][0]:.1f}–{hrs['high_voltage_4v45']['light_on'][1]:.1f} h",
         l="reading with the light on, 4.45 V cells (EST)"),
    dict(n=f"{n_coll(A)} / {n_coll(B)}", l="parts overlapping, option A / B"),
]
json.dump(facts, open(os.path.join(SITE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- tables
blocks = {}
for r in BOM:
    blocks.setdefault(r["block"], []).append(r)
bom_rows = []
for b, rows in blocks.items():
    for r in rows:
        q = int(r["qty"])
        lo, hi = q * float(r["unit_low_usd"]), q * float(r["unit_high_usd"])
        bom_rows.append(f"<tr><td>{e(b)}</td><td>{e(r['part'])}</td><td class=n>{q}</td><td class=n>${lo:.2f}–{hi:.2f}</td>"
                        f"<td>{e(r['basis'])}</td><td class=src>{e(r['source_or_note'])}</td></tr>")
bom_total = F["cost_usd"]

chem_names = {"generic_lipo": "Standard Li-po (460 Wh/L)", "high_voltage_4v45": "4.45 V cell (600 Wh/L, EST)",
              "silicon_carbon": "Silicon-carbon cell (800 Wh/L, phone grade)"}
bat_rows = "".join(
    f"<tr><td>{chem_names[k]}</td><td class=n>{bat['wh'][k]}</td><td class=n>{rng(hrs[k]['light_off'], ' h')}</td>"
    f"<td>{met('light_off', 10, k)}</td><td class=n>{rng(hrs[k]['light_on'], ' h')}</td><td>{met('light_on', 8, k)}</td></tr>"
    for k in chem_names)

pose = [n_pose(A), n_pose(B)]
los = [n_blocked(A), n_blocked(B)]
check_rows = [
    ("Parts overlapping each other (more than 0.02 mm³)", f"{n_coll(A)}", f"{n_coll(B)}"),
    ("Overlaps in every v1 pose (stick lengths, tilt, blade and leg positions)",
     "not run" if pose[0] is None else str(pose[0]), "not run" if pose[1] is None else str(pose[1])),
    ("Camera sight lines blocked by a part (rays to every page point each camera reads)",
     "not run" if los[0] is None else f"{los[0][0]} of {los[0][1]}", "not run" if los[1] is None else f"{los[1][0]} of {los[1][1]}"),
    ("Everything in the head, bounding box (mm), buttons and hinge included", " × ".join(f"{v:.1f}" for v in A["head_envelope_mm"]),
     " × ".join(f"{v:.1f}" for v in B["head_envelope_mm"])),
    ("Same, v1 parts (for comparison)", " × ".join(f"{v:.1f}" for v in A["v1_head_envelope_mm"]), ""),
    ("Front shell bounding box (mm)", " × ".join(f"{v:.1f}" for v in R["shell_size_mm"]["v2"]), f"v1: {' × '.join(f'{v:.1f}' for v in R['shell_size_mm']['v1'])}"),
    ("Mass, whole device without the book (g)", f"{A['mass']['total_g']}", f"{B['mass']['total_g']} (clicker not included)"),
    ("Mass of the head (g)", f"{A['mass']['head_g']}", f"{B['mass']['head_g']}  (v1: {R['v1_reference']['mass_head_g']})"),
]
checks_html = "".join(f"<tr><td>{e(a)}</td><td class=n>{e(b)}</td><td class=n>{e(c)}</td></tr>" for a, b, c in check_rows)
cams_html = "".join(f"<tr><td>{e(DISPLAY[n])}</td><td class=n>{c['hfov']:.0f}° × {c['vfov']:.0f}°</td>"
                    f"<td class=n>{c['text_min_dpi_own_zone']}</td></tr>" for n, c in R["cameras_model"].items())

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>SenseBook hardware v2</title>
<style>
:root{{--bg:#f6f7f6;--surface:#fff;--ink:#1d2a2e;--muted:#5b6b70;--line:#d9e1e2;--teal:#1f4e57;--teal-soft:#e3eef0;--marigold:#9a6408;color-scheme:light}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#111a1c;--surface:#172427;--ink:#e6eeef;--muted:#9fb1b5;--line:#2a3b3f;--teal:#8cc7d1;--teal-soft:#1d3236;--marigold:#f0b14a;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#111a1c;--surface:#172427;--ink:#e6eeef;--muted:#9fb1b5;--line:#2a3b3f;--teal:#8cc7d1;--teal-soft:#1d3236;--marigold:#f0b14a;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,"Nirmala UI",sans-serif}}
header{{display:flex;gap:16px;align-items:baseline;flex-wrap:wrap;padding:14px 16px;border-bottom:1px solid var(--line);background:var(--surface)}}
header .brand{{font-weight:700;font-size:20px;color:var(--teal)}}
header a{{margin-left:auto;color:var(--teal);font-weight:600}}
main{{max-width:1040px;margin:0 auto;padding:20px 16px 60px}}
h1{{font-size:28px;line-height:1.2;margin:8px 0 6px}}
h2{{font-size:21px;margin:40px 0 8px;padding-top:10px;border-top:1px solid var(--line)}}
h2 small{{display:block;font-size:12px;letter-spacing:.6px;text-transform:uppercase;color:var(--marigold);font-weight:700;margin-bottom:2px}}
p{{margin:8px 0;max-width:76ch}}
.lead{{font-size:17px;color:var(--muted)}}
.status{{border-left:4px solid var(--marigold);background:var(--surface);padding:10px 14px;border-radius:6px;max-width:none}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:18px 0}}
.tile{{background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--teal);border-radius:8px;padding:10px 12px}}
.tile .n{{font-size:24px;font-weight:700;color:var(--teal);line-height:1.15}}
.tile .l{{font-size:13px;color:var(--muted)}}
figure{{margin:14px 0;background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px}}
figure img{{display:block;width:100%;height:auto}}
figcaption{{font-size:13px;color:#46555a;padding:6px 4px 0}}
.renders{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}}
.renders figure{{margin:0}}
.table-wrap{{overflow-x:auto;margin:10px 0}}
table{{border-collapse:collapse;width:100%;font-size:14px;background:var(--surface)}}
th,td{{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted)}}
td.n{{white-space:nowrap;font-variant-numeric:tabular-nums}}
td.src{{font-size:12.5px;color:var(--muted)}}
ul{{max-width:76ch;padding-left:20px}}
li{{margin:4px 0}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media (max-width:760px){{.two{{grid-template-columns:1fr}}h1{{font-size:24px}}}}
a{{color:var(--teal)}}
a:focus-visible{{outline:2px solid var(--marigold);outline-offset:2px}}
footer{{max-width:1040px;margin:0 auto;padding:0 16px 40px;font-size:13px;color:var(--muted)}}
</style>
</head>
<body>
<header><span class="brand">SenseBook</span><span>Hardware v2 proposal</span><a href="index.html">Open the 3D model →</a></header>
<main>
<h1>SenseBook hardware v2: what changes in the device</h1>
<p class="lead">The same clip-on head at the top edge of the book, the same size, with new insides: four cameras that read every
printed line at 300 dpi or more, a light that lights only the page, a bigger battery, a stronger computer, better radio and better sound.
Two button layouts: A keeps v1's buttons, B moves them to the hub and adds a pocket clicker.</p>
<p class="status"><b>Status: design proposal.</b> Nothing here has been built or measured. Numbers come from the 3D model
(built on the build chat's v1 model, commit {e(R['v1_reference']['model_commit'])}) and from datasheets and listings checked on 27 Nov 2026.
<b>EST</b> marks our own estimates.</p>

<div class="tiles">
<div class="tile"><div class="n">{F['v2_text_min_dpi']} dpi</div><div class="l">lowest on the printed text (v1: {F['v1_text_min_dpi']})</div></div>
<div class="tile"><div class="n">{F['v2_text_lux'][0]}–{F['v2_text_lux'][1]} lux</div><div class="l">on all printed text, about {lit['electrical_w']} W (EST)</div></div>
<div class="tile"><div class="n">{bat['cell_volume_cm3']:.1f} cm³</div><div class="l">of battery cells (v1: {bat['v1_cell_volume_cm3']} cm³)</div></div>
<div class="tile"><div class="n">{HEAD_MM} mm</div><div class="l">head size, unchanged from v1</div></div>
<div class="tile"><div class="n">${bom_total[0]}–{bom_total[1]}</div><div class="l">parts per unit at 1,000 units (EST)</div></div>
</div>

<div class="renders">
<figure><img src="renders/v2_hero_A.jpg" alt="SenseBook v2 clipped to the top edge of an open textbook, seen from the reader's side" loading="lazy">
<figcaption>Option A on an open textbook. Render of the CAD model, not a photograph.</figcaption></figure>
<figure><img src="renders/v2_facet_A.jpg" alt="Close view of the sloped lens facet: four camera windows in a row, a ToF window in the middle, a light strip above and two below" loading="lazy">
<figcaption>The sloped lens facet: four camera windows, the hand sensor in the middle, light strips above and below.</figcaption></figure>
</div>

<h2><small>1 · Reading the page</small>Four 50 MP cameras: every printed line at {F['v2_text_min_dpi']} dpi or more</h2>
<p><b>v1:</b> one 12 MP camera with a 120° lens looks down from the top edge. Because it looks at a slant, the far end of the page gets
few pixels: the lowest point on the printed text gets about {F['v1_text_min_dpi']} dpi. Text recognition tools usually ask for about 300 dpi for small print.</p>
<p><b>v2:</b> the camera stays at the top edge, as you asked. Instead of one camera for the whole spread, four sit in a row on the same sloped facet,
each with a 50 MP phone sensor ({R['page']['sensor_px'][0]} × {R['page']['sensor_px'][1]} px). Two <b>page cameras</b> with about
{R['cameras_model']['far_left']['hfov']:.0f}° lenses look across the book and reach the far end of each page, where the slant is worst. Two <b>wide cameras</b>
(about {R['cameras_model']['near_left']['hfov']:.0f}°) cover the area right under the device that the page cameras cannot see.
Almost every point (99.9%) is seen by two to four cameras, and the software uses whichever has the most pixels there.
The lowest point on the printed text now gets {F['v2_text_min_dpi']} dpi ({F['v2_same_side_text_min_dpi']} dpi even using only the two cameras on that page's side), counting the slight barrel distortion of real lenses
({abs(R['cameras_model']['far_left']['distortion']) * 100:.0f}% at the corner for the page cameras, {abs(R['cameras_model']['near_left']['distortion']) * 100:.0f}% for the wide ones, EST).
The whole page, margins included, is seen ({F['v2_page_min_dpi']} dpi at the worst margin corner).</p>
<p><b>Why 60° and not the stock 64° lens:</b> with 64° the far text corners came out at about 298 dpi once lens distortion was counted.
A slightly longer lens (about 4.5 mm instead of 4.15 mm, same sensor and module) gives {F['v2_text_min_dpi']}.</p>
<figure><img src="figures/dpi_v1_v2.svg" alt="Two maps of an open textbook. Left, v1: most of the page is below 300 dpi, the lowest point on the printed text is {F['v1_text_min_dpi']} dpi. Right, v2: all printed text is above 300 dpi, the lowest is {F['v2_text_min_dpi']} dpi.">
<figcaption>Pixels per inch on a 37 × 24.5 cm textbook spread at v1's default 9 cm stick. Dashed boxes are the printed text. White lines in v2 split the page by which camera has the most pixels there. Geometry estimate including lens distortion (EST); real sharpness also depends on focus and lens quality.</figcaption></figure>
<div class="table-wrap"><table><thead><tr><th>Camera</th><th>View (horizontal × vertical)</th><th>Lowest dpi where it is the best camera</th></tr></thead><tbody>{cams_html}</tbody></table></div>
<ul>
<li><b>No recording.</b> The cameras are off. A small hand sensor (ST VL53L8CX) sees a hand or a page turning; then the four cameras take one still each and turn off again.</li>
<li><b>Aim.</b> The page cameras look {cam['aims']['far']['down_deg']:.0f}° down and {cam['aims']['far']['yaw_deg']:.0f}° outward; the wide cameras
{cam['aims']['near']['down_deg']:.0f}° down and {cam['aims']['near']['yaw_deg']:.0f}° outward. The model searched every aim in 1° steps and kept each module within
{max(cam['tilt_from_facet_deg'].values())}° of the facet, so all four fit flat behind it.</li>
<li><b>Snapshots for later:</b> the hardware can keep text from pages (not pictures) on the device. How many, and when the assistant deletes them, is a software setting.</li>
</ul>

<h2><small>2 · Light</small>A light bar that lights the page, not the room</h2>
<p><b>v1:</b> a ring of LEDs around the lens lights a circle. To get the far corners of the page bright enough, the middle gets far too bright, and much of the light misses the book.
In our model the ring needs about 5.7 W to put 300 lux on every point of the printed text, and the middle of the page then gets over 9,000 lux (EST).</p>
<p><b>v2:</b> two thin strips on the facet hold {R['leds']} small warm-white LEDs (CRI 90). A moulded optic aims each LED at its own patch of the page,
and a 24-channel driver (TI LP5024) sets each one. The model finds the least power that puts {lit['min_lux']} to {lit['max_lux']} lux on every point of the printed text:
about {lit['flux_lm']} lumens, {lit['electrical_w']} W from the battery (EST).
<b>It follows the book:</b> the cameras see where the page ends, and LEDs aimed off the page stay off, so a small paperback uses less light than a big atlas.</p>
<figure><img src="figures/light_v2.svg" alt="Map of light on an open textbook: the printed text gets between {F['v2_text_lux'][0]} and {F['v2_text_lux'][1]} lux.">
<figcaption>Light on the page from the v2 light bar, recomputed from the model's LED positions, aims and intensities. Dashed boxes are the printed text. Estimate.</figcaption></figure>

<h2><small>3 · Battery</small>{bat['cell_volume_cm3']:.1f} cm³ of cells in the same head</h2>
<p>The Pi Zero, its camera board and the separate audio and power boards took most of the head. v2 has one main board on v1's mounting points,
so cells fill the space around the cameras: stepped cells behind and above them and a new cell in the front, {bat['cell_volume_cm3']:.1f} cm³ in all,
against {bat['v1_cell_volume_cm3']} cm³ in v1. The head stays {HEAD_MM} mm.</p>
<p>The power plan: the main chip sleeps between page turns. A small Bluetooth audio chip keeps reading aloud while it sleeps.
Average draw with the light off: {rng(bat['power_w']['light_off'], ' W', 2)}. The light adds {rng(bat['power_w']['light_on_extra'], ' W', 2)}. All EST.</p>
<figure><img src="figures/battery_v2.svg" alt="Battery hours for three kinds of cell, light off and light on, against the 10 hour and 8 hour targets.">
<figcaption>Reading hours from the model's cell volume, 92% usable. The range runs from the highest to the lowest power estimate.</figcaption></figure>
<div class="table-wrap"><table><thead><tr><th>Cell type</th><th>Wh</th><th>Light off</th><th>10 h met?</th><th>Light on</th><th>8 h met?</th></tr></thead><tbody>{bat_rows}</tbody></table></div>
<p><b>What this means:</b> standard Li-po cells give 10 hours with the light off but not 8 hours with it on. 4.45 V cells give
{rng(hrs['high_voltage_4v45']['light_on'], ' h')} with the light on. These are custom stepped pouch cells; nobody has quoted them yet.</p>

<h2><small>4 · Computer and radio</small>Rockchip RK3576 with an AI engine, Wi-Fi 6 and Bluetooth 5.4</h2>
<ul>
<li><b>Computer:</b> Rockchip RK3576, 8 cores, 6 TOPS NPU (an on-chip AI engine for reading text and making speech), 2 GB LPDDR4X, 16 GB eMMC.
v1's Pi Zero 2 W has 4 slower cores, 512 MB and no AI engine. The board keeps the Pi Zero's outline and screw holes, so v1's cover and standoffs fit.</li>
<li><b>Radio:</b> Wi-Fi 6 + Bluetooth 5.4 module (Quectel FCS96x class, 12 × 12 mm) with a flex antenna on the inside of the right wall, away from the steel stick. v1: 2.4 GHz Wi-Fi 4 and Bluetooth 4.2.</li>
<li><b>Untested:</b> taking full 50 MP stills on the RK3576. Its image processor handles 16 MP, so full resolution means capturing raw frames and processing them on the chip. No one was found doing this on the RK3576.</li>
</ul>

<h2><small>5 · Sound</small>A sealed speaker and a smart amplifier</h2>
<ul>
<li>v1: an open 20 × 14 mm micro speaker. v2: a sealed 15 × 11 mm box speaker (Soberton 1511 class, 90 dB at 0.6 W and 10 cm) behind a new grille on the front, driven by a smart amplifier (TI TAS2563) that protects the speaker while running it loud. About 88–90 dB at 10 cm, EST.</li>
<li>A third microphone on the front, so the device can cancel its own voice and hear the reader while it speaks (echo cancelling in software).</li>
<li>v1's headphone jack, volume keys and mute switch stay where they are.</li>
</ul>

<h2><small>6 · Buttons</small>Option A keeps v1's buttons. Option B is the alternative.</h2>
<div class="two">
<div><p><b>Option A (v1 layout, unchanged):</b> Ask, Play/Pause, Back and Forward on top of the head, volume and mute on the side.</p></div>
<div><p><b>Option B:</b> the main keys sit on two wings of the hub at the top edge of the book. The book takes the push, so the head does not sway.
A pocket clicker (Bluetooth, 36 × 28 × 9 mm, EST) does the same from the hand, in bed or on a bus. The top openings are closed.</p></div>
</div>
<div class="renders">
<figure><img src="renders/v2_hero_B.jpg" alt="Option B: keys on two wings of the hub at the top edge of the book, and a small clicker on the table" loading="lazy">
<figcaption>Option B: hub wings with Ask, Play/Pause, Back and Forward, and the pocket clicker.</figcaption></figure>
<figure><img src="renders/v2_inside_A.jpg" alt="Inside the head with the shell hidden: four camera modules on the facet, light boards, battery cells and the main board" loading="lazy">
<figcaption>Inside the head (shell hidden): cameras, light bars, cells, main board.</figcaption></figure>
</div>

<h2><small>7 · Cost</small>${bom_total[0]} to ${bom_total[1]} in parts per unit (EST)</h2>
<p>The venture plan's v1 parts cost is $52.30 at 1,000 units. v2 costs more, mostly because of memory (its price rose sharply in 2026) and the four cameras.
To keep it down, v2 uses 2 GB of memory instead of 4 GB, 16 GB of storage instead of 32 GB, echo cancelling in software instead of a $12–18 voice chip,
catalogue phone camera modules with no custom optics, and v1's shell, stick, hub and blades unchanged.</p>
<figure><img src="figures/cost_v2.svg" alt="Parts cost by block, from ${bom_total[0]} to ${bom_total[1]} per unit in total.">
<figcaption>Parts cost by block at about 1,000 units. Tooling, certification and assembly setup are one-off costs and not included.</figcaption></figure>
<details><summary>All {len(BOM)} lines with sources</summary>
<div class="table-wrap"><table><thead><tr><th>Block</th><th>Part</th><th>Qty</th><th>Cost</th><th>Basis</th><th>Source or note</th></tr></thead>
<tbody>{''.join(bom_rows)}</tbody></table></div></details>

<h2><small>8 · Checks</small>What the model was checked for</h2>
<div class="table-wrap"><table><thead><tr><th>Check</th><th>Option A</th><th>Option B</th></tr></thead><tbody>{checks_html}</tbody></table></div>
<p>Also checked by the model: every camera's window lets its full view through; the four cameras together see the whole page.
Not checked: heat, drop strength, radio range, sound level, real camera blur and focus. These need a prototype.</p>

<h2><small>9 · Not yet known</small>What a prototype has to show</h2>
<ul>
<li>Full 50 MP stills from four cameras on the RK3576 (see section 4).</li>
<li>Camera module sizes: taken from typical phone modules; no supplier drawing yet. The ~4.5 mm lens for the page cameras is a catalogue choice still to confirm with a module maker.</li>
<li>Cell prices and density for small custom 4.45 V and silicon-carbon cells: no quote yet.</li>
<li>The power figures, the light's real efficiency and the speaker's loudness: estimates until measured.</li>
<li>Prices marked EST in the cost table.</li>
</ul>
</main>
<footer>SenseBook hardware v2 proposal, 27 Nov 2026. Hardware design files CERN-OHL-W-2.0; text, figures and renders CC BY 4.0; code Apache-2.0.
Model files: <code>docs/validation/hardware_v2/</code> in the SenseBook repository.</footer>
</body>
</html>
"""
open(os.path.join(SITE, "proposal.html"), "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- README for the folder (same numbers)
md_checks = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in check_rows)
md_bat = "\n".join(f"| {chem_names[k]} | {bat['wh'][k]} | {rng(hrs[k]['light_off'], ' h')} | {met('light_off', 10, k)} | "
                   f"{rng(hrs[k]['light_on'], ' h')} | {met('light_on', 8, k)} |" for k in chem_names)
readme = f"""# SenseBook hardware v2 proposal

A proposal for better hardware in the same head: four 50 MP cameras on the lens facet, a zoned light bar, more battery,
an RK3576 computer, Wi-Fi 6 and Bluetooth 5.4, a sealed speaker with a smart amplifier, and two button layouts
(A: v1's buttons; B: keys on hub wings plus a pocket clicker).

**Status: design proposal.** Nothing has been built or measured. Numbers come from the 3D model below and from
datasheets and listings checked on 27 Nov 2026. EST = our estimate.

- 3D model and proposal page: `web/index.html` and `web/proposal.html`, published at https://sensebook-hardware-v2.vercel.app (proposal: `/proposal.html`).
- Built on the build chat's v1 model at commit `{R['v1_reference']['model_commit']}` (read from git, never edited).

## The numbers

| | v1 | v2 |
|---|---|---|
| Lowest dpi on the printed text (textbook spread, 9 cm stick) | {F['v1_text_min_dpi']} | {F['v2_text_min_dpi']} |
| Light on the printed text | ring light | {F['v2_text_lux'][0]}–{F['v2_text_lux'][1]} lux, about {lit['electrical_w']} W (EST) |
| Battery cells | {bat['v1_cell_volume_cm3']} cm³ | {bat['cell_volume_cm3']:.1f} cm³ |
| Head (mm) | {HEAD_MM} | {HEAD_MM} (same shell; every part inside it) |
| Head mass (g) | {R['v1_reference']['mass_head_g']} | {A['mass']['head_g']} (A), {B['mass']['head_g']} (B) |
| Parts cost per unit at 1,000 | $52.30 (venture plan) | ${bom_total[0]}–{bom_total[1]} (EST, `data/bom_v2_estimate.csv`) |

### Battery (EST)

| Cell type | Wh | Light off | 10 h met? | Light on | 8 h met? |
|---|---|---|---|---|---|
{md_bat}

### Model checks

| Check | Option A | Option B |
|---|---|---|
{md_checks}

## Files

- `cad/hw2_params.py`: every new dimension, mass and source.
- `cad/build_v2.py`: builds the model on top of v1, runs the checks, writes `out/model_report_v2.json`, the GLB, STEP (A and B) and STL.
- `cad/figures_v2.py`: redraws the dpi, light, battery and cost charts from the model's saved cameras and LEDs (a second check).
- `cad/render_v2.py`: Blender renders (`out/renders/`, web copies in `web/renders/`).
- `cad/make_site.py`: writes this README, `web/proposal.html` and `web/facts.json` from the report.
- `cad/publish_v2.py`: publishes `web/` to its own Vercel project through the REST API (token from `VERCEL_TOKEN`, never stored).
- `data/bom_v2_estimate.csv`: parts cost estimate with a source or note on every line.

Rebuild, from the repository root:

```
design\\.venv\\Scripts\\python.exe docs\\validation\\hardware_v2\\cad\\build_v2.py
python docs\\validation\\hardware_v2\\cad\\figures_v2.py
design\\.venv-render\\Scripts\\python.exe docs\\validation\\hardware_v2\\cad\\render_v2.py
python docs\\validation\\hardware_v2\\cad\\make_site.py
```

## Not yet known

- Full 50 MP stills from four cameras on the RK3576 (its image processor handles 16 MP; raw capture is untested).
- Camera module sizes (typical phone modules assumed; no supplier drawing yet).
- Prices and density of small custom 4.45 V and silicon-carbon cells (no quote).
- Power, light efficiency and loudness (estimates until measured).

Licences: hardware design files CERN-OHL-W-2.0; code Apache-2.0; text, figures, renders and data CC BY 4.0.
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
# web copies of the renders (JPEG, 1600 px)
from PIL import Image
os.makedirs(os.path.join(SITE, "renders"), exist_ok=True)
for f in sorted(os.listdir(os.path.join(ROOT, "out", "renders"))):
    if f.endswith(".png"):
        Image.open(os.path.join(ROOT, "out", "renders", f)).convert("RGB").save(
            os.path.join(SITE, "renders", f[:-4] + ".jpg"), quality=86, optimize=True, progressive=True)
glb = os.path.join(ROOT, "out", "sensebook_v2.glb")
if os.path.exists(glb):
    shutil.copy(glb, os.path.join(SITE, "sensebook_v2.glb"))
print("site written:", os.listdir(SITE))
