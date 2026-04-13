# tests/test_normalize.py

import pytest


def test_normalize_empirical_proof():
    """v1 empirical proof converts to v3 evidence map."""
    from tools.lib.normalize import normalize_to_v3

    v1 = {
        "fact_registry": {
            "B1": {"key": "source_a", "label": "Source A confirms claim"},
            "A1": {"label": "Source count", "method": "count = 1", "result": "1"},
        },
        "claim_formal": {"subject": "X", "property": "Y", "operator": ">=", "threshold": 1},
        "claim_natural": "X is Y",
        "citations": {
            "B1": {
                "source_key": "source_a",
                "source_name": "Source A",
                "url": "https://example.com",
                "quote": "X is definitely Y",
                "status": "verified",
                "method": "full_quote",
                "coverage_pct": 100.0,
                "fetch_mode": "live",
                "credibility": {"domain": "example.com", "tier": 3, "source_type": "reference"},
            }
        },
        "extractions": {
            "B1": {"value": "confirmed", "value_in_quote": True, "quote_snippet": "X is definitely Y"},
        },
        "cross_checks": [
            {"description": "Sources agree", "n_sources_consulted": 1, "agreement": True}
        ],
        "adversarial_checks": [
            {"question": "Any counter-evidence?", "finding": "No", "breaks_proof": False}
        ],
        "verdict": "PROVED",
        "key_results": {"n_confirmed": 1},
        "generator": {"name": "proof-engine", "version": "1.0.0", "repo": "https://github.com/x", "generated_at": "2026-01-01"},
    }

    v3 = normalize_to_v3(v1)

    assert v3["format_version"] == 3

    # Evidence map created
    assert "evidence" in v3
    assert "B1" in v3["evidence"]
    assert v3["evidence"]["B1"]["type"] == "empirical"
    assert v3["evidence"]["B1"]["source"]["name"] == "Source A"
    assert v3["evidence"]["B1"]["source"]["url"] == "https://example.com"
    assert v3["evidence"]["B1"]["verification"]["status"] == "verified"
    assert v3["evidence"]["B1"]["extraction"]["value"] == "confirmed"

    # Computed fact
    assert "A1" in v3["evidence"]
    assert v3["evidence"]["A1"]["type"] == "computed"
    assert v3["evidence"]["A1"]["method"] == "count = 1"

    # Structured verdict
    assert isinstance(v3["verdict"], dict)
    assert v3["verdict"]["value"] == "PROVED"
    assert v3["verdict"]["qualified"] is False

    # Old parallel dicts removed
    assert "fact_registry" not in v3
    assert "citations" not in v3
    assert "extractions" not in v3

    # Cross-checks get empty fact_ids if not present
    assert v3["cross_checks"][0].get("fact_ids") == []

    # Other fields preserved
    assert v3["claim_formal"]["subject"] == "X"
    assert v3["adversarial_checks"][0]["question"] == "Any counter-evidence?"


def test_normalize_qualified_verdict():
    from tools.lib.normalize import normalize_to_v3

    v1 = _minimal_v1(verdict="PROVED (with unverified citations)")
    v3 = normalize_to_v3(v1)
    assert v3["verdict"]["value"] == "PROVED"
    assert v3["verdict"]["qualified"] is True
    assert v3["verdict"]["qualifier"] == "unverified_citations"


def test_normalize_v3_passthrough():
    """Already v3 — return as-is."""
    from tools.lib.normalize import normalize_to_v3

    v3_input = {
        "format_version": 3,
        "evidence": {"A1": {"type": "computed", "label": "test"}},
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "claim_formal": {}, "claim_natural": "test", "key_results": {},
        "generator": {"name": "proof-engine", "version": "1.0.0", "repo": "x", "generated_at": "2026-01-01"},
    }
    result = normalize_to_v3(v3_input)
    assert result is v3_input  # same object, no copy


