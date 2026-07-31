---
status: complete
---

# Remote Deploy

## Overview

`nixos-rebuild` can build and/or activate a NixOS configuration on a remote machine over SSH. Point `--build-host` and/or `--target-host` at `user@host` (or a hostname). This is the day-to-day remote update path after the machine already runs NixOS—contrast [nixos-anywhere](../installation/nixos-anywhere.md), which is for install-time remote installation.

Actions (`switch`, `boot`, `test`, …) are the same as local rebuilds; see [rebuild / switch / boot / test](rebuild-switch-boot-test.md). Flag names below match current `nixos-rebuild-ng` (`man nixos-rebuild`; NixOS 25.11+ default, sole frontend from 26.05).

## Details

### Build host vs target host

| Flag | Role |
|------|------|
| `--build-host user@host` | Build the new configuration on that host (SSH + Nix builds required). If `--target-host` is unset, the result is copied back to the local machine when done. |
| `--target-host user@host` | Activate on the remote host instead of locally. `switch`, `boot`, and `test` need root on the remote (or elevation—below). If `--build-host` is unset or empty, the build runs **locally**. |

Both may be set, and may name different hosts. Host strings may include a remote user (`user@host`). Extra SSH flags go in `NIX_SSHOPTS` (see `man nixos-rebuild`). Optional: `--use-substitutes` adds `--use-substitutes` to each `nix copy` when a build or target host is set—useful when the remote’s path to a binary cache is faster than host-to-host copy.

SSH must already work to the build/target hosts (keys, `known_hosts`, optional `~/.ssh/config` aliases). Activation still needs root on the target unless you elevate.

`nixos-rebuild` honors `nixpkgs.crossSystem` from the evaluated config and **does not** probe the target’s real architecture; that setting must match the target platform or activation fails.

### Privilege elevation on the target

Non-root SSH users cannot run activation as root without elevation. Prefer current flags from `nixos-rebuild(8)`:

- `--elevate=sudo` (alias `--sudo`) — prefix remote activation with `sudo` (`NIX_SUDOOPTS` for extra sudo flags)
- `--elevate=run0` — systemd/polkit elevation (remote uses `systemd-run --uid=0 --pipe`; passwordless polkit grant usually required unless prompting)
- `--ask-elevate-password` / `-S` — prompt locally for a password and feed it to elevation (implies `--elevate=sudo` if `--elevate` is omitted); `--ask-sudo-password` is an alias for `--elevate=sudo --ask-elevate-password`

`--use-remote-sudo` is a **deprecated** alias for `--elevate=sudo`.

### Configuration location (not the remote’s `/etc/nixos`)

Remote deploy usually evaluates a config from the **deploying** machine, not whatever sits in the target’s `/etc/nixos`. Typical choices:

- Flake: `nixos-rebuild switch --flake .#hostname --target-host user@host …`
- Classic: `-I nixos-config=/path/to/configuration.nix` (or documented `--file` / `--attr` forms)

Without that, you risk building the wrong system or the local default.

### Skip re-exec (`--no-reexec` / `--fast`)

By default, `nixos-rebuild` builds `config.system.build.nixos-rebuild` from the channel/flake and re-execs into it. That can fail when the build target architecture differs from the machine running the CLI (classic “Exec format error” when deploying across platforms).

Use `--no-reexec` to keep the current `nixos-rebuild` binary. `--fast` remains a **deprecated** alias for `--no-reexec` on `nixos-rebuild-ng`.

### Pre-built closures

`--store-path /nix/store/…-nixos-system-…` activates a closure built elsewhere (CI, dedicated builder) with `switch` / `boot` / `test` / `dry-activate`. It skips evaluate/build; `--build-host` is ignored. Mutually exclusive with `--flake` / `--file` / `--attr` / `--rollback`.

### Multi-host fleets vs install-time tools

| Approach | Fit |
|----------|-----|
| `nixos-rebuild --target-host` / `--build-host` | One (or a few) hosts; same CLI as local rebuild; no fleet inventory |
| [Colmena](../../12-deployment-and-infra/colmena.md) | Hive of many nodes: tags, parallel apply, shared defaults |
| [deploy-rs](../../12-deployment-and-infra/deploy-rs.md) | Flake `deploy.nodes` / profiles; magic-rollback after SSH activation |

For first-time remote installation (not ongoing rebuilds), use [nixos-anywhere](../installation/nixos-anywhere.md). SSH/Nix trust and activation failures: [troubleshooting](troubleshooting.md).

## Examples

Activate on a remote host as a non-root user (elevation via sudo):

```bash
nixos-rebuild switch --target-host user@host --elevate=sudo
# or: --sudo
# deprecated alias: --use-remote-sudo
```

Flake attribute plus a separate build host; skip re-exec when cross-platform:

```bash
nixos-rebuild switch \
  --flake .#hostname \
  --build-host builder@buildbox \
  --target-host user@host \
  --elevate=sudo \
  --no-reexec
```

Extra SSH options:

```bash
export NIX_SSHOPTS="-p 2222 -i ~/.ssh/deploy_ed25519"
nixos-rebuild switch --target-host user@host --elevate=sudo --flake .#hostname
```

Password prompt for remote sudo (implies sudo elevation):

```bash
nixos-rebuild switch --target-host user@host --ask-elevate-password --flake .#hostname
```

## See also

- [rebuild / switch / boot / test](rebuild-switch-boot-test.md)
- [troubleshooting](troubleshooting.md)
- [Colmena](../../12-deployment-and-infra/colmena.md)
- [deploy-rs](../../12-deployment-and-infra/deploy-rs.md)
- [Machine mesh](../../02-concepts/machine-mesh.md)
- [Clan and mesh](../../12-deployment-and-infra/clan-and-mesh.md)
- [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md)
- [nixos-anywhere](../installation/nixos-anywhere.md)

## References

- `man nixos-rebuild` — primary reference for `--build-host`, `--target-host`, `--elevate`, `--no-reexec`, `--store-path`, and `NIX_SSHOPTS` (verified against nixos-rebuild-ng; flag names vary on older Bash `nixos-rebuild`)
- [nixos-rebuild.8 (nixpkgs, nixos-rebuild-ng)](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/ni/nixos-rebuild-ng/nixos-rebuild.8.scd)
- [NixOS manual — Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)
- [NixOS Wiki — nixos-rebuild (Deploying on other machines)](https://wiki.nixos.org/wiki/Nixos-rebuild) — secondary; prefer the man page for flags
