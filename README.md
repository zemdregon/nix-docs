---
status: index
---

# Nix Docs

Plain-Markdown knowledge base for the full Nix stack: philosophy, language, store, nixpkgs, NixOS, flakes, experimental features, tooling, and current implementations.

Browse folders by number; each domain `README.md` lists its children. Conventions: [meta/conventions.md](meta/conventions.md).

**Published site:** [https://zemdregon.github.io/nix-docs/](https://zemdregon.github.io/nix-docs/) (MkDocs Material / GitHub Pages) — build notes in [meta/site.md](meta/site.md).

**v1 + Phase 7 (2026-08-01):** ~266 complete leaves including [16-configuration-examples](16-configuration-examples/README.md). Campaign plan: [EXPAND-PLAN.md](EXPAND-PLAN.md). Checklist: [meta/todo-coverage.md](meta/todo-coverage.md).

## How to navigate

Start with [00-roadmap](00-roadmap/README.md) (beginner / operator / contributor), or jump by domain below. Prefer relative links between topics. Want a full working config story? [16-configuration-examples](16-configuration-examples/README.md). Stuck? [FAQ: common errors](cheatsheets/faq-common-errors.md) then [Getting help and community](15-history-and-governance/getting-help-and-community.md). How to use upstream manuals: [Reading manuals and search](00-roadmap/reading-manuals-and-search.md).

## Domains

- [00-roadmap](00-roadmap/README.md) — Learning paths (beginner, operator, contributor)
- [01-philosophy](01-philosophy/README.md) — Design goals and tradeoffs
- [02-concepts](02-concepts/README.md) — Core vocabulary (derivation, closure, flake, …)
- [03-language](03-language/README.md) — Syntax, semantics, builtins, idioms
- [04-store-and-build](04-store-and-build/README.md) — Store, builders, caches, GC
- [05-cli-and-tooling](05-cli-and-tooling/README.md) — Classic/modern CLI, config, adjacent tools
- [06-nixpkgs](06-nixpkgs/README.md) — Architecture, packaging, overlays, contribution
- [07-flakes](07-flakes/README.md) — Schema, workflows, registries, migration
- [08-experimental-features](08-experimental-features/README.md) — Feature flags and experiments
- [09-nixos](09-nixos/README.md) — Modules, config, services, install, operations
- [10-home-and-user](10-home-and-user/README.md) — Home Manager, nix-darwin, multi-distro Nix
- [11-development](11-development/README.md) — Shells, CI, containers, tests
- [12-deployment-and-infra](12-deployment-and-infra/README.md) — Deploy tools, secrets, Hydra, caches
- [13-implementations](13-implementations/README.md) — Evaluators, UX, ecosystems, frameworks
- [14-security-and-trust](14-security-and-trust/README.md) — Trust, sandboxes, secrets, signing
- [15-history-and-governance](15-history-and-governance/README.md) — Timeline, foundation, RFCs, community help
- [16-configuration-examples](16-configuration-examples/README.md) — Picture-perfect multi-file configs that compose the domains above

## Cross-cutting

- [glossary.md](glossary.md) — Term index
- [comparisons](comparisons/README.md) — Nix vs related tools and models
- [cheatsheets](cheatsheets/README.md) — Dense quick references ([FAQ](cheatsheets/faq-common-errors.md))
- [meta](meta/README.md) — Conventions, sources, coverage, [site](meta/site.md), [example fixtures](meta/examples/README.md)
