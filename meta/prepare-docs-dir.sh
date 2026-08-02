#!/usr/bin/env bash
# Stage vault Markdown into ./docs for MkDocs (docs_dir cannot be repo root).
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
docs="$root/docs"

rm -rf "$docs"
mkdir -p "$docs"

# Numbered domains + cross-cutting trees (meta handled separately)
for d in \
  00-roadmap \
  01-philosophy \
  02-concepts \
  03-language \
  04-store-and-build \
  05-cli-and-tooling \
  06-nixpkgs \
  07-flakes \
  08-experimental-features \
  09-nixos \
  10-home-and-user \
  11-development \
  12-deployment-and-infra \
  13-implementations \
  14-security-and-trust \
  15-history-and-governance \
  16-configuration-examples \
  comparisons \
  cheatsheets
do
  ln -s "$root/$d" "$docs/$d"
done

# Root articles / indexes
for f in README.md glossary.md; do
  ln -s "$root/$f" "$docs/$f"
done

# Site chrome (favicon / header logo)
ln -s "$root/assets" "$docs/assets"

# meta/: publish files but skip audit tooling, attachments, and local RAG store
mkdir -p "$docs/meta"
for item in "$root/meta"/*; do
  base="$(basename "$item")"
  case "$base" in
    audit|attachments) continue ;;
    rag)
      # Publish the howto only — never stage .chroma / Python env artifacts.
      mkdir -p "$docs/meta/rag"
      ln -s "$item/README.md" "$docs/meta/rag/README.md"
      ;;
    *) ln -s "$item" "$docs/meta/$base" ;;
  esac
done

echo "Prepared $docs (symlinks to vault source)"
