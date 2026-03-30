#!/usr/bin/env python3
"""Validate a proof submission for the Proof Engine site."""

import json
import re
import subprocess
import sys
import tempfile
import typing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.lib.verdict import VERDICT_TAXONOMY
from tools.lib.proof_runner import run_proof_and_extract_json

# Import ProofData to get the known keys for unknown-key detection
sys.path.insert(0, str(Path(__file__).parent.parent / "proof-engine" / "skills" / "proof-engine" / "scripts"))
from proof_types import ProofData

KNOWN_JSON_KEYS = set(typing.get_type_hints(ProofData).keys())

REQUIRED_JSON_KEYS = ["fact_registry", "claim_formal", "claim_natural",
                      "verdict", "key_results", "generator"]
REQUIRED_GENERATOR_KEYS = ["name", "version", "repo", "generated_at"]
REQUIRED_CLAIM_FORMAL_KEYS = []  # claim_formal structure varies by proof type
INVARIANT_FIELDS = ["verdict", "claim_formal", "claim_natural", "fact_registry", "key_results"]

# Keys within search_registry entries that are authored (should not drift)
SEARCH_REGISTRY_AUTHORED_KEYS = [
    "database", "url", "search_url", "query_terms",
    "date_range", "result_count", "source_name",
]


def validate_json_structure(proof_data):
    errors = []
    warnings = []

    # Check for unknown keys not in ProofData TypedDict
    unknown_keys = set(proof_data.keys()) - KNOWN_JSON_KEYS
    for key in sorted(unknown_keys):
        warnings.append(
            f"proof.json contains unknown key '{key}' — "
            f"add it to ProofData in proof_types.py to silence this warning"
        )

    # Reject deprecated keys that have been migrated to site-level config
    REJECTED_KEYS = ["featured"]
    for key in REJECTED_KEYS:
        if key in proof_data:
            errors.append(
                f"proof.json contains rejected key '{key}' — "
                f"featured status is now managed via site/proofs/featured.json, "
                f"not per-proof. Remove this key."
            )

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

    # Conditional: absence proofs require search_registry
    claim_formal = proof_data.get("claim_formal", {})
    if claim_formal.get("proof_direction") == "absence":
        if "search_registry" not in proof_data:
            errors.append("Absence proof (proof_direction=absence) missing required search_registry")

    # For absence proofs, validate authored search metadata hasn't drifted
    if "search_registry" in proof_data:
        for key, entry in proof_data["search_registry"].items():
            for field in SEARCH_REGISTRY_AUTHORED_KEYS:
                if field not in entry:
                    errors.append(f"search_registry[{key}] missing authored field: {field}")

    return errors, warnings


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
    # First try to match the explicit "**Verdict: X**" declaration
    verdict_decl = re.search(r"\*\*Verdict:\s*(.+?)\*\*", conclusion)
    if verdict_decl:
        declared = verdict_decl.group(1).strip()
        for verdict in sorted(VERDICT_TAXONOMY.keys(), key=len, reverse=True):
            if verdict in declared:
                return verdict
    # Fall back to searching the full conclusion text
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
    struct_errors, struct_warnings = validate_json_structure(proof_data)
    errors.extend(struct_errors)
    warnings.extend(struct_warnings)

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
            known = ", ".join(sorted(VERDICT_TAXONOMY.keys(), key=len))
            errors.append(
                "Could not extract verdict from proof.md Conclusion section — "
                "the Conclusion must contain one of the known verdict strings "
                f"({known})"
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