def test_normalize_compound_subclaim_inference():
    """Sub-claim inferred from label prefix 'SC1: ...' and key prefix 'sc1_'."""
    from tools.lib.normalize import normalize_to_v3

    v1 = _minimal_v1()
    v1["fact_registry"] = {
        "B1": {"key": "sc1_source_a", "label": "SC1: NHS confirms UPFs"},
        "B2": {"key": "sc2_source_a", "label": "SC2: WHO study"},
        "A1": {"label": "SC1 source count", "method": "count", "result": "1"},
    }
    v1["citations"] = {
        "B1": {"source_key": "sc1_source_a", "source_name": "NHS", "url": "https://nhs.uk",
               "quote": "q", "status": "verified", "method": "full_quote",
               "fetch_mode": "live", "credibility": {}},
        "B2": {"source_key": "sc2_source_a", "source_name": "WHO", "url": "https://who.int",
               "quote": "q", "status": "verified", "method": "full_quote",
               "fetch_mode": "live", "credibility": {}},
    }

    v3 = normalize_to_v3(v1)
    assert v3["evidence"]["B1"]["sub_claim"] == "SC1"
    assert v3["evidence"]["B2"]["sub_claim"] == "SC2"
    # A1 inferred from label prefix
    assert v3["evidence"]["A1"]["sub_claim"] == "SC1"


def test_normalize_search_registry():
    """S-type facts map from search_registry."""
    from tools.lib.normalize import normalize_to_v3

    v1 = _minimal_v1()
    v1["fact_registry"]["S1"] = {"key": "pubmed", "label": "PubMed search"}
    v1["search_registry"] = {
        "pubmed": {
            "database": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov/",
            "search_url": "https://pubmed.ncbi.nlm.nih.gov/?term=test",
            "query_terms": "test", "date_range": "all", "result_count": 0,
            "source_name": "PubMed",
        }
    }
    v1["claim_formal"]["proof_direction"] = "absence"

    v3 = normalize_to_v3(v1)
    assert v3["evidence"]["S1"]["type"] == "search"
    assert v3["evidence"]["S1"]["search"]["database"] == "PubMed"
    assert "search_registry" not in v3


def test_normalize_prefix_matched_extractions():
    """Extraction keys like B1_napoleon_height match fact_id B1."""
    from tools.lib.normalize import normalize_to_v3

    v1 = _minimal_v1()
    v1["fact_registry"] = {
        "B1": {"key": "source_a", "label": "Height source"},
    }
    v1["citations"] = {
        "B1": {"source_name": "Wikipedia", "url": "https://en.wikipedia.org",
               "quote": "Napoleon was 1.69m tall", "status": "verified",
               "method": "full_quote", "fetch_mode": "live", "credibility": {}},
    }
    v1["extractions"] = {
        "B1_napoleon_height": {"value": "1.69", "value_in_quote": True,
                                "quote_snippet": "Napoleon was 1.69m tall"},
    }

    v3 = normalize_to_v3(v1)
    assert v3["evidence"]["B1"]["extraction"]["value"] == "1.69"
    assert v3["evidence"]["B1"]["extraction"]["value_in_quote"] is True


def test_normalize_preserves_optional_fields():
    from tools.lib.normalize import normalize_to_v3

    v1 = _minimal_v1()
    v1["date_note"] = "Time-sensitive proof"
    v1["sub_claim_results"] = [{"id": "SC1", "holds": True}]
    v1["verdict_note"] = "Note"
    v1["data_value_verification"] = {"B1": {"val": {"found": True}}}

    v3 = normalize_to_v3(v1)
    assert v3["date_note"] == "Time-sensitive proof"
    assert v3["sub_claim_results"] == [{"id": "SC1", "holds": True}]
    assert v3["verdict_note"] == "Note"
    assert "data_value_verification" in v3


# --- Helper ---

def _minimal_v1(verdict="PROVED"):
    return {
        "fact_registry": {"A1": {"label": "Test", "method": "test", "result": "1"}},
        "claim_formal": {"subject": "X", "property": "Y", "operator": "==", "threshold": 1},
        "claim_natural": "X is Y",
        "verdict": verdict,
        "key_results": {"result": 1},
        "generator": {"name": "proof-engine", "version": "1.0.0", "repo": "x", "generated_at": "2026-01-01"},
    }
