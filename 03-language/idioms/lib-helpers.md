---
status: complete
---

# lib Helpers

## Overview

`pkgs.lib` (also imported as `nixpkgs.lib`) is the nixpkgs function library: mostly pure Nix helpers for attribute sets, lists, strings, fixed points, modules, and similar. This page is a tour of high-traffic idioms, not a full catalog — see the [nixpkgs Functions reference](https://nixos.org/manual/nixpkgs/stable/#sec-functions-library) (and [noogle.dev](https://noogle.dev/) for discovery). For library layout in the tree, see [lib](../../06-nixpkgs/architecture/lib.md).

## Details

### Attribute sets

| Helper | Role |
|--------|------|
| `mapAttrs` | Map over each name/value; keep the same keys |
| `filterAttrs` | Keep attrs for which the predicate holds |
| `optionalAttrs` | Include an attrset only when a condition is true (else `{}`) |
| `genAttrs` | Build an attrset from a list of names and a value function |
| `getAttrFromPath` / `attrByPath` | Nested lookup by path; `attrByPath` takes a default |
| `recursiveUpdate` | Deep-merge two attrsets (see Merge below) |

Related builtins and operators: [attrset / list / string builtins](../builtins/attrset-list-string.md), [`//`](../syntax/operators.md).

### Lists

| Helper | Role |
|--------|------|
| `optional` | Zero or one element: `cond` → `[ x ]` or `[]` |
| `optionals` | Zero or many: `cond` → list or `[]` |
| `concatMap` | Map each element to a list, then flatten one level |
| `flatten` | Recursively flatten nested lists |
| `unique` | Deduplicate while preserving order |
| `toList` | Wrap a non-list as a singleton list |

`optionals` and `optionalAttrs` avoid empty-with noise when composing lists and attrsets conditionally.

### Strings

| Helper | Role |
|--------|------|
| `concatStringsSep` | Join a list of strings with a separator |
| `optionalString` | Empty string or a string, by condition |
| `hasPrefix` | Whether a string starts with a prefix |

### Trivial / composition

| Helper | Role |
|--------|------|
| `id` | Identity |
| `const` | Ignore the next argument; return a fixed value |
| `pipe` | Thread a value through a list of functions left-to-right |
| `max` / `min` | Numeric extremes |

### Merge: `//` vs `recursiveUpdate`

`a // b` replaces nested attribute sets wholesale: if both sides define `boot.loader`, the right-hand `boot.loader` wins entirely. `lib.recursiveUpdate a b` merges nested attrsets, so sibling keys under a shared path survive. Prefer `recursiveUpdate` for deep config-style overlays of attrsets.

### Fixed points (brief)

`lib.fix` computes the fixed point of a function (`f (fix f) = fix f`). `lib.extends` layers an overlay onto a fixed-point function — the pattern behind package overlays. Deep dive: [rec and fixed points](rec-and-fixed-points.md); overlays: [overlays pattern](overlays-pattern.md).

### Modules peek

NixOS/Home Manager modules use `lib.mkIf`, `lib.mkMerge`, `lib.mkDefault`, and `lib.mkForce` to condition and prioritize option values. Treat those as module idioms, not general-purpose Nix: [mkIf / mkMerge / mkOrder](../../09-nixos/modules/mkIf-mkMerge-mkOrder.md).

## Examples

Conditional list and attrset composition:

```nix
{ lib, enableDocs ? false, extra ? {} }:
{
  packages = [ "core" ] ++ lib.optionals enableDocs [ "docs" ];
  settings = { timeout = 30; } // lib.optionalAttrs enableDocs { format = "md"; } // extra;
}
```

Deep merge vs shallow `//`:

```nix
let
  lib = import <nixpkgs/lib>;
  base = { boot.loader.grub.enable = true; boot.loader.grub.device = "/dev/sda"; };
  override = { boot.loader.grub.device = "/dev/nvme0n1"; };
in
{
  shallow = base // override;           # drops enable — boot.loader replaced
  deep = lib.recursiveUpdate base override;  # enable kept; device updated
}
```

`pipe` and `mapAttrs`:

```nix
lib.pipe { a = 1; b = 2; } [
  (lib.mapAttrs (_: v: v * 10))
  (lib.filterAttrs (_: v: v > 15))
]
# => { b = 20; }
```

## See also

- [Attrset / list / string builtins](../builtins/attrset-list-string.md)
- [Operators](../syntax/operators.md) (`//`, `++`, …)
- [rec and fixed points](rec-and-fixed-points.md)
- [Overlays pattern](overlays-pattern.md)
- [nixpkgs `lib`](../../06-nixpkgs/architecture/lib.md)
- [mkIf / mkMerge / mkOrder](../../09-nixos/modules/mkIf-mkMerge-mkOrder.md)

## References

- [nixpkgs Manual — Functions reference](https://nixos.org/manual/nixpkgs/stable/#sec-functions-library) (stable / 26.05 channel docs as of 2026-07)
- [nixpkgs Manual — Attribute-set library](https://nixos.org/manual/nixpkgs/stable/#sec-functions-library-attrsets)
- [noogle.dev](https://noogle.dev/) — searchable `lib` / builtins index
