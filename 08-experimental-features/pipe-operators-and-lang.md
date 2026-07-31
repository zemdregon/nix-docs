---
status: complete
---

# Pipe Operators and Lang

## Overview

The **`pipe-operators`** experimental feature flag adds two pipe operators to the Nix language: `|>` and `<|`. They provide an alternative syntax for chaining function application—useful when a value should flow through several partial applications without nested parentheses. The flag is a **language experiment**: syntax and semantics may change until stabilisation, and evaluation fails unless you opt in explicitly.

**Version stamp:** As of the Nix **2.34.x** stable reference manual (`nix.dev/manual/nix/stable/` → 2.34; title 2.34.9), `pipe-operators` remains experimental (verified on Nix **2.34.8**: manual pipeline examples evaluate to `9` and `7`; without the flag, evaluation errors). This page covers the flag, how to enable it, and what the operators do at a high level. Full operator precedence and the rest of the language surface live in [Operators](../03-language/syntax/operators.md) and the [Nix language](../03-language/README.md) domain.

## Details

**What the flag unlocks.** With `pipe-operators` enabled, Nix accepts `|>` and `<|` in expressions. The [Nix 2.34 operators chapter](https://nix.dev/manual/nix/2.34/language/operators.html#pipe-operators) defines them as sugar for function application:

- `a |> b` is equivalent to `b a` — the left-hand value is passed as the **last** argument to the callable on the right (left-to-right pipeline; **left**-associative, precedence 15).
- `a <| b` is equivalent to `a b` — the right-hand value is passed as the **last** argument to the callable on the left (right-to-left pipeline; **right**-associative, precedence 15).

Both sit at the lowest precedence level among infix operators. Without the flag, expressions using them abort with an error that the experimental feature is disabled.

**Experimental status.** Like other flags in [experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html), `pipe-operators` is off by default. Language changes are exactly the sort of work guarded by flags: they can be reverted or altered in backwards-incompatible ways while maintainers gather feedback. Stabilisation is tracked on the [pipe-operators tracking issue](https://github.com/NixOS/nix/milestone/55); see [Tracking stabilization](tracking-stabilization.md) for the general lifecycle.

**Not covered here.** This leaf is about the `pipe-operators` flag and pipe syntax only. Other language-adjacent experimental features—such as [`fetch-tree`](fetch-tree-and-git.md) (built-in), [`fetch-closure`](https://nix.dev/manual/nix/2.34/development/experimental-features.html#xp-feature-fetch-closure), or [`parse-toml-timestamps`](https://nix.dev/manual/nix/2.34/development/experimental-features.html#xp-feature-parse-toml-timestamps) (TOML timestamp parsing in `builtins.fromTOML`)—are separate flags with their own pages or manual entries. For how flags fit together, see [Feature flags overview](feature-flags-overview.md).

## Examples

Enable the flag in `nix.conf` (Nix 2.34.x):

```ini
extra-experimental-features = pipe-operators
```

Or pass it for a single evaluation:

```bash
nix-instantiate --extra-experimental-features pipe-operators -E '1 |> builtins.add 2 |> builtins.mul 3'
```

In `nix repl` / `nix-instantiate` with the flag enabled, the manual’s pipeline examples evaluate as follows (verified Nix 2.34.8 → `9` and `7`):

```nix
# left-to-right: 1 |> add 2 |> mul 3  =>  mul 3 (add 2 1)  =>  9
1 |> builtins.add 2 |> builtins.mul 3

# right-to-left: add 1 <| mul 2 <| 3  =>  add 1 (mul 2 3)  =>  7
builtins.add 1 <| builtins.mul 2 <| 3
```

Without `pipe-operators` (Nix 2.34.8):

```text
error: experimental Nix feature 'pipe-operators' is disabled; add '--extra-experimental-features pipe-operators' to enable it
```

## References

- [Nix manual — experimental features (`pipe-operators`, 2.34)](https://nix.dev/manual/nix/2.34/development/experimental-features.html#xp-feature-pipe-operators) — version-stamped flag entry
- [Nix manual — experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — flag lifecycle and the `pipe-operators` entry
- [Nix manual — operators (pipe operators, 2.34)](https://nix.dev/manual/nix/2.34/language/operators.html#pipe-operators) — syntax, equivalence rules, precedence, and repl examples
- [pipe-operators tracking issue](https://github.com/NixOS/nix/milestone/55) — stabilisation milestone on the Nix repository

## See also

- [Operators](../03-language/syntax/operators.md) — full operator list and precedence (including pipes when enabled)
- [Nix language](../03-language/README.md) — syntax, semantics, and builtins
- [Feature flags overview](feature-flags-overview.md) — enabling experimental features
- [Tracking stabilization](tracking-stabilization.md) — path from experimental to stable
