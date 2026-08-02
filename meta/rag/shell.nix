# Local RAG / vector-search environment for nix-docs.
# Usage: nix-shell meta/rag/shell.nix
{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  packages = with pkgs; [
    (python3.withPackages (ps: with ps; [
      chromadb
      httpx
    ]))
  ];
}
