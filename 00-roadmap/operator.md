---
status: complete
---

# Operator Roadmap

Path for people who run and maintain NixOS systems: rebuilds, upgrades, rollbacks, deploy, secrets, caches, and troubleshooting. Prefer operations and infra pages; pull concepts only as needed to act safely. This page is a curated reading order only — no runnable example.

## Goals

- Rebuild, test, boot, and roll back generations with a clear activation model
- Upgrade channel- or flake-pinned systems without painting yourself into a corner
- Deploy to remote hosts and keep secrets, trust, and binary caches under control
- Diagnose failed builds, activation, and substituter problems with the right CLI

## Prerequisites

- A working NixOS host (or VM) you can rebuild
- Comfort with a shell and SSH; no need to write packages or modules yet
- Optional: skim [Beginner](beginner.md) if store/flake vocabulary is new

## Reading order

### Mental model (short)

- [Generation](../02-concepts/generation.md), [Profile](../02-concepts/profile.md), [Closure](../02-concepts/closure.md), [Store Path](../02-concepts/store-path.md) — what a system generation is
- [Generations and Boot](../09-nixos/architecture/generations-and-boot.md), [Activation Script](../09-nixos/architecture/activation-script.md) — how NixOS applies a new system
- [Flake (concept)](../02-concepts/flake.md) vs [Channel](../02-concepts/channel.md); optional [Flakes vs Channels](../comparisons/flakes-vs-channels.md)
- Flake ops: [nixosConfigurations](../07-flakes/workflows/nixos-configurations.md), [lockfile](../07-flakes/anatomy/lockfile.md); channel ops: [nix-channel](../05-cli-and-tooling/classic-cli/nix-channel.md)

### Day-2 NixOS operations (core)

- Hub: [NixOS Operations](../09-nixos/operations/README.md)
- [rebuild switch / boot / test](../09-nixos/operations/rebuild-switch-boot-test.md)
- [Rollbacks](../09-nixos/operations/rollbacks.md)
- [Upgrades](../09-nixos/operations/upgrades.md)
- [Remote Deploy](../09-nixos/operations/remote-deploy.md)
- [Troubleshooting](../09-nixos/operations/troubleshooting.md)
- Frontends: [nixos-rebuild](../13-implementations/frontends-and-ux/nixos-rebuild.md), [nh](../13-implementations/frontends-and-ux/nh.md), [nh / nvd / nixos-rebuild](../05-cli-and-tooling/adjacent-tools/nh-nvd-nixos-rebuild.md)

### Config you must touch to operate

- [configuration.nix](../09-nixos/configuration/configuration-nix.md), [Imports and Profiles](../09-nixos/configuration/imports-and-profiles.md)
- [Secrets Strategies](../09-nixos/configuration/secrets-strategies.md)
- [Partitioning and Bootloaders](../09-nixos/configuration/partitioning-and-bootloaders.md) when install/disk layout bites
- Desktop hosts (optional): [NixOS Desktop](../09-nixos/desktop/README.md) — compositors, PipeWire, fonts, Flatpak/FHS, Steam, printing
- Install/bootstrap only as needed: [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md), [disko](../12-deployment-and-infra/disko.md)
- Optional deepeners: [Impermanence](../09-nixos/configuration/impermanence.md), [Secure Boot and Lanzaboote](../09-nixos/configuration/secure-boot-and-lanzaboote.md), [ZFS and Btrfs](../09-nixos/configuration/zfs-and-btrfs.md), [Specialisations](../09-nixos/configuration/specialisations.md), [Enterprise identity](../09-nixos/configuration/enterprise-identity.md), [Disko recipes](../09-nixos/configuration/disko-recipes.md), [Overlay networks](../09-nixos/configuration/overlay-networks.md), [Firmware and microcode](../09-nixos/configuration/firmware-and-microcode.md)
- Bootstrap / edge (when relevant): [Netboot and PXE](../09-nixos/installation/netboot-and-pxe.md), [Airgap and offline](../12-deployment-and-infra/airgap-and-offline.md), [nix copy and bundles](../12-deployment-and-infra/nix-copy-and-bundles.md)
- Non-NixOS clients (optional): [WSL and foreign OS](../10-home-and-user/wsl-and-foreign-os.md) — Nix on Windows/macOS/Linux alongside NixOS fleet ops

### Scenario paths (pick one track)

**Risky change on production** — read in order: [rebuild switch / boot / test](../09-nixos/operations/rebuild-switch-boot-test.md) (`test` first) → [rollbacks](../09-nixos/operations/rollbacks.md) → [troubleshooting](../09-nixos/operations/troubleshooting.md) activation vs systemd table → [FAQ: common errors](../cheatsheets/faq-common-errors.md).

**Pin bump (channel or flake)** — [upgrades](../09-nixos/operations/upgrades.md) → [flake lockfile](../07-flakes/anatomy/lockfile.md) or [channel](../02-concepts/channel.md) → [specialisations](../09-nixos/configuration/specialisations.md) if you maintain boot variants on the same host.

**Fleet / multi-host** — [remote deploy](../09-nixos/operations/remote-deploy.md) → [machine mesh](../02-concepts/machine-mesh.md) + [inter-machine trust](../14-security-and-trust/inter-machine-trust.md) → tool pick: [Colmena](../12-deployment-and-infra/colmena.md) / [deploy-rs](../12-deployment-and-infra/deploy-rs.md) / [Clan and mesh](../12-deployment-and-infra/clan-and-mesh.md) → [overlay networks](../09-nixos/configuration/overlay-networks.md) when SSH/store URIs need VPN.

