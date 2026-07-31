---
status: complete
---

# systemd Integration

## Overview

NixOS uses **systemd** as its init and service manager. You do not maintain unit files under `/etc/systemd` as the source of truth—[module system](module-system.md) evaluation turns NixOS options into unit files in the **system closure**. A `nixos-rebuild switch` activates that closure and reconciles running unit state with what changed.

Operators care about two failure modes: **activation** (the switch/activation script did not finish cleanly) versus **unit** failure (switch succeeded but a service is `failed` or keeps restarting). The sections below cover how switch decides reload/restart/stop, and how to override units without clobbering upstream definitions.

## Details

**Generated units, not hand-edited `/etc`.** Service modules and your `configuration.nix` set options such as `systemd.services.<name>`. NixOS renders `.service`, `.timer`, `.socket`, and related unit fragments into the store as part of the new system generation. On activation, those files are linked into place; the live `/etc/systemd/system` tree reflects the active generation, not ad-hoc edits that survive the next rebuild.

**Typical option paths.**

| Area | Option prefix | Role |
|------|---------------|------|
| System services | `systemd.services.<name>` | Long-running daemons, one-shots, overrides |
| User services | `systemd.user.services.<name>` | Units for logged-in users |
| Timers | `systemd.timers.<name>` | Scheduled jobs (often paired with a service) |
| Sockets | `systemd.sockets.<name>` | Socket activation |
| Mounts / paths | `systemd.mounts`, `systemd.paths` | Mount units, path-triggered services |
| Upstream unit files | `systemd.packages` | Install units shipped by a package under `lib/systemd/` |
| High-level modules | `services.<name>.*` | Declarative knobs that expand into `systemd.*` (and sometimes other config) |

Most day-to-day services are enabled through **`services.<name>.enable`** (and related options) in nixpkgs modules; those modules translate your settings into concrete `systemd.services` definitions (often also using `systemd.packages`). Drop down to `systemd.services` when you need full control or there is no high-level module.

**`systemd.packages` vs `environment.systemPackages`.** A package in `environment.systemPackages` puts binaries on `$PATH`; it does **not** register upstream unit files with systemd. To make units from `lib/systemd/system/` (or user units under `lib/systemd/user/`) available, add the package to **`systemd.packages`**, or use a **`services.*.enable`** module that does so for you. Without one of those, `systemctl start foo.service` will not find a unit even if the package is installed.

**Unit change detection on switch.** After building the new closure, `switch-to-configuration` (invoked by `nixos-rebuild switch`) compares each managed unit’s file in the old and new generations by **parsing and diffing unit contents** (not raw file paths). It then stops affected units, runs the [activation script](activation-script.md), reloads systemd as needed, and reloads/restarts/starts units. Use `nixos-rebuild dry-activate` to print planned unit actions without applying them.

When unit files differ, NixOS maps declarative options to systemd `X-*` keys and applies a short decision chain (see the manual’s system-switch chapter for edge cases such as `.mount` and sysinit ordering):

| Option | Effect when unit file changed |
|--------|-------------------------------|
| `reloadTriggers` | If **only** `X-Reload-Triggers` changed → **reload** |
| `reloadIfChanged = true` | **Reload** instead of restart/stop-start (deactivated units are **started**) |
| `restartIfChanged = false` | Skip restart/reload handling for this unit |
| `stopIfChanged = true` (**default**) | **Stop**, then **start** after activation (avoids new unit running against old `/etc`) |
| `stopIfChanged = false` | **Restart** in place |
| `restartTriggers` | Store paths whose change forces a **restart** even when the rendered unit text is unchanged (typical for early/sysinit services tied to `/etc` snippets) |

Additional skips: `RefuseManualStop`, `X-OnlyManualStart`, and related unit keys can prevent stop/restart. **Socket-activated** services: NixOS auto-pairs a `.service` with its `.socket` unless `X-NotSocketActivated` is set. With default `stopIfChanged`, both socket and service are stopped and the **socket** is started so activation brings the service up on demand; with `stopIfChanged = false`, the service follows the normal restart path.

**Activation failure vs unit failure.**

| Symptom | Likely layer | What to inspect |
|---------|--------------|-----------------|
| `nixos-rebuild switch` exits non-zero; switch aborted mid-way | Activation / switch script | Rebuild output; [activation script](activation-script.md); `journalctl -b` around switch time |
| Switch succeeds; `systemctl status foo` shows `failed` or restart loop | Unit runtime | `systemctl status foo`, `systemctl cat foo`, `journalctl -u foo -b` |
| Unexpected stop/reload on switch | Unit reconciliation | `nixos-rebuild dry-activate`; compare generated unit under `/run/current-system` |

See [Troubleshooting](../operations/troubleshooting.md) for broader rebuild and boot issues.

