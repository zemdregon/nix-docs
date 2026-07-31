---
status: complete
---

# cgroups

**Version stamp:** Nix **2.34.x** stable experimental-features manual — still experimental; enable explicitly.

## Overview

The **`cgroups`** experimental feature lets Nix **execute builds inside cgroups** on Linux—a kernel mechanism for grouping processes and applying resource limits. It complements the filesystem isolation described in [Builders and Sandboxes](../04-store-and-build/builders-and-sandboxes.md): sandboxes hide undeclared host paths, while cgroups give the build scheduler a place to run builders under Linux resource boundaries.

The flag remains **experimental**: behavior may change until stabilisation. For how flags are enabled and how they graduate to stable, see [Feature Flags Overview](feature-flags-overview.md) and [Tracking Stabilization](tracking-stabilization.md).

## Details

**What the flag unlocks.** The manual states that enabling `cgroups` allows Nix to run builds inside cgroups. The concrete switch is the [`use-cgroups`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-use-cgroups) setting in `nix.conf` (default `false`). Cgroup-backed builds are **Linux-only**; other platforms ignore this path.

**Automatic use for `uid-range`.** Even when `use-cgroups` is off, cgroups are **required and enabled automatically** for derivations that need the `uid-range` system feature. On Linux, `uid-range` lets a build run in a user namespace with a large UID span—primarily for container-style builds such as `systemd-nspawn` inside the sandbox. That system feature is included by default on Linux when [`auto-allocate-uids`](auto-allocate-uids.md) is enabled; see the manual’s `system-features` and `uid-range` entries for scheduling details.

**Relationship to sandboxes.** Cgroups do not replace sandboxing. Typical multi-user setups still rely on build users, chroots or namespaces, and declared store inputs as in [Builders and Sandboxes](../04-store-and-build/builders-and-sandboxes.md). Opting into `use-cgroups` adds cgroup membership for builds where the daemon supports it—not a substitute for hermetic store access rules.

**Not a controller reference.** This page does not document individual cgroup controllers or hierarchy layout; those details are outside the Nix manual’s `cgroups` / `use-cgroups` entries. Treat upstream release notes and the manual as authoritative when upgrading Nix.

## Examples

Enable the feature and turn on cgroup-backed builds in `nix.conf`:

```ini
extra-experimental-features = cgroups
use-cgroups = true
```

Restart the Nix daemon (or use a fresh shell in single-user mode) so the settings apply. Builds that require `uid-range` get cgroups even without `use-cgroups = true`; see the manual for when that system feature is implied.

## References

- [Nix manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — `cgroups` flag description and lifecycle
- [Nix manual — nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `use-cgroups`, `system-features`, and related build settings

## See also

- [Feature Flags Overview](feature-flags-overview.md) — enabling experimental features
- [auto-allocate-uids](auto-allocate-uids.md) — automatic UID allocation (pairs with `uid-range` on Linux)
- [Builders and Sandboxes](../04-store-and-build/builders-and-sandboxes.md) — build users, sandbox modes, and hermetic builds
- [Tracking Stabilization](tracking-stabilization.md) — path from experimental to stable
