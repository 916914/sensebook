"""SenseBook v4 'tri-grip' - single source of truth for dimensions (mm, degrees).

Frames
------
UNIT frame (untipped): x across (+x = reader's right), y forward (+y = toward reader),
z up. Front face at y=0, back face at y=-UNIT_D, bottom at z=0, top at z=UNIT_H.
BOOK frame: page plane z=0 at the top edge, top edge of the book at y=0 (+y toward
reader), spine/gutter at x=0.
Everything marked EST is an estimate to be confirmed on the bench.
"""
import math

# ---------------------------------------------------------------- unit envelope
# 27 Nov 2026: grew from 88 x 40 x 34 to hold the real, documented parts (see PARTS below):
#   width  +4: the DAC board with its jack is 30.5 long and must sit beside the 25 mm camera board
#   height +5: the documented cell pack is 37.5 long with its protection board, and its leads leave the top
#   depth  +3: the Pi is 5.3 thick overall, and the bigger lens ring needs a longer facet
UNIT_W, UNIT_H, UNIT_D = 92.0, 45.0, 37.0
WALL = 1.8                                      # PC/ABS intent; print in PETG at 1.8 mm
R_FRONT = 9.0                                   # front-view corner radius (x-z)
R_EDGE = 4.0                                    # soft edge round on front/back perimeters
# Lens facet (unit frame): plane at FACET_ANGLE from horizontal, lens normal to it
FACET_ANGLE = 45.0                              # facet & internal camera axis: 45 deg below unit horizontal
FACET_TOP_Z = 18.0                              # where the facet meets the front face (was 17: the lens ring grew)
FACET_BOT_Y = -18.0                             # where the facet meets the bottom
LENS_Y, LENS_Z = -9.0, 9.0                      # lens front centre, on the facet mid-line
# The real M12 lens has a 14.8 mm front rim and a 17 mm head, and sees 152 degrees corner to corner, so
# there is no flat window in front of it: the lens front sits in a bezel, just inside the facet surface.
RING_OD, RING_ID = 23.8, 18.0                   # light-ring diffuser (2835 LEDs need a 2.9 mm wide ring)

# ---------------------------------------------------------------- tilt joint / kinematics
PIVOT_Y, PIVOT_Z = -20.0, -4.0                  # tilt pivot in unit frame (behind the facet)
TIP_NOMINAL = 20.0                              # unit tips forward 20 deg -> axis 65 deg below horiz.
TIP_RANGE = 15.0                                # +/-15 deg joint travel
# camera axis below horizontal = FACET_ANGLE + tip

# ---------------------------------------------------------------- stick (2-stage telescope)
STICK_COLLAPSED = 90.0                          # hub top -> joint base, normal use
STICK_EXTENDED = 180.0
STICK_OD_OUTER, STICK_OD_INNER = 10.0, 8.0      # stainless 304 tube, 0.5 mm wall (EST stock)
STICK_WALL = 0.5
JOINT_ABOVE_STICK = 6.0                          # pivot axis above stick top

# ---------------------------------------------------------------- hub / tri-grip (book frame)
HUB_W, HUB_D, HUB_H = 29.0, 18.0, 20.0           # width was 26: two stock torsion springs (7.5 long each) flank the leg
STICK_Y = -40.0                                 # stick axis behind the top-edge plane
HUB_TOP_Z = 10.0                                # hub top above the page plane
BLADE_T, BLADE_W = 0.4, 8.0                     # 301 spring-steel shim
BLADE_REACH = 70.0                              # flat run under the pages, from the top edge
BLADE_X = 11.0                                  # each blade centre-line from the gutter
REAR_LEG_LEN = 70.0
BLADE_SPLAY = 25.0                              # blades splay outward in plan (deg) for a wider base
REAR_FOOT_W = 50.0                              # TPU T-pad width on the rear leg
SPRING_TRAVEL_MAX = 60.0                        # book thickness range (closed-book attach)

# ---------------------------------------------------------------- masses (EST, grams)
# 27 Nov 2026: taken from the 3D model (build_model.py): printed and cut parts are volume x density, bought parts
# use the published mass (or an EST where none is published, see PARTS). Nothing has been weighed.
# The earlier budget was 137 g; the product spec says about 90 g. analysis.py reads this table.
MASS = {
    "unit_shells": 37.1, "pi_zero_2w": 10.3, "camera_m12": 9.0, "lipo_cells": 32.0,
    "speaker": 2.0, "audio_boards": 4.8, "power_boards": 5.6, "leds_buttons_motor": 4.0,
    "spreader_wiring": 8.2,
    "tilt_joint": 3.1, "stick_tubes_cord": 24.4,
    "hub_spring": 15.2, "blades": 5.9, "rear_leg_pad": 5.8,
}
UNIT_COM = (-20.6, 22.5)                         # centre of mass of the unit (y, z), unit frame, from the 3D model


