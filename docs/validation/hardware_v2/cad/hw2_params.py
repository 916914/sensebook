"""SenseBook hardware v2 proposal: every new dimension, mass and source in one place (mm, degrees, grams).

Built ON TOP of the build chat's v1 model (design/cad/sb_params.py and build_model.py, read-only).
Everything v1 already defines (outer shell 88 x 40 x 34 mm, stick, hub, blades, rear leg, buttons, side
controls, jack, USB-C, status dots, top microphones, cover screws, heat spreader) is reused unchanged.
This file only adds or replaces what v2 changes.

Frames are the v1 frames (see sb_params.py): UNIT frame for parts in the head (x across, +y toward the
reader, z up; front face y = 0, back y = -34), BOOK frame for the hub, stick and legs.
Facet-local coordinates (u, v, a) are v1's: u = x, v = up the lens facet, a = depth into the unit.

Sources (research notes in the session notes folder, 27 Nov 2026):
  [R1] compute_radio_power.md: RK3576 package, memory and radio module sizes and prices
  [R2] camera_audio_light_battery.md: camera FOV, speaker, sensors, LED driver, lens sizes
  [D1] design/cad/out/analysis_results.json: lens height and tip at the 9 cm stick (build chat)
EST = our estimate, not from a datasheet. Nothing has been built or measured.
"""

# ------------------------------------------------------------------ cameras (4 x 50 MP, stock phone-type AF modules)
# Sensor: Samsung S5KJN1-class 50 MP, 8160 x 6144 px, 1/2.76" [R2]. Module size EST 8.5-9.5 mm square [R2].
SENSOR_PX = (8160, 6144)
# All four cameras sit on v1's sloped lens facet (it already faces the page), in one row:
#   far-left, near-left, ToF sensor, near-right, far-right. Facet coords (u, v); lens front at depth CAM_A.
NEAR_HFOV = 108.0              # typical phone "120 deg" ultra-wide gives about 108 deg horizontal [R2]
FAR_HFOV = 60.0                # 50 MP S5KJN1 with a ~4.5 mm lens (EST: the listed module has 4.15 mm = 64 deg [R2]).
                               # 64 deg gave 298 dpi at the far text corners once lens distortion is counted; 60 deg gives ~315.
NEAR_DISTORTION = -0.10        # barrel distortion at the sensor corner (r_d = r (1 + D r^2/r_corner^2)), EST for an ultra-wide
FAR_DISTORTION = -0.02         # EST for a normal phone main lens (listed modules quote <1.5% [R2]); used in every dpi number
NEAR_UV = (13.0, 0.0)
FAR_UV = (25.0, 0.0)            # 25 not 27: the far-right module must clear v1's headphone jack (x >= 30)
NEAR_A = 1.5                   # lens front depth behind the outer facet, near pair (tilt ~4 deg; window pane is 0.2-1.0 mm deep)
FAR_A = 1.8                    # far pair: tilted ~10 deg, so set deeper to keep the barrel edge behind the pane
                               # (v1 used 1.4 for its untilted lens). Shallower near lenses keep their window clear of the light strips.
NEAR_BODY = (8.5, 8.5, 5.4)    # module body w x h x depth behind the barrel (EST)
NEAR_BARREL = (2.6, 1.2)       # lens barrel radius, length (EST)
FAR_BODY = (8.5, 8.5, 6.2)     # (EST; longer lens than the wide)
FAR_BARREL = (2.8, 2.0)        # (EST; ~0.4 mm longer for the ~4.5 mm lens)
CAM_STIFF = 0.5                # module stiffener plate thickness (EST)
CAM_MASS = 1.0                 # g per module (EST)
WINDOW_T = 0.8                 # clear window thickness (PMMA), set inside the wall
WINDOW_MARGIN_DEG = 4.0        # window opening = field of view + this margin on every side
# Aims: build_v2.py searches yaw/pitch; among aims that reach TARGET_DPI it takes the one closest to the facet normal
# (less tilt = the module sits flatter behind the facet). Facet normal = 55.5 deg below horizontal at the 9 cm stick [D1].
SEARCH_DOWN = [30.0 + i for i in range(36)]              # 30 .. 65 deg below horizontal (book frame), 1 deg steps
SEARCH_YAW = [1.0 * i for i in range(41)]                # 0 .. 40 deg outward, 1 deg steps
MAX_TILT = 10.5                # no module may tilt more than this from the facet normal, or it hits the shell and the light strips
                               # (found with the model: at ~22 deg they did). The search picks the best aim inside this limit.
