---
status: complete
---

# Graphical Installer

## Overview

The NixOS **graphical installer** is the recommended path for desktop users. Boot a **graphical** ISO or USB image—GNOME or Plasma variants from [nixos.org/download](https://nixos.org/download/)—and the live desktop starts a Calamares-based wizard that walks through language, location, keyboard, users, desktop choice, unfree software, partitioning, then install. **Minimal** images boot to a CLI instead; use [Manual install](manual-install.md).

The flow is local and desktop-oriented: it generates a default `configuration.nix` and installs to disk. It does not accept a pre-written flake or custom initial config. Remote, automated, or heavily custom layouts use other paths (see **When not to use graphical** below).

## Details

### Boot media and firmware

Download a graphical installation image, write it to USB (or burn a CD), and boot from that drive. Prefer **UEFI** when the machine supports both BIOS and UEFI. The manual notes you will often need to **disable Secure Boot** in firmware to boot the installer: the live ISO’s EFI bootloader is not signed for your platform’s keys, and there is no signed shim on the media. Exact firmware menus vary (Boot, Security, or Advanced). **Post-install Secure Boot**—enabling enforcement with signed boot artifacts—is a separate, advanced topic; see [Secure Boot and Lanzaboote](../configuration/secure-boot-and-lanzaboote.md).

Shortly after boot, leave the default menu entry. The graphical image brings up its desktop and the installer (this can take a while). If you landed on a shell only, you used a minimal image—switch to [Manual install](manual-install.md). For a command line during install, open Terminal (GNOME) or Konsole (Plasma) from the application menu; you are logged in as `nixos` with passwordless `sudo`.

### Networking on the live image

The installer downloads packages from binary caches, so networking must work before install completes. Graphical ISO profiles enable **NetworkManager**; you can configure Wi‑Fi from the desktop settings or with `nmtui` (also works from a non-graphical session). Check interfaces with `ip a`; if DHCP is unavailable, configure manually with `ip` or stop NetworkManager (`systemctl stop NetworkManager`) for static setup. The generated config does **not** automatically enable NetworkManager or wireless on first boot—you declare a backend afterward; see [Networking](../configuration/networking.md).

### Installer screens (in order)

1. **Welcome** — language for the installer and the installed system. Tip: leave **American English** if you want error text that is easier to search or report.
2. **Location / timezone** — set timezone (you can click the map). The installer may guess location from your public IP.
3. **Keyboard** — layout (and model if needed); pick the language you type in most comfortably.
4. **Users** — display name, login name, and password; optional automatic desktop login.
5. **Desktop environment** — choose a DE, or **No desktop** for a custom / window-manager setup. If undecided, GNOME or Plasma are both well-tested defaults with different designs.
6. **Unfree software** — option to allow unfree packages in the installed system.
7. **Partitioning** — easiest path is **Erase disk** (deletes all data on the selected disk). Also select **Swap (with Hibernation)** in the dropdown. Optional whole-disk **LUKS** encryption. Top-left shows whether the installer booted as **BIOS** or **UEFI**—if the machine is UEFI but the installer shows BIOS, reboot with the UEFI boot option. Confirm the **correct disk**; formatting destroys existing data. Dual-boot, multi-partition, ZFS/Btrfs, or other non-whole-disk layouts are outside this wizard—use [Manual install](manual-install.md) and [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md).
8. **Summary** — review choices, then **Install**.

### When not to use graphical

| Situation | Prefer |
|-----------|--------|
| Minimal ISO, custom disk layout, dual-boot with existing OS | [Manual install](manual-install.md), [Dual boot and VMs](dual-boot-and-vms.md) |
| Install from your flake over SSH to a remote machine | [nixos-anywhere](nixos-anywhere.md) |
| PXE/iPXE or rack provisioning | [Netboot and PXE](netboot-and-pxe.md) |
| Inject a specific initial `configuration.nix` or flake before first boot | Manual install, nixos-anywhere, or custom install media (patterns in nixpkgs installer modules—not the stock graphical wizard) |

The graphical path optimizes for “erase disk, pick a DE, go.” It is not a general substitute for declarative remote install tooling.

### Duration, generated config, and finish

Installation typically takes about **15 minutes** (varies with desktop choice, network, and disk speed). Calamares runs `nixos-generate-config` and builds the system into the target; generated hardware settings land in [hardware-configuration.nix](../configuration/hardware-configuration.md). Later changes go through [rebuild / switch / boot / test](../operations/rebuild-switch-boot-test.md)—the installer does not replace ongoing configuration.

When done, remove the USB drive and reboot into the new system.

### After first boot

**Firmware and Wi‑Fi.** Many laptops need redistributable firmware for Wi‑Fi or audio after install. The graphical “allow unfree” step covers nixpkgs policy, not necessarily `hardware.enableRedistributableFirmware`; enable it if wireless or sound is missing—see [Firmware and microcode](../configuration/firmware-and-microcode.md).

**Desktop tuning.** DE-specific services, Wayland vs X11, audio, and fonts are configured in [configuration.nix](../configuration/configuration-nix.md) after install. Starting points: [Desktop](../desktop/README.md), [Wayland and compositors](../desktop/wayland-and-compositors.md).

**Problems.** Boot failures, missing network, or rollback needs: [Troubleshooting](../operations/troubleshooting.md).

## Examples

Typical desktop path after booting a graphical ISO:

1. Boot from USB; disable Secure Boot in firmware if the media will not load under UEFI.
2. Connect Wi‑Fi (desktop settings or `nmtui`) if install needs network access.
3. Welcome → leave American English (or set your preferred language).
4. Location → timezone; Keyboard → layout.
5. Users → create account; enable autologin only if you want it.
6. Desktop → GNOME, Plasma, or **No desktop**.
7. Allow unfree if you need proprietary firmware/drivers/apps.
8. Partitioning → select the target disk → **Erase disk** → **Swap (with Hibernation)** → optional LUKS → verify BIOS/UEFI indicator and disk name.
9. Summary → **Install** → wait → remove media → reboot.
10. After first boot: if Wi‑Fi or audio is missing, set `hardware.enableRedistributableFirmware = true` and rebuild.

For CLI-only media, partitioning by hand, dual-boot, or remote flake installs, use [Manual install](manual-install.md), [nixos-anywhere](nixos-anywhere.md), and [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md).

## References

- [NixOS manual — Graphical Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation-graphical)
- [NixOS manual — Networking in the installer](https://nixos.org/manual/nixos/stable/index.html#sec-installation-manual) (shared with manual install; NetworkManager and `nmtui`)
- [NixOS download page](https://nixos.org/download/) — graphical and minimal ISO images

## See also

- [Manual install](manual-install.md)
- [nixos-anywhere](nixos-anywhere.md)
- [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md)
- [Secure Boot and Lanzaboote](../configuration/secure-boot-and-lanzaboote.md)
- [Firmware and microcode](../configuration/firmware-and-microcode.md)
- [rebuild / switch / boot / test](../operations/rebuild-switch-boot-test.md)
- [Desktop](../desktop/README.md)
