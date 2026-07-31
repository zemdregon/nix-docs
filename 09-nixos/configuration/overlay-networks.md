---
status: complete
---

# Overlay Networks

## Overview

Overlay / mesh VPN products (WireGuard, Tailscale, Headscale, ZeroTier, and similar) give Nix fleets a **reachability fabric**: stable private addresses and encrypted paths so [remote builders](../../04-store-and-build/remote-builders.md), [remote deploy](../operations/remote-deploy.md) SSH, and private [binary caches](../../12-deployment-and-infra/binary-cache-hosting.md) work across NATs and sites.

This is **not** a VPN tutorial. Host hostname, firewall defaults, and interface backends live in [Networking](networking.md). Overlay membership is only the **reachability** axis of a [machine mesh](../../02-concepts/machine-mesh.md)—it does not grant build, binary, deploy, or secret trust; see [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md).

**Last checked:** 2026-07-31 — NixOS module option names and Clan mesh-vpn pointers; confirm against your channel / Clan doc version.

## Details

### What Nix consumes

Nix and `nixos-rebuild` talk over ordinary hostnames and [store URIs](../../04-store-and-build/store-protocols.md) (`ssh://…`, `http(s)://…`). Once peers can resolve and route to each other on the overlay, builder lines, `--target-host`, and private substituter URLs look the same as on a LAN. Failures here are timeouts and unreachable hosts—not signature or `trusted-users` errors.

### NixOS module map (verified options)

| Product | Role for Nix fleets | NixOS surface (nixpkgs) |
|---------|---------------------|-------------------------|
| **WireGuard** | Peer-to-peer or hub/spoke tunnels you configure yourself | `networking.wireguard.enable`, `networking.wireguard.interfaces.<name>.*` (optional `networking.wireguard.useNetworkd`) |
| **Tailscale** | Managed mesh client (coordination via Tailscale or Headscale) | `services.tailscale.enable` (and related: `authKeyFile`, `openFirewall`, `useRoutingFeatures`, `extraUpFlags`, …) |
| **Headscale** | Self-hosted coordination server for Tailscale clients | `services.headscale.enable` (+ `address` / `port` / `settings`) |
| **ZeroTier** | Mesh with network IDs / controller auth | `services.zerotierone.enable`, `services.zerotierone.joinNetworks` |
| **Clan + ZeroTier** | Declarative fleet mesh via Clan inventory (`controller` / `peer` / optional `moon`) | Clan inventory `zerotier` instance—not raw `services.zerotierone` alone; see Clan mesh-vpn + zerotier service docs (26.05). Unstable Clan also documents inventory `wireguard` / `mycelium` networking services—cite that channel, not this table. |

