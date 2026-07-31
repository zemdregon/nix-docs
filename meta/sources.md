---
status: draft
---

# Sources

**Living `draft` forever by design — do not mark `complete`.** This is the wiki’s canonical upstream URL table, not a finished article: append/revise rows as content work needs them (see EXPAND-PLAN / coverage). Links only — no mirrored content here.

Prefer the stable/channel manuals unless documenting a version-specific feature; then pin the versioned manual URL and note the Nix / Nixpkgs / NixOS release.

## Official hubs

| Source | URL |
|--------|-----|
| nix.dev (ecosystem docs home) | https://nix.dev/ |
| nixos.org | https://nixos.org/ |
| NixOS Discourse | https://discourse.nixos.org/ |
| NixOS org on GitHub | https://github.com/NixOS |

## Nix (evaluator, language, store, CLI)

| Source | URL |
|--------|-----|
| Nix reference manual (latest) | https://nix.dev/manual/nix/ |
| Nix language | https://nix.dev/manual/nix/stable/language/ |
| Nix language — syntax / constructs | https://nix.dev/manual/nix/stable/language/syntax.html |
| Nix language — types | https://nix.dev/manual/nix/stable/language/types.html |
| Nix language — operators | https://nix.dev/manual/nix/stable/language/operators.html |
| Nix language — string literals | https://nix.dev/manual/nix/stable/language/string-literals.html |
| Nix language — string interpolation | https://nix.dev/manual/nix/stable/language/string-interpolation.html |
| Nix language — evaluation | https://nix.dev/manual/nix/stable/language/evaluation.html |
| Nix language — builtins | https://nix.dev/manual/nix/stable/language/builtins.html |
| Nix language — derivations | https://nix.dev/manual/nix/stable/language/derivations.html |
| Nix language — Import From Derivation (2.34) | https://nix.dev/manual/nix/2.34/language/import-from-derivation.html |
| `allow-import-from-derivation` (2.34) | https://nix.dev/manual/nix/2.34/command-ref/conf-file.html#conf-allow-import-from-derivation |
| `eval-cache` (2.34) | https://nix.dev/manual/nix/2.34/command-ref/conf-file.html#conf-eval-cache |
| Eval profiler (2.34) | https://nix.dev/manual/nix/2.34/advanced-topics/eval-profiler.html |
| `nix copy` (2.34, experimental) | https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-copy.html |
| `nix bundle` (2.34, experimental) | https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-bundle.html |
| Local binary cache store `file://` (2.34) | https://nix.dev/manual/nix/2.34/store/types/local-binary-cache-store.html |
| `nix-store --export` (2.34) | https://nix.dev/manual/nix/2.34/command-ref/nix-store/export.html |
| `nix-store --import` (2.34) | https://nix.dev/manual/nix/2.34/command-ref/nix-store/import.html |
| NixOS/bundlers | https://github.com/NixOS/bundlers |
| NixOS/nix#13225 (lazy trees PR) | https://github.com/NixOS/nix/pull/13225 |
| Determinate Nix — lazy trees (vendor) | https://docs.determinate.systems/determinate-nix/lazy-trees/ |
| Nix store | https://nix.dev/manual/nix/stable/store/ |
| Nix store path | https://nix.dev/manual/nix/stable/store/store-path.html |
| Store types (`nix help-stores`) | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html |
| Store object info / NAR info | https://nix.dev/manual/nix/stable/protocols/json/store-object-info.html |
| Binary cache substituter | https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html |
| Garbage collector roots | https://nix.dev/manual/nix/stable/package-management/garbage-collector-roots.html |
| `nix-store --gc` | https://nix.dev/manual/nix/stable/command-ref/nix-store/gc.html |
| Remote / distributed builds | https://nix.dev/manual/nix/stable/advanced-topics/distributed-builds.html |
| nix.dev — Setting up distributed builds | https://nix.dev/tutorials/nixos/distributed-builds-setup |
| NixOS options — `nix.buildMachines` | https://search.nixos.org/options?query=nix.buildMachines |
| nix.dev — Add a binary cache | https://nix.dev/guides/recipes/add-binary-cache |
| `nix.conf` | https://nix.dev/manual/nix/stable/command-ref/conf-file.html |
| Verifying build reproducibility (`diff-hook` / `--check`) | https://nix.dev/manual/nix/stable/advanced-topics/diff-hook.html |
| NixOS Reproducible Builds | https://reproducible.nixos.org/ |
| Experimental features | https://nix.dev/manual/nix/stable/development/experimental-features.html |
| Flakes concept (nix.dev) | https://nix.dev/concepts/flakes |
| `nix flake` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html |
| `nix flake check` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html |
| `nix flake init` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-init.html |
| `nix flake update` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-update.html |
| `nix flake prefetch-inputs` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-prefetch-inputs.html |
| `nix profile` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile.html |
| `nix store` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-store.html |
| `nix-channel` | https://nix.dev/manual/nix/stable/command-ref/nix-channel.html |
| `nix-env` | https://nix.dev/manual/nix/stable/command-ref/nix-env.html |
| `nix-build` | https://nix.dev/manual/nix/stable/command-ref/nix-build.html |
| `nix develop` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop.html |
| `nix-shell` | https://nix.dev/manual/nix/stable/command-ref/nix-shell.html |
| `nix-store` | https://nix.dev/manual/nix/stable/command-ref/nix-store.html |
| `nix repl` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-repl.html |
| `nix fmt` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-fmt.html |
| `nix edit` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-edit.html |
| `nix-collect-garbage` | https://nix.dev/manual/nix/stable/command-ref/nix-collect-garbage.html |
| nix.dev — Install Nix | https://nix.dev/install-nix |
| `nix registry` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-registry.html |
| `nix` (new CLI) | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html |
| `nix config show` | https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-config-show.html |
| Nix language operators (incl. pipe) | https://nix.dev/manual/nix/stable/language/operators.html |
| Advanced attrs (`__contentAddressed`) | https://nix.dev/manual/nix/stable/language/advanced-attributes.html |
| Content-addressed derivation outputs | https://nix.dev/manual/nix/stable/store/derivation/outputs/content-address.html |
| Command reference | https://nix.dev/manual/nix/stable/command-ref/ |
| Nix release notes | https://nix.dev/manual/nix/stable/release-notes/ |
| CppNix source | https://github.com/NixOS/nix |

