# SenseBook CAD: the parametric model

Everything in this folder is built by script from one file of numbers, [`sb_params.py`](sb_params.py). Change a number there, run the scripts, and the model, the print files, the checks and the pictures all follow.

> **Status.** This is a design model. No part has been printed or assembled. Sizes of bought parts (camera, cells, breakout boards) are typical sizes, marked EST in `sb_params.py`.

## What is here

| File | What it does |
|---|---|
| `sb_params.py` | Every dimension and mass. The top half is the original envelope; the "3D model layer" below it places the parts inside. |
| `analysis.py` | Camera coverage, page-turn clearance, stability and spring force from geometry alone (written before the 3D model). |
| `build_model.py` | Builds all 88 bodies with CadQuery, checks them for collisions in six poses, and exports STEP, STL, DXF and meshes. |
| `check_model.py` | Compares the 3D model with `analysis.py`: lens position, mass, centre of mass, tip-over, wall thickness. Writes the print notes. |
| `make_textures.py` | Plain textbook-style page pictures for the render scenes (our own text). |
| `render_scenes.py` | Renders the 15 pictures in `design/renders/` with Blender (Cycles) and exports `out/sensebook.glb` for the web viewer. |
| `annotate.py` | Adds the part labels and dimensions to the pictures. |

## What comes out (`out/`)

| File | Use |
|---|---|
| `SenseBook_assembly.step` | The whole device, every body named and coloured, in the open-hardcover pose. |
| `step/*.step` | One STEP file per body (88). |
| `stl/*.stl` | The 18 printed parts. See [`PRINT_NOTES.md`](out/PRINT_NOTES.md). |
| `blade_flat_pattern_*.dxf` | Flat outlines for cutting the two spring-steel blades (two step heights). |
| `sensebook.glb` | The model for the web viewer (`design/viewer/`). |
| `model_report.json` | Collisions, clearances, mass and centre of mass for every body and pose. |
| `check_report.json` | The model against `analysis.py`. Summarised in [`../VALIDATION.md`](../VALIDATION.md). |
| `analysis_results.json` | Output of `analysis.py`. |

## Run it

Two Python 3.11 environments, kept out of git:

```bash
cd design
python -m venv .venv         && .venv/Scripts/pip install cadquery trimesh rtree matplotlib numpy scipy shapely pillow pyyaml
python -m venv .venv-render  && .venv-render/Scripts/pip install bpy==4.2.0
cd cad
../.venv/Scripts/python analysis.py            # geometry checks and three diagrams
../.venv/Scripts/python build_model.py         # model, collision checks, STEP / STL / DXF  (about 5 minutes)
../.venv/Scripts/python check_model.py         # model against analysis.py, print notes, two diagrams
../.venv/Scripts/python make_textures.py       # page pictures for the scenes
../.venv-render/Scripts/python render_scenes.py   # 15 renders and the GLB  (about 45 minutes on a 12-thread CPU)
../.venv/Scripts/python annotate.py            # labels and dimensions
```

`render_scenes.py --draft hero side` renders chosen scenes quickly at low quality.

## Frames and handedness

- **Unit frame:** front face at y = 0, back at y = -34, bottom at z = 0, top at z = 40.
- **Book frame:** page surface z = 0 at the top edge, top edge of the book y = 0, y grows toward the reader, gutter at x = 0.
- `sb_params.py` calls +x the reader's right. With y toward the reader and z up that is a left-handed frame, so `build_model.py` mirrors every body once (`X_cad = -x`). **In the exported files +x is the reader's left.** Part names such as `cell_left` always mean the reader's left.

## Poses

`build_model.py` checks and exports six poses: open hardcover on a table (default), thin paperback, free-standing tripod with no book, held in the hands, stick pulled up to 18 cm on a thick book, and folded. The moving groups are the unit (tilt), the inner tube (telescope), the two blades (fold up) and the rear leg (swing).

## Model decisions that are not in the attachment plan

These were needed to make a complete model. Each is a proposal to test, not a settled design.

1. **Shell split:** a deep front "tub" and a shallow back cover, joined by a tongue and four M2 screws.
2. **Where things go inside:** the Pi against the back cover with a heat spreader, the two cells standing either side of the camera, audio boards on the reader's left, power board and sockets on the right.
3. **Controls:** Ask in the middle of the top with Play/Pause in front of it, Back and Forward either side; volume and mic mute on the left side; USB-C and headphone socket on the right side; speaker behind a grille on the front.
4. **Tilt joint:** two lugs under the unit, a tongue on the stick, an M3 screw with a thumb nut for friction.
5. **Hub:** the stick tubes run through the hub; blades clamp in small knuckles that pivot to fold; the rear leg hinges at the back with one torsion spring and swings from "on the table behind" to "under the spine".
6. **Hub sensor:** a small switch that reads "rear leg deployed", so it reports attached both on a table and in the hand.
7. **Blade shape:** a straight root, two bends to step down to the cover, then a flat run with the 25 degree splay cut into the outline.

## Licence

Everything in `design/cad/` (the scripts and the files they export) is hardware design: CERN-OHL-W-2.0. The renders and diagrams are CC BY 4.0. The viewer page in `design/viewer/` is software and carries its own Apache-2.0 notice. See the repository `LICENSE`.
