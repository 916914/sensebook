"""Publish docs/validation/hardware_v2/web/ as its own Vercel project, through Vercel's REST API (no Node needed).

The token is read from the VERCEL_TOKEN environment variable and is never printed or written anywhere.
The page is public to anyone with the link and asks search engines not to index it (X-Robots-Tag + robots meta).

    VERCEL_TOKEN=... python docs/validation/hardware_v2/cad/publish_v2.py [project-name]
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", "web"))
PROJECT = sys.argv[1] if len(sys.argv) > 1 else "sensebook-hardware-v2"
TOKEN = os.environ["VERCEL_TOKEN"]
API = "https://api.vercel.com"
VERCEL_JSON = {"cleanUrls": False, "headers": [{"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]}]}


def call(method, path, body=None, headers=None, raw=None):
    h = {"Authorization": f"Bearer {TOKEN}"}
    h.update(headers or {})
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    if body is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


st, user = call("GET", "/v2/user")
if st != 200:
    sys.exit(f"Vercel: could not read the account ({st}): {user.get('error', {}).get('message', '')}")
team = user.get("user", {}).get("defaultTeamId")
q = f"?teamId={team}" if team else ""

files = []
blobs = {"vercel.json": json.dumps(VERCEL_JSON, indent=1).encode()}
for dp, _, fs in os.walk(SITE):
    for f in fs:
        full = os.path.join(dp, f)
        rel = os.path.relpath(full, SITE).replace(os.sep, "/")
        blobs[rel] = open(full, "rb").read()
for rel, data in sorted(blobs.items()):
    sha = hashlib.sha1(data).hexdigest()
    st, res = call("POST", "/v2/files" + q, raw=data, headers={"Content-Type": "application/octet-stream", "x-vercel-digest": sha,
                                                               "Content-Length": str(len(data))})
    if st not in (200, 201):
        sys.exit(f"upload failed for {rel}: {st} {res.get('error', {}).get('message', '')}")
    files.append({"file": rel, "sha": sha, "size": len(data)})
    print(f"uploaded {rel} ({len(data) / 1e6:.2f} MB)")

st, dep = call("POST", "/v13/deployments" + q, body={"name": PROJECT, "files": files, "target": "production",
                                                       "projectSettings": {"framework": None}})
if st not in (200, 201):
    sys.exit(f"deployment failed: {st} {dep.get('error', {}).get('message', '')}")
did = dep["id"]
for _ in range(90):
    st, d = call("GET", f"/v13/deployments/{did}" + q)
    if d.get("readyState") in ("READY", "ERROR", "CANCELED"):
        break
    time.sleep(4)
print("state:", d.get("readyState"))
print("aliases:", ", ".join("https://" + a for a in d.get("alias", [])) or "(none)")
print("deployment:", "https://" + d.get("url", ""))
