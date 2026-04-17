#!/usr/bin/env python3
"""Batch retag proofs using LLM classification.

Usage:
    python tools/retag-proofs.py --all-in site/proofs              # retag all
    python tools/retag-proofs.py --proof-dir site/proofs/slug      # retag one
    python tools/retag-proofs.py --audit                           # vocabulary audit
    python tools/retag-proofs.py --audit --all-in site/proofs      # audit + retag
    python tools/retag-proofs.py --all-in site/proofs --dry-run    # preview
    python tools/retag-proofs.py --all-in site/proofs -v          # verbose
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from tools.lib.tagger import llm_tag


def _progress(i: int, total: int, label: str) -> None:
    """Print progress that survives piped output.

    On a TTY: inline \\r update (concise, no scrolling).
    Piped (CI, tail, log files): newline-terminated to stderr, one line per
    proof, unbuffered. Ensures a process running under `tee`, `tail`, or a
    log-collecting harness shows live progress instead of nothing until exit.
    """
    msg = f"  [{i}/{total}] {label}..."
    if sys.stderr.isatty():
        # Same line, inline update.
        sys.stderr.write("\r" + msg)
        if i == total:
            sys.stderr.write("\n")
        sys.stderr.flush()
    else:
        # Piped: one line per step, to stderr so stdout stays clean.
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()


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

    # Set-equality: reordering the same tags is a no-op, not a change.
    if set(old_tags) == set(new_tags):
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

    # --- Audit mode: full audit + retag cycle ---
    # proofs_dir is guaranteed non-None here: resolved from --all-in or defaulted
    # to site/proofs, and --audit --proof-dir is rejected by argparse above.
    if args.audit:
        from tools.lib.tagger import (
            audit_vocabulary, load_vocab_data, save_vocab_data,
            reload_vocabulary, count_proofs,
        )

        vocab_path = Path(__file__).parent / "lib" / "tag_vocabulary.json"

        import time

        # Phase 1: Collect claims (in-memory only — no meta.yaml writes)
        print("Phase 1: Collecting claims...")
        proof_dirs = [d for d in sorted(proofs_dir.iterdir())
                      if not d.name.startswith(".") and d.is_dir()
                      and (d / "proof.json").exists()]
        claims = {}
        uncached = 0
        for i, slug_dir in enumerate(proof_dirs, 1):
            proof_data = json.loads((slug_dir / "proof.json").read_text())
            claim = proof_data.get("claim_natural", "")
            meta_path = slug_dir / "meta.yaml"
            tags = []
            is_manual = False
            if meta_path.exists():
                meta = yaml.safe_load(meta_path.read_text()) or {}
                tags = meta.get("tags", [])
                is_manual = meta.get("tags_manual", False)
            if not is_manual and not tags and claim:
                uncached += 1
                try:
                    tags = llm_tag(claim, model="sonnet")
                    if not args.verbose:
                        _progress(i, len(proof_dirs), "collecting (tagging uncached)")
                except RuntimeError as e:
                    print(f"\n  WARNING: could not tag {slug_dir.name}: {e}",
                          file=sys.stderr)
            claims[slug_dir.name] = {
                "claim": claim,
                "tags": tags,
                "manual": is_manual,
            }
        if uncached:
            print(f"\n  Collected {len(claims)} claims ({uncached} needed tagging)")
        else:
            print(f"  Collected {len(claims)} claims (all cached)")

        # Phase 2: Run audit
        print("Phase 2: Running vocabulary audit (Sonnet)...")
        t0 = time.monotonic()
        try:
            accepted = audit_vocabulary(claims, model="sonnet")
        except RuntimeError as e:
            print(f"  Vocabulary audit failed ({time.monotonic() - t0:.1f}s): {e}",
                  file=sys.stderr)
            sys.exit(1)

        if not accepted:
            print("  No new tags needed")
            # Advance count so next publish doesn't re-audit immediately
            if not args.dry_run:
                vocab_data = load_vocab_data(vocab_path)
                vocab_data["proof_count_at_last_audit"] = count_proofs(proofs_dir)
                vocab_data["last_audit_at"] = (
                    __import__("datetime").date.today().isoformat()
                )
                save_vocab_data(vocab_path, vocab_data)
            return

        for prop in accepted:
            print(f"  NEW TAG: {prop['slug']} — {prop['description']}")

        if args.dry_run:
            print(f"  Would add {len(accepted)} new tag(s) to vocabulary (dry run)")
            return

        # Write new tags + retag_pending before retag starts
        vocab_data = load_vocab_data(vocab_path)
        for prop in accepted:
            vocab_data["vocabulary"][prop["slug"]] = prop["description"]
        vocab_data["retag_pending"] = True
        save_vocab_data(vocab_path, vocab_data)
        reload_vocabulary()
        print(f"  Added {len(accepted)} new tag(s) to vocabulary")

        # Phase 3: Full retag with expanded vocabulary
        print(f"Phase 3: Retagging {len(proof_dirs)} proofs with expanded vocabulary...")
        retag_failed = 0
        retag_changed = 0
        t1 = time.monotonic()
        for i, slug_dir in enumerate(proof_dirs, 1):
            try:
                if retag_proof(slug_dir, dry_run=False, model="sonnet",
                               verbose=args.verbose):
                    retag_changed += 1
                if not args.verbose:
                    _progress(i, len(proof_dirs), "retagging")
            except RuntimeError as e:
                print(f"\n  FAIL [{i}/{len(proof_dirs)}] {slug_dir.name}: {e}",
                      file=sys.stderr)
                retag_failed += 1
        retag_elapsed = time.monotonic() - t1

        if retag_failed == 0:
            vocab_data["retag_pending"] = False
            vocab_data["proof_count_at_last_audit"] = count_proofs(proofs_dir)
            vocab_data["last_audit_at"] = (
                __import__("datetime").date.today().isoformat()
            )
            save_vocab_data(vocab_path, vocab_data)
            print(f"\n  Retag complete: {retag_changed} proofs updated ({retag_elapsed:.1f}s)")
        else:
            print(f"\n  WARNING: {retag_failed} proofs failed to retag ({retag_elapsed:.1f}s). "
                  f"retag_pending left set — run --audit again or publish to retry.")

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
                    _progress(i, total, "retagging")
            except RuntimeError as e:
                print(f"\n  FAIL [{i}/{total}] {slug_dir.name}: {e}", file=sys.stderr)
                failed += 1
        elapsed = time.monotonic() - t0

        print(f"\n{changed}/{total} proofs retagged, {failed} failures ({elapsed:.1f}s)")
        if args.dry_run:
            print("(dry run — no files written)")


if __name__ == "__main__":
    main()
