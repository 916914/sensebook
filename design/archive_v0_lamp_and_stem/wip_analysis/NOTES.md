# SenseBook WIP notes: webcam-sized head on a stick at the top of the spine

Status: concept on hold until the founder picks a foot option (A, B or C). There is no CAD, STL or render yet; the earlier lamp and base-plus-stem direction was dropped before any modelling. Every figure below is a geometric or engineering **estimate**. Nothing has been built or measured.

Scripts in this folder (venv: `design/.venv`):
- `coverage_wide_head.py` (Wide and Standard lens, 46 × 30 cm design spread);
- `coverage_typical_textbook.py` (typical NCTB spread, about 37 × 24.5 cm);
- `coverage_standard_lens_*.py` (earlier Standard-lens scans from the lamp study).

Coordinates: y = 0 is the book's top edge, with +y toward the reader. The setback **d** is how far the lens sits behind the top edge. Tilt is the angle of the optical axis from straight down, toward the reader. The sensor's long side runs across the spread. The Wide lens model uses f = 2.75 mm (1964 px), with barrel distortion fitted to the published 102° H × 67° V. The published 120° diagonal implies stronger corner distortion than this model, so treat corner dpi as optimistic.

## 1. Camera coverage and dpi

Minimum lens height to see the full 46 × 30 cm spread, with best tilt:

| Lens | d = 20 mm | d = 40 mm | d = 60 mm |
|---|---|---|---|
| CM3 **Wide**, zero margin | 19.6 cm, 25° | 18.8 cm, 28° | 18.0 cm, 30° |
| CM3 **Wide**, 5 % margin | 20.8 cm, 25° | 20.2 cm, 27° | 19.4 cm, 30° |
| CM3 Standard, 5 % margin | 39.2 cm, 20° | 38.8 cm, 22° | 38.2 cm, 24° |

Wide lens dpi (d = 60 mm, best tilt):

| Lens height | Top edge (nearest camera) | Page centre | Reader-side edge (worst) | Reader-side corner* |
|---|---|---|---|---|
| 20 cm | 240 | 129 | **80** | 91 |
| 22 cm | 224 | 127 | **81** | 90 |
| 26 cm | 194 | 120 | **81** | 88 |
| 30 cm | 169 | 114 | **81** | 85 |

\* The corner figure is optimistic; see the note above.

Findings:
- **The Wide lens cannot meet the original "≥ 150 dpi everywhere" rule at any height.** The reader-side edge stays at about 80–98 dpi, depending on setback.
- **Raising the Wide lens does not add resolution.** It only adds coverage margin, while the centre and top-edge dpi drop. So "extend to 30 cm to read any print" does not help with the Wide lens.
- On a **typical NCTB textbook spread (about 37 × 24.5 cm)**:
  - Wide at about 16–17 cm: 102–116 dpi at the reader edge.
  - **Standard at about 31 cm (stick fully extended, d = 20–40 mm, tilt 21–24°): 176–188 dpi at the reader edge and about 230 dpi at the centre.** This meets the 150 dpi rule.
- Legibility check (rough): Bangla body text at 11–12 pt has a main glyph height of about 2.5–2.8 mm.
  - At 80–100 dpi that is about 8–11 px, which is marginal for conjuncts (juktakkhor).
  - At 150 dpi or more it is 15 px or more.
- Options for the founder:
  - (i) Wide lens: compact pose at about 21 cm covers even oversized books, at 80–100 dpi near the reader.
  - (ii) Standard lens: about 31 cm covers typical textbooks at 165 dpi or more. Oversized spreads would need about 39 cm, so the student slides the book closer or reads one page at a time.
- **Recommendation pending founder input: (ii) Standard lens at about 31 cm** if OCR quality on real textbooks matters most. The Pi Zero 2 W has only one camera port, so it cannot carry both lenses.

## 2. Page-turn clearance

Envelope for a hand turning a page:
- A turning page pivots on the gutter and stays in the region y ≥ 0. A stiff 23 cm page reaches about 25 cm above the table when vertical; typical flexible pages reach about 15–20 cm above the page.
- Allow fingers to reach 25 mm behind the top edge and about 3 cm above the page arc. That gives a keep-out zone of y ≥ −25 mm, up to about 28 cm high in the worst case.

Head geometry (85 × 38 × 30 mm, lens at the lower centre of the face):
- Tilted 25–30°, the top edge of the face sits about 26 mm *forward* of the lens.
- So the module stays at least 25 mm behind the top edge only if **d ≥ about 55 mm**.

Two ways to clear the envelope:
- **Behind:** d = 60 mm. The module's front-most point is then about 34 mm behind the top edge, at any height. This is the recommended pose: Wide at h = 21–22 cm, tilt about 29°, coverage margin 10–14 %. The stick sits about 15 mm further back.
- **Above:** a lens height of 30 cm or more puts the head's underside at about 29.5 cm. That clears even a stiff vertical page (about 25 cm) by about 4.5 cm, and flexible pages by 9 cm or more.

