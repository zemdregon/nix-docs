---
status: complete
---

# config vs options

## Overview

Every NixOS module contributes to two parallel trees: **`options`** declares the interface (schema, types, defaults, documentation), and **`config`** supplies **definitions**—concrete values or settings derived from other options. After the [module system](module-system.md) merges all modules, the final `config` drives the system closure; the merged `options` tree describes every knob that existed during evaluation.

End-user [`configuration.nix`](../configuration/configuration-nix.md) usually only assigns values (often as top-level keys, which is sugar for `config`). Library modules do both: declare new options, then wire related `config` from those options—often with [mkIf, mkMerge, mkOrder](../modules/mkIf-mkMerge-mkOrder.md).

## Details

**Declaration vs definition.** An entry under `options` says “this path exists, has this type, and may carry this description.” An entry under `config` says “at this path, use this value.” The same logical setting (e.g. `services.nginx.enable`) appears in both trees during a module’s body, but with different roles: you **declare** under `options.*` and **define** under `config.*` (or at the top level, which merges into `config`). Defining a path that no module declared is an error.

**Reading values in modules.** Module functions receive `config` and `options` among their arguments. To branch on another module’s setting, read **`config.services.foo.enable`**, not `options.services.foo.enable`—the latter is option metadata (type, description), not the merged value. Inspecting `options` is for documentation, type info, or advanced introspection; see [Options and types](options-and-types.md).

**Conditional and derived config.** Modules typically declare a user-facing option, then set downstream `config` only when it applies:

```nix
config = lib.mkIf config.foo.enable {
  systemd.services.foo = { /* … */ };
};
```

The condition reads `config.foo.enable` (the merged definition). Prefer `lib.mkIf` over a plain Nix `if` when the condition depends on `config`, so the module system can skip inactive branches without forcing a cycle.

**Merge priority.** Many modules may define the same option path. Conflicts are resolved by the option’s type merge function and by priority wrappers: `lib.mkDefault`, `lib.mkForce`, and `lib.mkOverride` mark how strongly a definition should win; `lib.mkMerge` combines several attrsets into one contribution. Details live in [mkIf, mkMerge, mkOrder](../modules/mkIf-mkMerge-mkOrder.md).

**Fixpoint and circular references.** The `config` argument passed into every module is the **lazy fixpoint** of all merged definitions: each module may read `config` while contributing to it. That is why `config.a = config.b` / `config.b = …` style wiring works when only values (not attrset *keys*) depend on other options. Strict cycles (a value that forces itself) or computing the *structure* of `config` from `config` (e.g. mapping over `config` to choose top-level attribute names) cause infinite recursion. Prefer declaring explicit options and deriving `config` in one direction; use `lib.mkIf` / `lib.mkMerge` so merge structure stays known before values are forced.

**Common beginner mistake.** Writing `options.myapp.enable = true` (or reading `options.*` expecting a boolean) confuses schema with value. User settings belong in `config` (or at the top level); `options` in your module is for **declaring** the knob, not setting it for the running system.

## Examples

Minimal module: declare `options.foo.enable`, then set service config when it is true.

```nix
{ config, lib, pkgs, ... }:
{
  options.foo = {
    enable = lib.mkEnableOption "example foo service";
    package = lib.mkPackageOption pkgs "hello" { };
  };

  config = lib.mkIf config.foo.enable {
    systemd.services.foo = {
      description = "Foo";
      wantedBy = [ "multi-user.target" ];
      serviceConfig.ExecStart = "${config.foo.package}/bin/hello";
    };
  };
}
```

In [`configuration.nix`](../configuration/configuration-nix.md) you would only supply the definition:

```nix
{ ... }: {
  foo.enable = true;
}
```

That top-level assignment merges into `config.foo.enable`; it does not add new entries under `options`.

## References

- [NixOS manual (stable) — Writing NixOS Modules](https://nixos.org/manual/nixos/stable/#sec-writing-modules)
- [NixOS option search](https://search.nixos.org/options)
- [nix.dev — Module system tutorial](https://nix.dev/tutorials/module-system/) (secondary)

## See also

- [Module system](module-system.md)
- [Options and types](options-and-types.md)
- [Writing a module](../modules/writing-a-module.md)
- [mkIf, mkMerge, mkOrder](../modules/mkIf-mkMerge-mkOrder.md)
- [configuration.nix](../configuration/configuration-nix.md)
