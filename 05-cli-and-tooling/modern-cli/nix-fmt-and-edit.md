---
status: complete
---

# nix fmt and edit

## Overview

**`nix fmt`** and **`nix edit`** are experimental Nix 3 subcommands for day-to-day package work: reformatting Nix source through a flake-defined formatter, and jumping to the `.nix` file that defines a package. Both require the [nix-command](../../08-experimental-features/nix-command.md) feature; **`nix fmt`** additionally needs [flakes](../../08-experimental-features/flakes.md) because it reads the **`formatter.<system>`** output from the nearest flake.

Behavior documented here follows the [stable Nix manual](https://nix.dev/manual/nix/stable/) and was checked against Nix 2.34.x. Subcommand flags and formatter integration can change between releases—confirm with `nix fmt --help` and the manual for your installed version.

## Details

### `nix fmt`

`nix fmt` is an alias for **`nix formatter run`**. From a directory inside a flake, it builds and runs the formatter declared in that flake’s outputs, then forwards arguments and flags to that program.

**Flake formatter output.** The flake must expose `formatter.<system>` as a derivation whose `$out/bin` is the formatter executable. The manual’s example wires [nixfmt-tree](https://github.com/NixOS/nixfmt) from nixpkgs:

```nix
# flake.nix (manual example; system binding omitted)
{
  outputs = { nixpkgs, self }: {
    formatter.x86_64-linux = nixpkgs.legacyPackages.${system}.nixfmt-tree;
  };
}
```

Which formatter you choose—official nixfmt, [Alejandra](../adjacent-tools/alejandra-nixpkgs-fmt.md), or another tool—is entirely up to the flake author. Nix does not define a formatter configuration schema beyond “run this derivation’s binary”; each formatter has its own CLI and config files.

**Invocation.**

- Run from within a flake tree (or a subdirectory): `nix fmt` formats according to the formatter’s defaults.
- Pass file paths as extra arguments: `nix fmt ./modules/foo.nix`.
- Forward formatter-specific flags after `--`: `nix fmt -- --check` (exact flags depend on the formatter).
- Nix sets **`PRJ_ROOT`** to the absolute path of the directory containing the closest parent `flake.nix` (per [prj-spec](https://github.com/numtide/prj-spec)); formatters may use it to locate project roots.

**Version and scope caveats.** Without a flake or without a `formatter.<system>` output for the current system, `nix fmt` cannot run. Formatter choice, check-vs-write semantics, and default file globs are defined by the formatter package—not by `nix fmt` itself. Community formatters and nixpkgs packaging notes are covered on the [Alejandra / nixpkgs-fmt](../adjacent-tools/alejandra-nixpkgs-fmt.md) page. Running `nix fmt` realizes the formatter derivation (may substitute or build).

### `nix edit`

**`nix edit`** opens the Nix expression that defines a derivation in **`$EDITOR`**. It takes a single [installable](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html#installables) (for example a flake ref or attribute path).

**How the file is chosen.** Nix uses the derivation’s **`meta.position`** attribute: a string `"<path>:<line>"`. In nixpkgs, **`stdenv.mkDerivation`** sets `meta.position` to the location of the `meta.description`, `version`, or `name` attribute in the calling file—typically the package’s `default.nix` or inline call site.

**Editor behavior.**

- **`EDITOR`** selects the program; if unset, Nix defaults to **`cat`** (prints the path only).
- For **`emacs`**, **`nano`**, **`vim`**, and **`kak`**, Nix passes **`+<lineno>`** so the editor opens on the definition line.

**Related inspection.** To print the path without launching an editor (eval-only; no package build):

```bash
nix eval --raw nixpkgs#hello.meta.position
# or: nix-instantiate --eval -E 'with import <nixpkgs> {}; hello.meta.position'
```

Flake refs like `nixpkgs#hello` require both **nix-command** and **flakes**; classic `-f` / `-A` installables work with **nix-command** alone. See [nix flake](nix-flake.md) for flake-oriented CLI commands.

## Examples

Enable experimental features for one-off use:

```bash
nix --extra-experimental-features 'nix-command flakes' fmt
nix --extra-experimental-features 'nix-command flakes' edit nixpkgs#hello
```

Format specific paths and pass a formatter check flag (syntax depends on the formatter; may build the formatter):

```bash
nix fmt -- ./flake.nix ./modules/
nix fmt -- --check
```

Open a package definition and inspect its source location:

```bash
export EDITOR=vim
nix edit nixpkgs#hello
nix eval --raw nixpkgs#hello.meta.position
```

## References

- [Nix manual — `nix fmt`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-fmt.html) — flake formatter integration, `PRJ_ROOT`, forwarding args
- [Nix manual — `nix edit`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-edit.html) — `meta.position`, `$EDITOR`, line-number handling
- [Nix manual — installables](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html#installables) — flake refs and attribute paths for `nix edit`

## See also

- [nix-command](../../08-experimental-features/nix-command.md) — enables the unified Nix 3 CLI
- [nix flake](nix-flake.md) — flake subcommands (`show`, `update`, …)
- [Alejandra / nixpkgs-fmt](../adjacent-tools/alejandra-nixpkgs-fmt.md) — community formatters often wired as `formatter.<system>`
