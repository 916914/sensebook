# SenseBook CAD: the parametric model

Everything in this folder is built by script from one file of numbers, [`sb_params.py`](sb_params.py). Change a number there, run the scripts, and the model, the print files, the drawings, the checks and the pictures all follow.

> **Status.** This is a design model. No part has been printed or assembled. Bought parts (camera, cells, boards, switches, springs, screws) are drawn at the sizes their makers publish: 23 parts, 188 values, each with its source and date in [`SOURCES.md`](SOURCES.md). 25 of those values are published by nobody. They are marked **EST** in `sb_params.py`, in `SOURCES.md` and on the drawings, with the reason and how to measure them.

## What is here

| File | What it does |
|---|---|
| `sb_params.py` | The single source of truth. The envelope and mechanics; `PARTS` and `SRC` (published sizes of every bought part and where they come from); `EST_WHY` (why each estimate is an estimate); `TOL` (the tolerances and fits the model is drawn for); the layout of the parts inside the unit; the mass table. |
| [`SOURCES.md`](SOURCES.md) | Written from `sb_params.py`: every bought part, every dimension, its value, its basis, its source. |
| `analysis.py` | Camera coverage, page-turn clearance, stability and spring force from geometry and the mass table. |
| `build_model.py` | Builds all 89 bodies with CadQuery, checks every neighbouring pair for clashes and clearance in the assembled pose and the moving parts in six poses, and exports STEP, STL, DXF and meshes. |
| `check_model.py` | Classifies every touching pair by its fit, measures the walls of the printed parts, checks the cable routes, mass, centre of mass and tip-over, and writes `out/FIT_REPORT.md`, `out/PRINT_NOTES.md` and `SOURCES.md`. |
| `make_drawings.py` | Dimensioned PDF drawings for every part and the assembly, into `design/drawings/`. |
| `make_textures.py` | Plain textbook-style page pictures for the render scenes (our own text). |
| `render_scenes.py` | Renders the 15 pictures in `design/renders/` with Blender (Cycles) and exports `out/sensebook.glb` for the web viewer. |
| `annotate.py` | Adds the part labels and dimensions to the pictures. |

## What comes out

| File | Use |
|---|---|
| `out/SenseBook_assembly.step` | The whole device, every body named and coloured, in the open-hardcover pose. |
| `out/step/*.step` | One STEP file per body (89). |
| `out/stl/*.stl` | The 18 printed parts. See [`PRINT_NOTES.md`](out/PRINT_NOTES.md). |
| `out/blade_flat_pattern_*.dxf` | Flat outlines for cutting the two spring-steel blades (two step heights). |
| [`out/FIT_REPORT.md`](out/FIT_REPORT.md) | Tolerances, the interference check, the clearance between every pair of parts that touch or come within 0.5 mm, wall thickness, cable routes, mass and stability. |
| [`../drawings/SenseBook_drawings.pdf`](../drawings/SenseBook_drawings.pdf) | All drawings in one file; `../drawings/parts/` has one PDF per part. |
| `out/sensebook.glb` | The model for the web viewer (`design/viewer/`). |
| `out/model_report.json`, `out/check_report.json`, `out/analysis_results.json` | The raw numbers behind the reports. |

## Run it

Two Python 3.11 environments, kept out of git:

```bash
cd design
python -m venv .venv         && .venv/Scripts/pip install cadquery trimesh rtree matplotlib numpy scipy shapely pillow pyyaml fast-simplification
python -m venv .venv-render  && .venv-render/Scripts/pip install bpy==4.2.0
cd cad
../.venv/Scripts/python build_model.py         # model, clash and clearance checks, STEP / STL / DXF  (about 12 minutes)
../.venv/Scripts/python analysis.py            # geometry checks and three diagrams
../.venv/Scripts/python check_model.py         # fit report, print notes, source table, two diagrams
../.venv/Scripts/python make_drawings.py       # the PDF drawings (about 10 minutes)
../.venv/Scripts/python make_textures.py       # page pictures for the scenes
../.venv-render/Scripts/python render_scenes.py   # 15 renders and the GLB  (about 45 minutes on a 12-thread CPU)
../.venv/Scripts/python annotate.py            # labels and dimensions
```

`build_model.py --quick --no-mesh` runs only the checks (about 4 minutes). `render_scenes.py --draft hero side` renders chosen scenes quickly at low quality. `make_drawings.py hub_body` draws only the parts whose names start that way.

The mass table in `sb_params.py` (`MASS`, `UNIT_COM`) is copied from the model's own report. If the model changes mass, copy the new numbers across and run `analysis.py` again.

