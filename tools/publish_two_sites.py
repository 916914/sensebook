"""Publish the two SenseBook hub sites to Vercel. Both open to anyone who has the link.

  1. the public hub  : everything except the venture plan and the financial model  -> project "sensebook-hub"
  2. the full hub    : everything included                                         -> a second project, name given by you

Owner's request, 27 Nov 2026: two separate links to use and share.

Needs only Python (no Node, no Vercel CLI): files go up through Vercel's REST API.
Token: VERCEL_TOKEN from the environment only. It is never written to disk or printed.
The full hub's project name comes from SENSEBOOK_FULL_PROJECT (or --full NAME), so it does not sit in this public repository.

  set VERCEL_TOKEN=...            (PowerShell: $env:VERCEL_TOKEN = '...')
  set SENSEBOOK_FULL_PROJECT=...
  python -I tools/publish_two_sites.py            # build both, publish both
  python -I tools/publish_two_sites.py --dry-run  # build both and list the files, publish nothing
  python -I tools/publish_two_sites.py --only public | --only full

Note: a link nobody can guess is not a lock. Anyone who is given the full link can open it and pass it on.
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.vercel.com"
PUBLIC_PROJECT = "sensebook-hub"
HEADERS = [{"source": "/(.*)", "headers": [
    {"key": "X-Robots-Tag", "value": "noindex, nofollow"},
    {"key": "X-Content-Type-Options", "value": "nosniff"},
    {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}]}]
KEPT_OFF_PUBLIC = ("venture_plan", "financial_model")       # checked again before upload


def call(token, method, path, body=None, team=None, raw=None, headers=None):
    if team:
        path += ("&" if "?" in path else "?") + "teamId=" + team
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    h = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
    h.update(headers or {})
    req = urllib.request.Request(API + path, method=method, data=data, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {}


def site_files(folder):
    out = []
    for d, _, fs in os.walk(folder):
        for f in fs:
            full = os.path.join(d, f)
            out.append((os.path.relpath(full, folder).replace("\\", "/"), full))
    if not any(rel == "index.html" for rel, _ in out):
        sys.exit(f"{folder} has no index.html")
    return sorted(out)


def build(public, folder):
    cmd = [sys.executable, "-I", os.path.join(ROOT, "tools", "build_site.py"), "--out", folder] + (["--public"] if public else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("build failed:\n" + r.stdout[-1500:] + r.stderr[-1500:])
    return r.stdout.strip().splitlines()[-1]


def opens_without_login(url):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a):
            return None
    try:
        with urllib.request.build_opener(NoRedirect).open(url, timeout=30) as r:
            return f"open (HTTP {r.status})"
    except urllib.error.HTTPError as e:
        return f"NOT open (HTTP {e.code})"
    except Exception as e:                                   # noqa: BLE001
        return f"could not check ({type(e).__name__})"


def publish(token, team, project_name, folder):
    code, p = call(token, "GET", f"/v9/projects/{project_name}", team=team)
    if code == 404:
        code, p = call(token, "POST", "/v11/projects", {"name": project_name, "framework": None}, team)
    if code >= 300:
        sys.exit(f"Could not get or create the project (HTTP {code}): {(p.get('error') or {}).get('message', '')}")
    if p.get("ssoProtection"):                               # open to anyone with the link
        code, p2 = call(token, "PATCH", f"/v9/projects/{project_name}", {"ssoProtection": None}, team)
        if code >= 300:
            sys.exit(f"Could not open the project to visitors (HTTP {code}). Nothing was deployed.")
    files = site_files(folder)
    tmp = os.path.join(folder, "vercel.json")
    with open(tmp, "w") as fh:
        json.dump({"headers": HEADERS}, fh)
    files = site_files(folder)
    manifest = []
    for rel, full in files:
        blob = open(full, "rb").read()
        sha = hashlib.sha1(blob).hexdigest()
        manifest.append({"file": rel, "sha": sha, "size": len(blob)})
        code, r = call(token, "POST", "/v2/files", team=team, raw=blob,
                       headers={"Content-Type": "application/octet-stream", "x-vercel-digest": sha, "Content-Length": str(len(blob))})
        if code >= 300:
            sys.exit(f"Upload failed for {rel} (HTTP {code}): {(r.get('error') or {}).get('message', '')}")
    code, d = call(token, "POST", "/v13/deployments?skipAutoDetectionConfirmation=1",
                   {"name": project_name, "project": p["id"], "target": "production", "files": manifest,
                    "projectSettings": {"framework": None}}, team)
    if code >= 300:
        sys.exit(f"Deployment refused (HTTP {code}): {(d.get('error') or {}).get('message', '')}")
    dep = d["id"]
    for _ in range(90):
        code, d = call(token, "GET", f"/v13/deployments/{dep}", team=team)
        if d.get("readyState") in ("READY", "ERROR", "CANCELED"):
            break
        time.sleep(2)
    if d.get("readyState") != "READY":
        sys.exit(f"Deployment did not become ready: {d.get('readyState')}")
    hosts = list(dict.fromkeys([*(d.get("alias") or []), d.get("url")]))
    return [f"https://{h}" for h in hosts if h], len(files)


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else "both"
    full_name = sys.argv[sys.argv.index("--full") + 1] if "--full" in sys.argv else os.environ.get("SENSEBOOK_FULL_PROJECT", "").strip()
    dry = "--dry-run" in sys.argv
    jobs = []
    if only in ("both", "public"):
        jobs.append(("public hub (no venture plan, no financial model)", PUBLIC_PROJECT, True))
    if only in ("both", "full"):
        if not full_name and not dry:
            sys.exit("Give the full hub's project name: SENSEBOOK_FULL_PROJECT or --full NAME")
        jobs.append(("full hub (everything)", full_name or "(name not given)", False))
    token = os.environ.get("VERCEL_TOKEN", "").strip()
    team = None
    if not dry:
        if not token:
            sys.exit("VERCEL_TOKEN is not set.")
        code, user = call(token, "GET", "/v2/user")
        if code >= 300:
            sys.exit(f"The Vercel token was refused (HTTP {code}).")
        team = user["user"]["defaultTeamId"]
    for label, name, public in jobs:
        folder = tempfile.mkdtemp(prefix="sensebook-site-")
        try:
            print(f"\n== {label} ==\n{build(public, folder)}")
            names = [rel.lower() for rel, _ in site_files(folder)]
            leaked = [n for n in names if any(k in n for k in KEPT_OFF_PUBLIC)]
            if public and leaked:
                sys.exit("STOP: the public build still contains " + ", ".join(leaked))
            if dry:
                print(f"{len(names)} files; venture plan / financial model present: {bool(leaked)}")
                continue
            urls, n = publish(token, team, name, folder)
            print(f"published {n} files")
            for u in urls:
                print(f"  {opens_without_login(u):22} {u}")
        finally:
            shutil.rmtree(folder, ignore_errors=True)


if __name__ == "__main__":
    main()
