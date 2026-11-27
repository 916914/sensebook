"""Finish the renders: add part labels and dimensions, flatten onto a plain background, save for the web.

Run after render_scenes.py, from design/cad:
    ..\\.venv\\Scripts\\python.exe annotate.py

Raw renders and their *.anchors.json move to design/cad/build/raw/ (not committed); the finished
pictures stay in design/renders/. Photographic scenes are saved as JPEG, labelled views as PNG.
Dimensions written on the pictures are read from the model, not typed in.
"""
import glob
import json
import math
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
RENDERS = os.path.normpath(os.path.join(HERE, "..", "renders"))
RAW = os.path.join(HERE, "build", "raw")
BG = (244, 244, 241)
INK = (29, 42, 46)
LINE = (104, 120, 125)
ACCENT = (192, 112, 20)
FONTS = r"C:\Windows\Fonts"


def font(size, bold=False):
    for n in (("seguisb.ttf" if bold else "segoeui.ttf"), "arial.ttf"):
        try:
            return ImageFont.truetype(os.path.join(FONTS, n), size)
        except OSError:
            continue
    return ImageFont.load_default()


def flatten(im):
    bg = Image.new("RGBA", im.size, BG + (255,))
    bg.alpha_composite(im.convert("RGBA"))
    return bg.convert("RGB")


def spread(ys, lo, hi, gap):
    """Keep the order, enforce a minimum gap, stay inside [lo, hi]."""
    n = len(ys)
    if n == 0:
        return []
    gap = min(gap, (hi - lo) / max(n - 1, 1))
    out = list(ys)
    for _ in range(200):
        moved = False
        for i in range(1, n):
            if out[i] - out[i - 1] < gap:
                mid = (out[i] + out[i - 1]) / 2
                out[i - 1], out[i] = mid - gap / 2, mid + gap / 2
                moved = True
        shift = max(0, lo - out[0]) - max(0, out[-1] - hi)
        out = [y + shift for y in out]
        if not moved:
            break
    for i in range(1, n):
        out[i] = max(out[i], out[i - 1] + gap * 0.999)
    over = out[-1] - hi
    if over > 0:
        out = [y - over for y in out]
    return out


def labelled(name, im, data, margin=None):
    W, H = im.size
    k = W / 2000.0
    margin = margin or int(470 * k)
    f = font(int(30 * k))
    canvas = Image.new("RGB", (W + 2 * margin, H), BG)
    canvas.paste(flatten(im), (margin, 0))
    d = ImageDraw.Draw(canvas)
    seen, items = set(), []
    for it in data["items"]:
        side = "L" if it["x"] < W / 2 else "R"
        key = (it["label"], side)
        if key in seen:
            continue
        seen.add(key)
        items.append(dict(label=it["label"], x=it["x"] + margin, y=it["y"], side=side))
    # balance the two columns
    for side, other in (("L", "R"), ("R", "L")):
        col = [i for i in items if i["side"] == side]
        oth = [i for i in items if i["side"] == other]
        while len(col) - len(oth) > 3:
            mv = max(col, key=lambda i: i["x"]) if side == "L" else min(col, key=lambda i: i["x"])
            mv["side"] = other
            col.remove(mv)
            oth.append(mv)
    for side in ("L", "R"):
        col = sorted([i for i in items if i["side"] == side], key=lambda i: i["y"])
        ys = spread([i["y"] for i in col], 46 * k, H - 46 * k, 50 * k)
        for it, y in zip(col, ys):
            tw = d.textlength(it["label"], font=f)
            if side == "L":
                tx = margin - 46 * k - tw
                x0, x1 = margin - 34 * k, margin - 6 * k
            else:
                tx = W + margin + 46 * k
                x0, x1 = W + margin + 34 * k, W + margin + 6 * k
            d.line([(x0, y), (x1, y), (it["x"], it["y"])], fill=LINE, width=max(2, int(2 * k)))
            r = 6 * k
            d.ellipse([it["x"] - r, it["y"] - r, it["x"] + r, it["y"] + r], fill=(255, 255, 255), outline=INK, width=max(2, int(2 * k)))
            d.text((tx, y - 20 * k), it["label"], font=f, fill=INK)
    canvas.save(os.path.join(RENDERS, name + ".png"), optimize=True)


