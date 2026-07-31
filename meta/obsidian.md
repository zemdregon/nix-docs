---
status: active
---

# Obsidian vault

This repo is a plain-Markdown wiki that also opens as an [Obsidian](https://obsidian.md/) vault (folder containing `.obsidian/`).

## Open

**File → Open folder as vault** and choose the repo root (the directory that contains `README.md` and `00-roadmap/`).

Trust the vault and keep **Restricted mode** off so community plugins load.

## Core settings

Checked into `.obsidian/app.json` (do not flip these casually):

| Setting | Value | Why |
|---------|-------|-----|
| Use Markdown links | on | Articles use standard Markdown links to `.md` files, not `[[wikilinks]]` |
| New link format | Relative path to file | Same as [conventions](conventions.md); avoids ambiguous `README` / `nix-darwin` short names |
| Automatically update internal links | on | Renames keep relative links working |

## Community plugins

Enabled in `.obsidian/community-plugins.json` (binaries + `data.json` under `.obsidian/plugins/`):

| Plugin | Role here |
|--------|-----------|
| **Folder notes** | Click a folder → opens its `README.md` (`folderNoteName: README`, inside folder) |
| **Omnisearch** | Fast ranked search across the wiki |
| **Various Complements** | Autocomplete for words and internal Markdown links |
| **Linter** | Optional formatting; YAML title/timestamp and file-name heading rules stay **off** so agents/docs keep control of frontmatter |
| **Dataview** | Query `status` frontmatter — start at [dashboard.md](dashboard.md) |

## Frontmatter

Every note uses YAML:

```yaml
---
status: complete
---
```

Values: `stub` / `draft` / `complete` (leaves), `index` (folder READMEs), `active` / `draft` / `superseded` (meta and plans). See [conventions](conventions.md).

## Authoring tips

- Prefer **relative** Markdown links with a `.md` target (or a `#heading` on the same note). Link folders via their `README.md`, not a bare directory path.
- Duplicate basenames exist (`README.md` in every domain; two `nix-darwin.md` leaves). Relative paths disambiguate; shortest-name links do not.
- Attachments go under [attachments/](attachments/) (configured as Obsidian’s attachment folder).
- Local UI state (`workspace.json`, caches) is gitignored — see root `.gitignore`. Plugin installs are tracked so clones work offline.

## See also

- [dashboard.md](dashboard.md) — Dataview status tables
- [conventions.md](conventions.md)
- [Root README](../README.md)
