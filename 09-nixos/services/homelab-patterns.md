---
status: draft
---

# Homelab Patterns

## Overview

Homelab and self-hosted stacks on NixOS rarely stop at `services.<app>.enable = true`. Most production-like setups repeat the same **composition**: enable the upstream module, bind the daemon to localhost, front it with a reverse proxy that terminates TLS, open only the ports you intend to expose, keep secrets out of the store, and plan for persistent state under `/var/lib`.

This page teaches those repeatable patterns—not a catalog of every `services.*` option tree. Start with [Service patterns](service-patterns.md) and [Common service examples](common-service-examples.md) for module shape and individual daemons; use this page when wiring several services into one host.

## Details

### The usual stack

| Layer | Role | Typical NixOS surface |
|-------|------|------------------------|
| Application | The actual daemon (media, sync, git, …) | `services.<name>.enable` + module settings |
| Reverse proxy | Public hostname, path routing, TLS termination | `services.nginx` or `services.caddy` `virtualHosts` |
| TLS | Certificates and renewal | `security.acme` + proxy ACME options, or Caddy automatic HTTPS |
| Firewall | Inbound exposure | `services.<name>.openFirewall` when the module provides it; else `networking.firewall.allowedTCPPorts` |
| Secrets | Passwords, API keys, TLS material | Paths via agenix, sops-nix, or `environmentFiles` — [Secrets strategies](../configuration/secrets-strategies.md) |
| State | Databases, uploads, indexes | Module data dirs (often `/var/lib/<name>`); plan backups separately |

Many homelab modules (Syncthing, Jellyfin, Forgejo, Nextcloud, and similar) follow this shape: flip `enable`, tune a few settings, then integrate with proxy and firewall rather than exposing the app port directly on the internet.

### Reverse proxy in front of backends

**Pattern:** the application listens on `127.0.0.1` (or a Unix socket); only the proxy binds publicly on 80/443.

- **nginx:** declare `services.nginx.virtualHosts."app.example.org"` with `proxyPass` / `proxyWebsockets` (or `locations`) pointing at the backend URL. Search [nginx options](https://search.nixos.org/options?query=services.nginx) for exact attribute names on your channel.
- **Caddy:** declare `services.caddy.virtualHosts."app.example.org"` with `extraConfig` or module helpers to reverse-proxy to the backend. Search [Caddy options](https://search.nixos.org/options?query=services.caddy).

Benefits: one place for TLS, HTTP→HTTPS redirects, multiple apps on one host (path or subdomain routing), and tighter firewall rules (open 80/443 only, not every app port).

### TLS with ACME

Public homelab hostnames usually use Let's Encrypt (or another ACME CA).

**nginx path:** define certificates under `security.acme.certs."app.example.org"` (email, `extraDomainNames`, DNS challenge plugins if needed), then on the matching `virtualHost` set options such as `enableACME`, `useACME`, and `forceSSL`. The manual documents the `security.acme` module: [NixOS manual — ACME](https://nixos.org/manual/nixos/stable/#module-security-acme).

**Caddy path:** the NixOS Caddy module can obtain and renew certificates automatically when `virtualHosts` are configured for public DNS names—confirm `services.caddy` ACME-related options on search.nixos.org for your release.

Keep ACME account keys and DNS API tokens out of evaluated config; reference decrypted paths from [Secrets strategies](../configuration/secrets-strategies.md).

### Firewall exposure

Prefer module-specific `services.<name>.openFirewall` when nixpkgs exposes it—it opens only the ports that service needs.

When no `openFirewall` exists, add explicit rules under `networking.firewall.allowedTCPPorts` / `allowedUDPPorts`. See [Networking](../configuration/networking.md).

**Tailnet-only exposure:** do not open public firewall holes; bind the service or proxy to the overlay address (Tailscale, WireGuard, …) and restrict listeners accordingly. Overlay setup and interface patterns: [Overlay networks](../configuration/overlay-networks.md).

### Secrets and configuration

Never put database passwords, admin tokens, or private keys as string literals in `configuration.nix`—they end up in the world-readable store. Wire modules through `*File`, `credentialsFile`, `environmentFiles`, or paths under `/run/agenix` / `/run/secrets` populated by agenix or sops-nix. Details: [Secrets strategies](../configuration/secrets-strategies.md).

### Stateful services

Databases (PostgreSQL, Redis), file sync (Syncthing), media libraries (Jellyfin), and groupware (Nextcloud) persist data under `/var/lib` (or paths the module documents). Declarative Nix config describes *how* the service runs; backup, restore, and off-site copies are operational concerns—treat state dirs as first-class assets when planning the host.

## Examples

### Minimal pattern: app + nginx + ACME + firewall

Illustrative composition (adjust option names per channel; backends and domains are placeholders):

```nix
{ ... }: {
  # Backend: git forge on localhost only
  services.forgejo = {
    enable = true;
    settings.server = {
      DOMAIN = "git.example.org";
      HTTP_PORT = 3000;
      ROOT_URL = "https://git.example.org/";
    };
    # Many modules expose openFirewall; prefer binding to localhost + proxy instead.
  };

  security.acme.certs."git.example.org" = {
    email = "admin@example.org";
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