def unit_mass():
    keys = ["unit_shells", "pi_zero_2w", "camera_m12", "lipo_cells", "speaker",
            "audio_boards", "power_boards", "leds_buttons_motor", "spreader_wiring"]
    return sum(MASS[k] for k in keys)


def total_mass():
    return sum(MASS.values())


# ---------------------------------------------------------------- kinematics
def rot_tip(y, z, tip_deg):
    """Rotate a unit-frame point (relative to pivot) forward by tip (front goes down)."""
    t = math.radians(tip_deg)
    return y * math.cos(t) + z * math.sin(t), -y * math.sin(t) + z * math.cos(t)


def unit_pose(stick_len, tip_deg):
    """Return dict with book-frame pivot, lens point, axis angle, front-most y, top z."""
    piv_y = STICK_Y
    piv_z = HUB_TOP_Z + stick_len + JOINT_ABOVE_STICK
    def to_book(yu, zu):
        dy, dz = rot_tip(yu - PIVOT_Y, zu - PIVOT_Z, tip_deg)
        return piv_y + dy, piv_z + dz
    ly, lz = to_book(LENS_Y, LENS_Z)
    # outline sample of the side profile (with corner rounds approximated)
    prof = side_profile()
    pts = [to_book(y, z) for (y, z) in prof]
    front = max(p[0] for p in pts)
    top = max(p[1] for p in pts)
    low = min(p[1] for p in pts)
    axis_below_h = FACET_ANGLE + tip_deg
    return dict(pivot=(piv_y, piv_z), lens=(ly, lz), axis_below_h=axis_below_h,
                theta_from_vertical=90 - axis_below_h, front_y=front, top_z=top,
                low_z=low, outline=pts)


def side_profile(n=8):
    """Unit side profile (y,z) polygon incl. facet, with small rounds (approx.)."""
    r = R_EDGE
    pts = []
    def arc(cy, cz, a0, a1):
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    D, H = UNIT_D, UNIT_H
    arc(-r, H - r, 0, 90)              # front-top
    arc(-D + r, H - r, 90, 180)        # back-top
    arc(-D + r, r, 180, 270)           # back-bottom
    pts.append((FACET_BOT_Y, 0.0))
    pts.append((0.0, FACET_TOP_Z))
    return pts


