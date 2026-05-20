"""Tests for proof_citations.resolvers.pubmed.

Three layers:
1. Pure-function parsing tests (no network) — verify the response mapping
   logic on canned E-utilities payloads.
2. Mocked end-to-end tests — patch the HTTPSession to return a canned response,
   verify the full resolve_pmid flow including ResolvedRecord shape.
3. Live network smoke test — marked @pytest.mark.network, hits the real
   eutils API for one well-known PMID. Skipped by default.
"""

import json
import socket
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from proof_citations.resolvers.base import ResolutionError, Author, ResolvedRecord
from proof_citations.resolvers.pubmed import (
    resolve_pmid,
    _parse_year,
    _parse_published_date,
    _parse_authors,
    _extract_doi,
)


def _has_network() -> bool:
    try:
        socket.gethostbyname("eutils.ncbi.nlm.nih.gov")
        return True
    except OSError:
        return False


needs_network = pytest.mark.skipif(
    not _has_network(),
    reason="eutils.ncbi.nlm.nih.gov DNS resolution required",
)


# ---------------------------------------------------------------------------
# Pure-function parsing tests
# ---------------------------------------------------------------------------

class TestParseYear:
    def test_year_only(self):
        assert _parse_year("2021") == 2021

    def test_year_month(self):
        assert _parse_year("2013 Feb") == 2013

    def test_year_month_day(self):
        assert _parse_year("2013 Feb 15") == 2013

    def test_empty(self):
        assert _parse_year("") is None
        assert _parse_year(None) is None

    def test_garbage(self):
        assert _parse_year("not a date") is None


class TestParsePublishedDate:
    def test_year_only(self):
        assert _parse_published_date("2021") == "2021"

    def test_year_month(self):
        assert _parse_published_date("2013 Feb") == "2013-02"

    def test_year_month_day(self):
        assert _parse_published_date("2013 Feb 15") == "2013-02-15"

    def test_pads_day(self):
        assert _parse_published_date("2013 Feb 5") == "2013-02-05"

    def test_empty(self):
        assert _parse_published_date("") is None


class TestParseAuthors:
    def test_pubmed_style_names(self):
        raw = [
            {"name": "Anderson CB", "authtype": "Author"},
            {"name": "Morgan TM", "authtype": "Author"},
        ]
        authors = _parse_authors(raw)
        assert len(authors) == 2
        assert authors[0].family == "Anderson"
        assert authors[0].given == "C B"
        assert authors[1].family == "Morgan"
        assert authors[1].given == "T M"

    def test_skips_collective_authors(self):
        raw = [
            {"name": "Smith J", "authtype": "Author"},
            {"name": "The Big Group", "authtype": "CollectiveName"},
        ]
        authors = _parse_authors(raw)
        assert len(authors) == 1
        assert authors[0].family == "Smith"

    def test_single_token_name(self):
        raw = [{"name": "Plato", "authtype": "Author"}]
        authors = _parse_authors(raw)
        assert authors[0].family == "Plato"
        assert authors[0].given == ""

    def test_empty(self):
        assert _parse_authors([]) == []
        assert _parse_authors(None) == []


class TestExtractDOI:
    def test_finds_doi(self):
        articleids = [
            {"idtype": "pubmed", "value": "12345"},
            {"idtype": "doi", "value": "10.1234/test"},
        ]
        assert _extract_doi(articleids) == "10.1234/test"

    def test_no_doi(self):
        articleids = [{"idtype": "pubmed", "value": "12345"}]
        assert _extract_doi(articleids) is None

    def test_empty(self):
        assert _extract_doi([]) is None
        assert _extract_doi(None) is None


# ---------------------------------------------------------------------------
# Mocked end-to-end tests
# ---------------------------------------------------------------------------

def _canned_eutils_response(pmid: str) -> dict:
    """A representative esummary payload — based on PMID 23260561 (Ren audit B3)."""
    return {
        "header": {"type": "esummary", "version": "0.3"},
        "result": {
            "uids": [pmid],
            pmid: {
                "uid": pmid,
                "pubdate": "2013 Feb",
                "epubdate": "2012 Dec 21",
                "source": "J Urol",
                "fulljournalname": "The Journal of urology",
                "title": "Ureteroenteric anastomotic strictures after radical cystectomy-does operative approach matter?",
                "volume": "189",
                "issue": "2",
                "pages": "541-7",
                "lang": ["eng"],
                "issn": "0022-5347",
                "essn": "1527-3792",
                "pubtype": ["Journal Article"],
                "authors": [
                    {"name": "Anderson CB", "authtype": "Author", "clusterid": ""},
                    {"name": "Morgan TM", "authtype": "Author", "clusterid": ""},
                ],
                "articleids": [
                    {"idtype": "pubmed", "idtypen": 1, "value": pmid},
                    {"idtype": "doi", "idtypen": 3, "value": "10.1016/j.juro.2012.09.034"},
                ],
            },
        },
    }


