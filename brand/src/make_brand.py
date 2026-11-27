"""Build the SenseBook brand assets: logo files, colour tokens, icons, illustration, packaging and tactile
drawings, and the audio identity. Run:  python brand/src/make_brand.py
Code: Apache-2.0. Outputs: CC BY 4.0.
"""
import json, math, os, struct, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brandkit as bk

B = bk.BRAND
C = bk.C


def w(rel, text):
    p = os.path.join(B, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return p


# ---------------------------------------------------------------------------------------- logo
def logos():
    k = bk.MARK
    x0, y0, x1, y1 = bk.MARK_BOX[k]
    vb = f"{x0 - 2} {y0 - 2} {x1 - x0 + 4} {y1 - y0 + 4}"
    variants = {
        "colour": (C["spine"], C["marigold"]),
        "one-colour-ink": (C["ink"], C["ink"]),
        "one-colour-spine": (C["spine"], C["spine"]),
        "reversed": (C["paper"], C["marigold"]),
        "reversed-white": (bk.WHITE, bk.WHITE),
    }
    for name, (fg, dot) in variants.items():
        w(f"logo/sensebook-mark-{name}.svg", bk.svg(bk.MARKS[k](fg, dot), 128, 128 * (y1 - y0 + 4) / (x1 - x0 + 4), vb=vb))
        for lang, nm, font, bn in (("en", bk.NAME, bk.WORDMARK_FONT, False), ("bn", bk.NAME_BN, bk.WORDMARK_FONT_BN, True)):
            inner, wd, ht = bk.lockup(k, fg, dot, fg, name=nm, font=font, size=64, bn=bn)
            w(f"logo/sensebook-lockup-{lang}-{name}.svg", bk.svg(inner, round(wd + 4), round(ht), vb=f"-2 0 {wd + 4:.1f} {ht:.1f}"))
    # bilingual stacked lockup: mark above, English then Bangla
    d_en, a_en, cap = bk.text_outline(bk.NAME, bk.WORDMARK_FONT, 64)
    d_bn, a_bn, _ = bk.text_outline(bk.NAME_BN, bk.WORDMARK_FONT_BN, 54)
    width = max(a_en, a_bn) + 20
    mk, mw = bk.place_mark(k, C["spine"], C["marigold"], 84, x=(width - 84 * (x1 - x0) / (y1 - y0)) / 2, bottom=94)
    inner = (mk + f'<path fill="{C["spine"]}" transform="translate({(width - a_en) / 2:.1f},176)" d="{d_en}"/>'
             f'<path fill="{C["spine"]}" transform="translate({(width - a_bn) / 2:.1f},258)" d="{d_bn}"/>')
    w("logo/sensebook-stacked-bilingual-colour.svg", bk.svg(inner, round(width), 286, vb=f"0 0 {width:.1f} 286"))
    # favicon / app icon: mark on a Spine rounded square
    icon = (f'<rect width="64" height="64" rx="14" fill="{C["spine"]}"/>'
            f'<g transform="translate(9.6 8) scale(0.7)">{bk.MARKS[k](C["paper"], C["marigold"])}</g>')
    w("logo/sensebook-app-icon.svg", bk.svg(icon, 64, 64))
    w("logo/favicon.svg", bk.svg(icon, 32, 32, vb="0 0 64 64"))


# ---------------------------------------------------------------------------------------- colour
def colour():
    rows = [{"token": t, "name": n, "name_bn": bn, "hex": h, "role": r,
             "rgb": [int(h[i:i + 2], 16) for i in (1, 3, 5)]} for t, n, bn, h, r in bk.PALETTE]
    pairs = []
    for f, b in [("ink", "paper"), ("spine", "paper"), ("teal", "paper"), ("paper", "spine"), ("marigold", "spine"),
                 ("marigold", "ink"), ("ink", "marigold"), ("ink", "mist"), ("brick", "paper"), ("leaf", "paper"), ("marigold", "paper")]:
        r = bk.contrast(C[f], C[b])
        pairs.append({"text": f, "background": b, "ratio": round(r, 2), "wcag": bk.grade(r)})
    w("colour/palette.json", json.dumps({"palette": rows, "contrast": pairs}, ensure_ascii=False, indent=2))
    css = ":root{\n" + "".join(f"  --sb-{t}:{h};\n" for t, _, _, h, _ in bk.PALETTE) + "}\n"
    w("colour/palette.css", "/* SenseBook colour tokens. CC BY 4.0 */\n" + css)


# ---------------------------------------------------------------------------------------- icons
ICONS = {  # 24 x 24, 2 px stroke, round caps and joins. Marigold is used only for the 'voice' dot.
    "read": '<path d="M12 8.5C9.5 6.8 6.5 6.4 3.5 7.2v11c3-.8 6-.4 8.5 1.3 2.5-1.7 5.5-2.1 8.5-1.3v-11c-3-.8-6-.4-8.5 1.3zM12 8.5v11"/><path d="M9.6 3.6a3.4 3.4 0 0 1 4.8 0"/>',
    "ask": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3" class="dot"/>',
    "explain": '<path d="M4 5.5h16v10.5H10l-4.5 3.5V16H4z"/><path d="M8.5 10.8h.01M12 10.8h.01M15.5 10.8h.01"/>',
    "quiz": '<rect x="3.5" y="3.5" width="17" height="17" rx="4"/><path d="M8 12.4l2.8 2.8L16.2 9"/>',
    "remind": '<path d="M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    "headphones": '<path d="M4 16v-3.5a8 8 0 0 1 16 0V16"/><path d="M4 15.5h3.5v5H5.2A1.2 1.2 0 0 1 4 19.3zM20 15.5h-3.5v5h2.3a1.2 1.2 0 0 0 1.2-1.2z"/>',
    "offline": '<path d="M12 3.5v9M8.5 9l3.5 3.5L15.5 9"/><path d="M4.5 14.5v4a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-4"/>',
    "page-turn": '<path d="M5 4.5h8v15H5z"/><path d="M13 4.5c3.5 0 6 2.5 6 7.5"/><path d="M16.8 10.2 19 12.4l2.2-2.2"/>',
    "tri-grip": '<rect x="7.5" y="2.5" width="9" height="4.5" rx="1.8"/><path d="M12 7v4.5M12 11.5 6 21M12 11.5l6 9.5M12 11.5V21"/>',
    "touch": '<circle cx="12" cy="9" r="2.6" class="dot"/><path d="M6.5 9a5.5 5.5 0 0 1 11 0"/><path d="M4 21c1.5-3.5 4.5-5.5 8-5.5s6.5 2 8 5.5"/>',
    "mic-off": '<rect x="9" y="3" width="6" height="10.5" rx="3"/><path d="M6 11a6 6 0 0 0 12 0M12 17v3.5M4 4l16 16"/>',
    "light": '<circle cx="12" cy="12" r="3.5"/><circle cx="12" cy="12" r="7.5"/>',
    "battery": '<rect x="2.5" y="7.5" width="17" height="9" rx="2.2"/><path d="M22 11v2M6 10.5v3M9.5 10.5v3"/>',
    "shared": '<circle cx="8" cy="8" r="3"/><circle cx="16.5" cy="8" r="3"/><path d="M2.5 20c.5-3.5 2.8-5.5 5.5-5.5s5 2 5.5 5.5M13 15c1-.4 2.2-.5 3.5-.5 2.7 0 5 2 5.5 5.5"/>',
    "open-source": '<path d="M8.5 7.5 4 12l4.5 4.5M15.5 7.5 20 12l-4.5 4.5M13.5 5l-3 14"/>',
    "language": '<path d="M4 5.5h9M8.5 3.5v2M6 5.5c.5 3 2.5 5.5 5.5 6.5M11 5.5c-.5 3-2.5 5.5-6.5 7"/><path d="M12.5 20.5l4-9 4 9M14 17.5h5"/>',
}
ICON_LABELS = {"read": "Read aloud", "ask": "Ask", "explain": "Explain", "quiz": "Test me", "remind": "Reminders",
               "headphones": "Headphones", "offline": "Downloaded books", "page-turn": "Page turn", "tri-grip": "Tri-grip",
               "touch": "By touch", "mic-off": "Mic off", "light": "Page light", "battery": "Battery", "shared": "Commons",
               "open-source": "Open source", "language": "Bangla and English"}


def icon_svg(name, stroke, dot=None, size=24):
    body = ICONS[name].replace('class="dot"', f'fill="{dot or stroke}" stroke="none"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" role="img" '
            f'aria-label="{ICON_LABELS[name]}"><title>{ICON_LABELS[name]}</title>{body}</svg>')


def icons():
    for n in ICONS:
        w(f"icons/{n}.svg", icon_svg(n, C["spine"], C["marigold"]))


# ---------------------------------------------------------------------------------------- illustration
def illustration(ink=None):
    """Flat concept illustration of SenseBook on an open book, front view. Not a photo, not a render."""
    sp, pa, mg, mi = C["spine"], C["paper"], C["marigold"], C["mist"]
    lines = ""
    for side in (-1, 1):
        for i in range(9):
            y = 252 + i * 22
            x_in, x_out = 400 + side * 34, 400 + side * (260 - (8 if i == 0 else 0))
            if i in (3, 7):
                x_out = 400 + side * 190
            a, b = sorted((x_in, x_out))
            lines += f'<rect x="{a}" y="{y + abs(b - a) * 0 :.0f}" width="{b - a}" height="7" rx="3.5" fill="{sp}" opacity=".16"/>'
    s = f"""<defs><linearGradient id="cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{mi}" stop-opacity=".0"/>
<stop offset="1" stop-color="{bk.C['teal']}" stop-opacity=".10"/></linearGradient></defs>
<ellipse cx="400" cy="498" rx="350" ry="18" fill="{sp}" opacity=".10"/>
<path d="M400 224C320 196 190 194 70 220L52 476C180 452 310 456 400 482z" fill="#E9E1D2"/>
<path d="M400 224C480 196 610 194 730 220L748 476C620 452 490 456 400 482z" fill="#E9E1D2"/>
<path d="M400 216C322 188 194 186 78 212L62 466C186 442 314 446 400 472z" fill="#FFFDF8"/>
<path d="M400 216C478 188 606 186 722 212L738 466C614 442 486 446 400 472z" fill="#FFFDF8"/>
<path d="M400 216V472" stroke="{sp}" stroke-opacity=".18" stroke-width="2"/>
{lines}
<path d="M400 124 92 214 66 462 400 470 734 462 708 214z" fill="url(#cone)"/>
<path d="M391 205 378 226M409 205 422 226" stroke="#8a9aa0" stroke-width="3" stroke-linecap="round"/>
<rect x="395" y="126" width="10" height="84" rx="5" fill="{sp}"/>
<circle cx="400" cy="206" r="9" fill="{sp}"/>
<rect x="334" y="58" width="132" height="70" rx="20" fill="{sp}"/>
<path d="M336 104h128v4c0 11-9 20-20 20H356c-11 0-20-9-20-20z" fill="#0E2D33"/>
<ellipse cx="400" cy="57" rx="15" ry="4.5" fill="{mg}"/>
{''.join(f'<circle cx="{354 + i * 10}" cy="76" r="2.6" fill="#fff"/>' for i in range(4))}
<circle cx="400" cy="112" r="11" fill="#cfe3e6" opacity=".55"/><circle cx="400" cy="112" r="7" fill="#9ec3cf"/><circle cx="400" cy="112" r="3.4" fill="#0b2328"/>"""
    return bk.svg(s, 800, 520, title="SenseBook on an open book (illustration)")


# ---------------------------------------------------------------------------------------- tactile + packaging
def tactile():
    sp, mg, ink = C["spine"], C["marigold"], C["ink"]
    k = bk.MARK
    s = f"""<rect width="900" height="420" fill="{C['paper']}"/>
<g font-family="Atkinson Hyperlegible Next, Segoe UI, sans-serif" fill="{ink}">
<text x="40" y="44" font-size="22" font-weight="700" fill="{sp}">Tactile identity: what a hand finds, in order</text>
<g transform="translate(40 80)"><rect width="240" height="120" rx="34" fill="{sp}"/>
<ellipse cx="120" cy="4" rx="34" ry="9" fill="{mg}"/><circle cx="120" cy="2" r="4" fill="#fff" stroke="{ink}" stroke-width="1.2"/>
<text x="0" y="160" font-size="15" font-weight="700">1. Ask button, top centre</text>
<text x="0" y="182" font-size="14">Concave, marigold, one raised dot</text><text x="0" y="200" font-size="14">Ø 2.0 mm, 0.6 mm high: larger than a</text>
<text x="0" y="218" font-size="14">braille dot, so it is never read as braille</text></g>
<g transform="translate(330 80)"><rect width="240" height="120" rx="34" fill="{sp}"/>
<g transform="translate(84 18) scale(1.1)" opacity=".9">{bk.MARKS[k]('#2c5960', '#2c5960')}</g>
<text x="0" y="160" font-size="15" font-weight="700">2. Raised mark, back face</text>
<text x="0" y="182" font-size="14">The logo mark, 14 mm wide, 0.5 mm relief</text><text x="0" y="200" font-size="14">The dot points up: it tells the hand</text>
<text x="0" y="218" font-size="14">which way is the top of the device</text></g>
<g transform="translate(620 80)">
<path d="M0 60h60M90 60h60M180 60h60" stroke="#c9c1b2" stroke-width="2"/>
<path d="M44 40 22 60l22 20" fill="none" stroke="{sp}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="100" y="52" width="40" height="16" rx="8" fill="{sp}"/><circle cx="120" cy="60" r="3" fill="#fff"/>
<path d="M196 40l22 20-22 20" fill="none" stroke="{sp}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
<text x="0" y="160" font-size="15" font-weight="700">3. Back · Play · Forward</text>
<text x="0" y="182" font-size="14">Three shapes you can tell apart</text><text x="0" y="200" font-size="14">by touch alone. Mic-mute slide has</text>
<text x="0" y="218" font-size="14">ridges and an orange flag</text></g>
<text x="40" y="340" font-size="15" font-weight="700">4. Tri-grip blades: a raised dot near the hub on each blade,</text><text x="62" y="360" font-size="15">so a blind reader knows which side goes under the cover.</text>
<text x="470" y="340" font-size="15" font-weight="700">5. Box: a notch on the opening edge, and the name</text><text x="492" y="360" font-size="15">in braille (English UEB and Bangla), proofread by</text><text x="492" y="380" font-size="15">braille readers before printing.</text>
</g>"""
    w("tactile/tactile-identity.svg", bk.svg(s, 900, 420, title="SenseBook tactile identity"))


def packaging():
    sp, mg, pa = C["spine"], C["marigold"], C["paper"]
    kraft = "#C8AE86"
    inner, lw, lh = bk.lockup(bk.MARK, sp, sp, sp, size=40)
    d_tag, a_tag, _ = bk.text_outline("বই এখন কথা বলে", "notoserif-bn-600", 30)
    d_tag2, a_tag2, _ = bk.text_outline("Knowledge, now conversational.", "literata-400", 20)
    ill = illustration().split(">", 1)[1].rsplit("</svg>", 1)[0].split("</title>", 1)[1]
    s = f"""<rect width="1000" height="560" fill="{pa}"/>
<path d="M120 80h360v420H120z" fill="{kraft}"/><path d="M480 80l130-50v420l-130 50z" fill="#b39770"/><path d="M120 80l130-50h360l-130 50z" fill="#d6c09c"/>
<g transform="translate(150 110)">{inner}</g>
<g transform="translate(150 190) scale(.375)" opacity=".95"><g style="filter:grayscale(1)">{ill.replace(C['paper'], kraft)}</g></g>
<g transform="translate(150 430)"><path fill="{sp}" d="{d_tag}"/></g>
<g transform="translate(150 466)"><path fill="{sp}" d="{d_tag2}"/></g>
<path d="M610 210l-14 5v60l14-5z" fill="{mg}"/>
<g fill="{sp}">{''.join(f'<circle cx="{506 + (i % 2) * 6 + (i // 6) * 16}" cy="{130 + ((i // 2) % 3) * 6 - (i // 6) * 6}" r="1.8"/>' for i in (0, 2, 3, 6, 7, 9, 12, 13, 15))}</g>
<g font-family="Atkinson Hyperlegible Next, Segoe UI, sans-serif" font-size="15" fill="{C['ink']}">
<text x="660" y="120" font-weight="700" fill="{sp}">Box</text>
<text x="660" y="146">Recycled kraft board, no plastic film</text><text x="660" y="168">One colour: Spine</text>
<text x="660" y="190">Marigold pull tab (echoes Ask)</text><text x="660" y="212">Braille name on the side panel</text>
<text x="660" y="234">(dots shown are placeholders,</text><text x="660" y="256">to be set and proofread by</text><text x="660" y="278">braille readers)</text>
<text x="660" y="312">Inside: large-print and braille</text><text x="660" y="334">quick start, and an audio guide</text>
<text x="660" y="356">the device plays on first start</text>
<text x="660" y="400" font-weight="700" fill="{sp}">On the device</text>
<text x="660" y="426">No logo on the front face: only</text><text x="660" y="448">the four dots and the lens</text>
<text x="660" y="470">Raised mark on the back face</text><text x="660" y="492">Name and regulatory marks underneath</text>
</g>"""
    w("packaging/packaging-direction.svg", bk.svg(s, 1000, 560, title="SenseBook packaging direction"))


# ---------------------------------------------------------------------------------------- audio
SR = 22050
SOUNDS = [  # (file, name, when, notes as (freq Hz, start s, length s, level), timbre)
    ("startup", "Startup", "Powering on. The sonic logo: three rising notes, like a page opening.", [(587.33, 0, .5, .8), (880, .14, .5, .7), (1174.66, .28, .9, .6)], "marimba"),
    ("ready", "Ready", "Attached and the page is in view; ready to listen.", [(880, 0, .35, .7), (1174.66, .12, .6, .6)], "marimba"),
    ("page", "Page captured", "A page has settled and been captured. Soft paper click.", [], "click"),
    ("explainer", "Explainer voice next", "Before any AI explanation, so it never sounds like the book.", [(1318.5, 0, 1.0, .55)], "bell"),
    ("listening", "Listening", "Ask is held: the microphone is on.", [(659.25, 0, .12, .6), (987.77, .07, .18, .6)], "blip"),
    ("stop", "Stopped listening", "Ask released: the microphone is off.", [(987.77, 0, .12, .5), (659.25, .07, .18, .5)], "blip"),
    ("reminder", "Reminder", "Before a spoken reminder. Three gentle notes.", [(587.33, 0, .45, .6), (739.99, .2, .45, .6), (880, .4, .8, .55)], "marimba"),
    ("error", "Something's wrong", "Low tone, always followed by a short spoken instruction.", [(220, 0, .45, .8), (196, .16, .55, .7)], "soft"),
    ("battery", "Battery low", "Two falling notes, then the device says how much is left.", [(880, 0, .3, .5), (659.25, .18, .45, .5)], "marimba"),
]
HAPTICS = [("Attached", "one short pulse (40 ms)"), ("Ready", "two short pulses"), ("Mic off", "one long pulse (300 ms)"),
           ("Error", "three short pulses"), ("Reminder (headphones in)", "two long pulses")]


def synth(notes, timbre, dur):
    import random
    n = int(SR * dur)
    out = [0.0] * n
    if timbre == "click":
        random.seed(7)
        prev = 0.0
        for i in range(int(SR * .03)):
            v = random.uniform(-1, 1)
            prev = prev * .55 + v * .45  # soft low-pass
            out[i] += prev * .5 * math.exp(-i / (SR * .006))
        return out
    for f, st, ln, lv in notes:
        s0 = int(st * SR)
        for i in range(int(ln * SR)):
            t = i / SR
            if timbre == "marimba":
                env = math.exp(-t * 7.5) * min(1, t / .004)
                v = math.sin(2 * math.pi * f * t) + .25 * math.sin(2 * math.pi * f * 4 * t) * math.exp(-t * 30)
            elif timbre == "bell":
                env = math.exp(-t * 3.2) * min(1, t / .003)
                v = (math.sin(2 * math.pi * f * t) + .5 * math.sin(2 * math.pi * f * 2.76 * t) * math.exp(-t * 6)
                     + .25 * math.sin(2 * math.pi * f * 5.4 * t) * math.exp(-t * 12))
            elif timbre == "blip":
                env = math.sin(math.pi * min(1, t / ln)) ** 2
                v = math.sin(2 * math.pi * f * t)
            else:  # soft
                env = math.exp(-t * 5) * min(1, t / .01)
                v = math.sin(2 * math.pi * f * t) + .15 * math.sin(2 * math.pi * f * 2 * t)
            if s0 + i < n:
                out[s0 + i] += v * env * lv
    return out


def write_wav(path, samples):
    peak = max(abs(x) for x in samples) or 1
    g = 0.7 / peak  # -3 dBFS peak
    fade = int(SR * .01)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        frames = bytearray()
        for i, x in enumerate(samples):
            if i > len(samples) - fade:
                x *= (len(samples) - i) / fade
            frames += struct.pack("<h", int(max(-1, min(1, x * g)) * 32767))
        wf.writeframes(bytes(frames))


def audio():
    os.makedirs(os.path.join(B, "audio"), exist_ok=True)
    meta = []
    for fn, name, when, notes, timbre in SOUNDS:
        dur = max([st + ln for _, st, ln, _ in notes] or [.06]) + .05
        samples = synth(notes, timbre, dur)
        write_wav(os.path.join(B, "audio", f"{fn}.wav"), samples)
        meta.append({"file": f"{fn}.wav", "name": name, "when": when, "seconds": round(dur, 2), "timbre": timbre,
                     "notes_hz": [n[0] for n in notes]})
    w("audio/sounds.json", json.dumps({"sample_rate": SR, "sounds": meta, "haptics": [{"event": e, "pattern": p} for e, p in HAPTICS]},
                                      ensure_ascii=False, indent=2))


def main():
    logos(); colour(); icons(); tactile(); packaging(); audio()
    w("illustration/sensebook-on-book.svg", illustration())
    print("brand assets written to", B)


if __name__ == "__main__":
    main()
