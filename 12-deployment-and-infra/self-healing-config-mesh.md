---
status: draft
---

# Self-Healing Config Mesh

## Overview

**Intentional `draft` — out of the v1 complete set.** This page is design analysis only (fleet gossip / self-upgrade config shapes). It is **not** a shipped Nix, NixOS, or Clan tool, and it stays `status: draft` on purpose. For shipped vocabulary and tooling, start with [Machine mesh](../02-concepts/machine-mesh.md) and [Clan and mesh](clan-and-mesh.md); related trust and offline context: [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md), [Airgap and offline](airgap-and-offline.md).

A **self-healing config mesh** is a fleet of mutually trusted devices that distribute and activate **versioned configuration** among themselves, without depending on anything outside the mesh for day-to-day updates: no GitHub, no central CI, no out-of-mesh build farm as a hard requirement.

The core loop:

1. Devices already trust each other (SSH keypairs, a group CA, signed peer identities, etc.).
2. One member receives (or authors) a new config with a **monotonically higher version**.
3. That member pushes or gossip-propagates the artifact to peers.
4. Peers verify trust + version, adopt, and continue the epidemic until the mesh converges.
5. If two peers meet on different versions, the newer one **refuses operational traffic** (or refuses “same-generation” assumptions) and **hands the older peer the upgrade** so it can rebuild/switch before continuing.

Scope of this draft: shapes, trust models, propagation protocols, what “config” actually is (especially under Nix), failure modes, and compensations. Contrast with hub push ([Colmena](colmena.md), [deploy-rs](deploy-rs.md)) and with inventory/peer fleets ([Clan and mesh](clan-and-mesh.md)).

## Problem being solved

Hub deploy assumes a **privileged outside**: a laptop with credentials, a CI runner, a Hydra, a Git forge that holds the source of truth. That works until:

- The forge or CI is unreachable (outage, censorship, air-gap, travel, disaster).
- The only machine that “knows” how to deploy is offline.
- You want the fleet itself to be the durable control plane.

The mesh goal is **operational closure**: once bootstrapped and mutually trusted, configuration can enter at any member and reach the rest using only in-mesh reachability and trust. External systems become optional injectors, not continuous dependencies.

What you do **not** fully eliminate without further work: first bootstrap, CA/key ceremony, hardware replacement, and (for Nix) evaluation/build of large closures if no peer already has the bits. Closure of *control* is easier than closure of *compute and supply chain*. See [Supply chain](../14-security-and-trust/supply-chain.md) and [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md).

## Details

### Mental model

```text
                    ┌─ inject vN (laptop / USB / one peer) ─┐
                    ▼                                        │
   peer-A (vN) ──gossip / push──► peer-B (vN-1 → vN)        │
      │                               │                      │
      │         reject + offer vN     │                      │
      └──────── peer-C (vN-2) ────────┘                      │
                    │                                        │
                    └── rebuild / switch / rejoin ────────────┘
```

Three layers must align:

| Layer | Job |
|-------|-----|
| **Trust fabric** | Prove “this peer may send me config / closures / activation commands.” |
| **Version / consensus** | Decide which config wins and when it is safe to activate. |
| **Payload plane** | Move source, lockfiles, NAR/closures, or activation instructions; then build/switch locally or pull store paths from peers. |

Conflating them (e.g. “VPN membership = may activate my root”) is the usual failure mode—same lesson as the six trust axes in [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md).

### What “versioned config” can mean

Different payload granularities change the protocol completely:

1. **Source tree + lock + version integer** — Peers sync a git-like object (or tarball + signature). Each peer evaluates and builds locally. Needs local Nix, CPU, and often substituters or peer stores.
2. **Evaluated NixOS/system closure** — Sync store paths (or a signed manifest of paths). Faster convergence if someone already built; needs [binary trust](../14-security-and-trust/signing-and-caches.md) and enough disk/bandwidth.
3. **Per-host projections of one logical version** — One fleet version maps to many host closures (`hostA@vN`, `hostB@vN`). Propagation must carry a **bundle** or a way to derive each host’s projection without a central evaluator.
4. **Activation receipt only** — “Switch to generation G / profile path P” when the closure is already present (or obtainable). Smallest message; weakest if peers diverge on store contents.

