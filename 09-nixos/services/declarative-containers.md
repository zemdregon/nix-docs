---
status: complete
---

# Declarative Containers

## Overview

**Declarative containers** are nested NixOS instances declared in the host’s [configuration.nix](../configuration/configuration-nix.md) under `containers.<name>`. Each entry embeds a full NixOS module in `config`; host-side options (`autoStart`, `privateNetwork`, and others) sit alongside it. On [nixos-rebuild switch](../operations/rebuild-switch-boot-test.md) the host builds or updates the container; a running instance is refreshed in place without rebooting the guest.

Under the hood, containers are **systemd-nspawn** guests managed as `container@<name>.service`. They share the host [Nix store](../../02-concepts/store-path.md): store paths are bind-mounted into the container root rather than duplicated, so adding a service is mostly evaluation plus a new unit—not a full image copy. Isolation is incomplete: namespaces and cgroups limit ordinary processes, but root inside the container can still reach host resources the nspawn setup exposes. The NixOS manual warns against giving container root to untrusted users.

Because declarative containers ride every host rebuild, the guest tracks the host’s [generation](../architecture/generations-and-boot.md) and channel or flake pin. When the guest should have an independent lifecycle, prefer imperative `nixos-container` instead (see [Containers and nspawn](containers-and-nspawn.md)).

## Details

**Declaration.** Declaring any `containers.*` entry turns on container support (`boot.enableContainers` defaults to true when the set is non-empty). The nested `config` accepts the same options as a standalone NixOS system—services, users, firewall rules inside the guest namespace, and so on. Host-only keys on the same attribute set control how systemd runs the unit:

```nix
containers.<name> = {
  config = { config, pkgs, ... }: {
    # nested NixOS module options
  };
  # host-side: autoStart, privateNetwork, hostAddress, localAddress, …
};
```

**Lifecycle.** `nixos-rebuild switch` builds the container configuration and activates the unit. Set `autoStart = true` to start it at boot. Manual control uses standard systemd commands:

```bash
systemctl start container@database
systemctl stop container@database
```

**Networking.** By default the container shares the host network namespace. It can bind privileged ports on the host’s interfaces but cannot reconfigure networking (addresses, routes, firewall rules) from inside the guest. For an isolated veth pair, set `privateNetwork = true` and assign both ends:

```nix
containers.database = {
  privateNetwork = true;
  hostAddress = "192.168.100.10";
  localAddress = "192.168.100.11";
};
```

Traffic between host and guest uses these addresses; reach the wider network through the host as usual.

**Removal.** Removing a container from `configuration.nix` and rebuilding disables the unit but does **not** delete `/var/lib/nixos-containers/<name>` (persistent state, secrets, databases). Destroy the root explicitly:

```bash
nixos-container destroy <name>
```

**When to choose declarative.** Declarative containers suit services you want versioned with the host—same pin, same rollback story, updated on every `switch`. A database or internal daemon that should always match the host’s nixpkgs revision is a typical fit. Imperative containers keep a separate config under `/var/lib/nixos-containers/<name>` and update on `nixos-container update`, which avoids coupling the guest to each host rebuild—better when operators upgrade the host and guest on different schedules. For stronger isolation or non-NixOS guests, consider [MicroVMs](microvms.md), [libvirt and VMs](libvirt-and-vms.md), or OCI images built with Nix ([Containers (OCI)](../../11-development/containers-oci.md)); those paths do not share the host store the way nspawn containers do.

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

After editing, run `nixos-rebuild switch`. The active unit is `container@database`.

## References

- [NixOS manual — Container Management](https://nixos.org/manual/nixos/stable/index.html#ch-containers) — declarative and imperative containers (stable manual, 26.05 era)

## See also

- [Containers and nspawn](containers-and-nspawn.md)
- [MicroVMs](microvms.md)
- [libvirt and VMs](libvirt-and-vms.md)
- [Containers (OCI)](../../11-development/containers-oci.md)
- [Service patterns](service-patterns.md)
- [configuration.nix](../configuration/configuration-nix.md)
- [Rebuild, switch, boot, and test](../operations/rebuild-switch-boot-test.md)
- [Generations and boot](../architecture/generations-and-boot.md)
