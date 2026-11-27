"""Build the SenseBook hub site into ./site: the venture's landing page and the home of every document.

It copies only finished deliverables (PDF, DOCX, XLSX, renders, figures, brand files, CAD exports, the 3D viewer)
and converts the Markdown documents to HTML pages. No source code, keys, data, notes or scripts are copied.
Standard library only. Run from the repository root:  python -I tools/build_site.py
Code: Apache-2.0. Site content: CC BY 4.0.
"""
import base64, html, json, os, re, shutil, zipfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
REPO = "https://github.com/916914/sensebook"
BUILT = f"{date.today():%d %b %Y}"

# Markdown documents rendered as pages: (slug, title, source, group, description)
PAGES = [
    ("positioning", "Positioning", "brand/POSITIONING.md", "Brand", "Who it's for, the problem, the category, the promise, sources, and the claims we never make."),
    ("brand", "Brand direction", "brand/BRAND.md", "Brand", "Story, personality, voice in English and Bangla, logo, colour, type, sound and touch."),
    ("name-check", "Name check", "brand/NAME_CHECK.md", "Brand", "Trademark and domain search for “SenseBook”, and the decision."),
    ("validation", "Validation report", "docs/validation/SenseBook_Validation_Report.md", "Evidence", "Does the plan hold up? Desk validation with about 390 dated sources."),
    ("validation/claims", "Claims and assumptions", "docs/validation/Claims_and_Assumptions.md", "Evidence", "Every claim the plan rests on, with a verdict."),
    ("validation/positioning-inputs", "Positioning inputs", "docs/validation/positioning-inputs.md", "Evidence", "What the evidence lets the brand say."),
    ("validation/kit", "Validation kit", "docs/validation/kit/README.md", "Evidence", "Interview guides, survey, one-week trial and go/change/stop thresholds."),
    ("validation/kit/students", "Interview guide: students", "docs/validation/kit/01_Interview_Students.md", "Kit", ""),
    ("validation/kit/blind-low-vision", "Interview guide: blind and low-vision readers", "docs/validation/kit/02_Interview_Blind_LowVision.md", "Kit", ""),
    ("validation/kit/parents", "Interview guide: parents", "docs/validation/kit/03_Interview_Parents.md", "Kit", ""),
    ("validation/kit/teachers-orgs", "Interview guide: teachers, schools and organisations", "docs/validation/kit/04_Interview_Teachers_Schools_Orgs.md", "Kit", ""),
    ("validation/kit/survey", "Parent survey", "docs/validation/kit/05_Survey.md", "Kit", ""),
    ("validation/kit/trial", "One-week trial and bench tests", "docs/validation/kit/06_One_Week_Trial.md", "Kit", ""),
    ("validation/kit/thresholds", "Go, change, stop thresholds", "docs/validation/kit/07_Go_Change_Stop_Thresholds.md", "Kit", ""),
    ("attachment-plan", "Tri-grip attachment plan", "design/SenseBook_Attachment_Plan.md", "Design", "How it holds any book: two blades and a rear leg."),
    ("industrial-design", "Industrial design", "design/SenseBook_Industrial_Design.md", "Design", "Form, dimensions and materials."),
    ("image-prompts", "Image prompts", "design/Image_Prompts.md", "Design", "Prompts for concept images (always labelled as concepts)."),
    ("prototype-hardware", "Prototype hardware", "prototype/hardware/README.md", "Prototype", "The hardware kit for the prototype."),
    ("prototype-bom", "Prototype bill of materials", "prototype/hardware/Prototype_BOM.md", "Prototype", "Parts and prices for the prototype."),
    ("pinmap", "Pin map", "prototype/hardware/pinmap.md", "Prototype", ""),
    ("assembly-guide", "Assembly guide", "prototype/hardware/Assembly_Guide.md", "Prototype", ""),
    ("test-checklist", "Test checklist", "prototype/hardware/Test_Checklist.md", "Prototype", ""),
    ("software", "Prototype software", "prototype/software/README.md", "Prototype", "Page following, faithful read-aloud, Ask, Chapter Talk, quizzes, memory and reminders."),
    ("software-architecture", "Software architecture", "prototype/software/docs/ARCHITECTURE.md", "Prototype", ""),
    ("software-audio", "Software: audio", "prototype/software/docs/AUDIO.md", "Prototype", ""),
]
SRC_TO_SLUG = {src: slug for slug, _, src, _, _ in PAGES}

