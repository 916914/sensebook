import math
from coverage_standard_lens_scan import analyse
def angmargins(h,d,th,W=460,D=300,hfov=66,vfov=41):
    # angular margins: horizontal at top corners, vertical at top and bottom edges
    t=math.radians(th)
    out=[]
    zt=d*math.sin(t)+h*math.cos(t)
    ah=math.degrees(math.atan((W/2)/zt))
    at=math.degrees(math.atan2(d,h)); ab=math.degrees(math.atan2(D+d,h))
    return hfov/2-ah, vfov/2-(th-at), vfov/2-(ab-th)
print("h d theta | Hmargin(deg) Vtop Vbot | dpi_min dpi_centre dpi_top")
for h in (340,350,360,370,375,380,385,390,395,400):
  for d in (0,10,20,30,40):
    best=None
    for t10 in range(0,350,1):
        th=t10/10
        mh,mt,mb=angmargins(h,d,th)
        m=min(mh,mt,mb)
        if best is None or m>best[0]: best=(m,th,mh,mt,mb)
    m,th,mh,mt,mb=best
    wx,wy,mn,dp=analyse(h,d,th)
    cen=[x for x in dp if abs(x[0]-150)<1][0]
    top=dp[0]; bot=dp[-1]
    print(f"{h} {d:3d} {th:5.1f} | {mh:5.2f} {mt:5.2f} {mb:5.2f} | {mn:6.1f} cen x{cen[1]:.0f}/y{cen[2]:.0f} top x{top[1]:.0f}/y{top[2]:.0f} bot x{bot[1]:.0f}/y{bot[2]:.0f}")
