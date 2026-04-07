# tests/test_narrative_validator.py
import pytest
from tools.lib.narrative_validator import validate_narrative


VALID_NARRATIVE = (
    "# Proof Narrative: Test claim is true\n\n"
    "## Verdict\n\n"
    "**Verdict: PROVED**\n\n"
    "Yes — and the numbers confirm it clearly and without any doubt whatsoever. "
    "The evidence is overwhelming and consistent across every source we examined.\n\n"
    "## What was claimed?\n\n"
    "The test claim states that something is true. "
    "This matters because it affects how we understand the world "
    "and make decisions based on evidence. "
    "Getting this right has real consequences for policy and practice.\n\n"
    "## What did we find?\n\n"
    "We found strong evidence supporting the claim. "
    "Multiple independent sources confirmed the core assertion. "
    "They approached it from different angles and methodologies. "
    "The data was consistent across all measurements taken "
    "over the full range of conditions tested. "
    "No contradictory evidence was identified in any of the sources we examined. "
    "The primary computation yielded a result that matched theoretical predictions "
    "within a very tight tolerance. "
    "Secondary verification through an independent calculation confirmed the same figure. "
    "Cross-referencing against published reference data showed agreement to within one percent. "
    "The statistical significance of the finding exceeds conventional thresholds by a wide margin. "
    "When we tested the claim against adversarial scenarios designed to break it, "
    "the conclusion held firm in every case.\n\n"
    "## What should you keep in mind?\n\n"
    "This analysis covers the specific claim as stated. "
    "Different framings of the question might yield different results. "
    "The methodology used here is optimized for this particular type of quantitative claim "
    "and may not generalize to qualitative assertions.\n\n"
    "## How was this verified?\n\n"
    "This was verified through computation. "
    "See [the structured proof report](proof.md) for the full evidence chain, "
    "[the full verification audit](proof_audit.md) for every source checked, "
    "or [re-run the proof yourself](proof.py).\n"
)


def test_valid_narrative_passes():
    errors, warnings = validate_narrative(VALID_NARRATIVE, verdict="PROVED", claim_natural="Test claim is true")
    assert errors == []


def test_missing_section_is_error():
    bad = VALID_NARRATIVE.replace("## What should you keep in mind?", "## Something else")
    errors, _ = validate_narrative(bad, verdict="PROVED", claim_natural="Test claim is true")
    assert any("What Should You Keep In Mind?" in e for e in errors)


def test_word_count_too_low():
    short = (
        "# Proof Narrative: Short\n\n"
        "## Verdict\n\n**Verdict: PROVED**\n\nYes it is true and confirmed.\n\n"
        "## What was claimed?\n\nShort claim.\n\n"
        "## What did we find?\n\nFound it.\n\n"
        "## What should you keep in mind?\n\nNothing.\n\n"
        "## How was this verified?\n\nSee [x](proof.md) [y](proof_audit.md) [z](proof.py).\n"
    )
    errors, _ = validate_narrative(short, verdict="PROVED", claim_natural="Short")
    assert any("200" in e for e in errors)


def test_word_count_too_high():
    long_body = " ".join(["word"] * 900)
    long = (
        "# Proof Narrative: Long\n\n"
        "## Verdict\n\n**Verdict: PROVED**\n\nYes it is true and confirmed beyond doubt.\n\n"
        "## What was claimed?\n\nLong claim about things.\n\n"
        f"## What did we find?\n\n{long_body}\n\n"
        "## What should you keep in mind?\n\nNothing special.\n\n"
        "## How was this verified?\n\nSee [x](proof.md) [y](proof_audit.md) [z](proof.py).\n"
    )
    errors, _ = validate_narrative(long, verdict="PROVED", claim_natural="Long")
    assert any("800" in e for e in errors)


def test_fact_id_rejected():
    bad = VALID_NARRATIVE.replace("something is true", "fact A1 confirms it")
    errors, _ = validate_narrative(bad, verdict="PROVED", claim_natural="Test claim is true")
    assert any("fact id" in e.lower() for e in errors)


