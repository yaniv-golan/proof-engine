# tests/test_mint_doi.py
import importlib
import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the hyphenated module via importlib and register it so @patch paths work
_spec = importlib.util.spec_from_file_location(
    "tools.proof_site",
    Path(__file__).parent.parent / "tools" / "proof-site.py",
)
proof_site = importlib.util.module_from_spec(_spec)
sys.modules["tools.proof_site"] = proof_site
_spec.loader.exec_module(proof_site)

cmd_mint_doi = proof_site.cmd_mint_doi


@pytest.fixture
def proof_dir(tmp_path):
    """Set up a minimal site with one proof for mint-doi testing."""
    site = tmp_path / "site" / "proofs" / "test-slug"
    site.mkdir(parents=True)
    (site / "proof.py").write_text("# proof\n")
    (site / "proof.md").write_text("# Proof\n")
    (site / "proof_audit.md").write_text("# Audit\n")
    (site / "proof_narrative.md").write_text("# Narrative\n")
    (site / "proof.json").write_text(json.dumps({
        "claim_natural": "Test claim",
        "verdict": "PROVED",
        "fact_registry": {},
        "claim_formal": {},
        "key_results": {},
        "generator": {
            "name": "proof-engine", "version": "1.0.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-04-07",
        },
    }))
    (site / "meta.yaml").write_text("tags:\n  - health\n")
    return tmp_path


def _mock_zenodo_client():
    """Return a mock ZenodoClient that simulates successful minting."""
    client = MagicMock()
    client.create_deposition.return_value = {
        "id": 12345,
        "links": {"bucket": "https://sandbox.zenodo.org/api/files/bucket-id"},
    }
    client.publish.return_value = {
        "doi": "10.5072/zenodo.12345",
        "conceptdoi": "10.5072/zenodo.12340",
        "id": 12345,
        "conceptrecid": "12340",
    }
    return client


@patch.dict("os.environ", {"ZENODO_TOKEN": "fake-token"})
@patch("tools.proof_site.ZenodoClient")
def test_mint_doi_creates_doi_json(mock_cls, proof_dir):
    """Successful mint writes doi.json with correct fields."""
    mock_cls.return_value = _mock_zenodo_client()
    args = MagicMock(
        slug="test-slug", site_dir=str(proof_dir / "site"),
        force=False, sandbox=True,
    )
    result = cmd_mint_doi(args)
    assert result == 0
    doi_path = proof_dir / "site" / "proofs" / "test-slug" / "doi.json"
    assert doi_path.exists()
    data = json.loads(doi_path.read_text())
    assert data["doi"] == "10.5072/zenodo.12345"
    assert data["concept_doi"] == "10.5072/zenodo.12340"
    assert data["claim_natural"] == "Test claim"


@patch.dict("os.environ", {"ZENODO_TOKEN": "fake-token"})
def test_mint_doi_refuses_if_doi_exists(proof_dir):
    """mint-doi without --force should refuse when doi.json exists."""
    doi_path = proof_dir / "site" / "proofs" / "test-slug" / "doi.json"
    doi_path.write_text(json.dumps({
        "doi": "10.5072/zenodo.99999",
        "zenodo_id": "99999",
        "concept_doi": "10.5072/zenodo.99990",
        "concept_zenodo_id": "99990",
        "claim_natural": "Test claim",
        "minted_at": "2026-04-07",
    }))
    args = MagicMock(
        slug="test-slug", site_dir=str(proof_dir / "site"),
        force=False, sandbox=True,
    )
    result = cmd_mint_doi(args)
    assert result == 1  # should fail


@patch.dict("os.environ", {"ZENODO_TOKEN": "fake-token"})
@patch("tools.proof_site.ZenodoClient")
def test_mint_doi_force_creates_new_version(mock_cls, proof_dir):
    """mint-doi --force should call new_version when doi.json exists."""
    doi_path = proof_dir / "site" / "proofs" / "test-slug" / "doi.json"
    doi_path.write_text(json.dumps({
        "doi": "10.5072/zenodo.99999",
        "zenodo_id": "99999",
        "concept_doi": "10.5072/zenodo.99990",
        "concept_zenodo_id": "99990",
        "claim_natural": "Test claim",
        "minted_at": "2026-04-07",
    }))
    client = _mock_zenodo_client()
    client.new_version.return_value = {
        "id": 100000,
        "links": {"bucket": "https://sandbox.zenodo.org/api/files/new-bucket"},
    }
    client.publish.return_value = {
        "doi": "10.5072/zenodo.100000",
        "conceptdoi": "10.5072/zenodo.99990",
        "id": 100000,
        "conceptrecid": "99990",
    }
    mock_cls.return_value = client
    args = MagicMock(
        slug="test-slug", site_dir=str(proof_dir / "site"),
        force=True, sandbox=True,
    )
    result = cmd_mint_doi(args)
    assert result == 0
    client.new_version.assert_called_once_with(99999)
    data = json.loads(doi_path.read_text())
    assert data["doi"] == "10.5072/zenodo.100000"


def test_mint_doi_fails_without_token(proof_dir):
    """mint-doi should fail if ZENODO_TOKEN is not set."""
    import os
    env = os.environ.copy()
    env.pop("ZENODO_TOKEN", None)
    with patch.dict("os.environ", env, clear=True):
        args = MagicMock(
            slug="test-slug", site_dir=str(proof_dir / "site"),
            force=False, sandbox=True,
        )
        result = cmd_mint_doi(args)
        assert result == 1


def test_mint_doi_fails_for_missing_proof(proof_dir):
    """mint-doi should fail for a non-existent slug."""
    args = MagicMock(
        slug="nonexistent", site_dir=str(proof_dir / "site"),
        force=False, sandbox=True,
    )
    result = cmd_mint_doi(args)
    assert result == 1


@patch.dict("os.environ", {"ZENODO_TOKEN": "fake-token"})
@patch("tools.proof_site.ZenodoClient")
def test_mint_doi_uploads_all_five_artifacts(mock_cls, proof_dir):
    """mint-doi should upload all 5 proof artifacts."""
    client = _mock_zenodo_client()
    mock_cls.return_value = client
    args = MagicMock(
        slug="test-slug", site_dir=str(proof_dir / "site"),
        force=False, sandbox=True,
    )
    cmd_mint_doi(args)
    uploaded_names = [
        call.kwargs.get("file_path", call.args[1] if len(call.args) > 1 else None)
        for call in client.upload_file.call_args_list
    ]
    uploaded_filenames = [Path(p).name for p in uploaded_names if p]
    assert "proof.py" in uploaded_filenames
    assert "proof.md" in uploaded_filenames
    assert "proof_audit.md" in uploaded_filenames
    assert "proof_narrative.md" in uploaded_filenames
    assert "proof.json" in uploaded_filenames
