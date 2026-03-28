import importlib.util
import json
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
    errors = validate_json_structure(data)
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
    errors = validate_json_structure(data)
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
    errors = validate_json_structure(data)
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
    errors = validate_json_structure(data)
    assert not any("Unknown verdict" in e for e in errors)


def test_supported_in_taxonomy():
    """SUPPORTED must be in VERDICT_TAXONOMY for dynamic error messages."""
    assert "SUPPORTED" in _mod.VERDICT_TAXONOMY
