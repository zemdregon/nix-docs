---
status: complete
---

# Writing HM Modules

## Overview

Home Manager modules use the same NixOS module system: declare options with `mkOption` / `mkEnableOption`, define values under `config`, and gate side effects with `lib.mkIf`. The Home Manager manual treats the NixOS [writing-modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules) chapter as the base; HM only adds home-oriented namespaces and a few extra types.

What differs is the **target**: user home state under `home.*`, XDG files, `programs.*`, and user-scoped `services.*` units—not system services or `/etc`. How you activate HM (standalone vs NixOS module) is separate; see [Standalone vs NixOS module](standalone-vs-nixos-module.md). Evaluation mechanics match [Module system](../../09-nixos/architecture/module-system.md).

## Details

**Same shape as NixOS.** A module is typically:

```nix
{ config, lib, pkgs, ... }:
let
  cfg = config.some.subtree;
in {
  imports = [ /* other modules */ ];
  options = { /* declarations */ };
  config = lib.mkIf cfg.enable { /* definitions */ };
}
```

Conditionals and merge helpers (`mkIf`, `mkMerge`, `mkDefault`, …) behave as in NixOS; see [mkIf, mkMerge, mkOrder](../../09-nixos/modules/mkIf-mkMerge-mkOrder.md) and [Writing a module](../../09-nixos/modules/writing-a-module.md).

**Home-oriented option trees.** Definitions usually land on HM’s declared options, for example:

- `home.file` — files under the home directory
- `xdg.configFile` — files under the XDG config directory
- `programs.<name>.enable` — enable a program module and its generated config
- `services.<name>` — user units / user services (not system `systemd.services` from NixOS)

Browse concrete option names in the [Home Manager options reference](https://nix-community.github.io/home-manager/options.xhtml); do not assume NixOS option paths exist under HM.

**Custom modules via `imports`.** Split your config into reusable files and pull them in with `imports = [ ./foo.nix ];`, the same composition model as NixOS. Shared library patterns (enable flags, `cfg = config.…`, typed options) transfer directly. File-layout tips for dotfiles live in [Dotfiles patterns](dotfiles-patterns.md).

**HM-specific types (when you need them).** Beyond standard `lib.types`, HM exposes helpers such as `hm.types.dagOf` (ordered attribute sets, e.g. activation / SSH match blocks) and GVariant helpers for dconf-style settings. Most personal modules never need these; reach for them only when ordering or desktop settings require it.

## Examples

Minimal invented module: declare an enable flag and, when on, drop a config file via `xdg.configFile`. Not a real HM program module.

```nix
{ config, lib, ... }:
let
  cfg = config.myTools.demo;
in {
  options.myTools.demo = {
    enable = lib.mkEnableOption "demo home-manager module";
  };

  config = lib.mkIf cfg.enable {
    xdg.configFile."demo/config".text = ''
      # managed by Home Manager
      greeting = hello
    '';
  };
}
```

Import the file from your HM config’s `imports` and set `myTools.demo.enable = true;`.

## References

- [Home Manager manual — Writing Home Manager Modules](https://nix-community.github.io/home-manager/index.xhtml#writing-home-manager-modules)
- [Home Manager — Configuration Options](https://nix-community.github.io/home-manager/options.xhtml)
- [NixOS manual — Writing NixOS Modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules)

## See also

- [Standalone vs NixOS module](standalone-vs-nixos-module.md)
- [Dotfiles patterns](dotfiles-patterns.md)
- [Writing a module](../../09-nixos/modules/writing-a-module.md)
- [mkIf, mkMerge, mkOrder](../../09-nixos/modules/mkIf-mkMerge-mkOrder.md)
- [Module system](../../09-nixos/architecture/module-system.md)
