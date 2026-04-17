import importlib.util
import json
import subprocess
import sys
import pytest
from pathlib import Path

# Load the hyphenated module
_spec = importlib.util.spec_from_file_location(
    "validate_site_proof",
    Path(__file__).parent.parent / "tools" / "validate-site-proof.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

validate_json_structure = _mod.validate_json_structure
INVARIANT_FIELDS = _mod.INVARIANT_FIELDS


def test_search_registry_not_in_invariant_fields():
    """search_registry as a whole is NOT an invariant (contains runtime status).
    Authored subfields are validated separately."""
    assert "search_registry" not in INVARIANT_FIELDS


def test_absence_proof_requires_search_registry():
    """Absence proof (proof_direction=absence) missing search_registry → error."""
    data = {
        "fact_registry": {},
        "claim_formal": {"proof_direction": "absence", "operator_note": "test"},
        "claim_natural": "test",
        "verdict": "SUPPORTED",
        "key_results": {},
        "generator": {"name": "proof-engine", "version": "0.11.0", "repo": "test", "generated_at": "2026-03-28"},
    }
    errors, _warnings = validate_json_structure(data)
    assert any("search_registry" in e for e in errors)


def test_non_absence_proof_no_search_registry_ok():
    """Non-absence proof without search_registry → no error."""
    data = {
        "fact_registry": {},
        "claim_formal": {"operator_note": "test"},
        "claim_natural": "test",
        "verdict": "PROVED",
        "key_results": {},
        "generator": {"name": "proof-engine", "version": "0.11.0", "repo": "test", "generated_at": "2026-03-28"},
    }
    errors, _warnings = validate_json_structure(data)
    assert not any("search_registry" in e for e in errors)


def test_absence_proof_search_metadata_validated():
    """Authored search metadata fields must be present and complete."""
    data = {
        "fact_registry": {},
        "claim_formal": {"proof_direction": "absence", "operator_note": "test"},
        "claim_natural": "test",
        "verdict": "SUPPORTED",
        "key_results": {},
        "search_registry": {
            "search_a": {
                "database": "PubMed",
                # missing url, search_url, query_terms, etc.
            }
        },
        "generator": {"name": "proof-engine", "version": "0.11.0", "repo": "test", "generated_at": "2026-03-28"},
    }
    errors, _warnings = validate_json_structure(data)
    assert any("missing authored field" in e for e in errors)


def test_supported_verdict_accepted():
    """SUPPORTED should be a valid verdict."""
    data = {
        "fact_registry": {},
        "claim_formal": {"operator_note": "test", "proof_direction": "absence"},
        "claim_natural": "test",
        "verdict": "SUPPORTED",
        "key_results": {},
        "search_registry": {"s1": {
            "database": "X", "url": "https://x.com", "search_url": "https://x.com/?q=y",
            "query_terms": ["y"], "date_range": "all", "result_count": 0, "source_name": "X",
        }},
        "generator": {"name": "proof-engine", "version": "0.11.0", "repo": "test", "generated_at": "2026-03-28"},
    }
    errors, _warnings = validate_json_structure(data)
    assert not any("Unknown verdict" in e for e in errors)


def test_supported_in_taxonomy():
    """SUPPORTED must be in VERDICT_TAXONOMY for dynamic error messages."""
    assert "SUPPORTED" in _mod.VERDICT_TAXONOMY


from tools.lib.narrative_validator import validate_narrative


def test_validate_narrative_imported():
    """validate_narrative is importable and callable."""
    errors, warnings = validate_narrative(
        "# Proof Narrative: Test claim is true\n\n"
        "## Verdict\n\n"
        "**Verdict: PROVED**\n\n"
        "Yes — the test claim is confirmed true beyond any reasonable doubt whatsoever. "
        "The evidence is overwhelming and consistent across every source examined.\n\n"
        "## What was claimed?\n\n"
        "Test claim is true. This matters for science "
        "and has real consequences for how we understand validity. "
        "Getting this right affects downstream decisions.\n\n"
        "## What did we find?\n\n"
        "We found strong evidence supporting the claim. "
        "Multiple independent sources confirmed the core assertion "
        "from different angles and methodologies. "
        "The data was consistent across all measurements taken "
        "over the full range of conditions tested. "
        "No contradictory evidence was identified in any source examined. "
        "The primary computation matched theoretical predictions within tight tolerance. "
        "Secondary verification through independent calculation confirmed the same figure. "
        "Cross-referencing against published reference data showed agreement within one percent. "
        "Statistical significance exceeds conventional thresholds by a wide margin. "
        "Adversarial scenarios designed to break the conclusion all failed to do so. "
        "The underlying dataset was large and diverse enough to support strong conclusions. "
        "Sensitivity analysis showed the result is robust to reasonable assumption changes. "
        "Peer-reviewed literature is consistent with the finding across multiple domains. "
        "No methodological flaws were identified that could invalidate the conclusion.\n\n"
        "## What should you keep in mind?\n\n"
        "This covers the specific claim as stated only. "
        "Different framings might yield different results. "
        "The methodology is optimized for quantitative claims.\n\n"
        "## How was this verified?\n\n"
        "Verified through computation. "
        "See [the structured proof report](proof.md), "
        "[the full verification audit](proof_audit.md), "
        "or [re-run the proof yourself](proof.py).\n",
        verdict="PROVED",
        claim_natural="Test claim is true",
    )
    assert errors == []


def test_validate_site_proof_missing_narrative(tmp_path):
    """validate-site-proof.py --structural-only should error when proof_narrative.md is missing."""
    proof_dir = tmp_path / "test-claim"
    proof_dir.mkdir()
    (proof_dir / "proof.py").write_text("# proof\n")
    (proof_dir / "proof.md").write_text(
        "# Proof\n\n## Key Findings\n\nDone.\n\n"
        "## Claim Interpretation\n\nMeans X.\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| A1 | X |\n\n"
        "## Proof Logic\n\nBecause Y.\n\n"
        "## Conclusion\n\nThe claim is PROVED.\n"
    )
    (proof_dir / "proof_audit.md").write_text("# Audit\n\n## Hardening Checklist\n\nAll pass.\n")
    (proof_dir / "proof.json").write_text(json.dumps({
        "fact_registry": {},
        "claim_formal": {"subject": "X", "property": "Y", "operator": ">",
                         "operator_note": "gt", "threshold": 0},
        "claim_natural": "Test",
        "verdict": "PROVED",
        "key_results": {"val": 1},
        "generator": {"name": "proof-engine", "version": "1.0.0",
                       "repo": "https://github.com/yaniv-golan/proof-engine",
                       "generated_at": "2026-01-01"},
    }))
    result = subprocess.run(
        [sys.executable, "tools/validate-site-proof.py", str(proof_dir), "--structural-only"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "proof_narrative.md" in result.stdout or "proof_narrative.md" in result.stderr


def test_v3_proof_passes_validation(tmp_path):
    """A valid v3 proof passes structural validation."""
    v3 = {
        "format_version": 3,
        "claim_natural": "Test",
        "claim_formal": {"subject": "X", "property": "Y"},
        "evidence": {
            "A1": {"type": "computed", "label": "Test", "method": "1+1", "result": "2"},
        },
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "key_results": {"x": 1},
        "generator": {"name": "proof-engine", "version": "1.0.0", "repo": "x", "generated_at": "2026-01-01"},
        "cross_checks": [],
        "adversarial_checks": [],
    }
    errors, warnings = validate_json_structure(v3)
    assert errors == [], f"Unexpected errors: {errors}"


def test_validate_site_proof_narrative_verdict_mismatch(tmp_path):
    """validate-site-proof.py --structural-only should error on verdict mismatch in narrative."""
    proof_dir = tmp_path / "test-claim"
    proof_dir.mkdir()
    (proof_dir / "proof.py").write_text("# proof\n")
    (proof_dir / "proof.md").write_text(
        "# Proof\n\n## Key Findings\n\nDone.\n\n"
        "## Claim Interpretation\n\nMeans X.\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| A1 | X |\n\n"
        "## Proof Logic\n\nBecause Y.\n\n"
        "## Conclusion\n\nThe claim is PROVED.\n"
    )
    (proof_dir / "proof_audit.md").write_text("# Audit\n\n## Hardening Checklist\n\nAll pass.\n")
    (proof_dir / "proof.json").write_text(json.dumps({
        "fact_registry": {},
        "claim_formal": {"subject": "X", "property": "Y", "operator": ">",
                         "operator_note": "gt", "threshold": 0},
        "claim_natural": "Test claim is true",
        "verdict": "PROVED",
        "key_results": {"val": 1},
        "generator": {"name": "proof-engine", "version": "1.0.0",
                       "repo": "https://github.com/yaniv-golan/proof-engine",
                       "generated_at": "2026-01-01"},
    }))
    # Narrative says DISPROVED but proof.json says PROVED
    (proof_dir / "proof_narrative.md").write_text(
        "# Proof Narrative: Test claim is true\n\n"
        "## Verdict\n\n**Verdict: DISPROVED**\n\n"
        "The claim turned out to be false when examined against the available evidence. "
        "Multiple sources contradicted the core assertion from different angles.\n\n"
        "## What was claimed?\n\nTest claim is true. This matters.\n\n"
        "## What did we find?\n\n"
        "We found that the claim does not hold under scrutiny. "
        "Multiple independent sources contradicted the core assertion "
        "from different angles and methodologies. "
        "The data was inconsistent across all measurements taken "
        "over the full range of conditions tested. "
        "Contradictory evidence was identified in every source. "
        "The primary computation did not match theoretical predictions. "
        "Secondary verification through independent calculation confirmed the mismatch. "
        "Cross-referencing against published reference data showed disagreement. "
        "Statistical significance was below conventional thresholds. "
        "Adversarial scenarios designed to confirm the conclusion all failed.\n\n"
        "## What should you keep in mind?\n\nScope is limited.\n\n"
        "## How was this verified?\n\n"
        "See [the structured proof report](proof.md), "
        "[the full verification audit](proof_audit.md), "
        "or [re-run the proof yourself](proof.py).\n"
    )
    result = subprocess.run(
        [sys.executable, "tools/validate-site-proof.py", str(proof_dir), "--structural-only"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "does not match" in result.stdout or "does not match" in result.stderr


def test_validate_site_proof_rejects_unknown_relation(tmp_path):
    """validate-site-proof.py exits non-zero when meta.yaml depends_on uses an
    unknown relation, even when --candidate-slug is supplied."""
    import yaml
    proof_dir = tmp_path / "candidate-slug"
    proof_dir.mkdir()
    (proof_dir / "proof.json").write_text(json.dumps({
        "format_version": 3,
        "claim_formal": {"operator_note": "x"},
        "claim_natural": "test",
        "evidence": {},
        "verdict": {"value": "PROVED"},
        "key_results": {},
        "generator": {
            "name": "proof-engine", "version": "1.0", "repo": "x",
            "generated_at": "2026-04-17",
        },
    }))
    (proof_dir / "proof.py").write_text("# x\n")
    (proof_dir / "proof.md").write_text("# x\n")
    (proof_dir / "proof_audit.md").write_text("# x\n")
    (proof_dir / "proof_narrative.md").write_text("# x\n")
    meta = {
        "tags": ["test"],
        "depends_on": [
            {"relation": "Bogus",
             "identifiers": [{"type": "slug", "value": "u"}]},
        ],
    }
    (proof_dir / "meta.yaml").write_text(yaml.dump(meta))

    tool = Path(__file__).parent.parent / "tools" / "validate-site-proof.py"
    result = subprocess.run(
        [sys.executable, str(tool), "--structural-only", str(proof_dir),
         "--candidate-slug", "candidate-slug"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "Bogus" in (result.stdout + result.stderr)


def test_validate_site_proof_fails_on_prose_mismatch(tmp_path):
    import subprocess, sys, shutil
    from pathlib import Path as P
    REPO = P(__file__).resolve().parent.parent
    src = REPO / "tests" / "fixtures" / "prose_refs" / "bad_attribution_proof"
    dst = tmp_path / "staged"
    shutil.copytree(src, dst)
    (dst / "proof.py").write_text("print('{}')")
    (dst / "proof.json").write_text('{"claim_natural":"x"}')
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "validate-site-proof.py"),
         "--structural-only", str(dst),
         "--candidate-slug", "bad_attribution_proof"],
        capture_output=True, text=True,
    )
    combined = r.stdout + r.stderr
    if r.returncode == 0:
        import pytest
        pytest.fail(f"validate-site-proof should have failed on prose mismatch; got {combined!r}")
