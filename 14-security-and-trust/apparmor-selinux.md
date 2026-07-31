---
status: complete
---

# AppArmor and SELinux

## Overview

AppArmor and SELinux are **Mandatory Access Control (MAC)** Linux Security Modules: kernel-enforced policies that restrict what confined processes may do beyond normal Unix permissions. On NixOS they sit in a different layer from the Nix **build sandbox** ([Sandbox escape surface](sandbox-escape-surface.md)), which isolates derivations during builds—not runtime confinement of system services.

As of early 2026, the [NixOS Security wiki](https://wiki.nixos.org/wiki/Security) still lists both MAC systems under “Awaiting NixOS support”: AppArmor is **available** via NixOS options but not yet **fully integrated** end-to-end; SELinux has **no proper stock integration** and remains experimental community work. Treat MAC as complementary hardening, not a substitute for daemon trust policy ([Trusted users](trusted-users.md)) or [supply-chain](supply-chain.md) controls.

## Details

### MAC vs the Nix build sandbox

| Layer | What it confines | Typical goal |
|-------|------------------|--------------|
| **Build sandbox** (`sandbox = true`) | Builder processes during `nix build` | Hermeticity, reproducibility, catching undeclared inputs |
| **AppArmor / SELinux** | Selected runtime processes on a running system | Limit blast radius if a service is compromised |

A correctly sandboxed build does not automatically confine the resulting binary at runtime. Conversely, enabling AppArmor does not stop a [trusted user](trusted-users.md) from weakening build isolation. Use both where they apply, with separate threat models.

### AppArmor on NixOS

NixOS ships a `security.apparmor` module (see [search.nixos.org options: `security.apparmor`](https://search.nixos.org/options?query=security.apparmor)). Main knobs:

| Option | Role |
|--------|------|
| `security.apparmor.enable` | Loads AppArmor in the kernel (`apparmor=1`, `security.lsm`), installs utils, runs `apparmor.service`. **First enable on a running system requires a reboot** before the LSM is active. |
| `security.apparmor.policies.<name>` | Per-profile config: `state` (`disable` / `complain` / `enforce`), and either inline `profile` text or a `path` to a profile file. Policy names must not contain `/`. |
| `security.apparmor.packages` | Extra packages whose `etc/apparmor.d` trees are added to the parser include path (default module wiring adds `pkgs.apparmor-profiles`). |
| `security.apparmor.includes` | NixOS-generated abstraction snippets (store-path aliases, `/etc` rules) merged into `/etc/apparmor.d`. |
| `security.apparmor.enableCache` | Policy parser cache under `/var/cache/apparmor/` (store paths in policies can churn cache entries). |
| `security.apparmor.killUnconfinedConfinables` | After loading profiles, send `SIGTERM` to processes that match a loaded profile but are still **unconfined** (AppArmor only confines **new** execs of a binary). Off by default—the module documents that default favors **stability over immediately enforcing** new profiles on already-running processes. |

**Maturity (honest framing).** Module maintainers and the wiki describe usable pieces—options, systemd load/reload, Nix-specific abstractions in `includes.nix`—but also note incomplete, case-by-case profile coverage and ongoing integration work. Expect to test services in `complain` mode, read audit logs, and iterate. This is **not** “flip one switch and every NixOS service is confined like on Ubuntu.”

**Store paths and profiles.** AppArmor rules are path-based. Nix store paths change when inputs change, so profiles must reference concrete `/nix/store/…` paths or generated rules. Nixpkgs exposes `pkgs.apparmorRulesFromClosure` (from `libapparmor` passthru): given a name and a list of packages, it writes a store file of read/`mr` rules covering those packages’ closure paths—enough for **dependency access**, not full application policy (network, capabilities, `/etc`, user data still need explicit rules). Many nixpkgs packages embed policies at build time using this helper; custom NixOS policies can `include` the generated file the same way.

**Operational notes.**

- Prefer `state = "complain"` while developing a profile, then `enforce` once violations are understood.
- `aa-logprof` is wired for journal-based tuning (`journalctl -b --since today --grep audit: | aa-logprof`).
- Profiles with exact executable paths (not name-only profiles) are required for `killUnconfinedConfinables` to target the right processes—see option documentation in nixpkgs.

### SELinux on NixOS

SELinux is widely used on RHEL-family distros with filesystem labeling and distribution-maintained policy bundles. NixOS’s immutable, content-addressed `/nix/store` makes **persistent, correct SELinux labels across rebuilds and garbage collection** difficult without bespoke tooling. The [Security wiki SELinux section](https://wiki.nixos.org/wiki/Security) states that proper integration **does not exist**; attention was sparse for years, with **revived experimental community work** reported around 2025—without a committed upstream timeline.

Community threads (e.g. roadmap and hardening discussions on [NixOS Discourse](https://discourse.nixos.org/)) often note **AppArmor as the more practical MAC direction for NixOS** given existing module work and path-based profiles that align somewhat better with store layouts. Treat those as **planning signals**, not shipped product decisions.

**Practical stance:** running SELinux in enforcing mode on stock NixOS is **possible only with custom, non-upstream integration** and should be assumed **not production-ready** for typical deployments. Operators needing SELinux policy ecosystems usually run RHEL/Fedora (or containers/VMs with labeled rootfs) rather than fighting store labeling on bare NixOS.

For general host hardening that *is* supported today—kernel modules, sysctl, systemd unit hardening, firewall—see [NixOS Hardening](https://wiki.nixos.org/wiki/NixOS_Hardening) alongside this page.

## Examples

**Minimal AppArmor enable** (matches [NixOS Hardening](https://wiki.nixos.org/wiki/NixOS_Hardening); reboot after first enable):

```nix
{
  security.apparmor.enable = true;
  security.apparmor.killUnconfinedConfinables = true;
}
```

**Custom policy for a store-backed binary** (illustrative pattern from nixpkgs/Discourse—start in `complain`, add capabilities/network separately):

```nix
{ pkgs, ... }:
{
  security.apparmor.enable = true;

  security.apparmor.policies."bin.hello" = {
    state = "complain"; # switch to "enforce" after validation
    profile = ''
      ${pkgs.hello}/bin/hello {
        include "${pkgs.apparmorRulesFromClosure { name = "hello"; } [ pkgs.hello ]}"
      }
    '';
  };
}
```

`apparmorRulesFromClosure` only grants closure path access; a real service profile still needs abstractions (`include <abstractions/base>` etc.), capabilities, network rules, and non-store paths as required.

## References

- [NixOS wiki — Security (AppArmor / SELinux)](https://wiki.nixos.org/wiki/Security) — integration status as of wiki revision (~2026)
- [NixOS wiki — NixOS Hardening (AppArmor snippet)](https://wiki.nixos.org/wiki/NixOS_Hardening)
- [search.nixos.org — `security.apparmor` options](https://search.nixos.org/options?query=security.apparmor)
- [Nixpkgs `nixos/modules/security/apparmor.nix`](https://github.com/NixOS/nixpkgs/blob/nixos-unstable/nixos/modules/security/apparmor.nix) — option semantics and systemd wiring
- [Discourse — What is `pkgs.apparmorRulesFromClosure`?](https://discourse.nixos.org/t/what-is-pkgs-apparmorrulesfromclosure/39423) — closure-scoped store rules (community explanation)

## See also

- [Sandbox escape surface](sandbox-escape-surface.md) — build sandbox vs runtime MAC
- [Trusted users](trusted-users.md) — daemon trust is orthogonal to AppArmor
- [Supply chain](supply-chain.md) — MAC does not verify what you built or substituted
