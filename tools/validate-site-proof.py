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
from tools.lib.narrative_validator import validate_narrative
from tools.lib.proof_runner import run_proof_and_extract_json
from tools.lib.normalize import normalize_to_v3

# Import ProofData to get the known keys for unknown-key detection
sys.path.insert(0, str(Path(__file__).parent.parent / "proof-engine" / "skills" / "proof-engine" / "scripts"))
from proof_types import ProofData

KNOWN_JSON_KEYS = set(typing.get_type_hints(ProofData).keys())

REQUIRED_JSON_KEYS = ["fact_registry", "claim_formal", "claim_natural",
                      "verdict", "key_results", "generator"]
REQUIRED_GENERATOR_KEYS = ["name", "version", "repo", "generated_at"]
REQUIRED_CLAIM_FORMAL_KEYS = []  # claim_formal structure varies by proof type
INVARIANT_FIELDS = ["verdict", "claim_formal", "claim_natural", "fact_registry", "key_results"]

KNOWN_JSON_KEYS_V3 = {
    "format_version", "claim_formal", "claim_natural", "evidence",
    "cross_checks", "adversarial_checks", "verdict", "key_results",
    "generator", "sub_claim_results", "date_note", "verdict_note",
    "verdict_reason", "data_value_verification",
}

# Keys within search_registry entries that are authored (should not drift)
SEARCH_REGISTRY_AUTHORED_KEYS = [
    "database", "url", "search_url", "query_terms",
    "date_range", "result_count", "source_name",
]


def validate_json_structure(proof_data):
    errors = []
    warnings = []
    is_v3 = proof_data.get("format_version") == 3

    if is_v3:
        known_keys = KNOWN_JSON_KEYS_V3
        required_keys = ["format_version", "claim_formal", "claim_natural",
                         "evidence", "verdict", "key_results", "generator"]
    else:
        known_keys = KNOWN_JSON_KEYS
        required_keys = REQUIRED_JSON_KEYS

    # Unknown key check
    unknown_keys = set(proof_data.keys()) - known_keys
    for key in sorted(unknown_keys):
        warnings.append(f"proof.json contains unknown key '{key}'")

    # Rejected keys
    REJECTED_KEYS = ["featured"]
    for key in REJECTED_KEYS:
        if key in proof_data:
            errors.append(
                f"proof.json contains rejected key '{key}' — "
                f"featured status is now managed via site/proofs/featured.json, "
                f"not per-proof. Remove this key."
            )

    # Required keys
    for key in required_keys:
        if key not in proof_data:
            errors.append(f"proof.json missing required key: {key}")

    # Generator validation
    if "generator" in proof_data:
        for key in REQUIRED_GENERATOR_KEYS:
            if key not in proof_data["generator"]:
                errors.append(f"generator missing key: {key}")

    if not is_v3:
        if "claim_formal" in proof_data:
            for key in REQUIRED_CLAIM_FORMAL_KEYS:
                if key not in proof_data["claim_formal"]:
                    errors.append(f"claim_formal missing key: {key}")

    # Verdict validation
    if "verdict" in proof_data:
        verdict = proof_data["verdict"]
        if is_v3:
            if not isinstance(verdict, dict):
                errors.append("v3 verdict must be a dict with 'value' key")
            elif "value" not in verdict:
                errors.append("v3 verdict dict missing 'value' key")
            else:
                v_str = verdict["value"]
                if verdict.get("qualified") and verdict.get("qualifier") == "unverified_citations":
                    v_str = f"{v_str} (with unverified citations)"
                if v_str not in VERDICT_TAXONOMY:
                    errors.append(f"Unknown verdict value: {v_str}")
        else:
            if verdict not in VERDICT_TAXONOMY:
                errors.append(f"Unknown verdict: {verdict}")

    # Absence proof: search evidence check
    claim_formal = proof_data.get("claim_formal", {})
    if claim_formal.get("proof_direction") == "absence":
        if is_v3:
            search_entries = {
                fid: e for fid, e in proof_data.get("evidence", {}).items()
                if e.get("type") == "search"
            }
            if not search_entries:
                errors.append("Absence proof missing search-type evidence entries")
            else:
                REQUIRED_SEARCH_FIELDS = [
                    "database", "url", "search_url", "query_terms",
                    "date_range", "result_count", "source_name",
                ]
                for fid, entry in search_entries.items():
                    search = entry.get("search", {})
                    for field in REQUIRED_SEARCH_FIELDS:
                        if field not in search:
                            errors.append(
                                f"evidence[{fid}].search missing authored field: {field}"
                            )
        else:
            if "search_registry" not in proof_data:
                errors.append("Absence proof (proof_direction=absence) missing required search_registry")

    # For v1/v2 absence proofs, validate authored search metadata hasn't drifted
    if not is_v3 and "search_registry" in proof_data:
        for key, entry in proof_data["search_registry"].items():
            for field in SEARCH_REGISTRY_AUTHORED_KEYS:
                if field not in entry:
                    errors.append(f"search_registry[{key}] missing authored field: {field}")

    return errors, warnings


