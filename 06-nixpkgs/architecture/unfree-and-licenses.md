---
status: complete
last-checked: 2026-08
---

# Unfree packages and license policy

## Overview

Nixpkgs records each package’s license in `meta.license`. Packages whose license is classified as **unfree** (proprietary or redistribution-restricted) are **refused by default** at evaluation time unless you opt in. Opt-in happens through nixpkgs **`config`**: `allowUnfree`, a narrower **`allowUnfreePredicate`**, the additive NixOS option **`nixpkgs.config.allowUnfreePackages`**, or—outside explicit `import nixpkgs` calls—the user **`~/.config/nixpkgs/config.nix`** file and the **`NIXPKGS_ALLOW_UNFREE`** environment variable (the latter requires **`--impure`** on flake-driven CLI commands).

Where you set policy depends on **which evaluation** needs the package: a NixOS system, a Home Manager profile, a flake dev shell, or an ad-hoc `nix shell` / `nix run`. The same knob names recur (`nixpkgs.config.*` on modules, `config` on `import nixpkgs`), but each layer only affects evaluations that read that configuration. NixOS `nixpkgs.config` does **not** flow to impure `nix shell nixpkgs#…` invocations.

## Details

### How nixpkgs decides “unfree”

Every derivation built with [`mkDerivation`](mkDerivation.md) can set `meta.license` to a value from `lib.licenses` (or a list of them). The check uses `lib.licenses.isFree`: any license with `free = false` (including `unfree`, `unfreeRedistributable`, and `unfreeRedistributableFirmware`) triggers the unfree gate unless config permits it. If neither `config.allowUnfree` nor `config.allowUnfreePredicate` (nor `allowUnfreePackages` on NixOS) permits the package, evaluation fails with an error naming the blocked attribute and its license string.

This is a **distribution policy** gate, not a legal review: you are declaring that you accept the upstream license terms for those artifacts. Nixpkgs still ships the expressions; it only blocks them until config allows installation. Unfree packages are not built on Hydra and typically have no public binary cache.

### `unfree` vs `unfreeRedistributable`

Nixpkgs distinguishes license markers by **what you may redistribute**, not by whether evaluation blocks them—both require `allowUnfree` or a predicate.

| License marker | `free` | Meaning |
|----------------|--------|---------|
| `lib.licenses.unfreeRedistributable` | `false` | Proprietary, but the **built output** may be redistributed (e.g. unmodified vendor binaries). May appear in the Nixpkgs channel tarball. |
| `lib.licenses.unfreeRedistributableFirmware` | `false` | Same idea for firmware blobs; separate marker so firmware policy can differ from application policy. |
| `lib.licenses.unfree` | `false` | Proprietary and **not redistributable**—you may build locally, but the output must not be redistributed. |

**Practical consequence:** maintainers choose the marker that matches upstream terms. If a builder **modifies** a redistributable binary (e.g. `patchelf` on NVIDIA drivers), the license is usually `unfree`, not `unfreeRedistributable`. From your config’s perspective, all three still need the same opt-in; the distinction matters for channel policy and maintainer obligations, not for which `config` key you set.

### `allowUnfree` vs `allowUnfreePredicate`

| Setting | Effect |
|---------|--------|
| `allowUnfree = true` | Permit every package nixpkgs marks unfree. Simplest; widest blast radius. |
| `allowUnfreePredicate = pkg: …` | Permit only packages for which the function returns `true`. Typical checks: `lib.getName pkg`, `lib.getLicenseFromMeta pkg`, or prefix lists. |
| `allowUnfreePackages` (NixOS only) | List of package **names** (strings). Merges additively across modules; composes with `allowUnfreePredicate`. Lets a service module allow its own unfree deps without global `allowUnfree`. |

For shared or corporate configs, prefer a **predicate** or **`allowUnfreePackages`** over blanket `allowUnfree` so only known-needed proprietary packages enter the closure. Ecosystem helpers exist—for example CUDA’s `pkgs._cuda.lib.allowUnfreeCudaPredicate` (see [CUDA, ROCm, and ML](../../11-development/cuda-rocm-ml.md)).

