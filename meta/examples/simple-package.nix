# Illustrative callPackage recipe — not evaluated in this vault.
# Use: pkgs.callPackage ./simple-package.nix { }
# No upstream fetch — wraps pkgs.hello to show dependency wiring without fake hashes.
{ lib, stdenv, hello }:
stdenv.mkDerivation {
  pname = "hello-wrapper";
  version = "0.1";

  dontUnpack = true;
  buildInputs = [ hello ];

  installPhase = ''
    mkdir -p $out/bin
    ln -s ${hello}/bin/hello $out/bin/hello-demo
  '';

  meta = with lib; {
    description = "Illustrative wrapper around hello for callPackage teaching";
    license = licenses.mit;
    platforms = platforms.all;
  };
}