**Disconnected or lab site** — [airgap and offline](../12-deployment-and-infra/airgap-and-offline.md) → [nix copy and bundles](../12-deployment-and-infra/nix-copy-and-bundles.md) → [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) → [netboot and PXE](../09-nixos/installation/netboot-and-pxe.md) for LAN imaging.

**Desktop laptop ops** — [networking](../09-nixos/configuration/networking.md) → [NixOS Desktop](../09-nixos/desktop/README.md) → [secrets strategies](../09-nixos/configuration/secrets-strategies.md) for Wi‑Fi PSKs.

### Virtualization and guests (optional)

- Hub: [NixOS Services](../09-nixos/services/README.md)
- [Libvirt and VMs](../09-nixos/services/libvirt-and-vms.md), [MicroVMs](../09-nixos/services/microvms.md)
- Containers: [Containers and nspawn](../09-nixos/services/containers-and-nspawn.md), [Declarative containers](../09-nixos/services/declarative-containers.md)
- Mental model vs orchestrators: [Nix vs containers / orchestrators](../comparisons/nix-vs-containers-orchestrators.md)

### CLI and daemon config

- Hub: [CLI and Tooling](../05-cli-and-tooling/README.md)
- Daily: [nix flake](../05-cli-and-tooling/modern-cli/nix-flake.md), [nix store ops](../05-cli-and-tooling/modern-cli/nix-store-ops.md), [nix-store](../05-cli-and-tooling/classic-cli/nix-store.md), [nix-collect-garbage](../05-cli-and-tooling/classic-cli/nix-collect-garbage.md)
- Daemon: [nix.conf](../05-cli-and-tooling/config/nix-conf.md), [Trusted Users and Substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md)
- Quick lookup: [CLI cheatsheet](../cheatsheets/cli.md); optional [nix.conf knobs](../cheatsheets/nix-conf-knobs.md); symptom table: [FAQ: common errors](../cheatsheets/faq-common-errors.md)

### Store, caches, and GC

- Hub: [Store and Build](../04-store-and-build/README.md)
- [Binary Caches](../04-store-and-build/binary-caches.md), [Substitutes and narinfo](../04-store-and-build/substitutes-and-narinfo.md)
- [Garbage Collection](../04-store-and-build/garbage-collection.md), [Remote Builders](../04-store-and-build/remote-builders.md)
- Hosting your own: [Binary Cache Hosting](../12-deployment-and-infra/binary-cache-hosting.md)

### Deploy and infra

- Hub: [Deployment and Infra](../12-deployment-and-infra/README.md)
- Tools: [Colmena](../12-deployment-and-infra/colmena.md), [deploy-rs](../12-deployment-and-infra/deploy-rs.md), [Morph / Nixinate](../12-deployment-and-infra/morph-nixinate.md)
- Optional: [Terraform + NixOS](../12-deployment-and-infra/terraform-nixos.md), [Hydra](../12-deployment-and-infra/hydra.md)
- Optional deepeners: [Airgap and offline](../12-deployment-and-infra/airgap-and-offline.md), [nix copy and bundles](../12-deployment-and-infra/nix-copy-and-bundles.md), [Clan and mesh](../12-deployment-and-infra/clan-and-mesh.md)
- Secrets on the wire: [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md)

### Security and trust

- Hub: [Security and Trust](../14-security-and-trust/README.md)
- [Trusted Users](../14-security-and-trust/trusted-users.md), [Signing and Caches](../14-security-and-trust/signing-and-caches.md)
- [Secrets Management](../14-security-and-trust/secrets-management.md), [Supply Chain](../14-security-and-trust/supply-chain.md)
- Mesh / interconnect (concept): [Machine mesh](../02-concepts/machine-mesh.md), [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md)
- Optional deepeners: [SSH and age plugins](../14-security-and-trust/ssh-and-age-plugins.md), [AppArmor and SELinux](../14-security-and-trust/apparmor-selinux.md), [Reproducible builds audit](../14-security-and-trust/reproducible-builds-audit.md)

## Next steps

- Keep [NixOS Operations](../09-nixos/operations/README.md) and [CLI cheatsheet](../cheatsheets/cli.md) bookmarked while you run systems
- Stuck on a message: [FAQ: common errors](../cheatsheets/faq-common-errors.md) before deep-diving every leaf
- Developers on Windows/WSL in the same org: [WSL and foreign OS](../10-home-and-user/wsl-and-foreign-os.md) (client Nix) plus this roadmap (NixOS servers)
- When you need to change packages or modules upstream, switch to [Contributor](contributor.md)
- Glossary fallback: [glossary.md](../glossary.md)

## See also

- [Learning roadmaps](README.md) — path chooser
- [Beginner](beginner.md) — first-pass philosophy, concepts, and a working system
- [Contributor](contributor.md) — packaging and module authorship
- [Security and Trust](../14-security-and-trust/README.md) — daemon trust, signing, secrets, inter-trust
- [Machine mesh](../02-concepts/machine-mesh.md) — multi-machine reachability / build / deploy axes
- [Airgap and offline](../12-deployment-and-infra/airgap-and-offline.md) · [Netboot and PXE](../09-nixos/installation/netboot-and-pxe.md) · [Specialisations](../09-nixos/configuration/specialisations.md)
