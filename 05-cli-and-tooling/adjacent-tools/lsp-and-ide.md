---
status: complete
---

# LSP and IDE

## Overview

Nix editors gain diagnostics, completion, hover, and (when configured) format-on-save through **Language Server Protocol (LSP)** servers. Among actively maintained options, [**nil**](https://github.com/oxalica/nil) (incremental Rust analysis) and [**nixd**](https://github.com/nix-community/nixd) (links the Nix C++ libraries for package and module-option completion) are the usual choices. Both ship in nixpkgs and as flakes; editors attach via native LSP clients, or via the [Nix IDE](https://github.com/nix-community/vscode-nix-ide) extension on VS Code / VSCodium.

Formatting is delegated to an external binary (for example `nixfmt` or Alejandra) through each server’s `formatting.command` setting—not built into the LSP. See [Alejandra / nixpkgs-fmt](alejandra-nixpkgs-fmt.md) for formatter choice and flake `formatter` wiring.

## Details

### nil

[nil](https://github.com/oxalica/nil) focuses on incremental analysis: diagnostics, completion, go-to-definition, and related LSP features, often with little flake-specific setup. Configuration lives under the `"nil"` key in LSP `workspace/configuration` (see [nil configuration docs](https://github.com/oxalica/nil/blob/main/docs/configuration.md)).

Notable tunables include `formatting.command` (defaults to `null`), `diagnostics.ignored`, and flake-related options under `nix.flake` (for example `autoEvalInputs`, `nixpkgsInputName`). Opt-in flake input or NixOS-option evaluation can improve completion but may cost time and memory (upstream docs note multi-gigabyte peaks for large flakes).

Packaging: nixpkgs attribute `nil`; flake output `github:oxalica/nil#`. Upstream editor examples include Neovim (nvim-lspconfig), Emacs (lsp-mode, eglot), and VS Code via Nix IDE.

### nixd

[nixd](https://github.com/nix-community/nixd) evaluates Nix expressions to offer richer **package** completion (from a configured `nixpkgs.expr`) and **option** completion for module systems. It typically needs more configuration than nil for flake-based NixOS, Home Manager, nix-darwin, or flake-parts—usually Nix `expr` strings (often with `builtins.getFlake`; see [nixd configuration](https://github.com/nix-community/nixd/blob/main/nixd/docs/configuration.md)).

With no custom settings, nixd defaults suit channel / `NIX_PATH` users (`import <nixpkgs> { }`, `<nixos>` options). Flake users often set `nix.nixPath` in NixOS or extend `options` / `nixpkgs.expr` in server settings. Configuration is under the `"nixd"` key; legacy v1.x `.nixd.json` files are no longer read.

### Choosing between nil and nixd

There is no single community consensus—teams pick based on setup cost vs. completion depth.

| | **nil** | **nixd** |
|---|---------|----------|
| Setup | Often works with defaults | More config for flakes and custom option sets |
| Packages | Completion via incremental analysis | Completion from evaluated `nixpkgs.expr` |
| NixOS / HM / darwin options | Optional via `nix.flake.nixpkgsInputName` when the input exists in the workspace flake | Via `options.*.expr` (`builtins.getFlake`, flake-parts `debug.options`, etc.) |
| Formatting | `nil.formatting.command` | `nixd.formatting.command` |
| Resource use | Lower by default; optional flake eval | Option trees evaluated lazily; nixpkgs name indexing alone is on the order of 200–300 MiB per nixd docs |

Either server may fit; switch by changing `nix.serverPath` (VS Code) or the LSP server name in Neovim/Emacs.

### Formatters and the extension

LSP format requests run whatever `formatting.command` lists (stdin/stdout formatter). That should match the formatter your repo pins—see [Alejandra / nixpkgs-fmt](alejandra-nixpkgs-fmt.md).

[Nix IDE](https://github.com/nix-community/vscode-nix-ide) also supports standalone formatting via `nix.formatterPath` when LSP is off or the server has no formatter configured; when LSP is enabled, `nix.serverSettings` formatting config is used instead of `nix.formatterPath` (per extension README).

### Historical note: rnix-lsp

[rnix-lsp](https://github.com/nix-community/rnix-lsp) was an earlier Rust LSP built on rnix parsing. It is **unmaintained**; new setups should use nil or nixd instead.

## Examples

**VS Code / VSCodium** — enable LSP and pick a server (from [vscode-nix-ide README](https://github.com/nix-community/vscode-nix-ide)):

```jsonc
{
  "nix.enableLanguageServer": true,
  "nix.serverPath": "nil",
  "nix.serverSettings": {
    "nil": {
      "formatting": {
        "command": ["nixfmt"]
      }
    }
  }
}
```

Switch `"nix.serverPath"` to `"nixd"` and nest a `"nixd"` block under `"nix.serverSettings"` for `options` / `nixpkgs.expr` (see nixd configuration docs).

**Neovim** — built-in LSP with nixd (pattern from [nixd configuration](https://github.com/nix-community/nixd/blob/main/nixd/docs/configuration.md); nil is supported via nvim-lspconfig’s `nil_ls`):

```lua
vim.lsp.config("nixd", {
  cmd = { "nixd" },
  filetypes = { "nix" },
  root_markers = { "flake.nix", ".git" },
  settings = {
    nixd = {
      formatting = { command = { "nixfmt" } },
    },
  },
})
vim.lsp.enable("nixd")
```

For nil, point `cmd` at `"nil"` and nest settings under `settings.nil` (see nil configuration docs).

## References

- [oxalica/nil](https://github.com/oxalica/nil) — incremental Nix language server; editor integration and flake package
- [nil — configuration](https://github.com/oxalica/nil/blob/main/docs/configuration.md) — LSP settings under `"nil"`
- [nix-community/nixd](https://github.com/nix-community/nixd) — Nix language server with package/option completion
- [nixd — configuration](https://github.com/nix-community/nixd/blob/main/nixd/docs/configuration.md) — `nixd` settings, editor examples
- [nix-community/vscode-nix-ide](https://github.com/nix-community/vscode-nix-ide) — VS Code / VSCodium extension (`nix.enableLanguageServer`, `nix.serverPath`, `nix.serverSettings`)

## See also

- [Alejandra / nixpkgs-fmt](alejandra-nixpkgs-fmt.md) — formatters LSPs invoke via `formatting.command`
- [devenv / devshell](devenv-devshell.md) — dev shells that can supply LSP binaries on `PATH`
- [Debugging evaluation](../../11-development/debugging-evaluation.md) — when completion or diagnostics disagree with `nix repl`
- [Emacs and Neovim tooling](../../11-development/emacs-neovim-tooling.md) — Home Manager / Nixvim editor setup patterns
- [Nix language cheatsheet](../../03-language/cheatsheet.md) — syntax reference while editing
