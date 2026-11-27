// SPDX-License-Identifier: Apache-2.0
// Copies SenseBook's renders and 3D model from the build chat's folder (../design) into
// public/design so the site can serve them. The copies are gitignored: design/ stays the only source.
// Missing files are reported, not fatal: the site shows a marked placeholder for anything absent.

import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const site = resolve(here, "..");
const design = resolve(site, "..", "design");
const out = join(site, "public", "design");

const files = [
  ["renders/01_hero.jpg", "renders/01_hero.jpg"],
  ["renders/02_front.png", "renders/02_front.png"],
  ["renders/03_side.png", "renders/03_side.png"],
  ["renders/04_top.png", "renders/04_top.png"],
  ["renders/05_exploded_unit.png", "renders/05_exploded_unit.png"],
  ["renders/07_cutaway_side.png", "renders/07_cutaway_side.png"],
  ["renders/10_on_open_hardcover.jpg", "renders/10_on_open_hardcover.jpg"],
  ["renders/11_on_thin_paperback.jpg", "renders/11_on_thin_paperback.jpg"],
  ["renders/12_table_tripod_no_book.jpg", "renders/12_table_tripod_no_book.jpg"],
  ["renders/13_held_in_the_hands.jpg", "renders/13_held_in_the_hands.jpg"],
  ["renders/14_folded.jpg", "renders/14_folded.jpg"],
  ["renders/15_stick_extended_small_print.jpg", "renders/15_stick_extended_small_print.jpg"],
  ["cad/out/sensebook.glb", "model/sensebook.glb"],
];

if (!existsSync(design)) {
  console.warn(`[sync-design] ${design} not found. Product visuals will show placeholders.`);
  process.exit(0);
}

let copied = 0;
const missing = [];
for (const [from, to] of files) {
  const src = join(design, from);
  const dst = join(out, to);
  if (!existsSync(src)) {
    missing.push(from);
    continue;
  }
  mkdirSync(dirname(dst), { recursive: true });
  const fresh = !existsSync(dst) || statSync(dst).mtimeMs < statSync(src).mtimeMs || statSync(dst).size !== statSync(src).size;
  if (fresh) {
    copyFileSync(src, dst);
    copied++;
  }
}

console.log(`[sync-design] ${files.length - missing.length} of ${files.length} files present, ${copied} updated.`);
if (missing.length) console.warn(`[sync-design] missing (placeholders will show): ${missing.join(", ")}`);
