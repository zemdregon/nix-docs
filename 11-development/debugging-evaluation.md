---
status: complete
---

# Debugging Evaluation

## Overview

**Evaluation** is when Nix turns expressions into values and derivations. Failures here happen *before* a builder runs: missing attributes, infinite recursion, type errors, module option clashes, or purity violations. **Build** failures happen *after* a `.drv` exists and the builder exits non-zero — different tools; see [Debugging builds](../04-store-and-build/debugging-builds.md).

Primary toolkit: `builtins.trace` (and friends), `--show-trace`, and `nix repl`. Language-level builtins are covered in depth in [Debugging and trace](../03-language/builtins/debugging-trace.md).

## Details

### Eval error vs build error

| Signal | Phase | First move |
|--------|-------|------------|
| Error before “building …” / no `.drv` for the failed attr | Evaluation | Re-run with `--show-trace`; probe in `nix repl` |
| “builder for … failed with exit code N” | Build | Read `nix log` / keep-failed tree — [Debugging builds](../04-store-and-build/debugging-builds.md) |
| “infinite recursion encountered” | Evaluation | Find a cycle (often `config` ↔ option, or a self-referential `let`) |
| “attribute '…' missing” | Evaluation | Wrong path, typo, or attr not yet forced into existence |
| “impure evaluation is not allowed” / forbidden builtins under flakes | Evaluation (purity) | Pin inputs, avoid `getEnv` / mutable paths, or use `--impure` only as a temporary escape |

Laziness means errors surface only when a thunk is forced — a bad attribute can hide until something selects it. See [Laziness](../03-language/semantics/laziness.md) and [Evaluation model](../03-language/semantics/evaluation-model.md).

### `builtins.trace`

`builtins.trace e1 e2` evaluates `e1`, prints its abstract syntax on **stderr** (`trace: …`), and returns `e2` unchanged. Use it to peek at values without altering the expression’s result.

Related forcing helpers (see [Debugging and trace](../03-language/builtins/debugging-trace.md)):

| Builtin | Role |
|---------|------|
| `trace` / `traceVerbose` | Print on stderr (`traceVerbose` only with `--trace-verbose`) |
| `seq` / `deepSeq` | Force WHNF / full nested evaluation so lazy errors appear now |
| `tryEval` | Shallow catch of `throw` / failed `assert` (not `abort` or most type errors) |
| `break` | Enter the debugger under `--debugger`; otherwise a no-op |

Leave `trace` out of library code you ship; it is for temporary probes. With `debugger-on-trace = true` and `--debugger`, `trace` can open an interactive session instead of only printing.

### `--show-trace`

By default Nix may **truncate** evaluation stacks and hint to re-run with `--show-trace`. The flag (and the matching `show-trace` setting in `nix.conf`) prints the full call stack: call sites, which functions ran, and which attributes were being forced.

Works with most evaluation entry points (`nix eval`, `nix build`, `nix-instantiate`, `nixos-rebuild`, …). Shallow one-line errors gain little; nested calls, modules, and `deepSeq` walks benefit most.

### `nix repl`

[`nix repl`](../05-cli-and-tooling/modern-cli/nix-repl.md) is an interactive evaluator (**experimental** `nix-command`). Load a file, flake, or `--expr`; bind names; try small expressions before pasting them into a module.

| Habit | Why |
|-------|-----|
| `:?` | List special commands (`:l`, `:r`, `:b`, `:log`, `:q`, …) |
| `--debugger` | Drop into the debugger when evaluation fails |
| `--file` / `-f` | Load a file into scope (**implies `--impure`**) |
| `--impure` | Allow mutable paths / impure builtins when diagnosing purity failures |

Prefer the REPL for “what is this attr?”; prefer `--show-trace` on the failing command for “how did evaluation get here?”; prefer `trace`/`deepSeq` when you need a probe *inside* an expression.

### Other non-interactive eval

| Tool | Role |
|------|------|
| `nix eval` | Evaluate an installable or `--expr`; fully evaluates nested attrs/lists; `--json` / `--raw` for scripting (**experimental** Nix 3 CLI) |
| `nix-instantiate` | Classic instantiate/eval; `--eval` prints the value without building |

`nix eval --json` fails if the result contains non-JSON values (functions, etc.).

### Common failure modes

