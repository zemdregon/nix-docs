---
status: complete
---

# nixpkgs NixOS Modules

## Overview

The **primary module ecosystem** in the Nix stack is the NixOS module set shipped in [nixpkgs](../../06-nixpkgs/README.md). Thousands of modules under `nixos/modules/` declare options and define config for services, networking, users, boot, and the rest of a Linux system. Evaluation uses `lib.evalModules` from nixpkgs `lib`; the NixOS entry points (`nixos/lib/eval-config.nix`, `nixos-rebuild`, flakes `nixosSystem`) wrap that once with the upstream module list plus your imports.

This ecosystem is about **OS configuration**, not package recipes. Derivations and package attributes live in the nixpkgs package set; modules consume those packages (via `pkgs`) and wire them into units, `/etc`, and activation. Other ecosystems—[Home Manager](home-manager.md), [nix-darwin](nix-darwin.md), [flake-parts](flake-parts.md)—reuse the same `evalModules` machinery with different option trees and outputs.

## Details

**Packages vs modules.** A package expression builds a store path. A NixOS module declares typed options and merges definitions into a `config` that the NixOS build turns into a system closure (systemd units, files, kernels, installed packages). Setting `environment.systemPackages = [ pkgs.ripgrep ];` is a module definition that *references* a package; it does not define how `ripgrep` is built. Overlays and package overrides change the package set; module options change how the OS uses that set.

**Where modules live.** Upstream modules are part of the nixpkgs tree (typically `nixos/modules/...`). Your `configuration.nix` and anything in `imports` are modules in the same merge. Third-party modules follow the same shape: `{ config, pkgs, lib, ... }: { options = …; config = …; }`.

**`lib.evalModules`.** nixpkgs documents the generic evaluator: pass `{ modules = [ … ]; specialArgs = …; }` and get back `{ config, options, … }`. NixOS calls this once with the full module list; applications that are not NixOS (Home Manager, nix-darwin, custom tooling) call it with their own modules. Imports must be static; inject extra arguments with `specialArgs` or `_module.args` (NixOS supplies `pkgs` that way). Deep merge semantics, `mkIf` / `mkMerge` / priorities: see the [module system](../../09-nixos/architecture/module-system.md) article.

**Discovering options.** Declared options are searchable at [search.nixos.org/options](https://search.nixos.org/options) (channel-scoped; stable channel **26.05** as of 2026-07). Locally, `man configuration.nix` and `nixos-option` expose the same tree after evaluation. The searchable catalog is the practical map of this ecosystem’s public API.

## Examples

Minimal custom evaluation (illustrative; real NixOS uses `eval-config` with the full module list):

```nix
let
  pkgs = import <nixpkgs> { };
  eval = pkgs.lib.evalModules {
    modules = [
      ({ lib, ... }: {
        options.demo.enable = lib.mkEnableOption "demo";
        config.demo.enable = true;
      })
    ];
  };
in
eval.config.demo.enable  # => true
```

Typical relationship in a NixOS module—config selects packages from `pkgs`:

```nix
{ config, pkgs, lib, ... }: {
  options.services.mytool.enable = lib.mkEnableOption "mytool";
  config = lib.mkIf config.services.mytool.enable {
    environment.systemPackages = [ pkgs.hello ];
  };
}
```

## References

- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/) — Modularity, Writing NixOS Modules, option reference (channel 26.05 as of 2026-07)
- [Nixpkgs manual (stable)](https://nixos.org/manual/nixpkgs/stable/) — Module system / `lib.evalModules`
- [NixOS options search](https://search.nixos.org/options)

## See also

- [Module system](../../09-nixos/architecture/module-system.md)
- [nixpkgs](../../06-nixpkgs/README.md)
- [Home Manager](home-manager.md)
- [nix-darwin](nix-darwin.md)
- [flake-parts](flake-parts.md)
