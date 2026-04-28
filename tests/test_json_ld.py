import json
import pytest
from tools.lib.json_ld import generate_claim_review


SAMPLE_PROOF_DATA = {
    "claim_natural": "The US dollar has lost more than 95% of its purchasing power",
    "verdict": "PROVED",
    "generator": {
        "generated_at": "2025-01-15",
    },
}


def test_generates_valid_json_ld():
    result = generate_claim_review(
        proof_data=SAMPLE_PROOF_DATA,
        canonical_url="https://example.com/proofs/test/",
    )
    parsed = json.loads(result)
    assert parsed["@type"] == "ClaimReview"


def test_claim_reviewed_from_claim_natural():
    result = json.loads(generate_claim_review(
        proof_data=SAMPLE_PROOF_DATA,
        canonical_url="https://example.com/proofs/test/",
    ))
    assert result["claimReviewed"] == SAMPLE_PROOF_DATA["claim_natural"]


def test_rating_value_proved():
    result = json.loads(generate_claim_review(
        proof_data=SAMPLE_PROOF_DATA,
        canonical_url="https://example.com/proofs/test/",
    ))
    assert result["reviewRating"]["ratingValue"] == 5


def test_rating_value_disproved():
    data = {**SAMPLE_PROOF_DATA, "verdict": "DISPROVED"}
    result = json.loads(generate_claim_review(
        proof_data=data,
        canonical_url="https://example.com/proofs/test/",
    ))
    assert result["reviewRating"]["ratingValue"] == 1


def test_author_is_hardcoded():
    result = json.loads(generate_claim_review(
        proof_data=SAMPLE_PROOF_DATA,
        canonical_url="https://example.com/proofs/test/",
    ))
    assert result["author"]["name"] == "Proof Engine"


def test_url_matches_canonical():
    result = json.loads(generate_claim_review(
        proof_data=SAMPLE_PROOF_DATA,
        canonical_url="https://example.com/proofs/my-proof/",
    ))
    assert result["url"] == "https://example.com/proofs/my-proof/"


def test_date_from_generator():
    result = json.loads(generate_claim_review(
        proof_data=SAMPLE_PROOF_DATA,
        canonical_url="https://example.com/proofs/test/",
    ))
    assert result["datePublished"] == "2025-01-15"


def test_rating_value_supported():
    data = {**SAMPLE_PROOF_DATA, "verdict": "SUPPORTED"}
    result = json.loads(generate_claim_review(data, "https://example.com/proof"))
    assert result["reviewRating"]["ratingValue"] == 4
    assert result["reviewRating"]["alternateName"] == "SUPPORTED"


def test_rating_value_supported_qualified():
    data = {**SAMPLE_PROOF_DATA, "verdict": "SUPPORTED (with unverified citations)"}
    result = json.loads(generate_claim_review(data, "https://example.com/proof"))
    assert result["reviewRating"]["ratingValue"] == 3
    assert result["reviewRating"]["alternateName"] == "SUPPORTED (with unverified citations)"


def test_json_ld_no_doi_by_default():
    result = json.loads(generate_claim_review(
        proof_data=SAMPLE_PROOF_DATA,
        canonical_url="https://example.com/proofs/test/",
    ))
    assert "sameAs" not in result
    assert "identifier" not in result


def test_json_ld_with_doi():
    result = json.loads(generate_claim_review(
        proof_data=SAMPLE_PROOF_DATA,
        canonical_url="https://example.com/proofs/test/",
        doi="10.5281/zenodo.1234567",
        concept_doi="10.5281/zenodo.1234560",
    ))
    assert result["sameAs"] == ["https://doi.org/10.5281/zenodo.1234567", "https://doi.org/10.5281/zenodo.1234560"]
    assert result["identifier"] == "10.5281/zenodo.1234567"


