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
    resolve_pmc,
    _parse_year,
    _parse_published_date,
    _parse_authors,
    _extract_doi,
    _extract_pmid,
    _normalize_pmc_input,
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


# ---------------------------------------------------------------------------
# PMC normalization + extraction helpers
# ---------------------------------------------------------------------------

class TestNormalizePmcInput:
    def test_with_pmc_prefix(self):
        assert _normalize_pmc_input("PMC2768535") == "2768535"

    def test_bare_numeric(self):
        assert _normalize_pmc_input("2768535") == "2768535"

    def test_pmcid_colon_prefix(self):
        assert _normalize_pmc_input("PMCID:PMC2768535") == "2768535"

    def test_pmc_colon_prefix(self):
        assert _normalize_pmc_input("pmc:PMC2768535") == "2768535"

    def test_lowercase_pmc(self):
        assert _normalize_pmc_input("pmc2768535") == "2768535"

    def test_whitespace(self):
        assert _normalize_pmc_input("  PMC2768535  ") == "2768535"


class TestExtractPmid:
    def test_pmid_idtype(self):
        ids = [{"idtype": "pmid", "value": "19152719"}]
        assert _extract_pmid(ids) == "19152719"

    def test_pubmed_idtype_synonym(self):
        ids = [{"idtype": "pubmed", "value": "19152719"}]
        assert _extract_pmid(ids) == "19152719"

    def test_skips_non_pmid(self):
        ids = [
            {"idtype": "doi", "value": "10.1017/S1462399409000957"},
            {"idtype": "pmcid", "value": "PMC2768535"},
        ]
        assert _extract_pmid(ids) is None

    def test_rejects_non_numeric(self):
        ids = [{"idtype": "pmid", "value": "PMC123"}]
        assert _extract_pmid(ids) is None

    def test_empty(self):
        assert _extract_pmid([]) is None
        assert _extract_pmid(None) is None


# ---------------------------------------------------------------------------
# PMC resolver — mocked tests
# ---------------------------------------------------------------------------

def _canned_pmc_response(pmc_num: str, *, pmid_xref: str = "19152719",
                         doi_xref: str = "10.1017/S1462399409000957") -> dict:
    """Representative esummary db=pmc payload (modeled on PMC2768535).

    `db=pmc` does NOT return `pubtype`, `issn`/`essn`, or `lang` (verified
    live against eutils on 2026-05-21). It DOES return `articleids` carrying
    both the `pmid` and `doi` cross-references."""
    return {
        "header": {"type": "esummary", "version": "0.3"},
        "result": {
            "uids": [pmc_num],
            pmc_num: {
                "uid": pmc_num,
                "pubdate": "2009 Jan 20",
                "epubdate": "2009 Jan 20",
                "source": "Expert Rev Mol Med",
                "fulljournalname": "Expert reviews in molecular medicine",
                "title": "Emerging role of the cannabinoid receptor CB2 in immune regulation.",
                "volume": "11",
                "issue": "",
                "pages": "e3",
                "authors": [
                    {"name": "Cabral GA", "authtype": "Author"},
                    {"name": "Griffin-Thomas L", "authtype": "Author"},
                ],
                "articleids": [
                    {"idtype": "pmcid", "value": f"PMC{pmc_num}"},
                    {"idtype": "pmid", "value": pmid_xref},
                    {"idtype": "doi", "value": doi_xref},
                ],
            },
        },
    }


def _mock_session_sequence(*payloads):
    """Build a mock HTTPSession that returns each payload in turn on
    successive `.get()` calls — needed when resolve_pmc enriches via
    resolve_pmid (two calls in one logical resolve)."""
    session = MagicMock()
    responses = []
    for p in payloads:
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = p
        r.text = json.dumps(p)
        responses.append(r)
    session.get.side_effect = responses
    return session


