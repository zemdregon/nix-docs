---
status: complete
---

# devenv / devshell

## Overview

**devenv** ([cachix/devenv](https://devenv.sh/)) and **devshell** ([numtide/devshell](https://github.com/numtide/devshell)) are higher-level developer-experience layers on top of Nix. They make *project shells*—packages on `PATH`, language toolchains, services, processes, env files—easier to declare than wiring everything by hand with [`pkgs.mkShell`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-mkShell) or a flake’s `devShells` and entering them with [`nix develop`](../modern-cli/nix-build-develop-run.md).

Neither tool is required to use Nix shells. Bare `mkShell` / `devShells` plus `nix develop` (or classic [`nix-shell`](../classic-cli/nix-shell.md)) is enough. These projects are convenience layers: more opinionated modules and CLI than raw Nix expressions.

## Details

### Versus bare `nix develop`

[`nix develop`](../modern-cli/nix-build-develop-run.md) enters the environment of a derivation (typically a flake `devShells.<system>.*` or a package’s build env). You define that shell yourself—often with `pkgs.mkShell`—and Nix does not prescribe languages, databases, or process supervisors.

devenv and numtide/devshell sit *above* that model: they generate or wrap a shell so teams can declare common DX concerns (tool menus, services, dotenv) without reinventing the same Nix each project.

### devenv (cachix/devenv)

[devenv](https://devenv.sh/) focuses on declarative project environments. Typical surface:

- **`devenv.nix`** — Nix module config: packages, `languages.*`, `services.*` (e.g. Postgres), `processes` (Procfile-style), `env` / dotenv, tasks, git hooks, and more.
- **`devenv.yaml`** — inputs, imports, and composition across folders or repos (lockfile via `devenv.lock`).
- **CLI** — `devenv init`, `devenv shell`, `devenv up` (processes/services), search/update helpers, optional containers and tests.

It integrates with [direnv](direnv-nix-direnv.md) (`use devenv` in `.envrc`). Recent devenv **2.x** versions (latest tag **v2.2** as of 2026-07) also support native shell hooks / auto-activation without direnv; direnv remains useful for in-place env loading. See [shells and direnv](../../11-development/shells-and-direnv.md) for the broader pattern.

devenv is a *wrapper around Nix*, not a replacement: evaluation and store builds still go through Nix.

### numtide/devshell

[numtide/devshell](https://github.com/numtide/devshell) aims at simpler per-project shells that stay compatible with `nix-shell`, direnv, and flakes. Notable ideas from the project:

- Cleaner interactive env than a default `stdenv`-heavy `mkShell` (fewer compiler/wrapper variables when you only want tools on `PATH`).
- Optional **TOML** config for common cases, with Nix as escape hatch.
- Welcome **MOTD** / command menu; usable as a flake app (`nix run`).

Treat it as an alternative or complement to devenv when you want a lighter shell module rather than devenv’s languages/services/processes stack.

### When to stay with raw Nix

Prefer plain `pkgs.mkShell` and flake `devShells` when you want minimal surface area, full control of the expression, or no extra CLI. Reach for devenv/devshell when the team values shared modules for languages, local services, or process orchestration. Language-specific toolchain notes live under [language toolchains](../../11-development/language-toolchains.md).

## Examples

Minimal devenv-style shell (illustrative; see upstream for current options):

```nix
# devenv.nix
{ pkgs, ... }: {
  packages = [ pkgs.git pkgs.jq ];

  env.GREET = "devenv";

  enterShell = ''
    echo "hello $GREET"
  '';
}
```

```bash
devenv init    # scaffolds devenv.nix, devenv.yaml, …
devenv shell   # enter the environment
```

Bare Nix equivalent shape (no devenv):

```nix
# flake.nix fragment — apps/devShells are flake outputs, not devenv modules
{
  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ pkgs.git pkgs.jq ];
      };
    };
}
```

```bash
nix develop    # enter that mkShell via the modern CLI
```

direnv + devenv (project `.envrc`; allow with `direnv allow`):

```bash
eval "$(devenv direnvrc)"
use devenv
```

## See also

- [direnv / nix-direnv](direnv-nix-direnv.md)
- [Shells and direnv](../../11-development/shells-and-direnv.md)
- [Language toolchains](../../11-development/language-toolchains.md)
- [nix build / develop / run](../modern-cli/nix-build-develop-run.md)
- [nix-shell](../classic-cli/nix-shell.md)

## References

- [devenv.sh](https://devenv.sh/) — official devenv site and docs (2.x as of 2026-07; latest release **v2.2**)
- [devenv getting started](https://devenv.sh/getting-started/) — `devenv init`, shell, `up`, update
- [devenv direnv integration](https://devenv.sh/integrations/direnv/)
- Source: [cachix/devenv](https://github.com/cachix/devenv)
- [numtide/devshell](https://github.com/numtide/devshell) — lighter project shell framework (README)
- [nixpkgs: pkgs.mkShell](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-mkShell)
