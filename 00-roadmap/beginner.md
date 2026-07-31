---
status: complete
---

# Beginner Roadmap

First-pass reading order for someone new to Nix and NixOS. Skim each linked page; skip deep dives until a later pass. This page is a curated path only — no runnable example.

## Goals

- Understand *why* Nix exists (purity, declarativeness, rollbacks)
- Learn the core vocabulary: derivation, store path, closure, generation
- Read enough Nix language to follow configs, not write packages yet
- Install and configure a basic NixOS system, then meet flakes and keep cheatsheets handy

## Prerequisites

- Comfortable with a Linux shell and editing text files
- Willing to install NixOS in a VM or spare machine (recommended), or follow along conceptually
- No prior functional programming required

## Reading order

### 1. Philosophy

Start with the design goals so later mechanics make sense.

1. [Philosophy overview](../01-philosophy/README.md)
2. [Why Nix](../01-philosophy/why-nix.md)
3. [Purity and reproducibility](../01-philosophy/purity-and-reproducibility.md)
4. [Declarative vs imperative](../01-philosophy/declarative-vs-imperative.md)
5. [Immutability and rollback](../01-philosophy/immutability-and-rollback.md)

Optional: [hermetic builds](../01-philosophy/hermetic-builds.md), [tradeoffs](../01-philosophy/tradeoffs-and-critiques.md).

### 2. Concepts

Build the mental model before touching installers or flakes.

1. [Concepts overview](../02-concepts/README.md)
2. [Derivation](../02-concepts/derivation.md)
3. [Store path](../02-concepts/store-path.md)
4. [Closure](../02-concepts/closure.md)
5. [Generation](../02-concepts/generation.md) and [profile](../02-concepts/profile.md)
6. Skim [channel](../02-concepts/channel.md) and [flake (concept)](../02-concepts/flake.md) — deep dive later

### 3. Language (light pass)

Enough syntax to read `configuration.nix` and simple expressions.

1. [Language overview](../03-language/README.md)
2. [Literals](../03-language/syntax/literals.md)
3. [Strings and interpolation](../03-language/syntax/strings-and-interpolation.md)
4. [Lists and attrsets](../03-language/syntax/lists-and-attrsets.md)
5. [Functions](../03-language/syntax/functions.md)
6. [let-in and with](../03-language/syntax/let-in-and-with.md)

Skip builtins, idioms, and packaging patterns for now. Use the [language cheatsheet](../cheatsheets/language.md) while reading.

### 4. Store basics

How builds land on disk and why GC and caches matter.

1. [Store and build overview](../04-store-and-build/README.md)
2. [Nix store layout](../04-store-and-build/nix-store-layout.md)
3. [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md)
4. Skim [binary caches](../04-store-and-build/binary-caches.md) and [garbage collection](../04-store-and-build/garbage-collection.md)

### 5. NixOS install and config

Installation and a minimal system config — not a full ops tour.

1. [NixOS overview](../09-nixos/README.md)
2. [Installation overview](../09-nixos/installation/README.md) — prefer [graphical installer](../09-nixos/installation/graphical-installer.md); [manual install](../09-nixos/installation/manual-install.md) if needed
3. Optional context: [dual boot and VMs](../09-nixos/installation/dual-boot-and-vms.md) if you are installing beside another OS or practicing in a hypervisor guest
4. [configuration.nix](../09-nixos/configuration/configuration-nix.md)
5. [hardware-configuration](../09-nixos/configuration/hardware-configuration.md)
6. [Module system](../09-nixos/architecture/module-system.md) and [generations and boot](../09-nixos/architecture/generations-and-boot.md)
7. [rebuild: switch, boot, test](../09-nixos/operations/rebuild-switch-boot-test.md) and [rollbacks](../09-nixos/operations/rollbacks.md)

Optional (desktop install): [NixOS Desktop](../09-nixos/desktop/README.md) — compositors, PipeWire, fonts, Flatpak; defer gaming and printing until needed.

Defer services, custom modules, virtualization hosts, and remote deploy until you have a working system.

### 6. Flakes intro

After channels/concepts click, learn the flake surface.

1. [Flakes overview](../07-flakes/README.md)
2. [flake.nix schema](../07-flakes/anatomy/flake-nix-schema.md)
3. [Inputs and outputs](../07-flakes/anatomy/inputs-and-outputs.md)
4. [Lockfile](../07-flakes/anatomy/lockfile.md)
5. Optional: [NixOS configurations workflow](../07-flakes/workflows/nixos-configurations.md)

### 7. Cheatsheets

Keep these open while practicing:

- [Cheatsheets index](../cheatsheets/README.md)
- [CLI](../cheatsheets/cli.md)
- [Language](../cheatsheets/language.md)
- [NixOS options patterns](../cheatsheets/nixos-options-patterns.md)
- [FAQ: common errors](../cheatsheets/faq-common-errors.md) — symptom → cause → deeper leaf

## Next steps

- Follow the [operator roadmap](operator.md) for upgrades, troubleshooting, and day-2 ops
- From Ubuntu or Arch: [Ubuntu / Arch to NixOS](../comparisons/ubuntu-arch-to-nixos.md); other apt/pacman/Docker mental models in [comparisons](../comparisons/README.md)
- When ready to package or contribute: [contributor roadmap](contributor.md)
- Home-manager and nix-darwin live under [10-home-and-user](../10-home-and-user/README.md) — after a solid NixOS baseline
- Stuck on an error message: [FAQ: common errors](../cheatsheets/faq-common-errors.md)
- Glossary fallback: [glossary](../glossary.md)

## See also

- [Learning roadmaps](README.md) — path chooser
- [Operator](operator.md) — rebuilds, upgrades, deploy, secrets, caches
- [Contributor](contributor.md) — packaging, modules, nixpkgs contribution
- [Comparisons](../comparisons/README.md) — mental-model bridges from other ecosystems
