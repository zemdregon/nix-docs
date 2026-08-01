---
status: active
---

# Coverage TODO

Living checklist. Sole campaign plan: [EXPAND-PLAN.md](../EXPAND-PLAN.md) (Phases 0–4, 6, 7 done; Phase 5.1 cadence ongoing). Draft weeks 0–11 history only — [ATTACK-PLAN.md](../ATTACK-PLAN.md) is a redirect.

**Meta truth snapshot (2026-08-01 — Phase 7 closed):** ~274 leaf articles `status: complete` (quality audit); intentional drafts: [self-healing-config-mesh](../12-deployment-and-infra/self-healing-config-mesh.md) + living [sources.md](sources.md); ~49 folder READMEs `status: index` (includes [16-configuration-examples](../16-configuration-examples/README.md)). Relative `.md` links: 0 broken in repo root (see [Audit hook](#audit-hook)). **Site:** [zemdregon.github.io/nix-docs](https://zemdregon.github.io/nix-docs/). **Active:** Phase 5.1 cadence only ([release-checklist.md](release-checklist.md)). Status lives in YAML frontmatter.

Weeks below are **historical** draft-campaign checkoffs. Phase 7 batches A–L are **closed** (see below). Track ongoing work under [Remaining work](#remaining-work).

## Structure / Week 0 (bootstrap)

- [x] Numbered domain directories and stub leaves
- [x] Root map and [conventions.md](conventions.md)
- [x] `00-roadmap/` draft paths (chooser + beginner / operator / contributor)
- [x] Concrete URLs in [sources.md](sources.md)
- [x] Week-keyed checklist (this file)
- [x] [research-method.md](research-method.md)

## Week 1 — `01-philosophy` + `02-concepts`

Mental model domain to **draft**.

### `01-philosophy/`

- [x] [why-nix.md](../01-philosophy/why-nix.md)
- [x] [declarative-vs-imperative.md](../01-philosophy/declarative-vs-imperative.md)
- [x] [functional-package-management.md](../01-philosophy/functional-package-management.md)
- [x] [purity-and-reproducibility.md](../01-philosophy/purity-and-reproducibility.md)
- [x] [hermetic-builds.md](../01-philosophy/hermetic-builds.md)
- [x] [immutability-and-rollback.md](../01-philosophy/immutability-and-rollback.md)
- [x] [tradeoffs-and-critiques.md](../01-philosophy/tradeoffs-and-critiques.md)

### `02-concepts/`

- [x] [derivation.md](../02-concepts/derivation.md)
- [x] [store-path.md](../02-concepts/store-path.md)
- [x] [closure.md](../02-concepts/closure.md)
- [x] [profile.md](../02-concepts/profile.md)
- [x] [generation.md](../02-concepts/generation.md)
- [x] [channel.md](../02-concepts/channel.md)
- [x] [flake.md](../02-concepts/flake.md)
- [x] [overlay.md](../02-concepts/overlay.md)
- [x] [overlay-vs-override.md](../02-concepts/overlay-vs-override.md)
- [x] [fixed-output-derivation.md](../02-concepts/fixed-output-derivation.md)
- [x] [content-addressed-store.md](../02-concepts/content-addressed-store.md)

## Week 2 — `03-language` syntax + semantics

- [x] Syntax: [literals](../03-language/syntax/literals.md), [strings-and-interpolation](../03-language/syntax/strings-and-interpolation.md), [lists-and-attrsets](../03-language/syntax/lists-and-attrsets.md), [functions](../03-language/syntax/functions.md), [let-in-and-with](../03-language/syntax/let-in-and-with.md), [operators](../03-language/syntax/operators.md), [conditionals-and-asserts](../03-language/syntax/conditionals-and-asserts.md), [antiquotation-and-paths](../03-language/syntax/antiquotation-and-paths.md), [comments-and-formatting](../03-language/syntax/comments-and-formatting.md)
- [x] Semantics: [evaluation-model](../03-language/semantics/evaluation-model.md), [laziness](../03-language/semantics/laziness.md), [types-and-coercion](../03-language/semantics/types-and-coercion.md), [scoping-and-shadowing](../03-language/semantics/scoping-and-shadowing.md), [purity-boundaries](../03-language/semantics/purity-boundaries.md)

## Week 3 — `03-language` builtins/idioms + `04-store-and-build`

- [x] Builtins: [attrset-list-string](../03-language/builtins/attrset-list-string.md), [path-and-filesystem](../03-language/builtins/path-and-filesystem.md), [import-and-fetch](../03-language/builtins/import-and-fetch.md), [derivation-builtins](../03-language/builtins/derivation-builtins.md), [debugging-trace](../03-language/builtins/debugging-trace.md)
- [x] Idioms: [callPackage](../03-language/idioms/callPackage.md), [overlays-pattern](../03-language/idioms/overlays-pattern.md), [rec-and-fixed-points](../03-language/idioms/rec-and-fixed-points.md), [lib-helpers](../03-language/idioms/lib-helpers.md), [anti-patterns](../03-language/idioms/anti-patterns.md)
- [x] [cheatsheet.md](../03-language/cheatsheet.md)
- [x] Store: [nix-store-layout](../04-store-and-build/nix-store-layout.md), [hashing-and-inputs](../04-store-and-build/hashing-and-inputs.md), [build-phases](../04-store-and-build/build-phases.md), [builders-and-sandboxes](../04-store-and-build/builders-and-sandboxes.md), [garbage-collection](../04-store-and-build/garbage-collection.md), [binary-caches](../04-store-and-build/binary-caches.md), [substitutes-and-narinfo](../04-store-and-build/substitutes-and-narinfo.md), [remote-builders](../04-store-and-build/remote-builders.md), [store-protocols](../04-store-and-build/store-protocols.md), [debugging-builds](../04-store-and-build/debugging-builds.md)

## Week 4 — `09-nixos` architecture + configuration

- [x] Architecture: [module-system](../09-nixos/architecture/module-system.md), [options-and-types](../09-nixos/architecture/options-and-types.md), [config-vs-options](../09-nixos/architecture/config-vs-options.md), [activation-script](../09-nixos/architecture/activation-script.md), [generations-and-boot](../09-nixos/architecture/generations-and-boot.md), [systemd-integration](../09-nixos/architecture/systemd-integration.md)
- [x] Configuration: [configuration-nix](../09-nixos/configuration/configuration-nix.md), [hardware-configuration](../09-nixos/configuration/hardware-configuration.md), [imports-and-profiles](../09-nixos/configuration/imports-and-profiles.md), [users-and-groups](../09-nixos/configuration/users-and-groups.md), [networking](../09-nixos/configuration/networking.md), [partitioning-and-bootloaders](../09-nixos/configuration/partitioning-and-bootloaders.md), [secrets-strategies](../09-nixos/configuration/secrets-strategies.md)

## Week 5 — rest of `09-nixos`

- [x] Modules: [writing-a-module](../09-nixos/modules/writing-a-module.md), [custom-options](../09-nixos/modules/custom-options.md), [mkIf-mkMerge-mkOrder](../09-nixos/modules/mkIf-mkMerge-mkOrder.md), [assertions-and-warnings](../09-nixos/modules/assertions-and-warnings.md), [upstreaming-modules](../09-nixos/modules/upstreaming-modules.md)
- [x] Services: [service-patterns](../09-nixos/services/service-patterns.md), [common-service-examples](../09-nixos/services/common-service-examples.md), [containers-and-nspawn](../09-nixos/services/containers-and-nspawn.md), [declarative-containers](../09-nixos/services/declarative-containers.md)
- [x] Installation: [graphical-installer](../09-nixos/installation/graphical-installer.md), [manual-install](../09-nixos/installation/manual-install.md), [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md), [dual-boot-and-vms](../09-nixos/installation/dual-boot-and-vms.md)
- [x] Operations: [rebuild-switch-boot-test](../09-nixos/operations/rebuild-switch-boot-test.md), [rollbacks](../09-nixos/operations/rollbacks.md), [upgrades](../09-nixos/operations/upgrades.md), [remote-deploy](../09-nixos/operations/remote-deploy.md), [troubleshooting](../09-nixos/operations/troubleshooting.md)

## Week 6 — `07-flakes` + `08-experimental-features`

- [x] Flakes anatomy: [flake-nix-schema](../07-flakes/anatomy/flake-nix-schema.md), [inputs-and-outputs](../07-flakes/anatomy/inputs-and-outputs.md), [lockfile](../07-flakes/anatomy/lockfile.md), [follow-and-overrides](../07-flakes/anatomy/follow-and-overrides.md)
- [x] Flakes workflows: [packages-apps-devShells](../07-flakes/workflows/packages-apps-devShells.md), [nixos-configurations](../07-flakes/workflows/nixos-configurations.md), [home-configurations](../07-flakes/workflows/home-configurations.md), [checks-and-hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md), [templates](../07-flakes/workflows/templates.md)
- [x] [registries-and-refs](../07-flakes/registries-and-refs.md), [pure-eval-and-impure](../07-flakes/pure-eval-and-impure.md), [migration-from-channels](../07-flakes/migration-from-channels.md)
- [x] Experimental: [feature-flags-overview](../08-experimental-features/feature-flags-overview.md), [flakes](../08-experimental-features/flakes.md), [nix-command](../08-experimental-features/nix-command.md), [ca-derivations](../08-experimental-features/ca-derivations.md), [fetch-tree-and-git](../08-experimental-features/fetch-tree-and-git.md), [dynamic-derivations](../08-experimental-features/dynamic-derivations.md), [impure-derivations](../08-experimental-features/impure-derivations.md), [recursive-nix](../08-experimental-features/recursive-nix.md), [auto-allocate-uids](../08-experimental-features/auto-allocate-uids.md), [cgroups](../08-experimental-features/cgroups.md), [pipe-operators-and-lang](../08-experimental-features/pipe-operators-and-lang.md), [tracking-stabilization](../08-experimental-features/tracking-stabilization.md)

## Week 7 — `06-nixpkgs` + start `05-cli-and-tooling`

- [x] Nixpkgs architecture: [stdenv](../06-nixpkgs/architecture/stdenv.md), [mkDerivation](../06-nixpkgs/architecture/mkDerivation.md), [lib](../06-nixpkgs/architecture/lib.md), [package-sets](../06-nixpkgs/architecture/package-sets.md), [maintainers-and-teams](../06-nixpkgs/architecture/maintainers-and-teams.md)
- [x] Packaging: [simple-package](../06-nixpkgs/packaging/simple-package.md), [multiple-outputs](../06-nixpkgs/packaging/multiple-outputs.md), [patches-and-overrides](../06-nixpkgs/packaging/patches-and-overrides.md), [cross-compilation](../06-nixpkgs/packaging/cross-compilation.md), [python-node-rust-go](../06-nixpkgs/packaging/python-node-rust-go.md), [tests-and-passthru](../06-nixpkgs/packaging/tests-and-passthru.md), [haskell-packaging](../06-nixpkgs/packaging/haskell-packaging.md), [jvm-php-and-others](../06-nixpkgs/packaging/jvm-php-and-others.md)
- [x] Overlays: [writing-overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md), [packageOverrides](../06-nixpkgs/overlays-and-overrides/packageOverrides.md), [pinning](../06-nixpkgs/overlays-and-overrides/pinning.md)
- [x] Contribution: [review-process](../06-nixpkgs/contribution/review-process.md), [staging-and-branches](../06-nixpkgs/contribution/staging-and-branches.md), [ofborg-and-ci](../06-nixpkgs/contribution/ofborg-and-ci.md)
- [x] CLI (start): modern + classic leaves under [05-cli-and-tooling/](../05-cli-and-tooling/README.md)

## Week 8 — finish CLI; `10-home-and-user` + `11-development`

- [x] Remaining [05-cli-and-tooling/](../05-cli-and-tooling/README.md) (config + adjacent tools)
- [x] Home/user: [standalone-vs-nixos-module](../10-home-and-user/home-manager/standalone-vs-nixos-module.md), [writing-hm-modules](../10-home-and-user/home-manager/writing-hm-modules.md), [dotfiles-patterns](../10-home-and-user/home-manager/dotfiles-patterns.md), [nix-darwin](../10-home-and-user/nix-darwin.md), [nix-on-other-distros](../10-home-and-user/nix-on-other-distros.md)
- [x] Dev: [shells-and-direnv](../11-development/shells-and-direnv.md), [language-toolchains](../11-development/language-toolchains.md), [ci-with-nix](../11-development/ci-with-nix.md), [containers-oci](../11-development/containers-oci.md), [testing-nixos-vm-tests](../11-development/testing-nixos-vm-tests.md), [debugging-evaluation](../11-development/debugging-evaluation.md)

## Week 9 — `12-deployment-and-infra` + `14-security-and-trust`

- [x] Deploy: [colmena](../12-deployment-and-infra/colmena.md), [deploy-rs](../12-deployment-and-infra/deploy-rs.md), [morph-nixinate](../12-deployment-and-infra/morph-nixinate.md), [disko](../12-deployment-and-infra/disko.md), [agenix-sops-nix](../12-deployment-and-infra/agenix-sops-nix.md), [terraform-nixos](../12-deployment-and-infra/terraform-nixos.md), [hydra](../12-deployment-and-infra/hydra.md), [binary-cache-hosting](../12-deployment-and-infra/binary-cache-hosting.md)
- [x] Security: [trusted-users](../14-security-and-trust/trusted-users.md), [signing-and-caches](../14-security-and-trust/signing-and-caches.md), [secrets-management](../14-security-and-trust/secrets-management.md), [supply-chain](../14-security-and-trust/supply-chain.md), [sandbox-escape-surface](../14-security-and-trust/sandbox-escape-surface.md)

## Week 10 — `13-implementations` + `15-history-and-governance`

- [x] Evaluators: [cpp-nix](../13-implementations/nix-evaluator/cpp-nix.md), [lix](../13-implementations/nix-evaluator/lix.md), [tvix](../13-implementations/nix-evaluator/tvix.md), [snix](../13-implementations/nix-evaluator/snix.md)
- [x] Module ecosystems / UX / cloud / frameworks under [13-implementations/](../13-implementations/README.md)
- [x] History: [timeline](../15-history-and-governance/timeline.md), [nixos-foundation](../15-history-and-governance/nixos-foundation.md), [rfc-process](../15-history-and-governance/rfc-process.md), [release-cadence](../15-history-and-governance/release-cadence.md), [forks-and-governance-splits](../15-history-and-governance/forks-and-governance-splits.md), [getting-help-and-community](../15-history-and-governance/getting-help-and-community.md)

## Week 11 — cross-cutting + polish

- [x] [glossary.md](../glossary.md)
- [x] Comparisons: [nix-vs-docker](../comparisons/nix-vs-docker.md), [nix-vs-apt-pacman](../comparisons/nix-vs-apt-pacman.md), [flakes-vs-channels](../comparisons/flakes-vs-channels.md), [nixos-vs-guix](../comparisons/nixos-vs-guix.md)
- [x] Cheatsheets: [cli](../cheatsheets/cli.md), [language](../cheatsheets/language.md), [nixos-options-patterns](../cheatsheets/nixos-options-patterns.md), [packaging-builders](../cheatsheets/packaging-builders.md)
- [x] Roadmap link audit ([00-roadmap/](../00-roadmap/README.md)) — tree-wide relative `.md` links: 0 broken (2026-07-29)
- [x] Complete-pass on high-traffic pages (beginner path + core concepts) — 2026-07-29: why-nix, core concepts (derivation/store-path/closure/generation/profile/flake), glossary, configuration-nix, module-system, rebuild/rollbacks, graphical-installer, flake-nix-schema, cli/language cheatsheets → `complete`

## Complete pass (EXPAND-PLAN Phase 1) — status checkoff

Rubric: [quality-checklist.md](quality-checklist.md). Checked = leaf has frontmatter `status: complete` (2026-07-30 tree scan). A later Phase 1 **quality** pass (examples, version stamps, See also mesh) is separate — see [Remaining work](#remaining-work).

### Tier A — Beginner path

- [x] Core entry: why-nix; derivation/store-path/closure/generation/profile/flake; glossary; configuration-nix; module-system; rebuild/rollbacks; graphical-installer; flake-nix-schema; cli/language cheatsheets
- [x] Philosophy leftovers: [purity-and-reproducibility](../01-philosophy/purity-and-reproducibility.md), [declarative-vs-imperative](../01-philosophy/declarative-vs-imperative.md), [immutability-and-rollback](../01-philosophy/immutability-and-rollback.md), [hermetic-builds](../01-philosophy/hermetic-builds.md), [tradeoffs-and-critiques](../01-philosophy/tradeoffs-and-critiques.md)
- [x] Concepts leftovers: [channel](../02-concepts/channel.md), [overlay](../02-concepts/overlay.md), [overlay-vs-override](../02-concepts/overlay-vs-override.md), [fixed-output-derivation](../02-concepts/fixed-output-derivation.md), [content-addressed-store](../02-concepts/content-addressed-store.md)
- [x] Language syntax: literals through comments-and-formatting under [03-language/syntax/](../03-language/syntax/README.md)
- [x] Store intro: [nix-store-layout](../04-store-and-build/nix-store-layout.md), [hashing-and-inputs](../04-store-and-build/hashing-and-inputs.md), [build-phases](../04-store-and-build/build-phases.md), [builders-and-sandboxes](../04-store-and-build/builders-and-sandboxes.md), [binary-caches](../04-store-and-build/binary-caches.md), [garbage-collection](../04-store-and-build/garbage-collection.md)
- [x] NixOS / flakes entry: [manual-install](../09-nixos/installation/manual-install.md), [hardware-configuration](../09-nixos/configuration/hardware-configuration.md), [generations-and-boot](../09-nixos/architecture/generations-and-boot.md), [inputs-and-outputs](../07-flakes/anatomy/inputs-and-outputs.md), [lockfile](../07-flakes/anatomy/lockfile.md), [nixos-configurations](../07-flakes/workflows/nixos-configurations.md)
- [x] [nixos-options-patterns](../cheatsheets/nixos-options-patterns.md)
- [x] Roadmaps: [beginner](../00-roadmap/beginner.md), [operator](../00-roadmap/operator.md), [contributor](../00-roadmap/contributor.md)

### Tier B — Operator path

- [x] CLI + config: modern/classic CLI leaves, [nix-conf](../05-cli-and-tooling/config/nix-conf.md), [trusted-users-and-substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md), [access-tokens](../05-cli-and-tooling/config/access-tokens.md), [nixos-rebuild](../13-implementations/frontends-and-ux/nixos-rebuild.md), [nh](../13-implementations/frontends-and-ux/nh.md)
- [x] Home/user: all leaves under [10-home-and-user/](../10-home-and-user/README.md)
- [x] Deploy: [colmena](../12-deployment-and-infra/colmena.md), [deploy-rs](../12-deployment-and-infra/deploy-rs.md), [morph-nixinate](../12-deployment-and-infra/morph-nixinate.md), [disko](../12-deployment-and-infra/disko.md), [agenix-sops-nix](../12-deployment-and-infra/agenix-sops-nix.md), [hydra](../12-deployment-and-infra/hydra.md), [terraform-nixos](../12-deployment-and-infra/terraform-nixos.md), [binary-cache-hosting](../12-deployment-and-infra/binary-cache-hosting.md)
- [x] Store ops: [remote-builders](../04-store-and-build/remote-builders.md), [substitutes-and-narinfo](../04-store-and-build/substitutes-and-narinfo.md), [store-protocols](../04-store-and-build/store-protocols.md)
- [x] Ops: [upgrades](../09-nixos/operations/upgrades.md), [remote-deploy](../09-nixos/operations/remote-deploy.md), [troubleshooting](../09-nixos/operations/troubleshooting.md)
- [x] NixOS architecture leftovers: [activation-script](../09-nixos/architecture/activation-script.md), [systemd-integration](../09-nixos/architecture/systemd-integration.md), [options-and-types](../09-nixos/architecture/options-and-types.md), [config-vs-options](../09-nixos/architecture/config-vs-options.md)
- [x] Config leftovers: [imports-and-profiles](../09-nixos/configuration/imports-and-profiles.md), [users-and-groups](../09-nixos/configuration/users-and-groups.md), [networking](../09-nixos/configuration/networking.md), [partitioning-and-bootloaders](../09-nixos/configuration/partitioning-and-bootloaders.md), [secrets-strategies](../09-nixos/configuration/secrets-strategies.md)

### Tier C — Contributor path

- [x] nixpkgs architecture / packaging / overlays / contribution under [06-nixpkgs/](../06-nixpkgs/README.md)
- [x] Language idioms: [callPackage](../03-language/idioms/callPackage.md), [overlays-pattern](../03-language/idioms/overlays-pattern.md), [anti-patterns](../03-language/idioms/anti-patterns.md), [lib-helpers](../03-language/idioms/lib-helpers.md), [rec-and-fixed-points](../03-language/idioms/rec-and-fixed-points.md)
- [x] Flakes: [follow-and-overrides](../07-flakes/anatomy/follow-and-overrides.md), [packages-apps-devShells](../07-flakes/workflows/packages-apps-devShells.md), [checks-and-hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) (+ other flake leaves already complete)
- [x] Adjacent CLI / DX under [05-cli-and-tooling/adjacent-tools/](../05-cli-and-tooling/adjacent-tools/README.md)
- [x] Dev: [shells-and-direnv](../11-development/shells-and-direnv.md), [ci-with-nix](../11-development/ci-with-nix.md), [testing-nixos-vm-tests](../11-development/testing-nixos-vm-tests.md), [debugging-evaluation](../11-development/debugging-evaluation.md) (+ other `11-development` leaves)
- [x] NixOS modules / services / install leftovers under [09-nixos/](../09-nixos/README.md)

### Tier D — Periphery

- [x] Language semantics + builtins under [03-language/](../03-language/README.md)
- [x] Implementations / frameworks / cloud / UX under [13-implementations/](../13-implementations/README.md)
- [x] Experimental features under [08-experimental-features/](../08-experimental-features/README.md) (re-stamp on releases — cadence, not status)
- [x] Security leaves under [14-security-and-trust/](../14-security-and-trust/README.md)
- [x] History under [15-history-and-governance/](../15-history-and-governance/README.md)
- [x] Comparisons: [nix-vs-docker](../comparisons/nix-vs-docker.md), [nix-vs-apt-pacman](../comparisons/nix-vs-apt-pacman.md), [flakes-vs-channels](../comparisons/flakes-vs-channels.md), [nixos-vs-guix](../comparisons/nixos-vs-guix.md)

## Phase M — Mesh / interconnect / inter-trust

### M.0 Existing (cross-link pass — done 2026-07-30)

Leaves below are `complete` and now carry cousin links to [machine-mesh](../02-concepts/machine-mesh.md), [inter-machine-trust](../14-security-and-trust/inter-machine-trust.md), and (where relevant) [clan-and-mesh](../12-deployment-and-infra/clan-and-mesh.md) / [overlay-networks](../09-nixos/configuration/overlay-networks.md).

- [x] Fleet: [colmena](../12-deployment-and-infra/colmena.md), [deploy-rs](../12-deployment-and-infra/deploy-rs.md), [morph-nixinate](../12-deployment-and-infra/morph-nixinate.md), [remote-deploy](../09-nixos/operations/remote-deploy.md)
- [x] Build/store: [remote-builders](../04-store-and-build/remote-builders.md), [binary-caches](../04-store-and-build/binary-caches.md), [binary-cache-hosting](../12-deployment-and-infra/binary-cache-hosting.md), [substitutes-and-narinfo](../04-store-and-build/substitutes-and-narinfo.md), [store-protocols](../04-store-and-build/store-protocols.md)
- [x] Trust: [trusted-users](../14-security-and-trust/trusted-users.md), [trusted-users-and-substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md), [signing-and-caches](../14-security-and-trust/signing-and-caches.md), [supply-chain](../14-security-and-trust/supply-chain.md), [sandbox-escape-surface](../14-security-and-trust/sandbox-escape-surface.md)
- [x] Secrets: [secrets-management](../14-security-and-trust/secrets-management.md), [agenix-sops-nix](../12-deployment-and-infra/agenix-sops-nix.md), [secrets-strategies](../09-nixos/configuration/secrets-strategies.md)
- [x] Networking host-level: [networking.md](../09-nixos/configuration/networking.md)
- [x] Disambiguate Digga/Hive vs mesh — [digga-hive](../13-implementations/community-frameworks/digga-hive.md) + Colmena name-clash + [glossary](../glossary.md) Clan / machine-mesh / inter-trust hooks (2026-07-30)

### M.1 New leaves

- [x] [02-concepts/machine-mesh.md](../02-concepts/machine-mesh.md) (complete)
- [x] [14-security-and-trust/inter-machine-trust.md](../14-security-and-trust/inter-machine-trust.md) (complete)
- [x] [12-deployment-and-infra/clan-and-mesh.md](../12-deployment-and-infra/clan-and-mesh.md) (complete)
- [x] [09-nixos/configuration/overlay-networks.md](../09-nixos/configuration/overlay-networks.md) (complete)
- [ ] Optional private-cache-mesh if needed — deferred (binary-cache-hosting sufficient)

### M.3 Exit

- [x] Concept + inter-trust + Clan + overlay leaves exist; glossary/READMEs/sources updated for mesh vocabulary
- [x] M.0 cousin cross-link pass finished (see M.0 above) — 2026-07-30
- [x] Promote Phase M leaves draft → complete on verify pass

## Remaining work

Prefer [EXPAND-PLAN.md](../EXPAND-PLAN.md) Phase 7 for scope.

### Still open

1. **Cadence (ongoing)** — use [release-checklist.md](release-checklist.md) each Nix/NixOS release and on quarterly triggers.
2. **Intentional drafts** — [self-healing-config-mesh](../12-deployment-and-infra/self-healing-config-mesh.md); living [sources.md](sources.md).
3. **Site** — live at [zemdregon.github.io/nix-docs](https://zemdregon.github.io/nix-docs/); ops in [site.md](site.md).
4. **Optional** — gold thicken thin audiences scored by [EXPAND-PLAN.md](../EXPAND-PLAN.md) priority rubric (not a numbered Phase 7 batch).

## Phase 7 — Toward definitive (**closed 2026-08-01**)

Plan: [EXPAND-PLAN.md](../EXPAND-PLAN.md) Phase 7. Batches A–L complete; closeout verify + audits 2026-08-01.

### Batch A — Cadence + first audience gaps (2026-08-01)

- [x] [release-checklist](release-checklist.md) — Phase 5.1 operational checklist
- [x] [reading-manuals-and-search](../00-roadmap/reading-manuals-and-search.md) — manuals + search.nixos.org
- [x] [installers-and-nix-variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md) — official / Lix / Determinate
- [x] Deepen [nix-darwin](../10-home-and-user/nix-darwin.md)
- [x] Deepen [amazon-gce-azure](../13-implementations/cloud-and-images/amazon-gce-azure.md)

### Batch B — Language ecosystems + org flakes (2026-08-01)

- [x] [haskell-packaging](../06-nixpkgs/packaging/haskell-packaging.md)
- [x] [jvm-php-and-others](../06-nixpkgs/packaging/jvm-php-and-others.md)
- [x] Deepen [config-repo-layout](../07-flakes/workflows/config-repo-layout.md)
- [x] [private-flakes-and-ci](../11-development/private-flakes-and-ci.md)

### Batch C — Gold thicken + getting help (2026-08-01)

- [x] [getting-help-and-community](../15-history-and-governance/getting-help-and-community.md)
- [x] Deepen [module-system-internals](../09-nixos/architecture/module-system-internals.md)
- [x] Deepen [store-protocols](../04-store-and-build/store-protocols.md)
- [x] Deepen [faq-common-errors](../cheatsheets/faq-common-errors.md)
- [x] Roadmaps → getting-help + FAQ (beginner / operator / contributor)

### Batch D — Site / GitHub Pages (2026-08-01)

- [x] MkDocs Material + [pages.yml](../.github/workflows/pages.yml) → [zemdregon.github.io/nix-docs](https://zemdregon.github.io/nix-docs/)
- [x] [meta/site.md](site.md) ops notes

### Batch E — Post-publish polish (2026-08-01)

- [x] Glossary Phase 7 terms
- [x] Deepen [language-toolchains](../11-development/language-toolchains.md)
- [x] Deepen [package-sets](../06-nixpkgs/architecture/package-sets.md)
- [x] Homepage / roadmap polish for web readers

### Batch F — Configuration examples domain (2026-08-01)

New top-level domain [16-configuration-examples](../16-configuration-examples/README.md) — multi-file walkthroughs that compose `00`–`15` (distinct from [meta/examples](examples/README.md) fixtures).

- [x] Domain index + nav (`README.md`, root map, `mkdocs.yml`, `prepare-docs-dir.sh`, conventions)
- [x] [minimal-flake-nixos-host](../16-configuration-examples/minimal-flake-nixos-host.md)
- [x] [nixos-with-home-manager](../16-configuration-examples/nixos-with-home-manager.md)
- [x] [project-devshell-and-direnv](../16-configuration-examples/project-devshell-and-direnv.md)
- [x] [custom-package-overlay-flake](../16-configuration-examples/custom-package-overlay-flake.md)
- [x] [homelab-proxy-secrets-services](../16-configuration-examples/homelab-proxy-secrets-services.md)
- [x] [multi-host-config-repo](../16-configuration-examples/multi-host-config-repo.md)
- [x] [nix-darwin-with-home-manager](../16-configuration-examples/nix-darwin-with-home-manager.md)
- [x] Roadmaps + cousin See also inbound links

### Batch L — Configuration examples expand (2026-08-01)

Second wave under [16-configuration-examples](../16-configuration-examples/README.md) — compose Batches G–J deepenings into worked configs.

- [x] [disko-impermanence-host](../16-configuration-examples/disko-impermanence-host.md)
- [x] [nixos-anywhere-bootstrap](../16-configuration-examples/nixos-anywhere-bootstrap.md)
- [x] [deploy-rs-fleet](../16-configuration-examples/deploy-rs-fleet.md)
- [x] [flake-ci-github-actions](../16-configuration-examples/flake-ci-github-actions.md)
- [x] Domain README + operator/contributor roadmaps + chooser See also inbound links

### Batch G — CI / Hydra / cross / builders cheatsheet (2026-08-01)

- [x] Deepen [hydra](../12-deployment-and-infra/hydra.md)
- [x] Deepen [ci-with-nix](../11-development/ci-with-nix.md)
- [x] Deepen [cross-compilation](../06-nixpkgs/packaging/cross-compilation.md)
- [x] [packaging-builders](../cheatsheets/packaging-builders.md) cheatsheet

### Batch H — Install bootstrap + secrets tools + VM tests (2026-08-01)

- [x] [install-and-bootstrap](../cheatsheets/install-and-bootstrap.md) chooser
- [x] Deepen [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md)
- [x] Deepen [agenix-sops-nix](../12-deployment-and-infra/agenix-sops-nix.md)
- [x] Deepen [testing-nixos-vm-tests](../11-development/testing-nixos-vm-tests.md)

### Batch I — Fleet deploy navigation (2026-08-01)

- [x] [fleet-deploy](../cheatsheets/fleet-deploy.md) chooser
- [x] Deepen [deploy-rs](../12-deployment-and-infra/deploy-rs.md)
- [x] Deepen [morph-nixinate](../12-deployment-and-infra/morph-nixinate.md)
- [x] Deepen [remote-deploy](../09-nixos/operations/remote-deploy.md)

### Batch J — Disk layout + impermanence (2026-08-01)

- [x] [disk-and-persistence](../cheatsheets/disk-and-persistence.md) chooser
- [x] Deepen [disko](../12-deployment-and-infra/disko.md)
- [x] Deepen [impermanence](../09-nixos/configuration/impermanence.md)
- [x] Deepen [disko-recipes](../09-nixos/configuration/disko-recipes.md)

### Batch K — Binary cache navigation (2026-08-01)

- [x] [binary-caches](../cheatsheets/binary-caches.md) chooser
- [x] Deepen [binary-cache-hosting](../12-deployment-and-infra/binary-cache-hosting.md)
- [x] Deepen [binary-caches](../04-store-and-build/binary-caches.md) (client)
- [x] Deepen [signing-and-caches](../14-security-and-trust/signing-and-caches.md)

### Closeout (2026-08-01)

- [x] Subagent quality verify on new G–L leaves (5 cheatsheets + 4 worked configs)
- [x] Parent review: sources rows, EXPAND-PLAN Batch L + Phase 7 exit, coverage sync
- [x] Audits: `broken-links.mjs` → `broken=0`; `quality-audit.mjs` green

### Batch D (historical note)

- [x] Batch D — site generator (live) — see Batch D section above / [site.md](site.md)

## Phase 6 — Homelab and config-repo gaps (2026-08-01)

New leaves from gap analysis (homelab / daily-driver config patterns):

- [x] [config-repo-layout](../07-flakes/workflows/config-repo-layout.md) — flake mono-repo `hosts/` / `modules/` / `users/` conventions (`complete`)
- [x] [homelab-patterns](../09-nixos/services/homelab-patterns.md) — reverse proxy, ACME, secrets, firewall composition (`complete`)
- [x] [backups-and-restore](../09-nixos/operations/backups-and-restore.md) — restic/borg vs generation rollback (`complete`)
- [x] [docker-and-podman](../09-nixos/services/docker-and-podman.md) — host container runtimes (`complete`)
- [x] [unfree-and-licenses](../06-nixpkgs/architecture/unfree-and-licenses.md) — `allowUnfree` policy hub (`complete`)
- [x] [nix-ld-and-foreign-binaries](../09-nixos/desktop/nix-ld-and-foreign-binaries.md) — prebuilt vendor binaries (`complete`)

Cross-links: operator + beginner roadmaps; `common-service-examples`, `nixos-configurations`, `imports-and-profiles`, `flatpak-and-fhs` See also updated.

### Landed (2026-07-31 installer/store/frontend gold)

3i. **Installer / store / frontend gold (done 2026-07-31)** — graphical-installer, firmware-and-microcode, content-addressed-store, nixos-rebuild frontend; evaluator README maturity table (Snix ≠ Tvix).

### Landed (2026-07-31 experimental/contributor gold)

3h. **Experimental/contributor gold (done 2026-07-31)** — cgroups, auto-allocate-uids, maintainers-and-teams, flake-parts, custom-options; named-args pitfall + Digga/Hive vs mesh disambiguation on flake-parts.

### Landed (2026-07-31 operator/module gold)

3g. **Operator/module/HM gold (done 2026-07-31)** — declarative-containers, assertions-and-warnings, writing-hm-modules, manual-install, nixpkgs `lib.md`; overlay-vs-override See also mesh.

### Landed (2026-07-31 further gold + corpus)

3e. **Beginner-concept gold (done 2026-07-31)** — profile, generation, channel, overlay, configuration-nix deepened toward derivation density; cousin links + CLI stamps.
3f. **Example corpus expand (done 2026-07-31)** — [minimal-configuration.nix](examples/minimal-configuration.nix), [simple-package.nix](examples/simple-package.nix), [fod-fetchurl.nix](examples/fod-fetchurl.nix); linked from configuration-nix, callPackage, simple-package, fixed-output-derivation, overlay.

### Landed (2026-07-31 post-v1 cadence / gold / corpus)

3a. **Phase 5.1 cadence pass (done 2026-07-31)** — experimental hub re-stamped Nix 2.34.x; release-cadence + evaluator maturity stamps; Clan/mesh + nh/lsp freshness (Clan cite stay on 26.05).
3b. **Lix glossary parity (done 2026-07-31)** — glossary Lix/Tvix/Snix + Flake CppNix/Lix wording.
3c. **Broader gold calibration (done 2026-07-31)** — derivation/store-path/closure/flake concepts; rebuild/hermetic/functional-PM/hashing; evaluator leaves (Snix ≠ Tvix rename).
3d. **Example corpus (done 2026-07-31; expanded 2026-07-31)** — [meta/examples/](examples/README.md) hello-flake, overlay-snippet, shell.nix, flake-with-checks, minimal-module.nix; linked from packages-apps-devShells, shells-and-direnv, checks-and-hydraJobs, writing-a-module, overlay-vs-override.
3e. **Tier A concept deepen (done 2026-07-31)** — [profile](../02-concepts/profile.md), [generation](../02-concepts/generation.md), [overlay](../02-concepts/overlay.md), [channel](../02-concepts/channel.md) thickened toward gold density; cross-links between profile/generation/channel.

### Landed this batch (2026-07-31 v1 polish)

4. **Phase 1 quality deepen (done 2026-07-31)** — high-traffic / high-churn walk: roadmaps + glossary; cheatsheets; nix-conf / trust; store protocols / builders / narinfo; upgrades / troubleshooting; experimental hub; colmena / deploy-rs / signing / supply-chain; CI / VM tests / shells / simple-package. Phase M.0 was already done 2026-07-30.
5. **Phase 2 deepen + consistency (done 2026-07-31)** — gold deepen: callPackage, overlays-pattern, anti-patterns, pure-eval-and-impure, checks-and-hydraJobs, packages-apps-devShells; tree consistency sweep (CLI preference, hive/mesh wording, `26.05` illustrative pins, CppNix glossary hook).

### Landed (Phases 2–4 — keep for history; do not reopen)

6. **Phase 3 slice A (done 2026-07-30)** — Under [09-nixos/configuration/](../09-nixos/configuration/README.md), all complete: [impermanence](../09-nixos/configuration/impermanence.md), [secure-boot-and-lanzaboote](../09-nixos/configuration/secure-boot-and-lanzaboote.md), [tpm-and-measured-boot](../09-nixos/configuration/tpm-and-measured-boot.md), [nixos-hardware](../09-nixos/configuration/nixos-hardware.md), [firmware-and-microcode](../09-nixos/configuration/firmware-and-microcode.md), [zfs-and-btrfs](../09-nixos/configuration/zfs-and-btrfs.md), [disko-recipes](../09-nixos/configuration/disko-recipes.md).
7. **Phase 3 slice B (done 2026-07-30)** — all `complete`: [faq-common-errors](../cheatsheets/faq-common-errors.md), [import-from-derivation](../02-concepts/import-from-derivation.md), [lazy-trees-and-eval-perf](../11-development/lazy-trees-and-eval-perf.md).
8. **Phase 3 slice C (done 2026-07-30)** — all `complete`: [nix-copy-and-bundles](../12-deployment-and-infra/nix-copy-and-bundles.md), [airgap-and-offline](../12-deployment-and-infra/airgap-and-offline.md), [specialisations](../09-nixos/configuration/specialisations.md). Skipped hosted-Garnix leaf: hosted Garnix shut down 2026-07-15 (see Discourse); FlakeHub remains vendor CI/cache.
9. **Phase 3 desktop (§3.2, done 2026-07-30)** — under [09-nixos/desktop/](../09-nixos/desktop/README.md), all `complete`: [wayland-and-compositors](../09-nixos/desktop/wayland-and-compositors.md), [audio-pipewire](../09-nixos/desktop/audio-pipewire.md), [fonts-and-locales](../09-nixos/desktop/fonts-and-locales.md), [flatpak-and-fhs](../09-nixos/desktop/flatpak-and-fhs.md), [gaming-steam-proton](../09-nixos/desktop/gaming-steam-proton.md), [printing-and-scanning](../09-nixos/desktop/printing-and-scanning.md).
10. **Phase 3 §3.3 workloads (done 2026-07-30)** — under [11-development/](../11-development/README.md), all `complete`: [cuda-rocm-ml](../11-development/cuda-rocm-ml.md), [scientific-and-hpc](../11-development/scientific-and-hpc.md), [android-and-mobile](../11-development/android-and-mobile.md), [emacs-neovim-tooling](../11-development/emacs-neovim-tooling.md).
11. **Phase 3 §3.4 virt/edge (done 2026-07-31)** — all `complete`: [libvirt-and-vms](../09-nixos/services/libvirt-and-vms.md), [microvms](../09-nixos/services/microvms.md), [netboot-and-pxe](../09-nixos/installation/netboot-and-pxe.md), [wsl-and-foreign-os](../10-home-and-user/wsl-and-foreign-os.md). ([specialisations](../09-nixos/configuration/specialisations.md) already complete in slice C.)
12. **Phase 3 §3.5 / §3.6 (done 2026-07-31)** — all `complete`: [enterprise-identity](../09-nixos/configuration/enterprise-identity.md), [fetchers-and-pinning](../06-nixpkgs/packaging/fetchers-and-pinning.md), [lsp-and-ide](../05-cli-and-tooling/adjacent-tools/lsp-and-ide.md), [module-system-internals](../09-nixos/architecture/module-system-internals.md), [experimental-backlog](../08-experimental-features/experimental-backlog.md). Skipped: hosted Garnix leaf (shut down 2026-07-15); Attic/Harmonia/Cachix stay on [binary-cache-hosting](../12-deployment-and-infra/binary-cache-hosting.md).
13. **Phase 3 §3.7 comparisons (done 2026-07-31)** — all `complete`: [nix-vs-bazel-buck](../comparisons/nix-vs-bazel-buck.md), [nix-vs-ansible-terraform](../comparisons/nix-vs-ansible-terraform.md), [nix-vs-containers-orchestrators](../comparisons/nix-vs-containers-orchestrators.md), [ubuntu-arch-to-nixos](../comparisons/ubuntu-arch-to-nixos.md). ([faq-common-errors](../cheatsheets/faq-common-errors.md) already complete in slice B.)
14. **Phase 3 §3.8 security (done 2026-07-31)** — all `complete`: [apparmor-selinux](../14-security-and-trust/apparmor-selinux.md), [ssh-and-age-plugins](../14-security-and-trust/ssh-and-age-plugins.md), [reproducible-builds-audit](../14-security-and-trust/reproducible-builds-audit.md).
15. **Phase 4 products (done 2026-07-31)** — [nix-conf-knobs](../cheatsheets/nix-conf-knobs.md); glossary enrichment (mesh/IFD/specialisation/AppArmor/freeform/age); beginner/operator/contributor roadmap refresh.

Cadence / churn detail (same as item 2 above):

- Refresh [tracking-stabilization.md](../08-experimental-features/tracking-stabilization.md) and [experimental-backlog.md](../08-experimental-features/experimental-backlog.md) each Nix/NixOS release
- Implementation landscape renames (CppNix / Lix / Tvix / Snix; Clan APIs)
- Adjacent tools under `05-cli-and-tooling/adjacent-tools/`

## Audit hook

From repo root (needs Node; no Python required):

```bash
node meta/audit/broken-links.mjs
node meta/audit/quality-audit.mjs
node meta/examples/validate.mjs   # requires Nix; skips if absent
```

CI runs the same checks on push/PR via [.github/workflows/docs-audit.yml](../.github/workflows/docs-audit.yml).

Legacy inline snippets (equivalent to `broken-links.mjs`):

```bash
# Status histogram from YAML frontmatter (leaves + indexes + meta)
node -e '
const fs=require("fs"),path=require("path");
function walk(d,a=[]){for(const e of fs.readdirSync(d,{withFileTypes:true})){
  if(e.name.startsWith("."))continue;const p=path.join(d,e.name);
  if(e.isDirectory())walk(p,a);else if(e.name.endsWith(".md"))a.push(p);}return a;}
const counts={}; let missing=0;
for(const file of walk(".")){const t=fs.readFileSync(file,"utf8");
  const fm=t.match(/^---\n([\s\S]*?)\n---\n/);
  if(!fm){missing++;continue;}
  const m=fm[1].match(/^status:\s*(\S+)/m);
  if(!m){missing++;continue;}
  counts[m[1]]=(counts[m[1]]||0)+1;}
console.log(Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`${String(v).padStart(4)} ${k}`).join("\n"));
console.log(`missing_frontmatter_status=${missing}`);
'

# Broken relative .md links (should print broken=0) — prefer: node meta/audit/broken-links.mjs
node -e '
const fs=require("fs"),path=require("path");
const re=/\[([^\]]*)\]\(([^)]+\.md)(#[^)]*)?\)/g;
function walk(d,a=[]){for(const e of fs.readdirSync(d,{withFileTypes:true})){
  if(e.name.startsWith("."))continue;const p=path.join(d,e.name);
  if(e.isDirectory())walk(p,a);else if(e.name.endsWith(".md"))a.push(p);}return a;}
const root=process.cwd();let checked=0,broken=[];
for(const file of walk(".")){const t=fs.readFileSync(file,"utf8");let m;
  while((m=re.exec(t))){const target=m[2];if(/^(https?:|mailto:)/.test(target))continue;checked++;
    const dest=path.resolve(path.dirname(file),target);
    if(!dest.startsWith(root+path.sep)&&dest!==root){broken.push([file,target,"outside"]);continue;}
    if(!fs.existsSync(dest)||!fs.statSync(dest).isFile())broken.push([file,target,"missing"]);}}
console.log(`checked=${checked} broken=${broken.length}`);
broken.forEach(b=>console.log(" ",b.join(" -> ")));
'
```

Last run (2026-07-31, post installer/store/frontend gold): frontmatter `status` histogram — 247 `complete`, 2 `draft` (self-healing-config-mesh + `sources.md`), 48 `index`, meta `active`/`superseded`; relative `.md` links `broken=0`.

**Quality audit (Phase 6+):** `node meta/audit/broken-links.mjs` · `node meta/audit/quality-audit.mjs` · `node meta/examples/validate.mjs` (Nix). CI: [.github/workflows/docs-audit.yml](../.github/workflows/docs-audit.yml). See [quality-checklist.md](quality-checklist.md) Complete+ bar.

## Definition of done (per article)

See [research-method.md](research-method.md), [quality-checklist.md](quality-checklist.md), and [AGENTS.md](../AGENTS.md).

- **Draft:** not `stub`; accurate Overview + Details; ≥1 relative wiki link; ≥1 upstream Reference; frontmatter `status: draft`
- **Complete:** verified minimal example (or version-noted); no uncited absolute claims; this checklist updated; frontmatter `status: complete`