NEAR_START_AIM = (56.0, 6.0)   # where the alternating search starts the near pair (down, yaw)

# ------------------------------------------------------------------ page geometry used by the checks
SPREAD = (370.0, 245.0)        # textbook spread, same as v1 analysis [D1]
TEXT_MARGIN = dict(top=15.0, bottom=15.0, outer=18.0, gutter=15.0)   # printed area (EST, typical textbook)
TARGET_DPI = 300.0

# ------------------------------------------------------------------ zoned light bar (replaces the v1 light ring)
# Two strips on the facet, above and below the camera row. The lower strip has a gap in the middle where
# the near-camera and ToF flex cables pass down to the board.
LIGHT_TOP = dict(v=(6.6, 10.8), u=((-30.0, 30.0),))
LIGHT_BOTTOM = dict(v=(-11.4, -7.6), u=((-30.5, -11.0), (11.0, 30.5)))   # 3.8 mm tall, set low to clear the camera windows
LED_TOP_U = tuple(-27.5 + 5.0 * k for k in range(12))           # 12 LEDs
LED_BOTTOM_U = (-29.0, -24.0, -19.0, -14.0, 14.0, 19.0, 24.0, 29.0)  # 8 LEDs -> 20 in all (LP5024 has 24 channels)
LED_PKG = (2.0, 1.6, 0.7)      # 2016 mid-power LED, CRI >= 90 (EST; efficacy ~155-175 lm/W claimed [R2])
LED_DRIVER = (4.0, 4.0, 0.8)   # TI LP5024, 24 channels at 35 mA [R2]
LIGHT_TARGET_LUX = (300.0, 750.0)  # every point on the printed area, darkest to brightest

# ------------------------------------------------------------------ hand / page-turn sensor (replaces the v1 lens window)
TOF = (6.4, 3.0, 1.75)         # ST VL53L8CX multizone ToF, 45 x 45 deg view [R2]
TOF_WINDOW = (7.4, 4.0)        # clear slot

# ------------------------------------------------------------------ main board (same outline and holes as the Pi Zero, so v1's standoffs fit)
BOARD = (65.0, 30.0, 1.0)      # PCB, 8-layer HDI (EST)
# (label, x0, x1, z0, z1, height above the PCB on the cover side, mass g, source)
BOARD_PARTS = [
    ("soc_rk3576", "Rockchip RK3576 SoC, 6 TOPS NPU, 16.1 x 17.2 mm FCCSP [R1]", -5.6, 11.6, 10.75, 26.85, 1.3, 0.9),
    ("ram_lpddr4x", "LPDDR4X 2 GB, 10 x 14.5 mm (memory doubled in price in 2026 [R1])", -21.5, -7.0, 21.0, 31.0, 1.0, 0.4),
    ("emmc", "eMMC 16 GB, 11.5 x 13 mm [R1]", -21.5, -8.5, 8.2, 19.7, 1.0, 0.4),
    ("pmic", "Power management IC (RK806-class, EST 7 x 7 mm)", 13.0, 20.0, 24.0, 31.0, 0.9, 0.1),
    ("wifi_bt", "Wi-Fi 6 + Bluetooth 5.4 module, Quectel FCS960K-class, 12 x 12 x 2.0 mm [R1]", 13.5, 25.5, 8.5, 20.5, 2.0, 0.5),
    ("bt_audio", "Low-power Bluetooth audio SoC: plays and streams while the main SoC sleeps (EST 5 x 5 mm)", -27.5, -22.5, 12.0, 17.0, 0.9, 0.05),
    ("charger", "1-cell charger with power path, TI BQ25895-class, 4 x 4 mm [R1]", -27.0, -23.0, 19.0, 23.0, 0.8, 0.05),
    ("usb_pd", "USB-C PD controller (EST 3 x 3 mm; the charger has no PD [R1])", -27.0, -24.0, 24.5, 27.5, 0.8, 0.02),
    ("fuel_gauge", "Fuel gauge, MAX17260, 1.5 x 1.5 mm [R1]", -27.0, -25.5, 9.5, 11.0, 0.6, 0.01),
    ("smart_amp", "Smart speaker amplifier, TI TAS2563, 2.5 x 3.0 mm [R2]", 21.5, 24.0, 25.0, 28.0, 0.6, 0.01),
    ("imu", "6-axis motion sensor, ST LSM6DSV, 2.5 x 3.0 mm [R2]", 25.5, 28.0, 22.0, 25.0, 0.83, 0.01),
    ("led_driver", "LED driver, TI LP5024, 24 channels, 4 x 4 mm [R2]", -6.0, -2.0, 28.0, 32.0, 0.8, 0.02),
    ("conn_far_left", "FPC connector: far-left camera + light bars", -24.5, -18.5, 4.2, 7.4, 1.0, 0.05),
    ("conn_near_left", "FPC connector: near-left camera", -10.0, -4.0, 4.2, 7.4, 1.0, 0.05),
    ("conn_tof", "FPC connector: ToF sensor", -2.8, 2.8, 4.2, 7.4, 1.0, 0.05),
    ("conn_near_right", "FPC connector: near-right camera", 4.0, 10.0, 4.2, 7.4, 1.0, 0.05),
    ("conn_far_right", "FPC connector: far-right camera", 18.5, 24.5, 4.2, 7.4, 1.0, 0.05),
    ("conn_top", "Board-to-board connector: buttons, speaker, mics, status LEDs, haptic", 0.0, 6.0, 30.2, 33.4, 1.0, 0.05),
]
ANTENNA = (30.0, 5.0, 0.2)     # flex antenna on the inside of the top wall, at the back, away from the steel stick (EST)

