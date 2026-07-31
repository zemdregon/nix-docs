---
status: complete
---

# Networking

## Overview

NixOS host networking is declared under `networking.*` in [configuration.nix](configuration-nix.md). Hostname, firewall holes, interface addresses, and the management backend (NetworkManager, scripted/`dhcpcd`, or `systemd-networkd`) are module values baked into the system [generation](../../02-concepts/generation.md). Nothing on the wire changes until you [rebuild](../operations/rebuild-switch-boot-test.md).

This page covers host-level setup only—not mesh/overlay VPN products ([overlay networks](overlay-networks.md), [machine mesh](../../02-concepts/machine-mesh.md)). Focus here: **stateful firewall** (iptables or nftables backend) and **NetworkManager** patterns for desktops and laptops.

## Details

### Hostname

Set `networking.hostName` to a single DNS label (no domain part; max 63 characters; prefer lowercase; avoid underscores). Default is the distro id (usually `nixos`). Use `""` if DHCP should supply the name. Optional `networking.domain` completes an FQDN for software that wants one; the kernel nodename remains the short hostname unless you work around it (see the option docs).

### Stateful firewall (defaults and holes)

`networking.firewall.enable` defaults to `true`: a simple stateful firewall for IPv4 and IPv6 that blocks unexpected inbound traffic. Open ports globally with `allowedTCPPorts` / `allowedUDPPorts` (or the `*PortRanges` variants). Enabling `services.openssh.enable` opens TCP 22 automatically (`openFirewall` defaults to `true` on that module). Disable the firewall only when you understand the exposure.

**Prefer service modules over hand-listing ports.** Many services expose `openFirewall = true` (or default it on) to open their listen ports in the generated rules. Use that when the module provides it; fall back to `networking.firewall.*` only when the service does not integrate with the firewall.

| Goal | Prefer | Fallback |
|------|--------|----------|
| Open SSH | `services.openssh.enable = true` (opens 22) | `allowedTCPPorts = [ 22 ]` |
| Open a daemon’s port | `services.<name>.openFirewall = true` if the option exists | `allowedTCPPorts` / `allowedUDPPorts` |
| Hole on one NIC only | `networking.firewall.interfaces."<iface>".allowedTCPPorts` (etc.) | Global allow + tighter routing elsewhere |
| Custom match (nftables backend) | `networking.firewall.extraInputRules` | `networking.nftables.tables` (avoid clobbering `nixos-fw`) |

### Firewall backend (iptables vs nftables)

The firewall implementation follows `networking.nftables.enable` (and firewalld when enabled). On recent NixOS releases, `networking.firewall.backend` documents the same auto-selection (`iptables`, `nftables`, or `firewalld`); you normally flip backends by enabling nftables or firewalld, not by setting `backend` directly.

| Backend | When | Notes |
|---------|------|-------|
| **iptables** (default) | `networking.nftables.enable = false`, firewalld off | Legacy `extraCommands` / `extraStopCommands` work; `filterForward` does not |
| **nftables** | `networking.nftables.enable = true` | Generated `nixos-fw` table; use `extraInputRules` for custom input accepts |
| **firewalld** | `services.firewalld.enable = true` | Different management model; see firewalld module docs |

**Switching to nftables.** Set `networking.nftables.enable = true`; keep using `networking.firewall.allowedTCPPorts` and friends—the nftables module translates them into the `input-allow` chain. Do **not** set `networking.firewall.extraCommands` or `extraStopCommands` with the nftables backend (eval assertions fail). `networking.nftables.rulesetFile` also conflicts with the generated firewall table.

**Custom rules on nftables.** Append nftables expressions via `networking.firewall.extraInputRules` (input), `extraForwardRules` (forward, needs `filterForward`), or `extraReversePathFilterRules` (rpfilter). These land in the generated `nixos-fw` chains—extend them, do not replace or duplicate the table at activation. For rules outside the firewall’s scope, use `networking.nftables.tables` carefully and avoid fighting `nixos-fw` on reload.

