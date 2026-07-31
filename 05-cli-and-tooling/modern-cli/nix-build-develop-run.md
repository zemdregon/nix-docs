---
status: complete
---

# nix build / develop / run

## Overview

`nix build`, `nix develop`, and `nix run` are the primary **installable-oriented** subcommands of the unified Nix 3 CLI. Together they cover the three everyday actions on derivations: **build** a package, **enter** its build environment, or **execute** a program.

These subcommands are still **experimental** (Nix stable manual as of 2026): interfaces may change between releases. They require the [`nix-command`](../../08-experimental-features/nix-command.md) feature. Flake installables (e.g. `nixpkgs#hello`, `.#`) also need [flakes](../../08-experimental-features/flakes.md). Historically both were off by default; enable them in `nix.conf` or per invocation with `--extra-experimental-features`.

Each command takes one or more **installables**—a shared syntax for pointing at a derivation, flake output, or store path. **`nix shell`** (manual page: `nix env shell`) is the related command for putting already-built packages on `$PATH`; it is **not** the same as `nix develop`.

For how flake outputs map to these commands, see [Packages, apps, devShells](../../07-flakes/workflows/packages-apps-devShells.md). Classic equivalents are [`nix-build`](../classic-cli/nix-build.md) and [`nix-shell`](../classic-cli/nix-shell.md).

## Details

### Experimental features

Enable `nix-command` (and usually `flakes`) in `nix.conf` or per invocation:

```bash
nix --extra-experimental-features 'nix-command flakes' build nixpkgs#hello
```

See [nix-command](../../08-experimental-features/nix-command.md) for the full feature-flag story. The remainder of this page assumes those features are enabled.

### Installables

Installables are the positional arguments after flags. Common forms:

| Form | Example | Meaning |
|------|---------|---------|
| Flake reference | `nixpkgs#hello`, `.#`, `.#myPkg` | Attribute from a flake (local `.` or registry name) |
| Attribute in a file | `nix build --file release.nix build.x86_64-linux` | Attribute path relative to a non-flake Nix file (`--file` implies `--impure`) |
| Inline expression | `nix build --impure --expr 'with import <nixpkgs> {}; hello'` | Attribute path relative to `--expr` (needs `--impure` when using `<nixpkgs>` / `$NIX_PATH`) |
| Store path | `/nix/store/…-hello-2.10` | Existing or substitutable store object |

Flake installables use `#` to separate the flake URL from the output name. Omitting the name selects each command's **default** output for the current system (see [nix flake](nix-flake.md) and [Packages, apps, devShells](../../07-flakes/workflows/packages-apps-devShells.md)).

Multiple installables are allowed on **`nix build`**. **`nix develop`** and **`nix run`** take a single installable.

### `nix build`

Builds derivations (locally or via substituters) or fetches store-path installables. Unless `--no-link` is set, it creates symlinks under the prefix `./result` (override with `--out-link` / `-o`). Each symlink gets a suffix `-<N>-<outname>`, where *N* is the installable index (omitted when *N* = 0) and *outname* is the derivation output name (omitted when it is the default `out`). So a second package becomes `result-1`, and `nixpkgs#glibc.dev` becomes `result-dev`.

Useful flags: `--print-out-paths` (print store paths; no need for the symlink), `--no-link`, `--profile` (record into a profile), `--json`. All outputs of a derivation: `"nixpkgs#openssl^*"`.

```bash
nix build                          # packages.<system>.default of flake in cwd
nix build nixpkgs#hello            # build hello from nixpkgs registry
nix build --file release.nix pkg   # attribute pkg in release.nix
./result/bin/hello
```

This subcommand replaces much of what [`nix-build`](../classic-cli/nix-build.md) did, with flake refs and consistent evaluation flags.

### `nix develop`

Starts an interactive **`bash`** shell whose environment matches what Nix would use to **build** the installable—compiler flags, `buildInputs`, stdenv phases, and related variables. It is for **developing** or debugging a package's build, not for casually running tools. Nix builds a modified derivation that records the `stdenv`-initialized environment and exits; that environment can be saved with `--profile`.

Without `#name`, resolution order is `devShells.<system>.default`, then `packages.<system>.default`. With a name: `devShells`, then `packages`, then `legacyPackages`.

