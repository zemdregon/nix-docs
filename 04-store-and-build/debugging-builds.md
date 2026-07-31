---
status: complete
---

# Debugging Builds

## Overview

When something fails, first decide whether Nix failed during **evaluation** (computing derivations and attributes) or during **realization** (running a builder). Evaluation errors surface before any build starts; build errors mean a derivation was computed but its builder exited non-zero. The two cases use different tools—traces and `--show-trace` for eval, logs and leftover build directories for builds.

This page covers the build side. For Nix-language and module evaluation failures, see [Debugging evaluation](../11-development/debugging-evaluation.md) and [`--show-trace`](../03-language/builtins/debugging-trace.md).

Modern CLI commands such as `nix build`, `nix log`, and `nix develop` require the experimental **`nix-command`** feature (and **`flakes`** when using flake installables). As of the Nix **2.34.x** stable manual, they remain experimental.

## Details

### Evaluation vs build failure

| Signal | Likely phase | First step |
|--------|--------------|------------|
| Error before “building …” / no store path for the failed attr | Evaluation | Re-run with `--show-trace`; see [Debugging evaluation](../11-development/debugging-evaluation.md) |
| “builder for … failed with exit code N” / log path printed | Build | Read the build log (below) |
| `hash mismatch in fixed-output derivation` | Build (FOD) | Update `outputHash` / `outputHashAlgo`; see [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) |
| Missing file under `/usr`, `/etc`, or `$HOME` inside the log | Build (sandbox) | Add declared inputs or fix impurity; see [Builders and sandboxes](builders-and-sandboxes.md) |

### Common failure modes (operator view)

| Symptom in the log | Likely cause | What to try |
|--------------------|--------------|-------------|
| `checkPhase` / `installCheckPhase` failure | Upstream or packaging tests | Read the failing test output; temporarily set `doCheck = false` only while investigating—not for shipping |
| `Permission denied`, chroot, or “Operation not permitted” | [Sandbox](builders-and-sandboxes.md) or missing declared inputs | Compare with a `nix develop` shell; fix `buildInputs` / impurity |
| No space left on device in `/tmp` or the build dir | Disk / `TMPDIR` | Free space or point `TMPDIR` at a larger filesystem |
| Build aborted / silent timeout | `timeout` or `max-silent-time` | Raise or disable the setting for that run; `nix-build` uses exit code **101** for timeouts |
| `hash mismatch in fixed-output derivation` | FOD upstream drift | Update declared hash; see [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) |
| `--check` / rebuild not reproducible | Non-deterministic builder | Compare outputs; `nix-build` uses exit code **104** for failed check mode |

Classic `nix-build` also documents exit codes **100** (generic build failure) and **102** (hash mismatch). With `--keep-going` / `-k`, multiple failures combine their codes with bitwise OR.

Do not confuse **`--keep-going` / `-k`** (continue other independent builds after one fails—handy when debugging a multi-attr set) with **`--keep-failed` / `-K`** (preserve the failed build tree for inspection).

### Reading build logs

Modern Nix prints whether each path was **substituted** from a cache or **built** locally. A cache miss is normal—it triggers a build, not necessarily a bug.

To stream logs as builds run:

```bash
nix build .#myPackage -L
```

`-L` is shorthand for `--print-build-logs`. Log printing and keep-failed are independent concerns.

After a failed build, fetch the log for a store path (works even if you no longer have the terminal scrollback):

```bash
nix log /nix/store/…-myPackage-1.0.drv
```

Classic `nix-build` also writes a human-readable log under `/nix/var/log/nix/drvs/…` on some installs; `nix log` is the portable interface on the modern CLI.

Scroll to the **last phase** that ran—stdenv runs [build phases](build-phases.md) in order (`unpackPhase`, `configurePhase`, `buildPhase`, …). The first error above the final `builder failed` line is usually the root cause.

### Keeping the build directory (`-K` / `--keep-failed`)

By default Nix deletes the temporary build tree when a builder fails. To inspect artifacts, re-run with the `keep-failed` setting enabled. Every `nix.conf` setting is also a CLI flag (Nix 2.34.x):

```bash
nix-build --keep-failed -A myPackage
# short form:
nix-build -K -A myPackage

# modern CLI (same setting):
nix build --keep-failed .#myPackage
```

On failure, Nix prints a note pointing at the preserved tree (often under the system temp dir / `build-dir`). `cd` into that directory: you will find partial `source/`, `build/`, and phase helper scripts from [stdenv](build-phases.md).

**`env-vars` (stdenv convention):** at the start of each phase, nixpkgs stdenv dumps the builder’s shell environment into `env-vars` at the top of that tree. After a `-K` run, `source env-vars` recreates the same variables and functions (`buildPhase`, `makeFlags`, …) so you can re-run `make` or individual phases by hand without starting from a dev shell. This is the usual workflow for “why did `make` die here?” inside the real sandbox layout.

### Interactive debugging (`nix develop` / `nix-shell`)

