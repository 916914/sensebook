"""Build the SenseBook brand guide (A4 landscape PDF) and page previews. Run: python brand/src/make_guide.py
Code: Apache-2.0. The guide: CC BY 4.0.
"""
import json, os, struct, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brandkit as bk
import brandcss
import make_brand as mb
import render

B = bk.BRAND
C = bk.C
OUT = os.path.join(B, "guide")
DATE = "27 November 2026"


def lock(fg=None, dot=None, size=56, name=bk.NAME, font=bk.WORDMARK_FONT, bn=False, word=None):
    inner, wd, ht = bk.lockup(bk.MARK, fg or C["spine"], dot or C["marigold"], word or fg or C["spine"], name=name, font=font, size=size, bn=bn)
    return bk.svg(inner, round(wd + 2), round(ht), vb=f"0 0 {wd + 2:.1f} {ht:.1f}")


def mark(px, fg=None, dot=None):
    x0, y0, x1, y1 = bk.MARK_BOX[bk.MARK]
    return bk.svg(bk.MARKS[bk.MARK](fg or C["spine"], dot or C["marigold"]), px, px * (y1 - y0 + 4) / (x1 - x0 + 4),
                  vb=f"{x0 - 2} {y0 - 2} {x1 - x0 + 4} {y1 - y0 + 4}")


def inline_svg(rel):
    with open(os.path.join(B, rel), encoding="utf-8") as f:
        s = f.read()
    return s.replace('<svg ', '<svg style="width:100%;height:auto" ', 1)


