---
status: complete
---

# nixos-generators

## Overview

**nixos-generators** ([nix-community/nixos-generators](https://github.com/nix-community/nixos-generators)) turns one NixOS configuration into many disk/image formats—cloud AMIs and cloud disks, installer ISOs, qcow2 VMs, SD card images, and more—without rewriting the config for each target.

Starting with **NixOS 25.05**, most of this tooling was upstreamed into nixpkgs. The project’s maintainers treat the standalone package as deprecated in favor of `nixos-rebuild build-image` and `config.system.build.images`. Older docs and flakes still refer to `nixos-generate` / `nixosGenerate`; new work should prefer the nixpkgs path unless you need a format that has not migrated yet.

## Details

### Role

You write a normal NixOS module graph (packages, services, users). A **format** selects which installer/image modules and `system.build.*` attr to materialize—for example `amazon` for EC2, `gce` for Google Compute, `iso` / `install-iso` for optical/USB install media, `qcow` / `qcow-efi` for QEMU, `raw` / `raw-efi` for bare metal flash, `sd-aarch64` for ARM boards. Same config, different `-f` / `--image-variant`.

Representative formats historically shipped by nixos-generators (many now have nixpkgs `build-image` equivalents): `amazon`, `azure`, `gce`, `do`, `openstack`, `iso`, `install-iso`, `qcow`, `qcow-efi`, `raw`, `raw-efi`, `virtualbox`, `vmware`, `hyperv`, `docker`, `lxc`, `proxmox`, `kexec`, and SD-card variants. Exact names and which ones appear in `nixos-rebuild build-image` change over releases—list variants with that command (no args) or check the project README’s format table.

### Classic surfaces

| Surface | What it does |
|---------|----------------|
| CLI `nixos-generate` | Build one format from a config (`-c`) or defaults; prints the store path |
| Flake `nixosGenerate` | Library function: `format`, `modules`, optional `customFormats` → package output |
| Module `all-formats` | Import into a NixOS config; build via `config.formats.<name>` |

The package has long been in nixpkgs as `nixos-generators`; flakes often pin `github:nix-community/nixos-generators` so `nixpkgs.follows` stays aligned.

### Upstream successor (NixOS ≥ 25.05)

| Old | New |
|-----|-----|
| `nixos-generate -f iso` | `nixos-rebuild build-image --image-variant iso` |
| flake `nixosGenerate { format = "iso"; … }` | attr of `config.system.build.images` (e.g. `.iso`) |
| some SD / installer names | renamed (e.g. `install-iso` → `iso-installer`; SD → `sd-card` + `system`) |

Flake example for the new API: expose `self.nixosConfigurations.myhost.config.system.build.images.iso` as a package, or run `nixos-rebuild build-image --image-variant iso --flake .#myhost`. Manual: [Building Images with nixos-rebuild build-image](https://nixos.org/manual/nixos/stable/#sec-image-nixos-rebuild-build-image).

### Fit with other topics

Cloud upload and provider-specific wiring: [Amazon / GCE / Azure](amazon-gce-azure.md). Board / SD images: [Raspberry Pi and embedded](raspberry-pi-embedded.md). Container-ish outputs (`docker`, `lxc`) sit next to [OCI containers](../../11-development/containers-oci.md); they are not a substitute for declarative container tooling. Installer ISOs relate to [manual install](../../09-nixos/installation/manual-install.md).

## Examples

Classic one-shot ISO from a configuration file (pre-upstream / still-supported CLI while the package exists):

```bash
nixos-generate -f iso -c ./configuration.nix
```

Run without installing (flake):

```bash
nix run github:nix-community/nixos-generators -- -f qcow -c ./configuration.nix
```

Minimal flake package using `nixosGenerate` (legacy API):

```nix
{
  inputs.nixos-generators.url = "github:nix-community/nixos-generators";
  inputs.nixos-generators.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { nixpkgs, nixos-generators, ... }: {
    packages.x86_64-linux.qcow = nixos-generators.nixosGenerate {
      system = "x86_64-linux";
      modules = [ ./configuration.nix ];
      format = "qcow";
    };
  };
}
```

Preferred on NixOS 25.05+ (same machine flake):

```bash
nixos-rebuild build-image --image-variant qcow --flake .#myhost
```

Or as a flake package:

```nix
packages.x86_64-linux.myhost-qcow =
  self.nixosConfigurations.myhost.config.system.build.images.qcow;
```

## See also

- [Amazon / GCE / Azure](amazon-gce-azure.md) — cloud image targets and provider context
- [Raspberry Pi and embedded](raspberry-pi-embedded.md) — SD / board images
- [OCI containers](../../11-development/containers-oci.md) — container images vs disk formats
- [Manual install](../../09-nixos/installation/manual-install.md) — installer media and traditional install path
- [nixos-rebuild](../frontends-and-ux/nixos-rebuild.md) — rebuild CLI that now owns `build-image`

## References

- [nix-community/nixos-generators](https://github.com/nix-community/nixos-generators) — README deprecation notice, format table, migration to `build-image` (verified 2026-07; upstreamed from NixOS **25.05**)
- [Building Images with nixos-rebuild build-image](https://nixos.org/manual/nixos/stable/#sec-image-nixos-rebuild-build-image) — NixOS manual (upstream successor, stable)
