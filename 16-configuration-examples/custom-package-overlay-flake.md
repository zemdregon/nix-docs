---
status: complete
last-checked: 2026-08
---

# Custom package and overlay flake

## Overview

This walkthrough combines three nixpkgs patterns in one flake: a **local package** defined as a `callPackage`-shaped recipe, a **set-level overlay** that adds that package and patches an upstream attr (`hello`), and **flake outputs** so you can `nix build` the package and wire the same overlay into a NixOS host. Snippets wrap `pkgs.hello`—no tarball fetch or placeholder hashes that pretend to build.

For the concept layer see [Overlay](../02-concepts/overlay.md) and [callPackage](../03-language/idioms/callPackage.md). For packaging and overlay mechanics see [Simple package](../06-nixpkgs/packaging/simple-package.md) and [Writing overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md). For flake output conventions see [Packages, apps, devShells](../07-flakes/workflows/packages-apps-devShells.md).

## Details

### What you get

One repository with a recipe under `pkgs/`, an overlay file, a root `flake.nix` that exposes `packages.<system>.default` and `overlays.default`, and an optional NixOS module that applies the overlay from the flake input. After `nix flake lock`, `nix build` produces the custom wrapper; `nixos-rebuild` on a configured host sees both the new attr and the patched `hello` everywhere `pkgs` is used.

### Domains composed

| Domain | Role in this example |
|--------|----------------------|
| [Overlay](../02-concepts/overlay.md) | `final: prev:` layer that adds attrs to the fixed point |
| [Overlay vs override](../02-concepts/overlay-vs-override.md) | Overlay reshapes `pkgs`; `.overrideAttrs` inside it tweaks one derivation set-wide |
| [callPackage](../03-language/idioms/callPackage.md) | Recipe function whose arguments are filled from the package set |
| [Hashing and inputs](../04-store-and-build/hashing-and-inputs.md) | Input-addressed builds here; tarball fetches would need [FOD](../02-concepts/fixed-output-derivation.md) hashes from a real build |
| [Simple package](../06-nixpkgs/packaging/simple-package.md) | `stdenv.mkDerivation` recipe shape (this example skips upstream fetch) |
| [Writing overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md) | `final` / `prev`, NixOS `nixpkgs.overlays` |
| [Packages, apps, devShells](../07-flakes/workflows/packages-apps-devShells.md) | `packages.${system}.default`, exporting `overlays` |
| [NixOS configurations](../07-flakes/workflows/nixos-configurations.md) | `nixosConfigurations` + `specialArgs` for flake inputs |
| [configuration.nix](../09-nixos/configuration/configuration-nix.md) | Host module that sets `nixpkgs.overlays` and `environment.systemPackages` |

**Overlay vs override:** the overlay returns a fragment of `pkgs` merged into the fixed point—anything resolving `pkgs.hello` or `pkgs.hello-wrapper` sees your versions. A bare `.override` on one value outside an overlay only affects that binding. This example uses `.overrideAttrs` *inside* the overlay so the patched `hello` is set-wide; see [Overlay vs override](../02-concepts/overlay-vs-override.md).

**When you need fetch:** recipes that download upstream sources use fixed-output fetchers (`fetchurl`, `fetchFromGitHub`, …). Those are [fixed-output derivations](../02-concepts/fixed-output-derivation.md); you obtain the `hash` from a failed build or `nix-prefetch-url`, not by guessing. The corpus fixture [fod-fetchurl.nix](../meta/examples/fod-fetchurl.nix) shows the shape with an obviously invalid hash. This walkthrough avoids FOD entirely by wrapping `hello` from nixpkgs.

### File layout

```text
.
├── flake.nix
├── flake.lock                 # after nix flake lock
├── overlay.nix                # final: prev: { … }
├── pkgs/
│   └── hello-wrapper.nix      # callPackage recipe (see corpus simple-package.nix)
└── configuration.nix          # optional NixOS host module
```

Larger config repos split `hosts/` and `overlays/` the same way; see [Config repo layout](../07-flakes/workflows/config-repo-layout.md).

### Annotated pieces

**`pkgs/hello-wrapper.nix`** — same idea as the vault fixture [simple-package.nix](../meta/examples/simple-package.nix): a function `{ lib, stdenv, hello }: …` built with `stdenv.mkDerivation`, depending on nixpkgs' `hello` instead of fetching upstream:

```nix
{ lib, stdenv, hello }:

stdenv.mkDerivation {
  pname = "hello-wrapper";
  version = "0.1";

  dontUnpack = true;
  buildInputs = [ hello ];

  installPhase = ''
    mkdir -p $out/bin
    ln -s ${hello}/bin/hello $out/bin/hello-demo
  '';

  meta = with lib; {
    description = "Illustrative wrapper around hello for callPackage teaching";
    license = licenses.mit;
    platforms = platforms.all;
  };
}
```

**`overlay.nix`** — matches the corpus [overlay-snippet.nix](../meta/examples/overlay-snippet.nix): add the local package via `prev.callPackage`, patch `hello` with `prev.hello.overrideAttrs`:

```nix
final: prev: {
  hello-wrapper = prev.callPackage ./pkgs/hello-wrapper.nix { };

  hello = prev.hello.overrideAttrs (old: {
    pname = old.pname + "-patched";
  });
}
```

Use **`prev`** for the package you replace and for `callPackage`; use **`final`** when a new package's dependencies must see the composed set (not needed in this minimal overlay).

**`flake.nix`** — pin nixpkgs, export the overlay, build `hello-wrapper` under an overlaid import, expose `packages.<system>.default`, optionally define `nixosConfigurations`:

