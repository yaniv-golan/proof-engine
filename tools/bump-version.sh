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

sedi "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$ROOT/.claude-plugin/plugin.json"
sedi "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$ROOT/.cursor-plugin/plugin.json"
sedi "s/version: \"[^\"]*\"/version: \"$VERSION\"/" "$ROOT/skills/proof-engine/SKILL.md"

echo "Version $VERSION applied to:"
echo "  .claude-plugin/plugin.json"
echo "  .cursor-plugin/plugin.json"
echo "  skills/proof-engine/SKILL.md"
