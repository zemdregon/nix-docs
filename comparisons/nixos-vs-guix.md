---
status: complete
---

# NixOS vs Guix

## Overview

[Nix](https://nixos.org/) and [GNU Guix](https://guix.gnu.org/) are sibling takes on [functional package management](../01-philosophy/functional-package-management.md): builds are functions of declared inputs, outputs live in a content-addressed store, profiles switch atomically, and upgrades can roll back. Guix grew from the same *deployment model* Nix pioneered (hashed store paths, isolated builds, transparent substitutes)—then rebuilt the packaging and system layers in **Guile Scheme** instead of the **Nix language**.

“NixOS vs Guix” is really two comparisons: **Nix ↔ Guix** (package managers / ecosystems) and **NixOS ↔ Guix System** (declarative Linux distributions built on each). Neither is a drop-in replacement for the other; they share ideas more than they share tooling or communities.

## Details

### Shared model

Both stacks aim at the same failure modes described in [Why Nix](../01-philosophy/why-nix.md): mutable shared prefixes, undeclared deps, and “upgrade broke everything.” Roughly the same mechanisms show up on both sides:

| Idea | Nix / NixOS | Guix / Guix System |
|------|-------------|--------------------|
| Unit of install | Store path under `/nix/store/…` | Store path under `/gnu/store/…` |
| User view | Profile / generation pointing into the store | Per-user profile (e.g. `~/.guix-profile`) into the store |
| Upgrades | Transactional; previous generations remain | Transactional; roll back to a previous profile instance |
| Builds | Isolated; hash of inputs in the path | Isolated; hash of inputs in the path |
| Binaries | Substitutes from a cache when available | Substitutes; source or binary as available |

Guix’s Features chapter states the functional story explicitly: each store directory name encodes a hash of the inputs used to build it, supporting reproducibility and transparent source-or-binary deployment. Nix’s story is the same class of design (see Dolstra’s thesis and the NixOS site). This is a different axis from containers or imperative distro PMs—see [Nix vs Docker](nix-vs-docker.md) and [Nix vs apt / pacman](nix-vs-apt-pacman.md).

### Language: Nix vs Guile

This is the sharpest everyday difference.

- **Nix** uses a custom, lazy, purely functional language aimed at package description. Evaluation produces derivations; the language is not a general application runtime. Package sets (nixpkgs) are large attribute graphs of functions and values.
- **Guix** embeds packaging and system configuration in **GNU Guile** (Scheme). Package definitions are ordinary Scheme values (records you can inspect and transform in Guile). Build-time staged code uses Guix’s G-expression syntax. The same language surface spans CLI helpers, package modules, and Guix System services.

Learning cost differs: Nix asks you to learn a small domain language; Guix asks you to work in a full Lisp dialect (with Guix-specific forms on top). Guix gains Scheme tooling and a continuum from “package recipe” to “extend Guix itself”; Nix gains a language tailored to lazy package graphs and a larger existing package collection.

Do not treat Guix as “Nix with parentheses.” Above the shared store/daemon lineage, APIs, module layout, and service models are separate ecosystems—prefer each project’s manual over folklore.

### Distributions and communities

- **NixOS** is a Linux OS whose system configuration is written in Nix and realized as store closures (bootable generations, rollbacks). The default init is systemd.
- **Guix System** (historically also called GuixSD) is the Guix-based GNU/Linux distribution; configuration is Guile. Guix System uses the Linux-libre kernel by default and the GNU Shepherd as init. The same Guix tooling also installs *on top of* another distro as a complementary package manager—mirroring “Nix on other distros.”

Policy and governance diverge: Guix is a **GNU** project and ships a free-software distribution by design. Nix / nixpkgs are broader and more pragmatic about non-free software (typically gated by config, not the default packaging story). Package count, contributor base, and binary-cache coverage also differ in practice—nixpkgs is the larger collection; Guix emphasizes documentation, free-software coherence, and Scheme extensibility. Forums, RFCs, and release processes are independent; choose based on language preference, free-software policy, and ecosystem size—not “which one is Nix but better.”

### History sketch

Nix’s model dates to the mid-2000s research line (see [Timeline](../15-history-and-governance/timeline.md)). Guix (first public work ~2012) reused the functional store/deployment ideas and replaced the Nix expression language and packaging stack with Guile. The low-level store concepts remain recognizable; the user-facing worlds diverged.

## Examples

**Same idea, two languages** (illustrative shapes only—not a full how-to).

Nix-style package sketch (attribute set / builder pattern common in nixpkgs):

```nix
# Conceptual: name + src + build inputs → store path
{ stdenv, fetchurl }:
stdenv.mkDerivation {
  pname = "hello";
  version = "2.10";
  src = fetchurl {
    url = "mirror://gnu/hello/hello-2.10.tar.gz";
    sha256 = "…";
  };
}
```

Guix package record (fields as in the Guix manual’s GNU Hello example; omit module boilerplate):

```scheme
(define-public hello
  (package
    (name "hello")
    (version "2.10")
    (source (origin
              (method url-fetch)
              (uri (string-append "mirror://gnu/hello/hello-"
                                  version ".tar.gz"))
              (sha256
               (base32
                "0ssi1wpaf7plaswqqjwigppsg5fyh99vdlb9kzl7c9lng89ndq1i"))))
    (build-system gnu-build-system)
    (inputs (list gawk))
    (synopsis "Hello, GNU world: An example GNU package")
    (description "Guess what GNU Hello prints!")
    (home-page "https://www.gnu.org/software/hello/")
    (license gpl3+)))
```

Both describe inputs and a build; Guix’s `hello` is a first-class Scheme `<package>` record, while Nix typically composes functions over an attribute set of packages.

**Transactional profile idea** (commands differ; mechanism rhymes):

```bash
# Guix: install / roll back a user profile generation
guix package --install hello
guix package --roll-back

# Nix: install / roll back a user profile generation
nix profile add nixpkgs#hello
nix profile rollback
# Classic: nix-env -iA nixpkgs.hello / nix-env --rollback
```

Exact flags and profile paths live in each project’s manual.

## References

- [GNU Guix](https://guix.gnu.org/) — project homepage (package manager + Guix System)
- [Nix & NixOS](https://nixos.org/) — project homepage
- [Guix manual — Introduction](https://guix.gnu.org/manual/en/html_node/Introduction.html) — Guix as package manager and Guix System
- [Guix manual — Features](https://guix.gnu.org/manual/en/html_node/Features.html) — store, profiles, transactions, substitutes
- [Guix manual — Defining Packages](https://guix.gnu.org/manual/en/html_node/Defining-Packages.html) — Guile package records (Hello example)
- [Guix manual — GNU Distribution](https://guix.gnu.org/manual/en/html_node/GNU-Distribution.html) — free-software policy, Guix System
- [Nix language](https://nix.dev/manual/nix/stable/language/) — Nix expression language reference
- [Nix manual — Profiles](https://nix.dev/manual/nix/stable/package-management/profiles.html) — generations and rollback
- [Ludovic Courtès, *Functional Package Management with Guix*](https://inria.hal.science/hal-00824004) — Guix design vs Nix-style deployment (Scheme EDSLs)

## See also

- [Functional package management](../01-philosophy/functional-package-management.md) — shared conceptual model
- [Why Nix](../01-philosophy/why-nix.md) — problems the Nix stack targets
- [Timeline](../15-history-and-governance/timeline.md) — Nix / NixOS milestones
- [Nix vs Docker](nix-vs-docker.md) — runtime images vs store closures (different axis)
- [Nix vs apt / pacman](nix-vs-apt-pacman.md) — imperative distro package managers (different axis)
