---
status: complete
---

# Custom Options

## Overview

Custom options are the typed interface your module exposes to the rest of the configuration. Declare them under `options` with `lib.mkOption` (or helpers like `mkEnableOption` / `mkPackageOption`); other modules and the host config then set values under `config`. Undeclared option names fail evaluation; declared ones must type-check.

Option types from `lib.types` control both validation and merge. Nested attrsets and dotted names (`services.myapp.enable`) are sugar for the same tree. Prefer namespaced paths so shared modules do not collide. See [options and types](../architecture/options-and-types.md) and [writing a module](writing-a-module.md).

## Details

**Declaring with `mkOption`.** A declaration typically sets `type`, optional `default`, `description`, and sometimes `example`. For nixpkgs-shipped modules, `type` is mandatory. Helpers cut boilerplate: `mkEnableOption "…"` for a boolean enable flag (default `false`), `mkPackageOption pkgs "name" { }` for a package-valued option (third argument is an attrset; may be empty when `"name"` is an attribute of `pkgs`).

**Naming.** Attribute path segments are generally camelCase. Exception: when an option refers to a Nixpkgs package, match that package’s attribute name (for example `services.nix-serve.bindAddress`).

**Nesting and dotted names.** Group related options in attrsets. Writing `options.services.myapp.enable = …` is equivalent to nesting under `options.services.myapp`; the module system treats both as the same path.

**Types validate and merge.** `lib.types` is not only a checker: each type defines how multiple definitions combine (`listOf` concatenates, `attrsOf` merges attributes, and so on). Choose the type that matches both the value shape and the intended merge. For repeated or plugin-style blocks, `types.submodule` nests a full module interface (options + config) inside one option.

**Definitions must match.** Values under `config` for a declared option must satisfy its type. Referring to an undeclared option name aborts evaluation—there is no silent ignore. If you omit `default`, some module must define the value or evaluation fails.

**Namespace to avoid collisions.** Prefer conventional prefixes (`services.foo`, `programs.foo`) or an org-specific root (`myOrg.foo`) when shipping modules for reuse. Local modules only affect your evaluation; options appear on [search.nixos.org](https://search.nixos.org/options) only after they are upstreamed into nixpkgs/NixOS.

## Examples

Illustrative declaration (not a nixpkgs service). Verified against NixOS manual option-declaration and `mkEnableOption` patterns (stable manual).

```nix
{ lib, ... }:
let
  inherit (lib) mkOption mkEnableOption types;
in
{
  options.services.myapp = {
    enable = mkEnableOption "myapp";

    port = mkOption {
      type = types.port;
      default = 8080;
      description = "TCP port the myapp daemon listens on.";
    };
  };
}
```

A host (or another module) then sets `services.myapp.enable = true;` (abbreviated form) or `config.services.myapp.enable = true;` and optionally overrides `port`. Wrong types or a typo like `services.myApp.enable` fail at eval time.

Package option shape from the manual (`mkPackageOption` needs the pkgs set and a trailing attrset):

```nix
# like: type = package; default = pkgs.hello; …
lib.mkPackageOption pkgs "hello" { }
```

## References

- [NixOS manual (stable) — Writing NixOS Modules (Option Declarations / Option Types)](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules)
- [NixOS options search](https://search.nixos.org/options)

## See also

- [Writing a module](writing-a-module.md)
- [Options and types](../architecture/options-and-types.md)
- [config vs options](../architecture/config-vs-options.md)
- [Module system](../architecture/module-system.md)
- [Assertions and warnings](assertions-and-warnings.md)
