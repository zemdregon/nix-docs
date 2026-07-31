---
status: complete
---

# Comments and Formatting

## Overview

Nix source is free-form text: the language defines **comment syntax** but does not prescribe layout or indentation. Comments are stripped during parsing and have no effect on evaluation. Formatting choices—indentation, line breaks, semicolon placement—are left to authors and to optional formatters in the wider ecosystem.

## Details

### Line comments

A line comment starts with `#` and runs to the end of the line. The `#` and everything after it on that line are ignored by the parser.

Line comments can appear on their own line or after an expression on the same line. They are the usual way to annotate [literals](literals.md), [lists and attribute sets](lists-and-attrsets.md), and larger expressions.

### Block comments

Block comments begin with `/*` and end at the next `*/`. They can span multiple lines.

Block comments are **not nestable**: an inner `/*` inside an open block comment is treated as ordinary text, and the first `*/` closes the comment. A second `*/` then typically causes a syntax error.

To document nested `/* … */` structure inside a block comment (for example in generated docs), escape the inner closing delimiter as `*\/` so the parser does not treat it as the end of the outer comment. Unescape in post-processing if needed.

### Formatting conventions (not language rules)

The Nix manual describes syntax, not a mandatory style guide. In practice, community and project conventions often include:

- **Indentation** — two spaces per level is common in hand-written Nix and in many upstream trees; tabs and other widths also parse.
- **Attribute sets** — attributes are typically written `name = value;` with a trailing semicolon after each binding, as in `{ x = 1; y = 2; }`.
- **Lists and nested structures** — break long `[ … ]` and `{ … }` across lines so bindings and elements stay readable; alignment is a readability choice, not a parser requirement.

These norms vary by repository. Nixpkgs, personal flakes, and generated code may look different while remaining equally valid.

### Optional formatters

Tools such as **nixfmt** and **alejandra** reformat `.nix` files according to each tool’s own rules. They are adjacent to the language: neither is built into the evaluator, and there is no single official formatter mandated by Nix itself. Use them when a project or team adopts one; flakes can expose a formatter via `formatter.<system>` and `nix fmt` (see [nix fmt and edit](../../05-cli-and-tooling/modern-cli/nix-fmt-and-edit.md)).

## Examples

```nix
# line comment on its own line
x = 42; # trailing comment after an expression

/*
  Block comment spanning
  multiple lines.
*/
{ a = 1; b = 2; }

# nested block-comment markers inside a comment (escape inner close)
/*
  Documenting: /* inner *\/ marker
  parses as one block comment; evaluates to 1 below.
*/
1
```

Soft formatting (two-space indent, semicolons in attrsets):

```nix
{
  services.nginx = {
    enable = true;
    virtualHosts."example.com" = {
      root = ./www;
    };
  };
}
```

## References

- [Nix language syntax — Comments](https://nix.dev/manual/nix/stable/language/syntax.html) — line and block comment rules, nesting limitation, escape pattern

## See also

- [Literals](literals.md) — primitive values often annotated with `#` comments
- [Lists and attribute sets](lists-and-attrsets.md) — structure most affected by formatting conventions
- [nix fmt and edit](../../05-cli-and-tooling/modern-cli/nix-fmt-and-edit.md) — flake `formatter` and `nix fmt`
- [CLI and tooling](../../05-cli-and-tooling/README.md) — optional formatters and related tooling
