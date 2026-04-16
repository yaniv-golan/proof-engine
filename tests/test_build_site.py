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
build_citation_summary = _bs_mod.build_citation_summary
build_pipeline_example_data = _bs_mod.build_pipeline_example_data
from tools.lib.latex_utils import strip_latex


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
        "# Proof\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| A1 | X |\n\n"
        "## Proof Logic\n\nBecause Y.\n\n"
        "## Conclusion\n\nThe claim is PROVED.\n"
    )
    (proof_dir / "proof_audit.md").write_text(
        "# Audit\n\n## Claim Specification\n\n| Field | Value |\n|---|---|\n| Subject | Test |\n\n"
        "## Claim Interpretation\n\nMeans X.\n\n"
        "## Hardening Checklist\n\nAll pass.\n"
    )
    (proof_dir / "proof_narrative.md").write_text(
        "# Proof Narrative: Test claim is true\n\n"
        "## Verdict\n\n"
        "**Verdict: PROVED**\n\n"
        "Yes — the test claim is confirmed true beyond any reasonable doubt whatsoever. "
        "The evidence is overwhelming and consistent across every source examined.\n\n"
        "## What was claimed?\n\n"
        "Test claim is true. This matters for science "
        "and has real consequences for how we understand validity. "
        "Getting this right affects downstream decisions.\n\n"
        "## What did we find?\n\n"
        "We found strong evidence supporting the claim. "
        "Multiple independent sources confirmed the core assertion "
        "from different angles and methodologies. "
        "The data was consistent across all measurements taken "
        "over the full range of conditions tested. "
        "No contradictory evidence was identified in any source. "
        "The primary computation matched theoretical predictions within tight tolerance. "
        "Secondary verification through independent calculation confirmed the same figure. "
        "Cross-referencing against published reference data showed agreement within one percent. "
        "Statistical significance exceeds conventional thresholds by a wide margin. "
        "Adversarial scenarios designed to break the conclusion all failed.\n\n"
        "## What should you keep in mind?\n\n"
        "This covers the specific claim as stated only. "
        "Different framings might yield different results. "
        "The methodology is optimized for quantitative claims.\n\n"
        "## How was this verified?\n\n"
        "Verified through computation. "
        "See [the structured proof report](proof.md), "
        "[the full verification audit](proof_audit.md), "
        "or [re-run the proof yourself](proof.py).\n"
    )
    (proof_dir / "proof.py").write_text("# proof script\n")
    (proof_dir / "proof.json").write_text(json.dumps({
        "format_version": 2,
        "fact_registry": {"A1": {"label": "test", "method": "1 == 1", "result": "True"}},
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
    (proof_dir / "meta.yaml").write_text("tags:\n  - health\n")

    (proof_dir.parent / "featured.json").write_text(
        json.dumps(["test-claim"]) + "\n",
    )

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
    # Meta description now uses verdict hook from narrative
    assert '<meta name="description" content="PROVED: ' in html
    assert "confirmed true" in html


def test_og_tags_in_proof_page(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert 'og:title" content="PROVED: Test claim is true"' in html
    assert 'og:description" content="PROVED: ' in html
    assert 'og:url" content="https://example.com/proof-engine/proofs/test-claim/"' in html
    assert 'og:type" content="article"' in html
    assert 'og:site_name" content="Proof Engine"' in html


def test_canonical_url_in_landing_page(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert '<link rel="canonical" href="https://example.com/proof-engine/">' in html


def test_landing_page_has_verdict_summary_in_featured_data(site_fixture):
    """FEATURED_PROOFS_DATA entries include verdict_summary."""
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert "verdict_summary" in html


def test_build_pipeline_example_data_with_citations(tmp_path):
    """Pipeline example includes citations, sources, and code snippet when present."""
    slug = "pipe-proof"
    proof_dir = tmp_path / "proofs" / slug
    proof_dir.mkdir(parents=True)
    (proof_dir / "proof.py").write_text(
        "x = 1\n"
        "def run():\n"
        "    compare(a, b)\n",
    )
    proof = {
        "slug": slug,
        "proof_data": {
            "claim_natural": "Example claim",
            "citations": {
                "B1": {
                    "source_name": "Source One",
                    "url": "https://example.com/one",
                    "status": "verified",
                    "method": "full_quote",
                    "quote": (
                        "A quote that is long enough to test truncation " * 3
                    ),
                    "credibility": {
                        "source_type": "government",
                    },
                },
                "B2": {
                    "source_name": "Source One",
                    "url": "https://example.com/dup",
                    "status": "partial",
                    "method": "fragment",
                    "quote": "short",
                    "credibility": {"source_type": "unknown"},
                },
            },
            "extractions": {
                "B1": {"quote_snippet": "from extraction"},
            },
            "claim_formal": {
                "subject": "S",
                "property": "P",
                "operator": ">",
                "threshold": 0,
            },
        },
        "verdict": {"raw": "PROVED", "category": "proved"},
        "verdict_summary": "Summary line.",
    }
    out = build_pipeline_example_data(proof, "/base/", tmp_path / "proofs")
    assert out is not None
    assert out["slug"] == slug
    assert out["proof_url"] == "/base/proofs/pipe-proof/"
    assert len(out["sources"]) == 1
    assert out["sources"][0]["source_type"] == "government"
    assert len(out["citations"]) == 2
    b1_row = next(r for r in out["citations"] if r["fact_id"] == "B1")
    assert b1_row["quote_snippet"] == "from extraction"
    b2_row = next(r for r in out["citations"] if r["fact_id"] == "B2")
    assert b2_row["quote_snippet"] == "short"
    assert out["claim_formal_summary"] == "S: P > 0"
    assert "compare" in out["code_example"]["snippet"]
    assert out["verdict"]["summary"] == "Summary line."


def test_build_pipeline_example_data_no_citations_returns_none():
    proof = {
        "slug": "x",
        "proof_data": {"claim_natural": "c", "citations": {}},
        "verdict": {"raw": "PROVED", "category": "proved"},
    }
    assert build_pipeline_example_data(proof, "/", Path("/tmp")) is None


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
            f"# Proof\n\n"
            f"## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| A1 | X |\n\n"
            f"## Proof Logic\n\nBecause Y.\n\n"
            f"## Conclusion\n\nThe claim is PROVED.\n"
        )
        (proof_dir / "proof_audit.md").write_text(
            "# Audit\n\n## Claim Specification\n\n| Field | Value |\n|---|---|\n| Subject | Test |\n\n"
            "## Claim Interpretation\n\nMeans X.\n\n"
            "## Hardening Checklist\n\nAll pass.\n"
        )
        (proof_dir / "proof.py").write_text("# proof script\n")
        (proof_dir / "proof.json").write_text(json.dumps({
            "format_version": 2,
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
        (proof_dir / "proof_narrative.md").write_text(
            f"# Proof Narrative: Test claim {i} is true\n\n"
            "## Verdict\n\n"
            "**Verdict: PROVED**\n\n"
            "Yes — this is confirmed true beyond any reasonable doubt whatsoever. "
            "The evidence is overwhelming and consistent across every source examined.\n\n"
            "## What was claimed?\n\n"
            f"Test claim {i} is true. This matters for science "
            "and has real consequences for how we understand validity. "
            "Getting this right affects downstream decisions.\n\n"
            "## What did we find?\n\n"
            "We found strong evidence supporting the claim. "
            "Multiple independent sources confirmed the core assertion "
            "from different angles and methodologies. "
            "The data was consistent across all measurements taken "
            "over the full range of conditions tested. "
            "No contradictory evidence was identified in any source. "
            "The primary computation matched theoretical predictions within tight tolerance. "
            "Secondary verification through independent calculation confirmed the same figure. "
            "Cross-referencing against published reference data showed agreement within one percent. "
            "Statistical significance exceeds conventional thresholds by a wide margin. "
            "Adversarial scenarios designed to break the conclusion all failed.\n\n"
            "## What should you keep in mind?\n\n"
            "This covers the specific claim as stated only. "
            "Different framings might yield different results. "
            "The methodology is optimized for quantitative claims.\n\n"
            "## How was this verified?\n\n"
            "Verified through computation. "
            "See [the structured proof report](proof.md), "
            "[the full verification audit](proof_audit.md), "
            "or [re-run the proof yourself](proof.py).\n"
        )

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
    assert "build ai agents that prove" in html.lower()


def test_build_exports_proof_md(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    assert (site_fixture / "_site" / "proofs" / "test-claim" / "proof.md").exists()


def test_build_exports_proof_narrative(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    assert (site_fixture / "_site" / "proofs" / "test-claim" / "proof_narrative.md").exists()


def test_submit_page_has_ai_agents_section(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "submit" / "index.html").read_text()
    assert "AI Agents" in html
    assert "https://example.com/proof-engine/llms.txt" in html
    assert "copy-btn" in html


def test_google_fonts_link_in_head(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert "fonts.googleapis.com" in html
    assert "JetBrains+Mono" in html


def test_favicon_links_in_head(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert 'rel="icon" href="/proof-engine/static/favicon.ico"' in html
    assert 'rel="apple-touch-icon" href="/proof-engine/static/apple-touch-icon.png"' in html


def test_google_analytics_in_head(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert "G-KSGK7C8RGD" in html
    assert "googletagmanager.com/gtag/js" in html


def test_favicon_links_with_root_base_url(site_fixture):
    result = _run_build(site_fixture, base_url="/")
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert 'rel="icon" href="/static/favicon.ico"' in html


def test_supported_not_counted_as_proved():
    """SUPPORTED proofs should not count in proved_count."""
    proofs = [
        {"verdict": {"raw": "PROVED", "filter_value": "proved"}, "tags": []},
        {"verdict": {"raw": "SUPPORTED", "filter_value": "supported"}, "tags": []},
    ]
    stats = compute_stats(proofs)
    assert stats["proved_count"] == 1
    assert stats["disproved_count"] == 0


def test_stats_proved_disproved_counts():
    proofs = [
        {"verdict": {"raw": "PROVED", "filter_value": "proved"}, "tags": []},
        {"verdict": {"raw": "DISPROVED", "filter_value": "disproved"}, "tags": []},
        {"verdict": {"raw": "SUPPORTED", "filter_value": "supported"}, "tags": []},
        {"verdict": {"raw": "PROVED (with unverified citations)", "filter_value": "proved"}, "tags": []},
    ]
    stats = compute_stats(proofs)
    assert stats["proved_count"] == 2  # includes qualified variant
    assert stats["disproved_count"] == 1
    assert "verification_rate" not in stats


def test_index_json_has_source_names(site_fixture):
    # Add citations (and matching fact_registry entries) to the test proof.json
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["fact_registry"]["B1"] = {"label": "MIT source"}
    data["fact_registry"]["B2"] = {"label": "Britannica source"}
    data["citations"] = {
        "B1": {
            "source_name": "MIT McGovern Institute",
            "url": "https://example.com/mit",
            "status": "verified",
        },
        "B2": {
            "source_name": "Encyclopaedia Britannica",
            "url": "https://example.com/britannica",
            "status": "verified",
        },
    }
    proof_json_path.write_text(json.dumps(data))

    result = _run_build(site_fixture, base_url="/")
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    catalog = json.loads((site_fixture / "_site" / "index.json").read_text())
    proof_entry = catalog["proofs"][0]
    assert "source_names" in proof_entry
    assert "MIT McGovern Institute" in proof_entry["source_names"]
    assert "Encyclopaedia Britannica" in proof_entry["source_names"]
    assert "source_names_extra" in proof_entry
    assert "has_citations" in proof_entry
    assert proof_entry["has_citations"] is True


def test_proof_page_evidence_table_with_citations(site_fixture):
    """Proof pages with citations render a structured evidence table with links."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["fact_registry"]["B1"] = {"label": "Test fact"}
    data["citations"] = {
        "B1": {
            "source_name": "Test Source",
            "url": "https://example.com/source",
            "status": "verified",
            "source_key": "test_src",
            "quote": "Test quote",
            "method": "full_quote",
            "credibility": {
                "domain": "example.com",
                "source_type": "academic",
                "tier": 4,
                "note": "Test note",
            },
        },
    }
    data["extractions"] = {
        "B1": {
            "value": "verified",
            "value_in_quote": True,
            "quote_snippet": "Test quote snippet",
        },
    }
    proof_json_path.write_text(json.dumps(data))

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    # Evidence table has linked source
    assert "evidence-table" in html
    assert 'href="https://example.com/source"' in html
    assert "Test Source" in html


def test_audit_extraction_links_with_suffixed_keys(site_fixture):
    """Extraction keys like B1_foo should resolve to citation B1's URL.

    After the detail-page redesign, the Linked Sources sub-tables inside the
    audit accordion were removed.  The canonical sources table (which iterates
    over fact_registry) still links each citation's URL, so the B1 source URL
    must appear at least once in the rendered page.
    """
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["fact_registry"]["B1"] = {"label": "Test fact"}
    data["citations"] = {
        "B1": {
            "source_name": "Test Source",
            "url": "https://example.com/source",
            "status": "verified",
            "source_key": "test_src",
            "quote": "Test quote",
            "method": "full_quote",
            "credibility": {
                "domain": "example.com",
                "source_type": "academic",
                "tier": 4,
                "note": "Test note",
            },
        },
    }
    data["extractions"] = {
        "B1_height": {
            "value": "1.68",
            "value_in_quote": True,
            "quote_snippet": "height is 1.68m",
        },
        "B1_weight": {
            "value": "70",
            "value_in_quote": True,
            "quote_snippet": "weight is 70kg",
        },
    }
    proof_json_path.write_text(json.dumps(data))

    # Also add audit markdown so the section renders
    audit_path = site_fixture / "site" / "proofs" / "test-claim" / "proof_audit.md"
    audit_text = audit_path.read_text()
    audit_text += "\n\n## Extraction Records\n\n| ID | Value |\n|---|---|\n| B1_height | 1.68 |\n"
    audit_path.write_text(audit_text)

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    # B1's source URL appears in the canonical sources table
    assert 'href="https://example.com/source"' in html


def test_twitter_card_meta_in_head(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert 'twitter:card' in html
    assert 'twitter:title' in html


def test_landing_page_has_schema_org(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert '"@type": "WebSite"' in html
    assert '"name": "Proof Engine"' in html


def test_landing_page_has_pipeline_diagram(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert "pipeline" in html
    assert "fetch sources" in html
    assert "verify quotes" in html
    assert "verdict" in html


def test_proof_page_has_share_bar(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "share-bar" in html
    assert "share-copy-verdict" in html
    assert "share-copy-link" in html
    assert "share-twitter" in html


def test_proof_page_friendly_download_labels(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "run the proof (Python)" in html
    assert "original audit log" in html
    assert "raw data (JSON)" in html


def test_proof_page_standards_download_links(site_fixture):
    """Downloads section exposes machine-readable format links with correct hrefs."""
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()

    # Locate the downloads section and assert within it only —
    # prevents false passes from hrefs that appear in JSON-LD or elsewhere.
    section_start = html.find('class="downloads-section"')
    assert section_start != -1, "downloads-section not found"
    section_end = html.find("</details>", section_start)
    assert section_end != -1
    section_html = html[section_start:section_end]

    # Exact hrefs (base_url=/proof-engine/, slug=test-claim)
    ipynb_href = 'href="/proof-engine/proofs/test-claim/proof.ipynb"'
    prov_href = 'href="/proof-engine/proofs/test-claim/provenance.json"'
    crate_href = 'href="/proof-engine/proofs/test-claim/ro-crate-metadata.json"'
    assert ipynb_href in section_html
    assert prov_href in section_html
    assert crate_href in section_html

    # Human-readable labels
    assert "interactive notebook (.ipynb)" in section_html
    assert "provenance trace (W3C PROV)" in section_html
    assert "research package (RO-Crate 1.1)" in section_html

    # Group label div must carry the correct CSS class (flex-row break depends on it)
    assert 'class="downloads-group-label"' in section_html

    # download attribute must be present on all three links
    assert 'href="/proof-engine/proofs/test-claim/proof.ipynb" class="download-link" download' in section_html
    assert 'href="/proof-engine/proofs/test-claim/provenance.json" class="download-link" download' in section_html
    assert 'href="/proof-engine/proofs/test-claim/ro-crate-metadata.json" class="download-link" download' in section_html

    # Group label must appear BEFORE all three hrefs — proves correct ordering,
    # not just co-presence in the same <details> block.
    label_pos = section_html.find("machine-readable formats")
    assert label_pos != -1, "group label text not found"
    assert label_pos < section_html.find(ipynb_href), "label must precede notebook href"
    assert label_pos < section_html.find(prov_href), "label must precede provenance href"
    assert label_pos < section_html.find(crate_href), "label must precede RO-Crate href"

    # Backing files must be emitted into _site — prevents 404s on the new links
    proof_out = site_fixture / "_site" / "proofs" / "test-claim"
    assert (proof_out / "proof.ipynb").exists(), "proof.ipynb not generated"
    assert (proof_out / "provenance.json").exists(), "provenance.json not generated"
    assert (proof_out / "ro-crate-metadata.json").exists(), "ro-crate-metadata.json not generated"


def test_proof_page_evidence_table_source_first(site_fixture):
    """Evidence table should have Source as first column, ID as second."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["citations"] = {
        "B1": {
            "source_name": "Test Source Alpha",
            "url": "https://example.com/alpha",
            "status": "verified",
        },
    }
    proof_json_path.write_text(json.dumps(data))

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    # Source column comes before ID column in the evidence-table header
    evidence_table_start = html.find("evidence-table")
    assert evidence_table_start != -1, "Evidence table not found"
    table_html = html[evidence_table_start:]
    source_pos = table_html.find("<th>Source</th>")
    id_pos = table_html.find("<th>ID</th>")
    assert source_pos != -1 and id_pos != -1, "Evidence table missing Source or ID header"
    assert source_pos < id_pos, "Source column should come before ID column"


def test_og_image_meta_in_head(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "index.html").read_text()
    assert 'og:image' in html
    assert 'og-default.png' in html


def test_proof_page_og_image(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert 'og:image' in html
    assert 'og-image.png' in html
    # Check OG image file was generated
    assert (site_fixture / "_site" / "proofs" / "test-claim" / "og-image.png").exists()


# --- Citation summary unit tests ---


def test_citation_summary_all_clean():
    """All verified, full_quote, live, tier>=3 → clean health, no flags."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Source A", "url": "https://example.com/a",
                "status": "verified", "method": "full_quote", "fetch_mode": "live",
                "credibility": {"tier": 4, "source_type": "academic"},
            },
            "B2": {
                "source_name": "Source B", "url": "https://example.com/b",
                "status": "verified", "method": "full_quote", "fetch_mode": "live",
                "credibility": {"tier": 3, "source_type": "major_news"},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["total"] == 2
    assert summary["verified"] == 2
    assert summary["health"] == "clean"
    assert summary["unflagged"] == 2
    assert summary["flagged"] == []


def test_citation_summary_partial_flagged():
    """Partial citation with aggressive_normalization is flagged."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Clean Source", "url": "https://example.com/a",
                "status": "verified", "method": "full_quote", "fetch_mode": "live",
                "credibility": {"tier": 4},
            },
            "B2": {
                "source_name": "Normalized Source", "url": "https://example.com/b",
                "status": "partial", "method": "aggressive_normalization",
                "fetch_mode": "live", "credibility": {"tier": 4},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["health"] == "notice"
    assert summary["unflagged"] == 1
    assert len(summary["flagged"]) == 1
    assert summary["flagged"][0]["id"] == "B2"
    assert "matched after normalization" in summary["flagged"][0]["reasons"]


def test_citation_summary_not_found_flagged():
    """not_found citation triggers warning health."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Good Source", "url": "https://example.com/a",
                "status": "verified", "method": "full_quote", "fetch_mode": "live",
                "credibility": {"tier": 3},
            },
            "B2": {
                "source_name": "Missing Source", "url": "https://example.com/b",
                "status": "not_found", "method": None, "fetch_mode": "live",
                "credibility": {"tier": 4},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["health"] == "warning"
    assert summary["not_found"] == 1
    assert len(summary["flagged"]) == 1
    assert "quote not found on page" in summary["flagged"][0]["reasons"]


def test_citation_summary_wayback_flagged():
    """Wayback fetch is flagged even if status is verified."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Wayback Source", "url": "https://example.com/a",
                "status": "verified", "method": "full_quote", "fetch_mode": "wayback",
                "credibility": {"tier": 4},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["health"] == "notice"
    assert summary["verified"] == 1
    assert summary["unflagged"] == 0
    assert len(summary["flagged"]) == 1
    assert "fetched from Wayback Machine" in summary["flagged"][0]["reasons"]


def test_citation_summary_snapshot_not_flagged():
    """Snapshot fetch_mode is clean — embedded offline copy."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Snapshot Source", "url": "https://example.com/a",
                "status": "verified", "method": "full_quote", "fetch_mode": "snapshot",
                "credibility": {"tier": 4},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["health"] == "clean"
    assert summary["flagged"] == []
    assert summary["unflagged"] == 1


def test_citation_summary_tier2_not_flagged():
    """Tier 2 sources are NOT flagged — too common to be noise."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Tier 2 Source", "url": "https://example.com/a",
                "status": "verified", "method": "full_quote", "fetch_mode": "live",
                "credibility": {"tier": 2, "source_type": "unknown"},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["health"] == "clean"
    assert summary["flagged"] == []
    assert summary["unflagged"] == 1


def test_citation_summary_no_citations():
    """No citations returns None."""
    assert build_citation_summary({}) is None
    assert build_citation_summary({"citations": {}}) is None


def test_citation_summary_fragment_with_coverage():
    """Fragment match shows coverage percentage in reason."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Fragment Source", "url": "https://example.com/a",
                "status": "partial", "method": "fragment", "fetch_mode": "live",
                "coverage_pct": 48.6, "credibility": {"tier": 3},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert len(summary["flagged"]) == 1
    assert "49% word match" in summary["flagged"][0]["reasons"]


def test_citation_summary_fetch_failed_distinct():
    """fetch_failed is counted separately from not_found."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Blocked Source", "url": "https://example.com/a",
                "status": "fetch_failed", "method": None, "fetch_mode": "live",
                "credibility": {"tier": 3},
            },
            "B2": {
                "source_name": "Missing Source", "url": "https://example.com/b",
                "status": "not_found", "method": None, "fetch_mode": "live",
                "credibility": {"tier": 3},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["health"] == "warning"
    assert summary["fetch_failed"] == 1
    assert summary["not_found"] == 1
    assert len(summary["flagged"]) == 2
    reasons_b1 = summary["flagged"][0]["reasons"]
    reasons_b2 = summary["flagged"][1]["reasons"]
    assert "source could not be fetched" in reasons_b1
    assert "quote not found on page" in reasons_b2


def test_citation_summary_verified_unicode_normalized_flagged():
    """verified + unicode_normalized is flagged with appropriate reason."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Unicode Source", "url": "https://example.com/a",
                "status": "verified", "method": "unicode_normalized", "fetch_mode": "live",
                "credibility": {"tier": 4},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["verified"] == 1
    assert summary["health"] == "notice"
    assert len(summary["flagged"]) == 1
    assert summary["unflagged"] == 0
    assert "matched after Unicode normalization" in summary["flagged"][0]["reasons"]


def test_citation_summary_verified_fragment_flagged():
    """verified + fragment is flagged."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "High Fragment Source", "url": "https://example.com/a",
                "status": "verified", "method": "fragment", "fetch_mode": "live",
                "coverage_pct": 85.0, "credibility": {"tier": 3},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["verified"] == 1
    assert len(summary["flagged"]) == 1
    assert summary["health"] == "notice"
    assert "verified via fragment match (85%)" in summary["flagged"][0]["reasons"]


def test_citation_summary_tier1_flagged_notice():
    """Tier 1 (unreliable/satire) is flagged and escalates health to notice."""
    proof_data = {
        "citations": {
            "B1": {
                "source_name": "Satire Site", "url": "https://theonion.com/article",
                "status": "verified", "method": "full_quote", "fetch_mode": "live",
                "credibility": {"tier": 1, "source_type": "satire"},
            },
        },
    }
    summary = build_citation_summary(proof_data)
    assert summary["verified"] == 1
    assert summary["health"] == "notice"
    assert len(summary["flagged"]) == 1
    assert summary["unflagged"] == 0


# --- Citation summary integration tests ---


def test_citation_summary_renders_clean(site_fixture):
    """Clean proof renders summary badge with no flagged items."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["citations"] = {
        "B1": {
            "source_name": "Test Source", "url": "https://example.com/source",
            "status": "verified", "source_key": "test_src", "quote": "Test quote",
            "method": "full_quote", "fetch_mode": "live",
            "credibility": {"domain": "example.com", "source_type": "academic", "tier": 4, "note": "Test"},
        },
    }
    proof_json_path.write_text(json.dumps(data))

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "cs-clean" in html
    assert "1/1 verified" in html
    assert "cs-flagged-item" not in html
    assert "citation-summary-bar" in html
    assert 'class="audit-header"' in html
    assert "Citation Verification Details</span>" not in html


def test_citation_summary_renders_flagged(site_fixture):
    """Flagged proof renders summary badge, flagged items, and preserves audit log."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["citations"] = {
        "B1": {
            "source_name": "Good Source", "url": "https://example.com/a",
            "status": "verified", "source_key": "src_a", "quote": "Quote A",
            "method": "full_quote", "fetch_mode": "live",
            "credibility": {"domain": "example.com", "source_type": "academic", "tier": 4, "note": "Test"},
        },
        "B2": {
            "source_name": "Partial Source", "url": "https://example.com/b",
            "status": "partial", "source_key": "src_b", "quote": "Quote B",
            "method": "aggressive_normalization", "fetch_mode": "live",
            "credibility": {"domain": "other.com", "source_type": "unknown", "tier": 2, "note": "Test"},
        },
    }
    proof_json_path.write_text(json.dumps(data))

    audit_path = site_fixture / "site" / "proofs" / "test-claim" / "proof_audit.md"
    audit_text = audit_path.read_text()
    audit_text += (
        "\n\n## Citation Verification Details\n\n"
        "**B1 — Good Source**\n- Status: verified\n\n"
        "**B2 — Partial Source**\n- Status: partial\n"
        "- Impact: Low impact — claim does not depend solely on this source.\n"
    )
    audit_path.write_text(audit_text)

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "cs-notice" in html
    assert "cs-flagged-item" in html
    assert "matched after normalization" in html
    assert "1/2 unflagged" in html
    assert "citation-summary-bar" in html
    assert "Citation Verification Details</span>" not in html
    assert "cs-full-details" in html
    assert "Impact: Low impact" in html


def test_citation_summary_absent_for_math_proof(site_fixture):
    """Pure-math proof (no citations) has no citation summary."""
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "citation-summary-bar" not in html


def test_citation_summary_renders_fetch_failed(site_fixture):
    """fetch_failed renders with distinct badge text and reason."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["fact_registry"]["B2"] = {"label": "blocked source"}
    data["citations"] = {
        "B1": {
            "source_name": "Good Source", "url": "https://example.com/a",
            "status": "verified", "source_key": "src_a", "quote": "Quote A",
            "method": "full_quote", "fetch_mode": "live",
            "credibility": {"domain": "example.com", "source_type": "academic", "tier": 4, "note": "Test"},
        },
        "B2": {
            "source_name": "Blocked Source", "url": "https://example.com/b",
            "status": "fetch_failed", "source_key": "src_b", "quote": "Quote B",
            "method": None, "fetch_mode": "live",
            "credibility": {"domain": "other.com", "source_type": "unknown", "tier": 3, "note": "Test"},
        },
    }
    proof_json_path.write_text(json.dumps(data))

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "cs-warning" in html
    assert "fetch failed" in html
    assert "source could not be fetched" in html
    assert "evidence-failed" in html
    assert "Fetch Failed" in html


def test_citation_summary_evidence_table_legacy_failed(site_fixture):
    """Legacy 'failed' status renders as 'Fetch Failed' in evidence table."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["citations"] = {
        "B1": {
            "source_name": "Legacy Source", "url": "https://example.com/a",
            "status": "failed", "source_key": "src_a", "quote": "Quote A",
            "method": None, "fetch_mode": "live",
            "credibility": {"domain": "example.com", "source_type": "unknown", "tier": 3, "note": "Test"},
        },
    }
    proof_json_path.write_text(json.dumps(data))

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "cs-warning" in html
    assert "source could not be fetched" in html
    assert "evidence-failed" in html
    assert "Fetch Failed" in html


def test_citation_summary_renders_wayback(site_fixture):
    """Wayback-fetched citation renders with flag reason."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["citations"] = {
        "B1": {
            "source_name": "Wayback Source", "url": "https://example.com/a",
            "status": "verified", "source_key": "src_a", "quote": "Quote A",
            "method": "full_quote", "fetch_mode": "wayback",
            "credibility": {"domain": "example.com", "source_type": "academic", "tier": 4, "note": "Test"},
        },
    }
    proof_json_path.write_text(json.dumps(data))

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "cs-flagged-item" in html
    assert "fetched from Wayback Machine" in html


def test_citation_summary_clean_has_full_details(site_fixture):
    """Clean proof still has 'Original audit log' expandable when audit section exists."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["citations"] = {
        "B1": {
            "source_name": "Test Source", "url": "https://example.com/source",
            "status": "verified", "source_key": "test_src", "quote": "Test quote",
            "method": "full_quote", "fetch_mode": "live",
            "credibility": {"domain": "example.com", "source_type": "academic", "tier": 4, "note": "Test"},
        },
    }
    proof_json_path.write_text(json.dumps(data))

    audit_path = site_fixture / "site" / "proofs" / "test-claim" / "proof_audit.md"
    audit_text = audit_path.read_text()
    audit_text += "\n\n## Citation Verification Details\n\n**B1 — Test Source**\n- Status: verified\n"
    audit_path.write_text(audit_text)

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "cs-all-clean" in html
    assert "cs-full-details" in html


def test_citation_audit_fallback_no_structured_citations(site_fixture):
    """Proof with no citations in proof.json but with Citation Verification Details
    in proof_audit.md still renders the audit section via the fallback path."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data.pop("citations", None)
    proof_json_path.write_text(json.dumps(data))

    audit_path = site_fixture / "site" / "proofs" / "test-claim" / "proof_audit.md"
    audit_text = audit_path.read_text()
    audit_text += (
        "\n\n## Citation Verification Details\n\n"
        "**B1 — Example Source**\n- Status: verified\n"
    )
    audit_path.write_text(audit_text)

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "citation-summary-bar" not in html
    assert "Citation Verification Details" in html
    assert "Example Source" in html


def test_citation_summary_stale_audit_json_authoritative(site_fixture):
    """When proof.json says verified but proof_audit.md says fetch_failed,
    the summary badge uses proof.json (authoritative)."""
    proof_json_path = site_fixture / "site" / "proofs" / "test-claim" / "proof.json"
    data = json.loads(proof_json_path.read_text())
    data["citations"] = {
        "B1": {
            "source_name": "Re-run Source", "url": "https://example.com/a",
            "status": "verified", "source_key": "src_a", "quote": "Quote A",
            "method": "full_quote", "fetch_mode": "live",
            "credibility": {"domain": "example.com", "source_type": "academic", "tier": 4, "note": "Test"},
        },
    }
    proof_json_path.write_text(json.dumps(data))

    audit_path = site_fixture / "site" / "proofs" / "test-claim" / "proof_audit.md"
    audit_text = audit_path.read_text()
    audit_text += (
        "\n\n## Citation Verification Details\n\n"
        "**B1 — Re-run Source**\n- Status: fetch_failed\n- Fetch mode: live (HTTP 403)\n"
        "- Impact: This source could not be fetched.\n"
    )
    audit_path.write_text(audit_text)

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "cs-clean" in html
    assert "1/1 verified" in html
    assert "cs-full-details" in html
    assert "fetch_failed" in html
    assert "citation-summary-bar" in html
    assert "Citation Verification Details</span>" not in html


def test_proof_page_has_narrative_content(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "What was claimed?" in html or "What Was Claimed?" in html
    assert "What did we find?" in html or "What Did We Find?" in html


def test_proof_page_has_detailed_evidence_collapsible(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "Detailed Evidence" in html


def test_proof_page_meta_description_uses_hook(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "confirmed true" in html or "overwhelming" in html


def test_proof_page_share_bar_has_hook(site_fixture):
    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "data-hook=" in html


def test_citation_files_generated(site_fixture):
    """Build should generate cite.bib, cite.ris, cite.txt for each proof."""
    _run_build(site_fixture)
    out = site_fixture / "_site" / "proofs" / "test-claim"
    assert (out / "cite.bib").exists()
    assert (out / "cite.ris").exists()
    assert (out / "cite.txt").exists()


def test_citation_bibtex_content(site_fixture):
    _run_build(site_fixture)
    bib = (site_fixture / "_site" / "proofs" / "test-claim" / "cite.bib").read_text()
    assert "@misc{proofengine_test_claim," in bib
    assert "Proof Engine" in bib
    assert "2025" in bib  # from fixture's generated_at


def test_citation_ris_content(site_fixture):
    _run_build(site_fixture)
    ris = (site_fixture / "_site" / "proofs" / "test-claim" / "cite.ris").read_text()
    assert "TY  - DATA" in ris
    assert "ER  -" in ris


def test_citation_txt_has_apa_and_chicago(site_fixture):
    _run_build(site_fixture)
    txt = (site_fixture / "_site" / "proofs" / "test-claim" / "cite.txt").read_text()
    assert "APA:" in txt
    assert "Chicago:" in txt


def test_citation_with_doi_json(site_fixture):
    """When doi.json exists, citation files include the DOI."""
    proof_dir = site_fixture / "site" / "proofs" / "test-claim"
    (proof_dir / "doi.json").write_text(json.dumps({
        "doi": "10.5281/zenodo.999",
        "zenodo_id": "999",
        "concept_doi": "10.5281/zenodo.990",
        "concept_zenodo_id": "990",
        "claim_natural": "Test claim is true",
        "minted_at": "2026-01-01",
    }))
    _run_build(site_fixture)
    bib = (site_fixture / "_site" / "proofs" / "test-claim" / "cite.bib").read_text()
    assert "10.5281/zenodo.999" in bib
    ris = (site_fixture / "_site" / "proofs" / "test-claim" / "cite.ris").read_text()
    assert "10.5281/zenodo.999" in ris


def test_built_proof_json_has_citation_block(site_fixture):
    """The built proof.json should include a citation block."""
    _run_build(site_fixture)
    built = json.loads(
        (site_fixture / "_site" / "proofs" / "test-claim" / "proof.json").read_text()
    )
    assert "citation" in built
    assert built["citation"]["author"] == "Proof Engine"
    assert built["citation"]["url"].endswith("/proofs/test-claim/")


def test_index_json_has_doi_field(site_fixture):
    """The site index.json should include doi per proof (null when no DOI)."""
    _run_build(site_fixture)
    index = json.loads((site_fixture / "_site" / "index.json").read_text())
    proof_entry = index["proofs"][0]
    assert "doi" in proof_entry
    assert proof_entry["doi"] is None


def test_index_json_has_doi_when_present(site_fixture):
    proof_dir = site_fixture / "site" / "proofs" / "test-claim"
    (proof_dir / "doi.json").write_text(json.dumps({
        "doi": "10.5281/zenodo.999",
        "zenodo_id": "999",
        "concept_doi": "10.5281/zenodo.990",
        "concept_zenodo_id": "990",
        "claim_natural": "Test claim is true",
        "minted_at": "2026-01-01",
    }))
    _run_build(site_fixture)
    index = json.loads((site_fixture / "_site" / "index.json").read_text())
    assert index["proofs"][0]["doi"] == "10.5281/zenodo.999"


def test_proof_page_has_cite_section(site_fixture):
    """The rendered proof page should contain the citation details element."""
    _run_build(site_fixture)
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert 'class="cite-section"' in html
    assert "Cite this proof" in html
    assert "cite-apa" in html
    assert "cite-bibtex" in html


def test_proof_page_cite_has_download_links(site_fixture):
    _run_build(site_fixture)
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "cite.bib" in html
    assert "cite.ris" in html


def test_proof_page_cite_shows_doi_when_present(site_fixture):
    proof_dir = site_fixture / "site" / "proofs" / "test-claim"
    (proof_dir / "doi.json").write_text(json.dumps({
        "doi": "10.5281/zenodo.999",
        "zenodo_id": "999",
        "concept_doi": "10.5281/zenodo.990",
        "concept_zenodo_id": "990",
        "claim_natural": "Test claim is true",
        "minted_at": "2026-01-01",
    }))
    _run_build(site_fixture)
    html = (site_fixture / "_site" / "proofs" / "test-claim" / "index.html").read_text()
    assert "10.5281/zenodo.999" in html
    assert "doi.org/10.5281/zenodo.999" in html


def test_v2_proof_renders_correctly(site_fixture):
    """V2 proof should render with v2 section names and layout."""
    v2_dir = site_fixture / "site" / "proofs" / "v2-test-proof"
    v2_dir.mkdir(parents=True)

    (v2_dir / "proof.json").write_text(json.dumps({
        "format_version": 2,
        "fact_registry": {"B1": {"label": "Test fact", "key": "test_fact"}},
        "claim_formal": {"subject": "Test", "property": "value", "operator": ">",
                         "operator_note": "Strictly greater", "threshold": 0},
        "claim_natural": "Test v2 claim is true",
        "verdict": "PROVED",
        "key_results": {"value": 1},
        "generator": {"name": "proof-engine", "version": "1.15.0",
                       "repo": "https://github.com/yaniv-golan/proof-engine",
                       "generated_at": "2026-04-11"},
        "citations": {
            "B1": {
                "source_name": "Test Source", "url": "https://example.com",
                "status": "verified", "method": "full_quote", "fetch_mode": "live",
                "quote": "test quote",
                "credibility": {"domain": "example.com", "source_type": "academic",
                                "tier": 4, "note": ""},
            }
        },
    }))

    (v2_dir / "proof.md").write_text(
        "# Proof: Test\n\n"
        "## Evidence Summary\n| ID | Fact | Verified |\n|---|---|---|\n| B1 | Test | Yes |\n\n"
        "## Proof Logic\nTest logic\n\n"
        "## Conclusion\n**PROVED.** Test.\n\n"
        "## What could challenge this verdict?\nNo counter-evidence found.\n"
    )

    (v2_dir / "proof_audit.md").write_text(
        "# Audit: Test\n\n"
        "## Claim Specification\n| Field | Value |\n|---|---|\n| Subject | test |\n\n"
        "## Claim Interpretation\nTest interpretation moved here.\n\n"
        "## Citation Verification Details\nAll verified.\n\n"
        "## Quality Checks\nAll rules pass.\n\n"
        "## Source Data\nB1: verified.\n"
    )

    (v2_dir / "proof_narrative.md").write_text(
        "# Proof Narrative: Test v2 claim is true\n\n"
        "## Verdict\n**Verdict: PROVED**\nTest hook.\n\n"
        "## What Was Claimed?\nTest claim.\n\n"
        "## What Did We Find?\nTest findings are strong. Multiple sources confirmed.\n\n"
        "## What Should You Keep In Mind?\nTest caveats.\n\n"
        "## How Was This Verified?\nTest method.\n"
    )

    (v2_dir / "meta.yaml").write_text("tags:\n  - science\n")
    (v2_dir / "proof.py").write_text("# proof script\n")

    result = _run_build(site_fixture)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"

    html = (site_fixture / "_site" / "proofs" / "v2-test-proof" / "index.html").read_text()

    # V2 section names should appear
    assert "What could challenge this verdict?" in html
    assert "Quality Checks" in html
    assert "Source Data" in html
    assert "Claim Interpretation" in html

    # V1-only sections should NOT appear
    assert "Key Findings" not in html
    assert "Hardening Checklist" not in html
    assert "Extraction Records" not in html

    # Canonical sources table should render
    assert "sources-table" in html
    assert "Academic" in html  # source_type_labels display value


# --- Math rendering integration tests ---


def test_strip_latex_passthrough_for_plain_claims():
    """strip_latex must not alter claims without LaTeX delimiters."""
    claim = "The US dollar has lost 95% of its purchasing power"
    assert strip_latex(claim) == claim


def test_strip_latex_converts_math_claim():
    """strip_latex converts LaTeX to Unicode for meta/title contexts."""
    claim = r"The rate \(\alpha_i\) exceeds \(\beta\)"
    result = strip_latex(claim)
    assert r"\(" not in result
    assert "\u03B1" in result  # alpha
    assert "\u03B2" in result  # beta


def test_strip_latex_preserves_currency():
    """Currency $ signs must not be touched by strip_latex."""
    claim = "If a company raises $5 million at a $25 million valuation"
    assert strip_latex(claim) == claim


def test_pipeline_example_claim_stripped(tmp_path):
    """build_pipeline_example_data must strip LaTeX from claim_natural."""
    slug = "math-proof"
    proof_dir = tmp_path / "proofs" / slug
    proof_dir.mkdir(parents=True)
    (proof_dir / "proof.py").write_text("x = 1\ndef run():\n    compare(a, b)\n")
    proof = {
        "slug": slug,
        "proof_data": {
            "claim_natural": r"The rate \(\alpha_i\) exceeds threshold",
            "citations": {
                "B1": {
                    "source_name": "Source",
                    "url": "https://example.com",
                    "status": "verified",
                    "method": "full_quote",
                    "quote": "A supporting quote here",
                    "credibility": {"source_type": "government"},
                },
            },
            "claim_formal": {
                "subject": "S", "property": "P",
                "operator": ">", "threshold": 0,
            },
        },
        "verdict": {"raw": "PROVED", "category": "proved"},
    }
    out = build_pipeline_example_data(proof, "/base/", tmp_path / "proofs")
    assert out is not None
    assert r"\(" not in out["claim_natural"]
    assert "\u03B1" in out["claim_natural"]  # alpha converted to Unicode


# --- Math-claim fixture: full build integration tests ---

@pytest.fixture
def site_fixture_math(tmp_path):
    """Site fixture with a math-containing claim for integration tests."""
    repo_root = Path(__file__).parent.parent
    site_src = repo_root / "site"

    shutil.copytree(site_src / "templates", tmp_path / "site" / "templates")
    shutil.copytree(site_src / "static", tmp_path / "site" / "static")
    shutil.copytree(site_src / "content", tmp_path / "site" / "content")

    proof_dir = tmp_path / "site" / "proofs" / "math-claim"
    proof_dir.mkdir(parents=True)

    math_claim = r"The Nash equilibrium rate \(\alpha^{NE}\) exceeds the cooperative rate \(\alpha^{CO}\)"

    (proof_dir / "proof.md").write_text(
        "# Proof\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| A1 | Verified |\n\n"
        "## Proof Logic\n\nBy FOC.\n\n"
        "## Conclusion\n\nThe claim is PROVED.\n"
    )
    (proof_dir / "proof_audit.md").write_text(
        "# Audit\n\n## Claim Specification\n\n| Field | Value |\n|---|---|\n| Subject | Rates |\n\n"
        "## Claim Interpretation\n\nNash vs cooperative.\n\n"
        "## Hardening Checklist\n\nAll pass.\n"
    )
    (proof_dir / "proof_narrative.md").write_text(
        "# Proof Narrative: " + math_claim + "\n\n"
        "## Verdict\n\n"
        "**Verdict: PROVED**\n\n"
        "Yes — the Nash equilibrium automation rate exceeds the cooperative optimum "
        "beyond any reasonable doubt. The algebraic gap is strictly positive. "
        "The evidence is confirmed across symbolic and numerical verification.\n\n"
        "## What was claimed?\n\n"
        "That the Nash rate exceeds the cooperative rate. This matters for policy "
        "because it shows firms systematically over-automate relative to the social "
        "optimum when they ignore demand externalities. "
        "Getting this right affects workforce planning.\n\n"
        "## What did we find?\n\n"
        "Symbolic differentiation confirms both FOC solutions. "
        "The gap is strictly positive for N >= 2. "
        "Numerical cross-checks at representative parameters agree. "
        "Second-order conditions verify both are global maxima. "
        "No parameter regime produces a zero or negative gap. "
        "The dominant-strategy property means the result is robust. "
        "Multiple adversarial checks found no issues. "
        "The demand function stays positive across all feasible profiles. "
        "Interiority conditions are documented as parameter assumptions. "
        "Cross-referencing against the theoretical economics literature confirms consistency.\n\n"
        "## What should you keep in mind?\n\n"
        "This covers the specific model as stated. "
        "Different demand structures might yield different results. "
        "Interiority of solutions is assumed.\n\n"
        "## How was this verified?\n\n"
        "Verified through symbolic computation with SymPy. "
        "See [the structured proof report](proof.md), "
        "[the full verification audit](proof_audit.md), "
        "or [re-run the proof yourself](proof.py).\n"
    )
    (proof_dir / "proof.py").write_text("# proof script\n")
    (proof_dir / "proof.json").write_text(json.dumps({
        "format_version": 2,
        "fact_registry": {"A1": {"label": "NE rate", "method": "SymPy FOC", "result": "Confirmed"}},
        "claim_formal": {
            "subject": "Automation rates", "property": "NE > CO", "operator": ">",
            "operator_note": "Strictly greater", "threshold": 0,
        },
        "claim_natural": math_claim,
        "verdict": "PROVED",
        "key_results": {"gap_positive": True},
        "generator": {
            "name": "proof-engine", "version": "1.16.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-04-16",
        },
    }))
    (proof_dir / "meta.yaml").write_text("tags:\n  - economics\n")

    (proof_dir.parent / "featured.json").write_text(
        json.dumps(["math-claim"]) + "\n",
    )

    return tmp_path


def test_math_claim_og_title_stripped(site_fixture_math):
    """OG title for math claims must use strip_latex (no raw LaTeX in meta)."""
    result = _run_build(site_fixture_math)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture_math / "_site" / "proofs" / "math-claim" / "index.html").read_text()
    # og:title should have Unicode, not raw LaTeX delimiters
    import re
    og_match = re.search(r'og:title"\s+content="([^"]*)"', html)
    assert og_match, "og:title meta tag not found"
    og_title = og_match.group(1)
    assert r"\(" not in og_title, f"og:title contains raw LaTeX: {og_title}"
    assert "\u03B1" in og_title or "α" in og_title, f"og:title missing Unicode alpha: {og_title}"


def test_math_claim_page_title_stripped(site_fixture_math):
    """<title> for math claims must use strip_latex."""
    result = _run_build(site_fixture_math)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture_math / "_site" / "proofs" / "math-claim" / "index.html").read_text()
    import re
    title_match = re.search(r'<title>(.*?)</title>', html)
    assert title_match, "<title> tag not found"
    title = title_match.group(1)
    assert r"\(" not in title, f"<title> contains raw LaTeX: {title}"


def test_math_claim_json_ld_stripped(site_fixture_math):
    """JSON-LD claimReviewed must use strip_latex."""
    result = _run_build(site_fixture_math)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture_math / "_site" / "proofs" / "math-claim" / "index.html").read_text()
    assert '"@type": "ClaimReview"' in html
    import re
    cr_match = re.search(r'"claimReviewed":\s*"([^"]*)"', html)
    assert cr_match, "claimReviewed not found in JSON-LD"
    claim_reviewed = cr_match.group(1)
    assert r"\(" not in claim_reviewed, f"claimReviewed contains raw LaTeX: {claim_reviewed}"


def test_math_claim_h1_has_raw_latex(site_fixture_math):
    """The <h1> should keep raw LaTeX delimiters for KaTeX to render."""
    result = _run_build(site_fixture_math)
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    html = (site_fixture_math / "_site" / "proofs" / "math-claim" / "index.html").read_text()
    import re
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    assert h1_match, "<h1> not found"
    h1 = h1_match.group(1)
    # h1 should contain raw \( for KaTeX auto-render
    assert r"\(" in h1 or "\\(" in h1, f"<h1> missing LaTeX delimiters: {h1}"
