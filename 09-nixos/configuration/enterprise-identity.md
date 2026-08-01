---
status: complete
---

# Enterprise identity

## Overview

Enterprise Linux hosts usually resolve users and groups from LDAP or Active Directory (AD) instead of only local `/etc/passwd`. On NixOS the common stack is **SSSD** (System Security Services Daemon) for NSS/PAM lookups, optional **realmd** for domain enrollment helpers, and **Kerberos** (`security.krb5`) when the directory uses tickets. Domain accounts are not declared in `users.users`; SSSD registers NSS modules so `getent passwd`, login, and sudo see directory users after a [rebuild](../operations/rebuild-switch-boot-test.md).

This page covers **patterns**—not a full AD/LDAP tutorial. Domain-specific DNS, trust, and GPO behavior vary; verify against your directory and the NixOS option docs before production use.

## Details

### Stack roles

| Piece | NixOS hook | Role |
|-------|------------|------|
| SSSD | `services.sssd.enable` | NSS/PAM (and optional SSH keys, subuid, KCM) via `sssd.conf` |
| realmd | `services.realmd.enable` | DBus service for `realm` CLI enrollment (`realm join`, …) |
| Kerberos | `security.krb5.enable` + `settings` | Ticket acquisition for AD/LDAP auth providers |
| Home dirs | `security.pam.makeHomeDir` | Create `$HOME` on first login for users not in `users.users` |
| Join tools | `environment.systemPackages` | Often `adcli`, `krb5`; enabling `services.sssd` adds the daemon, not these CLIs |

Declarative local accounts remain in [Users and groups](users-and-groups.md). Directory users are resolved through SSSD at lookup time and are **not** listed in `users.users`. With `users.mutableUsers = true` (default), imperative local accounts can coexist with declared ones; with `false`, `/etc/passwd` and `/etc/group` are replaced from `users.users` / `users.groups` on each activation (imperative locals disappear), but directory lookups still work via NSS. Many AD clients keep the default so ad-hoc local accounts survive rebuilds.

### `services.sssd`

The module (`nixpkgs/nixos/modules/services/misc/sssd.nix`) enables the `sssd` systemd unit, wires NSS databases (`passwd`, `group`, `shadow`, `services`, optionally `subuid`/`subgid`), and renders `/var/lib/sssd/sssd.conf` at start.

**Configuration shape (pick one).** `services.sssd.settings` is an INI attrset (via `formats.ini`); `services.sssd.config` is raw INI lines. They are **mutually exclusive**—the module asserts exactly one is non-empty. Prefer `settings` in NixOS config; use `config` only when you already have a line-oriented `sssd.conf` to port.

**Module options beyond `sssd.conf`:**

| Option | Purpose |
|--------|---------|
| `sshAuthorizedKeysIntegration` | sshd uses `sss_ssh_authorizedkeys`; requires `ssh` in SSSD `services` |
| `kcm` | SSSD Kerberos Cache Manager; sets `default_ccache_name = KCM:` |
| `subIDsIntegration` | NSS `subuid`/`subgid` from SSS (containers/rootless) |
| `environmentFile` | systemd `EnvironmentFile` for secrets referenced as `$VAR` in config (not in the store) |

SSSD depends on **nscd** and **network-online**; it runs before user sessions. The module writes `/var/lib/sssd/sssd.conf` and exposes it at `/etc/sssd/sssd.conf` so tools like `sssctl` can read the live config.

