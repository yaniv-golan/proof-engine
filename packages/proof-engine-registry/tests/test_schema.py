import json
from pathlib import Path

import pytest

from proof_engine_registry.schema import (
    Discovery, IndexEntry, Index, RegistryProof, Problem,
    to_json, from_json,
)


def test_discovery_round_trip():
    disco = Discovery(
        protocol_version="0.1",
        name="Test",
        homepage="https://example.com",
        publishes_supported=False,
        auth_required=False,
        proof_count=0,
        generated_at="2026-04-24T00:00:00Z",
        signing_key=None,
    )
    j = to_json(disco)
    assert j["protocol_version"] == "0.1"
    back = from_json(Discovery, j)
    assert back == disco


def test_index_entry_required_fields():
    entry = IndexEntry(
        claim_hash="a" * 64,
        slug="test-claim",
        claim="test claim",
        verdict="SUPPORTED",
        confidence=0.9,
        doi=None,
        proof_url="https://example.com/proofs/test-claim/",
        badge_url="https://example.com/proofs/test-claim/badge.json",
        generated_at="2026-04-24T00:00:00Z",
    )
    j = to_json(entry)
    assert set(j.keys()) == {
        "claim_hash", "slug", "claim", "verdict", "confidence",
        "doi", "proof_url", "badge_url", "generated_at",
    }


def test_index_contains_entries():
    entry = IndexEntry(
        claim_hash="a" * 64, slug="x", claim="x", verdict="SUPPORTED",
        confidence=1.0, doi=None,
        proof_url="https://e/proofs/x/", badge_url="https://e/proofs/x/badge.json",
        generated_at="2026-04-24T00:00:00Z",
    )
    idx = Index(
        protocol_version="0.1",
        generated_at="2026-04-24T00:00:00Z",
        entries=[entry],
    )
    j = to_json(idx)
    assert len(j["entries"]) == 1
    back = from_json(Index, j)
    assert back == idx


jsonschema = pytest.importorskip("jsonschema")

SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "schemas"


def _load(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text())


def test_discovery_payload_matches_schema():
    disco = Discovery(
        protocol_version="0.1", name="Test",
        homepage="https://example.com",
        publishes_supported=False, auth_required=False,
        proof_count=0, generated_at="2026-04-24T00:00:00Z",
        signing_key=None,
    )
    jsonschema.validate(to_json(disco), _load("registry-discovery.schema.json"))


def test_index_entry_payload_matches_schema():
    entry = IndexEntry(
        claim_hash="a" * 64, slug="x", claim="x",
        verdict="SUPPORTED", confidence=1.0, doi=None,
        proof_url="https://e/proofs/x/",
        badge_url="https://e/proofs/x/badge.json",
        generated_at="2026-04-24T00:00:00Z",
    )
    # The index.json contains an `entries` array; validate a single entry
    # against its item shape. Pull `items` out of the index schema for this.
    idx_schema = _load("registry-index.schema.json")
    item_schema = idx_schema["properties"]["entries"]["items"]
    jsonschema.validate(to_json(entry), item_schema)


def test_registry_proof_payload_matches_schema():
    rp = RegistryProof(
        claim_hash="a" * 64, slug="x", claim="x",
        verdict="SUPPORTED", confidence=1.0, doi=None,
        proof_url="https://e/proofs/x/",
        badge_url="https://e/proofs/x/badge.json",
        generated_at="2026-04-24T00:00:00Z",
        fact_ids=["B1"], source_urls=["https://example.com"],
        narrative_summary=None,
    )
    jsonschema.validate(to_json(rp), _load("registry-proof.schema.json"))


def test_problem_round_trip():
    p = Problem(
        type="https://proofengine.info/errors/not-found",
        status=404,
        title="Resource not found",
        detail="no proof with that claim_hash",
        code="not_found",
    )
    j = to_json(p)
    assert j["type"] == "https://proofengine.info/errors/not-found"
    assert j["status"] == 404
    assert j["code"] == "not_found"
    back = from_json(Problem, j)
    assert back == p


def test_problem_payload_matches_schema():
    p = Problem(
        type="https://proofengine.info/errors/not-found",
        status=404,
        title="Resource not found",
        detail="no proof with that claim_hash",
        code="not_found",
    )
    jsonschema.validate(to_json(p), _load("registry-problem.schema.json"))