Use a versioned path (e.g. `/manual/nix/2.34/`) when the fact depends on a specific Nix release shipped with a NixOS channel.

## Nixpkgs

| Source | URL |
|--------|-----|
| Nixpkgs manual (stable) | https://nixos.org/manual/nixpkgs/stable/ |
| Nixpkgs manual — Fetchers | https://nixos.org/manual/nixpkgs/stable/#chap-pkgs-fetchers |
| Nixpkgs manual — Standard environment | https://nixos.org/manual/nixpkgs/stable/#chap-stdenv |
| Nixpkgs manual — Using stdenv | https://nixos.org/manual/nixpkgs/stable/#sec-using-stdenv |
| Nixpkgs manual — stdenv phases | https://nixos.org/manual/nixpkgs/stable/#sec-stdenv-phases |
| Nixpkgs manual — `breakpointHook` | https://nixos.org/manual/nixpkgs/stable/#sec-breakpointHook |
| Nixpkgs manual — Functions / lib | https://nixos.org/manual/nixpkgs/stable/#chap-functions |
| Nixpkgs manual — Module system | https://nixos.org/manual/nixpkgs/stable/#module-system |
| nix.dev — Module system deep dive | https://nix.dev/tutorials/module-system/deep-dive.html |
| Nixpkgs manual — Overlays | https://nixos.org/manual/nixpkgs/stable/#chap-overlays |
| Nixpkgs manual — Cross-compilation | https://nixos.org/manual/nixpkgs/stable/#chap-cross |
| Nixpkgs manual — Multiple-output packages | https://nixos.org/manual/nixpkgs/stable/#chap-multiple-output |
| Nixpkgs manual — Passthru attributes | https://nixos.org/manual/nixpkgs/stable/#chap-passthru |
| Nixpkgs manual — `.overrideAttrs` | https://nixos.org/manual/nixpkgs/stable/#sec-pkg-overrideAttrs |
| Nixpkgs manual — `packageOverrides` | https://nixos.org/manual/nixpkgs/stable/#sec-modify-via-packageOverrides |
| Nixpkgs manual — Languages and frameworks | https://nixos.org/manual/nixpkgs/stable/#chap-language-support |
| Nixpkgs manual — CUDA (`#cuda`) | https://nixos.org/manual/nixpkgs/unstable/#cuda |
| Nixpkgs manual — Configuring Nixpkgs for CUDA | https://nixos.org/manual/nixpkgs/unstable/#cuda-configuring-nixpkgs-for-cuda |
| Nixpkgs manual — Using `pkgsCuda` | https://nixos.org/manual/nixpkgs/unstable/#cuda-using-pkgscuda |
| Nixpkgs manual — Android (`#android`) | https://nixos.org/manual/nixpkgs/unstable/#android |
| Nixpkgs manual — Switching MPI | https://nixos.org/manual/nixpkgs/unstable/#sec-overlays-alternatives-mpi |
| Nixpkgs manual — BLAS/LAPACK alternatives | https://nixos.org/manual/nixpkgs/unstable/#sec-overlays-alternatives-blas-lapack |
| NixOS-QChem (HPC/chemistry overlay) | https://github.com/Nix-QChem/NixOS-QChem |
| nix-community/robotnix | https://github.com/nix-community/robotnix |
| Robotnix docs | https://docs.robotnix.org |
| Mobile NixOS | https://github.com/mobile-nixos/mobile-nixos |
| Mobile NixOS website | https://mobile-nixos.github.io/ |
| Nixvim | https://nix-community.github.io/nixvim |
| Nixpkgs manual (unstable) | https://nixos.org/manual/nixpkgs/unstable/ |
| nix.dev — Pinning Nixpkgs | https://nix.dev/reference/pinning-nixpkgs |
| Contributing to Nixpkgs | https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md |
| Nixpkgs maintainers README | https://github.com/NixOS/nixpkgs/blob/master/maintainers/README.md |
| OfBorg | https://github.com/NixOS/ofborg |
| Hydra (NixOS) | https://hydra.nixos.org |
| Nixpkgs source | https://github.com/NixOS/nixpkgs |
| `pkgs/by-name/` | https://github.com/NixOS/nixpkgs/tree/master/pkgs/by-name |
| RFC 0035 (pname/version) | https://github.com/NixOS/rfcs/blob/master/rfcs/0035-package-naming.md |

