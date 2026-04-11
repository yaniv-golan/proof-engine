"""Tests for format_version-aware proof loading."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
from tools.lib.proof_loader import load_proof

@pytest.fixture(autouse=True)
def mock_llm_tag():
    """Mock llm_tag globally so tests don't call the real claude CLI."""
    with patch("tools.lib.proof_loader.llm_tag", return_value=["health"]) as m:
        yield m


@pytest.fixture
def v1_proof_dir(tmp_path):
    """Create a minimal v1 proof directory (no format_version in proof.json)."""
    d = tmp_path / "test-v1-proof"
    d.mkdir()

    proof_json = {
        "fact_registry": {
            "B1": {"label": "Test fact", "key": "test_fact"},
            "A1": {"label": "Count", "method": "count", "result": "1"},
        },
        "claim_formal": {"subject": "test"},
        "claim_natural": "Test claim for v1",
        "verdict": "PROVED",
        "key_results": ["Test result"],
        "generator": {
            "name": "proof-engine",
            "version": "1.14.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-04-11",
        },
        "citations": {
            "B1": {
                "source_name": "Test Source",
                "url": "https://example.com",
                "status": "verified",
                "method": "full_quote",
                "fetch_mode": "live",
                "quote": "test quote",
                "credibility": {"domain": "example.com", "source_type": "academic", "tier": 4, "note": ""},
            }
        },
    }
    (d / "proof.json").write_text(json.dumps(proof_json))

    (d / "proof.md").write_text(
        "# Proof: Test\n\n"
        "## Key Findings\nTest findings\n\n"
        "## Claim Interpretation\nTest interpretation\n\n"
        "## Evidence Summary\n| ID | Fact | Verified |\n|---|---|---|\n| B1 | Test | Yes |\n\n"
        "## Proof Logic\nTest logic\n\n"
        "## Conclusion\n**PROVED.** Test.\n\n"
        "## Counter-Evidence Search\nNo counter-evidence found.\n"
    )

    (d / "proof_audit.md").write_text(
        "# Audit: Test\n\n"
        "## Claim Specification\n| Field | Value |\n|---|---|\n| Subject | test |\n\n"
        "## Fact Registry\n| ID | Key |\n|---|---|\n| B1 | test |\n\n"
        "## Full Evidence Table\nTest\n\n"
        "## Citation Verification Details\nAll verified.\n\n"
        "## Computation Traces\n1 >= 1 = True\n\n"
        "## Independent Source Agreement\nN/A\n\n"
        "## Adversarial Checks\nNone found.\n\n"
        "## Hardening Checklist\nAll rules pass.\n\n"
        "## Source Credibility Assessment\nTier 4.\n\n"
        "## Extraction Records\nB1: verified.\n"
    )

    (d / "proof_narrative.md").write_text(
        "# Proof Narrative: Test\n\n"
        "## Verdict\n**Verdict: PROVED**\nTest hook.\n\n"
        "## What Was Claimed?\nTest claim.\n\n"
        "## What Did We Find?\nTest findings.\n\n"
        "## What Should You Keep In Mind?\nTest caveats.\n\n"
        "## How Was This Verified?\nTest method.\n"
    )

    (d / "meta.yaml").write_text("tags:\n  - science\n")

    return d


def test_v1_proof_has_format_version_1(v1_proof_dir):
    """V1 proof (no format_version in JSON) should get format_version=1."""
    proof = load_proof(v1_proof_dir)
    assert proof["format_version"] == 1


def test_v1_proof_loads_without_error(v1_proof_dir):
    """V1 proof with old section names should load cleanly."""
    proof = load_proof(v1_proof_dir)
    assert proof["verdict"]["raw"] == "PROVED"
    assert "Key Findings" in proof["sections_md"]
    assert "Claim Interpretation" in proof["sections_md"]
    assert "Counter-Evidence Search" in proof["sections_md"]


@pytest.fixture
def v2_proof_dir(tmp_path):
    """Create a minimal v2 proof directory (format_version: 2 in proof.json)."""
    d = tmp_path / "test-v2-proof"
    d.mkdir()

    proof_json = {
        "format_version": 2,
        "fact_registry": {
            "B1": {"label": "Test fact", "key": "test_fact"},
            "A1": {"label": "Count", "method": "count", "result": "1"},
        },
        "claim_formal": {"subject": "test"},
        "claim_natural": "Test claim for v2",
        "verdict": "PROVED",
        "key_results": ["Test result"],
        "generator": {
            "name": "proof-engine",
            "version": "1.15.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-04-11",
        },
        "citations": {
            "B1": {
                "source_name": "Test Source",
                "url": "https://example.com",
                "status": "verified",
                "method": "full_quote",
                "fetch_mode": "live",
                "quote": "test quote",
                "credibility": {"domain": "example.com", "source_type": "academic", "tier": 4, "note": ""},
            }
        },
    }
    (d / "proof.json").write_text(json.dumps(proof_json))

    # V2 proof.md: no Key Findings, no Claim Interpretation, renamed counter-evidence
    (d / "proof.md").write_text(
        "# Proof: Test\n\n"
        "## Evidence Summary\n| ID | Fact | Verified |\n|---|---|---|\n| B1 | Test | Yes |\n\n"
        "## Proof Logic\nTest logic\n\n"
        "## Conclusion\n**PROVED.** Test.\n\n"
        "## What could challenge this verdict?\nNo counter-evidence found.\n"
    )

    # V2 proof_audit.md: Claim Interpretation moved here, renamed sections
    (d / "proof_audit.md").write_text(
        "# Audit: Test\n\n"
        "## Claim Specification\n| Field | Value |\n|---|---|\n| Subject | test |\n\n"
        "## Claim Interpretation\nTest interpretation moved here.\n\n"
        "## Fact Registry\n| ID | Key |\n|---|---|\n| B1 | test |\n\n"
        "## Full Evidence Table\nTest\n\n"
        "## Citation Verification Details\nAll verified.\n\n"
        "## Computation Traces\n1 >= 1 = True\n\n"
        "## Independent Source Agreement\nN/A\n\n"
        "## Adversarial Checks\nNone found.\n\n"
        "## Quality Checks\nAll rules pass.\n\n"
        "## Source Credibility Assessment\nAcademic.\n\n"
        "## Source Data\nB1: verified.\n"
    )

    (d / "proof_narrative.md").write_text(
        "# Proof Narrative: Test\n\n"
        "## Verdict\n**Verdict: PROVED**\nTest hook.\n\n"
        "## What Was Claimed?\nTest claim.\n\n"
        "## What Did We Find?\nTest findings.\n\n"
        "## What Should You Keep In Mind?\nTest caveats.\n\n"
        "## How Was This Verified?\nTest method.\n"
    )

    (d / "meta.yaml").write_text("tags:\n  - science\n")

    return d