def dim(d, p0, p1, text, f, off=0.0, horizontal=True, k=1.0, side=1, tpos=0.5):
    """Dimension line between two pixel points, drawn at an offset."""
    if horizontal:
        y = (p0[1] if off == 0 else off)
        a, b = (p0[0], y), (p1[0], y)
        d.line([p0, a], fill=LINE, width=1)
        d.line([p1, b], fill=LINE, width=1)
        d.line([a, b], fill=INK, width=max(2, int(2 * k)))
        for q in (a, b):
            d.line([(q[0], q[1] - 9 * k), (q[0], q[1] + 9 * k)], fill=INK, width=max(2, int(2 * k)))
        tw = d.textlength(text, font=f)
        d.text((a[0] + (b[0] - a[0]) * tpos - tw / 2, y - 40 * k if side > 0 else y + 8 * k), text, font=f, fill=INK)
    else:
        x = (p0[0] if off == 0 else off)
        a, b = (x, p0[1]), (x, p1[1])
        d.line([p0, a], fill=LINE, width=1)
        d.line([p1, b], fill=LINE, width=1)
        d.line([a, b], fill=INK, width=max(2, int(2 * k)))
        for q in (a, b):
            d.line([(q[0] - 9 * k, q[1]), (q[0] + 9 * k, q[1])], fill=INK, width=max(2, int(2 * k)))
        tw = d.textlength(text, font=f)
        d.text((x + 14 * k if side > 0 else x - 14 * k - tw, (a[1] + b[1]) / 2 - 18 * k), text, font=f, fill=INK)


