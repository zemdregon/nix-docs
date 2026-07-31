---
status: complete
---

# Alejandra / nixpkgs-fmt

## Overview

Nix has no language-level layout rules (see [comments and formatting](../../03-language/syntax/comments-and-formatting.md)). Repositories pick an external formatter and usually enforce it in CI. The common choices are **Alejandra** (opinionated, “uncompromising”), the historical **nixpkgs-fmt** style tool (now archived), and **nixfmt** under the NixOS org, which [RFC 0166](https://github.com/NixOS/rfcs/blob/master/rfcs/0166-nix-formatting.md) designates as the official implementation of a standard Nix format.

The formatter landscape has shifted (nixpkgs-fmt → RFC-driven nixfmt; nixpkgs itself adopting that style). Prefer current project docs over older blog posts when choosing a tool. Do not treat “official” as meaning every repo must use nixfmt—RFC 166 defines the standard and the official *implementation*; individual flakes still select their own `formatter.<system>` output.

## Details

### The three names you will see

| Tool | Role | Notes |
|------|------|--------|
| [**nixfmt**](https://github.com/NixOS/nixfmt) | RFC 166 official formatter | Implements the standard Nix format; packaged in nixpkgs as `nixfmt` (and helpers such as `nixfmt-tree`). README: “official formatter for Nix language code” (verified 2026-07). |
| [**Alejandra**](https://github.com/kamadorueda/alejandra) | Opinionated community formatter | Different style rules from nixfmt; still widely used outside nixpkgs. |
| [**nixpkgs-fmt**](https://github.com/nix-community/nixpkgs-fmt) | Historical nixpkgs-oriented formatter | Aimed at consistency in nixpkgs with a rule-based, somewhat layout-preserving approach. **GitHub-archived**; maintainers point to nixfmt as the replacement. |

Mixing formatters in one tree produces noisy diffs. Pick **one** formatter per repository (and pin its version if CI reformats or checks).

### Wiring through `nix fmt`

Experimental [`nix fmt`](../modern-cli/nix-fmt-and-edit.md) (nix-command + flakes) does not embed a style: it builds and runs whatever derivation the flake exposes as `formatter.<system>`. That attribute is part of the [flake.nix schema](../../07-flakes/anatomy/flake-nix-schema.md); Nix forwards paths and flags after `--` to the formatter binary.

You can also invoke Alejandra, nixfmt, or other formatters directly from a shell, editor, or pre-commit hook without using `nix fmt`.

### CI and day-to-day practice

Typical patterns:

- Declare `formatter.<system>` so contributors run `nix fmt`.
- Add a check mode in CI (`nix fmt -- --check`, or the formatter’s own `--check` / equivalent) so PRs fail on unformatted Nix.
- Avoid reformatting unrelated files in the same change as logic edits.

Editor plugins and LSP setups often shell out to the same binary the flake pins, so local and CI stay aligned.

## Examples

**Flake output using nixfmt** (shape matches the Nix manual’s `nix fmt` example; package attribute names vary by nixpkgs revision—confirm locally):

```nix
# flake.nix (illustrative)
{
  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
    in {
      formatter.${system} = nixpkgs.legacyPackages.${system}.nixfmt-tree;
    };
}
```

**Alejandra as the flake formatter:**

```nix
formatter.${system} = nixpkgs.legacyPackages.${system}.alejandra;
```

**Run and check** (experimental features enabled; exact `--check` flag depends on the formatter):

```bash
nix --extra-experimental-features 'nix-command flakes' fmt
nix --extra-experimental-features 'nix-command flakes' fmt -- --check
```

**Direct invocation** (without `nix fmt`):

```bash
alejandra .
nixfmt .
```

## References

- [Nix manual — `nix fmt`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-fmt.html) — flake `formatter` integration (experimental `nix-command` + `flakes`)
- [RFC 0166 — Nix formatting](https://github.com/NixOS/rfcs/blob/master/rfcs/0166-nix-formatting.md) — standard format, Nix formatter team, official implementation requirements
- [NixOS/nixfmt](https://github.com/NixOS/nixfmt) — official formatter (per RFC 166; verified 2026-07)
- [kamadorueda/alejandra](https://github.com/kamadorueda/alejandra) — opinionated Nix formatter
- [nix-community/nixpkgs-fmt](https://github.com/nix-community/nixpkgs-fmt) — archived historical formatter (`archived: true`; points to nixfmt)

## See also

- [nix fmt and edit](../modern-cli/nix-fmt-and-edit.md) — experimental CLI entry point for flake formatters
- [Comments and formatting](../../03-language/syntax/comments-and-formatting.md) — language comment syntax vs. style tools
- [flake.nix schema](../../07-flakes/anatomy/flake-nix-schema.md) — where `formatter.<system>` lives in flake outputs