def compare_invariant_fields(checked_in, regenerated):
    diffs = []

    # If checked-in is v3 but regenerated is v1/v2 (old proof.py), normalize
    if checked_in.get("format_version") == 3 and regenerated.get("format_version") != 3:
        regenerated = normalize_to_v3(regenerated)

    if checked_in.get("format_version") == 3:
        # Compare core fields
        for field in ["claim_formal", "claim_natural", "key_results"]:
            if checked_in.get(field) != regenerated.get(field):
                if field == "key_results" and _is_snapshot_file_degradation(checked_in, regenerated):
                    continue
                diffs.append(f"Field '{field}' diverges")

        # Verdict: compare base value only
        ci_v = checked_in.get("verdict", {})
        rg_v = regenerated.get("verdict", {})
        if isinstance(ci_v, dict) and isinstance(rg_v, dict):
            if ci_v.get("value") != rg_v.get("value"):
                if not _is_snapshot_file_degradation(checked_in, regenerated):
                    diffs.append("Verdict base value diverges")

        # Evidence: compare authored content per entry
        ci_evidence = checked_in.get("evidence", {})
        rg_evidence = regenerated.get("evidence", {})
        if set(ci_evidence.keys()) != set(rg_evidence.keys()):
            diffs.append("Evidence fact IDs diverge")
        else:
            for fid in ci_evidence:
                ci_e = ci_evidence[fid]
                rg_e = rg_evidence[fid]
                if ci_e.get("type") != rg_e.get("type"):
                    diffs.append(f"Evidence '{fid}' type diverges")
                if ci_e.get("label") != rg_e.get("label"):
                    diffs.append(f"Evidence '{fid}' label diverges")
                if ci_e.get("type") == "empirical":
                    ci_src = ci_e.get("source", {})
                    rg_src = rg_e.get("source", {})
                    if ci_src.get("url") != rg_src.get("url"):
                        diffs.append(f"Evidence '{fid}' source URL diverges")
                    if ci_src.get("quote") != rg_src.get("quote"):
                        diffs.append(f"Evidence '{fid}' source quote diverges")
                elif ci_e.get("type") == "computed":
                    if ci_e.get("method") != rg_e.get("method"):
                        diffs.append(f"Evidence '{fid}' computation method diverges")
                    if ci_e.get("result") != rg_e.get("result"):
                        if not _is_snapshot_file_degradation(checked_in, regenerated):
                            diffs.append(f"Evidence '{fid}' computation result diverges")
    else:
        for field in INVARIANT_FIELDS:
            val_a = checked_in.get(field)
            val_b = regenerated.get(field)
            if val_a != val_b:
                if field in ("verdict", "key_results") and _is_snapshot_file_degradation(checked_in, regenerated):
                    continue
                diffs.append(f"Field '{field}' diverges between checked-in and regenerated proof.json")

    return diffs


