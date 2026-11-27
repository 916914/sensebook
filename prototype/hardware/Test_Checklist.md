# SenseBook prototype: test checklist

> **Status: nothing below has been run on hardware yet.** The "model says" column gives the value predicted by the CAD model or the geometry scripts (all estimates). Fill in the Result column on the bench. A unit goes to a tester only when sections B, G and F5 to F7 have passed.
>
> **Do section A before printing anything.** The model is drawn around real parts at their published sizes, but 25 sizes are published by nobody. If a real part is bigger than its estimate, change `sb_params.py` and re-run the model first.

Print this page, or copy the tables into a sheet. One row, one result, one date.

## A. Parts and prints

| # | Check | Pass when | Result |
|---|---|---|---|
| A1 | Every bought part measured against [SOURCES.md](../../design/cad/SOURCES.md) | Each published size within 0.2 mm; each of the 25 estimates measured and written down | |
| A2 | Cell packs, with their protection board | At most 10.5 thick, 26 wide, 37.5 long (mm). The documented pack is 9.5 x 26 x 37.5 | |
| A3 | Camera | Board 25.0 x 23.9 mm; lens rim 14.8 mm; 17.05 mm from the back of the board to the lens front (Arducam B0310) | |
| A4 | Fuel gauge with its sockets removed | 2.8 mm or less from the underside of the board to the tallest part | |
| A5 | DAC board and its jack | Board 30.48 x 20.32 mm; jack nose 6.0 mm across or less; note whether the jack has a detect contact | |
| A6 | All 18 printed parts present, no warping | Back cover seats in the front shell with no gap over 0.3 mm | |
| A7 | Blades | No sharp edge or corner anywhere (run a tissue along every edge) | |
| A8 | Mass, complete | Record it. Model says about 113 g (unit) and 167 g (whole device) | |

## B. Electrical, before closing the case

| # | Check | How | Pass when | Result |
|---|---|---|---|---|
| B1 | No shorts | Meter between 5 V, 3.3 V and GND with the battery disconnected | Open circuit on every pair | |
| B2 | Cell polarity and protection | Meter on each cell lead | 3.5 to 4.2 V, right polarity; protection cuts out when shorted through a 1 ohm resistor | |
| B3 | Boost output | Battery connected, Pi disconnected | 5.0 to 5.25 V | |
| B4 | Charging | USB-C in, USB power meter | Charge current 0.5 to 1 A, falls to zero when full, cells stay under 45 °C | |
| B5 | Idle and peak current | Pi running, then reading aloud with the light ring on | Record both. The charger board in the model is listed at 1 A on its 5 V output, and the two packs at 1.6 A together: the peak must stay under both with 30% spare | |
| B6 | Brown-out | Speaker at full volume, light ring on, camera capturing | No reboot, no under-voltage warning (`vcgencmd get_throttled` returns `0x0`) | |

## C. Pi, pins and peripherals

| # | Check | How | Pass when | Result |
|---|---|---|---|---|
| C1 | Camera detected | `rpicam-hello --list-cameras` | IMX708 listed | |
| C2 | Sound card | `aplay -l`, `arecord -l` | Card present for playback and capture | |
| C3 | Amp and mute pins free | `pinctrl get 16,25` before the app starts | No kernel consumer on either pin | |
| C4 | Speaker | `speaker-test -D default -c2 -t sine -f 440` | Clean tone, no buzz | |
| C5 | Microphones | `arecord -D mic_in -f S16_LE -r 16000 -c 1 -d 5 t.wav && aplay t.wav` | Speech clear at 40 cm, peaks near -12 dBFS | |
| C6 | Fuel gauge | `i2cdetect -y 1` | Address 0x36 answers | |
| C7 | Every input pin | `pinctrl get 5,6,13,26,23,24,16,7,8` while pressing each control | Each pin goes low when pressed, high when released | |
| C8 | Every output pin | Drive 17, 27, 22, 4, 12, 25, 11 high one at a time | The right dot, the light ring, the amp and the motor respond | |
| C9 | Battery dot at boot | Watch GPIO 4's LED during boot | Dark until the app starts (if it glows, see the pin map note) | |

## D. Software on the device

