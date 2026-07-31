---
status: complete
---

# Service Patterns

## Overview

Most NixOS daemons are not hand-written unit files. They are **modules** under `services.*` that expose an `enable` flag (and settings), then—when enabled—define concrete `systemd.services` / timers / sockets, plus supporting config such as firewall ports, system users, and files under `/etc`. Prefer those high-level options when nixpkgs already ships a module; drop to raw `systemd.*` only when you need control the module does not offer.

## Details

**The usual module shape.** A service module binds `cfg = config.services.foo`, declares options under `options.services.foo`, and wraps definitions in `config = lib.mkIf cfg.enable { … }`. Inside that `mkIf`, the module typically sets `systemd.services.foo` (and maybe timers or sockets), and may also touch `networking.firewall`, `users.users`, `environment.etc`, `systemd.tmpfiles`, and state under `/var/lib`. Conditioning on `enable` keeps unused services out of the evaluation result—see [mkIf, mkMerge, mkOrder](../modules/mkIf-mkMerge-mkOrder.md).

**High-level `services.*` first.** Search [NixOS options for `services.`](https://search.nixos.org/options?query=services.) before writing units. Upstream modules already wire package selection, config files, users, and units. Use `systemd.services.<name>` for one-offs or overrides when no suitable module exists; see [systemd integration](../architecture/systemd-integration.md).

**Related option clusters.**

| Concern | Typical options |
|---------|-----------------|
| Process / unit | `systemd.services.<name>`, timers, sockets |
| Network exposure | `networking.firewall.allowedTCPPorts` (and UDP / interfaces) — [networking](../configuration/networking.md) |
| Identity | `users.users.<name>.isSystemUser` (and groups) |
| Runtime layout | `systemd.tmpfiles`, state dirs under `/var/lib` |
| Static config files | `environment.etc` |

**Escaping `Exec*` interpolations.** systemd substitutes `%` specifiers and `$` / `${…}` environment forms, and splits on whitespace. Arguments you interpolate into `ExecStart` (and other `Exec*` lines)—especially from user-facing option lists—should go through `utils.escapeSystemdExecArgs` (or `utils.escapeSystemdExecArg`). The NixOS manual covers this under writing modules; do not disable environment substitution when using those helpers.

**Activation restarts units.** After evaluation and build, `switch-to-configuration` (via `nixos-rebuild switch`) reconciles the new generation with running systemd state: changed units are started, stopped, restarted, or reloaded as needed. One-shot setup still runs through the [activation script](../architecture/activation-script.md); ongoing lifecycle stays with systemd.

## Examples

Prefer an existing module when one exists:

```nix
{ ... }: {
  services.openssh.enable = true;
}
```

Minimal invented `services.hello`-style sketch (illustrative only—not a full production module):

```nix
{ config, lib, pkgs, ... }:
let
  cfg = config.services.hello;
in
{
  options.services.hello = {
    enable = lib.mkEnableOption "the hello demo service";
  };

  config = lib.mkIf cfg.enable {
    systemd.services.hello = {
      description = "Demo hello oneshot";
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        Type = "oneshot";
        ExecStart = "${pkgs.hello}/bin/hello";
      };
    };
  };
}
```

For dynamic args, pass them through escaping (module argument `utils`):

```nix
{ config, pkgs, utils, ... }:
# …
serviceConfig.ExecStart = ''
  ${pkgs.hello}/bin/hello ${utils.escapeSystemdExecArgs cfg.extraArgs}
'';
```

Concrete enable/settings for popular daemons: [common service examples](common-service-examples.md).

## References

- [NixOS manual — Writing NixOS modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules) — module structure; locate-service example
- [NixOS manual — Escaping in Exec directives](https://nixos.org/manual/nixos/stable/index.html#exec-escaping-example) — `utils.escapeSystemdExecArgs`
- [NixOS manual — Running NixOS](https://nixos.org/manual/nixos/stable/index.html#ch-running)
- [NixOS option search — `services.`](https://search.nixos.org/options?query=services.)

## See also

- [Common service examples](common-service-examples.md)
- [Writing a module](../modules/writing-a-module.md)
- [mkIf, mkMerge, mkOrder](../modules/mkIf-mkMerge-mkOrder.md)
- [systemd integration](../architecture/systemd-integration.md)
- [Activation script](../architecture/activation-script.md)
- [Networking](../configuration/networking.md)