## NixOS

| Source | URL |
|--------|-----|
| NixOS manual (stable) | https://nixos.org/manual/nixos/stable/ |
| NixOS manual (unstable) | https://nixos.org/manual/nixos/unstable/ |
| Graphical interfaces / X chapter (`#sec-x11`) | https://nixos.org/manual/nixos/unstable/#sec-x11 |
| nixpkgs `portal.nix` (`xdg.portal`) | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/config/xdg/portal.nix |
| nixpkgs `plasma6.nix` | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/services/desktop-managers/plasma6.nix |
| nixpkgs `steam.nix` (`programs.steam`) | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/programs/steam.nix |
| nixpkgs `flatpak.nix` | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/services/desktops/flatpak.nix |
| nixpkgs PipeWire module | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/services/desktops/pipewire/pipewire.nix |
| nixpkgs fonts `packages.nix` / `fontconfig.nix` | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/config/fonts/packages.nix |
| nixpkgs `i18n.nix` | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/config/i18n.nix |
| Option search — `services.pipewire` | https://search.nixos.org/options?query=services.pipewire |
| Option search — `services.flatpak` | https://search.nixos.org/options?query=services.flatpak |
| Option search — `programs.steam` | https://search.nixos.org/options?query=programs.steam |
| Option search — `services.printing` / `hardware.sane` | https://search.nixos.org/options?query=services.printing |
| Option search — `fonts.packages` / `fonts.fontconfig` | https://search.nixos.org/options?query=fonts.packages |
| nixpkgs FHS environments (`buildFHSEnv`) | https://nixos.org/manual/nixpkgs/unstable/#sec-fhs-environments |
| Networking | https://nixos.org/manual/nixos/stable/index.html#sec-networking |
| NetworkManager | https://nixos.org/manual/nixos/stable/index.html#sec-networkmanager |
| Firewall | https://nixos.org/manual/nixos/stable/index.html#sec-firewall |
| IPv6 configuration | https://nixos.org/manual/nixos/stable/index.html#sec-ipv6 |
| Wireless | https://nixos.org/manual/nixos/stable/index.html#sec-wireless |
| Option — `networking.nftables.enable` | https://nixos.org/manual/nixos/stable/options#opt-networking.nftables.enable |
| Option — `networking.firewall.extraInputRules` | https://nixos.org/manual/nixos/stable/options#opt-networking.firewall.extraInputRules |
| Option — `networking.networkmanager.ensureProfiles.profiles` | https://nixos.org/manual/nixos/stable/options#opt-networking.networkmanager.ensureProfiles.profiles |
| NixOS wiki — Firewall (secondary) | https://wiki.nixos.org/wiki/Firewall |
| Changing the configuration | https://nixos.org/manual/nixos/stable/index.html#sec-changing-config |
| Modularity | https://nixos.org/manual/nixos/stable/index.html#ch-modularity |
| Writing NixOS Modules | https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules |
| Option definitions (`mkIf` / priorities / `mkMerge`) | https://nixos.org/manual/nixos/stable/index.html#sec-option-definitions |
| Warnings and assertions | https://nixos.org/manual/nixos/stable/index.html#sec-assertions |
| Activation script | https://nixos.org/manual/nixos/stable/index.html#sec-activation-script |
| Option search — `specialisation` | https://search.nixos.org/options?query=specialisation |
| nixpkgs `specialisation.nix` | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/system/activation/specialisation.nix |
| Tweag — Introduction to NixOS specialisations (secondary) | https://www.tweag.io/blog/2022-08-18-nixos-specialisations/ |
| What happens during a system switch | https://nixos.org/manual/nixos/stable/index.html#ch-switching |
| System switch / unit handling | https://nixos.org/manual/nixos/stable/index.html#sec-switching-systems |
| systemd in NixOS | https://nixos.org/manual/nixos/stable/index.html#sect-nixos-systemd-nixos |
| Defining custom services | https://nixos.org/manual/nixos/stable/index.html#sect-nixos-systemd-custom-services |
| Option — `system.userActivationScripts` | https://search.nixos.org/options?show=system.userActivationScripts |
| Installing NixOS | https://nixos.org/manual/nixos/stable/index.html#ch-installation |
| Booting from netboot media (PXE) | https://nixos.org/manual/nixos/stable/#sec-booting-from-pxe |
| Graphical installation | https://nixos.org/manual/nixos/stable/index.html#sec-installation-graphical |
| Manual installation | https://nixos.org/manual/nixos/stable/index.html#sec-installation-manual |
| Option search — `virtualisation.libvirtd` | https://search.nixos.org/options?query=virtualisation.libvirtd |
| Option search — `services.pixiecore` | https://search.nixos.org/options?query=services.pixiecore |
| Option search — `services.sssd` | https://search.nixos.org/options?query=services.sssd |
| Option search — `security.apparmor` | https://search.nixos.org/options?query=security.apparmor |
| NixOS Wiki — Security (MAC notes) | https://wiki.nixos.org/wiki/Security |
| NixOS Wiki — NixOS Hardening | https://wiki.nixos.org/wiki/NixOS_Hardening |
| Option search — `services.realmd` | https://search.nixos.org/options?query=services.realmd |
| NixOS Wiki — Active Directory Client (secondary) | https://wiki.nixos.org/wiki/Active_Directory_Client |
| NixOS Wiki — Netboot (secondary) | https://wiki.nixos.org/wiki/Netboot |
| NixOS Wiki — Libvirt (secondary) | https://wiki.nixos.org/wiki/Libvirt |
| File systems | https://nixos.org/manual/nixos/stable/index.html#ch-file-systems |
| LUKS-encrypted file systems | https://nixos.org/manual/nixos/stable/index.html#sec-luks-file-systems |
| NixOS options — `boot.uki` | https://search.nixos.org/options?query=boot.uki |
| Boot Loader Specification (UAPI) | https://uapi-group.org/specifications/specs/boot_loader_specification/ |
| Lanzaboote (community Secure Boot) | https://github.com/nix-community/lanzaboote |
| Lanzaboote docs | https://nix-community.github.io/lanzaboote/ |
| Lanzaboote — enable measured boot | https://github.com/nix-community/lanzaboote/blob/master/docs/how-to-guides/enable-measured-boot.md |
| Lanzaboote — measured boot explanation | https://github.com/nix-community/lanzaboote/blob/master/docs/explanation/measured-boot.md |
| impermanence (community) | https://github.com/nix-community/impermanence |
| impermanence README | https://github.com/nix-community/impermanence/blob/master/README.org |
| nixpkgs `all-firmware.nix` | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/hardware/all-firmware.nix |
| nixpkgs Intel microcode module | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/hardware/cpu/intel-microcode.nix |
| nixpkgs AMD microcode module | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/hardware/cpu/amd-microcode.nix |
| nixpkgs ZFS filesystems module | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/tasks/filesystems/zfs.nix |
| nixpkgs Btrfs filesystems module | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/tasks/filesystems/btrfs.nix |
| nixpkgs `boot.initrd.clevis` | https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/system/boot/clevis.nix |
| NixOS Wiki — ZFS | https://wiki.nixos.org/wiki/ZFS |
| NixOS Wiki — Btrfs | https://wiki.nixos.org/wiki/Btrfs |
| UAPI Linux TPM PCR registry | https://uapi-group.org/specifications/specs/linux_tpm_pcr_registry/ |
| Upgrading NixOS | https://nixos.org/manual/nixos/stable/index.html#sec-upgrading |
| `system.autoUpgrade.flake` (option search) | https://search.nixos.org/options?show=system.autoUpgrade.flake |
| Rolling back | https://nixos.org/manual/nixos/stable/index.html#sec-rollback |
| Nix store corruption | https://nixos.org/manual/nixos/stable/index.html#sec-nix-store-corruption |
| Container management | https://nixos.org/manual/nixos/stable/index.html#ch-containers |
| NixOS profiles (manual) | https://nixos.org/manual/nixos/stable/index.html#sec-profiles |
| NixOS profiles (nixpkgs tree) | https://github.com/NixOS/nixpkgs/tree/master/nixos/modules/profiles |
| Escaping in Exec directives | https://nixos.org/manual/nixos/stable/index.html#sec-systemd-escaping |
| Configuration options search | https://search.nixos.org/options |
| Package search | https://search.nixos.org/packages |
| Channels | https://channels.nixos.org |
| Download / ISOs | https://nixos.org/download/ |
| NixOS source (modules) | https://github.com/NixOS/nixpkgs/tree/master/nixos |
| `nixos-rebuild(8)` (nixos-rebuild-ng) | https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/ni/nixos-rebuild-ng/nixos-rebuild.8.scd |
| nix.dev — Module system tutorial | https://nix.dev/tutorials/module-system/ |

