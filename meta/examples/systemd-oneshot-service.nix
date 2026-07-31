# Illustrative NixOS module fragment — oneshot unit via services.<name>.
# Look up exact options on search.nixos.org before production use.
{ pkgs, ... }: {
  systemd.services.demo-oneshot = {
    description = "Run a command once at activation";
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      ExecStart = "${pkgs.coreutils}/bin/touch /var/lib/demo-oneshot-ran";
    };
    wantedBy = [ "multi-user.target" ];
  };
}
