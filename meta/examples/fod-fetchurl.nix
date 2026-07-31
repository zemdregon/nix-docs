# Illustrative fixed-output fetchurl — not evaluated in this vault.
# Hash is a placeholder; after choosing a real URL run nix-prefetch-url or copy
# the hash Nix reports on the first failed build.
{ fetchurl }:
fetchurl {
  url = "https://example.com/releases/demo-1.0.tar.gz";
  # REPLACE_ME — sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
  hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
}
