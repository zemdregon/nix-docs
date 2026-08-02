---
status: complete
last-checked: 2026-08
---

# Private Cache Mesh

## Overview

A **private cache mesh** is how a fleet shares pre-built store paths: several hosts act as **substituters** (HTTP caches) and/or **push targets**, wired together with explicit signing keys—not with VPN membership alone. One org often runs a **central durable cache** (Attic, Cachix, S3) while **edge builders** expose live stores (Harmonia, nix-serve) or push upstream after CI builds.

This page owns **multi-host topology and client wiring**—who substitutes from whom, in what order, and how remote builders participate. It does not cover picking and operating a single cache backend ([Binary cache hosting](binary-cache-hosting.md)), mesh trust vocabulary ([Machine mesh](../02-concepts/machine-mesh.md)), USB/`file://` offline flows ([Airgap and offline](airgap-and-offline.md)), or design-only gossip config ([Self-healing config mesh](self-healing-config-mesh.md)).

Typical homelab split: CI or a builder pushes closures to a hub cache; long-lived builders run Harmonia for fast LAN/overlay hits; laptops and deploy targets list hub + edge URLs under `substituters` with matching `trusted-public-keys`, still keeping `cache.nixos.org` for upstream gaps.

## Details

### Peer substituters vs one cache host

| Model | Shape | Strength | Weakness |
|-------|-------|----------|----------|
| **Single hub** | All pushers → Attic/Cachix/S3; all clients → one URL | Durable, deduplicated, survives builder GC | Single ops surface; edge latency without CDN |
| **Edge live-store** | Each builder serves `/nix/store` (Harmonia/nix-serve) | Zero push step for paths already on disk; great on overlay LAN | Paths vanish after GC; no cross-site durability |
| **Mesh (mixed)** | Hub for CI/products + edges for hot paths + optional peer `nix copy` | Combines durability with local speed | More URLs, keys, and DNS to keep consistent |

A mesh is not “every peer trusts every peer’s store blindly.” Clients still need **reachability** ([Overlay networks](../09-nixos/configuration/overlay-networks.md)), **substituter allow-listing** on multi-user installs, and **signature trust** ([Inter-machine trust](../14-security-and-trust/inter-machine-trust.md)).

### Topology patterns

**Hub + edge.** CI or Hydra pushes to Attic/Cachix (or `nix copy --to s3://…`). Homelab builders run Harmonia on overlay hostnames (`http://builder-a.tailnet:8080/`). Laptops and servers add private URLs via `extra-substituters` (and matching keys) while keeping the default `https://cache.nixos.org/` for upstream gaps. Prefer fleet caches with lower `Priority` in `nix-cache-info` (or configure store-URL priority) so private hits win when both have the path.

**Builder-as-cache.** A machine that already runs [remote builds](../04-store-and-build/remote-builders.md) can serve its store without a separate cache VM—configure Harmonia/nix-serve on the same host that holds build products. Products appear for substitution only after they exist locally; schedule `nix copy --to` to the hub if you need durability.

**Laptop → builder → server chain.** The laptop offloads builds to a remote builder; the builder may substitute from its own caches (`builders-use-substitutes`, below) or build from source. Deploy hosts (NixOS servers) substitute from hub + builder HTTP caches; deploy tools may additionally `nix copy` closures over `ssh://` when HTTP is wrong for one-off shipping ([nix copy and bundles](nix-copy-and-bundles.md)).

**Peer copy alongside HTTP.** HTTP substituters scale for many clients pulling the same `.narinfo`/NAR. `nix copy --to ssh://host` (or `--from`) complements HTTP for ad hoc closure transfer, airgap handoff, or when no cache daemon runs on the donor—see [Store protocols](../04-store-and-build/store-protocols.md).

```text
                    ┌── Attic / Cachix (durable hub) ◄── CI push
                    │
laptop ──remote build──► builder-a (Harmonia, live store)
   │                           │
   │ substituters              │ substituters + optional push
   ▼                           ▼
server-1, server-2 ── HTTP ──► hub + builder-a + cache.nixos.org
```

### Declarative `nix.settings` by role

Illustrative NixOS fragments only—replace hostnames, keys, and tokens with your fleet. Use `extra-substituters` / `extra-trusted-public-keys` to append without dropping the default NixOS lists.

**CI pusher** (builds, pushes to hub; may still substitute from hub + upstream):

```nix
{ ... }: {
  nix.settings = {
    extra-substituters = [ "https://myorg.cachix.org" ];
    extra-trusted-public-keys = [ "myorg.cachix.org-1:BASE64…" ];
  };
  # Push step is tool-specific: cachix push, attic push, nix copy --to s3://…
}
```