All three are fields on the **`config`** argument to `import nixpkgs { }` / `nixpkgs.legacyPackages`, and on **`nixpkgs.config`** in NixOS and Home Manager module trees.

### Where policy applies (scope)

| Context | Config mechanism | Affects | Does **not** affect |
|---------|------------------|---------|---------------------|
| **NixOS system** | `nixpkgs.config.*` in system modules; optional pre-built `pkgs` passed to `nixosSystem` | `environment.systemPackages`, `systemd` services, NixOS module internals, system-wide firmware options | HM user profile (unless shared `pkgs`); impure `nix shell nixpkgs#…` |
| **Home Manager** | `nixpkgs.config.*` in HM modules (same option path) | `home.packages`, `programs.*`, user services | NixOS system `pkgs` unless `home-manager.useGlobalPkgs` shares one instantiation |
| **Flake `devShells` / `packages`** | `config` on `import inputs.nixpkgs { … }` or `nixpkgs.legacyPackages` with config | That flake output’s `pkgs` only | NixOS/HM rebuilds unless they import the same configured `pkgs` |
| **Ad-hoc CLI** (`nix shell`, `nix run`, channels) | `~/.config/nixpkgs/config.nix`; `NIXPKGS_ALLOW_UNFREE=1` + `--impure` for flakes | That CLI evaluation only | `nixos-rebuild`; flake outputs that pin their own `import nixpkgs` |

On NixOS, `NIXPKGS_CONFIG` points at `/etc/nix/nixpkgs-config.nix` for **user-level** commands (`nix-env`, legacy `nix-shell`), not for `nixos-rebuild`. System policy belongs in `nixpkgs.config` modules. See [nix.conf](../../05-cli-and-tooling/config/nix-conf.md) for Nix daemon/client settings (orthogonal to nixpkgs license policy).

**Home Manager is a separate evaluation.** When HM runs as a NixOS submodule, it imports nixpkgs again for the user closure unless `home-manager.useGlobalPkgs = true` reuses the system `pkgs`. Setting `allowUnfree` only in HM allows unfree packages in `home.packages` but **not** in a `systemd` service that pulls from the system `pkgs`. See [Home Manager](../../13-implementations/module-ecosystems/home-manager.md).

### Flake NixOS: module config vs pre-built `pkgs`

Two common patterns—pick one per host; mixing carelessly ignores module `nixpkgs.config`.

**Pattern A — `nixpkgs.config` in modules (usual).** Policy lives beside the rest of the system config; overlays and `nixpkgs.config` merge normally:

```nix
nixosConfigurations.host = nixpkgs.lib.nixosSystem {
  modules = [
    { nixpkgs.config.allowUnfree = true; }
    ./configuration.nix
  ];
};
```

Or inside [configuration.nix](../../09-nixos/configuration/configuration-nix.md):

```nix
{ nixpkgs.config.allowUnfreePredicate = pkg:
    lib.strings.hasPrefix "steam" (lib.getName pkg);
}
```

**Pattern B — pre-import `pkgs` with baked-in `config`.** The flake imports nixpkgs once and passes the result to `nixosSystem`:

```nix
let
  pkgs = import inputs.nixpkgs {
    system = "x86_64-linux";
    config.allowUnfree = true;
  };
in
nixosConfigurations.host = nixpkgs.lib.nixosSystem {
  inherit pkgs;
  modules = [ ./configuration.nix ];
};
```

When `pkgs` is passed this way, **`nixpkgs.config` and `nixpkgs.overlays` in modules are ignored** (nixpkgs warns if you also set `specialArgs.pkgs`). To reuse a pre-configured `pkgs` while still merging module options, import `nixosModules.readOnlyPkgs` and set `nixpkgs.pkgs`. See [nixosConfigurations](../../07-flakes/workflows/nixos-configurations.md).

Flake **dev shells** always use Pattern B at the flake level: pass `config` when you call `import nixpkgs` inside `outputs` (see [packages, apps, and devShells](../../07-flakes/workflows/packages-apps-devShells.md)).

