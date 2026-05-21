"""Tests for `verify_citation(..., expected_metadata=...)` and the
batch-level `verify_all_citations` pass-through.

Pins down the 6 cases opus #3 called out:
1. Default path (no expected_metadata) → metadata_result is None
2. Joint happy path (quote + metadata both pass)
3. Quote passes, metadata is chimera (paper-real, journal-forged)
4. Quote fails, metadata is genuine (real paper but quote not on page)
5. Unstructured URL → skipped_no_structured_identifier
6. No-resolver identifier type → skipped_no_resolver
Plus 2 batch-parity cases for verify_all_citations.

All network calls are mocked at the HTTPSession / resolve layer; no live
fetches are performed.
"""

from unittest.mock import MagicMock, patch

import pytest

from proof_citations import verify_citation, verify_all_citations
from proof_citations.resolvers.base import (
    Author,
    ResolvedRecord,
    ResolutionError,
    now_iso,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _genuine_record() -> ResolvedRecord:
    """Sung et al. cancer-statistics paper — what PubMed actually returns
    for PMID 33538338."""
    return ResolvedRecord(
        identifier_type="pmid",
        identifier_value="33538338",
        canonical_url="https://pubmed.ncbi.nlm.nih.gov/33538338/",
        title="Global Cancer Statistics 2020",
        authors=[Author(family="Sung")],
        year=2021,
        venue="CA: a cancer journal for clinicians",
        doi="10.3322/caac.21660",
        pmid="33538338",
        resolved_at=now_iso(),
        source_api="test",
    )


def _mock_quote_found(*args, **kwargs):
    """Stub `_fetch_page` to return a page containing the expected quote.
    Returns (page_text, fetch_mode, error). The page text includes a known
    substring we'll use as the expected quote."""
    return ("the quoted text. Global Cancer Statistics 2020 — the paper is here", "live", None)


def _mock_quote_not_found(*args, **kwargs):
    """Page fetched but quote not present."""
    return ("Some unrelated page content with no quote match.", "live", None)


# ---------------------------------------------------------------------------
# 1. Default path: no expected_metadata → metadata_result is None (key present)
# ---------------------------------------------------------------------------

class TestDefaultPath:
    def test_no_expected_metadata_kwarg(self):
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found):
            r = verify_citation(
                "https://pubmed.ncbi.nlm.nih.gov/33538338/",
                "Global Cancer Statistics 2020",
                "B1",
            )
        # status preserves its v1.34.x meaning (quote-on-page)
        assert r["status"] == "verified"
        # NEW key always present, value None when not requested
        assert "metadata_result" in r
        assert r["metadata_result"] is None


# ---------------------------------------------------------------------------
# 2. Joint happy path: quote on page + metadata matches
# ---------------------------------------------------------------------------

class TestJointHappyPath:
    def test_both_pass(self):
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found), \
             patch("proof_citations.verify_record.resolve", return_value=_genuine_record()):
            r = verify_citation(
                "https://pubmed.ncbi.nlm.nih.gov/33538338/",
                "Global Cancer Statistics 2020",
                "B1",
                expected_metadata={
                    "title": "Global Cancer Statistics 2020",
                    "year": 2021,
                    "doi": "10.3322/caac.21660",
                },
            )
        assert r["status"] == "verified"
        assert r["metadata_result"] is not None
        assert r["metadata_result"]["verdict"] == "genuine"
        # Caller composes the joint pass themselves
        joint_pass = r["status"] == "verified" and r["metadata_result"]["verdict"] == "genuine"
        assert joint_pass is True


# ---------------------------------------------------------------------------
# 3. Quote passes, metadata is a chimera (B3/B7 fraud pattern)
# ---------------------------------------------------------------------------

class TestQuotePassMetadataChimera:
    def test_real_quote_forged_metadata(self):
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found), \
             patch("proof_citations.verify_record.resolve", return_value=_genuine_record()):
            r = verify_citation(
                "https://pubmed.ncbi.nlm.nih.gov/33538338/",
                "Global Cancer Statistics 2020",
                "B1",
                expected_metadata={
                    "title": "Global Cancer Statistics 2020",  # matches
                    "year": 2099,  # ← FORGED
                },
            )
        # Quote-on-page passes (top-level status unchanged from v1.34.x semantics)
        assert r["status"] == "verified"
        # Metadata check detects the forgery
        assert r["metadata_result"]["verdict"] == "metadata_chimera"
        # Joint composition correctly flags the fraud
        joint_pass = r["status"] == "verified" and r["metadata_result"]["verdict"] == "genuine"
        assert joint_pass is False


# ---------------------------------------------------------------------------
# 4. Quote fails, metadata genuine (paper-real but quote isn't on page)
# ---------------------------------------------------------------------------

