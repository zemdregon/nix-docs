---
status: complete
last-checked: 2026-08
---

# nixos-generators

## Overview

**nixos-generators** ([nix-community/nixos-generators](https://github.com/nix-community/nixos-generators)) turns one NixOS configuration into many disk/image formats—cloud disks, installer ISOs, qcow2 VMs, SD card images, kexec tarballs, and more—without rewriting the config for each target.

From **NixOS 25.05** onward, nixpkgs owns this workflow. The nix-community project is **deprecated**; maintainers upstreamed most formats into `image.modules` / `config.system.build.images`. **New work should use `nixos-rebuild build-image --image-variant …`**, not `nixos-generate` or flake `nixosGenerate`, unless you are pinned to an older release or debugging a format that has not migrated. Older docs, blog posts, and flakes still reference the legacy CLI—treat those as historical.

## Details

### Preferred path (NixOS ≥ 25.05)

The upstream replacement is a first-class part of `nixos-rebuild`:

```bash
nixos-rebuild build-image --image-variant <name>
```

Run **`nixos-rebuild build-image` with no arguments** on the configuration you intend to ship. It prints the variant names valid for that eval—do not copy variant strings from an old blog post or the nixos-generators README without checking; names drift across releases (see [Name renames](#name-renames) below).

| Legacy (nixos-generators) | Upstream (25.05+) |
|---------------------------|-------------------|
| `nixos-generate -f iso -c ./configuration.nix` | `nixos-rebuild build-image --image-variant iso` |
| `nix run github:nix-community/nixos-generators -- -f qcow -c …` | `nixos-rebuild build-image --image-variant qcow --flake .#host` |
| flake `nixosGenerate { format = "qcow"; … }` | `self.nixosConfigurations.host.config.system.build.images.qcow` |
| module `config.formats.<name>` via `all-formats` | `config.system.build.images.<variant>` |

Per-variant tweaks use `image.modules.<variant>` (same idea as specialisations). Manual: [Building Images with nixos-rebuild build-image](https://nixos.org/manual/nixos/stable/#sec-image-nixos-rebuild-build-image).

Flake consumers expose the same derivations as packages:

```nix
packages.x86_64-linux.myhost-qcow =
  self.nixosConfigurations.myhost.config.system.build.images.qcow;
```

Build on the host with `nixos-rebuild build-image --image-variant qcow --flake .#myhost`. The command prints the store path of the finished artifact when the build completes.

### Role

You write a normal NixOS module graph (packages, services, users). An **image variant** selects which installer/image modules and `system.build.*` attribute to materialize. Same configuration, different `--image-variant` (or legacy `-f`).

Representative formats historically shipped by nixos-generators (most now have nixpkgs equivalents): `amazon`, `azure`, `gce`, `do`, `openstack`, `iso`, `install-iso`, `qcow`, `qcow-efi`, `raw`, `raw-efi`, `virtualbox`, `vmware`, `hyperv`, `docker`, `lxc`, `proxmox`, `kexec`, and SD-card variants. The [project README format table](https://github.com/nix-community/nixos-generators) maps legacy names to upstream support; confirm live names with `nixos-rebuild build-image` (no args).

### Cloud formats covered elsewhere

**Amazon EC2, Google Compute Engine, and Microsoft Azure** share the same build-image mechanics but differ sharply in upload, registration, and day-two ops. See [Amazon / GCE / Azure](amazon-gce-azure.md) for AMI discovery, GCE `.raw.tar.gz` upload, Azure VHD registration, and provider-specific pitfalls—this page does not duplicate that material.

### Other cloud and virtualization formats

These variants produce artifacts you upload or import on a provider or hypervisor. **Upload and register steps are provider-specific**; follow each vendor’s image-import documentation and the NixOS wiki for your platform. This wiki does not document provider APIs.

| Variant (legacy / upstream) | Typical artifact | Use case |
|------------------------------|------------------|----------|
| `do` | DigitalOcean-compatible disk image | Custom droplet images when you need modules or secrets beyond a stock install. After build, import via DigitalOcean’s custom-image workflow (see [DO docs](https://docs.digitalocean.com/products/custom-images/) and community wiki recipes). |
| `openstack` | qcow2 tuned for OpenStack | Private or public OpenStack clouds: build locally, upload the qcow2 to Glance (or your operator’s import path). |
| `proxmox` | [VMA](https://pve.proxmox.com/wiki/VMA) archive | Import into Proxmox VE as a VM template. Related upstream variant `proxmox-lxc` builds an LXC template instead of a full VM disk. |
| `qcow` / `qcow-efi` | qcow2 virtual disk | Local QEMU/KVM, libvirt, or generic VM testing—not tied to one cloud. `qcow-efi` targets UEFI guests; pick the variant that matches your firmware. |
| `kexec` | tarball (`kexec_nixos` tree) | Boot into NixOS **without** removable install media on a running Linux host: extract and run the bundled kexec script (see manual [kexec install path](https://nixos.org/manual/nixos/stable/#sec-installing-kexec)). Useful when you cannot attach an ISO but the machine has `kexec` available; hardware re-init quirks apply. |

After `build-image` finishes, note the printed store path and copy or upload the artifact using your provider’s tooling. No universal “register image” flag exists in NixOS itself.

### SD and board images

ARM/x86 SD-card outputs moved to the `sd-card` variant plus an explicit `system` (replacing names like `sd-aarch64`). Cross-compilation and partition layout are board-specific. See [Raspberry Pi and embedded](raspberry-pi-embedded.md) and the wiki [Building Images (ARM)](https://wiki.nixos.org/wiki/NixOS_on_ARM/Building_Images).

### Classic surfaces (legacy)

While the package remains in nixpkgs, three entry points still exist for older workflows:

| Surface | What it does |
|---------|----------------|
| CLI `nixos-generate` | Build one format from a config (`-c`) or defaults; prints the store path |
| Flake `nixosGenerate` | Library function: `format`, `modules`, optional `customFormats` → package output |
| Module `all-formats` | Import into a NixOS config; build via `config.formats.<name>` |

Flakes often pin `github:nix-community/nixos-generators` with `nixpkgs.follows` aligned to the host channel. Prefer upstream `build-image` for new flakes.

### Name renames

Upstream renamed several variants when absorbing nixos-generators. Wrong names fail at eval or build time with “unknown variant” errors.

| nixos-generators `-f` | NixOS ≥ 25.05 `--image-variant` | Notes |
|-----------------------|----------------------------------|-------|
| `install-iso` | `iso-installer` | Full installer ISO |
| `gce` | `google-compute` | See [Amazon / GCE / Azure](amazon-gce-azure.md) |
| `sd-aarch64`, `sd-aarch64-installer`, `sd-x86_64` | `sd-card` | Also set `system` (`aarch64-linux` / `x86_64-linux`); see [Raspberry Pi and embedded](raspberry-pi-embedded.md) |
| `kexec-bundle` | `kexec` | Single tarball workflow |

When migrating a flake, grep for `nixosGenerate`, `nixos-generate`, and hard-coded `format = "…"` strings.

### Failure modes

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| `error: unknown image variant '…'` | Typo, renamed variant, or variant not enabled for this config | Run `nixos-rebuild build-image` (no args) on the same flake/host; compare with [name renames](#name-renames) |
| Built image boots wrong firmware (BIOS vs UEFI) or wrong partition table | Picked `qcow` vs `qcow-efi`, `raw` vs `raw-efi`, or Azure Gen1 vs Gen2 expectations | Match variant to guest firmware; re-read provider docs ([Amazon / GCE / Azure](amazon-gce-azure.md) for cloud) |
| `aarch64` binary on `x86_64` builder (or vice versa) | Cross-system image build without `--system` / correct `system` in the NixOS config | Set `nixpkgs.hostPlatform` / build with `--system aarch64-linux`; for SD images see [Raspberry Pi and embedded](raspberry-pi-embedded.md) and the ARM wiki |
| Flake builds on CI but variant missing on laptop | Different nixpkgs pin or incomplete `nixosConfigurations` | Align `inputs.nixpkgs` and evaluate the same `#host` attr everywhere |
| “It worked with `nixos-generate`” but docs say deprecated | Following pre-25.05 tutorials | Switch to `build-image`; keep legacy CLI only on older NixOS or while bisecting a migration bug |
| Image builds but provider rejects upload | Wrong format for that cloud (e.g. uploading qcow where VHD expected) | Use the provider’s documented format column; cloud specifics live in [Amazon / GCE / Azure](amazon-gce-azure.md) and vendor docs—not in nixpkgs |
| SD image wrong size or missing firmware partition | Used generic `raw` instead of `sd-card` / board modules | Follow [Raspberry Pi and embedded](raspberry-pi-embedded.md) module imports |

### Fit with other topics

Container-ish outputs (`docker`, `lxc`, `proxmox-lxc`) sit next to [OCI containers](../../11-development/containers-oci.md); they are disk/tarball artifacts, not a substitute for declarative container runtime config. Installer ISOs relate to [manual install](../../09-nixos/installation/manual-install.md). The rebuild CLI that owns `build-image` is documented in [nixos-rebuild](../frontends-and-ux/nixos-rebuild.md).

## Examples

List variants for the current configuration (preferred discovery step):

```bash
nixos-rebuild build-image
# prints available --image-variant names for this config
```

Preferred build on NixOS 25.05+ (flake):

```bash
nixos-rebuild build-image --image-variant qcow --flake .#myhost
```

Flake package from `system.build.images`:

```nix
{
  outputs = { self, ... }: {
    packages.x86_64-linux.myhost-qcow =
      self.nixosConfigurations.myhost.config.system.build.images.qcow;
  };
}
```

Per-variant module override (upstream pattern):

```nix
{
  image.modules.qcow = {
    services.openssh.enable = lib.mkForce false;
  };
}
```

Legacy one-shot ISO (historical; use `build-image` for new work):

```bash
nixos-generate -f iso -c ./configuration.nix
```

Legacy flake `nixosGenerate` (migrate to `system.build.images`):

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

## See also

- [Amazon / GCE / Azure](amazon-gce-azure.md) — EC2, GCE, and Azure image targets, upload, and registration context
- [Raspberry Pi and embedded](raspberry-pi-embedded.md) — SD / board images and `sd-card` variant
- [OCI containers](../../11-development/containers-oci.md) — container images vs disk formats
- [Manual install](../../09-nixos/installation/manual-install.md) — installer media and traditional install path
- [nixos-rebuild](../frontends-and-ux/nixos-rebuild.md) — rebuild CLI that now owns `build-image`

## References

- [Building Images with nixos-rebuild build-image](https://nixos.org/manual/nixos/stable/#sec-image-nixos-rebuild-build-image) — upstream successor, `image.modules`, `system.build.images` (NixOS stable manual)
- [nix-community/nixos-generators](https://github.com/nix-community/nixos-generators) — deprecation notice, legacy format table, migration notes (upstreamed from NixOS **25.05**)
- [NixOS on ARM: Building Images](https://wiki.nixos.org/wiki/NixOS_on_ARM/Building_Images) — SD-card and cross-build context for embedded targets
