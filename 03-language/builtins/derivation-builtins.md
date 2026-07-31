---
status: complete
---

# Derivation Builtins

## Overview

`derivation` is the language primitive that turns an attribute set of build inputs into a [derivation](../../02-concepts/derivation.md) value and registers a store `.drv`. Almost all packaging goes through higher-level wrappers (`stdenv.mkDerivation` and friends); those wrappers still bottom out here.

Related builtins deal with **placeholders**, **string context** (how store references ride inside strings), **`toFile`** (inline builder scripts in the store), and a few experimental ops for dynamic/content-addressed outputs. Conceptual background lives in [02-concepts](../../02-concepts/README.md); store layout and sandboxes in [04-store-and-build](../../04-store-and-build/README.md).

## Details

### `derivation` / `derivationStrict`

`derivation attrs` requires at least:

| Attribute | Meaning |
|-----------|---------|
| `name` | Symbolic name (appears in store path basenames) |
| `system` | Platform the builder must run on (e.g. `"x86_64-linux"`) |
| `builder` | Executable path or store path of the builder |

Optional:

- `args` — argv list for the builder (default `[]`)
- `outputs` — named outputs (default `[ "out" ]`); first name is the default output selected when using the derivation value as a path-like
- every other attribute — passed to the builder as an environment variable after coercion (strings unchanged; paths copied to the store; nested derivations realized first; lists joined with spaces; `true` → `"1"`; `false`/`null` → `""`)

The result is an attribute set representing the derivation; evaluation has the side effect of writing the `.drv`. Select a non-default output with `drv.dev`, etc.

`derivationStrict` is also a global. Prefer documenting `derivation` unless you are working on evaluator internals; wrappers in nixpkgs call these primitives for you.

### Placeholders and multi-output wiring

`placeholder output` returns an **output placeholder** string for a named output (`"out"`, `"bin"`, `"dev"`, …). At build time the builder substitutes the real store path. Use this when you must refer to an output path before the derivation is fully constructed (unusual outside low-level packaging).

### String context

Strings that interpolate derivations or store paths carry a **context**: provenance of which `.drv` / outputs they depend on. Without context, Nix cannot schedule builds or GC correctly.

| Builtin | Role |
|---------|------|
| `getContext s` | Attrset of drv paths → involved outputs |
| `hasContext s` | Whether context is non-empty |
| `unsafeDiscardStringContext s` | Drop context (unsafe — loses dependency tracking) |
| `unsafeDiscardOutputDependency s` | Downgrade “derivation deep” context to constant |
| `addDrvOutputDependencies s` | Opposite: deepen a single constant `.drv` context element |

Prefer keeping context intact. Discard helpers exist for rare packaging tricks and are unsafe by name for a reason.

### Writing files into the store at eval time

`toFile name s` stores string `s` as a store object with suffix `name` and returns its path. Useful for inline builders or small config files. Interpolating another `toFile` result into `s` creates a dependency between the files; **mutual** references are forbidden (hash cycle). You cannot reference a normal derivation output from `toFile` — use nixpkgs helpers such as `writeTextFile` instead.

`toXML` / `toJSON` serialize Nix values for builders (structured config rather than space-joined env vars).

### System / version introspection

| Builtin | Notes |
|---------|------|
| `currentSystem` | `eval-system` or `system` from config; **not** in pure eval |
| `currentTime` | Unix time at first force; frozen afterward; impure |
| `nixVersion` / `langVersion` | Evaluator / language version |
| `parseDrvName` / `compareVersions` | Name-version splitting and comparison |

Setting `system = builtins.currentSystem` makes a low-level derivation target the evaluating host; cross builds set `system` explicitly.

### Experimental: `outputOf`

With `dynamic-derivations`, `builtins.outputOf drvRef outputName` returns a concrete output path or an input placeholder when the path is not yet statically known. Corresponds to deriving-path / `^` installable syntax on the CLI. Version-stamp and treat as unstable.

## Examples

```nix
# Minimal derivation (illustrative — prefer stdenv.mkDerivation in real packages).
# Eval registers a .drv; this does not run the builder.
derivation {
  name = "hello-file";
  system = "x86_64-linux";
  builder = "/bin/sh";
  args = [ "-c" "echo hello > $out" ];
}

# Inline builder via toFile (eval-only; no network)
let
  builder = builtins.toFile "builder.sh" ''
    echo "hi" > "$out"
  '';
in derivation {
  name = "hi";
  system = "x86_64-linux";
  inherit builder;
}

# Inspect context from interpolating a derivation
builtins.getContext "${derivation {
  name = "a";
  builder = "b";
  system = "c";
}}"
# => { "/nix/store/…-a.drv" = { outputs = [ "out" ]; }; }
```

## References

- [Nix language — Derivations](https://nix.dev/manual/nix/stable/language/derivations.html) — required/optional attributes and coercion rules
- [Nix language — Built-ins](https://nix.dev/manual/nix/stable/language/builtins.html) — `placeholder`, context helpers, `toFile`, `outputOf`

## See also

- [Derivation](../../02-concepts/derivation.md)
- [Fixed-output derivation](../../02-concepts/fixed-output-derivation.md)
- [Store path](../../02-concepts/store-path.md)
- [Import and fetch](import-and-fetch.md)
- [Build phases](../../04-store-and-build/build-phases.md)
