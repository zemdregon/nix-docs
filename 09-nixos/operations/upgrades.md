---
status: complete
---

# Upgrades

## Overview

Keep NixOS current by refreshing the expression source you track, then rebuilding. The workflow splits on how `/etc/nixos` is wired:

- **Channel hosts:** refresh root’s `nixos` channel, then rebuild (`nixos-rebuild switch --upgrade`, or `nix-channel --update` plus `nixos-rebuild switch`).
- **Flake hosts:** bump pins in `flake.lock` (`nix flake update` or a single input), then rebuild with `--flake`.

Channels ship Nix expressions plus pre-built binaries; which channel you subscribe to controls how aggressive updates are. Stable lines (`nixos-YY.MM`, e.g. the current stable on [channels.nixos.org](https://channels.nixos.org)) take conservative bug fixes and package bumps. `nixos-unstable` follows main development and is not recommended for production ([NixOS manual — Upgrading](https://nixos.org/manual/nixos/stable/index.html#sec-upgrading)). `*-small` variants of either carry fewer binary packages: they advance faster but often need more local builds—mainly for servers.

A first install subscribes root to the channel matching the install media. Upgrading packages and the OS does **not** mean bumping [`system.stateVersion`](#systemstateversion)—leave that alone unless you have audited migrations. Choosing [switch vs boot](#apply-switch-vs-boot) is a separate decision from the channel/flake refresh.

## Details

### Channel or flake: pick your upgrade path

| Host type | Refresh step | Rebuild step |
|-----------|--------------|--------------|
| Channel | `nix-channel --update nixos` (or `nixos-rebuild … --upgrade`) | `nixos-rebuild switch` |
| Flake | `nix flake update` (or update one input) | `nixos-rebuild switch --flake .#hostname` |

Channel-based systems read nixpkgs from root’s `nixos` channel subscription. Flake-based systems ignore that channel for the system configuration; pinned inputs live in `flake.lock`. See [channel (concept)](../../02-concepts/channel.md) and [flake (concept)](../../02-concepts/flake.md).

### Channel hosts

#### Channel kinds

| Kind | Example name | Role |
|------|--------------|------|
| Stable | `nixos-YY.MM` | Conservative updates; maintained until the next stable branch |
| Unstable | `nixos-unstable` | Main development branch; radical changes possible |
| Small | `nixos-YY.MM-small`, `nixos-unstable-small` | Same sources as above, fewer binaries, faster channel bumps |

Browse live channel URLs at [channels.nixos.org](https://channels.nixos.org). Unreleased lines may appear there during a release cycle; use the [download page](https://nixos.org/download/) for the newest supported stable.

#### Inspect and switch (as root)

System rebuilds use **root’s** channel list. List the NixOS subscription:

```bash
# as root
nix-channel --list | grep nixos
```

Switch channel (the subscription **name** must be `nixos`):

```bash
# as root — replace YY.MM with the current stable, e.g. 26.05
nix-channel --add https://channels.nixos.org/nixos-YY.MM nixos
```

Examples: `nixos-YY.MM-small` for a leaner server channel, or `nixos-unstable` for the bleeding edge.

**Per-user channels.** `nix-channel` is per user. Adding or updating a channel as a non-root user does **not** change what `/etc/nixos` rebuilds see. Run channel commands as root (or with `sudo`) for system upgrades.

#### Channel-based upgrade

Usual one-liner:

```bash
# as root
nixos-rebuild switch --upgrade
```

That is equivalent to:

```bash
# as root
nix-channel --update nixos
nixos-rebuild switch
```

Rebuild modes (`switch`, `boot`, `test`) are covered in [rebuild / switch / boot / test](rebuild-switch-boot-test.md). After a bad upgrade, use [rollbacks](rollbacks.md); for build failures see [troubleshooting](troubleshooting.md).

### Flake hosts

Flake hosts do not rely on root’s `nixos` channel for the system flake. Refresh pinned inputs in `flake.lock`, then rebuild:

```bash
# in the flake directory (often /etc/nixos)
nix flake update
sudo nixos-rebuild switch --flake .#hostname
```

Update one input only (e.g. `nixpkgs`):

```bash
nix flake update nixpkgs
sudo nixos-rebuild switch --flake .#hostname
```

`nix flake update` is experimental CLI (`nix-command` + `flakes`; see nix.dev). Replace `.#hostname` with your flake output. Concept and lockfile behavior: [flake](../../02-concepts/flake.md), [lockfile](../../07-flakes/anatomy/lockfile.md). Moving off channels: [migration from channels](../../07-flakes/migration-from-channels.md).

### Apply: switch vs boot

Refreshing the channel or lockfile only changes which expressions you build. How you apply the new generation still follows [rebuild actions](rebuild-switch-boot-test.md):

| Goal | Command (after refresh) |
|------|-------------------------|
| Activate now and set boot default | `nixos-rebuild switch` (channel: often via `--upgrade`) |
| Set boot default only; activate on next reboot | `nixos-rebuild boot` |
| Try now without changing the boot default | `nixos-rebuild test` |

Prefer `boot` (then reboot) when you want kernel/initrd changes deferred to the next boot, or when mid-session activation is undesirable. Prefer `test` for a risky upgrade you may abandon by rebooting. `system.autoUpgrade.operation` can be `"switch"` or `"boot"` for the same reason ([option search](https://search.nixos.org/options?show=system.autoUpgrade.operation)).

### Specialisations (cousin, not a pin bump)

[Specialisations](../configuration/specialisations.md) are extra system closures built with the parent generation. An upgrade that rebuilds the host rebuilds those children too; it does **not** replace channel/`flake.lock` refresh. After the new generation is active, switch into a named specialisation with `nixos-rebuild … --specialisation name` (or the child’s `switch-to-configuration`) when you need that variant—not as a substitute for updating nixpkgs.

### Schema / downgrade warning

Moving between channels is usually fine. Exception: a newer NixOS may ship a newer Nix that upgrades the Nix database schema. That change is hard to undo, so you may be unable to return to the older channel afterward ([NixOS manual — Upgrading](https://nixos.org/manual/nixos/stable/index.html#sec-upgrading)).

### Automatic upgrades (`system.autoUpgrade`)

Set options in [configuration.nix](../configuration/configuration-nix.md). `system.autoUpgrade.enable = true` starts a periodic `nixos-upgrade.service` (check schedule with `systemctl list-timers`).

**Channel path (default).** With no `flake` set, the service runs the equivalent of `nixos-rebuild <operation> --upgrade` (plus module defaults). Optional explicit channel URI:

```nix
{
  system.autoUpgrade.enable = true;
  system.autoUpgrade.channel = "https://channels.nixos.org/nixos-YY.MM";
  system.autoUpgrade.allowReboot = true; # optional
}
```

When `channel` is unset, the module uses root’s existing `nix-channel` subscription.

**Flake path.** Point at a flake URI instead of a channel—the two options cannot both be set:

```nix
{
  system.autoUpgrade.enable = true;
  system.autoUpgrade.flake = "github:owner/repo#hostname";
  system.autoUpgrade.upgrade = false; # honour lockfile; see below
}
```

With `flake` set, the service passes `--refresh --flake <uri>` to `nixos-rebuild`. Other useful options:

| Option | Default | Role |
|--------|---------|------|
| [`system.autoUpgrade.upgrade`](https://search.nixos.org/options?show=system.autoUpgrade.upgrade) | `true` | When `channel` is null, also pass `--upgrade`. Set `false` on flake hosts to rebuild from the pinned lockfile without that flag. |
| [`system.autoUpgrade.operation`](https://search.nixos.org/options?show=system.autoUpgrade.operation) | `"switch"` | `"switch"` or `"boot"`. |
| [`system.autoUpgrade.dates`](https://search.nixos.org/options?show=system.autoUpgrade.dates) | `"04:40"` | systemd calendar for the timer ([`systemd.time(7)`](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html)). |
| [`system.autoUpgrade.allowReboot`](https://search.nixos.org/options?show=system.autoUpgrade.allowReboot) | `false` | Reboot when the new generation changes kernel, initrd, or kernel modules. |

**Lockfile vs auto-upgrade.** Automatic rebuilds use whatever revision the flake URI resolves to—typically the lockfile in that repo. Refreshing inputs (`nix flake update`) is a **separate** step: run it (or a dedicated oneshot) before the timer fires, commit the updated `flake.lock`, and let the next scheduled rebuild pick it up. [`system.autoUpgrade.flags`](https://search.nixos.org/options?show=system.autoUpgrade.flags) can pass extra `nixos-rebuild` arguments, but using deprecated `--update-input` / `--recreate-lock-file` there is easy to get wrong; prefer explicit `nix flake update` plus rebuild, or a separate automation for lockfile bumps.

### `system.stateVersion`

`system.stateVersion` records the first NixOS release this machine was installed with, so modules can keep defaults compatible with on-disk state (databases, data dirs, and similar). It is **not** the channel or flake revision you are running ([`system.stateVersion` option](https://search.nixos.org/options?show=system.stateVersion); also asserted in nixpkgs `version.nix`).

- Most users should **never** change it after the initial install—even when moving to a newer `nixos-YY.MM` channel or updating flake inputs.
- Changing it does **not** upgrade packages or the OS; a lower value does **not** mean the system is outdated or unsupported.
- To switch releases or unstable, change only the channel and/or flake input URLs—**do not** touch `stateVersion` as an “upgrade” lever.
- Bump only after you have manually inspected every module effect that depends on it and migrated stateful data accordingly.

Set it once at install to the release you started on (e.g. `"26.05"`). Leave it alone through routine upgrades.

### Boundaries (what this page is not)

- [Rollback](rollbacks.md) procedures—selecting a previous generation at boot.
- [Flake schema](../../07-flakes/anatomy/flake-nix-schema.md)—`flake.nix` outputs and evaluation layout.
- nixpkgs [packaging](../../06-nixpkgs/packaging/simple-package.md)—adding or overriding packages.

## Examples

Channel host: list root’s NixOS channel, switch to current stable, and upgrade:

```bash
sudo nix-channel --list | grep nixos
sudo nix-channel --add https://channels.nixos.org/nixos-26.05 nixos
sudo nixos-rebuild switch --upgrade
```

(`26.05` is an example stable line from the manual at the time of writing; substitute the current `nixos-YY.MM` from [channels.nixos.org](https://channels.nixos.org).)

Same upgrade as two steps:

```bash
sudo nix-channel --update nixos
sudo nixos-rebuild switch
```

Flake host: update all inputs, then rebuild:

```bash
cd /etc/nixos   # or wherever the system flake lives
nix flake update
sudo nixos-rebuild switch --flake .#hostname
```

Unattended channel upgrades without reboot:

```nix
{
  system.autoUpgrade.enable = true;
  # system.autoUpgrade.allowReboot = false; # default
}
```

Flake host: scheduled rebuild from a pinned lockfile (refresh lockfile separately):

```nix
{
  system.autoUpgrade.enable = true;
  system.autoUpgrade.flake = "github:owner/nixos-config#myhost";
  system.autoUpgrade.upgrade = false;
}
```

## References

- [NixOS manual — Upgrading NixOS](https://nixos.org/manual/nixos/stable/index.html#sec-upgrading) — channels, `--upgrade`, schema warning, `system.autoUpgrade`
- [Official NixOS channels](https://channels.nixos.org) — live channel URLs and status
- [`system.stateVersion` (option search)](https://search.nixos.org/options?show=system.stateVersion) — do not bump casually; not the package channel
- [`system.autoUpgrade.flake` (option search)](https://search.nixos.org/options?show=system.autoUpgrade.flake) — flake URI; mutually exclusive with `channel`
- [`system.autoUpgrade.upgrade` (option search)](https://search.nixos.org/options?show=system.autoUpgrade.upgrade) — `--upgrade` flag when `channel` is null
- [`nix-channel` (nix.dev)](https://nix.dev/manual/nix/stable/command-ref/nix-channel.html) — `--update` and channel generations
- [`nix flake update` (nix.dev)](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-update.html) — refresh `flake.lock` (experimental CLI)

## See also

- [rebuild / switch / boot / test](rebuild-switch-boot-test.md)
- [Rollbacks](rollbacks.md)
- [Troubleshooting](troubleshooting.md)
- [Specialisations](../configuration/specialisations.md)
- [Remote deploy](remote-deploy.md)
- [Channel (concept)](../../02-concepts/channel.md) / [Flake (concept)](../../02-concepts/flake.md)
