# tests/test_proof_runner_export.py
from tools.lib.proof_runner import KNOWN_PROOF_JSON_KEYS

def test_known_keys_exported():
    assert "claim_natural" in KNOWN_PROOF_JSON_KEYS
    assert "verdict" in KNOWN_PROOF_JSON_KEYS
    assert isinstance(KNOWN_PROOF_JSON_KEYS, set)
