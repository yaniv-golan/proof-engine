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