# =====================================================================================
# BOUGHT PARTS: sizes from manufacturers' drawings and datasheets (looked up 27 Nov 2026).
# Each value is (mm, source id, basis). Basis:
#   "drawing" = labelled on the maker's drawing or datasheet
#   "design"  = read from the maker's published board design file
#   "model"   = measured on the maker's published 3D file
#   "scaled"  = measured from the 1:1 artwork inside the maker's drawing, not labelled (about +/-0.1)
#   "page"    = stated on the maker's or seller's product page
#   "EST"     = no source found: our estimate, to be measured on the real part
# design/cad/SOURCES.md is written from this table by check_model.py.
# =====================================================================================
SOURCE_DATE = "27 Nov 2026"
SRC = {
    "RPI-Z2W": ("Raspberry Pi Zero 2 W mechanical drawing", "https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf"),
    "RPI-Z": ("Raspberry Pi Zero mechanical drawing (same outline)", "https://datasheets.raspberrypi.com/rpizero/raspberry-pi-zero-mechanical-drawing.pdf"),
    "RPI-ZW": ("Raspberry Pi Zero W mechanical drawing (same outline)", "https://datasheets.raspberrypi.com/rpizero/raspberry-pi-zero-w-mechanical-drawing.pdf"),
    "ADA-5291": ("Adafruit product page, Raspberry Pi Zero 2 W", "https://www.adafruit.com/product/5291"),
    "ARDU-B0310": ("Arducam B0310 3D file (STEP), IMX708 with M12 mount and 120 degree lens", "https://www.arducam.com/downloads/3D_Model/B0310.STEP"),
    "ARDU-PAGE": ("Arducam B0310 product page (optics, listed size)", "https://www.uctronics.com/arducam-12mp-imx708-hdr-120-wide-angle-camera-module-with-m12-lens-for-raspberry-pi.html"),
    "RPI-FPC": ("Raspberry Pi Standard-Mini FPC cable reference drawing", "https://pip-assets.raspberrypi.com/categories/903-flexible-printed-circuit-fpc-cable-for-display-and-camera/documents/RP-008145-DS-1-mini-display-cable-200mm-reference-drawing.pdf"),
    "AKY-902535": ("Akyga LP902535 specification approval sheet (AKY1672), 14 Jul 2023", "https://elektronik.ropla.eu/pdf/stock/aky/aky1672.pdf"),
    "SS-CES20134": ("Same Sky (CUI Devices) CES-20134-088PM speaker datasheet", "https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf"),
    "ADA-3006": ("Adafruit MAX98357A amplifier breakout: product page and board file", "https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout"),
    "ADA-3421": ("Adafruit SPH0645LM4H I2S microphone breakout: product page and board file", "https://github.com/adafruit/Adafruit-I2S-Microphone-Breakout-PCB"),
    "ADA-6250": ("Adafruit PCM5102 I2S DAC with 3.5 mm jack: product page and board file", "https://github.com/adafruit/Adafruit-PCM510x-I2S-DAC-PCB"),
    "ADA-6106": ("Adafruit bq25185 USB-C charger with 5 V boost: product page and board file", "https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB"),
    "ADA-5580": ("Adafruit MAX17048 fuel gauge: product page and board file", "https://github.com/adafruit/Adafruit-MAX17048-PCB"),
    "HRO-USBC": ("Korean Hroparts TYPE-C-31-M-12 USB-C receptacle datasheet", "https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948"),
    "ALPS-SKQG": ("Alps Alpine SKQGABE010 tactile switch", "https://tech.alpsalpine.com/e/products/detail/SKQGABE010/"),
    "SH-MSK12C02": ("Shouhan MSK12C02 side-actuated slide switch datasheet", "https://cdn.shopify.com/s/files/1/0227/9171/6941/files/MSK12C02.pdf"),
    "ALPS-SPVE": ("Alps Alpine SPVE110200 detector switch datasheet", "https://www.tme.eu/Document/0727490ceeb48bc7ace14cd0fcab3099/SPVE110200.PDF"),
    "VYB-VC1026": ("Vybronics VC1026B002F coin vibration motor datasheet", "https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VC1026B002F-datasheet.pdf"),
    "WE-0603": ("Wurth 150060WS75000 white 0603 LED datasheet", "https://www.we-online.com/components/products/datasheet/150060WS75000.pdf"),
    "CREE-2835": ("Cree LED J Series 2835 3 V datasheet (CRI 90)", "https://downloads.cree-led.com/files/ds/j/JSeries-2835-3V-Consolidated.pdf"),
    "GUT-T18510": ("Gutekunst T-18510L torsion spring, 1.4310, catalogue page", "https://www.federnshop.com/en/products/torsion_springs/t-18510l.html"),
    "ISO-7049": ("ISO 7049 pan head tapping screws (ST2.2)", "https://cdn.standards.iteh.ai/samples/54046/49d73e73edab4028ac8a6f9f29f220bc/ISO-7049-2011.pdf"),
    "ISO-7380": ("ISO 7380 button head screws, secondary table", "https://www.fasteners.eu/standards/ISO/7380/"),
    "ISO-4032": ("ISO 4032 hexagon nuts, secondary table", "https://www.fasteners.eu/standards/ISO/4032/"),
    "RS-SHIM": ("RS PRO stainless shim 0.40 mm, 300-series full hard, datasheet", "https://docs.rs-online.com/b176/A700000015372078.pdf"),
    "TUBE-304": ("Stainless 304 tube 10 x 0.5 mm, hobby lengths (seller page)", "https://www.harfington.com/products/p-1630275"),
    "SD": ("microSD card outline (Kingston datasheet)", "https://www.kingston.com/datasheets/SDCS2_us.pdf"),
    "EST": ("No published source found: our estimate, to be measured", ""),
}

