---
status: complete
---

# Custom Options

## Overview

Custom options are the typed public interface your module exposes to the rest of the configuration. You declare them under `options` with `lib.mkOption`, helpers like `lib.mkEnableOption`, or occasionally `lib.mkPackageOption`; host configs and other modules then assign values under `config`. Undeclared names fail evaluation; declared ones must satisfy their type. This page is the module-author path for designing that interface—how to declare options, name them, and wire them into `config`. For the split between declaring new options and setting existing ones, see [config vs options](../architecture/config-vs-options.md) and [options and types](../architecture/options-and-types.md). Broader module shape: [writing a module](writing-a-module.md).

## Details

**Declaring with `mkOption`.** A declaration sets `type` (mandatory for nixpkgs-shipped modules), optional `default`, `description`, and sometimes `example` or `apply`. The `apply` function transforms a value after merge and before use—use sparingly for normalization, not hidden side effects. `lib.mkEnableOption "label"` is shorthand for a boolean enable flag defaulting to `false`; most service modules start there. `lib.mkPackageOption pkgs "name" { }` declares a package-valued option with a sensible default from `pkgs`.

**Options vs config in one module.** The `options` attrset defines what callers may set; `config` defines values—often on options *you* declared, and almost always on shared options declared elsewhere (`systemd.services`, `environment.systemPackages`). Gate side effects with `lib.mkIf cfg.enable` so disabled services contribute nothing. Merge helpers and conditional definitions: [mkIf, mkMerge, mkOrder](mkIf-mkMerge-mkOrder.md).

**Types validate and merge.** `lib.types` is not only a shape checker: each type defines how multiple definitions combine (`listOf` concatenates, `attrsOf` merges attributes, and so on). Pick a type that matches both the value shape and the intended merge semantics. Wrong shapes fail at eval time; incompatible *meanings* (port in use, mutually exclusive modes) belong in [assertions and warnings](assertions-and-warnings.md), not ad hoc throws inside `apply`.

**Nesting and dotted names.** Group related options in attrsets. Writing `options.services.myapp.enable = …` is equivalent to nesting under `options.services.myapp`; the module system treats both as the same path. For a nested module interface inside one option—plugin lists, open settings maps—use `types.submodule` or `types.submoduleWith`. When you need extra keys beyond declared children (typical `settings = { … }` pattern), freeform submodules relax strict name checking; see [module system internals](../architecture/module-system-internals.md).

**Naming and namespaces.** Attribute segments are generally camelCase; when an option refers to a Nixpkgs package, match that package’s attribute name (for example `services.nix-serve.bindAddress`). Prefer conventional roots—`services.*`, `programs.*`, or an org-specific prefix like `myOrg.*`—so shared modules do not collide at the top level. Options you upstream into nixpkgs appear on [search.nixos.org/options](https://search.nixos.org/options); local-only modules affect only your evaluation.

**Home Manager and beyond.** Home Manager modules use the same option machinery (`options`, `lib.mkOption`, `lib.types`, merge, assertions). The namespace differs (`services`, `programs`, `home`, …), but the author workflow is parallel: [writing Home Manager modules](../../10-home-and-user/home-manager/writing-hm-modules.md).

## Examples

Illustrative module declaring options and gating config (invented—not a nixpkgs service):

```nix
{ config, lib, pkgs, ... }:
let
  inherit (lib) mkEnableOption mkOption mkIf types;
  cfg = config.services.myapp;
in {
  options.services.myapp = {
    enable = mkEnableOption "myapp";
    port = mkOption {
      type = types.port;
      default = 8080;
      description = "TCP port the myapp daemon listens on.";
    };
  };

  config = mkIf cfg.enable {
    environment.systemPackages = [ pkgs.myapp ];
    systemd.services.myapp = {
      description = "Myapp daemon";
      wantedBy = [ "multi-user.target" ];
      serviceConfig.ExecStart = "${pkgs.myapp}/bin/myapp --port ${toString cfg.port}";
    };
  };
}
```

A host sets `services.myapp.enable = true;` and optionally overrides `port`. Typos (`services.myApp.enable`) or wrong types fail at eval time.

## References

- [NixOS manual (stable) — Writing NixOS Modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules)
- [NixOS manual (stable) — Option Declarations](https://nixos.org/manual/nixos/stable/index.html#sec-option-declarations)
- [NixOS options search](https://search.nixos.org/options)

## See also

- [Writing a module](writing-a-module.md)
- [Options and types](../architecture/options-and-types.md)
- [config vs options](../architecture/config-vs-options.md)
- [mkIf, mkMerge, mkOrder](mkIf-mkMerge-mkOrder.md)
- [Assertions and warnings](assertions-and-warnings.md)
- [Module system](../architecture/module-system.md)
- [Module system internals](../architecture/module-system-internals.md)
- [Writing Home Manager modules](../../10-home-and-user/home-manager/writing-hm-modules.md)
