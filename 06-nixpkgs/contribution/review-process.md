---
status: complete
---

# Review Process

## Overview

Nixpkgs changes land through [GitHub pull requests](https://docs.github.com/en/pull-requests) to [NixOS/nixpkgs](https://github.com/NixOS/nixpkgs). Contributing implies licensing your work under the repository’s [COPYING](https://github.com/NixOS/nixpkgs/blob/master/COPYING) (MIT-like) terms.

The path from idea to channel update is: fork and branch → implement and test → open a PR → automated and human review → merge → [Hydra](https://hydra.nixos.org) builds → [official channels](https://channels.nixos.org). This page summarizes that flow and the norms that keep review cycles short. Deeper branch topology and CI mechanics live in sibling pages.

## Details

### Opening a pull request

The standard workflow (see [CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)):

1. **Fork** Nixpkgs and clone your fork; add `upstream` pointing at `NixOS/nixpkgs`.
2. **Pick a base branch** — usually `master`; release fixes target `release-YY.MM`; mass-rebuild work may target `staging` (see [staging and branches](staging-and-branches.md)).
3. **Create a topic branch** from the current base (e.g. `git switch --create update-hello upstream/master`).
4. **Change, test, and document** — follow general and area-specific conventions; for a first package see [simple package](../packaging/simple-package.md).
5. **Commit** using [commit conventions](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#commit-conventions).
6. **Push** to your fork and **open a PR** against the chosen base branch, filling out the [PR template](https://github.com/NixOS/nixpkgs/blob/master/.github/PULL_REQUEST_TEMPLATE.md).
7. **Keep the PR mergeable** — respond to review comments, fix CI failures, rebase on conflicts, and force-push with `--force-with-lease` when history is rewritten.

### Testing expectations

The PR template asks contributors to record how they tested:

- **Sandboxing** — Nix’s build sandbox (default on Linux) mirrors what [Hydra](https://nixos.org/hydra) uses. Test with sandboxing enabled when you can; on other platforms it may be off by default for performance.
- **Platforms** — note which systems you built on; testing every platform is not required for merge, but maintainers need to know coverage gaps.
- **NixOS tests** — run existing applicable tests under `nixos/tests` when relevant (Linux only).
- **Dependent rebuilds** — when changing a widely used library or tool, run [`nixpkgs-review`](https://github.com/Mic92/nixpkgs-review) to rebuild reverse dependencies (see [Examples](#examples)).

Automated tests in the package or a NixOS test reduce manual review burden and often speed up merge.

### Automated checks (ofborg)

The [ofborg](https://github.com/NixOS/ofborg) CI bot runs on PRs and posts results at the bottom of the thread. It checks code quality and builds affected packages across platforms. Required GitHub status checks (jobs named like `PR / …`) can block merge on failing jobs; **ofborg itself is not a required check**. See [ofborg and CI](ofborg-and-ci.md) and the [ofborg README](https://github.com/NixOS/ofborg#readme) for command details and stuck-build handling.

Do not merge while CI that applies to your change is still failing. Reviewers know when ofborg stalls (common on `staging` or Darwin) and may proceed anyway; contributors should not worry unnecessarily about transient infra issues unrelated to their diff. If ofborg shows a real break on a platform you cannot test, consider adjusting `meta.broken`, `meta.badPlatforms`, or `meta.platforms`.

### Human review and merge

Anyone may review and approve PRs; timely, responsive review matters because long-open PRs accumulate rebase conflicts.

**Review norms** ([Review and Merge conventions](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#review-and-merge-conventions)):

- Comments are **non-blocking by default**. Blocking feedback must use GitHub’s “Request changes” review type; blocking reviewers should stay available for follow-up. An abandoned blocking review may be dismissed after reasonable time at the merger’s discretion.
- All suggestions should be **acknowledged** before merge — by applying them or explaining why not.
- Committers may **push to the contributor’s branch** (checkout via `gh pr checkout`) to fix trivial issues or commit structure, weighing another review cycle against contributor preference. Opt out by unchecking “Allow edits and access to secrets by maintainers.”

**Who merges:** a [committer](https://github.com/NixOS/nixpkgs-committers) must be confident in the change. Package [maintainers](../architecture/maintainers-and-teams.md) are not gatekeepers, but when a committer merges without maintainer endorsement, the maintainers README expects **at least one week** so listed maintainers can respond (critical packages and security fixes have negotiated exceptions). Maintainers of `pkgs/by-name` packages can invoke `@NixOS/nixpkgs-merge-bot merge` when the bot’s preconditions hold: invoker is a listed maintainer on the target branch, the package is under `by-name`, and the PR author is `@r-ryantm` or a Nixpkgs committer.

Reviewers should leave a short comment listing what they checked so other reviewers and mergers know the state of the review.

### After merge: Hydra and channels

Merged commits eventually reach [Hydra](https://hydra.nixos.org), which evaluates Nixpkgs and updates [official channels](https://channels.nixos.org) when jobs succeed. See [status.nixos.org](https://status.nixos.org) for current channel state. `master` feeds unstable channels (`nixpkgs-unstable`, `nixos-unstable`, …); `release-YY.MM` feeds stable channels. Staging batches mass rebuilds before they land on `master` — see [staging and branches](staging-and-branches.md).

Hydra is not a substitute for pre-merge testing; changes should be well tested before merge.

### Backports

After merge to `master`, fixes [acceptable for stable releases](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md#changes-acceptable-for-releases) can reach `release-YY.MM`:

- **Automatic** — add the [`backport release-YY.MM`](https://github.com/NixOS/nixpkgs/labels?q=backport) label (maintainers only); a GitHub Action opens a backport PR. The label works on open or already-merged PRs.
- **Manual** — cherry-pick onto `release-YY.MM` with `git cherry-pick -x` (or `-xe` when you need a reason), open a PR with `[YY.MM]` in the title, and link the original `master` PR. Do **not** target `nixos-YY.MM` (that branch tracks the tested channel tip).

### Getting your PR merged

Committers are volunteers; **days or weeks without feedback is normal**. To reduce review cycles:

- Explain **why** (not just what) in commits and the PR description for non-trivial changes.
- Keep diffs **reviewable** — atomic commits, clear code, smoke-test instructions or automated tests.
- Complete the PR template honestly (sandbox, platforms, `nixpkgs-review` when relevant).
- Get **early review from non-committers**; many committers prefer PRs that already look reviewed.
- If there is no activity for **at least one week**, politely ask again, @-mention someone, or post in Discourse “PRs ready for review” threads or the [Review Requests Matrix room](https://matrix.to/#/#review-requests:nixos.org).

Committers work on a **push basis** — an approval does not guarantee immediate merge. Re-request review or comment when you address feedback; do not assume silence means rejection, but do follow up if nothing happens after several days.

Broad governance changes (not routine packaging) may go through the NixOS [RFC process](../../15-history-and-governance/rfc-process.md) before or alongside Nixpkgs work.

## Examples

Commands from the Nixpkgs PR template / CONTRIBUTING (run from a Nixpkgs checkout or any flake-capable environment with network access to evaluate `nixpkgs`):

```bash
# Review a PR’s dependent rebuilds
nix run nixpkgs#nixpkgs-review -- pr 12345

# Same without flakes
nix-shell -p nixpkgs-review --run "nixpkgs-review pr 12345"

# Review uncommitted work in your checkout
nix-shell -p nixpkgs-review --run "nixpkgs-review wip"
```

## See also

- [Maintainers and teams](../architecture/maintainers-and-teams.md) — maintainer model, merge-bot, non-endorsed merge waiting period
- [OfBorg and CI](ofborg-and-ci.md) — automated PR checks
- [Staging and branches](staging-and-branches.md) — `master`, `staging`, release branches
- [Simple package](../packaging/simple-package.md) — minimal packaging walkthrough for first-time contributors

## References

- [Contributing to Nixpkgs (CONTRIBUTING.md)](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)
- [Nixpkgs maintainers README](https://github.com/NixOS/nixpkgs/blob/master/maintainers/README.md) — one-week wait and merge-bot context
- [ofborg](https://github.com/NixOS/ofborg)
- [nixpkgs-review](https://github.com/Mic92/nixpkgs-review)
