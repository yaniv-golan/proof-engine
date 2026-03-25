# Cross-Platform Architecture

This skill ships from a single source of truth and works across multiple AI platforms. This document explains how.

## Source of Truth

```
skills/proof-engine/
├── SKILL.md              <- canonical skill definition
├── scripts/              <- bundled Python verification scripts
├── references/           <- hardening rules documentation
├── evals/                <- evaluation test suite
└── agents/
    └── openai.yaml       <- Codex CLI UI metadata
```

## How Each Platform Consumes the Skill

### Claude Code — direct from repo

- Installs from the plugin marketplace: `/plugin marketplace add yaniv-golan/proof-engine`
- Manifest: `.claude-plugin/plugin.json` with `"skills": "./skills"`
- Claude Code discovers `skills/proof-engine/SKILL.md` automatically

### Cursor — direct from repo

- Installs as a plugin: Settings -> paste repo URL into "Search or Paste Link"
- Manifest: `.cursor-plugin/plugin.json` (no `skills` field needed — auto-discovers from `skills/`)
- Same `SKILL.md` as Claude Code

### Manus — upload zip from GitHub Releases

- Download `proof-engine.zip` from the latest release
- Upload at Settings -> Skills -> + Add -> Upload
- The zip contains a flat `proof-engine/` folder

### ChatGPT — upload zip from GitHub Releases

- Download `proof-engine.zip` from the latest release
- Upload as a skill in ChatGPT settings
- The zip contains a flat `proof-engine/` folder with all scripts

### Codex CLI — install from repo or zip

**From repo (preferred):**

```
$skill-installer https://github.com/yaniv-golan/proof-engine
```

**From zip (manual):** Download `proof-engine.zip` from GitHub Releases and extract to `~/.codex/skills/`.

### Others (Windsurf, etc.) — same zip

- Download and extract to `~/.agents/skills/` or `.agents/skills/` in the project root

## Release Workflow

CI (`.github/workflows/release.yml`) runs on version tags (`v*`) and produces the generic zip:

```bash
cp -r skills/proof-engine proof-engine
sed -i 's|\${CLAUDE_SKILL_DIR}/||g' proof-engine/SKILL.md
zip -r "proof-engine.zip" proof-engine/
```

## Version Management

The canonical version lives in `VERSION` at the repo root. Run `./tools/bump-version.sh` to propagate it to all locations. See [VERSIONING.md](../VERSIONING.md) for the full release process.