A single global integer is enough for “newer wins” only if the payload is self-contained and conflict-free. For multi-host Nix fleets, prefer **(logical fleet version, content hash, optional per-host attr)** so peers can detect “same version, different bytes” (corruption or fork) instead of blindly trusting the integer.

### Trust implementations

Any of these can underwrite “inherent trust”; they differ in rotation, blast radius, and offline friendliness.

#### Mutual SSH host/user keys

- Each peer has deploy keys for others (or a shared mesh principal).
- Propagation = authenticated `scp`/`nix copy`/`ssh` activate.
- **Pros:** Simple, works offline, matches today’s [remote deploy](../09-nixos/operations/remote-deploy.md) habits.
- **Cons:** O(n²) key distribution unless you use a CA; revocation is painful; compromised key ⇒ full deploy axis on every machine that trusts it.

**Compensation:** SSH CA for user/host certs with short TTLs; separate keys for “gossip config” vs “activate as root”; wrap activation behind a local agent that checks version + signature before `switch-to-configuration`.

#### Group / mesh CA (mTLS, SPIFFE-like, internal PKI)

- Peers present certs signed by a mesh CA; config artifacts signed by a **config-signing** key (ideally distinct from transport).
- **Pros:** Join/leave and rotation are manageable; transport auth ≠ content auth if you split keys.
- **Cons:** CA is a soft center. If the CA host is outside the mesh, you reintroduce external dependence; if inside, CA compromise or loss is catastrophic.

**Compensation:** Offline root CA, intermediate online only for enroll; multiple config-signing keys with threshold signatures; emergency break-glass USB ceremony documented separately from day-to-day gossip.

#### Pre-shared peer allowlist + artifact signatures

- Transport can be anything (WireGuard, Tor, LAN); acceptance is “signed by key K_i in allowlist AND version > current.”
- **Pros:** Clear content trust; works over untrusted links.
- **Cons:** Allowlist updates are themselves config—chicken-and-egg for membership changes.

**Compensation:** Membership changes require a higher-privilege signature set (e.g. 2-of-3 owners) than routine config bumps.

#### Threshold / multi-party approval

- Version N activates only if M of N signing keys endorse it.
- **Pros:** Stops single compromised peer from poisoning the mesh.
- **Cons:** Slower epidemic; partition can block upgrades; bad UX for solo admin meshes.

**Compensation:** Two tracks—**urgent signed-by-any-owner** for break-glass vs **quorum** for routine; or quarantine mode where single-sig updates apply only to non-prod roles.

Trust fabric must stay separate from [overlay reachability](../09-nixos/configuration/overlay-networks.md). Being on the same ZeroTier/WireGuard net is necessary for gossip, not sufficient for activation.

### Propagation designs

#### Push epidemic (infected push)

Node with vN connects to known peers still on &lt; vN and pushes payload + signature.

- **Pros:** Fast when connectivity is good; easy to reason about from the injector.
- **Cons:** Needs peer discovery/list; pushers spend bandwidth; NAT/firewall may block inbound unless overlay helps.

#### Pull / gossip on contact

Whenever peers communicate for any reason, they exchange version advertisements; lagging peer pulls.

- **Pros:** Natural fit for “reject and upgrade” on mismatch; no separate fan-out daemon required if all apps speak the protocol.
- **Cons:** Isolated nodes stay stale until they talk to someone newer; silent partitions diverge.

#### Hybrid anti-entropy

Periodic version vector / Merkle sync of “who has what,” plus push of missing payloads (like Cassandra repair or package mirror rsync).

- **Pros:** Converges under churn; good for large payloads (closures).
- **Cons:** More moving parts; must bound bandwidth (partial sync, prioritize manifests before NARs).

#### Spanning tree / designated spreaders

Elect (or configure) a few well-connected nodes as fan-out hubs *inside* the mesh.

- **Pros:** Efficient; mirrors how people already use a “build box.”
- **Cons:** Soft centers—if hubs die, fall back to full mesh gossip or upgrades stall.

**Compensation:** Hubs are optimization, not authority; any peer with a valid newer signature may seed.

For Nix store bits specifically: treat peers as [substituters](binary-cache-hosting.md) / `nix copy` sources with [signing](../14-security-and-trust/signing-and-caches.md), and treat the **versioned manifest** as the control-plane object that points at store paths. Do not invent a new binary format when NAR + narinfo (or `nix-store --export`) already exist.

### Version mismatch protocol (“reject and remediate”)

