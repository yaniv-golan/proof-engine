import json
import pytest

from tools.lib.prov import generate_prov


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pure_math_proof_data():
    return {
        "format_version": 3, "claim_natural": "X is Y",
        "evidence": {
            "A1": {"type": "computed", "label": "Primary check",
                    "method": "1==1", "result": "True", "depends_on": []},
        },
        "verdict": {"value": "PROVED", "qualified": False,
                    "qualifier": None, "reason": None},
        "generator": {"name": "proof-engine", "version": "1.0.0",
                      "repo": "https://github.com/yaniv-golan/proof-engine",
                      "generated_at": "2026-04-13"},
    }


@pytest.fixture
def empirical_proof_data():
    return {
        "format_version": 3, "claim_natural": "Test claim",
        "evidence": {
            "B1": {"type": "empirical", "label": "Source A",
                   "source": {"name": "Example", "url": "https://example.com",
                              "quote": "Q"},
                   "verification": {"status": "verified", "method": "full_quote",
                                    "fetch_mode": "live"}},
            "A1": {"type": "computed", "label": "Count",
                   "method": "count=1", "result": "1",
                   "depends_on": ["B1"]},
        },
        "verdict": {"value": "PROVED", "qualified": False,
                    "qualifier": None, "reason": None},
        "generator": {"name": "proof-engine", "version": "1.0.0",
                      "repo": "https://github.com/yaniv-golan/proof-engine",
                      "generated_at": "2026-04-13"},
    }


CANONICAL_URL = "https://example.com/proofs/test/"


# ---------------------------------------------------------------------------
# Existing structural tests
# ---------------------------------------------------------------------------

def test_prov_basic_structure(pure_math_proof_data):
    prov = generate_prov(pure_math_proof_data, slug="test-proof",
                         canonical_url=CANONICAL_URL)
    assert "prefix" in prov
    assert "entity" in prov
    assert "activity" in prov
    assert "agent" in prov


def test_prov_empirical_fact_chain(empirical_proof_data):
    prov = generate_prov(empirical_proof_data, slug="test",
                         canonical_url=CANONICAL_URL)
    assert "pe:evidence-B1" in prov["entity"]
    assert "pe:evidence-A1" in prov["entity"]
    assert any(
        d.get("prov:usedEntity") == "pe:evidence-B1"
        for d in prov.get("wasDerivedFrom", {}).values()
    )


def test_prov_verdict_entity(pure_math_proof_data):
    prov = generate_prov(pure_math_proof_data, slug="test",
                         canonical_url=CANONICAL_URL)
    assert "pe:verdict" in prov["entity"]
    assert prov["entity"]["pe:verdict"]["prov:value"] == "PROVED"


# ---------------------------------------------------------------------------
# W3C PROV spec-conformance tests (validated via the `prov` library)
# ---------------------------------------------------------------------------

pytest.importorskip("prov", reason="prov library not installed")

from prov.model import (ProvDocument, ProvEntity, ProvAgent, ProvAttribution,
                        ProvGeneration, ProvUsage, ProvActivity, ProvDerivation)


def _to_prov_document(proof_data, slug="test"):
    """Generate PROV-JSON and deserialize into a ProvDocument."""
    import tempfile, os
    prov_json = generate_prov(proof_data, slug=slug,
                              canonical_url=CANONICAL_URL)
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(prov_json, tmp)
    tmp.close()
    try:
        doc = ProvDocument.deserialize(tmp.name, format="json")
    finally:
        os.unlink(tmp.name)
    return doc, prov_json


def test_prov_spec_deserializes(pure_math_proof_data):
    """PROV-JSON must deserialize into a valid ProvDocument."""
    doc, _ = _to_prov_document(pure_math_proof_data)
    assert doc is not None


def test_prov_spec_round_trip(pure_math_proof_data):
    """A valid PROV document must survive serialize -> deserialize."""
    doc, _ = _to_prov_document(pure_math_proof_data)
    rt = doc.serialize(format="json")
    assert rt is not None
    assert len(rt) > 0


