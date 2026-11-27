# SenseBook prototype: bill of materials

> **Every price here is an estimate for planning.** "Listed" means a price seen on a Bangladeshi shop page on 27 November 2026; it is not a quote, and stock changes daily. "Est." means our own estimate, with no listing behind it. Nothing has been ordered. Exchange rate used: Tk 124.75 per US dollar (Bangladesh Bank sheet effective 26 November 2026).

One unit, built by hand from breakout boards and 3D-printed parts. This is the P1 "dev-kit, works-like" build in the venture plan, not the production design.

**How to read this list.** The 3D model is drawn around one documented part for each line, at the sizes its maker publishes. That part and its datasheet are in the column "Drawn in the model as". The full size table, with the date and the estimates, is in [design/cad/SOURCES.md](../../design/cad/SOURCES.md). Where the part on sale in Dhaka is a different make, the last column says so: either import the documented part, or measure the local one and change `sb_params.py` before printing.

## The short version

| | Per unit (Tk) |
|---|---|
| Parts with a Bangladesh listing | 9,026 |
| Camera with M12 lens, imported (list price, before shipping and duty) | 5,260 |
| Parts with no listing (our estimates) | 2,240 |
| **Total, estimate** | **about 16,500** (about US$132) |
| Without the optional fuel gauge | about 15,200 |

- These totals use the Dhaka listings. **Eight of those listings are not the same make as the part the model is drawn around** (amp, microphones, DAC, speaker, charger, tactile switches, mute switch, motor). We did not look up prices for importing the exact documented parts.
- The venture plan's pilot parts cost is US$101.50 (about Tk 12,660). A single hand-built unit at Dhaka retail prices comes out roughly 30% higher, mainly because the Pi Zero 2 W sells for about Tk 4,450 in Dhaka against a US$15 list price.
- Six units for P1: about Tk 1 lakh in parts (estimate), before the camera's shipping and duty.
- Shipping, duty and VAT on imported parts are **not** included. We found no official rate for a personal import of a camera board.

## Parts

### Compute and camera

