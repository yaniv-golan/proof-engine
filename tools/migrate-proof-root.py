#!/usr/bin/env python3
"""Rewrite proof.py files so PROOF_ENGINE_ROOT reads from an env var.

Handles two legacy shapes:

  A. Hardcoded absolute path:
         PROOF_ENGINE_ROOT = "<absolute path>"

  B. __file__-traversal via _REPO_ROOT (discouraged; 4 historical proofs):
         PROOF_ENGINE_ROOT = os.path.join(_REPO_ROOT, "proof-engine", "skills", "proof-engine")

Both are rewritten to:
    PROOF_ENGINE_ROOT = os.environ.get(
        "PROOF_ENGINE_ROOT",
        "<absolute path>",
    )

For shape B, the fallback path is a fixed constant (STANDARD_FALLBACK below)
since the legacy line didn't contain a literal path. _REPO_ROOT is left in place
because some proofs use it for unrelated lookups (e.g. reading VERSION).

Idempotent: running twice on the same file is a no-op.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

STANDARD_FALLBACK = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"

LEGACY_RE = re.compile(
    r'^PROOF_ENGINE_ROOT = "(?P<path>[^"]+)"$',
    re.MULTILINE,
)
LEGACY_JOIN_RE = re.compile(
    r'^PROOF_ENGINE_ROOT = os\.path\.join\(_REPO_ROOT, "proof-engine", "skills", "proof-engine"\)$',
    re.MULTILINE,
)
MIGRATED_RE = re.compile(
    r'^PROOF_ENGINE_ROOT = os\.environ\.get\(',
    re.MULTILINE,
)


def _build_replacement(path: str) -> str:
    return (
        f'PROOF_ENGINE_ROOT = os.environ.get(\n'
        f'    "PROOF_ENGINE_ROOT",\n'
        f'    "{path}",\n'
        f')'
    )


def migrate_text(text: str) -> str:
    if MIGRATED_RE.search(text):
        return text
    match = LEGACY_RE.search(text)
    if match:
        return LEGACY_RE.sub(_build_replacement(match.group("path")), text, count=1)
    if LEGACY_JOIN_RE.search(text):
        return LEGACY_JOIN_RE.sub(_build_replacement(STANDARD_FALLBACK), text, count=1)
    return text


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: migrate-proof-root.py <proof.py> [<proof.py> ...]", file=sys.stderr)
        return 2
    changed = 0
    for p in argv[1:]:
        path = Path(p)
        before = path.read_text()
        after = migrate_text(before)
        if after != before:
            path.write_text(after)
            changed += 1
            print(f"migrated {path}")
    print(f"done: {changed} file(s) changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