FILES = [  # (title, description, group, [(label, repo path)])
    ("Venture plan", "Strategy, go-to-market, pricing, unit economics, sourcing, roadmap, funding, risks.", "Venture",
     [("PDF", "docs/SenseBook_Venture_Plan.pdf"), ("Word", "docs/SenseBook_Venture_Plan.docx")]),
    ("Product specification", "Every feature, the controls, the hybrid AI design, accessibility and the release plan.", "Venture",
     [("PDF", "docs/SenseBook_Product_Spec.pdf"), ("Word", "docs/SenseBook_Product_Spec.docx")]),
    ("Pitch deck", "Ten slides: the story, the product, the evidence, the plan.", "Venture", [("PDF", "docs/pitch/SenseBook_Pitch_Deck.pdf")]),
    ("One-page summary", "SenseBook on one page.", "Venture", [("PDF", "docs/pitch/SenseBook_One_Pager.pdf")]),
    ("Financial model", "Formula-driven: change the blue cells and everything recalculates. Planning estimates.", "Venture",
     [("Excel", "finance/SenseBook_Financial_Model.xlsx")]),
    ("Validation report", "The designed report: verdict, evidence, numbers check, risks, recommendations.", "Evidence",
     [("PDF", "docs/validation/SenseBook_Validation_Report.pdf")]),
    ("Brand guide", "20 pages, visual: story, voice, logo, colour, type, icons, sound, touch, packaging.", "Brand",
     [("PDF", "brand/guide/SenseBook_Brand_Guide.pdf")]),
]

