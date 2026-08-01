---
status: complete
last-checked: 2026-08
---

# Package Sets

## Overview

A **package set** is a large attribute set whose values are mostly derivations (and nested sets of the same shape). Nixpkgs evaluates its tree into such a set; consumers receive it as `pkgs` from a [channel](../../02-concepts/channel.md), `import <nixpkgs> { }`, or a flake’s `nixpkgs` input ([inputs and outputs](../../07-flakes/anatomy/inputs-and-outputs.md)). The set also carries NixOS modules, cross-compilation variants, and helpers like [`lib`](lib.md)—but for most users `pkgs` means “everything installable,” wired through [stdenv](stdenv.md) and [`mkDerivation`](mkDerivation.md).

## Boundaries

- **Not a packaging tutorial.** Language builders, FOD hashes, and ecosystem idioms live under [packaging](../packaging/README.md) surveys; this page is the shape of `pkgs` and where attributes hang.
- **Not overlay mechanics.** Fixed-point overlay syntax and `.override` / `.overrideAttrs` are covered in [overlays](../../02-concepts/overlay.md), [writing overlays](../overlays-and-overrides/writing-overlays.md), and the [overlays pattern](../../03-language/idioms/overlays-pattern.md).
- **Not Hydra / CI ops.** Channel lag, ofborg, and staging branches belong under [contribution](../contribution/README.md); here only the consumer fact that “in `pkgs` ≠ binary available.”
- **Not a full directory map.** Category hierarchy paths and every language set’s registration file change; follow [CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md) and [`pkgs/by-name/README.md`](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/README.md) for current rules.

## Details

### Top-level composition

