#!/usr/bin/env python3
"""Generate proof_narrative.md for existing proofs using Claude Code CLI.

Uses `claude -p` (same auth as evals) — no ANTHROPIC_API_KEY needed.

Usage:
    # Single proof:
    python tools/generate-narratives.py --proof-dir site/proofs/some-slug

    # Batch from file (one path per line):
    python tools/generate-narratives.py --batch paths.txt

    # All proofs in a directory:
    python tools/generate-narratives.py --all-in site/proofs

    # Dry run (validate only, don't write):
    python tools/generate-narratives.py --proof-dir site/proofs/some-slug --dry-run
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.lib.narrative_validator import validate_narrative

REPO_ROOT = Path(__file__).parent.parent
SKILL_MD = REPO_ROOT / "proof-engine" / "skills" / "proof-engine" / "SKILL.md"


def _load_narrative_spec() -> str:
    """Load the narrative output spec from SKILL.md.

    Single source of truth: the same spec the LLM follows when creating
    new proofs also governs migration. No duplicated prompt.
    """
    skill_text = SKILL_MD.read_text()
    match = re.search(
        r"(### proof_narrative\.md.*?)(?=\n### |\n## |\Z)",
        skill_text, re.DOTALL,
    )
    if not match:
        print("ERROR: Could not find '### proof_narrative.md' section in SKILL.md", file=sys.stderr)
        sys.exit(1)
    return match.group(1).strip()


def _build_prompt(claim_natural: str, verdict: str, proof_data: dict,
                  proof_md: str, proof_audit: str) -> str:
    """Build the generation prompt from the canonical SKILL.md spec."""
    narrative_spec = _load_narrative_spec()
    return (
        f"You are generating a proof_narrative.md file for an existing proof.\n\n"
        f"Follow this specification EXACTLY:\n\n{narrative_spec}\n\n"
        f"The claim is: {claim_natural}\n"
        f"The verdict is: {verdict}\n\n"
        f"Read the proof artifacts below and write the proof_narrative.md content.\n"
        f"Output ONLY the markdown content. No code fences, no explanation.\n\n"
        f"---\n\n## proof.json\n\n```json\n{json.dumps(proof_data, indent=2)}\n```\n\n"
        f"---\n\n## proof.md\n\n{proof_md}\n\n"
        f"---\n\n## proof_audit.md\n\n{proof_audit}\n"
    )


def generate_narrative(proof_dir: Path, model: str, dry_run: bool = False) -> tuple[bool, list[str]]:
    """Generate proof_narrative.md for a single proof directory.

    Returns (success, messages).
    """
    messages = []
    proof_json_path = proof_dir / "proof.json"
    proof_md_path = proof_dir / "proof.md"
    proof_audit_path = proof_dir / "proof_audit.md"

    if not proof_json_path.exists():
        return False, [f"ERROR: {proof_dir}: proof.json not found"]

    proof_data = json.loads(proof_json_path.read_text())
    verdict = proof_data.get("verdict", "")
    claim_natural = proof_data.get("claim_natural", "")

    proof_md = proof_md_path.read_text() if proof_md_path.exists() else ""
    proof_audit = proof_audit_path.read_text() if proof_audit_path.exists() else ""

    prompt = _build_prompt(
        claim_natural=claim_natural, verdict=verdict,
        proof_data=proof_data, proof_md=proof_md, proof_audit=proof_audit,
    )

    # Use claude CLI — same auth as evals, no API key needed
    result = subprocess.run(
        ["claude", "-p", "--model", model, "--dangerously-skip-permissions", prompt],
        capture_output=True, text=True, timeout=120,
    )

    if result.returncode != 0:
        messages.append(f"ERROR: {proof_dir.name}: claude CLI failed (exit {result.returncode})")
        if result.stderr:
            messages.append(f"  stderr: {result.stderr[:200]}")
        return False, messages

    narrative = result.stdout.strip()

    # Validate
    errors, warnings = validate_narrative(narrative, verdict=verdict, claim_natural=claim_natural)

    for w in warnings:
        messages.append(f"WARNING: {proof_dir.name}: {w}")

    if errors:
        for e in errors:
            messages.append(f"ERROR: {proof_dir.name}: {e}")
        return False, messages

    if not dry_run:
        (proof_dir / "proof_narrative.md").write_text(narrative)

        # Run full structural validation — fail hard so invalid narratives don't persist
        val_result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "validate-site-proof.py"),
             str(proof_dir), "--structural-only"],
            capture_output=True, text=True,
        )
        if val_result.returncode != 0:
            (proof_dir / "proof_narrative.md").unlink(missing_ok=True)
            messages.append(f"ERROR: {proof_dir.name}: validate-site-proof.py failed:\n{val_result.stdout}")
            return False, messages

        messages.append(f"PASS: {proof_dir.name}: proof_narrative.md written and validated")
    else:
        messages.append(f"DRY RUN PASS: {proof_dir.name}: validation passed")

    return True, messages


def main():
    parser = argparse.ArgumentParser(description="Generate proof_narrative.md for existing proofs")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--proof-dir", type=Path, help="Single proof directory path")
    group.add_argument("--batch", type=Path, help="File with one proof directory path per line")
    group.add_argument("--all-in", type=Path, help="Generate for all proofs in directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't write files")
    parser.add_argument("--model", default="sonnet",
                        help="Model to use (default: sonnet)")
    args = parser.parse_args()

    if args.proof_dir:
        dirs = [args.proof_dir]
    elif args.batch:
        dirs = [Path(line.strip()) for line in args.batch.read_text().splitlines() if line.strip()]
    else:
        dirs = sorted(
            d for d in args.all_in.iterdir()
            if d.is_dir() and (d / "proof.json").exists() and not d.name.startswith(".")
        )

    total = len(dirs)
    passed = 0
    failed = 0

    for i, proof_dir in enumerate(dirs, 1):
        print(f"[{i}/{total}] Processing {proof_dir.name}...")
        success, messages = generate_narrative(proof_dir, model=args.model, dry_run=args.dry_run)
        for msg in messages:
            print(f"  {msg}")
        if success:
            passed += 1
        else:
            failed += 1

    print(f"\nDone: {passed} passed, {failed} failed out of {total}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
