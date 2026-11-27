"""Draw the three logo options side by side for the owner to choose. Output: brand/logo/options/. Apache-2.0."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brandkit as bk
import render

OUT = os.path.join(bk.BRAND, "logo", "options")
os.makedirs(OUT, exist_ok=True)
C = bk.C
LABELS = {"book": ("A", "Open book", "An open book with a dot sitting at the top of the spine: exactly where SenseBook sits. The dot is the marigold Ask button, the voice."),
          "matra": ("B", "Matra", "The headline stroke that Bangla letters hang from (মাত্রা), dipping at the spine, with the dot above. Bangla-rooted, more abstract."),
          "device": ("C", "Device face", "The unit itself: four status dots and the lens. Literal; the dots vanish at small sizes.")}


def mark_svg(kind, fg, dot, px):
    return bk.svg(bk.MARKS[kind](fg, dot), px, px, vb="0 0 64 64")


def lock_svg(kind, fg, dot, word, size, name=bk.NAME, font=bk.WORDMARK_FONT, bn=False):
    inner, w, h = bk.lockup(kind, fg, dot, word, name=name, font=font, size=size, bn=bn)
    return bk.svg(inner, round(w + 2), round(h), vb=f"0 0 {w + 2:.1f} {h:.1f}")


def main():
    rows = []
    for kind, (letter, title, why) in LABELS.items():
        for name, fg, dot in (("colour", C["spine"], C["marigold"]), ("one-colour", C["ink"], C["ink"])):
            with open(os.path.join(OUT, f"option_{letter}_{kind}_{name}.svg"), "w", encoding="utf-8") as f:
                f.write(lock_svg(kind, fg, dot, fg, 64))
        small = "".join(f'<div class="sz">{mark_svg(kind, C["spine"], C["marigold"], px)}<span>{px}px</span></div>' for px in (96, 48, 32, 16))
        rows.append(f"""
<section class="opt"><div class="head"><b>{letter}</b><div><h2>{title}</h2><p>{why}</p></div></div>
<div class="tiles">
 <div class="tile paper">{lock_svg(kind, C["spine"], C["marigold"], C["spine"], 54)}</div>
 <div class="tile dark">{lock_svg(kind, bk.C["paper"], C["marigold"], bk.C["paper"], 54)}</div>
 <div class="tile paper">{lock_svg(kind, C["ink"], C["ink"], C["ink"], 54)}</div>
 <div class="tile paper sizes">{small}</div>
