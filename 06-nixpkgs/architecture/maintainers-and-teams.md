---
status: complete
---

# Maintainers and Teams

## Overview

Nixpkgs maintainers are listed contacts for packages and areas—not exclusive owners. Anyone can open PRs for bumps and fixes; maintainers are expected to keep their packages working and updated, and they have priority when changes conflict. Teams group maintainers by expertise or functional area. Both are declared in central Nix files and referenced from package `meta` attributes.

## Details

### Maintainer model

Maintainers are **not** gatekeepers. The fluid model lets the tree scale: contributors routinely update packages without being listed. A maintainer’s duty is to keep assigned packages healthy and to decide on substantive changes to them.

When a non-maintainer committer merges without maintainer endorsement, [CONTRIBUTING](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md) conventions typically expect **at least one week** of waiting so listed maintainers can review. Critical packages—those that trigger mass rebuilds or have explicit OWNERS rules—follow negotiated conventions on that timeline. The security team may override for urgent security fixes.

If a maintainer and another contributor disagree, **maintainer priority** applies; a maintainer may revert changes they did not approve.

### Becoming a maintainer

No commit access is required to become a maintainer. Add yourself to [`maintainers/maintainer-list.nix`](https://github.com/NixOS/nixpkgs/blob/master/maintainers/maintainer-list.nix) **and** to the package’s `meta.maintainers`. If the list entry is a separate commit, title it `maintainers: add <name>`.

Long inactivity (~**three months** without responding to notifications) can lead to a removal PR; removed maintainers are welcome back anytime.

### Teams

Teams live in [`maintainers/team-list.nix`](https://github.com/NixOS/nixpkgs/blob/master/maintainers/team-list.nix). Packages reference them via `meta.teams`. Teams organize people by **expertise or area** (e.g. language ecosystems, infrastructure), not by employer.

### Meta attributes and tooling

`meta.maintainers` and `meta.teams` are **standard meta attributes**—they are not builder inputs, so changing them does not rebuild the derivation. CI notifies listed maintainers on relevant PRs. The [nixpkgs-merge-bot](https://github.com/NixOS/nixpkgs/blob/master/maintainers/README.md) can merge for maintainers on `by-name` packages under its constraints. New maintainers are invited to the GitHub team [`NixOS/nixpkgs-maintainers`](https://github.com/orgs/NixOS/teams/nixpkgs-maintainers) (invite is typically email-only and expires in about a week).

Packages with an empty `meta.maintainers` list can trigger a **maintainerless** evaluation warning.

## Examples

```nix
{ lib, ... }:

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

- [Review process](../contribution/review-process.md)
- [mkDerivation](mkDerivation.md) — `meta` attributes
- [Package sets](package-sets.md)
- [Supply chain](../../14-security-and-trust/supply-chain.md)
