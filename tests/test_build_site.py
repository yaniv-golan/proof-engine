import importlib.util
import json
import subprocess
import sys
import pytest
from pathlib import Path
import shutil

_bs_spec = importlib.util.spec_from_file_location(
    "build_site",
    Path(__file__).parent.parent / "tools" / "build-site.py",
)
_bs_mod = importlib.util.module_from_spec(_bs_spec)
_bs_spec.loader.exec_module(_bs_mod)
compute_stats = _bs_mod.compute_stats


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
    assert (output / "llms.txt").exists()


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


def test_robots_txt_at_root(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    robots = (site_fixture / "_site" / "robots.txt").read_text()
    assert "User-agent: *" in robots
    assert "Sitemap: https://example.com/proof-engine/sitemap.xml" in robots


def test_sitemap_xml_at_root(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    sitemap = (site_fixture / "_site" / "sitemap.xml").read_text()
    assert 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"' in sitemap
    assert "<url><loc>https://example.com/proof-engine/</loc></url>" in sitemap
    assert "<url><loc>https://example.com/proof-engine/catalog/</loc></url>" in sitemap
    assert "<url><loc>https://example.com/proof-engine/proofs/test-claim/</loc></url>" in sitemap
    assert "<url><loc>https://example.com/proof-engine/methodology/</loc></url>" in sitemap
    assert "<url><loc>https://example.com/proof-engine/submit/</loc></url>" in sitemap


def test_meta_description_in_proof_page(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert '<meta name="description" content="PROVED: Test claim is true' in html


def test_og_tags_in_proof_page(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert 'og:title" content="Test claim is true"' in html
    assert 'og:description" content="PROVED: Test claim is true' in html
    assert 'og:url" content="https://example.com/proof-engine/proofs/test-claim/"' in html
    assert 'og:type" content="article"' in html
    assert 'og:site_name" content="Proof Engine"' in html


def test_canonical_url_in_landing_page(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert '<link rel="canonical" href="https://example.com/proof-engine/">' in html


def test_json_ld_preserved_on_proof_page(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert '<script type="application/ld+json">' in html
    assert '"@type": "ClaimReview"' in html
    assert '"claimReviewed": "Test claim is true"' in html


@pytest.fixture
def site_fixture_paginated(tmp_path):
    """Set up a site with 51 proofs sharing one tag to force pagination."""
    repo_root = Path(__file__).parent.parent
    site_src = repo_root / "site"

    shutil.copytree(site_src / "templates", tmp_path / "site" / "templates")
    shutil.copytree(site_src / "static", tmp_path / "site" / "static")
    shutil.copytree(site_src / "content", tmp_path / "site" / "content")

    for i in range(51):
        proof_dir = tmp_path / "site" / "proofs" / f"claim-{i:03d}"
        proof_dir.mkdir(parents=True)
        (proof_dir / "proof.md").write_text(
            f"# Proof\n\n## Key Findings\n\n- Found it #{i}\n\n"
            f"## Claim Interpretation\n\nMeans X.\n\n"
            f"## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| B1 | X |\n\n"
            f"## Proof Logic\n\nBecause Y.\n\n"
            f"## Conclusion\n\nThe claim is PROVED.\n"
        )
        (proof_dir / "proof_audit.md").write_text("# Audit\n\n## Hardening Checklist\n\nAll pass.\n")
        (proof_dir / "proof.py").write_text("# proof script\n")
        (proof_dir / "proof.json").write_text(json.dumps({
            "fact_registry": {},
            "claim_formal": {
                "subject": "Test", "property": "value", "operator": ">",
                "operator_note": "Strictly greater", "threshold": 0,
            },
            "claim_natural": f"Test claim {i} is true",
            "verdict": "PROVED",
            "key_results": {"value": 1},
            "generator": {
                "name": "proof-engine", "version": "0.9.0",
                "repo": "https://github.com/yaniv-golan/proof-engine",
                "generated_at": "2025-01-15",
            },
        }))
        (proof_dir / "meta.yaml").write_text("tags:\n  - bulk-tag\n")

    return tmp_path


def test_sitemap_xml_tag_urls(site_fixture_paginated):
    result = _run_build(site_fixture_paginated)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    sitemap = (site_fixture_paginated / "_site" / "sitemap.xml").read_text()
    assert "<url><loc>https://example.com/proof-engine/tags/bulk-tag/</loc></url>" in sitemap
    assert "<url><loc>https://example.com/proof-engine/tags/bulk-tag/page/2/</loc></url>" in sitemap


def test_tag_page2_metadata_differs(site_fixture_paginated):
    result = _run_build(site_fixture_paginated)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    page1 = (site_fixture_paginated / "_site" / "tags" / "bulk-tag" / "index.html").read_text()
    page2 = (site_fixture_paginated / "_site" / "tags" / "bulk-tag" / "page" / "2" / "index.html").read_text()
    assert "(Page 2)" not in page1
    assert "(Page 2)" in page2
    assert '<title>bulk-tag (Page 2)' in page2


def test_seo_outputs_with_root_base_url(site_fixture):
    result = _run_build(site_fixture, base_url="/")
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    output = site_fixture / "_site"
    robots = (output / "robots.txt").read_text()
    assert "Sitemap: https://example.com/sitemap.xml" in robots
    sitemap = (output / "sitemap.xml").read_text()
    assert "<url><loc>https://example.com/</loc></url>" in sitemap
    assert "<url><loc>https://example.com/proofs/test-claim/</loc></url>" in sitemap
    html = (output / "index.html").read_text()
    assert '<link rel="canonical" href="https://example.com/">' in html


def test_base_url_without_trailing_slash(site_fixture):
    """base_url without trailing slash should produce the same URLs as with."""
    result = _run_build(site_fixture, base_url="/proof-engine")
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    output = site_fixture / "_site"
    sitemap = (output / "sitemap.xml").read_text()
    assert "<url><loc>https://example.com/proof-engine/</loc></url>" in sitemap
    assert "<url><loc>https://example.com/proof-engine/catalog/</loc></url>" in sitemap
    robots = (output / "robots.txt").read_text()
    assert "Sitemap: https://example.com/proof-engine/sitemap.xml" in robots
    html = (output / "index.html").read_text()
    assert '<link rel="canonical" href="https://example.com/proof-engine/">' in html


def test_llms_txt_at_root(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    llms = (site_fixture / "_site" / "llms.txt").read_text()
    assert llms.startswith("# Proof Engine")
    assert "https://example.com/proof-engine/catalog/" in llms
    assert "https://example.com/proof-engine/index.json" in llms
    assert "https://example.com/proof-engine/submit/" in llms
    assert "https://example.com/proof-engine/methodology/" in llms
    assert "https://github.com/yaniv-golan/proof-engine#installation" in llms
    assert "proof.py" in llms
    assert "proof.md" in llms
    assert "proof_audit.md" in llms
    assert "proof.json" in llms


def test_llms_txt_urls_with_root_base_url(site_fixture):
    result = _run_build(site_fixture, base_url="/")
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    llms = (site_fixture / "_site" / "llms.txt").read_text()
    assert "https://example.com/catalog/" in llms
    assert "https://example.com/index.json" in llms
    assert "/proof-engine/" not in llms


def test_landing_page_has_ai_agents_link(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert 'href="/proof-engine/submit/#ai-agents"' in html
    assert "AI Agents" in html
    assert "cta-row" in html


def test_submit_page_has_ai_agents_section(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "submit" / "index.html").read_text()
    assert "AI Agents" in html
    assert "https://example.com/proof-engine/llms.txt" in html
    assert "copy-btn" in html


def test_supported_not_fully_resolved():
    """SUPPORTED proofs should not count as fully resolved."""
    proofs = [
        {"verdict": {"raw": "PROVED"}, "tags": []},
        {"verdict": {"raw": "SUPPORTED"}, "tags": []},
    ]
    stats = compute_stats(proofs)
    assert stats["verification_rate"] == 50
