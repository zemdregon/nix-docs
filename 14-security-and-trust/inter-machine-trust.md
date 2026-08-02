---
status: complete
---

# Inter-Machine Trust

## Overview

A single Nix install has a clear local trust story: [trusted users](trusted-users.md) vs the daemon, [signatures](signing-and-caches.md) for substitutes, and [sandbox](sandbox-escape-surface.md) hermeticity. A **group of machines** that share builds, closures, secrets, and deploy authority needs more than one daemon setting. Inter-machine trust is the product of several **independent axes**—reachability, build privilege, binary authenticity, who may activate generations, who may decrypt secrets, and the still-present supply chain. Sharing a VPN or a Colmena hive does not collapse those axes into one “we trust each other” switch.

Short mental model: [Machine mesh](../02-concepts/machine-mesh.md). This page is the deep dive: how the axes compose, what each leaf already covers, and common false equivalences.

## Details

### Six axes (compose; do not conflate)

| Axis | Question | Where detail lives |
|------|----------|-------------------|
| **1. Reachability** | Can SSH / store URIs reach the peer? | Overlay, VPN, or LAN under the hosts you choose; store URI forms in [Store protocols](../04-store-and-build/store-protocols.md) |
| **2. Build trust** | May this host run builds for that one? | [Remote builders](../04-store-and-build/remote-builders.md): SSH keys + remote `trusted-users` |
| **3. Binary trust** | Whose signed NAR infos may enter the store? | [Signing and caches](signing-and-caches.md), [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md), [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) |
| **4. Deploy trust** | Who may activate a new generation on whom? | Hub tools: [remote deploy](../09-nixos/operations/remote-deploy.md), [Colmena](../12-deployment-and-infra/colmena.md), [deploy-rs](../12-deployment-and-infra/deploy-rs.md)—vs peer-oriented frameworks (contrast only) |
| **5. Secret trust** | Which host identities may decrypt which ciphertext? | [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md), [Secrets management](secrets-management.md) |
| **6. Supply chain** | Which inputs and caches are still in the TCB inside a friendly mesh? | [Supply chain](supply-chain.md) |

Granting one axis never implies the others. A laptop on the same WireGuard net as a builder can still lack remote-builder trust; a signed private cache does not authorize `colmena apply`; encrypting secrets for host A does not let host B activate A’s generation.

### 1. Reachability

Builders, `nix copy`, remote rebuild, and private HTTP caches all need a path: LAN, Tailscale/Headscale, WireGuard, or another overlay. Nix does not invent that fabric; it consumes hostnames and [store URIs](../04-store-and-build/store-protocols.md) (`ssh://…`, `https://…`, experimental `ssh-ng://…`). Failures here look like SSH timeouts or unreachable substituters—not signature errors.

Reachability is **necessary but not sufficient**. Putting every node on one overlay is membership of a network, not membership of `trusted-users`, not acceptance of a cache key, and not deploy authority.

### 2. Build trust

[Distributed builds](../04-store-and-build/remote-builders.md) forward derivations over SSH. The remote must run Nix, accept the client’s SSH key for a non-interactive user, and list that SSH user in **remote** `trusted-users` (see [`nix.conf`](../05-cli-and-tooling/config/nix-conf.md)). The local side lists builders (`builders` / `--builders` / `@/etc/nix/machines`).

That remote `trusted-users` entry is **daemon privilege on the builder**, scoped to “this SSH identity may drive privileged store operations there.” It is not fleet-wide mesh membership and should stay least-privilege (named builder accounts, not `*`). See [Trusted users](trusted-users.md).

### 3. Binary trust

Paths that arrive via substituters are trusted through **signatures and key lists**, not because the peer is “on the mesh.” Clients need matching `substituters` / `trusted-substituters` and `trusted-public-keys` (and usually `require-sigs = true`). Who may change those settings on a multi-user install is again local [trusted users](trusted-users.md) policy—orthogonal to whether the cache host is a VPN peer. Operational split: secret signing keys on writers; public keys on consumers—[Signing and caches](signing-and-caches.md), [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md).

### 4. Deploy trust

**Hub → hosts** tools evaluate somewhere with credentials, then SSH to targets and activate: `nixos-rebuild --target-host`, [Colmena](../12-deployment-and-infra/colmena.md), [deploy-rs](../12-deployment-and-infra/deploy-rs.md). Topology is deployer-centric. Hosts do not form a Colmena or deploy-rs control plane among themselves.