### Related but separate: `permittedInsecurePackages`

`config.permittedInsecurePackages` lists **package names with version** (e.g. `"hello-1.2.3"`) that are allowed despite `meta.knownVulnerabilities` being non-empty. That is an **insecure-build exception**, not a license exception. A package can be free yet blocked for insecurity, or unfree yet not insecure—configure both independently.

| Symptom | Likely gate | Fix |
|---------|-------------|-----|
| `has an unfree license ('…')` | Unfree policy | `allowUnfree`, `allowUnfreePredicate`, or `allowUnfreePackages` |
| `is marked as insecure` / `knownVulnerabilities` | Insecure policy | `permittedInsecurePackages` or `allowInsecurePredicate` |
| `has a blocklisted license` | `blocklistedLicenses` | Remove blocklist entry or change package; not fixable with `allowUnfree` alone |

`permittedInsecurePackages` is only consulted when `allowInsecurePredicate` is **not** set. Setting a predicate replaces the name list path entirely.

### Android SDK: license acceptance ≠ `allowUnfree`

Android tooling needs **two** gates: unfree packages (`config.allowUnfree` or predicate) **and** explicit SDK license acceptance (`config.android_sdk.accept_license = true` or `NIXPKGS_ACCEPT_ANDROID_SDK_LICENSE=1`). Allowing unfree does not imply you accepted Google’s SDK terms. See [Android and mobile](../../11-development/android-and-mobile.md).

### Failure modes

**Unfree only on Home Manager, service needs it on system.** Symptom: HM build succeeds but `nixos-rebuild` fails when enabling a system service (Steam system integration, CUPS with `hplipWithPlugin`, `hardware.enableAllFirmware`, NVIDIA/CUDA system modules). The error references an attribute under the **system** evaluation. Fix: add `nixpkgs.config.allowUnfree` (or a targeted predicate / `allowUnfreePackages`) to **NixOS** modules, not only HM—or enable `home-manager.useGlobalPkgs` and ensure the shared system `pkgs` already permits the package.

**Reading evaluation errors.** Unfree failures cite the **attribute path** (e.g. `environment.systemPackages`, a service’s `package` option) and the **license short name** in parentheses. The remediation block in the error is authoritative: (a) `NIXPKGS_ALLOW_UNFREE=1` for one-shot CLI (with `--impure` on `nix develop` / `nix shell` / `nix run` with flakes), (b) `nixpkgs.config.allowUnfree` for `nixos-rebuild`, (c) `~/.config/nixpkgs/config.nix` for channel/`nix-env` style commands. A suggested `allowUnfreePredicate` snippet with the blocked `lib.getName` is often included—prefer that over global `allowUnfree` when the message names a single package.

**`permittedInsecurePackages` confusion.** Users paste an unfree package name into `permittedInsecurePackages` when the error was about **license**, not CVEs—or vice versa. Match the error reason string (`unfree` vs `insecure`). Insecure entries need the **full** `name-version` string as shown in the error, not just `pname`.

**Flake purity.** `NIXPKGS_ALLOW_UNFREE=1` without `--impure` has no effect on flake evaluations because environment variables are not visible in pure eval. Either pass `--impure`, or bake `config` into the flake’s `import nixpkgs`.

**`nixpkgs.config` on NixOS does not fix `nix shell`.** After setting `allowUnfree` in `configuration.nix`, `nix shell -p <unfree>` can still fail. Use `~/.config/nixpkgs/config.nix` or env var + `--impure` for ad-hoc CLI, or a flake dev shell with explicit `config`.

### Common unfree needs

Many “batteries included” features pull unfree packages once enabled:

- **GPU / ML** — NVIDIA CUDA, cuDNN, some ROCm-adjacent blobs ([CUDA, ROCm, and ML](../../11-development/cuda-rocm-ml.md)).
- **Gaming** — Steam and Proton wrappers ([Gaming, Steam, and Proton](../../09-nixos/desktop/gaming-steam-proton.md)).
- **Firmware** — `hardware.enableAllFirmware` beyond redistributable sets ([firmware and microcode](../../09-nixos/configuration/firmware-and-microcode.md)).
- **Mobile SDKs** — Android SDK components and license acceptance ([Android and mobile](../../11-development/android-and-mobile.md)).
- **Scientific stacks** — Intel MKL and similar proprietary math libraries.

