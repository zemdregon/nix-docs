---
status: draft
---

# Unfree packages and license policy

## Overview

Nixpkgs records each package’s license in `meta.license`. Packages whose license is classified as **unfree** (proprietary or redistribution-restricted) are **refused by default** at evaluation time unless you opt in. Opt-in happens through nixpkgs **`config`**: `allowUnfree`, a narrower **`allowUnfreePredicate`**, or—outside explicit `import nixpkgs` calls—the Nix CLI setting **`allow-unfree`** in [`nix.conf`](../../05-cli-and-tooling/config/nix-conf.md).

Where you set policy depends on **which evaluation** needs the package: a NixOS system, a Home Manager profile, a flake dev shell, or an ad-hoc `nix shell` / `nix run`. The same knob names recur (`nixpkgs.config.*` on modules, `config` on `import nixpkgs`, `allow-unfree` in user `nix.conf`), but each layer only affects evaluations that read that configuration.

## Details

### How nixpkgs decides “unfree”

Every derivation built with [`mkDerivation`](mkDerivation.md) can set `meta.license` to a value from `lib.licenses` (or a list of them). Nixpkgs treats licenses in the unfree family—`lib.licenses.unfree`, `unfreeRedistributable`, and related markers—as requiring explicit permission. If neither `config.allowUnfree` nor `config.allowUnfreePredicate` permits the package, evaluation fails with an error naming the blocked attribute.

This is a **distribution policy** gate, not a legal review: you are declaring that you accept the upstream license terms for those artifacts. Nixpkgs still ships the expressions; it only blocks them until config allows installation.

### `allowUnfree` vs `allowUnfreePredicate`

| Setting | Effect |
|---------|--------|
| `allowUnfree = true` | Permit every package nixpkgs marks unfree. Simplest; widest blast radius. |
| `allowUnfreePredicate = pkg: …` | Permit only packages for which the function returns `true`. Typical checks: `lib.getName pkg`, `lib.getLicenseFromMeta pkg`, or prefix lists. |

For shared or corporate configs, prefer a **predicate** (or a small allowlist function) over blanket `allowUnfree` so only known-needed proprietary packages enter the closure. Ecosystem helpers exist—for example CUDA’s `pkgs._cuda.lib.allowUnfreeCudaPredicate` (see [CUDA, ROCm, and ML](../../11-development/cuda-rocm-ml.md)).

Both options are fields on the **`config`** argument to `import nixpkgs { }` / `nixpkgs.legacyPackages`, and on **`nixpkgs.config`** in NixOS and Home Manager module trees.

### Where to set policy

**NixOS (system-wide).** In [configuration.nix](../../09-nixos/configuration/configuration-nix.md) or an imported module:

```nix
nixpkgs.config.allowUnfree = true;
# or
nixpkgs.config.allowUnfreePredicate = pkg: builtins.elem (lib.getName pkg) [ "steam" "nvidia-settings" ];
```

This applies to the system’s `pkgs` (services, `environment.systemPackages`, module internals). Flake-based NixOS can also pass config through `nixpkgs.options` or by fixing `nixpkgs` input imports in the flake—same `config` keys.

**Home Manager.** HM evaluates its own nixpkgs import for `home.packages` and program modules. Set `nixpkgs.config.allowUnfree` (or a predicate) in the Home Manager configuration—the same option path as on NixOS. When HM runs as a NixOS submodule, system and home evaluations are separate unless you align both; user-only unfree tools (proprietary fonts, licensed IDEs) often belong on the HM side. See [Home Manager](../../13-implementations/module-ecosystems/home-manager.md).

**Flakes and dev shells.** Pass `config` when instantiating nixpkgs in `outputs`:

```nix
pkgs = import nixpkgs {
  inherit system;
  config.allowUnfree = true;
};
```

