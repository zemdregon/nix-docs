---
status: complete
---

# Common Service Examples

## Overview

Most NixOS services follow the same shape: flip an `enable` flag, then set a handful of typed options under `services.<name>.*`. This page shows a few high-level patterns people actually use—not a catalog of every module. For the shared conventions (`mkIf`, systemd units, option trees), see [Service patterns](service-patterns.md).

Look up exact names, types, and defaults on [search.nixos.org/options](https://search.nixos.org/options) or in the [NixOS manual](https://nixos.org/manual/nixos/stable/) before copying snippets into production.

## Details

**Enable first.** Almost every service module exposes `services.<name>.enable`. Setting it to `true` pulls in packages, systemd units, users/groups, and default config. Leaving it unset/`false` keeps that service out of the system.

**Discover options, don’t invent them.** Option trees differ per module (`ports` vs `port`, nested `settings`, `virtualHosts`, …). Search for the service name on [search.nixos.org](https://search.nixos.org/options); wrong attribute names fail evaluation.

**Firewall is often separate.** Enabling a daemon does not always open inbound ports. OpenSSH is an exception: with `services.openssh.enable = true`, TCP port 22 is opened by default (`openFirewall` defaults to `true`). Many others (including nginx) need an explicit `networking.firewall.allowedTCPPorts` / `allowedUDPPorts` entry. See [Networking](../configuration/networking.md).

**No secrets in plain config.** Passwords, TLS keys, and API tokens do not belong as string literals in `configuration.nix`. Use the approaches in [Secrets strategies](../configuration/secrets-strategies.md) (age/sops, `environmentFiles`, runtime files, and so on).

**Users and keys.** Declarative SSH authorized keys live under `users.users.<name>.openssh.authorizedKeys`; see [Users and groups](../configuration/users-and-groups.md).

## Examples

### OpenSSH

Minimal remote access with key auth and root logins disabled. Port 22 is opened in the firewall automatically unless you set `services.openssh.openFirewall = false`.

```nix
{
  services.openssh = {
    enable = true;
    ports = [ 22 ];
    settings = {
      PasswordAuthentication = false;
      PermitRootLogin = "no";
    };
  };

  users.users.alice.openssh.authorizedKeys.keys = [
    "ssh-ed25519 AAAA...placeholder... alice@laptop"
  ];
}
```

### nginx + firewall

Enable nginx, declare a virtual host, and open HTTP/HTTPS yourself—the nginx module does not open those ports by default.

```nix
{
  services.nginx = {
    enable = true;
    virtualHosts."docs.example.org" = {
      root = "/var/www/docs.example.org";
    };
  };

  networking.firewall.allowedTCPPorts = [ 80 443 ];
}
```

For TLS via ACME, see options such as `services.nginx.virtualHosts.<name>.enableACME` / `forceSSL` and `security.acme.*` on search.nixos.org—keep certificates and account email out of committed secrets where possible.

### PostgreSQL (local)

Database for local apps over the Unix socket. No TCP listen and no password in the config; peer/local auth is the usual default. Do not paste DB passwords into Nix—see [Secrets strategies](../configuration/secrets-strategies.md) if a password is required.

```nix
{
  services.postgresql = {
    enable = true;
    ensureDatabases = [ "app" ];
    ensureUsers = [
      {
        name = "app";
        ensureDBOwnership = true;
      }
    ];
  };
}
```

`ensureDBOwnership` requires a database with the same name as the user in `ensureDatabases`. Remote TCP access needs extra options (`enableTCPIP`, authentication, and firewall ports)—look those up before exposing PostgreSQL on the network.

### Custom oneshot unit (`systemd.services`)

When no upstream module exists, declare a unit directly. Illustrative fragment: [systemd-oneshot-service.nix](../../meta/examples/systemd-oneshot-service.nix).

```nix
{ pkgs, ... }: {
  systemd.services.my-backup = {
    description = "Run backup script once at boot";
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      ExecStart = "${pkgs.writeShellScript "backup" ''
        echo backup > /var/lib/backup-ran
      ''}";
    };
    wantedBy = [ "multi-user.target" ];
  };
}
```

## References

- [NixOS option search](https://search.nixos.org/options) — channel-scoped (`26.05` stable as of 2026-07)
- [NixOS manual (stable) — configuration / services](https://nixos.org/manual/nixos/stable/)
- [NixOS manual — Secure Shell Access](https://nixos.org/manual/nixos/stable/#sec-ssh)
- [NixOS manual — Firewall](https://nixos.org/manual/nixos/stable/#sec-firewall)

## See also

- [Service patterns](service-patterns.md)
- [Networking](../configuration/networking.md)
- [Secrets strategies](../configuration/secrets-strategies.md)
- [Users and groups](../configuration/users-and-groups.md)
- [Writing a module](../modules/writing-a-module.md)