def test_json_ld_concept_doi_as_additional_same_as():
    result = json.loads(generate_claim_review(
        proof_data=SAMPLE_PROOF_DATA,
        canonical_url="https://example.com/proofs/test/",
        doi="10.5281/zenodo.1234567",
        concept_doi="10.5281/zenodo.1234560",
    ))
    assert result["identifier"] == "10.5281/zenodo.1234567"
    assert "https://doi.org/10.5281/zenodo.1234567" in result["sameAs"]
    assert "https://doi.org/10.5281/zenodo.1234560" in result["sameAs"]


def test_json_ld_v3_structured_verdict():
    from tools.lib.json_ld import generate_claim_review
    import json
    proof_data = {
        "format_version": 3, "claim_natural": "Test claim",
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "generator": {"generated_at": "2026-04-13"},
    }
    result = json.loads(generate_claim_review(proof_data, "https://example.com/proofs/test/"))
    assert result["reviewRating"]["alternateName"] == "PROVED"
    assert result["reviewRating"]["ratingValue"] == 5


def test_json_ld_includes_is_based_on():
    from tools.lib.json_ld import generate_claim_review
    import json
    proof_data = {
        "format_version": 3, "claim_natural": "Test",
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "generator": {"generated_at": "2026-04-13"},
    }
    result = json.loads(generate_claim_review(proof_data, "https://example.com/proofs/test/",
        proof_py_url="https://example.com/proofs/test/proof.py"))
    assert "isBasedOn" in result
    assert result["isBasedOn"]["@type"] == "SoftwareSourceCode"
    assert result["isBasedOn"]["url"] == "https://example.com/proofs/test/proof.py"


def test_json_ld_includes_main_entity():
    from tools.lib.json_ld import generate_claim_review
    import json
    proof_data = {
        "format_version": 3, "claim_natural": "Test",
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "generator": {"generated_at": "2026-04-13"},
    }
    result = json.loads(generate_claim_review(proof_data, "https://example.com/proofs/test/",
        proof_json_url="https://example.com/proofs/test/proof.json"))
    assert "mainEntity" in result
    assert result["mainEntity"]["@type"] == "Dataset"
    assert result["mainEntity"]["description"]
    assert result["mainEntity"]["creator"]["name"] == "Proof Engine"
    assert "opensource.org" in result["mainEntity"]["license"]
    assert "identifier" not in result["mainEntity"]
    assert "sameAs" not in result["mainEntity"]


def test_json_ld_main_entity_carries_doi_when_minted():
    from tools.lib.json_ld import generate_claim_review
    import json
    proof_data = {
        "format_version": 3, "claim_natural": "Test",
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "generator": {"generated_at": "2026-04-13"},
    }
    result = json.loads(generate_claim_review(
        proof_data, "https://example.com/proofs/test/",
        proof_json_url="https://example.com/proofs/test/proof.json",
        doi="10.5281/zenodo.1234567",
        concept_doi="10.5281/zenodo.1234560",
    ))
    dataset = result["mainEntity"]
    assert dataset["identifier"] == "https://doi.org/10.5281/zenodo.1234567"
    assert dataset["sameAs"] == [
        "https://doi.org/10.5281/zenodo.1234567",
        "https://doi.org/10.5281/zenodo.1234560",
    ]


def test_json_ld_main_entity_doi_without_concept():
    from tools.lib.json_ld import generate_claim_review
    import json
    proof_data = {
        "format_version": 3, "claim_natural": "Test",
        "verdict": {"value": "PROVED", "qualified": False, "qualifier": None, "reason": None},
        "generator": {"generated_at": "2026-04-13"},
    }
    result = json.loads(generate_claim_review(
        proof_data, "https://example.com/proofs/test/",
        proof_json_url="https://example.com/proofs/test/proof.json",
        doi="10.5281/zenodo.1234567",
    ))
    dataset = result["mainEntity"]
    assert dataset["identifier"] == "https://doi.org/10.5281/zenodo.1234567"
    assert dataset["sameAs"] == ["https://doi.org/10.5281/zenodo.1234567"]
