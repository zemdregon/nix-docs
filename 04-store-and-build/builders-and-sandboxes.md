---
status: complete
---

# Builders and Sandboxes

## Overview

A **builder** is the process that **realizes** a [derivation](../02-concepts/derivation.md)—it runs the build script and writes outputs into the [Nix store](../02-concepts/store-path.md). On a typical multi-user install, the **Nix daemon** schedules builds and runs them under dedicated **build users** (`build-users-group`), not as the calling user or as root.

The **sandbox** is the isolation mechanism behind [hermetic builds](../01-philosophy/hermetic-builds.md): that page states the goal (declared inputs only); this page covers how Nix enforces it. When enabled, the builder sees declared store inputs, a temporary build directory, minimal pseudo-filesystems, and paths listed in `sandbox-paths`. Host paths such as `/usr/bin` are hidden so undeclared dependencies fail instead of silently succeeding. On Linux, ordinary builds also get a private network namespace—**network is blocked unless** the derivation is a [fixed-output derivation](../02-concepts/fixed-output-derivation.md) (FOD).

## Details

### Who runs the builder

In a multi-user setup, builds should not run as the Nix daemon account or the caller—both could influence store contents in unsafe ways. When `build-users-group` is set (commonly `nixbld`), Nix drops privileges to members of that group for each build. Nix never runs two builds under the same build-user account at once.

Single-user installs run builds under the invoking user; sandboxing still applies when enabled, but there is no separate build-user pool.

**Remote builders** are other machines listed in the `builders` setting; the local daemon can offload work over SSH. They run the same realization logic under their own sandbox rules. See [Remote builders](remote-builders.md) and the [Remote Builds](https://nix.dev/manual/nix/stable/advanced-topics/distributed-builds.html) chapter.

### Sandbox modes (`sandbox`)

Configured in `nix.conf` (or overridden on the CLI by [trusted users](../14-security-and-trust/trusted-users.md)):

| Value | Behavior |
|-------|----------|
| `true` | Sandboxed builds (when the platform supports it). |
| `false` | No sandbox; the builder sees the host filesystem layout. |
| `relaxed` | Sandboxed by default, but FODs and derivations with `__noChroot = true` skip the sandbox entirely. |

**Defaults (stable manual):** `true` on Linux, `false` on all other platforms. Sandboxing is implemented on Linux and macOS only; enabling it requires running Nix as root with build users performing the actual builds.

If the kernel rejects sandbox setup, `sandbox-fallback` (default `true`) can disable sandboxing for that build rather than failing immediately.

### Linux sandbox contents

When `sandbox = true` on Linux, the builder is isolated from the normal filesystem hierarchy. It can access:

- Input paths from the Nix store (the derivation’s dependency closure).
- The temporary build directory (host `build-dir`, visible inside the sandbox as `sandbox-build-dir`, default `/build`).
- Private `/proc`, `/dev`, `/dev/shm`, and `/dev/pts`.
- Extra host paths from `sandbox-paths` (bind-mounted; supports `target=source` and optional `?` if the source may be missing).

In addition, builds run in private **PID, mount, network, IPC, and UTS namespaces** so they cannot see or affect unrelated host processes—except for the FOD network exception below.

That namespace and bind-mount model is what enforces “only declared inputs”: a script that calls `/usr/bin/gcc` without a declared dependency typically fails because `/usr` is not mounted.

### Network and fixed-output derivations

Ordinary sandboxed builds on Linux run in a **private network namespace**, so outbound network access fails. FODs are the controlled exception: they do **not** use a private network namespace, so fetchers can reach the network. In exchange they must declare `outputHash` (and related attributes); mismatched content fails the build. Under `sandbox = relaxed`, FODs (and `__noChroot` derivations) skip the sandbox altogether; under `sandbox = true`, FODs stay filesystem-sandboxed but keep network access.

### `sandbox-paths`

Use this sparingly to expose host paths the sandbox would otherwise hide—for example binding a GPU device node or a known-good `/bin/sh`. Entries in the Nix store pull in their closures automatically. The default may be empty or include a `/bin/sh` bind-mount depending on how Nix was built.

Impure: every extra path is another possible undeclared dependency. Prefer declaring tools as derivation inputs instead.

### macOS differences

macOS supports sandboxing, but **not via Linux-style bind mounts and chroot**. The manual notes that when the platform does not support bind-mount sandboxing (for example macOS), the builder’s environment uses the real `build-dir` path instead of the virtual `sandbox-build-dir` location (`sandbox-build-dir` is Linux-only). Nix applies Darwin sandbox profiles that restrict which paths the builder may read or write.

Default `sandbox = false` on macOS; turn it on only when you accept platform-specific compatibility trade-offs. Treat macOS sandboxing as a hermeticity aid aligned with [hermetic builds](../01-philosophy/hermetic-builds.md), not as a complete security boundary.

### Relation to build phases

Sandbox setup happens before the derivation’s builder executable runs. The [build phases](build-phases.md) (`configurePhase`, `buildPhase`, etc.) all execute inside this environment. Input [hashing](hashing-and-inputs.md) and output path computation are unchanged—the sandbox only restricts what the running builder can observe.

### Limits

The sandbox targets reproducibility and complete dependency graphs. It is not a multi-tenant security boundary against a compromised host or a trusted user who can change daemon policy. For intentional widenings (relaxed mode, `__noChroot`, FOD network), see [sandbox escape surface](../14-security-and-trust/sandbox-escape-surface.md).

## Examples

**Enable sandboxing in `nix.conf` (Linux default):**

```ini
sandbox = true
```

**Relaxed mode**—sandbox most builds, but allow FOD fetches and derivations that opt out with `__noChroot` to skip the sandbox:

```ini
sandbox = relaxed
```

**Expose an optional device node inside the sandbox:**

```ini
sandbox-paths = /dev/nvidiactl?
```

**Trusted user override for one build** (disables sandbox; requires membership in `trusted-users`):

```bash
nix build --option sandbox false ./package.nix
```

## References

- [Nix reference manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `sandbox`, `sandbox-paths`, `sandbox-build-dir`, `sandbox-fallback`, `builders`, `build-users-group`
- [Nix reference manual — `sandbox` setting](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-sandbox)
- [Nix reference manual — Remote Builds](https://nix.dev/manual/nix/stable/advanced-topics/distributed-builds.html) — `builders` / distributed builds
- [Nix reference manual — Nix store](https://nix.dev/manual/nix/stable/store/) — store model and realization

## See also

- [Hermetic builds](../01-philosophy/hermetic-builds.md) — concept; this page is the mechanism
- [Purity and reproducibility](../01-philosophy/purity-and-reproducibility.md) — declared inputs and consistent outputs
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) — network exception for pinned fetches
- [Hashing and inputs](hashing-and-inputs.md) — how inputs determine output paths
- [Build phases](build-phases.md) — what runs inside the sandbox
- [Remote builders](remote-builders.md) — offloading builds to other machines
- [Sandbox escape surface](../14-security-and-trust/sandbox-escape-surface.md) — intentional widenings and threat-model limits
- [Trusted users](../14-security-and-trust/trusted-users.md) — who may override `sandbox` and related settings
