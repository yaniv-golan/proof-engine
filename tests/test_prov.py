import json
import pytest


def test_prov_basic_structure():
    from tools.lib.prov import generate_prov
    proof_data = {
        "format_version": 3, "claim_natural": "X is Y",
        "evidence": {"A1": {"type": "computed", "label": "Primary check", "method": "1==1", "result": "True", "depends_on": []}},
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "generator": {"name": "proof-engine", "version": "1.0.0", "repo": "x", "generated_at": "2026-04-13"},
    }
    prov = generate_prov(proof_data, slug="test-proof", canonical_url="https://example.com/proofs/test-proof/")
    assert "prefix" in prov
    assert "entity" in prov
    assert "activity" in prov
    assert "agent" in prov


def test_prov_empirical_fact_chain():
    from tools.lib.prov import generate_prov
    proof_data = {
        "format_version": 3, "claim_natural": "Test",
        "evidence": {
            "B1": {"type": "empirical", "label": "Source A",
                   "source": {"name": "Example", "url": "https://example.com", "quote": "Q"},
                   "verification": {"status": "verified", "method": "full_quote", "fetch_mode": "live"}},
            "A1": {"type": "computed", "label": "Count", "method": "count=1", "result": "1", "depends_on": ["B1"]},
        },
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "generator": {"name": "proof-engine", "version": "1.0.0", "repo": "x", "generated_at": "2026-04-13"},
    }
    prov = generate_prov(proof_data, slug="test", canonical_url="https://example.com/proofs/test/")
    assert "pe:evidence-B1" in prov["entity"]
    assert "pe:evidence-A1" in prov["entity"]
    assert any(d.get("prov:usedEntity") == "pe:evidence-B1" for d in prov.get("wasDerivedFrom", {}).values())


def test_prov_verdict_entity():
    from tools.lib.prov import generate_prov
    proof_data = {
        "format_version": 3, "claim_natural": "Test",
        "evidence": {"A1": {"type": "computed", "label": "Check", "method": "1", "result": "1"}},
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "generator": {"name": "proof-engine", "version": "1.0.0", "repo": "x", "generated_at": "2026-04-13"},
    }
    prov = generate_prov(proof_data, slug="test", canonical_url="https://example.com/proofs/test/")
    assert "pe:verdict" in prov["entity"]
    assert prov["entity"]["pe:verdict"]["prov:value"] == "PROVED"
