---
status: complete
---

# Pinning

## Overview

**Pinning** fixes Nixpkgs (and other expression sources) to a known Git revision or tarball hash so evaluation and builds do not float with [channel](../../02-concepts/channel.md) HEAD or an unpinned `import <nixpkgs>`. Without a pin, two machines—or the same machine on different days—can resolve different package versions even when configuration files are identical.

Pinning is separate from [overlays](writing-overlays.md) and overrides: it chooses *which* [package set](../architecture/package-sets.md) you import; overlays and `packageOverrides` reshape that set afterward. The preferred modern path is [flakes](../../02-concepts/flake.md) with a committed [flake.lock](../../07-flakes/anatomy/lockfile.md). Classic workflows pin inside the expression with `builtins.fetchTarball` / `builtins.fetchGit`, via `NIX_PATH`, or with small helper tools such as [niv](https://github.com/nmattia/niv) or [npins](https://github.com/serokell/npins).

## Details

**Why pin.** [Channels](../../02-concepts/channel.md) point at release lines, not single commits. Hydra tests and publishes channel snapshots asynchronously from `nixpkgs` `master`, so `nix-channel --update` can pull in surprise upgrades—new defaults, broken packages, or changed dependency graphs. Pinning makes the nixpkgs revision an explicit, reviewable input in your repo or shell expression.

**Pin the whole set vs pin inside the set.** Most projects pin the entire nixpkgs import once, then apply overlays on that fixed `pkgs`. You can also pin individual upstream sources *inside* nixpkgs (for example a specific commit of a library via `fetchFromGitHub` in an overlay), but that does not freeze the rest of the set. For reproducible environments, start with a pinned nixpkgs, then layer [writing overlays](writing-overlays.md) or per-package `.override` as needed.

**Flakes (preferred).** Declare `inputs.nixpkgs.url` in `flake.nix` (often a release branch such as `github:NixOS/nixpkgs/nixos-26.05`). The first flake evaluation writes [flake.lock](../../07-flakes/anatomy/lockfile.md), recording each input's exact `rev` and content hash. Commit the lockfile; bump intentionally with `nix flake update`. See [Migration from channels](../../07-flakes/migration-from-channels.md) for moving off `nix-channel` and `<nixpkgs>`.

**Classic: fetch in the expression.** Import nixpkgs from a hash-pinned tarball or Git tree so evaluation does not depend on host `NIX_PATH`:

- `builtins.fetchTarball { url = "…/archive/<rev>.tar.gz"; sha256 = "…"; }` — common for GitHub archive URLs.
- `builtins.fetchGit { url = "…"; rev = "…"; ref = "…"; }` — Git checkout pinned by commit.

Always supply `sha256` (tarballs) or a fixed `rev` (Git). Unhashed tarballs honor `tarball-ttl` and can change across runs. See [import and fetch](../../03-language/builtins/import-and-fetch.md) for fetcher behavior and pure-eval constraints.

**Classic: NIX_PATH and `-I`.** You can pin by setting `NIX_PATH=nixpkgs=<path-or-url>` or passing `-I nixpkgs=…` to `nix-build` / `nix-shell`. A tarball URL or `channel:nixos-26.05` shorthand works, but channel URLs still track the *current* channel snapshot, not an immutable Git commit. For VCS-tracked configs, prefer a commit-pinned tarball URL or a flake lock over a moving channel URL.

**Helper tools (optional).** [niv](https://github.com/nmattia/niv) and [npins](https://github.com/serokell/npins) generate or update JSON sources files and Nix glue so teams can bump pins without hand-editing hashes. They are alternatives when you want lockfile-like workflow without full flakes; this wiki does not document their CLI in detail—see upstream READMEs.

**Overlays on a pinned import.** Pattern: fetch or flake-input nixpkgs once, `import` it with your `config` and `overlays` list, and use the resulting `pkgs` everywhere in the project. Overlays do not pin nixpkgs by themselves; they only modify whatever revision you already imported.

**Choosing a revision.** Release branches (`nixos-26.05`, `nixpkgs-unstable`) identify lines; pick a concrete commit from [status.nixos.org](https://status.nixos.org/) when you need a tested snapshot, or lock via flakes and review `flake.lock` diffs on update.

## Examples

**Flake input (sketch):**

```nix
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  outputs = { self, nixpkgs, ... }: {
    packages.x86_64-linux.default =
      nixpkgs.legacyPackages.x86_64-linux.hello;
  };
}
```

Run any flake command once, commit `flake.lock`, and share the locked graph.

**Hash-pinned tarball import:**

```nix
let
  nixpkgs = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/abc123def456.tar.gz";
    sha256 = "0000000000000000000000000000000000000000000000000000"; # replace
  };
  pkgs = import nixpkgs {
    overlays = [ (final: prev: { /* … */ }) ];
  };
in pkgs.hello
```

On first build with a wrong hash, Nix prints the correct `sha256` in the error; `nix-prefetch-url --unpack <url>` also works.

**Git pin:**

```nix
import (builtins.fetchGit {
  url = "https://github.com/NixOS/nixpkgs";
  ref = "nixos-26.05";
  rev = "abc123def4567890abcdef1234567890abcdef12";
}) { }
```

## References

- [Nixpkgs manual](https://nixos.org/manual/nixpkgs/stable/) — package sets, overlays, and import patterns
- [nix.dev — Pinning Nixpkgs](https://nix.dev/reference/pinning-nixpkgs) — URL forms, `-I`, and `NIX_PATH` examples
- [nix.dev — Towards reproducibility: pinning Nixpkgs](https://nix.dev/tutorials/first-steps/towards-reproducibility-pinning-nixpkgs) — introductory `fetchTarball` workflow
- [Nix manual — flakes](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — flake commands and lockfile integration

## See also

- [Channel (concept)](../../02-concepts/channel.md) — moving snapshots vs exact pins
- [Flake (concept)](../../02-concepts/flake.md) — inputs and lockfiles
- [Lockfile](../../07-flakes/anatomy/lockfile.md) — `flake.lock` structure and updates
- [Migration from channels](../../07-flakes/migration-from-channels.md) — flakes as the primary reproducible path
- [Package sets](../architecture/package-sets.md) — what a pinned import evaluates to
- [Writing overlays](writing-overlays.md) — customizing a pinned `pkgs`
