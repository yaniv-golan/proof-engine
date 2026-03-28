import json
import subprocess
import sys
import pytest
from pathlib import Path
import shutil


@pytest.fixture
def site_fixture(tmp_path):
    """Set up a minimal site source tree with one proof."""
    repo_root = Path(__file__).parent.parent
    site_src = repo_root / "site"

    shutil.copytree(site_src / "templates", tmp_path / "site" / "templates")
    shutil.copytree(site_src / "static", tmp_path / "site" / "static")
    shutil.copytree(site_src / "content", tmp_path / "site" / "content")

    proof_dir = tmp_path / "site" / "proofs" / "test-claim"
    proof_dir.mkdir(parents=True)

    (proof_dir / "proof.md").write_text(
        "# Proof\n\n## Key Findings\n\n- Found it\n\n"
        "## Claim Interpretation\n\nMeans X.\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| B1 | X |\n\n"
        "## Proof Logic\n\nBecause Y.\n\n"
        "## Conclusion\n\nThe claim is PROVED.\n"
    )
    (proof_dir / "proof_audit.md").write_text(
        "# Audit\n\n## Hardening Checklist\n\nAll pass.\n"
    )
    (proof_dir / "proof.py").write_text("# proof script\n")
    (proof_dir / "proof.json").write_text(json.dumps({
        "fact_registry": {"B1": {"label": "test"}},
        "claim_formal": {
            "subject": "Test", "property": "value", "operator": ">",
            "operator_note": "Strictly greater", "threshold": 0,
        },
        "claim_natural": "Test claim is true",
        "verdict": "PROVED",
        "key_results": {"value": 1},
        "generator": {
            "name": "proof-engine", "version": "0.9.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2025-01-15",
        },
    }))

    return tmp_path


def _run_build(site_fixture, base_url="/proof-engine/"):
    repo_root = Path(__file__).parent.parent
    return subprocess.run(
        [sys.executable, str(repo_root / "tools" / "build-site.py"),
         "--site-dir", str(site_fixture / "site"),
         "--output-dir", str(site_fixture / "_site"),
         "--base-url", base_url,
         "--site-url", "https://example.com",
         "--design-md", str(repo_root / "docs" / "DESIGN.md"),
         "--hardening-rules-md", str(repo_root / "proof-engine" / "skills" / "proof-engine" / "references" / "hardening-rules.md"),
        ],
        capture_output=True, text=True,
    )


def test_build_produces_output(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    output = site_fixture / "_site"
    assert (output / "index.html").exists()
    assert (output / "index.json").exists()
    assert (output / "catalog" / "index.html").exists()
    assert (output / "methodology" / "index.html").exists()
    assert (output / "submit" / "index.html").exists()
    assert (output / "proofs" / "test-claim" / "index.html").exists()
    assert (output / "proofs" / "test-claim" / "proof.json").exists()
    assert (output / "proofs" / "test-claim" / "proof.py").exists()
    assert (output / "proofs" / "test-claim" / "proof_audit.md").exists()


def test_index_json_structure(site_fixture):
    result = _run_build(site_fixture, base_url="/")
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    catalog = json.loads((site_fixture / "_site" / "index.json").read_text())
    assert catalog["total"] == 1
    assert catalog["proofs"][0]["slug"] == "test-claim"
    assert catalog["proofs"][0]["verdict"] == "PROVED"
    assert catalog["proofs"][0]["verdict_category"] == "proved"
    assert "proof_py_url" in catalog["proofs"][0]


def test_proof_json_has_proof_py_url(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    pj = json.loads((site_fixture / "_site" / "proofs" / "test-claim" / "proof.json").read_text())
    assert pj["proof_py_url"] == "/proof-engine/proofs/test-claim/proof.py"