Enter an environment close to what the builder sees:

```bash
nix develop .#myPackage
# classic:
nix-shell -A myPackage
```

You get the same `buildInputs`, `nativeBuildInputs`, and environment variables the derivation declares. From there you can run individual phases manually (e.g. `unpackPhase`, then `cd source && configurePhase`) to reproduce the failure step by step. See [Build phases](build-phases.md) for the phase sequence and hooks.

**Phase flags (experimental `nix develop`):** without entering an interactive shell first, you can run a single stdenv phase directly:

```bash
nix develop .#myPackage --unpack
nix develop .#myPackage --configure
nix develop .#myPackage --build
nix develop .#myPackage --check
nix develop .#myPackage --install
nix develop .#myPackage --installcheck
nix develop .#myPackage --phase build
```

This does not disable the sandbox—host paths stay hidden—but it is enough to debug compiler flags, missing tools in `nativeBuildInputs`, and script logic. If behaviour differs between the shell and a sandboxed build, prefer `nix-build -K` with `source env-vars`, or `breakpointHook` below, to inspect the real failed tree.

### Pausing inside the sandbox (`breakpointHook`)

For failures that only reproduce under the real builder sandbox, add nixpkgs’ **`breakpointHook`** to `nativeBuildInputs`. It is a Linux-only setup hook: on build failure it **pauses** instead of exiting immediately, prints instructions for attaching into the sandbox (via `cntr`), and keeps the environment intact for inspection.

```nix
{ nativeBuildInputs = [ breakpointHook ]; }
```

**Remote builds:** attach on the **machine that ran the build**, not your laptop. While debugging locally, disable remotes with `--builders ''` (`nix build`) or `--option builders ''` (`nix-build`). See [Remote builders](remote-builders.md).

### Hash mismatches and impurity

**Fixed-output derivations** (fetchers, vendored tarballs) fail with an explicit hash mismatch when upstream content changes. Fix the declared hash in the expression; do not “patch around” the mismatch. Details: [Fixed-output derivation](../02-concepts/fixed-output-derivation.md).

**Sandbox violations** show up as “file not found” for paths outside the store closure—often `/bin/sh`, locale files, or tools not listed in `buildInputs`. Compare with [Builders and sandboxes](builders-and-sandboxes.md). With `sandbox = relaxed`, FODs and derivations that set `__noChroot = true` skip the sandbox; ordinary sandboxed builds still hide undeclared host paths.

### Substitution vs local build

If you expected a binary from cache but Nix built locally, check:

- Substituter configuration and network reachability (log lines mention “copying path” vs “building”).
- Whether the input hash changed (any dependency rebuild propagates).

The `fallback` setting (`--fallback`) builds from source when a binary substitute fails. To force a local rebuild of an already-built package for comparison, `nix build` supports `--rebuild` (Nix 2.34.x). To disable substitution entirely for a run: `--option substitute false`.

## Examples

A small package fails at compile time:

```bash
$ nix build .#hello-broken
error: builder for '/nix/store/abc…-hello-broken-0.1.drv' failed with exit code 2
```

1. Read the log:

   ```bash
   nix log /nix/store/abc…-hello-broken-0.1.drv
   ```

   The tail shows `buildPhase` invoking `gcc` and a missing header.

2. Preserve the tree and reload the builder environment:

   ```bash
   nix-build -K -A hello-broken
   # note: build failed … see /tmp/nix-build-…/
   cd /tmp/nix-build-…/
   source env-vars
   cd source
   make   # same error, now with the exact builder env
   ```

3. Or run one phase without an interactive shell:

   ```bash
   nix develop .#hello-broken --build
   ```

4. For sandbox-only failures, add `breakpointHook` temporarily and rebuild; follow the printed `cntr` attach steps on the build host.

5. Add the missing library to `buildInputs`, rebuild; confirm the log shows `copying path` from cache for unchanged dependencies and `building` only for the package you fixed.

When debugging several attrs at once, `-k` / `--keep-going` lets the rest of the set finish so you can triage multiple logs in one run.

## See also

- [Build phases](build-phases.md)
- [Builders and sandboxes](builders-and-sandboxes.md)
- [Remote builders](remote-builders.md)
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md)
- [Debugging evaluation](../11-development/debugging-evaluation.md)

## References

- [nix-build](https://nix.dev/manual/nix/stable/command-ref/nix-build.html) — `--keep-failed`, `--keep-going`, build-failure exit codes (100/101/102/104)
- [nix.conf — `keep-failed`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-keep-failed) — preserve failed build directories
- [nix develop](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop.html) — phase flags (`--build`, `--phase`, …; experimental `nix-command`)
- [stdenv build phases](https://nixos.org/manual/nixpkgs/stable/#sec-stdenv-phases) — phase names and hooks
- [breakpointHook](https://nixos.org/manual/nixpkgs/stable/#sec-breakpointHook) — pause on failure inside the Linux sandbox
- [nix.conf: sandbox](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-sandbox) — sandbox and related settings
