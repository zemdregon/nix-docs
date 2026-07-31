---
status: complete
---

# Debugging and Trace

## Overview

Debugging builtins let you **print**, **force**, **catch shallow failures**, or **break into the debugger** during evaluation. They do not replace reading stack traces from the CLI; they add intentional probes inside expressions — useful when laziness hides which branch was forced (see [laziness](../semantics/laziness.md) and [evaluation model](../semantics/evaluation-model.md)).

Most of these belong only in temporary debugging or library assertions. Leaving `trace` noise in library code surprises downstream users.

## Details

### Printing and warnings

| Builtin | Behavior |
|---------|----------|
| `trace e1 e2` | Force-print abstract syntax of `e1` on stderr; return `e2` |
| `traceVerbose e1 e2` | Like `trace`, but only when `--trace-verbose` is set |
| `warn msg e2` | Print `msg` (must be a string) as a warning; return `e2` |

With `--debugger`, config knobs can promote these into an interactive session:

- `debugger-on-trace` — start debugger on `trace` (and similarly for warn via `debugger-on-warn`)
- `abort-on-warn` — abort after `warn` so non-interactive runs show a stack

Prefer `warn` for “this still works but please notice”; prefer `trace` for ad-hoc value dumps.

### Strictness helpers

| Builtin | Behavior |
|---------|----------|
| `seq e1 e2` | Evaluate `e1` to WHNF, then return `e2` |
| `deepSeq e1 e2` | Fully evaluate `e1` (recurse into lists/sets), then return `e2` |

Use these when you must surface errors or side effects that laziness would otherwise defer — e.g. forcing a whole attrset before returning it from a function. Overuse hurts performance and can evaluate dead branches you meant to skip.

### Errors: soft vs hard

| Builtin | Behavior |
|---------|----------|
| `throw s` | Raise an evaluation error with message `s`. Some query tools (`nix-env -qa`, etc.) **skip** derivations that `throw` |
| `abort s` | Hard abort with message `s` — **not** skipped by those query tools |
| `tryEval e` | Shallow try: `{ success = true; value = e; }` or `{ success = false; value = false; }` |

`tryEval` only catches failures from `throw` and failed `assert`. It does **not** catch `abort`, type errors from builtins, or other internal failures. It does not evaluate deeply: a set whose attributes would throw still counts as success until those attributes are forced. Pair with `deepSeq` when you need a deep attempt:

```nix
builtins.tryEval (builtins.deepSeq e e)
```

`tryEval` deliberately omits the error message (avoids smuggling non-determinism into return values). Add context with `builtins.addErrorContext`, or use a Nix unit-test harness.

### Debugger break

`break v` pauses evaluation and opens the REPL when run under `--debugger`; otherwise it returns `v` unchanged. Use around suspicious expressions instead of littering `trace`.

### Position introspection

`unsafeGetAttrPos name set` returns source position metadata for an attribute. Nixpkgs uses this to improve error messages; treat the shape as an unstable implementation detail.

## Examples

```nix
# Peek at a value without changing the result
builtins.trace "x = ${toString x}" x

# Force a whole set so nested throws surface
let e = { a = 1; b = throw "boom"; };
in builtins.tryEval (builtins.deepSeq e e)
# => { success = false; value = false; }

# Soft failure vs hard abort
builtins.tryEval (throw "skip me")  # => { success = false; value = false; }
# builtins.tryEval (abort "nope")  # still aborts

# Only when --trace-verbose
builtins.traceVerbose "detail" result
```

## References

- [Nix language — Built-ins](https://nix.dev/manual/nix/stable/language/builtins.html) — `trace`, `tryEval`, `seq`, `deepSeq`, `break`, `warn`, debugger interaction notes
- [Nix command reference](https://nix.dev/manual/nix/stable/command-ref/) — `--debugger`, `--trace-verbose`, and related flags

## See also

- [Laziness](../semantics/laziness.md)
- [Evaluation model](../semantics/evaluation-model.md)
- [Conditionals and asserts](../syntax/conditionals-and-asserts.md)
- [Attrset, list, string](attrset-list-string.md)
