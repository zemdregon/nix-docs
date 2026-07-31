---
status: complete
---

# packageOverrides

## Overview

**`packageOverrides`** is the older nixpkgs **global configuration** hook for reshaping the package set. You set a function `pkgs: { … }` that returns attribute overrides and new packages—similar in spirit to an [overlay](../../02-concepts/overlay.md), but as a single layer wired through `config` rather than a composable list.

The mechanism predates overlays and still appears in the Nixpkgs manual under [Global configuration](https://nixos.org/manual/nixpkgs/stable/#chap-packageconfig). For new work, prefer [overlays](writing-overlays.md): they stack in order, expose both `final` and `prev`, and are easier to share across flakes, NixOS, and user config. **`packageOverrides` is not documented as removed**—treat it as a legacy alternative you may still encounter in older configs and wiki examples.

## Details

**Where it lives.** The usual entry point is `~/.config/nixpkgs/config.nix`:

```nix
{
  packageOverrides = pkgs: {
    # overrides and new attrs
  };
}
```

The same attribute can be passed when importing nixpkgs: `import <nixpkgs> { config.packageOverrides = pkgs: { … }; }`. Nixpkgs merges user config from `~/.config/nixpkgs/config.nix` (and legacy `~/.nixpkgs/config.nix`) unless you override `config` at import time—see the manual’s [Global configuration](https://nixos.org/manual/nixpkgs/stable/#chap-packageconfig) chapter.

**Shape.** The function takes one argument—the current `pkgs` set—and returns a set of attribute overrides, much like `pkgs/top-level/all-packages.nix`. Inside, you typically call `.override` or `.overrideAttrs` on existing packages (see [Overlay vs Override](../../02-concepts/overlay-vs-override.md) for package-level overrides). You can also add new top-level attributes (for example a custom `buildEnv` bundle).

**Relation to overlays.** The manual states that `packageOverrides` **acts as an overlay with only the `prev` argument**—you see the package set before your changes, not the fully composed `final` set. That limits patterns where a new package must depend on another override in the same layer. Overlays apply in list order and are the standard way to compose multiple customization layers; see [Installing overlays](https://nixos.org/manual/nixpkgs/stable/#sec-overlays-install) and [Writing Overlays](writing-overlays.md).

**When it still shows up.**

| Situation | Notes |
| --- | --- |
| Personal `config.nix` from pre-overlay workflows | Often a single `packageOverrides` block |
| Declarative “my packages” envs in config | Manual [Build an environment](https://nixos.org/manual/nixpkgs/stable/#sec-building-environment) examples use `packageOverrides` with `buildEnv` |
| Reading older blogs or configs | May use `packageOverrides` where overlays are used today |

**Not the same name everywhere.** Some language scopes (Python, Lua, PHP, and others) expose their own `packageOverrides` argument on the interpreter or package set. Those are **scoped** customization hooks, not the global nixpkgs `config.packageOverrides` described here.

**Prefer overlays when you can.** If you might add a second layer, share customization via a flake input, or need `final` for cross-references within the same overlay, use [Writing Overlays](writing-overlays.md) instead of growing one monolithic `packageOverrides` function. [Pinning](pinning.md) nixpkgs and layering overlays is the usual modern project layout; global `packageOverrides` in `config.nix` affects user-level commands like `nix-env` and `nix-shell` that read that config.

## Examples

**Override one package in `config.nix`.**

```nix
{
  packageOverrides = pkgs: {
    hello = pkgs.hello.overrideAttrs (old: {
      pname = old.pname + "-patched";
    });
  };
}
```

**Same change as an overlay (preferred for composability).**

```nix
final: prev: {
  hello = prev.hello.overrideAttrs (old: {
    pname = old.pname + "-patched";
  });
}
```

Pass that function in `overlays = [ … ]` when importing nixpkgs, via `nixpkgs.overlays` on NixOS, or under `~/.config/nixpkgs/overlays/`—details in [Writing Overlays](writing-overlays.md).

**Explicit import with `config`.**

```nix
import <nixpkgs> {
  config.packageOverrides = pkgs: {
    jq = pkgs.jq.overrideAttrs (old: {
      patches = (old.patches or [ ]) ++ [ ./jq-local.patch ];
    });
  };
}
```

## References

- [Nixpkgs manual — Modify packages via packageOverrides](https://nixos.org/manual/nixpkgs/stable/#sec-modify-via-packageOverrides)
- [Nixpkgs manual — Global configuration](https://nixos.org/manual/nixpkgs/stable/#chap-packageconfig)
- [Nixpkgs manual — Overriding](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-override) — `.override` and `.overrideAttrs` used inside overrides
- [Nixpkgs manual — Installing overlays](https://nixos.org/manual/nixpkgs/stable/#sec-overlays-install)
- [Nixpkgs manual — Defining overlays](https://nixos.org/manual/nixpkgs/stable/#sec-overlays-definition) — comparison with `packageOverrides`

## See also

- [Writing Overlays](writing-overlays.md) — preferred set-level customization
- [Overlay](../../02-concepts/overlay.md) — concept and composition model
- [Overlay vs Override](../../02-concepts/overlay-vs-override.md) — overlays vs per-package `.override`
- [Package Sets](../architecture/package-sets.md) — how `pkgs` is built and extended
- [Pinning](pinning.md) — fixing nixpkgs revision before applying overrides
