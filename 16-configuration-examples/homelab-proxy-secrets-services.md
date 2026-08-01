---
status: complete
last-checked: 2026-08
---

# Homelab proxy, services, and secrets

## Overview

This walkthrough is a **host-role module fragment**: one public-facing homelab machine that terminates TLS at a reverse proxy, runs an app on localhost, opens only the firewall holes it needs, and wires service credentials through **sops-nix** (with a pointer to [agenix](../12-deployment-and-infra/agenix-sops-nix.md) as an alternative). It is not a full disk layout, hardware profile, or fleet repo—adapt the snippets into your flake `hosts/` tree or standalone `configuration.nix`.

The composition matches what [Homelab patterns](../09-nixos/services/homelab-patterns.md) teaches: proxy in front, ACME for public DNS names, backend bound to `127.0.0.1`, secrets as runtime paths—not evaluated strings.

## Details

### What this fragment covers

| Concern | In this example | Deep dive |
|---------|-----------------|-----------|
| Reverse proxy + ACME | nginx `virtualHosts` → Forgejo on `127.0.0.1:3000` | [Homelab patterns](../09-nixos/services/homelab-patterns.md) |
| App + database | `services.forgejo` with integrated PostgreSQL | [Common service examples](../09-nixos/services/common-service-examples.md) |
| Firewall | nftables backend, TCP 80/443 only | [Networking](../09-nixos/configuration/networking.md), fixture [networking-nftables-minimal.nix](../meta/examples/networking-nftables-minimal.nix) |
| Secrets | `sops.secrets.*` → `/run/secrets/…` → `database.passwordFile` | [Secrets strategies](../09-nixos/configuration/secrets-strategies.md), [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md) |
| Store safety | Path options only; no plaintext; no `builtins.readFile` on decrypt paths | [Secrets management](../14-security-and-trust/secrets-management.md) |
| Flake wiring | `sops-nix` input + `specialArgs` | [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md) |

**Tailnet-only variant:** skip public `allowedTCPPorts` for the app, enable an overlay ([Overlay networks](../09-nixos/configuration/overlay-networks.md)), and reach the service over Tailscale or WireGuard instead of punching 80/443 on the WAN interface.

### Domains composed

- [Generation](../02-concepts/generation.md) — evaluated config becomes an immutable system generation after `nixos-rebuild switch`
- [Homelab patterns](../09-nixos/services/homelab-patterns.md) — proxy, TLS, firewall, and multi-service composition
- [Networking](../09-nixos/configuration/networking.md) — stateful firewall, nftables backend, per-interface holes
- [Secrets strategies](../09-nixos/configuration/secrets-strategies.md) — `*File` options and ciphertext-in-Git flow
- [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md) — decrypt at activation; agenix uses `age.secrets.*` → `/run/agenix/…` if you prefer file-per-secret age
- [Secrets management](../14-security-and-trust/secrets-management.md) — why the store is not a vault
- [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md) — `nixosConfigurations`, `specialArgs`, module imports

### Rules for this example

