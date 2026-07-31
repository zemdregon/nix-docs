# Illustrative NixOS module shape — not evaluated in this vault.
# Import from configuration.nix: imports = [ ./minimal-module.nix ];
{ config, lib, pkgs, ... }:

let
  cfg = config.services.example-widget;
in {
  options.services.example-widget = {
    enable = lib.mkEnableOption "example widget daemon";
  };

  config = lib.mkIf cfg.enable {
    systemd.services.example-widget = {
      wantedBy = [ "multi-user.target" ];
      serviceConfig.ExecStart = "${pkgs.coreutils}/bin/true";
    };
  };
}
