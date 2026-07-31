---
status: complete
---

# Reproducible builds audit

## Overview

A **reproducible builds audit** checks whether a derivation’s outputs are **deterministic**: rebuilding with the same declared inputs should yield the same bytes. Nix’s [sandbox](../04-store-and-build/builders-and-sandboxes.md), [fixed inputs](../01-philosophy/hermetic-builds.md), and [fixed-output derivations](../02-concepts/fixed-output-derivation.md) make builds *repeatable* far more often than on conventional distros, but they do **not** guarantee bit-for-bit identical artifacts everywhere. Timestamps, parallelism, toolchain drift, and upstream build systems that ignore `SOURCE_DATE_EPOCH` can still change file contents even when the [store path](../02-concepts/store-path.md) identity is stable.

Auditing matters for [supply chain](supply-chain.md) confidence: you want to know whether a substituted binary cache path could differ from a local rebuild, and whether packaging fixes actually remove non-determinism. The [Reproducible Builds](https://reproducible.nixos.org/) effort tracks nixpkgs progress; [content-addressed derivations](../08-experimental-features/ca-derivations.md) push identity toward output hashes rather than input hashes.

## Details

### Repeatable vs bit-identical

Nix optimizes for **repeatable builds**—same derivation graph → same store paths—so substitution and rollback work. **Bit-identical reproducibility** is stricter: every file in the output matches byte-for-byte across rebuilds, hosts, and (often) time. Packaging and upstream tooling must cooperate for the second property.

| Property | What it means | What Nix gives you |
|----------|---------------|-------------------|
| **Repeatable / input-addressed** | Same `.drv` + same input closure → same `/nix/store/<hash>-…` path | Default model; sandbox + pinned inputs enforce this strongly |
| **Bit-identical / deterministic** | Rebuilding the same `.drv` locally produces identical NAR contents | **Not automatic**; must be verified per package |
| **Cross-machine identical** | Two builders with the same pin produce identical bytes | Requires deterministic upstream + pinned toolchains; platform may still differ |
| **Cross-time identical** | Rebuild months later matches today | Needs `SOURCE_DATE_EPOCH`, no embedding of build timestamps, stable archives |

[Purity and reproducibility](../01-philosophy/purity-and-reproducibility.md) explains why input-addressed identity and byte-level reproducibility are related but not the same goal.

### Common non-determinism sources

Even with sandboxing and locked nixpkgs, builders may still vary:

- **Timestamps and dates** — archives, object files, or docs embedding `$SOURCE_DATE_EPOCH`-unaware build time
- **Parallelism** — unordered iteration written into outputs (map iteration order, race-y file lists)
- **Randomness** — reading `/dev/random`, `$RANDOM`, or UUIDs baked into artifacts
- **Host leakage** — impure env vars, `-march=native`, or undeclared paths when sandbox is off or relaxed
- **Upstream fetch drift** — caught by [FOD](../02-concepts/fixed-output-derivation.md) hash mismatch, not by `--check`

Fixes usually land in nixpkgs (patches, `postPatch`, `SOURCE_DATE_EPOCH`, `doCheck` for upstream test regressions) and are tracked via reproducible-builds issue tags in nixpkgs; see [reproducible.nixos.org](https://reproducible.nixos.org/) for project status and reports.

### Spot-checking with `--check` / `--rebuild`

Nix can **rebuild an already-realised derivation and compare** the new output to the store copy. The derivation must exist locally first; otherwise Nix reports that checking is not possible.

| CLI | Command | Notes |
|-----|---------|-------|
| Classic | `nix-build expr.nix -A attr --check` | Documented in the Nix manual; exit code **104** on non-determinism |
| Classic + preserve diff | `nix-build expr.nix -A attr --check --keep-failed` | Keeps the second build at a `.check` sibling path |
| Modern | `nix build .#attr --rebuild` | `--rebuild` compares to existing store paths (Nix 2.34+) |
| Modern + preserve diff | `nix build .#attr --rebuild --keep-failed` | Same `.check` path behaviour on failure |

On mismatch, Nix errors with “may not be deterministic” and names both paths, e.g. `/nix/store/…-hello` vs `/nix/store/…-hello.check`. The `.check` path is a copy of the second build for inspection; it is **not** GC-protected and may disappear after the command unless you copy it elsewhere.

### Comparing outputs: diffoscope and `diff-hook`

For human-readable diffs, use [diffoscope](https://diffoscope.org/) from the Reproducible Builds project:

```bash
diffoscope /nix/store/…-pkg /nix/store/…-pkg.check
```

For automated CI, configure a **`diff-hook`** in `nix.conf` (`run-diff-hook = true`). Nix invokes the hook **only when outputs differ**; it does not run on successful matches. The hook receives the two output paths and derivation name; typical setups shell out to `diffoscope` or `diff -r`. See the Nix manual section [Verifying build reproducibility](https://nix.dev/manual/nix/stable/advanced-topics/diff-hook.html).

### Where auditing fits in security work

Deterministic builds reduce “works on the builder” surprises and make cache substitution safer to reason about, but they do not prove benign intent—only stable bytes. Combine audits with hash review on FOD bumps, substituter trust, and broader [supply chain](supply-chain.md) practices. [CA derivations](../08-experimental-features/ca-derivations.md) change the trust model when outputs themselves become the address; reproducibility audits remain relevant for verifying that builders are well-behaved before content addresses stabilize.

## Examples

Minimal workflow (commands illustrative; full verification needs a built package and network for nixpkgs):

```bash
# 1. Build once (classic or flakes)
nix-build nixpkgs -A hello
# nix build nixpkgs#hello

# 2. Rebuild and compare
nix-build nixpkgs -A hello --check --keep-failed
# nix build nixpkgs#hello --rebuild --keep-failed

# 3. If non-deterministic, inspect
diffoscope /nix/store/…-hello /nix/store/…-hello.check
```

These steps cannot be fully verified offline in this wiki pass—they assume an installed Nix, a realised `hello` (or your target attr), and optionally `diffoscope` in `PATH`.

**Example `nix.conf` fragment** for a diff hook (paths are site-specific):

```ini
diff-hook = /etc/nix/diff-hook.sh
run-diff-hook = true
```

```bash
#!/bin/sh
# diff-hook.sh — args: path1 path2 derivationName
exec diffoscope "$1" "$2"
```

## See also

- [Purity and reproducibility](../01-philosophy/purity-and-reproducibility.md)
- [Hermetic builds](../01-philosophy/hermetic-builds.md)
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md)
- [Supply chain](supply-chain.md)
- [Content-addressed derivations](../08-experimental-features/ca-derivations.md)
- [Debugging builds](../04-store-and-build/debugging-builds.md) — `--keep-failed`, exit codes, logs

## References

- [Reproducible Builds for NixOS](https://reproducible.nixos.org/) — project status, metrics, and nixpkgs reproducibility tracking
- [Nix manual: Verifying build reproducibility (`diff-hook`, `--check`)](https://nix.dev/manual/nix/stable/advanced-topics/diff-hook.html)
- [diffoscope](https://diffoscope.org/) — Reproducible Builds project tool for deep output comparison
