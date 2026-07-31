---
status: complete
---

# nixos-rebuild

## Overview

`nixos-rebuild` is the primary CLI for applying a NixOS system configuration: it evaluates and builds a new system [generation](../../02-concepts/generation.md), optionally updates the boot default, and optionally activates the live machine. Activation goes through [`switch-to-configuration`](../../09-nixos/architecture/activation-script.md) in the built system closure.

From NixOS **25.11**, the default implementation is **`nixos-rebuild-ng`** (Python rewrite of the classic Bash script); the on-PATH name stays `nixos-rebuild`. From **26.05** onward the Bash implementation is removed, `system.rebuild.enableNg` must not be set, and all switchable systems use the Python rewrite.

This page is the **frontend / tooling** view—how you invoke the CLI, what it reads, and how it relates to alternate surfaces. For operational semantics of each action (`switch` / `boot` / `test` / …), root/user-service caveats, and activation ordering, see [nixos-rebuild actions](../../09-nixos/operations/rebuild-switch-boot-test.md).

## Details

### Implementation (25.11 / 26.05)

| Release | Behavior |
|---------|----------|
| Before 25.11 | Bash `nixos-rebuild` by default; opt into ng via `system.rebuild.enableNg = true` |
| 25.11+ | `nixos-rebuild-ng` is default; same command name on `$PATH` |
| 26.05+ | Bash frontend removed; do not set `system.rebuild.enableNg` |

The ng rewrite preserves the same subcommands and flags documented in `nixos-rebuild(8)`; release notes call out removals (for example deprecated `--fast` in favor of `--no-reexec`). When docs or scripts mention flag renames, check the man page for your NixOS version.

### Config inputs

By default the tool picks a config from the deploying machine:

- **`/etc/nixos/configuration.nix`** — channel-style single file (classic layout)
- **`/etc/nixos/flake.nix`** — when present, treated like passing `--flake` (automatic flake detection)

Overrides:

| Flag | Use |
|------|-----|
| `--file path` / `--attr attr` | Evaluate a specific `.nix` file and attribute instead of `/etc/nixos/configuration.nix` |
| `--flake flake-uri[#name]` | Explicit flake URL and optional `nixosConfigurations` name |
| `--no-flake` | Skip automatic flake detection even if `flake.nix` exists under `/etc/nixos` |

With flakes, the flake must export `nixosConfigurations.<name>`; omitting `#name` defaults to the current hostname. See [nixosConfigurations (flakes)](../../07-flakes/workflows/nixos-configurations.md).

Remote deploy usually evaluates from the **operator’s** tree (flake checkout or `-I nixos-config=…`), not whatever happens to sit in the target’s `/etc/nixos`—see [Remote deploy](../../09-nixos/operations/remote-deploy.md).

### Actions (summary)

One required verb per invocation. This table is the frontend cheat sheet; semantics, warnings, and edge cases live on the [operations page](../../09-nixos/operations/rebuild-switch-boot-test.md).

| Action | Build | Boot default | Activate now |
|--------|-------|--------------|--------------|
| `switch` | yes | yes | yes |
| `boot` | yes | yes | no |
| `test` | yes | no | yes |
| `build` | yes | no | no |

Related helpers on the same CLI: `dry-build`, `dry-activate`, `repl`, `build-vm`, `build-image`, `list-generations`, `--rollback`. Root (or elevation via `--elevate` / `--sudo`) is required for actions that activate or change the boot default; plain `build` does not need root.

### Re-exec

Unless `--no-reexec` is set, `nixos-rebuild` first builds `config.system.build.nixos-rebuild` from the target config and **execs into that binary** so the running tool matches the generation being applied. Skip re-exec when cross-architecture deploy would fail with “Exec format error” (common with `--target-host` / `--build-host`); details on [Remote deploy](../../09-nixos/operations/remote-deploy.md).

### Remote and elevation

SSH flags split **where builds run** from **where activation runs**:

| Flag | Role |
|------|------|
| `--build-host user@host` | Build on remote; copy closure back if no `--target-host` |
| `--target-host user@host` | Activate on remote instead of locally |

