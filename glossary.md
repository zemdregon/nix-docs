---
status: complete
---

# Glossary

Dense term index for the Nix stack. Each entry is a short definition; follow the relative link for the deep dive when one exists.

## A–D

**Activation (NixOS).** Applying a built system configuration to the running machine: switching services, users, files under `/etc`, and bootloader entries. Driven by the activation script produced with the system closure. See [activation script](09-nixos/architecture/activation-script.md) and [rebuild operations](09-nixos/operations/rebuild-switch-boot-test.md).

**`access-tokens` (`nix.conf`).** Host→credential map so Nix can fetch private GitHub/GitLab (and similar) HTTPS sources—flake inputs, `fetchGit`, and related downloads. Keep tokens out of flakes and lockfiles; inject them via local `nix.conf` or CI secrets. See [access tokens](05-cli-and-tooling/config/access-tokens.md) and [private flakes and CI](11-development/private-flakes-and-ci.md).

**Age plugin / sops-nix host keys.** [age](https://github.com/FiloSottile/age) can use SSH keys as identities; [agenix](https://github.com/ryantm/agenix) and [sops-nix](https://github.com/Mic92/sops-nix) typically encrypt secrets to each host’s SSH public key and decrypt with host private keys during activation—keep those keys on durable storage on impermanent hosts. See [SSH and age plugins](14-security-and-trust/ssh-and-age-plugins.md), [agenix / sops-nix](12-deployment-and-infra/agenix-sops-nix.md), and [secrets strategies](09-nixos/configuration/secrets-strategies.md).

**AppArmor.** Linux mandatory access control (LSM). NixOS exposes profiles and loading via `security.apparmor.*`; maturity is partial—usable options, incomplete end-to-end coverage. SELinux has no proper stock NixOS integration. Distinct from the Nix [build sandbox](#sandbox). See [AppArmor and SELinux](14-security-and-trust/apparmor-selinux.md).

**Attribute set (attrset).** The Nix language’s primary structured value: a map from names to values, written `{ key = value; ... }`. Packages, modules, and flake outputs are almost always attrsets. See [lists and attrsets](03-language/syntax/lists-and-attrsets.md).

**Binary cache.** A remote store of pre-built NAR archives (plus `.narinfo` metadata) that a [substituter](#substituter) can fetch instead of building locally. Public caches (e.g. `cache.nixos.org`) and private ones share the same protocol. See [binary caches](04-store-and-build/binary-caches.md) and [hosting](12-deployment-and-infra/binary-cache-hosting.md).

**Build phase.** A named step in the stdenv build (unpack, patch, configure, build, check, install, fixup, …). Packages override or hook into phases rather than reimplementing the whole builder. See [build phases](04-store-and-build/build-phases.md) and [stdenv](06-nixpkgs/architecture/stdenv.md).

**`build-image` (`nixos-rebuild`).** Upstream command (NixOS ≥ 25.05) that builds a configured system into a named image variant (`--image-variant amazon`, `google-compute`, `azure`, …). Preferred over deprecated [nixos-generators](13-implementations/cloud-and-images/nixos-generators.md) for new cloud/image work. See [Amazon / GCE / Azure](13-implementations/cloud-and-images/amazon-gce-azure.md).

**CA store / content-addressed store.** Store model where an output’s path is derived from the hash of its contents (or a declared content hash), not solely from the derivation’s input hash. Enables better sharing when identical bytes are produced by different recipes. See [content-addressed store](02-concepts/content-addressed-store.md) and [CA derivations](08-experimental-features/ca-derivations.md).

**Channel.** A named, periodically updated snapshot of nixpkgs (or another tree) that classic tooling pins via `nix-channel`. Still common on NixOS; flakes largely replace channels for reproducible pins. See [channel](02-concepts/channel.md), [nix-channel](05-cli-and-tooling/classic-cli/nix-channel.md), and [flakes vs channels](comparisons/flakes-vs-channels.md).

**Clan.** Multi-machine NixOS management (clan-core) with inventory and optional mesh VPN (e.g. ZeroTier)—peer-oriented fleet tooling, not hub→host deploy ([Colmena](12-deployment-and-infra/colmena.md), [deploy-rs](12-deployment-and-infra/deploy-rs.md)) and not [Digga / Hive](13-implementations/community-frameworks/digga-hive.md) flake layout. See [Clan and mesh](12-deployment-and-infra/clan-and-mesh.md) and [machine mesh](02-concepts/machine-mesh.md).

**Closure.** The transitive set of store paths needed to use a given path at runtime (or to realize a derivation’s runtime graph). What you copy to another machine or what GC must keep if the root is live. See [closure](02-concepts/closure.md).

**Community (getting help).** Where to ask Nix/NixOS questions (Discourse, Matrix, GitHub issues) and how to report bugs without dumping secrets. See [getting help and community](15-history-and-governance/getting-help-and-community.md).

**Cross-compilation.** Building for a different system than the build host (e.g. `aarch64-linux` on `x86_64-linux`) via nixpkgs package sets and stdenv cross stubs. See [cross-compilation](06-nixpkgs/packaging/cross-compilation.md).

**CppNix.** Community name for the reference C++ implementation ([NixOS/nix](https://github.com/NixOS/nix))—what most docs mean by “Nix,” and the default on NixOS. Distinct from [Lix](#lix), [Tvix](#tvix), and [Snix](#snix). See [CppNix](13-implementations/nix-evaluator/cpp-nix.md).

**Derivation.** A build recipe: inputs (sources, dependencies, builder, env) map to one or more output [store paths](#store-path). Evaluation yields a derivation value and usually a `.drv` in the store; **realization** runs the builder. Default model is input-addressed. See [derivation](02-concepts/derivation.md) and [derivation builtins](03-language/builtins/derivation-builtins.md).

**Determinate Nix.** Vendor distribution of [CppNix](#cppnix) from Determinate Systems (installer, defaults, and optional extras such as Determinate Nixd). Compare install paths and effective `nix.conf` with official CppNix and [Lix](#lix); do not assume identical experimental-feature defaults. See [installers and Nix variants](13-implementations/frontends-and-ux/installers-and-nix-variants.md).

**devShell.** A flake (or `nix develop` / `nix-shell`) environment that puts compilers and tools on `PATH` without installing them into a user profile. See [packages, apps, and devShells](07-flakes/workflows/packages-apps-devShells.md) and [shells and direnv](11-development/shells-and-direnv.md).

**Digga / Hive (divnix).** Flake layout / collector tools for hosts and modules—**not** a network mesh, not Clan’s mesh VPN, and not Colmena’s deploy “hive.” Digga is deprecated; Hive sits on std/Paisano. See [Digga / Hive](13-implementations/community-frameworks/digga-hive.md); contrast [machine mesh](#machine-mesh) and [Clan](#clan).

**disko.** Declarative disk partitioning for NixOS (`disko.devices`); templates and layout patterns live under [Disko recipes](09-nixos/configuration/disko-recipes.md). Tool overview: [disko](12-deployment-and-infra/disko.md).

**`.drv`.** The store object that serializes a derivation. Output paths point back to their deriver `.drv`; inspecting it shows inputs and planned outputs. See [derivation](02-concepts/derivation.md).

## E–H

**Experimental feature.** A Nix daemon/evaluator capability gated by `experimental-features` in `nix.conf` (or `--extra-experimental-features`). Examples: `flakes`, `nix-command`, `ca-derivations`. Behavior and stability vary by Nix release—check the tracking page. See [experimental features](08-experimental-features/README.md) and [feature flags overview](08-experimental-features/feature-flags-overview.md).

**Fixed-output derivation (FOD).** A derivation whose outputs are content-addressed by a hash you declare (`outputHash` / `outputHashAlgo`). Used for fetches and other cases where the result must match known bytes; the sandbox may allow limited network for FODs. See [fixed-output derivation](02-concepts/fixed-output-derivation.md).

**Flake.** A directory (or other flake reference) with a `flake.nix` that declares locked inputs and typed outputs (`packages`, `nixosConfigurations`, …), plus a [lockfile](#lockfile). Requires the `flakes` experimental feature on [CppNix](#cppnix); [Lix](#lix) also supports flakes (CLI/flag details can differ by implementation—check your version). See [flake (concept)](02-concepts/flake.md), [flake anatomy](07-flakes/README.md), and [experimental flakes](08-experimental-features/flakes.md).

**Flake registry.** A map from short names (e.g. `nixpkgs`) to flake URLs, used when resolving bare flake refs. Global, user, and flake-local registries can override each other. See [registries and refs](07-flakes/registries-and-refs.md).

**Freeform module (`freeformType`).** Inside a submodule, set `freeformType = someType;` so undeclared attribute names merge through that type instead of failing `_module.check` (surfaces as `_module.freeformType`). Common for open `settings = { … }` maps in service modules; prefer freeform only in submodules, not at the root. See [module system internals](09-nixos/architecture/module-system-internals.md) and [options and types](09-nixos/architecture/options-and-types.md).

**FHS environment (`buildFHSEnv` / steam-run).** nixpkgs helper that wraps a command in an FHS-like `/usr`/`/lib` view (bubblewrap) so unpatched Linux binaries can run on NixOS; Steam’s `steam-run` reuses that pattern. Not a security sandbox like Flatpak. See [Flatpak and FHS](09-nixos/desktop/flatpak-and-fhs.md) and [Gaming: Steam and Proton](09-nixos/desktop/gaming-steam-proton.md).

**Garbage collection (GC).** Deleting store paths that are not reachable from any GC root. Profiles, generations, result symlinks, and explicit roots keep closures alive. See [garbage collection](04-store-and-build/garbage-collection.md) and [nix-collect-garbage](05-cli-and-tooling/classic-cli/nix-collect-garbage.md).

**GC root.** A registered reference that prevents GC from deleting a store path and its closure—user profiles, NixOS system generations, `result` links, and paths under `/nix/var/nix/gcroots`. See [garbage collection](04-store-and-build/garbage-collection.md).

**Generation.** A numbered snapshot of a [profile](#profile) (user env or NixOS system) that you can roll back to. Each successful profile update or `nixos-rebuild` creates a new generation. See [generation](02-concepts/generation.md), [NixOS generations and boot](09-nixos/architecture/generations-and-boot.md), and [rollbacks](09-nixos/operations/rollbacks.md).

**`haskellPackages`.** Default GHC-backed Haskell package set in nixpkgs (Hackage-facing attributes; alias of a `haskell.packages.*` set for the current compiler). One pinned version per name—not a Cabal solver. See [Haskell packaging](06-nixpkgs/packaging/haskell-packaging.md).

**Hermetic build.** A build that sees only declared inputs: no ambient host packages, no undeclared network, sandbox-isolated filesystem and env. Closely related to [purity](#purity); hermeticity is the build-time isolation story. See [hermetic builds](01-philosophy/hermetic-builds.md) and [builders and sandboxes](04-store-and-build/builders-and-sandboxes.md).

**Home Manager.** A module system for declarative user environments (dotfiles, packages, services) that can run standalone or as a NixOS/nix-darwin module. See [home-manager](10-home-and-user/home-manager/README.md), [standalone vs NixOS module](10-home-and-user/home-manager/standalone-vs-nixos-module.md), and [module ecosystem note](13-implementations/module-ecosystems/home-manager.md).

## I–L

**Impure / impure eval.** Evaluation or builds that depend on ambient state (current time, impure env, unrestricted filesystem). Flake pure eval forbids many of these; `--impure` and impure-derivation features re-open controlled exceptions. See [pure eval and impure](07-flakes/pure-eval-and-impure.md), [purity boundaries](03-language/semantics/purity-boundaries.md), and [impure derivations](08-experimental-features/impure-derivations.md).

**Impermanence.** Ephemeral root (tmpfs or wipe-on-boot) with declared persistent paths—undeclared state vanishes at reboot. Usually via nix-community/impermanence. See [impermanence](09-nixos/configuration/impermanence.md).

**Import from derivation (IFD).** Evaluation reads a store path produced by another derivation (via `import`, `readFile`, and similar), so Nix realises that path mid-eval. Slow and often banned in CI (`allow-import-from-derivation = false`). Distinct from [FODs](#fixed-output-derivation-fod). See [import from derivation](02-concepts/import-from-derivation.md).

**Input-addressed.** The default store addressing: output path hashes come from the derivation’s inputs (recipe), not from hashing the built files. Contrast [FOD](#fixed-output-derivation-fod) and [CA store](#ca-store--content-addressed-store). See [derivation](02-concepts/derivation.md) and [hashing and inputs](04-store-and-build/hashing-and-inputs.md).

**Inter-machine trust (inter-trust).** How a group of Nix(OS) machines trusts each other across reachability, remote builds, binary caches, deploy authority, secrets, and supply chain—distinct from daemon [`trusted-users`](#trusted-user). See [inter-machine trust](14-security-and-trust/inter-machine-trust.md) and [machine mesh](02-concepts/machine-mesh.md).

**Lanzaboote / Secure Boot (NixOS).** Community UEFI Secure Boot (and measured-boot) stack for NixOS: custom stub, `lzbt`, and a NixOS module that signs boot artifacts and replaces stock systemd-boot install when enabled. Advanced; pin a release. See [Secure Boot and Lanzaboote](09-nixos/configuration/secure-boot-and-lanzaboote.md) and [TPM and measured boot](09-nixos/configuration/tpm-and-measured-boot.md).

**Lix.** Community-maintained fork of [CppNix](#cppnix) ([lix.systems](https://lix.systems/))—compatible for many day-to-day packaging and NixOS/Home Manager/nix-darwin workflows, with separate governance and documented technical differences. Not a claim of identical feature sets. Distinct from [Tvix](#tvix) and [Snix](#snix). See [Lix](13-implementations/nix-evaluator/lix.md).

**Lockfile (`flake.lock`).** JSON pin of every flake input to exact revisions and content hashes so evaluation is reproducible across machines and time. Updated with `nix flake update` / `nix flake lock`. See [lockfile](07-flakes/anatomy/lockfile.md).

**`lib` (nixpkgs).** The shared Nix library of helpers (`lib.mkIf`, `lib.optional`, fetchers wrappers elsewhere, etc.) shipped with nixpkgs and used by packages and modules. See [lib](06-nixpkgs/architecture/lib.md).

## M–P

**Machine mesh.** A group of Nix(OS) devices that share builds, closures, secrets, and/or deploy authority over a shared reachability fabric—not a VPN brand, not [Digga / Hive](13-implementations/community-frameworks/digga-hive.md), and not “the mesh” by itself. Concept page: [machine mesh](02-concepts/machine-mesh.md). Contrast hub→host fleet tools ([Colmena](12-deployment-and-infra/colmena.md), [deploy-rs](12-deployment-and-infra/deploy-rs.md)) and peer inventory tooling ([Clan](#clan)).

**Measured boot.** Binding LUKS (or similar) unlock to TPM PCR measurements of the boot chain—on NixOS usually via Lanzaboote + systemd-pcrlock. Experimental edges; LUKS2-oriented; not ZFS/Btrfs native encryption. See [TPM and measured boot](09-nixos/configuration/tpm-and-measured-boot.md).

**`mitmCache` (Gradle).** nixpkgs Gradle helper (`gradle.fetchDeps`) that pins dependency downloads into a [FOD](#fixed-output-derivation-fod)-backed MITM cache (`deps.json`); refresh via the cache’s `updateScript` when deps change. See [JVM / PHP and others](06-nixpkgs/packaging/jvm-php-and-others.md).

**`mkDerivation`.** The usual nixpkgs entry point for defining a package: `stdenv.mkDerivation { pname; version; src; ... }`. Wraps `builtins.derivation` with stdenv phases, setup hooks, and conventions. See [mkDerivation](06-nixpkgs/architecture/mkDerivation.md) and [stdenv](06-nixpkgs/architecture/stdenv.md).

**Module (NixOS).** A function or attrset that declares [options](#option-nixos) and/or sets `config`, merged by the module system with imports, types, and priority. Home Manager and nix-darwin reuse the same pattern. See [module system](09-nixos/architecture/module-system.md) and [writing a module](09-nixos/modules/writing-a-module.md).

**Multiple outputs.** Splitting one derivation into several store paths (`out`, `dev`, `doc`, …) so dependents can pull only what they need. See [multiple outputs](06-nixpkgs/packaging/multiple-outputs.md).

**NAR / narinfo.** NAR is Nix’s archive format for store objects; `.narinfo` is the binary-cache metadata (hash, size, references, signature) for a path. See [substitutes and narinfo](04-store-and-build/substitutes-and-narinfo.md).

**nix-command.** Experimental feature enabling the unified `nix` CLI (`nix build`, `nix flake`, `nix profile`, …) as opposed to only classic `nix-*` tools. Often enabled together with `flakes`. See [nix-command](08-experimental-features/nix-command.md) and [modern build/develop/run](05-cli-and-tooling/modern-cli/nix-build-develop-run.md).

**nix.conf.** Daemon and client configuration (`/etc/nix/nix.conf`, `~/.config/nix/nix.conf`): substituters, trusted users, experimental features, build sandboxes, and more. See [nix.conf](05-cli-and-tooling/config/nix-conf.md).

**nix-darwin.** Declarative macOS system configuration using a NixOS-like module system. See [nix-darwin](10-home-and-user/nix-darwin.md).

**nixos-hardware.** Optional NixOS modules for machine-specific quirks (laptops, SBCs, common PCs)—complements generated [`hardware-configuration.nix`](09-nixos/configuration/hardware-configuration.md), does not replace it. See [nixos-hardware](09-nixos/configuration/nixos-hardware.md).

**NixOS.** A Linux distribution whose entire system is a Nix derivation: modules evaluate to a system closure, then activation switches the running machine. See [NixOS](09-nixos/README.md).

**nixpkgs.** The package collection and stdenv/lib/module library that most Nix users evaluate—channels and flakes both typically pin a nixpkgs revision. See [nixpkgs](06-nixpkgs/README.md).

**Option (NixOS).** A typed, documented configuration knob declared with `mkOption` (or helpers); modules assign values that merge into `config`. Query with `nixos-option` / docs. See [options and types](09-nixos/architecture/options-and-types.md), [config vs options](09-nixos/architecture/config-vs-options.md), and [options cheatsheet](cheatsheets/nixos-options-patterns.md).

**Overlay.** A function `final: prev: { ... }` that extends or replaces attributes in a nixpkgs package set without forking the whole tree. Distinct from per-package `.override` / `.overrideAttrs`. See [overlay](02-concepts/overlay.md), [overlay vs override](02-concepts/overlay-vs-override.md), and [writing overlays](06-nixpkgs/overlays-and-overrides/writing-overlays.md).

**Overlay network (Nix context).** VPN or mesh fabric (WireGuard, Tailscale/Headscale, ZeroTier, …) used so builders, deploy SSH, and private caches can reach each other—not a general VPN tutorial. See [overlay networks](09-nixos/configuration/overlay-networks.md) and [Clan and mesh](12-deployment-and-infra/clan-and-mesh.md).

**Override.** Changing one package’s arguments (`.override`) or derivation attrs (`.overrideAttrs`) locally, without a full overlay. See [overlay vs override](02-concepts/overlay-vs-override.md) and [patches and overrides](06-nixpkgs/packaging/patches-and-overrides.md).

**Pinning.** Fixing nixpkgs or other inputs to exact revisions (flake lock, `fetchTarball` + hash, Niv/npins, channel generation) so builds do not drift. See [pinning](06-nixpkgs/overlays-and-overrides/pinning.md) and [lockfile](07-flakes/anatomy/lockfile.md).

**PipeWire.** Desktop audio/video server on NixOS (`services.pipewire`), usually with PulseAudio-protocol and ALSA shims; WirePlumber is the common session manager. See [Audio and PipeWire](09-nixos/desktop/audio-pipewire.md).

**Profile.** A user- or system-managed symlink forest of installed packages, versioned as [generations](#generation). Classic `nix-env` and modern `nix profile` both operate on profiles. See [profile](02-concepts/profile.md) and [nix profile](05-cli-and-tooling/modern-cli/nix-profile.md).

**Purity.** Evaluation and builds that depend only on declared inputs—same expression and inputs → same result. Flake pure eval and the build sandbox enforce different layers of this ideal. See [purity and reproducibility](01-philosophy/purity-and-reproducibility.md) and [purity boundaries](03-language/semantics/purity-boundaries.md).

## Q–T

**Realization.** Building or substituting a derivation so its output store paths exist on disk. Evaluation alone does not realize; `nix build`, `nix-build`, and `nix-store --realise` do. See [derivation](02-concepts/derivation.md).

**Remote builder.** Another machine the local Nix daemon can offload builds to over SSH (or similar), still producing paths for the local store. See [remote builders](04-store-and-build/remote-builders.md).

**Sandbox.** The isolated build environment (namespaces, bind mounts, restricted network) that enforces hermetic builds. Configurable in `nix.conf`; FODs may get network exceptions. See [builders and sandboxes](04-store-and-build/builders-and-sandboxes.md) and [sandbox escape surface](14-security-and-trust/sandbox-escape-surface.md).

**Snix.** Modular Rust reimplementation of Nix components (evaluator, store, builders)—continuation of the [Tvix](#tvix) stack under independent hosting; early / research maturity, not a drop-in for [CppNix](#cppnix) or [Lix](#lix). See [Snix](13-implementations/nix-evaluator/snix.md).

**`specialArgs` (module system).** Arguments passed into `lib.evalModules` that are available during **import resolution** and in module bodies—use for flake `inputs`, `modulesPath`, and anything referenced from `imports`. Contrast `_module.args` (module bodies only, after merge). See [module system internals](09-nixos/architecture/module-system-internals.md) and [config repo layout](07-flakes/workflows/config-repo-layout.md).

**Specialisation (NixOS).** Named alternate system closure built alongside the parent configuration (`specialisation.<name>`), linked under `/run/current-system/specialisation/<name>/` and switchable via that child’s activation script. See [specialisations](09-nixos/configuration/specialisations.md).

**stdenv.** The nixpkgs standard environment: compilers, core utilities, and the default builder/`mkDerivation` phase machinery for a platform. Almost every package builds inside some stdenv. See [stdenv](06-nixpkgs/architecture/stdenv.md).

**Store.** The content-addressed (by path hash) filesystem tree, usually `/nix/store`, holding `.drv` files, outputs, and sources registered with Nix. See [store layout](04-store-and-build/nix-store-layout.md).

**Store path.** A concrete path under the store (`/nix/store/<hash>-<name>`) naming a single store object—an output, source, or `.drv`. Hashes encode addressing mode and identity. See [store path](02-concepts/store-path.md).

**Substituter.** A configured store URL Nix queries to download a path instead of building it (`substituters` / `extra-substituters` in `nix.conf`). Usually a [binary cache](#binary-cache); signatures and trusted-user rules matter. See [substitutes and narinfo](04-store-and-build/substitutes-and-narinfo.md), [trusted users and substituters](05-cli-and-tooling/config/trusted-users-and-substituters.md), and [signing](14-security-and-trust/signing-and-caches.md).

**Trusted user.** A `nix.conf` principal allowed to set extra substituters or use restricted store operations that ordinary users cannot. Misconfiguration is a common cache/signing footgun. See [trusted users and substituters](05-cli-and-tooling/config/trusted-users-and-substituters.md) and [trusted users (security)](14-security-and-trust/trusted-users.md).

**Tvix.** Experimental Rust Nix reimplementation by TVL (modular evaluator/store/builder); not a production NixOS drop-in. Active modular continuation often tracked as [Snix](#snix). See [Tvix](13-implementations/nix-evaluator/tvix.md).

## U–Z

**`vendorHash`.** Content hash pinning a language builder’s vendored dependency tree as a [FOD](#fixed-output-derivation-fod) (notably PHP Composer via `php.buildComposerProject2`; same idea as `cargoHash` / `npmDepsHash`). Mismatch means refresh the pin after lock/deps change. See [JVM / PHP and others](06-nixpkgs/packaging/jvm-php-and-others.md) and [fixed-output derivation](02-concepts/fixed-output-derivation.md).

**XDG Desktop Portal.** Desktop integration bus for sandboxed and Wayland apps (file choosers, screenshare, …), configured on NixOS via `xdg.portal.*`. See [Wayland and compositors](09-nixos/desktop/wayland-and-compositors.md) and [Flatpak and FHS](09-nixos/desktop/flatpak-and-fhs.md).

**Aliases:** FOD → [fixed-output derivation](#fixed-output-derivation-fod); IFD → [import from derivation](#import-from-derivation-ifd); CA → [CA store](#ca-store--content-addressed-store); HM → [Home Manager](#home-manager); GC → [garbage collection](#garbage-collection-gc); Secure Boot (NixOS) → [Lanzaboote / Secure Boot](#lanzaboote--secure-boot-nixos); Hive (Digga) → [Digga / Hive](#digga--hive); age secrets → [Age plugin / sops-nix](#age-plugin--sops-nix-host-keys); specialisation → [Specialisation](#specialisation-nixos).

## References

- [Nix manual — glossary-adjacent store & language](https://nix.dev/manual/nix/stable/)
- [Nix manual — experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html)
- [Nixpkgs manual — stdenv / overlays](https://nixos.org/manual/nixpkgs/stable/)
- [NixOS manual — modules and configuration](https://nixos.org/manual/nixos/stable/)
- [nix.dev — flakes concept](https://nix.dev/concepts/flakes)
- [Lix](https://lix.systems/) — community Nix implementation (fork of CppNix)

## See also

- [Learning roadmaps](00-roadmap/README.md) — beginner / operator / contributor paths
- [Comparisons](comparisons/README.md) — [flakes vs channels](comparisons/flakes-vs-channels.md), [Nix vs apt/pacman](comparisons/nix-vs-apt-pacman.md), [NixOS vs Guix](comparisons/nixos-vs-guix.md), [Nix vs Docker](comparisons/nix-vs-docker.md), [Ubuntu / Arch to NixOS](comparisons/ubuntu-arch-to-nixos.md)
- [Cheatsheets](cheatsheets/README.md) — [CLI](cheatsheets/cli.md), [language](cheatsheets/language.md), [NixOS options patterns](cheatsheets/nixos-options-patterns.md), [FAQ common errors](cheatsheets/faq-common-errors.md), [nix.conf knobs](cheatsheets/nix-conf-knobs.md)
- [Concepts](02-concepts/README.md) — core mental-model pages linked throughout
- [Migration from channels](07-flakes/migration-from-channels.md)
