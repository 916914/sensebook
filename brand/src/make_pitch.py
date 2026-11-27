"""Build the SenseBook pitch deck (10 slides, 16:9 PDF) and one-page summary (A4 PDF) into docs/pitch/.
Run from PowerShell or cmd: python brand/src/make_pitch.py     Code: Apache-2.0. Outputs: CC BY 4.0.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brandkit as bk
import brandcss
import make_brand as mb
import render
from make_guide import lock, mark, previews

C = bk.C
OUT = os.path.join(os.path.dirname(bk.BRAND), "docs", "pitch")
HUB = "sensebook-hub.vercel.app"
REPO = "github.com/916914/sensebook"


def ill():
    with open(os.path.join(bk.BRAND, "illustration", "sensebook-on-book.svg"), encoding="utf-8") as f:
        return f.read().replace("<svg ", '<svg style="width:100%;height:auto;display:block" ', 1)


BASE = brandcss.font_faces(brandcss.file_base()) + brandcss.tokens() + f"""
*{{box-sizing:border-box}} html,body{{margin:0;padding:0}}
body{{font-family:{brandcss.SANS};color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}}
h1,h2,h3,.serif{{font-family:{brandcss.SERIF};font-weight:600;letter-spacing:-.005em;margin:0}}
.bn{{font-family:"Noto Sans Bengali",{brandcss.SANS}}} .bns{{font-family:"Noto Serif Bengali",serif}}
.kick{{font-size:15px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--teal);margin:0 0 10px}}
.dark .kick{{color:var(--marigold)}} p{{margin:0 0 12px}}
.card{{background:#fff;border-radius:14px;padding:20px 22px}} .dark .card{{background:#1B4A52;color:var(--paper)}}
.mg{{color:var(--marigold)}} .muted{{color:#4F5B5D}} .dark .muted{{color:#BFD2D3}}
.src{{font-size:12.5px;color:#5D686A}} .dark .src{{color:#A9C1C3}}
table{{border-collapse:collapse;width:100%}} td,th{{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid #DDD5C6}}
th{{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--teal)}}
.yes{{color:var(--leaf);font-weight:700}} .no{{color:#8A9497}}
"""

DECK_CSS = BASE + """
@page{size:1280px 720px;margin:0}
.s{width:1280px;height:720px;padding:56px 72px 48px;position:relative;overflow:hidden;background:var(--paper);page-break-after:always;break-after:page;font-size:21px;line-height:1.4}
.s.dark{background:var(--spine);color:var(--paper)} .s.mist{background:var(--mist)}
.s h2{font-size:46px;line-height:1.08;color:var(--spine);margin-bottom:20px;max-width:1000px} .dark h2{color:var(--paper)}
.ft{position:absolute;left:72px;right:72px;bottom:22px;display:flex;justify-content:space-between;font-size:12.5px;color:#6B7476}
.dark .ft{color:#A9C1C3}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:28px} .g3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px} .g4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.stat{font-family:Literata,serif;font-weight:600;font-size:60px;line-height:1;color:var(--spine);margin-bottom:8px} .dark .stat{color:var(--marigold)}
"""


def ft(n, src=""):
    return f'<div class="ft"><span>{src}</span><span>SenseBook · {n} / 10</span></div>'


def slides():
    S = []
    # 1 title
    S.append(f"""<section class="s dark"><div style="position:absolute;left:72px;top:56px">{lock(C['paper'], C['marigold'], 34, word=C['paper'])}</div>
<div style="position:absolute;left:72px;top:190px;width:560px"><p class="kick">Personal learning technology</p>
<h1 style="font-size:66px;line-height:1.04">Knowledge, now conversational.</h1><p class="bns" style="font-size:36px;color:var(--marigold);margin-top:16px">বই এখন কথা বলে</p>
<p style="font-size:22px;color:#D4E2E2;margin-top:18px">A screen-free companion that clips onto a printed book, reads it aloud, explains it and quizzes you on it. One product for every reader.</p></div>
<div style="position:absolute;right:56px;top:150px;width:560px;background:var(--paper);border-radius:22px;padding:18px">{ill()}</div>
<div class="ft"><span>Prototype stage · {HUB} · open source</span><span>27 November 2026</span></div></section>""")
    # 2 problem
    S.append(f"""<section class="s"><p class="kick">The problem</p><h2>Two students read the same textbook and get two different educations.</h2>
<div class="g4" style="margin-top:8px">
<div class="card"><div class="stat">49.8%</div><p>of children aged 7–14 could not show foundational reading skills.</p><p class="src">MICS 2025 (BBS, UNICEF)</p></div>
<div class="card"><div class="stat">60.8%</div><p>could not show foundational numeracy.</p><p class="src">MICS 2025 (BBS, UNICEF)</p></div>
<div class="card"><div class="stat">76.5%</div><p>of secondary students had private tutors or coaching.</p><p class="src">Education Watch 2023 (CAMPE)</p></div>
<div class="card"><div class="stat">Tk 27,340</div><p>a year spent on one Class 9 student's education by families.</p><p class="src">Education Watch 2022 (CAMPE)</p></div></div>
<p style="margin-top:26px;font-size:24px;max-width:1080px">One student can ask a tutor whenever something is hard; the other is alone with the page. A blind student often can't reach the printed words at all. <b>Access to knowledge is near-universal. Access to understanding is not.</b></p>
{ft(2, 'Sources: Dhaka Tribune on MICS 2025; The Daily Star on Education Watch 2022 and 2023')}</section>""")
    # 3 product
    steps = [("tri-grip", "Clip it on", "Two thin blades slip inside the covers, a third leg rests on the spine. Nothing touches the pages."),
             ("page-turn", "Turn the page", "It sees the spread, waits for the page to settle and carries on. No buttons."),
             ("read", "Listen", "The reader voice reads your textbook from verified text, and says when it isn't sure."),
             ("ask", "Ask and practise", "Hold Ask: after a bell, the explainer voice helps. Then it quizzes you and plans your revision.")]
    S.append(f"""<section class="s"><p class="kick">The product</p><h2>The book stays the screen.</h2>
<div class="g2" style="grid-template-columns:1fr 1.15fr;align-items:center"><div class="card" style="padding:12px">{ill()}<p class="src" style="margin:6px 8px 0">Illustration, not a photo or render. Unit about 8.5 × 3.8 × 3 cm (target).</p></div>
<div style="display:grid;gap:12px">{''.join(f'<div style="display:flex;gap:16px;align-items:flex-start">{mb.icon_svg(i, C["spine"], C["marigold"], 40)}<div><b class="serif" style="font-size:23px;color:var(--spine)">{t}</b><p style="margin:2px 0 0;font-size:19px" class="muted">{d}</p></div></div>' for i, t, d in steps)}
<p style="font-size:18px;margin:6px 0 0">Bangla and English · speaker, wired headphones or Bluetooth earbuds · downloaded textbooks read without internet.</p></div></div>
{ft(3, 'Product spec v1.1; tri-grip attachment plan. Prototype software runs on a laptop; hardware not yet built.')}</section>""")
    # 4 vs phone
    rows = [("No screen in the student's hands", "no", "yes"), ("Nothing to aim or hold", "no", "yes"), ("Follows real pages hands-free", "no", "yes"),
            ("Your textbook from verified text, offline", "no", "yes"), ("Every control by touch, for blind readers", "no", "yes"),
            ("Already owned, free, broad capability", "yes", "no")]
    tick = {"yes": '<span class="yes">Yes</span>', "no": '<span class="no">No</span>'}
    S.append(f"""<section class="s"><p class="kick">The real rival</p><h2>Why not just use the phone?</h2>
<div class="g2" style="grid-template-columns:1.25fr 1fr"><table style="font-size:20px"><tr><th></th><th>Phone + free AI</th><th>SenseBook</th></tr>
{''.join(f'<tr><td>{a}</td><td>{tick[b]}</td><td>{tick[c]}</td></tr>' for a, b, c in rows)}</table>
<div><div class="card" style="background:var(--spine);color:var(--paper)"><div class="stat" style="color:var(--marigold)">75.1%</div><p>of households have a smartphone. The phone is the rival, and we don't claim better AI: it can run the same models.</p><p class="src" style="color:#A9C1C3">BBS ICT survey 2026</p></div>
<div class="card" style="margin-top:16px"><div class="stat">8 of 14</div><p>blind users in a 2025 study needed sighted help to aim a phone camera.</p><p class="src">CHI 2025, arXiv 2502.16098</p></div></div></div>
{ft(4, 'Other rivals: guidebooks (used by 93%), Shikho EduTab, free DAISY talking textbooks, Lookout and Envision apps. Full table: validation report.')}</section>""")
    # 5 one product
    lives = [("The Class 9 student", "Physics at 10 pm, no tutor for every subject."), ("The blind student", "The same textbook and the same SenseBook as her classmates."),
             ("The university student", "A hard chapter to talk through, without five tabs."), ("The lifelong learner", "Economics, English, the manual for a new machine.")]
    S.append(f"""<section class="s mist"><p class="kick">One product, every reader</p><h2>Accessibility built in, like a kerb ramp: it helps everyone.</h2>
<div class="g4">{''.join(f'<div class="card" style="background:var(--paper)"><b class="serif" style="font-size:22px;color:var(--spine)">{a}</b><p class="muted" style="margin-top:8px">{b}</p></div>' for a, b in lives)}</div>
<div class="g3" style="margin-top:22px">
<div><b>Same device, same features.</b><p class="muted">No separate edition, no proof of disability, no hidden mode.</p></div>
<div><b>Two voices.</b><p class="muted">The reader voice reads the book; the explainer voice always comes after a bell.</p></div>
<div><b>Touch and sound first.</b><p class="muted">Ask button with a raised dot, three distinct buttons, a sound and a vibration for every state.</p></div></div>
{ft(5, 'Illustrative people, not customers. We start with Class 8–10 students preparing for the SSC, and with blind and low-vision students.')}</section>""")
    # 6 business model
    S.append(f"""<section class="s"><p class="kick">Business model</p><h2>Owned, shared, funded. Always the same SenseBook.</h2>
<div class="g3">
<div class="card" style="border-top:8px solid var(--spine)"><b class="serif" style="font-size:26px;color:var(--spine)">Personal</b><p class="muted" style="margin-top:6px">Families buy the device; a subscription adds unlimited questions, quizzes and parent reports.</p><p><b>Device Tk 14,990</b> (deposit test at Tk 9,990–14,990)<br><b>Learn Plus Tk 399 a month</b></p></div>
<div class="card" style="border-top:8px solid var(--teal)"><b class="serif" style="font-size:26px;color:var(--spine)">Commons</b><p class="muted" style="margin-top:6px">Schools, libraries and learning centres buy or lease shared devices, with support and a licence.</p><p><b>Plan: Tk 11,490 a device + Tk 1,990 a year</b></p></div>
<div class="card" style="border-top:8px solid var(--marigold)"><b class="serif" style="font-size:26px;color:var(--spine)">Access Fund</b><p class="muted" style="margin-top:6px">CSR teams, foundations and NGOs fund device, training, maintenance and two years of service.</p><p><b>Plan: Tk 16,990 a reader</b>, about 1/14 to 1/40 of imported readers for blind people</p></div></div>
<p style="margin-top:22px;font-size:19px" class="muted">Every price is a plan hypothesis, to be tested with real deposits and letters of intent. In the plan's model, a v1 device contributes about Tk 1,336 at sale; it loses money below Tk 12,990.</p>
{ft(6, 'Venture plan v1.1 and financial model (estimates); validation report section 4 (price checks and import price comparison)')}</section>""")
    # 7 market
    S.append(f"""<section class="s"><p class="kick">First customers</p><h2>Start where the need is sharpest and someone can pay.</h2>
<div class="g2">
<div class="card"><b class="serif" style="font-size:24px;color:var(--spine)">Learn: exam-year families</b>
<p style="margin-top:8px">Parents in roughly the <b>top 10–20% of urban households</b>, already paying for tutoring, with a Class 8–10 child preparing for the SSC.</p>
<p><b>0.8–1.0 million</b> serviceable students (validation estimate).</p><p class="muted">The device is about 11% of a top-decile monthly income, against about 33% of an average urban one (HIES 2022, estimate).</p></div>
<div class="card"><b class="serif" style="font-size:24px;color:var(--spine)">Access: programmes and sponsors</b>
<p style="margin-top:8px">About <b>35,000–40,000 blind children</b>, reached through the government's integrated programme: <b>76 centres in 64 districts</b> and 12 special schools.</p>
<p>Bank CSR gave <b>Tk 64 crore</b> to education in Jul–Dec 2025.</p><p class="muted">No Bangladeshi sponsor has yet funded a print-reading device. We would be the first.</p></div></div>
{ft(7, 'Validation report and positioning inputs: WHO 2017; Hussain et al. 2019; Prothom Alo, Jul 2025; Financial Express; HIES 2022')}</section>""")
    # 8 evidence
    S.append(f"""<section class="s dark"><p class="kick">The evidence, honestly</p><h2>Change, then test. Don't tool hardware yet.</h2>
<p style="font-size:21px;color:#D4E2E2;max-width:1060px">Our own desk validation (about 390 dated sources) found a real need and unproven hard parts. So the launch promise is narrow: <b>your own textbook, read from verified text, explained and quizzed.</b> Three cheap tests come before any pilot money.</p>
<div class="g3" style="margin-top:16px">
<div class="card"><b class="mg">1 · The phone test</b><p style="margin-top:6px">10 students try SenseBook and a phone with free AI on the same stand.</p><p class="muted">Pass: ≥60% keep SenseBook; ≥30% of parents place a deposit. ~Tk 40,000, 2 weeks.</p></div>
<div class="card"><b class="mg">2 · The Bangla reading test</b><p style="margin-top:6px">30 pages at the real camera view; voices; children's spoken questions.</p><p class="muted">Pass: ≤2% character error, ≤1 invented word per 1,000. ~Tk 5,000–10,000.</p></div>
<div class="card"><b class="mg">3 · Blind readers and sponsors</b><p style="margin-top:6px">8 blind and low-vision readers attach it and read alone; 10 funders asked.</p><p class="muted">Pass: ≥80% in ≤15 s; ≥2 letters of intent. ~Tk 20,000, 4–6 weeks.</p></div></div>
<p class="src" style="margin-top:14px">Also fixed first: the AI provider must allow use by under-18s; NCTB permission for textbook content; the 2026 data law's guardian consent. Costs are estimates.</p>
{ft(8, 'docs/validation/SenseBook_Validation_Report.pdf (27 Nov 2026)')}</section>""")
    # 9 roadmap and ask
    S.append(f"""<section class="s"><p class="kick">Roadmap and ask</p><h2>Prove it cheaply, then build.</h2>
<div class="g4" style="margin-bottom:22px">
<div class="card" style="border-top:8px solid var(--marigold)"><b>Now · Dec 2026–Jan 2027</b><p class="muted" style="margin-top:6px">The three tests; prototypes on the founders' Tk 10 lakh.</p></div>
<div class="card" style="border-top:8px solid var(--teal)"><b>Prove · to May 2027</b><p class="muted" style="margin-top:6px">Co-design with blind readers; home trials; tri-grip bench test on 30 books.</p></div>
<div class="card" style="border-top:8px solid var(--teal)"><b>Pilot · Jun–Nov 2027</b><p class="muted" style="margin-top:6px">100 units with an independent learning study.</p></div>
<div class="card" style="border-top:8px solid var(--teal)"><b>Launch · from Dec 2027</b><p class="muted" style="margin-top:6px">Personal, Commons, Access Fund, if the gates pass.</p></div></div>
<div class="g2"><div><b class="serif" style="font-size:24px;color:var(--spine)">What we ask for now</b>
<p style="margin-top:8px">1. <b>Partners</b> for the three tests: schools, blind-reader organisations, 10 families.<br>2. <b>Two letters of intent</b> from sponsors for 20+ Access units.<br>3. <b>Tk 5–10 lakh non-dilutive</b> for prototypes and tests.</p></div>
<div><b class="serif" style="font-size:24px;color:var(--spine)">Funding targets (to confirm)</b>
<p class="muted" style="margin-top:8px">Now: ICT Division startup grant (Tk 3–10 lakh at prototype stage), iDEA, the EATL pitch contest, a partnership with a2i. With prototype data: UNICEF Venture Fund, FID. Then: CSR deployments and impact investors.</p></div></div>
{ft(9, 'Plan dates; each stage waits for the one before. Grant ranges: ICT Division policy 2026 via validation report. Targets are leads, not commitments.')}</section>""")
    # 10 team and commitments
    S.append(f"""<section class="s dark"><div style="position:absolute;left:72px;top:56px">{lock(C['paper'], C['marigold'], 30, word=C['paper'])}</div>
<div class="g2" style="margin-top:110px;gap:48px"><div><p class="kick">Team</p>
<p><b>Founders:</b> business and partnerships; hardware; AI and software.</p>
<p><b>Recruiting:</b> an accessibility lead, ideally blind or low-vision; a curriculum lead (experienced NCTB teacher); an industrial designer.</p>
<p class="kick" style="margin-top:26px">Commitments</p>
<p>Open source: Apache-2.0, CERN-OHL-W, CC BY 4.0. No ads, no selling data. A no-bricking promise: the offline core keeps working if our servers stop.</p></div>
<div><p class="kick">SenseBook Impact Report, every year</p>
<p>Only what we measured, independently wherever possible:</p>
<p class="muted">learning gains on independent pre/post tests · retention weeks later · blind readers reading independently · learners and hours per shared device · lifetime cost per learner · local engineering jobs</p>
<p style="margin-top:30px;font-family:Literata,serif;font-size:30px;line-height:1.2">Knowledge belongs to everyone.<br><span class="mg">Understanding should too.</span></p></div></div>
<div class="ft"><span>{HUB} · {REPO}</span><span>SenseBook · 10 / 10</span></div></section>""")
    return S


ONE_CSS = BASE + """
@page{size:210mm 297mm;margin:0}
.pg{width:210mm;height:297mm;padding:13mm 14mm 11mm;background:var(--paper);font-size:10.6pt;line-height:1.42;position:relative;overflow:hidden}
.pg h2{font-size:14pt;color:var(--spine);margin:0 0 2mm} .card{padding:4mm 4.5mm;border-radius:3mm}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:4mm} .g3{display:grid;grid-template-columns:repeat(3,1fr);gap:3.5mm}
.stat{font-family:Literata,serif;font-weight:600;font-size:21pt;line-height:1;color:var(--spine)}
.hdr{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:.4mm solid var(--spine);padding-bottom:3mm;margin-bottom:4mm}
.ftr{position:absolute;left:14mm;right:14mm;bottom:7mm;font-size:7.5pt;color:#5D686A}
"""


def one_pager():
    return f"""<section class="pg"><div class="hdr"><div>{lock(size=30)}</div><div style="text-align:right"><div class="serif" style="font-size:15pt;color:var(--spine)">Knowledge, now conversational.</div><div class="bns" style="color:var(--teal);font-size:12pt">বই এখন কথা বলে</div></div></div>
<div class="g2" style="grid-template-columns:1.25fr 1fr;align-items:center;margin-bottom:4mm"><div>
<p style="font-size:12.5pt;margin:0 0 2mm"><b>SenseBook is personal learning technology:</b> a small, screen-free companion that clips onto a printed book. Turn the page of your own textbook: it reads it aloud, explains the hard parts and quizzes you on it, in Bangla and English, hands-free. A blind student and a university student use exactly the same SenseBook.</p>
<p class="muted" style="margin:0">Prototype stage, 27 November 2026. Figures are plan estimates unless a source is given.</p></div>
<div class="card" style="padding:2mm">{ill()}</div></div>
<h2>The problem: access to understanding is unequal</h2>
<div class="g3" style="margin-bottom:4mm">
<div class="card"><div class="stat">49.8%</div>of children aged 7–14 lack foundational reading; 60.8% lack numeracy <span class="src">(MICS 2025)</span></div>
<div class="card"><div class="stat">76.5%</div>of secondary students rely on tutors or coaching <span class="src">(Education Watch 2023)</span></div>
<div class="card"><div class="stat">8 of 14</div>blind users needed sighted help to aim a phone camera <span class="src">(CHI 2025)</span></div></div>
<div class="g2" style="margin-bottom:4mm">
<div><h2>Why not the phone?</h2><p>The phone is the real rival: 75.1% of households own one (BBS 2026). SenseBook wins where the phone can't: no screen in the child's hands, nothing to aim, hands-free page following, the student's own textbook from verified text even offline, and every control by touch. We don't claim better AI.</p></div>
<div><h2>One product, three routes</h2><p><b>Personal:</b> families buy (device Tk 14,990, to be tested; subscription Tk 399 a month).<br><b>Commons:</b> schools and libraries share devices.<br><b>Access Fund:</b> CSR, foundations and NGOs fund device, training and service (plan Tk 16,990 a reader). Same device for everyone.</p></div></div>
<div class="card" style="background:var(--spine);color:var(--paper);margin-bottom:4mm"><b class="mg">Evidence so far: "Change, then test. Don't tool hardware yet."</b> Our desk validation (about 390 sources) found a real need and unproven hard parts. Three cheap tests come next: <b>the phone test</b> (do families prefer it and pay a deposit?), <b>the Bangla reading test</b> (accuracy at the real camera view), and <b>the blind-reader and sponsor test</b> (attach and read alone; two letters of intent).</div>
<div class="g2"><div><h2>Roadmap</h2><p><b>Now:</b> the three tests. <b>To May 2027:</b> co-design and home trials. <b>Jun–Nov 2027:</b> 100-unit pilot with an independent learning study. <b>From Dec 2027:</b> launch, if the gates pass. Every year: a SenseBook Impact Report with only measured results.</p></div>
<div><h2>What we ask for now</h2><p>Partners for the tests (schools, blind-reader organisations, 10 families); two sponsor letters of intent for 20+ units; Tk 5–10 lakh non-dilutive for prototypes and tests.</p></div></div>
<div class="ftr">Open source: Apache-2.0 · CERN-OHL-W-2.0 · CC BY 4.0 · {HUB} · {REPO} · Sources: Dhaka Tribune (MICS 2025); The Daily Star (Education Watch 2023; BBS 2026); arXiv 2502.16098; SenseBook validation report, 27 Nov 2026.</div></section>"""


def main():
    os.makedirs(OUT, exist_ok=True)
    deck = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SenseBook pitch deck</title><style>{DECK_CSS}</style></head><body>{"".join(slides())}</body></html>'
    one = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SenseBook one-page summary</title><style>{ONE_CSS}</style></head><body>{one_pager()}</body></html>'
    for name, htmltext in (("SenseBook_Pitch_Deck", deck), ("SenseBook_One_Pager", one)):
        hp = os.path.join(OUT, name + ".html")
        with open(hp, "w", encoding="utf-8") as f:
            f.write(htmltext)
        pdf = render.pdf(hp, os.path.join(OUT, name + ".pdf"))
        previews(pdf, os.path.join(OUT, "preview", name), width=1280 if "Deck" in name else 1100, sheet_cols=3 if "Deck" in name else 1)
    print("pitch files written to", OUT)


if __name__ == "__main__":
    main()
