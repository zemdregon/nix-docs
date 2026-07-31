---
status: complete
---

# Assertions and Warnings

## Overview

NixOS modules can detect bad or surprising configuration during evaluation—before a system build starts. For that, prefer the module system’s `assertions` and `warnings` options over ad hoc `builtins.abort` or `builtins.trace`. Both are first-class list options: any module can append entries, lists merge like other `listOf` options, and feedback appears in the familiar `nixos-rebuild` output. Assertions fail evaluation with a clear message; warnings print advice and let the build continue. See [Writing a module](writing-a-module.md) and the [Module system](../architecture/module-system.md).

## Details

**Warnings.** Set `warnings = [ "…" … ]` to emit strings during evaluation. Warnings never fail the build. Use them for deprecations, known sharp edges, or advisory notes (“you enabled X; expect Y”). They are appropriate when the configuration is valid but suboptimal or likely to surprise the operator.

**Assertions.** Set `assertions = [ { assertion = bool; message = "…"; } … ]`. When any `assertion` evaluates to `false`, evaluation stops and Nix prints the corresponding `message`. Use assertions when the configuration cannot produce a working system: conflicting daemons, mutually exclusive backends, or required companion options left unset while a service is enabled.

**List merge.** Both options are ordinary module options with list types. Each module contributes zero or more entries; the module system concatenates them during merge—the same pattern as other append-only lists. Multiple unrelated modules can each add checks without coordinating imports. How list options merge is covered in [Options and types](../architecture/options-and-types.md).

**Gating with `mkIf`.** Place checks inside `lib.mkIf cfg.enable { … }` so they run only when the module (or feature) is active. Assert syslogd vs rsyslogd conflicts only when syslogd is enabled; warn about a risky sub-option only when the parent service is on. Conditional definitions and merge helpers are described in [mkIf / mkMerge / mkOrder](mkIf-mkMerge-mkOrder.md).

**Assertions vs option types.** Option types enforce shape: a string where an integer is declared fails at merge time with a type error. Assertions enforce semantics: values may be well-typed yet still incompatible (two syslog daemons enabled, or a backend selected without its required package). Use types for “this must be a path or null”; use assertions for “these two flags cannot both be true.” Neither replaces the other.

**Why not `abort` / `trace`.** Those builtins work anywhere in Nix, but inside modules they produce less structured feedback and do not participate in list merge. The NixOS manual recommends `warnings` and `assertions` for configuration problems discoverable at eval time.

| Mechanism | Fails eval? | Use for |
|-----------|-------------|---------|
| Option types | Yes (type mismatch) | Wrong type or shape |
| `warnings` | No | Deprecations, advisory notes |
| `assertions` | Yes (false assertion) | Impossible or incomplete configs |

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

A single conditional string can also be written with `lib.optional`.

## References

- [NixOS manual (stable) — Warnings and Assertions](https://nixos.org/manual/nixos/stable/index.html#sec-assertions)
- [NixOS manual (stable) — Writing NixOS Modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules)

## See also

- [Writing a module](writing-a-module.md)
- [mkIf / mkMerge / mkOrder](mkIf-mkMerge-mkOrder.md)
- [Module system](../architecture/module-system.md)
- [Module system internals](../architecture/module-system-internals.md)
- [Options and types](../architecture/options-and-types.md)
