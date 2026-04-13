#!/usr/bin/env python3
"""Migrate all site proofs from v1/v2 to v3 format.

Usage:
    python tools/migrate_proofs_v3.py --site-dir site [--dry-run]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.lib.normalize import normalize_to_v3


def migrate_proof(proof_dir: Path, dry_run: bool = False) -> tuple[str, str]:
    """Migrate a single proof.json to v3 format.

    Returns:
        (slug, status) where status is "migrated", "already_v3", or "error: ..."
    """
    slug = proof_dir.name
    proof_json_path = proof_dir / "proof.json"
    if not proof_json_path.exists():
        return slug, "error: proof.json not found"

    proof_data = json.loads(proof_json_path.read_text())
    if proof_data.get("format_version") == 3:
        return slug, "already_v3"

    try:
        v3 = normalize_to_v3(proof_data)
    except Exception as e:
        return slug, f"error: {e}"

    if not dry_run:
        proof_json_path.write_text(json.dumps(v3, indent=2, default=str) + "\n")

    return slug, "migrated"


def main():
    parser = argparse.ArgumentParser(description="Migrate proofs to v3 format")
    parser.add_argument("--site-dir", required=True, help="Site directory (e.g., site)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change")
    args = parser.parse_args()

    proofs_dir = Path(args.site_dir) / "proofs"
    if not proofs_dir.exists():
        print(f"ERROR: {proofs_dir} not found", file=sys.stderr)
        sys.exit(1)

    results = {"migrated": 0, "already_v3": 0, "errors": []}

    for slug_dir in sorted(proofs_dir.iterdir()):
        if slug_dir.name.startswith(".") or not slug_dir.is_dir():
            continue
        if not (slug_dir / "proof.json").exists():
            continue

        slug, status = migrate_proof(slug_dir, dry_run=args.dry_run)

        if status == "migrated":
            results["migrated"] += 1
            print(f"  {'[DRY RUN] ' if args.dry_run else ''}migrated: {slug}")
        elif status == "already_v3":
            results["already_v3"] += 1
        else:
            results["errors"].append((slug, status))
            print(f"  ERROR: {slug}: {status}", file=sys.stderr)

    print(f"\nResults: {results['migrated']} migrated, "
          f"{results['already_v3']} already v3, "
          f"{len(results['errors'])} errors")

    if results["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
