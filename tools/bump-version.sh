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
sedi "s/version: .*/version: \"$VERSION\"/" "$ROOT/proof-engine/skills/proof-engine/SKILL.md"
sedi "s/__PROOF_ENGINE_VERSION__/$VERSION/g" "$ROOT/proof-engine/skills/proof-engine/references/proof-templates.md"

echo "Version $VERSION applied to:"
echo "  proof-engine/.claude-plugin/plugin.json"
echo "  .cursor-plugin/plugin.json"
echo "  proof-engine/skills/proof-engine/SKILL.md"
echo "  proof-engine/skills/proof-engine/references/proof-templates.md (generator version)"
