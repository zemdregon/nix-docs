---
status: complete
---

# lib

## Overview

Nixpkgs ships a large pure-Nix library at `pkgs.lib` (or `import <nixpkgs/lib>`). It is the shared toolkit behind packaging, [package sets](package-sets.md), [stdenv](stdenv.md), NixOS modules, and flake outputs: attrset/list/string utilities, metadata (`licenses`, `platforms`, `maintainers`), fixed-point helpers, package customisation, and module-system primitives. It wraps common patterns; it is not the Nix language itself — [builtins](../../03-language/builtins/README.md) and operators live in the evaluator.

## Details

### Where it lives

The tree is under [`lib/`](https://github.com/NixOS/nixpkgs/tree/master/lib) in the nixpkgs repo. A typical import:

```nix
let
  lib = import <nixpkgs/lib>;
in
  lib.genAttrs [ "a" "b" ] (name: "value-${name}")
```

(`import <nixpkgs/lib>` evaluates to the library attrset directly.) In a flake or `import nixpkgs { }`, the same library is exposed as `pkgs.lib`.

### Namespaces

Functions are grouped into sub-attrsets rather than one flat namespace. Common areas:

| Namespace | Typical use |
|-----------|-------------|
| `lib.attrsets`, `lib.lists`, `lib.strings`, `lib.trivial` | Data manipulation and small utilities |
| `lib.fixedPoints` | `fix`, `extends` — package-set recursion and overlays |
| `lib.customisation` | `callPackageWith`, `makeScope`, `makeOverridable` — `.override` and `callPackage` |
| `lib.meta`, `lib.licenses`, `lib.platforms`, `lib.maintainers` | Package metadata and policy |
| `lib.options`, `lib.types` | Option schemas for the module system |

For day-to-day helper usage (`optional`, `mapAttrs`, merges, etc.), see [lib helpers](../../03-language/idioms/lib-helpers.md). The upstream [Functions reference](https://nixos.org/manual/nixpkgs/stable/#chap-functions) is the authoritative catalog; this page stays architectural.

### Customisation and package sets

`lib.customisation.makeOverridable` wraps a function so callers can use `.override` / `.overrideAttrs` on the result — the mechanism behind most nixpkgs packages. `callPackageWith` and friends implement [callPackage](../../03-language/idioms/callPackage.md): auto-fill function arguments from a package set and allow per-call overrides. Together with [fixed points](../../03-language/idioms/rec-and-fixed-points.md) and [overlays](../../03-language/idioms/overlays-pattern.md), these pieces compose [package sets](package-sets.md).

### Module system (surface only)

`lib.evalModules`, `lib.mkIf`, `lib.mkOption`, and `lib.types` belong to the same library but serve NixOS-style configuration. They are documented with the [module system](../../09-nixos/architecture/module-system.md); nixpkgs packaging code uses them less often than NixOS modules do.

## Examples

Conditional list fragments (common in `buildInputs` and module merges):

```nix
buildInputs = with lib; [
  openssl
]
++ optional stdenv.isDarwin libiconv
++ optionals enableDocs [ doxygen ];
```

Transform an attrset while keeping keys:

```nix
lib.mapAttrs (name: value: value // { pname = name; }) srcInfos
```

License shorthand in derivations:

```nix
meta.license = lib.licenses.mit;
```

## See also

- [lib helpers](../../03-language/idioms/lib-helpers.md) — idiomatic helpers, not a full API list
- [callPackage](../../03-language/idioms/callPackage.md)
- [Overlays pattern](../../03-language/idioms/overlays-pattern.md)
- [rec and fixed points](../../03-language/idioms/rec-and-fixed-points.md)
- [Package sets](package-sets.md)
- [stdenv](stdenv.md)
- [Module system](../../09-nixos/architecture/module-system.md)

## References

- [Nixpkgs manual — Functions reference](https://nixos.org/manual/nixpkgs/stable/#chap-functions)
- [Nixpkgs manual (stable)](https://nixos.org/manual/nixpkgs/stable/)
- [nixpkgs `lib/` tree](https://github.com/NixOS/nixpkgs/tree/master/lib)
