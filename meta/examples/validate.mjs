#!/usr/bin/env node
/**
 * Syntax-check example corpus .nix files when Nix is installed.
 * Run from repo root: node meta/examples/validate.mjs
 * Exit 0 if Nix missing (skip) or all checks pass; exit 1 on parse errors.
 */
import { execSync, spawnSync } from "child_process";
import fs from "fs";
import path from "path";

const ROOT = process.cwd();
const EXAMPLES = path.join(ROOT, "meta/examples");

function hasNix() {
  try {
    execSync("nix --version", { stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

function walkNix(dir, acc = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walkNix(p, acc);
    else if (ent.name.endsWith(".nix")) acc.push(p);
  }
  return acc;
}

function run(cmd, args, cwd) {
  const r = spawnSync(cmd, args, { cwd, encoding: "utf8" });
  return { ok: r.status === 0, stderr: (r.stderr || "").trim(), stdout: (r.stdout || "").trim() };
}

if (!hasNix()) {
  console.log("skip: nix not in PATH — example corpus not validated (install Nix to enable)");
  process.exit(0);
}

const files = walkNix(EXAMPLES);
const flakeDirs = new Set(
  files.filter((f) => path.basename(f) === "flake.nix").map((f) => path.dirname(f))
);
let failed = 0;

for (const dir of [...flakeDirs].sort()) {
  const rel = path.relative(ROOT, dir);
  const r = run("nix", ["flake", "check", "--no-build"], dir);
  if (r.ok) console.log(`ok flake ${rel}`);
  else {
    failed++;
    console.error(`FAIL flake ${rel}\n${r.stderr || r.stdout}`);
  }
}

for (const file of files.sort()) {
  if (path.basename(file) === "flake.nix") continue;
  const rel = path.relative(ROOT, file);
  const r = run("nix-instantiate", ["--parse", file], ROOT);
  if (r.ok) console.log(`ok parse ${rel}`);
  else {
    failed++;
    console.error(`FAIL parse ${rel}\n${r.stderr}`);
  }
}

if (failed) {
  console.error(`\n${failed} example file(s) failed validation`);
  process.exit(1);
}
console.log(`\nvalidated ${files.length} .nix file(s), ${flakeDirs.size} flake(s)`);
