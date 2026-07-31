---
status: complete
---

# Clan and mesh

## Overview

**Clan** ([clan.lol](https://clan.lol/), library **clan-core**) is a declarative, peer-oriented framework for managing fleets of [NixOS](../09-nixos/README.md) machines. Upstream positions it as multi-machine management **without a central controller**: inventory-driven services, first-class networking/backups/resources, and integrations with [sops-nix](agenix-sops-nix.md), [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md), and [disko](disko.md) for secrets and provisioning ([Clan docs 26.05](https://clan.lol/docs/26.05)).

**Maturity / last checked:** 2026-07-31 — production-oriented peer fleet tooling; inventory/CLI/options still churn across doc channels. Prefer versioned docs over blogs; re-check options before copying.

That is a different job from hub-style deploy tools:

| Tool | Role |
|------|------|
| [Colmena](colmena.md) / [deploy-rs](deploy-rs.md) | **Hub → hosts**: a deployer evaluates configs, copies closures over SSH, activates. No host-to-host overlay. |
| Bare [remote deploy](../09-nixos/operations/remote-deploy.md) | Same push model for one (or few) hosts via `nixos-rebuild --target-host`. |
| **Clan** | **Fleet + reachability**: inventory of machines and service instances; CLI (`clan machines update`, `clan ssh`) uses declared networking with automatic fallback; optional mesh VPN so peers can reach each other. |

Clan’s “mesh” is an overlay/VPN and connection policy among inventory machines—not Colmena’s “hive” attrset, and not [Digga / Hive](../13-implementations/community-frameworks/digga-hive.md) (divnix flake layout / collectors). See [Name clashes](#name-clashes-hive-vs-mesh) below.

Docs are versioned like NixOS releases. Prefer **[26.05](https://clan.lol/docs/26.05)** for stable citations (verified 2026-07-31: mesh-vpn, networking, zerotier service, quick-start all live). A **[26.11](https://clan.lol/docs/26.11)** URL tree also responds, but deep guide paths were incomplete relative to 26.05 at last check—do not migrate citations until the guide set matches. **[unstable](https://clan.lol/docs/unstable)** tracks newer networking services and priorities (`wireguard`, `p2p-ssh-iroh`, …)—confirm the path you follow before copying options.

## Details

### Inventory and clan-core

A Clan project is typically a flake that calls `clan-core.lib.clan` (often with a `clan.nix` attrset). Machines live under `inventory.machines`; reusable multi-host services under `inventory.instances` with **roles** and **tags**. The library produces `nixosConfigurations` (and related outputs) for ordinary NixOS evaluation.

Day-to-day ops use the Clan CLI rather than Colmena/`deploy` alone—for example `clan machines update` / `clan machines update <name>` to build and activate, and `clan ssh <name>` to open a session. Fresh installs go through Clan’s install/hardware/disk template flow (wrapping nixos-anywhere- and disko-style steps); see [Quick Start (Physical Machine) — 26.05](https://clan.lol/docs/26.05/getting-started/quick-start/). Exact inventory keys and CLI flags evolve—use the versioned options/reference, not memory.

Secrets: Clan integrates **sops-nix** (and age-key prompts in init/quick-start). Prefer [agenix / sops-nix](agenix-sops-nix.md) for the underlying model; treat Clan as the fleet wiring, not a separate crypto stack.

### Mesh VPN (ZeroTier via inventory roles)

**Doc stamp:** [Mesh VPN — docs 26.05](https://clan.lol/docs/26.05/guides/networking/mesh-vpn/); roles also listed in [zerotier service — 26.05](https://clan.lol/docs/26.05/services/official/zerotier).

By default, machines in one Clan are expected to share a chosen network technology (ZeroTier, Mycelium, …). The 26.05 guide configures **ZeroTier** through inventory:

- One machine gets role **`controller`** — signs/admits new member IDs; continuous uptime is not required after peers are admitted, but a reachable controller helps add new peers.
- Other machines get role **`peer`** (often via a tag such as `all`).
- Optional role **`moon`** — relay with `stableEndpoints` (public IPs) for peers behind NAT; see the zerotier service page (not required for the minimal mesh-vpn walkthrough).

Update the controller first (`clan machines update controller`), then peers (`clan machines update`). Verify with `zerotier-cli info` (expect `ONLINE`). Vars such as ZeroTier network/identity material are listed with `clan vars list <machine>` (see the same guide for debugging and manual `zerotier-members allow`).

Upstream note (26.05 mesh-vpn): ZeroTier is the mesh-VPN fully integrated into Clan’s networking story; Mycelium/Yggdrasil may appear via inventory but are not fully integrated into the networking module the same way. Unstable’s networking priority table also lists first-class `wireguard` and experimental `p2p-ssh-iroh`—cite that channel when using them; do not invent Tailscale/tinc inventory options from this wiki.

### Networking fallback (how Clan reaches hosts)

**Doc stamp:** [Networking — docs 26.05](https://clan.lol/docs/26.05/guides/networking/networking/). (Unstable expands service priorities; see [Networking — unstable](https://clan.lol/docs/unstable/guides/networking/networking/) if you follow tip.)

Clan needs a path for `clan machines update` and `clan ssh`. Prefer declaring **networking service instances** so Clan tries connections in priority order until one works (e.g. direct `internet` SSH, then VPN, then Tor). Setting inventory `deploy.targetHost` or `clan.core.networking.targetHost` **bypasses** that automatic fallback—use for static/debug cases only. Emergency override: `--target-host` on the CLI.

High-level 26.05 ordering: direct internet → VPN overlays → Tor → other configured networks. For numbered priorities (unstable, highest first: `p2p-ssh-iroh` 3000, `internet` 2000, `wireguard` 1000, `zerotier` 900, `mycelium` 800, `tor` 10), cite the **unstable** networking page and re-check before relying on them.

### Contrast: hub deploy vs peer fleet

- **Colmena / deploy-rs / remote rebuild** assume you already have SSH (or equivalent) to each target from the deployer. They push store paths; they do not define how hosts talk to each other afterward.
- **Clan** still deploys over SSH-like paths, but the **inventory + networking modules** are first-class: mesh VPN for peer reachability, fallback stacks for admin reachability, and shared services applied by role/tag.
- Inter-machine trust on the overlay (who may join ZeroTier, SSH auth after join, secret recipients) is operational policy—see [Machine mesh](../02-concepts/machine-mesh.md) and [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md); also [Secrets management](../14-security-and-trust/secrets-management.md) and [agenix / sops-nix](agenix-sops-nix.md) for secret distribution.

### Name clashes: Hive vs mesh

| Name | What it is |
|------|------------|
| Colmena **hive** | Attrset of deployable NixOS nodes for hub deploy. |
| Digga / **Hive** | divnix flake organization / collectors ([digga-hive](../13-implementations/community-frameworks/digga-hive.md)). |
| Clan **mesh** | Overlay/VPN and multi-path networking among Clan inventory machines. |

Do not equate “Hive” with Clan mesh, or Colmena tagging with Clan inventory tags—similar words, different systems.

## Examples

Minimal ZeroTier mesh sketch from upstream **docs 26.05** (illustrative; fill `meta` and follow current `clan-core` flake URL for your pin):

```nix
# flake.nix — structure from https://clan.lol/docs/26.05/guides/networking/mesh-vpn/
{
  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";

  outputs =
    { self, clan-core, ... }:
    let
      clan = clan-core.lib.clan {
        inherit self;
        meta.name = "myclan";
        meta.domain = "ccc";

        inventory.machines = {
          controller = { };
          new_machine = { };
        };

        inventory.instances = {
          zerotier = {
            roles.controller.machines."controller" = { };
            roles.peer.tags."all" = { };
          };
        };
      };
    in
    {
      inherit (clan) nixosConfigurations nixosModules clanInternals;
    };
}
```

Then (after machines exist and are reachable):

```bash
clan machines update controller
clan machines update
```

Pair with an `internet` (or other) networking instance so the admin path to the controller stays defined—see the 26.05 networking guide. Do not copy options from blogs without checking [Clan options](https://clan.lol/docs/26.05/) for your doc version.

## See also

- [Colmena](colmena.md) — hub → hosts hive deploy
- [deploy-rs](deploy-rs.md) — flake multi-profile hub deploy
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — `nixos-rebuild --target-host`
- [Morph / Nixinate](morph-nixinate.md) — other thin remote-deploy wrappers
- [disko](disko.md) — declarative disks (Clan install templates)
- [agenix / sops-nix](agenix-sops-nix.md) — secrets Clan wires via sops-nix
- [Digga / Hive](../13-implementations/community-frameworks/digga-hive.md) — name clash; not Clan mesh
- [Machine mesh](../02-concepts/machine-mesh.md) — interconnect / inter-trust mental model
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — six trust axes across a fleet/mesh
- [Overlay networks](../09-nixos/configuration/overlay-networks.md) — VPN/overlay as reachability fabric

## References

- [Clan documentation (26.05)](https://clan.lol/docs/26.05) — prefer this stamp for stable claims (last checked 2026-07-31)
- [Clan documentation (unstable)](https://clan.lol/docs/unstable) — tip; networking service priorities expand here
- [Mesh VPN (ZeroTier inventory roles) — 26.05](https://clan.lol/docs/26.05/guides/networking/mesh-vpn/)
- [zerotier service (controller / peer / moon) — 26.05](https://clan.lol/docs/26.05/services/official/zerotier)
- [Networking / fallback — 26.05](https://clan.lol/docs/26.05/guides/networking/networking/)
- [Networking / fallback — unstable](https://clan.lol/docs/unstable/guides/networking/networking/) — numbered priority table (`wireguard`, `p2p-ssh-iroh`, …)
- [Quick Start (Physical Machine) — 26.05](https://clan.lol/docs/26.05/getting-started/quick-start/)
- [clan-core on Gitea](https://git.clan.lol/clan/clan-core) — source / releases
- [Clan site](https://clan.lol/) — project entry
