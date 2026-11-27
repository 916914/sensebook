"""Page textures for the render scenes (plain textbook-style pages, our own text; no real book is copied).

Run:  ..\\.venv\\Scripts\\python.exe make_textures.py   -> design/cad/build/tex/*.png
"""
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "build", "tex")
os.makedirs(TEX, exist_ok=True)
FONTS = r"C:\Windows\Fonts"


def font(name, size):
    for n in (name, "georgia.ttf", "times.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(os.path.join(FONTS, n), size)
        except OSError:
            continue
    return ImageFont.load_default()


PARAS = [
    "Light travels in straight lines until it meets a surface. When it passes from air into glass it slows down, "
    "and its path bends toward the normal. This bending is called refraction.",
    "A convex lens is thicker in the middle than at the edges. Rays that arrive parallel to the principal axis "
    "are bent inward and meet at a single point, the principal focus. The distance from the centre of the lens "
    "to this point is the focal length.",
    "Hold a convex lens between a window and a sheet of paper. Move the paper slowly until a sharp, upside-down "
    "picture of the window appears. Measure the distance from the lens to the paper: this is close to the focal "
    "length of the lens.",
    "The image formed by a lens depends on where the object stands. Far beyond the focus the image is small, real "
    "and inverted. As the object comes closer, the image grows and moves away from the lens.",
    "When the object is nearer than the focus, no real image is formed. Looking through the lens we see an "
    "enlarged, upright image on the same side as the object. A magnifying glass is used in exactly this way.",
    "A camera uses a convex lens to form a small real image on a sensor. The eye works in a similar way: the "
    "lens of the eye changes its shape, so that near and distant things can both be seen clearly.",
    "Work in pairs. Draw the path of three rays from the top of a candle through a convex lens, and mark where "
    "they meet. Compare your drawing with the picture you found on the paper.",
]
QUESTIONS = [
    "1.  What happens to a ray of light when it enters glass from air?",
    "2.  Define the focal length of a convex lens.",
    "3.  Where must an object be placed so that a lens acts as a magnifier?",
    "4.  Explain why the image on the paper is upside down.",
]


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def ray_diagram(d, x, y, w, h, ink):
    cx, cy = x + w * 0.5, y + h * 0.5
    d.line([(x, cy), (x + w, cy)], fill=ink, width=2)
    d.ellipse([cx - w * 0.035, cy - h * 0.42, cx + w * 0.035, cy + h * 0.42], outline=ink, width=3)
    ox = x + w * 0.14
    d.line([(ox, cy), (ox, cy - h * 0.3)], fill=ink, width=4)
    d.polygon([(ox, cy - h * 0.36), (ox - 8, cy - h * 0.28), (ox + 8, cy - h * 0.28)], fill=ink)
    fx = cx + w * 0.17
    ix = x + w * 0.84
    iy = cy + h * 0.27
    for (ya, yb) in ((cy - h * 0.3, cy - h * 0.3), (cy - h * 0.3, cy)):
        pass
    d.line([(ox, cy - h * 0.3), (cx, cy - h * 0.3), (ix, iy)], fill=ink, width=2)
    d.line([(ox, cy - h * 0.3), (ix, iy)], fill=ink, width=2)
    d.line([(ix, cy), (ix, iy)], fill=ink, width=4)
    for px in (fx, cx - w * 0.17):
        d.ellipse([px - 5, cy - 5, px + 5, cy + 5], fill=ink)
    f = font("georgiai.ttf", 26)
    d.text((fx - 6, cy + 12), "F", font=f, fill=ink)
    d.text((cx - w * 0.17 - 6, cy + 12), "F", font=f, fill=ink)


def page(path, number, heading, paras, left, figure=False, questions=False, size=(1480, 1960), seed=0):
    W, H = size
    paper = (243, 238, 226)
    img = Image.new("RGB", size, paper)
    d = ImageDraw.Draw(img)
    ink, soft = (38, 36, 34), (92, 88, 84)
    m_in, m_out, top = 150, 120, 150
    x0 = m_out if left else m_in
    tw = W - m_in - m_out
    d.text((x0, 78), "Chapter 9   Light and lenses" if left else "General Science", font=font("georgiai.ttf", 26), fill=soft)
    d.line([(x0, 118), (x0 + tw, 118)], fill=soft, width=2)
    y = top
    if heading:
        d.text((x0, y), heading, font=font("georgiab.ttf", 50), fill=ink)
        y += 92
    body = font("georgia.ttf", 33)
    for i, p in enumerate(paras):
        if figure and i == 2:
            fh = 330
            d.rectangle([x0, y + 8, x0 + tw, y + fh], outline=soft, width=2)
            ray_diagram(d, x0 + 30, y + 24, tw - 60, fh - 60, ink)
            d.text((x0, y + fh + 12), "Figure 9.4   A convex lens forms a real, inverted image.", font=font("georgiai.ttf", 27), fill=soft)
            y += fh + 72
        for ln in wrap(d, p, body, tw):
            d.text((x0, y), ln, font=body, fill=ink)
            y += 47
        y += 26
        if y > H - 420:
            break
    if questions:
        y += 10
        d.text((x0, y), "Check your understanding", font=font("georgiab.ttf", 36), fill=ink)
        y += 64
        for q in QUESTIONS:
            for ln in wrap(d, q, body, tw):
                d.text((x0, y), ln, font=body, fill=ink)
                y += 47
            y += 12
    num = str(number)
    nf = font("georgia.ttf", 30)
    d.text((x0 if left else x0 + tw - d.textlength(num, font=nf), H - 110), num, font=nf, fill=soft)
    # faint paper tone variation toward the gutter
    shade = Image.new("L", size, 0)
    sd = ImageDraw.Draw(shade)
    for k in range(120):
        xg = (W - 1 - k) if left else k
        sd.line([(xg, 0), (xg, H)], fill=int(46 * (1 - k / 120) ** 2))
    img = Image.composite(Image.new("RGB", size, (150, 140, 125)), img, shade)
    img.save(path)


def main():
    random.seed(4)
    page(os.path.join(TEX, "page_left.png"), 142, "9.3  Convex lenses", PARAS[:5], True, figure=True)
    page(os.path.join(TEX, "page_right.png"), 143, None, PARAS[3:7], False, questions=True)
    page(os.path.join(TEX, "pb_left.png"), 26, "Refraction", PARAS[:4], True, size=(1160, 1640))
    page(os.path.join(TEX, "pb_right.png"), 27, None, PARAS[4:7] + PARAS[:1], False, questions=False, size=(1160, 1640))
    page(os.path.join(TEX, "sheet.png"), 1, "Notice", PARAS[1:5], False, size=(1480, 2090))
    print("textures ->", TEX)


if __name__ == "__main__":
    main()
