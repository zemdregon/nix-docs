---
status: complete
---

# Graphical Installer

## Overview

The NixOS **graphical installer** is the recommended path for desktop users. Boot a **graphical** ISO or USB image (GNOME or Plasma variants from [nixos.org/download](https://nixos.org/download/)); the live desktop starts the installer and walks through language, location, keyboard, users, desktop choice, unfree software, partitioning, then install. **Minimal** images boot to a CLI instead—use [Manual install](manual-install.md).

## Details

**Boot media.** Download a graphical installation image, write it to USB (or use a CD), and boot from that drive. Prefer **UEFI** when the machine supports both BIOS and UEFI; you will often need to disable **Secure Boot** first. Shortly after boot, leave the default menu entry. The graphical image brings up its desktop and the installer (this can take a while). If you landed on a shell only, you used a minimal image—switch to [Manual install](manual-install.md).

**Installer screens (in order):**

1. **Welcome** — language for the installer and the installed system. Tip: leave **American English** if you want error text that is easier to search or report.
2. **Location / timezone** — set timezone (you can click the map). The installer may guess location from your public IP.
3. **Keyboard** — layout (and model if needed); pick the language you type in most comfortably.
4. **Users** — display name, login name, and password; optional automatic desktop login.
5. **Desktop environment** — choose a DE, or **No desktop** for a custom / window-manager setup. If undecided, GNOME or Plasma are both well-tested defaults with different designs.
6. **Unfree software** — option to allow unfree packages in the installed system.
7. **Partitioning** — easiest path is **Erase disk** (deletes all data on the selected disk). Also select **Swap (with Hibernation)** in the dropdown. Optional whole-disk **LUKS** encryption. Top-left shows whether the installer booted as **BIOS** or **UEFI**—if the machine is UEFI but the installer shows BIOS, reboot with the UEFI boot option. Confirm the **correct disk**; formatting destroys existing data. Deeper layout and boot-loader concepts: [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md).
8. **Summary** — review choices, then **Install**.

**Duration and finish.** Installation typically takes about **15 minutes** (varies with desktop choice, network, and disk speed). When done, remove the USB drive and reboot into the new system. Generated hardware settings land in [hardware-configuration.nix](../configuration/hardware-configuration.md); later changes use [rebuild / switch / boot / test](../operations/rebuild-switch-boot-test.md). Dual-boot and VMs: [Dual boot and VMs](dual-boot-and-vms.md).

## Examples

Typical desktop path after booting a graphical ISO:

1. Welcome → leave American English (or set your preferred language).
2. Location → timezone; Keyboard → layout.
3. Users → create account; enable autologin only if you want it.
4. Desktop → GNOME, Plasma, or **No desktop**.
5. Allow unfree if you need proprietary firmware/drivers/apps.
6. Partitioning → select the target disk → **Erase disk** → **Swap (with Hibernation)** → optional LUKS → verify BIOS/UEFI indicator and disk name.
7. Summary → **Install** → wait → remove media → reboot.

For CLI-only media, partitioning by hand, or dual-boot layouts the graphical flow does not cover, use [Manual install](manual-install.md) and [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md).

## References

- [NixOS manual — Graphical Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation-graphical)
- [NixOS download page](https://nixos.org/download/) — graphical and minimal ISO images

## See also

- [Manual install](manual-install.md)
- [Dual boot and VMs](dual-boot-and-vms.md)
- [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md)
- [hardware-configuration.nix](../configuration/hardware-configuration.md)
- [rebuild / switch / boot / test](../operations/rebuild-switch-boot-test.md)
