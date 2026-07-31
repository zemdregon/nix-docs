---
status: complete
---

# TPM and measured boot

## Overview

**Measured boot** seals disk unlock (typically LUKS2) to TPM Platform Configuration Register (PCR) measurements of the boot chain: the volume unlocks only when those PCRs match an enrolled policy. On NixOS with [Lanzaboote](https://github.com/nix-community/lanzaboote), the documented path is **systemd-pcrlock** plus `boot.lanzaboote.measuredBoot`. Set up [Secure Boot and Lanzaboote](secure-boot-and-lanzaboote.md) first; this page covers the measured-boot follow-on only.

Lanzaboote’s guide targets **LUKS2**. It explicitly does **not** integrate ZFS or btrfs filesystem-level encryption—you can reuse a managed TPM2 policy yourself, but there is no Lanzaboote integration for those layouts.

## Details

**Support check.** Before enabling, confirm systemd-pcrlock accepts your TPM:

```console
$ /run/current-system/systemd/lib/systemd/systemd-pcrlock is-supported
yes
```

Anything other than `yes` means Lanzaboote measured boot will not work on that hardware (TPM not supported by systemd-pcrlock).

**Module options.** Measured boot needs systemd in the initrd and Lanzaboote’s measured-boot switch:

- `boot.initrd.systemd.enable = true`
- `boot.lanzaboote.measuredBoot.enable = true`
- `boot.lanzaboote.measuredBoot.pcrs` — Lanzaboote’s how-to uses e.g. `[ 0 4 7 ]`. PCRs `1`, `2`, and `3` may be flaky depending on hardware; try them only after checking behavior on your machine. Upstream explanation highlights **PCR 4** as covering the boot loader and Lanzaboote stub (and thus, via the stub’s checks, kernel/initrd/cmdline)—do not invent further PCR semantics here; see the [UAPI PCR registry](https://uapi-group.org/specifications/specs/linux_tpm_pcr_registry/) and Lanzaboote’s measured-boot explanation.

**`configurationLimit` ≤ 8.** With measured boot enabled, the maximum allowed `configurationLimit` is **8**. systemd-pcrlock currently will not create a policy for more than eight variants ([systemd#41526](https://github.com/systemd/systemd/issues/41526)).

**Switch and enroll.** Apply with `nixos-rebuild boot`, reboot into the new generation, then enroll the pcrlock policy into the LUKS2 volume with `systemd-cryptenroll`. Always keep a recovery passphrase or other recovery unlock path—**systemd-pcrlock is still experimental** per systemd. For an attended workstation, bind a user PIN as well (`--tpm2-with-pin=true`). After enroll, Lanzaboote updates measurements and the TPM policy on subsequent `nixos-rebuild`; you should not need to re-enroll the LUKS2 volume for normal generation updates.

**Ephemeral root.** If root is wiped each boot ([Impermanence](impermanence.md)), persist `boot.lanzaboote.measuredBoot.pcrlockPolicy` and `boot.lanzaboote.measuredBoot.pcrlockDirectory` across reboots (paths as configured / documented upstream).

**Separate path: Clevis.** NixOS also ships `boot.initrd.clevis` ([clevis.nix](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/system/boot/clevis.nix)): set `enable`, map `devices.<name>.secretFile` to a Clevis JWE, and optionally `useTang` (requires initrd networking for Tang pins). Unlock uses TPM2, Tang, or SSS pins via JWE. That is orthogonal to Lanzaboote measured boot / pcrlock. Soft edge: Clevis wires JWE material into the initrd secret tree; anything that changes initrd content can interact badly with PCR4-style sealing of the stub/initrd chain—treat combining Clevis-in-initrd with PCR4 policies as a sharp edge and verify against current Lanzaboote/systemd docs rather than assuming they compose. Disk unlock is not a substitute for application [secrets strategies](secrets-strategies.md).

## Examples

Minimal options fragment after Lanzaboote Secure Boot is already working (not a full host config). Enroll LUKS with `systemd-cryptenroll` separately against the real block device—do not invent device paths into the Nix config.

```nix
{
  boot.initrd.systemd.enable = true;
  boot.lanzaboote.measuredBoot = {
    enable = true;
    pcrs = [
      0
      4
      7
    ];
  };
  # With measured boot: keep configurationLimit ≤ 8 (systemd-pcrlock variant limit).
}
```

Illustrative enroll (run as root against your LUKS partition; keep a recovery passphrase):

```console
systemd-cryptenroll \
  --tpm2-device=auto \
  --tpm2-with-pin=true \
  --tpm2-pcrlock=/var/lib/systemd/pcrlock.json \
  /dev/sdX
```

## See also

- [Secure Boot and Lanzaboote](secure-boot-and-lanzaboote.md) — Secure Boot / Lanzaboote setup before measured boot
- [Partitioning and bootloaders](partitioning-and-bootloaders.md) — LUKS / ESP context
- [ZFS and Btrfs](zfs-and-btrfs.md) — native FS encryption is a different stack
- [Secrets strategies](secrets-strategies.md) — store vs unlock vs app secrets
- [Impermanence](impermanence.md) — ephemeral root; persist pcrlock paths when needed

## References

- [Lanzaboote: Enable Measured Boot](https://github.com/nix-community/lanzaboote/blob/master/docs/how-to-guides/enable-measured-boot.md) — support check, options, `configurationLimit`, enroll, ephemeral-root persistence, LUKS2-only integration note
- [Lanzaboote documentation](https://nix-community.github.io/lanzaboote/) — Secure Boot prerequisites and book index
- [Lanzaboote: Measured Boot (explanation)](https://github.com/nix-community/lanzaboote/blob/master/docs/explanation/measured-boot.md) — PCR set and PCR 4 / stub coverage
- [nixpkgs `boot.initrd.clevis`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/system/boot/clevis.nix) — Clevis JWE unlock module (separate from pcrlock)
- [UAPI TPM PCR registry](https://uapi-group.org/specifications/specs/linux_tpm_pcr_registry/) — PCR semantics reference cited by Lanzaboote
- [Brave New Trusted Boot World](https://0pointer.net/blog/brave-new-trusted-boot-world.html) — secondary systemd/trusted-boot context (not NixOS-specific)