CSS = r"""
@font-face{font-family:Literata;src:url(/fonts/literata-latin-600-normal.woff2) format("woff2");font-weight:600;font-display:swap}
@font-face{font-family:Literata;src:url(/fonts/literata-latin-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Atkinson Hyperlegible Next";src:url(/fonts/atkinson-hyperlegible-next-latin-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Atkinson Hyperlegible Next";src:url(/fonts/atkinson-hyperlegible-next-latin-700-normal.woff2) format("woff2");font-weight:700;font-display:swap}
@font-face{font-family:"Noto Sans Bengali";src:url(/fonts/noto-sans-bengali-bengali-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Noto Sans Bengali";src:url(/fonts/noto-sans-bengali-bengali-700-normal.woff2) format("woff2");font-weight:700;font-display:swap}
@font-face{font-family:"Noto Serif Bengali";src:url(/fonts/noto-serif-bengali-bengali-600-normal.woff2) format("woff2");font-weight:600;font-display:swap}
:root{--bg:#F7F2E8;--surface:#FFFFFF;--surface2:#DCE9E8;--ink:#161B1C;--muted:#4D5A5C;--line:#DDD5C6;--spine:#133B42;--teal:#1F5560;
--link:#1F5560;--marigold:#E8A317;--on-dark:#F7F2E8;--brick:#A63D2A;--leaf:#2E6B4A;color-scheme:light;
--sans:"Atkinson Hyperlegible Next","Noto Sans Bengali","Nirmala UI",system-ui,sans-serif;--serif:Literata,"Noto Serif Bengali","Noto Sans Bengali",Georgia,serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0D2428;--surface:#133B42;--surface2:#173F46;--ink:#F2EEE5;--muted:#B5C7C8;
--line:#26535A;--link:#9FD3D9;--teal:#9FD3D9;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0D2428;--surface:#133B42;--surface2:#173F46;--ink:#F2EEE5;--muted:#B5C7C8;--line:#26535A;--link:#9FD3D9;--teal:#9FD3D9;color-scheme:dark}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:18px/1.55 var(--sans)}
:lang(bn){font-family:"Noto Sans Bengali",var(--sans);line-height:1.7}
.wrap{max-width:1120px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}
a{color:var(--link);text-underline-offset:.18em}a:focus-visible,button:focus-visible{outline:3px solid var(--marigold);outline-offset:3px;border-radius:4px}
.skip{position:absolute;left:-999px;top:8px;background:var(--marigold);color:#161B1C;padding:8px 14px;border-radius:6px;z-index:9}.skip:focus{left:12px}
header.top{border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;gap:14px 24px;flex-wrap:wrap;padding-block:14px}
header.top .logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--spine)}
header.top .logo img{height:34px;width:auto;display:block}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) header.top .logo img.l{display:none}}
@media (prefers-color-scheme:light){header.top .logo img.d{display:none}}
:root[data-theme="dark"] header.top .logo img.l{display:none}:root[data-theme="light"] header.top .logo img.d{display:none}
nav.main{display:flex;gap:4px 18px;flex-wrap:wrap;margin-left:auto;font-size:16px}nav.main a{text-decoration:none;color:var(--ink)}nav.main a:hover{text-decoration:underline}
h1,h2,h3{font-family:var(--serif);font-weight:600;letter-spacing:-.005em;text-wrap:balance}
h1{font-size:clamp(34px,5.4vw,60px);line-height:1.06;margin:0 0 14px;color:var(--spine)}
h2{font-size:clamp(26px,3.4vw,38px);line-height:1.12;margin:0 0 12px;color:var(--spine)}
h3{font-size:21px;line-height:1.25;margin:0 0 6px;color:var(--spine)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) :is(h1,h2,h3){color:var(--ink)}}
:root[data-theme="dark"] :is(h1,h2,h3){color:var(--ink)}
section{padding-block:56px}section+section{border-top:1px solid var(--line)}
.kick{font-size:14px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--teal);margin:0 0 10px}
.lead{font-size:clamp(19px,2.1vw,23px);line-height:1.45;color:var(--muted);max-width:44em;margin:0 0 18px}
.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:32px;align-items:center;padding-block:44px 56px}
.hero .bn{font-family:"Noto Serif Bengali",var(--serif);font-size:clamp(22px,2.8vw,30px);color:var(--teal);margin:0 0 18px;line-height:1.5}
.hero figure{margin:0}.hero img{width:100%;height:auto;display:block}
.hero>*{min-width:0}.chip{display:inline-flex;gap:8px;align-items:center;font-size:15px;background:var(--surface2);color:var(--ink);padding:6px 12px;border-radius:99px;margin:0 0 16px}
.chip::before{content:"";width:9px;height:9px;border-radius:50%;background:var(--marigold);flex:none}
.btns{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-block;padding:12px 20px;border-radius:10px;font-weight:700;text-decoration:none;background:var(--spine);color:var(--on-dark)}
.btn.alt{background:transparent;color:var(--link);box-shadow:inset 0 0 0 2px var(--link)}
.band{background:var(--spine);color:var(--on-dark)}.band h2,.band h3{color:var(--on-dark)!important}.band .kick{color:var(--marigold)}.band .lead{color:#CFDEDF}.band a{color:#FFE2A0}
.band .big{font-family:var(--serif);font-weight:600;font-size:clamp(30px,4.6vw,52px);line-height:1.08;margin:0 0 10px;text-wrap:balance}
.band .bn{font-family:"Noto Serif Bengali",var(--serif);color:var(--marigold);font-size:clamp(20px,2.6vw,28px);margin:0 0 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:16px}
.grid.two{grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr))}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px;min-width:0}
.band .card{background:#1A4952;border-color:#2B5D66}
.card p{margin:0 0 10px;color:var(--muted)}.band .card p{color:#D4E2E2}.card p:last-child{margin-bottom:0}
.card .ico{width:36px;height:36px;margin-bottom:10px;display:block}
.step{counter-increment:s}.steps{counter-reset:s}.step h3::before{content:counter(s) ". ";color:var(--marigold)}
.tag{display:inline-block;font-size:13px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;color:var(--teal);margin-bottom:6px}
.stat{font-family:var(--serif);font-weight:600;font-size:clamp(34px,4vw,46px);line-height:1;color:var(--spine);margin:0 0 6px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .stat{color:var(--marigold)}}:root[data-theme="dark"] .stat{color:var(--marigold)}
.src{font-size:14px;color:var(--muted)}
.verdict{border-left:6px solid var(--marigold);background:var(--surface);padding:18px 22px;border-radius:0 14px 14px 0;margin:0 0 22px}
.verdict b{font-family:var(--serif);font-size:24px;color:var(--spine)}
.road{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;counter-reset:r}
.road .card{border-top:6px solid var(--teal)}.road .card.now{border-top-color:var(--marigold)}
.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr));gap:14px}
.gallery figure{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.gallery img{width:100%;height:auto;display:block}.gallery figcaption{padding:8px 12px;font-size:15px;color:var(--muted)}
.links a{display:inline-block;margin:0 14px 4px 0;font-weight:700}
.files h3{font-family:var(--sans);font-size:18px;font-weight:700}
article{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:clamp(18px,3vw,36px);min-width:0;max-width:900px}
article h1{font-size:clamp(30px,4vw,42px)}article h2{font-size:clamp(23px,2.6vw,30px);margin-top:36px}article h3{margin-top:26px}
article img{max-width:100%;height:auto;border-radius:8px;background:#fff}
.table-wrap{overflow-x:auto;margin:14px 0}table{border-collapse:collapse;width:100%;font-size:16px}
th,td{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}th{font-size:14px;letter-spacing:.04em;text-transform:uppercase;color:var(--teal)}
code,pre{font-family:ui-monospace,Consolas,monospace;font-size:15px}pre{background:var(--surface2);padding:14px;border-radius:10px;overflow-x:auto}
blockquote{margin:16px 0;padding:10px 18px;border-left:5px solid var(--marigold);background:var(--surface2);border-radius:0 10px 10px 0}
.crumbs{font-size:16px;margin:26px 0 16px}
footer{border-top:1px solid var(--line);padding-block:28px 40px;font-size:15px;color:var(--muted)}
footer .wrap{display:grid;gap:8px}
.sound{display:flex;gap:14px;align-items:center;flex-wrap:wrap}.sound audio{max-width:100%}
@media (max-width:820px){.hero{grid-template-columns:1fr}.hero figure{max-width:460px}section{padding-block:40px}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""


def esc(s):
    return html.escape(s, quote=True)


def page(title, body, desc="SenseBook: personal learning technology. A screen-free companion that reads, explains and quizzes, on the printed page.", lang="en"):
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:image" content="/img/og.png">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml"><style>{CSS}</style></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="logo" href="/" aria-label="SenseBook home"><img class="l" src="/img/lockup.svg" alt="SenseBook"><img class="d" src="/img/lockup-reversed.svg" alt="SenseBook"></a>
<nav class="main" aria-label="Main"><a href="/#how">How it works</a><a href="/#who">Who it's for</a><a href="/#product">Product</a><a href="/#evidence">Evidence</a><a href="/#roadmap">Roadmap</a><a href="/#documents">Documents</a></nav></div></header>
<main id="main">{body}</main>
<footer><div class="wrap"><div><b>Prototype and plan.</b> Nothing here is a finished or certified product. Figures are planning estimates unless a source is given; nothing has been tested with users yet.</div>
<div>Open source: software Apache-2.0 · hardware CERN-OHL-W-2.0 · documents, images and data CC BY 4.0 · <a href="{REPO}">GitHub</a> · built {BUILT}</div></div></footer></body></html>"""


