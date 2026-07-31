---
status: complete
---

# Lix

## Overview

[Lix](https://lix.systems/) is a community-maintained implementation of the Nix language and package manager. It forked from [CppNix](cpp-nix.md) at last shared release **2.18** and stays in that lineage: cleanup, compatibility, and deliberate UX—not a greenfield rewrite of the evaluator or store.

For many workflows it is a practical substitute for CppNix. The project states compatibility with existing Nix expressions and documents use as the Nix implementation under NixOS, Home Manager, and nix-darwin. That is not identical feature-set parity: Lix publishes technical differences and releases on its own schedule. Governance and hosting are separate from upstream CppNix; prefer first-party Lix docs over secondary narrative. Broader fork context: [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md).

## Details

### Maturity (last checked 2026-07-31)

| Aspect | Stamp |
|--------|--------|
| Lineage | Soft fork of CppNix (shared root at 2.18); C++ codebase with meson builds and planned gradual Rust |
| Compatibility (stated) | Existing Nix expressions; not lockstep CLI / experimental-feature parity with every CppNix release |
| Production role | Usable day-to-day daemon/CLI when deliberately installed; NixOS / Home Manager / nix-darwin supported via config overlays |
| Vs [Snix](snix.md) | Different approach: evolve the CppNix foundation vs modular from-scratch Rust ([About Lix](https://lix.systems/about/)) |
| Verify before pinning | Version output, documented deltas, and Lix manual for your release |

Treat the table as a snapshot. Re-check [About Lix](https://lix.systems/about/) when a claim about deltas or Flakes matters to a deployment.

### What it is

Lix implements the same core model as other Nix evaluators: pure package builds, the Nix store, channels/substituters, and the Nix expression language. The [reference manual](https://docs.lix.systems/) covers language, store, GC, multi-user, and binary-cache behavior for the Lix tree.

### Relation to CppNix

Per [About Lix](https://lix.systems/about/), the fork aims to remain compatible while allowing language and tooling evolution. Stated foci include code cleanup, better errors, meson-based builds, selective stability guarantees (what is frozen vs allowed to change), community-owned infrastructure, and planned gradual Rust—not a total rewrite story.

Documented divergences (subject to change; check upstream for your version) include: no lazy trees as in upstream CppNix (a functionally equivalent replacement is planned); no usable content-addressed derivations while a rewrite is planned; no libgit2; deprecation of some legacy language footguns; REPL and performance work relative to 2.18. Do not assume every CppNix flag or experimental feature exists or behaves the same.

### Relation to Tvix / Snix

[About Lix](https://lix.systems/about/) contrasts Lix with [Snix](snix.md): Snix is a from-scratch Rust reimplementation aiming at modular second-generation components; Lix evolves the CppNix lineage toward a stable foundation without breaking clients along the way. The projects share some goals and developer overlap; Lix states openness to integrating Snix components where it makes sense. [Tvix](tvix.md) is the TVL monorepo project that Snix forked from—compare goals there rather than treating any pair as drop-in equivalents.

### Flakes and platforms

Flakes remain supported; Lix says it will not remove Flake support, while aiming to make Flake-exclusive capabilities less special over time and to tighten some Flake behavior for dependability. First-party docs cover Linux and macOS; NixOS and nix-darwin installs go through configuration overlays rather than only the standalone installer.

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
- [Tvix](tvix.md) — TVL monorepo Rust reimplementation (Snix’s prior home)
- [Snix](snix.md) — modular from-scratch Rust stack (contrasted by Lix)
- [Nix Evaluators](README.md) — evaluator index
- [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md) — governance and fork landscape

## References

- [Lix](https://lix.systems/) — project site
- [About Lix](https://lix.systems/about/) — fork lineage (CppNix 2.18), goals, vs Snix, Flakes stance, technical differences
- [Installing Lix](https://lix.systems/install/) — installer, upgrades, NixOS / nix-darwin notes
- [Lix reference manual](https://docs.lix.systems/) — language, store, and CLI documentation
- [Lix governance](https://lix.systems/governance/) — core / community / committer roles
