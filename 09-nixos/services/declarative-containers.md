---
status: complete
---

# Declarative Containers

## Overview

**Declarative containers** are nested NixOS instances declared in the host’s [configuration.nix](../configuration/configuration-nix.md) under `containers.<name>`. On [nixos-rebuild switch](../operations/rebuild-switch-boot-test.md) they are built; if already running, they update in place without a reboot. They share the host Nix store and run under systemd as `container@<name>`. Isolation is incomplete: container root can affect the host—do not give untrusted users container root.

Declarative containers upgrade with the host on every rebuild, which is often undesirable when you want independent lifecycles. For that, use imperative `nixos-container` instead (see [Containers and nspawn](containers-and-nspawn.md)).

## Details

**Declaration.** In the host config:

```nix
containers.<name> = {
  config = { config, pkgs, ... }: {
    # nested NixOS module options
  };
  # host-side options: autoStart, privateNetwork, …
};
```

The nested `config` is a full NixOS module for the container.

**Lifecycle.** `nixos-rebuild switch` builds the container. A running container is updated in place (no reboot). Set `containers.<name>.autoStart = true` to start it automatically. Start and stop manually with:

```bash
systemctl start container@database
systemctl stop container@database
```

**Networking.** By default the container shares the host network namespace: it can bind privileged ports, but it cannot change network configuration. For a private veth pair:

```nix
containers.database = {
  privateNetwork = true;
  hostAddress = "192.168.100.10";
  localAddress = "192.168.100.11";
};
```

**Removal.** Dropping the entry from `configuration.nix` and rebuilding disables the container but does **not** delete `/var/lib/nixos-containers/<name>`. Destroy the root with:

```bash
nixos-container destroy <name>
```

**Declarative vs imperative.** Declarative containers ride the host [generation](../architecture/generations-and-boot.md) and channel/flake pin. Imperative containers (`nixos-container create` / `update`) keep a separate config and update path—prefer that when the guest should not track every host rebuild.

## Examples

PostgreSQL in a declarative container (adapted from the NixOS manual):

```nix
{
  containers.database = {
    autoStart = true;
    config =
      { config, pkgs, ... }:
      {
        services.postgresql.enable = true;
      };
  };
}
```

After editing, run `nixos-rebuild switch`. The container unit is `container@database`.

## References

- [NixOS manual — Container Management](https://nixos.org/manual/nixos/stable/index.html#ch-containers) — imperative and declarative containers (stable / 26.05 as of 2026-07)

## See also

- [Containers and nspawn](containers-and-nspawn.md)
- [Service patterns](service-patterns.md)
- [configuration.nix](../configuration/configuration-nix.md)
- [Rebuild, switch, boot, and test](../operations/rebuild-switch-boot-test.md)
- [Generations and boot](../architecture/generations-and-boot.md)