# ------------------------------------------------------------------------------------------ markdown
def slugify(s):
    s = re.sub(r"<[^>]+>", "", s).strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s+", "-", s)


class Converter:
    def __init__(self, src_rel):
        self.src = src_rel
        self.dir = os.path.dirname(src_rel)

    def link(self, href, image=False):
        if href.startswith(("http://", "https://", "mailto:", "#", "/")):
            return href
        path, _, frag = href.partition("#")
        rel = os.path.normpath(os.path.join(self.dir, path)).replace("\\", "/")
        if image or rel.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp")):
            return copy(rel, "assets/" + rel) or f"{REPO}/blob/main/{rel}"
        if rel in SRC_TO_SLUG and os.path.isfile(os.path.join(ROOT, rel)):
            return f"/{SRC_TO_SLUG[rel]}/" + (f"#{frag}" if frag else "")
        if rel.lower().endswith((".pdf", ".docx", ".xlsx", ".csv", ".zip")) and os.path.isfile(os.path.join(ROOT, rel)):
            return copy(rel) or f"{REPO}/blob/main/{rel}"
        kind = "tree" if not os.path.splitext(rel)[1] else "blob"
        return f"{REPO}/{kind}/main/{rel}" + (f"#{frag}" if frag else "")

    def inline(self, s):
        s = html.escape(s, quote=False)
        s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", lambda m: f'<img alt="{m.group(1)}" src="{self.link(html.unescape(m.group(2)), True)}" loading="lazy">', s)
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{self.link(html.unescape(m.group(2)))}">{m.group(1)}</a>', s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![*\w])\*([^*\s][^*]*)\*(?!\w)", r"<em>\1</em>", s)
        s = re.sub(r"(?<![\w>\"=/])(https?://[^\s<)]+[^\s<).,;:])", r'<a href="\1">\1</a>', s)
        return s

    def convert(self, md):
        out, lines, i, para = [], md.replace("\r\n", "\n").split("\n"), 0, []

        def flush():
            if para:
                out.append("<p>" + self.inline(" ".join(para)) + "</p>")
                para.clear()

        while i < len(lines):
            line = lines[i]
            if line.startswith("```"):
                flush(); i += 1; code = []
                while i < len(lines) and not lines[i].startswith("```"):
                    code.append(lines[i]); i += 1
                out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>"); i += 1; continue
            m = re.match(r"^(#{1,4})\s+(.*)", line)
            if m:
                flush(); lvl = len(m.group(1)); txt = self.inline(m.group(2))
                out.append(f'<h{lvl} id="{slugify(m.group(2))}">{txt}</h{lvl}>'); i += 1; continue
            if line.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
                flush(); rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    rows.append([c.strip() for c in re.split(r"(?<!\\)\|", lines[i].strip().strip("|"))]); i += 1
                head, body = rows[0], rows[2:]
                t = '<div class="table-wrap"><table><thead><tr>' + "".join(f"<th>{self.inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                t += "".join("<tr>" + "".join(f"<td>{self.inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>"
                out.append(t); continue
            if re.match(r"^\s*([-*]|\d+\.)\s+", line):
                flush(); ordered = bool(re.match(r"^\s*\d+\.", line)); tag = "ol" if ordered else "ul"; items = []
                while i < len(lines) and (re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]) or (lines[i].startswith("   ") and lines[i].strip() and items)):
                    if re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                        depth = len(lines[i]) - len(lines[i].lstrip())
                        items.append([depth, re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])])
                    else:
                        items[-1][1] += " " + lines[i].strip()
                    i += 1
                html_items, base = [], items[0][0]
                for depth, txt in items:
                    pre = '<li style="margin-left:1.4em;list-style-type:circle">' if depth > base else "<li>"
                    html_items.append(pre + self.inline(txt) + "</li>")
                out.append(f"<{tag}>" + "".join(html_items) + f"</{tag}>"); continue
            if line.startswith(">"):
                flush(); quote = []
                while i < len(lines) and lines[i].startswith(">"):
                    q = lines[i][1:]
                    quote.append(q[1:] if q.startswith(" ") else q); i += 1
                out.append("<blockquote>" + self.convert("\n".join(quote)) + "</blockquote>"); continue
            if re.match(r"^\s*-{3,}\s*$", line):
                flush(); out.append("<hr>"); i += 1; continue
            if not line.strip():
                flush(); i += 1; continue
            para.append(line.strip()); i += 1
        flush()
        return "\n".join(out)