class TestQuoteFailMetadataPass:
    def test_paper_real_quote_paraphrased(self):
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_not_found), \
             patch("proof_citations.verify_record.resolve", return_value=_genuine_record()), \
             patch("proof_citations.verify._try_oa_fallback", return_value=(None, None)):
            r = verify_citation(
                "https://pubmed.ncbi.nlm.nih.gov/33538338/",
                "A paraphrased quote that isn't verbatim on the page",
                "B1",
                expected_metadata={
                    "title": "Global Cancer Statistics 2020",
                    "year": 2021,
                },
                oa_lookup=False,  # don't try OA fallback in the test
            )
        # Quote-on-page fails
        assert r["status"] == "not_found"
        # Metadata is genuine — the paper itself is real and correctly cited
        assert r["metadata_result"]["verdict"] == "genuine"


# ---------------------------------------------------------------------------
# 5. Unstructured URL → skipped_no_structured_identifier
# ---------------------------------------------------------------------------

class TestUnstructuredURLSkip:
    def test_plain_url_metadata_check_skipped(self):
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found):
            r = verify_citation(
                "https://example.com/blog/post",
                "the quoted text",
                "B1",
                expected_metadata={"title": "Some title", "year": 2024},
            )
        assert r["status"] == "verified"  # quote-on-page still works
        assert r["metadata_result"]["status"] == "skipped_no_structured_identifier"
        # Skip dict has the expected shape
        assert r["metadata_result"]["verdict"] == "skipped"
        assert "OG-extraction" in r["metadata_result"]["message"]


# ---------------------------------------------------------------------------
# 6. No-resolver identifier type → skipped_no_resolver
# ---------------------------------------------------------------------------

class TestNoResolverSkip:
    def test_skipped_when_backend_missing(self):
        # As of v1.41.0, pmc has a registered backend, so we simulate the
        # no-resolver path by patching get_backend to return None. This pins
        # down the skip behavior for any future identifier type that lands in
        # ALLOWED_TYPES without a corresponding resolver.
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found), \
             patch("proof_citations.resolvers.get_backend", return_value=None):
            r = verify_citation(
                "https://pmc.ncbi.nlm.nih.gov/articles/PMC12345/",
                "the quoted text",
                "B1",
                expected_metadata={"title": "x", "year": 2024},
            )
        assert r["metadata_result"]["status"] == "skipped_no_resolver"
        assert "pmc" in r["metadata_result"]["message"].lower()


# ---------------------------------------------------------------------------
# Batch-parity tests
# ---------------------------------------------------------------------------

class TestVerifyAllCitationsBatchParity:
    """v1.40.0: `expected_metadata` per-fact passes through `verify_all_citations`."""

    def test_per_fact_expected_metadata_single_source(self):
        empirical_facts = {
            "B1": {
                "url": "https://pubmed.ncbi.nlm.nih.gov/33538338/",
                "quote": "Global Cancer Statistics 2020",
                "expected_metadata": {
                    "title": "Global Cancer Statistics 2020",
                    "year": 2021,
                },
            },
            "B2": {
                "url": "https://example.com/blog",
                "quote": "the quoted text",
                # No expected_metadata — should not run a metadata check
            },
        }
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found), \
             patch("proof_citations.verify_record.resolve", return_value=_genuine_record()):
            results = verify_all_citations(empirical_facts)

        # B1 ran the metadata check
        assert results["B1"]["metadata_result"] is not None
        assert results["B1"]["metadata_result"]["verdict"] == "genuine"
        # B2 didn't request a check → key present, value None
        assert results["B2"]["metadata_result"] is None

    def test_per_fact_expected_metadata_multi_source(self):
        empirical_facts = {
            "B1": {
                "sources": [
                    {
                        "url": "https://pubmed.ncbi.nlm.nih.gov/33538338/",
                        "quote": "Global Cancer Statistics 2020",
                        "expected_metadata": {"title": "Global Cancer Statistics 2020"},
                    },
                ],
            },
        }
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found), \
             patch("proof_citations.verify_record.resolve", return_value=_genuine_record()):
            results = verify_all_citations(empirical_facts)

        check_id = "B1_source_0"
        assert results[check_id]["metadata_result"] is not None
        assert results[check_id]["metadata_result"]["verdict"] == "genuine"


# ---------------------------------------------------------------------------
# Shape-stability tests (deterministic return-dict shape)
# ---------------------------------------------------------------------------

class TestReturnShape:
    """`metadata_result` is always present in the return dict — deterministic shape."""

    def test_key_present_when_not_requested(self):
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found):
            r = verify_citation("https://example.com/", "x", "B1")
        assert "metadata_result" in r

    def test_key_present_when_requested(self):
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found), \
             patch("proof_citations.verify_record.resolve", return_value=_genuine_record()):
            r = verify_citation(
                "https://pubmed.ncbi.nlm.nih.gov/33538338/",
                "x",
                "B1",
                expected_metadata={"title": "x"},
            )
        assert "metadata_result" in r

    def test_credibility_key_still_present(self):
        """Existing `credibility` field is preserved by the new code path."""
        with patch("proof_citations.verify._fetch_page", side_effect=_mock_quote_found):
            r = verify_citation("https://example.com/", "x", "B1")
        assert "credibility" in r
