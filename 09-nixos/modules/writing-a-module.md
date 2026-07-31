---
status: complete
---

# Writing a Module

## Overview

A NixOS module is a file (or inline fragment) that owns one slice of configuration—a service, hardware quirk, or shared option tree. Most shipped modules live under nixpkgs `nixos/modules`; your [`configuration.nix`](../configuration/configuration-nix.md) is a module too. Modules **declare** options others can set, and **define** options declared elsewhere (for example `pam.nix` declares `security.pam.services`; `sshd` fills PAM entries through that option).

Authoring is mostly: declare a small `options` tree, bind `let cfg = config.…;`, and wrap side effects in `lib.mkIf cfg.enable`. The evaluation model is covered in [Module system](../architecture/module-system.md); this page is the practical shape and pitfalls.

## Details

**Full vs abbreviated form.** The full shape is:

```nix
{ config, pkgs, lib, ... }: {
  imports = [ /* other modules */ ];
  options = { /* declarations */ };
  config = { /* definitions */ };
}
```

The common abbreviated form—top-level keys that look like option paths without an `options` / `config` wrapper—only **defines** existing options (sugar for `config`). It does not declare any. Defining a path no module declared is an error. See [config vs options](../architecture/config-vs-options.md).

**Where modules come from.** NixOS already imports the default set listed in `modules/module-list.nix`. Do not re-import those paths; add only your own modules (or third-party ones) via `imports`. Details: [Imports and profiles](../configuration/imports-and-profiles.md).

**Declare / define split.** Declaring creates the schema (`mkOption`, `mkEnableOption`, types). Defining sets values on options some module already declared—`environment.systemPackages`, `systemd.services`, `security.pam.services`, and so on. Cross-module composition depends on that split: one module owns the option, many modules contribute definitions. Option types and helpers: [Options and types](../architecture/options-and-types.md), [Custom options](custom-options.md).

**Idiomatic enable pattern.** Bind the subtree once, declare options, gate definitions with `mkIf`:

```nix
let
  cfg = config.services.foo;
in {
  options.services.foo.enable = lib.mkEnableOption "foo";
  config = lib.mkIf cfg.enable { /* packages, units, … */ };
}
```

Conditionals and merge priority (`mkIf`, `mkMerge`, `mkDefault`, …) are covered in [mkIf, mkMerge, mkOrder](mkIf-mkMerge-mkOrder.md). For impossible configs or soft guidance at eval time, use [assertions and warnings](assertions-and-warnings.md).

**Static `imports`.** Paths in `imports` must be known before the module fixpoint—they cannot depend on `config`. Pass values needed during import resolution (flake inputs, paths) through `specialArgs`. Prefer `_module.args` for ordinary extra module arguments that are not needed in `imports`.

**Systemd `Exec*` escaping.** When interpolating dynamic strings into `ExecStart` / other `Exec*` lines, systemd expands `%` specifiers, expands `$FOO` / `${FOO}`, splits on whitespace, and splits commands on `;`. Escape with the module argument `utils`: `utils.escapeSystemdExecArg` / `utils.escapeSystemdExecArgs`. After using those helpers, do not also disable environment substitution explicitly. Broader unit wiring: [systemd integration](../architecture/systemd-integration.md).

## Examples

Minimal enable-option module: when enabled, install a package and run a oneshot unit. Invented for illustration—not a real nixpkgs service.

```nix
{ config, lib, pkgs, ... }:
let
  cfg = config.services.helloWorld;
in {
  options.services.helloWorld = {
    enable = lib.mkEnableOption "hello-world demo service";
  };

  config = lib.mkIf cfg.enable {
    environment.systemPackages = [ pkgs.hello ];

    systemd.services.hello-world = {
      description = "Print hello once at boot";
      wantedBy = [ "multi-user.target" ];
      serviceConfig.Type = "oneshot";
      serviceConfig.ExecStart = "${pkgs.hello}/bin/hello";
    };
  };
}
```

Import the file from [`configuration.nix`](../configuration/configuration-nix.md) (or another module’s `imports`) and set `services.helloWorld.enable = true;`.

Escaping dynamic `Exec*` args (adapted from the NixOS manual; `utils` is a module argument):

```nix
{ pkgs, utils, ... }:
let
  echoAll = pkgs.writeScript "echo-all" ''
    #!${pkgs.runtimeShell}
    for s in "$@"; do printf '%s\n' "$s"; done
  '';
  args = [ "a%Nything" "lang=\${LANG}" ";" "/bin/sh -c date" ];
in {
  systemd.services.echo = {
    wantedBy = [ "multi-user.target" ];
    serviceConfig.Type = "oneshot";
    serviceConfig.ExecStart = "${echoAll} ${utils.escapeSystemdExecArgs args}";
  };
}
```

## References

- [NixOS manual — Writing NixOS Modules](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules)
- [nix.dev — Module system tutorial](https://nix.dev/tutorials/module-system/) (secondary)

## See also

- [Module system](../architecture/module-system.md)
- [Options and types](../architecture/options-and-types.md)
- [config vs options](../architecture/config-vs-options.md)
- [Custom options](custom-options.md)
- [mkIf, mkMerge, mkOrder](mkIf-mkMerge-mkOrder.md)
- [Assertions and warnings](assertions-and-warnings.md)
- [configuration.nix](../configuration/configuration-nix.md)
- [Imports and profiles](../configuration/imports-and-profiles.md)
- [systemd integration](../architecture/systemd-integration.md)
