---
status: complete
---

# Installers and Nix Variants

## Overview

This page compares ways to install the **Nix package manager** (and closely related implementations) on Linux and macOS. It is not about the NixOS live ISO or Calamares — that path is [GUIs and installers](guis-and-installers.md). For running Nix beside apt/dnf/pacman without becoming NixOS, see [Nix on other distros](../../10-home-and-user/nix-on-other-distros.md).

Common choices: the official [CppNix](../nix-evaluator/cpp-nix.md) installer from [nixos.org/download](https://nixos.org/download/), [Lix](../nix-evaluator/lix.md) via its own install docs, and Determinate Systems’ Determinate Nix / installer (vendor docs at [docs.determinate.systems](https://docs.determinate.systems/)). Treat them as alternative distributions of a Nix-compatible stack, not interchangeable product rankings.

## Details

### Official Nix (CppNix)

The NixOS project documents install commands on [Download](https://nixos.org/download/) (and [nix.dev — Install Nix](https://nix.dev/install-nix)). On Linux, the recommended path is **multi-user** with a daemon (`--daemon`): better build isolation, shared builds, and a systemd unit. Single-user (`--no-daemon`) is for hosts without a suitable daemon setup. macOS and WSL2 variants are listed on the same page—use those instructions rather than inventing flags.

What you get is stock [CppNix](../nix-evaluator/cpp-nix.md): experimental features such as flakes are **opt-in** unless you enable them in [`nix.conf`](../../05-cli-and-tooling/config/nix-conf.md) (or equivalent NixOS settings). Exact script URLs and platform notes change; prefer the download page for the current commands.

### Lix

[Lix](../nix-evaluator/lix.md) is a community fork of the C++ lineage (last shared CppNix release: 2.18). Fresh installs on ordinary Linux/macOS use the [Lix install guide](https://lix.systems/install/) (installer at `install.lix.systems`). On NixOS or nix-darwin, Lix’s docs point at configuration overlays rather than only the curl installer.

Compatibility with existing Nix expressions is a stated project goal; CLI flags, experimental features, and release cadence still differ from CppNix—verify against Lix docs for your version. Governance and fork context: [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md).

### Determinate Nix

Determinate Systems ships **Determinate Nix**, documented as a downstream distribution of [NixOS/nix](https://github.com/NixOS/nix), plus related tooling (e.g. Determinate Nixd). Entry point: [docs.determinate.systems](https://docs.determinate.systems/). Linux migration docs show a curl-based installer (`install.determinate.systems`); macOS and NixOS have separate vendor paths (package / flake module)—follow those guides.

Vendor docs state that the installer writes `/etc/nix/nix.conf` with carefully chosen values, and that extra settings belong in `/etc/nix/nix.custom.conf` rather than editing the generated file. Do **not** assume stock CppNix experimental-feature defaults; inspect effective config (`nix config show` or equivalent) and the current Determinate docs. Extra product features (lazy trees, parallel eval, etc.) are Determinate-specific unless also present upstream—see their feature pages, not this wiki’s CppNix baseline.

### Choosing among them

| Concern | What to check |
|---------|----------------|
| nixpkgs / NixOS compatibility | Tutorials and NixOS channels assume CppNix unless you deliberately switch; Lix aims at expression compatibility; Determinate positions as upstream-compatible with vendor extras |
| Experimental / flake defaults | Stock CppNix: opt-in via [`nix.conf`](../../05-cli-and-tooling/config/nix-conf.md); other installers may ship different defaults—confirm after install |
| Support / governance | Foundation/community process vs Lix governance vs commercial vendor support—see [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md) |
| Uninstall / upgrade | Stick to **one** installer’s documented upgrade and uninstall path; mixing installers on one host is a common failure mode |

Evaluator deep dives: [CppNix](../nix-evaluator/cpp-nix.md), [Lix](../nix-evaluator/lix.md), [Nix evaluators](../nix-evaluator/README.md).

### On NixOS

NixOS usually ships its Nix from nixpkgs (e.g. via `nix.package` / module settings)—declarative, channel-pinned with the system. Installing a third-party Nix with a foreign curl installer on a running NixOS host is a **special case**: you can fight the module system, diverge from rebuilds, and confuse trust/substituter policy. Prefer the implementation’s documented NixOS module path (Lix and Determinate both document configuration-based installs) over a one-off daemon install.

Daemon privilege and cache trust still apply: [`nix.conf`](../../05-cli-and-tooling/config/nix-conf.md), [Trusted users](../../14-security-and-trust/trusted-users.md), [Trusted users and substituters](../../05-cli-and-tooling/config/trusted-users-and-substituters.md).

## Examples

Point at official commands; do not re-run on a host that already has Nix.

**Official multi-user (Linux)** — from [nixos.org/download](https://nixos.org/download/):

```bash
curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install | sh -s -- --daemon
```

**Lix (Linux/macOS, no existing daemon)** — from [Installing Lix](https://lix.systems/install/):

```bash
curl -sSf -L https://install.lix.systems/lix | sh -s -- install
```

**Determinate Nix (Linux / WSL migration path)** — from [Migrating from upstream Nix](https://docs.determinate.systems/guides/migrating-from-upstream-nix/):

```bash
curl -fsSL https://install.determinate.systems/nix | sh -s -- install
```

After any install, confirm which binary you have:

```bash
nix --version
which nix
```

Expect wording that identifies CppNix/Nix, Lix, or Determinate Nix depending on the distribution.

## References

- [NixOS Download — Nix package manager](https://nixos.org/download/) — official install commands (Linux, macOS, WSL, Docker)
- [nix.dev — Install Nix](https://nix.dev/install-nix)
- [Lix — Installing Lix](https://lix.systems/install/)
- [Lix](https://lix.systems/) — project site
- [Determinate docs](https://docs.determinate.systems/) — Determinate Nix and related tooling
- [Determinate Nix](https://docs.determinate.systems/determinate-nix/) — distribution overview and `nix.conf` / `nix.custom.conf`
- [Migrating from upstream Nix](https://docs.determinate.systems/guides/migrating-from-upstream-nix/) — Linux installer command and migration notes
- [Advanced installation (NixOS)](https://docs.determinate.systems/guides/advanced-installation/) — Determinate on NixOS via flake module

## See also

- [GUIs and installers](guis-and-installers.md) — NixOS graphical ISO / Calamares (not package-manager install)
- [Nix on other distros](../../10-home-and-user/nix-on-other-distros.md) — Nix beside a foreign OS
- [CppNix](../nix-evaluator/cpp-nix.md) — reference C++ implementation
- [Lix](../nix-evaluator/lix.md) — C++-lineage fork
- [Nix evaluators](../nix-evaluator/README.md) — evaluator index
- [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md)
- [`nix.conf`](../../05-cli-and-tooling/config/nix-conf.md)
- [Trusted users](../../14-security-and-trust/trusted-users.md)
