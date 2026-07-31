---
status: complete
---

# Migration from Channels

## Overview

**Channels** ([`nix-channel`](../02-concepts/channel.md)) plus `NIX_PATH` / `<nixpkgs>` are the classic way to supply Nixpkgs and other expression trees: you subscribe to a moving URL, run `nix-channel --update`, and import `<nixpkgs>` in Nix files or shell commands. **Flakes** replace that implicit lookup with **explicit inputs** in `flake.nix` and exact pins in [flake.lock](anatomy/lockfile.md).

Migrating a project or NixOS configuration means enabling the flake CLI, declaring inputs, moving configuration into [flake outputs](anatomy/inputs-and-outputs.md), committing the lockfile, and switching rebuild commands to `--flake`. You stop treating channel updates as the source of truth for that repo; the lockfile is. See [Flakes vs Channels](../comparisons/flakes-vs-channels.md) for a side-by-side comparison and [Flake (concept)](../02-concepts/flake.md) for vocabulary.

## Details

**Enable the new CLI and flakes.** Add to `nix.conf` (system-wide or user):

```ini
experimental-features = nix-command flakes
```

Or on NixOS / Home Manager: `nix.settings.experimental-features = [ "nix-command" "flakes" ];`. Both features remain **experimental** (Nix ≥ 2.4); see [nix-command](../08-experimental-features/nix-command.md) and [flakes](../08-experimental-features/flakes.md). Without them, `nix build`, `nix flake`, and flake-based `nixos-rebuild` are unavailable.

**Add `flake.nix` with pinned inputs.** Declare at least `inputs.nixpkgs.url` on a release branch or tag (for example `github:NixOS/nixpkgs/nixos-26.05`). Add other inputs (Home Manager, custom flakes, tarballs) the same way. Run any flake command once to generate [flake.lock](anatomy/lockfile.md), then **commit** it so CI and collaborators share the same dependency graph. If the flake lives in a Git tree, only **tracked** files are copied into the evaluation; stage new config files before rebuild or Nix will not see them.

**Move configuration into outputs.** NixOS systems belong under `nixosConfigurations.<name>` via `nixpkgs.lib.nixosSystem`; standalone Home Manager setups use `homeConfigurations`. Package overrides and dev shells use `packages`, `devShells`, and related keys. Output shapes and rebuild commands are documented in [nixosConfigurations](workflows/nixos-configurations.md) and [homeConfigurations](workflows/home-configurations.md)—this page focuses on what changes relative to channels.

**Replace `<nixpkgs>` imports.** In channel workflows, modules and shells often do `import <nixpkgs> { ... }`. In flakes, nixpkgs comes from the realized input:

- Inside `outputs`: `nixpkgs.legacyPackages.${system}.hello` or `import nixpkgs { inherit system; config = ...; }`.
- In modules that need other inputs: pass `inputs` through `specialArgs` on `nixosSystem` / `homeManagerConfiguration`, then reference `inputs.home-manager` (or similar) in module code instead of hard-coded paths.

**Stop relying on `nix-channel --update` for this project.** Channel subscriptions can remain on the machine for ad hoc `nix-shell` or legacy tools, but the flake's locked inputs define what that repository builds. Bump nixpkgs intentionally with `nix flake update` (or a targeted input update such as `nix flake update nixpkgs`), review the diff in `flake.lock`, and rebuild.

**Update rebuild and build commands.** Classic NixOS on channels:

```bash
sudo nixos-rebuild switch
```

Flake-based equivalent (configuration name from `nixosConfigurations`):

```bash
sudo nixos-rebuild switch --flake .#hostname
```

Omitting `#hostname` makes `nixos-rebuild` look up `nixosConfigurations.<current-hostname>`. The same flake reference works for `nix build`, `nix develop`, and remote deploy. [Pure evaluation](pure-eval-and-impure.md) applies to flake builds; impure channel paths are not part of the locked graph.

**Registry vs project inputs.** The [flake registry](registries-and-refs.md) still provides CLI convenience (`nixpkgs#hello`, `nix run github:owner/repo#app`) without a local channel. For **projects**, locked flake inputs—not the registry default—are the source of truth. Registry entries can move; your `flake.lock` does not unless you update it.

**If you are not adopting flakes fully.** Flakes are optional on nix.dev; alternatives include [npins](https://github.com/serokell/npins) or `builtins.fetchTarball` with an explicit hash pin, or a thin `flake.nix` that only wraps fetched sources. Those patterns trade flake-native locking and `nix flake check` integration for smaller surface area. This wiki treats flakes as the primary reproducible path; mention the others when a team cannot enable experimental features yet.

## Examples

**Before — channel subscription + `configuration.nix`.** Machine tracks `nixpkgs-unstable`; NixOS config imports the channel implicitly:

```bash
nix-channel --add https://channels.nixos.org/nixpkgs-unstable nixpkgs
nix-channel --update
```

```nix
# configuration.nix (fragment)
{ config, pkgs, ... }:

{
  imports = [ ./hardware-configuration.nix ];
  system.stateVersion = "26.05";
  environment.systemPackages = [ pkgs.hello ];
}
```

Rebuild: `sudo nixos-rebuild switch` (uses `<nixpkgs>` from `NIX_PATH` / default channel layout).

**After — flake with `nixosConfigurations` + lock.** Same logical config; nixpkgs revision is pinned in git:

```nix
# flake.nix
{
  description = "My NixOS system";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  };

  outputs = { self, nixpkgs, ... }@inputs: {
    nixosConfigurations.hostname = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      modules = [
        ./configuration.nix
        ./hardware-configuration.nix
      ];
    };
  };
}
```

```bash
nix flake lock   # writes flake.lock; commit both files
sudo nixos-rebuild switch --flake .#hostname
```

To upgrade nixpkgs later: `nix flake update nixpkgs`, inspect `flake.lock`, then rebuild—not `nix-channel --update` for this configuration.

## References

- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — introduction; notes that flakes are optional; enable via `experimental-features`
- [Nix manual — `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — inputs, outputs, lock file, and CLI
- [Nix manual — `nix flake update`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-update.html) — bump locked inputs (all or named)
- [NixOS Wiki — Flakes](https://wiki.nixos.org/wiki/Flakes) — `nixos-rebuild --flake`, Git tracked-files caveat (secondary to manuals)
- [npins](https://github.com/serokell/npins) — non-flake dependency pinning alternative

## See also

- [Channel](../02-concepts/channel.md) — `nix-channel`, generations, and `NIX_PATH`
- [Flake (concept)](../02-concepts/flake.md) — inputs, outputs, and lockfile at concept level
- [Flakes vs Channels](../comparisons/flakes-vs-channels.md) — trade-offs and when each model fits
- [Inputs and outputs](anatomy/inputs-and-outputs.md) — output keys and composition
- [Lockfile](anatomy/lockfile.md) — pin structure and update semantics
- [nixosConfigurations](workflows/nixos-configurations.md) — NixOS flake wiring and `--flake` rebuilds
- [homeConfigurations](workflows/home-configurations.md) — Home Manager output shape
- [Registries and refs](registries-and-refs.md) — `nixpkgs#` and symbolic flake names
- [Pure eval and impure](pure-eval-and-impure.md) — hermetic evaluation vs channel impurity
