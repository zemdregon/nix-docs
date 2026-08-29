#!/usr/bin/env node
/**
 * Quality audit beyond broken-link check (todo-coverage.md Audit hook).
 * Run from repo root: node meta/audit/quality-audit.mjs
 */
import fs from "fs";
import path from "path";

const ROOT = process.cwd();
const SKIP_DIRS = new Set([".git", "node_modules", ".cursor", "docs", "site"]);

/** Leaves intentionally without runnable ## Examples (roadmaps, cheatsheets, …). */
const THIN_EXAMPLES_EXEMPT = [
  /^00-roadmap\//,
  /^cheatsheets\//,
  /^glossary\.md$/,
  /^03-language\/cheatsheet\.md$/,
  /^07-flakes\/pure-eval-and-impure\.md$/, // large Examples with ### subsections
  /^09-nixos\/configuration\/networking\.md$/,
  /^09-nixos\/services\/common-service-examples\.md$/,
];

function walk(dir, acc = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.name.startsWith(".") && ent.name !== ".") continue;
    if (SKIP_DIRS.has(ent.name)) continue;
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p, acc);
    else if (ent.name.endsWith(".md")) acc.push(p);
  }
  return acc;
}

function parseFrontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) return { body: text, fm: {} };
  const fm = {};
  for (const line of m[1].split("\n")) {
    const kv = line.match(/^(\w[\w-]*):\s*(.+)$/);
    if (kv) fm[kv[1]] = kv[2].trim();
  }
  return { body: text.slice(m[0].length), fm };
}

function rel(p) {
  return path.relative(ROOT, p).replace(/\\/g, "/");
}

/** Extract body of a level-2 section (stops at next `## ` heading; `###` is included). */
function sectionBody(body, title) {
  const re = new RegExp(`^## ${title}\\s*\\n([\\s\\S]*?)(?=^## )`, "m");
  const m = body.match(re);
  if (m) return m[1];
  const reLast = new RegExp(`^## ${title}\\s*\\n([\\s\\S]*)$`, "m");
  return (body.match(reLast) || [null, null])[1];
}

function isExamplesExempt(relPath, body) {
  if (THIN_EXAMPLES_EXEMPT.some((re) => re.test(relPath))) return true;
  if (/no runnable example/i.test(body.slice(0, 800))) return true;
  return false;
}

const files = walk(ROOT);
const inbound = new Map();
const linkRe = /\[([^\]]*)\]\(([^)]+\.md)(#[^)]*)?\)/g;

for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  let m;
  while ((m = linkRe.exec(text))) {
    const target = m[2];
    if (/^(https?:|mailto:)/.test(target)) continue;
    const dest = path.resolve(path.dirname(file), target);
    const key = rel(dest);
    inbound.set(key, (inbound.get(key) || 0) + 1);
  }
}

const completeLeaves = [];
const thinExamples = [];
const noSeeAlso = [];
const noBoundaries = [];
const staleLastChecked = [];
const today = new Date();
const STALE_MONTHS = 6;

for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  const { body, fm } = parseFrontmatter(text);
  if (fm.status !== "complete") continue;

  const isLeaf =
    !file.endsWith("/README.md") &&
    !["glossary.md", "AGENTS.md"].includes(path.basename(file)) &&
    !file.startsWith(path.join(ROOT, "meta") + path.sep);
  if (!isLeaf) continue;

  completeLeaves.push(file);
  const relPath = rel(file);

  const exBody = sectionBody(body, "Examples");
  const exLen = exBody ? exBody.trim().length : 0;
  if (!isExamplesExempt(relPath, body) && exLen < 40) {
    thinExamples.push(relPath);
  }

  if (!/## See also/.test(body)) noSeeAlso.push(relPath);

  const isConceptOrOps =
    /\/02-concepts\//.test(file) ||
    /\/09-nixos\/(operations|configuration)\//.test(file);
  if (isConceptOrOps && !/Boundaries|what this page is not/i.test(body)) {
    noBoundaries.push(relPath);
  }

  if (fm["last-checked"]) {
    const d = new Date(fm["last-checked"] + "-01");
    const ageMonths =
      (today.getFullYear() - d.getFullYear()) * 12 +
      (today.getMonth() - d.getMonth());
    if (ageMonths > STALE_MONTHS) staleLastChecked.push(relPath);
  }
}

const orphans = completeLeaves
  .map((f) => rel(f))
  .filter((f) => (inbound.get(f) || 0) < 2);

console.log(`complete_leaves=${completeLeaves.length}`);
console.log(`thin_examples=${thinExamples.length}`);
console.log(`no_see_also=${noSeeAlso.length}`);
console.log(`no_boundaries=${noBoundaries.length}`);
console.log(`orphan_inbound_lt2=${orphans.length}`);
console.log(`stale_last_checked=${staleLastChecked.length}`);

function sample(label, arr, n = 12) {
  if (!arr.length) return;
  console.log(`\n# ${label} (showing up to ${n})`);
  arr.slice(0, n).forEach((x) => console.log(`  ${x}`));
}

sample("thin_examples", thinExamples);
sample("no_see_also", noSeeAlso);
sample("no_boundaries", noBoundaries);
sample("orphans", orphans);
sample("stale_last_checked", staleLastChecked);