1. **Proxy terminates TLS.** Forgejo listens on localhost; nginx holds the public hostname and ACME certificate.
2. **Do not double-expose.** Leave `services.forgejo.openFirewall` unset (default off)—open 80/443 on the firewall, not the app port.
3. **Secrets are paths.** Declare `sops.secrets.<name>`; pass `config.sops.secrets.<name>.path` into module `*File` options. Never paste passwords in Nix; never `builtins.readFile` a decrypted `/run/secrets/…` path into evaluation.
4. **Discover option names.** Attribute trees differ by channel—confirm on [search.nixos.org/options](https://search.nixos.org/options) before copying to production.

### `stateVersion`

When you merge this fragment into a real host module, set `system.stateVersion` once to the NixOS release present at **first install** on that machine (for example `"26.05"`). It gates stateful defaults for databases and services; do not bump it on every upgrade. This fragment omits disk and bootloader facts—your host module or `hardware-configuration.nix` should set it alongside platform imports.

## Examples

Multi-file layout (paths are illustrative):

```
.
├── flake.nix
├── hosts/
│   └── git/
│       └── default.nix          # host role (this walkthrough)
└── secrets/
    ├── homelab.yaml             # SOPS-encrypted (ciphertext in Git)
    └── .sops.yaml               # creation rules / age recipients
```

### `flake.nix` — pin nixpkgs and sops-nix

```nix
{
  description = "Homelab git host (proxy + secrets)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    sops-nix.url = "github:Mic92/sops-nix";
  };

  outputs = { self, nixpkgs, sops-nix, ... }@inputs: {
    nixosConfigurations.git = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      modules = [
        sops-nix.nixosModules.sops
        ./hosts/git
      ];
    };
  };
}
```

Rebuild with `sudo nixos-rebuild switch --flake .#git` on the target (hostname need not match the output name, but keeping them aligned avoids confusion).

### `secrets/.sops.yaml` — recipients (illustrative)

Edit with the `sops` CLI; host SSH keys converted to age pubkeys are the usual homelab recipients. This file is **not** imported into Nix evaluation—it drives encryption only.

```yaml
creation_rules:
  - path_regex: homelab\.yaml$
    age: >-
      age1examplehostkeypubplaceholder...
```

See [sops-nix](https://github.com/Mic92/sops-nix) for `ssh-to-age` and team recipient workflows.

### `secrets/homelab.yaml` — encrypted document (structure only)

Plaintext values live only in the encrypted blob on disk after `sops homelab.yaml`. Commit ciphertext, not decrypted content.

```yaml
forgejo:
  database_password: ENC[AES256_GCM,data:…,type:str]
```

### `hosts/git/default.nix` — proxy, app, firewall, secrets

nginx + ACME + Forgejo + PostgreSQL + sops-nix + nftables firewall. Domains and paths are placeholders.

```nix
{ config, inputs, pkgs, ... }:
{
  networking.hostName = "git";

  # Set once at first install on this machine; see Details above.
  system.stateVersion = "26.05";

  # --- Secrets (sops-nix) ---
  sops.defaultSopsFile = ../../secrets/homelab.yaml;
  sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];

  sops.secrets.forgejo-database-password = { };

  # --- TLS (ACME) ---
  security.acme = {
    acceptTerms = true;
    defaults.email = "admin@example.org";
    certs."git.example.org" = { };
  };

  # --- Application (localhost backend) ---
  services.forgejo = {
    enable = true;
    database.type = "postgres";
    database.passwordFile = config.sops.secrets.forgejo-database-password.path;
    settings.server = {
      DOMAIN = "git.example.org";
      HTTP_PORT = 3000;
      ROOT_URL = "https://git.example.org/";
    };
    # Do not set openFirewall when nginx terminates TLS publicly.
  };

  # --- Reverse proxy ---
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

  # --- Firewall (nftables backend) ---
  # Fixture: ../meta/examples/networking-nftables-minimal.nix
  networking.nftables.enable = true;

  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 80 443 ];
    # Optional: scope web ports to one NIC instead of globally:
    # interfaces."enp1s0".allowedTCPPorts = [ 80 443 ];
  };
}
```

After activation, `config.sops.secrets.forgejo-database-password.path` resolves to `/run/secrets/forgejo-database-password` (default layout). PostgreSQL reads the password file at runtime; the plaintext never enters the Nix store.

### agenix alternative (sketch)

If you prefer one `.age` file per secret, swap the sops-nix import for [agenix](../12-deployment-and-infra/agenix-sops-nix.md):

```nix
# imports = [ inputs.agenix.nixosModules.default ];
# age.secrets.forgejo-database-password.file = ../../secrets/forgejo-database-password.age;
# services.forgejo.database.passwordFile = config.age.secrets.forgejo-database-password.path;
# → /run/agenix/forgejo-database-password
```

### Tailnet-only exposure (contrast)

For an admin UI that should not be on the public internet, omit WAN firewall holes for that service and use an overlay:

```nix
{
  services.syncthing.enable = true;
  services.tailscale.enable = true;
  # No networking.firewall.allowedTCPPorts for Syncthing — reach over the tailnet.
}
```

See [Overlay networks](../09-nixos/configuration/overlay-networks.md) for interface and routing patterns.

### Failure modes (quick)

| Symptom | Likely cause |
|---------|----------------|
| Forgejo reachable on `:3000` from WAN | Module `openFirewall` enabled or app bound to `0.0.0.0` |
| ACME fails | Port 80 blocked upstream; confirm nginx `enableACME` and firewall allow 80 |
| Password in `/nix/store` | Secret inlined in Nix or `builtins.readFile` on a decrypted path |
| Web UI loads but live logs stall | Missing `proxyWebsockets = true` on the nginx `location` |

## References

- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/)
- [NixOS manual — ACME (`security.acme`)](https://nixos.org/manual/nixos/stable/#module-security-acme)
- [Mic92/sops-nix](https://github.com/Mic92/sops-nix) — SOPS decrypt at activation; `sops.secrets.*`
- [ryantm/agenix](https://github.com/ryantm/agenix) — age-encrypted secrets; `age.secrets.*`
- [NixOS option search](https://search.nixos.org/options) — confirm `services.forgejo`, `services.nginx`, and firewall option names on your channel

## See also

- [Homelab patterns](../09-nixos/services/homelab-patterns.md) — decision table: nginx vs Caddy, tailnet-only exposure
- [Common service examples](../09-nixos/services/common-service-examples.md) — OpenSSH, nginx, PostgreSQL snippets
- [Networking](../09-nixos/configuration/networking.md) — firewall backends and `extraInputRules`
- [Overlay networks](../09-nixos/configuration/overlay-networks.md) — Tailscale / WireGuard without public port holes
- [Secrets strategies](../09-nixos/configuration/secrets-strategies.md) — pattern matrix for `*File` options
- [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md) — tool comparison and module usage
- [Secrets management](../14-security-and-trust/secrets-management.md) — store readability and trust boundaries
- [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md) — `specialArgs`, checks, rebuild
- [Minimal flake NixOS host](minimal-flake-nixos-host.md) — slimmer single-host flake layout
- [Multi-host config repo](multi-host-config-repo.md) — fleet `hosts/` / `modules/` structure