You can run a single command instead of a shell (`--command` / `-c`), invoke individual stdenv phases (`--unpack`, `--configure`, `--build`, `--install`, …), redirect a dependency to a writable path (`--redirect`), or reuse a previously recorded profile.

```bash
nix develop                        # devShell or default package in cwd flake
nix develop nixpkgs#hello          # hello's build environment
nix develop --command cargo build  # one-shot command in that env
```

Contrast with [`nix-shell`](../classic-cli/nix-shell.md) (classic) and with **`nix shell`** below: `develop` gives you the **build** environment of a derivation; it does not simply prepend package `bin/` directories to `$PATH`.

### `nix run`

Builds (if needed) and **executes** a program from the installable. If the installable is an **app** (`type = "app"` with a `program` path in the store), that executable runs. If it is an ordinary derivation, Nix runs `$out/bin/<name>` where `<name>` is the first of: `meta.mainProgram`, then `pname`, then the name component of `name` (e.g. `hello-1.10` → `hello`).

Default resolution: `apps.<system>.default`, then `packages.<system>.default`. With a name: `apps`, then `packages`, then `legacyPackages`.

The first positional argument is always the installable. Pass program arguments after `--`, and name the installable explicitly when you want the flake default:

```bash
nix run nixpkgs#hello
nix run nixpkgs#vim -- --help
nix run . -- arg1 arg2             # args to the default app/package
nix run blender-bin#blender_2_83
```

### `nix shell` (brief)

**`nix shell`** (manual name: `nix env shell`) runs a command—or your `$SHELL` if none is given—with **`$PATH`** extended so the listed installables' packages are available. It is the modern, ephemeral counterpart to putting tools on PATH without entering a full build env or linking `./result`.

```bash
nix shell nixpkgs#hello            # interactive shell with hello on PATH
nix shell nixpkgs#hello --command hello --greeting 'Hi!'
```

Use **`nix develop`** when you need stdenv, hooks, and build-time dependencies for hacking on a derivation. Use **`nix shell`** when you only need binaries from built packages available temporarily.

### Command comparison

| Goal | Command | Typical outcome |
|------|---------|-----------------|
| Build and link outputs | `nix build` | `./result` → store path |
| Hack on building a package | `nix develop` | bash with build env |
| Run a program once | `nix run` | executes app or `$out/bin/…` |
| Temporary tools on PATH | `nix shell` | shell or `--command` with packages |

## Examples

**Flake in current directory** (requires `packages`, `apps`, and/or `devShells` outputs):

```bash
nix build              # → ./result
nix develop            # bash for building default package / devShell
nix run                # run default app or package binary
```

**Registry flake, explicit output:**

```bash
nix build nixpkgs#cowsay
nix run nixpkgs#cowsay -- --help
nix shell nixpkgs#jq nixpkgs#curl
```

**Multiple packages / print paths:**

```bash
nix build nixpkgs#hello nixpkgs#cowsay   # → result, result-1
nix build nixpkgs#hello --print-out-paths
```

**Non-flake expression:**

```bash
nix build --file ./default.nix myPackage
nix develop --file ./default.nix myPackage
```

**Inline expression** (needs `--impure` when using `<nixpkgs>` / `$NIX_PATH`):

```bash
nix build --impure --expr 'with import <nixpkgs> {}; hello' --print-out-paths
```

## References

- [Nix manual — `nix build`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-build.html) (experimental)
- [Nix manual — `nix develop`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop.html) (experimental)
- [Nix manual — `nix run`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-run.html) (experimental)
- [Nix manual — `nix env shell`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-env-shell.html) — `nix shell`; no separate `nix3-shell.html` on stable

## See also

- [nix-command](../../08-experimental-features/nix-command.md) — enabling the unified CLI
- [nix flake](nix-flake.md) — flake refs, registries, and output discovery
- [Packages, apps, devShells](../../07-flakes/workflows/packages-apps-devShells.md) — flake output conventions for these commands
- [nix-build](../classic-cli/nix-build.md) — classic build command
- [nix-shell](../classic-cli/nix-shell.md) — classic shell / build-env command
