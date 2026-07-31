---
status: complete
last-checked: 2026-07
---

# Feature Flags Overview

## Overview

**Experimental features** are Nix capabilities that are still being iterated on: they may change behavior, gain new requirements, or be removed entirely. Since Nix 2.4, each one is guarded by a named **feature flag** that must be enabled explicitly—nothing experimental runs unless you opt in via configuration or a CLI flag.

Before 2.4, unstable behavior often shipped without a clear switch, which made it hard to tell what was supported versus in flux. Flags exist so risky changes (language extensions, new CLI surfaces, store semantics) can land in releases while remaining off by default until the project is confident in the design.

This page explains how flags work, how to enable them, and how they relate to stabilization and RFCs. For individual flags and their status, see the sibling pages in this domain and [Tracking Stabilization](tracking-stabilization.md).

**Version stamp (Phase 5.1 re-check, 2026-07-31):** facts and the flag inventory below match the [Nix stable manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) for **Nix 2.34.x** (stable → `/manual/nix/2.34/…`; manual title **2.34.9**; local `nix (Nix) 2.34.8`). Re-check that page and [release notes](https://nix.dev/manual/nix/stable/release-notes/) after each Nix stable release or NixOS `nix` pin bump—flag names appear and disappear between releases. `flakes` and `nix-command` remain **experimental** in this series (still listed; not stabilized).

## Details

**Why flags exist.** A flag guards a change when experience might still lead to revert or compatibility breaks: new Nix language constructs, CLI command shapes, or store/evaluation behavior that affects downstream tooling. Shipping behind a flag lets early adopters try real workflows without implying stability for everyone.

**Typical lifecycle** (from the manual):

1. A change merges with its flag **disabled by default**.
2. A Nix release ships; users who want the behavior enable the flag.
3. Over time, the feature either **stabilizes** (flag removed, behavior always on) or is **dropped** (implementation and flag removed).

Stabilization is a judgment call, not a timer. Common criteria include evidence of real-world use, confidence in the API/design, understood interactions with other features, and acceptable maintenance burden. [Tracking Stabilization](tracking-stabilization.md) summarizes what has landed versus what remains experimental in this wiki.

**Relationship to RFCs.** Feature flags and [RFCs](https://github.com/NixOS/rfcs) are orthogonal. An RFC documents and socializes a design; a flag controls whether an **implementation** is available. A feature can ship flagged without an RFC, an RFC can precede a flagged implementation, or both can run in parallel—the flag is about iteration safety, not community process.

**Enabling flags.**

| Mechanism | Where |
|-----------|--------|
| `experimental-features = …` | [nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — replaces the list for that setting (default: empty) |
| `extra-experimental-features = …` | nix.conf — appends to `experimental-features` |
| `--extra-experimental-features …` | One-shot on a single `nix` invocation (appends) |
| `--experimental-features …` / `--option experimental-features …` | One-shot replace of the effective list |
| `nix.settings.experimental-features` | NixOS module — writes the corresponding nix.conf settings |

Flag values are space-separated names (e.g. `nix-command flakes`). Inspect the effective set with `nix config show experimental-features` (needs `nix-command`). Do not assume a flag from an older blog post still exists without checking the manual for your Nix version.

**Flags available in Nix 2.34.x stable** (21 names from the manual; not a full catalog of behavior):

| Flag | Wiki leaf (if any) |
|------|--------------------|
| `auto-allocate-uids` | [auto-allocate-uids](auto-allocate-uids.md) |
| `blake3-hashes` | — |
| `ca-derivations` | [ca-derivations](ca-derivations.md) |
| `cgroups` | [cgroups](cgroups.md) |
| `configurable-impure-env` | — |
| `daemon-trust-override` | — |
| `dynamic-derivations` | [dynamic-derivations](dynamic-derivations.md) |
| `external-builders` | — |
| `fetch-closure` | — |
| `fetch-tree` | [fetch-tree-and-git](fetch-tree-and-git.md) |
| `flakes` | [flakes](flakes.md) |
| `git-hashing` | [fetch-tree-and-git](fetch-tree-and-git.md) |
| `impure-derivations` | [impure-derivations](impure-derivations.md) |
| `local-overlay-store` | — |
| `mounted-ssh-store` | — |
| `nix-command` | [nix-command](nix-command.md) |
| `parse-toml-timestamps` | — |
| `pipe-operators` | [pipe-operators-and-lang](pipe-operators-and-lang.md) |
| `read-only-local-store` | — |
| `recursive-nix` | [recursive-nix](recursive-nix.md) |
| `verified-fetches` | [fetch-tree-and-git](fetch-tree-and-git.md) |

Common entry points among those: [nix-command](nix-command.md), [flakes](flakes.md) (concept: [Flake](../02-concepts/flake.md); workflows: [Flakes](../07-flakes/README.md)), and [ca-derivations](ca-derivations.md). Other flags and language experiments live under [Experimental Features](README.md); the nine flags without dedicated leaves are listed in [Experimental backlog](experimental-backlog.md).

**Maintenance cadence.** After each Nix stable / NixOS `nix` pin bump: re-diff this table to the manual, move rows to or from [Experimental backlog](experimental-backlog.md) as leaves are written, and re-stamp [Tracking Stabilization](tracking-stabilization.md). See [Release cadence](../15-history-and-governance/release-cadence.md).

## Examples

**Persistent enable in `nix.conf`** — typical for flakes and the new CLI:

```ini
experimental-features = nix-command flakes
```

**Append without replacing an existing list:**

```ini
extra-experimental-features = ca-derivations
```

**One-shot on the command line** (does not change nix.conf):

```bash
nix --extra-experimental-features 'nix-command flakes' flake show .
```

**NixOS** (declarative equivalent):

```nix
nix.settings.experimental-features = [ "nix-command" "flakes" ];
```

**Inspect what is actually enabled:**

```bash
nix config show experimental-features
```

## References

- [Nix manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — flag list and lifecycle (Nix **2.34.x** / manual **2.34.9**)
- [Nix manual — nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `experimental-features` / `extra-experimental-features` (default empty)
- [Nix manual — Release notes](https://nix.dev/manual/nix/stable/release-notes/) — when flags were added, changed, or stabilized
- [Nix manual — `nix config show`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-config-show.html) — inspect effective settings (needs `nix-command`)

## See also

- [nix-command](nix-command.md) — experimental unified CLI
- [flakes](flakes.md) — flakes feature flag
- [Tracking Stabilization](tracking-stabilization.md) — how to track experimental → stable
- [Experimental backlog](experimental-backlog.md) — manual-only flags without dedicated leaves
- [nix.conf](../05-cli-and-tooling/config/nix-conf.md) — configuration file that holds these settings
- [Release cadence](../15-history-and-governance/release-cadence.md) — when to re-check this inventory
