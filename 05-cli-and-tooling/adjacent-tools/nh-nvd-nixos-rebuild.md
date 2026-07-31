---
status: complete
---

# nh / nvd / nixos-rebuild

## Overview

Applying a NixOS (or Home Manager / nix-darwin) config means building a new system derivation and running the platform’s activation path. Three tools show up together in day-to-day workflows:

- **`nixos-rebuild`** — the official NixOS entry point for `switch` / `boot` / `test` / `build` (and related actions).
- **`nh`** (Yet Another Nix Helper) — a community CLI that *reimplements* NixOS / Home Manager / Darwin rebuild-style workflows with clearer output, build-tree visualization, and pre-activation diffs. Upstream states it is **not** a `nixos-rebuild` wrapper.
- **`nvd`** (Nix version diff) — a focused tool that summarizes package/version differences between two store paths or generations.

`nh` and `nvd` improve review and ergonomics. Activation itself still goes through the same switch-to-configuration path once you choose to switch; they do not invent a separate activation model.

**Last checked:** 2026-07-31 — aligned with [nh](../../13-implementations/frontends-and-ux/nh.md) / [nixos-rebuild](../../13-implementations/frontends-and-ux/nixos-rebuild.md) frontends; confirm flags with `--help` / man pages.

## Details

### `nixos-rebuild`

Official command for changing configuration (see [rebuild actions](../../09-nixos/operations/rebuild-switch-boot-test.md)):

| Action | Effect |
|--------|--------|
| `switch` | Build, set boot default, activate now |
| `test` | Build + activate now; do **not** change boot default |
| `boot` | Build + set boot default; activate on next reboot |
| `build` | Build only (leaves a `result` symlink; no activate / boot menu) |

Root (or elevating appropriately) is required for actions that activate or change the boot default. With flakes, pass a flake attribute, e.g. `nixos-rebuild switch --flake .#host`. Rollback and generation selection are covered under [rollbacks](../../09-nixos/operations/rollbacks.md).

On NixOS **26.05** (current stable), the on-PATH `nixos-rebuild` is the Python **`nixos-rebuild-ng`** rewrite; the classic Bash implementation is gone. Frontend notes: [nixos-rebuild (implementations)](../../13-implementations/frontends-and-ux/nixos-rebuild.md).

### `nh`

Packaged in nixpkgs as `nh` ([nix-community/nh](https://github.com/nix-community/nh)). Subcommands include **`nh os`**, **`nh home`**, **`nh darwin`**, plus **`nh search`** and **`nh clean`**.

Per the upstream README (default branch `master`, checked 2026-07-31):

- `nh os` reimplements `nixos-rebuild-ng` in Rust (not a shell wrapper around `nixos-rebuild`).
- Additions called out upstream: build-tree display via **nix-output-monitor** (nom), pretty diffs via **dix**, and confirmation before activation.
- Feature parity with stock `nixos-rebuild` is incomplete; see upstream [issue #358](https://github.com/nix-community/nh/issues/358).

Deeper UX placement: [nh (implementations)](../../13-implementations/frontends-and-ux/nh.md).

Typical flake mapping from the README:

| Without nh | With nh |
|------------|---------|
| `nixos-rebuild switch --flake .#myHost` | `nh os switch . -H myHost` |
| `darwin-rebuild switch --flake .#myHost` | `nh darwin switch . -H myHost` |
| `home-manager switch --flake .#myHost` | `nh home switch . -c myHome` |

If `NH_FLAKE` / `NH_OS_FLAKE` (or the NixOS module’s `programs.nh.flake`) is set, the flake path can be omitted; hostname (`-H`) may also be omitted when NH can autodiscover it. Prefer `nh os switch --help` / `man 1 nh` for the current flag set—do not rely on memorized long options across releases.

### `nvd`

Attribute `nvd` in nixpkgs. Diffs package versions in the closures of two Nix store paths and prints a compact summary (added / removed / version changes), with special highlighting for packages that appear in `environment.systemPackages`. Useful for comparing system generations or a newly built `result` against `/run/current-system`.

Canonical project page: [khumba.net/projects/nvd](https://khumba.net/projects/nvd). Source: [git.sr.ht/~khumba/nvd](https://git.sr.ht/~khumba/nvd) (moved to Sourcehut; older GitHub mirrors are not current upstream).

`nvd` is independent of `nh`. nh’s built-in pre-switch diffs use **dix**; many people still use `nvd` with plain `nixos-rebuild build` for a package-version summary.

### How they fit together

A common pattern is build → diff → activate: `nixos-rebuild build` then `nvd diff /run/current-system result` before `switch` (pattern from the nvd docs). With nh, build-tree / dix review and confirmation are integrated into `nh os switch` (and peers). Generations under `/nix/var/nix/profiles/` remain the durable history for [rollbacks](../../09-nixos/operations/rollbacks.md).

## Examples

**Official rebuild** (from the [NixOS manual](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)):

```bash
# as root
nixos-rebuild switch
nixos-rebuild test
nixos-rebuild boot
nixos-rebuild build
```

**Flake host:**

```bash
sudo nixos-rebuild switch --flake .#myhost
```

**Diff two generations with nvd** (form shown on the nvd project page):

```bash
nvd diff /nix/var/nix/profiles/system-{14,15}-link
```

**Build then review before switching** (recommended pattern from nvd):

```bash
nixos-rebuild build && nvd diff /run/current-system result
# then, if the diff looks right:
sudo nixos-rebuild switch
```

**nh-shaped NixOS switch** (examples from the [nh README](https://github.com/nix-community/nh); confirm with `nh os switch --help`):

```bash
nh os switch . -H myHost
# with NH_FLAKE / NH_OS_FLAKE (or programs.nh.flake) set:
nh os switch
```

## References

- [NixOS manual — Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config) — `nixos-rebuild` switch/boot/test/build
- [nix-community/nh](https://github.com/nix-community/nh) — Yet Another Nix Helper (README: not a nixos-rebuild wrapper; `nh os` / dix / nom)
- [nh issue #358](https://github.com/nix-community/nh/issues/358) — `nh os` vs `nixos-rebuild` feature parity roadmap
- [nvd — Nix/NixOS package version diff](https://khumba.net/projects/nvd) — project page; nixpkgs attribute `nvd`
- [nvd source (Sourcehut)](https://git.sr.ht/~khumba/nvd) — upstream repository

## See also

- [nixos-rebuild actions](../../09-nixos/operations/rebuild-switch-boot-test.md) — switch / boot / test / build semantics
- [Rollbacks](../../09-nixos/operations/rollbacks.md) — generations and undoing a bad switch
- [nh (implementations)](../../13-implementations/frontends-and-ux/nh.md) — deeper nh notes
- [nixos-rebuild (implementations)](../../13-implementations/frontends-and-ux/nixos-rebuild.md) — frontend-oriented rebuild notes (`nixos-rebuild-ng` on 26.05)
