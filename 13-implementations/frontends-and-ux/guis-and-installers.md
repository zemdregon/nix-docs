---
status: complete
---

# GUIs and Installers

## Overview

NixOS ships one official **graphical** first-install path: a Calamares-based installer on the **graphical** live ISOs from [nixos.org/download](https://nixos.org/download/) (stable channel **nixos-26.05** as of 2026-07). That UI walks desktop users through language, users, desktop choice, partitioning, and install. After the system is installed, day-to-day configuration still goes through the NixOS module system and CLI rebuild frontends—primarily [`nixos-rebuild`](nixos-rebuild.md), or wrappers such as [`nh`](nh.md)—not through that installer.

This page situates those surfaces. Step-by-step installer screens live under [Graphical installer](../../09-nixos/installation/graphical-installer.md). Do not assume a stock desktop “NixOS settings GUI” for ongoing system changes; treat third-party GUIs as optional community tooling and verify them independently.

## Details

### Official graphical installer (Calamares)

Graphical installation images include a live desktop and the graphical installer. Upstream NixOS packages that installer as **Calamares** with NixOS-specific extensions (`calamares-nixos`, `calamares-nixos-extensions` in nixpkgs); the NixOS manual documents the flow as “Graphical Installation” without requiring you to know Calamares by name.

- **Recommended for** desktop users who want a guided install.
- **Not on** minimal ISOs—those boot to a console; use a manual install path instead.
- **Does not replace** later rebuilds: Calamares generates and builds a NixOS configuration into the target disk; afterward you edit config and rebuild with CLI tools.

Boot media, Secure Boot / UEFI notes, and screen-by-screen detail: [Graphical installer](../../09-nixos/installation/graphical-installer.md). Canonical procedure: [NixOS manual — Graphical Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation-graphical).

### CLI rebuild frontends (post-install)

| Surface | Role |
|---------|------|
| [`nixos-rebuild`](nixos-rebuild.md) | Classic, documented way to build and activate a NixOS configuration (`switch`, `boot`, `test`, …) |
| [`nh`](nh.md) | Community-oriented rebuild UX (nicer output / helpers); still a CLI around the same activation model |

Both operate on declarative config (e.g. `/etc/nixos` or a flake). Neither is a graphical installer substitute.

### Optional community GUIs

The broader Nix ecosystem has occasional community frontends (package browsers, rebuild helpers with a GUI, etc.). Names, maturity, and packaging change often. This wiki does not endorse specific products here: if you use one, confirm it matches your Nix/NixOS version and that it ultimately drives the same store/rebuild model as the CLI tools above.

## Examples

**First install (graphical path):**

1. Download a **Graphical** ISO from [nixos.org/download](https://nixos.org/download/) (not Minimal).
2. Write it to USB, boot (prefer UEFI; Secure Boot often needs to be off).
3. Complete the Calamares / graphical installer wizard (see [Graphical installer](../../09-nixos/installation/graphical-installer.md)).
4. Reboot into the installed system.

**Ongoing changes (CLI, not the installer):**

```bash
# Classic
sudo nixos-rebuild switch

# Or, if you use nh (once installed / configured for your setup)
nh os switch
```

Exact flags and flake vs channels differ by setup—see [`nixos-rebuild`](nixos-rebuild.md) and [`nh`](nh.md).

## References

- [NixOS manual — Graphical Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation-graphical) (stable / 26.05 as of 2026-07)
- [NixOS download page](https://nixos.org/download/) — graphical vs minimal ISO images
- [nixpkgs — `installation-cd-graphical-calamares.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/installer/cd-dvd/installation-cd-graphical-calamares.nix) — Calamares on graphical install media

## See also

- [Graphical installer](../../09-nixos/installation/graphical-installer.md) — installer screens and boot media
- [Installers and Nix variants](installers-and-nix-variants.md) — package-manager installs (official / Lix / Determinate), not the ISO
- [nixos-rebuild](nixos-rebuild.md) — classic rebuild frontend
- [nh](nh.md) — modern rebuild UX wrapper
