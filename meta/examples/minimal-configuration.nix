# Illustrative NixOS module shape — not evaluated in this vault.
# Real hosts need ./hardware-configuration.nix (disk, boot, kernel modules).
# After editing, apply with nixos-rebuild switch (or flake equivalent).
{ config, pkgs, ... }: {
  imports = [ ./hardware-configuration.nix ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "demo";
  networking.networkmanager.enable = true;

  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };

  environment.systemPackages = with pkgs; [ git vim ];

  # Set once at install to the NixOS release you started on; do not bump casually.
  system.stateVersion = "26.05";
}