**Builder + edge Harmonia** (serves live store; substitutes from hub):

```nix
{ ... }: {
  services.harmonia = {
    enable = true;
    signKeyPaths = [ "/run/keys/cache-signing.secret" ];
  };

  nix.settings = {
    extra-substituters = [ "https://attic.internal.example/my-cache" ];
    extra-trusted-public-keys = [ "attic.internal.example-1:BASE64…" ];
  };
}
```

**Deploy target / server** (consumes hub + nearby builders; keep default `cache.nixos.org` via NixOS defaults):

```nix
{ ... }: {
  nix.settings = {
    extra-substituters = [
      "http://builder-a.tailnet:8080/"
      "https://attic.internal.example/my-cache"
    ];
    extra-trusted-public-keys = [
      "builder-a.example-1:BASE64…"
      "attic.internal.example-1:BASE64…"
    ];
    trusted-substituters = [
      "http://builder-a.tailnet:8080/"
      "https://attic.internal.example/my-cache"
    ];
  };
}
```

**Laptop (coordinator + remote builds)**:

```nix
{ ... }: {
  nix.distributedBuilds = true;
  nix.settings.builders-use-substitutes = true;

  nix.buildMachines = [
    {
      hostName = "builder-a.tailnet";
      sshUser = "remotebuild";
      system = "x86_64-linux";
    }
  ];

  nix.settings = {
    extra-substituters = [
      "http://builder-a.tailnet:8080/"
      "https://myorg.cachix.org"
    ];
    extra-trusted-public-keys = [
      "builder-a.example-1:BASE64…"
      "myorg.cachix.org-1:BASE64…"
    ];
    trusted-substituters = [
      "http://builder-a.tailnet:8080/"
      "https://myorg.cachix.org"
    ];
  };
}
```

Multi-user daemons need `trusted-substituters` (or a `trusted-users` entry) so unprivileged `nix build` can use private HTTP caches—see [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md).

### Substituter priority, fallback, and remote builders

Nix prefers substituters by **priority** (lower number = higher priority; often from each cache’s `nix-cache-info`). Keep `cache.nixos.org` as a fallback for paths the mesh never built; use `extra-substituters` so you do not accidentally drop the default official cache when adding private URLs.

With `fallback = true` (non-default), a failed substitute attempt can fall back to building locally after substituters are exhausted. Without it, some failures stop early—know your default on the channel.

**`builders-use-substitutes = true`** (on the machine that *schedules* remote builds) lets each remote builder pull **its own** `substituters` for build inputs instead of waiting for the coordinator to upload every path. Default is `false`. Remotes must independently trust the same private keys and reach the same URLs (overlay DNS, firewall). Details: [Remote builders](../04-store-and-build/remote-builders.md), [Binary caches](../04-store-and-build/binary-caches.md).

### Signing and reachability are separate axes

Overlay membership (Tailscale, WireGuard, ZeroTier) gives **hostnames and routes**—it does not add a public key to `trusted-public-keys` or a URL to `trusted-substituters`. A peer on the VPN can still serve unsigned or wrongly signed `.narinfo`; Nix rejects those when `require-sigs` is true (default).

Configure stable names for substituter URLs: MagicDNS, Headscale DNS, or static WG `AllowedIPs`—see [Overlay networks](../09-nixos/configuration/overlay-networks.md). Signing ceremony and key rotation: [Signing and caches](../14-security-and-trust/signing-and-caches.md), [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md).

### GC vs durable cache

**Live-store servers** (Harmonia, nix-serve) expose whatever paths exist under `/nix/store` on that host. When `nix-collect-garbage` or auto-GC runs, substitutable paths **404** even though clients still reference the store hash. Treat edges as accelerators, not the sole copy of release artifacts.

**Durable org caches** (Attic, Cachix, S3 populated by `nix copy`) decouple substitution from any single builder’s lifecycle. CI pushes release closures to the hub; edges may mirror hot paths but should not be the only retention policy.

Operational habit: after important builds, **push to hub**; use Harmonia for same-day repeats; expect edge misses after GC and fall back to hub or `cache.nixos.org`.

### Peer `nix copy` vs HTTP substituter

| Mechanism | Best for | Notes |
|-----------|----------|-------|
| **HTTP substituter** | Many clients, repeat pulls, CI/deploy hosts | Needs cache daemon or static HTTPS tree; signed `.narinfo` |
| **`nix copy` over `ssh://`** | One-off closure to a host, deploy prep, no HTTP server | Uses [store protocols](../04-store-and-build/store-protocols.md); `--substitute-on-destination` can let the target fetch |
| **Hub push (`cachix` / `attic` / `s3`)** | Durable sharing across sites | Not peer-to-peer; central index |

