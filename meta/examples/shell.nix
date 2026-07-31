# Illustrative classic mkShell — not evaluated in this vault.
# Enter with: nix-shell
# With direnv + nix-direnv: echo 'use nix' > .envrc && direnv allow
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = [ pkgs.hello pkgs.git ];
  shellHook = ''
    echo "entered classic mkShell"
  '';
}
