---
status: complete
last-checked: 2026-07
---

# Tracking Stabilization

## Overview

Experimental features move through a predictable **lifecycle**: an idea becomes a merged implementation behind a flag, ships in a Nix release as opt-in behavior, and eventually either **stabilizes** (the flag is removed and the behavior is always on) or is **removed** entirely. This page is about **how to track** that progress—not a second catalog of every flag.

**Version stamp (Phase 5.1 re-check, 2026-07-31):** named experimental-feature flags exist since **Nix 2.4**. Facts below match the Nix **stable** manual for **2.34.x** ([experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) → `/manual/nix/2.34/…`; manual title **2.34.9**) and local `nix (Nix) 2.34.8`. Flag names and status change between releases—re-check that manual page and [release notes](https://nix.dev/manual/nix/stable/release-notes/) when upgrading.

Upstream sources of truth are that manual list, release notes, and per-feature tracking issues or milestones on the [Nix repository](https://github.com/NixOS/nix). This wiki’s sibling leaf pages document selected flags; refresh this page when a new Nix stable release or NixOS `nix` pin bump lands. Do not invent stabilization dates—treat a feature as stabilized only when release notes remove its flag.

For how flags are enabled and how they relate to RFCs, see [Feature flags overview](feature-flags-overview.md).

## Details

**Lifecycle (from the [manual](https://nix.dev/manual/nix/stable/development/experimental-features.html)).**

1. **Idea** — design discussion, sometimes an [RFC](../15-history-and-governance/rfc-process.md), sometimes not.
2. **PR with flag** — implementation merges with a named flag, **disabled by default**.
3. **Experimental in release** — users who opt in exercise real workflows; behavior may change between releases.
4. **Outcome** — **stabilize** (remove the flag; behavior becomes normal Nix) or **remove** (drop implementation and flag).

Stabilization is a judgment call, not a schedule. The project typically looks for:

- **Evidence of use** — real configs, flakes, and tooling depend on the feature in production-like settings.
- **Design confidence** — APIs and semantics are unlikely to need breaking changes.
- **Understood interactions** — behavior with other flags, the store, and downstream tools is documented and predictable.
- **Acceptable maintenance** — the cost of supporting the feature long term is justified.

**RFCs vs flags.** [RFCs](https://github.com/NixOS/rfcs) and feature flags are **orthogonal**. An RFC socializes and records a design; a flag gates whether an **implementation** is available. A feature can ship flagged without an RFC, an RFC can precede code by months, or both can run in parallel. Process docs: [RFC process](../15-history-and-governance/rfc-process.md). Flag mechanics: [Feature flags overview](feature-flags-overview.md).

**Where to look (practical tracking).**

| Source | What it tells you |
|--------|-------------------|
| [experimental-features.html](https://nix.dev/manual/nix/stable/development/experimental-features.html) | Current flag names and short descriptions for **your manual version** (authoritative list) |
| [Release notes](https://nix.dev/manual/nix/stable/release-notes/) | When flags were added, changed, stabilized, or removed |
| Nix GitHub [issues](https://github.com/NixOS/nix/issues) / [milestones](https://github.com/NixOS/nix/milestones) | Per-feature stabilization work (linked from many manual entries) |
| `nix.conf` / NixOS `nix.settings` | What **you** have enabled (see [Feature flags overview](feature-flags-overview.md)) |
| This wiki — leaf pages below | Focused notes for selected flags; not a substitute for the manual |

**As of Nix 2.34.x (stable manual 2.34.9).** The manual lists **21** named flags. Widely used flags such as [`flakes`](flakes.md) and [`nix-command`](nix-command.md) remain **experimental**—still listed with tracking links; not stabilized in 2.34. Example of a completed lifecycle in this series: `no-url-literals` was **stabilized** in 2.34 (flag removed; behavior now via `lint-url-literals`—see [2.34 release notes](https://nix.dev/manual/nix/stable/release-notes/rl-2.34.html)). Flags without a dedicated wiki leaf are catalogued in [Experimental backlog](experimental-backlog.md) (for example `blake3-hashes`, `external-builders`, `fetch-closure`, `local-overlay-store`). Treat the manual as complete; this page’s sibling inventory is a curated subset.

**Maintenance cadence for this wiki.** After each Nix stable release (and when NixOS pins a new `nix` version—see [Release cadence](../15-history-and-governance/release-cadence.md)):

1. Skim release notes for experimental-feature **adds**, **removals**, and **stabilizations**.
2. Diff the manual’s flag list against [Feature flags overview](feature-flags-overview.md) and [Experimental backlog](experimental-backlog.md); add or retire sibling leaves as flags appear or disappear.
3. Re-stamp version numbers on this page and those two cousins; update cross-links if tracking issues or milestones move; do **not** speculate on future stabilization dates.

**Inventory (sibling leaves).** Individual flags are documented on dedicated pages—use those for behavior and enablement, not this page:

- [nix-command](nix-command.md) — unified `nix` CLI
- [flakes](flakes.md) — flake format and `nix flake` (concept: [Flake](../02-concepts/flake.md); workflows: [Flakes](../07-flakes/README.md))
- [ca-derivations](ca-derivations.md) — content-addressed derivations
- [fetch-tree-and-git](fetch-tree-and-git.md) — `fetchTree` / git fetch experiments
- [dynamic-derivations](dynamic-derivations.md) — dynamic derivations
- [impure-derivations](impure-derivations.md) — impure derivations
- [recursive-nix](recursive-nix.md) — Nix-in-Nix builds
- [auto-allocate-uids](auto-allocate-uids.md) — UID allocation in the sandbox
- [cgroups](cgroups.md) — cgroup build isolation
- [pipe-operators-and-lang](pipe-operators-and-lang.md) — language experiments (pipe operators, etc.)

The domain index is [Experimental Features](README.md). New flags may appear in a release before this list is updated—always check the [manual](https://nix.dev/manual/nix/stable/development/experimental-features.html) first.

## Examples

**See which experimental features are effective on this machine** (merged from `experimental-features` and `extra-experimental-features` in nix.conf). Requires the `nix-command` feature:

```bash
nix config show experimental-features
```

Example output (verified on Nix **2.34.8**; yours will differ):

```
fetch-tree flakes nix-command
```

**Inspect raw nix.conf settings** (when you need the split between replace vs append):

```bash
grep -E 'experimental-features|extra-experimental-features' /etc/nix/nix.conf ~/.config/nix/nix.conf 2>/dev/null
```

**After upgrading Nix**, read the release notes section for experimental features before assuming a flag still exists or behaves the same:

```bash
nix --version
# Then open: https://nix.dev/manual/nix/stable/release-notes/
# And the flag list: https://nix.dev/manual/nix/stable/development/experimental-features.html
```

**Follow stabilization work** for a specific flag: open its entry on [experimental-features.html](https://nix.dev/manual/nix/stable/development/experimental-features.html)—many entries link to a GitHub issue or milestone (e.g. [flakes](flakes.md) points at its tracking milestone).

## References

- [Nix manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — lifecycle (since Nix 2.4), flag list, tracking links (Nix **2.34.x** / manual **2.34.9**)
- [Nix manual — Release notes](https://nix.dev/manual/nix/stable/release-notes/) — stabilization and removal announcements
- [Nix manual — nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `experimental-features` and `extra-experimental-features`
- [Nix manual — `nix config show`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-config-show.html) — show effective configuration values
- [NixOS/rfcs](https://github.com/NixOS/rfcs) — design proposals (separate from flag status)
- [NixOS/nix — issues and milestones](https://github.com/NixOS/nix) — implementation and stabilization tracking

## See also

- [Feature flags overview](feature-flags-overview.md) — enabling flags, full 2.34 inventory
- [flakes](flakes.md) — `flakes` flag (still experimental in 2.34.x)
- [nix-command](nix-command.md) — unified CLI flag (still experimental in 2.34.x)
- [Experimental backlog](experimental-backlog.md) — flags without dedicated wiki leaves
- [RFC process](../15-history-and-governance/rfc-process.md) — community design process
- [Release cadence](../15-history-and-governance/release-cadence.md) — when to re-check this page
