---
status: complete
---

# Lazy Trees and Evaluation Performance

## Overview

**Evaluation performance** is how long and how much work Nix spends turning expressions into values and derivations *before* any builder runs. Common slowdowns in stock Nix come from forcing more of the language than a command needs, realising derivations during eval ([import from derivation](../02-concepts/import-from-derivation.md)), copying large flake source trees into the store, or re-evaluating unchanged flakes without benefit from the eval cache.

This page is an operator runbook for **stock Nix** (CppNix / nix.dev manual). **Lazy trees**—copying only demanded files via a virtual filesystem—are covered separately as **vendor-specific or upstream work-in-progress**, not as default upstream behavior.

Verified against the Nix **2.34.9** manual entries for `eval-cache`, `eval-profiler`, and related `nix.conf` settings.

## Details

### Laziness: force only what you need

Nix is lazy: thunks stay unevaluated until something demands them. Performance problems often come from *over-forcing*:

| Pattern | Why it hurts |
|---------|----------------|
| Selecting a whole huge attrset (`flake.outputs`, all of `config`) | Walks branches you never build |
| `builtins.deepSeq`, `lib.recursiveUpdate` on large trees | Forces nested thunks eagerly |
| Dumping every flake output (`nix flake show --all-systems` on a wide flake) | Evaluates many system keys at once |
| Module systems merging large option trees | Cost scales with option count and merge depth |

Prefer narrow selection: `nix build .#packages.x86_64-linux.myPkg` rather than evaluating unrelated outputs. When debugging, `--show-trace` and `deepSeq` are correct tools for *finding* errors, not for routine builds—see [Debugging evaluation](debugging-evaluation.md), [Laziness](../03-language/semantics/laziness.md), and [Evaluation model](../03-language/semantics/evaluation-model.md).

### Import from derivation (IFD)

[Import from derivation](../02-concepts/import-from-derivation.md) runs store realisation *during* evaluation: Nix must build (or substitute) a derivation before the outer expression can continue. IFD is inherently sequential and blocks parallel eval of the outer graph.

