---
status: complete
---

# Import From Derivation

## Overview

**Import from derivation** (IFD) happens when evaluation passes an expression that evaluates to a [store path](store-path.md) or [derivation](derivation.md) into a builtin that reads the filesystem. The evaluator pauses, **realises** the required store object, reads from it, then resumes. IFD therefore couples evaluation to the build store: finishing eval may require running builds first.

This is distinct from [fixed-output derivations](fixed-output-derivation.md) (FODs), which pin remote content by declared hash at build time. IFD is about reading already-defined build outputs **during** evaluation, before the full dependency graph is known.

Verified against Nix 2.34.x.

## Details

### What triggers IFD

Passing an expression that evaluates to a [store path](store-path.md) or [derivation](derivation.md) (not a literal path or hash-pinned source) to **any built-in that reads from the filesystem** constitutes IFD. Common cases include:

- `import expr`
- `builtins.readFile expr`
- `builtins.readFileType expr`
- `builtins.readDir expr`
- `builtins.pathExists expr`
- `builtins.filterSource f expr`
- `builtins.path { path = expr; }`
- `builtins.hashFile t expr`
- `builtins.scopedImport x drv`

The Nix 2.34 manual does not enumerate every triggering built-in; treat the list above as illustrative, not exhaustive.

The evaluator discovers IFD sequentially: it finds one dependency, realises it, continues, and repeats. Unlike a normal build plan, IFD realisations are not planned in parallel. Evaluations that use IFD are typically much slower than equivalent non-IFD flows.

### Control and observability

| Mechanism | Default (Nix 2.34.x) | Effect |
|-----------|----------------------|--------|
| `allow-import-from-derivation` in [nix.conf](../05-cli-and-tooling/config/nix-conf.md) | `true` | When `false`, IFD is rejected even if the store object already exists—evaluation needs no builds. |
| `--allow-import-from-derivation` / `--no-allow-import-from-derivation` | (follows config) | CLI override for a single invocation. |
| `trace-import-from-derivation` | `false` | When `true`, warn when IFD occurs; has no effect if IFD is disabled. |

Hydra and many CI setups set `allow-import-from-derivation = false` so evaluation alone cannot trigger builds. Prefer generating Nix files at commit time (for example from a schema or lockfile) over relying on IFD in shared pipelines.

### IFD vs pure flake evaluation

[Pure flake evaluation](../07-flakes/pure-eval-and-impure.md) restricts undeclared filesystem and impure builtins; it does **not** by itself disable IFD. A flake can still trigger builds during eval if IFD is allowed and the expression reads from a derivation output. Disabling IFD and using pure eval address different boundaries: IFD controls whether eval may realise derivations; pure eval controls which paths and builtins are visible during eval.

### Contrast with fixed-output derivations

FODs declare an output hash before the build runs; network fetches and similar steps produce content-addressed store paths bounded by that hash. IFD does not pin content—it reads whatever a derivation produced once that derivation is built. Both can appear in the same project, but they solve different problems: FODs for controlled external input at build time, IFD for introspecting build outputs at eval time.

## Examples

**Minimal IFD.** A derivation writes a file; evaluation reads it with `builtins.readFile`:

```nix
let
  drv = derivation {
    name = "hello";
    builder = "/bin/sh";
    args = [ "-c" "echo -n hello > $out" ];
    system = builtins.currentSystem; # impure; in flakes pass system explicitly
  };
in "${builtins.readFile drv} world"
```

With IFD allowed, realising and evaluating prints `"hello world"`:

```bash
nix-instantiate IFD.nix --eval --read-write-mode
```

Classic `--eval` without a writable store may not realise the derivation; `--read-write-mode` (or an equivalent build-capable command) is needed when the store object is not already present. For flake workflows, avoid `builtins.currentSystem`; pass `system` from the flake attribute set instead.

**CI posture.** Setting `allow-import-from-derivation = false` in Hydra or CI ensures `nix flake check` and similar eval-only jobs fail fast if an expression would need a build during evaluation, rather than silently building inside eval.

## See also

- [Derivation](derivation.md) — build recipes and realisation
- [Fixed-output derivation](fixed-output-derivation.md) — hash-pinned fetches (not IFD)
- [Pure eval and impure](../07-flakes/pure-eval-and-impure.md) — flake eval restrictions vs IFD
- [Debugging evaluation](../11-development/debugging-evaluation.md) — tracing eval-time failures
- [CI with Nix](../11-development/ci-with-nix.md) — pipelines and eval-only checks
- [Debugging builds](../04-store-and-build/debugging-builds.md) — when realisation fails after IFD
- [nix.conf](../05-cli-and-tooling/config/nix-conf.md) — `allow-import-from-derivation` and related options

## References

- [Nix 2.34 manual — Import From Derivation](https://nix.dev/manual/nix/2.34/language/import-from-derivation.html)
- [Nix 2.34 manual — `allow-import-from-derivation`](https://nix.dev/manual/nix/2.34/command-ref/conf-file.html#conf-allow-import-from-derivation)
- [Nix 2.34 manual — `trace-import-from-derivation`](https://nix.dev/manual/nix/2.34/command-ref/conf-file.html#conf-trace-import-from-derivation)
