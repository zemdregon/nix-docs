# Illustrative only — not evaluated in this vault.
# Needs experimental features: nix-command flakes.
# Adjust system / nixpkgs pin for your machine.
{
  description = "minimal packages.default and devShells.default";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      packages.${system}.default = pkgs.hello;

      devShells.${system}.default = pkgs.mkShell {
        packages = [ self.packages.${system}.default pkgs.git ];
      };
    };
}
