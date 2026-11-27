"""Build the private SenseBook hub site into D:\\Sensebook\\site (a clean folder that is safe to deploy).

It copies only finished deliverables (PDF, DOCX, XLSX, renders, wiring diagram, CAD exports, the 3D viewer page and
its GLB model) and converts the Markdown design and prototype documents to HTML pages. No source code, keys, data, notes or scripts are copied.
Standard library only. Run:  python -I tools/build_site.py   (from D:\\Sensebook)
"""
import html, os, re, shutil, sys, zipfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")

DOCS = [  # (title, description, file)
    ("Venture plan", "Strategy, go-to-market, pricing, unit economics, sourcing, prototyping, funding, risks, 90-day plan.", "docs/SenseBook_Venture_Plan"),
    ("Product specification", "Every feature, controls, hybrid AI design, accessibility, release plan.", "docs/SenseBook_Product_Spec"),
]
MODEL = ("Financial model", "Formula-driven: change the blue cells and everything recalculates.", "finance/SenseBook_Financial_Model.xlsx")
PAGES = [  # (slug, title, source markdown, group)
    ("attachment-plan", "Tri-grip attachment plan", "design/SenseBook_Attachment_Plan.md", "Design"),
    ("industrial-design", "Industrial design", "design/SenseBook_Industrial_Design.md", "Design"),
    ("image-prompts", "Image prompts", "design/Image_Prompts.md", "Design"),
    ("build-validation", "3D build and project validation", "design/VALIDATION.md", "Design"),
    ("prototype-bom", "Prototype bill of materials", "prototype/hardware/Prototype_BOM.md", "Prototype"),
    ("pinmap", "Pin map", "prototype/hardware/pinmap.md", "Prototype"),
    ("assembly-guide", "Assembly guide", "prototype/hardware/Assembly_Guide.md", "Prototype"),
    ("test-checklist", "Test checklist", "prototype/hardware/Test_Checklist.md", "Prototype"),
    ("print-notes", "3D-print notes", "design/cad/out/PRINT_NOTES.md", "Prototype"),
    ("software", "Prototype software", "prototype/software/README.md", "Prototype"),
    ("software-architecture", "Software architecture", "prototype/software/docs/ARCHITECTURE.md", "Prototype"),
]

CSS = """
:root{--bg:#f6f7f6;--surface:#ffffff;--ink:#1d2a2e;--muted:#5b6b70;--line:#d9e1e2;--teal:#1f4e57;--teal-soft:#e3eef0;--marigold:#d9921c;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#111a1c;--surface:#172427;--ink:#e6eeef;--muted:#9fb1b5;--line:#2a3b3f;--teal:#8cc7d1;--teal-soft:#1d3236;--marigold:#f0b14a;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,"Nirmala UI",sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header.top{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:16px;margin-bottom:28px}
header.top a.brand{font-weight:700;font-size:22px;color:var(--teal);text-decoration:none;letter-spacing:.2px}
header.top span{color:var(--muted);font-size:13px}
h1{font-size:30px;line-height:1.2;margin:0 0 8px;text-wrap:balance}h2{font-size:20px;margin:36px 0 12px;color:var(--teal)}h3{font-size:16px;margin:24px 0 8px}
p.lead{font-size:17px;color:var(--muted);max-width:68ch;margin:0 0 24px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px;min-width:0}
.card h3{margin:0 0 6px}.card p{margin:0 0 10px;color:var(--muted);font-size:14px}
.links a{display:inline-block;margin-right:12px;font-weight:600;color:var(--teal)}
.tag{display:inline-block;font-size:11px;letter-spacing:.6px;text-transform:uppercase;color:var(--marigold);font-weight:700;margin-bottom:6px}
.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.gallery figure{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.gallery img{width:100%;height:auto;display:block}.gallery figcaption{padding:8px 12px;font-size:13px;color:var(--muted)}
article{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:24px;min-width:0}
article img{max-width:100%;height:auto;border-radius:8px}
.table-wrap{overflow-x:auto;margin:12px 0}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{background:var(--teal-soft)}
code,pre{font-family:ui-monospace,Consolas,monospace;font-size:13px}pre{background:var(--teal-soft);padding:12px;border-radius:8px;overflow-x:auto}
blockquote{margin:12px 0;padding:8px 14px;border-left:3px solid var(--marigold);background:var(--teal-soft);border-radius:0 8px 8px 0}
a{color:var(--teal)}a:focus-visible{outline:2px solid var(--marigold);outline-offset:2px}
.note{font-size:13px;color:var(--muted);margin-top:40px}
"""


