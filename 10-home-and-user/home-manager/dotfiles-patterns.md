---
status: complete
---

# Dotfiles Patterns

## Overview

Home Manager manages user config in two complementary ways: **program modules** (`programs.*`, `services.*`) with structured options, and **raw file declarations** (`home.file`, `xdg.configFile`, …) that place text or store-backed sources into the home directory. Prefer modules when they exist for a tool; fall back to file options for one-off paths or apps without a module. Managed targets are usually **symlinks into the Nix store** (immutable across generations); collisions, mutable out-of-store links, and secrets need explicit handling.

## Details

### Modules vs raw files

| Approach | When to use | Trade-off |
|----------|-------------|-----------|
| `programs.git`, `programs.neovim`, … | Tool has a Home Manager module | Typed options, sensible defaults, less boilerplate |
| `xdg.configFile."…"`, `home.file."…"` | No module, or you need an exact file tree | Full control; you own format and updates |
| Mix | Module for core settings + `xdg.configFile` for extras | Common; avoid fighting the same path twice |

Prefer `xdg.configFile` for XDG config paths rather than hard-coding `home.file.".config/…"`. Check the [options search](https://nix-community.github.io/home-manager/options.xhtml) before inventing a raw file for a well-covered program.

### Mutable vs immutable

- Default: sources go through the store; activation links `~` paths to store copies. Editing the live file under `~` is wrong—change the Nix expression and switch.
- **Collisions:** activation aborts if an unmanaged file is in the way. Resolve by moving settings into config and removing the unmanaged file, or by backup / force (below).
- **Backup:** standalone `home-manager switch -b backup` (or NixOS/nix-darwin module option `home-manager.backupFileExtension`) renames colliding non-symlink paths before linking. Use sparingly as a migration aid.
- **`force = true`:** on `home.file` / `xdg.configFile` entries, skips the collision check and replaces the target. Can silently delete local changes—use only when intentional.
- **Mutable sources:** `config.lib.file.mkOutOfStoreSymlink` links to a path outside the store so the target follows live edits (useful for WIP configs; weaker reproducibility).

### Secrets

Do **not** put secrets in Nix expressions or files that land in the store—world-readable store paths leak them. Keep secrets out of the flake and use runtime files or secret tools; see [secrets management](../../14-security-and-trust/secrets-management.md), [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md), and [NixOS secret strategies](../../09-nixos/configuration/secrets-strategies.md).

### Layering

Share common home config as modules (e.g. `modules/home/git.nix`) and `imports` them from per-machine or per-user entrypoints. Keep host-specific packages and paths in the leaf config. See [writing HM modules](writing-hm-modules.md) and [standalone vs NixOS module](standalone-vs-nixos-module.md) for how those imports attach to the activation path.

## Examples

**Prefer a module** (structured options):

```nix
{
  programs.git = {
    enable = true;
    userName = "Jane Doe";
    userEmail = "jane.doe@example.org";
  };
}
```

**Raw XDG file** when there is no suitable module (or for a custom snippet):

```nix
{
  xdg.configFile."myapp/config.toml".text = ''
    theme = "dark"
  '';
}
```

**Force replace a colliding target** (after checking it is safe):

```nix
{
  xdg.configFile."example" = {
    source = ./example;
    force = true;
  };
}
```

**Shared module + per-machine import** (illustrative layout):

```nix
# machines/laptop/home.nix
{ ... }:
{
  imports = [ ../../modules/home/common.nix ];
  home.packages = [ /* host-only pkgs */ ];
}
```

## References

- [Home Manager manual](https://nix-community.github.io/home-manager/) — usage overview
- [Home Manager options](https://nix-community.github.io/home-manager/options.xhtml) — `programs.*`, `home.file`, `xdg.configFile`
- [Keeping your ~ safe from harm](https://nix-community.github.io/home-manager/index.xhtml#sec-usage-dotfiles) — collisions, `-b` / `backupFileExtension`, `force`, `mkOutOfStoreSymlink`

## See also

- [Writing HM modules](writing-hm-modules.md) — authoring and composing Home Manager modules
- [Standalone vs NixOS module](standalone-vs-nixos-module.md) — how home config is activated
- [Secrets management](../../14-security-and-trust/secrets-management.md) — keeping secrets out of the store
- [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md) — encrypted secret tooling
- [NixOS secret strategies](../../09-nixos/configuration/secrets-strategies.md) — system-level patterns that pair with HM
