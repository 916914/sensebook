# SenseBook hardware v2 proposal

A proposal for better hardware in the same head: four 50 MP cameras on the lens facet, a zoned light bar, more battery,
an RK3576 computer, Wi-Fi 6 and Bluetooth 5.4, a sealed speaker with a smart amplifier, and two button layouts
(A: v1's buttons; B: keys on hub wings plus a pocket clicker).

**Status: design proposal.** Nothing has been built or measured. Numbers come from the 3D model below and from
datasheets and listings checked on 27 Nov 2026. EST = our estimate.

- 3D model and proposal page: `web/index.html` and `web/proposal.html`, published at https://sensebook-hardware-v2.vercel.app (proposal: `/proposal.html`).
- Built on the build chat's v1 model at commit `598d0f3` (read from git, never edited).

## The numbers

| | v1 | v2 |
|---|---|---|
| Lowest dpi on the printed text (textbook spread, 9 cm stick) | 82 | 315 |
| Light on the printed text | ring light | 300–753 lux, about 0.59 W (EST) |
| Battery cells | 17.5 cm³ | 24.5 cm³ |
| Head (mm) | 88 × 40 × 34 | 88 × 40 × 34 (same shell; every part inside it) |
| Head mass (g) | 108.8 | 109.0 (A), 106.2 (B) |
| Parts cost per unit at 1,000 | $52.30 (venture plan) | $149–259 (EST, `data/bom_v2_estimate.csv`) |

### Battery (EST)

| Cell type | Wh | Light off | 10 h met? | Light on | 8 h met? |
|---|---|---|---|---|---|
| Standard Li-po (460 Wh/L) | 11.3 | 16.0 to 29.7 h | yes, even in the worst case | 6.5 to 10.9 h | only in the better cases |
| 4.45 V cell (600 Wh/L, EST) | 14.7 | 20.8 to 38.7 h | yes, even in the worst case | 8.5 to 14.3 h | yes, even in the worst case |
| Silicon-carbon cell (800 Wh/L, phone grade) | 19.6 | 27.8 to 51.6 h | yes, even in the worst case | 11.3 to 19.0 h | yes, even in the worst case |

### Model checks

| Check | Option A | Option B |
|---|---|---|
| Parts overlapping each other (more than 0.02 mm³) | 0 | 0 |
| Overlaps in every v1 pose (stick lengths, tilt, blade and leg positions) | 0 | 0 |
| Camera sight lines blocked by a part (rays to every page point each camera reads) | 0 of 3626 | 0 of 3626 |
| Everything in the head, bounding box (mm), buttons and hinge included | 89.2 × 34.0 × 53.5 | 89.2 × 34.0 × 52.1 |
| Same, v1 parts (for comparison) | 89.2 × 34.0 × 53.5 |  |
| Front shell bounding box (mm) | 88.0 × 30.0 × 48.3 | v1: 88.0 × 30.0 × 48.3 |
| Mass, whole device without the book (g) | 160.2 | 166.1 (clicker not included) |
| Mass of the head (g) | 109.0 | 106.2  (v1: 108.8) |

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
design\.venv\Scripts\python.exe docs\validation\hardware_v2\cad\build_v2.py
python docs\validation\hardware_v2\cad\figures_v2.py
design\.venv-render\Scripts\python.exe docs\validation\hardware_v2\cad\render_v2.py
python docs\validation\hardware_v2\cad\make_site.py
```

## Not yet known

- Full 50 MP stills from four cameras on the RK3576 (its image processor handles 16 MP; raw capture is untested).
- Camera module sizes (typical phone modules assumed; no supplier drawing yet).
- Prices and density of small custom 4.45 V and silicon-carbon cells (no quote).
- Power, light efficiency and loudness (estimates until measured).

Licences: hardware design files CERN-OHL-W-2.0; code Apache-2.0; text, figures, renders and data CC BY 4.0.
