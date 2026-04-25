import json

from tools.lib.cli_verdict import Verdict, RegistryHit, GeneratedProof


def test_verdict_from_registry():
    v = Verdict(
        schema_version="1.0",
        claim="The sky is blue.",
        claim_hash="a" * 64,
        source="registry",
        verdict="SUPPORTED",
        confidence=0.9,
        registry_hit=RegistryHit(
            registry_name="public",
            slug="sky-is-blue",
            proof_url="https://proofengine.info/proofs/sky-is-blue/",
            doi=None,
        ),
        generated=None,
        errors=[],
    )
    payload = v.to_json()
    assert payload["source"] == "registry"
    assert payload["generated"] is None
    assert payload["registry_hit"]["slug"] == "sky-is-blue"


def test_verdict_from_generation():
    v = Verdict(
        schema_version="1.0", claim="x", claim_hash="b" * 64,
        source="generated",
        verdict="PROVED", confidence=1.0,
        registry_hit=None,
        generated=GeneratedProof(
            output_dir="/tmp/out", proof_py="/tmp/out/proof.py",
            proof_md="/tmp/out/proof.md",
            proof_audit_md="/tmp/out/proof_audit.md",
            proof_narrative_md="/tmp/out/proof_narrative.md",
            model="opus", duration_seconds=42.0,
        ),
        errors=[],
    )
    payload = v.to_json()
    assert payload["generated"]["model"] == "opus"
    assert payload["generated"]["duration_seconds"] == 42.0


def test_verdict_exit_code_mapping():
    cases = {
        # Plain verdicts.
        "PROVED": 0,
        "SUPPORTED": 0,
        "PARTIALLY VERIFIED": 0,
        "DISPROVED": 1,
        "UNDETERMINED": 1,
        # Qualified-variant prefixes must map to the same family.
        # Canonical form is "VALUE (with <qualifier>)" — matches
        # tools/lib/verdict.py::VERDICT_TAXONOMY. See Phase 1b verdict_string.
        "SUPPORTED (with unverified citations)": 0,
        "PROVED (with unverified citations)": 0,
        "DISPROVED (with unverified citations)": 1,
        # Unknown strings fall through to exit 2.
        "MAYBE": 2,
        "": 2,
    }
    for verdict_value, expected_exit in cases.items():
        v = Verdict(
            schema_version="1.0", claim="x", claim_hash="c" * 64,
            source="registry", verdict=verdict_value, confidence=1.0,
            registry_hit=None, generated=None, errors=[],
        )
        assert v.exit_code() == expected_exit, verdict_value