**Ops footgun — Docker.** Container runtimes (notably Docker) may install their own netfilter rules and, in some setups, interact badly with the NixOS firewall ([nixpkgs#111852](https://github.com/NixOS/nixpkgs/issues/111852)). Treat this as a known interaction to check when ports “mysteriously” open or close after container activity—not as “Docker always breaks NixOS firewalls.”

### Per-interface holes

Scope allows to a physical or virtual interface when global holes are too broad:

```nix
networking.firewall.interfaces."enp1s0".allowedTCPPorts = [ 8080 ];
```

The same `allowedUDPPorts` / `*PortRanges` keys exist under `interfaces."<name>"` as on the top-level firewall attrset.

### NetworkManager recipe

**Enable and delegate control.** `networking.networkmanager.enable = true` installs NetworkManager and its systemd units. Interactive control: `nmcli`, `nmtui`, or the desktop environment. Add human users to the `networkmanager` group (or rely on polkit rules your DE provides).

**Declarative profiles (optional).** `networking.networkmanager.ensureProfiles.profiles` holds keyfile-shaped connection profiles (see the option’s official example and [NetworkManager keyfile docs](https://networkmanager.dev/docs/api/latest/nm-settings-keyfile.html)). Profile keys follow NM’s ini sections (`connection`, `wifi`, `wifi-security`, `ipv4`, …)—do not invent undocumented keys; copy from an exported profile or the option example. Secrets can be substituted from `ensureProfiles.environmentFiles` via envsubst (illustrative pattern below).

**Coexistence with wpa_supplicant.** If `networking.wireless.enable = true` and NetworkManager are both on, mark wpa-managed interfaces as NM-unmanaged or you hit an assertion:

```nix
networking.networkmanager.unmanaged = [ "interface-name:wlp2s0" ];
```

Prefer one Wi‑Fi path on a given interface: NetworkManager *or* `networking.wireless`, not both fighting for the same netdev.

### Backend choice (interfaces and DHCP)

| Pattern | Typical use | How |
|---------|-------------|-----|
| NetworkManager | Laptops / desktops, Wi‑Fi roaming | `networking.networkmanager.enable = true`; `networkmanager` group |
| Scripted + `networking.interfaces` | Simple servers, static or DHCP | Default path when NM is off; configure `interfaces` / `useDHCP` |
| `systemd-networkd` | Servers wanting native `.network` units | `systemd.network.enable` + `systemd.network.networks.*`, or experimental `networking.useNetworkd` |

Do not let two managers fight over the same interface. `networking.useNetworkd` is marked experimental—prefer explicit `systemd.network.*` when you want networkd long-term.

**Interfaces and DHCP.** By default NixOS uses DHCP (`dhcpcd` on the scripted path) for interfaces without manual IPv4 addresses (`networking.useDHCP` defaults to `true`; hardware scans often set this in [hardware-configuration.nix](hardware-configuration.md)). Static setup uses `networking.interfaces.<name>.ipv4.addresses`, plus usually `networking.defaultGateway` and `networking.nameservers`. Prefer predictable names (`enp…`, `wlp…`) or pin names with `systemd.network.links` / udev; `networking.usePredictableInterfaceNames = false` restores classic `eth0`-style naming when you accept reorder risk.

**Wireless (host-level).** On desktops, use NetworkManager (`nmcli` / `nmtui` / DE settings), optionally with declarative profiles under `ensureProfiles`. Without NM, set `networking.wireless.enable = true` and usually `networking.wireless.interfaces`. Keep PSKs out of the store (`secretsFile` / `ext:` for wpa_supplicant, or NM `environmentFiles`)—see [Secrets strategies](secrets-strategies.md).

**Installer vs installed system.** The live ISO often has working networking (including Wi‑Fi via NetworkManager). `nixos-generate-config` does **not** enable wireless or NetworkManager in the generated config—declare a backend before expecting network after first boot.

### IPv6

IPv6 is enabled by default (`networking.enableIPv6` defaults to `true`): SLAAC, privacy/temporary addresses (`networking.tempAddresses`), and the usual dual-stack firewall behavior. Disable globally with `networking.enableIPv6 = false` only when you intend a v4-only host. See the manual IPv6 section for per-interface tuning.

## Examples

### Desktop: NetworkManager, firewall holes, SSH

```nix
{ config, pkgs, ... }: {
  networking.hostName = "demo";
  networking.networkmanager.enable = true;

  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 8080 ];
  };

  services.openssh.enable = true;  # opens TCP 22

  users.users.alice.extraGroups = [ "networkmanager" ];
}
```

### NetworkManager: declarative Wi‑Fi profile (illustrative)

Adapt section names and keys from the [ensureProfiles option example](https://nixos.org/manual/nixos/stable/options#opt-networking.networkmanager.ensureProfiles.profiles); this sketch shows the envsubst pattern for a PSK:

```nix
{
  networking.networkmanager = {
    enable = true;
    ensureProfiles = {
      environmentFiles = [ "/run/secrets/network-manager.env" ];
      profiles = {
        home-wifi = {
          connection = {
            id = "home-wifi";
            type = "wifi";
          };
          wifi = { ssid = "Home Wi-Fi"; mode = "infrastructure"; };
          wifi-security = {
            key-mgmt = "wpa-psk";
            psk = "$HOME_WIFI_PASSWORD";
          };
          ipv4.method = "auto";
          ipv6.method = "auto";
        };
      };
    };
  };
}
```

### nftables backend with allowed ports and custom input rule

```nix
{
  networking.nftables.enable = true;

  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 443 ];
    allowedUDPPorts = [ 51820 ];
    # nftables syntax — appended to input-allow
    extraInputRules = ''
      ip saddr 192.168.1.0/24 tcp dport 9100 accept
    '';
  };
}
```

### Per-interface allow (scripted server, one public NIC)

```nix
{
  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 22 ];           # global SSH
    interfaces."enp1s0".allowedTCPPorts = [ 80 443 ];  # web only on WAN
  };
}
```

### Minimal static Ethernet (scripted path)

Interface name must match the machine:

```nix
{
  networking.hostName = "srv";
  networking.useDHCP = false;
  networking.interfaces.enp1s0.ipv4.addresses = [{
    address = "192.168.1.10";
    prefixLength = 24;
  }];
  networking.defaultGateway = "192.168.1.1";
  networking.nameservers = [ "1.1.1.1" ];
}
```

## References

- [NixOS manual — Networking](https://nixos.org/manual/nixos/stable/index.html#sec-networking)
- [NixOS manual — NetworkManager](https://nixos.org/manual/nixos/stable/index.html#sec-networkmanager)
- [NixOS manual — IPv4 configuration](https://nixos.org/manual/nixos/stable/index.html#sec-ipv4)
- [NixOS manual — IPv6 configuration](https://nixos.org/manual/nixos/stable/index.html#sec-ipv6)
- [NixOS manual — Firewall](https://nixos.org/manual/nixos/stable/index.html#sec-firewall)
- [NixOS manual — Wireless](https://nixos.org/manual/nixos/stable/index.html#sec-wireless)
- [Option — `networking.hostName`](https://nixos.org/manual/nixos/stable/options#opt-networking.hostName)
- [Option — `networking.firewall.enable`](https://nixos.org/manual/nixos/stable/options#opt-networking.firewall.enable)
- [Option — `networking.firewall.backend`](https://nixos.org/manual/nixos/stable/options#opt-networking.firewall.backend)
- [Option — `networking.firewall.extraInputRules`](https://nixos.org/manual/nixos/stable/options#opt-networking.firewall.extraInputRules)
- [Option — `networking.nftables.enable`](https://nixos.org/manual/nixos/stable/options#opt-networking.nftables.enable)
- [Option — `networking.networkmanager.ensureProfiles.profiles`](https://nixos.org/manual/nixos/stable/options#opt-networking.networkmanager.ensureProfiles.profiles)
- [Option — `networking.enableIPv6`](https://nixos.org/manual/nixos/stable/options#opt-networking.enableIPv6)
- [Option — `networking.useNetworkd`](https://nixos.org/manual/nixos/stable/options#opt-networking.useNetworkd)
- [NixOS wiki — Firewall](https://wiki.nixos.org/wiki/Firewall) (nftables-oriented patterns; secondary to manual/options)
- [NixOS option search — `networking`](https://search.nixos.org/options?query=networking)
- [nixpkgs#111852 — Docker vs NixOS firewall interaction](https://github.com/NixOS/nixpkgs/issues/111852)

## See also

- [configuration.nix](configuration-nix.md)
- [hardware-configuration.nix](hardware-configuration.md)
- [Secrets strategies](secrets-strategies.md)
- [Rebuild, switch, boot, and test](../operations/rebuild-switch-boot-test.md)
- [Overlay networks](overlay-networks.md) — VPN/overlay fabric for multi-host reachability
- [Machine mesh](../../02-concepts/machine-mesh.md) — reachability is necessary but not sufficient for mesh trust
- [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md)
