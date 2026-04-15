# tests/test_emit_format_version.py
import sys
import json
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path("proof-engine/skills/proof-engine/scripts")))
from computations import emit_proof_summary


def test_emit_injects_format_version_2():
    """Legacy emit_proof_summary should inject format_version: 2 if missing."""
    summary = {
        "fact_registry": {},
        "claim_formal": {"subject": "test"},
        "claim_natural": "test claim",
        "verdict": "PROVED",
        "key_results": {},
        "generator": {"name": "test", "version": "0.0.0", "repo": "", "generated_at": "2026-01-01"},
    }
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    emit_proof_summary(summary)
    sys.stdout = old_stdout
    output = captured.getvalue()

    marker = "=== PROOF SUMMARY (JSON) ==="
    json_str = output[output.index(marker) + len(marker):]
    result = json.loads(json_str)
    assert result["format_version"] == 2


def test_emit_preserves_explicit_format_version():
    """emit_proof_summary should not overwrite an explicit format_version."""
    summary = {
        "format_version": 3,
        "fact_registry": {},
        "claim_formal": {"subject": "test"},
        "claim_natural": "test claim",
        "verdict": "PROVED",
        "key_results": {},
        "generator": {"name": "test", "version": "0.0.0", "repo": "", "generated_at": "2026-01-01"},
    }
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    emit_proof_summary(summary)
    sys.stdout = old_stdout
    output = captured.getvalue()

    marker = "=== PROOF SUMMARY (JSON) ==="
    json_str = output[output.index(marker) + len(marker):]
    result = json.loads(json_str)
    assert result["format_version"] == 3
