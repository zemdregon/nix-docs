---
status: complete
---

# Maintainers and Teams

## Overview

Nixpkgs maintainers are listed contacts for packages and areas—not exclusive owners. Anyone can open PRs for version bumps and fixes; maintainers are expected to keep their packages working and updated, and they have priority when changes conflict. Teams group maintainers by expertise or functional area. Both are declared in central Nix files and referenced from package `meta` attributes.

Understanding this model matters for contributors: you do not need to be a maintainer to improve most packages, but you should know when to wait for review, how to reach the right people, and how to become a listed maintainer yourself.

## Details

### Maintainer model

Maintainers are **not** gatekeepers. The fluid model lets the tree scale: contributors routinely update packages without being listed. A maintainer’s duty is to keep assigned packages healthy, respond to notifications, and decide on substantive changes to them. Listed maintainers are empowered on their packages—anyone can PR bumps, but maintainers set direction when it matters.

When a **non-maintainer committer** merges without maintainer endorsement, [CONTRIBUTING](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md) conventions typically expect **at least one week** of waiting so listed maintainers can review. This applies to most packages. **Critical packages**—those that trigger mass rebuilds or have explicit OWNERS rules—use negotiated timelines instead of the default week. The security team may override for urgent security fixes.

If a maintainer and another contributor disagree, **maintainer priority** applies; a maintainer may revert changes they did not approve.

### Becoming a maintainer

No commit access is required. To become a maintainer, add yourself to [`maintainers/maintainer-list.nix`](https://github.com/NixOS/nixpkgs/blob/master/maintainers/maintainer-list.nix) **and** to the package’s `meta.maintainers`. If the list entry is bundled with other changes, put it in a **separate commit** titled `maintainers: add <name>`.

**Inactivity** (~**three months** without responding to notifications) can lead to a removal PR. The usual process is to add the inactive maintainer as a reviewer, wait about a week, then merge removal if there is still no response. Removed maintainers are welcome back anytime.

### Teams

Teams live in [`maintainers/team-list.nix`](https://github.com/NixOS/nixpkgs/blob/master/maintainers/team-list.nix). Packages reference them via `meta.teams`. Teams organize people by **expertise or area** (language ecosystems, infrastructure, security)—not by employer.

Some teams are mirrored as GitHub teams under the parent [`NixOS/nixpkgs-maintainers`](https://github.com/orgs/NixOS/teams/nixpkgs-maintainers) org team. That sync is optional tooling, not a second source of truth; the Nix files remain canonical.

### Meta attributes and tooling

`meta.maintainers` and `meta.teams` are **standard meta attributes**—they are not builder inputs, so changing them does not rebuild the derivation. See the [Nixpkgs manual](https://nixos.org/manual/nixpkgs/stable/#sec-standard-meta-attributes) for the full attribute set.

**CI** notifies listed maintainers on relevant PRs (see [Ofborg and CI](../contribution/ofborg-and-ci.md)). The [nixpkgs-merge-bot](https://github.com/NixOS/nixpkgs/blob/master/maintainers/README.md) can merge on a maintainer’s behalf for `by-name` packages under its constraints. New maintainers receive a GitHub team invite (typically email-only, valid for about one week).

Packages with an empty `meta.maintainers` list can trigger a **maintainerless** evaluation warning—worth fixing when you touch a package, even if you are not taking ownership yet.

Community trackers such as [zh.fail](https://zh.fail/) and [Repology](https://repology.org/) help find outdated packages and who last touched them; they are unofficial and do not replace `meta.maintainers`.

## Examples

```nix
{ lib, stdenv }:

stdenv.mkDerivation {
  pname = "example";
  version = "1.0";

  meta = with lib; {
    maintainers = with maintainers; [ alice ];
    teams = with teams; [ python ];
  };
}
```

`alice` must exist in `maintainer-list.nix`; `python` in `team-list.nix`. See [mkDerivation](mkDerivation.md) for the full `meta` attribute set.

## References

- [Nixpkgs maintainers README](https://github.com/NixOS/nixpkgs/blob/master/maintainers/README.md)
- [Standard meta attributes (maintainers)](https://nixos.org/manual/nixpkgs/stable/#sec-standard-meta-attributes)
- [`maintainers/maintainer-list.nix`](https://github.com/NixOS/nixpkgs/blob/master/maintainers/maintainer-list.nix)
- [`maintainers/team-list.nix`](https://github.com/NixOS/nixpkgs/blob/master/maintainers/team-list.nix)
- [Nixpkgs CONTRIBUTING](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)

## See also

- [Review process](../contribution/review-process.md) — merge timing and maintainer endorsement
- [Ofborg and CI](../contribution/ofborg-and-ci.md) — maintainer notifications
- [Staging and branches](../contribution/staging-and-branches.md) — critical packages and mass rebuilds
- [mkDerivation](mkDerivation.md) — `meta` attributes
- [lib.md](lib.md) — `lib.maintainers` and `lib.teams` imports
- [Package sets](package-sets.md)
- [Supply chain](../../14-security-and-trust/supply-chain.md) — security-team overrides
