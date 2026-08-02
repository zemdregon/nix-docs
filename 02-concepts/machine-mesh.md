---
status: complete
---

# Machine Mesh

## Overview

A **machine mesh** is a mental model for a *group* of Nix / NixOS devices that share builds, store closures, secrets, and deploy authority—not a single tool or a VPN brand. Members need **reachability** to each other (or to shared hubs) and an explicit **inter-trust** policy: who may build for whom, who may substitute signed binaries, who may activate generations, who may decrypt secrets, and which inputs/caches remain outside the friendly group.

That is distinct from **single-host** Nix trust. [`trusted-users`](../14-security-and-trust/trusted-users.md) is daemon privilege on one install; putting an account there does not enroll a machine in a mesh, and mesh membership does not require (or justify) `trusted-users = *`.

Fleet deploy tools such as [Colmena](../12-deployment-and-infra/colmena.md) and [deploy-rs](../12-deployment-and-infra/deploy-rs.md) usually implement a **hub → hosts** push over SSH. Peer-oriented frameworks such as [Clan](../12-deployment-and-infra/clan-and-mesh.md) aim at managing fleets of machines **without a central controller**—a different topology, still built on NixOS ([Clan docs 26.05](https://clan.lol/docs/26.05)). Either pattern can share the same builders, caches, and secret recipients; what changes is the **deploy graph** (who evaluates and activates on whom), not whether build, binary, and secret trust edges exist.

**Last checked:** 2026-07-31 — vocabulary / topology only; Clan API and inventory options live on [Clan and mesh](../12-deployment-and-infra/clan-and-mesh.md).

## Details

### What “mesh” means here

In this wiki, “machine mesh” means **interconnected Nix devices plus the trust edges between them**. Typical shared concerns:

- Distributed or remote builds and shared [closures](closure.md)
- Private or peer [binary caches](../04-store-and-build/binary-caches.md)
- Host-scoped secrets (age / sops recipients)
- Who may deploy or activate system generations

It is **not** a synonym for overlay networking alone, and it is **not** a flake layout name.

### Hub deploy vs peer mesh tooling

| Pattern | Shape | Examples in this wiki |
|---------|--------|------------------------|
| **Hub → hosts** | One deployer evaluates, builds/copies, activates on SSH targets. Hosts do not form a control plane among themselves. | [Colmena](../12-deployment-and-infra/colmena.md), [deploy-rs](../12-deployment-and-infra/deploy-rs.md), [remote deploy](../09-nixos/operations/remote-deploy.md) |
| **Peer / no central controller** | Multi-machine management framed as peer infrastructure on NixOS (inventory, services, networking, secrets)—verify current Clan docs for capabilities. | [Clan and mesh](../12-deployment-and-infra/clan-and-mesh.md) / [Clan 26.05 docs](https://clan.lol/docs/26.05) (declarative fleets without a central controller; integrates with sops-nix, nixos-anywhere, disko) |

Hub fleets and peer tooling differ in *who coordinates*; both still need explicit policy on builders, caches, secrets, and deploy authority.

### Name collisions (not a network mesh)

- **[Digga / Hive](../13-implementations/community-frameworks/digga-hive.md)** — flake organization / std collectors for hosts and modules. Repository layout, not a deploy graph or trust topology.
- **Colmena “hive”** — an attrset of deployable NixOS nodes for hub deploy. Unrelated to Digga/Hive and not a host-to-host mesh.

### Six trust axes (link out)

Treat each axis separately; least privilege on one does not imply the others.

**Reachability** comes first: LAN or overlay paths so SSH and store URIs work between members and to builders/caches.

For **build trust**, see [remote builders](../04-store-and-build/remote-builders.md), SSH identities, and remote daemon [`trusted-users`](../14-security-and-trust/trusted-users.md) policy.

**Binary trust** covers who signs artifacts and who lists which keys in `trusted-public-keys` / substituters ([binary caches](../04-store-and-build/binary-caches.md), [signing and caches](../14-security-and-trust/signing-and-caches.md)).

**Deploy trust** is who may copy closures and activate generations on whom—hub tools (Colmena, deploy-rs, remote rebuild) versus peer mesh coordinators.

Host-scoped **secret trust** means age/sops recipients and host identities ([agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md), [secrets management](../14-security-and-trust/secrets-management.md)).

Even inside a friendly group, **supply-chain boundaries** still apply: flake inputs and public caches remain part of the threat model ([supply chain](../14-security-and-trust/supply-chain.md)).

### Anti-patterns

- Treating `trusted-users = *` (or every interactive account) as “mesh membership.”
- Equating Digga/Hive flake layout or Colmena’s hive attrset with a network mesh.
- Assuming shared VPN membership implies shared deploy, cache-signing, or secret-decrypt rights.

This page maps topology and the six axes above. Policy detail (SSH keys, substituters, signing) lives on [inter-machine trust](../14-security-and-trust/inter-machine-trust.md); tool walkthroughs on [Clan and mesh](../12-deployment-and-infra/clan-and-mesh.md), [Colmena](../12-deployment-and-infra/colmena.md), and [deploy-rs](../12-deployment-and-infra/deploy-rs.md); reachability without deploy rights on [overlay networks](../09-nixos/configuration/overlay-networks.md).

## Examples

Conceptual sketch only—no Clan CLI or options invented here. A small mesh might look like:

```text
laptop ──SSH/VPN──► builder-a     (build trust: remote builder)
   │                      │
   │                 signed NARs
   ▼                      ▼
server-1 ◄── cache ◄── builder-a   (binary trust: shared substituter keys)
server-2
   ▲
   └── deploy from laptop          (deploy trust: hub → hosts)
        secrets: age recipients
        = host identities          (secret trust)
```

Hub tools express the deploy edge; builders and caches express build/binary edges. Peer frameworks may rearrange coordination, but the same trust edges still apply.

## References

- [Clan documentation (26.05)](https://clan.lol/docs/26.05) — declarative multi-machine management on NixOS without a central controller; peer-oriented framing; integrates sops-nix, nixos-anywhere, disko (last checked 2026-07-31)
- [Colmena docs](https://colmena.cli.rs/) — hub → hosts hive deploy (contrast topology)
- [deploy-rs](https://github.com/serokell/deploy-rs) — flake-based hub deploy with multi-profile activation

## See also

- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — six axes in depth
- [Private cache mesh](../12-deployment-and-infra/private-cache-mesh.md) — fleet substituter topology
- [Store protocols](../04-store-and-build/store-protocols.md) — `ssh://` / store URI forms peers use
- [Overlay networks](../09-nixos/configuration/overlay-networks.md) — reachability fabric (WG/Tailscale/ZeroTier)
- [Closure](closure.md) — store paths members share and substitute
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — hub `nixos-rebuild --target-host`
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — binary-trust signatures
