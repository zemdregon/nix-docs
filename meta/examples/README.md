---
status: index
---

# Example corpus

Tiny illustrative Nix snippets other wiki pages can cite. **Not** a second tutorial track or full project templates.

Snippets are invented minimal fixtures—not copied host configs. They are **not evaluated** in this vault. Pins such as `nixos-26.05` and `system = "x86_64-linux"` are illustrative; adjust for your machine. Flake examples need experimental [`nix-command`](../../08-experimental-features/nix-command.md) and [`flakes`](../../08-experimental-features/flakes.md) (e.g. `experimental-features = nix-command flakes` in `nix.conf`).

## Contents

- [hello-flake/flake.nix](hello-flake/flake.nix) — minimal `packages.default` + `devShells.default`
- [flake-with-checks/flake.nix](flake-with-checks/flake.nix) — hello-flake plus `checks.${system}.smoke` and a tiny `hydraJobs` leaf
- [overlay-snippet.nix](overlay-snippet.nix) — `final: prev:` overlay shape
- [shell.nix](shell.nix) — classic `mkShell` for `nix-shell` / direnv `use nix`
- [minimal-module.nix](minimal-module.nix) — tiny NixOS module with `mkEnableOption` + `lib.mkIf`
