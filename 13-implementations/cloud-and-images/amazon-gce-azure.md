---
status: complete
---

# Amazon / GCE / Azure

## Overview

NixOS on the big three clouds is mostly an **image** problem: boot a NixOS disk image, then manage the system with flakes and deploy tools. Coverage is uneven. **Amazon EC2** has official AMIs published by the NixOS project (discover them via API/Terraform—do not hardcode IDs). **Google Compute Engine** and **Azure** do not ship maintained public NixOS images from the project; you build and register your own (or install onto a generic VM with [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md)).

Image formats for `amazon`, `gce` / `google-compute`, and `azure` live in nixpkgs. Historically [nixos-generators](nixos-generators.md) wrapped them; from NixOS **25.05** onward, prefer `nixos-rebuild build-image --image-variant …` (generators is marked deprecated in favor of that upstream path).

## Details

### Amazon EC2

[nixos.org/download](https://nixos.org/download/) documents official NixOS AMIs: weekly publishes to all AWS regions for `x86_64` and `arm64`. The download page names the AWS account owner to filter on and recommends a Terraform/OpenTofu `aws_ami` data source (or `ec2 describe-images`) with a **name prefix** for the release channel (e.g. `nixos/26.05*`) plus architecture—not a pinned AMI ID.

Older images are expected to be deprecated and garbage-collected (the download page notes a ~90-day horizon). Hardcoding AMI IDs in Terraform or scripts will break; always resolve “latest matching filter” at apply time. An image searcher is linked from the download page for one-off lookups.

Custom AMIs: build with `--image-variant amazon` (or the generators `amazon` format), upload/register in your account when you need modules or secrets baked in that the public image does not provide.

### Google Compute Engine

There are **no** publicly maintained recent NixOS GCE images from the project. Old objects in community buckets (`gs://nixos-images`, `gs://nixos-cloud-images`) are stale. The [NixOS Wiki: Install NixOS on GCE](https://wiki.nixos.org/wiki/Install_NixOS_on_GCE) recipe is: build a google-compute image (nixpkgs `create-gce.sh` or `build-image` / generators `gce`), upload the `.raw.tar.gz` to a GCS bucket, register a GCE image, then launch VMs from it.

Treat ACL warnings seriously: the stock `create-gce.sh` path makes objects/images broadly readable—build custom configs with secrets using tighter upload permissions. After boot, OS Login / metadata expectations are documented on the wiki for that image family.

### Azure

The NixOS project does **not** publish a maintained official Marketplace image. Historical in-tree AMI-style ID lists for Azure were dropped as years out of date. Practical paths:

1. Build a VHD with `--image-variant azure` (generators format `azure`: Generation 1 / VHD; Gen 2 via image options in nixpkgs) and upload it into your subscription as a managed image / gallery image.
2. Provision a generic Linux VM and install with [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md).
3. Treat third-party Marketplace listings as unaudited community/vendor images, not project releases.

### First boot and ongoing config

Cloud images typically consume **provider metadata** (and often **cloud-init**) for SSH keys, hostname, and similar first-boot glue. After that, prefer declarative NixOS config activated over SSH—same split as [Terraform + NixOS](../../12-deployment-and-infra/terraform-nixos.md): IaC owns instance + which image boots; Nix owns the system closure. Baking every package bump into a new AMI/GCE/Azure image is optional, not required.

### Image tooling

| Path | Role |
|------|------|
| Official EC2 AMIs | Fastest start on AWS; query by owner + name filter |
| `nixos-rebuild build-image --image-variant amazon\|google-compute\|azure` | Custom images from your `nixosConfigurations` (25.05+) |
| [nixos-generators](nixos-generators.md) | Same formats historically (`amazon`, `gce`, `azure`); migrating to `build-image` |
| nixpkgs scripts (`create-gce.sh`, Azure maintainer scripts) | Upload/register helpers around those builds |
| [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md) | Skip custom images: install onto a throwaway cloud Linux |

## Examples

Resolve the latest official arm64 NixOS AMI in one region (from [nixos.org/download](https://nixos.org/download/); adjust release prefix and region; do not paste a fixed AMI id):

```hcl
provider "aws" {
  region = "eu-central-1"
}

data "aws_ami" "nixos_arm64" {
  owners      = ["427812963091"]
  most_recent = true

  filter {
    name   = "name"
    values = ["nixos/26.05*"]
  }
  filter {
    name   = "architecture"
    values = ["arm64"] # or "x86_64"
  }
}

resource "aws_instance" "nixos_arm64" {
  ami           = data.aws_ami.nixos_arm64.id
  instance_type = "t4g.nano"
}
```

Equivalent CLI shape (same filters):

```bash
aws ec2 describe-images \
  --owners 427812963091 \
  --filters 'Name=name,Values=nixos/26.05*' 'Name=architecture,Values=arm64' \
  --query 'sort_by(Images, &CreationDate)'
```

Build a cloud disk image from a flake host (variant names: list with `nixos-rebuild build-image` with no args; amazon example from the NixOS manual):

```bash
nixos-rebuild build-image --flake .#myhost --image-variant amazon
# then: google-compute | azure — upload/register per cloud docs
```

Typical Terraform pairing (conceptual): data source or custom image → `aws_instance` / `google_compute_instance` / `azurerm_linux_virtual_machine` → optional cloud-init user-data → later [nixos-rebuild](../frontends-and-ux/nixos-rebuild.md) / deploy tools. See [Terraform + NixOS](../../12-deployment-and-infra/terraform-nixos.md).

## References

- [NixOS Download — Amazon AMIs](https://nixos.org/download/) — official AMI discovery; owner `427812963091`, name prefix `nixos/26.05*` (verified 2026-07)
- [Building Images with nixos-rebuild build-image](https://nixos.org/manual/nixos/stable/#sec-image-nixos-rebuild-build-image) — upstream image variants (`amazon`, `google-compute`, `azure`, …)
- [nix-community/nixos-generators](https://github.com/nix-community/nixos-generators) — historical multi-format builders; deprecation note toward `build-image` (NixOS ≥ 25.05)
- [Install NixOS on GCE (NixOS Wiki)](https://wiki.nixos.org/wiki/Install_NixOS_on_GCE) — build/upload/register GCE images
- [nixpkgs `create-gce.sh`](https://github.com/NixOS/nixpkgs/blob/master/nixos/maintainers/scripts/gce/create-gce.sh) — GCE image build + GCS upload helper

## See also

- [nixos-generators](nixos-generators.md)
- [Terraform + NixOS](../../12-deployment-and-infra/terraform-nixos.md)
- [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md)
