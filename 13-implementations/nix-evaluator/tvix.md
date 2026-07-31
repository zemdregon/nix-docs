---
status: complete
---

# Tvix

## Overview

[Tvix](https://code.tvl.fyi/about/tvix) is a Rust reimplementation of Nix language evaluation and store-related components by [The Virus Lounge (TVL)](https://tvl.fyi/). It is modular—evaluator, store, and builder are separable—and aims at nixpkgs-compatible evaluation and builds, not at being a drop-in replacement for [CppNix](cpp-nix.md) or a production NixOS host stack.

**Maturity (last checked 2026-07-31):** experimental / research. Useful for correctness work, alternative store designs, and embedding Nix evaluation—not for day-to-day system management. Prefer [CppNix](cpp-nix.md) or [Lix](lix.md) for real systems.

In March 2025, maintainers forked the active modular stack into [Snix](snix.md) on dedicated infrastructure. Tvix remains the TVL monorepo project (`//tvix`); for the continuation of that component line under independent hosting, see Snix. Glossary: [Tvix](../../glossary.md#tvix).

## Details

**Who and where.** Tvix lives in TVL’s monorepo (`//tvix`). Prefer the [depot about page](https://code.tvl.fyi/about/tvix) as the durable entry point (`tvix.dev` has been intermittently unreachable). Development tracks evaluator correctness against CppNix, store and castore work, and early build plumbing.

**Architecture.** Unlike a single monolithic daemon-plus-CLI, Tvix splits concerns: a language evaluator (`tvix-eval`), Nix-compat libraries (derivations, hashes, encodings), content-addressed blob/tree storage (`tvix-castore`) plus Nix path metadata (`tvix-store`), and builders that can use OCI-style sandboxing rather than Nix’s custom sandbox code. The evaluator keeps I/O behind an `EvalIO` interface so callers can plug different stores or filesystem models.

**Goals (stated by TVL).** Full reuse of nixpkgs expressions; faster evaluation; first-class IFD-style “drive builds on IO” without a hard eval-then-build wall; clear protocols between evaluator, builder, and store. TVL frames Tvix as an alternative implementation to improve the ecosystem, not as a replacement for Nix itself.

**Vs Snix.** Snix is the independently hosted continuation of this modular stack—not a rename of the TVL tree. Both names remain in use: Tvix for `//tvix` in the TVL depot; Snix for the Forgejo/`snix.dev` line. Compare [Snix](snix.md) for current library-first packaging and early tools.

## Examples

Illustrative component map (names from TVL / Tvix docs; not an install recipe):

```text
tvix-eval     → Nix language evaluation (I/O via EvalIO)
nix-compat    → derivations, ATerm fingerprints, wire formats
tvix-castore  → content-addressed blobs / directory trees
tvix-store    → Nix store-path metadata + cache compatibility
builder       → realize derivations (e.g. OCI / runc-oriented work)
```

Typical research use: evaluate expressions and compare `drvPath` / `outPath` with CppNix for the same nixpkgs input—Tvix’s correctness path—rather than `nixos-rebuild` on a machine.

## See also

- [CppNix](cpp-nix.md) — reference C++ Nix implementation
- [Lix](lix.md) — community fork of the C++ lineage
- [Snix](snix.md) — fork continuation of the modular Tvix stack
- [Nix Evaluators](README.md) — evaluator index
- [Glossary](../../glossary.md#tvix) — CppNix / Lix / Tvix / Snix term index
- [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md) — implementation landscape
- [Timeline](../../15-history-and-governance/timeline.md) — project history context

## References

- [Tvix in the TVL depot](https://code.tvl.fyi/about/tvix) — monorepo entry / about (preferred)
