"""Tests for proof_citations.identify."""

import pytest

from proof_citations.identify import identify


class TestPubMedURLs:
    def test_canonical_pubmed_url(self):
        assert identify("https://pubmed.ncbi.nlm.nih.gov/23260561/") == ("pmid", "23260561")

    def test_pubmed_without_trailing_slash(self):
        assert identify("https://pubmed.ncbi.nlm.nih.gov/23260561") == ("pmid", "23260561")

    def test_pubmed_with_query_string(self):
        assert identify("https://pubmed.ncbi.nlm.nih.gov/23260561/?foo=bar") == ("pmid", "23260561")

    def test_legacy_pubmed_url(self):
        assert identify("https://www.ncbi.nlm.nih.gov/pubmed/12345") == ("pmid", "12345")

    def test_pubmed_with_www(self):
        assert identify("https://www.pubmed.ncbi.nlm.nih.gov/23260561/") == ("pmid", "23260561")


class TestPMCURLs:
    def test_canonical_pmc_url(self):
        assert identify("https://pmc.ncbi.nlm.nih.gov/articles/PMC12591951/") == ("pmc", "PMC12591951")

    def test_legacy_pmc_url(self):
        assert identify("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12591951/") == ("pmc", "PMC12591951")


class TestDOIURLs:
    def test_doi_org_url(self):
        assert identify("https://doi.org/10.1016/j.juro.2012.09.034") == ("doi", "10.1016/j.juro.2012.09.034")

    def test_dx_doi_org_url(self):
        assert identify("https://dx.doi.org/10.1016/j.juro.2012.09.034") == ("doi", "10.1016/j.juro.2012.09.034")

    def test_iop_doi_url(self):
        assert identify("https://iopscience.iop.org/article/10.1088/1742-5468/abc") == (
            "doi", "10.1088/1742-5468/abc",
        )

    def test_doi_with_encoded_slash(self):
        result = identify("https://doi.org/10.1234/foo%2Fbar")
        assert result == ("doi", "10.1234/foo/bar")  # unquoted


class TestArXivURLs:
    def test_arxiv_abs(self):
        assert identify("https://arxiv.org/abs/2106.09685") == ("arxiv", "2106.09685")

    def test_arxiv_html(self):
        assert identify("https://arxiv.org/html/2106.09685") == ("arxiv", "2106.09685")

    def test_arxiv_pdf(self):
        assert identify("https://arxiv.org/pdf/2106.09685") == ("arxiv", "2106.09685")

    def test_arxiv_with_version(self):
        assert identify("https://arxiv.org/abs/2106.09685v2") == ("arxiv", "2106.09685")

    def test_ar5iv(self):
        assert identify("https://ar5iv.labs.arxiv.org/html/2106.09685") == ("arxiv", "2106.09685")


class TestSWHID:
    def test_swhid_url(self):
        url = "https://archive.softwareheritage.org/swh:1:dir:abc123" + "0" * 34
        result = identify(url)
        assert result is not None
        assert result[0] == "swhid"


class TestBareIdentifiers:
    def test_bare_pmid_with_prefix(self):
        assert identify("PMID: 12345") == ("pmid", "12345")

    def test_bare_pmid_no_prefix(self):
        assert identify("12345") == ("pmid", "12345")

    def test_bare_pmc(self):
        assert identify("PMC12591951") == ("pmc", "PMC12591951")

    def test_bare_pmc_lowercase(self):
        assert identify("pmc12591951") == ("pmc", "PMC12591951")

    def test_bare_doi_with_prefix(self):
        assert identify("doi:10.3322/caac.21660") == ("doi", "10.3322/caac.21660")

    def test_bare_doi_no_prefix(self):
        assert identify("10.3322/caac.21660") == ("doi", "10.3322/caac.21660")

    def test_bare_arxiv_with_prefix(self):
        assert identify("arxiv:2106.09685") == ("arxiv", "2106.09685")

    def test_bare_arxiv_no_prefix(self):
        assert identify("2106.09685") == ("arxiv", "2106.09685")


class TestEdgeCases:
    def test_empty_returns_none(self):
        assert identify("") is None
        assert identify(None) is None

    def test_whitespace_only_returns_none(self):
        assert identify("   ") is None

    def test_unrecognized_url_returns_url_tuple(self):
        result = identify("https://example.com/some/page")
        assert result == ("url", "https://example.com/some/page")

    def test_strips_whitespace(self):
        assert identify("  PMID: 12345  ") == ("pmid", "12345")

    def test_unstructured_string_returns_none(self):
        assert identify("not an identifier at all") is None


class TestPriorityWhenAmbiguous:
    def test_pubmed_url_takes_precedence_over_pmc(self):
        # If the URL is unambiguous, only one regex matches
        assert identify("https://pubmed.ncbi.nlm.nih.gov/23260561/")[0] == "pmid"
        assert identify("https://pmc.ncbi.nlm.nih.gov/articles/PMC1234/")[0] == "pmc"
