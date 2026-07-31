---
status: complete
---

# Snix

## Overview

[Snix](https://snix.dev/) is a modular Rust reimplementation of Nix package-manager components: evaluator, content-addressed store, builders, and related libraries. It presents a Nix-compatible surface (aiming at nixpkgs-compatible evaluation and binary-cache interoperability) while exposing pieces as embeddable crates rather than a single monolithic CLI.

It continues the [Tvix](tvix.md)-lineage work under independent infrastructure and community. On **2025-03-16**, maintainers [announced](https://snix.dev/blog/announcing-snix/) a fork of Tvix into Snix—**new project name and hosting**, not a soft fork of [CppNix](cpp-nix.md)—to separate priorities from the TVL monorepo (contributor onboarding, CI, architecture focus). Maturity is early / research: project docs state APIs are unstable and there is no full drop-in replacement for CppNix yet.

## Details

### Maturity (last checked 2026-07-31)

| Aspect | Stamp |
|--------|--------|
| Lineage | From-scratch Rust modular stack; forked from TVL [Tvix](tvix.md) (2025-03-16), not a CppNix/Lix soft fork |
| Hosting | [snix.dev](https://snix.dev/), Forgejo [git.snix.dev/snix/snix](https://git.snix.dev/snix/snix) |
| Compatibility | Incomplete—nixpkgs / binary-cache *goals* stated; APIs unstable; no full-featured Nix CLI drop-in |
| Production role | Early adopter / research / embedding; prefer CppNix or [Lix](lix.md) for day-to-day systems |
| License / funding | GPLv3; funded in part by NLnet ([About Snix](https://snix.dev/about/)) |

### Relationship to other implementations

Snix reimplements components from scratch in Rust. Relative to Tvix, it is the **active continuation** of that modular stack on dedicated hosting—not a TVL-side project. Relative to Lix, Lix evolves the C++ CppNix lineage for compatibility-first day-to-day use; Snix targets modular second-generation components. Do not treat Snix binaries as a silent swap for `nix` on a production host.

### Architecture

Crates compose freely. Notable pieces (see the [component overview](https://snix.dev/docs/components/overview/)):

- `snix-eval` — bytecode compiler/VM for the Nix language; pluggable builtins and an `EvalIO` trait for IO
- `snix-castore` — content-addressed merkle/chunked storage (not Nix-specific)
- `snix-store` — Nix store metadata on top of castore
- `nix-compat` — low-dependency parsers/encodings for Nix formats and protocols (usable outside Snix)
- `snix-glue` / `snix-build` — store/builder integration and pluggable sandboxed builds (e.g. OCI)
- `nar-bridge` — HTTP binary-cache front end over `snix-store`, so CppNix can substitute from or copy into Snix storage

### Library-first and tooling

The design targets embedding Nix evaluation and store concepts in other programs (`snix-serde` for Nix-as-config), not only shipping a user-facing `nix` binary. Early tools include `snix-cli` (evaluator REPL used to compare against nixpkgs), `snix-store` (gRPC daemon, import/copy, FUSE/virtiofs), `snix-boot` (microVMs via virtiofs), and `snixbolt` (browser WASM bytecode explorer).

### Compatibility goals

Internals may differ (especially castore granularity and builders), but the project aims for a Nix-compatible surface: same build expressions bit-by-bit where claimed, and interoperability with existing binary caches. Regression testing and docs emphasize matching Nix behavior; treat CLI and crate APIs as moving targets until the project declares otherwise. Stamp: **incomplete compatibility** as of last check—do not claim parity with CppNix or Lix.

## Examples

Clone and build the evaluator CLI from the Snix tree (requires Nix; from the [building guide](https://snix.dev/docs/guides/building/)):

```bash
git clone https://git.snix.dev/snix/snix.git
cd snix
nix-build -A snix.cli.default-cli
```

`snix-cli` is for evaluation / REPL and nixpkgs comparison work; it is not a `nix-build` replacement. Optional CI substituter (`cache.snix.dev`) paths are not guaranteed long-term.

## See also

- [Tvix](tvix.md) — TVL monorepo project Snix forked from
- [CppNix](cpp-nix.md) — reference C++ Nix implementation
- [Lix](lix.md) — community fork of the C++ lineage (compatibility-first alternative)
- [Nix Evaluators](README.md) — evaluator index
- [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md) — C++-lineage fork map (Snix is a separate effort)

## References

- [Snix](https://snix.dev/) — project site
- [About Snix](https://snix.dev/about/) — maturity / tools / early-adopter stance
- [Announcing Snix](https://snix.dev/blog/announcing-snix/) — 2025-03-16 fork from Tvix; new name and infra
- [Component overview](https://snix.dev/docs/components/overview/) — crate map
- [Building Snix](https://snix.dev/docs/guides/building/) — clone / `nix-build` / cache notes
- [Snix source (Forgejo)](https://git.snix.dev/snix/snix) — GPLv3 source tree
