---
status: complete
---

# Android and mobile Nix

## Overview

Nix touches mobile Android in **three separate layers**—do not conflate them:

| Layer | Goal | Primary entry |
|-------|------|---------------|
| **A. Nixpkgs `androidenv`** | Develop or build Android *apps* with a pinned SDK/NDK | [Nixpkgs Android manual](https://nixos.org/manual/nixpkgs/unstable/#android) |
| **B. Robotnix** | Rebuild Android/AOSP *images* (LineageOS, GrapheneOS, …) with Nix | [nix-community/robotnix](https://github.com/nix-community/robotnix) |
| **C. Mobile NixOS** | Run **NixOS on a phone** (Linux userspace, not Android) | [mobile-nixos/mobile-nixos](https://github.com/mobile-nixos/mobile-nixos) |

Layer A is the practical default for app developers. Layers B and C are long-running community projects with very different maturity and hardware requirements.

## Details

### A. Nixpkgs Android SDK tooling (app development)

Nixpkgs ships **`androidenv`** helpers to compose an Android SDK from store paths instead of a hand-installed SDK tree. Typical paths:

- **`android-studio-full`** — convenience attribute bundling a fairly complete SDK (including system images). Equivalent to `androidStudioPackages.stable.full`.
- **`androidenv.composeAndroidPackages { … }`** — explicit composition: platform API levels, build-tools, NDK, emulator, system images, extras. Returns an attribute set; `.androidsdk` is the deployable SDK root.
- **Studio + custom SDK** — `android-studio.withSdk (androidenv.composeAndroidPackages { … }).androidsdk)` wires a composed SDK into Android Studio and exports **`ANDROID_HOME`** / **`ANDROID_NDK_ROOT`** for Gradle and CLI tools.

Most SDK components are **unfree** (Google license terms). Expect `config.allowUnfree = true` (or a narrower predicate) and **`config.android_sdk.accept_license = true`** on the nixpkgs import (or the env var `NIXPKGS_ACCEPT_ANDROID_SDK_LICENSE=1`). Extra / preview licenses can be listed via `composeAndroidPackages`’s `extraLicenses`. First-time builds **download SDK artifacts** and need network access; offline verification of a full SDK closure is often impractical.

Use this layer inside [dev shells](shells-and-direnv.md) or CI the same way as other [language toolchains](language-toolchains.md): pin platforms/NDK versions in Nix, not on the host.

### B. Robotnix (build Android/AOSP with Nix) — **alpha**

**Maturity: alpha / in-development** (last checked upstream README: 2026-07-30).

[Robotnix](https://github.com/nix-community/robotnix) wraps the AOSP multi-repo build (kernel, webview, vendor blobs, signing, OTA, optional apps) in a **NixOS-style module system** (`lib.robotnixSystem` in flakes, or `nix-build` with a `configuration` attrset). Flavors historically include LineageOS, GrapheneOS, and vanilla AOSP (Pixel); optional modules cover MicroG, F-Droid, custom kernels, AVB signing, and more.

Upstream status (README, 2026-07-30):

- Project is being picked up by a new maintainer after ~3 years unmaintained; many components remain in disrepair.
- LineageOS and GrapheneOS upstream tracking works **for now** but may change.
- Explicit warning: **not ready for daily use** — treat as alpha.

Component maintenance (from upstream status table; snapshot 2026-07-30):

| Area | Maintained (per README) |
|------|-------------------------|
| LineageOS, GrapheneOS, signing, OTA updater, F-Droid, MicroG, Pixel vendor blobs (adevtool) | Yes |
| Vanilla AOSP, Waydroid, Anbox, Webview, kernels, emulator, Chromium source build, Seedvault, Auditor, hosts-file module | No |

Build requirements are heavy (hundreds of GB disk, 16GB+ RAM, long build times, user namespaces). Upstream also warns against mounting `/tmp` on `tmpfs`—intermediate AOSP artifacts can exhaust RAM. **Do not treat Robotnix as a production daily-driver path**; use it for experimentation, research, or custom ROM builds when you accept alpha breakage and self-support.

Robotnix builds **Android**; it does not install NixOS on a handset.

### C. Mobile NixOS — “NixOS on your phone”

**Maturity: experimental; device-dependent** (last checked upstream `README.adoc` on `development`: 2026-07-30).

[Mobile NixOS](https://github.com/mobile-nixos/mobile-nixos) is a **superset of NixOS** aimed at abstracting differences between mobile devices—mainline Linux on supported phones, not a rebuilt Android image. Upstream docs: [mobile-nixos.github.io](https://mobile-nixos.github.io/) (rendered from the repo `doc/` tree on the `development` branch).

Expectations from upstream (README / about docs):

- Builds are expected to succeed only against **nixpkgs unstable** (not stable channels).
- Support is **per device**—the project targets many handsets as building blocks, but telephony, sensors, and daily-driver polish vary by device; read device docs before assuming anything works.
- **No published CI artifacts** for now; follow project docs to build for supported hardware.

Distinct from Robotnix: Mobile NixOS replaces the phone OS with NixOS/Linux; Robotnix produces Android ROM images.

### Maturity at a glance

| | App/SDK dev (`androidenv`) | Robotnix | Mobile NixOS |
|---|---------------------------|----------|----------------|
| **Typical user** | App developer, CI | ROM builder, researcher | Enthusiast on supported hardware |
| **Maturity** | Stable nixpkgs tooling | **Alpha** — not daily-driver ready | **Experimental** — device-specific |
| **Output** | SDK + tools in store | Flashable Android `img`/OTA | NixOS system on phone |
| **Channel** | Match your nixpkgs pin | Robotnix flake/input + upstream AOSP | **nixpkgs unstable** |
| **Unfree / licenses** | Common (SDK) | AOSP/vendor blobs (separate legal stack) | Device firmware blobs; MIT for repo expressions |

## Examples

Minimal dev shell with a composed SDK (illustrative pin; adjust `platformVersions` / ABI to your project). SDK fetch and license acceptance may fail without network and unfree config:

```nix
# flake.nix (excerpt)
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
          android_sdk.accept_license = true;
        };
      };
      android = pkgs.androidenv.composeAndroidPackages {
        platformVersions = [ "34" "35" "latest" ];
        includeNDK = true;
      };
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ android.androidsdk pkgs.jdk17 ];
        shellHook = ''
          export ANDROID_HOME="${android.androidsdk}/libexec/android-sdk"
          export ANDROID_NDK_ROOT="$ANDROID_HOME/ndk-bundle"
        '';
      };
    };
}
```

For a batteries-included Studio bundle without manual composition, `pkgs.android-studio-full` (or `androidStudioPackages.stable.full`) is the quick nixpkgs attribute; see the manual for `withSdk` if you need a custom composition.

## References

- [Nixpkgs manual — Android](https://nixos.org/manual/nixpkgs/unstable/#android)
- [nix-community/robotnix](https://github.com/nix-community/robotnix) (alpha; see README status table)
- [Robotnix docs](https://docs.robotnix.org)
- [mobile-nixos/mobile-nixos](https://github.com/mobile-nixos/mobile-nixos)
- [Mobile NixOS website](https://mobile-nixos.github.io/)

## See also

- [Shells and direnv](shells-and-direnv.md) — wiring SDK env vars in `mkShell`
- [Language toolchains](language-toolchains.md) — dev shells vs packaging
- [Nix on other distros](../10-home-and-user/nix-on-other-distros.md) — Android dev on non-NixOS hosts with Nix
- [NixOS modules in nixpkgs](../13-implementations/module-ecosystems/nixpkgs-nixos.md) — module-system context for Mobile NixOS and Robotnix
- [NixOS installation](../09-nixos/installation/README.md) — general install concepts (Mobile NixOS is device-specific)