In CI, `allow-import-from-derivation = false` (when your flake can comply) avoids surprise realise-during-eval latency. See [CI with Nix](ci-with-nix.md) and the [IFD manual section](https://nix.dev/manual/nix/2.34/language/import-from-derivation.html).

### Flake source trees and pure eval

Git flakes copy **indexed** files from the working tree into the store for evaluation. Large monorepos pay copy and hash cost even when the expression only reads a few paths. Untracked or `.gitignore`d files are invisible under pure flake eval—see [Pure eval and impure](../07-flakes/pure-eval-and-impure.md).

Mitigations that stay within stock Nix:

- Keep flake roots small; split packages into separate flakes, or point a flake URL / input at a subdirectory (`dir=` / `?dir=`) when that fits.
- Stage or commit files the evaluator must see before building.
- Avoid importing the entire repo tree when a narrower path suffices.

### `eval-cache` (stock)

`eval-cache` in [`nix.conf`](../05-cli-and-tooling/config/nix-conf.md) defaults to **`true`**. For certain flake commands, a second invocation with the **same flake version** can skip full re-evaluation. **Intermediate** expression results are not cached—only the command-level shortcut described in the manual.

Disable for timing comparisons: `--no-eval-cache` or `eval-cache = false`. Do not assume the cache fixes slow first runs or deep IFD chains.

### Evaluation profiling (stock)

Nix **2.34** documents evaluation profiling via `nix.conf`:

| Setting | Role |
|---------|------|
| `eval-profiler` | Enables profiling; default `disabled`. Documented mode: `flamegraph` (stack sampling, output for `flamegraph.pl`). |
| `eval-profiler-frequency` | Sampling rate in hertz; default `99`. Use `0` to sample after each function call (heavier). |
| `eval-profile-file` | Output path; default `nix.profile`. |

Set them in user or system `nix.conf`, or pass matching options on the CLI (see Examples). Run the slow command once, then inspect the profile with the workflow in the manual. This is stack sampling for eval hotspots—useful when guesses about where time goes fail. Stick to documented settings and the manual’s profiler section; do not invent flags.

### Recursion limits

`max-call-depth` caps function call depth before erroring. Nix **2.34** documents the default as **10000**. Deep nesting or runaway recursion may surface as a max-call-depth error rather than a clear infinite-recursion message. See [`max-call-depth`](https://nix.dev/manual/nix/2.34/command-ref/conf-file.html#conf-max-call-depth).

### Lazy trees: vendor and upstream (not universal stock Nix)

**Lazy trees** defer copying flake source files until evaluation actually reads them, often via a virtual filesystem layer. They can reduce store churn and wall time on large repositories, but **stock CppNix 2.34 does not ship lazy trees as a stable, default feature**.

| Source | Status (soft) |
|--------|----------------|
| **Upstream** [NixOS/nix#13225](https://github.com/NixOS/nix/pull/13225) | Treat as experimental until merged and released in upstream Nix. |
| **Determinate Nix** | Ships [lazy trees](https://docs.determinate.systems/determinate-nix/lazy-trees/) (documented since Determinate Nix 3.5.2). Enable/disable via `lazy-trees` in their config or `--no-lazy-trees` on the CLI—these are **Determinate product** knobs, not portable stock `nix.conf` options. |

Determinate’s docs report large speedups and disk savings on big trees; treat such numbers as **vendor-reported**, environment-dependent, and not a guarantee for your flake.

**Practical order:** apply stock tips (narrow selection, IFD discipline, smaller flake roots, eval cache awareness, documented profiler) first. Consider lazy trees only when you run a distribution that documents them, or when upstream merges and releases equivalent behavior—then re-verify flags against that version’s manual.

## Examples

Narrow build selection (avoid evaluating unrelated flake outputs):

```bash
nix build .#packages.x86_64-linux.myPackage
```

Time a cold eval without flake eval cache:

```bash
nix build --no-eval-cache .#checks.x86_64-linux.default
```

CI-style IFD guard (when your evaluation graph allows it):

```ini
# fragment for nix.conf or NIX_CONFIG in CI
allow-import-from-derivation = false
```

Profile a slow eval with the documented `flamegraph` mode (Nix 2.34 manual — classic CLI form):

```bash
nix-instantiate '<nixpkgs>' -A hello --eval-profiler flamegraph
# Default profile file: nix.profile in cwd; then:
# flamegraph.pl nix.profile > flamegraph.svg
```

`eval-profile-file` and `eval-profiler-frequency` in [nix.conf](../05-cli-and-tooling/config/nix-conf.md) (or matching `--option` overrides) adjust output path and sample rate.

Determinate Nix only—disable lazy trees for A/B timing (not stock Nix):

```bash
nix build --no-lazy-trees .#my-package
```

## See also

- [Debugging evaluation](debugging-evaluation.md) — traces and REPL; not a performance toolkit
- [CI with Nix](ci-with-nix.md) — caching, IFD policy, runner hygiene
- [Import from derivation](../02-concepts/import-from-derivation.md) — realise-during-eval cost model
- [Pure eval and impure](../07-flakes/pure-eval-and-impure.md) — Git-visible source trees
- [Laziness](../03-language/semantics/laziness.md) — when thunks force
- [Evaluation model](../03-language/semantics/evaluation-model.md) — eval phases and values
- [nix.conf](../05-cli-and-tooling/config/nix-conf.md) — configuration merge order and flags

## References

- [Nix 2.34 manual — `eval-cache`](https://nix.dev/manual/nix/2.34/command-ref/conf-file.html#conf-eval-cache)
- [Nix 2.34 manual — `eval-profiler`](https://nix.dev/manual/nix/2.34/command-ref/conf-file.html#conf-eval-profiler)
- [Nix 2.34 manual — Using the eval-profiler](https://nix.dev/manual/nix/2.34/advanced-topics/eval-profiler.html)
- [Nix 2.34 manual — `max-call-depth`](https://nix.dev/manual/nix/2.34/command-ref/conf-file.html#conf-max-call-depth)
- [Nix 2.34 manual — Import from derivation](https://nix.dev/manual/nix/2.34/language/import-from-derivation.html)
- [NixOS/nix#13225](https://github.com/NixOS/nix/pull/13225) — lazy trees upstream PR (status may change)
- [Determinate Nix — Lazy trees](https://docs.determinate.systems/determinate-nix/lazy-trees/) — vendor documentation (Determinate Nix 3.5.2+)