| # | Check | How | Pass when | Result |
|---|---|---|---|---|
| D1 | Test suite on the laptop | `python -m pytest -q` with `gpiozero` installed | 72 passed (54 passed and 1 skipped without `gpiozero`) | |
| D2 | Offline demo | `python -m sensebook --mode dev --provider mock --fake-camera --silent` | Reads, flips, quizzes, announces battery | |
| D3 | Device mode starts | `python -m sensebook --mode device --provider gemini` | "SenseBook ready" spoken, web app opens on the LAN | |
| D4 | Each button: tap and hold | Ask, Play/Pause, Back, Forward, Vol+, Vol- | Tap and hold actions match the README table | |
| D5 | Mic mute | Slide the switch | "Microphone off" spoken, orange flag shows, Ask records nothing | |
| D6 | Headphones | Plug in, unplug | "Headphones", speaker silent; "Speaker" on unplug | |
| D7 | Hub sensor | Swing the rear leg out, then fold it away, with `hardware.hub_active_low: false` | "Attached" plus a buzz when the leg is out; "Detached" and pause when it is folded away | |
| D8 | Battery announcements | Run down, or use a bench supply on the gauge | Spoken at 20% and at 10% | |
| D9 | Real AI call | A Gemini key in `.env`, one real textbook page | Page read correctly, Ask answered | |

## E. Camera and optics

| # | Check | How | Pass when | Model says | Result |
|---|---|---|---|---|---|
| E1 | Lens height | Ruler from the page to the lens, stick down | 114 to 120 mm | 117 mm | |
| E2 | Coverage, textbook | Open a 37 x 24.5 cm spread, capture | All four corners inside the frame | 3.5% margin | |
| E3 | Corner vignetting | Same capture, look at the corners | No dark arc from the bezel | the lens front sits in the bezel with nothing in front of the glass, so none is expected | |
| E4 | Sharpness, far edge | Read 10-point text at the reader-side edge | Readable after correction | about 75 dpi at the far edge | |
| E5 | Stick up | Pull to 18 cm, capture a 46 x 30 cm spread | Corners inside the frame | 18% margin | |
| E6 | Light ring glare | Glossy page, ring at 40% | No hot spot over text | not modelled | |
| E7 | Lens calibration | `scripts/calibrate_camera.py` with a 9x6 board | Reprojection error under 1 pixel | not modelled | |
| E8 | Own parts in view | Capture with no book | No stick, hub, lug or bezel inside the frame; blades only at the top edge | not modelled: the lens sees 152° corner to corner | |

## F. Mechanics

| # | Check | How | Pass when | Model says | Result |
|---|---|---|---|---|---|
| F1 | Grip, 30 books | Attach to 30 books from 3 mm to 60 mm thick | Holds every one, no page marked | not modelled | |
| F2 | Page turn | Turn 50 pages fast, on a table and in the hand | No page touches the unit, stick or blades | unit front 12 mm behind the top edge | |
| F3 | Blade catch | Flush-cut paperbacks | Pages near the spine do not catch on the blade bend | not modelled | |
| F4 | In the hand | Hold the book at 30°, 45°, 60°, 90°; shake gently | Unit moves under 5 mm and returns; no slip | blade root stress 198 to 377 MPa (shim yield about 965 MPa) | |
| F5 | Tripod tilt, no book | Tilt the table slowly until it tips, each direction | Stands to at least 12° | tips at 15.5° (sideways first) | |
| F6 | Tripod push, no book | Push the unit sideways with a small spring scale | Takes at least 0.25 N | 0.33 N | |
| F7 | Tripod, stick up | Same as F5 and F6 with the stick at 18 cm | Record. This is the weak case | tips at 9.9°, 0.21 N | |
| F8 | Telescope | Pull to full length, wobble the unit | Under 2 mm play at the unit | 11.5 mm tube overlap at 18 cm, which is short | |
| F9 | Tilt joint | Set the angle, tap the unit | Holds its angle | not modelled | |
| F10 | Folded size | Fold legs up, measure | Record | 93 x 38 x 170 mm (the README says about 10 x 4 x 3.5 cm) | |
| F11 | Drop | 50 cm onto a wooden floor, unit and legs | Still works, nothing cracked | not modelled | |
| F12 | Rear-leg springs | Clamp a thin paperback, a hardcover and a 33 mm book; spring scale on the pad | Pad presses with 2 to 4 N; neither spring wound past 94° | 2.5 to 3.8 N; up to 96% of the stock spring's limit on the thinnest book | |
| F13 | Hub cord | Pull the stick up and down 50 times; tilt the unit through its range 50 times | Cord does not snag, pinch or pull tight; sensor still reads | not modelled | |

## G. Heat and battery

