#!/usr/bin/env python3
"""One-time migration: resolve + prose-scan every existing proof under site/proofs.

Does NOT auto-apply fixes. Writes a migration-report.md listing:
  (a) identifiers needing resolution (unknown in cache);
  (b) prose identifiers not covered by depends_on/evidence;
  (c) author/title mismatches (Pass 2 + Pass 4 findings).

Author reviews and either rewrites the citation as {{cite:...}} + runs
cite-expand, OR edits the text in place, then re-runs `verify-prose`.
"""

import argparse
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools.lib.reference_resolver import (
    collect_identifiers, load_cache, save_cache, resolve,
)
from tools.lib.prose_reference_scan import verify_prose


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--site-dir", default="site")
    p.add_argument("--refresh", action="store_true", help="Actually re-fetch from registries")
    p.add_argument("--report", default="migration-report.md")
    args = p.parse_args()

    proofs_dir = Path(args.site_dir) / "proofs"
    report_lines = ["# Prose reference migration report", ""]

    for proof_dir in sorted(proofs_dir.iterdir()):
        if not proof_dir.is_dir() or proof_dir.name.startswith("."):
            continue
        print(f"migrate: {proof_dir.name}")
        idents = collect_identifiers(proof_dir)
        cache = load_cache(proof_dir)
        for t, v in idents:
            key = f"{t}:{v}"
            if key in cache and not args.refresh:
                continue
            try:
                cache[key] = resolve(t, v, refresh=True)
            except Exception as e:
                report_lines.append(f"- {proof_dir.name}: unresolved {key}: {e}")
                continue
        if args.refresh:
            save_cache(proof_dir, cache)

        result = verify_prose(proof_dir)
        for e in result.errors:
            report_lines.append(f"- {proof_dir.name}/{e.file}:{e.line}: {e.message}")
        for w in result.warnings:
            report_lines.append(f"- {proof_dir.name}: (advisory) {w}")

    Path(args.report).write_text("\n".join(report_lines) + "\n")
    print(f"migration report: {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
