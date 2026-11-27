# SenseBook: where every part size comes from

Looked up on 27 Nov 2026. This table is written by `check_model.py` from `sb_params.py` (`PARTS`, `SRC`, `EST_WHY`), which is the single source of truth: the 3D model, the drawings and the bill of materials all read the same numbers.

**23 bought parts, 188 values, 25 of them estimates (marked EST).** An EST value is one no published source gives. It is listed at the end with the reason and how to measure it.

How to read the *basis* column:

- **drawing**: maker's drawing or datasheet, labelled
- **design**: maker's published board file
- **model**: measured on the maker's published 3D file
- **scaled**: measured from the 1:1 artwork in the maker's drawing (about ±0.1)
- **page**: maker's or seller's product page
- **EST**: no source found: our estimate, to be measured on the real part

No third-party 3D file is stored in this repository. Each part is modelled from the published dimensions below, and the drawing or file they were read from is cited. (Raspberry Pi drawings are open, but their STEP files may not be redistributed; Arducam's STEP file carries no stated licence; KiCad library models are CC-BY-SA.)

## Raspberry Pi Zero 2 W

Key in `sb_params.PARTS`: `pi`. Bodies in the model: `pi_gpio_pads`, `pi_zero_2w_chips`, `pi_zero_2w_connectors`, `pi_zero_2w_pcb`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 65 mm | drawing | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `wid` | 30 mm | drawing | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `corner_r` | 3 mm | drawing | [Raspberry Pi Zero mechanical drawing (same outline)](https://datasheets.raspberrypi.com/rpizero/raspberry-pi-zero-mechanical-drawing.pdf) |
| `hole_d` | 2.75 mm | drawing | [Raspberry Pi Zero mechanical drawing (same outline)](https://datasheets.raspberrypi.com/rpizero/raspberry-pi-zero-mechanical-drawing.pdf) |
| `hole_inset` | 3.5 mm | drawing | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `gpio_cx` | 32.5 mm | drawing | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `gpio_cy` | 26.5 mm | drawing | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `gpio_pitch` | 2.54 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `hdmi_cx` | 12.4 mm | drawing | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `hdmi_w` | 10.9 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `hdmi_d` | 7.5 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `hdmi_over` | 0.55 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `usb_cx1` | 41.4 mm | drawing | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `usb_cx2` | 54 mm | drawing | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `usb_w` | 8.1 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `usb_d` | 5.3 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `usb_over` | 1.2 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `sd_cy` | 16.9 mm | drawing | [Raspberry Pi Zero W mechanical drawing (same outline)](https://datasheets.raspberrypi.com/rpizero/raspberry-pi-zero-w-mechanical-drawing.pdf) |
| `sd_w` | 11.45 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `sd_x0` | 1.65 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `sd_x1` | 13.1 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `csi_cy` | 15 mm | drawing | [Raspberry Pi Zero W mechanical drawing (same outline)](https://datasheets.raspberrypi.com/rpizero/raspberry-pi-zero-w-mechanical-drawing.pdf) |
| `csi_w` | 16.1 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `csi_d` | 3.4 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `sip` | 15 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `sip_cx` | 27.35 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `sip_cy` | 14.05 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `can` | 12.2 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `can_cx` | 43.8 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `can_cy` | 13.6 mm | scaled | [Raspberry Pi Zero 2 W mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| `thick_total` | 5.3 mm | page | [Adafruit product page, Raspberry Pi Zero 2 W](https://www.adafruit.com/product/5291) |
| `mass_g` | 10 g | page | [Adafruit product page, Raspberry Pi Zero 2 W](https://www.adafruit.com/product/5291) |
| `pcb_t` | 1.2 mm | **EST** | No published source found: our estimate, to be measured |
| `hdmi_h` | 3.3 mm | **EST** | No published source found: our estimate, to be measured |
| `usb_h` | 2.8 mm | **EST** | No published source found: our estimate, to be measured |
| `sd_h` | 1.5 mm | **EST** | No published source found: our estimate, to be measured |
| `csi_h` | 1.3 mm | **EST** | No published source found: our estimate, to be measured |
| `sip_h` | 1.4 mm | **EST** | No published source found: our estimate, to be measured |
| `can_h` | 1.8 mm | **EST** | No published source found: our estimate, to be measured |

## Arducam B0310: 12 MP IMX708, M12 mount, 120 degree lens

Key in `sb_params.PARTS`: `cam`. Bodies in the model: `camera_board_imx708`, `camera_connector`, `camera_holder_m12`, `camera_lens_m12`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `board_w` | 25 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `board_h` | 23.862 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `pcb_t` | 1.6 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `corner_r` | 2 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `hole_d` | 2.2 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `hole_pitch_w` | 21 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `hole_pitch_h` | 12.5 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `hole_edge` | 2 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `axis_from_far_edge` | 6.98 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `holder_w` | 22 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `holder_d` | 14 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `holder_h` | 8.5 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `holder_screw_pitch` | 18 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `lens_thread_d` | 12 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `lens_head_d` | 17 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `lens_rim_d` | 14.8 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `back_to_rim` | 15.57 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `back_to_apex` | 17.05 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `holder_top_from_back` | 10.1 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `conn_w` | 17.6 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `conn_d` | 5.2 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `conn_h` | 2.05 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `conn_over` | 0.71 mm | model | [Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens](https://www.arducam.com/downloads/3D_Model/B0310.STEP) |
| `hfov_deg` | 120 ° | page | [Arducam B0310 product page (optics, listed size)](https://www.uctronics.com/arducam-12mp-imx708-hdr-120-wide-angle-camera-module-with-m12-lens-for-raspberry-pi.html) |
| `vfov_deg` | 66.7 ° | page | [Arducam B0310 product page (optics, listed size)](https://www.uctronics.com/arducam-12mp-imx708-hdr-120-wide-angle-camera-module-with-m12-lens-for-raspberry-pi.html) |
| `dfov_deg` | 152.2 ° | page | [Arducam B0310 product page (optics, listed size)](https://www.uctronics.com/arducam-12mp-imx708-hdr-120-wide-angle-camera-module-with-m12-lens-for-raspberry-pi.html) |
| `efl` | 2.87 mm | page | [Arducam B0310 product page (optics, listed size)](https://www.uctronics.com/arducam-12mp-imx708-hdr-120-wide-angle-camera-module-with-m12-lens-for-raspberry-pi.html) |
| `lens_head_len` | 4.7 mm | **EST** | No published source found: our estimate, to be measured |
| `mass_g` | 9 g | **EST** | No published source found: our estimate, to be measured |

## Pi Zero camera cable, 22-pin to 15-pin

Key in `sb_params.PARTS`: `fpc`. Bodies in the model: `camera_flex`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `w15` | 16 mm | drawing | [Raspberry Pi Standard-Mini FPC cable reference drawing](https://pip-assets.raspberrypi.com/categories/903-flexible-printed-circuit-fpc-cable-for-display-and-camera/documents/RP-008145-DS-1-mini-display-cable-200mm-reference-drawing.pdf) |
| `w22` | 11.5 mm | drawing | [Raspberry Pi Standard-Mini FPC cable reference drawing](https://pip-assets.raspberrypi.com/categories/903-flexible-printed-circuit-fpc-cable-for-display-and-camera/documents/RP-008145-DS-1-mini-display-cable-200mm-reference-drawing.pdf) |
| `t` | 0.1 mm | drawing | [Raspberry Pi Standard-Mini FPC cable reference drawing](https://pip-assets.raspberrypi.com/categories/903-flexible-printed-circuit-fpc-cable-for-display-and-camera/documents/RP-008145-DS-1-mini-display-cable-200mm-reference-drawing.pdf) |
| `t_stiff` | 0.31 mm | drawing | [Raspberry Pi Standard-Mini FPC cable reference drawing](https://pip-assets.raspberrypi.com/categories/903-flexible-printed-circuit-fpc-cable-for-display-and-camera/documents/RP-008145-DS-1-mini-display-cable-200mm-reference-drawing.pdf) |
| `len` | 150 mm | page | [Arducam B0310 product page (optics, listed size)](https://www.uctronics.com/arducam-12mp-imx708-hdr-120-wide-angle-camera-module-with-m12-lens-for-raspberry-pi.html) |

## Akyga LP902535 LiPo pack with protection board and NTC, 800 mAh

Key in `sb_params.PARTS`: `cell`. Bodies in the model: `cell_left`, `cell_pcm_left`, `cell_pcm_right`, `cell_right`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `t_max` | 9.5 mm | drawing | [Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023](https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf) |
| `w_max` | 26 mm | drawing | [Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023](https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf) |
| `len_max` | 37.5 mm | drawing | [Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023](https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf) |
| `len_bare_max` | 35.5 mm | drawing | [Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023](https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf) |
| `capacity_mah` | 800 mAh | drawing | [Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023](https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf) |
| `max_discharge_a` | 0.8 A | drawing | [Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023](https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf) |
| `lead_awg` | 24 AWG | drawing | [Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023](https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf) |
| `lead_len` | 150 mm | drawing | [Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023](https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf) |
| `mass_g` | 16 g | **EST** | No published source found: our estimate, to be measured |

## Same Sky CES-20134-088PM enclosed micro speaker, 8 ohm, 0.8 W

Key in `sb_params.PARTS`: `spk`. Bodies in the model: `speaker`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 20 mm | drawing | [Same Sky (CUI Devices) CES-20134-088PM speaker datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf) |
| `wid` | 13 mm | drawing | [Same Sky (CUI Devices) CES-20134-088PM speaker datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf) |
| `h` | 4.87 mm | drawing | [Same Sky (CUI Devices) CES-20134-088PM speaker datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf) |
| `across_lugs` | 21 mm | drawing | [Same Sky (CUI Devices) CES-20134-088PM speaker datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf) |
| `lug_pitch` | 16.09 mm | drawing | [Same Sky (CUI Devices) CES-20134-088PM speaker datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf) |
| `lug_d` | 5 mm | drawing | [Same Sky (CUI Devices) CES-20134-088PM speaker datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf) |
| `lug_hole_d` | 2 mm | drawing | [Same Sky (CUI Devices) CES-20134-088PM speaker datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf) |
| `lug_from_end` | 7.5 mm | drawing | [Same Sky (CUI Devices) CES-20134-088PM speaker datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf) |
| `mass_g` | 2 g | drawing | [Same Sky (CUI Devices) CES-20134-088PM speaker datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf) |
| `lug_t` | 1 mm | **EST** | No published source found: our estimate, to be measured |

## Adafruit 3006: MAX98357A I2S amplifier breakout

Key in `sb_params.PARTS`: `amp`. Bodies in the model: `amp_board_max98357a`, `amp_board_parts`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 19.05 mm | design | [Adafruit MAX98357A amplifier breakout: product page and board file](https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout) |
| `wid` | 17.78 mm | design | [Adafruit MAX98357A amplifier breakout: product page and board file](https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout) |
| `h` | 3 mm | page | [Adafruit MAX98357A amplifier breakout: product page and board file](https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout) |
| `hole_d` | 2.5 mm | design | [Adafruit MAX98357A amplifier breakout: product page and board file](https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout) |
| `mass_g` | 1.2 g | page | [Adafruit MAX98357A amplifier breakout: product page and board file](https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout) |
| `pcb_t` | 1.6 mm | **EST** | No published source found: our estimate, to be measured |

## Adafruit 3421: SPH0645LM4H I2S microphone breakout

Key in `sb_params.PARTS`: `mic`. Bodies in the model: `mic_left`, `mic_right`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 16.51 mm | design | [Adafruit SPH0645LM4H I2S microphone breakout: product page and board file](https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB) |
| `wid` | 12.7 mm | design | [Adafruit SPH0645LM4H I2S microphone breakout: product page and board file](https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB) |
| `h` | 1.8 mm | page | [Adafruit SPH0645LM4H I2S microphone breakout: product page and board file](https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB) |
| `port_x` | 8.255 mm | design | [Adafruit SPH0645LM4H I2S microphone breakout: product page and board file](https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB) |
| `port_y` | 7.822 mm | design | [Adafruit SPH0645LM4H I2S microphone breakout: product page and board file](https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB) |
| `port_d` | 1.025 mm | design | [Adafruit SPH0645LM4H I2S microphone breakout: product page and board file](https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB) |
| `mass_g` | 0.4 g | page | [Adafruit SPH0645LM4H I2S microphone breakout: product page and board file](https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB) |
| `pcb_t` | 0.8 mm | **EST** | No published source found: our estimate, to be measured |

## Adafruit 6250: PCM5102 I2S DAC with 3.5 mm jack

Key in `sb_params.PARTS`: `dac`. Bodies in the model: `dac_board_pcm5102`, `dac_jack`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 30.48 mm | design | [Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file](https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB) |
| `wid` | 20.32 mm | design | [Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file](https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB) |
| `h` | 6.2 mm | page | [Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file](https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB) |
| `len_with_jack` | 32.5 mm | page | [Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file](https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB) |
| `jack_cy` | 10.16 mm | design | [Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file](https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB) |
| `hole_d` | 2.5 mm | design | [Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file](https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB) |
| `hole_inset` | 2.54 mm | design | [Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file](https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB) |
| `mass_g` | 2.8 g | page | [Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file](https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB) |
| `pcb_t` | 1.6 mm | **EST** | No published source found: our estimate, to be measured |
| `jack_w` | 6 mm | **EST** | No published source found: our estimate, to be measured |
| `jack_len` | 12 mm | **EST** | No published source found: our estimate, to be measured |
| `jack_barrel_d` | 6 mm | **EST** | No published source found: our estimate, to be measured |

## Adafruit 6106: bq25185 USB-C LiPo charger with 5 V boost

Key in `sb_params.PARTS`: `chg`. Bodies in the model: `charger_board`, `charger_board_parts`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 29.21 mm | design | [Adafruit bq25185 USB-C charger with 5 V boost: product page and board file](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) |
| `wid` | 19.05 mm | design | [Adafruit bq25185 USB-C charger with 5 V boost: product page and board file](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) |
| `usb_cy` | 9.525 mm | design | [Adafruit bq25185 USB-C charger with 5 V boost: product page and board file](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) |
| `hole_d` | 2.5 mm | design | [Adafruit bq25185 USB-C charger with 5 V boost: product page and board file](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) |
| `hole_inset` | 2.54 mm | design | [Adafruit bq25185 USB-C charger with 5 V boost: product page and board file](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) |
| `out_a` | 1 A | page | [Adafruit bq25185 USB-C charger with 5 V boost: product page and board file](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) |
| `pcb_t` | 1.6 mm | **EST** | No published source found: our estimate, to be measured |
| `h` | 5.2 mm | **EST** | No published source found: our estimate, to be measured |
| `mass_g` | 3 g | **EST** | No published source found: our estimate, to be measured |

## USB-C receptacle, 16-pin (as on the charger board)

Key in `sb_params.PARTS`: `usbc`. Bodies in the model: `usb_c_receptacle`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `w` | 8.94 mm | drawing | [Korean Hroparts TYPE-C-31-M-12 USB-C receptacle datasheet](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948) |
| `h` | 3.26 mm | drawing | [Korean Hroparts TYPE-C-31-M-12 USB-C receptacle datasheet](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948) |
| `d` | 7.35 mm | drawing | [Korean Hroparts TYPE-C-31-M-12 USB-C receptacle datasheet](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948) |

## Adafruit 5580: MAX17048 fuel gauge

Key in `sb_params.PARTS`: `gauge`. Bodies in the model: `fuel_gauge_max17048`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 25.4 mm | design | [Adafruit MAX17048 fuel gauge: product page and board file](https://github.com/adafruit/Adafruit-MAX17048-PCB) |
| `wid` | 20.32 mm | design | [Adafruit MAX17048 fuel gauge: product page and board file](https://github.com/adafruit/Adafruit-MAX17048-PCB) |
| `h_as_sold` | 7.2 mm | page | [Adafruit MAX17048 fuel gauge: product page and board file](https://github.com/adafruit/Adafruit-MAX17048-PCB) |
| `hole_inset` | 2.54 mm | design | [Adafruit MAX17048 fuel gauge: product page and board file](https://github.com/adafruit/Adafruit-MAX17048-PCB) |
| `mass_g` | 2.6 g | page | [Adafruit MAX17048 fuel gauge: product page and board file](https://github.com/adafruit/Adafruit-MAX17048-PCB) |
| `pcb_t` | 1.6 mm | **EST** | No published source found: our estimate, to be measured |
| `h_no_connectors` | 2.8 mm | **EST** | No published source found: our estimate, to be measured |

## Alps Alpine SKQGABE010 tactile switch

Key in `sb_params.PARTS`: `tact`. Bodies in the model: `ask_button_board`, `top_bar_switches`, `volume_board`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `w` | 5.2 mm | drawing | [Alps Alpine SKQGABE010 tactile switch](https://tech.alpsalpine.com/e/products/detail/SKQGABE010/) |
| `h` | 1.5 mm | drawing | [Alps Alpine SKQGABE010 tactile switch](https://tech.alpsalpine.com/e/products/detail/SKQGABE010/) |
| `travel` | 0.25 mm | drawing | [Alps Alpine SKQGABE010 tactile switch](https://tech.alpsalpine.com/e/products/detail/SKQGABE010/) |
| `force_n` | 1.57 N | drawing | [Alps Alpine SKQGABE010 tactile switch](https://tech.alpsalpine.com/e/products/detail/SKQGABE010/) |

## Shouhan MSK12C02 side-actuated slide switch

Key in `sb_params.PARTS`: `slide`. Bodies in the model: `mic_mute_switch`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 8 mm | drawing | [Shouhan MSK12C02 side-actuated slide switch datasheet](https://cdn.shopify.com/s/files/1/0227/9171/6941/files/MSK12C02.pdf) |
| `d` | 2.8 mm | drawing | [Shouhan MSK12C02 side-actuated slide switch datasheet](https://cdn.shopify.com/s/files/1/0227/9171/6941/files/MSK12C02.pdf) |
| `h` | 1.4 mm | drawing | [Shouhan MSK12C02 side-actuated slide switch datasheet](https://cdn.shopify.com/s/files/1/0227/9171/6941/files/MSK12C02.pdf) |
| `lever_len` | 1.5 mm | drawing | [Shouhan MSK12C02 side-actuated slide switch datasheet](https://cdn.shopify.com/s/files/1/0227/9171/6941/files/MSK12C02.pdf) |
| `lever_t` | 1 mm | drawing | [Shouhan MSK12C02 side-actuated slide switch datasheet](https://cdn.shopify.com/s/files/1/0227/9171/6941/files/MSK12C02.pdf) |
| `travel` | 1.6 mm | drawing | [Shouhan MSK12C02 side-actuated slide switch datasheet](https://cdn.shopify.com/s/files/1/0227/9171/6941/files/MSK12C02.pdf) |
| `lever_w` | 1.3 mm | **EST** | No published source found: our estimate, to be measured |

## Alps Alpine SPVE110200 detector switch

Key in `sb_params.PARTS`: `det`. Bodies in the model: `hub_sensor_switch`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 3.4 mm | drawing | [Alps Alpine SPVE110200 detector switch datasheet](https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF) |
| `wid` | 3 mm | drawing | [Alps Alpine SPVE110200 detector switch datasheet](https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF) |
| `h` | 2.3 mm | drawing | [Alps Alpine SPVE110200 detector switch datasheet](https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF) |
| `plunger_free` | 4.8 mm | drawing | [Alps Alpine SPVE110200 detector switch datasheet](https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF) |
| `plunger_on` | 4.5 mm | drawing | [Alps Alpine SPVE110200 detector switch datasheet](https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF) |
| `plunger_full` | 3.6 mm | drawing | [Alps Alpine SPVE110200 detector switch datasheet](https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF) |
| `plunger_w` | 0.75 mm | drawing | [Alps Alpine SPVE110200 detector switch datasheet](https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF) |

## Vybronics VC1026B002F coin vibration motor

Key in `sb_params.PARTS`: `motor`. Bodies in the model: `haptic_motor`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `d` | 10 mm | drawing | [Vybronics VC1026B002F coin vibration motor datasheet](https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VC1026B002F-datasheet.pdf) |
| `t` | 2.7 mm | drawing | [Vybronics VC1026B002F coin vibration motor datasheet](https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VC1026B002F-datasheet.pdf) |
| `lead_len` | 27 mm | drawing | [Vybronics VC1026B002F coin vibration motor datasheet](https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VC1026B002F-datasheet.pdf) |
| `mass_g` | 0.9 g | **EST** | No published source found: our estimate, to be measured |

## Wurth 150060WS75000 white LED, 0603

Key in `sb_params.PARTS`: `led_dot`. Bodies in the model: `status_leds`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 1.6 mm | drawing | [Wurth 150060WS75000 white 0603 LED datasheet](https://www.we-online.com/components/products/datasheet/150060WS75000.pdf) |
| `wid` | 0.8 mm | drawing | [Wurth 150060WS75000 white 0603 LED datasheet](https://www.we-online.com/components/products/datasheet/150060WS75000.pdf) |
| `h` | 0.45 mm | drawing | [Wurth 150060WS75000 white 0603 LED datasheet](https://www.we-online.com/components/products/datasheet/150060WS75000.pdf) |

## Cree J Series 2835, 2700 K, CRI 90

Key in `sb_params.PARTS`: `led_ring`. Bodies in the model: `light_ring_leds`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 3.5 mm | drawing | [Cree LED J Series 2835 3 V datasheet (CRI 90)](https://downloads.cree-led.com/files/ds/j/JSeries-2835-3V-Consolidated.pdf) |
| `wid` | 2.8 mm | drawing | [Cree LED J Series 2835 3 V datasheet (CRI 90)](https://downloads.cree-led.com/files/ds/j/JSeries-2835-3V-Consolidated.pdf) |
| `h` | 0.7 mm | drawing | [Cree LED J Series 2835 3 V datasheet (CRI 90)](https://downloads.cree-led.com/files/ds/j/JSeries-2835-3V-Consolidated.pdf) |

## Gutekunst T-18510L / T-18510R torsion spring, 1.4310

Key in `sb_params.PARTS`: `spring`. Bodies in the model: `torsion_spring_left`, `torsion_spring_right`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `wire` | 1 mm | drawing | [Gutekunst T-18510L torsion spring, 1.4310, catalogue page](https://www.federnshop.com/en/products/torsion_springs/t-18510l.html) |
| `id` | 5.5 mm | drawing | [Gutekunst T-18510L torsion spring, 1.4310, catalogue page](https://www.federnshop.com/en/products/torsion_springs/t-18510l.html) |
| `coils` | 6.5 turns | drawing | [Gutekunst T-18510L torsion spring, 1.4310, catalogue page](https://www.federnshop.com/en/products/torsion_springs/t-18510l.html) |
| `body_len` | 7.5 mm | drawing | [Gutekunst T-18510L torsion spring, 1.4310, catalogue page](https://www.federnshop.com/en/products/torsion_springs/t-18510l.html) |
| `leg_len` | 45 mm | drawing | [Gutekunst T-18510L torsion spring, 1.4310, catalogue page](https://www.federnshop.com/en/products/torsion_springs/t-18510l.html) |
| `max_torque_nmm` | 111.87 N·mm | drawing | [Gutekunst T-18510L torsion spring, 1.4310, catalogue page](https://www.federnshop.com/en/products/torsion_springs/t-18510l.html) |
| `max_angle_deg` | 93.82 ° | drawing | [Gutekunst T-18510L torsion spring, 1.4310, catalogue page](https://www.federnshop.com/en/products/torsion_springs/t-18510l.html) |

## Tapping screw ST2.2, pan head

Key in `sb_params.PARTS`: `st22`. Bodies in the model: `camera_screws`, `cover_screw_1`, `cover_screw_2`, `cover_screw_3`, `cover_screw_4`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `head_d` | 4 mm | drawing | [ISO 7049 pan head tapping screws (ST2.2)](https://cdn.standards.iteh.ai/samples/54046/49d73e73edab4028ac8a6f9f29f220bc/ISO-7049-2011.pdf) |
| `head_h` | 1.6 mm | drawing | [ISO 7049 pan head tapping screws (ST2.2)](https://cdn.standards.iteh.ai/samples/54046/49d73e73edab4028ac8a6f9f29f220bc/ISO-7049-2011.pdf) |
| `thread_d` | 2.2 mm | drawing | [ISO 7049 pan head tapping screws (ST2.2)](https://cdn.standards.iteh.ai/samples/54046/49d73e73edab4028ac8a6f9f29f220bc/ISO-7049-2011.pdf) |

## M3 button head screw and hex nut

Key in `sb_params.PARTS`: `m3`. Used for sizes only (no body of its own).

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `head_d` | 5.7 mm | page | [ISO 7380 button head screws, secondary table](https://www.fasteners.eu/standards/ISO/7380/) |
| `head_h` | 1.65 mm | page | [ISO 7380 button head screws, secondary table](https://www.fasteners.eu/standards/ISO/7380/) |
| `nut_af` | 5.5 mm | page | [ISO 4032 hexagon nuts, secondary table](https://www.fasteners.eu/standards/ISO/4032/) |
| `nut_h` | 2.4 mm | page | [ISO 4032 hexagon nuts, secondary table](https://www.fasteners.eu/standards/ISO/4032/) |

## microSD card

Key in `sb_params.PARTS`: `sd`. Bodies in the model: `microsd_card`.

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `len` | 15 mm | page | [microSD card outline (Kingston datasheet)](https://www.kingston.com/datasheets/SDCS2_us.pdf) |
| `wid` | 11 mm | page | [microSD card outline (Kingston datasheet)](https://www.kingston.com/datasheets/SDCS2_us.pdf) |
| `t` | 1 mm | page | [microSD card outline (Kingston datasheet)](https://www.kingston.com/datasheets/SDCS2_us.pdf) |

## Stainless shim 0.40 mm, 300-series full hard (blades)

Key in `sb_params.PARTS`: `shim`. Used for sizes only (no body of its own).

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `t` | 0.4 mm | drawing | [RS PRO stainless shim 0.40 mm, 300-series full hard, datasheet](https://docs.rs-online.com/b176/A700000015372078.pdf) |
| `yield_mpa` | 965 MPa | drawing | [RS PRO stainless shim 0.40 mm, 300-series full hard, datasheet](https://docs.rs-online.com/b176/A700000015372078.pdf) |
| `tensile_mpa` | 1172 MPa | drawing | [RS PRO stainless shim 0.40 mm, 300-series full hard, datasheet](https://docs.rs-online.com/b176/A700000015372078.pdf) |

## Stainless 304 tube (stick)

Key in `sb_params.PARTS`: `tube`. Used for sizes only (no body of its own).

| Dimension | Value | Basis | Source |
|---|---|---|---|
| `od_outer` | 10 mm | page | [Stainless 304 tube 10 x 0.5 mm, hobby lengths (seller page)](https://www.harfington.com/products/p-1630275) |
| `wall` | 0.5 mm | page | [Stainless 304 tube 10 x 0.5 mm, hobby lengths (seller page)](https://www.harfington.com/products/p-1630275) |
| `od_inner` | 8 mm | **EST** | No published source found: our estimate, to be measured |

## Estimates: what to measure on the real parts

| Part | Dimension | Value used | Why it is an estimate | How to measure |
|---|---|---|---|---|
| Raspberry Pi Zero 2 W | `pcb_t` | 1.2 mm | Board thickness is not labelled on the Raspberry Pi drawing. | Calipers across the bare board edge. |
| Raspberry Pi Zero 2 W | `hdmi_h` | 3.3 mm | Not on the Raspberry Pi drawing: only the 5.3 mm overall thickness is published. | Calipers, board face to the top of the mini-HDMI shell. |
| Raspberry Pi Zero 2 W | `usb_h` | 2.8 mm | Not on the Raspberry Pi drawing: only the 5.3 mm overall thickness is published. | Calipers, board face to the top of a micro-USB shell. |
| Raspberry Pi Zero 2 W | `sd_h` | 1.5 mm | Not on the Raspberry Pi drawing: only the 5.3 mm overall thickness is published. | Calipers, board face to the top of the card slot. |
| Raspberry Pi Zero 2 W | `csi_h` | 1.3 mm | Not on the Raspberry Pi drawing: only the 5.3 mm overall thickness is published. | Calipers, board face to the top of the camera connector. |
| Raspberry Pi Zero 2 W | `sip_h` | 1.4 mm | Not on the Raspberry Pi drawing: only the 5.3 mm overall thickness is published. | Calipers, board face to the top of the main chip. This sets the thermal pad thickness. |
| Raspberry Pi Zero 2 W | `can_h` | 1.8 mm | Not on the Raspberry Pi drawing: only the 5.3 mm overall thickness is published. | Calipers, board face to the top of the radio can. |
| Arducam B0310: 12 MP IMX708, M12 mount, 120 degree lens | `lens_head_len` | 4.7 mm | The maker's 3D file shows the lens as one piece; where the wide head ends was read off it by eye. | Calipers along the lens barrel, front rim to the step down to the M12 thread. |
| Arducam B0310: 12 MP IMX708, M12 mount, 120 degree lens | `mass_g` | 9 g | Arducam does not publish the mass. | Scale reading to 0.1 g, camera with lens, without cable. |
| Akyga LP902535 LiPo pack with protection board and NTC, 800 mAh | `mass_g` | 16 g | The Akyga sheet gives no mass. | Scale reading to 0.1 g, one pack with its leads. |
| Same Sky CES-20134-088PM enclosed micro speaker, 8 ohm, 0.8 W | `lug_t` | 1 mm | The mounting-lug thickness is not dimensioned on the datasheet. | Calipers across one lug. |
| Adafruit 3006: MAX98357A I2S amplifier breakout | `pcb_t` | 1.6 mm | Board thickness is not in the maker's board file; the usual thickness is assumed. | Calipers across the board edge. Also check for a screw terminal block: it would add height. |
| Adafruit 3421: SPH0645LM4H I2S microphone breakout | `pcb_t` | 0.8 mm | Board thickness is not in the maker's board file; the usual thickness is assumed. (0.8 mm here: the page gives 1.8 mm overall with a 1.0 mm microphone.) | Calipers across the board edge. |
| Adafruit 6250: PCM5102 I2S DAC with 3.5 mm jack | `pcb_t` | 1.6 mm | Board thickness is not in the maker's board file; the usual thickness is assumed. | Calipers across the board edge. |
| Adafruit 6250: PCM5102 I2S DAC with 3.5 mm jack | `jack_w` | 6 mm | No drawing we could tie to the jack fitted on this board. | Calipers across the jack body. |
| Adafruit 6250: PCM5102 I2S DAC with 3.5 mm jack | `jack_len` | 12 mm | No drawing we could tie to the jack fitted on this board. | Calipers along the jack body. |
| Adafruit 6250: PCM5102 I2S DAC with 3.5 mm jack | `jack_barrel_d` | 6 mm | No drawing we could tie to the jack fitted on this board. | Calipers across the round nose. The hole in the side wall is cut 0.2 mm larger all round. |
| Adafruit 6106: bq25185 USB-C LiPo charger with 5 V boost | `pcb_t` | 1.6 mm | Board thickness is not in the maker's board file; the usual thickness is assumed. | Calipers across the board edge. |
| Adafruit 6106: bq25185 USB-C LiPo charger with 5 V boost | `h` | 5.2 mm | The height of the tallest part (inductor or USB-C shell) is not published. | Calipers, board underside to the tallest part. |
| Adafruit 6106: bq25185 USB-C LiPo charger with 5 V boost | `mass_g` | 3 g | Not published. | Scale reading to 0.1 g. |
| Adafruit 5580: MAX17048 fuel gauge | `pcb_t` | 1.6 mm | Board thickness is not in the maker's board file; the usual thickness is assumed. | Calipers across the board edge. |
| Adafruit 5580: MAX17048 fuel gauge | `h_no_connectors` | 2.8 mm | Sold 7.2 mm tall with its JST and Stemma sockets. The model assumes they are removed and wires soldered on. | Desolder the sockets, then calipers from the board underside to the tallest part left. |
| Shouhan MSK12C02 side-actuated slide switch | `lever_w` | 1.3 mm | The lever width is not labelled on the MSK12C02 sheet. | Calipers across the lever. The slider cap pocket is cut to it. |
| Vybronics VC1026B002F coin vibration motor | `mass_g` | 0.9 g | Not on the Vybronics sheet. | Scale reading to 0.1 g. |
| Stainless 304 tube (stick) | `od_inner` | 8 mm | We found a seller page for the 10 x 0.5 mm tube but none we could confirm for 8 x 0.5 mm. | Buy both, then check the 8 mm tube with its glide bush slides in the 9.0 mm bore of the 10 mm tube. |

## All sources

| Id | Source | Link |
|---|---|---|
| RPI-Z2W | Raspberry Pi Zero 2 W mechanical drawing | https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf |
| RPI-Z | Raspberry Pi Zero mechanical drawing (same outline) | https://datasheets.raspberrypi.com/rpizero/raspberry-pi-zero-mechanical-drawing.pdf |
| RPI-ZW | Raspberry Pi Zero W mechanical drawing (same outline) | https://datasheets.raspberrypi.com/rpizero/raspberry-pi-zero-w-mechanical-drawing.pdf |
| ADA-5291 | Adafruit product page, Raspberry Pi Zero 2 W | https://www.adafruit.com/product/5291 |
| ARDU-B0310 | Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens | https://www.arducam.com/downloads/3D_Model/B0310.STEP |
| ARDU-PAGE | Arducam B0310 product page (optics, listed size) | https://www.uctronics.com/arducam-12mp-imx708-hdr-120-wide-angle-camera-module-with-m12-lens-for-raspberry-pi.html |
| RPI-FPC | Raspberry Pi Standard-Mini FPC cable reference drawing | https://pip-assets.raspberrypi.com/categories/903-flexible-printed-circuit-fpc-cable-for-display-and-camera/documents/RP-008145-DS-1-mini-display-cable-200mm-reference-drawing.pdf |
| AKY-902535 | Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023 | https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf |
| SS-CES20134 | Same Sky (CUI Devices) CES-20134-088PM speaker datasheet | https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf |
| ADA-3006 | Adafruit MAX98357A amplifier breakout: product page and board file | https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout |
| ADA-3421 | Adafruit SPH0645LM4H I2S microphone breakout: product page and board file | https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB |
| ADA-6250 | Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file | https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB |
| ADA-6106 | Adafruit bq25185 USB-C charger with 5 V boost: product page and board file | https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB |
| ADA-5580 | Adafruit MAX17048 fuel gauge: product page and board file | https://github.com/adafruit/Adafruit-MAX17048-PCB |
| HRO-USBC | Korean Hroparts TYPE-C-31-M-12 USB-C receptacle datasheet | https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948 |
| ALPS-SKQG | Alps Alpine SKQGABE010 tactile switch | https://tech.alpsalpine.com/e/products/detail/SKQGABE010/ |
| SH-MSK12C02 | Shouhan MSK12C02 side-actuated slide switch datasheet | https://cdn.shopify.com/s/files/1/0227/9171/6941/files/MSK12C02.pdf |
| ALPS-SPVE | Alps Alpine SPVE110200 detector switch datasheet | https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF |
| VYB-VC1026 | Vybronics VC1026B002F coin vibration motor datasheet | https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VC1026B002F-datasheet.pdf |
| WE-0603 | Wurth 150060WS75000 white 0603 LED datasheet | https://www.we-online.com/components/products/datasheet/150060WS75000.pdf |
| CREE-2835 | Cree LED J Series 2835 3 V datasheet (CRI 90) | https://downloads.cree-led.com/files/ds/j/JSeries-2835-3V-Consolidated.pdf |
| GUT-T18510 | Gutekunst T-18510L torsion spring, 1.4310, catalogue page | https://www.federnshop.com/en/products/torsion_springs/t-18510l.html |
| ISO-7049 | ISO 7049 pan head tapping screws (ST2.2) | https://cdn.standards.iteh.ai/samples/54046/49d73e73edab4028ac8a6f9f29f220bc/ISO-7049-2011.pdf |
| ISO-7380 | ISO 7380 button head screws, secondary table | https://www.fasteners.eu/standards/ISO/7380/ |
| ISO-4032 | ISO 4032 hexagon nuts, secondary table | https://www.fasteners.eu/standards/ISO/4032/ |
| RS-SHIM | RS PRO stainless shim 0.40 mm, 300-series full hard, datasheet | https://docs.rs-online.com/b176/A700000015372078.pdf |
| TUBE-304 | Stainless 304 tube 10 x 0.5 mm, hobby lengths (seller page) | https://www.harfington.com/products/p-1630275 |
| SD | microSD card outline (Kingston datasheet) | https://www.kingston.com/datasheets/SDCS2_us.pdf |
| EST | No published source found: our estimate, to be measured | none |
