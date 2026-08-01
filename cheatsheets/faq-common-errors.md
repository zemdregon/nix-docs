---
status: complete
---

# FAQ: Common Errors

## Overview

Symptom → likely cause → wiki leaf. Classify the failure first: **eval** (before “building …”), **build** (builder exit / FOD hash mismatch), **activation** (`switch`/`test` after the closure exists), or **boot** (new generation will not reach multi-user). Full checklists and recovery: [Troubleshooting](../09-nixos/operations/troubleshooting.md).

## Details

### Evaluation

| Symptom (approx) | Likely cause | Read |
|------------------|--------------|------|
| `experimental Nix feature '…' is disabled` | Need `nix-command` and/or `flakes` in `experimental-features` | [CLI cheatsheet](cli.md), [nix.conf knobs](nix-conf-knobs.md), [Feature flags overview](../08-experimental-features/feature-flags-overview.md) |
| `infinite recursion encountered` | Plain `if config.…` around `config` that also sets that option; value cycle; bad `rec` / self-shadowing | [mkIf / mkMerge / mkOrder](../09-nixos/modules/mkIf-mkMerge-mkOrder.md), [Debugging evaluation](../11-development/debugging-evaluation.md), [Anti-patterns](../03-language/idioms/anti-patterns.md) |
| “The option … does not exist”, “is not a …”, conflicting / multiple definitions | Typo’d option path, wrong type, incompatible merge | [Troubleshooting](../09-nixos/operations/troubleshooting.md), [Options and types](../09-nixos/architecture/options-and-types.md), [NixOS options patterns](nixos-options-patterns.md) |
| Option missing in docs / wrong defaults vs your pin; hunting services in Nixpkgs manual | Wrong manual or channel; search not matched to pin | [Reading manuals and search](../00-roadmap/reading-manuals-and-search.md), [Options and types](../09-nixos/architecture/options-and-types.md) |
| `attribute '…' missing` | Typo’d attr path; flake pure eval (`currentSystem`, `<nixpkgs>`); lazy set not populated yet | [Pure eval and impure](../07-flakes/pure-eval-and-impure.md), [Debugging evaluation](../11-development/debugging-evaluation.md) |
| `impure evaluation is not allowed` / forbidden builtins under flakes | Undeclared inputs, `getEnv`, mutable paths, unpinned fetches | [Pure eval and impure](../07-flakes/pure-eval-and-impure.md) |
| Long “eval” with no `.drv` yet; CI eval suddenly needs builds | [Import-from-derivation](../02-concepts/import-from-derivation.md) (eval reads a store path from another derivation) | [Import-from-derivation](../02-concepts/import-from-derivation.md), [Lazy trees and eval perf](../11-development/lazy-trees-and-eval-perf.md), [Debugging evaluation](../11-development/debugging-evaluation.md) |
| New file on disk but flake build ignores it | Git flake copies only **indexed** files (`git add` / commit); untracked or `.gitignore`d paths invisible | [Pure eval and impure](../07-flakes/pure-eval-and-impure.md) (Git flakes and the source tree) |

### Install / auth

| Symptom (approx) | Likely cause | Read |
|------------------|--------------|------|
| Wrong `nix --version` / odd defaults; two `nix` on `PATH`; mixed upgrade/uninstall breakage | Multiple installers (CppNix / Lix / Determinate) or foreign curl install on NixOS | [Installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md) |
| 401 / 404 on private `github:` / `gitlab:` flake input (esp. CI); works locally, fails on runner | Missing/wrong `access-tokens` / `netrc-file`; token not injected in CI | [Private flakes and CI](../11-development/private-flakes-and-ci.md), [Access tokens](../05-cli-and-tooling/config/access-tokens.md) |

### Build

| Symptom (approx) | Likely cause | Read |
|------------------|--------------|------|
| `hash mismatch in fixed-output derivation` | Upstream tarball/git content changed; wrong declared `outputHash` | [Fixed-output derivation](../02-concepts/fixed-output-derivation.md), [Debugging builds](../04-store-and-build/debugging-builds.md) |
| Haskell Cabal version-bound / dependency check fails | Set pins one version per name; need `jailbreak` / `doJailbreak` (still no Cabal solver) | [Haskell packaging](../06-nixpkgs/packaging/haskell-packaging.md) |
| Gradle deps / `mitmCache` fail; PHP `vendorHash` mismatch | Stale `deps.json` / Composer lock hash; refresh FOD pins | [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md), [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) |
| `builder for … failed with exit code N` / `builder failed` | Compile/test/sandbox failure in a phase | [Debugging builds](../04-store-and-build/debugging-builds.md), [Troubleshooting](../09-nixos/operations/troubleshooting.md) |
| `No space left on device` (often `/tmp` or build dir) | Disk full on `/`, `/nix`, or `TMPDIR` | [Troubleshooting](../09-nixos/operations/troubleshooting.md), [Garbage collection](../04-store-and-build/garbage-collection.md) |
| `ignoring untrusted substituter` / cannot add substituter | Unprivileged user; URL not in daemon `trusted-substituters` (do not widen `trusted-users` casually) | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md), [nix.conf knobs](nix-conf-knobs.md) |

