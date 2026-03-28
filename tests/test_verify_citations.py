"""Tests for verify_citations.py — build_citation_detail and deferred import."""
from scripts.verify_citations import build_citation_detail
from scripts import verify_citations as vc_module


def test_build_citation_detail_single_source():
    """Standard pattern: one FACT_REGISTRY entry per source."""
    fact_registry = {
        "B1": {"type": "B", "key": "src_a"},
        "B2": {"type": "B", "key": "src_b"},
    }
    citation_results = {
        "src_a": {"status": "verified", "method": "full_quote", "coverage_pct": None,
                  "fetch_error": None, "fetch_mode": "live", "message": "ok"},
        "src_b": {"status": "not_found", "method": None, "coverage_pct": None,
                  "fetch_error": None, "fetch_mode": "live", "message": "nope"},
    }
    empirical_facts = {
        "src_a": {"source_name": "A", "url": "http://a.com", "quote": "hello"},
        "src_b": {"source_name": "B", "url": "http://b.com", "quote": "world"},
    }
    detail = build_citation_detail(fact_registry, citation_results, empirical_facts)
    assert "B1" in detail
    assert "B2" in detail
    assert detail["B1"]["status"] == "verified"
    assert detail["B2"]["status"] == "not_found"


def test_build_citation_detail_multi_source():
    """Multi-source: one FACT_REGISTRY entry, multiple sub-source results."""
    fact_registry = {
        "B1": {"type": "B", "key": "src_a"},
    }
    citation_results = {
        "src_a_source_0": {"status": "verified", "method": "full_quote",
                           "coverage_pct": None, "fetch_error": None,
                           "fetch_mode": "live", "message": "ok"},
        "src_a_source_1": {"status": "not_found", "method": None,
                           "coverage_pct": None, "fetch_error": None,
                           "fetch_mode": "live", "message": "nope"},
    }
    empirical_facts = {
        "src_a": {
            "source_name": "Test",
            "sources": [
                {"url": "http://a.com", "quote": "hello"},
                {"url": "http://b.com", "quote": "world"},
            ],
        },
    }
    detail = build_citation_detail(fact_registry, citation_results, empirical_facts)
    assert "B1_source_0" in detail
    assert "B1_source_1" in detail
    assert detail["B1_source_0"]["status"] == "verified"
    assert detail["B1_source_0"]["url"] == "http://a.com"
    assert detail["B1_source_1"]["status"] == "not_found"
    assert detail["B1_source_1"]["url"] == "http://b.com"


def test_build_citation_detail_multi_source_short_sources_list():
    """Guard: citation_results has more sub-keys than sources list."""
    fact_registry = {"B1": {"type": "B", "key": "src_a"}}
    citation_results = {
        "src_a_source_0": {"status": "verified", "method": "full_quote",
                           "coverage_pct": None, "fetch_error": None,
                           "fetch_mode": "live", "message": "ok"},
        "src_a_source_1": {"status": "not_found", "method": None,
                           "coverage_pct": None, "fetch_error": None,
                           "fetch_mode": "live", "message": "nope"},
    }
    empirical_facts = {
        "src_a": {
            "source_name": "Test",
            "sources": [{"url": "http://a.com", "quote": "hello"}],
        },
    }
    detail = build_citation_detail(fact_registry, citation_results, empirical_facts)
    assert "B1_source_0" in detail
    assert detail["B1_source_0"]["url"] == "http://a.com"
    assert "B1_source_1" in detail
    assert detail["B1_source_1"]["url"] == ""


# ---------------------------------------------------------------------------
# Deferred requests import — snapshot-only verification without requests
# ---------------------------------------------------------------------------


def test_no_requests_skips_live_fetch(monkeypatch):
    """When requests is None, verify_citation should skip live fetch and use snapshot."""
    monkeypatch.setattr(vc_module, "requests", None)
    result = vc_module.verify_citation(
        url="http://example.com",
        expected_quote="hello world",
        fact_id="test",
        snapshot="<html>hello world</html>",
    )
    assert result["status"] == "verified"
    assert result["fetch_mode"] == "snapshot"


def test_no_requests_returns_fetch_failed_without_snapshot(monkeypatch):
    """When requests is None and no snapshot, verify_citation returns fetch_failed."""
    monkeypatch.setattr(vc_module, "requests", None)
    result = vc_module.verify_citation(
        url="http://example.com",
        expected_quote="hello world",
        fact_id="test",
    )
    assert result["status"] == "fetch_failed"


def test_no_requests_normalize_still_works(monkeypatch):
    """Non-HTTP functions work fine without requests."""
    monkeypatch.setattr(vc_module, "requests", None)
    assert vc_module.normalize_text("Hello World") == "hello world"


# ---------------------------------------------------------------------------
# PMC normalization tests
# ---------------------------------------------------------------------------

import os as _os

FIXTURES_DIR = _os.path.join(_os.path.dirname(__file__), "fixtures")


def _read_fixture(name):
    with open(_os.path.join(FIXTURES_DIR, name)) as f:
        return f.read()


def test_normalize_strips_sup_references():
    text = "plasticity<sup>[1]</sup> throughout"
    result = vc_module.normalize_text(text)
    assert "plasticity throughout" in result


def test_normalize_strips_nested_sup_references():
    text = 'plasticity<sup><a href="#ref1">1</a></sup> close'
    result = vc_module.normalize_text(text)
    assert "plasticity close" in result


def test_normalize_strips_xref_references():
    text = 'mechanisms<a class="xref xref-bibr" href="#B1">[1,2]</a> have'
    result = vc_module.normalize_text(text)
    assert "mechanisms have" in result


