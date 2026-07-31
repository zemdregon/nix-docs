---
status: complete
---

# OfBorg and CI

## Overview

[OfBorg](https://github.com/NixOS/ofborg) is the Nixpkgs pull-request CI bot. It evaluates changed Nix expressions and selectively builds affected packages on shared builders, reporting status on GitHub. OfBorg runs **before merge** on PRs; [Hydra](https://hydra.nixos.org) evaluates and builds **after merge** on trunk branches and drives [official channels](https://channels.nixos.org). The two systems overlap in purpose (catching breakage) but operate at different stages of the contribution flow.

## Details

### What OfBorg does on PRs

Per [CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md), OfBorg performs checks to ensure code quality; results appear at the bottom of the PR.

Typical OfBorg work on a pull request:

- **Evaluation** — instantiates Nixpkgs and NixOS release expressions (`nix-instantiate` on `./pkgs/top-level/release.nix` and `./nixos/release.nix`, `-A manual`). Every PR is evaluated automatically when opened and when commits change; re-running `@ofborg eval` is rarely needed unless eval failed oddly or `master` was previously broken.
- **Selective builds** — when commit titles follow Nixpkgs conventions (package attribute as prefix, e.g. `vim: 1.0.0 -> 2.0.0`), OfBorg schedules builds for the detected attributes. Multiple commits pushed one-by-one each get a separate build job; a multi-commit PR opened at once gets one job for all detected packages. WIP-titled PRs (`WIP:` prefix or `[WIP]` anywhere) skip automatic builds; draft status alone does not.
- **NixOS tests** — `@ofborg test …` runs selected `nixosTests.*` attributes when requested.

Builders use sandboxed `nix-build` / `nix-instantiate` with `restrict-eval`, a 1800s build timeout, and per-system `--argstr system` (see the [OfBorg README](https://github.com/NixOS/ofborg#readme) for the exact command shapes).

### PR comments and commands

Reviewers and contributors can trigger extra work by commenting on the PR. Lines must start with `@ofborg` (case insensitive). Supported subcommands from the [OfBorg README — Commands](https://github.com/NixOS/ofborg#commands):

| Command | Effect |
| --- | --- |
| `@ofborg build attr1 attr2 …` | `nix-build ./default.nix -A …` for each attr |
| `@ofborg test name1 name2 …` | builds `nixosTests.name1`, … |
| `@ofborg eval` | re-runs release-expression instantiation |

Multiple `@ofborg` lines (or several commands on one line) are allowed; commentary may be interwoven as long as bot lines start with `@ofborg`. Do not append free text on the same line after `build`/`test` attrs—those words become attribute names.

Guidelines from upstream: review code before triggering the bot; avoid mass rebuilds or very large builds (e.g. Chromium) on shared infrastructure.

**Trusted users (operational note):** the README’s trusted-user gate (extra platforms for a short allowlist) is **currently disabled**; all users’ builds/tests may run on available platforms including Darwin. Confirm current state in the [OfBorg README](https://github.com/NixOS/ofborg#trusted-users-currently-disabled) / [`config.public.json`](https://github.com/NixOS/ofborg/blob/released/config.public.json) before relying on platform differences.

### Required checks vs OfBorg status

GitHub **required status checks** (jobs named like `PR / …`) can block merge when they fail. As stated in [CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md), **OfBorg is not required** by those checks—merge gating and OfBorg reports are separate concerns. A PR may still need human review and green required checks even when OfBorg is pending or ignored.

OfBorg builds can stall (notably on PRs targeting `staging` or on Darwin builders). Reviewers often know when to wait or disregard stuck jobs; contributors should still fix failures caused by their change. Platform gaps surfaced by OfBorg may warrant `meta.broken`, `meta.badPlatforms`, or `meta.platforms` adjustments—see [package sets](../architecture/package-sets.md) for how platform support tiers steer CI coverage.

### Local review alongside OfBorg

OfBorg covers a subset of platforms and attributes per PR. Contributors often run [`nixpkgs-review`](https://github.com/Mic92/nixpkgs-review) locally to rebuild dependents of a change (`nixpkgs-review pr <number>` or `wip` on uncommitted work)—see CONTRIBUTING’s PR template section. Local sandboxed builds mirror Hydra’s environment; see [builders and sandboxes](../../04-store-and-build/builders-and-sandboxes.md) and [binary caches](../../04-store-and-build/binary-caches.md) when reproducing CI locally.

### Maintainers, merge-bot, and notifications

Listed `meta.maintainers` receive notifications on relevant PRs. That is distinct from OfBorg itself. The [nixpkgs-merge-bot](https://github.com/NixOS/nixpkgs/blob/master/maintainers/README.md) is a separate automation for eligible `pkgs/by-name` merges by maintainers—see [Maintainers and teams](../architecture/maintainers-and-teams.md).

### After merge: Hydra and channels

Once a PR lands on `master`, `nixos-unstable`, or release branches, [Hydra jobsets](https://hydra.nixos.org) take over: regular evaluation and builds, then channel updates when jobsets succeed. That pipeline must not be treated as a substitute for pre-merge testing—CONTRIBUTING warns against using Hydra as a testing platform.

| Stage | System | Scope |
| --- | --- | --- |
| Pull request | OfBorg | Changed attrs, eval, optional tests; comment-triggered builds |
| Trunk / release branches | Hydra | Full jobsets, channel promotion |
| Local | `nixpkgs-review`, `nix-build` | Contributor-chosen depth |

Branch-specific Hydra usage (e.g. `staging` vs `staging-next`) is covered in [Staging and branches](staging-and-branches.md). Channel lag and promotion are summarized in [Channel](../../02-concepts/channel.md).

## Examples

Request OfBorg builds for specific attributes (PR comment; syntax from the OfBorg README):

```text
@ofborg build hello vim
```

Run selected NixOS tests:

```text
@ofborg test nginx
```

Minimal local check of a PR’s rebuild closure (after installing `nixpkgs-review`):

```shell
nix run nixpkgs#nixpkgs-review -- pr 12345
```

## See also

- [Review process](review-process.md) — human review alongside CI
- [Staging and branches](staging-and-branches.md) — where Hydra builds land before `master`
- [Maintainers and teams](../architecture/maintainers-and-teams.md) — notifications and merge-bot
- [Package sets](../architecture/package-sets.md) — platforms, tiers, and CI coverage
- [Channel](../../02-concepts/channel.md) — how Hydra updates what users install
- [Binary caches](../../04-store-and-build/binary-caches.md) — substituters for CI-built artifacts

## References

- [OfBorg repository](https://github.com/NixOS/ofborg)
- [OfBorg README (commands and automatic builds)](https://github.com/NixOS/ofborg#readme)
- [Nixpkgs CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)
- [Hydra](https://hydra.nixos.org)
- [Official Nix channels](https://channels.nixos.org)
- [Nixpkgs manual — platform support](https://nixos.org/manual/nixpkgs/stable/#sec-package-platform-support)