Both stay out of the keep-out zone, and nothing touches the pages.

## 3. Stability (estimated masses and forces)

Assumed masses:
- head about 70 g (Pi, camera and audio inside);
- upper telescoping stages plus a coiled 2-core cable about 20 g;
- lower battery segment about 80 g (18650 cell 47 g, tube, charger, USB-C, hinge).

Push forces below are applied at the head, at about 22.5 cm.

| Foot | Total mass | 10° table tilt | Push to tip (worst direction) | Stowed size (estimate) |
|---|---|---|---|---|
| **A** slide-under plate (2.5 mm aluminium, 110 × 135 mm, 100 g), on the table with no book | 270 g | passes; tips at 24° backward, 33° sideways | 0.43 N backward, 0.65 N sideways | about 140 × 110 × 36 mm (about 140 × 60 × 40 mm if the plate folds in half) |
| **A** with a book on the plate | — | passes easily | several times higher: the book's weight pins the plate | — |
| **B** weighted puck (Ø 70 × 15 mm, about 320 g, steel-filled) | 490 g | passes; tips at 33° | about 0.70 N in all directions | about 160 × 85 × 70 mm (bulky) |
| **C** fold-out tripod (3 × 70 mm legs) | 200 g | passes only just; tips at 16° | **about 0.28 N** (a brush can tip it) | about 165 × 38 × 32 mm (marker-like) |

- **A** is the most stable once a book is on it, and the most compact plate design.
  - The 2.5 mm step under the top 60–75 mm tilts the page by about 0.6°. A 15 mm taper on the leading edge hides the step. The effect on camera focus and dpi is negligible.
  - A 2 mm stainless plate (235 g) would raise the no-book figures by about 1.7×, but makes the device heavier.
- **B** is the best standalone option, but heavy and bulky.
- **C** is the smallest, but weak unless one leg slides under the book.

## 4. Does a Pi Zero 2 W fit in an 85 × 38 × 30 mm head?

**Yes, but tightly, and not with the WM8960 HAT.**

Stack-up inside the head (internal space about 81 × 34 × 26 mm with 2 mm walls):

| Item | Depth |
|---|---|
| Front wall | 2 mm |
| CM3 Wide (25 × 24 × 12.4 mm) behind the lens | 12.4 mm |
| Gap | 1 mm |
| Pi mounted vertically against the back wall, no header, wires soldered to the pads (65 × 30 × about 5 mm with connectors), on a 1 mm standoff | about 6 mm |
| Back wall | 2 mm |
| **Total** | **about 23.4 mm (fits within 30 mm)** |

- Width: about 71 mm. Height: about 35 mm.
- The Ask switch (12 × 12 × 7.3 mm) above the camera just fits the 38 mm height.

**Audio path:**
- The WM8960 HAT stacked on the Pi adds about 12–15 mm of depth, so it does not fit. Electrokit lists it at 65 × 30 mm; Waveshare gives the size only in a drawing.
- Proposed instead, all on the existing I2S pins 18–21 so the pin map stays largely intact:
  - 2 × I2S MEMS mics (INMP441 or SPH0645 class);
  - a MAX98357A amp driving a 20–28 mm speaker behind the four-dot grille;
  - a small I2S DAC with a 3.5 mm jack (UDA1334A class) on the same bus;
  - jack-detect switching off the amp.
- New GPIOs needed: amp shutdown and jack-detect. GPIO 2/3 are freed.

**Size verdict:**
- With loose breakout boards, the realistic head is about 88 × 40 × 30 mm.
- Reaching 85 × 38 × 30 mm needs one small carrier board that combines mics, amp, DAC and buttons.
- The v2 custom SoC board (about 40 × 30 mm) would allow about 70 × 30 × 25 mm.

**Power and thermal:**
- Putting the Pi in the head means only 2 power wires (5 V and ground) run up the telescoping stick, as a coiled 24–26 AWG cord. No camera ribbon crosses a sliding joint.
- Battery: one 18650 (3,000–3,500 mAh, about 8.6–10 Wh usable after the boost converter).
  - Light off (1.2–1.5 W): **about 6–8 h**.
  - Light ring on (about 2.0–2.3 W): **about 4–5 h**.
- Thermal risk: at 1.4 W the head surface is about 11 K above ambient. Sustained heavy load (about 3 W) inside a closed plastic head at 35 °C ambient may throttle the SoC. Add an aluminium spreader on the back wall.

## 5. Open questions for the founder

1. Which foot: A, B or C?
2. Which lens: Wide (whole spread, about 80–100 dpi near the reader) or Standard at about 31 cm (typical textbooks at 165 dpi or more)?
3. Is a stowed width of about 110 mm (plate A) acceptable, or should the plate fold in half to about 60 mm?
4. The status lights on the face are hard for the reader to see when the head is tilted 25–30° down; the face then meets their eye line at only about 18°. The capture light should also appear on the top-front edge.
