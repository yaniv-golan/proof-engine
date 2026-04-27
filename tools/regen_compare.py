"""Compare old and new proof claims/verdicts for the regen pipeline.

Exit codes:
  0 — claim matches (whitespace-canonical); comparison JSON on stdout.
  2 — claim mismatch under --strict-claim; diff on stderr.
  1 — script error.

Note: this script reads proof.json and .old_claim but NOT agent_result.json.
The agent_result.json is consumed by regen_pr_body.py (PR body rendering).
The claim-equivalence gate runs only after the workflow already confirmed the
agent exited 0, so checking agent status here would be redundant.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def _canon(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def canonical_display(v) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    base = v.get("value", "")
    if v.get("qualified") and v.get("qualifier") == "unverified_citations":
        return f"{base} (with unverified citations)"
    return base


class _Parser(argparse.ArgumentParser):
    """Override so missing-argument errors exit 1, not 2.

    Exit code 2 is reserved for --strict-claim claim mismatch (spec §3.9).
    Default argparse exits 2 on missing required args, which would collide.
    """
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        print(f"error: {message}", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    p = _Parser()
    p.add_argument("--slug", required=True)
    p.add_argument("--draft-dir", type=Path, required=True)
    p.add_argument("--old-claim-file", type=Path, required=True)
    p.add_argument("--old-verdict", required=True)
    p.add_argument("--strict-claim", action="store_true")
    args = p.parse_args()

    try:
        old_claim = args.old_claim_file.read_text().strip()
        proof_json = json.loads((args.draft_dir / "proof.json").read_text())
    except Exception as e:
        print(f"Error reading inputs: {e}", file=sys.stderr)
        return 1

    if not old_claim:
        print("Error: --old-claim-file is empty", file=sys.stderr)
        return 1

    new_claim = proof_json.get("claim_natural", "")
    if not isinstance(new_claim, str):
        print(f"Error: proof.json claim_natural is not a string: {type(new_claim).__name__}",
              file=sys.stderr)
        return 1
    new_verdict = canonical_display(proof_json.get("verdict", ""))
    old_verdict = args.old_verdict.strip()

    claim_match = _canon(old_claim) == _canon(new_claim)
    verdict_changed = old_verdict != new_verdict

    if not claim_match and args.strict_claim:
        print(f"Claim mismatch:\n  old: {old_claim!r}\n  new: {new_claim!r}",
              file=sys.stderr)
        return 2

    diff_lines = []
    if verdict_changed:
        diff_lines = [f"- {old_verdict}", f"+ {new_verdict}"]

    out = {
        "claim_match": claim_match,
        "verdict_old": old_verdict,
        "verdict_new": new_verdict,
        "verdict_changed": verdict_changed,
        "diff_lines": diff_lines,
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
