#!/bin/bash
# Reads version from VERSION file and updates all locations.
# Usage: ./tools/bump-version.sh [new-version]
#   If new-version is provided, updates VERSION file first.
#   If omitted, propagates current VERSION file to all locations.
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION_FILE="$ROOT/VERSION"

if [ -n "$1" ]; then
  echo "$1" > "$VERSION_FILE"
fi

VERSION="$(cat "$VERSION_FILE" | tr -d '[:space:]')"

if [ -z "$VERSION" ]; then
  echo "Error: VERSION file is empty" >&2
  exit 1
fi

# Cross-platform sed -i (macOS uses BSD sed which requires '' after -i)
sedi() {
  if sed --version 2>/dev/null | grep -q GNU; then
    sed -i "$@"
  else
    sed -i '' "$@"
  fi
}

sedi "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$ROOT/proof-engine/.claude-plugin/plugin.json"
sedi "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$ROOT/.cursor-plugin/plugin.json"
sedi "s/^  version: .*/  version: \"$VERSION\"/" "$ROOT/proof-engine/skills/proof-engine/SKILL.md"
cp "$VERSION_FILE" "$ROOT/proof-engine/skills/proof-engine/VERSION"
sedi "s/^version: .*/version: $VERSION/" "$ROOT/CITATION.cff"

# Subpackages — keep their pyproject.toml + __init__.py in sync with the
# repo VERSION so the proof-engine-registry / proof-citations wheels can be
# released in lockstep with the skill.
for pkg in packages/proof-citations packages/proof-engine-registry packages/proof-engine-wiki; do
  if [ -f "$ROOT/$pkg/pyproject.toml" ]; then
    sedi "s/^version = \"[^\"]*\"/version = \"$VERSION\"/" "$ROOT/$pkg/pyproject.toml"
  fi
  for init_file in "$ROOT/$pkg"/src/*/__init__.py; do
    if [ -f "$init_file" ]; then
      sedi "s/^__version__ = \"[^\"]*\"/__version__ = \"$VERSION\"/" "$init_file"
    fi
  done
done

echo "Version $VERSION applied to:"
echo "  proof-engine/.claude-plugin/plugin.json"
echo "  .cursor-plugin/plugin.json"
echo "  proof-engine/skills/proof-engine/SKILL.md"
echo "  proof-engine/skills/proof-engine/VERSION (copied)"
echo "  CITATION.cff"
echo "  packages/*/pyproject.toml (when present)"
echo "  packages/*/src/*/__init__.py (when present)"