| # | Check | How | Pass when | Result |
|---|---|---|---|---|
| G1 | Pi temperature | 30 minutes reading aloud in a 30 °C room, `vcgencmd measure_temp` | Under 75 °C, no throttling | |
| G2 | Case temperature | Same run, thermometer on the back cover and over the cells | Back under 45 °C, cells under 40 °C | |
| G3 | Running time | Full charge, reading aloud at mid volume, light at 40% | Record. The plan says about 5 hours; the documented packs give 1,600 mAh, not the 2,000 mAh in the plan | |
| G4 | Charge time | Empty to full | Record | |
| G5 | Left in a hot place | 2 hours at 45 °C, powered off | No swelling, starts normally | |

## H. Accessibility

| # | Check | How | Pass when | Result |
|---|---|---|---|---|
| H1 | Find the controls by touch | Eyes closed, name each control | All eight found and named in under 30 seconds | |
| H2 | Attach by touch | 3 blind testers, 10 books each | Attached alone in under 15 seconds | |
| H3 | Spoken guidance | Attach upside down, then too close | "Book upside down" and the move-the-book prompt are spoken | |

## I. Privacy

| # | Check | How | Pass when | Result |
|---|---|---|---|---|
| I1 | Sending dot | Watch the third dot during a capture and an Ask | Lit whenever a picture or audio leaves the device, dark otherwise | |
| I2 | Mic mute is real | Mute on, hold Ask, speak | Nothing recorded, nothing sent | |
| I3 | Captures | Read five pages with `keep_captures: false` | `data/captures` stays empty | |

## J. First print: measure these fits

The model has no clashes and every gap is at or above its drawn clearance, but a print is only good to about 0.2 mm. Print the front shell, the back cover and the hub first, then measure these with calipers and feeler gauges before printing the rest. Drawn values are from the [fit report](../../design/cad/out/FIT_REPORT.md).

| # | Fit | How to measure | Drawn | Result |
|---|---|---|---|---|
| J1 | Back cover tongue in the front shell | Feeler gauge between the tongue and the wall, four sides | 0.15 mm clear all round; cover seats flush | |
| J2 | Button caps in their openings (Ask, three bars, two volume) | Drop each in; feeler gauge at the edge | 0.15 mm per side; each falls back under its own weight | |
| J3 | Mute slider in its slot | Slide end to end | 0.15 mm per side; 1.6 mm of travel | |
| J4 | Lens opening in the facet | Calipers across | 24.0 mm; the 23.8 mm diffuser pushes in by hand | |
| J5 | Lens rim in the bezel | Fit the camera; feeler gauge round the rim | 0.2 mm all round; lens front 0.4 mm inside the facet surface | |
| J6 | Camera board on its two posts and two cradle ribs | Seat the board, sight along the lens axis | Board flat on the post tops; lens square to the facet | |
| J7 | Pi on the four cover pins | Press the board on | Pins 2.55 mm in 2.75 mm holes; board flat on the four posts | |
| J8 | Cell pockets | Slide both packs in with their foam | 10.5 mm deep pocket; 0.4 mm to the camera board; 3.5 mm above the packs | |
| J9 | USB-C opening and headphone hole | Fit the two boards, look from outside | 0.2 mm all round each connector | |
| J10 | DAC board against the left wall | Feeler gauge | 0.3 mm to the wall; 0.3 mm to the lip of the lower volume cap | |
| J11 | Stick bore in the hub | Calipers; push the 10 mm tube in | 10.16 mm drawn; drill 10.1 mm; a firm push fit | |
| J12 | Hinge and knuckle pin holes | Drill, then try the pins | 2.0 mm pin turns freely in the leg, tight in the hub; 1.6 mm pin likewise | |
| J13 | Spring pockets in the hub | Drop a spring into each | 8.0 mm pocket for a 7.5 mm spring; 0.25 mm around it | |
| J14 | Lead groove in the hub and notch in the tube foot | Lay the 0.9 mm lead in | Groove 1.2 mm wide; lead sits below the surface; the inner tube does not pinch it | |
| J15 | Tilt lugs over the joint head | Fit the M3 screw | 0.3 mm each side of the tongue; holds its angle when the nut is snug | |
| J16 | Thin walls | Look at the camera posts, the cover tongue (0.9 mm) and the lugs | Printed solid, no gaps between perimeters | |

## Pass criteria from the product specification (section 9)

These are the pilot gates. This checklist feeds them; it does not replace them.

- About 5 hours of battery on the prototype.
- The tri-grip holds all 30 test books without slipping, and a turning page clears the unit.
- Blind testers attach it alone in under 15 seconds.
- Reading resumes within 1 second after a page settles; no capture ever shows a hand over text.
- No data leaves the device without the capture indicator lit.
