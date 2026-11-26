import math
H=66.0; V=41.0
def analyse(h,d,th,W=460,D=300,hfov=H,vfov=V,npx=4608):
    th=math.radians(th); tx=math.tan(math.radians(hfov/2)); ty=math.tan(math.radians(vfov/2))
    f=(npx/2)/tx
    worst_x=0; worst_y=0; dpis=[]
    for yi in range(0,31):
        y=D*yi/30
        u=y+d  # horizontal offset toward reader from lens
        zc=u*math.sin(th)+h*math.cos(th)
        yc=u*math.cos(th)-h*math.sin(th)
        rx=(W/2)/zc/tx; ry=abs(yc/zc)/ty
        worst_x=max(worst_x,rx); worst_y=max(worst_y,ry)
        # scales px/mm
        sx=f/zc
        a=math.atan2(u,h); R2=u*u+h*h
        sy=f*h/(R2*math.cos(a-th)**2)
        dpis.append((y,sx*25.4,sy*25.4))
    mn=min(min(a[1],a[2]) for a in dpis)
    return worst_x,worst_y,mn,dpis
best={}
for h in range(330,421,5):
  res=[]
  for d in range(-20,121,5):
    for t10 in range(0,400,5):
      th=t10/10
      wx,wy,mn,_=analyse(h,d,th)
      res.append((max(wx,wy),wx,wy,mn,d,th))
  ok=[r for r in res if r[3]>=150]
  r=min(ok) if ok else None
  r2=min(res)
  print(h,'best(dpi>=150):',None if r is None else tuple(round(v,3) for v in r),' best any:',tuple(round(v,3) for v in r2))
