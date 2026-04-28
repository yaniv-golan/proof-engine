import json
import os
import pytest
import tempfile
from unittest.mock import patch
import yaml
from tools.lib.proof_loader import load_proof, load_all_proofs


@pytest.fixture(autouse=True)
def mock_llm_tag():
    """Mock llm_tag globally so tests don't call the real claude CLI."""
    with patch("tools.lib.proof_loader.llm_tag", return_value=["health"]) as m:
        yield m


@pytest.fixture
def proof_dir(tmp_path):
    """Create a minimal valid proof directory (v2 format, normalises to v3)."""
    slug_dir = tmp_path / "test-claim"
    slug_dir.mkdir()

    (slug_dir / "proof.md").write_text(
        "# Proof\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| A1 | X |\n\n"
        "## Proof Logic\n\nBecause Y.\n\n"
        "## Conclusion\n\nThe claim is PROVED.\n"
    )
    (slug_dir / "proof_audit.md").write_text(
        "# Audit\n\n## Claim Specification\n\n| Field | Value |\n|---|---|\n| Subject | Test |\n\n"
        "## Claim Interpretation\n\nMeans X.\n\n"
        "## Hardening Checklist\n\nAll pass.\n"
    )
    (slug_dir / "proof.py").write_text("# proof script\n")
    (slug_dir / "proof.json").write_text(json.dumps({
        "format_version": 2,
        "fact_registry": {"A1": {"label": "test", "method": "1 == 1", "result": "True"}},
        "claim_formal": {
            "subject": "Test",
            "property": "value",
            "operator": ">",
            "operator_note": "Strictly greater",
            "threshold": 0,
        },
        "claim_natural": "Test claim is true",
        "verdict": "PROVED",
        "key_results": {"value": 1},
        "generator": {
            "name": "proof-engine",
            "version": "0.9.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2025-01-15",
        },
    }))
    (slug_dir / "proof_narrative.md").write_text(
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
    return tmp_path


def test_load_proof_returns_dict(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert isinstance(proof, dict)
    assert proof["slug"] == "test-claim"


def test_load_proof_has_required_fields(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert "proof_data" in proof
    assert "sections_md" in proof
    assert "sections_audit" in proof
    assert "verdict" in proof
    assert "tags" in proof


def test_load_proof_extracts_verdict(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert proof["verdict"]["raw"] == "PROVED"


def test_load_proof_auto_tags(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert isinstance(proof["tags"], list)
    assert proof["tags"] == ["health"]
    # Should have cached to meta.yaml
    meta_path = proof_dir / "test-claim" / "meta.yaml"
    assert meta_path.exists()
    meta = yaml.safe_load(meta_path.read_text())
    assert meta["tags"] == ["health"]


def test_load_proof_meta_yaml_override(proof_dir):
    meta_path = proof_dir / "test-claim" / "meta.yaml"
    meta_path.write_text(yaml.dump({"tags": ["custom-tag", "Another Tag"]}))
    proof = load_proof(proof_dir / "test-claim")
    assert "custom-tag" in proof["tags"]
    assert "another-tag" in proof["tags"]


def test_load_proof_missing_generator_raises(proof_dir):
    data = json.loads((proof_dir / "test-claim" / "proof.json").read_text())
    del data["generator"]
    (proof_dir / "test-claim" / "proof.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="generator"):
        load_proof(proof_dir / "test-claim")


def test_load_proof_missing_required_section_raises(proof_dir):
    (proof_dir / "test-claim" / "proof.md").write_text(
        "# Proof\n\n## Key Findings\n\n- Found it\n"
    )
    with pytest.raises(ValueError, match="missing required"):
        load_proof(proof_dir / "test-claim")


def test_load_proof_theorem_profile_missing_sections_raises(proof_dir):
    """When claim_type == 'theorem', loader dispatches to v2_theorem profile.

    Existing v2-shaped proof.md (Evidence Summary / Proof Logic / Conclusion)
    is missing the theorem-required sections (Theorem Statement, Proof,
    Corollaries, Scope, Relation To Prior Work, What Could Challenge This
    Verdict?). The loader must raise ValueError naming those missing sections.
    """
    claim_dir = proof_dir / "test-claim"
    data = json.loads((claim_dir / "proof.json").read_text())
    data["claim_formal"]["claim_type"] = "theorem"
    (claim_dir / "proof.json").write_text(json.dumps(data))

    with pytest.raises(ValueError) as exc:
        load_proof(claim_dir)

    msg = str(exc.value)
    assert "missing required" in msg
    # At least some of the new theorem-only required sections must be flagged.
    assert "Theorem Statement" in msg
    assert "Corollaries" in msg


def test_load_proof_theorem_profile_with_all_sections_succeeds(proof_dir):
    """A theorem-typed proof with every canonical section should load cleanly."""
    claim_dir = proof_dir / "test-claim"
    data = json.loads((claim_dir / "proof.json").read_text())
    data["claim_formal"]["claim_type"] = "theorem"
    (claim_dir / "proof.json").write_text(json.dumps(data))

    (claim_dir / "proof.md").write_text(
        "# Proof\n\n"
        "## Theorem statement\n\nLet G be finite. Then P(G).\n\n"
        "## Proof\n\n1. Step one. 2. Step two.\n\n"
        "## Corollaries\n\nC1: trivially follows.\n\n"
        "## Scope\n\nNot covered: infinite G.\n\n"
        "## Relation to prior work\n\nMonderer & Shapley 1996.\n\n"
        "## What could challenge this verdict?\n\nA counterexample.\n\n"
        "## Conclusion\n\n**PROVED.** The theorem holds.\n"
    )

    # v2_theorem audit profile requires Implementation Regression Checks.
    (claim_dir / "proof_audit.md").write_text(
        "# Audit\n\n## Implementation Regression Checks\n\nSampled N games; 0 violations.\n"
    )

    proof = load_proof(claim_dir)
    assert proof["slug"] == "test-claim"
    # Verify the title-cased canonical headings are present in the extracted sections.
    assert "Theorem Statement" in proof["sections_md"]
    assert "Corollaries" in proof["sections_md"]
    assert "Relation To Prior Work" in proof["sections_md"]


def test_load_all_proofs(proof_dir):
    proofs = load_all_proofs(proof_dir)
    assert len(proofs) == 1
    assert proofs[0]["slug"] == "test-claim"


def test_load_proof_citation_count_empirical(proof_dir):
    data = json.loads((proof_dir / "test-claim" / "proof.json").read_text())
    data["fact_registry"]["B1"] = {"label": "Source 1"}
    data["fact_registry"]["B2"] = {"label": "Source 2"}
    data["citations"] = {"B1": {"status": "verified"}, "B2": {"status": "verified"}}
    (proof_dir / "test-claim" / "proof.json").write_text(json.dumps(data))
    proof = load_proof(proof_dir / "test-claim")
    assert proof["citation_count"] == 2


def test_load_proof_citation_count_pure_math(proof_dir):
    proof = load_proof(proof_dir / "test-claim")
    assert proof["citation_count"] is None


def test_load_proof_search_count(proof_dir):
    """Absence proof with search_registry should have search_count."""
    data = json.loads((proof_dir / "test-claim" / "proof.json").read_text())
    data["fact_registry"]["S1"] = {"label": "PubMed search", "key": "search_a"}
    data["fact_registry"]["S2"] = {"label": "Cochrane search", "key": "search_b"}
    data["search_registry"] = {
        "search_a": {"database": "PubMed", "verification": {"status": "accessible"}},
        "search_b": {"database": "Cochrane", "verification": {"status": "accessible"}},
    }
    (proof_dir / "test-claim" / "proof.json").write_text(json.dumps(data))
    proof = load_proof(proof_dir / "test-claim")
    assert proof["search_count"] == 2


def test_load_proof_no_search_registry(proof_dir):
    """Proof without search_registry should have search_count None."""
    proof = load_proof(proof_dir / "test-claim")
    assert proof["search_count"] is None


def test_load_proof_meta_yaml_featured_raises(proof_dir):
    """meta.yaml with deprecated featured key should raise ValueError."""
    meta_path = proof_dir / "test-claim" / "meta.yaml"
    meta_path.write_text(yaml.dump({"featured": True}))
    with pytest.raises(ValueError, match="deprecated"):
        load_proof(proof_dir / "test-claim")


def test_load_all_proofs_applies_featured(proof_dir):
    """load_all_proofs should set featured=True for slugs in featured.json."""
    featured_path = proof_dir / "featured.json"
    featured_path.write_text(json.dumps(["test-claim"]))
    proofs = load_all_proofs(proof_dir)
    assert proofs[0]["featured"] is True


def test_load_all_proofs_no_featured_file(proof_dir):
    """Without featured.json, all proofs should have featured=False."""
    proofs = load_all_proofs(proof_dir)
    assert proofs[0]["featured"] is False


def test_load_all_proofs_featured_not_in_list(proof_dir):
    """Proofs not in featured.json should have featured=False."""
    featured_path = proof_dir / "featured.json"
    featured_path.write_text(json.dumps([]))
    proofs = load_all_proofs(proof_dir)
    assert proofs[0]["featured"] is False


def test_load_all_proofs_dangling_featured_raises(proof_dir):
    """Dangling ref in featured.json should raise."""
    featured_path = proof_dir / "featured.json"
    featured_path.write_text(json.dumps(["nonexistent-slug"]))
    with pytest.raises(ValueError, match="nonexistent-slug"):
        load_all_proofs(proof_dir)


def test_verdict_summary_strips_bold_prefix(proof_dir):
    """verdict_summary strips bold verdict prefix from Conclusion."""
    (proof_dir / "test-claim" / "proof.md").write_text(
        "# Proof\n\n## Key Findings\n\n- Found it\n\n"
        "## Claim Interpretation\n\nMeans X.\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| B1 | X |\n\n"
        "## Proof Logic\n\nBecause Y.\n\n"
        "## Conclusion\n\n**PROVED.** The claim holds under all conditions.\n"
    )
    proof = load_proof(proof_dir / "test-claim")
    assert proof["verdict_summary"] == "The claim holds under all conditions."


def test_verdict_summary_no_bold_prefix(proof_dir):
    """Conclusion without bold prefix uses first sentence as-is."""
    (proof_dir / "test-claim" / "proof.md").write_text(
        "# Proof\n\n## Key Findings\n\n- Found it\n\n"
        "## Claim Interpretation\n\nMeans X.\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| B1 | X |\n\n"
        "## Proof Logic\n\nBecause Y.\n\n"
        "## Conclusion\n\nThe claim is PROVED.\n"
    )
    proof = load_proof(proof_dir / "test-claim")
    assert proof["verdict_summary"] == "The claim is PROVED."


def test_verdict_summary_disproved_prefix(proof_dir):
    """DISPROVED bold prefix is stripped correctly."""
    (proof_dir / "test-claim" / "proof.md").write_text(
        "# Proof\n\n## Key Findings\n\n- Found it\n\n"
        "## Claim Interpretation\n\nMeans X.\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| B1 | X |\n\n"
        "## Proof Logic\n\nBecause Y.\n\n"
        "## Conclusion\n\n**DISPROVED.** The spider myth is false. "
        "All sources agree.\n"
    )
    proof = load_proof(proof_dir / "test-claim")
    assert proof["verdict_summary"] == "The spider myth is false."


VALID_NARRATIVE = (
    "# Proof Narrative: Test claim is true\n\n"
    "## Verdict\n\n"
    "**Verdict: PROVED**\n\n"
    "Yes — the test claim is confirmed true beyond any reasonable doubt whatsoever.\n\n"
    "## What was claimed?\n\n"
    "Test claim is true. This matters for science.\n\n"
    "## What did we find?\n\n"
    "We found strong evidence supporting the claim. "
    "Multiple independent sources confirmed the core assertion. "
    "The data was consistent across all measurements taken. "
    "No contradictory evidence was identified.\n\n"
    "## What should you keep in mind?\n\n"
    "This covers the specific claim as stated only.\n\n"
    "## How was this verified?\n\n"
    "Verified through computation. "
    "See [the structured proof report](proof.md), "
    "[the full verification audit](proof_audit.md), "
    "or [re-run the proof yourself](proof.py).\n"
)


def test_load_proof_has_narrative_fields(proof_dir):
    (proof_dir / "test-claim" / "proof_narrative.md").write_text(VALID_NARRATIVE)
    proof = load_proof(proof_dir / "test-claim")
    assert "sections_narrative" in proof
    assert "verdict_declaration" in proof
    assert "verdict_hook" in proof


def test_load_proof_narrative_sections(proof_dir):
    (proof_dir / "test-claim" / "proof_narrative.md").write_text(VALID_NARRATIVE)
    proof = load_proof(proof_dir / "test-claim")
    assert "Verdict" in proof["sections_narrative"]
    assert "What Was Claimed?" in proof["sections_narrative"]
    assert "What Did We Find?" in proof["sections_narrative"]
    assert "What Should You Keep In Mind?" in proof["sections_narrative"]
    assert "How Was This Verified?" in proof["sections_narrative"]


def test_load_proof_verdict_declaration(proof_dir):
    (proof_dir / "test-claim" / "proof_narrative.md").write_text(VALID_NARRATIVE)
    proof = load_proof(proof_dir / "test-claim")
    assert proof["verdict_declaration"] == "**Verdict: PROVED**"


def test_load_proof_verdict_hook(proof_dir):
    (proof_dir / "test-claim" / "proof_narrative.md").write_text(VALID_NARRATIVE)
    proof = load_proof(proof_dir / "test-claim")
    assert "confirmed true" in proof["verdict_hook"]
    # Hook should not contain the declaration line
    assert "**Verdict:" not in proof["verdict_hook"]


def test_load_proof_missing_narrative_raises(proof_dir):
    (proof_dir / "test-claim" / "proof_narrative.md").unlink()
    with pytest.raises(ValueError, match="proof_narrative.md"):
        load_proof(proof_dir / "test-claim")


def test_load_proof_narrative_missing_section_raises(proof_dir):
    bad = VALID_NARRATIVE.replace("## What should you keep in mind?", "## Other Section")
    (proof_dir / "test-claim" / "proof_narrative.md").write_text(bad)
    with pytest.raises(ValueError, match="missing required"):
        load_proof(proof_dir / "test-claim")


def test_load_proof_missing_section_shows_found(proof_dir):
    """Error message should include the sections that WERE found."""
    # Remove "Evidence Summary" section heading from proof.md
    claim_dir = proof_dir / "test-claim"
    proof_md = claim_dir / "proof.md"
    content = proof_md.read_text()
    content = content.replace("## Evidence Summary", "## Facts & Evidence")
    proof_md.write_text(content)

    with pytest.raises(ValueError, match="Found:"):
        load_proof(claim_dir)


def test_load_proof_tags_manual_without_tags_raises(proof_dir):
    """tags_manual: true without tags should raise ValueError."""
    meta_path = proof_dir / "test-claim" / "meta.yaml"
    meta_path.write_text(yaml.dump({"tags_manual": True}))
    with pytest.raises(ValueError, match="tags_manual.*no tags"):
        load_proof(proof_dir / "test-claim")


def test_load_proof_tags_manual_preserves_tags(proof_dir):
    """tags_manual: true with tags should use those tags and not call LLM."""
    meta_path = proof_dir / "test-claim" / "meta.yaml"
    meta_path.write_text(yaml.dump({"tags": ["economics"], "tags_manual": True}))
    proof = load_proof(proof_dir / "test-claim")
    assert proof["tags"] == ["economics"]


# ---- v3 native format tests ----

def _create_v3_proof_dir(base_dir, n_empirical=1, slug="test-v3"):
    """Create a minimal v3 proof directory with all required artifacts."""
    proof_dir = base_dir / slug
    proof_dir.mkdir()

    # Build evidence entries
    evidence = {}
    for i in range(1, n_empirical + 1):
        evidence[f"B{i}"] = {
            "type": "empirical",
            "label": f"Source {i}",
            "sub_claim": None,
            "source": {"name": f"Source {i}", "url": f"https://example.com/{i}", "quote": "Q"},
            "verification": {"status": "verified", "method": "full_quote",
                             "coverage_pct": 100.0, "fetch_mode": "live",
                             "credibility": {"domain": "example.com", "tier": 3}},
            "extraction": {"value": "v", "value_in_quote": True, "quote_snippet": "Q"},
        }
    evidence["A1"] = {
        "type": "computed", "label": "Count", "sub_claim": None,
        "method": f"count = {n_empirical}", "result": str(n_empirical),
        "depends_on": [f"B{i}" for i in range(1, n_empirical + 1)],
    }

    proof_data = {
        "format_version": 3,
        "claim_natural": "Test claim",
        "claim_formal": {"subject": "X", "property": "Y", "operator": "==", "threshold": 1},
        "evidence": evidence,
        "cross_checks": [{"description": "test", "fact_ids": ["A1"], "agreement": True}],
        "adversarial_checks": [{"question": "Any?", "finding": "No", "breaks_proof": False}],
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "key_results": {"n": n_empirical},
        "generator": {"name": "proof-engine", "version": "1.0.0",
                       "repo": "https://github.com/yaniv-golan/proof-engine",
                       "generated_at": "2026-04-13"},
    }
    (proof_dir / "proof.json").write_text(json.dumps(proof_data, indent=2))

    # proof.md — required sections: Evidence Summary, Proof Logic, Conclusion
    (proof_dir / "proof.md").write_text(
        "# Proof\n\n"
        "## Evidence Summary\n\nEvidence here.\n\n"
        "## Proof Logic\n\nLogic here.\n\n"
        "## Conclusion\n\n**PROVED.** Test conclusion.\n"
    )

    # proof_audit.md — required sections: Claim Specification, Claim Interpretation
    (proof_dir / "proof_audit.md").write_text(
        "# Audit\n\n"
        "## Claim Specification\n\nSpec.\n\n"
        "## Claim Interpretation\n\nInterpretation.\n"
    )

    # proof_narrative.md — required sections from REQUIRED_NARRATIVE_SECTIONS
    (proof_dir / "proof_narrative.md").write_text(
        "# Proof Narrative: Test claim\n\n"
        "## Verdict\n\n**Verdict: PROVED**\n\n"
        "This claim is fully verified through independent computation and empirical "
        "evidence from multiple sources. The evidence consistently supports the claim.\n\n"
        "## What Was Claimed?\n\n"
        "The test claim asserts a specific property about the subject under investigation.\n\n"
        "## What Did We Find?\n\n"
        "Multiple lines of evidence confirmed the claim. Empirical sources agreed with "
        "computed results, and no counter-evidence was found.\n\n"
        "## What Should You Keep In Mind?\n\n"
        "This proof is based on currently available data. Future data could change the "
        "conclusion. The sources used are reputable but not exhaustive.\n\n"
        "## How Was This Verified?\n\n"
        "Verification combined Type A (computed) and Type B (empirical) evidence. "
        "Citations were fetched and matched against source text. Cross-checks confirmed "
        "agreement. See [proof.md](proof.md), [proof_audit.md](proof_audit.md), "
        "and [proof.py](proof.py) for details.\n"
    )

    return proof_dir


def test_load_v3_proof(tmp_path, monkeypatch):
    """Proof loader handles v3 format natively."""
    monkeypatch.setattr("tools.lib.tagger.llm_tag", lambda claim: ["test"])
    from tools.lib.proof_loader import load_proof

    proof_dir = _create_v3_proof_dir(tmp_path)
    proof = load_proof(proof_dir)

    assert proof["format_version"] == 3
    assert proof["verdict"]["raw"]  # normalized verdict has 'raw' key


def test_v3_citation_count_from_evidence(tmp_path, monkeypatch):
    """Citation count derived from empirical evidence entries in v3."""
    monkeypatch.setattr("tools.lib.tagger.llm_tag", lambda claim: ["test"])
    from tools.lib.proof_loader import load_proof

    proof_dir = _create_v3_proof_dir(tmp_path, n_empirical=3)
    proof = load_proof(proof_dir)
    assert proof["citation_count"] == 3


def test_load_proof_exposes_depends_on(proof_dir, mock_llm_tag):
    """load_proof reads depends_on from meta.yaml and returns the parsed list."""
    meta = {
        "tags": ["test"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "arxiv", "value": "2603.21852"}]},
        ],
    }
    (proof_dir / "test-claim" / "meta.yaml").write_text(yaml.dump(meta))

    result = load_proof(proof_dir / "test-claim")
    deps = result["depends_on"]
    assert len(deps) == 1
    assert deps[0].relation == "IsDerivedFrom"
    assert deps[0].identifiers[0].type == "arxiv"
    assert deps[0].identifiers[0].value == "2603.21852"


def test_load_proof_absent_depends_on_returns_empty_list(proof_dir, mock_llm_tag):
    """A proof with no depends_on key in meta.yaml returns []."""
    result = load_proof(proof_dir / "test-claim")
    assert result["depends_on"] == []


def test_load_proof_rejects_invalid_depends_on(proof_dir, mock_llm_tag):
    """An unresolvable relation must be rejected at load time."""
    meta = {
        "tags": ["test"],
        "depends_on": [
            {"relation": "NotARealRelation",
             "identifiers": [{"type": "slug", "value": "u"}]},
        ],
    }
    (proof_dir / "test-claim" / "meta.yaml").write_text(yaml.dump(meta))
    with pytest.raises(ValueError, match="depends_on invalid"):
        load_proof(proof_dir / "test-claim")
