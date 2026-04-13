# tests/test_schema_validation.py

import json
from pathlib import Path
import pytest

SCHEMA_PATH = Path(__file__).parent.parent / "proof-engine" / "skills" / "proof-engine" / "references" / "proof-schema.json"


def test_schema_file_exists():
    assert SCHEMA_PATH.exists(), f"Schema not found at {SCHEMA_PATH}"


def test_schema_is_valid_json():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
    assert schema.get("type") == "object"


def test_schema_requires_v3_keys():
    schema = json.loads(SCHEMA_PATH.read_text())
    required = schema.get("required", [])
    for key in ["format_version", "claim_natural", "claim_formal",
                "evidence", "verdict", "key_results", "generator"]:
        assert key in required, f"'{key}' should be required"


def test_v3_proof_validates_against_schema():
    """A well-formed v3 proof.json validates against the schema."""
    try:
        import jsonschema
    except ImportError:
        pytest.skip("jsonschema not installed")

    schema = json.loads(SCHEMA_PATH.read_text())
    v3_proof = {
        "format_version": 3,
        "claim_natural": "Test claim",
        "claim_formal": {"subject": "X", "property": "Y", "operator": "==", "threshold": 1},
        "evidence": {
            "A1": {
                "type": "computed",
                "label": "Primary check",
                "method": "1 == 1",
                "result": "True",
            }
        },
        "cross_checks": [],
        "adversarial_checks": [],
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "key_results": {"claim_holds": True},
        "generator": {
            "name": "proof-engine", "version": "1.0.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-04-13",
        },
    }
    jsonschema.validate(v3_proof, schema)  # raises on failure


def test_v1_proof_fails_schema():
    """A v1 proof.json (no evidence key) fails validation."""
    try:
        import jsonschema
    except ImportError:
        pytest.skip("jsonschema not installed")

    schema = json.loads(SCHEMA_PATH.read_text())
    v1_proof = {
        "fact_registry": {"A1": {"label": "Test"}},
        "claim_natural": "Test",
        "claim_formal": {},
        "verdict": "PROVED",
        "key_results": {},
        "generator": {"name": "proof-engine", "version": "1.0.0", "repo": "x", "generated_at": "2026-01-01"},
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(v1_proof, schema)
