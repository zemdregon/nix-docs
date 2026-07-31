---
status: complete
---

# nix repl

## Overview

`nix repl` starts an interactive **read–eval–print loop** for Nix expressions. Type expressions at the `nix-repl>` prompt, see reduced values immediately, and bind names for later lines — useful for probing [evaluation](../../03-language/semantics/evaluation-model.md), inspecting package attributes, or trying small snippets before pasting them into a module.

The command is part of the [Nix 3 CLI](../../08-experimental-features/nix-command.md) and remains **experimental** (verified against Nix 2.34.x / stable manual); flags and REPL behavior can change between releases.

## Details

### Starting the REPL

```bash
nix repl                                    # empty scope
nix repl --file ./flake.nix                 # top-level attrs from a file
nix repl --expr '{ pkgs = import <nixpkgs> {}; }' pkgs
nix repl nixpkgs                           # flake root (needs flakes feature)
```

On startup, Nix **loads installables** (files, `--expr` values, flake refs, attribute paths) and binds their contents into the REPL’s lexical scope. The prompt reports how many top-level names were added.

| Flag | Role |
|------|------|
| `--file` / `-f` | Evaluate the file and expose its result; installables are attribute paths into that value. Reading `-` loads an expression from stdin. **Implies `--impure`.** |
| `--expr` | Same as `--file`, but the expression is given on the command line. |
| `--stdin` | Read installables from standard input; no default installable. |
| `--arg`, `--argstr`, `--arg-from-file`, `--arg-from-stdin` | Pass arguments to functions in the loaded expression (same as other eval commands). |
| `-I` / `--include` | Add lookup-path entries for `<nixpkgs>` and similar. |
| `--debugger` | Enter the evaluation debugger when an expression fails (see [debugging evaluation](../../11-development/debugging-evaluation.md)). |

Enable the unified CLI (and flakes when using flake refs) as for other Nix 3 commands:

```bash
nix --extra-experimental-features 'nix-command flakes' repl nixpkgs
```

### Pure vs impure

By default the REPL runs in **pure** mode: mutable filesystem paths and impure environment inputs are not available unless you opt in.

- **`--impure`** — allow access to mutable paths and repositories (needed for some local trees and `builtins.getEnv`-style probes).
- **`--file` / `-f`** — always implies **`--impure`**, because the file path itself is a mutable reference.

Pure sessions are closer to how Nix evaluates in CI; use `--impure` or `--file` when you deliberately need to import from the working tree or resolve `<nixpkgs>` via `NIX_PATH`.

### REPL commands

Type `:?` at the prompt to list **special commands** (exact set depends on your Nix version). Common ones (Nix 2.34):

| Command | Purpose |
|---------|---------|
| `:?` / `:help` | Help — list special commands |
| `:l` / `:load` *path* | Load a file into scope |
| `:lf` / `:load-flake` *ref* | Load a flake into scope |
| `:r` / `:reload` | Reload all files loaded so far |
| `:q` / `:quit` | Quit |
| `:b` *expr* | Build a derivation (may substitute or build) |
| `:log` *expr* | Show the build log for a derivation (often after `:b`) |
| `:e` / `:edit` *expr* | Open package or function in `$EDITOR` |
| `:p` / `:print` *expr* | Print recursively (strings unescaped) |
| `:t` *expr* | Describe the result type |

Ordinary Nix syntax still applies: assignments (`name = expr`), function application, and attribute selection work line by line. Prefer eval-only exploration before `:b` if you want to avoid builds.

### Exploring `pkgs` and `lib`

**Flake nixpkgs** — loads flake outputs; packages live under `legacyPackages.<system>`:

```text
nix-repl> legacyPackages.x86_64-linux.hello.name
"hello-2.12.2"
```

**Classic import** — one shot import puts every package name in scope (large attrset; slow to tab-complete):

```bash
nix repl --expr 'import <nixpkgs> {}'
```

```text
nix-repl> hello.pname
"hello"
nix-repl> lib.hasPrefix "hello" hello.name
true
```

For **`lib`** helpers without importing the full package set, load a smaller expression:

```bash
nix repl --expr 'let pkgs = import <nixpkgs> {}; in { inherit (pkgs) lib; }'
```

Or select from a flake: `nix repl nixpkgs#legacyPackages.x86_64-linux.lib` (attribute path as installable).

Use the REPL to try [debugging builtins](../../03-language/builtins/debugging-trace.md) (`trace`, `break`, etc.) on real values, or to walk lazy structures before committing to a `nix-instantiate --eval` one-liner.

## Examples

**Arithmetic and lists** (empty REPL; verified eval-only):

```bash
nix repl
```

```text
nix-repl> 1 + 2
3
nix-repl> map (x: x * 2) [1 2 3]
[ 2 4 6 ]
```

**Scoped attribute from `--expr`:**

```bash
nix repl --expr '{ a = { b = 3; c = 4; }; }' a
```

```text
nix-repl> b + c
7
```

**Inspect without building** (with nixpkgs in scope):

```text
nix-repl> hello.name
"hello-2.12.1"
nix-repl> builtins.typeOf hello
"set"
```

`:b` and `:log` realize a derivation when you need a store path; skip them for offline / no-substituter sessions.

**Quit:** `:q` or Ctrl-D.

## References

- [Nix manual — `nix repl`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-repl.html) — synopsis, options, and REPL examples

## See also

- [Evaluation model](../../03-language/semantics/evaluation-model.md) — values, WHNF, and laziness behind each REPL result
- [Debugging and trace](../../03-language/builtins/debugging-trace.md) — `trace`, `break`, and related builtins in expressions
- [Debugging evaluation](../../11-development/debugging-evaluation.md) — CLI debugger and failure-time inspection
- [nix-command](../../08-experimental-features/nix-command.md) — enabling the experimental Nix 3 command tree