PARTS = {
    "pi": dict(name="Raspberry Pi Zero 2 W", dims={
        "len": (65.0, "RPI-Z2W", "drawing"), "wid": (30.0, "RPI-Z2W", "drawing"), "corner_r": (3.0, "RPI-Z", "drawing"),
        "hole_d": (2.75, "RPI-Z", "drawing"), "hole_inset": (3.5, "RPI-Z2W", "drawing"),
        "gpio_cx": (32.5, "RPI-Z2W", "drawing"), "gpio_cy": (26.5, "RPI-Z2W", "drawing"), "gpio_pitch": (2.54, "RPI-Z2W", "scaled"),
        "hdmi_cx": (12.4, "RPI-Z2W", "drawing"), "hdmi_w": (10.9, "RPI-Z2W", "scaled"), "hdmi_d": (7.5, "RPI-Z2W", "scaled"),
        "hdmi_over": (0.55, "RPI-Z2W", "scaled"),
        "usb_cx1": (41.4, "RPI-Z2W", "drawing"), "usb_cx2": (54.0, "RPI-Z2W", "drawing"), "usb_w": (8.1, "RPI-Z2W", "scaled"),
        "usb_d": (5.3, "RPI-Z2W", "scaled"), "usb_over": (1.2, "RPI-Z2W", "scaled"),
        "sd_cy": (16.9, "RPI-ZW", "drawing"), "sd_w": (11.45, "RPI-Z2W", "scaled"), "sd_x0": (1.65, "RPI-Z2W", "scaled"),
        "sd_x1": (13.1, "RPI-Z2W", "scaled"),
        "csi_cy": (15.0, "RPI-ZW", "drawing"), "csi_w": (16.1, "RPI-Z2W", "scaled"), "csi_d": (3.4, "RPI-Z2W", "scaled"),
        "sip": (15.0, "RPI-Z2W", "scaled"), "sip_cx": (27.35, "RPI-Z2W", "scaled"), "sip_cy": (14.05, "RPI-Z2W", "scaled"),
        "can": (12.2, "RPI-Z2W", "scaled"), "can_cx": (43.8, "RPI-Z2W", "scaled"), "can_cy": (13.6, "RPI-Z2W", "scaled"),
        "thick_total": (5.3, "ADA-5291", "page"), "mass_g": (10.0, "ADA-5291", "page"),
        "pcb_t": (1.2, "EST", "EST"), "hdmi_h": (3.3, "EST", "EST"), "usb_h": (2.8, "EST", "EST"), "sd_h": (1.5, "EST", "EST"),
        "csi_h": (1.3, "EST", "EST"), "sip_h": (1.4, "EST", "EST"), "can_h": (1.8, "EST", "EST"),
    }),
    "cam": dict(name="Arducam B0310: 12 MP IMX708, M12 mount, 120 degree lens", dims={
        "board_w": (25.0, "ARDU-B0310", "model"), "board_h": (23.862, "ARDU-B0310", "model"), "pcb_t": (1.6, "ARDU-B0310", "model"),
        "corner_r": (2.0, "ARDU-B0310", "model"), "hole_d": (2.2, "ARDU-B0310", "model"), "hole_pitch_w": (21.0, "ARDU-B0310", "model"),
        "hole_pitch_h": (12.5, "ARDU-B0310", "model"), "hole_edge": (2.0, "ARDU-B0310", "model"),
        "axis_from_far_edge": (6.98, "ARDU-B0310", "model"),
        "holder_w": (22.0, "ARDU-B0310", "model"), "holder_d": (14.0, "ARDU-B0310", "model"), "holder_h": (8.5, "ARDU-B0310", "model"),
        "holder_screw_pitch": (18.0, "ARDU-B0310", "model"), "lens_thread_d": (12.0, "ARDU-B0310", "model"),
        "lens_head_d": (17.0, "ARDU-B0310", "model"), "lens_rim_d": (14.8, "ARDU-B0310", "model"),
        "back_to_rim": (15.57, "ARDU-B0310", "model"), "back_to_apex": (17.05, "ARDU-B0310", "model"),
        "holder_top_from_back": (10.1, "ARDU-B0310", "model"),
        "conn_w": (17.6, "ARDU-B0310", "model"), "conn_d": (5.2, "ARDU-B0310", "model"), "conn_h": (2.05, "ARDU-B0310", "model"),
        "conn_over": (0.71, "ARDU-B0310", "model"),
        "hfov_deg": (120.0, "ARDU-PAGE", "page"), "vfov_deg": (66.7, "ARDU-PAGE", "page"), "dfov_deg": (152.2, "ARDU-PAGE", "page"),
        "efl": (2.87, "ARDU-PAGE", "page"), "lens_head_len": (4.7, "EST", "EST"), "mass_g": (9.0, "EST", "EST"),
    }),
    "fpc": dict(name="Pi Zero camera cable, 22-pin to 15-pin", dims={
        "w15": (16.0, "RPI-FPC", "drawing"), "w22": (11.5, "RPI-FPC", "drawing"), "t": (0.1, "RPI-FPC", "drawing"),
        "t_stiff": (0.31, "RPI-FPC", "drawing"), "len": (150.0, "ARDU-PAGE", "page"),
    }),
    "cell": dict(name="Akyga LP902535 LiPo pack with protection board and NTC, 800 mAh", dims={
        "t_max": (9.5, "AKY-902535", "drawing"), "w_max": (26.0, "AKY-902535", "drawing"), "len_max": (37.5, "AKY-902535", "drawing"),
        "len_bare_max": (35.5, "AKY-902535", "drawing"), "capacity_mah": (800.0, "AKY-902535", "drawing"),
        "max_discharge_a": (0.8, "AKY-902535", "drawing"), "lead_awg": (24.0, "AKY-902535", "drawing"),
        "lead_len": (150.0, "AKY-902535", "drawing"), "mass_g": (16.0, "EST", "EST"),
    }),
    "spk": dict(name="Same Sky CES-20134-088PM enclosed micro speaker, 8 ohm, 0.8 W", dims={
        "len": (20.0, "SS-CES20134", "drawing"), "wid": (13.0, "SS-CES20134", "drawing"), "h": (4.87, "SS-CES20134", "drawing"),
        "across_lugs": (21.0, "SS-CES20134", "drawing"), "lug_pitch": (16.09, "SS-CES20134", "drawing"),
        "lug_d": (5.0, "SS-CES20134", "drawing"), "lug_hole_d": (2.0, "SS-CES20134", "drawing"),
        "lug_from_end": (7.5, "SS-CES20134", "drawing"), "mass_g": (2.0, "SS-CES20134", "drawing"), "lug_t": (1.0, "EST", "EST"),
    }),
    "amp": dict(name="Adafruit 3006: MAX98357A I2S amplifier breakout", dims={
        "len": (19.05, "ADA-3006", "design"), "wid": (17.78, "ADA-3006", "design"), "h": (3.0, "ADA-3006", "page"),
        "hole_d": (2.5, "ADA-3006", "design"), "mass_g": (1.2, "ADA-3006", "page"), "pcb_t": (1.6, "EST", "EST"),
    }),
    "mic": dict(name="Adafruit 3421: SPH0645LM4H I2S microphone breakout", dims={
        "len": (16.51, "ADA-3421", "design"), "wid": (12.70, "ADA-3421", "design"), "h": (1.8, "ADA-3421", "page"),
        "port_x": (8.255, "ADA-3421", "design"), "port_y": (7.822, "ADA-3421", "design"), "port_d": (1.025, "ADA-3421", "design"),
        "mass_g": (0.4, "ADA-3421", "page"), "pcb_t": (0.8, "EST", "EST"),
    }),
    "dac": dict(name="Adafruit 6250: PCM5102 I2S DAC with 3.5 mm jack", dims={
        "len": (30.48, "ADA-6250", "design"), "wid": (20.32, "ADA-6250", "design"), "h": (6.2, "ADA-6250", "page"),
        "len_with_jack": (32.5, "ADA-6250", "page"), "jack_cy": (10.16, "ADA-6250", "design"), "hole_d": (2.5, "ADA-6250", "design"),
        "hole_inset": (2.54, "ADA-6250", "design"), "mass_g": (2.8, "ADA-6250", "page"), "pcb_t": (1.6, "EST", "EST"),
        "jack_w": (6.0, "EST", "EST"), "jack_len": (12.0, "EST", "EST"), "jack_barrel_d": (6.0, "EST", "EST"),
    }),
    "chg": dict(name="Adafruit 6106: bq25185 USB-C LiPo charger with 5 V boost", dims={
        "len": (29.21, "ADA-6106", "design"), "wid": (19.05, "ADA-6106", "design"), "usb_cy": (9.525, "ADA-6106", "design"),
        "hole_d": (2.5, "ADA-6106", "design"), "hole_inset": (2.54, "ADA-6106", "design"), "out_a": (1.0, "ADA-6106", "page"),
        "pcb_t": (1.6, "EST", "EST"), "h": (5.2, "EST", "EST"), "mass_g": (3.0, "EST", "EST"),
    }),
    "usbc": dict(name="USB-C receptacle, 16-pin (as on the charger board)", dims={
        "w": (8.94, "HRO-USBC", "drawing"), "h": (3.26, "HRO-USBC", "drawing"), "d": (7.35, "HRO-USBC", "drawing"),
    }),
    "gauge": dict(name="Adafruit 5580: MAX17048 fuel gauge", dims={
        "len": (25.40, "ADA-5580", "design"), "wid": (20.32, "ADA-5580", "design"), "h_as_sold": (7.2, "ADA-5580", "page"),
        "hole_inset": (2.54, "ADA-5580", "design"), "mass_g": (2.6, "ADA-5580", "page"),
        "pcb_t": (1.6, "EST", "EST"), "h_no_connectors": (2.8, "EST", "EST"),
    }),
    "tact": dict(name="Alps Alpine SKQGABE010 tactile switch", dims={
        "w": (5.2, "ALPS-SKQG", "drawing"), "h": (1.5, "ALPS-SKQG", "drawing"), "travel": (0.25, "ALPS-SKQG", "drawing"),
        "force_n": (1.57, "ALPS-SKQG", "drawing"),
    }),
    "slide": dict(name="Shouhan MSK12C02 side-actuated slide switch", dims={
        "len": (8.0, "SH-MSK12C02", "drawing"), "d": (2.8, "SH-MSK12C02", "drawing"), "h": (1.4, "SH-MSK12C02", "drawing"),
        "lever_len": (1.5, "SH-MSK12C02", "drawing"), "lever_t": (1.0, "SH-MSK12C02", "drawing"), "travel": (1.6, "SH-MSK12C02", "drawing"),
        "lever_w": (1.3, "EST", "EST"),
    }),
    "det": dict(name="Alps Alpine SPVE110200 detector switch", dims={
        "len": (3.4, "ALPS-SPVE", "drawing"), "wid": (3.0, "ALPS-SPVE", "drawing"), "h": (2.3, "ALPS-SPVE", "drawing"),
        "plunger_free": (4.8, "ALPS-SPVE", "drawing"), "plunger_on": (4.5, "ALPS-SPVE", "drawing"), "plunger_full": (3.6, "ALPS-SPVE", "drawing"),
        "plunger_w": (0.75, "ALPS-SPVE", "drawing"),
    }),
    "motor": dict(name="Vybronics VC1026B002F coin vibration motor", dims={
        "d": (10.0, "VYB-VC1026", "drawing"), "t": (2.7, "VYB-VC1026", "drawing"), "lead_len": (27.0, "VYB-VC1026", "drawing"),
        "mass_g": (0.9, "EST", "EST"),
    }),
    "led_dot": dict(name="Wurth 150060WS75000 white LED, 0603", dims={
        "len": (1.6, "WE-0603", "drawing"), "wid": (0.8, "WE-0603", "drawing"), "h": (0.45, "WE-0603", "drawing"),
    }),
    "led_ring": dict(name="Cree J Series 2835, 2700 K, CRI 90", dims={
        "len": (3.5, "CREE-2835", "drawing"), "wid": (2.8, "CREE-2835", "drawing"), "h": (0.7, "CREE-2835", "drawing"),
    }),
    "spring": dict(name="Gutekunst T-18510L / T-18510R torsion spring, 1.4310", dims={
        "wire": (1.0, "GUT-T18510", "drawing"), "id": (5.5, "GUT-T18510", "drawing"), "coils": (6.5, "GUT-T18510", "drawing"),
        "body_len": (7.5, "GUT-T18510", "drawing"), "leg_len": (45.0, "GUT-T18510", "drawing"),
        "max_torque_nmm": (111.87, "GUT-T18510", "drawing"), "max_angle_deg": (93.82, "GUT-T18510", "drawing"),
    }),
    "st22": dict(name="Tapping screw ST2.2, pan head", dims={
        "head_d": (4.0, "ISO-7049", "drawing"), "head_h": (1.6, "ISO-7049", "drawing"), "thread_d": (2.2, "ISO-7049", "drawing"),
    }),
    "m3": dict(name="M3 button head screw and hex nut", dims={
        "head_d": (5.7, "ISO-7380", "page"), "head_h": (1.65, "ISO-7380", "page"), "nut_af": (5.5, "ISO-4032", "page"),
        "nut_h": (2.4, "ISO-4032", "page"),
    }),
    "sd": dict(name="microSD card", dims={"len": (15.0, "SD", "page"), "wid": (11.0, "SD", "page"), "t": (1.0, "SD", "page")}),
    "shim": dict(name="Stainless shim 0.40 mm, 300-series full hard (blades)", dims={
        "t": (0.40, "RS-SHIM", "drawing"), "yield_mpa": (965.0, "RS-SHIM", "drawing"), "tensile_mpa": (1172.0, "RS-SHIM", "drawing"),
    }),
    "tube": dict(name="Stainless 304 tube (stick)", dims={
        "od_outer": (10.0, "TUBE-304", "page"), "wall": (0.5, "TUBE-304", "page"), "od_inner": (8.0, "EST", "EST"),
    }),
}


