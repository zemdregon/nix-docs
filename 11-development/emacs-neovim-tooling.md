---
status: complete
---

# Emacs and Neovim tooling

## Overview

Emacs and Neovim can be managed at three common levels in a Nix setup: **Home Manager program modules** (declarative editor + plugins in home config), **Nixvim** (Neovim config as Nix modules, often imported into Home Manager), and **pure nixpkgs wrappers** (`emacsWithPackages`, `wrapNeovim`) for package-level installs without full dotfile management.

This page covers **integration patterns**—where each approach fits and how options compose—not init.el/init.lua tutorials or exhaustive plugin catalogs.

## Details

### Home Manager `programs.emacs`

The [Home Manager Emacs module](https://github.com/nix-community/home-manager/blob/master/modules/programs/emacs.nix) builds an Emacs with selected packages and optional init snippets:

| Option | Role |
|--------|------|
| `enable` | Turn on the module and install the wrapped Emacs |
| `package` | Base Emacs derivation (default from nixpkgs) |
| `extraPackages` | `epkgs: [ … ]` — packages from the Emacs package set |
| `extraConfig` | Elisp written to **`default.el`** inside the wrapped Emacs (not `~/.emacs.d`), so it is less likely to fight Spacemacs/Doom-style frameworks |
| `overrides` | Adjust individual `emacsPackages` derivations |
| `finalPackage` | Read-only: the built `emacsWithPackages` result |

For daemon / socket activation / `defaultEditor`, see [`services.emacs`](https://nix-community.github.io/home-manager/options.xhtml#opt-services.emacs.enable) — optional; only needed when you want a long-lived Emacs server or system-wide default editor integration.

### Home Manager `programs.neovim`

The [Neovim module](https://github.com/nix-community/home-manager/blob/master/modules/programs/neovim/default.nix) wraps Neovim with plugins and generated init files:

| Option | Role |
|--------|------|
| `enable` | Install configured Neovim |
| `package` | Base derivation (default `pkgs.neovim-unwrapped`; HM’s wrapper adds plugins) |
| `plugins` | List of `{ plugin, config?, optional?, type? }` entries |
| `initLua` | Lua for `$XDG_CONFIG_HOME/nvim/init.lua`; supports `lib.mkOrder` / `mkBefore` / `mkAfter` (alias: **`extraLuaConfig`**) |
| `extraConfig` | Vimscript passed to the Neovim wrapper (legacy or small snippets; separate from `initLua`) |

Plugin `config` strings are merged into the generated init. Default `type` is **lua** when `home.stateVersion >= 26.05`, else **viml**. Heavy logic may be clearer in Nixvim or a separate file via `xdg.configFile`.

### Nixvim

[Nixvim](https://nix-community.github.io/nixvim) treats Neovim configuration as **Nix modules** under `programs.nixvim`: options generate Lua, plugins are typically `plugins.<name>.enable` plus `settings`, and the flake can be consumed standalone or as a Home Manager import. Use Nixvim when you want module composition, shared flakes, and typed plugin options beyond HM’s flat `plugins` list. The upstream site is the source of truth for option names—this wiki does not duplicate that manual.

### nixpkgs-only wrappers

Without Home Manager, nixpkgs still provides:

- **`emacsPackages` / `emacsWithPackages`** — Emacs + ELPA/MELPA-style packages in one derivation (system profile, dev shell, or flake `packages`).
- **`vimPlugins` + `wrapNeovim`** — Neovim with a plugin list and optional `configure` Lua (see nixpkgs manual for `wrapNeovim` / `neovimUtils`).

These are **package-level** only: they do not manage `~/.config/nvim` or Emacs init files unless you add separate file options or modules.

### Choosing an approach

| Layer | Manages | Good when |
|-------|---------|-----------|
| HM `programs.emacs` / `programs.neovim` | Editor binary + HM-generated init | Dotfiles in Home Manager; moderate plugin lists |
| Nixvim (`programs.nixvim`) | Neovim as modular Nix config | Larger Neovim setups, flake sharing, typed plugins |
| nixpkgs wrappers | Store path with bundled plugins | System packages, CI, dev shells; init elsewhere or minimal |

Prefer HM program modules when they exist ([dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md)); use Nixvim for Neovim-specific depth; use raw wrappers when the editor is just another tool on `PATH`. Language servers and formatters often live in [dev shells](shells-and-direnv.md) or [language toolchains](language-toolchains.md) rather than inside editor config.

## Examples

**Home Manager — Emacs with packages and a short init snippet:**

```nix
{
  programs.emacs = {
    enable = true;
    extraPackages = epkgs: [
      epkgs.magit
      epkgs.use-package
    ];
    extraConfig = ''
      (require 'magit)
      (global-set-key (kbd "C-x g") 'magit-status)
    '';
  };
}
```

**Home Manager — Neovim with plugins and `initLua`:**

```nix
{
  programs.neovim = {
    enable = true;
    package = pkgs.neovim-unwrapped;
    plugins = with pkgs.vimPlugins; [
      { plugin = nvim-treesitter; }
      { plugin = telescope-nvim; config = "require('telescope').setup({})"; }
    ];
    initLua = ''
      vim.opt.number = true
      vim.g.mapleader = " "
    '';
  };
}
```

Nixvim is typically a separate flake input with `programs.nixvim.enable = true` and `imports = [ … ]`; see the [Nixvim documentation](https://nix-community.github.io/nixvim) for module shape and Home Manager integration.

## References

- [Home Manager — `programs.emacs.enable`](https://nix-community.github.io/home-manager/options.xhtml#opt-programs.emacs.enable)
- [Home Manager — `programs.neovim.enable`](https://nix-community.github.io/home-manager/options.xhtml#opt-programs.neovim.enable)
- [Home Manager — `services.emacs`](https://nix-community.github.io/home-manager/options.xhtml#opt-services.emacs.enable)
- [Home Manager Emacs module (source)](https://github.com/nix-community/home-manager/blob/master/modules/programs/emacs.nix)
- [Home Manager Neovim module (source)](https://github.com/nix-community/home-manager/blob/master/modules/programs/neovim/default.nix)
- [Nixvim](https://nix-community.github.io/nixvim)

## See also

- [Home Manager dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md)
- [Standalone vs NixOS module](../10-home-and-user/home-manager/standalone-vs-nixos-module.md)
- [Writing HM modules](../10-home-and-user/home-manager/writing-hm-modules.md)
- [Shells and direnv](shells-and-direnv.md)
- [Language toolchains](language-toolchains.md)
