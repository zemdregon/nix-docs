# Illustrative NixOS fragment — nftables backend + firewall holes.
# Not evaluated in this vault. Adjust interface names and ports for your host.
{
  networking.nftables.enable = true;

  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 443 ];
    allowedUDPPorts = [ 51820 ];
    extraInputRules = ''
      ip saddr 192.168.1.0/24 tcp dport 9100 accept
    '';
  };
}