def copy(rel, dest_rel=None):
    src = os.path.join(ROOT, rel)
    if not os.path.isfile(src):
        return None
    dest = os.path.join(OUT, dest_rel or rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)
    return "/" + (dest_rel or rel).replace("\\", "/")


def tracked(prefix):
    """Files under `prefix` that are committed to git, so uncommitted work in progress is never published.
    Returns None if git isn't available (then everything on disk is used)."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT, "ls-files", "--", prefix], capture_output=True, text=True, check=True)
        return {line.strip() for line in r.stdout.splitlines() if line.strip()}
    except (OSError, subprocess.CalledProcessError):
        return None


def read(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        return ""
    with open(p, encoding="utf-8") as f:
        return f.read()


def icon(name):
    s = read(f"brand/icons/{name}.svg")
    return s.replace("<svg ", '<svg class="ico" aria-hidden="true" ', 1) if s else ""


# ------------------------------------------------------------------------------------------ landing page
def landing(have):
    renders = have["renders"]
    hero_img = "/img/sensebook-on-book.svg"
    hero_cap = "Illustration of SenseBook on a textbook spread (not a photo)"
    viewer = '<a class="btn" href="/viewer/">Open the 3D model</a>' if have["viewer"] else ""
    gallery = ""
    if renders:
        gallery = '<div class="gallery" style="margin-top:18px">' + "".join(
            f'<figure><a href="{u}"><img src="{u}" alt="SenseBook render: {esc(c)}" loading="lazy"></a><figcaption>Render: {esc(c)}</figcaption></figure>'
            for u, c in zip(renders, have["render_caps"])) + "</div>"
    lives = [("The Class 9 student", "Studying physics at 10 pm with no tutor for every subject. She turns the page; SenseBook reads, explains and quizzes her."),
             ("The blind student", "The same textbook as her classmates, on the same SenseBook. Nothing to aim; everything by touch and sound."),
             ("The university student", "A hard chapter he wants to talk through, without switching between five tabs."),
             ("The lifelong learner", "Out of school and still curious: economics, English, the manual for a new machine.")]
    steps = [("tri-grip", "Clip it on", "Two thin blades slide inside the covers and a third leg rests on the spine. Nothing touches the pages.", "বইয়ের মাথায় আটকে দাও"),
             ("page-turn", "Turn the page", "It sees the whole spread, waits for the page to settle, and carries on. No buttons.", "পাতা ওল্টাও"),
             ("read", "Listen", "The reader voice reads the page exactly as printed, from verified text for your textbook.", "শোনো"),
             ("ask", "Ask and practise", "Hold Ask: after a bell, the explainer voice helps. Then it quizzes you and reminds you when to revise.", "প্রশ্ন করো, পড়া দাও")]
    body = f"""
<div class="wrap hero">
 <div><p class="chip">Prototype · desk-validated · not yet tested with users</p>
 <p class="kick">Personal learning technology</p>
 <h1>Never get stuck learning alone again.</h1>
 <p class="bn" lang="bn">পড়তে গিয়ে আর একা আটকে থাকতে হবে না।</p>
 <p class="lead">SenseBook is a small, screen-free companion that clips onto a printed book. Turn the page of your own textbook: it reads it aloud, explains the hard parts and quizzes you on it, in Bangla and English, hands-free.</p>
 <div class="btns"><a class="btn" href="#documents">Read the plan</a><a class="btn alt" href="#evidence">See the evidence</a></div></div>
 <figure><img src="{hero_img}" alt="SenseBook, a small slate-teal unit on a short stick, gripping the top of an open textbook at the spine"><figcaption class="src">{hero_cap}</figcaption></figure>
</div>
<section class="band"><div class="wrap"><p class="kick">Why we exist</p>
 <p class="big">Knowledge belongs to everyone.<br>Understanding should too.</p><p class="bn" lang="bn">জ্ঞান সবার। বোঝার সুযোগও সবার।</p>
 <div class="grid two"><p class="lead">Two students can read the same textbook and get two different educations. One can ask a tutor whenever something is hard. The other is alone with the page. For a blind reader, even reaching the printed words is a barrier.</p>
 <p class="lead">The knowledge is the same; the chance to understand it is not. In Bangladesh, <b>49.8%</b> of children aged 7–14 could not show foundational reading skills and <b>60.8%</b> foundational numeracy (MICS 2025), and <b>76.5%</b> of secondary students rely on tutors or coaching (Education Watch 2023). SenseBook exists to give every reader someone to learn with.</p></div>
 <p class="src" style="color:#B9CDCE">Sources: <a href="https://www.dhakatribune.com/bangladesh/education/419986/in-school-but-failing-to-learn">MICS 2025 via Dhaka Tribune</a> · <a href="https://www.thedailystar.net/node/3578376">Education Watch 2023 via The Daily Star</a></p></div></section>
