---
status: complete
---

# nix-darwin

## Overview

**nix-darwin** is the main **macOS module ecosystem** in the Nix stack: a large set of NixOS-style modules plus `darwinSystem` / `darwin-rebuild`, so you declare system packages, launchd jobs, defaults, and related settings in Nix on top of Apple’s OS. Upstream frames it as “`/etc/nixos/configuration.nix` for macOS.”

It sits beside [nixpkgs NixOS modules](nixpkgs-nixos.md) (full Linux OS) and [Home Manager](home-manager.md) (per-user environments). Same module *mechanics* (options, imports, `mkIf`); different option set and activation backend. It is **not** NixOS—no systemd, no kernel/rootfs rebuild.

How-to depth (activation, flakes, Home Manager wiring, option coverage): [nix-darwin (home and user)](../../10-home-and-user/nix-darwin.md). This page is the landscape slot among module ecosystems.

## Details

### Role in the module landscape

| Ecosystem | Scope | Typical entry |
|-----------|--------|----------------|
| [nixpkgs NixOS modules](nixpkgs-nixos.md) | Full NixOS system | `nixosSystem` / `nixos-rebuild` |
| **nix-darwin** | macOS host config layered on Darwin | `darwinSystem` / `darwin-rebuild` |
| [Home Manager](home-manager.md) | User home / dotfiles | standalone or NixOS/Darwin module |
| [flake-parts](flake-parts.md) | Flake-shaped module composition | `mkFlake` / flake modules |

nix-darwin consumes Nixpkgs packages and the shared module evaluation model; it does not replace NixOS’s option tree. Many Darwin options are macOS-specific—use the [nix-darwin manual](https://nix-darwin.github.io/nix-darwin/manual/index.html), not NixOS option names by assumption.

### What the ecosystem provides

- A maintained module tree for system profile packages, environment, **launchd**, macOS **defaults**, fonts, nix daemon settings, optional Homebrew hooks, and more.
- Flake output `darwinConfigurations` via `nix-darwin.lib.darwinSystem` (channels/`configuration.nix` still work).
- Activation CLI `darwin-rebuild` (first install often via `nix run …#darwin-rebuild`).
- Release branches aligned with Nixpkgs (e.g. `nix-darwin-26.05` next to unstable/`master`, as of 2026-07)—pin flake inputs so both stay compatible. Flakes remain experimental; upstream still recommends them for new setups.

### Composition with Home Manager

Home Manager is a separate ecosystem that commonly **plugs into** nix-darwin via `home-manager.darwinModules.home-manager`, so system and user config activate together. That does not make HM part of nix-darwin’s upstream tree; treat them as composed stacks. Details: [nix-darwin deep dive](../../10-home-and-user/nix-darwin.md) and [Home Manager](home-manager.md).

### Prerequisites and implementations

Any Nix implementation that can evaluate the modules and drive the store works; upstream documents both Nix and Lix. nix-darwin can manage the Nix install on the Mac; interpreter choice is orthogonal to the module set itself.

## Examples

Ecosystem shape only—minimal flake attr (hostname illustrative):

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nix-darwin.url = "github:nix-darwin/nix-darwin/master";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = inputs@{ self, nix-darwin, nixpkgs }: {
    darwinConfigurations."example-host" = nix-darwin.lib.darwinSystem {
      modules = [ ./configuration.nix ];
    };
  };
}
```

That is the Darwin analogue of NixOS’s `nixosConfigurations`: one named system module graph, applied with `darwin-rebuild switch --flake .#example-host`. Full install and HM module snippets: [nix-darwin](../../10-home-and-user/nix-darwin.md).

## See also

- [nix-darwin (home and user)](../../10-home-and-user/nix-darwin.md) — activation, flakes, HM integration, option docs
- [Home Manager](home-manager.md) — user-level module ecosystem (often composed with Darwin)
- [nixpkgs NixOS modules](nixpkgs-nixos.md) — Linux OS module ecosystem counterpart
- [flake-parts](flake-parts.md) — flake module framework (orthogonal layer)
- [Module ecosystems](README.md) — sibling stacks in this domain

## References

- [nix-darwin/nix-darwin](https://github.com/nix-darwin/nix-darwin) — source, README, install/uninstall; templates `nix-darwin/master` and `nix-darwin/nix-darwin-26.05` (verified 2026-07)
- [nix-darwin reference manual](https://nix-darwin.github.io/nix-darwin/manual/index.html) — options reference
- [nix-darwin site](https://nix-darwin.github.io/nix-darwin/) — project landing page
