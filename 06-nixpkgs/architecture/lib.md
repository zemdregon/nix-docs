---
status: complete
---

# lib

## Overview

Nixpkgs ships a large pure-Nix library at `pkgs.lib` (or `import <nixpkgs/lib>`). It is the shared toolkit behind packaging, [package sets](package-sets.md), [stdenv](stdenv.md), NixOS and Home Manager modules, and flake outputs: attrset/list/string utilities, metadata (`licenses`, `platforms`, `maintainers`), fixed-point helpers, package customisation, and module-system primitives. It wraps common patterns in Nix; it is not the Nix language itself — [builtins](../../03-language/builtins/README.md) and operators live in the evaluator. It is also not [stdenv](stdenv.md): stdenv is the build environment and hook layer for derivations; `lib` is the functional library nixpkgs code imports everywhere else.

## Details

### Where it lives

The tree is under [`lib/`](https://github.com/NixOS/nixpkgs/tree/master/lib) in the nixpkgs repo. A typical standalone import:

```nix
let
  lib = import <nixpkgs/lib>;
in
  lib.genAttrs [ "a" "b" ] (name: "value-${name}")
```

(`import <nixpkgs/lib>` evaluates to the library attrset directly.) In a flake or `import nixpkgs { }`, the same library is exposed as `pkgs.lib`.

**When to import `lib` alone vs use `pkgs.lib`:** import `<nixpkgs/lib>` (or `import (path/to/nixpkgs + "/lib")`) when you only need helpers — attrset merges, option types, license constants — and want evaluation without instantiating the full package set or building anything. Use `pkgs.lib` when you already have `pkgs` in scope (NixOS modules, overlays, `callPackage` bodies) so you do not import nixpkgs twice. The attrset is the same; only the import path differs.

### Namespaces

Functions are grouped into sub-attrsets rather than one flat namespace. Common areas:

| Namespace | Typical use |
|-----------|-------------|
| `lib.attrsets`, `lib.lists`, `lib.strings`, `lib.trivial` | Data manipulation and small utilities |
| `lib.fixedPoints` | `fix`, `extends` — self-reference and layered package sets |
| `lib.customisation` | `makeOverridable`, `callPackageWith`, `makeScope` — `.override` and [callPackage](../../03-language/idioms/callPackage.md) |
| `lib.meta`, `lib.licenses`, `lib.platforms`, `lib.maintainers` | Package metadata and packaging policy |
| `lib.options`, `lib.types` | Option schemas for the module system |

For day-to-day helper usage (`optional`, `mapAttrs`, merges, etc.), see [lib helpers](../../03-language/idioms/lib-helpers.md). The upstream [Functions reference](https://nixos.org/manual/nixpkgs/stable/#chap-functions) is the authoritative catalog; this page stays architectural.

### Customisation and overrides

`lib.customisation.makeOverridable` wraps a function so the result supports `.override` and `.overrideAttrs` — the mechanism behind most nixpkgs packages. `callPackageWith` takes a package set and a function, fills named arguments from that set, and returns an overridable call; `callPackage` is the usual `pkgs`-scoped entry point. Together they encode the nixpkgs convention: declare dependencies as function parameters, get them auto-filled, then tweak versions or flags with `.override { … }` without rewriting the call site.

### Fixed points and package sets

`lib.fixedPoints.fix` implements recursive self-reference (`fix f = f (fix f)`). `extends` composes a base fixed point with a modifier function — the same shape as stacking [overlays](../../03-language/idioms/overlays-pattern.md) on a package set. Nixpkgs package sets (`pkgs`, `pkgsCross`, custom scopes) are built from these primitives plus `makeScope`; see [rec and fixed points](../../03-language/idioms/rec-and-fixed-points.md) and [package sets](package-sets.md).

### Module system (surface only)

`lib.evalModules`, `lib.mkOption`, `lib.mkIf`, and `lib.types` belong to the same library but serve declarative configuration. NixOS and Home Manager both evaluate modules through this surface; packaging expressions use it less often. Full behaviour lives under the [module system](../../09-nixos/architecture/module-system.md).

### Metadata and policy hooks

`meta.license`, `meta.platforms`, and `meta.maintainers` on derivations draw on `lib.licenses`, `lib.platforms`, and `lib.maintainers` — curated attrsets so Hydra, review tooling, and policy checks see consistent values. Maintainer entries tie packages to teams and review expectations; see [maintainers and teams](maintainers-and-teams.md).

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
- [Maintainers and teams](maintainers-and-teams.md)

## References

- [Nixpkgs manual — Functions reference](https://nixos.org/manual/nixpkgs/stable/#chap-functions)
- [Nixpkgs manual (stable)](https://nixos.org/manual/nixpkgs/stable/)
- [nixpkgs `lib/` tree](https://github.com/NixOS/nixpkgs/tree/master/lib)