Desired behavior when peer New (vN) meets peer Old (vK, K &lt; N):

1. **Advertise** versions (and content hashes) in a handshake before privileged work.
2. **Refuse** operations that assume same generation (cluster joins, shared service protocols, “we’re in sync” admin APIs). Unprivileged read-only status may still be allowed.
3. **Offer** the upgrade package: manifest + signatures + locator (inline blob, peer store URI, chunked transfer).
4. **Old verifies** trust policy, disk space, and that vN is a valid successor (see forks below).
5. **Old fetches** missing store paths from New or other peers, builds if required, activates, reboots if needed.
6. **Retry** the original communication only after Old reports vN (or New accepts a grace profile).

Design knobs:

| Knob | Choices | Tradeoff |
|------|---------|----------|
| Hard vs soft reject | Drop all app traffic vs allow degraded mode | Safety vs availability |
| Who builds | Old builds from source vs pull closure from New | CPU/isolation vs trusting New’s build environment |
| Blocking | Handshake waits for upgrade vs async upgrade + retry | Simple protocol vs long stalls |
| Partial mesh versions | Require global vN vs allow mixed versions per role | Consistency vs rolling upgrades |

**Rolling upgrades:** Strict “never talk across versions” can deadlock a service that needs old and new to coexist (DB primary/replica, k8s-style). Compensations: version the *wire protocol* separately from *host config version*; allow listed compatibility windows; or upgrade in waves with explicit `min_peer_version` in the manifest.

### Successor rules and forks

A bare integer is dangerous:

- Clock skew does not apply to integers, but **human or bug can mint vN+1 twice with different contents**.
- A compromised peer can mint a huge version and brick rollback if you only allow “forward.”
- Split-brain: two injectors offline from each other both issue vN+1.

Safer successor policy:

- Require `version` **and** `prev_content_hash` (hash chain), or a signed hash chain / lightweight blockchain-of-config.
- Detect divergence: same version, different hash ⇒ stop and alarm; do not auto-pick.
- Optional: **quorum of peers** must ACK before a version is “committed” mesh-wide (at cost of partition intolerance).
- Preserve NixOS [generations / rollbacks](../09-nixos/operations/rollbacks.md) locally even when mesh version only moves forward—mesh version ≠ local boot generation.

### Nix-specific realization sketches

None of these are “the” implementation; they show how the abstract mesh maps onto Nix pieces.

#### A. Signed flake bundle epidemic

Payload: flake source + `flake.lock` + version metadata + signature. Peers `nixos-rebuild switch` (or equivalent) locally; use peer stores as substituters.

- Closest to “config as code” mental model.
- Still needs eval/build capacity on each class of hardware ([remote builders](../04-store-and-build/remote-builders.md) inside the mesh help).
- Pins must not point at unreachable `github:` for runtime—vendor inputs into the bundle or use in-mesh git/HTTP.

#### B. Manifest of store paths per host

Injector (any peer) builds all host closures (or builds what it can), publishes a signed manifest `{ version, hosts: { name: outPath } }`. Peers fetch their outPath from whoever has it, then activate.

- Fast when builds already exist.
- Injector or build-capable peers become soft centers for *compute*, not for *authority* if signatures are separate.
- Multi-arch fleets need manifests that cover each system.

#### C. Activation-only gossip

Assume closures replicated by a background `nix copy` mesh. Control plane only spreads “activate path P at version N.”

- Smallest control messages.
- Dangerous if store replication lags—always bind activation to content hash verification.

#### D. Compare to existing tools

| Approach | Outside dependence | Peer remediation |
|----------|--------------------|------------------|
| Colmena / deploy-rs / `nixos-rebuild --target-host` | Deployer + usually git/CI | No; hub retries |
| Hydra + caches | CI + cache host | Clients pull; not peer reject/upgrade |
| Clan mesh VPN + `clan machines update` | Still typically admin-driven update; VPN is reachability | Not automatic version epidemic |
| Self-healing config mesh (this doc) | Bootstrap only (ideal) | First-class |

Clan’s mesh is primarily [reachability and inventory](clan-and-mesh.md), not an automatic versioned-config epidemic. You could *build* this pattern *on* Clan/WG/ZeroTier; they are not the same thing.

### Entry points (how vN appears without GitHub)

In-mesh closure still needs **some** way for bits to enter:

