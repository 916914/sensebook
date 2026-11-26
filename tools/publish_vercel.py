"""Publish the SenseBook hub (D:\\Sensebook\\site) to the founder's personal Vercel, LOCKED to their login.

Follows a tested deploy pattern:
- deploys a clean copy of site/ only (Vercel's CLI ignores .gitignore);
- creates the project and turns on Vercel Authentication for ALL deployments BEFORE the first upload;
- adds noindex headers; checks the live URL from outside and reports "locked" or "open".
Token: VERCEL_TOKEN from the environment only. It is never written to disk or printed.
Run via tools/Publish-SenseBook.ps1 (which asks for the token at a hidden prompt).
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
PROJECT = "sensebook-hub"          # neutral name
VERCEL = [shutil.which("npx") or "npx", "--yes", "vercel@62.5.0"]
API = "https://api.vercel.com"
EXCLUDE = [r"(^|/)\.", r"\.md$", r"\.(py|pyc|sqlite|db|env|local|bak|log|wav)$", r"(^|/)(scripts|data|node_modules|__pycache__|\.venv)/"]
HEADERS = [{"source": "/(.*)", "headers": [
    {"key": "X-Robots-Tag", "value": "noindex, nofollow"},
    {"key": "X-Content-Type-Options", "value": "nosniff"},
    {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}]}]


def files():
    if not os.path.isfile(os.path.join(SITE, "index.html")):
        sys.exit("site/ is missing. Run: python -I tools/build_site.py")
    skip = [re.compile(p) for p in EXCLUDE]
    out = []
    for rel in glob.glob("**", root_dir=SITE, recursive=True, include_hidden=True):
        rel = rel.replace("\\", "/")
        if os.path.isfile(os.path.join(SITE, rel)) and not any(s.search(rel) for s in skip):
            out.append(rel)
    return sorted(out)


def api(token, method, path, body=None, team=None):
    if team:
        path += ("&" if "?" in path else "?") + "teamId=" + team
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, method=method, data=data,
                                 headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def ready_project(token, team, public):
    code, p = api(token, "GET", f"/v9/projects/{PROJECT}", team=team)
    if code == 404:
        code, p = api(token, "POST", "/v11/projects", {"name": PROJECT, "framework": None}, team)
    if code >= 300:
        sys.exit(f"Could not get or create project {PROJECT}: HTTP {code} {p.get('error', {}).get('message', '')}")
    want = None if public else {"deploymentType": "all"}
    if ((p.get("ssoProtection") or {}).get("deploymentType")) != ((want or {}).get("deploymentType")):
        code, p = api(token, "PATCH", f"/v9/projects/{PROJECT}", {"ssoProtection": want}, team)
        if code >= 300:
            sys.exit(f"Could not set access for {PROJECT} (HTTP {code}). Nothing was deployed.")
    return p


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def access(url):
    try:
        with urllib.request.build_opener(NoRedirect).open(url):
            return "OPEN"
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location", "") or ""
        if e.code in (401, 403) or "vercel.com/login" in loc or "sso" in loc:
            return "locked"
        return f"redirect {e.code}" if 300 <= e.code < 400 else f"HTTP {e.code}"


def main():
    names = files()
    size = sum(os.path.getsize(os.path.join(SITE, n)) for n in names)
    public = "--public" in sys.argv
    print(f"{PROJECT}: {len(names)} files, {size / 1e6:.1f} MB, {'open to anyone with the link' if public else 'locked to your Vercel login'}")
    if "--dry-run" in sys.argv:
        print("\n".join("  " + n for n in names))
        return
    token = os.environ.get("VERCEL_TOKEN", "").strip()
    if not token:
        sys.exit("VERCEL_TOKEN is not set. Run tools/Publish-SenseBook.ps1, which asks for it at a hidden prompt.")
    code, user = api(token, "GET", "/v2/user")
    if code >= 300:
        sys.exit(f"The Vercel token was refused (HTTP {code}).")
    team = user["user"]["defaultTeamId"]
    project = ready_project(token, team, public)

    out = tempfile.mkdtemp(prefix="sensebook-deploy-")
    try:
        for n in names:
            os.makedirs(os.path.dirname(os.path.join(out, n)), exist_ok=True)
            shutil.copy2(os.path.join(SITE, n), os.path.join(out, n))
        with open(os.path.join(out, "vercel.json"), "w") as f:
            json.dump({"headers": HEADERS}, f)
        env = {**os.environ, "VERCEL_ORG_ID": team, "VERCEL_PROJECT_ID": project["id"]}
        env.pop("VERCEL_TOKEN", None)
        run = subprocess.run([*VERCEL, "deploy", out, "--prod", "--yes", "--token", token], env=env, capture_output=True, text=True)
    finally:
        shutil.rmtree(out, ignore_errors=True)
    if run.returncode:
        sys.exit("Deploy failed:\n" + run.stderr.replace(token, "***")[-2000:])

    _, p = api(token, "GET", f"/v9/projects/{PROJECT}", team=team)
    prod = (p.get("targets") or {}).get("production") or {}
    print("Deployed:", prod.get("readyState"))
    for u in ["https://" + h for h in [prod.get("url"), *prod.get("alias", [])] if h]:
        print(f"  {access(u):8}  {u}")
    print("Open to anyone with the link." if public else "Open the links after signing in to your personal Vercel in the browser.")


main()
