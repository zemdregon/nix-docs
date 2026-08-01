---
status: complete
last-checked: 2026-07
---

# Experimental backlog

## Overview

This page lists **experimental feature flags that do not yet have dedicated wiki leaves** in this domain. Each entry is a one-line purpose and a pointer to the upstream manual—not a deep dive.

For **how flags move from experimental to stable**, use [Tracking Stabilization](tracking-stabilization.md) as the lifecycle hub. For **enabling flags and the full Nix 2.34 inventory**, see [Feature flags overview](feature-flags-overview.md). Flags already covered here have sibling leaf pages linked from those two pages.

**Version stamp (Phase 5.1 re-check, 2026-07-31):** backlog checked against the Nix **stable** manual for **2.34.x** ([experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) → `/manual/nix/2.34/…`; manual title **2.34.9**; local `nix (Nix) 2.34.8`). Flag names and descriptions change between releases—re-check that page and [release notes](https://nix.dev/manual/nix/stable/release-notes/) when upgrading.

## Details

**Maintenance cadence.** After each Nix stable release (and when NixOS pins a new `nix` version—see [Release cadence](../15-history-and-governance/release-cadence.md)):

1. Diff the [manual flag list](https://nix.dev/manual/nix/stable/development/experimental-features.html) against this backlog, [Feature flags overview](feature-flags-overview.md), and sibling leaves.
2. Move flags off this page when a dedicated leaf is written; add new manual-only flags here; drop rows when a flag is stabilized or removed (release notes).
3. Do **not** invent stabilization dates—follow release notes and per-flag tracking issues linked from the manual.

**Flags with wiki leaves (not backlog).** Use these for behavior and enablement instead of this page:

| Flag | Wiki leaf |
|------|-----------|
| `auto-allocate-uids` | [auto-allocate-uids](auto-allocate-uids.md) |
| `ca-derivations` | [ca-derivations](ca-derivations.md) |
| `cgroups` | [cgroups](cgroups.md) |
| `dynamic-derivations` | [dynamic-derivations](dynamic-derivations.md) |
| `fetch-tree` | [fetch-tree-and-git](fetch-tree-and-git.md) |
| `flakes` | [flakes](flakes.md) |
| `git-hashing` | [fetch-tree-and-git](fetch-tree-and-git.md) |
| `impure-derivations` | [impure-derivations](impure-derivations.md) |
| `nix-command` | [nix-command](nix-command.md) |
| `pipe-operators` | [pipe-operators-and-lang](pipe-operators-and-lang.md) |
| `recursive-nix` | [recursive-nix](recursive-nix.md) |
| `verified-fetches` | [fetch-tree-and-git](fetch-tree-and-git.md) |

**Backlog (Nix 2.34.x stable manual — 9 of 21 flags).** No dedicated leaf yet—see the manual section for each flag and its GitHub tracking link:

| Flag | One-line purpose |
|------|------------------|
| `blake3-hashes` | Enables support for BLAKE3 hashes. |
| `configurable-impure-env` | Allows the [`impure-env`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-impure-env) nix.conf setting. |
| `daemon-trust-override` | Lets `nix-daemon` force trust or distrust of clients (testing and `nix-daemon --stdio` experiments). |
| `external-builders` | Enables support for external builders / sandbox providers. |
| `fetch-closure` | Enables the `fetchClosure` built-in in the Nix language. |
| `local-overlay-store` | Allows use of the local overlay store. |
| `mounted-ssh-store` | Allows use of the mounted SSH store. |
| `parse-toml-timestamps` | Allows parsing of timestamps in `builtins.fromTOML`. |
| `read-only-local-store` | Allows the `read-only` parameter in local store URIs. |

Authoritative descriptions and stabilization tracking: [Nix manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) (one section per flag above).

## Examples

**See which experimental features are effective on this machine** (requires `nix-command`):

```bash
nix config show experimental-features
```

Example output (Nix 2.34.x; yours will differ):

```
fetch-tree flakes nix-command
```

**Confirm the full upstream list for your Nix version**—the manual is the source of truth, not this wiki table:

```bash
nix --version
# Open: https://nix.dev/manual/nix/stable/development/experimental-features.html
```

After upgrading, skim [release notes](https://nix.dev/manual/nix/stable/release-notes/) for flags added, changed, stabilized, or removed before assuming a backlog entry still applies.

## References

- [Nix manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — flag list, descriptions, tracking links (Nix **2.34.x** / manual **2.34.9**)
- [Nix manual — Release notes](https://nix.dev/manual/nix/stable/release-notes/) — when flags appear, change, or stabilize
- [Nix manual — nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `experimental-features` / `extra-experimental-features`
- [Nix manual — `nix config show`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-config-show.html) — inspect effective configuration

## See also

- [Tracking Stabilization](tracking-stabilization.md) — lifecycle and how to track stabilization
- [Feature flags overview](feature-flags-overview.md) — enabling flags, full 2.34 inventory
- [Experimental Features](README.md) — domain index
- [Release cadence](../15-history-and-governance/release-cadence.md) — Nix / NixOS release rhythm
