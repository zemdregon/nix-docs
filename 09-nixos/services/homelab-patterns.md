---
status: complete
last-checked: 2026-08
---

# Homelab Patterns

## Overview

Homelab and self-hosted stacks on NixOS rarely stop at `services.<app>.enable = true`. Most production-like setups repeat the same **composition**: enable the upstream module, bind the daemon to localhost, front it with a reverse proxy that terminates TLS, open only the ports you intend to expose, keep secrets out of the store, and plan for persistent state under `/var/lib`.

This page teaches those repeatable patterns—not a catalog of every `services.*` option tree. Start with [Service patterns](service-patterns.md) and [Common service examples](common-service-examples.md) for module shape and individual daemons; use this page when wiring several services into one host.

## Boundaries

**In scope:** how to compose proxy, TLS, firewall, secrets, and state for typical self-hosted apps (Forgejo, Jellyfin, Syncthing as *examples* of the pattern—not exhaustive module documentation).

**Out of scope:** per-service option reference, container orchestration beyond a pointer, backup job configuration (see [Backups and restore](../operations/backups-and-restore.md)), and overlay VPN setup details (see [Overlay networks](../configuration/overlay-networks.md)).

If you need the full option tree for one daemon, use [search.nixos.org/options](https://search.nixos.org/options) and that module's manual section—not this page.

## Details

### Decision: proxy, exposure, and reachability

| Goal | Reverse proxy | Exposure | Notes |
|------|---------------|----------|-------|
| Public HTTPS app on a domain | **nginx** or **Caddy** | Open 80/443; backend on `127.0.0.1` | nginx: mature `virtualHosts`, `locations`, `proxyPass`, `proxyWebsockets`, `enableACME`, `forceSSL`. Caddy: `services.caddy.enable`, `virtualHosts.<host>.extraConfig` with `reverse_proxy`; automatic HTTPS or `useACMEHost` + `security.acme`. |
| Multiple apps, one hostname (path routing) | **nginx** (preferred) or Caddy `handle_path` in `extraConfig` | Same as above | nginx `locations."/app1/"` / `locations."/app2/"` with distinct `proxyPass` targets. |
| LAN or tailnet only, no public DNS | **None** (direct) or proxy on overlay address | **No** public `openFirewall`; `services.tailscale.enable` (or WireGuard) | Reach `https://<host>.<tailnet>:<port>` or bind listeners to the overlay IP. Do not punch 80/443 on the public interface if the app is private. |
| Quick internal tool, trusted LAN | **Direct expose** | Module `openFirewall` or explicit `allowedTCPPorts` | Acceptable on a flat home LAN; avoid on VPS or mixed-trust networks. |
| App with built-in TLS and you accept bypassing a proxy | **Direct expose** | Open the app's port | Loses centralized TLS, path routing, and uniform headers; rarely ideal for internet-facing hosts. |

**nginx vs Caddy (homelab lens):** both integrate with `security.acme`. nginx fits complex `locations`, header tweaks, and modules already documented in nixpkgs. Caddy reduces Caddyfile-style boilerplate for simple `reverse_proxy` vhosts; advanced routing still belongs in `extraConfig`. Pick one proxy per host unless you have a deliberate split (e.g. nginx for legacy, Caddy for new).

### The usual stack

| Layer | Role | Typical NixOS surface |
|-------|------|------------------------|
| Application | The actual daemon (media, sync, git, …) | `services.<name>.enable` + module settings |
| Reverse proxy | Public hostname, path routing, TLS termination | `services.nginx` or `services.caddy` `virtualHosts` |
| TLS | Certificates and renewal | `security.acme` + proxy ACME options, or Caddy automatic HTTPS |
| Firewall | Inbound exposure | `services.<name>.openFirewall` when the module provides it; else `networking.firewall.allowedTCPPorts` |
| Secrets | Passwords, API keys, TLS material | Paths via agenix, sops-nix, or `environmentFiles` — [Secrets strategies](../configuration/secrets-strategies.md) |
| State | Databases, uploads, indexes | Module data dirs (often `/var/lib/<name>`); plan [backups](../operations/backups-and-restore.md) separately |

Many homelab modules (Syncthing, Jellyfin, Forgejo, Nextcloud, and similar) follow this shape: flip `enable`, tune a few settings, then integrate with proxy and firewall rather than exposing the app port directly on the internet.

### Reverse proxy in front of backends

**Pattern:** the application listens on `127.0.0.1` (or a Unix socket); only the proxy binds publicly on 80/443.

- **nginx:** declare `services.nginx.virtualHosts."app.example.org"` with `locations` containing `proxyPass` and, for WebSockets or server-sent events (SSE), `proxyWebsockets = true`. Search [nginx options](https://search.nixos.org/options?query=services.nginx) for exact attribute names on your channel.
- **Caddy:** `services.caddy.enable = true`; declare `services.caddy.virtualHosts."app.example.org"` with `extraConfig` containing a `reverse_proxy` directive to the backend URL. Search [Caddy options](https://search.nixos.org/options?query=services.caddy).

Benefits: one place for TLS, HTTP→HTTPS redirects, multiple apps on one host (path or subdomain routing), and tighter firewall rules (open 80/443 only, not every app port).

### TLS with ACME

Public homelab hostnames usually use Let's Encrypt (or another ACME CA).

**Shared ACME setup:** accept the provider terms and set a contact address once, then define per-host certificates:

```nix
security.acme = {
  acceptTerms = true;
  defaults.email = "admin@example.org";
  certs."app.example.org" = {
    # extraDomainNames = [ "www.app.example.org" ];
  };
};
```

Alternatively, set `email` on individual `security.acme.certs."<name>"` entries instead of `defaults.email`.

**nginx path:** on the matching `virtualHost`, set `enableACME = true` and `forceSSL = true` (or `useACMEHost` when reusing a cert defined above). The manual documents the module: [NixOS manual — ACME](https://nixos.org/manual/nixos/stable/#module-security-acme).

**Caddy path:** either let Caddy obtain certificates for public DNS names automatically, or set `virtualHosts.<host>.useACMEHost` to a name under `security.acme.certs` so Caddy uses the centrally managed cert files. Confirm ACME-related options on search.nixos.org for your release.

Keep ACME account keys and DNS API tokens out of evaluated config; reference decrypted paths from [Secrets strategies](../configuration/secrets-strategies.md).

### Firewall exposure

Prefer module-specific `services.<name>.openFirewall` when nixpkgs exposes it—it opens only the ports that service needs.

When no `openFirewall` exists, add explicit rules under `networking.firewall.allowedTCPPorts` / `allowedUDPPorts`. See [Networking](../configuration/networking.md).

**Tailnet-only exposure:** do not open public firewall holes; enable `services.tailscale.enable` (or another overlay), leave public `allowedTCPPorts` empty for the app, and reach the service over the tailnet. Overlay setup and interface patterns: [Overlay networks](../configuration/overlay-networks.md).

### Secrets and configuration

Never put database passwords, admin tokens, or private keys as string literals in `configuration.nix`—they end up in the world-readable store. Wire modules through `*File`, `credentialsFile`, `environmentFiles`, or paths under `/run/agenix` / `/run/secrets` populated by agenix or sops-nix. Details: [Secrets strategies](../configuration/secrets-strategies.md).

### Stateful services

Databases (PostgreSQL, Redis), file sync (Syncthing), media libraries (Jellyfin), and groupware (Nextcloud) persist data under `/var/lib` (or paths the module documents). Declarative Nix config describes *how* the service runs; backup, restore, and off-site copies are operational concerns—treat state dirs as first-class assets and wire [Backups and restore](../operations/backups-and-restore.md) for anything under `/var/lib` you cannot recreate from config alone.

### Failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| ACME renewal or initial issue fails; logs mention HTTP-01 challenge | Port 80 blocked upstream (ISP CGNAT, CDN orange-cloud, another host), or no listener on `/.well-known/acme-challenge/` | Ensure 80 reaches this host; for nginx use `enableACME` / webroot as documented; for DNS-only names use `security.acme` DNS challenge plugins. Do not assume HTTPS-only exposure works for HTTP-01. |
| App reachable on `:3000` (or module default) from the internet, bypassing TLS | `services.forgejo.openFirewall = true` (or similar) while also running a proxy | Disable module `openFirewall`; bind app to `127.0.0.1`; expose only 80/443 via nginx/Caddy. |
| Password or API key visible in `/nix/store` | Secret pasted in `configuration.nix`, `builtins.readFile` on a tracked file, or `pkgs.writeText` with credentials | Move to `environmentFile`, `passwordFile`, or agenix/sops paths under `/run`. |
| Forgejo/Git UI loads but live logs, CI streams, or Jellyfin notifications stall | Missing WebSocket/SSE proxy headers | Set `proxyWebsockets = true` on the nginx `location` (or equivalent Caddy `reverse_proxy` transport). Without it, long-poll and SSE connections hang behind the proxy. |
| TLS works on subdomain but not alias | Certificate SAN mismatch | Add `extraDomainNames` on `security.acme.certs."<primary>"` or `serverAliases` on the nginx vhost before renewal. |
| Database empty after reinstall despite "declarative" config | `/var/lib/postgresql` (or app data) not in backup scope | Generations restore *config*, not arbitrary `/var/lib` trees—see [Backups and restore](../operations/backups-and-restore.md). |

## Examples

### Minimal pattern: app + nginx + ACME + firewall

Illustrative composition (adjust option names per channel; backends and domains are placeholders):

```nix
{ ... }: {
  security.acme = {
    acceptTerms = true;
    defaults.email = "admin@example.org";
    certs."git.example.org" = { };
  };

  services.forgejo = {
    enable = true;
    settings.server = {
      DOMAIN = "git.example.org";
      HTTP_PORT = 3000;
      ROOT_URL = "https://git.example.org/";
    };
    # Do not set openFirewall when using a reverse proxy.
  };

  services.nginx = {
    enable = true;
    virtualHosts."git.example.org" = {
      enableACME = true;
      forceSSL = true;
      locations."/" = {
        proxyPass = "http://127.0.0.1:3000";
        proxyWebsockets = true;
      };
    };
  };

  networking.firewall.allowedTCPPorts = [ 80 443 ];
}
```

### Caddy reverse proxy + central ACME

```nix
{ config, ... }: {
  security.acme = {
    acceptTerms = true;
    defaults.email = "admin@example.org";
    certs."media.example.org" = {
      group = config.services.caddy.group;
    };
  };

  services.jellyfin.enable = true;
  # Jellyfin listens on localhost by default; confirm port in module docs.

  services.caddy = {
    enable = true;
    virtualHosts."media.example.org" = {
      useACMEHost = "media.example.org";
      extraConfig = ''
        reverse_proxy http://127.0.0.1:8096
      '';
    };
  };

  networking.firewall.allowedTCPPorts = [ 80 443 ];
}
```

### Path-based routing: two apps, one hostname

nginx routes `/git/` and `/sync/` to different localhost backends:

```nix
{ ... }: {
  security.acme = {
    acceptTerms = true;
    defaults.email = "admin@example.org";
  };

  services.forgejo = {
    enable = true;
    settings.server.HTTP_PORT = 3000;
  };
  services.syncthing.enable = true;
  # Confirm Syncthing GUI port in services.syncthing options.

  services.nginx = {
    enable = true;
    virtualHosts."home.example.org" = {
      enableACME = true;
      forceSSL = true;
      locations."/git/" = {
        proxyPass = "http://127.0.0.1:3000/";
        proxyWebsockets = true;
      };
      locations."/sync/" = {
        proxyPass = "http://127.0.0.1:8384/";
        proxyWebsockets = true;
      };
    };
  };

  networking.firewall.allowedTCPPorts = [ 80 443 ];
}
```

Trailing slashes on `proxyPass` and `location` paths must match what each app expects—check upstream docs if redirects loop.

### PostgreSQL backend for an app (localhost only)

Forgejo’s module can provision PostgreSQL for you when `database.type = "postgres"` (default `database.createDatabase = true` enables `services.postgresql` with matching DB/user). For apps without that helper, use a standalone [PostgreSQL snippet](common-service-examples.md) on the Unix socket—no TCP listen, no password in Nix:

```nix
{ ... }: {
  services.forgejo = {
    enable = true;
    database.type = "postgres";
    # Module enables postgresql and creates DB/user; use database.passwordFile for auth.
  };
}
```

For password auth or remote TCP, add module-specific settings and secrets via [Secrets strategies](../configuration/secrets-strategies.md)—do not inline passwords.

### Syncthing or Jellyfin without public exposure

Enable the service, skip wide firewall opens, reach it over Tailscale or WireGuard:

```nix
{ ... }: {
  services.syncthing = {
    enable = true;
    # GUI/API often defaults to a local port; confirm services.syncthing options.
  };

  services.tailscale.enable = true;
  # Access https://<host>.<tailnet>:<port> over the overlay; see overlay-networks.md.
}
```

### Secrets via environment file (sketch)

```nix
{ ... }: {
  services.some-app = {
    enable = true;
    environmentFile = "/run/secrets/some-app.env";
  };
}
```

Populate `/run/secrets/some-app.env` with agenix, sops-nix, or deploy-time material—not `builtins.readFile` in Nix.

### Homelab state and backups

Declarative service config does not snapshot `/var/lib/forgejo`, `/var/lib/jellyfin`, or PostgreSQL data directories. After composition is working, add Restic or Borg jobs targeting those paths—patterns in [Backups and restore](../operations/backups-and-restore.md).

## References

- [NixOS manual — ACME (`security.acme`)](https://nixos.org/manual/nixos/stable/#module-security-acme)
- [NixOS option search — `services.nginx`](https://search.nixos.org/options?query=services.nginx)
- [NixOS option search — `services.caddy`](https://search.nixos.org/options?query=services.caddy)

## See also

- [Service patterns](service-patterns.md) — module shape, `mkIf`, systemd wiring
- [Common service examples](common-service-examples.md) — OpenSSH, nginx, PostgreSQL snippets
- [Networking](../configuration/networking.md) — firewall and interfaces
- [Secrets strategies](../configuration/secrets-strategies.md) — keeping credentials out of the store
- [Overlay networks](../configuration/overlay-networks.md) — Tailscale, WireGuard, private reachability
- [Backups and restore](../operations/backups-and-restore.md) — `/var/lib` state and off-site copies
- [Docker and Podman](docker-and-podman.md) — upstream compose stacks vs declarative modules
