---
status: complete
---

# Reading Manuals and Search

## Overview

The Nix stack ships three primary manuals plus a channel-aware search site. Pick the manual by *what you are changing* (evaluator/store/CLI, a package, or an OS module), then confirm option and package names against [search.nixos.org](https://search.nixos.org/options) for the channel or pin you actually use. This wiki explains patterns and vocabulary; it does **not** vendor full option or package trees — look those up upstream.

## Details

### Three manuals, three audiences

| Manual | Default URL | Use when you need… |
|--------|-------------|--------------------|
| **Nix** | [nix.dev/manual/nix/stable/](https://nix.dev/manual/nix/stable/) | Language, store, builders, `nix.conf`, CLI |
| **Nixpkgs** | [nixos.org/manual/nixpkgs/stable/](https://nixos.org/manual/nixpkgs/stable/) | Packaging, `stdenv`, overlays, language frameworks |
| **NixOS** | [nixos.org/manual/nixos/stable/](https://nixos.org/manual/nixos/stable/) | Modules, services, install/upgrade, system options |

Do not hunt NixOS service options in the Nixpkgs manual, or store/`nix.conf` details in the NixOS manual. Cross-links exist, but the primary audience split above is the fastest filter.

### Stable vs unstable vs versioned

- NixOS and Nixpkgs manuals publish **stable** and **unstable** trees (`…/stable/`, `…/unstable/`). Prefer the tree that matches your channel or flake input.
- The Nix manual also has a **stable** alias and **versioned** paths (for example `/manual/nix/2.34/`). When a flag, experimental feature, or CLI behavior depends on the Nix release you run, cite the versioned page — not only “latest.”

### Search: always match your pin

- [Options](https://search.nixos.org/options) and [packages](https://search.nixos.org/packages) are **channel-aware**. Set the channel (or equivalent) to the revision family you evaluate against before trusting names, types, or defaults.
- Blog posts and Discord snippets often omit channel context. Treat option and attribute names as hypotheses until search or the matching manual confirms them.
- Search shows declarations from nixpkgs/NixOS for that channel; your local overlays and custom modules will not appear there.

### Local help when available

On a NixOS system (or with the docs packages installed), prefer local sources that match the evaluated config:

- `man configuration.nix` — option appendix for the installed docs set
- `nixos-option` — query options against a configuration when the tool is on `PATH`
- nix-darwin: `darwin-help` (and the darwin option docs) instead of NixOS option search — see [nix-darwin](../10-home-and-user/nix-darwin.md)

### What this wiki deliberately skips

Leaf articles link to manuals and search for concrete option lists. For how options are *typed and declared*, see [Options and types](../09-nixos/architecture/options-and-types.md). For error-oriented lookups, keep [FAQ / common errors](../cheatsheets/faq-common-errors.md) and the [glossary](../glossary.md) nearby.

## Examples

**Wrong manual.** You want to know whether `services.nginx.enable` exists and what type its sibling options have → open [option search](https://search.nixos.org/options?query=services.nginx) (channel matched to your pin), not the Nix or Nixpkgs packaging chapters.

**Channel mismatch.** A tutorial written against `nixos-unstable` mentions an option that fails to evaluate on your `xx.xx` stable pin. Check search with *your* channel selected; if the option is absent, the tutorial is ahead of your pin (or wrong).

**Version-sensitive Nix CLI.** You are documenting or debugging a flag that appeared in a specific Nix release → open the versioned Nix manual for that release (e.g. `https://nix.dev/manual/nix/2.34/…`), and confirm with `nix --version` on the machine.

**Illustrative local checks** (names only; availability depends on install):

```bash
man configuration.nix
nixos-option services.openssh.enable
# nix-darwin hosts:
darwin-help
```

## See also

- [Beginner roadmap](beginner.md)
- [Operator roadmap](operator.md)
- [Glossary](../glossary.md)
- [FAQ / common errors](../cheatsheets/faq-common-errors.md)
- [Options and types](../09-nixos/architecture/options-and-types.md)
- [nix-darwin](../10-home-and-user/nix-darwin.md)

## References

- [Nix reference manual (stable)](https://nix.dev/manual/nix/stable/)
- [Nixpkgs manual (stable)](https://nixos.org/manual/nixpkgs/stable/)
- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/)
- [Configuration options search](https://search.nixos.org/options)
- [Package search](https://search.nixos.org/packages)
