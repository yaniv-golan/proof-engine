import json
import pytest
import yaml
from unittest.mock import patch, MagicMock
from pathlib import Path


def _make_proof_dir(tmp_path, slug="test-proof", claim="Test claim about health",
                    tags=None, tags_manual=False):
    """Create a minimal proof directory for retag testing."""
    proof_dir = tmp_path / slug
    proof_dir.mkdir()
    (proof_dir / "proof.json").write_text(json.dumps({
        "claim_natural": claim,
        "verdict": "PROVED",
    }))
    if tags is not None:
        meta = {"tags": tags}
        if tags_manual:
            meta["tags_manual"] = True
        (proof_dir / "meta.yaml").write_text(yaml.dump(meta, default_flow_style=False))
    return proof_dir


# Import retag_proof by loading the module dynamically (hyphen in filename)
import importlib.util
import sys

_spec = importlib.util.spec_from_file_location(
    "retag_proofs", Path(__file__).parent.parent / "tools" / "retag-proofs.py"
)
_retag_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_retag_mod)
retag_proof = _retag_mod.retag_proof


@patch("tools.lib.tagger.subprocess.run")
def test_retag_skips_manual_tags(mock_run, tmp_path):
    proof_dir = _make_proof_dir(tmp_path, tags=["economics"], tags_manual=True)
    result = retag_proof(proof_dir)
    assert result is False
    mock_run.assert_not_called()


@patch("tools.lib.tagger.subprocess.run")
def test_retag_raises_on_llm_failure(mock_run, tmp_path):
    mock = MagicMock()
    mock.returncode = 1
    mock.stderr = "model error"
    mock_run.return_value = mock
    proof_dir = _make_proof_dir(tmp_path)
    with pytest.raises(RuntimeError, match="claude CLI failed"):
        retag_proof(proof_dir)


@patch("tools.lib.tagger.subprocess.run")
def test_retag_idempotent(mock_run, tmp_path):
    """Re-running retag on proof with same tags returns False (no change)."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"result": json.dumps(["health"])})
    mock.stderr = ""
    mock_run.return_value = mock
    proof_dir = _make_proof_dir(tmp_path, tags=["health"])
    result = retag_proof(proof_dir)
    assert result is False


@patch("tools.lib.tagger.subprocess.run")
def test_retag_updates_tags(mock_run, tmp_path):
    """Retag changes tags when LLM returns different tags."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"result": json.dumps(["health", "nutrition"])})
    mock.stderr = ""
    mock_run.return_value = mock
    proof_dir = _make_proof_dir(tmp_path, tags=["health"])
    result = retag_proof(proof_dir)
    assert result is True
    meta = yaml.safe_load((proof_dir / "meta.yaml").read_text())
    assert meta["tags"] == ["health", "nutrition"]


@patch("tools.lib.tagger.subprocess.run")
def test_retag_audit_proposes_and_updates_vocab(mock_run, tmp_path):
    """audit_vocabulary + vocab update flow: proposals accepted, vocab file updated."""
    from tools.lib.tagger import audit_vocabulary, load_vocab_data, save_vocab_data

    # Create vocab file
    vocab_file = tmp_path / "tag_vocabulary.json"
    vocab_data = {
        "proof_count_at_last_audit": 0,
        "last_audit_at": "2026-01-01",
        "vocabulary": {"politics": "Elections, legislation"}
    }
    vocab_file.write_text(json.dumps(vocab_data))

    # Mock audit response proposing a new tag
    audit_response = json.dumps({
        "proposals": [{"slug": "law", "description": "Legal claims", "proofs": ["p1", "p2", "p3"]}],
        "rationale": "test"
    })
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"result": audit_response})
    mock.stderr = ""
    mock_run.return_value = mock

    claims = {
        "p1": {"claim": "Legal claim 1", "tags": ["politics"], "manual": False},
        "p2": {"claim": "Legal claim 2", "tags": ["politics"], "manual": False},
        "p3": {"claim": "Legal claim 3", "tags": ["politics"], "manual": False},
    }
    accepted = audit_vocabulary(claims)
    assert len(accepted) == 1
    assert accepted[0]["slug"] == "law"

    # Simulate the vocab update that --audit would do
    for prop in accepted:
        vocab_data["vocabulary"][prop["slug"]] = prop["description"]
    save_vocab_data(vocab_file, vocab_data)

    # Verify vocab file was updated
    reloaded = load_vocab_data(vocab_file)
    assert "law" in reloaded["vocabulary"]
    assert reloaded["vocabulary"]["law"] == "Legal claims"
