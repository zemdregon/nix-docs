---
status: complete
---

# Supply Chain

## Overview

Nix’s [hermetic builds](../01-philosophy/hermetic-builds.md) and content-addressed store shrink *some* supply-chain risk, but they do not remove trust. You still choose **what** enters the evaluation graph (flake inputs, [channels](../02-concepts/channel.md), fetchers) and **who** may hand you prebuilt store paths ([substituters](../04-store-and-build/binary-caches.md)). Lockfiles and fixed-output hashes pin *which* bytes you accept; they do not vouch for the authors of those bytes or the operators of the caches that serve them.

**Threat-model sketch (three different pins):**

| Mechanism | Pins | Attests |
|-----------|------|---------|
| **Flake lock** (`flake.lock`) | Input `rev` / `narHash` of the dependency graph | Not authors, forge integrity forever, or cache honesty |
| **FOD `outputHash`** | Fetched/built bytes for that derivation | Not safety of content or honesty of other (input-addressed) substitutes |
| **Substituter signatures** (`trusted-public-keys` / `.narinfo` `Sig:`) | That a cache operator signed an input-addressed path | Not that the operator is benign, or that locked sources are reviewed |

A friendly [machine mesh](../02-concepts/machine-mesh.md) or shared deploy hub does not shrink this TCB by itself—see [inter-machine trust](inter-machine-trust.md) (supply-chain as a sixth axis).

## Details

### Trust surfaces

Typical places trust enters a Nix project:

| Surface | What you trust |
|---------|----------------|
| **Flake inputs** | Repos, refs, and authors behind each input (and transitive inputs unless overridden with `follows`) |
| **Channels** | Channel publishers and the commit each channel currently points at |
| **Fixed-output derivations (FODs)** | That the declared hash matches intended upstream content; URL alone is not the pin |
| **Substituters** | Cache operators and their signing keys—substituted NAR contents are not re-audited as source |
| **Overlays / overrides** | Whoever wrote the overlay and that it does not swap packages under a pinned nixpkgs |
| **CI runners** (e.g. GitHub Actions) | The runner image, action versions, and any secrets/tokens injected into builds |

[Trusted users](trusted-users.md) and daemon config decide who may add substituters or change trust settings on a machine; that is orthogonal but related—misconfigured trust amplifies a bad cache or input.

### Failure modes and controls

Nix pins and signatures address *integrity* and *reproducibility*; they are not a full provenance or safety program. Map common breaks to the control that actually applies:

| Failure mode | What helps (and what does not) |
|--------------|--------------------------------|
| **Compromised or malicious flake input** (push access, tag move, replaced tarball behind a ref) | Same `flake.lock` → same graph (reproducibility). **Does not** attest authors; review `rev` / `narHash` on `nix flake update`; use `follows` to avoid silent multi-rev deps |
| **Malicious or mistaken substituter** | `require-sigs = true` (default) + keys in `trusted-public-keys` for non–content-addressed paths. **Does not** help if you disable signatures or over-trust a store |
| **Silent upstream content swap at a fetch URL** | FOD `outputHash` mismatch fails the build. **Does not** prove the content is safe—only that it matches the hash you declared |
| **Wrong or unaudited FOD hash bump** | Build succeeds if bytes match hash—even malware. Treat hash updates as a review of *what* changed, not a mechanical fix |
| **Overlay / override swaps a package** | Review overlays like dependency changes. A locked `nixpkgs` pin **does not** protect against local overrides |
| **Channel advances to an unexpected commit** | Pin a branch or commit; diff channel or lock updates like any trust event |
| **Compromised CI runner or Action** | Pin Action SHAs, minimize secrets. Locked flakes reduce pin drift **but** the runner stays in the TCB |

### Lockfiles pin, they do not attest

A [flake.lock](../07-flakes/anatomy/lockfile.md) records exact revisions and `narHash` values for inputs. Two checkouts with the same lock evaluate the same dependency graph. That is reproducibility, not provenance: you still trust the upstream authors at those revisions, and anyone who can push to those remotes (or replace artifacts behind a weak pin).

