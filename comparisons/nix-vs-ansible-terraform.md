---
status: complete
---

# Nix vs Ansible / Terraform

## Overview

**Ansible** is a **config-management** tool: playbooks and roles describe desired host state, but agents apply it by **converging over SSH**—modules run commands, edit files, restart services, and install packages until checks pass. The live machine accumulates those mutations; drift is reconciled on the next run, not replaced as a single atomic system image.

**Terraform** (and OpenTofu) is **declarative infrastructure-as-code** for **cloud and provider APIs**: you declare resources (VMs, networks, DNS, buckets); the engine computes a plan from configuration plus a **state file**, then creates or updates remote objects. **Provisioners** and remote-exec are an escape hatch for one-off imperative steps—they are not the primary model.

**Nix / NixOS** is **declarative system configuration** evaluated into a **store closure**: [configuration.nix](../09-nixos/configuration/configuration-nix.md) and the module system describe packages, users, services, and settings; `nixos-rebuild` builds and **activates** that closure. Changes become new [generations](../02-concepts/generation.md) with rollback, not a transcript of remote package installs.

These tools sit at different layers. Terraform owns **cloud resources**; NixOS owns the **guest OS** once a host exists; Ansible still fits where you manage non-NixOS fleets or glue around legacy stacks. Deep dive on the Terraform + NixOS split: [Terraform + NixOS](../12-deployment-and-infra/terraform-nixos.md).

## Details

**Who owns what.**

| Layer | Typical owner | Source of truth | How change applies |
|-------|---------------|-----------------|-------------------|
| Cloud infra (VMs, VPC, LB, DNS) | Terraform / OpenTofu | `.tf` + provider **state** | `terraform apply` → API calls |
| Guest OS (packages, `/etc`, services) | NixOS | Flake / `configuration.nix` → **store closure** | Build + `switch` / deploy tool → **activation** |
| Non-Nix hosts or mixed fleets | Ansible (or similar) | Playbooks / inventory | SSH modules → **converge** host by host |

**Declarative vs imperative.** All three can be “declarative” in the sense of checked-in config, but the **realization model** differs. Terraform’s declaration targets **provider objects** tracked in state. NixOS’s declaration targets a **system closure** realized atomically on switch (see [Declarative vs imperative](../01-philosophy/declarative-vs-imperative.md)). Ansible declares tasks, but execution is **imperative convergence**: each module mutates what is already on the box until idempotent checks succeed—closer to replaying installs than swapping generations.

**State vs store.** Terraform **state** maps resource addresses to cloud IDs so plans stay accurate when configs change. Nix does not use a Terraform-style state file for packages: the **Nix store** and `/nix/var/nix/profiles` (plus NixOS generation links) record what was built and what is active. Garbage collection and rollback use that history, not a separate IaC state backend.

**SSH overlap.** Ansible’s default transport is SSH mutation. NixOS remote updates also use SSH—but to **copy closures and activate**, not to `apt install` piecemeal: [Remote deploy](../09-nixos/operations/remote-deploy.md), [Colmena](../12-deployment-and-infra/colmena.md), deploy-rs, and nixos-anywhere follow that pattern. Using Terraform **provisioners** to apt-install on every apply fights both Terraform’s model (infra lifecycle) and Nix’s (OS as a closed configuration).

**Complementary stack.** A common split: Terraform provisions reachable machines; a flake defines `nixosConfigurations`; ongoing OS changes leave Terraform and go through Colmena, deploy-rs, or `nixos-rebuild --target-host`. Ansible remains reasonable for **non-NixOS** nodes, brownfield migration, or teams that have not adopted NixOS on every host—it is not made obsolete by Nix, but it does not replace NixOS’s closure-based OS model where NixOS is in use.

**What each is not.** NixOS is not a cloud API provisioner: it does not replace Terraform for VPCs, IAM, or autoscaling groups. Terraform is not an OS package manager: baking every config change into a new AMI or re-running shell provisioners scales poorly compared to activating a NixOS generation. Ansible is not a substitute for the Nix store on NixOS: playbooks that fight the module system recreate imperative drift NixOS is designed to avoid.

## Examples

**Mental model — responsibility boundaries:**

| Question | Reach for |
|----------|-----------|
| “Create a Hetzner server and attach a floating IP?” | Terraform |
| “This NixOS host should run PostgreSQL 16 and these firewall rules?” | NixOS (`configuration.nix` / flake) |
| “These Ubuntu boxes need nginx and a vhost; we are not on NixOS yet.” | Ansible |
| “Re-deploy OS config to ten NixOS machines after merge?” | Colmena / deploy-rs / `nixos-rebuild --target-host` |

**Typical handoff** (same spirit as [Terraform + NixOS](../12-deployment-and-infra/terraform-nixos.md)):

```text
1. terraform apply     → VM, network, SSH access, maybe image ID
2. nixos-anywhere /    → install or first NixOS closure on that host
   cloud image
3. colmena / deploy-rs → later OS changes without reprovisioning the VM
   / nixos-rebuild
```

## References

- [Terraform documentation — What is Terraform?](https://developer.hashicorp.com/terraform/intro) — declarative IaC, providers, state, and plan/apply
- [NixOS manual — Configuration options](https://nixos.org/manual/nixos/stable/options) — declarative OS settings evaluated by the module system
- [NixOS manual — Module system](https://nixos.org/manual/nixos/stable/index.html#ch-module-system) — how `configuration.nix` and imports compose a system closure

## See also

- [Terraform + NixOS](../12-deployment-and-infra/terraform-nixos.md) — integration patterns in this wiki
- [Declarative vs imperative](../01-philosophy/declarative-vs-imperative.md) — source of truth and activation vs mutation
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — `nixos-rebuild` over SSH
- [Colmena](../12-deployment-and-infra/colmena.md) — fleet deploy after infra exists
- [configuration.nix](../09-nixos/configuration/configuration-nix.md) — primary NixOS system declaration