## Process and design

| Source | URL |
|--------|-----|
| NixRFCs | https://github.com/NixOS/rfcs |
| RFC 0080 (NixOS release schedule) | https://github.com/NixOS/rfcs/blob/master/rfcs/0080-nixos-release-schedule.md |
| NixOS Foundation (community) | https://nixos.org/community/ |
| Governance (board vs SC) | https://nixos.org/governance/ |
| Nix Governance Constitution | https://github.com/NixOS/org/blob/main/doc/constitution.md |
| Foundation impressum | https://github.com/NixOS/foundation/blob/master/impressum.md |
| Official channels | https://channels.nixos.org/ |
| Release calendar / status | https://status.nixos.org/ |

## Language learning (guided, secondary to the reference manual)

| Source | URL |
|--------|-----|
| nix.dev tutorials | https://nix.dev/tutorials/ |
| nix.dev learning journey | https://nix.dev/ |

## Ecosystem manuals and project docs

| Source | URL |
|--------|-----|
| Home Manager manual | https://nix-community.github.io/home-manager/ |
| Home Manager — Writing modules | https://nix-community.github.io/home-manager/index.xhtml#writing-home-manager-modules |
| Home Manager — Dotfiles / collisions | https://nix-community.github.io/home-manager/index.xhtml#sec-usage-dotfiles |
| Home Manager — Nix Flakes | https://nix-community.github.io/home-manager/index.xhtml#ch-nix-flakes |
| Home Manager options | https://nix-community.github.io/home-manager/options.xhtml |
| Home Manager source | https://github.com/nix-community/home-manager |
| nix-darwin | https://github.com/nix-darwin/nix-darwin |
| NixOS-WSL | https://github.com/nix-community/NixOS-WSL |
| NixOS-WSL docs | https://nix-community.github.io/NixOS-WSL/ |
| NixOS-WSL install | https://nix-community.github.io/NixOS-WSL/install.html |
| microvm.nix | https://github.com/microvm-nix/microvm.nix |
| microvm.nix handbook | https://microvm-nix.github.io/microvm.nix/ |
| npins | https://github.com/andir/npins |
| nil (Nix LSP) | https://github.com/oxalica/nil |
| nixd (Nix LSP) | https://github.com/nix-community/nixd |
| nixd configuration | https://github.com/nix-community/nixd/blob/main/nixd/docs/configuration.md |
| vscode-nix-ide | https://github.com/nix-community/vscode-nix-ide |
| flake-parts | https://flake.parts/ |
| Snowfall Lib | https://snowfall.org/guides/lib/quickstart/ |
| snowfallorg/lib | https://github.com/snowfallorg/lib |
| numtide/blueprint | https://github.com/numtide/blueprint |
| divnix/std | https://github.com/divnix/std |
| paisano-nix/core | https://github.com/paisano-nix/core |
| Hydra (CI) | https://hydra.nixos.org/ |
| Hydra source / README | https://github.com/NixOS/hydra |
| NixOS options — `services.hydra` | https://search.nixos.org/options?channel=26.05&query=services.hydra |
| Hydra wiki | https://wiki.nixos.org/wiki/Hydra |
| nixos-hardware | https://github.com/NixOS/nixos-hardware |
| nixos-generators | https://github.com/nix-community/nixos-generators |
| disko | https://github.com/nix-community/disko |
| disko-templates | https://github.com/nix-community/disko-templates |
| nixos-anywhere | https://github.com/nix-community/nixos-anywhere |
| nixos-anywhere docs | https://nix-community.github.io/nixos-anywhere/ |
| nixos-anywhere quickstart | https://nix-community.github.io/nixos-anywhere/quickstart.html |
| sops-nix | https://github.com/Mic92/sops-nix |
| age-plugin-yubikey | https://github.com/str4d/age-plugin-yubikey |
| age plugins (FiloSottile/age) | https://github.com/FiloSottile/age#plugins |
| agenix | https://github.com/ryantm/agenix |
| Colmena | https://github.com/nix-community/colmena |
| deploy-rs | https://github.com/serokell/deploy-rs |
| Morph | https://github.com/DBCDK/morph |
| nixinate | https://github.com/MatthewCroughan/nixinate |
| nix.dev — CI with GitHub Actions | https://nix.dev/guides/recipes/continuous-integration-github-actions |
| cachix/install-nix-action | https://github.com/cachix/install-nix-action |
| Cachix docs | https://docs.cachix.org/ |
| Determinate Nix Action | https://github.com/DeterminateSystems/determinate-nix-action |
| Attic | https://github.com/zhaofengli/attic |
| Harmonia | https://github.com/nix-community/harmonia |
| Colmena docs | https://colmena.cli.rs/ |
| Clan docs (26.05) | https://clan.lol/docs/26.05 |
| Clan mesh VPN guide | https://clan.lol/docs/26.05/guides/networking/mesh-vpn |
| Clan networking | https://clan.lol/docs/26.05/guides/networking/networking |
| Clan zerotier service | https://clan.lol/docs/26.05/services/official/zerotier |
| Attic | https://docs.attic.rs/ |
| Harmonia | https://github.com/nix-community/harmonia |
| Cachix docs | https://docs.cachix.org/ |
| nix-darwin | https://github.com/nix-darwin/nix-darwin |
| nh | https://github.com/nix-community/nh |
| nvd | https://khumba.net/projects/nvd/ |
| nix-index / comma | https://github.com/nix-community/nix-index |
| nix-index-database | https://github.com/nix-community/nix-index-database |
| devenv | https://devenv.sh/ |
| numtide/devshell | https://github.com/numtide/devshell |
| direnv | https://direnv.net/ |
| nix-direnv | https://github.com/nix-community/nix-direnv |
| NixOS/nixfmt | https://github.com/NixOS/nixfmt |
| Alejandra | https://github.com/kamadorueda/alejandra |
| RFC 0166 (Nix formatting) | https://github.com/NixOS/rfcs/blob/master/rfcs/0166-nix-formatting.md |
| terraform-nixos (historical) | https://github.com/nix-community/terraform-nixos |

