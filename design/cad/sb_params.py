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
UNIT_W, UNIT_H, UNIT_D = 88.0, 40.0, 34.0      # grew from 85x38x30 target (see doc 5.2)
WALL = 1.8                                      # PC/ABS intent; print in PETG at 1.8 mm
R_FRONT = 9.0                                   # front-view corner radius (x-z)
R_EDGE = 4.0                                    # soft edge round on front/back perimeters
# Lens facet (unit frame): plane at FACET_ANGLE from horizontal, lens normal to it
FACET_ANGLE = 45.0                              # facet & internal camera axis: 45 deg below unit horizontal
FACET_TOP_Z = 17.0                              # where the facet meets the front face
FACET_BOT_Y = -17.0                             # where the facet meets the bottom
LENS_Y, LENS_Z = -8.5, 8.5                      # lens front centre, on the facet mid-line
LENS_WIN_D = 14.0                               # clear glass window
RING_OD, RING_ID = 20.0, 15.0                   # light-ring diffuser

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
HUB_W, HUB_D, HUB_H = 26.0, 18.0, 20.0
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
MASS = {
    "unit_shells": 24.0, "pi_zero_2w": 11.0, "camera_m12": 9.0, "lipo_2x102535": 34.0,
    "speaker": 4.0, "audio_boards": 6.0, "power_boards": 4.0, "leds_buttons_motor": 6.0,
    "spreader_wiring": 6.0,
    "tilt_joint": 5.0, "stick_tubes_cord": 13.0,
    "hub_spring": 9.0, "blades": 2.0, "rear_leg_pad": 4.0,
}


def unit_mass():
    keys = ["unit_shells", "pi_zero_2w", "camera_m12", "lipo_2x102535", "speaker",
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
