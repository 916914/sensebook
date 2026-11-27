# SenseBook prototype: 3D-print notes

> **Not yet printed.** These files come straight from the parametric model (`build_model.py`). Sizes and masses below are read from the STL files. Expect one or two fit iterations on the first prints, mainly holes and the cover fit.

Eighteen printed parts, about **49 g of filament** in total at 100% infill (estimate; supports not counted).

## Settings that should work

- 0.4 mm nozzle, 0.16 mm layers for the two shells and the buttons, 0.2 mm for the rest.
- PETG: 240 °C nozzle, 80 °C bed, 3 perimeters. Walls are 1.8 mm, so the shells print as solid walls.
- TPU 95A for the pad: 225 °C, slow (25 mm/s), no retraction tricks needed for a flat pad.
- Holes print small. Drill them to size: 1.6 mm for the M2 self-tapping screws, 2.0 mm and 1.6 mm for the hinge pins, 3.0 mm for the tilt pivot, 10.1 mm for the stick.

## Parts

| File | Qty | Material | Size (mm) | Mass (g, est.) | On the bed | Notes |
|---|---|---|---|---|---|---|
| `stl/shell_front_tub.stl` | 1 | PETG, slate-teal | 88 x 48 x 30 | 20.4 | Open back down on the bed (front face up). | Supports inside for the top wall and under the lens facet; none on the visible front. 3 perimeters, 0.16 mm layers. Clean the four dot holes with a 2.4 mm drill and the lens opening with a blade. |
| `stl/shell_back_cover.stl` | 1 | PETG, slate-teal | 88 x 40 x 7 | 9.0 | Outside face down on the bed. | No supports. The four Pi posts end in 2.5 mm locating pins: check they pass the Pi holes before fitting the board. |
| `stl/button_ask.stl` | 1 | PETG, marigold (or paint) | 15 x 15 x 3 | 0.6 | Flange down. | The dished top prints without support. 100% infill. |
| `stl/button_play_pause.stl` | 1 | PETG, lighter teal | 12 x 6 x 4 | 0.2 | Flange down. | 100% infill. |
| `stl/button_back.stl` | 1 | PETG, lighter teal | 10 x 10 x 4 | 0.3 | Flange down. | The raised arrow points away from the Ask button. |
| `stl/button_forward.stl` | 1 | PETG, lighter teal | 10 x 10 x 4 | 0.3 | Flange down. | Mirror of Back. |
| `stl/button_vol_up.stl` | 1 | PETG, lighter teal | 10 x 5 x 4 | 0.1 | Flange down. | Has the raised dot. |
| `stl/button_vol_down.stl` | 1 | PETG, lighter teal | 10 x 5 x 4 | 0.1 | Flange down. |  |
| `stl/mic_mute_slider.stl` | 1 | PETG, lighter teal | 3 x 3 x 2 | 0.0 | Flat side down. | Tiny part: print four and keep the best. Paint the flag area orange. |
| `stl/light_ring_diffuser.stl` | 1 | PETG, natural / clear | 20 x 16 x 16 | 0.4 | Flat on the bed. | 0.12 mm layers, 100% infill so it glows evenly. Glue in with a drop of clear glue. |
| `stl/status_dot_pipes.stl` | 1 | PETG, natural / clear | 20 x 2 x 2 | 0.0 | Standing on end. | Four 2.4 mm pins in one file. Or cut them from 2.4 mm clear filament / acrylic rod. |
| `stl/tilt_joint_head.stl` | 1 | PETG | 17 x 8 x 8 | 0.8 | Spigot up, tongue on the bed with support, or split and glue. | Drill the pivot hole to 3.0 mm. 100% infill: this part carries the unit. |
| `stl/stick_collar.stl` | 1 | PETG | 13 x 13 x 8 | 0.5 | Wide end down. | Ream to slide on the 10 mm tube and grip the 8 mm tube lightly. |
| `stl/hub_body.stl` | 1 | PETG | 26 x 25 x 24 | 9.0 | Top face down on the bed. | Supports in the leg slot and the knuckle seats. Drill: stick bore 10.1 mm, leg pin 2.0 mm, knuckle pin 1.6 mm. 100% infill. |
| `stl/blade_knuckle_right.stl` | 1 | PETG | 9 x 8 x 7 | 0.5 | Slit vertical. | Saw or file the blade slit to 0.45 mm if it closes up. Drill 1.6 mm (pin) and 2.0 mm (clamp screw). |
| `stl/blade_knuckle_left.stl` | 1 | PETG | 9 x 8 x 7 | 0.5 | Slit vertical. | Mirror of the right knuckle. |
| `stl/rear_leg.stl` | 1 | PETG | 67 x 50 x 8 | 4.1 | Flat on its side, barrel axis vertical. | Layers then run along the arm, which is stronger. Drill the barrel 2.0 mm. |
| `stl/rear_leg_pad.stl` | 1 | TPU 95A | 50 x 14 x 2 | 1.7 | Flat. | Glue to the T-foot with flexible CA or contact glue. |

## Not printed

- **Blades:** cut from 0.4 mm 301 spring-steel shim with the `blade_flat_pattern_*.dxf` outlines (two bends each, see the assembly guide). `hardcover` has the shorter step, `thin_book` the longer one. Round and deburr every edge.
- **Stick:** 10 mm and 8 mm tube, 0.5 mm wall, cut to 103.5 mm and 106.5 mm.
- **Lens window:** 14 mm clear acrylic or glass disc, 0.8 to 1 mm thick. **Lens bezel:** turned or printed ring, 15 mm outside, 12.6 mm inside.
- **Heat spreader:** 40 x 21 x 1 mm aluminium sheet.

## Frames

- Unit parts are in the unit frame from `sb_params.py` (mm): front face at y = 0, bottom at z = 0.
- Stick, hub and leg parts are in the book frame: page surface z = 0, top edge of the book y = 0.
- The CAD files are right-handed, so x is mirrored against `sb_params.py`: in the files, +x is the reader's left.
- `SenseBook_assembly.step` holds all 88 bodies in place (hardcover pose); `step/` has one STEP per body.
