---
status: complete
---

# Amazon / GCE / Azure

## Overview

NixOS on AWS, Google Compute Engine, and Azure is mostly an **image** problem: boot a NixOS disk image, then manage the system with flakes and deploy tools. Coverage is uneven. **Amazon EC2** has official AMIs published by the NixOS project (discover them via API/Terraform—do not hardcode IDs). **GCE** and **Azure** do not ship maintained public NixOS images from the project; you build and register your own, or install onto a generic VM with [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md).

From NixOS **25.05** onward, the preferred build path is upstream `nixos-rebuild build-image --image-variant …`. [nixos-generators](nixos-generators.md) historically wrapped the same formats and is deprecated in favor of that path.

## Details

### Preferred build path (NixOS ≥ 25.05)

nixpkgs defines cloud/virtualization image variants under `image.modules` / `system.build.images`. Build them with:

```bash
nixos-rebuild build-image --image-variant <name>
```

Run `nixos-rebuild build-image` **with no arguments** to list variants available for the evaluated config. Relevant cloud names include `amazon`, `google-compute`, and `azure` (confirm with that listing—names can change across releases).

Flake form (host attr from `nixosConfigurations`):

```bash
nixos-rebuild build-image --flake .#host --image-variant amazon
```

Same pattern for `--image-variant google-compute` or `azure`. Manual: [Building Images with nixos-rebuild build-image](https://nixos.org/manual/nixos/stable/#sec-image-nixos-rebuild-build-image) (`#sec-image-nixos-rebuild-build-image`).

Per-variant tweaks use `image.modules.<variant>` (same idea as specialisations). Older workflows used [nixos-generators](nixos-generators.md) formats `amazon` / `gce` / `azure`; new work should prefer `build-image` unless a format has not migrated.

### Amazon EC2

[nixos.org/download](https://nixos.org/download/) documents official NixOS AMIs: weekly publishes to all AWS regions for `x86_64` and `arm64`. Filter on the documented AWS account owner and a **name prefix** for the release channel (illustrative: `nixos/26.05*`) plus architecture—via Terraform/OpenTofu `aws_ami` or `ec2 describe-images`. Never pin a fixed AMI ID.

Older images are expected to be deprecated and garbage-collected (~90-day horizon on the download page; verified 2026-08). An image searcher is linked from the download page for one-off lookups.

Custom AMIs: build with `--image-variant amazon`, then upload/register in your account when you need modules or secrets the public image does not provide.

### Google Compute Engine

There are **no** publicly maintained recent NixOS GCE images from the project. Old objects in community buckets (`gs://nixos-images`, `gs://nixos-cloud-images`) are stale.

Primary path: build `--image-variant google-compute` (produces a `.raw.tar.gz`), upload to a GCS bucket, register a GCE image, then launch VMs from it. Secondary recipe and upload helper: [Install NixOS on GCE](https://wiki.nixos.org/wiki/Install_NixOS_on_GCE) and nixpkgs `create-gce.sh`.

Treat ACL warnings seriously: the stock `create-gce.sh` path makes objects/images broadly readable—build custom configs with secrets using tighter upload permissions. After boot, OS Login / metadata expectations are documented on that wiki page.

### Azure

The NixOS project does **not** publish a maintained official Marketplace image. Historical in-tree ID lists were dropped as years out of date. Practical paths:

1. Build a VHD with `--image-variant azure` (Generation 1 / VHD; Gen 2 via image options in nixpkgs) and upload it into your subscription as a managed image or Shared Image Gallery image.
2. Provision a generic Linux VM and install with [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md).
3. Treat third-party Marketplace listings as unaudited community/vendor images, not project releases.

### Ops split and first boot

Cloud images typically consume **provider metadata** (and often **cloud-init**) for SSH keys, hostname, and similar first-boot glue. After that, prefer declarative NixOS config activated over SSH.

Same ownership split as [Terraform + NixOS](../../12-deployment-and-infra/terraform-nixos.md): **IaC** (Terraform/OpenTofu/etc.) owns instance lifecycle and which image boots; **Nix** owns the system closure. Ongoing activation uses [remote deploy](../../09-nixos/operations/remote-deploy.md) / [nixos-rebuild](../frontends-and-ux/nixos-rebuild.md) (or [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md) for first install). Baking every package bump into a new AMI/GCE/Azure image is optional, not required.

### Image tooling

| Path | Role |
|------|------|
| Official EC2 AMIs | Fastest start on AWS; query by owner + name filter |
| `nixos-rebuild build-image --image-variant amazon\|google-compute\|azure` | Custom images from your `nixosConfigurations` (25.05+) |
| [nixos-generators](nixos-generators.md) | Historical multi-format CLI; deprecated toward `build-image` |
| nixpkgs scripts (`create-gce.sh`, Azure maintainer scripts) | Upload/register helpers around those builds |
| [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md) | Skip custom images: install onto throwaway cloud Linux |

## Examples

List variants, then build cloud images from a flake host (NixOS ≥ 25.05):

```bash
nixos-rebuild build-image
# prints available --image-variant names for this config

nixos-rebuild build-image --flake .#host --image-variant amazon
nixos-rebuild build-image --flake .#host --image-variant google-compute
nixos-rebuild build-image --flake .#host --image-variant azure
```

Upload/register the resulting store path per cloud (AMI register, GCS → GCE image, Azure managed/gallery VHD). For AMI discovery filters (owner + `nixos/26.05*` name prefix, no hardcoded IDs), see [nixos.org/download](https://nixos.org/download/) and pair with [Terraform + NixOS](../../12-deployment-and-infra/terraform-nixos.md).

## References

- [Building Images with nixos-rebuild build-image](https://nixos.org/manual/nixos/stable/#sec-image-nixos-rebuild-build-image) — `#sec-image-nixos-rebuild-build-image`; variants via `image.modules` / `system.build.images`
- [NixOS Download — Amazon AMIs](https://nixos.org/download/) — official AMI discovery; owner `427812963091`; name prefix e.g. `nixos/26.05*`; ~90-day GC note (verified 2026-08)
- [Install NixOS on GCE (NixOS Wiki)](https://wiki.nixos.org/wiki/Install_NixOS_on_GCE) — build/upload/register; ACL warning
- [nixpkgs `create-gce.sh`](https://github.com/NixOS/nixpkgs/blob/master/nixos/maintainers/scripts/gce/create-gce.sh) — GCE image build + GCS upload helper
- [nix-community/nixos-generators](https://github.com/nix-community/nixos-generators) — historical builders; deprecation toward `build-image` (NixOS ≥ 25.05)

## See also

- [nixos-generators](nixos-generators.md)
- [Terraform + NixOS](../../12-deployment-and-infra/terraform-nixos.md)
- [Remote deploy](../../09-nixos/operations/remote-deploy.md)
- [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md)
- [nixos-rebuild](../frontends-and-ux/nixos-rebuild.md)