**Active Directory (community pattern).** The [NixOS Wiki AD client note](https://wiki.nixos.org/wiki/Active_Directory_Client) describes a typical domain section with `id_provider = ad`, Kerberos enabled, and DNS pointing at domain controllers—confirm `ad_domain`, `krb5_realm`, and time sync (`services.timesyncd` or `chrony`) on your network. Treat wiki steps as a checklist, not guaranteed defaults.

**LDAP.** Use an LDAP domain section (`id_provider = ldap`, bind DN/password or TLS client cert). Bind passwords belong in `environmentFile` placeholders (see [Secrets strategies](secrets-strategies.md)), not evaluated Nix strings.

### `services.realmd`

`services.realmd.enable` installs **realmd**, enables DBus, and starts the `realmd` service—enrollment orchestration for AD/realm membership. It does **not** replace SSSD configuration; you still define SSSD domains after join.

Community reports note **`realm join` can be flaky** on NixOS; many admins configure Kerberos/realmd, then run **`adcli join`** (or join from another host) and rely on SSSD for ongoing lookups. Test join paths in your lab; fallback procedures are site-specific.

### Kerberos and PAM

For AD and many LDAP deployments, enable client Kerberos:

```nix
security.krb5.enable = true;
security.krb5.settings = {
  libdefaults = {
    default_realm = "EXAMPLE.COM";
  };
  # realms, domain_realm, KDC hostnames, … per your KDC layout
};
```

When `services.sssd.kcm = true`, ticket caching goes through SSSD’s KCM responder (module sets `default_ccache_name = KCM:`).

Domain users need home directories created on first login:

```nix
security.pam.makeHomeDir = true;
security.pam.makeHomeDir.skelDirectory = "/etc/skel";
```

Some community AD guides suggest shorter nscd `passwd`/`group` cache TTLs while debugging stale IDs. SSSD already requires nscd; tune via `services.nscd.settings` only when you understand cache vs directory latency tradeoffs.

### Secrets and networking

- **Never** put bind passwords or `ldap_default_authtok` in the Nix store. Use `services.sssd.environmentFile` with placeholders in `settings` / `config`, populated from a root-only path or [secrets tooling](../../14-security-and-trust/secrets-management.md). See [Secrets strategies](secrets-strategies.md).
- **DNS and reachability**: clients must resolve SRV records and reach LDAP/Kerberos ports; align [Networking](networking.md) (firewall, DNS servers, search domain) with directory docs. Time skew breaks Kerberos.

### Troubleshooting sketch

| Symptom | Checks |
|---------|--------|
| `getent passwd` misses domain user | `systemctl status sssd`; `sssctl domain-status`; NSS order includes `sss` |
| Auth fails, local works | Kerberos ticket (`klist`), clock sync, PAM stack, SSSD logs |
| SSH key from AD | `ssh` in SSSD services + `sshAuthorizedKeysIntegration` |
| Stale groups | nscd cache TTL; `sss_cache -E` during tests |

More general NixOS debug flow: [Troubleshooting](../operations/troubleshooting.md).

### Boundaries (what this page is not)

- [Secrets strategies](secrets-strategies.md)—agenix, sops-nix, and deploy-time credential delivery.
- Generic [networking](networking.md)—interfaces, firewall, and DNS outside identity integration.
- [Home Manager](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md) user dotfiles and per-user packages.

## Examples

Examples below match the option shapes in `nixpkgs` modules (`sssd.nix`, `realmd.nix`, `security/krb5`, `pam.nix`). End-to-end login against a real directory cannot be verified offline—you need working DNS, time sync, domain join, and reachable KDC/LDAP in a lab or production forest.

**Minimal AD-oriented SSSD (`settings`)**—illustrative names only; replace realm, domain, and DC discovery with your AD layout:

```nix
{ config, pkgs, ... }: {
  services.sssd.enable = true;
  services.sssd.settings = {
    sssd = {
      services = "nss, pam";
      domains = "example.com";
    };
    nss = { };
    pam = { };
    "domain/example.com" = {
      id_provider = "ad";
      ad_domain = "example.com";
      krb5_realm = "EXAMPLE.COM";
      # realmd/adcli join and DNS must match your forest
    };
  };

  security.krb5.enable = true;
  security.pam.makeHomeDir = true;

  environment.systemPackages = [ pkgs.adcli pkgs.krb5 ];
}
```

**LDAP bind secret via `environmentFile`** (placeholder in `settings`, secret in the env file—not in the Nix store):

```nix
services.sssd.enable = true;
services.sssd.environmentFile = "/var/lib/secrets/sssd.env";
services.sssd.settings = {
  "domain/corp" = {
    id_provider = "ldap";
    ldap_uri = "ldaps://ldap.corp.example";
    ldap_default_bind_dn = "cn=nixos-bind,ou=svc,dc=corp,dc=example";
    ldap_default_authtok = "$SSSD_LDAP_DEFAULT_AUTHTOK";
  };
};
# /var/lib/secrets/sssd.env (root 0600, not in Git):
# SSSD_LDAP_DEFAULT_AUTHTOK=…
```

**Raw `config` alternative**—same INI as above, but only if you are not using `settings`:

```nix
# Do not set services.sssd.settings when using config.
services.sssd.config = ''
  [domain/example.com]
  id_provider = ad
  ad_domain = example.com
'';
```

**realmd + optional SSH keys from directory:**

```nix
services.realmd.enable = true;
services.sssd.enable = true;
services.sssd.sshAuthorizedKeysIntegration = true;
# In settings: sssd.services must include "ssh"
```

## References

- [NixOS options — `services.sssd`](https://search.nixos.org/options?query=services.sssd)
- [NixOS options — `services.realmd`](https://search.nixos.org/options?query=services.realmd)
- [NixOS options — `security.krb5`](https://search.nixos.org/options?query=security.krb5)
- [NixOS options — `security.pam.makeHomeDir`](https://search.nixos.org/options?query=security.pam.makeHomeDir)
- [NixOS Wiki — Active Directory Client](https://wiki.nixos.org/wiki/Active_Directory_Client) (community patterns; verify against modules)
- Upstream: [SSSD documentation](https://sssd.io/docs/)

## See also

- [Users and groups](users-and-groups.md)
- [Secrets strategies](secrets-strategies.md)
- [Networking](networking.md)
- [Troubleshooting](../operations/troubleshooting.md)
- [Secrets management](../../14-security-and-trust/secrets-management.md)
