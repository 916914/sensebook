# SenseBook prototype: 3D-print notes

> **Not yet printed.** These files come straight from the parametric model (`build_model.py`). Sizes and masses below are read from the STL files. Expect one or two fit iterations on the first prints, mainly holes and the cover fit. Every part also has a dimensioned drawing in `design/drawings/`.

18 printed parts, about **56 g of filament** in total at 100% infill (estimate; supports not counted).

## Settings that should work

- 0.4 mm nozzle, 0.16 mm layers for the two shells and the buttons, 0.2 mm for the rest.
- PETG: 240 °C nozzle, 80 °C bed, 3 perimeters. Walls are 1.8 mm, so the shells print as solid walls.
- TPU 95A for the pad: 225 °C, slow (25 mm/s), no retraction tricks needed for a flat pad.
- The model is drawn for a general print tolerance of ±0.2 mm, with 0.15 mm clearance per side on sliding fits (buttons, slider, cover tongue).
- Holes print small. Drill them to size: 1.7 mm pilots for the ST2.2 tapping screws, 2.0 mm and 1.6 mm for the hinge pins, 3.0 mm for the tilt pivot, 10.1 mm for the stick.

## Parts

| File | Qty | Material | Size (mm) | Mass (g, est.) | On the bed | Notes |
|---|---|---|---|---|---|---|
| `stl/shell_front_tub.stl` | 1 | PETG, slate-teal | 92.0 x 53.3 x 33.0 | 23.8 | Open back down on the bed (front face up). | Supports inside for the top wall and under the lens facet; none on the visible front. 3 perimeters, 0.16 mm layers. Clean the four dot holes with a 2.4 mm drill, the cover screw pilots with a 1.7 mm drill, and the lens opening with a blade. |
| `stl/shell_back_cover.stl` | 1 | PETG, slate-teal | 92.0 x 45.0 x 8.3 | 11.0 | Outside face down on the bed. | No supports. The four Pi posts end in 2.55 mm locating pins: check they pass the 2.75 mm Pi holes before fitting the board. |
| `stl/button_ask.stl` | 1 | PETG, marigold (or paint) | 15.0 x 15.0 x 3.4 | 0.6 | Flange down. | The dished top prints without support. 100% infill. |
| `stl/button_play_pause.stl` | 1 | PETG, lighter teal | 11.6 x 6.0 x 4.1 | 0.2 | Flange down. | 100% infill. |
| `stl/button_back.stl` | 1 | PETG, lighter teal | 11.6 x 6.0 x 4.2 | 0.2 | Flange down. | The raised arrow points away from the Play button. |
| `stl/button_forward.stl` | 1 | PETG, lighter teal | 11.6 x 6.0 x 4.2 | 0.2 | Flange down. | Mirror of Back. |
| `stl/button_vol_up.stl` | 1 | PETG, lighter teal | 7.2 x 4.7 x 4.0 | 0.1 | Flange down. | Has the raised dot. |
| `stl/button_vol_down.stl` | 1 | PETG, lighter teal | 7.2 x 4.7 x 3.5 | 0.1 | Flange down. |  |
| `stl/mic_mute_slider.stl` | 1 | PETG, lighter teal | 3.6 x 2.8 x 2.2 | 0.0 | Flat side down. | Tiny part: print four and keep the best. Paint the flag area orange. |
| `stl/light_ring_diffuser.stl` | 1 | PETG, natural / clear | 23.8 x 18.5 x 18.5 | 0.6 | Flat on the bed. | 0.12 mm layers, 100% infill so it glows evenly. Glue in with a drop of clear glue. |
| `stl/status_dot_pipes.stl` | 1 | PETG, natural / clear | 20.4 x 2.4 x 2.0 | 0.0 | Standing on end. | Four 2.4 mm pins in one file. Or cut them from 2.4 mm clear filament or acrylic rod. |
| `stl/tilt_joint_head.stl` | 1 | PETG | 17.5 x 8.0 x 7.9 | 0.7 | Spigot up, tongue on the bed with support, or split and glue. | Drill the pivot hole to 3.0 mm. 100% infill: this part carries the unit. |
| `stl/stick_collar.stl` | 1 | PETG | 13.0 x 13.0 x 7.5 | 0.5 | Wide end down. | Ream to push onto the 10 mm tube and grip the 8 mm tube lightly. |
| `stl/hub_body.stl` | 1 | PETG | 29.0 x 24.6 x 23.6 | 10.7 | Top face down on the bed. | Supports in the leg slot, the spring pockets and the knuckle seats. Drill: stick bore 10.1 mm, leg pin 2.0 mm, knuckle pin 1.6 mm. 100% infill. |
| `stl/blade_knuckle_right.stl` | 1 | PETG | 8.8 x 8.0 x 6.8 | 0.5 | Slit vertical. | Saw or file the blade slit to 0.45 mm if it closes up. Drill 1.7 mm (pin); clamp screw hole 1.7 mm above the slit, 1.3 mm pilot below it. |
| `stl/blade_knuckle_left.stl` | 1 | PETG | 8.8 x 8.0 x 6.8 | 0.5 | Slit vertical. | Mirror of the right knuckle. |
| `stl/rear_leg.stl` | 1 | PETG | 66.5 x 50.0 x 7.6 | 4.1 | Flat on its side, barrel axis vertical. | Layers then run along the arm, which is stronger. Drill the barrel 2.1 mm. |
| `stl/rear_leg_pad.stl` | 1 | TPU 95A | 50.0 x 14.0 x 2.0 | 1.7 | Flat. | Glue to the T-foot with flexible CA or contact glue. |

## Not printed

- **Blades:** cut from 0.4 mm full-hard 300-series stainless spring shim with the `blade_flat_pattern_*.dxf` outlines (two bends each, see the assembly guide). `hardcover` has the shorter step, `thin_book` the longer one. Round and deburr every edge.
- **Stick:** 10 mm and 8 mm stainless tube, 0.5 mm wall, cut to 103.5 mm and 105.5 mm (±0.2).
- **Lens bezel:** turned or printed ring, 18 mm outside, 15.2 mm inside, 1.8 mm thick, chamfered on the outer face. There is no window: the lens front sits in the bezel.
- **Heat spreader:** 40 x 21 x 1 mm aluminium sheet.
- **Pins:** leg hinge pin 2.0 x 28.6 mm, knuckle pin 1.6 x 30.8 mm, steel.

## Frames

- Unit parts are in the unit frame from `sb_params.py` (mm): front face at y = 0, bottom at z = 0.
- Stick, hub and leg parts are in the book frame: page surface z = 0, top edge of the book y = 0.
- The CAD files are right-handed, so x is mirrored against `sb_params.py`: in the files, +x is the reader's left.
- `SenseBook_assembly.step` holds all 89 bodies in place (hardcover pose); `step/` has one STEP per body.
