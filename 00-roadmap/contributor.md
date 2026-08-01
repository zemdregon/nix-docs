---
status: complete
---

# Contributor Roadmap

Suggested reading order for packaging, NixOS modules, and upstream contribution. Skips day-2 ops; follow the [Operator](operator.md) path for that. This page is a curated reading order only — no runnable example.

## Goals

- Write and review Nix confidently enough to land packages and modules
- Navigate nixpkgs layout, contribution norms, and CI/review expectations
- Author and upstream NixOS modules; use flakes as a development and delivery workflow
- Know which evaluator/features/RFCs matter before you depend on them

## Prerequisites

- Comfortable with a shell and git (branches, PRs, rebases)
- Have run Nix or NixOS at least once (install or rebuild). If not, skim [Beginner](beginner.md) first
- Optional but useful: one language you will package (Python, Node, Rust, Go, …)

## Reading order

### 1. Mental model (light)

- [Why Nix](../01-philosophy/why-nix.md), [purity and reproducibility](../01-philosophy/purity-and-reproducibility.md), [hermetic builds](../01-philosophy/hermetic-builds.md)
- Core vocabulary: [derivation](../02-concepts/derivation.md), [closure](../02-concepts/closure.md), [fixed-output derivation](../02-concepts/fixed-output-derivation.md), [import from derivation](../02-concepts/import-from-derivation.md), [overlay vs override](../02-concepts/overlay-vs-override.md), [flake](../02-concepts/flake.md)

### 2. Language

- Hub: [Language](../03-language/README.md)
- Syntax and evaluation: [functions](../03-language/syntax/functions.md), [lists and attrsets](../03-language/syntax/lists-and-attrsets.md), [laziness](../03-language/semantics/laziness.md), [scoping and shadowing](../03-language/semantics/scoping-and-shadowing.md), [evaluation model](../03-language/semantics/evaluation-model.md), [purity boundaries](../03-language/semantics/purity-boundaries.md)
- Idioms used in nixpkgs: [callPackage](../03-language/idioms/callPackage.md), [overlays pattern](../03-language/idioms/overlays-pattern.md), [lib helpers](../03-language/idioms/lib-helpers.md), [anti-patterns](../03-language/idioms/anti-patterns.md)
- Quick ref: [language cheatsheet](../cheatsheets/language.md) or [03-language/cheatsheet](../03-language/cheatsheet.md)

### 3. Store and build surface

- [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md), [build phases](../04-store-and-build/build-phases.md), [hashing and inputs](../04-store-and-build/hashing-and-inputs.md), [debugging builds](../04-store-and-build/debugging-builds.md)
- Trust context when reviewing: [supply chain](../14-security-and-trust/supply-chain.md), [signing and caches](../14-security-and-trust/signing-and-caches.md), [reproducible builds audit](../14-security-and-trust/reproducible-builds-audit.md)

### 4. nixpkgs packaging and contribution

- Hub: [nixpkgs](../06-nixpkgs/README.md)
- Architecture: [stdenv](../06-nixpkgs/architecture/stdenv.md), [mkDerivation](../06-nixpkgs/architecture/mkDerivation.md), [package sets](../06-nixpkgs/architecture/package-sets.md), [lib](../06-nixpkgs/architecture/lib.md), [maintainers and teams](../06-nixpkgs/architecture/maintainers-and-teams.md)
- Packaging: [simple package](../06-nixpkgs/packaging/simple-package.md), [fetchers and pinning](../06-nixpkgs/packaging/fetchers-and-pinning.md), [patches and overrides](../06-nixpkgs/packaging/patches-and-overrides.md), [multiple outputs](../06-nixpkgs/packaging/multiple-outputs.md), [language ecosystems](../06-nixpkgs/packaging/python-node-rust-go.md), [tests and passthru](../06-nixpkgs/packaging/tests-and-passthru.md), [cross-compilation](../06-nixpkgs/packaging/cross-compilation.md)
- Local iteration: [writing overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md), [pinning](../06-nixpkgs/overlays-and-overrides/pinning.md)
- Upstream process: [contribution](../06-nixpkgs/contribution/README.md) — [review process](../06-nixpkgs/contribution/review-process.md), [ofborg and CI](../06-nixpkgs/contribution/ofborg-and-ci.md), [staging and branches](../06-nixpkgs/contribution/staging-and-branches.md)

### 5. NixOS modules (authoring, not operating)

