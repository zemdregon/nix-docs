---
status: complete
---

# Users and Groups

## Overview

NixOS declares Unix accounts through `users.users` and `users.groups` in [configuration.nix](configuration-nix.md). Membership, SSH keys, home packages, and password material are option values evaluated into the system [generation](../../02-concepts/generation.md). How strictly the live `/etc/passwd` and `/etc/group` files track that declaration depends on `users.mutableUsers`.

## Details

**User records.** Each account is `users.users.<name> = { … }`. Setting `isNormalUser = true` marks a login account and sets `group` to `users`, `createHome` to `true`, `home` to `/home/<name>`, `useDefaultShell` to `true`, and `isSystemUser` to `false`. Exactly one of `isNormalUser` and `isSystemUser` must be true.

| Option | Role |
|--------|------|
| `isNormalUser` | Normal login user (home under `/home`, default shell) |
| `extraGroups` | Supplementary groups (e.g. `"wheel"` for `sudo`) |
| `packages` | Per-user packages in that user's profile |
| `openssh.authorizedKeys.keys` | Public keys for `~/.ssh/authorized_keys` |
| `uid` / `shell` / `description` | Optional overrides; uid is assigned automatically if omitted |

Full option docs: [search.nixos.org — `users.users`](https://search.nixos.org/options?query=users.users).

**Groups.** Declare named groups with `users.groups.<name> = { … }` (for example a fixed `gid`). Assign membership mainly via `users.users.<name>.extraGroups`. The primary group defaults from the account setup (`users` for normal users) unless you set `group`.

**Passwords (pick one pattern).** Several options control the account password; set only one to avoid surprising precedence. Prefer paths that keep plaintext out of the store:

| Pattern | When to use |
|---------|-------------|
| `hashedPasswordFile` | Path to a one-line file holding a `mkpasswd` hash; read on each activation. Prefer this over embedding hashes or plaintext in config. (`passwordFile` is a deprecated alias.) |
| `hashedPassword` / `initialHashedPassword` | Hash string in config (from `mkpasswd`). Lives in the store as a hash, not plaintext. |
| `initialPassword` | Plaintext initial password. World-readable in the Nix store — only for guests or throwaway bootstrap passwords you change immediately with `passwd`. |

With `users.mutableUsers = true`, password options apply when the account is **first created**; later `passwd` changes persist. With `mutableUsers = false`, activation always resets passwords from the configured options. If none are set, password login is disabled (SSH keys can still work). Details and secret hygiene: [Secrets strategies](secrets-strategies.md).

**Declarative vs imperative accounts.** `users.mutableUsers` (default `true`) controls merge vs replace of `/etc/passwd` and `/etc/group`:

| Value | Behavior |
|-------|----------|
| `true` | Imperative `useradd` / `groupadd` state can merge with declared users; initial passwords from config, existing passwords kept |
| `false` | Files are replaced from config; users removed from `users.users` disappear on rebuild; passwords reset from options |

**Bootstrap and SSH.** Fresh and headless installs often set `users.users.<admin>.openssh.authorizedKeys.keys` (and `extraGroups = [ "wheel" ]`) so the first rebuild enables key login without a console password.

### Boundaries (what this page is not)

- [Enterprise identity](enterprise-identity.md)—LDAP, SSSD, and directory-sourced accounts.
- OpenSSH [service module examples](../services/common-service-examples.md)—daemon options beyond declarative users.
- [Secrets strategies](secrets-strategies.md)—encrypted keys and deploy-time credential files.

## Examples

Immutable users with a hash file and an SSH key (no real secrets):

```nix
{ config, pkgs, ... }: {
  users.mutableUsers = false;

  users.groups.deploy = { };

  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" "deploy" ];
    # One line: output of `mkpasswd` (e.g. mkpasswd -m sha-512).
    # Place the file on the host; do not copy it into the Nix store.
    hashedPasswordFile = "/etc/nixos/secrets/alice.passwd.hash";
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAA…example alice@example"
    ];
  };
}
```

For a temporary guest with mutable users, `initialPassword = "changeme";` sets a first login password only; change it with `passwd` afterward. Prefer [secrets strategies](secrets-strategies.md) over committing real hashes or plaintext when the repo is shared.

## References

- [NixOS manual — User Management](https://nixos.org/manual/nixos/stable/#sec-user-management)
- [NixOS options — `users.users`](https://search.nixos.org/options?query=users.users)
- [NixOS options — `users.mutableUsers`](https://search.nixos.org/options?query=users.mutableUsers)
- [NixOS options — `users.users.<name>.hashedPasswordFile`](https://search.nixos.org/options?query=users.users.hashedPasswordFile)

## See also

- [configuration.nix](configuration-nix.md)
- [Secrets strategies](secrets-strategies.md)
- [Secrets management](../../14-security-and-trust/secrets-management.md)