Non-root SSH users need elevation on the target: `--elevate={none,sudo,run0}` (aliases `--sudo`, `--ask-sudo-password` / `--ask-elevate-password`). Prefer these over the deprecated `--use-remote-sudo`. Full flag matrix and `NIX_SSHOPTS`: [Remote deploy](../../09-nixos/operations/remote-deploy.md).

### Choosing a frontend

All paths below still end in the same activation model (`switch-to-configuration` on a built system closure). They differ in **who runs the CLI**, **UX**, and **fleet scale**—not in what “switch” means on the machine.

| Surface | When to prefer it |
|---------|-------------------|
| **`nixos-rebuild`** | Official manual path; scripts, docs, and modules assume it; single-host or ad hoc `--target-host` |
| **[nh](nh.md)** | One ergonomic CLI across NixOS, Home Manager, and nix-darwin; pre-switch diffs and progress; still drives rebuild/activation, not a new model ([adjacent-tools detail](../../05-cli-and-tooling/adjacent-tools/nh-nvd-nixos-rebuild.md)) |
| **`nixos-rebuild --build-host` / `--target-host`** | Few remotes, same verbs as local; no inventory file |
| **[Colmena](../../12-deployment-and-infra/colmena.md)** | Many-node hive: tags, parallel apply, shared defaults |
| **[deploy-rs](../../12-deployment-and-infra/deploy-rs.md)** | Flake `deploy.nodes` / profiles; CI-oriented activation with magic rollback |

Fleet tools are **cousins**, not replacements: they orchestrate SSH/build/copy and call into the same switch/boot/test semantics. Install-time remote provisioning (not ongoing rebuild) is [nixos-anywhere](../../09-nixos/installation/nixos-anywhere.md).

## Examples

Channel-style host (root shell recommended for activate verbs):

```bash
sudo -i
nixos-rebuild switch
nixos-rebuild boot      # next reboot only
nixos-rebuild test      # activate now; reboot undoes boot default
```

Flake on the same machine (`#name` optional when it matches hostname):

```bash
sudo nixos-rebuild switch --flake /etc/nixos
sudo nixos-rebuild switch --flake .#myhost
```

Non-default config path (evaluate from a checkout, not `/etc/nixos`):

```bash
nixos-rebuild switch --file ~/configs/desktop.nix --attr machine
nixos-rebuild switch --flake git+file:///home/user/nixos#laptop
```

Force classic file mode when a flake also exists:

```bash
sudo nixos-rebuild switch --no-flake
```

Build-only check (no root):

```bash
nixos-rebuild build
nixos-rebuild build --flake .#myhost
nixos-rebuild dry-build --flake .
```

Remote activate (operator machine → target); see [Remote deploy](../../09-nixos/operations/remote-deploy.md) for cross-build and `--no-reexec`:

```bash
nixos-rebuild switch --flake .#hostname --target-host user@host --elevate=sudo
```

## References

- [NixOS manual — Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)
- [`nixos-rebuild(8)` (nixos-rebuild-ng man source)](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/ni/nixos-rebuild-ng/nixos-rebuild.8.scd)
- [NixOS 25.11 release notes — `nixos-rebuild-ng` default](https://nixos.org/manual/nixos/stable/release-notes.html#sec-release-25.11)
- [NixOS 26.05 release notes — Bash `nixos-rebuild` removed](https://nixos.org/manual/nixos/stable/release-notes.html#sec-release-26.05)

## See also

- [nixos-rebuild actions](../../09-nixos/operations/rebuild-switch-boot-test.md) — switch / boot / test / build ops deep dive
- [Remote deploy](../../09-nixos/operations/remote-deploy.md) — `--build-host`, `--target-host`, elevation, `--no-reexec`
- [Activation script](../../09-nixos/architecture/activation-script.md) — what activation actually runs
- [nh](nh.md) — alternate rebuild UX
- [nh / nvd / nixos-rebuild](../../05-cli-and-tooling/adjacent-tools/nh-nvd-nixos-rebuild.md) — CLI comparison and diff workflows
- [nixosConfigurations (flakes)](../../07-flakes/workflows/nixos-configurations.md)
- [Colmena](../../12-deployment-and-infra/colmena.md) — multi-host hive deploy
- [deploy-rs](../../12-deployment-and-infra/deploy-rs.md) — flake-native fleet activation
- [Machine mesh](../../02-concepts/machine-mesh.md) — how fleet tools relate in the wider landscape
