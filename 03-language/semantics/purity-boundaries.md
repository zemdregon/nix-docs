---
status: complete
---

# Purity Boundaries

## Overview

The Nix language is **pure** in the usual functional sense: values do not mutate, and a pure subexpression with the same inputs yields the same output. Evaluation is also **lazy** and **memoized** — see [evaluation model](evaluation-model.md) and [laziness](laziness.md).

That purity holds for **computation on values already in scope**. At **boundaries**, evaluation can still observe **impure** host state: the filesystem, environment variables, clock, and network. Whether those observations are allowed depends on **evaluation mode**. **Build-time** impurity is a separate layer: ordinary derivations run in a hermetic sandbox, while [fixed-output derivations](../../02-concepts/fixed-output-derivation.md) allow controlled fetches.

## Details

### Pure computation vs impure observation

Inside a Nix expression, function application, attribute selection, and arithmetic behave deterministically. There is no assignment or in-place update; sharing is by value identity once forced.

Impurity enters when built-ins or path syntax reach **outside** the expression:

| Mechanism | What it observes |
|-----------|------------------|
| `builtins.getEnv` | Process environment |
| Path literals and imports | Host filesystem (including paths copied into the store) |
| `builtins.readFile`, `readDir`, path → store | File contents or directory listings |
| `builtins.fetchurl`, `fetchGit`, `fetchTarball`, … | Network (and often local cache state) |
| `builtins.currentTime` | Wall clock |
| `builtins.nixPath` / `<nixpkgs>` lookups | `NIX_PATH` and related search paths |
| `~/…` and `~user/…` | Home directory expansion |

Path resolution, antiquotation, and tilde expansion are covered in [antiquotation and paths](../syntax/antiquotation-and-paths.md). Classic channel workflows lean on `NIX_PATH` and impure lookups; [flakes](../../02-concepts/flake.md) push toward locked, auditable inputs instead.

### Pure evaluation mode

**Pure evaluation** restricts what the evaluator may observe so that, for a fixed command line and declared inputs, the **eval result** does not depend on undeclared ambient state.

Enable it per invocation or in config:

- CLI: `nix eval --pure-eval …` (and other commands that evaluate Nix code)
- Config: `pure-eval = true` in `nix.conf` (default is `false`)

When pure evaluation is active, Nix generally:

- **Restricts** filesystem and network access to inputs pinned by cryptographic hash (or otherwise declared).
- **Empties** ambient `builtins.getEnv` results — the builtin remains, but undeclared env vars evaluate to `""`.
- **Disables** impure built-in constants: `builtins.currentSystem`, `builtins.currentTime`, `builtins.nixPath`, and `builtins.storePath` (see the `pure-eval` entry in the Nix manual).
- **Allows** file and fetch operations when the content is pinned — for example by hash on `builtins.path` / `fetchTarball`, or by an explicit commit/revision for `fetchGit`.

The goal is reproducible **evaluation**: same CLI arguments and locked inputs → same value, without surprise dependence on `$HOME`, `$NIX_PATH`, or arbitrary paths under `/`.

Flake-based workflows default toward this stricter model; flags and escape hatches are summarized in [pure eval and impure](../../07-flakes/pure-eval-and-impure.md). Philosophically, evaluation purity supports [purity and reproducibility](../../01-philosophy/purity-and-reproducibility.md); it is not the same thing as build sandboxing.

### Build-time impurity (separate concern)

**Eval purity** and **build purity** overlap in vocabulary but apply at different stages:

- **Evaluation** resolves Nix expressions to values (and optionally [derivations](../../02-concepts/derivation.md)). Pure eval limits what the evaluator can read while doing that.
- **Builds** run builder scripts inside a sandbox. Ordinary derivations are **hermetic**: no network, no undeclared host paths — see [hermetic builds](../../01-philosophy/hermetic-builds.md).

When a source truly must be downloaded at build time, a [fixed-output derivation](../../02-concepts/fixed-output-derivation.md) declares the expected output hash. The sandbox may grant network access for that step, but a mismatch fails the build instead of silently changing the closure. That is controlled impurity at **build** time, not a license for arbitrary impurity during **eval**.

## Examples

### Impure path import (default eval)

```nix
# Resolves ./config.nix on the host filesystem at eval time.
import ./config.nix
```

Under pure evaluation, importing an unrestricted relative path like this is rejected unless the path is declared in a way the mode accepts (for example, already in the store or otherwise pinned).

### Environment and time (impure by default)

```nix
{
  home = builtins.getEnv "HOME";
  now = builtins.currentTime;
}
```

With `--pure-eval`, `getEnv` returns `""` and `currentTime` is disabled; expressions must not depend on ambient host state.

### Pinned fetch vs open-ended lookup

```nix
# Pure-eval-friendly when rev and hash are fixed:
builtins.fetchGit {
  url = "https://github.com/NixOS/nixpkgs.git";
  rev = "abc123…";
  sha256 = "…";
}

# Classic impure pattern (depends on NIX_PATH / channels):
import <nixpkgs> {}
```

The first form declares exactly which Git tree enters evaluation; the second depends on how the machine’s `NIX_PATH` is configured.

## See also

- [Purity and reproducibility](../../01-philosophy/purity-and-reproducibility.md) — purity as a design goal
- [Hermetic builds](../../01-philosophy/hermetic-builds.md) — sandboxed builds
- [Fixed-output derivation](../../02-concepts/fixed-output-derivation.md) — controlled network at build time
- [Flake](../../02-concepts/flake.md) — locked inputs and flake evaluation
- [Pure eval and impure](../../07-flakes/pure-eval-and-impure.md) — flags and flake-specific rules
- [Antiquotation and paths](../syntax/antiquotation-and-paths.md) — paths, `~`, and `<…>` lookup
- [Evaluation model](evaluation-model.md) — how values are computed

## References

- [Nix language](https://nix.dev/manual/nix/stable/language/) — pure, lazy functional language
- [Nix configuration (`pure-eval`)](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-pure-eval) — pure evaluation mode settings
- [Nix 2.0 release notes (`--pure-eval`)](https://nix.dev/manual/nix/stable/release-notes/rl-2.0.html) — introduction of pure evaluation for the new CLI