def _is_snapshot_file_degradation(checked_in, regenerated):
    """Check if difference is due to missing snapshot_file citations.

    Returns True if the regenerated proof shows degradation consistent
    with snapshot_file citations being unavailable (verdict gains
    "unverified citations" suffix, key_results counts change).
    """
    original_verdict = checked_in.get("verdict", "")
    new_verdict = regenerated.get("verdict", "")

    # v3 dict verdicts: check qualifier field
    if isinstance(new_verdict, dict):
        new_qualified = new_verdict.get("qualified", False) and \
                        new_verdict.get("qualifier") == "unverified_citations"
        orig_qualified = isinstance(original_verdict, dict) and \
                         original_verdict.get("qualified", False) and \
                         original_verdict.get("qualifier") == "unverified_citations"
        return new_qualified and not orig_qualified

    # v1/v2 string verdicts: substring check
    if "unverified citations" in new_verdict and "unverified citations" not in original_verdict:
        return True
    return False


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
    import argparse
    parser = argparse.ArgumentParser(
        description="Validate a proof submission for the Proof Engine site."
    )
    parser.add_argument("proof_dir", help="Path to the proof directory")
    parser.add_argument(
        "--structural-only",
        action="store_true",
        help="Skip provenance check (do not re-execute proof.py)",
    )
    parser.add_argument(
        "--candidate-slug",
        default=None,
        help="Slug the proof will be published under; used for self-reference "
             "check on depends_on. Defaults to the basename of proof_dir.",
    )
    args = parser.parse_args()

    structural_only = args.structural_only
    proof_dir = Path(args.proof_dir)
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
        json_verdict = proof_data["verdict"]
        if isinstance(json_verdict, dict):
            json_verdict_str = json_verdict.get("value", "")
            if json_verdict.get("qualified") and json_verdict.get("qualifier") == "unverified_citations":
                json_verdict_str = f"{json_verdict_str} (with unverified citations)"
        else:
            json_verdict_str = json_verdict

        if md_verdict and md_verdict != json_verdict_str:
            errors.append(
                f"Verdict mismatch: proof.md says '{md_verdict}', "
                f"proof.json says '{json_verdict_str}'"
            )
        elif not md_verdict:
            known = ", ".join(sorted(VERDICT_TAXONOMY.keys(), key=len))
            errors.append(
                "Could not extract verdict from proof.md Conclusion section — "
                "the Conclusion must contain one of the known verdict strings "
                f"({known})"
            )

    # 4. Narrative validation
    narrative_path = proof_dir / "proof_narrative.md"
    if narrative_path.exists():
        verdict_for_narrative = proof_data.get("verdict", "")
        if isinstance(verdict_for_narrative, dict):
            verdict_for_narrative = verdict_for_narrative.get("value", "")
            if proof_data["verdict"].get("qualified") and \
               proof_data["verdict"].get("qualifier") == "unverified_citations":
                verdict_for_narrative = f"{verdict_for_narrative} (with unverified citations)"

        narrative_errors, narrative_warnings = validate_narrative(
            narrative_path.read_text(),
            verdict=verdict_for_narrative,
            claim_natural=proof_data.get("claim_natural", ""),
        )
        errors.extend(narrative_errors)
        warnings.extend(narrative_warnings)
    else:
        errors.append("proof_narrative.md not found")

    # 5. depends_on validation (proof-local only — cross-proof checks run in
    # proof-site.py publish and tools/lib/depends_on.py:validate_repo).
    import yaml
    from tools.lib.depends_on import parse_depends_on, check_local

    meta_path = proof_dir / "meta.yaml"
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text()) or {}
        candidate_slug = args.candidate_slug or proof_dir.name
        depends_entries, dep_errors = parse_depends_on(
            meta, source=str(meta_path),
        )
        dep_errors.extend(check_local(
            depends_entries, candidate_slug=candidate_slug,
        ))
        errors.extend(dep_errors)

    # 6. Prose reference verification (skipped with --structural-only)
    # Rule 9 depends on resolved-identifier metadata in
    # depends_on_resolved.json, which is populated by network fetches
    # during publish. Structural-only mode runs without network and
    # without guaranteed cache presence, so treat prose verification
    # as a provenance-class check.
    if not structural_only:
        try:
            from tools.lib.prose_reference_scan import verify_prose as _vp
            vp_result = _vp(proof_dir)
            for e in vp_result.errors:
                errors.append(f"{e.file}:{e.line}: {e.message}")
        except Exception as e:
            errors.append(f"verify_prose raised {e}")

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
