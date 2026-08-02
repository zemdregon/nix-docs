---
status: complete
last-checked: 2026-08
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

[Lix](../nix-evaluator/lix.md) is a community fork of the C++ lineage (last shared CppNix release: 2.18). Fresh installs on ordinary Linux/macOS use the [Lix install guide](https://lix.systems/install/) (installer at `install.lix.systems`) into a **separate install path** from CppNix—do not assume the same `/nix` layout or uninstall script.

On **NixOS** or **nix-darwin**, Lix’s docs point at **module overlays** (nixpkgs / nix-darwin options) rather than the curl installer. Running `install.lix.systems` on a declarative host bypasses the module system: `nixos-rebuild` can revert or fight the foreign daemon, `which nix` may still resolve to the channel-pinned binary, and you inherit two competing upgrade paths. Prefer the documented overlay/module path so the chosen implementation is pinned with the system config.

Compatibility with existing Nix expressions is a stated project goal; CLI flags, experimental features, and release cadence still differ from CppNix—verify against Lix docs for your version. Governance and fork context: [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md).

### Determinate Nix

Determinate Systems ships **Determinate Nix**, documented as a downstream distribution of [NixOS/nix](https://github.com/NixOS/nix), plus related tooling (e.g. Determinate Nixd). Entry point: [docs.determinate.systems](https://docs.determinate.systems/). Linux migration docs show a curl-based installer (`install.determinate.systems`); macOS and NixOS have separate vendor paths (package / flake module)—follow those guides.

The Determinate installer generates **`/etc/nix/nix.conf`** with fixed baseline settings (including experimental-feature defaults that may differ from stock CppNix). **Do not edit that file by hand**—upgrades can overwrite it. Put local overrides in **`/etc/nix/nix.custom.conf`**; the stack merges custom settings on top of the generated file.

After install or migration, confirm the **effective** config rather than guessing from memory:

```bash
nix config show
```

Look for keys such as `experimental-features`, `substituters`, and `trusted-users`. If you added settings only in `nix.custom.conf`, they should appear here; if you edited `nix.conf` directly and an upgrade “lost” your changes, that is expected. Do **not** assume stock CppNix flake defaults—Determinate may enable features CppNix leaves opt-in via [`nix.conf`](../../05-cli-and-tooling/config/nix-conf.md). Extra product features (lazy trees, parallel eval, etc.) are Determinate-specific unless also present upstream—see their docs, not this wiki’s CppNix baseline.

### Choosing among them

| Concern | What to check |
|---------|----------------|
| nixpkgs / NixOS compatibility | Tutorials and NixOS channels assume CppNix unless you deliberately switch; Lix aims at expression compatibility; Determinate positions as upstream-compatible with vendor extras |
| Experimental / flake defaults | Stock CppNix: opt-in via [`nix.conf`](../../05-cli-and-tooling/config/nix-conf.md); other installers may ship different defaults—confirm after install |
| Support / governance | Foundation/community process vs Lix governance vs commercial vendor support—see [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md) |
| Uninstall / upgrade | Follow **one** distribution’s documented uninstall before switching; see [Migration, uninstall, and failure modes](#migration-uninstall-and-failure-modes) |

Evaluator deep dives: [CppNix](../nix-evaluator/cpp-nix.md), [Lix](../nix-evaluator/lix.md), [Nix evaluators](../nix-evaluator/README.md).

### Migration, uninstall, and failure modes

Switching implementations is not “install the new script on top.” Each distribution documents its own uninstall or migration sequence—run **that** before another installer touches `/nix`, launchd/systemd units, or `/etc/nix`. Partial cleanup leaves the worst failures below.

| Failure mode | Typical symptoms | Prevention / recovery |
|--------------|------------------|------------------------|
| **Mixing installers** | Two `nix` binaries in `PATH`, conflicting `/etc/profile.d` hooks, half-removed daemon, builds fail with obscure store errors | Uninstall per the **current** distribution’s docs, then install the target; never stack curl installers without cleanup |
| **Wrong uninstall path** | Leftover `nix-daemon` / `nixbld` users, stale `/etc/nix` or LaunchDaemon plist, new install refuses to proceed | Use the uninstall script/docs for the implementation **actually installed** (CppNix, Lix, and Determinate each differ)—not a generic “remove /nix” blog post |
| **Duplicate daemon** | Two daemons or units fighting for the socket; `nix build` hangs or permission errors | Ensure only one multi-user install owns the daemon; stop/disable the old unit before enabling the new one |
| **Wrong store ownership** | `error: opening lock file … Permission denied`, builds as root while store owned by another profile | Multi-user installs expect `root` + `nixbld` (or vendor-equivalent) ownership; foreign single-user remnants under `/nix/var` need the documented reset, not `chown` guesses |

On **NixOS**, foreign curl installers are a common trigger for the rows above: the live system already has nixpkgs-managed Nix, modules, and store layout. Switch via **NixOS / nix-darwin modules or overlays** (Lix overlay, Determinate flake module, or `nix.package`) so `nixos-rebuild` remains the single source of truth—see [On NixOS](#on-nixos).

### On NixOS

NixOS usually ships its Nix from nixpkgs (e.g. via `nix.package` / module settings)—declarative, channel-pinned with the system. Installing a third-party Nix with a foreign curl installer on a running NixOS host is a **special case** and a frequent source of the failure modes above: the module system and the curl script both manage daemons, `nix.conf`, and upgrade channels; `nixos-rebuild switch` can overwrite foreign changes or leave two stacks half-active; trust and substituter policy diverge from what modules declare.

**Preferred path:** use the implementation’s documented NixOS integration—Lix via nixpkgs overlay options, Determinate via its flake module ([Advanced installation (NixOS)](https://docs.determinate.systems/guides/advanced-installation/)), or stock CppNix via `nix.package` / channel pin. Reserve curl-based installers for non-NixOS Linux/macOS hosts unless upstream docs explicitly cover NixOS migration edge cases.

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

After any install **or migration**, verify the **active stack** before relying on tutorials or flake defaults:

```bash
nix --version
which nix
type -a nix    # optional: list all nix binaries on PATH
```

**`nix --version`** should name the distribution you intended (upstream Nix/CppNix, Lix, or Determinate Nix) and a plausible version string. **`which nix`** should point at that distribution’s profile hook (e.g. `/nix/var/nix/profiles/default/bin/nix` for a typical multi-user CppNix layout—not a stale single-user path or a second install’s prefix). If output disagrees with what you just installed, stop: you likely have PATH ordering issues or a leftover install from the [failure modes](#migration-uninstall-and-failure-modes) table.

On multi-user hosts, also confirm the daemon matches the CLI you are exercising (e.g. `systemctl status nix-daemon` on Linux) before debugging build failures as “Nix bugs.”

For Determinate migrations, pair version checks with **`nix config show`** so effective `experimental-features` and substituters match policy—not only the binary brand.

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
