---
status: complete
---

# Home Manager

## Overview

[Home Manager](https://nix-community.github.io/home-manager/) is a [nix-community](https://github.com/nix-community/home-manager) project that manages a **user environment** with Nix: declarative user packages and dotfiles, evaluated with the same Nix module system as NixOS. It is not part of Nixpkgs; it ships its own option tree and module set, parallel to the [nixpkgs NixOS modules](nixpkgs-nixos.md) and [nix-darwin](nix-darwin.md) ecosystems.

This page places Home Manager in the module-ecosystem landscape. Install modes, authoring modules, and dotfile patterns live under [Home Manager (user domain)](../../10-home-and-user/home-manager/README.md).

## Details

**What it evaluates.** Home Manager calls the Nixpkgs module system (`lib.evalModules`) over a curated list of HM modules plus the user’s config. Options land under home-oriented namespaces (`home.*`, `programs.*`, `services.*`, `xdg.*`, …), not the system-wide NixOS tree (`boot.*`, `networking.*`, `systemd.services`, …). The evaluation target is a user profile and home-directory state, not a full OS closure. Mechanics of writing modules: [Writing HM modules](../../10-home-and-user/home-manager/writing-hm-modules.md); module-system basics: [Module system](../../09-nixos/architecture/module-system.md).

**Where it sits vs NixOS modules.** NixOS modules (from Nixpkgs) configure the host. Home Manager modules configure one user’s home. Overlap exists for some programs (both ecosystems may wrap the same package), but the option paths and activation targets differ—do not assume a NixOS option exists under HM, or the reverse. When HM is imported as a NixOS module, it adds NixOS options such as `home-manager.users.<name>` that nest a full HM evaluation inside the system eval.

**Three entry points (same options).**

| Mode | Role in the ecosystem |
|------|------------------------|
| Standalone (`home-manager` / `homeConfigurations`) | Independent user profile; only choice on non-NixOS / non-Darwin |
| NixOS module (`home-manager.nixosModules.home-manager`) | User profiles rebuild with `nixos-rebuild` |
| nix-darwin module (`home-manager.darwinModules.home-manager`) | Same shape on Darwin with `darwin-rebuild` |

Mode choice and flake wiring: [Standalone vs NixOS module](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md).

**Release track.** Developed against `nixpkgs-unstable`; stable users pin matching `release-YY.MM` branches so HM and Nixpkgs stay aligned (e.g. `release-26.05` next to NixOS 26.05, as of 2026-07). New modules usually land on unstable first.

**Among module ecosystems.** Like NixOS and nix-darwin, HM is a large, opinionated option catalog for a domain (the home directory). [flake-parts](flake-parts.md) also uses modules, but for flake *outputs*, not user state—orthogonal composition, not a substitute for HM.

## Examples

Illustrative contrast: system vs home option trees (not a full install):

```nix
# NixOS module (host) — from nixpkgs
{ services.openssh.enable = true; }

# Home Manager module (user) — from home-manager
{ programs.git.enable = true; home.packages = [ pkgs.htop ]; }
```

Embedding HM inside NixOS (landscape shape only):

```nix
imports = [ home-manager.nixosModules.home-manager ];
home-manager.users.alice = import ./home.nix;
```

For concrete standalone vs embedded flakes and activation commands, see [Standalone vs NixOS module](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md).

## References

- [Home Manager manual](https://nix-community.github.io/home-manager/) — install modes, Nix flakes chapter (verified 2026-07; tracks release-26.05 / unstable)
- [Home Manager configuration options](https://nix-community.github.io/home-manager/options.xhtml)
- Source / README: [nix-community/home-manager](https://github.com/nix-community/home-manager)

## See also

- [Standalone vs NixOS module](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md)
- [Writing HM modules](../../10-home-and-user/home-manager/writing-hm-modules.md)
- [Dotfiles patterns](../../10-home-and-user/home-manager/dotfiles-patterns.md)
- [Home Manager (user domain)](../../10-home-and-user/home-manager/README.md)
- [nixpkgs NixOS modules](nixpkgs-nixos.md)
- [nix-darwin](nix-darwin.md)
- [flake-parts](flake-parts.md)
- [Module system](../../09-nixos/architecture/module-system.md)
