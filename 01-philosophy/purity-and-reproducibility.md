---
status: complete
---

# Purity and Reproducibility

## Overview

In Nix, **purity** means evaluation and builds should not depend on undeclared ambient state—system libraries on `$PATH`, impure environment variables, or untracked network access. Given the same declared inputs, Nix aims to produce the same [store paths](../02-concepts/store-path.md).

**Reproducibility** is the goal: anyone with the same inputs can obtain the same artifacts. Purity is how Nix pursues that goal. [Hermetic builds](hermetic-builds.md)—sandboxes, fixed inputs, isolated builders—are the main mechanism; see [Why Nix](why-nix.md) for how this fits the broader design.

## Details

### What “pure” means in practice

A [derivation](../02-concepts/derivation.md) lists its inputs explicitly: sources copied into the store, dependency store paths, builder, and the environment variables the builder sees. During a build, the **sandbox** (when enabled) isolates the builder from the normal filesystem hierarchy so it sees only declared store inputs, a temporary build directory, and configured `sandbox-paths`. On Linux it also uses private namespaces; sandboxed builds other than [fixed-output derivations](../02-concepts/fixed-output-derivation.md) get no network, which prevents undeclared fetches (see the manual [`sandbox`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-sandbox) setting). Sandboxing is available on Linux and macOS; `sandbox` defaults to `true` on Linux and `false` elsewhere per that setting.

Evaluation can also be impure—reading arbitrary host paths, depending on `$HOME` / `NIX_PATH`, or fetching without a content hash. **Pure evaluation** is a separate, eval-phase restriction: the `pure-eval` setting (flake evaluation turns it on by default; non-flake workflows can enable it, for example with `nix eval --pure-eval`) limits filesystem and network access to hash-pinned inputs and disables impure constants such as `builtins.currentSystem` and `builtins.currentTime`. That is related to build purity but applies before the builder runs; see [Pure eval and impure](../07-flakes/pure-eval-and-impure.md).

### Controlled impurity: fixed-output derivations

Some work genuinely needs the network (downloading upstream sources or vendored dependencies). [Fixed-output derivations](../02-concepts/fixed-output-derivation.md) (FODs) are the controlled exception: the builder may use the network (on Linux, FODs are not placed in a private network namespace), but `outputHash`, `outputHashAlgo`, and `outputHashMode` fix the expected output in advance. If the fetched content does not match, the build fails rather than silently changing the closure.

### Input-addressed identity vs bit-for-bit binaries

By default, derivations are **input-addressed**: the hash in the output [store path](../02-concepts/store-path.md) is derived from the derivation and its inputs, so the same input graph yields the same path. That identity is what makes caching, sharing, and rollback practical.

**Bit-for-bit reproducibility** of every file across all hosts and compilers is a stronger property and is not guaranteed by input addressing alone. Timestamps, parallelism, toolchain differences, and platform-specific behavior can still change bytes even when the store path name matches the input hash. Nix’s model is reproducible *enough* for substitution and rollback: if inputs match, you get the same store object identity; producing identical NAR bytes everywhere is a separate packaging concern—see [Reproducible builds audit](../14-security-and-trust/reproducible-builds-audit.md).

## Examples

**Same inputs, same store path.** Two machines build the same derivation with the same pinned nixpkgs and sources. Both realize the same `/nix/store/<hash>-…` path—not because they share `/usr`, but because the derivation and its closure are identical.

**Undeclared impurity breaks reproducibility.** A builder script reads `/etc/ssl/certs` or relies on `$HTTP_PROXY` without going through a FOD / `impureEnvVars`. One machine succeeds; another fails or produces a different result. Sandboxing surfaces this by failing closed when the host path is invisible.

**FOD pins upstream content.** A fixed-output derivation declares the expected digest before the builder runs (attributes from the Nix manual; a real fetch also needs `name`, `system`, `builder`, and a downloader—use nixpkgs `fetchurl` rather than inventing one):

```nix
# Marks the derivation as fixed-output. Needs network to realize;
# mismatch against upstream bytes fails the build.
{
  outputHashMode = "flat";
  outputHashAlgo = "sha256";
  outputHash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
}
```

If upstream changes the artifact, the build fails until `outputHash` is updated—the network was used, but the *output* remains fixed.

## References

- [Nix manual — derivations](https://nix.dev/manual/nix/stable/language/derivations.html) — declared inputs and builder environment
- [Nix manual — advanced attributes](https://nix.dev/manual/nix/stable/language/advanced-attributes.html) — `outputHash*` / FOD vs input-addressed kinds
- [Nix manual — `sandbox` setting](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-sandbox) — hermetic build isolation
- [Nix manual — `pure-eval` setting](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-pure-eval) — eval-phase purity
- E. Dolstra, *The Purely Functional Software Deployment Model* ([PhD thesis PDF](https://edolstra.github.io/pubs/phd-thesis.pdf)) — historical design rationale; background only, not a normative spec for current Nix

## See also

- [Hermetic builds](hermetic-builds.md) — sandboxes and fixed inputs as mechanism
- [Why Nix](why-nix.md) — design motivation
- [Derivation](../02-concepts/derivation.md) — the unit of build description
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) — controlled network fetch
- [Pure eval and impure](../07-flakes/pure-eval-and-impure.md) — purity during evaluation
- [Store path](../02-concepts/store-path.md) — input-addressed path identity
- [Reproducible builds audit](../14-security-and-trust/reproducible-builds-audit.md) — auditing bit-identical vs repeatable builds