def test_v2_proof_has_format_version_2(v2_proof_dir):
    """V2 proof should get format_version=2."""
    proof = load_proof(v2_proof_dir)
    assert proof["format_version"] == 2


def test_v2_proof_loads_without_error(v2_proof_dir):
    """V2 proof with new section names should load cleanly."""
    proof = load_proof(v2_proof_dir)
    assert proof["verdict"]["raw"] == "PROVED"
    assert "Evidence Summary" in proof["sections_md"]
    # Key Findings and Claim Interpretation should NOT be in proof.md for v2
    assert "Key Findings" not in proof["sections_md"]
    # Counter-evidence uses new title-cased heading
    assert "What Could Challenge This Verdict?" in proof["sections_md"]


def test_v2_proof_has_claim_interpretation_in_audit(v2_proof_dir):
    """V2 proof should have Claim Interpretation in proof_audit.md."""
    proof = load_proof(v2_proof_dir)
    assert "Claim Interpretation" in proof["sections_audit"]


@pytest.fixture
def v1_proof_dir_missing_claim_spec(tmp_path):
    """Create a v1 proof directory missing 'Claim Specification' in proof_audit.md."""
    d = tmp_path / "test-v1-no-claim-spec"
    d.mkdir()

    proof_json = {
        "fact_registry": {
            "B1": {"label": "Test fact", "key": "test_fact"},
            "A1": {"label": "Count", "method": "count", "result": "1"},
        },
        "claim_formal": {"subject": "test"},
        "claim_natural": "Test claim for v1",
        "verdict": "PROVED",
        "key_results": ["Test result"],
        "generator": {
            "name": "proof-engine",
            "version": "1.14.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-04-11",
        },
        "citations": {
            "B1": {
                "source_name": "Test Source",
                "url": "https://example.com",
                "status": "verified",
                "method": "full_quote",
                "fetch_mode": "live",
                "quote": "test quote",
                "credibility": {"domain": "example.com", "source_type": "academic", "tier": 4, "note": ""},
            }
        },
    }
    (d / "proof.json").write_text(json.dumps(proof_json))

    (d / "proof.md").write_text(
        "# Proof: Test\n\n"
        "## Key Findings\nTest findings\n\n"
        "## Claim Interpretation\nTest interpretation\n\n"
        "## Evidence Summary\n| ID | Fact | Verified |\n|---|---|---|\n| B1 | Test | Yes |\n\n"
        "## Proof Logic\nTest logic\n\n"
        "## Conclusion\n**PROVED.** Test.\n\n"
        "## Counter-Evidence Search\nNo counter-evidence found.\n"
    )

    # proof_audit.md WITHOUT "Claim Specification" section
    (d / "proof_audit.md").write_text(
        "# Audit: Test\n\n"
        "## Fact Registry\n| ID | Key |\n|---|---|\n| B1 | test |\n\n"
        "## Full Evidence Table\nTest\n\n"
        "## Citation Verification Details\nAll verified.\n\n"
        "## Computation Traces\n1 >= 1 = True\n\n"
        "## Independent Source Agreement\nN/A\n\n"
        "## Adversarial Checks\nNone found.\n\n"
        "## Hardening Checklist\nAll rules pass.\n\n"
        "## Source Credibility Assessment\nTier 4.\n\n"
        "## Extraction Records\nB1: verified.\n"
    )

    (d / "proof_narrative.md").write_text(
        "# Proof Narrative: Test\n\n"
        "## Verdict\n**Verdict: PROVED**\nTest hook.\n\n"
        "## What Was Claimed?\nTest claim.\n\n"
        "## What Did We Find?\nTest findings.\n\n"
        "## What Should You Keep In Mind?\nTest caveats.\n\n"
        "## How Was This Verified?\nTest method.\n"
    )

    (d / "meta.yaml").write_text("tags:\n  - science\n")

    return d


def test_v1_missing_claim_spec_raises(v1_proof_dir_missing_claim_spec):
    """V1 proof without 'Claim Specification' in audit should raise ValueError."""
    with pytest.raises(ValueError, match="missing required"):
        load_proof(v1_proof_dir_missing_claim_spec)
