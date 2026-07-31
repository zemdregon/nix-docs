---
status: index
---

# Nix Docs

Plain-Markdown knowledge base for the full Nix stack: philosophy, language, store, nixpkgs, NixOS, flakes, experimental features, tooling, and current implementations.

No site generator. Browse folders by number; each domain `README.md` lists its children. Opens as an [Obsidian](https://obsidian.md/) vault (Open folder as vault → this directory); vault settings and plugins: [meta/obsidian.md](meta/obsidian.md); Dataview status tables: [meta/dashboard.md](meta/dashboard.md).

**v1 (2026-07-31):** Stable Obsidian / plain-Markdown vault. Content campaign through Phase 4 landed; Phase 1 quality deepen and Phase 2 gold/consistency polish on high-traffic leaves also landed (~247 complete leaves, 0 broken relative `.md` links). Remaining work is release cadence refresh and optional further calibration — see [EXPAND-PLAN.md](EXPAND-PLAN.md) and [meta/todo-coverage.md](meta/todo-coverage.md). Site generator still deferred (optional Phase 5). Historical draft campaign: [ATTACK-PLAN.md](ATTACK-PLAN.md).

## How to navigate

Start with [00-roadmap](00-roadmap/README.md) for a suggested path, or jump by domain below. Prefer relative links between topics. Conventions for stubs and growth live in [meta/conventions.md](meta/conventions.md).

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
- [15-history-and-governance](15-history-and-governance/README.md) — Timeline, foundation, RFCs, releases

## Cross-cutting

- [glossary.md](glossary.md) — Term index
- [comparisons](comparisons/README.md) — Nix vs related tools and models
- [cheatsheets](cheatsheets/README.md) — Dense quick references
- [meta](meta/README.md) — Conventions, sources, coverage tracking
