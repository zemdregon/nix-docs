---
status: complete
---

# Terraform + NixOS

## Overview

[Terraform](https://www.terraform.io/) and [OpenTofu](https://opentofu.org/) provision cloud resources (VMs, networks, disks, firewall rules). NixOS owns the **system closure**—what runs on those machines after boot. The useful pattern is a clean split: IaC creates reachable hosts; Nix builds and activates configurations separately (or via a thin Terraform module that shells out to Nix tools).

Common bridges: prebuilt NixOS images ([nixos-generators](../13-implementations/cloud-and-images/nixos-generators.md), official cloud images), first-boot via cloud-init, or SSH install/redeploy with [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md). Ongoing updates often leave Terraform and use [Colmena](colmena.md), [deploy-rs](deploy-rs.md), or `nixos-rebuild --target-host`.

## Details

### Separation of concerns

| Layer | Tooling | Responsibility |
|-------|---------|----------------|
| Infrastructure | Terraform / OpenTofu providers (AWS, GCP, Hetzner, …) | Instances, IPs, security groups, load balancers |
| Bootstrap / image | Official AMIs/images, nixos-generators, cloud-init, nixos-anywhere | Get a NixOS system (or installer) onto the host |
| System config | Flake `nixosConfigurations`, deploy tools, or Terraform modules that invoke Nix | Build, copy, and activate the closure |

Terraform state tracks infra objects. The Nix store and NixOS generation history track the OS. Crossing those boundaries without a clear handoff (e.g. baking every package change into a new AMI) usually costs more than it buys.

### Integration patterns

**1. Image then configure.** Build or reuse a NixOS AMI/GCE/Azure image ([cloud images](../13-implementations/cloud-and-images/amazon-gce-azure.md), [nixos-generators](../13-implementations/cloud-and-images/nixos-generators.md)). Terraform launches VMs from that image. First boot may apply cloud-init; later changes go through SSH deploy tools.

**2. Generic VM + nixos-anywhere.** Terraform creates a throwaway Linux (or installer) host. [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) kexecs, partitions (often with disko), and installs a flake system. The nixos-anywhere repo ships Terraform/OpenTofu modules (`install`, `nixos-rebuild`, `all-in-one`, helpers) that wrap those steps behind `null`/`external` providers—not a proprietary “NixOS cloud API.”

**3. Historical terraform-nixos modules.** [nix-community/terraform-nixos](https://github.com/nix-community/terraform-nixos) collected modules such as `deploy_nixos` (evaluate a NixOS config and activate over SSH) and GCE image helpers. Treat this as a pattern archive and check current maintenance before adopting; many workflows have moved to nixos-anywhere modules or out-of-band deploy tools.

**4. Third-party providers.** Registry providers that claim to manage NixOS over SSH exist and evolve independently. Prefer documented nix-community / nixos-anywhere modules over inventing resource types; do not assume a stable official HashiCorp “NixOS provider.”

### What Terraform should (and should not) own

- **Own:** instance size, VPC/subnet, floating IPs, DNS records, which image ID boots, SSH key material for bootstrap.
- **Hand off:** package set, services, users, firewall inside NixOS, secrets via NixOS-oriented tools—activated as a system closure, not as ad-hoc remote-exec package installs.
- **Optional glue:** write a small JSON/vars file from Terraform into the repo (or pass `specialArgs`-style data through nixos-anywhere modules) so the flake can read infra-assigned IPs/hostnames without duplicating truth.

## Examples

Illustrative flow only (providers and resource schemas differ by cloud; do not copy as a complete module):

```text
1. terraform apply          → VM + public IP + SSH access
2. nixos-anywhere / image   → NixOS system on that host
3. deploy-rs / colmena /    → later config changes without
   nixos-rebuild            → re-provisioning the VM
```

Conceptual module wiring when using nixos-anywhere’s Terraform modules (see upstream `terraform/` docs for real inputs):

```hcl
# After the cloud provider resource exposes an address:
# module "nixos" {
#   source            = "github.com/nix-community/nixos-anywhere//terraform/all-in-one"
#   target_host       = <instance_ip>
#   nixos_system_attr = ".#nixosConfigurations.host.config.system.build.toplevel"
#   # … partitioner attr, instance_id, etc. per upstream README
# }
```

OpenTofu uses the same module sources and provider plugins in typical setups; pin module `ref`s the same way you pin flakes.

## References

- [nix-community/nixos-anywhere](https://github.com/nix-community/nixos-anywhere) — install over SSH; [Terraform howto](https://github.com/nix-community/nixos-anywhere/blob/main/docs/howtos/terraform.md) and [terraform modules](https://github.com/nix-community/nixos-anywhere/tree/main/terraform) (verified 2026-07)
- [nix-community/nixos-generators](https://github.com/nix-community/nixos-generators) — build cloud/VM images for Terraform to launch (deprecated in favor of `nixos-rebuild build-image` on NixOS ≥ 25.05)
- [nix-community/terraform-nixos](https://github.com/nix-community/terraform-nixos) — historical Terraform modules (`deploy_nixos`, GCE image helpers); check maintenance before adopting
- [NixOS Download — Amazon AMIs](https://nixos.org/download/) — resolve official EC2 AMIs for Terraform data sources (26.05 as of 2026-07)

## See also

- [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md)
- [nixos-generators](../13-implementations/cloud-and-images/nixos-generators.md)
- [Amazon / GCE / Azure images](../13-implementations/cloud-and-images/amazon-gce-azure.md)
- [Colmena](colmena.md)
- [deploy-rs](deploy-rs.md)
