---
status: complete
---

# auto-allocate-uids

**Version stamp:** Nix **2.34.x** stable experimental-features manual — still experimental; enable explicitly.

## Overview

The **`auto-allocate-uids`** experimental feature lets Nix pick UIDs for builds automatically instead of relying on pre-created **`nixbld*`** accounts in [`build-users-group`](../04-store-and-build/builders-and-sandboxes.md). That removes the need to provision and size a pool of dedicated build users on multi-user installs.

The flag is **experimental**: behaviour and requirements may change until stabilization. Enabling it also unlocks the homonymous [`auto-allocate-uids`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-auto-allocate-uids) setting in `nix.conf`—the flag alone is not enough to turn the behaviour on. For how experimental features are organized, see [Feature flags overview](feature-flags-overview.md).

## Details

**What the flag unlocks.** With `auto-allocate-uids` enabled, Nix can allocate UIDs dynamically for sandboxed builds rather than dropping privileges to members of `build-users-group`. The manual describes this as an alternative to the traditional model where builds run under fixed `nixbld1`, `nixbld2`, … accounts. See [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md) for the classic build-user setup.

**The companion setting.** The [`auto-allocate-uids`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-auto-allocate-uids) `nix.conf` option controls whether automatic UID selection is actually used; it defaults to `false` and requires the experimental feature to be enabled before it can be changed. Allocation start points, platform behaviour, and related options such as [`start-id`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-start-id) are documented there—do not hard-code values from blog posts; check the manual for your Nix version.

**Relation to `uid-range` and cgroups.** On Linux, enabling the `auto-allocate-uids` setting also advertises the `uid-range` system feature by default, which lets builds use a user namespace with a block of UIDs (useful for container-style builds). Derivations that require `uid-range` need cgroups; the [`use-cgroups`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-use-cgroups) setting documents when cgroups are required and enabled automatically. See [cgroups](cgroups.md) for the separate cgroups experimental feature.

**Not covered here.** Sandbox layout, remote builders, and the full privilege-drop model remain under [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md). Stabilization progress is summarized in [Tracking stabilization](tracking-stabilization.md).

## Examples

Enable the feature and turn on automatic UID allocation in `nix.conf` (pattern from the manual):

```ini
extra-experimental-features = auto-allocate-uids
auto-allocate-uids = true
```

One-shot enablement of the flag on a single invocation (does not persist the setting):

```bash
nix --extra-experimental-features auto-allocate-uids build .
```

Persistent automatic allocation still requires `auto-allocate-uids = true` in `nix.conf` after the feature is enabled.

## References

- [Nix manual — experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — `auto-allocate-uids` flag description
- [Nix manual — nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — [`auto-allocate-uids`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-auto-allocate-uids) and related settings

## See also

- [Feature flags overview](feature-flags-overview.md) — how to enable experimental features
- [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md) — classic `build-users-group` / `nixbld*` model
- [cgroups](cgroups.md) — cgroup-based build isolation (related via `uid-range`)
- [Tracking stabilization](tracking-stabilization.md) — experimental-to-stable lifecycle
