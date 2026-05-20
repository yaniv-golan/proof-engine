"""Tests for proof_citations.verify_record.verify_citation_record."""

from unittest.mock import MagicMock, patch

import pytest

from proof_citations.resolvers.base import Author, ResolvedRecord, ResolutionError, now_iso
from proof_citations.verify_record import verify_citation_record


def _stub_record() -> ResolvedRecord:
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


class TestVerifyCitationRecord:
    def test_genuine_path(self):
        with patch("proof_citations.verify_record.resolve", return_value=_stub_record()):
            r = verify_citation_record(("pmid", "33538338"), {
                "title": "Global Cancer Statistics 2020",
                "year": 2021,
                "doi": "10.3322/caac.21660",
            })
        assert r["status"] == "verified"
        assert r["verdict"] == "genuine"
        assert r["resolved"] is not None

    def test_metadata_chimera_path(self):
        with patch("proof_citations.verify_record.resolve", return_value=_stub_record()):
            r = verify_citation_record(("pmid", "33538338"), {
                "title": "Global Cancer Statistics 2020",
                "year": 2099,
            })
        assert r["status"] == "metadata_chimera"
        assert r["verdict"] == "metadata_chimera"

    def test_no_expected_returns_resolved(self):
        with patch("proof_citations.verify_record.resolve", return_value=_stub_record()):
            r = verify_citation_record(("pmid", "33538338"))
        assert r["status"] == "resolved"
        assert r["verdict"] == "no_expected"
        assert r["resolved"] is not None

    def test_url_input_uses_identify(self):
        with patch("proof_citations.verify_record.resolve", return_value=_stub_record()) as mock_resolve:
            r = verify_citation_record("https://pubmed.ncbi.nlm.nih.gov/33538338/", {
                "title": "Global Cancer Statistics 2020"
            })
            # resolve should have been called with the extracted ("pmid", "33538338")
            args, _ = mock_resolve.call_args
            assert args[0] == ("pmid", "33538338")
        assert r["verdict"] == "genuine"

    def test_unrecognized_url_returns_unresolvable(self):
        # identify() returns ("url", url) for unrecognized URLs, which has no backend
        with patch(
            "proof_citations.verify_record.resolve",
            side_effect=ValueError("no backend"),
        ):
            r = verify_citation_record("https://example.com/something", {"title": "x"})
        assert r["status"] == "fetch_failed"

    def test_not_found_returns_unresolvable(self):
        err = ResolutionError("PMID not found", kind="not_found", details={"pmid": "99999"})
        with patch("proof_citations.verify_record.resolve", side_effect=err):
            r = verify_citation_record(("pmid", "99999"), {"title": "x"})
        assert r["status"] == "unresolvable"
        assert r["error"] is err

    def test_fetch_failed_propagates(self):
        err = ResolutionError("network", kind="fetch_failed")
        with patch("proof_citations.verify_record.resolve", side_effect=err):
            r = verify_citation_record(("pmid", "99999"), {"title": "x"})
        assert r["status"] == "fetch_failed"


class TestVerifyCitationRecordWithRealCompare:
    """Integration: mock only the registry call, let compare_metadata run for real."""

    def test_chimera_message_includes_similarity(self):
        with patch("proof_citations.verify_record.resolve", return_value=_stub_record()):
            r = verify_citation_record(("pmid", "33538338"), {
                "title": "Global Cancer Statistics 2020",
                "year": 2099,
            })
        assert r["title_similarity"] is not None
        assert r["title_similarity"] > 0.85
        assert "similarity" in r["message"].lower()

    def test_title_chimera_message(self):
        with patch("proof_citations.verify_record.resolve", return_value=_stub_record()):
            r = verify_citation_record(("pmid", "33538338"), {
                "title": "A completely unrelated paper on something else entirely",
            })
        assert r["status"] == "title_chimera"