<section id="how"><div class="wrap"><p class="kick">How it works</p><h2>The book stays the screen.</h2>
 <p class="lead">No phone in the hands, nothing to aim. The reader voice reads the book; the explainer voice, always after a bell, helps. You always know which is which.</p>
 <div class="grid steps">{''.join(f'<div class="card step">{icon(i)}<h3>{t}</h3><p>{d}</p><p lang="bn" class="src">{b}</p></div>' for i, t, d, b in steps)}</div></div></section>
<section id="who"><div class="wrap"><p class="kick">Who it's for</p><h2>One product. Different lives.</h2>
 <p class="lead">Every reader gets the same SenseBook, with the same design, features and intelligence. Accessibility is built in, like a kerb ramp that helps everyone, never a separate edition.</p>
 <div class="grid">{''.join(f'<div class="card"><h3>{a}</h3><p>{b}</p></div>' for a, b in lives)}</div>
 <p class="src" style="margin-top:12px">Illustrative people, not customers or testimonials. We start with Class 8–10 students preparing for the SSC, and with blind and low-vision students.</p></div></section>
<section><div class="wrap"><p class="kick">Three ways to reach a reader</p><h2>Owned, shared, funded. Always the same SenseBook.</h2>
 <div class="grid">
 <div class="card">{icon('read')}<h3>SenseBook Personal</h3><p>Your own SenseBook. For readers and families.</p><p class="src">Planned launch price Tk 14,990, to be tested with deposits (Tk 9,990–14,990 range).</p></div>
 <div class="card">{icon('shared')}<h3>SenseBook Commons</h3><p>Shared SenseBooks in schools, libraries and learning centres, so learners who can't own one still get one to use.</p><p class="src">Institutions buy or lease. Not yet tested.</p></div>
 <div class="card">{icon('touch')}<h3>SenseBook Access Fund</h3><p>CSR teams, foundations and NGOs fund the device, training, maintenance and service for learners who need it, starting with blind and low-vision students.</p><p class="src">Plan figure Tk 16,990 per reader; no sponsor yet.</p></div></div></div></section>
<section id="product"><div class="wrap"><p class="kick">The product</p><h2>Webcam-sized, on a tri-grip.</h2>
 <div class="grid two" style="align-items:start"><div>
 <p class="lead">A small slate-teal unit on a short stick, centred on the spine. Two wafer-thin spring-steel blades slip inside the covers and a third leg presses on the back of the spine, so it moves with the book on a table or in the hands.</p>
 <div class="btns">{viewer}<a class="btn alt" href="/attachment-plan/">How the tri-grip works</a></div></div>
 <div class="card"><div class="table-wrap" style="margin:0"><table>
 <tr><th scope="row">Unit</th><td>About 8.5 × 3.8 × 3 cm; four status dots, one lens looking down at the pages</td></tr>
 <tr><th scope="row">Grip</th><td>Designed for books from a thin booklet to about 6 cm thick (to be bench-tested)</td></tr>
 <tr><th scope="row">Controls</th><td>Marigold Ask button with a raised dot; back, play, forward; mic-mute switch</td></tr>
 <tr><th scope="row">Audio</th><td>Speaker, wired headphones, Bluetooth earbuds</td></tr>
 <tr><th scope="row">Offline</th><td>Reads downloaded textbooks without internet; questions need internet</td></tr>
 <tr><th scope="row">Status</th><td>Targets from the spec. Prototype software runs on a laptop; hardware not yet built</td></tr></table></div></div></div>
 {gallery}</div></section>
<section id="evidence"><div class="wrap"><p class="kick">The evidence</p><h2>What holds, and what we still have to prove.</h2>
 <div class="verdict"><b>Change, then test. Don't tool hardware yet.</b><p style="margin:6px 0 0">The verdict of our own desk validation (27 Nov 2026, about 390 dated sources). The need is real; the hard parts are unproven. We have re-scoped the promise to the student's own textbook and set three cheap tests before any pilot money is spent.</p></div>
 <div class="grid">
 <div class="card"><p class="stat">76.5%</p><p>of secondary students had private tutors or coaching in 2023. The need for help at home is real.</p><p class="src">Education Watch 2023 (CAMPE)</p></div>
 <div class="card"><p class="stat">75.1%</p><p>of households have a smartphone. The free phone is the real rival, so SenseBook must win on no screen and no aiming.</p><p class="src">BBS ICT survey 2026</p></div>
 <div class="card"><p class="stat">8 of 14</p><p>blind users in a 2025 study needed sighted help to aim a phone camera. A fixed, hands-free camera removes the aiming.</p><p class="src">CHI 2025, arXiv 2502.16098</p></div>
 <div class="card"><p class="stat">74 dpi</p><p>at the reader's edge of a spread, against the 200–300 dpi text recognition normally uses. So we promise textbooks first; other print is in testing.</p><p class="src">SenseBook design analysis</p></div></div>
 <div class="btns" style="margin-top:20px"><a class="btn" href="/validation/">Read the validation report</a><a class="btn alt" href="/validation/claims/">Every claim and its verdict</a></div></div></section>
