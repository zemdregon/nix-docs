---
status: complete
---

# Lix

## Overview

[Lix](https://lix.systems/) is a community-maintained implementation of the Nix language and package manager. It forked from [CppNix](cpp-nix.md) (last shared release: 2.18) and positions itself around correctness, usability, and deliberate stability—cleanup and maintenance over flashy divergence.

For many workflows it is a practical substitute for CppNix: the project states compatibility with existing Nix expressions and documents use as the Nix implementation under NixOS, Home Manager, and nix-darwin. That is not a claim of identical feature sets; Lix publishes explicit technical differences from CppNix and evolves on its own schedule.

**Maturity (last checked 2026-07-31):** production-oriented compatible fork of the C++ lineage—not the NixOS default, but positioned for day-to-day use with selective stability guarantees and community-owned infrastructure. Prefer first-party Lix docs over secondary narrative. Broader fork context: [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md). Glossary: [Lix](../../glossary.md#lix).

## Details

**What it is.** Lix implements the same core model as other Nix evaluators: pure package builds, the Nix store, channels/substituters, and the Nix expression language. The reference manual introduces Lix as an implementation of Nix with the usual store, GC, multi-user, and binary-cache story.

**Relation to CppNix.** Per [About Lix](https://lix.systems/about/), Lix is a fork of CppNix aimed at remaining compatible while allowing language and tooling evolution. Stated foci include code cleanup, better errors, meson-based builds, and planned gradual Rust use—not a greenfield rewrite. Documented divergences (subject to change; check upstream) include: no lazy trees as in upstream CppNix (a functionally equivalent replacement is planned); no usable content-addressed derivations while a rewrite is planned; no libgit2; deprecation of some legacy language footguns; REPL and performance work relative to 2.18. Do not assume every CppNix flag or experimental feature exists or behaves the same—verify in Lix docs for your version.

**Relation to Tvix / Snix.** [About Lix](https://lix.systems/about/) contrasts Lix with [Snix](snix.md): Snix is a from-scratch Rust reimplementation aiming at modular second-generation components; Lix evolves the CppNix lineage toward a stable foundation without breaking clients along the way. [Tvix](tvix.md) is the TVL-side Rust effort in this wiki’s evaluator set—compare project goals there rather than treating any pair as drop-in equivalents.

**Stability and community.** Lix markets clear stability boundaries (what is frozen vs allowed to change), community-owned hosting (e.g. avoiding sole dependence on corporate forges), and volunteer governance with published conflict-of-interest posture. Flakes remain supported; the project says it will not remove Flake support, while aiming to make Flake-exclusive capabilities less special over time and to tighten some Flake behavior for dependability. None of that is a guarantee of lockstep CLI or experimental-feature parity with CppNix.

**Platforms.** First-party docs: Linux and macOS; NixOS and nix-darwin installs go through configuration overlays rather than only the standalone installer.

## Examples

**Fresh install (Linux / macOS, no existing Nix daemon)** — from the [Lix install guide](https://lix.systems/install/):

```bash
curl -sSf -L https://install.lix.systems/lix | sh -s -- install
```

Prefer the current instructions on that page over copying version-pinned upgrade scripts from elsewhere; upgrade paths for existing CppNix/Lix installs are documented separately there.

**Confirm the binary is Lix** (wording from upstream install docs; version numbers change):

```bash
nix --version
# expect output containing "Lix", e.g. nix (Lix, like Nix) …
```

On NixOS or nix-darwin, follow the configuration steps linked from [Installing Lix](https://lix.systems/install/) rather than only the curl installer.

## See also

- [CppNix](cpp-nix.md) — upstream / reference Nix implementation Lix forked from
- [Tvix](tvix.md) — separate Rust Nix implementation (TVL)
- [Snix](snix.md) — from-scratch Rust Nix implementation (contrasted by Lix)
- [Nix Evaluators](README.md) — evaluator index
- [Glossary](../../glossary.md#lix) — CppNix / Lix / Tvix / Snix term index
- [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md) — governance and fork landscape
- [Release cadence](../../15-history-and-governance/release-cadence.md) — NixOS channels vs which Nix binary you run

## References

- [Lix](https://lix.systems/) — project site
- [About Lix](https://lix.systems/about/) — fork lineage (CppNix 2.18), goals, vs Snix, Flakes stance, technical differences
- [Lix reference manual](https://docs.lix.systems/) — language, store, and CLI documentation