- Admin laptop briefly joins overlay, pushes once, leaves.
- USB / sneaker-net signed bundle.
- Out-of-band message (Signal, email) carrying a small manifest + retrieval from a peer that already has NARs.
- One peer pulls from the internet when available, then seeds the mesh (internet is optional *injector*, not continuous control plane).

Document which entry methods your threat model allows; “no GitHub” is not “no human.”

### Drawbacks and shortcomings

#### Security blast radius

Inherent mutual trust means **one compromised peer can often become a worm**: it already has the keys to push “upgrades.” Version monotonicity accelerates spread of malice as well as fixes.

**Compensations:** Quorum signatures; separate transport and config-signing keys; staging/canary cohort that must succeed before signature is valid for `prod` tags; hardware-backed keys (TPM/Secure Boot) so stolen disk ≠ signing; attestation before accepting activation ([TPM / measured boot](../09-nixos/configuration/tpm-and-measured-boot.md) as a hard optional layer).

#### Rollback and bad versions

“Newer always wins” fights emergency rollback. A bad vN that bricks networking can prevent remediation gossip.

**Compensations:** Local automatic rollback if health checks fail post-switch (watchdog); out-of-band serial/KVM; **rollback versions** that are explicitly signed as `supersedes: N` with higher privilege; keep previous generation bootable regardless of mesh version; dual-homed management link not tied to mesh overlay.

#### Partitions and split-brain

Two islands each accept different vN+1. On heal, naive max(version) may pick arbitrarily wrong content if versions collide, or refuse forever if hash chains diverge.

**Compensations:** Hash chaining; partition-aware versions (vector clocks or replica-sets—usually overkill); human merge ritual; prefer availability in partition only for *serving*, never for *accepting new config* without quorum.

#### Resource and heterogeneity

Not every peer can build every closure (arch, memory, private sources). Epidemic of source-only configs stalls on weak devices.

**Compensations:** Path B (prebuilt closures); in-mesh remote builders; arch-specific manifests; “build class” tags so phones/routers only pull.

#### Bandwidth and store growth

Shipping full system closures mesh-wide is expensive; GC policy fights “keep enough history to remediate.”

**Compensations:** Chunked/repair sync; advertise before transfer; compress; keep only last K manifests; shared substitute layer among peers; delta/ closure diff research (limited tooling—don’t assume magic deltas).

#### Membership churn

Adding a host requires trust update; removing a compromised host requires **revocation** that itself must propagate—possibly against a hostile node that ignores revocation.

**Compensations:** Short-lived certs; CRLs or epoch numbers in manifests (“epoch E ignores keys revoked in E”); network-layer isolation (overlay ACL) in parallel with app-layer reject; physical decommission checklist.

#### Liveness vs safety

Hard reject-on-mismatch maximizes config consistency and minimizes weird mixed-version bugs; it also maximizes outage during upgrades and can strand nodes.

**Compensations:** Explicit compatibility matrix; feature flags inside one version; soak time; pause epidemic if error budget exceeded.

#### Supply chain still exists

In-mesh distribution does not make `flake.lock` inputs or FODs trustworthy. You moved *where* bits flow, not *whether* they were malicious when first injected.

**Compensations:** Vendoring; in-mesh mirrors of inputs; signature over entire closure; review at injection time; see [Supply chain](../14-security-and-trust/supply-chain.md).

#### Secrets

Config epidemic must not casually replicate decrypted secrets. Peer trust for deploy ≠ every peer should hold every secret.

**Compensations:** Keep [agenix / sops-nix](agenix-sops-nix.md)-style recipient encryption inside the bundle; gossip ciphertext; only recipients decrypt at activate; separate secret-signing/recipient rotation from routine version bumps ([Secrets management](../14-security-and-trust/secrets-management.md)).

#### Observability and intent

Without a central board, “what version is the mesh on?” and “who injected this?” become gossip questions.

**Compensations:** Each peer exposes signed status; optional append-only log replicated in-mesh; require `injector_id` in metadata; alerting on version skew.

### Compensating patterns (summary)

