---
status: complete
---

# Options and Types

## Overview

NixOS modules expose a typed **options** interface. Each option is declared under `options` with `lib.mkOption` (or helpers such as `mkEnableOption` and `mkPackageOption`) and carries a **type**, optional **default**, **description**, and related metadata. Values under `config` are **definitions** that must satisfy those types; a failed check aborts evaluation before the rebuild finishes.

Types live in `lib.types`. They validate values and decide how multiple definitions **merge**. Declarations plus types are what [search.nixos.org](https://search.nixos.org/options) and the NixOS options appendix render.

This page is the schema and typing layer. For the declare-under-`options` vs define-under-`config` workflow, see [config vs options](config-vs-options.md); for evaluation order, see [Module system](module-system.md).

## Details

**`mkOption` fields.** A declaration typically sets:

| Field | Role |
|-------|------|
| `type` | Constraint and merge rule from `lib.types` (mandatory for nixpkgs modules; strongly recommended elsewhere) |
| `default` | Value used when no module defines the option; omit it only if callers must set a value |
| `defaultText` | Manual rendering when the default is a complex expression (`lib.literalExpression` / `lib.literalMD`) |
| `example` | Sample value shown in generated docs |
| `description` | Nixpkgs-flavored Markdown for the manual and option search |

Other fields (`apply`, `readOnly`, `visible`, `internal`) exist for advanced or internal options; most module authors need only the table above.

**Helpers.** `mkEnableOption "thing"` expands to a `types.bool` option defaulting to `false` with description “Whether to enable thing.” `mkPackageOption pkgs "name" { … }` declares a package-valued option with a documented default path into `pkgs`.

**Common types.** Primitives include `types.bool`, `types.str`, `types.int`, `types.port`, and `types.path`. Prefer `types.package` over a bare path when the value is a derivation. Structured types compose: `types.listOf t`, `types.attrsOf t`, `types.nullOr t`, `types.enum [ "a" "b" ]`. Each type’s merge function matters as much as its check—e.g. `listOf` concatenates, `attrsOf` merges attributes, `bool` requires agreement after priorities.

**Nested options.** Options form an attr tree. Dotted names such as `services.httpd.enable` are sugar for nested paths; the module system treats both the same.

**Submodules.** `types.submodule { options = …; }` nests a full module interface inside an option—useful for plugin lists or repeated blocks (`listOf (submodule …)`, `attrsOf (submodule …)`). `types.submoduleWith` is the more flexible form (`modules`, `specialArgs`, …).

**`freeformType` (briefly).** Inside a submodule, the attribute `freeformType = someType;` (not a member of `lib.types` itself) accepts undeclared attribute names and merges them with `someType`. Declared child options still get normal type-checking and defaults. The manual recommends freeform only in submodules (often `settings`-style maps), because it disables strict name checking for that tree.

**Eval-time checking.** During `nixos-rebuild`, contributing modules merge `config` fragments; each final value must match its option type. Undeclared option paths and type mismatches fail at evaluation.

## Examples

```nix
{ lib, ... }:
let
  inherit (lib) mkOption mkEnableOption types;
in
{
  options.services.example = {
    enable = mkEnableOption "the example daemon";

    port = mkOption {
      type = types.port;
      default = 8080;
      example = 9090;
      description = "TCP port the example daemon listens on.";
    };

    # Declared keys type-check; extra attrs merge as strings via freeformType.
    settings = mkOption {
      type = types.submodule {
        freeformType = types.attrsOf types.str;
        options.logLevel = mkOption {
          type = types.enum [ "debug" "info" "warn" ];
          default = "info";
          description = "Daemon log verbosity.";
        };
      };
      default = { };
      description = "Daemon settings; undeclared keys must be strings.";
    };
  };
}
```

A host then sets e.g. `services.example.enable = true;` and optionally `services.example.settings.extraFlag = "on";`. Wrong types or a typo’d option path fail at eval time.

Browse live declarations on [search.nixos.org/options](https://search.nixos.org/options) or in the [NixOS options appendix](https://nixos.org/manual/nixos/stable/options).

## References

- [NixOS manual — Writing NixOS Modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules)
- [NixOS manual — Option Declarations](https://nixos.org/manual/nixos/stable/index.html#sec-option-declarations)
- [NixOS manual — Option Types](https://nixos.org/manual/nixos/stable/index.html#sec-option-types)
- [NixOS manual — Freeform modules](https://nixos.org/manual/nixos/stable/index.html#sec-freeform-modules)
- [nixpkgs `lib/types.nix`](https://github.com/NixOS/nixpkgs/blob/master/lib/types.nix)
- [nixpkgs `lib/options.nix` (`mkOption`)](https://github.com/NixOS/nixpkgs/blob/master/lib/options.nix)
- [NixOS options search](https://search.nixos.org/options)

## See also

- [Module system](module-system.md)
- [config vs options](config-vs-options.md)
- [Custom options](../modules/custom-options.md)
- [Writing a module](../modules/writing-a-module.md)
