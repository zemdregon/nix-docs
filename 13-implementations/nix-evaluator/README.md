---
status: index
---

# Nix Evaluators

Implementations of the Nix language, store, and CLI. Four active lineages are documented here: the C++ reference shipped with NixOS, a compatible C++ fork, and two modular Rust efforts (TVL-side and independently hosted).

## Maturity snapshot

Last checked **2026-07-31**. Treat labels as a snapshot—verify before pinning production tooling to a non-default implementation. Detail lives on each leaf.

| Evaluator | Lineage | Posture (2026-07-31) |
|-----------|---------|----------------------|
| [CppNix](cpp-nix.md) | [NixOS/nix](https://github.com/NixOS/nix) C++ | Reference / NixOS-default |
| [Lix](lix.md) | C++ fork of CppNix | Production-oriented compatible fork (not identical feature set) |
| [Tvix](tvix.md) | TVL modular Rust (`//tvix`) | Experimental / research |
| [Snix](snix.md) | Independent continuation of modular Rust stack | Early / research (not a Tvix rename) |

Tvix and Snix share architectural heritage but diverged in March 2025: Tvix remains the TVL monorepo project; Snix continues the modular stack on dedicated infrastructure. See [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md).

## Contents

- [CppNix](cpp-nix.md) — Reference C++ Nix; NixOS default
- [Lix](lix.md) — Production-oriented C++ fork (compatible, not identical)
- [Tvix](tvix.md) — TVL research modular Rust (`//tvix`)
- [Snix](snix.md) — Independent modular Rust continuation (not a Tvix rename)