def PD(part, key):
    """Datasheet value of a bought part."""
    return PARTS[part]["dims"][key][0]


# Why each EST value is an estimate, and how to measure it on the real part. Every EST above must be here.
_H = "Not on the Raspberry Pi drawing: only the 5.3 mm overall thickness is published."
_T = "Board thickness is not in the maker's board file; the usual thickness is assumed."
EST_WHY = {
    ("pi", "pcb_t"): ("Board thickness is not labelled on the Raspberry Pi drawing.", "Calipers across the bare board edge."),
    ("pi", "hdmi_h"): (_H, "Calipers, board face to the top of the mini-HDMI shell."),
    ("pi", "usb_h"): (_H, "Calipers, board face to the top of a micro-USB shell."),
    ("pi", "sd_h"): (_H, "Calipers, board face to the top of the card slot."),
    ("pi", "csi_h"): (_H, "Calipers, board face to the top of the camera connector."),
    ("pi", "sip_h"): (_H, "Calipers, board face to the top of the main chip. This sets the thermal pad thickness."),
    ("pi", "can_h"): (_H, "Calipers, board face to the top of the radio can."),
    ("cam", "lens_head_len"): ("The maker's 3D file shows the lens as one piece; where the wide head ends was read off it by eye.",
                               "Calipers along the lens barrel, front rim to the step down to the M12 thread."),
    ("cam", "mass_g"): ("Arducam does not publish the mass.", "Scale reading to 0.1 g, camera with lens, without cable."),
    ("cell", "mass_g"): ("The Akyga sheet gives no mass.", "Scale reading to 0.1 g, one pack with its leads."),
    ("spk", "lug_t"): ("The mounting-lug thickness is not dimensioned on the datasheet.", "Calipers across one lug."),
    ("amp", "pcb_t"): (_T, "Calipers across the board edge. Also check for a screw terminal block: it would add height."),
    ("mic", "pcb_t"): (_T + " (0.8 mm here: the page gives 1.8 mm overall with a 1.0 mm microphone.)", "Calipers across the board edge."),
    ("dac", "pcb_t"): (_T, "Calipers across the board edge."),
    ("dac", "jack_w"): ("No drawing we could tie to the jack fitted on this board.", "Calipers across the jack body."),
    ("dac", "jack_len"): ("No drawing we could tie to the jack fitted on this board.", "Calipers along the jack body."),
    ("dac", "jack_barrel_d"): ("No drawing we could tie to the jack fitted on this board.",
                               "Calipers across the round nose. The hole in the side wall is cut 0.2 mm larger all round."),
    ("chg", "pcb_t"): (_T, "Calipers across the board edge."),
    ("chg", "h"): ("The height of the tallest part (inductor or USB-C shell) is not published.", "Calipers, board underside to the tallest part."),
    ("chg", "mass_g"): ("Not published.", "Scale reading to 0.1 g."),
    ("gauge", "pcb_t"): (_T, "Calipers across the board edge."),
    ("gauge", "h_no_connectors"): ("Sold 7.2 mm tall with its JST and Stemma sockets. The model assumes they are removed and wires soldered on.",
                                   "Desolder the sockets, then calipers from the board underside to the tallest part left."),
    ("slide", "lever_w"): ("The lever width is not labelled on the MSK12C02 sheet.", "Calipers across the lever. The slider cap pocket is cut to it."),
    ("motor", "mass_g"): ("Not on the Vybronics sheet.", "Scale reading to 0.1 g."),
    ("tube", "od_inner"): ("We found a seller page for the 10 x 0.5 mm tube but none we could confirm for 8 x 0.5 mm.",
                           "Buy both, then check the 8 mm tube with its glide bush slides in the 9.0 mm bore of the 10 mm tube."),
}


