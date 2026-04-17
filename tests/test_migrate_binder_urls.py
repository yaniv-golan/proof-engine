"""Unit tests for tools/migrate-binder-urls.py."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tools" / "migrate-binder-urls.py"


def _run(path: Path) -> dict:
    subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(path.read_text())


def test_rewrites_old_zenodo_url(tmp_path):
    doi = "10.5281/zenodo.19635623"
    before = {
        "doi": doi,
        "zenodo_id": "19635623",
        "binder_url": "https://mybinder.org/v2/zenodo/19635623/?filepath=proof.ipynb",
    }
    (tmp_path / "doi.json").write_text(json.dumps(before))
    after = _run(tmp_path / "doi.json")
    expected = (
        "https://mybinder.org/v2/gh/yaniv-golan/proof-engine-binder/v1.21.0"
        "?urlpath=lab%2Ftree%2Flauncher.ipynb%3Fdoi%3D10.5281%2Fzenodo.19635623"
    )
    assert after["binder_url"] == expected


def test_adds_binder_url_if_missing(tmp_path):
    doi = "10.5281/zenodo.19635623"
    before = {"doi": doi, "zenodo_id": "19635623"}
    (tmp_path / "doi.json").write_text(json.dumps(before))
    after = _run(tmp_path / "doi.json")
    assert after["binder_url"].startswith("https://mybinder.org/v2/gh/yaniv-golan/proof-engine-binder/v1.21.0")
    assert "10.5281%2Fzenodo.19635623" in after["binder_url"]


def test_idempotent(tmp_path):
    path = tmp_path / "doi.json"
    path.write_text(json.dumps({
        "doi": "10.5281/zenodo.19635623",
        "zenodo_id": "19635623",
        "binder_url": (
            "https://mybinder.org/v2/gh/yaniv-golan/proof-engine-binder/v1.21.0"
            "?urlpath=lab%2Ftree%2Flauncher.ipynb%3Fdoi%3D10.5281%2Fzenodo.19635623"
        ),
    }))
    first = _run(path)
    second = _run(path)
    assert first == second


def test_skips_non_zenodo_doi(tmp_path):
    before = {"doi": "10.1234/other.999", "binder_url": "https://example.com/old"}
    (tmp_path / "doi.json").write_text(json.dumps(before))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "doi.json")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    after = json.loads((tmp_path / "doi.json").read_text())
    assert after == before
