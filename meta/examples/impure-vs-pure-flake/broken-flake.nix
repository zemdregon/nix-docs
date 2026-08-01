# Broken under flake pure eval — depends on NIX_PATH / <nixpkgs>.
# Compare with fixed-flake.nix in this directory.
{
  description = "Anti-pattern: impure import inside flake outputs";

  outputs = { ... }: {
    packages.x86_64-linux.default =
      (import <nixpkgs> { system = "x86_64-linux"; }).hello;
  };
}
