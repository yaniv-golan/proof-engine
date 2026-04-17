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


@patch.dict("os.environ", {"ZENODO_TOKEN": "fake-token"})
@patch("tools.proof_site.ZenodoClient")
def test_mint_doi_passes_related_identifiers_to_create_deposition(mock_cls, proof_dir):
    """Create-path must pass the computed related_identifiers graph (not just
    a single webpage edge) into ZenodoClient.create_deposition."""
    proof = proof_dir / "site" / "proofs" / "test-slug"
    proof.joinpath("meta.yaml").write_text(
        "tags: [math]\n"
        "depends_on:\n"
        "  - relation: References\n"
        "    identifiers:\n"
        "      - type: arxiv\n"
        "        value: '2603.21852'\n"
        "  - relation: IsDerivedFrom\n"
        "    identifiers:\n"
        "      - type: doi\n"
        "        value: 10.5281/zenodo.9999\n"
    )
    client = _mock_zenodo_client()
    mock_cls.return_value = client
    args = MagicMock(
        slug="test-slug", site_dir=str(proof_dir / "site"),
        force=False, sandbox=True,
    )
    assert cmd_mint_doi(args) == 0

    call = client.create_deposition.call_args
    rel = call.kwargs["related_identifiers"]
    relations = [r["relation"] for r in rel]
    assert relations == ["isSupplementedBy", "isDerivedFrom", "references"]
    arxiv_edge = next(r for r in rel if r.get("scheme") == "arxiv")
    assert arxiv_edge["identifier"] == "2603.21852"
    assert arxiv_edge["resource_type"] == "publication-preprint"
    doi_edge = next(r for r in rel if r.get("scheme") == "doi")
    assert doi_edge["identifier"] == "10.5281/zenodo.9999"
    assert "resource_type" not in doi_edge


@patch.dict("os.environ", {"ZENODO_TOKEN": "fake-token"})
@patch("tools.proof_site.ZenodoClient")
def test_mint_doi_force_passes_related_identifiers_to_update_metadata(mock_cls, proof_dir):
    """--force path must pass the full related_identifiers graph into
    ZenodoClient.update_metadata on the new version draft."""
    proof = proof_dir / "site" / "proofs" / "test-slug"
    proof.joinpath("meta.yaml").write_text(
        "tags: [math]\n"
        "depends_on:\n"
        "  - relation: References\n"
        "    identifiers:\n"
        "      - type: arxiv\n"
        "        value: '2603.21852'\n"
    )
    proof.joinpath("doi.json").write_text(json.dumps({
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
    assert cmd_mint_doi(args) == 0

    update_call = client.update_metadata.call_args
    payload = update_call.args[1] if len(update_call.args) > 1 else update_call.kwargs["metadata"]
    rel = payload["related_identifiers"]
    relations = [r["relation"] for r in rel]
    assert relations == ["isSupplementedBy", "references"]


@patch.dict("os.environ", {"ZENODO_TOKEN": "fake-token"})
@patch("tools.proof_site.ZenodoClient")
def test_mint_doi_aborts_before_zenodo_call_on_invalid_depends_on(mock_cls, proof_dir):
    """Malformed depends_on must return 1 without creating any deposition."""
    proof = proof_dir / "site" / "proofs" / "test-slug"
    # relation value 'BogusRelation' is not in ALLOWED_RELATIONS — parser rejects
    proof.joinpath("meta.yaml").write_text(
        "tags: [math]\n"
        "depends_on:\n"
        "  - relation: BogusRelation\n"
        "    identifiers:\n"
        "      - type: doi\n"
        "        value: 10.5281/zenodo.1\n"
    )
    client = _mock_zenodo_client()
    mock_cls.return_value = client
    args = MagicMock(
        slug="test-slug", site_dir=str(proof_dir / "site"),
        force=False, sandbox=True,
    )
    assert cmd_mint_doi(args) == 1
    assert not client.create_deposition.called
    assert not client.new_version.called
    assert not client.update_metadata.called


def test_mint_doi_preflight_blocks_on_unexpanded_token(tmp_path, monkeypatch):
    import subprocess
    import sys
    import os
    from pathlib import Path as P
    REPO = P(__file__).resolve().parent.parent
    slug = "bad_slug"
    site = tmp_path / "site"
    proof = site / "proofs" / slug
    proof.mkdir(parents=True)
    (proof / "proof.py").write_text("print('{}')")
    (proof / "proof.md").write_text("See {{cite:arxiv:2603.21852}}.\n")
    (proof / "proof_audit.md").write_text("x\n")
    (proof / "proof_narrative.md").write_text("x\n")
    (proof / "proof.json").write_text('{"claim_natural": "x"}')
    (proof / "meta.yaml").write_text(
        "tags: [math]\ndepends_on:\n  - relation: References\n"
        "    identifiers:\n      - type: arxiv\n        value: '2603.21852'\n"
    )
    (proof / "depends_on_resolved.json").write_text(
        '{"arxiv:2603.21852": {"identifier_type":"arxiv","identifier_value":"2603.21852",'
        '"canonical_url":"u","title":"t","authors":["Andrzej Odrzywo\u0142ek"],"year":2026,'
        '"venue":null,"version":null,"resolved_at":"r","source_api":"s","raw":{}}}'
    )

    env = {**os.environ, "ZENODO_TOKEN": "dummy"}
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "proof-site.py"), "mint-doi",
         "--slug", slug, "--site-dir", str(site)],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode != 0
    combined = r.stdout + r.stderr
    assert "cite-expand" in combined or "unexpanded" in combined
