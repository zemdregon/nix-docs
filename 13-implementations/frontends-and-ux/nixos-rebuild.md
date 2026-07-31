---
status: complete
---

# nixos-rebuild

## Overview

`nixos-rebuild` is the primary CLI for applying a NixOS system configuration: it evaluates and builds a new system [generation](../../02-concepts/generation.md), optionally updates the boot default, and optionally activates the live machine. Activation goes through [`switch-to-configuration`](../../09-nixos/architecture/activation-script.md) in the built system closure.

From NixOS **25.11**, the default implementation is **`nixos-rebuild-ng`** (Python rewrite of the classic Bash script); the on-PATH name stays `nixos-rebuild`. In **26.05** (current stable) the Bash implementation is removed and `system.rebuild.enableNg` must not be set — all switchable systems use the Python rewrite.

This page is the **frontend / tooling** view. For operational semantics of each action (`switch` / `boot` / `test` / …), see [nixos-rebuild actions](../../09-nixos/operations/rebuild-switch-boot-test.md).

## Details

**What it builds from.** By default the tool uses `/etc/nixos/configuration.nix` (channel-style), or `/etc/nixos/flake.nix` when that file exists (treated like `--flake`). Overrides: `--file` / `--attr`, `--flake flake-uri[#name]`, or `--no-flake` to skip automatic flake detection. With flakes, the flake must export `nixosConfigurations.<name>`; omitting `#name` defaults to the current hostname.

**Actions (summary).** One required verb:

| Action | Build | Boot default | Activate now |
|--------|-------|--------------|--------------|
| `switch` | yes | yes | yes |
| `boot` | yes | yes | no |
| `test` | yes | no | yes |
| `build` | yes | no | no |

Related helpers: `dry-build`, `dry-activate`, `repl`, `build-vm`, `build-image`, `list-generations`, `--rollback`. Root (or elevation via `--elevate` / `--sudo`) is required for actions that activate or change the boot default; plain `build` does not need root. Details and warnings (user services, `sudo -i`) live on the [operations page](../../09-nixos/operations/rebuild-switch-boot-test.md).

**Re-exec.** Unless `--no-reexec` is set, `nixos-rebuild` first builds `config.system.build.nixos-rebuild` from the target config and execs into that binary so the running tool matches the generation being applied.

**Remote / elevate.** `--build-host` and `--target-host` (SSH) split build vs activate; `--elevate={none,sudo,run0}` (and aliases `--sudo`, `--ask-sudo-password`) cover non-root local or remote activation. Prefer these over the deprecated `--use-remote-sudo`.

**Landscape.** The CLI verbs are the stable activation frontend; [nh](nh.md) is a separate, nicer UX that still drives rebuild/activation rather than replacing the activation model.

## Examples

```bash
# Channel / configuration.nix — day-to-day apply
# sudo -i
# nixos-rebuild switch

# Flake (hostname omitted → current host; or pass #name)
# nixos-rebuild switch --flake /etc/nixos
# nixos-rebuild switch --flake .#myhost

# Build only (no root needed)
$ nixos-rebuild build
$ nixos-rebuild build --flake .#myhost
```

## References

- [NixOS manual — Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)
- [`nixos-rebuild(8)` (nixos-rebuild-ng man source)](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/ni/nixos-rebuild-ng/nixos-rebuild.8.scd)
- [NixOS 25.11 release notes — `nixos-rebuild-ng` default](https://nixos.org/manual/nixos/stable/release-notes.html#sec-release-25.11)
- [NixOS 26.05 release notes — Bash `nixos-rebuild` removed](https://nixos.org/manual/nixos/stable/release-notes.html#sec-release-26.05)

## See also

- [nixos-rebuild actions](../../09-nixos/operations/rebuild-switch-boot-test.md) — switch / boot / test / build ops deep dive
- [Activation script](../../09-nixos/architecture/activation-script.md) — what activation actually runs
- [nh](nh.md) — alternate rebuild UX
- [nixosConfigurations (flakes)](../../07-flakes/workflows/nixos-configurations.md)