- Architecture: [module system](../09-nixos/architecture/module-system.md), [module system internals](../09-nixos/architecture/module-system-internals.md) (freeformType / `evalModules`), [options and types](../09-nixos/architecture/options-and-types.md), [config vs options](../09-nixos/architecture/config-vs-options.md)
- Writing: [writing a module](../09-nixos/modules/writing-a-module.md), [mkIf / mkMerge / mkOrder](../09-nixos/modules/mkIf-mkMerge-mkOrder.md), [custom options](../09-nixos/modules/custom-options.md), [assertions and warnings](../09-nixos/modules/assertions-and-warnings.md), [upstreaming modules](../09-nixos/modules/upstreaming-modules.md)
- Patterns: [service patterns](../09-nixos/services/service-patterns.md), [NixOS options cheatsheet](../cheatsheets/nixos-options-patterns.md)
- Related ecosystems: [Home Manager modules](../10-home-and-user/home-manager/writing-hm-modules.md), [module ecosystems overview](../13-implementations/module-ecosystems/README.md)

### 6. Flakes as contributor workflow

- Schema: [flake.nix schema](../07-flakes/anatomy/flake-nix-schema.md), [inputs and outputs](../07-flakes/anatomy/inputs-and-outputs.md), [lockfile](../07-flakes/anatomy/lockfile.md), [follows and overrides](../07-flakes/anatomy/follow-and-overrides.md)
- Outputs you will ship or test: [packages / apps / devShells](../07-flakes/workflows/packages-apps-devShells.md), [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md), [templates](../07-flakes/workflows/templates.md), [nixosConfigurations](../07-flakes/workflows/nixos-configurations.md)
- Eval rules: [pure eval and impure](../07-flakes/pure-eval-and-impure.md); CLI: [nix flake](../05-cli-and-tooling/modern-cli/nix-flake.md)
- Context: [flakes vs channels](../comparisons/flakes-vs-channels.md)

### 7. Experimental features (awareness)

- [Feature flags overview](../08-experimental-features/feature-flags-overview.md), [nix-command](../08-experimental-features/nix-command.md), [flakes](../08-experimental-features/flakes.md)
- Packaging-adjacent: [ca-derivations](../08-experimental-features/ca-derivations.md), [dynamic derivations](../08-experimental-features/dynamic-derivations.md), [fetch-tree and git](../08-experimental-features/fetch-tree-and-git.md), [pipe operators](../08-experimental-features/pipe-operators-and-lang.md)
- Stabilization tracking: [tracking stabilization](../08-experimental-features/tracking-stabilization.md), [experimental backlog](../08-experimental-features/experimental-backlog.md)

### 8. Dev tooling for contribution

- [Shells and direnv](../11-development/shells-and-direnv.md), [language toolchains](../11-development/language-toolchains.md), [CI with Nix](../11-development/ci-with-nix.md), [testing NixOS VM tests](../11-development/testing-nixos-vm-tests.md), [debugging evaluation](../11-development/debugging-evaluation.md), [lazy trees and eval perf](../11-development/lazy-trees-and-eval-perf.md)
- Editor support: [LSP and IDE](../05-cli-and-tooling/adjacent-tools/lsp-and-ide.md); formatters: [alejandra / nixpkgs-fmt](../05-cli-and-tooling/adjacent-tools/alejandra-nixpkgs-fmt.md)
- Optional (GPU/ML packaging): [CUDA, ROCm, and ML stacks](../11-development/cuda-rocm-ml.md)

### 9. History, governance, and implementations

- [Timeline](../15-history-and-governance/timeline.md), [NixOS Foundation](../15-history-and-governance/nixos-foundation.md), [RFC process](../15-history-and-governance/rfc-process.md), [release cadence](../15-history-and-governance/release-cadence.md), [forks and governance splits](../15-history-and-governance/forks-and-governance-splits.md)
- Evaluators: [cpp Nix](../13-implementations/nix-evaluator/cpp-nix.md), [Lix](../13-implementations/nix-evaluator/lix.md), [Tvix](../13-implementations/nix-evaluator/tvix.md), [Snix](../13-implementations/nix-evaluator/snix.md)
- Frameworks you may meet in the wild: [flake-parts](../13-implementations/module-ecosystems/flake-parts.md), [community frameworks](../13-implementations/community-frameworks/README.md)

### Scenario paths (pick one track)

