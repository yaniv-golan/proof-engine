# Lint runbook (for Claude)

When asked to lint a wiki:

1. Run `proof-engine-wiki lint WIKI_DIR/ --json --pretty`.
2. Group findings by `kind`:
   - `unresolved_marker` — `{{prove:}}` that hasn't been processed.
   - `stale_proof` — a cited proof URL is no longer reachable.
   - `badge_unreachable` — the SVG badge 404s.
3. Report counts per kind to the user.
4. For `unresolved_marker`: offer to run ingest.
5. For `stale_proof`: report which URLs; do NOT auto-fix (may indicate the
   registry moved or the proof was retracted — user should investigate).
