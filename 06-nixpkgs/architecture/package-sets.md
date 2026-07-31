---
status: complete
---

# Package Sets

## Overview

A **package set** is a large attribute set whose values are mostly derivations (and nested sets of the same shape). Nixpkgs evaluates its tree into such a set; consumers receive it as `pkgs` from a [channel](../../02-concepts/channel.md), `import <nixpkgs> { }`, or a flake’s `nixpkgs` input ([inputs and outputs](../../07-flakes/anatomy/inputs-and-outputs.md)). The set also carries NixOS modules, cross-compilation variants, and helpers like [`lib`](lib.md)—but for most users `pkgs` means “everything installable,” wired through [stdenv](stdenv.md) and [`mkDerivation`](mkDerivation.md).

## Details

### Top-level composition

Historically, most package names were registered in [`pkgs/top-level/all-packages.nix`](https://github.com/NixOS/nixpkgs/blob/master/pkgs/top-level/all-packages.nix): a fixed-point over `self` that imports individual package files and attaches metadata. Newer packages often live under [`pkgs/by-name/`](https://github.com/NixOS/nixpkgs/tree/master/pkgs/by-name/) as `…/<ab>/<name>/package.nix` and are discovered from the directory tree rather than hand-listed for every name. Exact import rules evolve; see [CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md) and the live tree when adding or moving packages.

### callPackage and siblings

Most top-level entries are built with [callPackage](../../03-language/idioms/callPackage.md): a function `{ stdenv, fetchurl, … }: …` gets its arguments filled from the set by name, with optional overrides at the call site. That keeps package files small and makes dependency wiring declarative.

### Nested and scoped sets

Language ecosystems and kernel-related trees are not flat `pkgs.<name>` entries. They appear as nested attrsets—`python3Packages`, `haskellPackages`, `nodePackages`, `linuxPackages`, and many others—often created with `lib.customisation.makeScope` / `newScope` so packages inside the scope can depend on siblings (same interpreter version, same kernel headers, etc.) without polluting the top level. The manual’s [Functions reference](https://nixos.org/manual/nixpkgs/stable/#chap-functions) documents [`makeScope`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.customisation.makeScope) and related helpers.

Directory-shaped trees are also turned into attrsets: `lib.packagesFromDirectoryRecursive` and similar patterns map folders of `package.nix` files into nested attribute names, which is how large auto-generated scopes stay maintainable.

### Overlays and overrides

The package set is a fixed point: `final` (self) and `prev` (super) in overlay notation. [Overlays](../../02-concepts/overlay.md) and legacy `packageOverrides` reshape `pkgs` by layering functions that add, replace, or tweak attributes—see the [overlays chapter](https://nixos.org/manual/nixpkgs/stable/#chap-overlays) and [writing overlays](../overlays-and-overrides/writing-overlays.md). The [overlays pattern](../../03-language/idioms/overlays-pattern.md) explains the recursion model in Nix terms.

### Platforms, Hydra, and channels

Not every attribute is built on every platform. Support tiers and `meta.platforms` / broken markers steer Hydra and ofborg; what lands on [channels](../../02-concepts/channel.md) lags `master` until release-critical tests pass. A package existing in `pkgs` does not guarantee a binary substitute on your system. See the [Overview of Nixpkgs](https://nixos.org/manual/nixpkgs/stable/#overview-of-nixpkgs) and [Platform Support](https://nixos.org/manual/nixpkgs/stable/#chap-platform-support) chapters in the manual.

## Examples

Top-level style (arguments injected by `callPackage`):

```nix
{ lib, stdenv, fetchurl, zlib }:

stdenv.mkDerivation {
  pname = "demo";
  version = "0.1";
  src = fetchurl { url = "…"; hash = "…"; };
  buildInputs = [ zlib ];
}
```

Scoped ecosystem (conceptual): `python3Packages.requests` is built inside `python3Packages`, sharing that scope’s `python3`, `setuptools`, and sibling libraries.

Overlay sketch—add or override one attribute on top of `prev`:

```nix
final: prev: {
  hello = prev.hello.overrideAttrs (old: {
    postInstall = (old.postInstall or "") + ''
      echo patched > $out/share/hello-patched
    '';
  });
}
```

## See also

- [callPackage](../../03-language/idioms/callPackage.md)
- [Overlays pattern](../../03-language/idioms/overlays-pattern.md)
- [Overlay](../../02-concepts/overlay.md)
- [Channel](../../02-concepts/channel.md)
- [lib](lib.md)
- [stdenv](stdenv.md)
- [mkDerivation](mkDerivation.md)
- [Writing overlays](../overlays-and-overrides/writing-overlays.md)
- [Inputs and outputs (flakes)](../../07-flakes/anatomy/inputs-and-outputs.md)

## References

- [Overview of Nixpkgs](https://nixos.org/manual/nixpkgs/stable/#overview-of-nixpkgs) — what the repository evaluates to
- [Platform Support](https://nixos.org/manual/nixpkgs/stable/#chap-platform-support)
- [Overlays](https://nixos.org/manual/nixpkgs/stable/#chap-overlays)
- [`all-packages.nix`](https://github.com/NixOS/nixpkgs/blob/master/pkgs/top-level/all-packages.nix)
- [`pkgs/by-name/`](https://github.com/NixOS/nixpkgs/tree/master/pkgs/by-name)
- [Contributing to Nixpkgs](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)
- [`makeScope`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.customisation.makeScope)
- [`packagesFromDirectoryRecursive`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.filesystem.packagesFromDirectoryRecursive)