<section id="roadmap"><div class="wrap"><p class="kick">Roadmap</p><h2>Prove it cheaply, then build.</h2>
 <div class="road">
 <div class="card now"><span class="tag">Now · Dec 2026–Jan 2027</span><h3>Three tests</h3><p><b>Phone test:</b> do families prefer it to a phone on a stand, and pay a deposit? <b>Bangla reading test.</b> <b>Blind-reader and sponsor test.</b></p></div>
 <div class="card"><span class="tag">Prove · to May 2027</span><h3>Co-design and home trials</h3><p>Dev-kit prototypes with students and blind readers; the tri-grip bench test on 30 real books.</p></div>
 <div class="card"><span class="tag">Pilot · Jun–Nov 2027</span><h3>100 units</h3><p>Paying families and funded readers, with an independent learning study.</p></div>
 <div class="card"><span class="tag">Launch · from Dec 2027</span><h3>Personal, Commons, Access Fund</h3><p>Only if the pilot gates pass. Then the first SenseBook Impact Report.</p></div></div>
 <p class="src" style="margin-top:12px">Dates are the plan's, and each stage waits for the one before. Before any child uses a pilot, the AI provider must allow use by under-18s.</p></div></section>
<section class="band"><div class="wrap"><p class="kick">Open source</p><h2>Check how it works. Build your own.</h2>
 <div class="grid">
 <div class="card">{icon('open-source').replace('stroke="#133B42"', 'stroke="#F7F2E8"')}<h3>Software</h3><p>Python prototype: page following, faithful read-aloud, Ask, Chapter Talk, quizzes, memory and reminders. Apache-2.0.</p><p><a href="/software/">Read about it</a></p></div>
 <div class="card">{icon('tri-grip').replace('stroke="#133B42"', 'stroke="#F7F2E8"')}<h3>Hardware</h3><p>Tri-grip design, CAD and print files. CERN-OHL-W-2.0.</p><p><a href="#documents">Design files</a></p></div>
 <div class="card">{icon('read').replace('stroke="#133B42"', 'stroke="#F7F2E8"')}<h3>Documents and brand</h3><p>Plan, spec, model, validation and the whole brand. CC BY 4.0.</p><p><a href="{REPO}">The repository</a></p></div></div></div></section>