HTTP scales for “always-on” consumption; `nix copy` fits “ship this closure now” without standing up substitution for every builder.

### Failure modes

| Symptom / mistake | Likely cause | What to check |
|-------------------|--------------|---------------|
| Private cache works from one laptop, not others | URL missing from `trusted-substituters`; user not in `trusted-users` | System `nix.settings.trusted-substituters` on multi-user targets; [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |
| VPN up but substituter timeout | Wrong hostname, firewall on overlay, or cache bound to LAN only | Ping/curl `nix-cache-info` over overlay IP; [Overlay networks](../09-nixos/configuration/overlay-networks.md) |
| Edge cache 404 for known-good path | GC removed path from builder; never pushed to hub | Rebuild or copy to hub; use durable cache for releases |
| Remote build slow despite nearby cache | `builders-use-substitutes = false` (default) | Enable on coordinator; ensure builder trusts same substituters/keys |
| Signatures rejected fleet-wide | Key name mismatch, rotated secret without updating clients | Compare `Sig:` on `.narinfo` to `trusted-public-keys`; use `extra-trusted-public-keys` |
| Only `cache.nixos.org` hits | Missing private URLs/keys, or private cache priority higher than expected | Confirm `extra-substituters` + `trusted-public-keys`; check cache `Priority` / store-URL priority |
| Assumed “mesh VPN = trusted binaries” | Conflated reachability with binary trust | Add explicit keys; VPN does not replace [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) |
| Harmonia works, Attic empty | No push pipeline from builders/CI | Wire [CI with Nix](../11-development/ci-with-nix.md) or post-build `nix copy` / `attic push` |

### Where to go next

- **Chooser / symptom table:** [Binary caches (cheatsheet)](../cheatsheets/binary-caches.md)
- **Run one backend (sign, push, TLS):** [Binary cache hosting](binary-cache-hosting.md)

## Examples

**Sanity-check a mesh substituter** from any fleet member (overlay or LAN):

```bash
curl -sf "http://builder-a.tailnet:8080/nix-cache-info"
# Optional: fetch a known path's .narinfo (hash = store basename without /nix/store/):
# curl -sf "http://builder-a.tailnet:8080/<hash>.narinfo" | head
```

**Ship a closure to a server without HTTP cache** (peer copy):

```bash
nix copy --to ssh://root@server-1.tailnet ./result
```

**Coordinator: remote builder uses its own caches** (`nix.conf` fragment):

```ini
builders = ssh://remotebuild@builder-a.tailnet x86_64-linux /root/.ssh/id_remote 8 1 -
builders-use-substitutes = true
```

## References

- [nix.dev — Setting up an HTTP binary cache](https://nix.dev/tutorials/nixos/binary-cache-setup) — NixOS nix-serve/Harmonia-style serving, signing, client trust
- [Harmonia](https://github.com/nix-community/harmonia) — live-store HTTP cache server
- [Nix reference manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `substituters`, `trusted-substituters`, `trusted-public-keys`, `fallback`, `builders-use-substitutes`

## See also

- [Binary cache hosting](binary-cache-hosting.md) — pick and operate one cache backend
- [Binary caches](../04-store-and-build/binary-caches.md) — substitution model and settings
- [Binary caches (cheatsheet)](../cheatsheets/binary-caches.md) — consume / host / sign chooser
- [Machine mesh](../02-concepts/machine-mesh.md) — fleet trust axes (not topology detail)
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — binary authenticity vs VPN
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — keys, `require-sigs`
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — multi-user allow lists
- [Remote builders](../04-store-and-build/remote-builders.md) — `builders-use-substitutes`, SSH builders
- [Overlay networks](../09-nixos/configuration/overlay-networks.md) — stable hostnames for mesh URLs
- [nix copy and bundles](nix-copy-and-bundles.md) — peer closure copy over SSH
- [Store protocols](../04-store-and-build/store-protocols.md) — `ssh://`, HTTP store URIs
- [CI with Nix](../11-development/ci-with-nix.md) — push pipelines into org caches
- [Clan and mesh](clan-and-mesh.md) — declarative peer fleets (reachability + inventory)
- [Airgap and offline](airgap-and-offline.md) — non-HTTP offline paths (contrast)
- [Self-healing config mesh](self-healing-config-mesh.md) — design-only gossip (not shipped)