| # | Part | Qty | Drawn in the model as (source of the sizes) | Where, Bangladesh | Price each (Tk) | Basis | Same part? |
|---|---|---|---|---|---|---|---|
| 1 | Raspberry Pi Zero 2 W | 1 | 65 x 30 mm board, from the [Raspberry Pi mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf). Connector and chip heights are estimates | [CityTech BD](https://www.citytechbd.com/raspberry-pi-zero-2-w), in stock. RoboticsBD (4,515) and TechShopBD (4,520) out of stock | 4,449 | Listed | Yes |
| 2 | 12 MP IMX708 camera with M12 mount and 120° lens | 1 | Arducam B0310: board 25.0 x 23.86 mm, lens rim 14.8 mm, 17.05 mm from the back of the board to the lens front, from [Arducam's 3D file](https://www.arducam.com/downloads/3D_Model/B0310.STEP) | Not found in Bangladesh. [RobotShop](https://www.robotshop.com/products/arducam-12mp-imx708-hdr-120-wide-angle-camera-module-w-m12-lens-rpi), US$42.16 | 5,260 | List price, converted | Yes |
| 3 | Pi Zero camera cable, 22-pin to 15-pin | 1 | 150 mm, 16 mm and 11.5 mm wide ends, from the [Raspberry Pi cable drawing](https://pip-assets.raspberrypi.com/categories/903-flexible-printed-circuit-fpc-cable-for-display-and-camera/documents/RP-008145-DS-1-mini-display-cable-200mm-reference-drawing.pdf). The route is 79 mm; the rest folds behind the Pi | [RoboticsBD](https://store.roboticsbd.com/raspberry-pi/1156-raspberry-pi-zero-camera-adapter-robotics-bangladesh.html), in stock | 250 | Listed | Check the length: 150 to 160 mm is fine |
| 4 | microSD card, 32 GB, A1 | 1 | Standard 15 x 11 x 1 mm card ([Kingston sheet](https://www.kingston.com/datasheets/SDCS2_us.pdf)) | [Star Tech](https://www.startech.com.bd/sandisk-ultra-32gb-100mbps-micro-sdhc-uhs-i-memory-card): Apacer 1,000, SanDisk Ultra 1,600 to 1,700 | 1,000 | Listed | Yes |

For the first bench tests a standard Camera Module 3 also works (RoboticsBD lists the standard one at Tk 6,880, out of stock, and the Wide at Tk 12,170). It does not fit the lens facet and sees less of the page.

### Audio

| # | Part | Qty | Drawn in the model as (source of the sizes) | Where, Bangladesh | Price each (Tk) | Basis | Same part? |
|---|---|---|---|---|---|---|---|
| 5 | MAX98357A I2S amplifier breakout | 1 | Adafruit 3006: 19.05 x 17.78 x 3.0 mm ([board file](https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout)) | [RoboticsBD](https://store.roboticsbd.com/electronics-module/2919-max98357a-i2s-dac-class-d-mono-amplifier-module-robotics-bangladesh.html), in stock; BDTronics 450 | 450 | Listed | **No.** Generic module, about 18 x 18 mm. Measure it; leave off any screw terminal |
| 6 | I2S MEMS microphone breakout | 2 | Adafruit 3421 (SPH0645LM4H): 16.51 x 12.70 x 1.8 mm, sound hole through the board ([board file](https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB)) | INMP441 modules: [RoboticsBD](https://store.roboticsbd.com/sensors/1753-inmp441-compatible-omnidirectional-microphone-module-robotics-bangladesh.html) 244 ("compatible"); [BDTronics](https://www.bdtronics.com/inmp441-omnidirectional-microphone-module.html) 380 | 244 | Listed | **No.** The local modules are 14 mm round. Import the Adafruit board or re-draw the microphone seats |
| 7 | PCM5102 I2S DAC board with 3.5 mm jack | 1 | Adafruit 6250: 30.48 x 20.32 mm, 6.2 mm tall, 32.5 mm long with the jack ([board file](https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB)). Jack body size is an estimate | [RoboticsBD](https://store.roboticsbd.com/audio-voice-piezo-buzzer-speech-module/4097-pcm5102a-i2s-dac-sound-card-board-with-phat-35mm-stereo-output-black-robotics-bangladesh.html), out of stock | 655 | Listed | **No.** A different board with its own jack. Measure it, or import the Adafruit one |
| 8 | Enclosed micro speaker, 8 ohm | 1 | Same Sky CES-20134-088PM: 20 x 13 x 4.87 mm, 8 ohm, 0.8 W ([datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf)) | [RoboticsBD](https://store.roboticsbd.com/robotics-parts/2813-15w-8ohm-micro-speaker-diy-robotics-bangladesh.html), in stock | 50 | Listed | **No.** The page gives two different sizes. Measure before buying six |

The headphone jack is the one on the DAC board, so there is no separate socket in this list. We could not confirm that this jack has a plug-detect contact (see the [pin map](pinmap.md)).

### Power

| # | Part | Qty | Drawn in the model as (source of the sizes) | Where, Bangladesh | Price each (Tk) | Basis | Same part? |
|---|---|---|---|---|---|---|---|
| 9 | LiPo cell pack, 3.7 V, with protection board | 2 | Akyga LP902535: at most 9.5 x 26 x 37.5 mm, **800 mAh**, 0.8 A maximum discharge ([specification sheet](https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf)). The pocket is 10.5 mm thick, so a 10 mm "102535" pack of the same length and width also fits | No listing of this size found. Nearest: [electronics.com.bd](https://electronics.com.bd/lithium-li-polymer-1000mah-rechargeable-battery-1-cell-3-7v) 340 (no size given); RoboticsBD 510 (50 x 30 x 5 mm, does not fit) | 450 | Est. | **No local source.** Import, or re-draw the unit around a size sold here |
| 10 | USB-C LiPo charger with 5 V boost | 1 | Adafruit 6106 (bq25185): 29.21 x 19.05 mm, **1 A** at 5 V ([board file](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB)). Height is an estimate | [RoboticsBD](https://store.roboticsbd.com/power-module-adapter/4608-type-c-usb-5v-2a-power-bank-boost-converter-charger-module.html), in stock | 95 | Listed | **No.** Generic power-bank module, size and chip not given. The USB-C opening is cut for the Adafruit board |
| 11 | MAX17048 fuel gauge breakout (optional) | 1 | Adafruit 5580: 25.40 x 20.32 mm, 7.2 mm tall as sold ([board file](https://github.com/adafruit/Adafruit-MAX17048-PCB)). **Fits only with its two sockets removed** (2.8 mm, an estimate) | [RoboticsBD](https://store.roboticsbd.com/sensors/4096-max17048-li-ion-battery-fuel-gauge-and-monitor-module-stemma-qt-qwiic-compatible-robotics-bangladesh.html), 3 left | 1,297 | Listed | Probably (STEMMA QT form). Check it is 25.4 x 20.3 mm |
| 12 | Slide switch, in the battery lead | 1 | **Not in the 3D model.** No place has been drawn for a power switch | [RoboticsBD](https://store.roboticsbd.com/electronic-switches/146-spdt-slide-switch-200mm-spacing-robotics-bangladesh.html) | 10 | Listed | Open item |

Two 800 mAh packs give 1,600 mAh. The product documents say 2,000 mAh. Each pack allows 0.8 A, so 1.6 A for the pair.

### Controls, lights, motor

| # | Part | Qty | Drawn in the model as (source of the sizes) | Where, Bangladesh | Price each (Tk) | Basis | Same part? |
|---|---|---|---|---|---|---|---|
| 13 | Low-profile tactile switch | 6 | Alps Alpine SKQGABE010: 5.2 x 5.2 x 1.5 mm ([product page](https://tech.alpsalpine.com/e/products/detail/SKQGABE010/)) | [BDTronics](https://www.bdtronics.com/mini-push-button-tactile-switch-4-pin-6mm-6mm-4-5mm.html), 6 x 6 x 4.5 mm | 5 | Listed | **No.** The local switch is 3 mm too tall. Import a 1.5 mm switch |
| 14 | Side-actuated slide switch, mic mute | 1 | Shouhan MSK12C02: 8 x 2.8 x 1.4 mm ([datasheet](https://cdn.shopify.com/s/files/1/0227/9171/6941/files/MSK12C02.pdf)). Lever width is an estimate | RoboticsBD, as item 12 | 10 | Listed | **No.** The listed switch is a larger through-hole part |
| 15 | Detector switch for the hub | 1 | Alps Alpine SPVE110200: 3.4 x 3.0 x 2.3 mm ([datasheet](https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF)) | Not found | 20 | Est. | Import |
| 16 | Coin vibration motor, 10 mm, 3 V | 1 | Vybronics VC1026B002F: 10 mm across, 2.7 mm thick ([datasheet](https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VC1026B002F-datasheet.pdf)) | [electronics.com.bd](https://electronics.com.bd/components-price-in-Bangladesh/vibration-micro-motor-3v-10mmx3mm-coin-shape), in stock | 115 | Listed | **No.** Listed as 10 x 3 mm. It should still fit: nothing sits behind it within 0.5 mm |
| 17 | White LED, 0603, for the status dots | 4 | Wurth 150060WS75000: 1.6 x 0.8 x 0.8 mm ([datasheet](https://www.we-online.com/components/products/datasheet/150060WS75000.pdf)) | [electronics.com.bd](https://electronics.com.bd/white-0603-smd-led-diodes-light) | 5 | Listed | Any 0603 |
| 18 | Light ring: 6 warm-white 2835 LEDs on a ring board, 23.8 mm outside, 17.8 mm inside | 1 | Cree J Series 2835, 3 V, CRI 90 ([datasheet](https://downloads.cree-led.com/files/ds/j/JSeries-2835-3V-Consolidated.pdf)). The ring board is our own and has no layout yet | Warm-white 2835 LEDs not found locally; ring board made by hand or ordered | 150 | Est. | To be made |
| 19 | MOSFET, transistor, diode, resistors, capacitors | 1 set | Not drawn | Any Dhaka component shop | 100 | Est. | n/a |

### Mechanical

| # | Part | Qty | Drawn in the model as (source of the sizes) | Where, Bangladesh | Price each (Tk) | Basis |
|---|---|---|---|---|---|---|
| 20 | PETG filament for 17 printed parts | 54 g | [Drawings](../../design/drawings/SenseBook_drawings.pdf) and [print notes](../../design/cad/out/PRINT_NOTES.md) | [BDTronics](https://www.bdtronics.com/sunlu-petg-1kg-1-75mm-filament-for-3d-printer.html), Tk 1,899 per kg | 102 | Listed, by weight |
| 21 | TPU filament for the pad | 1.7 g | Drawing of `rear_leg_pad` | [BDTronics](https://www.bdtronics.com/sunlu-1kg-1-75mm-flexible-tpu-filament-for-3d-printer.html), Tk 3,200 per kg | 5 | Listed, by weight |
| 22 | Stainless spring shim, full hard, 0.4 mm, for two blades (8 mm wide, about 115 mm each) | 1 strip | 300-series full-hard shim, yield about 965 MPa ([RS PRO sheet](https://docs.rs-online.com/b176/A700000015372078.pdf)); cut from the DXF patterns | No online source found. Try the hardware market on Nawabpur Road, or a 0.4 mm feeler-gauge strip | 200 | Est. |
| 23 | Stainless tube 10 x 0.5 mm, 103.5 mm, and 8 x 0.5 mm, 105.5 mm | 1 pair | 10 x 0.5 mm tube as on a [seller page](https://www.harfington.com/products/p-1630275). **No seller confirmed for 8 x 0.5 mm** | No online source found. A selfie stick or radio aerial is a workable donor | 300 | Est. |
| 24 | Torsion spring, 1.0 mm wire, 5.5 mm inside, 6.5 coils | 2 | Gutekunst T-18510: 111.87 N·mm allowed at 93.82° ([catalogue page](https://www.federnshop.com/en/products/torsion_springs/t-18510l.html)). One left-hand and one right-hand wound | Not found | 30 | Est. |
| 25 | Hinge pins: 2.0 x 28.6 mm and 1.6 x 30.8 mm steel | 1 set | Our own sizes | Hardware shop | 20 | Est. |
| 26 | Screws: ST2.2 x 6.5 pan head tapping (6), M1.6 x 6 (2), M3 x 18 button head and a thumb nut | 1 set | ISO 7049 head 4.0 x 1.6 mm; ISO 7380 head 5.7 x 1.65 mm | Hardware shop | 80 | Est. |
| 27 | Lens bezel ring, 18 mm outside, 15.2 mm inside, 1.8 mm thick | 1 | Our own part: turned in aluminium, or printed | Workshop | 50 | Est. |
| 28 | Aluminium sheet 40 x 21 x 1 mm and a 15 x 15 mm soft thermal pad, about 2.5 mm thick | 1 | Our own sizes. Pad thickness depends on the Pi's chip height, which is an estimate | Hardware shop | 80 | Est. |
| 29 | 2-wire cord for the hub sensor, 0.9 mm across, about 420 mm | 1 | Route lengths in the [fit report](../../design/cad/out/FIT_REPORT.md): 304 mm coil, 51 mm in the unit, 16 mm in the joint, 26 mm in the hub | Component shop | 30 | Est. |
| 30 | Wire (30 AWG), heat-shrink, 0.7 mm foam tape, Kapton, glue | 1 set | Not drawn, except the main cable routes | Component shop | 250 | Est. |

Printing through a service instead of an own printer: we could not confirm a per-gram price on any page we opened. Search results suggested about Tk 5 to 8 per gram for PLA and PETG; treat that as unverified.

## What this list shows

1. **The model is exact to published sizes, but most of those parts are not on sale in Dhaka.** Eight electronic lines above are a different make locally. Each one either has to be imported or measured and re-drawn. The model is parametric, so a re-draw is a change in `sb_params.py` and a re-run, but it is still a new print.
2. **The cells are the main sourcing gap.** No Bangladeshi shop we found lists a pack near 9.5 x 26 x 37.5 mm.
3. **The camera has no local source at all.** It also sets the page coverage, so it should be ordered first.
4. **Battery capacity is below the documents.** The documented cell is 800 mAh, so two give 1,600 mAh, not 2,000 mAh.
5. **Four mechanical items need a market visit:** spring shim, thin-wall tube (the 8 mm size has no confirmed seller anywhere), the torsion springs and the pins.
6. **There is no power switch in the model yet.**
7. **The Pi Zero 2 W is the largest single cost** and only one of four shops had it in stock.

## Not included

- Shipping, duty and VAT on the imported camera. One forwarder's page says duty and taxes on consumer electronics often total 50 to 60%; we found no official source, so treat that as unverified.
- Tools, the 3D printer, a soldering station, a multimeter, calipers.
- Spares. Buy one extra of every part under Tk 500, and two extra cells.
- Packaging, cable and quick-start guide (in the venture plan's bill of materials at US$2).

## How this compares with the venture plan

| | Venture plan, pilot (100 units) | This list (1 unit, Dhaka retail) |
|---|---|---|
| Compute | US$15.00 | Tk 4,449 (about US$36) |
| Camera with M12 lens | US$30.00 | US$42.16 list |
| Audio, including the speaker | US$11.50 | Tk 1,643 (about US$13) |
| Power, including battery | US$9.00 | Tk 2,302 with the fuel gauge (about US$18) |
| Whole unit | US$101.50 | about Tk 16,500 (about US$132) |

The plan's figure is for 100 units bought through distributors. This list is for one unit bought over the counter. The gap is expected, but the Pi price in Dhaka is worth a quote from an approved reseller before the pilot budget is fixed.