<section id="documents"><div class="wrap files"><p class="kick">Documents</p><h2>Everything, in one place.</h2>
 {have["docs_html"]}</div></section>"""
    return body


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    # fonts, brand images, favicon
    for f in sorted(os.listdir(os.path.join(ROOT, "brand", "type", "fonts"))):
        if f.endswith(".woff2"):
            copy(f"brand/type/fonts/{f}", f"fonts/{f}")
    copy("brand/logo/sensebook-lockup-en-colour.svg", "img/lockup.svg")
    copy("brand/logo/sensebook-lockup-en-reversed.svg", "img/lockup-reversed.svg")
    copy("brand/logo/favicon.svg", "img/favicon.svg")
    copy("brand/illustration/sensebook-on-book.svg", "img/sensebook-on-book.svg")
    copy("brand/site/og.png", "img/og.png")
    for d in ("logo", "icons"):
        for f in sorted(os.listdir(os.path.join(ROOT, "brand", d))):
            if f.endswith(".svg"):
                copy(f"brand/{d}/{f}", f"brand-files/{d}/{f}")

    # renders and 3D viewer from the build
    renders_dir = os.path.join(ROOT, "design", "renders")
    renders, caps = [], []
    ok_renders = tracked("design/renders")
    if os.path.isdir(renders_dir):
        for f in sorted(os.listdir(renders_dir)):
            if ok_renders is not None and f"design/renders/{f}" not in ok_renders:
                continue
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                renders.append(copy(f"design/renders/{f}", f"renders/{f}"))
                caps.append(os.path.splitext(f)[0].replace("_", " ").replace("-", " "))
    viewer = False
    vdir = os.path.join(ROOT, "design", "viewer")
    ok_viewer = tracked("design/viewer")
    if os.path.isfile(os.path.join(vdir, "index.html")) and (ok_viewer is None or "design/viewer/index.html" in ok_viewer):
        for d, _, fs in os.walk(vdir):
            for f in fs:
                if f.endswith((".py", ".pyc", ".md")) or f.startswith("."):
                    continue
                rel = os.path.relpath(os.path.join(d, f), ROOT).replace("\\", "/")
                if ok_viewer is not None and rel not in ok_viewer:
                    continue
                copy(rel, "viewer/" + os.path.relpath(os.path.join(d, f), vdir).replace("\\", "/"))
        viewer = True

    # Markdown pages
    made = {}
    for slug, title, src, group, desc in PAGES:
        md = read(src)
        if not md:
            continue
        art = Converter(src).convert(md)
        os.makedirs(os.path.join(OUT, slug), exist_ok=True)
        crumbs = f'<p class="crumbs"><a href="/">SenseBook</a> · <a href="/#documents">Documents</a> · {esc(title)} · <a href="{REPO}/blob/main/{src}">source</a></p>'
        with open(os.path.join(OUT, slug, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page(f"{title} · SenseBook", f'<div class="wrap">{crumbs}<article>{art}</article></div>', desc or title))
        made[slug] = (title, group, desc)

    # sounds page (WAVs inlined, because the publish step skips .wav files)
    sounds = json.loads(read("brand/audio/sounds.json") or "{}").get("sounds", [])
    if sounds:
        rows = ""
        for s in sounds:
            p = os.path.join(ROOT, "brand", "audio", s["file"])
            if os.path.isfile(p):
                b64 = base64.b64encode(open(p, "rb").read()).decode()
                rows += f'<div class="card sound"><div style="flex:1;min-width:220px"><h3>{esc(s["name"])}</h3><p>{esc(s["when"])}</p></div><audio controls preload="none" src="data:audio/wav;base64,{b64}" aria-label="{esc(s["name"])} sound"></audio></div>'
        os.makedirs(os.path.join(OUT, "brand", "sounds"), exist_ok=True)
        with open(os.path.join(OUT, "brand", "sounds", "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page("Sound identity · SenseBook", f'<div class="wrap"><p class="crumbs"><a href="/">SenseBook</a> · <a href="/brand/">Brand</a> · Sounds</p><h1>Sound identity</h1><p class="lead">First drafts, to be tested with blind and sighted listeners. Short, never melodies; the bell always comes before the explainer voice.</p><div class="grid" style="grid-template-columns:1fr">{rows}</div></div>'))
        made["brand/sounds"] = ("Sound identity", "Brand", "Listen to the startup, ready, page, explainer, reminder and error sounds.")

    # documents index
    groups = {}
    for title, desc, group, links in FILES:
        got = [(lab, copy(p)) for lab, p in links]
        got = [(lab, u) for lab, u in got if u]
        if got:
            links_html = " ".join('<a href="%s">%s</a>' % (u, lab) for lab, u in got)
            groups.setdefault(group, []).append(f'<div class="card"><h3>{esc(title)}</h3><p>{esc(desc)}</p><div class="links">{links_html}</div></div>')
    for slug, (title, group, desc) in made.items():
        if group == "Kit":
            continue
        groups.setdefault(group, []).append(f'<div class="card"><h3>{esc(title)}</h3>{f"<p>{esc(desc)}</p>" if desc else ""}<div class="links"><a href="/{slug}/">Open</a></div></div>')
    cad = os.path.join(ROOT, "design", "cad", "out")
    if os.path.isdir(cad) and any(f.lower().endswith((".stl", ".step", ".stp", ".dxf", ".3mf")) for f in os.listdir(cad)):
        zpath = os.path.join(OUT, "downloads", "SenseBook_CAD_files.zip")
        os.makedirs(os.path.dirname(zpath), exist_ok=True)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(os.listdir(cad)):
                if f.lower().endswith((".stl", ".step", ".stp", ".dxf", ".3mf")):
                    z.write(os.path.join(cad, f), f)
        groups.setdefault("Design", []).append('<div class="card"><h3>3D-print and CAD files</h3><p>STL for printing, STEP for editing, DXF patterns.</p><div class="links"><a href="/downloads/SenseBook_CAD_files.zip">Download ZIP</a></div></div>')
    if viewer:
        groups.setdefault("Design", []).insert(0, '<div class="card"><h3>3D model viewer</h3><p>Turn the SenseBook model around in your browser.</p><div class="links"><a href="/viewer/">Open</a></div></div>')
    for f in ("wiring_diagram.png", "wiring_diagram.svg"):
        u = copy(f"prototype/hardware/{f}", f"renders/{f}")
        if u:
            groups.setdefault("Prototype", []).append(f'<div class="card"><h3>Wiring diagram ({f.rsplit(".", 1)[1].upper()})</h3><div class="links"><a href="{u}">Open</a></div></div>')
    order = ["Venture", "Evidence", "Brand", "Design", "Prototype"]
    docs_html = "".join(f'<h3 style="margin:26px 0 10px;font-family:var(--serif);font-size:24px">{g}</h3><div class="grid">{"".join(groups[g])}</div>' for g in order if g in groups)

    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page("SenseBook · Knowledge, now conversational", landing({"renders": renders, "render_caps": caps, "viewer": viewer, "docs_html": docs_html})))
    with open(os.path.join(OUT, "robots.txt"), "w") as fh:
        fh.write("User-agent: *\nDisallow: /\n")
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    print(f"site built: {n} files, {size / 1e6:.1f} MB, {len(made)} pages, renders: {len(renders)}, viewer: {viewer} -> {OUT}")


if __name__ == "__main__":
    main()
