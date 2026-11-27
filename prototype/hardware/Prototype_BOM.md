# SenseBook prototype: bill of materials

> **Every price here is an estimate for planning.** "Listed" means a price seen on a Bangladeshi shop page on 27 November 2026; it is not a quote, and stock changes daily. "Est." means our own estimate, with no listing behind it. Nothing has been ordered. Exchange rate used: Tk 124.75 per US dollar (Bangladesh Bank sheet effective 26 November 2026).

One unit, built by hand from breakout boards and 3D-printed parts. This is the P1 "dev-kit, works-like" build in the venture plan, not the production design.

## The short version

| | Per unit (Tk) |
|---|---|
| Parts with a Bangladesh listing | 9,030 |
| Camera with M12 lens, imported (list price, before shipping and duty) | 5,260 |
| Parts with no listing (our estimates) | 2,210 |
| **Total, estimate** | **about 16,500** (about US$132) |
| Without the optional fuel gauge | about 15,200 |

- The venture plan's pilot parts cost is US$101.50 (about Tk 12,660). A single hand-built unit at Dhaka retail prices comes out roughly 30% higher, mainly because the Pi Zero 2 W sells for about Tk 4,450 in Dhaka against a US$15 list price.
- Six units for P1: about Tk 1 lakh in parts (estimate), before the camera's shipping and duty.
- Shipping, duty and VAT on imported parts are **not** included. We found no official rate for a personal import of a camera board.

## Parts

Fit check: **OK** = the size in the 3D model is the size of this part. **Check** = the part sold locally is a different size or its size is not given, so it must be measured against the model before buying six.

### Compute and camera