Do not invent option names: confirm against [NixOS option search](https://search.nixos.org/options) for your channel. Keep private keys and auth material out of the store—prefer `privateKeyFile` / `authKeyFile` and [secrets strategies](secrets-strategies.md).

### Patterns that matter for Nix

**Builders.** Point `builders` / `/etc/nix/machines` at overlay hostnames or Stable IPs (`ssh://nix@builder.tailnet-name.ts.net` or `ssh://nix@100.x.y.z`). SSH must work non-interactively for the daemon user; overlay DNS (MagicDNS, Headscale DNS, ZeroTier names) is optional but convenient.

**Deploy.** `nixos-rebuild --target-host` / `--build-host`, Colmena, and deploy-rs need the same SSH reachability. Prefer overlay addresses when public IPs are dynamic or firewalled.

**Private caches.** Serve nix-serve / Harmonia / Attic on an overlay-only address (or bind on all interfaces and rely on firewall + overlay). Clients list that URL under `substituters` with the matching `trusted-public-keys`. Overlay reachability does **not** replace signatures.

**Firewall.** Open the overlay’s UDP listen port when peers must initiate to you (`networking.firewall.allowedUDPPorts`, or Tailscale’s `services.tailscale.openFirewall` / `config.services.tailscale.port`). Many setups trust the tunnel interface for inbound mesh traffic via `networking.firewall.trustedInterfaces` (e.g. `tailscale0`, `wg0`, `zt*`). For Tailscale routing features (subnet router / exit node), the module’s `useRoutingFeatures` may loosen reverse-path filtering; otherwise strict RPF can drop tunnel-related traffic—see option docs for `services.tailscale.useRoutingFeatures` and `networking.firewall.checkReversePath`.

**Headscale vs Tailscale SaaS.** Run `services.headscale` on a reachable control plane; clients still use `services.tailscale` and point login at Headscale (commonly via `extraUpFlags`, e.g. `--login-server=https://headscale.example.com`). Verify current Headscale client flags upstream when you wire this.

**Clan mesh-vpn.** On docs **26.05**, Clan’s fully integrated mesh is **ZeroTier** through inventory roles (`controller`, `peer`, optional `moon` with `stableEndpoints`). Deploy the controller first, then peers (`clan machines update`). That fabric is what Clan expects for machine-to-machine reachability; fleet inventory and tooling: [Clan and mesh](../../12-deployment-and-infra/clan-and-mesh.md). Unstable networking also lists inventory WireGuard and other overlays—vocabulary only here; options live upstream.

### Anti-patterns

- Treating VPN membership as `trusted-users`, cache-key acceptance, or deploy authority.
- Putting WireGuard `privateKey` or Tailscale auth keys as plaintext evaluated strings (world-readable store).
- Opening SSH / cache HTTP on the public Internet “because the overlay exists”—bind or firewall so only the fabric (or intentional public endpoints) can reach them.
- Running two overlays on the same hosts without a clear which-address policy for builders and deploy URIs.

## Examples

**Tailscale client** (enable daemon; open UDP; optionally trust the interface for inbound mesh traffic):

```nix
{ config, ... }: {
  services.tailscale.enable = true;
  # Optional: services.tailscale.authKeyFile = "/run/secrets/tailscale_key";
  # Optional: services.tailscale.openFirewall = true;

  networking.firewall = {
    trustedInterfaces = [ config.services.tailscale.interfaceName ];
    allowedUDPPorts = [ config.services.tailscale.port ];
  };
}
```

**Minimal WireGuard interface** (illustrative keys/addresses—replace; prefer `privateKeyFile`):

```nix
{
  networking.firewall.allowedUDPPorts = [ 51820 ];

  networking.wireguard.interfaces.wg0 = {
    ips = [ "10.100.0.2/24" ];
    listenPort = 51820;
    privateKeyFile = "/var/lib/wireguard/privatekey";
    peers = [{
      publicKey = "PEER_PUBLIC_KEY_BASE64=";
      allowedIPs = [ "10.100.0.1/32" ];
      endpoint = "vpn.example.org:51820";
      persistentKeepalive = 25;
    }];
  };
}
```

**ZeroTier client** (join a network ID; membership still requires controller approval unless the network is public):

```nix
{
  services.zerotierone.enable = true;
  services.zerotierone.joinNetworks = [ "a8a2c3c10c1a68de" ];
}
```

After the overlay is up, a builder line is ordinary SSH over fabric addresses:

```text
ssh://nix@10.100.0.1 x86_64-linux /root/.ssh/id_builder 4 1 kvm
```

## References

- [NixOS manual — Networking](https://nixos.org/manual/nixos/stable/index.html#sec-networking)
- [NixOS option search — `networking.wireguard`](https://search.nixos.org/options?query=networking.wireguard)
- [NixOS option search — `services.tailscale`](https://search.nixos.org/options?query=services.tailscale)
- [NixOS option search — `services.headscale`](https://search.nixos.org/options?query=services.headscale)
- [NixOS option search — `services.zerotierone`](https://search.nixos.org/options?query=services.zerotierone)
- [Clan — Mesh VPN (ZeroTier) — 26.05](https://clan.lol/docs/26.05/guides/networking/mesh-vpn/) — last checked 2026-07-31
- [Clan — zerotier service (roles) — 26.05](https://clan.lol/docs/26.05/services/official/zerotier)
- [Clan — Networking (unstable priorities)](https://clan.lol/docs/unstable/guides/networking/networking/) — `wireguard` / `p2p-ssh-iroh` / … when not on 26.05
- [WireGuard](https://www.wireguard.com/) / [Tailscale docs](https://tailscale.com/kb) / [Headscale](https://headscale.net/) / [ZeroTier](https://docs.zerotier.com/) — product behavior beyond NixOS modules

## See also

- [Networking](networking.md) — hostName, firewall, interface backends (not overlays)
- [Machine mesh](../../02-concepts/machine-mesh.md) — interconnect mental model
- [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md) — reachability vs build/binary/deploy/secret axes
- [Clan and mesh](../../12-deployment-and-infra/clan-and-mesh.md) — Clan fleet tooling; ZeroTier mesh-vpn as reachability
- [Remote builders](../../04-store-and-build/remote-builders.md) — builders over overlay SSH
- [Store protocols](../../04-store-and-build/store-protocols.md) — URI forms once peers route
- [Remote deploy](../operations/remote-deploy.md) — hub SSH activate over fabric
- [Colmena](../../12-deployment-and-infra/colmena.md) / [deploy-rs](../../12-deployment-and-infra/deploy-rs.md) — hub deploy needing reachability
- [Binary cache hosting](../../12-deployment-and-infra/binary-cache-hosting.md) — private caches on overlay addresses
- [Secrets strategies](secrets-strategies.md) — keys/auth material out of the store
