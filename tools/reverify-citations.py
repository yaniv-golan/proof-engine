#!/usr/bin/env python3
"""Re-verify citations that previously fell back to fragment/aggressive_normalization.

Fetches live URLs and re-runs the matching pipeline with the current normalizer.
Updates proof.json in place for citations that improve (e.g., fragment → full_quote).
Does NOT downgrade results (if a citation was previously full_quote, it stays).

Usage:
    python tools/reverify-citations.py [--dry-run] [--slug SLUG]
"""

import argparse
import json
import glob
import os
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "proof-engine" / "skills" / "proof-engine" / "scripts"))
from verify_citations import verify_citation


METHOD_RANK = {
    "full_quote": 4,
    "unicode_normalized": 3,
    "fragment": 2,
    "aggressive_normalization": 1,
    None: 0,
}


def main():
    parser = argparse.ArgumentParser(description="Re-verify fragment/aggressive citations")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    parser.add_argument("--slug", help="Only re-verify a specific proof slug")
    parser.add_argument("--all-methods", action="store_true",
                        help="Re-verify ALL citations, not just fragment/aggressive")
    args = parser.parse_args()

    proof_jsons = sorted(glob.glob("site/proofs/*/proof.json"))
    if args.slug:
        proof_jsons = [p for p in proof_jsons if args.slug in p]

    total_checked = 0
    total_improved = 0
    total_unchanged = 0
    total_failed = 0
    changes = []

    for pj_path in proof_jsons:
        slug = os.path.basename(os.path.dirname(pj_path))
        with open(pj_path) as f:
            data = json.load(f)

        citations = data.get("citations", {})
        if not isinstance(citations, dict):
            continue

        modified = False
        for fid, cit in citations.items():
            old_method = cit.get("method") or ""
            old_status = cit.get("status", "")

            # Skip citations that don't need re-verification
            if not args.all_methods:
                if "fragment" not in old_method and old_method != "aggressive_normalization":
                    continue

            url = cit.get("url")
            quote = cit.get("quote")
            if not url or not quote:
                continue

            total_checked += 1
            print(f"  {slug}/{fid}: {old_method} ({old_status}) ... ", end="", flush=True)

            try:
                result = verify_citation(url, quote, fid, timeout=20, wayback_fallback=True)
            except Exception as e:
                print(f"ERROR: {e}")
                total_failed += 1
                continue

            new_method = result.get("method")
            new_status = result.get("status", "")
            new_coverage = result.get("coverage_pct")

            old_rank = METHOD_RANK.get(old_method, 0)
            new_rank = METHOD_RANK.get(new_method, 0)

            improved = new_rank > old_rank or (
                new_rank == old_rank and new_status == "verified" and old_status != "verified"
            )

            if improved:
                total_improved += 1
                label = f"IMPROVED: {old_method}→{new_method} ({new_status})"
                print(label)
                changes.append(f"  {slug}/{fid}: {label}")

                if not args.dry_run:
                    cit["status"] = new_status
                    cit["method"] = new_method
                    cit["coverage_pct"] = new_coverage
                    cit["fetch_mode"] = result.get("fetch_mode", "live")
                    if "credibility" in result:
                        cit["credibility"] = result["credibility"]
                    modified = True
            else:
                total_unchanged += 1
                print(f"unchanged ({new_method}, {new_status})")

        if modified and not args.dry_run:
            with open(pj_path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"  → Updated {pj_path}")

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Summary:")
    print(f"  Checked:   {total_checked}")
    print(f"  Improved:  {total_improved}")
    print(f"  Unchanged: {total_unchanged}")
    print(f"  Failed:    {total_failed}")
    if changes:
        print(f"\nImprovements:")
        for c in changes:
            print(c)


if __name__ == "__main__":
    main()
