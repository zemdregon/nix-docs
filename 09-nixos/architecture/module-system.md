---
status: complete
---

# Module System

## Overview

NixOS configuration is not one big attribute set—it is the **evaluation of many modules** through the NixOS module system (`lib.evalModules`). Your [`configuration.nix`](../configuration/configuration-nix.md) is itself a module: it declares options, sets values, and pulls in others via `imports`.

The module system turns hundreds of small declarations into a single merged `config` (concrete values) and a unified `options` tree (schemas and metadata). That merged result drives the system closure built by `nixos-rebuild`.

## Details

**Module shape.** A module is typically a function returning an attribute set:

```nix
{ config, pkgs, lib, ... }: {
  imports = [ /* other modules */ ];
  options = { /* option declarations */ };
  config = { /* option definitions */ };
}
```

Top-level keys that match declared option names (without wrapping them in `config`) are **sugar** for `config`—both forms merge the same way.

**Evaluation flow.** `evalModules` collects every module (from nixpkgs, your imports, and inline fragments), merges their `options` declarations, then merges their `config` definitions according to each option's type. The output is `{ config, options, … }`; NixOS uses `config` to produce derivations, systemd units, `/etc` files, and the rest of the system.

**How merging works.** Declarations with the same option path must agree on type and description; conflicts fail evaluation. Definitions for the same option merge **by type**: lists concatenate, attribute sets recurse, booleans and strings often use priority helpers (`lib.mkDefault`, `lib.mkForce`, etc.—see [mkIf, mkMerge, mkOrder](../modules/mkIf-mkMerge-mkOrder.md)). This is why many modules can set `services.nginx.enable` or append to `environment.systemPackages` without hand-written conflict resolution.

**Static imports.** Paths in `imports` must be known at import time—they cannot depend on `config` values. When a module needs extra arguments (custom flakes inputs, paths under nixpkgs), pass them through `_module.args` or module-function `specialArgs` instead of reading config inside `imports`. See [imports and profiles](../configuration/imports-and-profiles.md).

**Args available to modules.** Besides `config`, `pkgs`, and `lib`, modules receive `_module`, `modulesPath`, and any keys you inject via `_module.args` or `specialArgs`. Downstream modules read injected values as ordinary function arguments.

For option schemas, merge semantics, and the split between declaration and definition, see [Options and types](options-and-types.md) and [config vs options](config-vs-options.md). Step-by-step module authoring lives under [Writing a module](../modules/writing-a-module.md).

## Examples

Two tiny modules: one declares an option, the other imports the first and sets it.

```nix
# options-module.nix
{ lib, ... }: {
  options.myapp.enable = lib.mkEnableOption "myapp";
}

# config-module.nix
{ ... }: {
  imports = [ ./options-module.nix ];
  myapp.enable = true;
}
```

When both are passed to `evalModules`, the result's `config.myapp.enable` is `true` and `options.myapp.enable` carries the declaration metadata. Real NixOS stacks thousands of such modules; your [`configuration.nix`](../configuration/configuration-nix.md) sits at the top of that graph.

## References

- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/) — Modularity, Writing NixOS Modules
- [`_module.args` option reference](https://nixos.org/manual/nixos/stable/options#opt-_module.args)
- [nix.dev — Module system tutorial](https://nix.dev/tutorials/module-system/) (secondary)

## See also

- [Module system internals](module-system-internals.md) — `evalModules`, freeform, `specialArgs` / `_module.args`
- [Options and types](options-and-types.md)
- [config vs options](config-vs-options.md)
- [configuration.nix](../configuration/configuration-nix.md)
- [Imports and profiles](../configuration/imports-and-profiles.md)
- [Writing a module](../modules/writing-a-module.md)
- [Generation](../../02-concepts/generation.md)