def dashed(d, p0, p1, fill, width=2, dash=14):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = int(L // dash)
    for i in range(0, n, 2):
        a = (p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n)
        b = (p0[0] + (p1[0] - p0[0]) * (i + 1) / n, p0[1] + (p1[1] - p0[1]) * (i + 1) / n)
        d.line([a, b], fill=fill, width=width)


def ortho(name, im, data, view):
    W, H = im.size
    k = W / 1500.0
    pad = int(360 * k)
    canvas = Image.new("RGB", (W + 2 * pad, H), BG)
    canvas.paste(flatten(im), (pad, 0))
    d = ImageDraw.Draw(canvas)
    f, fs = font(int(30 * k)), font(int(25 * k))
    P = {i["label"]: (i["x"] + pad, i["y"]) for i in data["items"]}
    ppm = abs(P["stick_top"][1] - P["hub_top"][1]) / 90.0 if view != "top" else None      # pixels per mm
    if view == "top":
        ppm = abs(P["unit_hi"][0] - P["unit_lo"][0]) / 89.2
    mm = lambda px: abs(px) / ppm
    ulo, uhi, alo, ahi = P["unit_lo"], P["unit_hi"], P["all_lo"], P["all_hi"]
    xs = sorted((ulo[0], uhi[0]))
    ys = sorted((ulo[1], uhi[1]))
    axs = sorted((alo[0], ahi[0]))
    ays = sorted((alo[1], ahi[1]))
    if view in ("front", "side"):
        y0, yt = P["origin"][1], P["table"][1]
        dashed(d, (pad * 0.25, y0), (W + pad * 1.75, y0), ACCENT, width=max(2, int(2 * k)))
        d.text((pad * 0.25, y0 - 36 * k), "page surface", font=fs, fill=ACCENT)
        d.line([(pad * 0.25, yt), (W + pad * 1.75, yt)], fill=LINE, width=max(2, int(2 * k)))
        d.text((pad * 0.25, yt + 6 * k), "table", font=fs, fill=LINE)
        dim(d, (xs[0], ys[0]), (xs[1], ys[0]), f"{mm(xs[1] - xs[0]):.0f} mm", f, off=ys[0] - 50 * k, k=k)
        dim(d, (axs[1], ays[0]), (axs[1], yt), f"{mm(yt - ays[0]):.0f} mm over the table", f, off=max(axs[1], xs[1]) + 70 * k,
            horizontal=False, k=k)
        lens = P["lens"]
        dim(d, lens, (lens[0], y0), f"lens {mm(y0 - lens[1]):.0f} mm above the page", f, off=min(axs[0], xs[0]) - 60 * k,
            horizontal=False, k=k, side=-1)
    if view == "front":
        d.text((pad * 0.25, 40 * k), "Front (reader's view)", font=font(int(34 * k), True), fill=INK)
    if view == "side":
        d.text((pad * 0.25, 40 * k), "Side (reader on the right)", font=font(int(34 * k), True), fill=INK)
        ox = P["origin"][0]
        dashed(d, (ox, ays[0] - 40 * k), (ox, yt + 20 * k), ACCENT, width=max(2, int(2 * k)))
        d.text((ox + 10 * k, ays[0] - 44 * k), "top edge of the book", font=fs, fill=ACCENT)
        yb = yt + 70 * k
        dim(d, (P["pad_lo"][0], yt), (P["blade_hi"][0], yt), f"{mm(P['blade_hi'][0] - P['pad_lo'][0]):.0f} mm from rear pad to blade tips",
            f, off=yb, k=k, side=-1)
    if view == "top":
        d.text((pad * 0.25, 40 * k), "Top (reader at the bottom)", font=font(int(34 * k), True), fill=INK)
        dim(d, (xs[0], ys[1]), (xs[1], ys[1]), f"{mm(xs[1] - xs[0]):.0f} mm", f, off=ys[1] + 46 * k, k=k, side=-1, tpos=0.2)
        blo, bhi = P["blade_lo"], P["blade_hi"]
        bx = sorted((blo[0], bhi[0]))
        btop = max(blo[1], bhi[1]) if P["pad_lo"][1] < P["unit_lo"][1] else min(blo[1], bhi[1])     # the blade-tip end
        up = btop < ys[0]
        dim(d, (bx[0], btop), (bx[1], btop), f"{mm(bx[1] - bx[0]):.0f} mm across the blade tips", f,
            off=btop + (-46 * k if up else 46 * k), k=k, side=1 if up else -1)
        dim(d, (axs[1], ays[0]), (axs[1], ays[1]), f"{mm(ays[1] - ays[0]):.0f} mm from rear pad to blade tips", f,
            off=max(axs[1], bx[1]) + 60 * k, horizontal=False, k=k)
    canvas.save(os.path.join(RENDERS, name + ".png"), optimize=True)


def main():
    os.makedirs(RAW, exist_ok=True)
    for a in glob.glob(os.path.join(RENDERS, "*.anchors.json")):       # stash raw renders that have label data
        n = os.path.basename(a)[:-len(".anchors.json")]
        shutil.move(a, os.path.join(RAW, n + ".anchors.json"))
        if os.path.exists(os.path.join(RENDERS, n + ".png")):
            shutil.move(os.path.join(RENDERS, n + ".png"), os.path.join(RAW, n + ".png"))
    for a in sorted(glob.glob(os.path.join(RAW, "*.anchors.json"))):
        n = os.path.basename(a)[:-len(".anchors.json")]
        im = Image.open(os.path.join(RAW, n + ".png"))
        data = json.load(open(a))
        if n.startswith("02_"):
            ortho(n, im, data, "front")
        elif n.startswith("03_"):
            ortho(n, im, data, "side")
        elif n.startswith("04_"):
            ortho(n, im, data, "top")
        elif n.startswith("14_"):
            flatten(im).save(os.path.join(RENDERS, n + ".jpg"), quality=90)
        else:
            labelled(n, im, data)
        print("finished", n)
    for p in glob.glob(os.path.join(RENDERS, "*.png")):                # photographic scenes -> JPEG
        n = os.path.splitext(os.path.basename(p))[0]
        if os.path.exists(os.path.join(RAW, n + ".anchors.json")):
            continue
        Image.open(p).convert("RGB").save(os.path.join(RENDERS, n + ".jpg"), quality=90)
        os.remove(p)
        print("jpeg", n)


if __name__ == "__main__":
    main()
