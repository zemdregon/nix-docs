---
status: complete
---

# Nix vs Docker

## Overview

**Docker** packages a runnable filesystem as an **image**: stacked **layers** (each a set of filesystem changes) plus config (entrypoint, env, user). A [container](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/) is an isolated process that uses that layered tree as its root filesystem. Sharing across images happens when layer digests match in the daemon or registry.

**Nix** packages software as immutable [store paths](https://nix.dev/manual/nix/stable/store/store-path.html) under `/nix/store` (see [Nix store layout](../04-store-and-build/nix-store-layout.md)). The deployable unit is a [closure](../02-concepts/closure.md)—a store path plus every path it references at runtime—not a single layer tarball. Sharing is by store path: the same `/nix/store/<hash>-…` is reused wherever it appears.

They solve different problems. Docker isolates *runtime* (namespaces, cgroups, a rootfs). Nix isolates *builds and package graphs* (sandbox, referential integrity, content-addressed deps). They are complementary: [`pkgs.dockerTools`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-dockerTools) turns Nix closures into Docker Image Spec–compatible images; Docker itself is not used during those Nix builds. Deep dive: [Containers (OCI)](../11-development/containers-oci.md).

## Details

**Unit of packaging.**

| | Docker | Nix |
|---|---|---|
| Artifact | Image (layered rootfs + config) | Store paths; a closure is the transitive set needed to run |
| Identity | Layer/image digests (registry/daemon) | Store path digests under `/nix/store` |
| Sharing | Identical layer digests across images | Identical store paths across profiles, shells, and builds |
| Mutation | New layers on top; rebuild invalidates cache from the changed instruction down | New store paths; old paths stay until GC; no in-place overwrite |
| Isolation | Process + filesystem namespaces at run time | Build sandbox + referential integrity; not a substitute for container runtime isolation |

**Closures vs layers.** A Nix closure is a *set of store paths* computed from references. A Docker layer is a *filesystem diff* in an image history. Mapping one onto the other is a packaging choice: `dockerTools.buildImage` packs new contents (and missing deps) into **one** layer; `buildLayeredImage` / `streamLayeredImage` put distinct store paths into **separate** layers so common dependencies can be shared across images once loaded into Docker. The image still embeds a copy of those paths as a rootfs—it does not share the host `/nix/store` unless you deliberately mount it.

**Build model.** A Dockerfile is an imperative recipe (`RUN`, `COPY`, `FROM`). Each instruction becomes a layer; when a layer changes, that layer and all following layers rebuild ([Docker build cache](https://docs.docker.com/build/cache/)). A Nix derivation is a pure build of declared inputs; reproducibility comes from the store model, not from layer-cache heuristics. Imperative package managers on a base image (apt inside a Dockerfile) are closer to [Nix vs apt / pacman](nix-vs-apt-pacman.md) than to Nix itself.

**Complementary via `dockerTools`.** Use Nix to build the dependency graph; use Docker, Podman, or Kubernetes to run the resulting image. Per the nixpkgs manual, `pkgs.dockerTools` builds images according to the Docker Image Specification v1.3.1 and does not invoke Docker for those operations. Prefer `streamLayeredImage` when you want a script that streams a multi-layer tarball (avoids storing the full image in the Nix store); prefer `buildLayeredImage` when a compressed store tarball for `docker image load` is fine. This is unrelated to NixOS [declarative containers](../09-nixos/services/declarative-containers.md) / nspawn, which share the host store rather than exporting an OCI image.

**What each is not.** Nix is not a container runtime: a profile or `nix run` does not give you Docker’s network/filesystem isolation. Docker is not a package manager for the host: installing tools only inside images does not give you Nix’s side-by-side store versions, generations, or `nix copy` of closures between machines.

## Examples

**Same app, different packaging units:**

```bash
# Nix: inspect the runtime closure (store paths)
nix-store --query --requisites $(nix-build '<nixpkgs>' -A hello --no-out-link)

# Docker: inspect layers of a local image (after load/pull)
docker image history hello:latest
docker image inspect hello:latest --format '{{json .RootFS.Layers}}'
```

**Build an image from a Nix closure (`dockerTools`), then run it** (pattern from the nixpkgs manual):

```nix
{ dockerTools, hello }:
dockerTools.buildLayeredImage {
  name = "hello";
  tag = "latest";
  contents = [ hello ];
  config.Cmd = [ "/bin/hello" ];
}
```

```bash
nix-build -A helloImage   # attribute that evaluates to the expression above
docker image load -i result
docker run --rm hello:latest
```

Layered builders put each included store path in its own layer where possible so registries/daemons can reuse shared deps across images. `buildImage` is simpler but packs new content into a single layer—see the nixpkgs manual section linked below.

## References

- [nixpkgs manual — `pkgs.dockerTools`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-dockerTools) — Image Spec v1.3.1; `buildImage`, `buildLayeredImage`, `streamLayeredImage`
- [Docker docs — What is a container?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/) — isolated process + packaged filesystem
- [Docker docs — Understanding image layers](https://docs.docker.com/get-started/docker-concepts/building-images/understanding-image-layers/) — layer model and reuse
- [Docker docs — Build cache](https://docs.docker.com/build/cache/) — instruction/layer cache invalidation
- [Nix manual — Store path](https://nix.dev/manual/nix/stable/store/store-path.html) — `/nix/store/<digest>-name` identity

## See also

- [Containers (OCI)](../11-development/containers-oci.md) — Nix-built OCI/Docker images in this wiki
- [Closure](../02-concepts/closure.md) — transitive store-path unit Nix deploys
- [Nix store layout](../04-store-and-build/nix-store-layout.md) — `/nix/store/<hash>-name` on disk
- [Nix vs apt / pacman](nix-vs-apt-pacman.md) — imperative host package managers vs Nix