| Shortcoming | Pattern |
|-------------|---------|
| Wormable trust | Quorum / dual-key; canaries; TPM-bound signing |
| Bad upgrade bricks gossip | Local watchdog rollback; break-glass channel; unsigned-offline recovery |
| Split-brain | Hash chain; refuse divergent same-version; human merge |
| Weak builders | Prebuilt manifests; in-mesh builders; arch tags |
| Huge payloads | Peer substituters; anti-entropy; last-K retention |
| Revocation | Cert TTL; epoch revocation; overlay ACL |
| Mixed-version services | Wire compat windows; staged waves |
| Secrets sprawl | Per-host encryption in-band; least recipients |
| Lost external CI | Optional injector only; don’t encode forge URLs as runtime deps |
| No central UI | Signed status documents; mesh-wide version report over gossip |

### When not to use this

- Small fleets happy with a laptop + Colmena and reliable network to targets.
- Strong requirement for a single audited CI gate before any production activate (keep CI as mandatory injector, use mesh only as distribution).
- Highly adversarial environment where any peer compromise is likely—then “inherent trust” is the wrong premise; use hub deploy with tight credentials and attested one-way pushes.
- Devices that cannot store prior generations or run health-checked rollback.

### Design checklist (if you build it)

1. Split **transport identity**, **config signing**, and **secret recipients**.
2. Define payload: source bundle vs store manifest vs activate-only—and content hashes, not bare integers.
3. Specify mismatch behavior per traffic class (cluster protocol vs admin SSH vs substitute fetch).
4. Define rollback and break-glass that work when the overlay is dead.
5. Plan membership/revocation epochs before the first compromise.
6. Decide build topology inside the mesh (everyone builds vs few build).
7. Measure convergence: max version skew, bytes per upgrade, time-to-heal after partition.
8. Keep external systems as **optional injectors**; never as blocking dependencies for peer remediation.

## Examples

Illustrative handshake sketch (not a real protocol):

```text
A→B: HELLO mesh_id=home version=42 content=sha256:…
B→A: HELLO mesh_id=home version=40 content=sha256:…
A→B: REJECT reason=version_skew offer=v42 size=… sig=…
B→A: FETCH manifest
A→B: MANIFEST + sig + store_hints
B:    verify sig, nix copy missing paths, switch, healthcheck
B→A: HELLO version=42 content=sha256:…   # retry
A→B: OK; continue application protocol
```

Minimal policy fragment (conceptual):

```nix
# Illustrative only — not an existing NixOS module API
{
  mesh.id = "home";
  mesh.trustedConfigPublishers = [ "ssh-ed25519 AAAA…" "ssh-ed25519 BBBB…" ];
  mesh.requireContentHash = true;
  mesh.rejectAppTrafficOnSkew = true;
  mesh.localRollbackOnHealthFail = true;
}
```

## References

- [Clan documentation (26.05)](https://clan.lol/docs/26.05) — peer-oriented NixOS fleets and mesh VPN (reachability contrast, not this epidemic model)
- [Colmena docs](https://colmena.cli.rs/) — hub → hosts deploy (control-plane contrast)
- [deploy-rs](https://github.com/serokell/deploy-rs) — flake hub deploy
- [NixOS manual — remote deployment / nixos-rebuild](https://nixos.org/manual/nixos/stable/) — classic push activation building blocks
- Gossip / anti-entropy background (general CS): epidemic dissemination and repair are classical distributed-systems patterns; apply carefully—Nix store semantics and activation safety are stricter than typical KV gossip

## See also

- [Machine mesh](../02-concepts/machine-mesh.md) — vocabulary for interconnected Nix devices
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — trust axes this design must not collapse
- [Clan and mesh](clan-and-mesh.md) — inventory + overlay tooling
- [Colmena](colmena.md) / [deploy-rs](deploy-rs.md) / [Remote deploy](../09-nixos/operations/remote-deploy.md) — hub alternatives
- [Binary cache hosting](binary-cache-hosting.md) — peer-as-substituter building block
- [Remote builders](../04-store-and-build/remote-builders.md) — in-mesh compute
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — binary trust for closure epidemic
- [agenix / sops-nix](agenix-sops-nix.md) — secrets inside a versioned bundle
- [Rollbacks](../09-nixos/operations/rollbacks.md) — local safety net vs mesh forward-only versions
- [Supply chain](../14-security-and-trust/supply-chain.md) — what mesh distribution does not fix
- [Overlay networks](../09-nixos/configuration/overlay-networks.md) — reachability fabric
- [Airgap and offline](airgap-and-offline.md) — offline injectors / sneaker-net vs in-mesh epidemic