def test_fact_id_with_vitamin_context_not_rejected():
    """vitamin B12, vitamin B6 etc. should not trigger the fact ID check."""
    ok = VALID_NARRATIVE.replace("something is true", "vitamin B12 is essential")
    errors, _ = validate_narrative(ok, verdict="PROVED", claim_natural="Test claim is true")
    assert not any("fact id" in e.lower() for e in errors)


def test_missing_proof_md_link():
    bad = VALID_NARRATIVE.replace("(proof.md)", "(other.md)")
    errors, _ = validate_narrative(bad, verdict="PROVED", claim_natural="Test claim is true")
    assert any("proof.md" in e for e in errors)


def test_missing_proof_audit_link():
    bad = VALID_NARRATIVE.replace("(proof_audit.md)", "(other.md)")
    errors, _ = validate_narrative(bad, verdict="PROVED", claim_natural="Test claim is true")
    assert any("proof_audit.md" in e for e in errors)


def test_missing_proof_py_link():
    bad = VALID_NARRATIVE.replace("(proof.py)", "(other.py)")
    errors, _ = validate_narrative(bad, verdict="PROVED", claim_natural="Test claim is true")
    assert any("proof.py" in e for e in errors)


def test_verdict_mismatch_is_error():
    errors, _ = validate_narrative(VALID_NARRATIVE, verdict="DISPROVED", claim_natural="Test claim is true")
    assert any("verdict" in e.lower() for e in errors)


def test_qualified_verdict_must_match_exactly():
    qualified = VALID_NARRATIVE.replace("**Verdict: PROVED**", "**Verdict: PROVED (with unverified citations)**")
    errors, _ = validate_narrative(qualified, verdict="PROVED (with unverified citations)", claim_natural="Test claim is true")
    assert errors == []
    # But if proof.json says qualified and narrative drops the qualifier:
    errors2, _ = validate_narrative(VALID_NARRATIVE, verdict="PROVED (with unverified citations)", claim_natural="Test claim is true")
    assert any("verdict" in e.lower() for e in errors2)


def test_verdict_hook_too_short():
    short_hook = VALID_NARRATIVE.replace(
        "Yes — and the numbers confirm it clearly and without any doubt whatsoever. "
        "The evidence is overwhelming and consistent across every source we examined.",
        "Yes."
    )
    errors, _ = validate_narrative(short_hook, verdict="PROVED", claim_natural="Test claim is true")
    assert any("10 words" in e for e in errors)


def test_table_syntax_rejected():
    bad = VALID_NARRATIVE.replace(
        "Multiple independent sources confirmed the core assertion.",
        "| Col1 | Col2 |\n|---|---|\n| a | b |"
    )
    errors, _ = validate_narrative(bad, verdict="PROVED", claim_natural="Test claim is true")
    assert any("table" in e.lower() for e in errors)


def test_html_table_rejected():
    bad = VALID_NARRATIVE.replace(
        "Multiple independent sources confirmed the core assertion.",
        "<table><tr><td>a</td></tr></table>"
    )
    errors, _ = validate_narrative(bad, verdict="PROVED", claim_natural="Test claim is true")
    assert any("table" in e.lower() for e in errors)


def test_preamble_before_verdict_is_error():
    bad = "Some preamble text.\n\n" + VALID_NARRATIVE
    errors, _ = validate_narrative(bad, verdict="PROVED", claim_natural="Test claim is true")
    assert any("preamble" in e.lower() or "title" in e.lower() for e in errors)


def test_claim_drift_is_warning_not_error():
    _, warnings = validate_narrative(
        VALID_NARRATIVE.replace("something is true", "completely different topic"),
        verdict="PROVED",
        claim_natural="Quantum entanglement violates locality"
    )
    assert any("claim" in w.lower() for w in warnings)


def test_empty_nuance_section_is_error():
    bad = VALID_NARRATIVE.replace(
        "This analysis covers the specific claim as stated. "
        "Different framings of the question might yield different results. "
        "The methodology used here is optimized for this particular type of quantitative claim "
        "and may not generalize to qualitative assertions.",
        ""
    )
    errors, _ = validate_narrative(bad, verdict="PROVED", claim_natural="Test claim is true")
    assert any("keep in mind" in e.lower() or "empty" in e.lower() for e in errors)
