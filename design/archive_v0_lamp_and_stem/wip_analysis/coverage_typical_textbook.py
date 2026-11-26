"""WIP: same model as coverage_wide_head.py, for a typical NCTB secondary textbook spread
(page ~18.5 x 24.5 cm -> spread ~37 x 24.5 cm). ESTIMATES only."""
import coverage_wide_head as c
c.W, c.D = 370.0, 245.0
for lens in (c.WIDE, c.STD):
    for d in (20, 40, 60):
        hmin = None
        for h in range(120, 460, 2):
            m, th = c.best_tilt(lens, h, d)
            if m >= 0.05:
                hmin = (h, th); break
        h, th = hmin
        far = c.dpi(lens, h, d, th, 0, c.D)[0]; cen = c.dpi(lens, h, d, th, 0, c.D/2)[0]
        cor = c.dpi(lens, h, d, th, c.W/2, c.D)[0]; top = c.dpi(lens, h, d, th, 0, 0)[0]
        print(f"{lens['name']:22s} d={d:2d}: h(5% margin)={h} tilt={th:.1f}  dpi top={top:.0f} centre={cen:.0f} reader-edge={far:.0f} reader-corner={cor:.0f}")
