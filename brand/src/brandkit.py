"""Shared SenseBook brand definitions: colours, fonts, the mark geometry and text-to-outline helpers.

Used by make_logos.py, make_guide.py and tools/build_site.py. Needs: fontTools, brotli, uharfbuzz.
Licence: Apache-2.0 (code). The brand assets it produces are CC BY 4.0.
"""
import io, os
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
FONTS = os.path.join(BRAND, "type", "fonts")

# ---- colour -------------------------------------------------------------------------------
# Rooted in the product: the slate-teal unit, the marigold Ask button, white status dots, paper.
PALETTE = [  # (token, name, Bangla name, hex, role)
    ("spine", "Spine", "মলাট", "#133B42", "Primary. The device colour. Text, logo, dark backgrounds."),
    ("teal", "Teal", "নদী", "#1F5560", "Secondary. Links, headings on paper, secondary fills."),
    ("mist", "Mist", "কুয়াশা", "#DCE9E8", "Light tint. Panels and cards on paper."),
    ("marigold", "Marigold", "গাঁদা", "#E8A317", "Accent. The Ask button and the dot. Fill or on dark only, never text on light."),
    ("paper", "Paper", "কাগজ", "#F7F2E8", "Background. Warm, like a printed page."),
    ("ink", "Ink", "কালি", "#161B1C", "Body text and one-colour print."),
    ("brick", "Brick", "ইট", "#A63D2A", "Errors and warnings only."),
    ("leaf", "Leaf", "পাতা", "#2E6B4A", "Success and 'ready' only."),
]
C = {t: h for t, _, _, h, _ in PALETTE}
WHITE = "#FFFFFF"


def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexcol):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def grade(ratio):
    return "AAA" if ratio >= 7 else "AA" if ratio >= 4.5 else "AA large" if ratio >= 3 else "fail"


# ---- fonts --------------------------------------------------------------------------------
FONT_FILES = {
    "literata-600": "literata-latin-600-normal.woff2",
    "literata-700": "literata-latin-700-normal.woff2",
    "literata-400": "literata-latin-400-normal.woff2",
    "atkinson-700": "atkinson-hyperlegible-next-latin-700-normal.woff2",
    "atkinson-400": "atkinson-hyperlegible-next-latin-400-normal.woff2",
    "notosans-bn-700": "noto-sans-bengali-bengali-700-normal.woff2",
    "notoserif-bn-700": "noto-serif-bengali-bengali-700-normal.woff2",
    "notoserif-bn-600": "noto-serif-bengali-bengali-600-normal.woff2",
}


@lru_cache(None)
def _font(key):
    from fontTools.ttLib import TTFont
    import uharfbuzz as hb
    tt = TTFont(os.path.join(FONTS, FONT_FILES[key]))
    tt.flavor = None
    buf = io.BytesIO()
    tt.save(buf)
    data = buf.getvalue()
    tt = TTFont(io.BytesIO(data))
    face = hb.Face(data)
    return tt, hb.Font(face), tt["head"].unitsPerEm


def text_outline(text, key, size, tracking=0.0, x=0.0, baseline=0.0):
    """Shape `text` with HarfBuzz and return (svg path d, advance width, cap height) at `size` px."""
    import uharfbuzz as hb
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    tt, font, upem = _font(key)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    scale = size / upem
    pen = SVGPathPen(gs)
    pen_x = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        tx = x + (pen_x + pos.x_offset) * scale
        ty = baseline - pos.y_offset * scale
        gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, tx, ty)))
        pen_x += pos.x_advance + tracking * upem
    os2 = tt["OS/2"]
    cap = getattr(os2, "sCapHeight", 0) or upem * 0.7
    return pen.getCommands(), (pen_x - tracking * upem) * scale, cap * scale


# ---- the mark -----------------------------------------------------------------------------
# All marks are drawn on a 64 x 64 grid. Each function returns SVG elements (no <svg> wrapper).
def mark_book(fg, dot):
    """Option A, 'Open book': an open book with a dot sitting at the top of the spine."""
    return (f'<path fill="{fg}" d="M29 52V30.2C23 25.6 14 24.6 5 26.6v22c9-2 18-1 24 3.4z"/>'
            f'<path fill="{fg}" d="M35 52V30.2c6-4.6 15-5.6 24-3.6v22c-9-2-18-1-24 3.4z"/>'
            f'<circle fill="{dot}" cx="32" cy="17" r="6.6"/>')


def mark_matra(fg, dot):
    """Option B, 'Matra': the headline stroke of Bangla script dipping at the spine, with the dot above."""
    return (f'<path fill="none" stroke="{fg}" stroke-width="6.4" stroke-linecap="round" stroke-linejoin="round" '
            f'd="M6 33H25l7 8 7-8h19"/><circle fill="{dot}" cx="32" cy="19" r="6.6"/>')


def mark_device(fg, dot):
    """Option C, 'Device face': the unit seen from the front, four status dots and the lens."""
    return (f'<rect x="4" y="15" width="56" height="34" rx="11" fill="{fg}"/>'
            + "".join(f'<circle cx="{x}" cy="24.5" r="2.1" fill="#fff"/>' for x in (13, 19.5, 26, 32.5))
            + f'<circle cx="32" cy="38.5" r="6.2" fill="none" stroke="{dot}" stroke-width="3"/>')


MARKS = {"book": mark_book, "matra": mark_matra, "device": mark_device}
MARK = "book"  # the chosen mark; change here and re-run make_logos.py


def svg(inner, w, h, title="SenseBook", vb=None):
    vb = vb or f"0 0 {w:g} {h:g}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" viewBox="{vb}" role="img" '
            f'aria-label="{title}"><title>{title}</title>{inner}</svg>')


NAME = "SenseBook"
NAME_BN = "সেন্সবুক"
WORDMARK_FONT = "literata-600"
WORDMARK_FONT_BN = "notoserif-bn-700"


# Visible extent of each mark on its 64 grid: (x0, y0, x1, y1). The bottom edge sits on the text baseline.
MARK_BOX = {"book": (5, 10.4, 59, 52), "matra": (2.8, 12.4, 61.2, 44.4), "device": (4, 15, 60, 49)}


def place_mark(kind, fg, dot, height, x=0.0, bottom=0.0):
    """Mark scaled so its visible height is `height`, left edge at x, bottom edge at `bottom`. Returns (svg, width)."""
    x0, y0, x1, y1 = MARK_BOX[kind]
    s = height / (y1 - y0)
    return (f'<g transform="translate({x - x0 * s:.2f},{bottom - y1 * s:.2f}) scale({s:.4f})">{MARKS[kind](fg, dot)}</g>',
            (x1 - x0) * s)


def lockup(mark="book", fg=None, dot=None, word=None, name=NAME, font=WORDMARK_FONT, size=64, bn=False):
    """Horizontal lockup: mark, then wordmark on the same baseline. Returns (inner svg, width, height)."""
    fg = fg or C["spine"]
    dot = dot or C["marigold"]
    word = word or fg
    d, adv, cap = text_outline(name, font, size)
    if bn:
        cap = size * 0.62  # Bangla: align to the headline (matra) rather than Latin cap height
    mh = cap * 1.42
    pad = size * 0.06
    base = pad + mh
    h = base + size * (0.32 if bn else 0.24)
    mk, mw = place_mark(mark, fg, dot, mh, x=0, bottom=base)
    gap = size * 0.36
    inner = mk + f'<path fill="{word}" transform="translate({mw + gap:.2f},{base:.2f})" d="{d}"/>'
    return inner, mw + gap + adv, h