| # | Part | Qty | Where | Price each (Tk) | Basis | Fit check |
|---|---|---|---|---|---|---|
| 1 | Raspberry Pi Zero 2 W | 1 | [CityTech BD](https://www.citytechbd.com/raspberry-pi-zero-2-w), in stock. RoboticsBD (4,515) and TechShopBD (4,520) out of stock | 4,449 | Listed | OK |
| 2 | 12 MP IMX708 camera with M12 mount and 120° lens (Arducam B0310) | 1 | Not found in Bangladesh. [RobotShop](https://www.robotshop.com/products/arducam-12mp-imx708-hdr-120-wide-angle-camera-module-w-m12-lens-rpi), US$42.16 | 5,260 | List price, converted | **Check:** board size against the 24 x 25 mm space; lens length against 15 mm |
| 3 | Pi Zero camera cable, 22-pin to 15-pin | 1 | [RoboticsBD](https://store.roboticsbd.com/raspberry-pi/1156-raspberry-pi-zero-camera-adapter-robotics-bangladesh.html), in stock | 250 | Listed | **Check:** 16 cm is long; it has to fold twice |
| 4 | microSD card, 32 GB, A1 | 1 | [Star Tech](https://www.startech.com.bd/sandisk-ultra-32gb-100mbps-micro-sdhc-uhs-i-memory-card): Apacer 1,000, SanDisk Ultra 1,600 to 1,700 | 1,000 | Listed | OK |

For the first bench tests a standard Camera Module 3 also works (RoboticsBD lists the standard one at Tk 6,880, out of stock, and the Wide at Tk 12,170). It does not fit the lens facet and sees less of the page.

### Audio

| # | Part | Qty | Where | Price each (Tk) | Basis | Fit check |
|---|---|---|---|---|---|---|
| 5 | MAX98357A I2S amplifier breakout | 1 | [RoboticsBD](https://store.roboticsbd.com/electronics-module/2919-max98357a-i2s-dac-class-d-mono-amplifier-module-robotics-bangladesh.html), in stock; BDTronics 450 | 450 | Listed | OK (18 x 18 mm) |
| 6 | INMP441 I2S microphone module | 2 | [RoboticsBD](https://store.roboticsbd.com/sensors/1753-inmp441-compatible-omnidirectional-microphone-module-robotics-bangladesh.html) 244 ("compatible"); [BDTronics](https://www.bdtronics.com/inmp441-omnidirectional-microphone-module.html) 380 | 244 | Listed | **Check:** common modules are 14 mm round; the model has 9 x 8 mm |
| 7 | PCM5102A I2S DAC board | 1 | [RoboticsBD](https://store.roboticsbd.com/audio-voice-piezo-buzzer-speech-module/4097-pcm5102a-i2s-dac-sound-card-board-with-phat-35mm-stereo-output-black-robotics-bangladesh.html), out of stock | 655 | Listed | **Check:** this board carries its own jack and is larger than the 20 x 12 mm in the model |
| 8 | Micro speaker, 8 ohm, 1 W | 1 | [RoboticsBD](https://store.roboticsbd.com/robotics-parts/2813-15w-8ohm-micro-speaker-diy-robotics-bangladesh.html), in stock | 50 | Listed | **Check:** the page gives two different sizes; the model has 20 x 14 x 4 mm |
| 9 | 3.5 mm stereo socket | 1 | [electronics.com.bd](https://electronics.com.bd/horizontal-3-5mm-audio-socket-stereo), in stock | 18 | Listed | **Check:** needs a switch contact for jack detect; not stated on the page |

### Power

| # | Part | Qty | Where | Price each (Tk) | Basis | Fit check |
|---|---|---|---|---|---|---|
| 10 | LiPo cell, 3.7 V, about 1,000 mAh, size 102535, with protection | 2 | No 102535 listing found in Bangladesh. Nearest: [electronics.com.bd](https://electronics.com.bd/lithium-li-polymer-1000mah-rechargeable-battery-1-cell-3-7v) 340 (no size given); RoboticsBD 510 (50 x 30 x 5 mm) | 450 | Est. | **Check:** the unit is laid out around 10 x 25 x 35 mm cells with 1.4 mm to spare |
| 11 | USB-C charger + 5 V boost module | 1 | [RoboticsBD](https://store.roboticsbd.com/power-module-adapter/4608-type-c-usb-5v-2a-power-bank-boost-converter-charger-module.html), in stock | 95 | Listed | **Check:** size and chip not given; the model allows 26 x 16 mm with USB-C on the short edge |
| 12 | MAX17048 fuel gauge breakout (optional) | 1 | [RoboticsBD](https://store.roboticsbd.com/sensors/4096-max17048-li-ion-battery-fuel-gauge-and-monitor-module-stemma-qt-qwiic-compatible-robotics-bangladesh.html), 3 left | 1,297 | Listed | **Check:** STEMMA-size board is larger than the 13 x 10 mm in the model |
| 13 | Slide switch, in the battery lead | 1 | [RoboticsBD](https://store.roboticsbd.com/electronic-switches/146-spdt-slide-switch-200mm-spacing-robotics-bangladesh.html) | 10 | Listed | Not in the 3D model yet |

### Controls, lights, motor

| # | Part | Qty | Where | Price each (Tk) | Basis | Fit check |
|---|---|---|---|---|---|---|
| 14 | Tactile switch | 6 | [BDTronics](https://www.bdtronics.com/mini-push-button-tactile-switch-4-pin-6mm-6mm-4-5mm.html), 6 x 6 x 4.5 mm | 5 | Listed | **Check:** the model needs low-profile 4 x 4 x 1.6 mm switches, not found locally |
| 15 | Slide switch, mic mute | 1 | RoboticsBD, as item 13 | 10 | Listed | **Check:** the model has a 7 x 3 x 3.6 mm side-slide part |
| 16 | Detector switch for the hub | 1 | Not found | 20 | Est. | Check |
| 17 | Coin vibration motor, 10 mm, 3 V | 1 | [electronics.com.bd](https://electronics.com.bd/components-price-in-Bangladesh/vibration-micro-motor-3v-10mmx3mm-coin-shape), in stock | 115 | Listed | OK |
| 18 | White LED, 0603, for the status dots | 4 | [electronics.com.bd](https://electronics.com.bd/white-0603-smd-led-diodes-light) | 5 | Listed | OK |
| 19 | Light ring: 8 warm-white LEDs on a small ring board | 1 | Warm-white SMD LEDs not found locally; ring board made by hand or ordered | 150 | Est. | OK |
| 20 | MOSFET, transistor, diode, resistors, capacitors | 1 set | Any Dhaka component shop | 100 | Est. | n/a |

### Mechanical

| # | Part | Qty | Where | Price each (Tk) | Basis | Fit check |
|---|---|---|---|---|---|---|
| 21 | PETG filament for 17 printed parts (about 47 g) | 47 g | [BDTronics](https://www.bdtronics.com/sunlu-petg-1kg-1-75mm-filament-for-3d-printer.html), Tk 1,899 per kg | 89 | Listed, by weight | OK |
| 22 | TPU filament for the pad (about 2 g) | 2 g | [BDTronics](https://www.bdtronics.com/sunlu-1kg-1-75mm-flexible-tpu-filament-for-3d-printer.html), Tk 3,200 per kg | 6 | Listed, by weight | OK |
| 23 | Spring-steel shim, 0.4 mm, for two blades (8 x 115 mm each) | 1 strip | No online source found. Try the hardware market on Nawabpur Road, or a 0.4 mm feeler-gauge strip | 200 | Est. | OK |
| 24 | Stainless tube 10 x 0.5 mm and 8 x 0.5 mm, 110 mm of each | 1 pair | No online source found. A selfie stick or radio aerial is a workable donor | 300 | Est. | OK |
| 25 | Torsion spring, 1.0 mm wire, 5 coils, 6 mm inside | 1 | Not found | 30 | Est. | OK |
| 26 | Hinge pins: 2 x 25 mm and 1.6 x 31 mm steel | 1 set | Hardware shop | 20 | Est. | OK |
| 27 | Screws: M2 x 8 self-tapping (4), M2 x 6 (2), M1.6 x 5 (4), M3 x 18 and a thumb nut | 1 set | Hardware shop | 80 | Est. | OK |
| 28 | Lens window, 14 mm clear disc, and bezel ring | 1 | Cut from acrylic sheet | 50 | Est. | OK |
| 29 | Aluminium sheet 40 x 21 x 1 mm and a 15 mm thermal pad | 1 | Hardware shop | 80 | Est. | OK |
| 30 | 2-wire cord for the hub sensor, about 300 mm | 1 | Component shop | 30 | Est. | OK |
| 31 | Wire (30 AWG), heat-shrink, foam tape, Kapton, glue | 1 set | Component shop | 250 | Est. | n/a |

Printing through a service instead of an own printer: we could not confirm a per-gram price on any page we opened. Search results suggested about Tk 5 to 8 per gram for PLA and PETG; treat that as unverified.

## What this list shows

1. **Seven parts need a size check before buying for six units.** The 3D model was laid out around typical sizes. The cells, the DAC board, the fuel gauge, the microphones, the charger module and the tactile switches sold in Dhaka are different sizes or do not state a size. The unit has under 1.5 mm of spare room in several places, so each of these can force a layout change.
2. **The cell size is the main sourcing gap.** No Bangladeshi shop we found lists a 102535 cell. Either import that size, or re-lay the unit around a size that is sold here.
3. **The camera is the only part with no local source at all.** It also sets the page coverage, so it should be ordered first.
4. **Three mechanical items need a market visit:** spring-steel shim, thin-wall tube and the torsion spring. None has an online price.
5. **The Pi Zero 2 W is the largest single cost** and only one of four shops had it in stock.

## Not included

- Shipping, duty and VAT on the imported camera. One forwarder's page says duty and taxes on consumer electronics often total 50 to 60%; we found no official source, so treat that as unverified.
- Tools, the 3D printer, a soldering station, a multimeter.
- Spares. Buy one extra of every part under Tk 500, and two extra cells.
- Packaging, cable and quick-start guide (in the venture plan's bill of materials at US$2).

## How this compares with the venture plan

| | Venture plan, pilot (100 units) | This list (1 unit, Dhaka retail) |
|---|---|---|
| Compute | US$15.00 | Tk 4,449 (about US$36) |
| Camera with M12 lens | US$30.00 | US$42.16 list |
| Audio, including the speaker | US$11.50 | Tk 1,661 (about US$13) |
| Power, including battery | US$9.00 | Tk 2,302 with the fuel gauge (about US$18) |
| Whole unit | US$101.50 | about Tk 16,500 (about US$132) |

The plan's figure is for 100 units bought through distributors. This list is for one unit bought over the counter. The gap is expected, but the Pi price in Dhaka is worth a quote from an approved reseller before the pilot budget is fixed.