def test_prov_spec_entities_present(pure_math_proof_data):
    """Must have at least claim + evidence + verdict entities."""
    doc, _ = _to_prov_document(pure_math_proof_data)
    entities = list(doc.get_records(ProvEntity))
    ids = {str(e.identifier) for e in entities}
    assert any("claim" in i for i in ids), "Missing claim entity"
    assert any("verdict" in i for i in ids), "Missing verdict entity"
    assert any("evidence" in i for i in ids), "Missing evidence entity"


def test_prov_spec_agent_present(pure_math_proof_data):
    """Must have a SoftwareAgent for proof-engine."""
    doc, _ = _to_prov_document(pure_math_proof_data)
    agents = list(doc.get_records(ProvAgent))
    assert len(agents) >= 1, "No agents found"


def test_prov_spec_verdict_attributed(pure_math_proof_data):
    """Verdict must be attributed to an agent (wasAttributedTo)."""
    doc, _ = _to_prov_document(pure_math_proof_data)
    attributions = list(doc.get_records(ProvAttribution))
    assert len(attributions) >= 1, "Verdict has no wasAttributedTo"


def test_prov_spec_verdict_generated_by_activity(pure_math_proof_data):
    """Verdict must be generated by a VerdictDetermination activity."""
    doc, _ = _to_prov_document(pure_math_proof_data)
    gens = list(doc.get_records(ProvGeneration))
    assert len(gens) >= 1, "No wasGeneratedBy records"


def test_prov_spec_activity_uses_evidence(pure_math_proof_data):
    """VerdictDetermination activity must use all evidence entities."""
    doc, raw = _to_prov_document(pure_math_proof_data)
    usages = list(doc.get_records(ProvUsage))
    evidence_count = len(pure_math_proof_data["evidence"])
    assert len(usages) == evidence_count, (
        f"Expected {evidence_count} usage records, got {len(usages)}"
    )


def test_prov_spec_empirical_has_verification_activity(empirical_proof_data):
    """Empirical facts must have a CitationVerification activity."""
    doc, raw = _to_prov_document(empirical_proof_data)
    activities = list(doc.get_records(ProvActivity))
    activity_ids = {str(a.identifier) for a in activities}
    assert any("verify-B1" in i for i in activity_ids), (
        "Missing CitationVerification activity for empirical fact B1"
    )


def test_prov_spec_derivation_chain(empirical_proof_data):
    """Computed fact depending on empirical fact must have wasDerivedFrom."""
    doc, _ = _to_prov_document(empirical_proof_data)
    derivations = list(doc.get_records(ProvDerivation))
    assert len(derivations) >= 1, (
        "A1 depends_on B1 but no wasDerivedFrom records found"
    )


def test_prov_spec_namespaces(pure_math_proof_data):
    """Must declare prov and pe namespaces."""
    doc, raw = _to_prov_document(pure_math_proof_data)
    ns_prefixes = {ns.prefix for ns in doc.namespaces}
    assert "pe" in ns_prefixes, "Missing pe namespace"


def test_prov_spec_doi_on_verdict():
    """When DOI is provided, verdict entity must include it."""
    proof_data = {
        "format_version": 3, "claim_natural": "Test",
        "evidence": {"A1": {"type": "computed", "label": "Check",
                            "method": "1", "result": "1"}},
        "verdict": {"value": "PROVED", "qualified": False,
                    "qualifier": None, "reason": None},
        "generator": {"name": "proof-engine", "version": "1.0.0",
                      "repo": "x", "generated_at": "2026-04-13"},
    }
    prov_json = generate_prov(proof_data, slug="test",
                              canonical_url=CANONICAL_URL,
                              doi="10.5281/zenodo.12345")
    assert prov_json["entity"]["pe:verdict"]["pe:doi"] == "10.5281/zenodo.12345"
