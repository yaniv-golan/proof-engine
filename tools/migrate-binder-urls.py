#!/usr/bin/env python3
"""Rewrite binder_url in doi.json files to point at the launcher repo.

Old:  https://mybinder.org/v2/zenodo/<zenodo_id>/?filepath=proof.ipynb
New:  https://mybinder.org/v2/gh/<LAUNCHER_REPO>/<LAUNCHER_TAG>?urlpath=...

Idempotent: running twice yields the same output.
Skips doi.json files whose DOI is not a Zenodo DOI.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

BINDER_LAUNCHER_REPO = "yaniv-golan/proof-engine-binder"
BINDER_LAUNCHER_TAG = "v1.21.0"  # IMMUTABLE tag — pins published URLs to an exact launcher release.

ZENODO_DOI_RE = re.compile(r"^10\.\d{4,9}/zenodo\.\d+$")


def build_url(doi: str) -> str:
    return (
        f"https://mybinder.org/v2/gh/{BINDER_LAUNCHER_REPO}/{BINDER_LAUNCHER_TAG}"
        f"?urlpath=lab%2Ftree%2Flauncher.ipynb%23doi%3D{quote(doi, safe='')}"
    )


def migrate_file(path: Path) -> bool:
    data = json.loads(path.read_text())
    doi = data.get("doi", "")
    if not ZENODO_DOI_RE.fullmatch(doi):
        return False
    expected = build_url(doi)
    if data.get("binder_url") == expected:
        return False
    data["binder_url"] = expected
    path.write_text(json.dumps(data, indent=2) + "\n")
    return True


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: migrate-binder-urls.py <doi.json> [<doi.json> ...]", file=sys.stderr)
        return 2
    changed = 0
    for p in argv[1:]:
        if migrate_file(Path(p)):
            changed += 1
            print(f"migrated {p}")
    print(f"done: {changed} file(s) changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
