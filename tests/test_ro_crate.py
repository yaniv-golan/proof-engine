import json
import pytest


def test_ro_crate_basic_structure():
    from tools.lib.ro_crate import generate_ro_crate
    result = generate_ro_crate(
        proof_data={"format_version": 3, "claim_natural": "Test claim",
                     "verdict": {"value": "PROVED", "qualified": False},
                     "generator": {"name": "proof-engine", "version": "1.0.0",
                                   "repo": "https://github.com/yaniv-golan/proof-engine",
                                   "generated_at": "2026-04-13"}},
        slug="test-proof", canonical_url="https://example.com/proofs/test-proof/",
        available_files=["proof.py", "proof.json", "proof.md", "proof_audit.md",
                         "proof_narrative.md", "provenance.json", "proof.ipynb"],
    )
    assert result["@context"] == "https://w3id.org/ro/crate/1.1/context"
    graph = {item["@id"]: item for item in result["@graph"]}
    assert "./" in graph
    root = graph["./"]
    assert root["@type"] == "Dataset"
    assert "proof.py" in [p["@id"] for p in root["hasPart"]]


def test_ro_crate_proof_py_typed():
    from tools.lib.ro_crate import generate_ro_crate
    result = generate_ro_crate(
        proof_data=_minimal_proof_data(), slug="test",
        canonical_url="https://example.com/proofs/test/",
        available_files=["proof.py", "proof.json"],
    )
    graph = {item["@id"]: item for item in result["@graph"]}
    assert graph["proof.py"]["@type"] == "SoftwareSourceCode"
    assert graph["proof.json"]["@type"] == "Dataset"


def test_ro_crate_includes_doi():
    from tools.lib.ro_crate import generate_ro_crate
    result = generate_ro_crate(
        proof_data=_minimal_proof_data(), slug="test",
        canonical_url="https://example.com/proofs/test/",
        available_files=["proof.py"],
        doi="10.5281/zenodo.12345",
    )
    graph = {item["@id"]: item for item in result["@graph"]}
    root = graph["./"]
    assert root.get("identifier") == "https://doi.org/10.5281/zenodo.12345"


def test_ro_crate_only_includes_existing_files():
    from tools.lib.ro_crate import generate_ro_crate
    result = generate_ro_crate(
        proof_data=_minimal_proof_data(), slug="test",
        canonical_url="https://example.com/proofs/test/",
        available_files=["proof.py", "proof.json"],
    )
    graph = {item["@id"]: item for item in result["@graph"]}
    assert "provenance.json" not in graph


def _minimal_proof_data():
    return {"format_version": 3, "claim_natural": "Test",
            "verdict": {"value": "PROVED", "qualified": False},
            "generator": {"name": "proof-engine", "version": "1.0.0",
                          "repo": "https://github.com/yaniv-golan/proof-engine",
                          "generated_at": "2026-04-13"}}
