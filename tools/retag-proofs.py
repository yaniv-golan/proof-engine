#!/usr/bin/env python3
"""Batch retag proofs using LLM classification.

Use after changing TAG_VOCABULARY to regenerate tags for all proofs.
Respects tags_manual: true in meta.yaml (skips those proofs).

Usage:
    python tools/retag-proofs.py --all-in site/proofs              # retag all
    python tools/retag-proofs.py --proof-dir site/proofs/slug      # retag one
    python tools/retag-proofs.py --all-in site/proofs --dry-run    # preview
    python tools/retag-proofs.py --audit                           # vocabulary audit
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from tools.lib.tagger import llm_tag


def retag_proof(proof_dir: Path, dry_run: bool = False, model: str = "haiku",
                verbose: bool = False) -> bool:
    """Retag a single proof. Returns True if tags changed, False if no change.

    Raises RuntimeError on LLM failure.
    Skips proofs with tags_manual: true (returns False).
    """
    proof_json_path = proof_dir / "proof.json"
    if not proof_json_path.exists():
        return False

    proof_data = json.loads(proof_json_path.read_text())
    claim = proof_data.get("claim_natural", "")
    if not claim:
        if verbose:
            print(f"  SKIP {proof_dir.name}: no claim_natural")
        return False

    meta_path = proof_dir / "meta.yaml"
    old_tags = []
    meta = {}
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text()) or {}
        old_tags = meta.get("tags", [])
        if meta.get("tags_manual"):
            if verbose:
                print(f"  SKIP {proof_dir.name}: tags_manual")
            return False

    # Raises RuntimeError on failure — caller decides how to handle
    new_tags = llm_tag(claim, model=model)

    if old_tags == new_tags:
        if verbose:
            print(f"  UNCHANGED {proof_dir.name}: {old_tags}")
        return False

    if dry_run:
        print(f"  {proof_dir.name}: {old_tags} -> {new_tags}")
    else:
        meta["tags"] = new_tags
        meta_path.write_text(yaml.dump(meta, default_flow_style=False))
        print(f"  {proof_dir.name}: {old_tags} -> {new_tags}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Retag proofs using LLM classification",
        epilog="Examples:\n"
               "  python tools/retag-proofs.py --all-in site/proofs\n"
               "  python tools/retag-proofs.py --proof-dir site/proofs/slug\n"
               "  python tools/retag-proofs.py --audit\n"
               "  python tools/retag-proofs.py --audit --all-in site/proofs\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--all-in", help="Retag all proofs in directory")
    parser.add_argument("--proof-dir", help="Retag a single proof directory")
    parser.add_argument("--audit", action="store_true",
                        help="Run vocabulary audit before retagging (whole-catalog only)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print per-proof details (skip reasons, tag changes)")
    parser.add_argument("--model", default="haiku",
                        help="Claude model for retagging (default: haiku)")

    args = parser.parse_args()

    if not args.audit and not args.all_in and not args.proof_dir:
        parser.error("one of --all-in, --proof-dir, or --audit is required")

    if args.audit and args.proof_dir:
        parser.error("--audit operates on the whole catalog; cannot combine with --proof-dir")

    proofs_dir = None
    if args.all_in:
        proofs_dir = Path(args.all_in)
    elif args.audit:
        proofs_dir = Path(__file__).parent.parent / "site" / "proofs"
    if proofs_dir and not proofs_dir.is_dir():
        print(f"Not a directory: {proofs_dir}", file=sys.stderr)
        sys.exit(1)

    # --- Audit mode placeholder (filled in Task 5) ---
    if args.audit:
        # TODO: filled in Task 5
        pass
        return

    # --- Single proof retag ---
    if args.proof_dir:
        proof_dir = Path(args.proof_dir)
        if not proof_dir.is_dir():
            print(f"Not a directory: {proof_dir}", file=sys.stderr)
            sys.exit(1)
        try:
            changed = retag_proof(proof_dir, dry_run=args.dry_run, model=args.model,
                                  verbose=args.verbose)
        except RuntimeError as e:
            print(f"FAIL: {e}", file=sys.stderr)
            sys.exit(1)
        if not changed:
            print("No changes.")
        return

    # --- Batch retag (--all-in without --audit) ---
    if args.all_in and proofs_dir:
        import time
        proof_dirs = [d for d in sorted(proofs_dir.iterdir())
                      if not d.name.startswith(".") and d.is_dir()
                      and (d / "proof.json").exists()]
        total = len(proof_dirs)
        changed = 0
        failed = 0
        t0 = time.monotonic()
        for i, slug_dir in enumerate(proof_dirs, 1):
            try:
                if retag_proof(slug_dir, dry_run=args.dry_run, model=args.model,
                               verbose=args.verbose):
                    changed += 1
                if not args.verbose:
                    print(f"\r  [{i}/{total}] retagging...", end="", flush=True)
            except RuntimeError as e:
                print(f"\n  FAIL [{i}/{total}] {slug_dir.name}: {e}", file=sys.stderr)
                failed += 1
        elapsed = time.monotonic() - t0

        print(f"\n{changed}/{total} proofs retagged, {failed} failures ({elapsed:.1f}s)")
        if args.dry_run:
            print("(dry run — no files written)")


if __name__ == "__main__":
    main()