**First nixpkgs package PR** — [simple package](../06-nixpkgs/packaging/simple-package.md) + [example corpus](../meta/examples/simple-package.nix) → [fetchers and pinning](../06-nixpkgs/packaging/fetchers-and-pinning.md) → language builders ([Python/Node/Rust/Go](../06-nixpkgs/packaging/python-node-rust-go.md), [Haskell](../06-nixpkgs/packaging/haskell-packaging.md), [JVM/PHP/others](../06-nixpkgs/packaging/jvm-php-and-others.md) as needed) → [tests and passthru](../06-nixpkgs/packaging/tests-and-passthru.md) → [ofborg and CI](../06-nixpkgs/contribution/ofborg-and-ci.md) → [review process](../06-nixpkgs/contribution/review-process.md).

**NixOS module upstream** — [writing a module](../09-nixos/modules/writing-a-module.md) + [minimal-module.nix](../meta/examples/minimal-module.nix) → [module system internals](../09-nixos/architecture/module-system-internals.md) when merge/`specialArgs` bite → [custom options](../09-nixos/modules/custom-options.md) → [service patterns](../09-nixos/services/service-patterns.md) → [upstreaming modules](../09-nixos/modules/upstreaming-modules.md).

**Flake library / devShell** — [flake.nix schema](../07-flakes/anatomy/flake-nix-schema.md) + [hello-flake](../meta/examples/hello-flake/flake.nix) → [packages / apps / devShells](../07-flakes/workflows/packages-apps-devShells.md) → [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) → [CI with Nix](../11-development/ci-with-nix.md).

**Private inputs in CI** — [access tokens](../05-cli-and-tooling/config/access-tokens.md) → [private flakes and CI](../11-development/private-flakes-and-ci.md) → [config repo layout](../07-flakes/workflows/config-repo-layout.md) when the flake is a fleet mono-repo.

**Debugging eval failures** — [scoping and shadowing](../03-language/semantics/scoping-and-shadowing.md) → [laziness](../03-language/semantics/laziness.md) → [purity boundaries](../03-language/semantics/purity-boundaries.md) → [pure eval and impure](../07-flakes/pure-eval-and-impure.md) → [debugging evaluation](../11-development/debugging-evaluation.md) → [FAQ: common errors](../cheatsheets/faq-common-errors.md).

**Hash / fetch breakage** — [fixed-output derivation](../02-concepts/fixed-output-derivation.md) + [fod-fetchurl.nix](../meta/examples/fod-fetchurl.nix) → [debugging builds](../04-store-and-build/debugging-builds.md) → [fetchers and pinning](../06-nixpkgs/packaging/fetchers-and-pinning.md).

**Experimental feature in a PR** — [feature flags overview](../08-experimental-features/feature-flags-overview.md) → specific leaf (e.g. [ca-derivations](../08-experimental-features/ca-derivations.md)) → [tracking stabilization](../08-experimental-features/tracking-stabilization.md); stamp behavior in commit message / PR text.

### Example corpus (shared fixtures)

Reusable snippets under [meta/examples/](../meta/examples/README.md) — cite from your docs/PRs; not a second tutorial track. Validate locally when Nix is installed: `node meta/examples/validate.mjs`.

## Next steps

- Pick one concrete contribution: a package bump/add, a module fix, or an RFC comment — then work the relevant **scenario path** above as a checklist
- Shared snippets: [meta/examples](../meta/examples/README.md) (`hello-flake`, `overlay-snippet`, `minimal-module`, …)
- Eval/build symptom shortcuts: [FAQ: common errors](../cheatsheets/faq-common-errors.md) (IFD, FOD hash mismatch, pure-eval failures)
- Ask upstream after a minimal repro: [Getting help and community](../15-history-and-governance/getting-help-and-community.md)
- Use [glossary](../glossary.md) when terms collide; track wiki gaps in [todo-coverage](../meta/todo-coverage.md)
- Switch to [Operator](operator.md) only if you need install/rebuild/maintenance order, not for packaging or module design

## See also

- [Learning roadmaps](README.md) — path chooser
- [Beginner](beginner.md) — first-pass philosophy, concepts, and a working system
- [Operator](operator.md) — day-2 rebuild, deploy, and trust ops
- Upstream entry points (via leaf refs): [nixpkgs contribution](../06-nixpkgs/contribution/README.md), [RFC process](../15-history-and-governance/rfc-process.md)
- [Import from derivation](../02-concepts/import-from-derivation.md) — eval cost when packaging or reviewing flakes
- [Example corpus](../meta/examples/README.md) · [FAQ: common errors](../cheatsheets/faq-common-errors.md)