def _mock_session(json_payload, status_code=200):
    """Build a mock HTTPSession that returns the given JSON payload."""
    session = MagicMock()
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_payload
    response.text = json.dumps(json_payload)
    session.get.return_value = response
    return session


class TestResolvePMIDMocked:
    def test_happy_path(self):
        session = _mock_session(_canned_eutils_response("23260561"))
        record = resolve_pmid("23260561", session=session)

        assert isinstance(record, ResolvedRecord)
        assert record.identifier_type == "pmid"
        assert record.identifier_value == "23260561"
        assert record.canonical_url == "https://pubmed.ncbi.nlm.nih.gov/23260561/"
        assert record.title == "Ureteroenteric anastomotic strictures after radical cystectomy-does operative approach matter?"
        assert record.year == 2013
        assert record.published_date == "2013-02"
        assert record.venue == "The Journal of urology"
        assert record.issn == "0022-5347"
        assert record.doi == "10.1016/j.juro.2012.09.034"
        assert record.pmid == "23260561"
        assert record.volume == "189"
        assert record.issue == "2"
        assert record.pages == "541-7"
        assert record.publication_type == "journal-article"
        assert record.update_status is None  # not retracted
        assert record.source_api == "eutils.ncbi.nlm.nih.gov"
        assert len(record.authors) == 2
        assert record.authors[0].family == "Anderson"
        assert "eutils" in record.raw

    def test_strip_pmid_prefix(self):
        session = _mock_session(_canned_eutils_response("23260561"))
        record = resolve_pmid("PMID:23260561", session=session)
        assert record.identifier_value == "23260561"

    def test_non_numeric_raises(self):
        session = _mock_session({})
        with pytest.raises(ValueError, match="PMID must be numeric"):
            resolve_pmid("not-a-pmid", session=session)

    def test_http_429_raises_rate_limited(self):
        session = _mock_session({}, status_code=429)
        with pytest.raises(ResolutionError) as exc_info:
            resolve_pmid("12345", session=session)
        assert exc_info.value.kind == "rate_limited"

    def test_http_500_raises_fetch_failed(self):
        session = _mock_session({}, status_code=500)
        with pytest.raises(ResolutionError) as exc_info:
            resolve_pmid("12345", session=session)
        assert exc_info.value.kind == "fetch_failed"

    def test_missing_record_raises_malformed(self):
        # E-utilities response with no matching record
        payload = {"result": {"uids": ["12345"]}}  # no pmid key in result
        session = _mock_session(payload)
        with pytest.raises(ResolutionError) as exc_info:
            resolve_pmid("12345", session=session)
        assert exc_info.value.kind == "malformed_response"

    def test_pmid_not_found_raises_not_found(self):
        payload = {"result": {"uids": ["12345"], "12345": {"error": "cannot get document summary"}}}
        session = _mock_session(payload)
        with pytest.raises(ResolutionError) as exc_info:
            resolve_pmid("12345", session=session)
        assert exc_info.value.kind == "not_found"

    def test_retraction_detected_in_pubtype(self):
        payload = _canned_eutils_response("99999")
        payload["result"]["99999"]["pubtype"] = ["Journal Article", "Retraction of Publication"]
        session = _mock_session(payload)
        record = resolve_pmid("99999", session=session)
        assert record.update_status == "retracted"

    def test_expression_of_concern(self):
        payload = _canned_eutils_response("99999")
        payload["result"]["99999"]["pubtype"] = ["Journal Article", "Expression of Concern"]
        session = _mock_session(payload)
        record = resolve_pmid("99999", session=session)
        assert record.update_status == "expression_of_concern"


# ---------------------------------------------------------------------------
# Live network smoke test
# ---------------------------------------------------------------------------

@needs_network
@pytest.mark.network
def test_resolve_pmid_live_smoke():
    """Hit the real E-utilities for the Sung et al. 2021 cancer-statistics paper
    (PMID 33538338) — known stable, frequently cited reference."""
    from proof_citations.resolvers.base import HTTPSession
    record = resolve_pmid("33538338", session=HTTPSession())
    assert record.identifier_value == "33538338"
    assert record.title and "cancer statistics" in record.title.lower()
    assert record.year == 2021
    assert record.venue and "cancer" in record.venue.lower()
    assert record.doi == "10.3322/caac.21660"
