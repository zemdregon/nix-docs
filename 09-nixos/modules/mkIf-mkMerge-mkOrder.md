---
status: complete
---

# mkIf / mkMerge / mkOrder

## Overview

Option definitions in the [module system](../architecture/module-system.md) are not plain Nix attrsets forever—helpers in `lib` wrap values so evaluation can delay conditionals, discard weaker overrides, and control merge order. The important ones are `mkIf`, `mkOverride` (plus `mkForce` / `mkDefault`), `mkOrder` (plus `mkBefore` / `mkAfter`), and `mkMerge`.

Use these when a module’s `config` depends on other options, when several modules set the same path, or when list order matters. Prefer them over raw `if`, `//`, or `lib.recursiveUpdate` on module-system nodes.

## Details

**`mkIf` — delayed conditionals.** Plain Nix `if config.x then { … } else { }` around a `config` attrset that also contributes to `config.x` causes infinite recursion: evaluating the condition forces the same attrset being built. `lib.mkIf condition defs` pushes the conditional into the individual definitions, so the module system can resolve the fixed-point without forcing the whole set first. Definitions under `mkIf` apply only when the condition is true; a false condition contributes nothing for those paths.

**Priorities — which definition wins.** For a given option, only definitions with the **lowest** priority number survive; others are discarded. Survivors at that priority are then merged by the option’s type (for example lists concatenate). Defaults:

| Kind | Priority |
|------|----------|
| Ordinary definitions | 100 |
| Option defaults (`mkOption` default / `mkOptionDefault`) | 1500 |

Set an explicit priority with `lib.mkOverride priority value`. Shorthands:

- `lib.mkForce` = `mkOverride 50`
- `lib.mkDefault` = `mkOverride 1000`

So a bare assignment (100) beats `mkDefault` (1000); `mkForce` (50) beats a bare assignment. Lower number always wins.

**`mkOrder` — merge order, not inclusion.** `lib.mkOrder` changes the order in which surviving definitions are merged (lists concatenate in that order, and so on). It does **not** decide whether a definition is kept—that is override priority. Default order is 1000. Shorthands:

- `lib.mkBefore` = `mkOrder 500`
- `lib.mkAfter` = `mkOrder 1500`

**`mkMerge` — several definition sets as one.** `lib.mkMerge [ attrs… ]` merges multiple definition attrsets as if they came from separate modules. Useful when combining unconditional config with `mkIf` branches in one module’s `config`.

**Do not `//` or `recursiveUpdate` special nodes.** Results of `mkIf` / `mkMerge` / priority wrappers are ordinary Nix attrsets with module-system metadata (`_type`, etc.). `//` and `lib.recursiveUpdate` treat them as plain data and can strip or bury that metadata. Combine module config with `mkMerge` instead.

For declaration vs definition and how types merge, see [config vs options](../architecture/config-vs-options.md) and [Options and types](../architecture/options-and-types.md). Authoring walkthrough: [Writing a module](writing-a-module.md).

## Examples

Enable-gated config with `mkIf` (avoids infinite recursion on `config.services.httpd.enable`):

```nix
{ config, lib, ... }:
{
  config = lib.mkIf config.services.httpd.enable {
    environment.systemPackages = [ /* … */ ];
  };
}
```

Force an override over other modules’ definitions:

```nix
{ lib, ... }:
{
  services.openssh.enable = lib.mkForce false;
}
```

Put an entry early in a list option (order only; still merged with other definitions):

```nix
{ lib, ... }:
{
  hardware.firmware = lib.mkBefore [ myFirmware ];
}
```

Unconditional and conditional branches via `mkMerge`:

```nix
{ config, lib, ... }:
{
  config = lib.mkMerge [
    { environment.systemPackages = [ /* always */ ]; }
    (lib.mkIf config.services.bla.enable {
      environment.systemPackages = [ /* when enabled */ ];
    })
  ];
}
```

## References

- [NixOS manual (stable) — Option Definitions](https://nixos.org/manual/nixos/stable/index.html#sec-option-definitions)
- [NixOS manual (stable) — Writing NixOS Modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules)
- [`lib/modules.nix` — `mkIf` / `mkMerge` / `mkOverride` / `mkOrder`](https://github.com/NixOS/nixpkgs/blob/master/lib/modules.nix)

## See also

- [Writing a module](writing-a-module.md)
- [Module system](../architecture/module-system.md)
- [Options and types](../architecture/options-and-types.md)
- [config vs options](../architecture/config-vs-options.md)
