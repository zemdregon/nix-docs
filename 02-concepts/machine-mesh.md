---
status: complete
---

# Machine Mesh

## Overview

A **machine mesh** is a mental model for a *group* of Nix / NixOS devices that share builds, store closures, secrets, and deploy authority—not a single tool or a VPN brand. Members need **reachability** to each other (or to shared hubs) and an explicit **inter-trust** policy: who may build for whom, who may substitute signed binaries, who may activate generations, who may decrypt secrets, and which inputs/caches remain outside the friendly group.

That is distinct from **single-host** Nix trust. [`trusted-users`](../14-security-and-trust/trusted-users.md) is daemon privilege on one install; putting an account there does not enroll a machine in a mesh, and mesh membership does not require (or justify) `trusted-users = *`.

Fleet deploy tools such as [Colmena](../12-deployment-and-infra/colmena.md) and [deploy-rs](../12-deployment-and-infra/deploy-rs.md) usually implement a **hub → hosts** push over SSH. Peer-oriented frameworks such as [Clan](https://clan.lol/docs/26.05) aim at managing fleets of machines **without a central controller**—a different topology, still built on NixOS. Both can participate in the same interconnect story; neither is “the mesh” by itself.

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
| **Peer / no central controller** | Multi-machine management framed as peer infrastructure on NixOS (inventory, services, networking, secrets)—verify current Clan docs for capabilities. | [Clan 26.05 docs](https://clan.lol/docs/26.05) (declarative fleets without a central controller; integrates with sops-nix, nixos-anywhere, disko) |

A hub fleet still needs the same trust axes (builders, caches, secrets); peer tooling changes *who coordinates*, not whether those axes exist.

### Name collisions (not a network mesh)

- **[Digga / Hive](../13-implementations/community-frameworks/digga-hive.md)** — flake organization / std collectors for hosts and modules. Repository layout, not inter-machine interconnect.
- **Colmena “hive”** — an attrset of deployable NixOS nodes for hub deploy. Unrelated to Digga/Hive and not a host-to-host mesh.

### Six trust axes (link out)

Treat each axis separately; least privilege on one does not imply the others.

1. **Reachability** — LAN or overlay so SSH and store URIs work between members (and to builders/caches).
2. **Build trust** — [remote builders](../04-store-and-build/remote-builders.md), SSH identities, and remote daemon [`trusted-users`](../14-security-and-trust/trusted-users.md) policy.
3. **Binary trust** — who signs, who is in `trusted-public-keys` / substituters ([binary caches](../04-store-and-build/binary-caches.md), [signing and caches](../14-security-and-trust/signing-and-caches.md)).
4. **Deploy trust** — who may copy closures and activate generations on whom (Colmena / deploy-rs / remote rebuild vs peer mesh tools).
5. **Secret trust** — age/sops recipients and host identities ([agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md), [secrets management](../14-security-and-trust/secrets-management.md)).
6. **Supply-chain boundary** — flake inputs and public caches still matter inside a friendly group ([supply chain](../14-security-and-trust/supply-chain.md)).

### Anti-patterns

- Treating `trusted-users = *` (or every interactive account) as “mesh membership.”
- Equating Digga/Hive flake layout or Colmena’s hive attrset with a network mesh.
- Assuming shared VPN membership implies shared deploy, cache-signing, or secret-decrypt rights.

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

Hub tools express the deploy edge; builders and caches express build/binary edges. Peer frameworks may rearrange coordination, but the edges remain the checklist.

## References

- [Clan documentation (26.05)](https://clan.lol/docs/26.05) — declarative multi-machine management on NixOS without a central controller; peer-oriented framing; integrates sops-nix, nixos-anywhere, disko
- [Colmena docs](https://colmena.cli.rs/) — hub → hosts hive deploy (contrast topology)
- [deploy-rs](https://github.com/serokell/deploy-rs) — flake-based hub deploy with multi-profile activation

## See also

- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — six axes in depth
- [Clan and mesh](../12-deployment-and-infra/clan-and-mesh.md) — peer fleet tooling + Clan mesh VPN
- [Overlay networks](../09-nixos/configuration/overlay-networks.md) — reachability fabric (WG/Tailscale/ZeroTier)
- [Trusted users](../14-security-and-trust/trusted-users.md) — single-host daemon privilege ≠ inter-trust
- [Remote builders](../04-store-and-build/remote-builders.md) — build-trust axis
- [Binary caches](../04-store-and-build/binary-caches.md) — binary-trust axis
- [Store protocols](../04-store-and-build/store-protocols.md) — `ssh://` / store URI forms peers use
- [Colmena](../12-deployment-and-infra/colmena.md) — hub deploy; “hive” ≠ mesh
- [deploy-rs](../12-deployment-and-infra/deploy-rs.md) — hub deploy peer to Colmena
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — hub `nixos-rebuild --target-host`
- [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md) — secret-trust axis
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — binary-trust signatures
- [Secrets management](../14-security-and-trust/secrets-management.md) — secrets vs store
- [Digga / Hive](../13-implementations/community-frameworks/digga-hive.md) — flake “Hive”, not network mesh
- [Supply chain](../14-security-and-trust/supply-chain.md) — inputs/caches inside a friendly group