# ------------------------------------------------------------------ cells: three pouch cells in parallel, filling the space the Pi-era parts used
CELL_R = 1.5
# Stepped cells: an upper cell at full depth above the camera row, a thinner lower cell behind the cameras.
# The step height and the lower cells' front face are computed in build_v2.py from the camera modules (0.7 mm gap).
CELL_SIDE_X = (11.8, 37.6)
CELL_CENTER_X = (-9.2, 9.2)
CELL_Y_BACK, CELL_Y_FRONT = -27.2, -15.8
CELL_Z = dict(side=(4.0, 34.4), center=(8.0, 30.6))
CELL_GAP = 0.7
# Front cell: the block above the camera row and behind the front wall, free once every camera sits on the facet.
# x stops short of the USB-C sub-board (x 33); the top stays under the v1 top-button boards; z0 = the step height.
CELL_FRONT = dict(x=(-37.5, 32.4), y=(-15.1, -6.0), z1=33.0)
# [R2]: Grepow shaped cells up to 460 Wh/L; 4.45 V cells ~500-600 Wh/L for a small custom cell (EST, low end used);
# phones claim 805-850 Wh/L for silicon-carbon cells (small cells lose some of that to seals and tabs).
CELL_WH_PER_L = dict(generic_lipo=460.0, high_voltage_4v45=600.0, silicon_carbon=800.0)
CELL_DENSITY = 2.0             # g/cm3 (EST; a 102535 cell is about 17 g for 8.75 cm3)
USABLE = 0.92                  # usable share after protection cut-off (EST)

# ------------------------------------------------------------------ speaker and front parts
SPEAKER = (15.0, 11.0, 3.0)    # Soberton 1511 box speaker, 90 dB at 0.6 W, 10 cm [R2]
SPEAKER_XZ = (0.0, 28.0)
GRILLE = dict(cols=5, rows=3, pitch=2.6, r=0.55)
MIC3_XZ = (13.5, 34.0)         # third microphone, front, for echo cancellation and beamforming
HAPTIC_A = (0.0, -21.0, 31.2, 5.0, 2.7)   # Option A: coin motor under the top, x, y, z0, radius, thickness

# ------------------------------------------------------------------ Option B controls (book frame): hub wings + pocket clicker
WING_X = (13.0, 36.5)          # each wing spans |x| (touches the hub side at 13)
WING_Y = (-48.0, -38.5)        # behind the blade knuckles' folding path (knuckles reach y -37.2 when folded)
WING_Z = (-2.0, 10.0)
WING_KEYS = [("ask", 20.5, 6.5), ("forward", 31.0, 3.4), ("back", -31.0, 3.4), ("play_pause", -20.5, 0.0)]
CLICKER = (205.0, 241.0, 108.0, 136.0, 9.0)   # on the table beside the book: x0, x1, y0, y1, height (EST 36 x 28 x 9)
CLICKER_MASS = 12.0

# ------------------------------------------------------------------ power budget (estimates) used for battery hours
POWER_W = dict(
    light_off=(0.35, 0.65),    # main SoC asleep between page turns; BT-audio SoC plays; amp at reading volume (EST)
    light_on_extra=(0.6, 0.95),  # zoned light, 300+ lux on the printed area (EST, from the light model)
)

# ------------------------------------------------------------------ flex cable routes (x where each flex runs back under the cells)
FLEX_X = dict(near=7.0, far=21.5, tof=0.0, far_drop=33.0)