```nix
{
  description = "Local callPackage recipe + overlay + flake packages";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ self.overlays.default ];
      };
    in {
      overlays.default = import ./overlay.nix;

      packages.${system} = {
        default = pkgs.hello-wrapper;
        hello-wrapper = pkgs.hello-wrapper;
      };

      nixosConfigurations.demo = nixpkgs.lib.nixosSystem {
        specialArgs = { inherit inputs; };
        modules = [ ./configuration.nix ];
      };
    };
}
```

Import nixpkgs **with** `overlays = [ self.overlays.default ]` when defining `packages` so `pkgs.hello-wrapper` exists—the overlay adds that attr. Flakes can also expose `overlays.default` for downstream consumers without copying the file.

**NixOS host** — pass flake `inputs` through `specialArgs`, then reference the overlay output (same pattern as importing `./overlays.nix` in [Writing overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md)):

```nix
{ inputs, pkgs, ... }: {
  nixpkgs.overlays = [ inputs.self.overlays.default ];

  networking.hostName = "demo";

  environment.systemPackages = with pkgs; [
    hello-wrapper   # from overlay
    hello           # patched "-patched" pname via overlay
  ];

  system.stateVersion = "26.05";
}
```

`nixpkgs.overlays` applies to **system** nixpkgs evaluation only—it does not change standalone `nix build` unless you pass the same overlay list at import time.

### Activate / verify

```bash
# nix.conf or --extra-experimental-features 'nix-command flakes'
nix flake lock
nix flake check
nix build                    # packages.<system>.default → ./result/bin/hello-demo
./result/bin/hello-demo

# optional NixOS (on a real or VM host with matching platform)
sudo nixos-rebuild build --flake .#demo
```

`nix flake check` evaluates `packages` and any `nixosConfigurations.*.config.system.build.toplevel` derivations.

### Failure modes

| Symptom | Likely cause |
|---------|----------------|
| `attribute 'hello-wrapper' missing` | Built `packages` against plain `legacyPackages` without applying `self.overlays.default` |
| Patched `hello` not visible in a module | Overlay not in `nixpkgs.overlays`, or a module imported `pkgs` via `specialArgs` bypassing module nixpkgs |
| `experimental Nix feature 'flakes' is disabled` | Enable [`flakes`](../08-experimental-features/flakes.md) and [`nix-command`](../08-experimental-features/nix-command.md) |
| Fetch hash errors after adding tarball `src` | Expected for FOD—copy hash from Nix's error; see [Hashing and inputs](../04-store-and-build/hashing-and-inputs.md) |

## Examples

Full tree (illustrative pin; adapt `system` and `stateVersion`):

**`pkgs/hello-wrapper.nix`** — identical to the Annotated pieces block above (corpus: [simple-package.nix](../meta/examples/simple-package.nix)).

**`overlay.nix`**

```nix
final: prev: {
  hello-wrapper = prev.callPackage ./pkgs/hello-wrapper.nix { };

  hello = prev.hello.overrideAttrs (old: {
    pname = old.pname + "-patched";
  });
}
```

**`flake.nix`**

```nix
{
  description = "Local callPackage recipe + overlay + flake packages";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ self.overlays.default ];
      };
    in {
      overlays.default = import ./overlay.nix;

      packages.${system} = {
        default = pkgs.hello-wrapper;
        hello-wrapper = pkgs.hello-wrapper;
      };

      nixosConfigurations.demo = nixpkgs.lib.nixosSystem {
        specialArgs = { inherit inputs; };
        modules = [ ./configuration.nix ];
      };
    };
}
```

**`configuration.nix`**

```nix
{ inputs, pkgs, ... }: {
  nixpkgs.overlays = [ inputs.self.overlays.default ];

  networking.hostName = "demo";

  environment.systemPackages = with pkgs; [
    hello-wrapper
    hello
  ];

  system.stateVersion = "26.05";
}
```

**Operator sequence**

```bash
nix flake lock
nix build
./result/bin/hello-demo
nix flake check
sudo nixos-rebuild build --flake .#demo   # optional
```

To consume only the overlay from another flake, add this repo as an input and set `nixpkgs.overlays = [ inputs.myPkg.overlays.default ];` in that flake's NixOS modules—the same option as `inputs.self` above.

## References

- [Nixpkgs manual — Defining overlays](https://nixos.org/manual/nixpkgs/stable/#sec-overlays-definition) — `final` / `prev`, return shape
- [Nixpkgs manual — callPackage](https://nixos.org/manual/nixpkgs/stable/#chap-callpackage) — auto-fill and `.override`
- [Nixpkgs manual — Installing overlays](https://nixos.org/manual/nixpkgs/stable/#sec-overlays-install) — import and NixOS
- [nix.dev — Flakes](https://nix.dev/concepts/flakes) — inputs, outputs, locking

## See also

- [Overlay](../02-concepts/overlay.md)
- [Overlay vs override](../02-concepts/overlay-vs-override.md)
- [callPackage](../03-language/idioms/callPackage.md)
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md)
- [Simple package](../06-nixpkgs/packaging/simple-package.md)
- [Writing overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md)
- [Packages, apps, devShells](../07-flakes/workflows/packages-apps-devShells.md)
- [Config repo layout](../07-flakes/workflows/config-repo-layout.md)
- [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md)
- [Example corpus](../meta/examples/README.md) — [simple-package.nix](../meta/examples/simple-package.nix), [overlay-snippet.nix](../meta/examples/overlay-snippet.nix)
