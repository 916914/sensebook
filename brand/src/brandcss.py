"""Shared CSS for every SenseBook document and page: fonts, colour tokens, base type. Apache-2.0."""
import os
import brandkit as bk

FACES = [  # (family, file, weight, style)
    ("Literata", "literata-latin-400-normal.woff2", 400, "normal"),
    ("Literata", "literata-latin-400-italic.woff2", 400, "italic"),
    ("Literata", "literata-latin-600-normal.woff2", 600, "normal"),
    ("Literata", "literata-latin-700-normal.woff2", 700, "normal"),
    ("Atkinson Hyperlegible Next", "atkinson-hyperlegible-next-latin-400-normal.woff2", 400, "normal"),
    ("Atkinson Hyperlegible Next", "atkinson-hyperlegible-next-latin-600-normal.woff2", 600, "normal"),
    ("Atkinson Hyperlegible Next", "atkinson-hyperlegible-next-latin-700-normal.woff2", 700, "normal"),
    ("Noto Sans Bengali", "noto-sans-bengali-bengali-400-normal.woff2", 400, "normal"),
    ("Noto Sans Bengali", "noto-sans-bengali-bengali-600-normal.woff2", 600, "normal"),
    ("Noto Sans Bengali", "noto-sans-bengali-bengali-700-normal.woff2", 700, "normal"),
    ("Noto Serif Bengali", "noto-serif-bengali-bengali-600-normal.woff2", 600, "normal"),
    ("Noto Serif Bengali", "noto-serif-bengali-bengali-700-normal.woff2", 700, "normal"),
]

SANS = '"Atkinson Hyperlegible Next","Noto Sans Bengali","Nirmala UI",system-ui,sans-serif'
SERIF = 'Literata,"Noto Serif Bengali","Noto Sans Bengali",Georgia,serif'


def font_faces(base):
    """@font-face rules. `base` is a URL prefix ending in '/': a file:/// URL for PDFs, '/fonts/' for the site."""
    return "".join(f'@font-face{{font-family:"{fam}";src:url("{base}{f}") format("woff2");font-weight:{wt};font-style:{st};font-display:swap}}'
                   for fam, f, wt, st in FACES)


def file_base():
    return "file:///" + bk.FONTS.replace("\\", "/") + "/"


def tokens():
    return ":root{" + "".join(f"--{t}:{h};" for t, _, _, h, _ in bk.PALETTE) + "}"
