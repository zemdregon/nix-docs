# Illustrative overlay shape — not evaluated in this vault.
# Wire in via: import nixpkgs { overlays = [ (import ./overlay-snippet.nix) ]; }
# or NixOS nixpkgs.overlays. See wiki: overlay / overlays-pattern.
final: prev: {
  hello = prev.hello.overrideAttrs (old: {
    pname = old.pname + "-patched";
  });
}
