---
status: complete
---

# Containers (OCI)

## Overview

Nix can build **OCI / Docker images** from Nix store closures—without a Docker daemon in the build. The image contents are the packages you put in plus their runtime dependencies: reproducible, self-contained, and often larger than a hand-tuned Dockerfile unless you layer or stream carefully.

This is unrelated to [NixOS declarative containers](../09-nixos/services/declarative-containers.md) and [nspawn](../09-nixos/services/containers-and-nspawn.md), which run NixOS guests on a host. Those share the host store; they do not export an OCI image.

## Details

### `pkgs.dockerTools` (nixpkgs)

[`pkgs.dockerTools`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-dockerTools) builds Docker Image Spec–compatible repository tarballs. Docker is not required during the Nix build.

| Function | Role |
|----------|------|
| `buildImage` | One layer for the added contents (optionally on a `fromImage` base). Result is a store tarball for `docker image load`. |
| `buildLayeredImage` | Multi-layer image written as a compressed tarball in the store. Implemented via `streamLayeredImage`. |
| `streamLayeredImage` | Builds a **script** that streams a multi-layer tarball to stdout—avoids storing the full image in the Nix store (better for large images). |

Layered builders put store paths into separate layers where possible, so common dependencies can be shared across images. `buildImage` is simpler but packs new content into a single layer.

Images are [closures](../02-concepts/closure.md): everything needed at runtime is copied into the image filesystem. That yields bit-reproducible content (static creation dates by default) but can bloat size and store usage if you always materialize full tarballs.

### nix2container (community)

[nix2container](https://github.com/nlewo/nix2container) is a community alternative aimed at faster rebuild/push cycles: it avoids writing layer tarballs into the Nix store and can skip already-pushed layers. Use it when `dockerTools` store/IO cost dominates your workflow; stay on `dockerTools` when you want the stock nixpkgs path with no extra flake input.

### Not the same as NixOS containers

| | OCI via `dockerTools` / nix2container | NixOS containers / nspawn |
|--|--------------------------------------|---------------------------|
| Product | Image tarball / registry push | Running guest on a NixOS host |
| Store | Closure **copied into** the image | Host store **shared** |
| Runtime | Docker, Podman, Kubernetes, … | `systemd-nspawn` / `nixos-container` |

## Examples

Minimal layered image (from the nixpkgs manual pattern):

```nix
{ dockerTools, hello }:
dockerTools.buildLayeredImage {
  name = "hello";
  tag = "latest";
  contents = [ hello ];
  config.Cmd = [ "/bin/hello" ];
}
```

Build and load:

```bash
nix-build -A helloImage   # or your package attr
docker image load -i result
docker run --rm hello:latest
```

For streaming instead of a store tarball, the derivation output **is** the script (not `…/bin/stream`):

```bash
nix-build -A helloStream
./result | docker image load
```

(`streamLayeredImage` outputs an executable store path such as `…-stream-hello`; run it and pipe to `docker image load`.)

## References

- [nixpkgs manual — `pkgs.dockerTools`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-dockerTools) — `buildImage`, `buildLayeredImage`, `streamLayeredImage`
- [nlewo/nix2container](https://github.com/nlewo/nix2container) — archive-less / efficient layering for Nix-built images

## See also

- [Containers and nspawn](../09-nixos/services/containers-and-nspawn.md) — NixOS guest containers (not OCI export)
- [Declarative containers](../09-nixos/services/declarative-containers.md) — `containers.*` on NixOS
- [Closure](../02-concepts/closure.md) — why image contents are full dependency graphs
- [Language toolchains](language-toolchains.md) — packaging apps that often end up in images