**Infinite recursion.** A definition depends on itself through forced evaluation — classic in the module system when a plain `if config.…` closes a cycle. Prefer `mkIf` so conditions stay delayed. Symptom string: `infinite recursion encountered`.

**Missing attributes.** Typo’d paths (`pkgs.helol`), selecting an attr that only exists on another system or overlay, or assuming a lazy set already contains something that another branch would have added.

**Import-from-derivation (IFD) surprises.** Evaluating an expression that `import`s (or otherwise reads) a store path produced by another derivation forces a build *during* eval. That can look like a mysterious long “eval”, fail under restricted evaluators, or break purity/CI expectations. Concept deep dive: [Import from derivation](../02-concepts/import-from-derivation.md); cost/runbook: [Lazy trees and eval perf](lazy-trees-and-eval-perf.md).

**Impure eval under flakes.** Flake evaluation is pure by default: no mutable paths, no `builtins.getEnv`-style leaks, locked inputs. Failures that work with `nix-build -E 'import <nixpkgs> {}'` but fail on `nix build .#…` are often purity issues. Fix the expression; use `--impure` only to confirm the diagnosis. Note: `nix eval --expr 'import <nixpkgs> {}'` needs `--impure` (or an `-I` / flake pin) because pure mode cannot resolve `<nixpkgs>`.

### Module system and NixOS

For NixOS / Home Manager–style modules:

- Read option docs (manual / `man configuration.nix`) for types and defaults.
- Inspect a merged value: `nixos-option OPTION` (e.g. `nixos-option services.nginx.enable`).
- Explore interactively: `nixos-rebuild repl` — configuration is under `config`; `:r` reloads after edits.
- Treat **evaluation warnings** (deprecated options, `mkRenamedOptionModule` notices) as signals before they become hard errors.

Ops-oriented recovery (rollback, boot menu) lives in [Troubleshooting](../09-nixos/operations/troubleshooting.md); this page stops at making the eval error readable.

## Examples

Truncated vs full stack (`--show-trace` verified with Nix 2.34):

```bash
nix eval --expr 'let f = x: ({ a = 1; }).missing; g = y: f y; in g 0'
# error: attribute 'missing' missing  (no callers)

nix eval --show-trace --expr 'let f = x: ({ a = 1; }).missing; g = y: f y; in g 0'
# … while calling 'g' / 'f' … then the missing-attr error
```

`builtins.trace` prints on stderr and returns the second argument:

```bash
nix eval --expr 'builtins.trace "hello" 42'
# trace: hello
# 42
```

Force nested failures that laziness would hide:

```nix
# In a file or nix repl — deepSeq walks the set so `b` throws now
let e = { a = 1; b = throw "boom"; };
in builtins.deepSeq e e
```

Peek without changing the result:

```nix
builtins.trace "x = ${toString x}" x
```

JSON output for scripting (Nix 3 CLI; enable `nix-command` as needed):

```bash
nix eval --json --expr '{ x = 1; y = "hi"; }'
# {"x":1,"y":"hi"}
```

Interactive session (see [nix repl](../05-cli-and-tooling/modern-cli/nix-repl.md)):

```bash
nix repl --file ./default.nix
nix-repl> :?
nix-repl> builtins.attrNames pkgs   # or whatever was loaded
```

Classic instantiate without building:

```bash
nix-instantiate --eval -E '1 + 2'
# 3
```

## References

- [nix3-repl](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-repl.html) — interactive REPL, loading installables, `--debugger` (experimental)
- [Built-ins](https://nix.dev/manual/nix/stable/language/builtins.html) — `trace`, `deepSeq`, `seq`, `tryEval`, related helpers
- [nix3-eval](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-eval.html) — `nix eval`, `--json`, `--raw`, `--apply` (experimental)
- [nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `show-trace`, `trace-verbose`, `debugger-on-trace`

## See also

- [Debugging and trace](../03-language/builtins/debugging-trace.md)
- [Laziness](../03-language/semantics/laziness.md)
- [Evaluation model](../03-language/semantics/evaluation-model.md)
- [nix repl](../05-cli-and-tooling/modern-cli/nix-repl.md)
- [Debugging builds](../04-store-and-build/debugging-builds.md)
- [Troubleshooting (NixOS)](../09-nixos/operations/troubleshooting.md)
