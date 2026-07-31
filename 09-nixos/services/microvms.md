---
status: complete
---

# MicroVMs

## Overview

[microvm.nix](https://github.com/microvm-nix/microvm.nix) is a Flake that builds and runs lightweight NixOS virtual machines on NixOS and macOS. Each guest runs its own kernel on a Type-2 hypervisor, giving stronger isolation than [NixOS containers](containers-and-nspawn.md) (which share the host kernel). VMs can be run as packages or managed as systemd services on the host.

Typical use: partition services into separate NixOS systems with independent update and rollback, without maintaining full hand-written VM images.

## Details

### Hypervisors and platforms

Set `microvm.hypervisor` on the guest NixOS module. Supported backends include **qemu**, **firecracker**, **cloud-hypervisor**, **crosvm**, **kvmtool**, and **stratovirt**. On macOS, **vfkit** uses Apple’s Virtualization.framework; building the guest still requires a Linux builder (see the project FAQ).

MicroVMs use virtio-oriented device models rather than fully emulated hardware, reducing overhead compared with traditional QEMU setups.

### Declaring a guest (flake)

Import the flake’s guest module and add a `nixosConfigurations` entry. The flake produces disk images and a runner script for each configuration:

```nix
{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.microvm.url = "github:microvm-nix/microvm.nix";
  inputs.microvm.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { nixpkgs, microvm }: {
    nixosConfigurations.my-microvm = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        microvm.nixosModules.microvm
        {
          networking.hostName = "my-microvm";
          microvm.hypervisor = "cloud-hypervisor";
        }
      ];
    };
  };
}
```

Quick start: `nix flake init -t github:microvm-nix/microvm.nix`.

### Declarative host management

On a NixOS host, import the flake’s host module and declare VMs under `microvm.vms`. The handbook binds `microvm` to `inputs.microvm.nixosModules` via `specialArgs`, so `imports = [ microvm.host ]` is the usual pattern (equivalent to `inputs.microvm.nixosModules.host` when not using that binding):

| Field | Meaning |
|-------|---------|
| `config` | Full in-place NixOS module for the guest — **fully declarative**; updates with the host rebuild (similar to [declarative containers](declarative-containers.md)). |
| `flake` | Reference to a `nixosConfigurations` entry — **declarative deploy**, imperative update via the `microvm` CLI afterward. |

The host module creates per-VM state under `/var/lib/microvms`. Building all guests with the host increases host build time and closure size.

### Root filesystem and store

By default the guest root is a read-only **erofs** or **squashfs** image containing only the closure needed for that NixOS configuration. Optionally share the host `/nix/store` (commonly via virtiofs) to avoid rebuilding large images or to speed up in-guest builds; a writable overlay is another documented tradeoff.

### How this differs from other tooling

| Approach | Role |
|----------|------|
| [Libvirt and VMs](libvirt-and-vms.md) | General hypervisor management (domains, networks, pools) — not NixOS-specific. |
| `nixos-rebuild build-vm` | One-off test VM for a single config — not a service isolation pattern. |
| [Containers and nspawn](containers-and-nspawn.md) | Shared kernel, cheaper, weaker isolation. |

## Examples

Minimal host-side fully declarative VM with shared store (from the handbook):

```nix
# microvm is inputs.microvm.nixosModules (via specialArgs)
{ microvm, ... }: {
  imports = [ microvm.host ];

  microvm.vms.my-microvm = {
    config = {
      microvm.shares = [{
        source = "/nix/store";
        mountPoint = "/nix/.ro-store";
        tag = "ro-store";
        proto = "virtiofs";
      }];
      # … guest NixOS options …
    };
  };
}
```

Declarative deploy with later imperative updates:

```nix
microvm.vms.my-microvm = {
  flake = self;
  updateFlake = "git+file:///etc/nixos";
};
```

## References

- [microvm.nix handbook](https://microvm-nix.github.io/microvm.nix/)
- [Declaring MicroVMs](https://microvm-nix.github.io/microvm.nix/declaring.html)
- [Declarative MicroVMs](https://microvm-nix.github.io/microvm.nix/declarative.html)
- [microvm-nix/microvm.nix (GitHub)](https://github.com/microvm-nix/microvm.nix)

## See also

- [Containers and nspawn](containers-and-nspawn.md)
- [Declarative containers](declarative-containers.md)
- [Libvirt and VMs](libvirt-and-vms.md)
- [Dual boot and VMs](../installation/dual-boot-and-vms.md)