class TestResolvePmcMocked:
    def test_happy_path_with_enrichment(self):
        pmc_payload = _canned_pmc_response("2768535")
        pmid_payload = _canned_eutils_response("19152719")
        session = _mock_session_sequence(pmc_payload, pmid_payload)

        record = resolve_pmc("PMC2768535", session=session)

        assert isinstance(record, ResolvedRecord)
        assert record.identifier_type == "pmc"
        assert record.identifier_value == "PMC2768535"
        assert record.canonical_url == "https://pmc.ncbi.nlm.nih.gov/articles/PMC2768535/"
        assert record.year == 2009
        assert record.doi == "10.1017/S1462399409000957"
        assert record.pmid == "19152719"
        # Enriched from the PMID round-trip:
        assert record.issn == "0022-5347"  # canned pmid response carries this
        assert record.publication_type == "journal-article"
        assert record.source_api == "eutils.ncbi.nlm.nih.gov"

    def test_outbound_id_is_numeric_not_prefixed(self):
        """E-utilities rejects `id=PMC2768535`. Verify we strip the prefix."""
        pmc_payload = _canned_pmc_response("2768535")
        pmid_payload = _canned_eutils_response("19152719")
        session = _mock_session_sequence(pmc_payload, pmid_payload)

        resolve_pmc("PMC2768535", session=session)

        # First call is the db=pmc fetch
        first_call = session.get.call_args_list[0]
        assert first_call.kwargs["params"]["id"] == "2768535"
        assert first_call.kwargs["params"]["db"] == "pmc"

    def test_accepts_bare_numeric_input(self):
        pmc_payload = _canned_pmc_response("2768535")
        pmid_payload = _canned_eutils_response("19152719")
        session = _mock_session_sequence(pmc_payload, pmid_payload)
        record = resolve_pmc("2768535", session=session)
        assert record.identifier_value == "PMC2768535"

    def test_non_numeric_raises(self):
        session = _mock_session({})
        with pytest.raises(ValueError, match="PMCID must be numeric"):
            resolve_pmc("PMCfoo", session=session)

    def test_http_429_raises_rate_limited(self):
        session = _mock_session({}, status_code=429)
        with pytest.raises(ResolutionError) as exc_info:
            resolve_pmc("PMC2768535", session=session)
        assert exc_info.value.kind == "rate_limited"

    def test_pmc_not_found_raises_not_found(self):
        payload = {"result": {"uids": ["999999999"],
                              "999999999": {"error": "cannot get document summary"}}}
        session = _mock_session(payload)
        with pytest.raises(ResolutionError) as exc_info:
            resolve_pmc("PMC999999999", session=session)
        assert exc_info.value.kind == "not_found"

    def test_enrichment_failure_is_swallowed(self):
        """If the cross-ref PMID resolve fails, return the pmc-only record."""
        pmc_payload = _canned_pmc_response("2768535")
        # Second response (the enrichment) returns 500 — resolve_pmid raises.
        bad_pmid_response = MagicMock()
        bad_pmid_response.status_code = 500
        bad_pmid_response.json.return_value = {}
        bad_pmid_response.text = ""

        pmc_response = MagicMock()
        pmc_response.status_code = 200
        pmc_response.json.return_value = pmc_payload
        pmc_response.text = json.dumps(pmc_payload)

        session = MagicMock()
        session.get.side_effect = [pmc_response, bad_pmid_response]

        record = resolve_pmc("PMC2768535", session=session)
        # PMC-side fields populated:
        assert record.identifier_value == "PMC2768535"
        assert record.year == 2009
        assert record.doi == "10.1017/S1462399409000957"
        assert record.pmid == "19152719"
        # Enrichment-side fields stayed None:
        assert record.issn is None
        assert record.publication_type is None
        assert record.update_status is None

    def test_no_pmid_xref_no_enrichment_call(self):
        """If db=pmc returns no pmid articleid, only one HTTP call is made."""
        payload = _canned_pmc_response("2768535", pmid_xref="")
        payload["result"]["2768535"]["articleids"] = [
            {"idtype": "pmcid", "value": "PMC2768535"},
            {"idtype": "doi", "value": "10.1017/S1462399409000957"},
        ]
        session = _mock_session(payload)
        record = resolve_pmc("PMC2768535", session=session)
        assert session.get.call_count == 1
        assert record.pmid is None
        assert record.doi == "10.1017/S1462399409000957"


# ---------------------------------------------------------------------------
# Live network smoke test — PMC
# ---------------------------------------------------------------------------

@needs_network
@pytest.mark.network
def test_resolve_pmc_live_smoke():
    """Hit the real E-utilities for PMC2768535 (Cabral & Griffin-Thomas 2009 —
    used in proof-engine's CB2/microglia proof)."""
    from proof_citations.resolvers.base import HTTPSession
    record = resolve_pmc("PMC2768535", session=HTTPSession())
    assert record.identifier_type == "pmc"
    assert record.identifier_value == "PMC2768535"
    assert record.canonical_url == "https://pmc.ncbi.nlm.nih.gov/articles/PMC2768535/"
    assert record.year == 2009
    assert record.doi  # Crossref cross-ref populated
    assert record.pmid  # PubMed cross-ref populated