## Tolerances the model is drawn for

| What | Value |
|---|---|
| Printed PETG part, general | ±0.2 mm |
| Sliding fit, printed (button caps, slider, cover tongue) | 0.15 mm clear per side |
| Steel pin in a drilled hole | 0.05 mm per side |
| Bought part to anything it must not touch | at least 0.3 mm |
| Cut sheet / cut tube and pin length / turned part | ±0.1 / ±0.2 / ±0.05 mm |

They live in `sb_params.TOL`. The fit report lists every pair against them.

## Frames and handedness

- **Unit frame:** front face at y = 0, back at y = -37, bottom at z = 0, top at z = 45.
- **Book frame:** page surface z = 0 at the top edge, top edge of the book y = 0, y grows toward the reader, gutter at x = 0.
- `sb_params.py` calls +x the reader's right. With y toward the reader and z up that is a left-handed frame, so `build_model.py` mirrors every body once (`X_cad = -x`). **In the exported files and on the drawings +x is the reader's left.** Part names such as `cell_left` always mean the reader's left.

## Poses

`build_model.py` checks and exports six poses: open hardcover on a table (default), thin paperback, free-standing tripod with no book, held in the hands, stick pulled up to 18 cm on a thick book, and folded. The moving groups are the unit (tilt), the inner tube (telescope), the two blades (fold up) and the rear leg (swing).

## What changed when the real part sizes went in (27 November 2026)

1. **The unit grew from 88 x 40 x 34 mm to 92 x 45 x 37 mm.** Width: the DAC board with its jack is 30.5 mm long and sits beside the 25 mm camera board. Height: the documented cell pack is 37.5 mm long and its leads leave the top. Depth: the Pi is 5.3 mm thick overall and the real lens needs a bigger ring.
2. **No lens window.** The real lens has a 14.8 mm rim and sees 152 degrees corner to corner, so a flat window in front of it would have to be very large. The lens front now sits in a bezel, 0.4 mm inside the facet.
3. **Camera on two posts and a cradle.** The upper holes of the real board take two screws; its lower edge rests in two notched ribs.
4. **Two stock torsion springs** either side of the leg, acting only in the clamp range. One stock spring of this size cannot give the torque the first analysis assumed.
5. **Hub wider (29 mm)** for the two springs; sensor pocket behind the stick; a groove for the sensor lead and a notch in the foot of the tube.
6. **The hub cord is routed end to end:** through the joint head, into the unit between the lugs, up to the Pi. The first model drew it through the tilt screw.
7. **Blade clamp screws are M1.6**, 2.7 mm in front of the knuckle pin, so that plastic remains between the two holes.
8. **The cover tongue is fused to the cover.** In the first model it was a separate ring that touched nothing.

## Model decisions that are not in the attachment plan

Each is a proposal to test, not a settled design.

1. **Shell split:** a deep front "tub" and a shallow back cover, joined by a tongue and four ST2.2 tapping screws.
2. **Where things go inside:** the Pi against the back cover with a heat spreader, the two cells standing either side of the camera, DAC and amp on the reader's left, charger and fuel gauge on the right, microphones flat under the top.
3. **Controls:** Ask in the middle of the top, with Back, Play/Pause and Forward in a row in front of it; volume and mic mute on the left side with the headphone jack; USB-C on the right side; speaker behind a grille on the front.
4. **Tilt joint:** two lugs under the unit, a tongue on the stick, an M3 screw with a thumb nut for friction.
5. **Hub:** the stick tubes run through the hub; blades clamp in small knuckles that pivot to fold; the rear leg hinges at the back and swings from "on the table behind" to "under the spine".
6. **Hub sensor:** a detector switch pressed by the rear leg when it is folded away, so it reads "in use" both on a table and in the hand.
7. **Blade shape:** a straight root, two bends to step down to the cover, then a flat run with the 25 degree splay cut into the outline.

## Third-party models

None is stored here. Raspberry Pi's drawings are open but their STEP files may not be redistributed; Arducam's STEP file carries no stated licence; KiCad library models are CC-BY-SA. Every bought part is therefore modelled from its published dimensions, and the drawing or file the numbers were read from is cited in `SOURCES.md`.

## Licence

Everything in `design/cad/` and `design/drawings/` (the scripts and the files they export) is hardware design: CERN-OHL-W-2.0. The renders and diagrams are CC BY 4.0. The viewer page in `design/viewer/` is software and carries its own Apache-2.0 notice. See the repository `LICENSE`.
