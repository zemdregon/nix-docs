---
status: index
---

# NixOS Architecture

Module system and boot/activation model.

## Contents

- [Module System](module-system.md) — Module evaluation model
- [Module system internals](module-system-internals.md) — `evalModules`, freeform, `specialArgs` / `_module.args`
- [Options and Types](options-and-types.md) — Option declarations and types
- [config vs options](config-vs-options.md) — Defining vs setting
- [Activation Script](activation-script.md) — System activation
- [systemd Integration](systemd-integration.md) — Units and services
- [Generations and Boot](generations-and-boot.md) — Boot entries and rollbacks
