// SPDX-License-Identifier: Apache-2.0
// Publishes the website to Vercel production. Run only on the owner's yes.
//
//   VERCEL_TOKEN=... node scripts/publish-vercel.mjs [--dry-run]
//
// - Token: VERCEL_TOKEN from the environment only. It is never written to disk or printed.
// - Gets or creates the Vercel project "human-advancement" (framework: Next.js).
// - Stages the site's source plus the SenseBook renders and model already copied into
//   public/design (by scripts/sync-design.mjs), so Vercel's own build has them even though
//   the build chat's design/ folder is not uploaded.
// - Optional: NEXT_PUBLIC_CONTACT_EMAIL is passed to the build if set; it is never committed.

import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdtempSync, readdirSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const PROJECT = "human-advancement";
const VERCEL_CLI = ["--yes", "vercel@62.5.0"];
const API = "https://api.vercel.com";
const site = resolve(dirname(fileURLToPath(import.meta.url)), "..");

const skip = new Set(["node_modules", ".next", ".vercel", "tsconfig.tsbuildinfo", "next-env.d.ts"]);
const skipPaths = [join("docs", "screenshots")];
const include = (src) => {
  const rel = relative(site, src);
  if (!rel) return true;
  const first = rel.split(sep)[0];
  if (skip.has(first) || rel.startsWith(".env")) return false;
  return !skipPaths.some((p) => rel === p || rel.startsWith(p + sep));
};

function listFiles(dir) {
  return readdirSync(dir).flatMap((n) => {
    const p = join(dir, n);
    if (!include(p)) return [];
    return statSync(p).isDirectory() ? listFiles(p) : [p];
  });
}

const files = listFiles(site);
const size = files.reduce((s, f) => s + statSync(f).size, 0);
const renders = files.filter((f) => f.includes(join("public", "design"))).length;
console.log(`${PROJECT}: ${files.length} files, ${(size / 1e6).toFixed(1)} MB (${renders} SenseBook renders/model files)`);
if (renders < 12) console.warn("Warning: SenseBook renders are missing. Run `npm run sync-design` first.");
if (process.argv.includes("--dry-run")) process.exit(0);

const token = (process.env.VERCEL_TOKEN || "").trim();
if (!token) {
  console.error("VERCEL_TOKEN is not set.");
  process.exit(1);
}
const scrub = (s) => String(s).split(token).join("***");

async function api(method, path, body, team) {
  const url = new URL(API + path);
  if (team) url.searchParams.set("teamId", team);
  const res = await fetch(url, {
    method,
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  return { status: res.status, json: await res.json().catch(() => ({})) };
}

const user = await api("GET", "/v2/user");
if (user.status >= 300) {
  console.error(`The Vercel token was refused (HTTP ${user.status}).`);
  process.exit(1);
}
const team = user.json.user?.defaultTeamId || undefined;

let project = await api("GET", `/v9/projects/${PROJECT}`, undefined, team);
if (project.status === 404) {
  project = await api("POST", "/v11/projects", { name: PROJECT, framework: "nextjs" }, team);
  console.log(project.status < 300 ? `Created project ${PROJECT}.` : "");
}
if (project.status >= 300) {
  console.error(`Could not get or create project ${PROJECT}: HTTP ${project.status} ${project.json.error?.message || ""}`);
  process.exit(1);
}

const stage = mkdtempSync(join(tmpdir(), "human-advancement-deploy-"));
let run;
try {
  cpSync(site, stage, { recursive: true, filter: include });
  const args = [...VERCEL_CLI, "deploy", stage, "--prod", "--yes", "--token", token];
  const prodUrl = `https://${PROJECT}.vercel.app`;
  args.push("--build-env", `NEXT_PUBLIC_SITE_URL=${process.env.NEXT_PUBLIC_SITE_URL || prodUrl}`);
  if (process.env.NEXT_PUBLIC_CONTACT_EMAIL) args.push("--build-env", `NEXT_PUBLIC_CONTACT_EMAIL=${process.env.NEXT_PUBLIC_CONTACT_EMAIL}`);
  args.push("--build-env", "NEXT_TELEMETRY_DISABLED=1");
  const env = { ...process.env, VERCEL_PROJECT_ID: project.json.id, VERCEL_ORG_ID: team || project.json.accountId };
  delete env.VERCEL_TOKEN;
  // Run npx through this Node binary (no shell), so the token is never parsed by a shell.
  const npxCli = [join(dirname(process.execPath), "node_modules", "npm", "bin", "npx-cli.js"), join(dirname(process.execPath), "..", "lib", "node_modules", "npm", "bin", "npx-cli.js")].find(existsSync);
  run = npxCli
    ? spawnSync(process.execPath, [npxCli, ...args], { env, encoding: "utf8" })
    : spawnSync("npx", args, { env, encoding: "utf8" });
} finally {
  rmSync(stage, { recursive: true, force: true });
}
if (run.status !== 0) {
  console.error("Deploy failed:\n" + scrub((run.stderr || "") + (run.stdout || "")).slice(-3000));
  process.exit(1);
}

const after = await api("GET", `/v9/projects/${PROJECT}`, undefined, team);
const prod = after.json.targets?.production || {};
console.log(`Deployed: ${prod.readyState || "unknown state"}`);
for (const host of [...new Set([...(prod.alias || []), prod.url].filter(Boolean))]) console.log(`  https://${host}`);
if (!existsSync(join(site, "public", "design"))) console.warn("Note: public/design was missing locally; product images will show placeholders.");