def page(title, body):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>{html.escape(title)} · SenseBook</title><style>{CSS}</style></head>
<body><div class="wrap"><header class="top"><a class="brand" href="/">SenseBook</a><span>Private project hub · built {date.today():%d %b %Y}</span></header>
{body}
<p class="note">Private. Everything here is a planning document or prototype; figures are estimates until tested.</p></div></body></html>"""


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: f'<img alt="{m.group(1)}" src="{fix_link(m.group(2))}">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{fix_link(m.group(2))}">{m.group(1)}</a>', s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", s)
    return s


def fix_link(href):
    """Point image links at the copied renders and document links at their hub pages; leave web links alone."""
    if href.startswith(("http://", "https://", "#", "/")):
        return href
    name = os.path.basename(href)
    if name.lower().endswith((".png", ".jpg", ".jpeg", ".svg")):
        return "/renders/" + name
    for slug, _title, src, _group in PAGES:                 # a link to another Markdown document that has a hub page
        if name and name == os.path.basename(src) and href.replace("\\", "/").split("#")[0].endswith(name):
            return f"/{slug}/"
    return href


def md_to_html(md):
    out, lines, i = [], md.replace("\r\n", "\n").split("\n"), 0
    para = []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
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
            flush(); lvl = min(len(m.group(1)) + 0, 4); out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            flush(); rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], rows[2:]
            t = "<div class=\"table-wrap\"><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>"
            out.append(t); continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            flush(); ordered = bool(re.match(r"^\s*\d+\.", line)); tag = "ol" if ordered else "ul"; items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        if line.startswith(">"):
            flush(); quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i].lstrip("> ")); i += 1
            out.append("<blockquote>" + inline(" ".join(quote)) + "</blockquote>"); continue
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


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    body = ["<h1>SenseBook</h1>",
            "<p class=\"lead\">A webcam-sized AI reading companion that grips the top of any open book like a tiny tripod. "
            "It reads aloud, explains, discusses, tests and reminds, in Bangla and English, on a table or in the hands. "
            "Built for students and for blind and low-vision readers.</p>"]

    body.append("<h2>Documents</h2><div class=\"grid\">")
    for title, desc, stem in DOCS:
        pdf, docx = copy(stem + ".pdf"), copy(stem + ".docx")
        links = " ".join(f'<a href="{u}">{k}</a>' for k, u in (("PDF", pdf), ("Word", docx)) if u)
        body.append(f'<div class="card"><span class="tag">Document</span><h3>{title}</h3><p>{desc}</p><div class="links">{links}</div></div>')
    x = copy(MODEL[2])
    if x:
        body.append(f'<div class="card"><span class="tag">Spreadsheet</span><h3>{MODEL[0]}</h3><p>{MODEL[1]}</p><div class="links"><a href="{x}">Excel</a></div></div>')
    body.append("</div>")

    renders_dir = os.path.join(ROOT, "design", "renders")
    imgs = sorted(f for f in os.listdir(renders_dir) if f.lower().endswith((".png", ".jpg"))) if os.path.isdir(renders_dir) else []
    if imgs:
        body.append("<h2>Renders</h2><div class=\"gallery\">")
        for f in imgs:
            u = copy(os.path.join("design", "renders", f), os.path.join("renders", f))
            cap = re.sub(r"^\d+\s+", "", os.path.splitext(f)[0].replace("_", " ").replace("-", " "))
            body.append(f'<figure><a href="{u}"><img src="{u}" alt="SenseBook render: {cap}" loading="lazy"></a><figcaption>{cap}</figcaption></figure>')
        body.append("</div>")

    diagrams_dir = os.path.join(ROOT, "design", "diagrams")          # figures used inside the document pages
    for f in sorted(os.listdir(diagrams_dir)) if os.path.isdir(diagrams_dir) else []:
        if f.lower().endswith((".png", ".jpg", ".svg")):
            copy(os.path.join("design", "diagrams", f), os.path.join("renders", f))

    for group in ("Design", "Prototype"):
        cards = []
        if group == "Design":                                         # interactive 3D viewer (three.js page + GLB model)
            v_page = copy(os.path.join("tools", "viewer", "index.html"), os.path.join("viewer", "index.html"))
            v_glb = copy(os.path.join("design", "cad", "out", "sensebook.glb"), os.path.join("viewer", "sensebook.glb"))
            if v_page and v_glb:
                cards.append('<div class="card"><span class="tag">Design</span><h3>3D model viewer</h3>'
                             '<p>Turn the prototype model, pull it apart and look inside.</p>'
                             '<div class="links"><a href="/viewer/">Open the 3D model</a></div></div>')
        for slug, title, src, g in PAGES:
            if g != group:
                continue
            p = os.path.join(ROOT, src)
            if not os.path.isfile(p):
                continue
            with open(p, encoding="utf-8") as fh:
                art = md_to_html(fh.read())
            os.makedirs(os.path.join(OUT, slug), exist_ok=True)
            with open(os.path.join(OUT, slug, "index.html"), "w", encoding="utf-8") as fh:
                fh.write(page(title, f'<p><a href="/">← All files</a></p><article>{art}</article>'))
            cards.append(f'<div class="card"><span class="tag">{group}</span><h3>{title}</h3><div class="links"><a href="/{slug}/">Open</a></div></div>')
        extra = []
        if group == "Prototype":
            for f in ("wiring_diagram.png", "wiring_diagram.svg"):
                u = copy(os.path.join("prototype", "hardware", f), os.path.join("renders", f))
                if u:
                    extra.append(f'<a href="{u}">{f.split(".")[-1].upper()}</a>')
            if extra:
                cards.append(f'<div class="card"><span class="tag">Prototype</span><h3>Wiring diagram</h3><div class="links">{" ".join(extra)}</div></div>')
            cad = os.path.join(ROOT, "design", "cad", "out")
            cad_files = [(os.path.join(d, f), os.path.relpath(os.path.join(d, f), cad)) for d, _, fs in os.walk(cad) for f in sorted(fs)
                         if f.lower().endswith((".stl", ".step", ".stp", ".dxf")) or f == "PRINT_NOTES.md"] if os.path.isdir(cad) else []
            if cad_files:
                zpath = os.path.join(OUT, "downloads", "SenseBook_CAD_files.zip")
                os.makedirs(os.path.dirname(zpath), exist_ok=True)
                with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
                    for full, rel in sorted(cad_files, key=lambda t: t[1]):
                        z.write(full, rel.replace("\\", "/"))
                cards.append('<div class="card"><span class="tag">Prototype</span><h3>3D-print and CAD files</h3><p>STL for printing, STEP for editing, DXF blade patterns.</p><div class="links"><a href="/downloads/SenseBook_CAD_files.zip">Download ZIP</a></div></div>')
        if cards:
            body.append(f"<h2>{group}</h2><div class=\"grid\">" + "".join(cards) + "</div>")

    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page("Project hub", "\n".join(body)))
    with open(os.path.join(OUT, "robots.txt"), "w") as fh:
        fh.write("User-agent: *\nDisallow: /\n")
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    print(f"site built: {n} files, {size / 1e6:.1f} MB -> {OUT}")


if __name__ == "__main__":
    main()
