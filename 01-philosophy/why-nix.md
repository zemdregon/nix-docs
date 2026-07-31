---
status: complete
---

# Why Nix

## Overview

Nix is a package manager and build system aimed at **repeatable environments**: the same description should produce the same result on your laptop, in CI, and on a server. It tackles a familiar failure mode of conventional package managers—**dependency hell** and **incomplete dependency specifications**—by treating each build as a pure function of its inputs and storing every output in an isolated, hashed path under `/nix/store`.

That model supports multiple versions side by side, transparent source-or-binary installs, and (with NixOS) whole-system configuration with atomic upgrades and rollbacks. The [nix.dev](https://nix.dev/) learning materials assume comfort with the command line and a need for environments you can reproduce and share.

## Details

### The problem Nix targets

Traditional installs mix packages into shared prefixes (`/usr`, `/opt/homebrew`, …). Upgrades overwrite files in place; implicit runtime dependencies are easy to miss; two projects may need incompatible versions of the same library. Rollback means hoping backups or manual undo still match reality.

Nix instead records **what** goes into a build and **what** comes out. Each package lives at a unique store path whose name includes a cryptographic hash of its inputs, so changing a dependency changes the path. Old paths remain until garbage-collected, so upgrades do not silently break other software still linked to an earlier generation.

### Functional package descriptions

Builds are described in the [Nix language](https://nix.dev/manual/nix/stable/language/) as expressions that declare sources, build steps, and dependencies. Evaluation yields a [derivation](../02-concepts/derivation.md)—a build recipe—whose output path is fixed by its inputs. When the sandbox and fixed-output rules hold, builds aim to be **deterministic**: the same expression and inputs yield the same store path on any machine that can build it.

See [functional package management](functional-package-management.md), [purity and reproducibility](purity-and-reproducibility.md), and [hermetic builds](hermetic-builds.md) for how that philosophy shows up in practice.

### Store, closures, and caches

Everything installed through Nix is a symlink farm into `/nix/store`. A package’s **closure** is the full set of store paths it needs at runtime, computed from declared dependencies rather than whatever happened to be on `$PATH` yesterday.

If a path is not already local, Nix can **substitute** a bit-identical copy from a **binary cache** (for example [cache.nixos.org](https://cache.nixos.org/)) or build from source. From the user’s perspective the source-or-binary choice is transparent: the store path is the unit of correctness, not the install mechanism.

### Beyond single packages

The same ideas scale to **declarative configuration**: NixOS describes an entire OS—kernel, services, users—from one configuration. Activating a new generation is an **atomic switch**; the previous generation stays bootable until you discard it, which enables [rollback](immutability-and-rollback.md) without ad hoc snapshots. Home Manager and nix-darwin apply the pattern to user environments on Linux and macOS.

Nix is not the only answer to reproducibility (containers, language-specific lockfiles, and immutable OS images each address part of the problem). Its distinguishing bet is a **single store and language** for packages, development shells, and system config, with sharing and caching across all of them.

## Examples

**Side-by-side versions.** Project A needs OpenSSL 1.1; project B needs OpenSSL 3. Both closures can coexist in the store because each resolved dependency graph gets its own hashed paths. Nothing in `/nix/store` is overwritten when you add B’s environment.

**Reproducible dev shell.** A `shell.nix` or flake dev shell pins compiler and library versions in the expression. A colleague checks out the repo, enters the shell, and gets the same toolchain paths you use—without a separate “setup script” that drifts from the declared inputs.

**NixOS generation switch.** After changing `configuration.nix`, `nixos-rebuild switch` builds or substitutes a new system profile and flips the boot default. If something breaks, `nixos-rebuild switch --rollback` (or choosing the previous generation at boot) returns to the last known-good closure.

These scenarios are expanded in the [beginner roadmap](../00-roadmap/beginner.md); they intentionally stay high level here.

## References

- [nix.dev — Nix documentation home](https://nix.dev/)
- [Nix manual — introduction](https://nix.dev/manual/nix/stable/introduction.html)
- [Nix manual — Nix store](https://nix.dev/manual/nix/stable/store/index.html)
- [Nix manual — serving a store via HTTP (binary caches)](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html) (see also [cache.nixos.org](https://cache.nixos.org/))
- [NixOS manual — system configuration](https://nixos.org/manual/nixos/stable/index.html#ch-configuration)
- E. Dolstra, *The Purely Functional Software Deployment Model* ([PhD thesis PDF](https://edolstra.github.io/pubs/phd-thesis.pdf)) — historical design rationale; cite for background, not as a normative spec for current Nix.

## See also

- [Declarative vs imperative](declarative-vs-imperative.md)
- [Immutability and rollback](immutability-and-rollback.md)
- [Derivation](../02-concepts/derivation.md)
