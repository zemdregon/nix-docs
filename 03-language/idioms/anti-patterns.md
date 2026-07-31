---
status: complete
---

# Anti-Patterns

## Overview

Language-level habits that hurt readability or reproducibility. Tracked against [nix.dev best practices](https://nix.dev/guides/best-practices.html), the [Nixpkgs overlays](https://nixos.org/manual/nixpkgs/stable/#chap-overlays) chapter, and Nix builtins docs—not ops mistakes (channels, `nixos-rebuild` flags). Prefer explicit scope (`let` / `inherit`), pinned inputs, shell-safe interpolation, and deep merges only when you mean them.

## Details

### Unquoted URLs

The language still accepts bare URLs (`https://example.com`). [RFC 45](https://github.com/NixOS/rfcs/blob/master/rfcs/0045-deprecate-url-literals.md) deprecated them; always quote URL strings.

### Wide `with`

`with pkgs;` at file top (or nested `with`) dumps a huge attribute set into lexical scope. Readers cannot see where bare names come from; tools cannot resolve them without evaluating. Nested `with` makes origin ambiguous.

```nix
# avoid
with import <nixpkgs> { };
# … bare names from the whole set

# prefer
let
  pkgs = import <nixpkgs> { };
  inherit (pkgs) curl jq;
in
  # use curl, jq, or pkgs.foo
```

Small list scopes (`buildInputs = with pkgs; [ … ]`) are less bad but still surprising under [shadowing rules](../semantics/scoping-and-shadowing.md). To avoid `with` in lists: `builtins.attrValues { inherit (pkgs) curl jq; }`. Prefer [`let` / `inherit`](../syntax/let-in-and-with.md).

### `rec` overuse

`rec { … }` puts every attribute in scope of every other. Shadowing an outer name with itself (`let a = 1; in rec { a = a; }`) yields infinite recursion that is hard to debug.

```nix
# infinite recursion
let a = 1; in rec { a = a; }

# prefer
let
  a = 1;
in {
  inherit a;
  b = a + 2;
}
```

Or name the set and refer through that binding (`argset.a`). See [rec and fixed points](rec-and-fixed-points.md).

### `<nixpkgs>` / lookup paths

`<nixpkgs>` resolves via `$NIX_PATH` — host state, often a [channel](../../02-concepts/channel.md) tip that differs per machine. Fine for tiny examples; for real configs pin nixpkgs (flakes, `fetchTarball` + hash, npins, or a fixed `NIX_PATH` under VCS). See [flake](../../02-concepts/flake.md) and [purity boundaries](../semantics/purity-boundaries.md).

### Impure default Nixpkgs config

Even with a pinned path, `import nixpkgs { }` still reads host config/overlays from the filesystem by default. For reproducible imports, pass empty sets explicitly:

```nix
import nixpkgs { config = { }; overlays = [ ]; }
```

### Unpinned fetchers

`fetchTarball` / tip-of-branch URLs without a content hash can change across runs (`tarball-ttl`, caches). Pin with `sha256` (or use flake inputs). Details: [import and fetch](../builtins/import-and-fetch.md), [purity boundaries](../semantics/purity-boundaries.md).

### `src = ./.` and directory names

Copying a path literal like `./.` into the store names the store path after the parent directory. Different checkout directory names → different store paths and needless rebuilds.

```nix
# avoid
src = ./.;

# prefer
src = builtins.path { path = ./.; name = "myproject"; };
```

See [path and filesystem](../builtins/path-and-filesystem.md).

### Shallow `//` (and overlays)

Attrset update (`//`) and overlay composition **replace** nested attrsets; they do not deep-merge. `{ a = { b = 1; }; } // { a = { c = 3; }; }` drops `b`. When deep merge is intended, use `lib.recursiveUpdate` (see [lib helpers](lib-helpers.md)). Overlay return values combine the same way — see [overlays pattern](overlays-pattern.md).

```nix
# shallow — loses a.b
{ a = { b = 1; }; } // { a = { c = 3; }; }

# deep merge when that is the intent
lib.recursiveUpdate { a = { b = 1; }; } { a = { c = 3; }; }
```

### Overlay `final` vs `prev` (and infinite recursion)

Per the Nixpkgs manual: use `final` for dependencies of packages you add or override (resolve against the finished set); use `prev` for the package being replaced and for helpers such as `callPackage`. Swapping them breaks consistency across the fixed-point set and often causes `infinite recursion encountered`.

```nix
# avoid — base package via final forces the attr being defined
final: prev: {
  hello = final.hello.overrideAttrs (old: { /* … */ });
}

# prefer — replace via prev; take deps from final
final: prev: {
  hello = prev.hello.overrideAttrs (old: {
    nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ final.someTool ];
  });
  myPkg = prev.callPackage ./my-pkg.nix { inherit (final) someDep; };
}
```

Also avoid forcing `final` in a top-level `let` of the overlay body before returning attrs—that can demand the fixed point too early. See [overlays pattern](overlays-pattern.md) and [callPackage](callPackage.md).

### `pkgs.extend` / `appendOverlays` inside Nixpkgs

These recompute the Nixpkgs fixed point and are expensive. The overlays chapter says not to use them in nixpkgs itself; prefer composing overlays at import / `nixpkgs.overlays` instead.

### IFD in flakes without need

[Import from derivation](../../02-concepts/import-from-derivation.md) (IFD) realises a store path mid-evaluation (`import`, `readFile`, … on a derivation output). Slow, sequential, and often banned in CI (`allow-import-from-derivation = false`). [Pure flake eval](../../07-flakes/pure-eval-and-impure.md) does **not** disable IFD by itself.

```nix
# avoid — eval reads a built store path
let
  generated = pkgs.runCommand "gen.nix" { } ''echo '{ x = 1; }' > $out'';
in
  import generated

# prefer — commit or generate the .nix at edit time; eval only sources
import ./generated.nix
```

### Ambient / mutated `PATH`

Builders and scripts that assume host `/usr/bin` tools, or prepend host paths onto `$PATH`, smuggle impurities into “hermetic” builds. Declare tools as derivation inputs and call them by store path (or a PATH built only from those inputs).

```nix
# avoid
buildPhase = ''
  export PATH=/usr/bin:$PATH
  make
'';

# prefer
nativeBuildInputs = [ pkgs.gnumake pkgs.gcc ];
# sandbox PATH comes from inputs; or call ${pkgs.gnumake}/bin/make explicitly
```

### Unescaped store paths / strings in shell

Interpolating arbitrary strings into shell without quoting breaks on spaces and metacharacters, and can turn data into syntax. Use [`lib.escapeShellArg`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.strings.escapeShellArg) / `escapeShellArgs` (see [lib helpers](lib-helpers.md)).

```nix
# avoid
''
  install -Dm644 ${configFile} $out/etc/app.conf
  ${pkgs.curl}/bin/curl ${url}
''

# prefer
''
  install -Dm644 ${lib.escapeShellArg configFile} $out/etc/app.conf
  ${lib.getExe pkgs.curl} ${lib.escapeShellArg url}
''
```

Store paths from packages are usually alphanumeric-safe, but user-facing paths, URLs, and filenames are not—escape by default when they become shell words.

### Careless `builtins.unsafeDiscardStringContext`

Strings that interpolate derivations carry a [string context](../builtins/derivation-builtins.md) so Nix tracks runtime/build dependencies. `builtins.unsafeDiscardStringContext` drops that tracking: the text of a store path can survive while the dependency is forgotten (wrong GC roots, missing build inputs, “file not found” at build time).

```nix
# avoid — path text without dependency edge
let
  p = builtins.unsafeDiscardStringContext "${pkgs.hello}";
in
  pkgs.writeText "note" "see ${p}"

# prefer — keep context so hello stays in the closure
pkgs.writeText "note" "see ${pkgs.hello}"
```

Only discard when you deliberately need a context-free string and understand the cost; prefer constructing from literals or hashes instead of stripping a live reference. Documented as unsafe in the [Nix builtins manual](https://nix.dev/manual/nix/stable/language/builtins.html).

## Examples

**Pinned vs floating nixpkgs input**

```nix
# floating (example-only)
import <nixpkgs> { }

# pinned + empty host config (hash must match the URL)
import (builtins.fetchTarball {
  url = "https://github.com/NixOS/nixpkgs/archive/<rev>.tar.gz";
  sha256 = "…";
}) { config = { }; overlays = [ ]; }
```

**Fixed store name for local `src`**

```nix
pkgs.stdenv.mkDerivation {
  name = "foo";
  src = builtins.path { path = ./.; name = "myproject"; };
}
```

## See also

- [callPackage](callPackage.md)
- [Overlays pattern](overlays-pattern.md)
- [lib helpers](lib-helpers.md)
- [Import from derivation](../../02-concepts/import-from-derivation.md)
- [Pure eval and impure](../../07-flakes/pure-eval-and-impure.md)
- [Derivation builtins (string context)](../builtins/derivation-builtins.md)

## References

- [Best practices — nix.dev](https://nix.dev/guides/best-practices.html)
- [Towards reproducibility: pinning Nixpkgs — nix.dev](https://nix.dev/tutorials/first-steps/towards-reproducibility-pinning-nixpkgs.html)
- [Language syntax (recursive sets, with) — Nix manual](https://nix.dev/manual/nix/stable/language/syntax.html)
- [Builtins (`unsafeDiscardStringContext`, string context) — Nix manual](https://nix.dev/manual/nix/stable/language/builtins.html)
- [Import From Derivation — Nix manual](https://nix.dev/manual/nix/stable/language/import-from-derivation.html)
- [Overlays — Nixpkgs manual](https://nixos.org/manual/nixpkgs/stable/#chap-overlays)
- [`lib.strings.escapeShellArg` — Nixpkgs manual](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.strings.escapeShellArg)
- [RFC 0045 — Deprecate URL literals](https://github.com/NixOS/rfcs/blob/master/rfcs/0045-deprecate-url-literals.md)
