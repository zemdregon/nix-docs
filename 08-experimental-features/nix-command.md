---
status: complete
---

# nix-command

## Overview

The **`nix-command`** experimental feature enables the unified Nix 3 CLI: subcommands such as `nix build`, `nix run`, `nix develop`, `nix eval`, and `nix flake` under a single `nix` entry point. It replaces the classic tool split (`nix-build`, `nix-shell`, `nix-env`, and related scripts) with one command tree documented in the [new CLI reference](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html).

As of **Nix 2.34.x** (stable manual title **2.34.9**; verified on **2.34.8**), the feature remains **experimental**—subcommand names, flags, installable syntax, and output formats can change between releases. Do not treat it as stabilized unless release notes say so. Feature flags themselves date to **Nix 2.4**. Enable the flag in `nix.conf` or pass it per invocation; see [Feature flags overview](feature-flags-overview.md) for the general mechanism.

## Details

**What it unlocks.** With `nix-command`, the `nix` binary exposes the modern command surface: build and run derivations, enter dev shells, evaluate expressions, search and profile packages, copy store paths, and inspect store objects. Many subcommands share **installables** (flake refs, `--file` / `--expr`, store paths) plus common flags such as `--json`. Installables are themselves part of this unstable surface—see the [manual warning on `nix`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html).

**Not the same as flakes.** `nix-command` does **not** enable [flakes](flakes.md). Flake-oriented workflows—`nix build .`, `nix flake show`, registry refs like `nixpkgs#hello`—require **both** `nix-command` and `flakes`. You can use the new CLI without flakes via `--file` / `--expr` (and store paths). In practice both flags are enabled together on systems that follow current nix.dev guidance.

**Relation to classic CLI.** Classic commands remain available when Nix is installed; enabling `nix-command` does not remove them. New documentation and community examples increasingly assume the unified CLI. Command-by-command migration lives under [CLI and tooling](../05-cli-and-tooling/README.md) (classic vs [modern](../05-cli-and-tooling/modern-cli/README.md)).

**Stabilization.** Upstream tracks work under the [nix-command stabilisation milestone](https://github.com/NixOS/nix/milestone/28) (still open against Nix **2.34.x** as of this pass). Related CLI review is discussed in the [CLI stabilization effort](https://github.com/NixOS/nix/issues/7701). No invented stabilization date—follow release notes and that milestone; see [Tracking stabilization](tracking-stabilization.md).

## Examples

Enable the feature for a one-shot evaluation (no flakes required). Verified with Nix **2.34.8**:

```bash
nix --experimental-features 'nix-command' eval --expr '1 + 1'
# → 2
```

With only `nix-command`, flake installables fail until `flakes` is also enabled:

```bash
nix --experimental-features 'nix-command' flake show
# error: experimental Nix feature 'flakes' is disabled; …
```

Typical persistent enablement (new CLI + flakes) in `nix.conf`:

```ini
experimental-features = nix-command flakes
```

Or on NixOS / Home Manager:

```nix
nix.settings.experimental-features = [ "nix-command" "flakes" ];
```

After that, common modern invocations work without extra flags:

```bash
nix build .
nix run nixpkgs#hello
nix develop
nix flake show
```

## References

- [Nix manual — `nix-command` (experimental features)](https://nix.dev/manual/nix/stable/development/experimental-features.html#xp-feature-nix-command) — flag description (Nix **2.34.x** / manual **2.34.9**)
- [Nix manual — `nix` (new CLI)](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html) — unified command reference and installables
- [nix-command stabilisation milestone](https://github.com/NixOS/nix/milestone/28) — upstream tracking
- [CLI stabilization effort](https://github.com/NixOS/nix/issues/7701) — incremental CLI review notes

## See also

- [Feature flags overview](feature-flags-overview.md) — how experimental features are enabled
- [flakes](flakes.md) — companion feature for flake inputs, outputs, and lockfiles
- [Tracking stabilization](tracking-stabilization.md) — experimental → stable path
- [Modern CLI](../05-cli-and-tooling/modern-cli/README.md) — `nix build` / `develop` / `run` and related guides
- [Experimental backlog](experimental-backlog.md) — other experimental flags without wiki leaves
- [flake.nix schema](../07-flakes/anatomy/flake-nix-schema.md) — flake outputs when using both flags
