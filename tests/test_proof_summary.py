# tests/test_proof_summary.py

import sys
from pathlib import Path

# Make scripts importable
sys.path.insert(0, str(Path(__file__).parent.parent / "proof-engine" / "skills" / "proof-engine" / "scripts"))

import pytest


def test_builder_produces_v3_format():
    from proof_summary import ProofSummaryBuilder

    builder = ProofSummaryBuilder(
        claim_natural="X is Y",
        claim_formal={"subject": "X", "property": "Y", "operator": "==", "threshold": 1},
    )
    builder.add_computed_fact("A1", label="Primary check", method="1 == 1", result=True)
    builder.add_cross_check(
        description="Independent verification",
        fact_ids=["A1"],
        values_compared=["True", "True"],
        agreement=True,
    )
    builder.add_adversarial_check(
        question="Any counter-evidence?",
        verification_performed="Searched for counter-evidence",
        finding="None found",
        breaks_proof=False,
    )
    builder.set_key_results(primary_result=True, claim_holds=True)
    builder.set_verdict("PROVED")

    summary = builder.build()
    assert summary["format_version"] == 3
    assert "evidence" in summary
    assert summary["evidence"]["A1"]["type"] == "computed"
    assert isinstance(summary["verdict"], dict)
    assert summary["verdict"]["value"] == "PROVED"


def test_builder_empirical_fact():
    from proof_summary import ProofSummaryBuilder

    builder = ProofSummaryBuilder(
        claim_natural="test",
        claim_formal={"subject": "X", "property": "Y", "operator": ">=", "threshold": 1},
    )
    builder.add_empirical_fact(
        "B1", label="Source A", source_name="Example",
        source_url="https://example.com", source_quote="X is Y",
    )
    builder.set_verification("B1", status="verified", method="full_quote",
                              coverage_pct=100.0, fetch_mode="live")
    builder.set_extraction("B1", value="confirmed", value_in_quote=True,
                            quote_snippet="X is Y")
    builder.set_verdict("PROVED")
    builder.set_key_results(n_confirmed=1)

    summary = builder.build()
    b1 = summary["evidence"]["B1"]
    assert b1["type"] == "empirical"
    assert b1["source"]["name"] == "Example"
    assert b1["verification"]["status"] == "verified"
    assert b1["extraction"]["value"] == "confirmed"


def test_builder_search_fact():
    from proof_summary import ProofSummaryBuilder

    builder = ProofSummaryBuilder(
        claim_natural="No evidence of X",
        claim_formal={"subject": "X", "proof_direction": "absence"},
    )
    builder.add_search_fact(
        "S1", label="PubMed search",
        database="PubMed", url="https://pubmed.ncbi.nlm.nih.gov/",
        search_url="https://pubmed.ncbi.nlm.nih.gov/?term=test",
        query_terms="test", date_range="all", result_count=0,
        source_name="PubMed",
    )
    builder.set_verdict("SUPPORTED")
    builder.set_key_results(n_null_results=1)

    summary = builder.build()
    assert summary["evidence"]["S1"]["type"] == "search"
    assert summary["evidence"]["S1"]["search"]["database"] == "PubMed"


def test_builder_with_subclaim():
    from proof_summary import ProofSummaryBuilder

    builder = ProofSummaryBuilder(
        claim_natural="X and Y",
        claim_formal={"sub_claims": [{"id": "SC1"}, {"id": "SC2"}], "compound_operator": "AND"},
    )
    builder.add_empirical_fact("B1", label="SC1 source", source_name="A",
                                source_url="https://a.com", source_quote="q",
                                sub_claim="SC1")
    builder.add_empirical_fact("B2", label="SC2 source", source_name="B",
                                source_url="https://b.com", source_quote="q",
                                sub_claim="SC2")
    builder.set_verdict("PROVED")
    builder.set_key_results(result=True)

    summary = builder.build()
    assert summary["evidence"]["B1"]["sub_claim"] == "SC1"
    assert summary["evidence"]["B2"]["sub_claim"] == "SC2"


def test_builder_depends_on():
    from proof_summary import ProofSummaryBuilder

    builder = ProofSummaryBuilder(claim_natural="t", claim_formal={})
    builder.add_empirical_fact("B1", label="Source", source_name="A",
                                source_url="https://a.com", source_quote="q")
    builder.add_computed_fact("A1", label="Derived", method="calc(B1)",
                              result=42, depends_on=["B1"])
    builder.set_verdict("PROVED")
    builder.set_key_results(x=42)

    summary = builder.build()
    assert summary["evidence"]["A1"]["depends_on"] == ["B1"]


def test_builder_rejects_verdict_not_set():
    from proof_summary import ProofSummaryBuilder

    builder = ProofSummaryBuilder(claim_natural="t", claim_formal={})
    builder.add_computed_fact("A1", label="Test", method="1+1", result=2)
    builder.set_key_results(x=2)
    with pytest.raises(ValueError, match="[Vv]erdict"):
        builder.build()


def test_builder_rejects_unknown_fact_in_verification():
    from proof_summary import ProofSummaryBuilder

    builder = ProofSummaryBuilder(claim_natural="t", claim_formal={})
    with pytest.raises(KeyError):
        builder.set_verification("B99", status="verified", method="full_quote")


def test_builder_emit_prints_json(capsys):
    from proof_summary import ProofSummaryBuilder

    builder = ProofSummaryBuilder(claim_natural="test", claim_formal={})
    builder.add_computed_fact("A1", label="Test", method="1+1", result=2)
    builder.set_verdict("PROVED")
    builder.set_key_results(x=2)
    builder.emit()

    captured = capsys.readouterr()
    assert "=== PROOF SUMMARY (JSON) ===" in captured.out
    assert '"format_version": 3' in captured.out
