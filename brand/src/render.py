"""Render local HTML to PNG or PDF with headless Microsoft Edge (or Chrome). Apache-2.0."""
import os, shutil, subprocess, tempfile, time

CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    shutil.which("msedge") or "", shutil.which("chrome") or "", shutil.which("chromium") or "",
]


def browser():
    for c in CANDIDATES:
        if c and os.path.isfile(c):
            return c
    raise SystemExit("Needs Microsoft Edge or Chrome to render HTML.")


def _run(args, scale=1):
    prof = tempfile.mkdtemp(prefix="sb-render-")
    try:
        subprocess.run([browser(), "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                        "--hide-scrollbars", f"--force-device-scale-factor={scale}", f"--user-data-dir={prof}",
                        "--virtual-time-budget=4000", *args], check=True, capture_output=True, timeout=180)
    finally:
        time.sleep(0.3)
        shutil.rmtree(prof, ignore_errors=True)


def url(path):
    return "file:///" + os.path.abspath(path).replace("\\", "/")


def png(html_path, out_png, width, height, scale=1):
    _run([f"--screenshot={os.path.abspath(out_png)}", f"--window-size={width},{height}", url(html_path)], scale)
    return out_png


def pdf(html_path, out_pdf):
    _run([f"--print-to-pdf={os.path.abspath(out_pdf)}", "--no-pdf-header-footer", url(html_path)])
    return out_pdf
