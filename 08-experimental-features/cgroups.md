---
status: complete
---

# cgroups

**Version stamp:** Nix **2.34.x** stable experimental-features manual — still experimental; enable explicitly.

## Overview

The **`cgroups`** experimental feature lets Nix **execute builds inside cgroups** on Linux—kernel groups for processes that can carry resource limits and membership rules. It complements the filesystem isolation described in [Builders and Sandboxes](../04-store-and-build/builders-and-sandboxes.md): sandboxes hide undeclared host paths and enforce declared store inputs, while cgroups give the build scheduler a supported place to run builders under Linux resource boundaries when you opt in.

The flag remains **experimental**: behaviour and requirements may change until stabilization. For how flags are enabled and how they graduate to stable, see [Feature Flags Overview](feature-flags-overview.md) and [Tracking Stabilization](tracking-stabilization.md).

## Details

**What the flag unlocks.** The manual states that enabling `cgroups` allows Nix to run builds inside cgroups. The concrete switch is the [`use-cgroups`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-use-cgroups) setting in `nix.conf` (default `false`). Cgroup-backed builds are **Linux-only**; other platforms ignore this path. Enabling the experimental feature is necessary but not sufficient—you still set `use-cgroups = true` when you want cgroup membership for ordinary builds.

**Automatic use for `uid-range`.** Even when `use-cgroups` is off, cgroups are **required and enabled automatically** for derivations that need the `uid-range` system feature. On Linux, `uid-range` lets a build run in a user namespace as root with 65,536 UIDs—primarily for container-style builds such as `systemd-nspawn` inside the sandbox. That system feature is included by default on Linux when the [`auto-allocate-uids`](auto-allocate-uids.md) **setting** is enabled (which requires the homonymous experimental feature). The manual’s [`system-features`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-system-features) and `uid-range` entries describe when schedulers advertise and require it.

**Relationship to sandboxes.** Cgroups do not replace sandboxing. Typical multi-user setups still rely on build users, chroots or namespaces, and declared store inputs as in [Builders and Sandboxes](../04-store-and-build/builders-and-sandboxes.md). Opting into `use-cgroups` adds cgroup membership for builds where the daemon supports it—not a substitute for hermetic store access rules.

**When to enable `use-cgroups`.** Many installs never set `use-cgroups = true` and still build normally—the sandbox path is unchanged. Enable it when you want cgroup membership for builds broadly, not only for derivations that declare a need for `uid-range`. If you already use [auto-allocate-uids](auto-allocate-uids.md), Linux builds may hit the automatic cgroup path whenever `uid-range` is advertised; turning on `use-cgroups` extends cgroup use beyond that subset.

**Applying configuration.** On multi-user installs the daemon reads `nix.conf` at startup; after changing `extra-experimental-features` or `use-cgroups`, restart the Nix daemon so new builds pick up the policy. Single-user mode applies settings for the invoking user’s session without a long-lived daemon.

**Not a controller reference.** This page does not document individual cgroup controllers or hierarchy layout; those details are outside the Nix manual’s `cgroups` / `use-cgroups` entries. Treat upstream release notes and the manual as authoritative when upgrading Nix.

## Examples

Enable the feature and turn on cgroup-backed builds in `nix.conf`:

```ini
extra-experimental-features = cgroups
use-cgroups = true
```

Restart the Nix daemon on multi-user systems (or use a fresh shell in single-user mode). One-shot enablement of the flag on a single invocation does not persist `use-cgroups`:

```bash
nix --extra-experimental-features cgroups build .
```

Persistent cgroup-backed builds still require `use-cgroups = true` in `nix.conf`. Builds that require `uid-range` get cgroups even without that setting; see the manual for when the system feature is implied.

## References

- [Nix manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — `cgroups` flag description and lifecycle
- [Nix manual — nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `use-cgroups`, `system-features`, and related build settings

## See also

- [Feature Flags Overview](feature-flags-overview.md) — enabling experimental features
- [auto-allocate-uids](auto-allocate-uids.md) — automatic UID allocation (pairs with `uid-range` on Linux)
- [Builders and Sandboxes](../04-store-and-build/builders-and-sandboxes.md) — build users, sandbox modes, and hermetic builds
- [Tracking Stabilization](tracking-stabilization.md) — path from experimental to stable