# =====================================================================================
# 3D MODEL LAYER: where each part sits (unit frame unless noted). These are our layout
# choices, driven by the part sizes above. build_model.py reads only this file.
# =====================================================================================
SEAM_Y = -(UNIT_D - 4.0)                         # tub (front) / back cover split plane
TONGUE_T, TONGUE_H, TONGUE_GAP = 0.9, 1.8, 0.15   # cover tongue inside the tub wall
PIVOT_PIN_D = 3.0                                # M3 friction pivot of the tilt joint
LUG_T, LUG_GAP = 4.0, 6.2                         # tilt lugs under the unit, gap for the tongue

# ---- tolerances and fits the model is designed to (mm)
TOL = {
    "fdm": 0.2,      # general tolerance of a printed PETG part
    "sheet": 0.1,    # cut sheet metal outline
    "cut": 0.2,      # cut length of tube and pin
    "turn": 0.05,    # turned part
    "slide": 0.15,   # clearance per side for a printed sliding fit (button cap in its opening, cover tongue)
    "pin": 0.05,     # clearance per side for a steel pin in a drilled hole
    "seat": 0.30,    # least clearance we allow between a bought part and anything it does not touch
}

# ---- camera: lens front just inside the facet, board on two posts and a lower cradle
CAM_LENS_RECESS = 0.4                            # lens dome apex this far behind the outer facet surface
LENS_OPENING_D = PD("cam", "lens_rim_d") + 0.4   # hole in the bezel for the lens rim