### Store / disk (eval or build)

| Symptom (approx) | Likely cause | Read |
|------------------|--------------|------|
| Missing store paths, hash mismatch on realized paths, corrupt closure (often after crash) | Store corruption; partial download | [Troubleshooting](../09-nixos/operations/troubleshooting.md) (`--repair`, `nix-store --verify`) |
| Paths vanish after GC; “path is no longer valid” | Unrooted paths collected; missing profile/GC root | [Garbage collection](../04-store-and-build/garbage-collection.md), [Troubleshooting](../09-nixos/operations/troubleshooting.md) |

### Activation

| Symptom (approx) | Likely cause | Read |
|------------------|--------------|------|
| Rebuild exits during `switch`/`test`; “Failed to start …” while `nixos-rebuild` still running | Activation script or unit restart during `switch-to-configuration` | [Troubleshooting](../09-nixos/operations/troubleshooting.md), [Activation script](../09-nixos/architecture/activation-script.md) |
| Rebuild succeeds but unit is `failed` or in a restart loop | Systemd unit failure after activation (config/runtime, not the activate script itself) | [Troubleshooting](../09-nixos/operations/troubleshooting.md), [Systemd integration](../09-nixos/architecture/systemd-integration.md) |
| System units updated but `systemd --user` units unchanged after `switch` | Documented limitation — rebuild does not start/stop user services | [Troubleshooting](../09-nixos/operations/troubleshooting.md) |
| `darwin-rebuild` / flake: `attribute '…' missing` for host name | `--flake .#name` ≠ `darwinConfigurations` key; ComputerName vs `LocalHostName` (`scutil`) | [nix-darwin](../10-home-and-user/nix-darwin.md) |

### Boot / images (after successful build/activation)

| Symptom (approx) | Likely cause | Read |
|------------------|--------------|------|
| Unbootable after `switch` — hang, emergency shell, reboot loop | Bad bootloader/kernel/initrd/generation default | [Rollbacks](../09-nixos/operations/rollbacks.md), [Troubleshooting](../09-nixos/operations/troubleshooting.md) |
| Need previous generation from bootloader / `nixos-rebuild --rollback` | Bad generation still selected as default | [Rollbacks](../09-nixos/operations/rollbacks.md) |
| AMI / GCE / Azure image confusion; `nixos-generators` vs `build-image` | Prefer `nixos-rebuild build-image --image-variant …` (25.05+); query AMIs, don’t hardcode IDs | [Amazon / GCE / Azure](../13-implementations/cloud-and-images/amazon-gce-azure.md) |

## Examples

Re-run eval with a full stack when the error site is unclear:

```bash
nixos-rebuild switch --show-trace
# or
nix build .#pkg --show-trace
```

Build side: stream logs with `-L` / `--print-build-logs`, then `nix log /nix/store/….drv` — see [Debugging builds](../04-store-and-build/debugging-builds.md).

Auth side (private flake inputs): confirm effective tokens with config inspection, not by echoing secrets — see [Access tokens](../05-cli-and-tooling/config/access-tokens.md) and [Private flakes and CI](../11-development/private-flakes-and-ci.md).

## See also

- [Troubleshooting](../09-nixos/operations/troubleshooting.md) — full NixOS recovery checklists
- [Debugging evaluation](../11-development/debugging-evaluation.md) — eval toolkit (`trace`, `nix repl`, module merges)
- [Debugging builds](../04-store-and-build/debugging-builds.md) — logs, keep-failed, FOD vs sandbox
- [NixOS options patterns](nixos-options-patterns.md) — `mkIf` / merge helpers that prevent recursion
- [Reading manuals and search](../00-roadmap/reading-manuals-and-search.md) — which manual / channel for option lookup
- [Getting help and community](../15-history-and-governance/getting-help-and-community.md) — Discourse / Matrix / GitHub norms
- [CLI cheatsheet](cli.md) · [nix.conf knobs](nix-conf-knobs.md)

## References

- [Nix stable manual](https://nix.dev/manual/nix/stable/)
- [NixOS manual — Delaying Conditionals](https://nixos.org/manual/nixos/stable/index.html#sec-option-definitions-delaying-conditionals) — plain `if config.…` and infinite recursion
- [NixOS manual — Nix Store Corruption](https://nixos.org/manual/nixos/stable/index.html#sec-nix-store-corruption) — `nixos-rebuild switch --repair`, `nix-store --verify`
- [Nix manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `show-trace`, trust/substituter settings, `access-tokens`
- [Nix manual — `show-trace`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-show-trace) — full evaluation stack traces
