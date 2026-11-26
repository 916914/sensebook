"""SenseBook WIP - camera coverage / dpi, page-turn clearance and stability estimates
for the webcam-sized head on a short stick at the top of the spine.

Coordinates (mm): x across the spread (spine at x=0), y toward the reader
(book top edge at y=0, reader-side edge at y=300), z up from the table.
Lens at (0, -d, h): d = setback BEHIND the book's top edge, h = height above table.
Tilt theta = angle of the optical axis from straight down, toward the reader.
Sensor long axis parallel to x (spread width).

Lens models (IMX708, 4608 x 2592 px, 1.4 um pixels):
  WIDE     f = 2.75 mm -> 1964 px paraxial; radial model r = f*t/(1 + a t^2 + b t^4), t = tan(field angle)
           a, b fitted so the image edges sit exactly at the published 102 deg H and 67 deg V.
           (The published 120 deg diagonal implies even stronger corner barrel; corner dpi here
           is therefore an optimistic estimate - verify with a printed chart.)
  STANDARD pinhole with f chosen to match the published 66 deg H (3548 px).
All numbers are ESTIMATES from geometry; nothing here has been measured.
"""
import math

W, D = 460.0, 300.0          # design spread (mm)
HALF_U, HALF_V = 2304.0, 1296.0


def fit_wide():
    f = 2.75 / 0.0014
    t1, t2 = math.tan(math.radians(33.5)), math.tan(math.radians(51.0))
    # f*t/(1+a t^2+b t^4) = r  ->  a t^2 + b t^4 = f t / r - 1
    r1, r2 = HALF_V, HALF_U
    c1, c2 = f * t1 / r1 - 1, f * t2 / r2 - 1
    # solve 2x2
    A = [[t1**2, t1**4], [t2**2, t2**4]]
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    a = (c1 * A[1][1] - A[0][1] * c2) / det
    b = (A[0][0] * c2 - c1 * A[1][0]) / det
    return f, a, b


WIDE = dict(name="CM3 Wide (102x67)", f=fit_wide()[0], a=fit_wide()[1], b=fit_wide()[2])
STD = dict(name="CM3 Standard (66x41)", f=HALF_U / math.tan(math.radians(33.0)), a=0.0, b=0.0)


def project(lens, h, d, th_deg, x, y):
    """Return image (u, v) in px for table point (x, y, 0); None if behind camera."""
    th = math.radians(th_deg)
    px, py, pz = x, y + d, -h                       # vector lens -> point
    zc = py * math.sin(th) - pz * math.cos(th)      # along optical axis
    yc = py * math.cos(th) + pz * math.sin(th)      # image 'vertical' (toward reader = +)
    xc = px
    if zc <= 0:
        return None
    tx, ty = xc / zc, yc / zc
    t = math.hypot(tx, ty)
    if t == 0:
        return 0.0, 0.0
    r = lens["f"] * t / (1 + lens["a"] * t * t + lens["b"] * t**4)
    return r * tx / t, r * ty / t


def margins(lens, h, d, th):
    """Min fractional margin to the image border over the spread outline (1.0 = centre, 0 = edge)."""
    worst = 9.0
    for i in range(0, 47):
        for y in (0.0, D):
            x = -W / 2 + W * i / 46
            p = project(lens, h, d, th, x, y)
            if p is None:
                return -9
            worst = min(worst, 1 - abs(p[0]) / HALF_U, 1 - abs(p[1]) / HALF_V)
    for j in range(0, 31):
        y = D * j / 30
        for x in (-W / 2, W / 2):
            p = project(lens, h, d, th, x, y)
            if p is None:
                return -9
            worst = min(worst, 1 - abs(p[0]) / HALF_U, 1 - abs(p[1]) / HALF_V)
    return worst


def dpi(lens, h, d, th, x, y, e=0.5):
    """Local sampling (dots per inch) along page x and page y; returns min of the two."""
    p0 = project(lens, h, d, th, x, y)
    px_ = project(lens, h, d, th, x + e, y)
    py_ = project(lens, h, d, th, x, y + e)
    sx = math.hypot(px_[0] - p0[0], px_[1] - p0[1]) / e * 25.4
    sy = math.hypot(py_[0] - p0[0], py_[1] - p0[1]) / e * 25.4
    return min(sx, sy), sx, sy


def best_tilt(lens, h, d):
    best = (-9, 0)
    for t10 in range(0, 600):
        th = t10 / 10
        m = margins(lens, h, d, th)
        if m > best[0]:
            best = (m, th)
    return best


def report_row(lens, h, d):
    m, th = best_tilt(lens, h, d)
    pts = {
        "top-edge centre (0,0)": (0, 0),
        "page centre (0,150)": (0, 150),
        "reader edge centre (0,300)": (0, 300),
        "reader-side corner (230,300)": (230, 300),
        "top corner (230,0)": (230, 0),
    }
    vals = {k: dpi(lens, h, d, th, *v)[0] for k, v in pts.items()}
    return m, th, vals


if __name__ == "__main__":
    print("WIDE model a=%.4f b=%.4f f=%.0f px" % (WIDE["a"], WIDE["b"], WIDE["f"]))
    print("\n=== Minimum lens height for full 46 x 30 cm coverage (best tilt) ===")
    for lens in (WIDE, STD):
        for d in (0, 20, 40, 60):
            hmin0 = hmin5 = None
            for h in range(120, 460, 2):
                m, th = best_tilt(lens, h, d)
                if hmin0 is None and m >= 0:
                    hmin0 = (h, th)
                if hmin5 is None and m >= 0.05:
                    hmin5 = (h, th)
                    break
            print(f"{lens['name']:22s} setback {d:3d} mm: zero-margin h={hmin0}, 5%-margin h={hmin5}")

    print("\n=== WIDE: dpi at key points (best tilt for each case) ===")
    print("h   d  | tilt  margin | top-edge  centre  reader-edge  reader-corner  top-corner")
    for h in (180, 200, 220, 240, 260, 280, 300):
        for d in (20, 40, 60):
            m, th, v = report_row(WIDE, h, d)
            vv = list(v.values())
            print(f"{h} {d:3d} | {th:4.1f}  {m*100:5.1f}% | {vv[0]:7.0f} {vv[1]:7.0f} {vv[3-1]:9.0f} {vv[3]:12.0f} {vv[4]:11.0f}")
