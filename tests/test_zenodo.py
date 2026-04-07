import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from tools.lib.zenodo import ZenodoClient, ZenodoError


@pytest.fixture
def client():
    return ZenodoClient(token="test-token", sandbox=True)


def _mock_response(status_code=200, json_data=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = json.dumps(json_data or {})
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


@patch("tools.lib.zenodo.requests.post")
def test_create_deposition(mock_post, client):
    mock_post.return_value = _mock_response(201, {
        "id": 12345,
        "metadata": {"prereserve_doi": {"doi": "10.5072/zenodo.12345"}},
        "links": {"bucket": "https://sandbox.zenodo.org/api/files/bucket-id"},
    })
    dep = client.create_deposition(
        title="Test Proof",
        description="A test",
        creators=[{"name": "Proof Engine"}],
        keywords=["test"],
        license="MIT",
        related_identifiers=[],
    )
    assert dep["id"] == 12345
    mock_post.assert_called_once()


@patch("tools.lib.zenodo.requests.put")
def test_upload_file(mock_put, client):
    mock_put.return_value = _mock_response(201, {"key": "proof.py"})
    client.upload_file(
        bucket_url="https://sandbox.zenodo.org/api/files/bucket-id",
        file_path=Path(__file__),
    )
    mock_put.assert_called_once()


@patch("tools.lib.zenodo.requests.post")
def test_publish_deposition(mock_post, client):
    mock_post.return_value = _mock_response(202, {
        "doi": "10.5072/zenodo.12345",
        "conceptdoi": "10.5072/zenodo.12340",
        "id": 12345,
        "conceptrecid": "12340",
    })
    result = client.publish(12345)
    assert result["doi"] == "10.5072/zenodo.12345"
    assert result["conceptdoi"] == "10.5072/zenodo.12340"


@patch("tools.lib.zenodo.requests.post")
def test_create_new_version(mock_post, client):
    mock_post.return_value = _mock_response(201, {
        "id": 12346,
        "links": {"bucket": "https://sandbox.zenodo.org/api/files/bucket-id-2"},
    })
    result = client.new_version(12345)
    assert result["id"] == 12346


def test_sandbox_uses_sandbox_url(client):
    assert "sandbox" in client.base_url


def test_production_uses_production_url():
    c = ZenodoClient(token="test", sandbox=False)
    assert "sandbox" not in c.base_url
    assert c.base_url == "https://zenodo.org/api"
