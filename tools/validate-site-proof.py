#!/usr/bin/env python3
"""Validate a proof submission for the Proof Engine site."""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.lib.verdict import VERDICT_TAXONOMY

REQUIRED_JSON_KEYS = ["fact_registry", "claim_formal", "claim_natural",
                      "verdict", "key_results", "generator"]
REQUIRED_GENERATOR_KEYS = ["name", "version", "repo", "generated_at"]
REQUIRED_CLAIM_FORMAL_KEYS = []  # claim_formal structure varies by proof type
INVARIANT_FIELDS = ["verdict", "claim_formal", "claim_natural", "fact_registry", "key_results"]


def validate_json_structure(proof_data):
    errors = []
    for key in REQUIRED_JSON_KEYS:
        if key not in proof_data:
            errors.append(f"proof.json missing required key: {key}")

    if "generator" in proof_data:
        for key in REQUIRED_GENERATOR_KEYS:
            if key not in proof_data["generator"]:
                errors.append(f"generator missing key: {key}")

    if "claim_formal" in proof_data:
        for key in REQUIRED_CLAIM_FORMAL_KEYS:
            if key not in proof_data["claim_formal"]:
                errors.append(f"claim_formal missing key: {key}")

    if "verdict" in proof_data:
        if proof_data["verdict"] not in VERDICT_TAXONOMY:
            errors.append(f"Unknown verdict: {proof_data['verdict']}")

    return errors


def run_proof_and_extract_json(proof_py_path):
    env = dict(os.environ)
    env.pop("GITHUB_TOKEN", None)
    env.pop("ACTIONS_RUNTIME_TOKEN", None)

    result = subprocess.run(
        [sys.executable, str(proof_py_path)],
        capture_output=True, text=True, timeout=600, env=env,
    )
    if result.returncode != 0:
        return None, f"proof.py failed: {result.stderr[:500]}"

    marker = "=== PROOF SUMMARY (JSON) ==="
    output = result.stdout
    idx = output.find(marker)
    if idx == -1:
        return None, "proof.py output missing JSON summary marker"

    json_str = output[idx + len(marker):].strip()
    try:
        return json.loads(json_str), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in proof.py output: {e}"


def compare_invariant_fields(checked_in, regenerated):
    diffs = []
    for field in INVARIANT_FIELDS:
        val_a = checked_in.get(field)
        val_b = regenerated.get(field)
        if val_a != val_b:
            diffs.append(f"Field '{field}' diverges between checked-in and regenerated proof.json")
    return diffs


def extract_verdict_from_conclusion(proof_md_path):
    text = Path(proof_md_path).read_text()
    sections = {}
    pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[heading.lower()] = text[start:end].strip()

    conclusion = sections.get("conclusion", "")
    for verdict in sorted(VERDICT_TAXONOMY.keys(), key=len, reverse=True):
        if verdict in conclusion:
            return verdict
    return None


def main():
    structural_only = "--structural-only" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if not args:
        print("Usage: validate-site-proof.py [--structural-only] <proof-dir>", file=sys.stderr)
        sys.exit(1)

    proof_dir = Path(args[0])
    errors = []
    warnings = []

    # 1. Structural validation
    proof_json_path = proof_dir / "proof.json"
    if not proof_json_path.exists():
        errors.append("proof.json not found")
        print_results(errors, warnings)
        sys.exit(1)

    proof_data = json.loads(proof_json_path.read_text())
    errors.extend(validate_json_structure(proof_data))

    # 2. Provenance check (skipped with --structural-only)
    if not structural_only:
        proof_py_path = proof_dir / "proof.py"
        if proof_py_path.exists():
            regenerated, err = run_proof_and_extract_json(proof_py_path)
            if err:
                errors.append(f"Provenance check failed: {err}")
            elif regenerated:
                diffs = compare_invariant_fields(proof_data, regenerated)
                errors.extend(diffs)
        else:
            errors.append("proof.py not found")

    # 3. Verdict cross-check
    proof_md_path = proof_dir / "proof.md"
    if proof_md_path.exists() and "verdict" in proof_data:
        md_verdict = extract_verdict_from_conclusion(proof_md_path)
        if md_verdict and md_verdict != proof_data["verdict"]:
            errors.append(
                f"Verdict mismatch: proof.md says '{md_verdict}', "
                f"proof.json says '{proof_data['verdict']}'"
            )
        elif not md_verdict:
            errors.append(
                "Could not extract verdict from proof.md Conclusion section — "
                "the Conclusion must contain one of the known verdict strings "
                "(PROVED, DISPROVED, PARTIALLY VERIFIED, UNDETERMINED)"
            )

    print_results(errors, warnings)
    sys.exit(1 if errors else 0)


def print_results(errors, warnings):
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if not errors:
        print("PASS")


if __name__ == "__main__":
    main()
