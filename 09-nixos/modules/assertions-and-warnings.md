---
status: complete
---

# Assertions and Warnings

## Overview

When a module can detect a bad or surprising configuration at evaluation time, prefer the module system’s `assertions` and `warnings` over `builtins.abort` / `builtins.trace`. They give clearer feedback during `nixos-rebuild`, and assertions stop a broken system before it builds.

Both are ordinary options that modules append to (lists merge). Use them for impossible combinations, missing required settings when `enable = true`, and deprecation notices. See [Writing a module](writing-a-module.md) and [Module system](../architecture/module-system.md).

## Details

**Warnings.** `warnings = [ "…" … ]` — strings printed during evaluation. They do not fail the build. Good for soft guidance: deprecated option usage, known sharp edges, or “you enabled X; expect Y.”

**Assertions.** `assertions = [ { assertion = bool; message = "…"; } … ]` — if `assertion` is `false`, evaluation fails with `message`. Use this when the configuration cannot produce a working system (conflicting daemons, mutually exclusive backends, required companion options unset).

**Why not `abort` / `trace`.** Those builtins work anywhere in Nix, but they are awkward inside modules: feedback is less structured, and they do not participate in the module merge the way `warnings` / `assertions` do. The NixOS manual recommends the module options for config problems.

**Typical placement.** Gate with `lib.mkIf cfg.enable` so checks run only when the module is active. Assert conflicts (for example syslogd vs rsyslogd) or exclusive backends inside that block. Multiple modules can each contribute entries; the lists concatenate like other `listOf` options—see [options and types](../architecture/options-and-types.md) and [mkIf / mkMerge / mkOrder](mkIf-mkMerge-mkOrder.md).

**What belongs where.**

| Mechanism | Fails eval? | Use for |
|-----------|-------------|---------|
| `warnings` | No | Deprecations, advisory notes |
| `assertions` | Yes | Impossible or incomplete configs |

## Examples

Assertion pattern from the NixOS manual (syslogd / rsyslogd): only one syslog daemon may be enabled.

```nix
{ config, lib, ... }:
{
  config = lib.mkIf config.services.syslogd.enable {
    assertions = [
      {
        assertion = !config.services.rsyslogd.enable;
        message = "rsyslogd conflicts with syslogd";
      }
    ];
  };
}
```

Warning pattern from the manual (advisory; does not fail eval):

```nix
{ config, lib, ... }:
{
  config = lib.mkIf config.services.foo.enable {
    warnings =
      if config.services.foo.bar then
        [
          ''
            You have enabled the bar feature of the foo service.
            This is known to cause some specific problems in certain situations.
          ''
        ]
      else
        [ ];
  };
}
```

Equivalent compact form using `lib.optional` is fine for a single conditional string.

## References

- [NixOS manual (stable) — Warnings and Assertions](https://nixos.org/manual/nixos/stable/index.html#sec-assertions)
- [NixOS manual (stable) — Writing NixOS Modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules)

## See also

- [Writing a module](writing-a-module.md)
- [mkIf / mkMerge / mkOrder](mkIf-mkMerge-mkOrder.md)
- [Module system](../architecture/module-system.md)
- [Options and types](../architecture/options-and-types.md)