# ---- Pi Zero 2 W: against the back cover, parts facing the cover (heat path), GPIO edge up
PI_Z0 = 6.2                                      # lower long edge
CELL_POCKET_T = 10.5                             # room left for a cell up to 10.5 mm thick (documented cell is 9.5)
CELL_GAP_X = 0.4                                 # between the camera board and each cell
CELL_Z0 = 2.2                                    # bottom of the cells
SPREADER = (40.0, 21.0, 1.0)                     # aluminium heat spreader on the cover (x, z, thickness)

# ---- controls
ASK_D, ASK_XY = 13.0, (0.0, -19.0)               # top, centre
BAR_SIZE = (10.0, 4.4)                           # Play/Pause, Back and Forward caps (capsules along x)
BAR_Y, NAV_X = -7.0, 15.0                        # Back at -x, Play/Pause at 0, Forward at +x
VOL_SIZE, VOL_Y, VOL_Z = (6.0, 3.5), -7.6, (33.0, 26.0)   # left side: Vol+ above Vol-
MUTE_Z = 20.4                                    # left side slide switch (lever height)
DOT_X, DOT_Z, DOT_D = (-34.0, -28.0, -22.0, -16.0), 39.5, 2.4
SPK_X, SPK_Z0 = 21.0, 19.2                       # speaker centre x and lower end, behind the front grille
MIC_X0 = 20.4                                    # inner edge of each microphone board, under the top

