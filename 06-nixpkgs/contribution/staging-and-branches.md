---
status: complete
---

# Staging and Branches

## Overview

Nixpkgs uses several long-lived Git branches so day-to-day development on `master` stays fast while **mass rebuilds** are batched for [Hydra](https://hydra.nixos.org). The **staging workflow** collects large-impact changes on `staging`, periodically merges them to Hydra-built `staging-next` for validation, then lands them on `master` via a manual pull request when builds look good. Branch choice for a pull request depends on rebuild scope, release backports, and special cases such as kernel or NixOS test-driver changes.

## Details

### Why staging exists

Hydra cannot afford to rebuild huge fractions of nixpkgs on every merge to `master`. The staging workflow **batches** mass rebuilds: contributors target `staging`, maintainers merge `staging` → `staging-next` when ready, Hydra builds the [`nixpkgs:staging-next` jobset](https://hydra.nixos.org/jobset/nixpkgs/staging-next), and after fixups and verification, `staging-next` merges to `master`. Coordination happens in the [Staging room on Matrix](https://matrix.to/#/#staging:nixos.org).

`staging-next` should receive only changes that fix Hydra builds; for anything else, ask in the Staging room first. Because `staging-next` is separate from `staging`, mass-rebuild PRs may still merge into `staging` at any time.

Changes must be well tested before landing on any branch—Hydra is not a substitute for local or CI checks ([ofborg-and-ci.md](ofborg-and-ci.md)).

### Branch roles

| Branch | Hydra-built | Accepts mass rebuilds | Typical use |
| --- | --- | --- | --- |
| `master` | Yes | No (ideally) | Default target for most PRs; development |
| `staging` | No | Yes | Batch mass-rebuild work; merge anytime |
| `staging-next` | Yes | Only Hydra fixups | Build and validate batched staging merges |
| `staging-nixos` | No | Limited[^1] | Kernel updates and changes that rebuild all NixOS tests |

[^1]: Except changes that cause no more rebuilds than kernel updates (see upstream CONTRIBUTING).

**Critical security fixes:** non–mass-rebuild fixes go to `master`; mass-rebuild security fixes go to `staging-next` (not `staging`). Critical security work may also land on `staging-nixos`.

**Automated merges** keep branches current: `master` → `staging-next` → `staging`, and `master` → `staging-nixos`, on a schedule ([periodic-merge-6h](https://github.com/NixOS/nixpkgs/blob/master/.github/workflows/periodic-merge-6h.yml) / [periodic-merge-24h](https://github.com/NixOS/nixpkgs/blob/master/.github/workflows/periodic-merge-24h.yml)). **Manual merges** move batched work forward: `staging` → `staging-next`, then `staging-next` → `master` (PR, often labeled [`4.workflow: staging`](https://github.com/NixOS/nixpkgs/issues?q=label%3A%224.workflow%3A+staging%22)). `staging-nixos` merges to `master` manually—typically when mainline kernel updates or critical security fixes land (often about weekly).

### Commit flow (rolling development)

```mermaid
gitGraph
    commit id:" "
    branch staging
    commit id:"  "
    branch staging-next

    merge master id:"auto"
    checkout staging
    merge staging-next id:"auto"

    checkout staging-next
    merge staging type:HIGHLIGHT id:"manual"
    commit id:"fixup"

    checkout master
    merge staging-next type:HIGHLIGHT id:"manual PR"
```

Mass-rebuild PRs land on `staging`. Maintainers manually merge `staging` into `staging-next`; Hydra builds and fixups happen on `staging-next`. When healthy, `staging-next` merges to `master`. Meanwhile, automated merges from `master` keep `staging-next` and `staging` aligned with ongoing development.

### Choosing a target branch

Most changes belong on `master`. Use upstream [branch conventions](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#branch-conventions) when deciding otherwise:

1. **Release backports** — supported fixes may go to `release-YY.MM` (see [release cadence](../../15-history-and-governance/release-cadence.md)); mass-rebuild backports use `staging-YY.MM` instead of the release branch directly.
2. **Mass rebuilds** — target `staging` (or `staging-YY.MM` for a stable line), not `master`. Whether a change qualifies is **not formally defined**; CI assigns [`rebuild` labels](https://github.com/NixOS/nixpkgs/labels?q=rebuild) from estimated rebuild counts. CONTRIBUTING’s rule of thumb: **≥500** rebuilds → consider `staging`; **≥1000** → treat as a mass rebuild and target `staging`. See [Changes causing mass rebuilds](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#changes-causing-mass-rebuilds)—do not treat those numbers as hard laws.
3. **All NixOS tests / kernel** — changes with the [`10.rebuild-nixos-tests`](https://github.com/NixOS/nixpkgs/issues?q=label%3A10.rebuild-nixos-tests) label, or Linux kernel updates, should target a `staging` line or `staging-nixos` (or the matching `*-YY.MM` stable branch). Kernel PRs are an exception to the mass-rebuild→`staging` rule. Backports from `staging-nixos` are **not** automatic; backport relevant commits manually.

### Retargeting a PR to staging

If a PR aimed at `master` causes too many rebuilds, rebase onto the merge base and retarget:

```console
git rebase --onto upstream/staging... upstream/master
git push origin feature --force-with-lease
```

`upstream/staging...` means the merge base of `upstream/staging` and `HEAD`. Use GitHub’s **Edit** to change the base branch to `staging`, then rebase onto `upstream/staging` if merge conflicts remain. Full steps are in [Rebasing between branches](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#rebasing-between-branches-ie-from-master-to-staging) in CONTRIBUTING.

### Stable release counterparts

The same staging pattern applies per release line:

| Rolling | Stable release |
| --- | --- |
| `master` | `release-YY.MM` |
| `staging` | `staging-YY.MM` |
| `staging-next` | `staging-next-YY.MM` |
| `staging-nixos` | `staging-nixos-YY.MM` |

Merged staging work eventually reaches users through [channels](../../02-concepts/channel.md) after it lands on `master` or a release branch and Hydra publishes new channel snapshots ([channels.nixos.org](https://channels.nixos.org)).

## Examples

- **Toolchain bump affecting 2000 packages:** open PR against `staging`; after merge, wait for a staging → staging-next batch and Hydra green builds before the change reaches `master`.
- **Small security patch, few rebuilds:** target `master` directly; backport to `release-YY.MM` if applicable ([review-process.md](review-process.md)).
- **Mass-rebuild security fix:** target `staging-next`, not `staging`, so it rides the next Hydra-validated batch into `master` faster.
- **Kernel update:** target `staging-nixos` per CONTRIBUTING’s test-driver section; expect a manual merge to `master` around weekly kernel/security landings, then backport by hand if needed.

## See also

- [Review process](review-process.md) — reviews, backports, and merge expectations
- [OfBorg and CI](ofborg-and-ci.md) — rebuild labels and builder behavior on staging PRs
- [Channel](../../02-concepts/channel.md) — how built branches become installable snapshots
- [Package sets](../architecture/package-sets.md) — what Hydra rebuilds when the package set changes
- [Release cadence](../../15-history-and-governance/release-cadence.md) — supported release branches and timing

## References

- [CONTRIBUTING.md — Staging](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#staging)
- [CONTRIBUTING.md — Branch conventions](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#branch-conventions)
- [CONTRIBUTING.md — Changes causing mass rebuilds](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#changes-causing-mass-rebuilds)
- [CONTRIBUTING.md — Changes rebuilding all NixOS tests](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#changes-rebuilding-all-nixos-tests)
- [CONTRIBUTING.md — Rebasing between branches](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#rebasing-between-branches-ie-from-master-to-staging)
- [Hydra jobset: nixpkgs:staging-next](https://hydra.nixos.org/jobset/nixpkgs/staging-next)
- [Official NixOS channels](https://channels.nixos.org)
- [Matrix: #staging:nixos.org](https://matrix.to/#/#staging:nixos.org)
