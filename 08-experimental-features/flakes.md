---
status: complete
---

# flakes

## Overview

The **`flakes`** experimental feature flag enables Nix’s flake format and the `nix flake` subcommands. Flakes provide a standardized project entry point (`flake.nix`, `flake.lock`) and integrate with the Nix 3 CLI. The flag remains **experimental** as of **Nix 2.34.x** (stable manual [2.34.9 `flakes` entry](https://nix.dev/manual/nix/2.34/development/experimental-features.html#xp-feature-flakes); verified on **2.34.8**): the interface can change in backwards-incompatible ways until stabilisation, even though flakes are widely used in practice for new projects.

Enabling `flakes` is almost always paired with [`nix-command`](nix-command.md). Schema, workflows, registries, and migration belong in [Flakes](../07-flakes/README.md)—this page covers the flag, how to turn it on, and how it relates to other experimental features. For vocabulary before diving in, see [Flake (concept)](../02-concepts/flake.md).

## Details

**What the flag unlocks.** With `flakes` enabled, Nix accepts flake references in commands such as `nix build`, `nix run`, and `nix develop`, and exposes `nix flake` for lockfile management, input updates, and inspection. The on-disk format and CLI behaviour are documented in the [Nix manual — `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html); the original design is [RFC 49](https://github.com/NixOS/rfcs/pull/49). Deep dive material lives under [07-flakes](../07-flakes/README.md): [flake.nix schema](../07-flakes/anatomy/flake-nix-schema.md), [inputs and outputs](../07-flakes/anatomy/inputs-and-outputs.md), [lockfile](../07-flakes/anatomy/lockfile.md), [registries and refs](../07-flakes/registries-and-refs.md), and [workflows](../07-flakes/workflows/README.md).

**Experimental status.** Like all flags listed under [experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html), `flakes` is disabled by default and must be opted into explicitly. Feature flags have existed since Nix 2.4; `flakes` is still listed as experimental in the **2.34.x** series—do not assume stabilisation without release notes. Stabilisation progress is tracked on the [flakes tracking milestone](https://github.com/NixOS/nix/milestone/27); see [Tracking stabilization](tracking-stabilization.md) for the general lifecycle.

**Relationship to `fetch-tree`.** Enabling `flakes` also enables the [`fetch-tree`](fetch-tree-and-git.md) built-in: the manual states that the flakes feature flag always enables `fetch-tree`. You can enable `fetch-tree` alone to try tree fetching in isolation, but full flake workflows require `flakes`.

**Not covered here.** Input/output schema, lockfile semantics, pure evaluation, and publishing flakes are documented under [07-flakes](../07-flakes/README.md). For how experimental flags fit together, see [Feature flags overview](feature-flags-overview.md).

## Examples

Add both flags to `nix.conf` (user or system):

```ini
experimental-features = nix-command flakes
```

After restarting the daemon or opening a new shell, flake commands work (Nix 2.34.x; `nix flake` still prints the experimental-interface warning):

```bash
nix flake init
nix build .
nix run nixpkgs#hello
```

One-off enablement without editing `nix.conf`:

```bash
nix --extra-experimental-features 'nix-command flakes' flake metadata .
```

Without `flakes`, the same invocations fail with (Nix 2.34.8):

```text
error: experimental Nix feature 'flakes' is disabled; add '--extra-experimental-features flakes' to enable it
```

## References

- [Nix manual — experimental features (`flakes`, 2.34)](https://nix.dev/manual/nix/2.34/development/experimental-features.html#xp-feature-flakes) — version-stamped flag entry (manual **2.34.9**)
- [Nix manual — experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — flag lifecycle and current `flakes` entry
- [Nix manual — `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — flake format, inputs, outputs, and lock file
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — high-level introduction
- [RFC 49 — Flakes](https://github.com/NixOS/rfcs/pull/49) — original design specification
- [flakes tracking milestone](https://github.com/NixOS/nix/milestone/27) — stabilisation tracking on the Nix repository

## See also

- [nix-command](nix-command.md) — companion flag for Nix 3 subcommands
- [Feature flags overview](feature-flags-overview.md) — enabling flags and full inventory
- [Tracking stabilization](tracking-stabilization.md) — experimental → stable path
- [flake.nix schema](../07-flakes/anatomy/flake-nix-schema.md) — outputs attrset and evaluation entry
- [fetchTree and Git](fetch-tree-and-git.md) — `fetch-tree` built-in (always enabled with `flakes`)
- [Experimental backlog](experimental-backlog.md) — other experimental flags without wiki leaves
