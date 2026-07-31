---
status: complete
---

# Libvirt and VMs

## Overview

On NixOS, **libvirt** is the persistent host hypervisor for managing QEMU/KVM virtual machines. Enabling `virtualisation.libvirtd` starts `libvirtd`, which exposes a common API for creating, starting, and configuring guests. Typical clients include `virsh`, GNOME Boxes, and [virt-manager](https://search.nixos.org/options?query=programs.virt-manager).

This path suits arbitrary guest OS images (Windows, other Linux distros, etc.) that you manage over time. It differs from `nixos-rebuild build-vm`, which builds a one-shot QEMU test of *your* NixOS configuration, and from NixOS [containers](containers-and-nspawn.md), which share the host store with weaker isolation than full VMs.

## Details

### Enabling libvirtd

Set `virtualisation.libvirtd.enable = true`. The module is defined in nixpkgs `nixos/modules/virtualisation/libvirtd.nix`. The daemon requires Polkit (`security.polkit.enable`; the module enables it when libvirt is on).

Users in the **`libvirtd`** group can manage VMs via the Unix socket (for example with `virsh` or virt-manager). Add non-root accounts with `users.users.<name>.extraGroups = [ "libvirtd" ];`.

### Common companion options

| Option | Role |
|--------|------|
| `programs.virt-manager.enable` | Installs the virt-manager GUI and default `qemu:///system` connection |
| `virtualisation.libvirtd.qemu.swtpm.enable` | Lets libvirtd use swtpm for emulated TPM in guests |
| `virtualisation.spiceUSBRedirection.enable` | Setuid helper so users can redirect USB devices into SPICE guests |
| `virtualisation.libvirtd.qemu.vhostUserPackages` | Out-of-tree vhost-user drivers (for example `[ pkgs.virtiofsd ]` for virtiofs shares) |

Guest networking, storage, UEFI/OVMF, hooks, and firewall rules for `virbr0` are configured through libvirt (XML, `virsh`, or a GUI)—not only through NixOS options. The module symlinks QEMU emulators and OVMF firmware under `/run/libvirt` and copies default network XML into `/var/lib/libvirt`.

### Compared to other isolation models

| Approach | Isolation | Typical use |
|----------|-----------|-------------|
| **libvirt / KVM** | Full VM, separate kernel | Arbitrary OS images, desktop VMs, passthrough |
| **`nixos-rebuild build-vm`** | Full VM, ephemeral disk | Test *this* NixOS config without switching the host |
| **NixOS containers (nspawn)** | Shared store, root-in-container can affect host | Lightweight NixOS instances on one machine |
| **MicroVMs** | Minimal VM with declarative NixOS guest config | Sandboxed NixOS services (see [MicroVMs](microvms.md)) |

For install-time VM scenarios (VirtualBox guest, dual boot), see [Dual boot and VMs](../installation/dual-boot-and-vms.md). For rebuild modes including `build-vm`, see [rebuild switch / boot / test](../operations/rebuild-switch-boot-test.md).

## Examples

Minimal host configuration:

```nix
{
  virtualisation.libvirtd.enable = true;

  programs.virt-manager.enable = true;

  virtualisation.libvirtd.qemu.swtpm.enable = true;
  virtualisation.spiceUSBRedirection.enable = true;

  users.users.alice.extraGroups = [ "libvirtd" ];
}
```

After `nixos-rebuild switch`, open virt-manager or run `virsh list --all` as a member of `libvirtd`.

## References

- [NixOS option search: `virtualisation.libvirtd`](https://search.nixos.org/options?query=virtualisation.libvirtd)
- nixpkgs module: [`nixos/modules/virtualisation/libvirtd.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/virtualisation/libvirtd.nix)
- [Libvirt (NixOS Wiki)](https://wiki.nixos.org/wiki/Libvirt) — community examples (networking, virtiofs, hooks)

## See also

- [Dual boot and VMs](../installation/dual-boot-and-vms.md) — guest install and `build-vm`
- [rebuild switch / boot / test](../operations/rebuild-switch-boot-test.md) — `build-vm` testing workflow
- [Containers and nspawn](containers-and-nspawn.md) — shared-store NixOS containers
- [Declarative containers](declarative-containers.md) — `containers.*` in configuration
- [MicroVMs](microvms.md) — declarative minimal VMs
