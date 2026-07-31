---
status: complete
---

# NixOS Options Patterns

Dense module/option idioms for NixOS configs. Depth: [module system](../09-nixos/architecture/module-system.md) · [mkIf / mkMerge / mkOrder](../09-nixos/modules/mkIf-mkMerge-mkOrder.md) · [options and types](../09-nixos/architecture/options-and-types.md) · [custom options](../09-nixos/modules/custom-options.md) · [assertions](../09-nixos/modules/assertions-and-warnings.md) · [imports](../09-nixos/configuration/imports-and-profiles.md).

Prefer `lib.*` helpers over raw `if` / `//` / `recursiveUpdate` on module `config` nodes — those strip `_type` metadata. Symptom lookup: [FAQ: Common Errors](faq-common-errors.md).

## Priority (lowest number wins)

| Helper | Priority | Beats |
|--------|----------|-------|
| `lib.mkForce v` | 50 (`mkOverride 50`) | bare defs, `mkDefault` |
| bare definition | 100 | `mkDefault`, option default |
| `lib.mkDefault v` | 1000 (`mkOverride 1000`) | option default only |
| `mkOption` `default` | 1500 | nothing above |

`lib.mkOverride prio v` for any priority. Image/media helpers may use other fixed priorities (e.g. `mkImageMediaOverride` ≈ 60); they still yield to `mkForce`.

## Conditionals and merge

| Helper | Role |
|--------|------|
| `lib.mkIf cond defs` | Delayed conditional — use when `defs` depend on `config` you also set |
| `lib.mkMerge [ a b … ]` | Several definition sets as one module `config` |
| `lib.mkBefore` / `lib.mkAfter` | List merge order (`mkOrder` 500 / 1500); not inclusion |
| `lib.mkOrder n v` | Explicit merge order (default 1000) |

Do **not** wrap a whole `config = if config.x then …` that also defines `x` — infinite recursion. Put the condition inside `mkIf`.

## Declaring options

| Helper | Role |
|--------|------|
| `lib.mkOption { type; default?; description; … }` | Declare a typed option (`lib.options`) |
| `lib.mkEnableOption "desc"` | Bool `enable`; default `false`; desc → “Whether to enable …” |
| `lib.mkPackageOption pkgs "name" {…}` | Package-typed option; default from `pkgs` attr path |

Unknown option paths fail eval. Types also define **merge** (`listOf` concat, `attrsOf` join, …).

## Common types (`lib.types`)

| Type | Notes / merge |
|------|----------------|
| `bool` | All defs must agree (after priority) |
| `boolByOr` | OR-merge |
| `str` / `int` / `port` / `path` / `package` | Scalars; prefer `package` over `path` for store paths |
| `enum [ … ]` | One of listed values; no multi-def merge |
| `nullOr t` | `null` or `t` |
| `listOf t` | Concatenate |
| `attrsOf t` | Join attrs (strict values) |
| `lazyAttrsOf t` | Join attrs (lazy); `mkIf false` edge cases — see manual |
| `submodule { options = …; }` | Nested module interface |

Full catalog: NixOS manual § Option Types. Teaching page: [options and types](../09-nixos/architecture/options-and-types.md).

## Imports

```nix
{ modulesPath, ... }: {
  imports = [
    ./hardware-configuration.nix
    ./services.nix
    (modulesPath + "/profiles/headless.nix")
  ];
}
```

`imports` is static — cannot branch on `config.*`. Pass flake inputs / paths via `specialArgs` / `_module.args`, not by reading merged config.

## Assertions and warnings

| Option | Fails eval? | Shape |
|--------|-------------|--------|
| `assertions` | Yes if `assertion == false` | `{ assertion = bool; message = "…"; }` |
| `warnings` | No | string list |

Prefer these over `builtins.abort` / `trace` inside modules.

## Patterns

Enable-gated config:

```nix
{ config, lib, ... }:
{
  config = lib.mkIf config.services.httpd.enable {
    environment.systemPackages = [ /* … */ ];
  };
}
```

Unconditional + conditional via `mkMerge`:

```nix
{ config, lib, ... }:
{
  config = lib.mkMerge [
    { environment.systemPackages = [ /* always */ ]; }
    (lib.mkIf config.services.bla.enable {
      environment.systemPackages = [ /* when enabled */ ];
    })
  ];
}
```

Soft default vs hard override:

```nix
{ lib, ... }:
{
  networking.firewall.enable = lib.mkDefault true;  # host can override
  services.openssh.enable = lib.mkForce false;      # wins over other modules
}
```

Declare + assert when enabled:

```nix
{ config, lib, ... }:
let
  inherit (lib) mkEnableOption mkOption mkIf types;
  cfg = config.services.myapp;
in
{
  options.services.myapp = {
    enable = mkEnableOption "myapp";
    port = mkOption {
      type = types.port;
      default = 8080;
      description = "Listen port.";
    };
  };

  config = mkIf cfg.enable {
    assertions = [
      {
        assertion = cfg.port != 22;
        message = "services.myapp.port must not be 22.";
      }
    ];
    # … systemd / networking defs …
  };
}
```

List ordering (after priority filter):

```nix
{ lib, ... }:
{
  boot.kernelParams = lib.mkBefore [ "quiet" ];
}
```

## See also

- [Modules](../09-nixos/modules/README.md) · [Writing a module](../09-nixos/modules/writing-a-module.md)
- [mkIf / mkMerge / mkOrder](../09-nixos/modules/mkIf-mkMerge-mkOrder.md)
- [Options and types](../09-nixos/architecture/options-and-types.md) · [Custom options](../09-nixos/modules/custom-options.md)
- [Assertions and warnings](../09-nixos/modules/assertions-and-warnings.md)
- [Imports and profiles](../09-nixos/configuration/imports-and-profiles.md)
- [FAQ: Common Errors](faq-common-errors.md)

## References

- [NixOS manual — Option definitions](https://nixos.org/manual/nixos/stable/#sec-option-definitions) (`mkIf`, priorities, `mkMerge`, `mkOrder`)
- [NixOS manual — Option declarations](https://nixos.org/manual/nixos/stable/#sec-option-declarations) (`mkOption`)
- [NixOS manual — Option types](https://nixos.org/manual/nixos/stable/#sec-option-types)
- [NixOS manual — Assertions](https://nixos.org/manual/nixos/stable/#sec-assertions)
- [NixOS manual — Writing modules](https://nixos.org/manual/nixos/stable/#sec-writing-modules)
- [nixpkgs lib.options](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.options) (`mkOption`, `mkEnableOption`, `mkPackageOption`)
- [nixpkgs `lib/options.nix`](https://github.com/NixOS/nixpkgs/blob/master/lib/options.nix)