Flake lock commands require experimental `flakes` (and usually `nix-command`); interfaces may still change. `nix flake lock` creates missing lock entries without bumping existing pins. `nix flake update` (optionally with input names) refreshes selected inputs and rewrites the lock. Updating inputs—or bumping a channel—is a deliberate trust event: review the lock or channel diff (`rev` / `narHash`), not only that evaluation still succeeds. Prefer bumping one input at a time when investigating breakage or suspicious changes. Use `inputs.*.follows` when you intend a shared pin across transitive flakes so you are not silently carrying multiple revisions of the same dependency.

### Fixed-output hashes

[Fixed-output derivations](../02-concepts/fixed-output-derivation.md) are the controlled impurity for fetchers (`fetchurl`, `fetchFromGitHub`, …): the builder may use the network, must declare `outputHash` (with `outputHashAlgo` / `outputHashMode`), and Nix hashes the output and fails on mismatch. The output path depends on the declared hash and name, not on other derivation attributes—so a mirror or URL change with bit-identical content keeps the same store path.

**What FODs buy / do not buy:**

| FOD **buys** | FOD **does not buy** |
|--------------|----------------------|
| Integrity check: fetched or built output matches the declared hash | Trustworthiness or safety of the *content* (malicious bytes still build if the hash matches) |
| Protection against silent content swap at a URL (mismatch fails loudly) | Author identity, SBOM, or provenance attestation (Nix does not supply that via FODs alone) |
| Ability to change URL or mirror without changing the store path when bytes are identical | Confidence that the hash you typed was audited or came from a trusted reviewer |
| A pin on *bytes*, not on the URL string | Substituter or cache honesty for **other** (non-FOD, input-addressed) store paths |
| | Immunity to [overlays](../02-concepts/overlay.md) or overrides that replace packages downstream |
| | Vulnerability-free or policy-compliant upstream |

Supply-chain practice: treat hash updates as reviews of *what* changed, not busywork. Mirror flips that keep bit-identical content are fine; silent content swaps should fail loudly. An untrusted mirror is acceptable **if** the downloaded bytes match the declared hash—the hash is the trust boundary for that artifact, not the hostname.

### Overlays and local overrides

Overlays, `packageOverrides`, and ad-hoc `callPackage` overrides sit between pinned nixpkgs and what you actually build. A reviewed lock on `nixpkgs` does not protect you if an overlay swaps a critical package for an unreviewed expression. Keep overlays small, version-controlled, and reviewed like any other dependency change.

### Substituters and binary caches

Accepting paths from a substituter means trusting whoever signed (or otherwise authorized) those paths. With `require-sigs = true` (default), non-content-addressed substitutes need a signature from a key in `trusted-public-keys`. Configure and rotate keys carefully; see [signing and caches](signing-and-caches.md) and [binary caches](../04-store-and-build/binary-caches.md). Prefer known public caches (e.g. `cache.nixos.org`) plus project caches you control; do not add anonymous substituters from blogs without checking signatures and operators. Disabling `require-sigs` or marking a store `trusted=true` is a high-impact trust decision.

### Nixpkgs CI: OfBorg and Hydra

For consumers of nixpkgs and `cache.nixos.org`, two public CI systems matter differently:

- **OfBorg** runs pull-request checks (and optional builds when triggered by trusted reviewers). It evaluates untrusted PR code on contributor-facing builders and does **not** sign or publish to the official binary cache. Treat OfBorg results as review aid, not as a cache trust root.
- **Hydra** (`hydra.nixos.org`) is the authoritative build farm for released nixpkgs/NixOS artifacts: it builds merged commits, signs store paths, and feeds `cache.nixos.org`. Channel advancement depends on Hydra jobsets succeeding for critical sets—not on OfBorg alone.

