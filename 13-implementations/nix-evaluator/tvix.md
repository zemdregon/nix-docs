---
status: complete
---

# Tvix

## Overview

[Tvix](https://tvl.fyi/blog/rewriting-nix) is a Rust reimplementation of Nix language evaluation and store-related components by [The Virus Lounge (TVL)](https://tvl.fyi/). It is modular—evaluator, store, and builder are separable—and aims at nixpkgs-compatible evaluation and builds, not at being a drop-in replacement for [CppNix](cpp-nix.md) or a production NixOS host stack. Treat it as experimental / research software: useful for correctness work, alternative store designs, and embedding Nix evaluation, not for day-to-day system management.

On **2025-03-16**, maintainers announced a fork of the active modular stack as [Snix](snix.md): new name, dedicated hosting and community, to resolve conflicting priorities with the TVL monorepo (onboarding, CI, architecture focus). That is a **fork with a rename of the continuing line**, not a silent rebrand of the TVL tree in place. Tvix remains the TVL monorepo project (`//tvix`); for the independent continuation of that component line, see Snix.

## Details

### Maturity (last checked 2026-07-31)

| Aspect | Stamp |
|--------|--------|
| Hosting | TVL depot (`//tvix`); entry via [depot about](https://code.tvl.fyi/about/tvix) and [TVL blog](https://tvl.fyi/) posts |
| Compatibility | Incomplete vs CppNix / [Lix](lix.md)—regression-tested niches exist; full feature parity and CLI drop-in do **not** |
| Production role | Research / alternative implementation; not a NixOS host swap |
| Active modular line | Prefer [Snix](snix.md) for post-2025-03 independent development of this architecture |
| `tvix.dev` | Do not rely on it as a stable project URL (TLS / content unreliable as of last check); use TVL and Snix first-party sources |

### Who and where

Canonical technical home is the TVL monorepo path `//tvix` ([depot about](https://code.tvl.fyi/about/tvix)). Historical design goals and status updates live on the TVL blog ([rewrite announcement](https://tvl.fyi/blog/rewriting-nix), [August 2024 status](https://tvl.fyi/blog/tvix-update-august-24)). Snix’s [announcement](https://snix.dev/blog/announcing-snix/) is the primary source for the 2025 fork/rename facts.

### Architecture

Unlike a single monolithic daemon-plus-CLI, Tvix splits concerns: a language evaluator (`tvix-eval`), Nix-compat libraries (derivations, hashes, encodings), content-addressed blob/tree storage (`tvix-castore`) plus Nix path metadata (`tvix-store`), and builders that can use OCI / `runc`-style sandboxing rather than Nix’s custom sandbox code. The evaluator keeps I/O behind an `EvalIO` interface so callers can plug different stores or filesystem models. Later TVL status work also covers store composition, fetchers, tracing, and `nar-bridge` as a binary-cache lens—still under experimental / incomplete compatibility.

### Goals (stated by TVL)

Full reuse of nixpkgs expressions; faster evaluation; first-class IFD-style “drive builds on IO” without a hard eval-then-build wall; clear protocols between evaluator, builder, and store. TVL frames Tvix as an alternative implementation to improve the ecosystem, not as a replacement for Nix itself.

### Maturity caveats

Pieces such as eval regression tests against nixpkgs derivations, store backends, and preliminary CLI/REPL exist; full feature parity, production NixOS replacement, and “just swap binaries” workflows do not. Prefer CppNix or Lix for real systems; compare [Snix](snix.md) for the forked continuation of this modular stack under independent infrastructure.

## Examples

Illustrative component map (names from TVL / Tvix docs; not an install recipe):

```text
tvix-eval     → Nix language evaluation (I/O via EvalIO)
nix-compat    → derivations, ATerm fingerprints, wire formats
tvix-castore  → content-addressed blobs / directory trees
tvix-store    → Nix store-path metadata + cache compatibility
builder       → realize derivations (e.g. OCI / runc-oriented work)
```

Typical research use: evaluate expressions and compare `drvPath` / `outPath` with CppNix for the same nixpkgs input—Tvix’s correctness path—rather than `nixos-rebuild` on a machine. For current crates and tooling under independent hosting, follow [Snix](snix.md) docs instead.

## See also

- [Snix](snix.md) — fork continuation of the modular Tvix stack (announced 2025-03-16)
- [CppNix](cpp-nix.md) — reference C++ Nix implementation
- [Lix](lix.md) — community fork of the C++ lineage
- [Nix Evaluators](README.md) — evaluator index
- [Timeline](../../15-history-and-governance/timeline.md) — project history context

## References

- [Tvix: We are rewriting Nix](https://tvl.fyi/blog/rewriting-nix) — TVL announcement and high-level goals
- [Tvix Status — August 2024](https://tvl.fyi/blog/tvix-update-august-24) — builds, eval correctness, store work (pre-Snix fork)
- [Tvix in the TVL depot](https://code.tvl.fyi/about/tvix) — monorepo entry / about
- [Announcing Snix](https://snix.dev/blog/announcing-snix/) — 2025-03-16 fork: new name, dedicated infra
