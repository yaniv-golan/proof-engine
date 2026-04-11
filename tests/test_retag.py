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
