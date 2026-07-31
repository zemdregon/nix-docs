---
status: complete
---

# auto-allocate-uids

**Version stamp:** Nix **2.34.x** stable experimental-features manual — still experimental; enable explicitly.

## Overview

The **`auto-allocate-uids`** experimental feature lets Nix pick UIDs for builds automatically instead of relying on pre-created **`nixbld*`** accounts in [`build-users-group`](../04-store-and-build/builders-and-sandboxes.md). That removes the need to provision and size a pool of dedicated build users on multi-user installs.

The flag is **experimental**: behaviour and requirements may change until stabilization. Enabling it unlocks the homonymous [`auto-allocate-uids`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-auto-allocate-uids) setting in `nix.conf`—the flag alone is not enough to turn the behaviour on. For how experimental features are organized, see [Feature flags overview](feature-flags-overview.md).

## Details

**What the flag unlocks.** With the `auto-allocate-uids` experimental feature enabled, Nix can allocate UIDs dynamically for sandboxed builds rather than dropping privileges to members of `build-users-group`. The manual describes this as an alternative to the traditional model where builds run under fixed `nixbld1`, `nixbld2`, … accounts managed through [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md).

**The companion setting.** The [`auto-allocate-uids`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-auto-allocate-uids) `nix.conf` option controls whether automatic UID selection is actually used; it defaults to `false` and requires the experimental feature before it can be changed. When enabled, UIDs are allocated starting at **872415232** (`0x34000000`) on Linux and **56930** on macOS. The related [`start-id`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-start-id) setting sets the first UID and GID for dynamic allocation (default **872415232** in the manual for your Nix version—re-check when upgrading).

**Relation to `uid-range` and cgroups.** On Linux, enabling the `auto-allocate-uids` **setting** (not merely the flag) also includes the `uid-range` system feature by default. That feature lets builds run in a user namespace with a large UID span—primarily for container-style builds such as `systemd-nspawn` inside the sandbox. Derivations that require `uid-range` need cgroups; Nix enables cgroups automatically for those builds even when [`use-cgroups`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-use-cgroups) is off. See [cgroups](cgroups.md) for the separate cgroups experimental feature and [`system-features`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-system-features) in the manual for scheduling details.

**Multi-user installs.** On a daemon-backed setup, both the experimental feature and `auto-allocate-uids = true` must be set in the daemon's `nix.conf` (typically `/etc/nix/nix.conf`), followed by a daemon restart. Passing `--extra-experimental-features auto-allocate-uids` on a client command enables the flag for that invocation only—it does not persist the setting or schedule daemon builds with automatic UID allocation.

**Classic model contrast.** The traditional path provisions a fixed pool of `nixbld*` users, assigns one build user per build, and never runs two concurrent builds under the same account. Automatic UID allocation replaces that provisioning burden but does not remove sandboxing or store-access rules; see [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md) for the full privilege-drop model.

**Tracking.** The feature remains experimental in Nix **2.34.x**; stabilisation is tracked on the [auto-allocate-uids tracking milestone](https://github.com/NixOS/nix/milestone/34). See [Tracking stabilization](tracking-stabilization.md) for the general lifecycle.

## Examples

Enable the feature and turn on automatic UID allocation in `nix.conf` (pattern from the manual):

```ini
extra-experimental-features = auto-allocate-uids
auto-allocate-uids = true
```

Restart the Nix daemon on multi-user installs so the daemon picks up both settings.

One-shot enablement of the flag on a single invocation (does not persist the setting):

```bash
nix --extra-experimental-features auto-allocate-uids build .
```

Persistent automatic allocation still requires `auto-allocate-uids = true` in `nix.conf` after the feature is enabled.

## References

- [Nix manual — experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — `auto-allocate-uids` flag description
- [Nix manual — nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — [`auto-allocate-uids`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-auto-allocate-uids), [`start-id`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-start-id), [`system-features`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-system-features), and [`use-cgroups`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-use-cgroups)
- [auto-allocate-uids tracking milestone](https://github.com/NixOS/nix/milestone/34) — stabilisation tracking on the Nix repository

## See also

- [Feature flags overview](feature-flags-overview.md) — how to enable experimental features
- [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md) — classic `build-users-group` / `nixbld*` model
- [cgroups](cgroups.md) — cgroup-based build isolation (related via `uid-range`)
- [Tracking stabilization](tracking-stabilization.md) — experimental-to-stable lifecycle
