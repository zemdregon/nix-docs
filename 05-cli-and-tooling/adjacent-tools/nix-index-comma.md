---
status: complete
last-checked: 2026-07
---

# nix-index / comma

## Overview

**nix-index** builds a local database mapping files (especially binaries under `bin/`) to the [nixpkgs](../../06-nixpkgs/README.md) packages that provide them. Query with `nix-locate`, or hook a shell **command-not-found** handler that suggests an attribute path when you type a missing command.

**comma** (the `,` command) uses that index to run a program from nixpkgs without installing it permanently—wrapping something like `nix shell nixpkgs#pkg -c …`. Together they answer “which package has this binary?” and “run it once now.”

Useful on NixOS and on other distros with Nix installed (see [Nix on other distros](../../10-home-and-user/nix-on-other-distros.md)). Building a full index locally can take several minutes; [nix-index-database](https://github.com/nix-community/nix-index-database) ships weekly prebuilt indexes (and modules that wire them in).

## Details

### nix-index

- Indexes built derivations from binary caches, not a full source tree walk.
- `nix-index` generates (or refreshes) the database under `~/.cache/nix-index/` by default.
- `nix-locate PATTERN` searches that database (e.g. `bin/hello`, or a library/header path).
- Optional shell integration: source the package’s `command-not-found` script so unknown commands print install / one-shot run hints. Disable NixOS’s stock `programs.command-not-found` if you replace it with nix-index’s handler.

### comma

- Prefix any command with `,` (e.g. `, cowsay hi`) to look up the package via the nix-index DB and run it in a temporary shell.
- Needs a current nix-index database (local `nix-index` or a prebuilt one).
- Optional caching of package choice and store path (`--cache-level` / `COMMA_CACHING`) speeds repeats; higher cache levels may lag behind the latest nixpkgs until GC / refresh.

### nix-index-database

- Weekly updated indexes for the nixos-unstable channel (nix-community).
- Offers NixOS, nix-darwin, and Home Manager modules that wrap `nix-index` / `nix-locate` against the prebuilt DB; optional `programs.nix-index-database.comma.enable` installs comma without duplicating packages in `systemPackages` / `home.packages`.
- **Full** DB (all files) vs **small** (binaries only)—small downloads faster and uses less memory when you only care about commands.
- Requires a recent enough Nix for the packaged database (project docs: **Nix 2.18+** for their packaging tricks; verified 2026-07).

Relation to the modern CLI: comma’s one-shot run is the same idea as [`nix shell` / `nix run`](../modern-cli/nix-build-develop-run.md), with the index choosing the attribute for you.

## Examples

Locate which package provides a binary:

```bash
nix-locate 'bin/hello'
```

One-shot run via comma (after database is present):

```bash
, cowsay neato
```

Equivalent without comma (you already know the attribute):

```bash
nix shell nixpkgs#cowsay -c cowsay neato
```

Ad-hoc download of a prebuilt index (from nix-index-database docs):

```bash
filename="index-$(uname -m | sed 's/^arm64$/aarch64/')-$(uname | tr A-Z a-z)"
mkdir -p ~/.cache/nix-index && cd ~/.cache/nix-index
wget -q -N "https://github.com/nix-community/nix-index-database/releases/latest/download/$filename"
ln -f "$filename" files
```

## See also

- [nix build / develop / run](../modern-cli/nix-build-develop-run.md) — `nix shell` / `nix run` without the index
- [nixpkgs](../../06-nixpkgs/README.md) — packages comma and nix-index resolve into
- [Nix on other distros](../../10-home-and-user/nix-on-other-distros.md) — same tools outside NixOS

## References

- [nix-community/nix-index](https://github.com/nix-community/nix-index) — README: `nix-index` / `nix-locate` (verified 2026-07)
- [nix-community/comma](https://github.com/nix-community/comma) — `,` one-shot runner
- [nix-community/nix-index-database](https://github.com/nix-community/nix-index-database) — weekly prebuilt indexes; Nix 2.18+ note
