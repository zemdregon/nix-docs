#!/usr/bin/env node
/**
 * Broken relative .md link check (todo-coverage.md Audit hook).
 * Run from repo root: node meta/audit/broken-links.mjs
 * Exit 1 if any target is missing; prints broken=N.
 */
import fs from "fs";
import path from "path";

const ROOT = process.cwd();
const re = /\[([^\]]*)\]\(([^)]+\.md)(#[^)]*)?\)/g;

function walk(dir, acc = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.name.startsWith(".")) continue;
    if (ent.name === "node_modules") continue;
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p, acc);
    else if (ent.name.endsWith(".md")) acc.push(p);
  }
  return acc;
}

let checked = 0;
const broken = [];

for (const file of walk(ROOT)) {
  const t = fs.readFileSync(file, "utf8");
  let m;
  while ((m = re.exec(t))) {
    const target = m[2];
    if (/^(https?:|mailto:)/.test(target)) continue;
    checked++;
    const dest = path.resolve(path.dirname(file), target);
    if (!dest.startsWith(ROOT + path.sep) && dest !== ROOT) {
      broken.push([file, target, "outside"]);
      continue;
    }
    if (!fs.existsSync(dest) || !fs.statSync(dest).isFile()) {
      broken.push([file, target, "missing"]);
    }
  }
}

console.log(`checked=${checked} broken=${broken.length}`);
broken.forEach((b) => console.log(" ", b.join(" -> ")));
process.exit(broken.length ? 1 : 0);