def waveform(fn, wpx=300, hpx=46, colour=None):
    with wave.open(os.path.join(B, "audio", fn)) as wf:
        n = wf.getnframes()
        data = struct.unpack("<" + "h" * n, wf.readframes(n))
    bins = 90
    step = max(1, len(data) // bins)
    peaks = [max(abs(x) for x in data[i:i + step]) / 32767 for i in range(0, step * bins, step)]
    bw = wpx / bins
    bars = "".join(f'<rect x="{i * bw:.1f}" y="{(hpx - max(1.5, p * hpx)) / 2:.1f}" width="{bw * .6:.1f}" height="{max(1.5, p * hpx):.1f}" rx="1"/>'
                   for i, p in enumerate(peaks))
    return f'<svg width="{wpx}" height="{hpx}" viewBox="0 0 {wpx} {hpx}" fill="{colour or C["teal"]}">{bars}</svg>'


CSS = brandcss.font_faces(brandcss.file_base()) + brandcss.tokens() + f"""
@page{{size:297mm 210mm;margin:0}}
*{{box-sizing:border-box}} html,body{{margin:0;padding:0}}
body{{font-family:{brandcss.SANS};color:var(--ink);font-size:12.5pt;line-height:1.45;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pg{{width:297mm;height:210mm;padding:15mm 17mm 13mm;position:relative;overflow:hidden;background:var(--paper);page-break-after:always;break-after:page}}
.pg.dark{{background:var(--spine);color:var(--paper)}} .pg.mist{{background:var(--mist)}}
.folio{{position:absolute;left:17mm;right:17mm;bottom:7mm;display:flex;justify-content:space-between;font-size:8pt;color:#5d686a}}
.dark .folio{{color:#a9c1c3}}
h1,h2,h3,.serif{{font-family:{brandcss.SERIF};font-weight:600;letter-spacing:-.005em}}
h1{{font-size:34pt;line-height:1.08;margin:0 0 6mm;color:var(--spine)}} .dark h1{{color:var(--paper)}}
h2{{font-size:20pt;line-height:1.15;margin:0 0 4mm;color:var(--spine)}} .dark h2{{color:var(--paper)}}
h3{{font-size:12.5pt;margin:0 0 2mm;color:var(--spine)}} .dark h3{{color:var(--marigold)}}
.kick{{font-size:9pt;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--teal);margin:0 0 3mm}}
.dark .kick{{color:var(--marigold)}}
p{{margin:0 0 3mm}} .lead{{font-size:14pt;line-height:1.4;max-width:200mm}} .muted{{color:#4f5b5d}} .dark .muted{{color:#c6d6d7}}
.bn{{font-family:"Noto Sans Bengali",{brandcss.SANS};line-height:1.6}} .bnserif{{font-family:"Noto Serif Bengali",serif;line-height:1.5}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:9mm}} .grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:6mm}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:5mm}} .grid5{{display:grid;grid-template-columns:repeat(5,1fr);gap:4mm}}
.card{{background:#fff;border-radius:4mm;padding:5mm}} .dark .card{{background:#1b4a52}} .mist .card{{background:var(--paper)}}
.tag{{display:inline-block;font-size:8pt;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:1mm 2.4mm;border-radius:10mm;background:var(--mist);color:var(--spine)}}
.tag.mg{{background:var(--marigold);color:var(--ink)}}
table{{border-collapse:collapse;width:100%;font-size:11pt}} td,th{{text-align:left;vertical-align:top;padding:2mm 2.5mm;border-bottom:.3mm solid #d9d2c4}}
th{{font-size:8pt;letter-spacing:.06em;text-transform:uppercase;color:var(--teal)}}
.big{{font-family:{brandcss.SERIF};font-weight:600;font-size:40pt;line-height:1.05;color:var(--spine)}}
.dark .big{{color:var(--paper)}}
.dot{{display:inline-block;width:3.2mm;height:3.2mm;border-radius:50%;background:var(--marigold);vertical-align:middle;margin-right:2mm}}
.x{{color:var(--brick);font-weight:700}} .ok{{color:var(--leaf);font-weight:700}}
.note{{font-size:9.5pt;color:#5d686a}}
"""


def folio(n, title, dark=False):
    return f'<div class="folio"><span>SenseBook brand guide · direction v1 · {DATE}</span><span>{title} · {n}</span></div>'


def pages():
    P = []
    n = lambda: len(P) + 1

    # 1 cover
    P.append(f"""<section class="pg dark"><div style="position:absolute;left:17mm;top:15mm">{lock(C['paper'], C['marigold'], 40, word=C['paper'])}</div>
<div style="position:absolute;left:17mm;top:62mm;width:180mm"><p class="kick">Brand guide · direction v1</p>
<div class="big" style="font-size:52pt">Knowledge,<br>now conversational.</div>
<p class="bnserif" style="font-size:30pt;margin-top:6mm;color:var(--marigold)">বই এখন কথা বলে</p></div>
<div style="position:absolute;right:-8mm;bottom:-6mm;width:150mm;opacity:.9">{mark(560, '#1d4d55', C['marigold'])}</div>
<div class="folio"><span>{DATE}</span><span>Open source · CC BY 4.0</span></div></section>""")

    # 2 how to use / status
    P.append(f"""<section class="pg"><p class="kick">Read this first</p><h1>One story, one product,<br>one brand for every reader.</h1>
<div class="grid3" style="margin-top:8mm">
<div class="card"><h3>What this guide is</h3><p>The direction for how SenseBook looks, sounds, feels and speaks, in English and Bangla. Everything here is free to use under CC BY 4.0; the files are in <b>brand/</b>.</p></div>
<div class="card"><h3>What is settled</h3><p>The story and positioning, the palette, the type, the icon style, the voice, the audio and tactile identity, and the claims we never make.</p><p>The name stays <b>SenseBook</b>, pending a Bangladesh trademark search.</p></div>
<div class="card" style="border:.5mm solid var(--marigold)"><h3>What is still open</h3><p><b>The logo is a working mark.</b> It sets the direction; the founders will confirm or replace it. Every file is generated from one script, so a new mark updates everything.</p></div></div>
<div class="grid4" style="margin-top:8mm">
{''.join(f'<div><p class="kick" style="color:var(--spine)">{a}</p><p class="muted">{b}</p></div>' for a, b in [('Story', 'Pages 3–5'), ('Personality and voice', 'Pages 6–7'), ('Logo, colour, type, icons', 'Pages 8–12'), ('Imagery, accessibility, sound, touch, packaging', 'Pages 13–18')])}
</div>{folio(n(), 'Read this first')}</section>""")

    # 3 story
    P.append(f"""<section class="pg dark"><p class="kick">The story</p>
<div class="big" style="font-size:44pt;max-width:220mm">Knowledge belongs to everyone.<br>Understanding should too.</div>
<p class="bnserif" style="font-size:22pt;color:var(--marigold);margin:4mm 0 9mm">জ্ঞান সবার। বোঝার সুযোগও সবার।</p>
<div class="grid2" style="max-width:250mm"><div><p class="lead" style="font-size:12.5pt">Two students can read the same textbook and get two different educations. One can ask a tutor whenever something is hard. The other is alone with the page. For a blind reader, even reaching the printed words is a barrier.</p>
<p class="lead" style="font-size:12.5pt">The knowledge is the same. The chance to understand it is not. <b>SenseBook exists to give every reader someone to learn with.</b></p></div>
<table style="color:var(--paper)"><tr><th style="color:var(--marigold)">Purpose</th><td>Democratise understanding.</td></tr>
<tr><th style="color:var(--marigold)">Promise</th><td>Never get stuck learning alone again.<br><span class="bn">পড়তে গিয়ে আর একা আটকে থাকতে হবে না।</span></td></tr>
<tr><th style="color:var(--marigold)">Tagline</th><td>Knowledge, now conversational. · <span class="bn">বই এখন কথা বলে</span></td></tr>
<tr><th style="color:var(--marigold)">Category</th><td>Personal learning technology</td></tr>
<tr><th style="color:var(--marigold)">Model</th><td>One product. One brand. Equal intelligence.</td></tr></table></div>
{folio(n(), 'The story')}</section>""")

    # 4 positioning on a page
    P.append(f"""<section class="pg"><p class="kick">Positioning on a page</p><h2>The mission is wide. The first promise is narrow.</h2>
<div class="grid3" style="gap:5mm">
<div class="card"><h3>Who uses it</h3><p>Everyone who reads, on one identical device. First: <b>Class 8–10 students</b> preparing for the SSC, and <b>blind and low-vision students</b>.</p></div>
<div class="card"><h3>Who pays</h3><p><b>Personal:</b> families, starting with the top 10–20% of urban households.<br><b>Commons:</b> schools, libraries, centres.<br><b>Access Fund:</b> CSR, foundations, NGOs.</p></div>
<div class="card"><h3>The problem</h3><p>Access to understanding is unequal: 49.8% of children aged 7–14 lack foundational reading, 60.8% foundational numeracy (MICS 2025). 76.5% of secondary students have tutors (Education Watch 2023).</p></div>
<div class="card"><h3>Main alternative</h3><p>The phone already in the house, plus the guidebook. For blind readers: free talking textbooks, free apps and people.</p></div>
<div class="card"><h3>Why us, not the phone</h3><p>The book stays the screen: no phone in the child's hands, hands-free page following, your own textbook from verified text even offline, nothing to aim.</p></div>
<div class="card" style="background:var(--spine);color:var(--paper)"><h3 style="color:var(--marigold)">Launch promise</h3><p>Turn the page of your own textbook. SenseBook reads it aloud, explains the hard parts, and quizzes you on it, hands-free.</p></div></div>
<p class="note" style="margin-top:5mm">Full version with sources, proof still needed and the never-say list: brand/POSITIONING.md. Evidence: docs/validation/.</p>
{folio(n(), 'Positioning')}</section>""")

    # 5 brand idea + one product, different lives
    lives = [("The Class 9 student", "Studying physics at 10 pm. No tutor for every subject. She turns the page; SenseBook reads, explains, and quizzes her."),
             ("The blind student", "The same textbook as her classmates, on the same device, with the same features. Nothing to aim, everything by touch and sound."),
             ("The university student", "Reading a hard chapter and wanting to talk it through, without switching between five tabs."),
             ("The lifelong learner", "Out of school, still curious: economics, English, a manual for a new machine.")]
    P.append(f"""<section class="pg mist"><p class="kick">Brand idea</p><div class="grid2" style="grid-template-columns:1.1fr 1.9fr;align-items:start">
<div><div class="big">Someone to learn with.</div><p class="bnserif" style="font-size:20pt;color:var(--teal);margin-top:3mm">শেখার একজন সঙ্গী।</p>
<p style="margin-top:5mm">SenseBook sits at the top of the page, like a patient friend reading over your shoulder. It never takes the book away; it helps you understand it.</p></div>
<div><h3>One product. Different lives.</h3><div class="grid2" style="gap:4mm">{''.join(f'<div class="card"><span class="dot"></span><b>{a}</b><p class="muted" style="margin-top:2mm">{b}</p></div>' for a, b in lives)}</div>
<p class="note" style="margin-top:3mm">Illustrative people, not customers or testimonials. The common thread is intellectual independence, never disability, poverty or charity.</p></div></div>
{folio(n(), 'Brand idea')}</section>""")

    # 6 personality
    traits = [("Patient", "ধৈর্যশীল", "Explains again, a different way, as often as needed.", "Rushed, salesy"),
              ("Honest", "সৎ", "Says what the page says, and when it isn't sure.", "Hype, overclaiming"),
              ("Curious", "কৌতূহলী", "Asks good questions back; makes you think.", "An answer machine"),
              ("Calm", "শান্ত", "Quiet sounds, plain words, grown-up design.", "Gamified, cute, loud"),
              ("Equal", "সমান", "Speaks to every reader the same way.", "Pitying, childish, charitable")]
    P.append(f"""<section class="pg"><p class="kick">Personality</p><h2>If SenseBook were a person, it would be the best teacher you had.</h2>
<div class="grid5" style="margin-top:6mm">{''.join(f'<div class="card" style="min-height:92mm"><div class="serif" style="font-size:19pt;color:var(--spine)">{a}</div><div class="bn" style="color:var(--teal);font-size:13pt">{b}</div><p style="margin-top:4mm">{c}</p><p class="note"><span class="x">Not:</span> {d}</p></div>' for a, b, c, d in traits)}</div>
{folio(n(), 'Personality')}</section>""")

    # 7 voice
    ex = [("Device, reading", "Page 42. Chapter 3: Light.", "পাতা ৪২। তৃতীয় অধ্যায়: আলো।"),
          ("Device, unsure", "I'm not sure of this word. It may be 'refraction'.", "এই শব্দটা নিয়ে আমি নিশ্চিত নই। সম্ভবত 'প্রতিসরণ'।"),
          ("Device, offline", "No internet. I can still read downloaded books.", "ইন্টারনেট নেই। ডাউনলোড করা বই এখনো পড়তে পারি।"),
          ("Marketing", "Help on the page you're reading, any evening.", "যে পাতা পড়ছ, সেখানেই সাহায্য, যেকোনো সন্ধ্যায়।"),
          ("To a parent", "The microphone only listens while your child holds Ask.", "আপনার সন্তান Ask চেপে ধরলে তবেই মাইক্রোফোন শোনে।")]
    P.append(f"""<section class="pg"><p class="kick">Voice</p><div class="grid2" style="grid-template-columns:1fr 1.5fr">
<div><h2>Plain, warm, exact.</h2>
<p><b>Short sentences.</b> One idea each. Concrete words: the page, the chapter, the button.</p>
<p><b>Say what we know.</b> Mark estimates as estimates. Say "in testing" when it is.</p>
<p><b>Bangla first in Bangladesh.</b> Standard colloquial (চলিত). <span class="bn">তুমি</span> to students, <span class="bn">আপনি</span> to parents, adults and institutions. Bangla numerals in Bangla text.</p>
<p><b>Two voices on the device.</b> The <b>reader voice</b> reads the page; a chime, then the <b>explainer voice</b> helps. The AI never speaks in the book's voice.</p>
<p><span class="x">Never:</span> revolutionary, magic, smart, genius, never wrong, replaces, the only.</p></div>
<table><tr><th>Where</th><th>English</th><th>বাংলা</th></tr>{''.join(f'<tr><td class="muted">{a}</td><td>{b}</td><td class="bn">{c}</td></tr>' for a, b, c in ex)}</table></div>
{folio(n(), 'Voice')}</section>""")

    # 8 logo direction
    x0, y0, x1, y1 = bk.MARK_BOX[bk.MARK]
    grid = "".join(f'<line x1="{i}" y1="4" x2="{i}" y2="60" stroke="#d9d2c4" stroke-width=".15"/><line x1="4" y1="{i}" x2="60" y2="{i}" stroke="#d9d2c4" stroke-width=".15"/>' for i in range(4, 61, 4))
    constr = f'<svg viewBox="0 0 64 64" style="width:92mm;height:92mm">{grid}{bk.MARKS[bk.MARK](C["spine"], C["marigold"])}<circle cx="32" cy="17" r="10.2" fill="none" stroke="{C["teal"]}" stroke-width=".25" stroke-dasharray="1 1"/></svg>'
    P.append(f"""<section class="pg"><p class="kick">Logo direction · working mark</p><div class="grid2" style="grid-template-columns:1fr 1.25fr;align-items:center">
<div style="text-align:center">{constr}</div>
<div><h2>An open book, and someone at the top of the page.</h2>
<p><b>The pages</b> are any printed book. <b>The gap</b> is the spine. <b>The marigold dot</b> is SenseBook, sitting exactly where the device sits, and the colour of its Ask button: the voice.</p>
<p>It reads as a person with a book, a reader. It works at 16 px, in one colour, and as a raised mark a hand can feel.</p>
<p>The wordmark is Literata SemiBold, outlined. Bangla: Noto Serif Bengali Bold, outlined.</p>
<div style="margin-top:6mm;display:grid;gap:5mm">{lock(size=50)}{lock(size=46, name=bk.NAME_BN, font=bk.WORDMARK_FONT_BN, bn=True)}</div>
<p class="note" style="margin-top:4mm">Status: working mark for drafts. The founders will confirm or replace it.</p></div></div>
{folio(n(), 'Logo')}</section>""")

    # 9 logo use
    misuse = [("transform:scaleX(1.5)", "Don't stretch"), ("transform:rotate(-12deg)", "Don't rotate"),
              ("filter:drop-shadow(0 0 3mm #8a5cff)", "No glows or effects"), ("filter:hue-rotate(160deg)", "Don't recolour")]
    P.append(f"""<section class="pg"><p class="kick">Using the logo</p><div class="grid2" style="grid-template-columns:1.2fr 1fr">
<div><div class="grid2" style="gap:4mm">
<div class="card" style="display:grid;place-items:center;height:42mm">{lock(size=34)}</div>
<div class="card" style="display:grid;place-items:center;height:42mm;background:var(--spine)">{lock(C['paper'], C['marigold'], 34, word=C['paper'])}</div>
<div class="card" style="display:grid;place-items:center;height:42mm">{lock(C['ink'], C['ink'], 34)}</div>
<div class="card" style="display:grid;place-items:center;height:42mm;background:var(--marigold)">{lock(C['ink'], C['paper'], 34, word=C['ink'])}</div></div>
<p class="note" style="margin-top:3mm">Colour on paper · reversed on Spine · one colour (Ink) for print and fax · on Marigold, ink with a paper dot.</p></div>
<div><h3>Clear space and size</h3><p>Keep clear space of one dot diameter on every side. Smallest sizes: mark 16 px or 5 mm; lockup 96 px or 25 mm wide.</p>
<div style="display:flex;gap:6mm;align-items:end;margin:3mm 0 6mm">{mark(96)}{mark(48)}{mark(24)}{mark(16)}</div>
<h3>Don't</h3><div class="grid4" style="gap:3mm">{''.join(f'<div class="card" style="padding:3mm;text-align:center"><div style="height:16mm;display:grid;place-items:center"><div style="{s}">{mark(40)}</div></div><p class="note"><span class="x">×</span> {t}</p></div>' for s, t in misuse)}</div>
<p class="note" style="margin-top:3mm">Also: no gradients, no sparkles, never on a busy photo without a solid panel, never the device front.</p></div></div>
{folio(n(), 'Logo use')}</section>""")

    # 10 colour
    sw = "".join(f'<div style="background:{h};color:{C["paper"] if bk.luminance(h) < .25 else C["ink"]};border-radius:4mm;padding:4mm;height:58mm;display:flex;flex-direction:column">'
                 f'<b class="serif" style="font-size:14pt">{nm}</b><span class="bn">{bn}</span><code style="margin-top:2mm">{h}</code><span style="margin-top:auto;font-size:8.5pt">{r}</span></div>'
                 for _, nm, bn, h, r in bk.PALETTE)
    pairs = [("ink", "paper"), ("spine", "paper"), ("paper", "spine"), ("marigold", "spine"), ("ink", "marigold"), ("marigold", "paper")]
    pr = "".join(f'<div style="background:{C[b]};color:{C[f]};border-radius:3mm;padding:3mm 4mm;border:.3mm solid #0001"><b style="font-size:16pt">Aa <span class="bn">অআ</span></b><br><span style="font-size:8.5pt">{f} on {b} · {bk.contrast(C[f], C[b]):.1f}:1 · {bk.grade(bk.contrast(C[f], C[b]))}</span></div>' for f, b in pairs)
    P.append(f"""<section class="pg"><p class="kick">Colour</p><h2>The device, the button, the page.</h2>
<div style="display:grid;grid-template-columns:repeat(8,1fr);gap:3mm">{sw}</div>
<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:3mm;margin-top:5mm">{pr}</div>
<p class="note" style="margin-top:3mm">Proportions: mostly Paper and Spine, a little Teal and Mist, Marigold only for the dot, Ask and one key action. Body text is Ink or Spine on Paper (AAA). Marigold is never text on a light background. High-contrast mode: Paper on Spine, or Marigold on Ink.</p>
{folio(n(), 'Colour')}</section>""")

    # 11 type
    P.append(f"""<section class="pg"><p class="kick">Type</p><div class="grid2" style="grid-template-columns:1.35fr 1fr">
<div><div class="serif" style="font-size:36pt;line-height:1.1;color:var(--spine)">Knowledge, now conversational.</div>
<div class="bnserif" style="font-size:30pt;color:var(--spine);margin:2mm 0 6mm">বই এখন কথা বলে</div>
<p style="font-size:13pt">Body text is set in Atkinson Hyperlegible Next, designed for readers with low vision: every letter is easy to tell apart. Il1 O0 rn m.</p>
<p class="bn" style="font-size:13pt">বাংলা লেখা নোটো সান্স বাংলায়। যুক্তবর্ণ পরিষ্কার: ক্ষ ঙ্গ ন্স ষ্ট্র। লাইনের ফাঁক একটু বেশি, যাতে মাত্রা আর কার জায়গা পায়।</p></div>
<div><table><tr><th>Role</th><th>Latin</th><th>Bangla</th></tr>
<tr><td>Display, headings</td><td>Literata 600</td><td>Noto Serif Bengali 600/700</td></tr>
<tr><td>Text, interface</td><td>Atkinson Hyperlegible Next 400/700</td><td>Noto Sans Bengali 400/700</td></tr></table>
<h3 style="margin-top:5mm">Large type is the default</h3>
<table><tr><td>Web body</td><td>18 px, line height 1.5 (Bangla 1.65)</td></tr><tr><td>Print body</td><td>11 pt minimum</td></tr>
<tr><td>Large-print versions</td><td>18 pt, for every printed guide</td></tr><tr><td>Line length</td><td>60–70 characters</td></tr></table>
<p class="note" style="margin-top:3mm">All four families are open source (SIL OFL); the files are in brand/type/fonts.</p></div></div>
{folio(n(), 'Type')}</section>""")

    # 12 icons
    ic = "".join(f'<div class="card" style="text-align:center;padding:4mm 2mm">{mb.icon_svg(k, C["spine"], C["marigold"], 40)}<div class="note" style="margin-top:2mm;color:var(--ink)">{mb.ICON_LABELS[k]}</div></div>' for k in mb.ICONS)
    P.append(f"""<section class="pg mist"><p class="kick">Icons</p><h2>Drawn like the mark: simple lines, one dot.</h2>
<div style="display:grid;grid-template-columns:repeat(8,1fr);gap:3mm">{ic}</div>
<p style="margin-top:5mm">24 px grid, 2 px stroke, round ends and joins, no fills except the marigold dot for "voice" and "touch". Always with a text label: icons support words, they never replace them.</p>
{folio(n(), 'Icons')}</section>""")

    # 13 imagery
    P.append(f"""<section class="pg"><p class="kick">Photography and renders</p><div class="grid2" style="grid-template-columns:1.1fr 1fr">
<div><div class="card" style="padding:2mm">{inline_svg('illustration/sensebook-on-book.svg')}</div><p class="note" style="margin-top:2mm">Brand illustration of SenseBook on a textbook spread. An illustration, labelled as one: not a photo, not a measured render.</p></div>
<div><h2>Real, warm, ordinary.</h2>
<p><span class="ok">Do</span> real Bangladeshi homes, classrooms and libraries; evening table-lamp and window light; real hands, real books, the device at true size.</p>
<p><span class="ok">Do</span> show every kind of reader as capable: a Class 9 student, a university student, a teacher, an older learner, a blind reader in control. Photograph with consent, and with blind readers, not about them.</p>
<p><span class="ok">Do</span> label renders as renders and match them to the CAD dimensions.</p>
<p><span class="x">Don't</span> use AI-generated people or scenes as if they were real; glowing holograms, neon, purple gradients, floating screens; staged pity; foreign stock classrooms; readable NCTB covers used as endorsement.</p></div></div>
{folio(n(), 'Imagery')}</section>""")

    # 14 accessibility identity
    acc = [("touch", "Every control by touch", "Ask, back, play, forward and mic-mute are shapes a hand can tell apart. Nothing depends on sight."),
           ("explain", "Every state has a sound", "Short, distinct sounds and a spoken line, plus a vibration when the speaker is off."),
           ("read", "Two voices", "The reader voice reads the book; a chime, then the explainer voice helps."),
           ("light", "High contrast", "Body text AAA (7:1+). Nothing important is shown by colour alone."),
           ("language", "Plain words, two languages", "Bangla first in Bangladesh. Short sentences. Every guide in large print, braille and audio."),
           ("shared", "The same product for everyone", "No separate edition, no proof of disability, no 'accessibility mode' to find.")]
    P.append(f"""<section class="pg dark"><p class="kick">Accessibility is the identity</p><h2>Built in, like a kerb ramp: good for everyone.</h2>
<div class="grid3" style="gap:5mm;margin-top:6mm">{''.join(f'<div class="card"><div style="margin-bottom:2mm">{mb.icon_svg(i, C["paper"], C["marigold"], 30)}</div><h3>{a}</h3><p style="color:#d9e6e6">{b}</p></div>' for i, a, b in acc)}</div>
{folio(n(), 'Accessibility')}</section>""")

    # 15 audio
    meta = json.load(open(os.path.join(B, "audio", "sounds.json"), encoding="utf-8"))
    rows = "".join(f'<tr><td><b>{s["name"]}</b></td><td>{waveform(s["file"], 190, 26)}</td><td class="muted">{s["when"]}</td><td class="note">{s["file"]} · {s["seconds"]} s</td></tr>' for s in meta["sounds"])
    hap = "".join(f'<tr><td>{h["event"]}</td><td>{h["pattern"]}</td></tr>' for h in meta["haptics"])
    P.append(f"""<section class="pg"><p class="kick">Sound identity</p><div class="grid2" style="grid-template-columns:2.1fr 1fr">
<div><table>{rows}</table></div>
<div><h2>Soft wood and one bell.</h2><p>The startup sound is the sonic logo: three rising notes, like a page opening. Everything else is shorter. Sounds are never melodies or jingles, and can be turned down separately from speech.</p>
<p>The single bell always comes before the explainer voice, so the AI never sounds like the book.</p>
<h3 style="margin-top:4mm">Vibration</h3><table>{hap}</table>
<p class="note" style="margin-top:3mm">Files: brand/audio (WAV, 22 kHz, mono). First drafts, to be tested with blind and sighted listeners.</p></div></div>
{folio(n(), 'Sound')}</section>""")

    # 16 tactile
    P.append(f"""<section class="pg"><p class="kick">Tactile identity</p><h2>A hand finds the brand first.</h2>
<div class="card" style="padding:2mm">{inline_svg('tactile/tactile-identity.svg')}</div>
<p class="note" style="margin-top:3mm">Sizes are design targets, to be tested with blind readers in the attachment bench test. Braille on packaging is set and proofread by braille readers before printing.</p>
{folio(n(), 'Touch')}</section>""")

    # 17 packaging
    P.append(f"""<section class="pg"><p class="kick">Packaging and on-device marks</p><h2>Quiet outside, generous inside.</h2>
<div class="card" style="padding:2mm">{inline_svg('packaging/packaging-direction.svg')}</div>
{folio(n(), 'Packaging')}</section>""")

    # 18 architecture
    arch = [("SenseBook Personal", "Your own SenseBook.", "Readers and families"),
            ("SenseBook Commons", "Shared SenseBooks in schools, libraries and learning centres.", "Institutions"),
            ("SenseBook Access Fund", "Funded access: device, training, maintenance and service.", "CSR, foundations, NGOs, donors")]
    P.append(f"""<section class="pg mist"><p class="kick">Brand architecture</p><h2>One master brand, three ways to reach a reader.</h2>
<div class="grid3" style="gap:5mm;margin-top:4mm">{''.join(f'<div class="card"><div style="margin-bottom:3mm">{lock(size=26)}</div><div class="serif" style="font-size:15pt;color:var(--teal)">{a.replace("SenseBook ", "")}</div><p style="margin-top:2mm">{b}</p><p class="note">Who pays: {c}</p></div>' for a, b, c in arch)}</div>
<div class="grid2" style="margin-top:6mm"><div><h3>Rules</h3><p>Every route gets the same device, the same software and the same look. No "charity edition", no different colour, no label on the device. Programme names are set in the text typeface after the logo, never in a separate logo.</p></div>
<div><h3>SenseBook Impact Report</h3><p>Published every year, independently evaluated wherever possible. It reports only what was measured: learners reached, hours, reading independence, and comprehension from independent studies.</p></div></div>
{folio(n(), 'Architecture')}</section>""")

    # 19 words
    P.append(f"""<section class="pg"><p class="kick">Words we use, claims we never make</p><div class="grid2">
<div><h3>Say</h3><table>
<tr><td>Reads your textbooks. Other print: in testing.</td></tr><tr><td>Reads verified text for your textbook, and tells you when it isn't sure.</td></tr>
<tr><td>Help on the page you're reading, any evening.</td></tr><tr><td>Reads downloaded textbooks without internet.</td></tr>
<tr><td>The mic only listens while you hold Ask.</td></tr><tr><td>Designed from day one for blind and low-vision readers.</td></tr>
<tr><td>A small fraction of the price of imported readers (with the real figures).</td></tr><tr><td>Prototype. Not yet tested or certified.</td></tr></table></div>
<div><h3>Never say</h3><table>
<tr><td><span class="x">×</span> Reads any book, letter or newspaper</td></tr><tr><td><span class="x">×</span> Never makes mistakes · 100% accurate</td></tr>
<tr><td><span class="x">×</span> Improves grades · saves tutor money (until measured)</td></tr><tr><td><span class="x">×</span> Replaces your tutor or teacher</td></tr>
<tr><td><span class="x">×</span> NCTB-approved · any endorsement not signed</td></tr><tr><td><span class="x">×</span> Powered by (an AI provider's name)</td></tr>
<tr><td><span class="x">×</span> Built with blind students (until co-design happens)</td></tr><tr><td><span class="x">×</span> Invented users, quotes, ratings or counts</td></tr></table></div></div>
{folio(n(), 'Words')}</section>""")

    # 20 back cover
    P.append(f"""<section class="pg dark"><div style="position:absolute;left:17mm;top:15mm">{lock(C['paper'], C['marigold'], 34, word=C['paper'])}</div>
<div style="position:absolute;left:17mm;bottom:28mm;width:230mm"><p class="kick">Files</p>
<p>brand/logo · brand/colour · brand/type/fonts · brand/icons · brand/audio · brand/tactile · brand/packaging · brand/illustration · brand/POSITIONING.md · brand/BRAND.md</p>
<p class="muted">Generated by brand/src (Apache-2.0). Brand assets and this guide: CC BY 4.0. Fonts: SIL Open Font License.</p></div>
<div class="folio"><span>{DATE}</span><span>Knowledge belongs to everyone. Understanding should too.</span></div></section>""")
    return P


def main():
    os.makedirs(OUT, exist_ok=True)
    html = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SenseBook brand guide</title><style>{CSS}</style></head><body>{"".join(pages())}</body></html>'
    hp = os.path.join(OUT, "SenseBook_Brand_Guide.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html)
    pdf = render.pdf(hp, os.path.join(OUT, "SenseBook_Brand_Guide.pdf"))
    previews(pdf, os.path.join(OUT, "preview"))
    print("guide:", pdf)


def previews(pdf, outdir, width=1400, sheet_cols=4):
    import fitz
    os.makedirs(outdir, exist_ok=True)
    doc = fitz.open(pdf)
    files = []
    for i, pg in enumerate(doc):
        zoom = width / pg.rect.width
        pix = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        fp = os.path.join(outdir, f"page-{i + 1:02d}.png")
        pix.save(fp)
        files.append(fp)
    # contact sheet
    from PIL import Image
    ims = [Image.open(f) for f in files]
    tw = 480
    th = int(ims[0].height * tw / ims[0].width)
    rows = (len(ims) + sheet_cols - 1) // sheet_cols
    sheet = Image.new("RGB", (sheet_cols * (tw + 16) + 16, rows * (th + 16) + 16), (236, 230, 218))
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw, th)), (16 + (i % sheet_cols) * (tw + 16), 16 + (i // sheet_cols) * (th + 16)))
    sheet.save(os.path.join(outdir, "contact-sheet.png"))
    print(len(files), "pages")
    return files


if __name__ == "__main__":
    main()