Enable only what you need; use predicates scoped to those names when possible.

### Boundaries

- **License policy ≠ legal compliance.** `allowUnfree` only disables nixpkgs’ evaluation guard. You remain responsible for upstream license terms, redistribution, and organizational policy.
- **License policy ≠ insecure policy.** Use `permittedInsecurePackages` / `allowInsecurePredicate` for CVE-flagged packages; do not conflate with unfree settings.
- **License policy ≠ `android_sdk.accept_license`.** SDK builds need both unfree permission and explicit license acceptance.
- **License policy ≠ `requireFile` / vendor blobs.** Some derivations need you to supply a binary or run `--impure` to read paths outside the flake; `allowUnfree` alone does not satisfy those requirements.
- **System config ≠ user CLI config.** `nixpkgs.config` in NixOS/HM/flakes does not configure impure `nixpkgs#` invocations; use `~/.config/nixpkgs/config.nix` or env vars.
- **Channel vs flake.** Flakes ignore `~/.config/nixpkgs/config.nix` when you pass an explicit `config` to `import nixpkgs`; implicit config applies only when `config` is omitted from the import.

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

NixOS: additive per-module allowlist (preferred for service modules):

```nix
{ nixpkgs.config.allowUnfreePackages = [ "hplipWithPlugin" ]; }
```

Flake `pkgs` with a narrow predicate:

```nix
pkgs = import nixpkgs {
  inherit system;
  config.allowUnfreePredicate = pkg:
    builtins.elem (lib.getName pkg) [ "cudatoolkit" "cudnn" ];
};
```

For CUDA, prefer `pkgs._cuda.lib.allowUnfreeCudaPredicate` once `pkgs` exists (see [CUDA, ROCm, and ML](../../11-development/cuda-rocm-ml.md)).

User `~/.config/nixpkgs/config.nix` for impure/channel commands:

```nix
{ allowUnfree = true; }
```

One-shot flake CLI (needs `--impure`):

```bash
NIXPKGS_ALLOW_UNFREE=1 nix shell --impure nixpkgs#vscode
```

Dev shell (`shell.nix` or flake fragment):

```nix
{ pkgs ? import <nixpkgs> { config.allowUnfree = true; } }:
pkgs.mkShell { buildInputs = [ pkgs.jdk ]; }
```

## References

- [Nixpkgs manual — Configuring Nixpkgs](https://nixos.org/manual/nixpkgs/stable/#sec-configuring-nixpkgs) — `config`, `allowUnfree`, `allowUnfreePredicate`, `permittedInsecurePackages`
- [Nixpkgs manual — Installing unfree packages](https://nixos.org/manual/nixpkgs/stable/#sec-allow-unfree) — predicates, `NIXPKGS_ALLOW_UNFREE`, user `config.nix`
- [Nixpkgs manual — License metadata](https://nixos.org/manual/nixpkgs/stable/#sec-meta-attributes) — `unfree` vs `unfreeRedistributable`

## See also

- [Package sets](package-sets.md) — how `pkgs` is built from nixpkgs
- [mkDerivation](mkDerivation.md) — `meta.license` on derivations
- [configuration.nix](../../09-nixos/configuration/configuration-nix.md) — NixOS host policy
- [nix.conf](../../05-cli-and-tooling/config/nix-conf.md) — Nix client/daemon settings (separate from nixpkgs `config`)
- [CUDA, ROCm, and ML](../../11-development/cuda-rocm-ml.md)
- [Gaming, Steam, and Proton](../../09-nixos/desktop/gaming-steam-proton.md)
- [Home Manager](../../13-implementations/module-ecosystems/home-manager.md)
- [packages, apps, and devShells](../../07-flakes/workflows/packages-apps-devShells.md)
- [nixosConfigurations](../../07-flakes/workflows/nixos-configurations.md) — flake `nixosSystem` wiring
