# Pure-eval fix — declare nixpkgs as a locked flake input.
# Run `nix flake lock` after copying to a real flake.nix; requires nix-command + flakes.
{
  description = "Pattern: locked nixpkgs input instead of <nixpkgs>";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { nixpkgs, ... }: {
    packages.x86_64-linux.default =
      nixpkgs.legacyPackages.x86_64-linux.hello;
  };
}