**Peer / inventory-oriented** frameworks (for contrast: [Clan 26.05](https://clan.lol/docs/26.05) describes declarative fleet management without a central controller, peer-oriented NixOS ops, and networking/secrets integrations) are a different deploy-trust shape. Do not assume Clan APIs here; treat upstream docs as the authority if you adopt that stack. Either way, **who holds SSH/deploy keys** (or peer identities) is the activation trust boundary—separate from builder and cache trust.

### 5. Secret trust

[agenix](../12-deployment-and-infra/agenix-sops-nix.md) and [sops-nix](../12-deployment-and-infra/agenix-sops-nix.md) encrypt for **recipients** (typically host SSH or age keys). Only machines whose private identities match can decrypt at activation. Being able to reach a host, build for it, or substitute its closures does not decrypt its secrets. Recipient lists are the secret-trust ACL; rotate them when hosts join or leave. Broader store rules: [Secrets management](secrets-management.md).

### 6. Supply chain (still inside a friendly mesh)

A closed overlay does not pin flake inputs or vouch for cache operators. Locked `flake.lock` revisions, FODs, overlays, and which public keys you accept remain in the TCB—see [Supply chain](supply-chain.md). “Only our machines can talk” is not “only reviewed source and only our signing keys.” Compromised `github:` inputs or an over-trusted substituter key still matter on every node that evaluates or substitutes.

### Anti-patterns

| Anti-pattern | Why it fails |
|--------------|--------------|
| `trusted-users = *` (or every interactive account) as “mesh membership” | Local daemon root-equivalence on **that** install; does not define SSH peers, deploy graph, or cache keys. Manual: membership ≈ root. Prefer named builder/operator accounts. |
| Digga / Hive as a network mesh | [Digga / Hive](../13-implementations/community-frameworks/digga-hive.md) is flake layout / collectors for hosts—not overlay membership or peer interconnect. |
| Colmena “hive” as peer mesh | Colmena’s hive is an **attrset of deployable nodes** pushed from a hub over SSH—not host-to-host mesh fabric. Unrelated to Digga/Hive naming. |

Vocabulary: **trusted** (daemon / signatures) ≠ **inter-trust** (multi-machine composition); **hive** (Colmena or Digga) ≠ **mesh** (peer interconnect / peer-oriented fleet tools).

### Least privilege across a fleet

Configure each axis narrowly:

- Overlay/SSH only where needed; distinct keys for build vs deploy vs interactive login when practical.
- Remote builders: dedicated SSH users in remote `trusted-users`, not `*`.
- Caches: sign; distribute only needed public keys; avoid `require-sigs = false` / blanket `trusted=true` on shared stores.
- Deploy: limit who can run hub tools or hold target SSH/sudo.
- Secrets: encrypt only for hosts that must decrypt; drop recipients on decommission.

## Examples

**Axes are separate config surfaces** (illustrative fragments—not a full mesh):

```ini
# On a remote builder (build trust) — named user, not *
# /etc/nix/nix.conf
trusted-users = root nixbuilder
```

```text
# On a client that offloads builds (reachability + build trust)
# /etc/nix/machines
ssh://nixbuilder@builder.mesh  x86_64-linux  /root/.ssh/id_builder  4 1 kvm
```

```ini
# On consumers (binary trust) — public key of *your* signer, plus official cache if still used
substituters = https://cache.nixos.org/ https://cache.mesh.example/
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= cache.mesh.example-1:BASE64PUBLICKEY=
```

Deploy trust is whoever can run `nixos-rebuild --target-host`, `colmena apply`, or `deploy` with working SSH to the target—not implied by the lines above. Secret trust is the age/SOPS recipient list for that host’s identity—again independent.

## References

- [Nix manual — `trusted-users`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-trusted-users) — daemon privilege; root-equivalence warning
- [Nix manual — Remote builds](https://nix.dev/manual/nix/stable/advanced-topics/distributed-builds.html) — SSH builders, remote `trusted-users`
- [Nix manual — `trusted-public-keys` / substituters](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — binary trust settings
- [ryantm/agenix](https://github.com/ryantm/agenix) / [Mic92/sops-nix](https://github.com/Mic92/sops-nix) — recipient / host-identity secret trust
- [Clan documentation (26.05)](https://clan.lol/docs/26.05) — peer-oriented fleet contrast only (verify APIs upstream; not mirrored here)

## See also

- [Machine mesh](../02-concepts/machine-mesh.md) — concept-level interconnect vs single-host trust
- [Clan and mesh](../12-deployment-and-infra/clan-and-mesh.md) — Clan inventory / mesh VPN contrast with hub deploy
- [Overlay networks](../09-nixos/configuration/overlay-networks.md) — reachability fabric (WG/Tailscale/ZeroTier)
- [Trusted users](trusted-users.md) — local daemon privilege
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — who may change substituter settings
- [Signing and caches](signing-and-caches.md) — binary trust
- [Supply chain](supply-chain.md) — inputs/caches still in the TCB
- [Secrets management](secrets-management.md) — secrets vs store
- [Sandbox escape surface](sandbox-escape-surface.md) — hermeticity (local, not fleet)
- [Remote builders](../04-store-and-build/remote-builders.md) — build-trust axis
- [Store protocols](../04-store-and-build/store-protocols.md) — reachability URI forms
- [Binary caches](../04-store-and-build/binary-caches.md) / [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) / [Private cache mesh](../12-deployment-and-infra/private-cache-mesh.md)
- [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md) — recipient secret trust
- [Colmena](../12-deployment-and-infra/colmena.md) / [deploy-rs](../12-deployment-and-infra/deploy-rs.md) — hub deploy trust
- [Remote deploy](../09-nixos/operations/remote-deploy.md)
- [Digga / Hive](../13-implementations/community-frameworks/digga-hive.md) — name clash; not a network mesh
