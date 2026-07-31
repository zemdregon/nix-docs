---
status: complete
---

# Sandbox Escape Surface

## Overview

The Nix [build sandbox](../04-store-and-build/builders-and-sandboxes.md) isolates builders so ordinary derivations cannot see undeclared host paths or reach the network. That is a **hermeticity** control: it catches accidental impurities and keeps builds reproducible. It is **not** a multi-tenant security boundary against a malicious party who can already submit builds as a [trusted user](trusted-users.md) or who can change daemon configuration.

Several documented modes intentionally widen what a builder can do—fixed-output network access, `sandbox = relaxed` / `__noChroot`, and experimental features such as [impure derivations](../08-experimental-features/impure-derivations.md) and [recursive-nix](../08-experimental-features/recursive-nix.md). Treat those as an **escape surface**: useful, but they expand trust assumptions. Do not claim the sandbox alone makes Nix “secure against all attackers.”

## Details

### What the sandbox is for

With `sandbox = true` (Linux default), builds run with a restricted view of the filesystem and, on Linux, private PID, mount, network, IPC, and UTS namespaces. The builder sees declared store inputs, the temporary build directory, minimal `/proc` and `/dev`, and any paths in `sandbox-paths`. Host layout such as `/usr/bin` is hidden so undeclared dependencies fail instead of silently succeeding.

That model protects reproducibility and undeclared-input detection. Kernel namespaces and chroots are imperfect; a determined privileged or trusted actor who controls what gets built can still abuse weaker modes, bind-mounts, or daemon policy. For how builders are scheduled and sandboxed in normal operation, see [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md).

### Configured modes (`sandbox`)

| Value | Effect on escape surface |
|-------|--------------------------|
| `true` | Ordinary builds sandboxed; FODs still get network (see below). `__noChroot` is rejected. |
| `false` | No sandbox; builders see the host filesystem layout. |
| `relaxed` | Sandboxed by default, but FODs and derivations with `__noChroot = true` skip the sandbox entirely. |

`sandbox = false` and `relaxed` plus `__noChroot` are the main **operator-controlled** ways to drop isolation. Defaults (stable manual): `true` on Linux, `false` elsewhere. Sandboxing is implemented on Linux and macOS only.

### Trusted users can weaken the sandbox

In a multi-user install, daemon policy lives in the system `nix.conf`. [Trusted users](trusted-users.md) may override restricted client settings such as `sandbox` on the CLI (for example `nix build --option sandbox false` or `--option sandbox relaxed`). Untrusted clients’ overrides are ignored (recent Nix versions warn). Membership in `trusted-users` is essentially root-equivalent for store integrity—treat sandbox overrides as part of that trust, not as a casual developer convenience.

### Fixed-output derivations (network)

[Fixed-output derivations](../02-concepts/fixed-output-derivation.md) (FODs) declare `outputHash` / `outputHashAlgo` / `outputHashMode`. On Linux they do **not** use a private network namespace, so fetches can reach the network; the declared hash is the integrity check. FODs may also use `impureEnvVars` (for example proxy settings)—allowed only on FODs. That is intentional—not a bug—but it means “sandboxed build” does not mean “no network” for every derivation.

With `sandbox = relaxed`, FODs additionally skip the sandbox filesystem isolation, not only the network restriction.

### `__noChroot`

When `sandbox = relaxed`, a derivation may set `__noChroot = true` to run **outside** the sandbox (JSON derivation option `noChroot`: disable the build sandbox *if allowed*). That is an explicit opt-out of chroot/namespace isolation for packages that cannot build hermetically.

Under `sandbox = true`, `__noChroot = true` is **not** ignored quietly: Nix fails with an error that `__noChroot` is not allowed when `sandbox` is `true`. Under `sandbox = false`, nothing is sandboxed anyway.

### Experimental wideners

Experimental feature flags have existed since **Nix 2.4**; the features below remain experimental (verify against your Nix version—stable manual as of Nix **2.34.x** still lists them as experimental).

- **[impure-derivations](../08-experimental-features/impure-derivations.md)** — `__impure = true` allows non-fixed outputs and **network access**. Only FODs or other impure derivations may depend on impure outputs. Enable with `extra-experimental-features = impure-derivations`.
- **[recursive-nix](../08-experimental-features/recursive-nix.md)** — builders may invoke Nix inside the build (`requiredSystemFeatures = [ "recursive-nix" ]`). That expands what a builder can schedule and touch in the store. An important restriction: recursive builders may **not** substitute arbitrary store paths (for example unrestricted `nix-store -r`); only paths already in the derivation’s inputs or produced by earlier recursive Nix calls in that build are allowed—otherwise hidden dependencies and store-state-dependent builds could break reproducibility. Still experimental.

Other knobs (`sandbox-paths`, `sandbox-fallback`, `allow-new-privileges`) also change isolation; use them sparingly and document why.

### Threat model (keep claims modest)

| Assumption | Role of the sandbox |
|------------|---------------------|
| Accidental host deps / non-hermetic scripts | Sandbox helps; undeclared paths fail. |
| Untrusted content fetched as a FOD | Hash pins content; network is allowed by design. |
| Malicious derivation from a trusted builder / daemon admin | Sandbox is **not** a sufficient boundary; trust [trusted-users](trusted-users.md) and [supply-chain](supply-chain.md) controls instead. |
| “Nix is secure against all attackers” | Overclaim—avoid. |

## Examples

**Strict sandboxing (Linux default):**

```ini
sandbox = true
```

**Relaxed mode**—FODs and `__noChroot` skip isolation:

```ini
sandbox = relaxed
```

**Trusted-user override for one build** (weakens isolation; requires `trusted-users`):

```bash
nix build --option sandbox false ./package.nix
```

**Derivation opt-out** (only effective when `sandbox = relaxed`; errors under `sandbox = true`):

```nix
derivation {
  name = "needs-host";
  # ...
  __noChroot = true;
}
```

**Enable experimental wideners** (unstable; stamp your Nix version—flags since 2.4; still experimental in 2.34.x):

```ini
extra-experimental-features = impure-derivations recursive-nix
```

## References

- [nix.conf: sandbox](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-sandbox) — `true` / `relaxed` / `false`, FOD network exception, `__noChroot`
- [nix.conf: trusted-users](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-trusted-users) — elevated daemon rights (root-equivalent warning)
- [Advanced attributes](https://nix.dev/manual/nix/stable/language/advanced-attributes.html) — FOD hash attrs, `impureEnvVars`, `requiredSystemFeatures`
- [Derivation options (`noChroot`)](https://nix.dev/manual/nix/stable/protocols/json/derivation/options.html#noChroot) — disable sandbox if allowed
- [Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — flag lifecycle (since Nix 2.4); `impure-derivations`, `recursive-nix`

## See also

- [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md) — sandbox mechanics and defaults
- [impure-derivations](../08-experimental-features/impure-derivations.md) — `__impure` and network
- [recursive-nix](../08-experimental-features/recursive-nix.md) — Nix inside builders
- [Trusted users](trusted-users.md) — who can change daemon / sandbox policy
- [Supply chain](supply-chain.md) — trust beyond the local sandbox
- [Inter-machine trust](inter-machine-trust.md) — sandbox is local hermeticity; mesh trust is separate
- [Machine mesh](../02-concepts/machine-mesh.md) — how machines relate in a flake-driven fleet