Historically, most package names were registered in [`pkgs/top-level/all-packages.nix`](https://github.com/NixOS/nixpkgs/blob/master/pkgs/top-level/all-packages.nix): a fixed-point over `self` that imports package files and attaches metadata. Newer top-level packages often live under [`pkgs/by-name/`](https://github.com/NixOS/nixpkgs/tree/master/pkgs/by-name/) as `…/<ab>/<name>/package.nix` and are discovered from the directory tree.

### by-name vs all-packages (where does my package go?)

Contributor-facing high level—exact checks evolve; cite the live docs when opening a PR:

| Situation | Prefer | Notes (from by-name docs / CONTRIBUTING) |
|-----------|--------|------------------------------------------|
| New **top-level** package via `pkgs.callPackage` | [`pkgs/by-name/`](https://github.com/NixOS/nixpkgs/tree/master/pkgs/by-name/) | Auto-included; no hand entry in `all-packages.nix` needed for the default call |
| Need non-default `callPackage` arguments | Keep / add entry in `all-packages.nix` | Changing implicit defaults must stay visible; see [Changing implicit attribute defaults](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/README.md#changing-implicit-attribute-defaults) |
| Package belongs in a **nested** set (`python3Packages.*`, etc.) | That set’s registration path | by-name is **top-level only**; it excludes `pkgs.python3Packages.callPackage` and similar scopes ([Limitations](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/README.md#limitations)) |
| Older packages still in the category hierarchy | Leave or migrate deliberately | Manual migration is ongoing; auto-merge of maintainer PRs currently requires the package in `pkgs/by-name` ([CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)) |

Do not invent placement policy beyond what those documents state. When unsure, match a sibling package in the same ecosystem and ask reviewers.

### callPackage and siblings

Most top-level entries are built with [callPackage](../../03-language/idioms/callPackage.md): a function `{ stdenv, fetchurl, … }: …` gets its arguments filled from the set by name, with optional overrides at the call site. Nested sets expose their own `callPackage` (same idea, different auto-fill scope).

### Nested and scoped sets

Language ecosystems and kernel-related trees are not flat `pkgs.<name>` entries. They appear as nested attrsets—often created with `lib.customisation.makeScope` / `newScope`—so packages inside the scope can depend on siblings (same interpreter, same GHC, same kernel headers) without polluting the top level. See [`makeScope`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.customisation.makeScope) and `lib.packagesFromDirectoryRecursive` in the [Functions reference](https://nixos.org/manual/nixpkgs/stable/#chap-functions).

Common nested sets (surveys, not full APIs):

| Set | Role | Survey / deep dive |
|-----|------|--------------------|
| `python3Packages` | Libraries and apps for the default CPython 3; depend on siblings for one interpreter | [Python / Node / Rust / Go](../packaging/python-node-rust-go.md) |
| `haskellPackages` | Default GHC + curated Hackage-facing set (`haskell.packages.*` for other compilers) | [Haskell packaging](../packaging/haskell-packaging.md) |
| `perlPackages` | CPAN-style libs via `buildPerlPackage` | [JVM / PHP and others](../packaging/jvm-php-and-others.md) |
| `linuxPackages` (and `linuxPackages_*`) | Kernel + out-of-tree modules for a kernel version; NixOS `boot.kernelPackages` picks one | Manual [Linux kernel](https://nixos.org/manual/nixpkgs/stable/#sec-linux-kernel); not a language survey |

Many other scopes exist (`nodePackages`, `ocamlPackages`, `javaPackages`, …)—same pattern: pick the set that matches the runtime/compiler, then package inside it.

### Overlays and overrides

The package set is a fixed point: `final` (self) and `prev` (super) in overlay notation. [Overlays](../../02-concepts/overlay.md) reshape `pkgs` by layering functions that add, replace, or tweak attributes—see the [overlays chapter](https://nixos.org/manual/nixpkgs/stable/#chap-overlays) and [writing overlays](../overlays-and-overrides/writing-overlays.md).

### Platforms, Hydra, and channels

Not every attribute is built on every platform. Support tiers and `meta.platforms` / broken markers steer Hydra and ofborg; what lands on [channels](../../02-concepts/channel.md) lags `master` until release-critical tests pass. A package existing in `pkgs` does not guarantee a binary substitute on your system. See [Overview of Nixpkgs](https://nixos.org/manual/nixpkgs/stable/#overview-of-nixpkgs) and [Platform Support](https://nixos.org/manual/nixpkgs/stable/#chap-platform-support).

### Failure modes

**Wrong scope (e.g. `python2` / legacy vs `python3Packages`).** Mixing packages from different interpreters or language sets yields ABI/`PYTHONPATH` mismatches, missing attrs, or “works in repl, fails at runtime.” Prefer the current default set (`python3Packages`, not retired Python 2 trees) and take every library dependency from that same scope.

**Overlay that breaks the fixed point.** Referring to `prev` where `final` is required (or introducing cycles with self-references) causes infinite recursion or silently inconsistent dependency graphs. Depend on `final` for packages you also override; see the [overlays pattern](../../03-language/idioms/overlays-pattern.md).

**Expecting a Hydra binary for every attr.** Evaluation success ≠ substitute on `cache.nixos.org`. Broken/unfree/unsupported-platform packages, rarely built nested attrs, and fresh `master` commits often require a local build.

### Decision table: top-level vs nested vs overlay

| Need | Use | Why |
|------|-----|-----|
| Installable CLI/lib used across ecosystems | Top-level `pkgs.foo` | Default consumer path; new packages → by-name when eligible |
| Library tied to one interpreter/compiler/kernel | Nested set (`python3Packages.bar`, …) | Shared scope and versioning; by-name does not apply |
| Local or org-specific patch / extra package | Overlay (or flake overlay) | Layer on the fixed point without forking the whole tree |
| One-off tweak in a shell/module | `.override` / `.overrideAttrs` | Narrower than an overlay when you only need one call site |

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
- [Haskell packaging](../packaging/haskell-packaging.md)
- [Python / Node / Rust / Go](../packaging/python-node-rust-go.md)
- [JVM / PHP and others](../packaging/jvm-php-and-others.md)
- [Overlays pattern](../../03-language/idioms/overlays-pattern.md)
- [Overlay](../../02-concepts/overlay.md)
- [Channel](../../02-concepts/channel.md)
- [lib](lib.md)
- [stdenv](stdenv.md)
- [mkDerivation](mkDerivation.md)
- [Writing overlays](../overlays-and-overrides/writing-overlays.md)
- [Inputs and outputs (flakes)](../../07-flakes/anatomy/inputs-and-outputs.md)

## References

- [Overview of Nixpkgs](https://nixos.org/manual/nixpkgs/stable/#overview-of-nixpkgs) — what the repository evaluates to; Hydra and channels
- [Platform Support](https://nixos.org/manual/nixpkgs/stable/#chap-platform-support)
- [Overlays](https://nixos.org/manual/nixpkgs/stable/#chap-overlays)
- [Linux kernel](https://nixos.org/manual/nixpkgs/stable/#sec-linux-kernel) — `linuxPackages` / custom kernels
- [`pkgs/by-name/README.md`](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/README.md) — name-based top-level packages, limitations vs nested sets
- [Contributing to Nixpkgs](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)
- [`all-packages.nix`](https://github.com/NixOS/nixpkgs/blob/master/pkgs/top-level/all-packages.nix)
- [`pkgs/by-name/`](https://github.com/NixOS/nixpkgs/tree/master/pkgs/by-name)
- [`makeScope`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.customisation.makeScope)
- [`packagesFromDirectoryRecursive`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.filesystem.packagesFromDirectoryRecursive)