## Implementations (evaluators)

| Source | URL |
|--------|-----|
| Lix | https://lix.systems/ |
| Lix docs | https://docs.lix.systems/ |
| About Lix | https://lix.systems/about/ |
| Lix governance | https://lix.systems/governance/ |
| Tvix | https://code.tvl.fyi/about/tvix |
| Snix | https://snix.dev/ |

## Guix (comparisons / sibling stack)

| Source | URL |
|--------|-----|
| GNU Guix | https://guix.gnu.org/ |
| Guix manual — Introduction | https://guix.gnu.org/manual/en/html_node/Introduction.html |
| Guix manual — Features | https://guix.gnu.org/manual/en/html_node/Features.html |
| Guix manual — Defining Packages | https://guix.gnu.org/manual/en/html_node/Defining-Packages.html |
| Guix manual — GNU Distribution | https://guix.gnu.org/manual/en/html_node/GNU-Distribution.html |
| Courtès, *Functional Package Management with Guix* | https://inria.hal.science/hal-00824004 |

## Adjacent build / deploy systems (comparisons)

| Source | URL |
|--------|-----|
| Bazel basics | https://bazel.build/basics |
| Kubernetes documentation | https://kubernetes.io/docs/home/ |
| Nomad documentation | https://developer.hashicorp.com/nomad/docs |
| Kubenix | https://github.com/hall/kubenix |
| Terraform introduction | https://developer.hashicorp.com/terraform/intro |

## Philosophy / background (cite carefully)

| Source | URL |
|--------|-----|
| Dolstra PhD thesis (Nix) | https://edolstra.github.io/pubs/phd-thesis.pdf |
| Purely Functional Software Deployment (related papers) | https://edolstra.github.io/ |

## Community signal (gotchas only; confirm in manuals)

| Source | URL |
|--------|-----|
| NixOS Discourse | https://discourse.nixos.org/ |
| nixpkgs issues | https://github.com/NixOS/nixpkgs/issues |
| Nix issues | https://github.com/NixOS/nix/issues |

## Notes

- Prefer primary manuals over blog posts when documenting behavior.
- Record version or release channel when citing unstable features.
- Add a row here when a new first-party doc becomes a recurring citation target.
- Real-world config repos are for **patterns** in articles, not authority over manuals — attribute with a link and strip secrets.