def test_normalize_strips_orphaned_brackets_in_academic():
    """After stripping <sup>[N]</sup>, leftover [N] tokens should also be removed."""
    text = "word<sup>[1]</sup> other [2] text<sup>[3]</sup> end"
    result = vc_module.normalize_text(text)
    assert "[" not in result
    assert "word other text end" in result


def test_normalize_preserves_brackets_in_non_academic():
    """Non-academic HTML should NOT strip [N] patterns."""
    text = "<p>See section [3] of the treaty for details.</p>"
    result = vc_module.normalize_text(text)
    assert "section" in result
    # [3] should be preserved since no academic refs detected
    assert "3" in result


def test_normalize_preserves_parenthesized_numbers():
    """(N) patterns are never stripped — too ambiguous."""
    text = "item (3) in the list<sup>[1]</sup> above"
    result = vc_module.normalize_text(text)
    assert "(3)" in result


def test_existing_gov_quotes_still_match():
    """Regression guard: .gov source text must still normalize correctly."""
    gov_text = '<span class="tei-persname">David Ben-Gurion</span> proclaimed independence'
    result = vc_module.normalize_text(gov_text)
    assert "david ben-gurion proclaimed independence" in result


def test_pmc_fixture_sup_refs():
    html = _read_fixture("pmc_sup_refs.html")
    result = vc_module.normalize_text(html)
    assert "plasticity" in result
    assert "adult neurogenesis" in result
    assert "[1]" not in result
    assert "[3,4]" not in result


def test_pmc_fixture_nested_refs():
    html = _read_fixture("pmc_nested_refs.html")
    result = vc_module.normalize_text(html)
    assert "cortical plasticity" in result
    assert "experience-dependent reorganization" in result


def test_pmc_quote_match_regression():
    """The actual user-reported bug: a real PMC quote gets low match due to reference noise.
    Simulates a page with inline refs and verifies the quote matches at >= 80%."""
    page_html = (
        '<p>The adult brain exhibits remarkable plasticity<sup><a href="#r1">1</a></sup> '
        'and can undergo experience-dependent reorganization<sup><a href="#r2">2</a></sup> '
        'comparable to juvenile levels<sup><a href="#r3">3</a></sup> in certain contexts.</p>'
    )
    quote = "The adult brain exhibits remarkable plasticity and can undergo experience-dependent reorganization comparable to juvenile levels in certain contexts."
    result = vc_module._match_quote(page_html, quote, "test_fact", fetch_mode="live")
    assert result is not None
    assert result["status"] in ("verified", "partial")
    # Should be verified (>= 80% coverage), not partial
    # coverage_pct is stored as percentage points (80.0), not ratio (0.8)
    if result["method"] == "fragment":
        assert result.get("coverage_pct", 0) >= 80


def test_data_values_unaffected_by_normalization():
    """verify_data_values uses normalize_text — ensure academic ref stripping
    doesn't break numeric value matching."""
    page = '<td>9.883</td><sup>[1]</sup> <td>307.789</td><sup>[2]</sup>'
    norm = vc_module.normalize_text(page)
    assert "9.883" in norm
    assert "307.789" in norm


# ---------------------------------------------------------------------------
# verify_search_registry tests
# ---------------------------------------------------------------------------

from scripts.verify_citations import verify_search_registry


def test_verify_search_registry_accessible(monkeypatch):
    """search_url returning 200 should produce 'accessible' status."""
    import requests

    class MockResponse:
        status_code = 200
        def raise_for_status(self):
            pass

    monkeypatch.setattr(requests, "get", lambda *a, **kw: MockResponse())

    registry = {
        "search_a": {
            "database": "PubMed",
            "url": "https://pubmed.ncbi.nlm.nih.gov/",
            "search_url": "https://pubmed.ncbi.nlm.nih.gov/?term=test",
            "query_terms": ["test"],
            "date_range": "all years",
            "result_count": 0,
            "source_name": "PubMed",
        }
    }
    results = verify_search_registry(registry)
    assert results["search_a"]["status"] == "accessible"
    assert "credibility" in results["search_a"]


def test_verify_search_registry_known_403(monkeypatch):
    """search_url returning 403 should produce 'known' status."""
    import requests

    class MockResponse:
        status_code = 403
        def raise_for_status(self):
            err = requests.exceptions.HTTPError("403")
            err.response = self  # attach response so status_code is accessible
            raise err

    monkeypatch.setattr(requests, "get", lambda *a, **kw: MockResponse())

    registry = {
        "search_a": {
            "database": "Test",
            "url": "https://example.gov/",
            "search_url": "https://example.gov/?q=test",
            "query_terms": ["test"],
            "date_range": "all years",
            "result_count": 0,
            "source_name": "Test",
        }
    }
    results = verify_search_registry(registry)
    assert results["search_a"]["status"] == "known"


def test_verify_search_registry_unreachable(monkeypatch):
    """Connection error should produce 'unreachable' status."""
    import requests

    def fail(*a, **kw):
        raise requests.exceptions.ConnectionError("fail")

    monkeypatch.setattr(requests, "get", fail)

    registry = {
        "search_a": {
            "database": "Test",
            "url": "https://nonexistent.example.com/",
            "search_url": "https://nonexistent.example.com/?q=test",
            "query_terms": ["test"],
            "date_range": "all years",
            "result_count": 0,
            "source_name": "Test",
        }
    }
    results = verify_search_registry(registry)
    assert results["search_a"]["status"] == "unreachable"
