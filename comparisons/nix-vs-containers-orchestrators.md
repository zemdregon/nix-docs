---
status: complete
---

# Nix vs containers / orchestrators

## Overview

**Kubernetes**, **Nomad**, and similar tools are **orchestrators**: they schedule, place, and operate **container** workloads across many machines—replicas, rolling updates, service discovery, health checks, and cluster networking. Their unit at runtime is an OCI/Docker **image** pulled from a registry and started by a container runtime (containerd, runc, …).

**Nix** builds immutable [store paths](../02-concepts/closure.md) and can export them as OCI images via [`pkgs.dockerTools`](../11-development/containers-oci.md). That is a **build and packaging** layer, not cluster scheduling.

They solve different problems and commonly **coexist**: Nix produces a reproducible image; the orchestrator decides where and how many copies run. This is complementary to [Nix vs Docker](nix-vs-docker.md), which contrasts closure vs layer packaging. It is **not** the same as NixOS [declarative containers](../09-nixos/services/declarative-containers.md) or [nspawn](../09-nixos/services/containers-and-nspawn.md)—those are nested NixOS guests on one host, sharing the store, not a multi-node scheduler.

## Details

**Division of labor.**

| Layer | Orchestrator (K8s, Nomad, …) | Nix |
|---|---|---|
| Primary job | Schedule and operate containers at scale | Build closures; optionally export OCI images |
| Artifact at deploy | Image reference + manifest/job spec | Store closure or image tarball from `dockerTools` |
| Sharing model | Registry layers / image digests | Store paths and layered image tarballs |
| Isolation | Pod/job boundaries, network policies, quotas | Build sandbox; image contents are a frozen rootfs |
| State | Desired replica count, rollout status | Pure derivations; image is a build output |

An orchestrator does not replace a package manager: it assumes images (or other task drivers) already exist. Nix does not replace an orchestrator: a `dockerTools` image does not give you cross-host scheduling, Services, or autoscaling by itself.

**Typical coexistence workflow.**

1. **Build** — Evaluate a Nix expression with `dockerTools.buildLayeredImage` (or `streamLayeredImage`) so the app closure becomes an Image Spec–compatible tarball ([nixpkgs manual](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-dockerTools)).
2. **Publish** — Tag and push to a registry the cluster can pull from (`docker push`, `skopeo copy`, CI, …).
3. **Schedule** — Reference `registry.example/myapp:tag` in a Kubernetes Deployment, Nomad job, or other orchestrator spec. The platform pulls the image and starts containers on chosen nodes.

Nix controls **what is inside** the image; the orchestrator controls **where and how many** run. See [Containers (OCI)](../11-development/containers-oci.md) for builders and layering trade-offs.

**NixOS containers ≠ Kubernetes.** [Declarative containers](../09-nixos/services/declarative-containers.md) (`containers.<name>`) and nspawn guests are **single-host** NixOS modules: they share the host `/nix/store`, upgrade with the host rebuild, and use `systemd-nspawn`. Kubernetes schedules **OCI images** on a **cluster** with its own control plane, CNI, and API objects (Pod, Deployment, Service, …). You might run K8s *on* NixOS, but the two models are not interchangeable.

**Nix + Kubernetes manifests (Kubenix).** [Kubenix](https://github.com/hall/kubenix) is a community project that maps Kubernetes resources into the NixOS **module system**, evaluates them, and emits JSON manifests (and optional apply tooling). It illustrates one pattern—declarative K8s objects as Nix options—not a Nix-built runtime. Treat it as a **survey reference**: active community fork lineage (from earlier kubenix efforts), flake-friendly entrypoints, and examples for Pods/Deployments; API surface and operational maturity vary by release—evaluate against your cluster version and team before adopting. It does not build container images; you still supply image strings (often from `dockerTools` + registry push).

**Nomad and others.** [Nomad](https://developer.hashicorp.com/nomad/docs) schedules container, VM, and binary workloads from job HCL. The same Nix → image → registry → job-spec split applies: Nix supplies the image artifact; Nomad places `task` groups on agents. Docker Swarm, ECS, and similar schedulers fit the same pattern at different abstraction levels.

**What each is not.** Nix is not a cluster orchestrator: exporting an image does not implement rolling updates or multi-node networking. Kubernetes is not a reproducible build system: a Dockerfile or registry tag does not give you Nix’s store-level dependency graph or bit-reproducible closures unless you built the image with Nix (or equivalent) upstream.

## Examples

**Build a layered image with Nix, then deploy via an orchestrator** (image build from the nixpkgs manual; cluster spec is illustrative):

```nix
{ dockerTools, hello }:
dockerTools.buildLayeredImage {
  name = "registry.example/hello";
  tag = "1.0";
  contents = [ hello ];
  config.Cmd = [ "/bin/hello" ];
}
```

```bash
nix-build -A helloImage
docker load -i result
docker push registry.example/hello:1.0
```

A Kubernetes Deployment (or Nomad job) then references that tag; the platform pulls and schedules containers—Nix’s job ends at the pushed image digest.

**Kubenix manifest generation** (minimal pattern from upstream docs—outputs JSON under `./result`):

```nix
{ kubenix ? import (builtins.fetchGit {
  url = "https://github.com/hall/kubenix.git";
  ref = "main";
}) }:
(kubenix.evalModules.x86_64-linux {
  module = { kubenix, ... }: {
    imports = [ kubenix.modules.k8s ];
    kubernetes.resources.pods.example.spec.containers.nginx.image =
      "registry.example/hello:1.0";
  };
}).config.kubernetes.result
```

Apply with your usual GitOps/CI path, or Kubenix’s optional CLI—separate from building the image in Nix.

## References

- [nixpkgs manual — `pkgs.dockerTools`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-dockerTools) — OCI/Docker images from Nix closures
- [Kubernetes docs — Pods](https://kubernetes.io/docs/concepts/workloads/pods/) — smallest schedulable unit; one or more containers sharing context
- [Kubernetes docs — Workloads](https://kubernetes.io/docs/concepts/workloads/) — Deployments, Jobs, and related controllers
- [HashiCorp Nomad — Documentation](https://developer.hashicorp.com/nomad/docs) — cluster scheduler for container and other task drivers
- [hall/kubenix](https://github.com/hall/kubenix) — Nix module patterns for Kubernetes manifests (community; verify fit for your cluster)

## See also

- [Nix vs Docker](nix-vs-docker.md) — closures vs layers; `dockerTools` complementarity
- [Containers (OCI)](../11-development/containers-oci.md) — `dockerTools`, nix2container, build vs NixOS containers
- [Declarative containers](../09-nixos/services/declarative-containers.md) — `containers.*` on a NixOS host (not K8s)
- [Containers and nspawn](../09-nixos/services/containers-and-nspawn.md) — imperative guests and nspawn on NixOS
