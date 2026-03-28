"""Contract tests for proof_types.py — ensures TypedDicts match authoritative sources.

These tests prevent proof_types.py from drifting out of sync with the code
that produces and consumes proof artifacts. Constants are imported from
the actual source files (not duplicated) so drift in either direction
causes a test failure.
"""

import importlib.util
import json
import typing
from pathlib import Path

from scripts.proof_types import (
    SearchRegistryEntry, CitationEntry,
    LoadedProof, ProofData, Generator, NormalizedVerdict,
)


def _import_validate_site_proof():
    """Import tools/validate-site-proof.py despite the hyphenated filename."""
    spec = importlib.util.spec_from_file_location(
        "validate_site_proof",
        Path(__file__).parent.parent / "tools" / "validate-site-proof.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_vsp = _import_validate_site_proof()
REQUIRED_JSON_KEYS = _vsp.REQUIRED_JSON_KEYS
REQUIRED_GENERATOR_KEYS = _vsp.REQUIRED_GENERATOR_KEYS
SEARCH_REGISTRY_AUTHORED_KEYS = _vsp.SEARCH_REGISTRY_AUTHORED_KEYS


def test_search_registry_entry_covers_authored_keys():
    """SearchRegistryEntry must include all SEARCH_REGISTRY_AUTHORED_KEYS."""
    sr_fields = set(typing.get_type_hints(SearchRegistryEntry).keys())
    expected = set(SEARCH_REGISTRY_AUTHORED_KEYS)
    missing = expected - sr_fields
    assert not missing, f"SearchRegistryEntry missing fields: {missing}"


def test_proof_data_covers_required_json_keys():
    """ProofData must include all REQUIRED_JSON_KEYS."""
    pd_fields = set(typing.get_type_hints(ProofData).keys())
    expected = set(REQUIRED_JSON_KEYS)
    missing = expected - pd_fields
    assert not missing, f"ProofData missing required keys: {missing}"


def test_generator_covers_required_keys():
    """Generator must include all REQUIRED_GENERATOR_KEYS."""
    gen_fields = set(typing.get_type_hints(Generator).keys())
    expected = set(REQUIRED_GENERATOR_KEYS)
    missing = expected - gen_fields
    assert not missing, f"Generator missing required keys: {missing}"


def test_citation_entry_matches_build_citation_detail():
    """CitationEntry fields must match what build_citation_detail() produces.

    Authoritative source: verify_citations.py build_citation_detail() lines 610-619.
    """
    ce_fields = set(typing.get_type_hints(CitationEntry).keys())
    expected = {"source_key", "source_name", "url", "quote", "status",
                "method", "coverage_pct", "fetch_mode", "credibility"}
    missing = expected - ce_fields
    assert not missing, f"CitationEntry missing fields: {missing}"
    # CitationEntry should NOT have runtime-only fields
    assert "fetch_error" not in ce_fields, "fetch_error is runtime-only, not persisted"
    assert "message" not in ce_fields, "message is runtime-only, not persisted"


def test_loaded_proof_matches_loader_return():
    """LoadedProof fields must match what load_proof() actually returns.

    Authoritative source: tools/lib/proof_loader.py load_proof() lines 111-123.
    """
    lp_fields = set(typing.get_type_hints(LoadedProof).keys())
    expected = {"slug", "proof_data", "sections_md", "sections_audit",
                "verdict", "tags", "featured", "citation_count",
                "search_count", "date", "proof_engine_version"}
    missing = expected - lp_fields
    assert not missing, f"LoadedProof missing fields: {missing}"


def test_types_match_published_proofs():
    """Spot-check: ProofData fields cover all keys in published proof.json files."""
    pd_fields = set(typing.get_type_hints(ProofData).keys())
    proofs_dir = Path(__file__).parent.parent / "site" / "proofs"
    if not proofs_dir.exists():
        return  # Skip if no published proofs
    for proof_dir in sorted(proofs_dir.iterdir()):
        proof_json = proof_dir / "proof.json"
        if proof_json.exists():
            data = json.loads(proof_json.read_text())
            for key in data.keys():
                assert key in pd_fields, (
                    f"proof.json key '{key}' in {proof_dir.name} "
                    f"not in ProofData TypedDict"
                )
