---
status: complete
---

# Flake (concept)

## Overview

A **flake** is a Nix project's standardized entry point: a directory whose root contains `flake.nix`, declaring **inputs** (dependencies on other flakes or sources) and **outputs** (packages, NixOS modules, dev shells, and other values). The first time you build or evaluate, Nix writes **`flake.lock`**, pinning each input to an exact revision so two checkouts get the same dependency graph.

Flakes are an **experimental** feature (enable `nix-command` and `flakes` in `nix.conf`, or pass `--extra-experimental-features 'nix-command flakes'`). They are widely used for reproducible projects and replace the implicit `NIX_PATH` / `<nixpkgs>` lookup of [channels](channel.md) with explicit, version-controlled inputs. Schema, workflows, registries, and migration are covered in [Flakes](../07-flakes/README.md)—this page stays at the concept level.

## Details

**Entry file.** `flake.nix` must provide `outputs` (a function of the realized inputs). Optional top-level attributes include `description`, `inputs`, and `nixConfig`. Inputs are named references such as `nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05"`; `outputs` returns the artifacts this flake provides (often keyed by system, e.g. `packages.x86_64-linux.default`).

**Lockfile.** Unlocked URLs in `flake.nix` are resolved to concrete Git revisions (or tarball hashes) in [flake.lock](../07-flakes/anatomy/lockfile.md). Commit the lockfile so CI and collaborators share the same pins; run `nix flake update` when you intentionally bump inputs. That is the main reproducibility advantage over [channels](channel.md), which only track a moving release URL.

**Discovery and CLI.** Flakes integrate with the Nix 3 commands: `nix build`, `nix run`, `nix develop`, and `nix flake show` accept flake references like `.`, `github:owner/repo`, or `nixpkgs#hello`. A [flake registry](../07-flakes/registries-and-refs.md) maps symbolic names to default URLs.

**Pure evaluation.** Flake evaluation is **restricted**: no arbitrary access to the filesystem or environment unless declared as inputs. That supports hermetic, cache-friendly builds and makes “what went into this evaluation?” auditable. Impure escape hatches and flags are documented under [pure eval and impure](../07-flakes/pure-eval-and-impure.md).

**Not a tutorial surface.** Defining outputs, composing NixOS configurations, and publishing flakes belong in the [07-flakes](../07-flakes/README.md) domain and CLI docs—not here. Treat this page as vocabulary before reading those guides.

## Examples

- **Minimal shape:** `flake.nix` lists `inputs.nixpkgs` and exposes `outputs.packages.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.hello`.
- **Pinned third-party input:** After `nix build`, `flake.lock` records the exact `nixpkgs` commit; another clone builds against the same revision without running `nix-channel --update`.
- **Remote reference:** `nix run nixpkgs#hello` uses the registry to find Nixpkgs and run a package output—no local channel subscription required.

## References

- [Nix manual — flakes and `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — format, inputs, outputs, and lock file
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — high-level introduction
- [Nixpkgs manual](https://nixos.org/manual/nixpkgs/stable/) — package set typically consumed as a flake input
- [RFC 49 — Flakes](https://github.com/NixOS/rfcs/pull/49) — original design specification

## See also

- [Channel](channel.md) — classic nixpkgs distribution via `nix-channel`
- [Flakes](../07-flakes/README.md) — deep dive: anatomy, workflows, migration
- [Lockfile](../07-flakes/anatomy/lockfile.md) — structure and update semantics
- [Flakes vs Channels](../comparisons/flakes-vs-channels.md) — when to use which
- [flakes (experimental feature)](../08-experimental-features/flakes.md) — enabling and status in Nix
