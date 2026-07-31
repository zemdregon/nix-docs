---
status: complete
---

# Writing HM Modules

## Overview

Home Manager modules use the same NixOS module system: declare options with `mkOption` / `mkEnableOption`, define values under `config`, and gate side effects with `lib.mkIf`. The Home Manager manual treats the NixOS [writing-modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules) chapter as the base; HM only adds home-oriented namespaces and a few extra types.

What differs is the **target**: user home state under `home.*`, XDG files, `programs.*`, and user-scoped `services.*` units—not system services or `/etc`. How you activate HM (standalone vs NixOS module) is separate; see [Standalone vs NixOS module](standalone-vs-nixos-module.md). Evaluation mechanics match [Module system](../../09-nixos/architecture/module-system.md).

Most users write modules to compose their own dotfiles: split a large `home.nix` into reusable pieces, declare a small option tree for a tool HM does not ship, or wrap shared defaults for a team. Upstream HM program modules follow the same pattern; your custom files are peers imported via `imports`.

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

Conditionals and merge helpers (`mkIf`, `mkMerge`, `mkDefault`, …) behave as in NixOS; see [mkIf, mkMerge, mkOrder](../../09-nixos/modules/mkIf-mkMerge-mkOrder.md) and [Writing a module](../../09-nixos/modules/writing-a-module.md). Option declarations follow the same rules—types, defaults, descriptions—as in [Custom options](../../09-nixos/modules/custom-options.md).

**Home-oriented option trees.** Definitions usually land on HM’s declared options, for example:

- `home.file` — files under the home directory
- `xdg.configFile` — files under the XDG config directory
- `programs.<name>.enable` — enable a program module and its generated config
- `services.<name>` — user units / user services (not system `systemd.services` from NixOS)

Browse concrete option names in the [Home Manager options reference](https://nix-community.github.io/home-manager/options.xhtml); do not assume NixOS option paths exist under HM. When you add your own options (e.g. `myTools.demo.enable`), keep them namespaced so they do not collide with HM or other imports.

**Custom modules via `imports`.** Split your config into reusable files and pull them in with `imports = [ ./foo.nix ];`, the same composition model as NixOS. A parent module can import children; children can import shared library modules that only declare options and helpers. Shared library patterns (enable flags, `cfg = config.…`, typed options) transfer directly. File-layout tips for dotfiles live in [Dotfiles patterns](dotfiles-patterns.md).

**Assertions and warnings.** HM modules support the same `assertions` and `warnings` list options as NixOS—use them to fail fast on invalid combinations or emit deprecations during evaluation instead of ad hoc `builtins.abort`. See [Assertions and warnings](../../09-nixos/modules/assertions-and-warnings.md).

**HM-specific types (when you need them).** Beyond standard `lib.types`, HM exposes helpers such as `hm.types.dagOf` (ordered attribute sets, e.g. activation scripts or SSH match blocks) and GVariant helpers for dconf-style settings. Most personal modules never need these; reach for them only when ordering or desktop settings require it.

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
- [Custom options](../../09-nixos/modules/custom-options.md)
- [Assertions and warnings](../../09-nixos/modules/assertions-and-warnings.md)
- [Module system](../../09-nixos/architecture/module-system.md)
