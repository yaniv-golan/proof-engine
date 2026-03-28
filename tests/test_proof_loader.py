import json
import os
import pytest
import tempfile
import yaml
from tools.lib.proof_loader import load_proof, load_all_proofs


@pytest.fixture
def proof_dir(tmp_path):
    """Create a minimal valid proof directory."""
    slug_dir = tmp_path / "test-claim"
    slug_dir.mkdir()

    (slug_dir / "proof.md").write_text(
        "# Proof\n\n## Key Findings\n\n- Found it\n\n"
        "## Claim Interpretation\n\nMeans X.\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| B1 | X |\n\n"
        "## Proof Logic\n\nBecause Y.\n\n"
        "## Conclusion\n\nThe claim is PROVED.\n"
    )
    (slug_dir / "proof_audit.md").write_text(
        "# Audit\n\n## Hardening Checklist\n\nAll pass.\n"
    )
    (slug_dir / "proof.py").write_text("# proof script\n")
    (slug_dir / "proof.json").write_text(json.dumps({
        "fact_registry": {"B1": {"label": "test"}},
        "claim_formal": {
            "subject": "Test",
            "property": "value",
            "operator": ">",
            "operator_note": "Strictly greater",
            "threshold": 0,
        },
        "claim_natural": "Test claim is true",
        "verdict": "PROVED",
        "key_results": {"value": 1},
        "generator": {
            "name": "proof-engine",
            "version": "0.9.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2025-01-15",
        },
    }))
    return tmp_path


def test_load_proof_returns_dict(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert isinstance(proof, dict)
    assert proof["slug"] == "test-claim"


def test_load_proof_has_required_fields(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert "proof_data" in proof
    assert "sections_md" in proof
    assert "sections_audit" in proof
    assert "verdict" in proof
    assert "tags" in proof


def test_load_proof_extracts_verdict(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert proof["verdict"]["raw"] == "PROVED"


def test_load_proof_auto_tags(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert isinstance(proof["tags"], list)


def test_load_proof_meta_yaml_override(proof_dir):
    meta_path = proof_dir / "test-claim" / "meta.yaml"
    meta_path.write_text(yaml.dump({"tags": ["custom-tag", "Another Tag"]}))
    proof = load_proof(proof_dir / "test-claim")
    assert "custom-tag" in proof["tags"]
    assert "another-tag" in proof["tags"]


def test_load_proof_missing_generator_raises(proof_dir):
    data = json.loads((proof_dir / "test-claim" / "proof.json").read_text())
    del data["generator"]
    (proof_dir / "test-claim" / "proof.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="generator"):
        load_proof(proof_dir / "test-claim")


def test_load_proof_missing_required_section_raises(proof_dir):
    (proof_dir / "test-claim" / "proof.md").write_text(
        "# Proof\n\n## Key Findings\n\n- Found it\n"
    )
    with pytest.raises(ValueError, match="missing required"):
        load_proof(proof_dir / "test-claim")


def test_load_all_proofs(proof_dir):
    proofs = load_all_proofs(proof_dir)
    assert len(proofs) == 1
    assert proofs[0]["slug"] == "test-claim"


def test_load_proof_citation_count_empirical(proof_dir):
    data = json.loads((proof_dir / "test-claim" / "proof.json").read_text())
    data["citations"] = {"B1": {"status": "verified"}, "B2": {"status": "verified"}}
    (proof_dir / "test-claim" / "proof.json").write_text(json.dumps(data))
    proof = load_proof(proof_dir / "test-claim")
    assert proof["citation_count"] == 2


def test_load_proof_citation_count_pure_math(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert proof["citation_count"] is None


def test_load_proof_search_count(proof_dir):
    """Absence proof with search_registry should have search_count."""
    data = json.loads((proof_dir / "test-claim" / "proof.json").read_text())
    data["search_registry"] = {
        "search_a": {"database": "PubMed", "verification": {"status": "accessible"}},
        "search_b": {"database": "Cochrane", "verification": {"status": "accessible"}},
    }
    (proof_dir / "test-claim" / "proof.json").write_text(json.dumps(data))
    proof = load_proof(proof_dir / "test-claim")
    assert proof["search_count"] == 2


def test_load_proof_no_search_registry(proof_dir):
    """Proof without search_registry should have search_count None."""
    proof = load_proof(proof_dir / "test-claim")
    assert proof["search_count"] is None
