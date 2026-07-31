---
status: complete
---

# Writing Overlays

## Overview

An **overlay** is a function `final: prev: { … }` that adds a layer to the nixpkgs fixed point. You return a fragment of the package set—new attributes and replacements—without editing the upstream tree.

**Overlay vs override:** an overlay reshapes the whole [package set](../architecture/package-sets.md). `.override` / `.overrideAttrs` return one new derivation and change nothing else in `pkgs` unless you wire that value in (often *inside* an overlay). Prefer an overlay when dependents must see the same change via `final`; prefer a bare override for a one-off in a shell or module. See [Overlay vs Override](../../02-concepts/overlay-vs-override.md).

For the concept and fixed-point mechanics, see [Overlay](../../02-concepts/overlay.md) and [Overlays pattern](../../03-language/idioms/overlays-pattern.md). For patch lists and override APIs, see [Patches and overrides](../packaging/patches-and-overrides.md).

## Details

### Shape

Newer code uses `final` / `prev`; older code often uses `self` / `super`. The return value should look like a slice of [`all-packages.nix`](https://github.com/NixOS/nixpkgs/blob/master/pkgs/top-level/all-packages.nix): top-level names mapping to derivations or nested sets.

```nix
final: prev: {
  myTool = prev.callPackage ./my-tool.nix { };
  hello = prev.hello.overrideAttrs (old: {
    pname = old.pname + "-patched";
  });
}
```

Overlays merge with shallow `//`: later layers replace top-level keys from earlier ones. Nested attrsets are not merged recursively.

### `final` vs `prev`

| Argument | Meaning | Use for |
| --- | --- | --- |
| `final` | The composed set after this overlay and all later overlays | Dependencies of packages you define or override |
| `prev` | The set from nixpkgs and overlays *before* this one | The package you are overriding; helpers such as `callPackage` |

Canonical manual example—dependencies from `final`, original recipe and `callPackage` from `prev`:

```nix
final: prev: {
  boost = prev.boost.override { python = final.python3; };
  rr = prev.callPackage ./pkgs/rr { stdenv = final.stdenv_32bit; };
}
```

### Order

Overlays apply in list order. If two set `python3`, the later one wins at the top level. Put foundational pins (interpreters, stdenv, BLAS providers) before overlays that depend on them. See [Pinning](pinning.md) for revision pins; overlays pin *attributes inside* a given nixpkgs import.

### Installing overlays

**Explicit import** — if you pass `overlays`, nixpkgs does **not** look up path-based overlay files:

```nix
import <nixpkgs> {
  overlays = [ myOverlay anotherOverlay ];
}
```

Do not use that pattern *inside* nixpkgs. `pkgs.extend` / `pkgs.appendOverlays` recompute the fixpoint and are expensive; prefer `overlays` at import time.

**NixOS** — `nixpkgs.overlays` applies to the system’s nixpkgs evaluation only. It does not affect standalone `nix-env` or ad-hoc `import <nixpkgs>` unless you share the same list.

**Path lookup** (when `overlays` is not passed), in order:

1. `<nixpkgs-overlays>` on `NIX_PATH`, if set
2. Else `~/.config/nixpkgs/overlays.nix` (a list of overlays) **or** `~/.config/nixpkgs/overlays/` (`.nix` files and subdirs with `default.nix`, lexicographic order)—error if both exist

Reuse one file as both `nixpkgs.overlays` and `~/.config/nixpkgs/overlays.nix` so NixOS and user tools stay aligned.

### Legacy `packageOverrides`

[`packageOverrides`](packageOverrides.md) is roughly an overlay that only receives `prev`. Prefer overlays for anything you might share, layer, or install from `overlays.nix`.

## Examples

**Add a local package.**

```nix
final: prev: {
  myCli = prev.callPackage ./tools/my-cli.nix {
    inherit (final) lib openssl;
  };
}
```

**Pin a top-level interpreter for the whole import.**

```nix
final: prev: {
  python3 = prev.python312;
}
```

**Override one package’s derivation attrs (set-wide).**

```nix
final: prev: {
  hello = prev.hello.overrideAttrs (old: {
    patches = (old.patches or [ ]) ++ [ ./hello-fix.patch ];
  });
}
```

**Stack two overlays** (base pin, then dependent tweak).

```nix
import <nixpkgs> {
  overlays = [
    (final: prev: { python3 = prev.python312; })
    (final: prev: {
      myApp = prev.myApp.override { python3 = final.python3; };
    })
  ];
}
```

**NixOS + user config** — same overlay list:

```nix
# configuration.nix
{ ... }: {
  nixpkgs.overlays = import ./overlays.nix;
}
```

```nix
# overlays.nix — also usable as ~/.config/nixpkgs/overlays.nix
[
  (final: prev: { /* … */ })
]
```

## References

- [Nixpkgs manual — Overlays](https://nixos.org/manual/nixpkgs/stable/#chap-overlays) — chapter overview
- [Nixpkgs manual — Defining overlays](https://nixos.org/manual/nixpkgs/stable/#sec-overlays-definition) — `final` / `prev`, return shape, `boost` / `rr` example
- [Nixpkgs manual — Installing overlays](https://nixos.org/manual/nixpkgs/stable/#sec-overlays-install) — import, NixOS, path lookup
- [Nixpkgs manual — Overriding](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-override) — `.override` / `.overrideAttrs` vs overlays

## See also

- [Overlay](../../02-concepts/overlay.md) — concept and when to use overlays
- [Overlay vs Override](../../02-concepts/overlay-vs-override.md) — scope: set vs single package
- [Overlays pattern](../../03-language/idioms/overlays-pattern.md) — fixed point, `extends`, shallow merge
- [Package sets](../architecture/package-sets.md) — how `pkgs` is composed
- [Patches and overrides](../packaging/patches-and-overrides.md) — `.override`, `.overrideAttrs`, patches
- [packageOverrides](packageOverrides.md) — legacy hook
- [Pinning](pinning.md) — pinning nixpkgs revisions