</div></section>""")
    fonts = "".join(f'<div class="tile paper wm">{lock_svg("book", C["spine"], C["marigold"], C["spine"], 50, name=n, font=f, bn=b)}<span>{lab}</span></div>'
                    for n, f, b, lab in ((bk.NAME, "literata-600", False, "Literata SemiBold (recommended)"),
                                         (bk.NAME, "atkinson-700", False, "Atkinson Hyperlegible Next Bold"),
                                         (bk.NAME_BN, "notoserif-bn-700", True, "Noto Serif Bengali Bold"),
                                         (bk.NAME_BN, "notosans-bn-700", True, "Noto Sans Bengali Bold")))
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#ECE6DA;font:15px/1.45 "Segoe UI",sans-serif;color:{C['ink']};padding:28px 32px;width:1536px;box-sizing:border-box}}
h1{{font-size:24px;margin:0 0 4px;color:{C['spine']}}} .sub{{margin:0 0 18px;color:#4b5557}}
.opt{{margin:0 0 18px}} .head{{display:flex;gap:14px;align-items:flex-start;margin-bottom:8px}}
.head b{{font-size:22px;background:{C['spine']};color:{C['paper']};width:36px;height:36px;border-radius:50%;display:grid;place-items:center;flex:none}}
.head h2{{margin:0;font-size:18px}} .head p{{margin:2px 0 0;color:#4b5557;max-width:900px}}
.tiles{{display:grid;grid-template-columns:1.25fr 1.25fr 1.25fr 1fr;gap:10px}}
.tile{{border-radius:10px;height:130px;display:flex;align-items:center;justify-content:center;gap:14px}}
.paper{{background:{C['paper']}}} .dark{{background:{C['spine']}}}
.sizes .sz{{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:11px;color:#6b7476}}
.wmrow{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}} .wm{{flex-direction:column;height:150px}} .wm span{{font-size:12px;color:#6b7476}}
</style></head><body><h1>SenseBook logo options</h1><p class="sub">Each option on paper, on Spine (the device colour), in one colour, and at small sizes. Wordmark: Literata SemiBold, outlined.</p>
{''.join(rows)}<h2 style="font-size:18px;margin:20px 0 8px">Wordmark type, with option A</h2><div class="wmrow">{fonts}</div></body></html>"""
    html_path = os.path.join(OUT, "logo_options.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)
    render.png(html_path, os.path.join(OUT, "logo_options.png"), 1536, 1010)
    names_board()
    palette_board()
    print("wrote", OUT)


def names_board():
    """The name question, drawn: the recommended mark with each candidate name in English and Bangla."""
    cands = [("SenseBook", "সেন্সবুক", "Keep (recommended for now)", "No live identical mark found; Bangladesh search still needed. Near-identical SENSEEBOOK (braille books, Korea) is live in the US."),
             ("Kothaboi", "কথাবই", "Alternative 1: 'talking book'", "The headline বই এখন কথা বলে in one word. No clash found; .com, .app, .io, .com.bd free."),
             ("Pathsathi", "পাঠসাথী", "Alternative 2: 'study companion'", "Says the tutor role. No clash found; .com, .app, .io, .com.bd free.")]
    cards = ""
    for en, bn, lab, note in cands:
        cards += (f'<div class="card"><div class="lab">{lab}</div><div class="lk">{lock_svg("book", C["spine"], C["marigold"], C["spine"], 46, name=en)}</div>'
                  f'<div class="lk">{lock_svg("book", C["spine"], C["marigold"], C["spine"], 42, name=bn, font=bk.WORDMARK_FONT_BN, bn=True)}</div><p>{note}</p></div>')
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#ECE6DA;font:15px/1.45 "Segoe UI",sans-serif;color:{C['ink']};padding:28px 32px;width:1536px;box-sizing:border-box}}
h1{{font-size:24px;margin:0 0 16px;color:{C['spine']}}} .row{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.card{{background:{C['paper']};border-radius:12px;padding:20px 22px}} .lab{{font-weight:700;color:{C['teal']};margin-bottom:12px}}
.lk{{height:84px;display:flex;align-items:center}} p{{color:#4b5557;margin:10px 0 0;font-size:14px}}
</style></head><body><h1>The name question: how each name looks in the brand</h1><div class="row">{cards}</div></body></html>"""
    p = os.path.join(OUT, "name_options.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(page)
    render.png(p, os.path.join(OUT, "name_options.png"), 1536, 420)


def palette_board():
    sw = ""
    for tok, name, bn, hx, role in bk.PALETTE:
        dark = bk.luminance(hx) < 0.25
        fg = bk.C["paper"] if dark else bk.C["ink"]
        sw += (f'<div class="sw" style="background:{hx};color:{fg}"><b>{name}</b> <span class="bn">{bn}</span><br><code>{hx}</code>'
               f'<small>{role}</small></div>')
    pairs = [("ink", "paper"), ("spine", "paper"), ("teal", "paper"), ("paper", "spine"), ("marigold", "spine"), ("marigold", "ink"),
             ("spine", "marigold"), ("ink", "mist"), ("brick", "paper"), ("leaf", "paper"), ("marigold", "paper")]
    rows = ""
    for f_, b_ in pairs:
        r = bk.contrast(bk.C[f_], bk.C[b_])
        g = bk.grade(r)
        rows += (f'<div class="pair" style="background:{bk.C[b_]};color:{bk.C[f_]}"><span class="aa">Aa অআ</span>'
                 f'<span class="meta">{f_} on {b_}<br><b>{r:.1f}:1 · {g}</b></span></div>')
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#ECE6DA;font:15px/1.4 "Segoe UI","Nirmala UI",sans-serif;color:{C['ink']};padding:28px 32px;width:1536px;box-sizing:border-box}}
h1{{font-size:24px;margin:0 0 14px;color:{C['spine']}}} h2{{font-size:17px;margin:18px 0 8px}}
.sws{{display:grid;grid-template-columns:repeat(8,1fr);gap:8px}} .sw{{border-radius:10px;padding:14px;height:190px;box-sizing:border-box;display:flex;flex-direction:column;gap:2px}}
.sw small{{margin-top:auto;font-size:12px;opacity:.9}} .bn{{font-weight:400}} code{{font-size:13px}}
.pairs{{display:grid;grid-template-columns:repeat(6,1fr);gap:8px}} .pair{{border-radius:10px;padding:12px 14px;display:flex;flex-direction:column;gap:6px;border:1px solid #0001}}
.aa{{font-size:30px;font-weight:700;line-height:1}} .meta{{font-size:12.5px}}
</style></head><body><h1>Colour palette with measured contrast (WCAG 2.2)</h1><div class="sws">{sw}</div>
<h2>Text pairs: AAA ≥ 7:1, AA ≥ 4.5:1. Marigold on paper fails, so marigold is never text on a light background.</h2><div class="pairs">{rows}</div></body></html>"""
    p = os.path.join(OUT, "palette.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(page)
    render.png(p, os.path.join(OUT, "palette.png"), 1536, 540)


if __name__ == "__main__":
    main()
