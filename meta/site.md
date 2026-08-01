---
status: active
---

# Site (GitHub Pages)

Published docs site for this wiki via [MkDocs](https://www.mkdocs.org/) + [Material](https://squidfunk.github.io/mkdocs-material/), deployed by [`.github/workflows/pages.yml`](../.github/workflows/pages.yml).

**Live URL:** [https://zemdregon.github.io/nix-docs/](https://zemdregon.github.io/nix-docs/)

## Design choices

- **Source = repo root** — plain Markdown tree; no checked-in `docs/` mirror.
- **Stage step** — [prepare-docs-dir.sh](prepare-docs-dir.sh) symlinks wiki paths into gitignored `docs/` (MkDocs requires `docs_dir` to be a child of the config directory).
- **Logo / favicon** — [assets/nixos-logomark.svg](../assets/nixos-logomark.svg) (official NixOS logomark; staged into `docs/assets/`).
- **Nav** — numbered domain `README.md` indexes + glossary / comparisons / cheatsheets / meta (leaves via in-page Contents and search).
- **Excluded** — `AGENTS.md`, `.github/`, `meta/audit/`, `meta/attachments/`.
- **Edit links** — paths under `docs/` match repo paths, so Material “edit” URLs hit the real files on `main`.

## Attribution

“NixOS Logo” by Simon Frankau, Tim Cuthbertson, and Daniel Baker (maintained by the [NixOS Marketing Team](https://nixos.org/community/teams/marketing/)), from [nixos/branding](https://github.com/NixOS/branding), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Local build

```bash
bash meta/prepare-docs-dir.sh
pip install -r requirements-docs.txt
mkdocs build            # writes ./site
mkdocs serve            # preview at http://127.0.0.1:8000
```

With Nix (cache.nixos.org if a local substituter is down):

```bash
nix-shell -p python3 python3Packages.pip --run '
  python3 -m venv /tmp/nix-docs-venv
  /tmp/nix-docs-venv/bin/pip install -r requirements-docs.txt
  bash meta/prepare-docs-dir.sh
  /tmp/nix-docs-venv/bin/mkdocs build
'
```

Link warnings for repo-only targets (`AGENTS.md`, `.github/workflows/*`, `.nix` fixtures, `mkdocs.yml`) are expected; CI does not use `--strict`.

## Enable GitHub Pages (one-time)

1. Push `mkdocs.yml`, `requirements-docs.txt`, prepare script, and the Pages workflow to `main`.
2. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Re-run the **GitHub Pages** workflow if the first deploy waited on that setting.

Do not commit `docs/` or `site/`.

## See also

- [conventions.md](conventions.md) — wiki layout and linking rules
