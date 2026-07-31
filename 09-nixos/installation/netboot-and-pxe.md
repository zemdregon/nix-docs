---
status: complete
---

# Netboot and PXE

## Overview

Netboot (PXE or iPXE) lets you boot the NixOS installer over the network instead of attaching USB or ISO media. The upstream path assumes you already run a PXE/iPXE stack (DHCP/TFTP and often HTTP); you build `bzImage`, `initrd`, and an example iPXE script from nixpkgs, host them on your infrastructure, then follow the same install steps as a [manual install](manual-install.md) once the live environment is up.

This is an advanced install path—most users should use the [graphical installer](graphical-installer.md) or a normal minimal ISO. Netboot fits homelab racks, datacenter provisioning, or a NixOS host that serves installers to other machines on the LAN.

## Details

**Build netboot artifacts.** From a checkout or channel of nixpkgs, build the release netboot attribute for your architecture (example for `x86_64-linux`):

```bash
nix-build -A netboot.x86_64-linux '<nixpkgs/nixos/release.nix>'
```

The `result/` directory contains:

- `bzImage` — Linux kernel
- `initrd` — initial ramdisk
- `netboot.ipxe` — example iPXE script with the correct kernel command line for this image

Copy these files to whatever serves your netboot clients (TFTP root, HTTP directory, etc.). The manual does not publish fixed Hydra download URLs for these artifacts; build locally or mirror your own `result/` until upstream documents otherwise.

**Plain PXE.** Point the bootloader at `bzImage` and `initrd`, and pass the same kernel command-line arguments shown in `netboot.ipxe` (including the `init=` path into the netboot store path).

**iPXE.** Depending on how HTTP/FTP is laid out, you may use `netboot.ipxe` unchanged or edit the kernel/initrd URLs to match your server paths. Clients need reachable URLs for both files and enough RAM for the installer initrd.

**After boot.** You land in the same installer environment as other live images: partition and mount the target, run `nixos-generate-config`, edit `configuration.nix`, and run `nixos-install`. See [Manual install](manual-install.md). For unattended or remote installs over SSH after boot, compare [nixos-anywhere](nixos-anywhere.md).

**Serving from a NixOS host (Pixiecore).** The [NixOS Wiki — Netboot](https://wiki.nixos.org/wiki/Netboot) documents patterns using [Pixiecore](https://github.com/danderson/pixiecore) on an existing NixOS machine with a working DHCP server. Those examples are community/wiki-shaped—adapt ports, firewall, and paths to your network. Option names below match `services.pixiecore` in current nixpkgs (verify on [search.nixos.org](https://search.nixos.org/options?query=services.pixiecore)).

- **netboot.xyz (multi-OS menu):** `mode = "quick"` with `quick = "xyz"` uses Pixiecore’s built-in netboot.xyz chain. Recent iPXE on clients is required for HTTPS boot URLs. Some wiki snippets set `kernel = "https://boot.netboot.xyz"` instead; the module’s `quick` mode is the supported equivalent.
- **Custom NixOS netboot image:** Import `modulesPath + "/installer/netboot/netboot-minimal.nix"` in a small `nixosSystem`, build kernel and netboot ramdisk from `config.system.build`, then set `mode = "boot"` with `kernel`, `initrd`, and `cmdLine`. Match the command line in `netboot.ipxe` (at minimum `init=${config.system.build.toplevel}/init` plus `boot.kernelParams`; wiki examples often add `loglevel=4`). The wiki also shows wrapping `pixiecore boot …` in a `nix-build` script when you want a one-shot runner outside `services.pixiecore`.

Set `dhcpNoBind = true` when another DHCP server already binds port 67; open firewall ports or use `openFirewall = true` where appropriate.

**Offline and airgapped sites.** Netboot still needs network delivery of kernel/initrd (local TFTP/HTTP on an isolated LAN is fine). Building the closure on a connected machine and serving it internally overlaps with [Airgap and offline](../../12-deployment-and-infra/airgap-and-offline.md); do not assume `boot.netboot.xyz` works without outbound HTTPS.

## Examples

Build the stock installer netboot bundle:

```bash
nix-build -A netboot.x86_64-linux '<nixpkgs/nixos/release.nix>'
# ls result/   # bzImage  initrd  netboot.ipxe
```

Inspect `result/netboot.ipxe` for the kernel cmdline, then configure your PXE/iPXE server to serve `result/bzImage` and `result/initrd` with matching arguments.

Pixiecore on a NixOS host — netboot.xyz quick menu (wiki-style; requires recent iPXE clients):

```nix
services.pixiecore = {
  enable = true;
  openFirewall = true;
  dhcpNoBind = true;
  mode = "quick";
  quick = "xyz";
};
```

Pixiecore serving a custom netboot-minimal system (paths come from your `nixosSystem` build output):

```nix
services.pixiecore = {
  enable = true;
  openFirewall = true;
  dhcpNoBind = true;
  mode = "boot";
  kernel = "${build.kernel}/${build.kernel.target}"; # bzImage on x86_64-linux
  initrd = "${build.netbootRamdisk}/initrd";
  cmdLine = "init=${build.toplevel}/init loglevel=4"; # extend to match netboot.ipxe if boot fails
};
```

Replace `build` with the `config.system.build` attrset from a `nixosSystem` that imports `installer/netboot/netboot-minimal.nix`. The wiki’s `nix-build` wrapper script is an alternative when you prefer not to enable the systemd service.

## References

- [NixOS manual — Booting from the netboot media (PXE)](https://nixos.org/manual/nixos/stable/#sec-booting-from-pxe)
- [NixOS manual — Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation)
- [NixOS Wiki — Netboot](https://wiki.nixos.org/wiki/Netboot)
- [NixOS option — `services.pixiecore`](https://search.nixos.org/options?query=services.pixiecore)

## See also

- [Manual install](manual-install.md)
- [Graphical installer](graphical-installer.md)
- [nixos-anywhere](nixos-anywhere.md)
- [Dual-boot and VMs](dual-boot-and-vms.md)
- [Airgap and offline](../../12-deployment-and-infra/airgap-and-offline.md)