# ---- stick / hub / legs (book frame)
TUBE_OUT_Z = (-7.5, 96.0)                        # outer tube runs through the hub
TUBE_IN_Z0, TUBE_IN_LEN = -5.5, 105.5            # inner tube bottom (collapsed) and length; it stops 2 mm above the
#   foot of the outer tube so the hub-sensor lead can pass under it
COLLAR = (13.0, 89.5, 97.0)                      # twist-lock collar OD, z0, z1
LEG_PIVOT = (-50.0, -8.0)                        # rear-leg pivot axis (y, z), along x
LEG_CHORD = 57.0                                 # pivot -> pad centre
PAD = (REAR_FOOT_W, 14.0, 2.0)                   # TPU pad x, along-leg, thickness
KNUCKLE_PIN = (-33.2, -1.4)                      # blade-knuckle pin (y, z), along x
CLAMP_Y = -30.5                                  # blade clamp screw (M1.6), 2.7 in front of the knuckle pin so 1 mm of plastic stays between them
CORD_D = 0.9                                     # hub-sensor cord: two fine wires side by side, laid as one 0.9 mm round
CORD_ENTRY = (0.0, -25.6)                        # where the cord enters the unit: hole in the bottom, between the tilt lugs (x, y)
BLADE_ROOT_Z = -4.0                              # blade root height (book frame, hub centred on z=0)
BLADE_ROOT_Y = -36.5
SPRING_PRELOAD_DEG = 20.0                        # each spring is wound this far when the leg first meets it
#   (20 + 70 = 90 degrees at a leg angle of 180, inside the 93.82 degrees the stock spring allows)
SPRING_ENGAGE_DEG = 110.0                        # leg angle at which the springs start to act (clamp range only)
COVER_HARD, BLOCK_HARD = 3.0, 12.0               # hardcover scene: cover board and page-block thickness at the gutter
COVER_SOFT, BLOCK_SOFT = 0.4, 4.0                # thin paperback scene
COVER_THICK, BLOCK_THICK = 3.0, 30.0             # thick reference book scene (stick extended)

# ---- material densities (g/cm3) for volume-based mass checks
RHO = {"petg": 1.27, "tpu": 1.21, "steel": 7.9, "al": 2.70, "pmma": 1.18, "brass": 8.5}
