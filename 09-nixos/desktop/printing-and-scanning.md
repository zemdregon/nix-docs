---
status: complete
---

# Printing and scanning

## Overview

NixOS configures local printing through CUPS (`services.printing`) and scanner access through SANE (`hardware.sane`). Driver packages belong in printing and SANE option lists—not ad-hoc `environment.systemPackages`—so daemons find PPDs and backends on the store path. Network printers and driverless IPP devices often need Avahi (`services.avahi`) alongside CUPS; firewall holes for discovery/IPP belong in [networking](../configuration/networking.md). Declarative queue definitions use `hardware.printers`. Scanning may require extra backends, group membership, or a fresh login after backend changes.

## Details

**CUPS and drivers.** `services.printing.enable = true` starts the CUPS daemon. Add PPD/driver packages to `services.printing.drivers` so CUPS discovers models under each package’s `share/cups/model/` tree. Common examples (not exhaustive): `pkgs.cups-filters`, `pkgs.gutenprint`, `pkgs.hplip`, `pkgs.hplipWithPlugin` (unfree HP plugin), `pkgs.brlaser`, `pkgs.epson-escpr`, `pkgs.epson-escpr2`. Proprietary drivers need an allow-unfree policy in [configuration.nix](../configuration/configuration-nix.md). After enable, the CUPS web UI is at `http://localhost:631`.

**Network discovery.** Many post-2013 and Wi‑Fi printers speak IPP Everywhere (AirPrint-class). Bonjour/mDNS discovery is often enabled with:

```nix
services.avahi = {
  enable = true;
  nssmdns4 = true;
  openFirewall = true;
};
```

Adjust firewall rules if you restrict UDP 5353 or IPP ports—see [networking](../configuration/networking.md). USB-only devices may additionally need `services.ipp-usb.enable` for IPP-over-USB.

**Declarative printers.** `hardware.printers.ensurePrinters` adds queues at activation; `ensureDefaultPrinter` sets the default queue name. Both require `services.printing.enable = true` — the activation unit is only created when printing is enabled. Each entry needs at least `name`, `deviceUri`, and usually `model` (from `lpinfo -m` on a running system). Optional `ppdOptions` set PPD defaults. Model strings and URIs are device-specific.

**Scanning (SANE).** `hardware.sane.enable = true` installs SANE backends and related services. Extra backends go in `hardware.sane.extraBackends`—for example `pkgs.sane-airscan` for Apple AirScan/eSCL and Microsoft WSD driverless scanning. Fujitsu ScanSnap models may need `hardware.sane.drivers.scanSnap.enable` (unfree driver files extracted from the vendor image). NixOS also ships optional Brother modules (`hardware.sane.brscan4`, and related brscan generations) with a `netDevices` pattern for network Brother scanners; enable the matching generation when your model needs it.

**Users and groups.** Depending on the device and backend, non-root access may require membership in `scanner`, `lp`, or `lpadmin`. Check your desktop environment and `scanimage -L` / `lpstat -p` as the target user; add groups via [users and groups](../configuration/users-and-groups.md). SANE reads `LD_LIBRARY_PATH` at login—log out and back in after changing backends.

## Examples

Printing with drivers and Avahi (illustrative network printer):

```nix
{ pkgs, ... }: {
  services.avahi = {
    enable = true;
    nssmdns4 = true;
    openFirewall = true;
  };

  services.printing = {
    enable = true;
    drivers = with pkgs; [
      cups-filters
      gutenprint
    ];
  };

  hardware.printers = {
    ensureDefaultPrinter = "office-laser";
    ensurePrinters = [
      {
        name = "office-laser";
        deviceUri = "ipp://192.0.2.50/ipp/print";
        model = "everywhere";
        location = "Example subnet (RFC 5737)";
      }
    ];
  };
}
```

Scanning with an extra AirScan/WSD backend:

```nix
{ pkgs, ... }: {
  hardware.sane = {
    enable = true;
    extraBackends = [ pkgs.sane-airscan ];
  };
}
```

Unfree HP printing/scan plugin (requires allow-unfree):

```nix
{ pkgs, ... }: {
  nixpkgs.config.allowUnfree = true;

  services.printing.drivers = [ pkgs.hplipWithPlugin ];
  hardware.sane.extraBackends = [ pkgs.hplipWithPlugin ];
}
```

## See also

- [configuration.nix](../configuration/configuration-nix.md)
- [Networking](../configuration/networking.md)
- [Users and groups](../configuration/users-and-groups.md)
- [Wayland and compositors](wayland-and-compositors.md)

## References

- [NixOS options — `services.printing`](https://search.nixos.org/options?query=services.printing)
- [NixOS options — `hardware.sane`](https://search.nixos.org/options?query=hardware.sane)
- [NixOS options — `hardware.printers`](https://search.nixos.org/options?query=hardware.printers)
- [NixOS Wiki — Printing](https://wiki.nixos.org/wiki/Printing) (examples and troubleshooting)
- [NixOS Wiki — Scanners](https://wiki.nixos.org/wiki/Scanners) (backends and Brother modules)