Pinning `github:NixOS/nixpkgs/...` in a flake (or following a channel) therefore trusts both the nixpkgs commit graph and the Hydra/cache signing story for any substituted paths you download rather than rebuild.

### CI as part of the chain

Shared runners and marketplace Actions are part of the supply chain: they can inject env, rewrite checkout, or exfiltrate tokens. Pin Action SHAs where practical, minimize secrets on the runner, and treat cache push credentials as high-value. Building the same locked flake in CI as locally reduces “works on my machine / different pins” drift but does not shrink runner trust.

## Examples

**Pinning does not equal auditing.** After locking `nixpkgs`, you still run whatever packages that revision defines. Pick a release branch you intend to track (for example `nixos-unstable` or a stable `nixos-YY.MM`—verify the branch name when you pin):

```nix
# flake.nix (illustrative)
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default =
      nixpkgs.legacyPackages.x86_64-linux.hello;
  };
}
```

Commit `flake.lock`. Review bumps like a dependency update (experimental `flakes` / `nix-command`):

```bash
nix flake update nixpkgs
git diff flake.lock   # inspect rev / narHash changes
```

**FOD hash as the real pin** (illustrative `fetchurl` shape):

```nix
fetchurl {
  url = "https://example.com/release.tar.gz";
  hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
}
```

If upstream replaces the tarball, the build fails until you verify the new artifact and update `hash`. Accepting a new hash without review can pin malware just as easily as a legitimate release.

**Review overlays.** Prefer a minimal overlay over forking nixpkgs for one package—and review that overlay on every change:

```nix
final: prev: {
  # Prefer: why this override exists, and who maintains the source
  mytool = prev.mytool.overrideAttrs (old: {
    src = final.fetchFromGitHub { /* owner, repo, rev, hash */ };
  });
}
```

**Client trust for a substituter** (pair with a known public key; see [signing and caches](signing-and-caches.md)):

```ini
substituters = https://cache.nixos.org/
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=
require-sigs = true
```

## References

- [Nix reference manual — advanced attributes](https://nix.dev/manual/nix/stable/language/advanced-attributes.html) — `outputHash`, `outputHashAlgo`, `outputHashMode`, and FOD behavior
- [Nix reference manual — content-addressing derivation outputs](https://nix.dev/manual/nix/stable/store/derivation/outputs/content-address.html) — fixed-output content-addressing and fetch rationale
- [Nix reference manual — `nix flake lock`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-lock.html) — create missing lock entries without bumping pins (experimental `flakes` / `nix-command`)
- [Nix reference manual — `nix flake update`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-update.html) — refresh flake input pins
- [nix.dev — Flakes](https://nix.dev/concepts/flakes) — inputs, lockfiles, `follows`, and dependency management overview
- [Nix reference manual — Serving a Nix store via HTTP](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html) — binary caches / substituters
- [Nix reference manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `substituters`, `trusted-public-keys`, `require-sigs`, `trusted-substituters`
- [OfBorg](https://github.com/NixOS/ofborg) — nixpkgs PR check / build automation
- [Hydra (NixOS)](https://hydra.nixos.org/) — official build farm behind `cache.nixos.org`
- [Discourse — Difference between OfBorg and Hydra?](https://discourse.nixos.org/t/difference-between-ofborg-and-hydra/3235) — community clarification of roles (OfBorg vs Hydra/cache)

## See also

- [Signing and caches](signing-and-caches.md) — trusting substituted store paths
- [Trusted users](trusted-users.md) — who may change daemon trust settings
- [Binary caches](../04-store-and-build/binary-caches.md) — substituter configuration and defaults
- [Lockfile](../07-flakes/anatomy/lockfile.md) — how `flake.lock` pins inputs
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) — declared hashes on fetches
- [Machine mesh](../02-concepts/machine-mesh.md) — friendly mesh does not shrink supply-chain TCB automatically
- [Inter-machine trust](inter-machine-trust.md) — supply-chain as sixth axis