**Overrides without clobbering.** Multiple modules often set the same `systemd.services.<name>`. Attribute-set options merge by key; to override one `serviceConfig` field without wiping upstream `ExecStart`, `Environment`, and friends, force **that key only**:

```nix
systemd.services.foo.serviceConfig.Restart = lib.mkForce "no";
```

Avoid `serviceConfig = lib.mkForce { … }` unless you intend to replace the entire section— that discards merged keys from other modules. Priorities and ordering use `lib.mkForce`, `lib.mkDefault`, `lib.mkIf`, and `lib.mkMerge`; see [mkIf / mkMerge / mkOrder](../modules/mkIf-mkMerge-mkOrder.md).

**Template units (brief).** systemd templates use a base unit `name@.service` and instances `name@instance.service`. In NixOS, define the base (e.g. `"foo@"`) and each instance (e.g. `"foo@bar"`) under `systemd.services`. Each **instance** needs `overrideStrategy = "asDropin"` so change detection works, and `wantedBy` (or equivalent) so NixOS manages that instance on switch—not only the template file.

**Store-backed executables.** `ExecStart`, `Environment`, and path options typically reference binaries and config under the [Nix store](../../04-store-and-build/nix-store-layout.md) (e.g. `${pkgs.openssh}/bin/sshd`). That keeps service environments hermetic and tied to the generation you switched to.

**Initrd systemd (brief).** Some advanced setups run systemd in **stage-1** (initrd) for early mounting, decryption, or networking. That is optional and separate from normal `systemd.services` on the booted system; treat it as an advanced boot topic rather than the default path.

**Escaping in Exec directives.** Values in `serviceConfig` (and similar) pass through Nix string interpolation *and* systemd’s own rules (`%` specifiers, `$FOO` / `${FOO}`, whitespace, `;`). Prefer `utils.escapeSystemdExecArg` / `utils.escapeSystemdExecArgs` for non-trivial argument lists—see the manual example linked under References.

## Examples

Prefer a high-level enable when nixpkgs already provides a module:

```nix
{ ... }: {
  services.openssh.enable = true;
}
```

That option expands into OpenSSH package selection, config files, and a `systemd.services.sshd` unit. For a minimal custom service without a dedicated module:

```nix
{ pkgs, ... }: {
  systemd.services.foo = {
    description = "Example foo daemon";
    wantedBy = [ "multi-user.target" ];
    after = [ "network.target" ];
    serviceConfig = {
      Type = "simple";
      ExecStart = "${pkgs.writeShellScript "foo" ''
        exec sleep infinity
      ''}";
    };
  };
}
```

Reload when only managed config changes—list the store path in `reloadTriggers` so switch reloads instead of stop-start:

```nix
{ config, pkgs, ... }: {
  environment.etc."myapp.conf".text = "listen=8080";
  systemd.services.myapp = {
    wantedBy = [ "multi-user.target" ];
    reloadTriggers = [ config.environment.etc."myapp.conf".source ];
    serviceConfig = {
      ExecStart = "${pkgs.writeShellScript "myapp" "exec sleep infinity"}";
      ExecReload = "${pkgs.coreutils}/bin/kill -HUP $MAINPID";
    };
  };
}
```

Single-key override of an upstream module default:

```nix
{ lib, ... }: {
  systemd.services.nginx.serviceConfig.Restart = lib.mkForce "no";
}
```

Inspect generated units on a built system with `systemctl cat <unit>` or by browsing the store path for the active generation (`systemctl status` shows the loaded unit path under `/nix/store/...`).

## References

- [NixOS manual — Running NixOS / Service Management](https://nixos.org/manual/nixos/stable/index.html#ch-running) — systemd as init; [systemd in NixOS](https://nixos.org/manual/nixos/stable/index.html#sect-nixos-systemd-nixos); [Defining custom services](https://nixos.org/manual/nixos/stable/index.html#sect-nixos-systemd-custom-services)
- [What happens during a system switch?](https://nixos.org/manual/nixos/stable/index.html#sec-switching-systems) — `switch-to-configuration`, unit start/stop/reload, `restartTriggers`
- [Escaping in Exec directives (example)](https://nixos.org/manual/nixos/stable/index.html#exec-escaping-example)
- [NixOS option search — `systemd.services`](https://search.nixos.org/options?query=systemd.services)
- [NixOS options index](https://nixos.org/manual/nixos/stable/options)

## See also

- [Activation script](activation-script.md)
- [Troubleshooting](../operations/troubleshooting.md)
- [Rebuild, switch, boot, and test](../operations/rebuild-switch-boot-test.md)
- [mkIf / mkMerge / mkOrder](../modules/mkIf-mkMerge-mkOrder.md)
- [Service patterns](../services/service-patterns.md)
- [Nix store layout](../../04-store-and-build/nix-store-layout.md)
