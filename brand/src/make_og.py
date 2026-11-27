"""Render the social-sharing image for the hub site (1200 x 630). Output: brand/site/og.png. Apache-2.0."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brandkit as bk
import brandcss
import render

OUT = os.path.join(bk.BRAND, "site")


def main():
    os.makedirs(OUT, exist_ok=True)
    inner, w, h = bk.lockup(bk.MARK, bk.C["paper"], bk.C["marigold"], bk.C["paper"], size=44)
    lock = bk.svg(inner, round(w), round(h), vb=f"0 0 {w:.1f} {h:.1f}")
    with open(os.path.join(bk.BRAND, "illustration", "sensebook-on-book.svg"), encoding="utf-8") as f:
        ill = f.read()
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>{brandcss.font_faces(brandcss.file_base())}
body{{margin:0;width:1200px;height:630px;background:{bk.C['spine']};color:{bk.C['paper']};font-family:{brandcss.SANS};overflow:hidden;position:relative}}
.t{{position:absolute;left:64px;top:150px;width:560px;font:600 58px/1.05 {brandcss.SERIF}}} .b{{position:absolute;left:64px;top:370px;font:600 34px/1.4 "Noto Serif Bengali";color:{bk.C['marigold']}}}
.l{{position:absolute;left:64px;top:52px}} .i{{position:absolute;right:-40px;bottom:40px;width:640px;background:{bk.C['paper']};border-radius:24px;padding:20px}}
.s{{position:absolute;left:64px;bottom:48px;font-size:22px;color:#BFD2D3}}</style></head><body>
<div class="l">{lock}</div><div class="t">Knowledge, now conversational.</div><div class="b">বই এখন কথা বলে</div>
<div class="i">{ill.replace('<svg ', '<svg style="width:100%;height:auto" ', 1)}</div><div class="s">Personal learning technology · open source</div></body></html>"""
    p = os.path.join(OUT, "og.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(page)
    render.png(p, os.path.join(OUT, "og.png"), 1200, 630)
    print("og image written")


if __name__ == "__main__":
    main()
