---
status: complete
---

# Snix

## Overview

[Snix](https://snix.dev/) is a modular Rust reimplementation of Nix package-manager components: evaluator, content-addressed store, builders, and related libraries. It presents a Nix-compatible surface (aiming at nixpkgs-compatible evaluation and binary-cache interoperability) while exposing pieces as embeddable crates rather than a single monolithic CLI.

It continues the [Tvix](tvix.md)-lineage work under independent infrastructure and community. In March 2025, maintainers forked Tvix into Snix to resolve conflicting priorities with the TVL monorepo, onboarding, and architecture focus—not a wholesale rename of TVL’s `//tvix` tree.

**Maturity (last checked 2026-07-31):** early / research. Project docs state APIs are unstable and there is no full drop-in replacement for [CppNix](cpp-nix.md) yet. Glossary: [Snix](../../glossary.md#snix).

## Details

**Relationship to other implementations.** Snix is not a soft fork of CppNix or [Lix](lix.md); it reimplements components from scratch in Rust. Relative to Tvix, it is the active continuation of that modular stack on dedicated hosting (`snix.dev`, Forgejo at `git.snix.dev`), not a TVL-side project.

**Architecture.** Crates compose freely. Notable pieces (see the [component overview](https://snix.dev/docs/components/overview/)):

- `snix-eval` — bytecode compiler/VM for the Nix language; pluggable builtins and an `EvalIO` trait for IO
- `snix-castore` — content-addressed merkle/chunked storage (not Nix-specific)
- `snix-store` — Nix store metadata on top of castore
- `nix-compat` — low-dependency parsers/encodings for Nix formats and protocols (usable outside Snix)
- `snix-glue` / `snix-build` — store/builder integration and pluggable sandboxed builds (e.g. OCI)
- `nar-bridge` — HTTP binary-cache front end over `snix-store`, so CppNix can substitute from or copy into Snix storage

**Library-first.** The design targets embedding Nix evaluation and store concepts in other programs (`snix-serde` for Nix-as-config), not only shipping a user-facing `nix` binary. Early tools include `snix-cli` (evaluator REPL used to compare against nixpkgs), `snix-store` (gRPC daemon, import/copy, FUSE/virtiofs), `snix-boot` (microVMs via virtiofs), and `snixbolt` (browser WASM bytecode explorer).

**Compatibility goals.** Internals may differ (especially castore granularity and builders), but the project aims for a Nix-compatible surface: same build expressions bit-by-bit where claimed, and interoperability with existing binary caches. Regression testing and docs emphasize matching Nix behavior; treat CLI and crate APIs as moving targets until the project declares otherwise.

**License and funding.** GPLv3; funded in part by NLnet. Source: [git.snix.dev/snix/snix](https://git.snix.dev/snix/snix).

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
- [Lix](lix.md) — community fork of the C++ lineage
- [Nix Evaluators](README.md) — evaluator index
- [Glossary](../../glossary.md#snix) — CppNix / Lix / Tvix / Snix term index
- [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md) — implementation landscape

## References

- [Snix](https://snix.dev/) — project site
- [About Snix](https://snix.dev/about/) — maturity / tools / early-adopter stance
- [Snix source (Forgejo)](https://git.snix.dev/snix/snix) — GPLv3 source tree