Use the same pattern inside `devShells` / `shell.nix` so `buildInputs` can reference unfree packages. See [packages, apps, and devShells](../../07-flakes/workflows/packages-apps-devShells.md).

**Ad-hoc CLI (`nix run`, `nix shell`, impure nixpkgs).** When the CLI pulls nixpkgs without your flake’s pinned `config`, user **`allow-unfree = true`** in `~/.config/nix/nix.conf` opts in for those commands. Documented in the Nix manual and summarized on the [nix.conf](../../05-cli-and-tooling/config/nix-conf.md) page. This does **not** replace `nixpkgs.config` on a NixOS or HM rebuild—it only affects evaluations that honor the user/daemon nix.conf merge.

### Common unfree needs

Many “batteries included” features pull unfree packages once enabled:

- **GPU / ML** — NVIDIA CUDA, cuDNN, some ROCm-adjacent blobs ([CUDA, ROCm, and ML](../../11-development/cuda-rocm-ml.md)).
- **Gaming** — Steam and Proton wrappers ([Gaming, Steam, and Proton](../../09-nixos/desktop/gaming-steam-proton.md)).
- **Firmware** — `hardware.enableAllFirmware` beyond redistributable sets ([firmware and microcode](../../09-nixos/configuration/firmware-and-microcode.md)).
- **Mobile SDKs** — Android SDK components and license acceptance ([Android and mobile](../../11-development/android-and-mobile.md)).
- **Scientific stacks** — Intel MKL and similar proprietary math libraries.

Enable only what you need; use predicates scoped to those names when possible.

### Related but separate: `permittedInsecurePackages`

`config.permittedInsecurePackages` lists **package names** (strings) that are allowed despite known security advisories flagged in nixpkgs. That is an **insecure-build exception**, not a license exception. A package can be free yet blocked for insecurity, or unfree yet not insecure—configure both independently when needed.

## Examples

NixOS: allow all unfree (simple desktop):

```nix
{ nixpkgs.config.allowUnfree = true; }
```

NixOS: allow only Steam-related names:

```nix
{ lib, ... }: {
  nixpkgs.config.allowUnfreePredicate = pkg:
    lib.strings.hasPrefix "steam" (lib.getName pkg);
}
```

Flake `pkgs` with CUDA predicate:

```nix
pkgs = import nixpkgs {
  inherit system;
  config = {
    allowUnfreePredicate = pkg:
      builtins.elem (lib.getName pkg) [ "cudatoolkit" "cudnn" ];
  };
};
```

User `~/.config/nix/nix.conf` for impure commands:

```ini
allow-unfree = true
```

Dev shell (`shell.nix` or flake fragment):

```nix
{ pkgs ? import <nixpkgs> { config.allowUnfree = true; } }:
pkgs.mkShell { buildInputs = [ pkgs.jdk ]; }
```

## References

- [Nixpkgs manual — Configuring Nixpkgs](https://nixos.org/manual/nixpkgs/stable/#sec-configuring-nixpkgs) — `config`, `allowUnfree`, `allowUnfreePredicate`, `permittedInsecurePackages`
- [Nix manual — `allow-unfree`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-allow-unfree) — user/daemon setting for impure nixpkgs use

## See also

- [Package sets](package-sets.md) — how `pkgs` is built from nixpkgs
- [mkDerivation](mkDerivation.md) — `meta.license` on derivations
- [configuration.nix](../../09-nixos/configuration/configuration-nix.md) — NixOS host policy
- [nix.conf](../../05-cli-and-tooling/config/nix-conf.md) — `allow-unfree` for CLI-driven evals
- [CUDA, ROCm, and ML](../../11-development/cuda-rocm-ml.md)
- [Gaming, Steam, and Proton](../../09-nixos/desktop/gaming-steam-proton.md)
- [Home Manager](../../13-implementations/module-ecosystems/home-manager.md)
- [packages, apps, and devShells](../../07-flakes/workflows/packages-apps-devShells.md)
