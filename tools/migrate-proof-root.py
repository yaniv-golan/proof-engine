#!/usr/bin/env python3
"""Rewrite proof.py files so PROOF_ENGINE_ROOT reads from an env var.

Legacy shape:
    PROOF_ENGINE_ROOT = "<absolute path>"

Migrated shape:
    PROOF_ENGINE_ROOT = os.environ.get(
        "PROOF_ENGINE_ROOT",
        "<absolute path>",
    )

Idempotent: running twice on the same file is a no-op.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LEGACY_RE = re.compile(
    r'^PROOF_ENGINE_ROOT = "(?P<path>[^"]+)"$',
    re.MULTILINE,
)
MIGRATED_RE = re.compile(
    r'^PROOF_ENGINE_ROOT = os\.environ\.get\(',
    re.MULTILINE,
)


def migrate_text(text: str) -> str:
    if MIGRATED_RE.search(text):
        return text
    match = LEGACY_RE.search(text)
    if not match:
        return text
    path = match.group("path")
    replacement = (
        f'PROOF_ENGINE_ROOT = os.environ.get(\n'
        f'    "PROOF_ENGINE_ROOT",\n'
        f'    "{path}",\n'
        f')'
    )
    return LEGACY_RE.sub(replacement, text, count=1)


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
