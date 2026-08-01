---
status: complete
---

# Release Cadence

## Overview

**NixOS** ships a new stable release about twice a year. [RFC 0080](https://github.com/NixOS/rfcs/blob/master/rfcs/0080-nixos-release-schedule.md) moved the targets from March/September to **May** and **November** (first applied by delaying 21.03 → **21.05**); since then names follow `YY.05` and `YY.11` (for example `26.05`, `25.11`). Each stable line gets its own channel (`nixos-26.05`, …) that takes conservative fixes until the next stable branch takes over. The [NixOS Release Team](https://nixos.org/community/) runs the cut from roadmap through artifacts.

That cadence is **not** the same as **Nix** (the evaluator/daemon) versioning. NixOS and Nixpkgs advance on the six-month schedule above; the Nix package manager has its own release notes and version numbers (the [download page](https://nixos.org/download/) lists them separately). A NixOS release may bump the packaged Nix, but you track Nix CLI/experimental-feature changes separately from “which NixOS stable am I on?”

Day to day, most installs follow a **channel** rather than a calendar date: stable lines vs `nixos-unstable` / `nixpkgs-unstable`. Live channel health is on [status.nixos.org](https://status.nixos.org/); channel URLs live at [channels.nixos.org](https://channels.nixos.org/).

When refreshing this wiki after a release, follow [meta/release-checklist.md](../meta/release-checklist.md).

**Current illustrative stable (last checked 2026-07-31):** the [NixOS download page](https://nixos.org/download/) listed **NixOS 26.05** as current; `nixos-26.05` and the prior line `nixos-25.11` both resolve on [channels.nixos.org](https://channels.nixos.org/). Re-check those pages before treating any `YY.MM` as “latest.”

## Details

**Stable release line.** Roughly every six months, Nixpkgs branches a `release-YY.MM` line and publishes a matching `nixos-YY.MM` channel. Stable channels receive bug and security updates, not wholesale desktop or ABI churn. The previous stable is typically maintained until the next one is established; check the current supported stable on the [download page](https://nixos.org/download/) and [channels.nixos.org](https://channels.nixos.org/).

**Unstable.** `nixos-unstable` (and `nixpkgs-unstable` for non-NixOS Nixpkgs users) tracks main development after Hydra tests pass. Updates are rolling: channel bumps can include large package or module changes. Unstable is the cutting edge, not a second “LTS.”

**Small channels.** Names like `nixos-26.05-small` or `nixos-unstable-small` use the same sources with a smaller binary set, so they advance faster but may force more local builds—common for servers.

**Channel advancement vs calendar release.** Cutting `YY.05` / `YY.11` is a discrete event (branch-off, ZHF, announcement). After that, the *channel* for that line still moves whenever Hydra’s tested job succeeds. [status.nixos.org](https://status.nixos.org/) shows last update, commit, and whether a channel is progressing.

**Nix vs NixOS versions.** Upgrading NixOS channels can pull a newer Nix when the release packages one; Nix’s own major/minor releases and experimental-feature stabilization follow Nix release notes, not the NixOS `YY.MM` label. See [tracking stabilization](../08-experimental-features/tracking-stabilization.md) for how Nix flags land and stabilize across Nix releases. Which binary you run ([CppNix](../13-implementations/nix-evaluator/cpp-nix.md), [Lix](../13-implementations/nix-evaluator/lix.md), …) is a separate choice from which NixOS channel you follow.

**Flakes.** Flake-based systems pin `nixpkgs` (or a flake input) to a revision or branch instead of (or in addition to) classic channels. The same `release-YY.MM` / `nixos-unstable` lines exist as Git branches; the twice-yearly cadence still describes when stable branches appear.

## Examples

- **Current stable channel (illustrative):** subscribe root to the line matching your install, e.g. `nixos-26.05`:

  ```bash
  # as root — replace YY.MM with the release you want
  nix-channel --add https://channels.nixos.org/nixos-26.05 nixos
  nixos-rebuild switch --upgrade
  ```

- **Unstable:** `nix-channel --add https://channels.nixos.org/nixos-unstable nixos` then rebuild with `--upgrade`. Prefer stable for production; see [upgrades](../09-nixos/operations/upgrades.md).

- **Check channel progress:** open [status.nixos.org](https://status.nixos.org/) for last-updated times and Hydra job status; browse [channels.nixos.org](https://channels.nixos.org/) for available channel names and redirects to the current snapshot.

## References

- [Download Nix / NixOS](https://nixos.org/download/) — current NixOS stable label and separate Nix package-manager version
- [NixOS manual — Upgrading NixOS](https://nixos.org/manual/nixos/stable/index.html#sec-upgrading) — stable / unstable / small channels and upgrade commands
- [NixOS channel status](https://status.nixos.org/) — live channel update and Hydra job status
- [Official NixOS channels](https://channels.nixos.org/) — channel URLs and current snapshots
- [RFC 0080 — NixOS release schedule](https://github.com/NixOS/rfcs/blob/master/rfcs/0080-nixos-release-schedule.md) — YY.05 / YY.11 twice-yearly target
- [NixOS Wiki — Channel branches](https://wiki.nixos.org/wiki/Channel_branches) — how channel updates progress

## See also

- [Timeline](timeline.md) — historical milestones in the Nix ecosystem
- [Upgrades](../09-nixos/operations/upgrades.md) — day-to-day channel upgrades on NixOS
- [Channel](../02-concepts/channel.md) — what a channel is and how subscriptions work
- [Tracking stabilization](../08-experimental-features/tracking-stabilization.md) — Nix feature flags across Nix releases (separate from NixOS YY.MM)
- [CppNix](../13-implementations/nix-evaluator/cpp-nix.md) — reference Nix implementation often packaged by NixOS
