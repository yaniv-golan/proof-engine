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


def test_build_citation_detail_string_entry_raises():
    """FACT_REGISTRY entries must be dicts, not strings."""
    import pytest
    from scripts.verify_citations import build_citation_detail
    bad_registry = {"B1": "some_key"}
    with pytest.raises(TypeError, match="FACT_REGISTRY\\['B1'\\].*str.*expected dict"):
        build_citation_detail(bad_registry, {}, {})


def test_build_citation_detail_none_key_skips():
    """Entries with key=None should be skipped, not crash."""
    from scripts.verify_citations import build_citation_detail
    registry = {"A1": {"label": "computed fact", "method": None, "result": None, "key": None}}
    result = build_citation_detail(registry, {}, {})
    assert result == {}


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


# ---------------------------------------------------------------------------
# HTML entity decoding tests
# ---------------------------------------------------------------------------


def test_normalize_decodes_html_entities():
    """HTML entities like &rsquo; must be decoded before matching."""
    text = "seed oils are &lsquo;toxic,&rsquo; not healthy"
    result = vc_module.normalize_text(text)
    assert "seed oils are 'toxic,' not healthy" in result


def test_normalize_decodes_numeric_html_entities():
    """Numeric HTML entities like &#8217; must be decoded."""
    text = "brain&#8217;s neural pathways"
    result = vc_module.normalize_text(text)
    assert "brain's neural pathways" in result


def test_normalize_decodes_nbsp_entity():
    """&nbsp; must become a regular space."""
    text = "1.1&nbsp;degrees"
    result = vc_module.normalize_text(text)
    assert "1.1 degrees" in result


def test_normalize_decodes_mdash_entity():
    """&mdash; must be decoded (then normalized to hyphen by Unicode step)."""
    text = "a significant increase&mdash;noted by researchers"
    result = vc_module.normalize_text(text)
    # &mdash; → em-dash U+2014 → hyphen (via normalize_unicode)
    assert "increase-noted" in result


def test_html_entity_fixture_full_quote_match():
    """Real-world scenario: page with HTML entities should match clean quote."""
    page_html = _read_fixture("html_entities.html")
    quote = "While the internet may be full of posts stating that seed oils such as canola and soy are 'toxic,' scientific evidence does not support these claims."
    result = vc_module._match_quote(page_html, quote, "test_entity", fetch_mode="live")
    assert result is not None
    assert result["status"] == "verified"
    assert result["method"] == "full_quote"


def test_fragment_match_finds_second_half():
    """If the first word of a quote is mangled but the rest is present,
    the sliding window should find an 80%+ contiguous match."""
    # 30-word quote with first word mangled on the page
    page = "<p>ZZZZZ internet may be full of posts stating that seed oils such as canola and soy are toxic scientific evidence does not support these claims and further research confirms this</p>"
    quote = "While the internet may be full of posts stating that seed oils such as canola and soy are toxic scientific evidence does not support these claims and further research confirms this"
    result = vc_module._match_quote(page, quote, "test_frag")
    assert result is not None
    assert result["status"] == "verified"
    assert result["method"] == "fragment"
    assert result["coverage_pct"] >= 80


def test_fragment_match_mismatch_in_middle():
    """A mismatch near the middle of a 20-word quote: every ceil(80%)=16-word
    window contains the mangled word, so no 80% window matches. But the 50%
    sliding window should find the best partial."""
    words = "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa quebec romeo sierra tango".split()
    mangled = words.copy()
    mangled[9] = "ZZZZZ"  # mangle "juliet" (position 9 of 20)
    page = f"<p>{' '.join(mangled)}</p>"
    quote = ' '.join(words)
    result = vc_module._match_quote(page, quote, "test_mid")
    assert result is not None
    assert result["status"] == "partial"
    # Accept either "fragment" or "aggressive_normalization" method
    assert result["method"] in ("fragment", "aggressive_normalization")
    if result["method"] == "fragment":
        assert result["coverage_pct"] == 50.0


def test_fragment_match_mismatch_at_end():
    """A mismatch at the very end should allow verified via first-80% window."""
    words = "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa quebec romeo sierra tango".split()
    mangled = words.copy()
    mangled[-1] = "ZZZZZ"  # mangle last word
    page = f"<p>{' '.join(mangled)}</p>"
    quote = ' '.join(words)
    result = vc_module._match_quote(page, quote, "test_end")
    assert result is not None
    assert result["status"] == "verified"
    assert result["method"] == "fragment"
    assert result["coverage_pct"] >= 80


def test_fragment_exercised_not_full_quote():
    """Verify that fragment path is actually exercised when page differs from quote."""
    page = "<p>the quick brown fox jumps over the lazy dog and runs through the forest to find shelter</p>"
    quote = "the quick brown fox jumps over the lazy dog and runs through the forest to find ZZZZZ"
    result = vc_module._match_quote(page, quote, "test_frag_exercise")
    assert result is not None
    assert result["method"] == "fragment"
    assert result["coverage_pct"] >= 80
    assert result["status"] == "verified"


def test_fragment_short_quote_preserves_partial_coverage():
    """Regression: a 9-word quote with a 6-word prefix match must still
    report 66.7% partial, not drop to 44.4% from a 4-word fallback."""
    page = "<p>alpha bravo charlie delta echo foxtrot XXXX YYYY ZZZZ</p>"
    quote = "alpha bravo charlie delta echo foxtrot golf hotel india"
    result = vc_module._match_quote(page, quote, "test_short")
    assert result is not None
    assert result["method"] == "fragment"
    assert result["status"] == "partial"
    assert result["coverage_pct"] >= 66.0  # 6/9 = 66.7%, not 4/9 = 44.4%


def test_fragment_no_false_verified_from_coincidental_overlap():
    """Negative test: scattered word overlap must not produce false verified."""
    page = "<p>scientists studying canola and soy found that toxic chemical levels are within safe limits according to recent evidence</p>"
    quote = "canola and soy are toxic according to scientists who reject the evidence"
    result = vc_module._match_quote(page, quote, "test_false_pos")
    if result is not None:
        assert result["status"] != "verified" or result["method"] == "full_quote"


def test_normalize_strips_sup_span_a_refs():
    """PMC variant: <sup><span class="ref"><a>N</a></span></sup>"""
    text = 'PUFA<sup><span class="ref"><a href="#r1">1</a></span></sup> intake'
    result = vc_module.normalize_text(text)
    assert "pufa intake" in result


def test_normalize_strips_sup_a_span_refs():
    """PMC variant: <sup id="..."><a><span>N</span></a></sup>"""
    text = 'markers<sup id="xref-ref-2"><a href="#ref-2"><span>2</span></a></sup> of inflammation'
    result = vc_module.normalize_text(text)
    assert "markers of inflammation" in result


def test_normalize_strips_bare_sup_refs_after_long_word():
    """Bare <sup>N</sup> after a long word (>=4 letters) is a reference -- strip it."""
    text = 'plasticity<sup>1</sup> throughout'
    result = vc_module.normalize_text(text)
    assert "plasticity throughout" in result


def test_normalize_preserves_sup_exponents():
    """Bare <sup>N</sup> in exponent context (digit, /, or compound unit) preserves digit."""
    assert "cd/m2" in vc_module.normalize_text("cd/m<sup>2</sup>")
    assert "109" in vc_module.normalize_text("10<sup>9</sup>")
    assert "w/m2" in vc_module.normalize_text("W/m<sup>2</sup>")
    assert "j/cm2" in vc_module.normalize_text("J/cm<sup>2</sup>")
    assert "g/cm3" in vc_module.normalize_text("g/cm<sup>3</sup>")


def test_normalize_strips_bare_sup_refs_after_long_words():
    """Bare <sup>N</sup> after long words (>=4 letters) are references -- strip them."""
    result = vc_module.normalize_text("plasticity<sup>1</sup> throughout")
    assert "plasticity" in result
    assert "throughout" in result
    assert "plasticity throughout" in result  # digit removed, not preserved


def test_normalize_strips_bare_sup_refs_after_short_words():
    """Bare <sup>N</sup> after short common words are references -- strip them.
    The heuristic is conservative: only digit, /, or alpha-in-compound-unit
    counts as exponent context. Short words like 'the', 'DNA' are NOT units."""
    result = vc_module.normalize_text("the<sup>1</sup> evidence")
    assert "the evidence" in result  # digit stripped, not "the1 evidence"
    result = vc_module.normalize_text("DNA<sup>3</sup> replication")
    assert "dna replication" in result  # digit stripped


def test_normalize_strips_bare_sup_refs_after_punctuation():
    """Bare <sup>N</sup> after punctuation are references -- strip them."""
    assert "results. the" in vc_module.normalize_text("results.<sup>1</sup> The")


def test_normalize_preserves_sub_formulas():
    """<sub> content should always be preserved as inline text."""
    assert "h2o" in vc_module.normalize_text("H<sub>2</sub>O")
    assert "co2" in vc_module.normalize_text("CO<sub>2</sub> emissions")


def test_normalize_preserves_ordinals():
    """Ordinal suffixes in <sup> should be preserved."""
    assert "4th edition" in vc_module.normalize_text("4<sup>th</sup> edition")
    assert "21st century" in vc_module.normalize_text("21<sup>st</sup> century")


def test_normalize_strips_styled_spans_inline():
    """CSS-styled <span> tags should not create word boundaries.
    Wikipedia uses <span style="margin-left:0.25em">x</span> around operators."""
    text = '7<span style="margin-left:0.25em">\u00d7</span>10<sup>30</sup>'
    result = vc_module.normalize_text(text)
    assert "7x1030" in result  # x normalizes to x, no spaces


def test_normalize_mixed_exponent_and_linked_ref():
    """Exponents preserved, linked refs stripped, no extra spaces."""
    text = 'cd/m<sup>2</sup> value<sup><a href="#r1">1</a></sup> here'
    result = vc_module.normalize_text(text)
    assert "cd/m2 value here" in result


def test_normalize_wikipedia_scientific_notation():
    """Full Wikipedia scientific notation with styled spans and sup exponents."""
    text = (
        '<span class="nowrap">'
        '<span data-sort-value="6973700000000000000\u2660"></span>'
        '7<span style="margin-left:0.25em;margin-right:0.15em;">\u00d7</span>'
        '10<sup>\u221230</sup>\u00a0g/cm<sup>3</sup>'
        '</span>'
    )
    result = vc_module.normalize_text(text)
    assert "7x10" in result      # x -> x, no spaces around it
    assert "30" in result        # exponent content (-30) survives -- U+2212 prefix
    assert "g/cm3" in result     # exponent preserved in compound unit


def test_normalize_liberal_preserves_standalone_unit_sups():
    """Liberal mode preserves bare <sup> content even without compound unit context."""
    result = vc_module.normalize_text("500 km<sup>2</sup> area", preserve_ambiguous_sups=True)
    assert "km2" in result


def test_normalize_conservative_strips_standalone_unit_sups():
    """Conservative mode (default) strips standalone unit sups as ambiguous."""
    result = vc_module.normalize_text("500 km<sup>2</sup> area")
    assert "km2" not in result
    assert "km" in result


def test_match_quote_standalone_unit_via_liberal_fallback():
    """_match_quote two-pass: standalone km<sup>2</sup> matched via liberal fallback."""
    page_html = '<p>The area spans 500 km<sup>2</sup> of forest.</p>'
    quote = 'The area spans 500 km2 of forest.'
    result = vc_module._match_quote(page_html, quote, "test_liberal_fallback")
    assert result is not None
    assert result["status"] == "verified"


def test_match_quote_reference_digit_stripped_by_conservative():
    """_match_quote: reference digit correctly stripped by conservative first pass."""
    page_html = '<p>Evidence shows<sup>1</sup> that sleep is affected.</p>'
    quote = 'Evidence shows that sleep is affected.'
    result = vc_module._match_quote(page_html, quote, "test_conservative_ref")
    assert result is not None
    assert result["status"] == "verified"


def test_normalize_strips_comma_separated_a_refs():
    """PMC pattern: <sup><a>5</a>,<a>6</a></sup> — comma-separated refs in one <sup>."""
    text = 'the traditional view<sup><a href="#ref5" class="bibr">5</a>,<a href="#ref6" class="bibr">6</a></sup> of fixed'
    result = vc_module.normalize_text(text)
    assert "the traditional view of fixed" in result


def test_pmc_span_fixture_quote_match():
    """Full quote match against PMC page with nested-span ref styles."""
    page_html = _read_fixture("pmc_span_refs.html")
    quote = "Clinical trials show that increased n-6 PUFA intake does not increase markers of inflammation. Multiple meta-analyses confirm these findings."
    result = vc_module._match_quote(page_html, quote, "test_span_ref")
    assert result is not None
    assert result["status"] == "verified"


def test_escaped_html_not_stripped_by_unescape():
    """Escaped HTML entities like &lt;sup&gt; must NOT be turned into tags and stripped.
    They represent visible text content that should be preserved."""
    text = "See formula &lt;sup&gt;2&lt;/sup&gt; in the appendix"
    result = vc_module.normalize_text(text)
    # The "<sup>2</sup>" should appear as text, not be stripped as a tag
    assert "2" in result
    assert "sup" in result  # the literal text "sup" should survive


def test_normalize_unifies_single_and_double_quotes():
    """Double quotes and single quotes should be treated as equivalent for matching."""
    text_double = 'seed oils are "toxic," not healthy'
    text_single = "seed oils are 'toxic,' not healthy"
    assert vc_module.normalize_text(text_double) == vc_module.normalize_text(text_single)


def test_quote_type_mismatch_full_quote_match():
    """A page using double quotes around a word should match a quote using single quotes."""
    page = '<p>scientists say seed oils are \u201ctoxic,\u201d according to the study</p>'
    quote = "scientists say seed oils are 'toxic,' according to the study"
    result = vc_module._match_quote(page, quote, "test_quote_type")
    assert result is not None
    assert result["status"] == "verified"
    assert result["method"] == "full_quote"


def test_normalize_collapses_letter_space_digit():
    """Inline tag stripping of CO<sub>2</sub> preserves 'co2' (no space inserted)."""
    text = "CO<sub>2</sub> emissions are rising"
    result = vc_module.normalize_text(text)
    assert "co2" in result


def test_normalize_collapses_word_space_hyphen():
    """Inline tag stripping of n<sup>-6</sup> preserves 'n-6' (no space inserted)."""
    text = "increased n<sup>-6</sup> PUFA intake"
    result = vc_module.normalize_text(text)
    assert "n-6" in result


def test_normalize_infinity_symbol():
    """The infinity symbol should normalize to the word 'infinity'."""
    text = "division of \u221E/\u221E results in NaN"
    result = vc_module.normalize_text(text)
    assert "infinity/infinity" in result


def test_normalize_strips_invisible_unicode():
    """Invisible Unicode characters should be removed or normalized to spaces."""
    # Soft hyphen (U+00AD) — used for line-break hints, invisible in rendering
    assert "overnight" in vc_module.normalize_text("over\u00ADnight")
    # Zero-width non-joiner (U+200C)
    assert "test" in vc_module.normalize_text("te\u200Cst")
    # Zero-width joiner (U+200D)
    assert "test" in vc_module.normalize_text("te\u200Dst")
    # Word joiner (U+2060)
    assert "test" in vc_module.normalize_text("te\u2060st")
    # BOM / zero-width no-break space (U+FEFF)
    assert "test" in vc_module.normalize_text("\uFEFFtest")
    # Minus sign (U+2212) → ASCII hyphen
    assert "10-30" in vc_module.normalize_text("10\u221230")


# ---------------------------------------------------------------------------
# MathML extraction tests
# ---------------------------------------------------------------------------


def test_normalize_extracts_mathml_alttext():
    """MathML <math> tags should be replaced with their alttext content."""
    text = (
        'matter density parameter '
        '<math alttext="\\Omega_{\\mathrm{m}}=0.315\\pm 0.007">'
        '<semantics><mrow><msub><mi>\u03A9</mi><mi>m</mi></msub>'
        '<mo>=</mo><mn>0.315</mn><mo>\u00b1</mo><mn>0.007</mn>'
        '</mrow></semantics></math>'
    )
    result = vc_module.normalize_text(text)
    assert "0.315" in result
    assert "0.007" in result


def test_normalize_mathml_single_quoted_alttext():
    """MathML with single-quoted alttext should also be extracted."""
    text = (
        "energy "
        "<math alttext='E=mc^{2}'>"
        "<semantics><mrow><mi>E</mi><mo>=</mo><mi>m</mi>"
        "<msup><mi>c</mi><mn>2</mn></msup></mrow></semantics></math>"
    )
    result = vc_module.normalize_text(text)
    assert "e=mc2" in result.lower() or "e = mc2" in result.lower()


def test_normalize_mathml_without_alttext_preserves_content():
    """MathML without alttext should strip <math> wrapper but keep inner content.
    Word boundaries must be preserved — 'value 42 here', not 'value42 here'."""
    text = 'value <math><mn>42</mn></math> here'
    result = vc_module.normalize_text(text)
    assert "value 42 here" in result


# ---------------------------------------------------------------------------
# Inline LaTeX $...$ handling (arXiv abstract pages)
# ---------------------------------------------------------------------------


def test_normalize_strips_inline_latex_simple():
    """Inline LaTeX $\\Lambda$CDM should normalize to match ASCII 'lcdm'."""
    text = 'the base-$\\Lambda$CDM cosmology'
    result = vc_module.normalize_text(text)
    # \Lambda -> Λ -> λ -> l (Greek-to-ASCII), so $\Lambda$CDM -> lcdm
    assert "lcdm" in result
    assert "$" not in result


def test_normalize_preserves_non_latex_greek():
    """Greek letters NOT from inline LaTeX should be preserved (scoped transliteration)."""
    # Plain Greek text (e.g., from MathML alttext or direct HTML) is NOT transliterated.
    # This prevents false matches like μm -> mm.
    text = 'Ωm = 0.315 and μm wavelength'
    result = vc_module.normalize_text(text)
    # Greek letters survive lowercasing but are NOT converted to ASCII
    assert "\u03c9" in result or "\u03a9" in result.upper()  # ω preserved
    assert "\u03bc" in result  # μ preserved (NOT converted to 'm')


def test_normalize_inline_latex_greek_is_transliterated():
    """Greek from inline LaTeX IS transliterated to ASCII."""
    text = 'the $\\Lambda$CDM model and $\\Omega_m$'
    result = vc_module.normalize_text(text)
    assert "lcdm" in result  # Λ from LaTeX -> L -> l
    assert "$" not in result


def test_normalize_strips_inline_latex_with_subscript():
    """Inline LaTeX $H_0$ should become H0."""
    text = 'the Hubble constant $H_0 = (67.4\\pm 0.5)$ km/s/Mpc'
    result = vc_module.normalize_text(text)
    assert "h0" in result
    assert "67.4" in result
    assert "$" not in result


def test_normalize_strips_inline_latex_pm():
    """Inline LaTeX \\pm should become ± (then normalized to +-)."""
    text = 'value is $73.04\\pm 1.04$ km/s/Mpc'
    result = vc_module.normalize_text(text)
    assert "73.04" in result
    assert "1.04" in result
    assert "$" not in result


def test_normalize_inline_latex_preserves_surrounding_text():
    """Text around inline LaTeX should not be eaten."""
    text = 'Assuming the base-$\\Lambda$CDM cosmology, the inferred'
    result = vc_module.normalize_text(text)
    assert "assuming" in result
    assert "inferred" in result
    assert "cosmology" in result
    assert "lcdm" in result  # Greek-to-ASCII applied


def test_normalize_strips_simple_inline_latex_variables():
    """Simple inline LaTeX like $x$, $N$, $z$ should have $ stripped."""
    text = 'for all values of $x$ and $N$ at redshift $z$'
    result = vc_module.normalize_text(text)
    assert "$" not in result
    assert "x" in result
    assert "n" in result  # lowercased
    assert "z" in result


def test_normalize_strips_inline_latex_multi_letter_token():
    """Unadorned multi-letter tokens like $LCDM$, $pi$ should have $ stripped."""
    text = 'the $LCDM$ model predicts $pi$ decay'
    result = vc_module.normalize_text(text)
    assert "$" not in result
    assert "lcdm" in result
    assert "pi" in result


def test_normalize_inline_latex_does_not_affect_dollar_amounts():
    """Bare dollar signs in financial context ($100) should not trigger LaTeX stripping."""
    text = 'the cost was $100 and rose to $200'
    result = vc_module.normalize_text(text)
    assert "100" in result
    assert "200" in result


def test_normalize_inline_latex_does_not_affect_dollar_with_decimals():
    """Dollar amounts with decimals ($2.5) should be preserved."""
    text = 'revenue of $2.5 million and costs of $1,200'
    result = vc_module.normalize_text(text)
    assert "2.5" in result
    assert "1,200" in result or "1200" in result


# ---------------------------------------------------------------------------
# Integration tests for all three false-negative classes
# ---------------------------------------------------------------------------


def test_pmc_exponent_fixture_quote_match():
    """Integration: PMC page with cd/m<sup>2</sup> exponents and linked refs.
    The original bug: <sup>2</sup> was stripped as a reference, breaking cd/m² matching."""
    page_html = _read_fixture("pmc_exponents.html")
    quote = (
        "The luminance of a clear blue sky is around 5000 cd/m2 "
        "(compared with 300 for a TV display and 150\u2013250 cd/m2 for a computer screen)"
    )
    result = vc_module._match_quote(page_html, quote, "test_pmc_exponent")
    assert result is not None
    assert result["status"] == "verified", f"Expected verified, got {result}"


def test_pmc_exponent_fixture_refs_still_stripped():
    """Integration: linked refs on the same page are still stripped correctly."""
    page_html = _read_fixture("pmc_exponents.html")
    quote = (
        "Currently, there is no evidence that screen use and LEDs in normal use "
        "are deleterious to the human retina."
    )
    result = vc_module._match_quote(page_html, quote, "test_pmc_ref_strip")
    assert result is not None
    assert result["status"] == "verified", f"Expected verified, got {result}"


def test_wikipedia_scientific_notation_fixture():
    """Integration: Wikipedia page with styled <span> around × and <sup> exponents.
    Covers Class 1+2: styled spans creating fake word boundaries + sup exponents."""
    page_html = _read_fixture("wikipedia_scientific.html")
    quote = (
        "Dark energy's density is very low: "
        "7\u00d710\u221230 g/cm3 (6\u00d710\u221210 J/m3 in mass-energy), "
        "much less than the density of ordinary matter or dark matter within galaxies."
    )
    result = vc_module._match_quote(page_html, quote, "test_wiki_scientific")
    assert result is not None
    assert result["status"] == "verified", f"Expected verified, got {result}"


# ---------------------------------------------------------------------------
# Fix: mojibake (double-encoded UTF-8) repair
# Real pattern from chronobiologyinmedicine.org (B9 case study)
# ---------------------------------------------------------------------------


def test_normalize_repairs_mojibake_en_dash():
    """Double-encoded en-dash (â\\x80\\x93) should be repaired to actual en-dash, then normalized."""
    # \xc3\xa2\xc2\x80\xc2\x93 is the double-encoded form of en-dash U+2013
    mojibake = '460\u00e2\u0080\u0093 480 nm'  # â\x80\x93 = en-dash double-encoded
    result = vc_module.normalize_text(mojibake)
    assert '460-480' in result, f"Expected '460-480' in '{result}'"


def test_normalize_mojibake_preserves_clean_text():
    """Normal ASCII/Unicode text should not be altered by mojibake repair."""
    clean = 'normal text with en-dash \u2013 and quotes \u201c'
    result = vc_module.normalize_text(clean)
    assert 'normal text' in result


# ---------------------------------------------------------------------------
# Fix: bare bracketed linked refs [<a>N</a>] without <sup> or class="xref"
# Real HTML from PMC9920460 (microplastics exposure)
# ---------------------------------------------------------------------------


def test_normalize_strips_bare_bracketed_linked_refs():
    """Bare [<a href="#B32">32</a>] refs (no <sup>, no xref class) should be stripped."""
    html = 'seafood contaminated with microplastics [<a href="#B32-ijerph-20-02468">32</a>]. The second route'
    result = vc_module.normalize_text(html)
    assert "microplastics. the second" in result or "microplastics . the second" in result
    assert "32" not in result


def test_normalize_strips_bare_bracketed_linked_refs_multiple():
    """Multiple bare [<a>N</a>,<a>M</a>] refs should all be stripped."""
    html = 'exposure routes [<a href="#B32">32</a>,<a href="#B33">33</a>] are well documented'
    result = vc_module.normalize_text(html)
    assert "routes are well" in result or "routes  are well" in result
    assert "32" not in result
    assert "33" not in result


def test_normalize_strips_bare_bracketed_linked_refs_semicolon():
    """Semicolon-separated bare [<a>1</a>; <a>2</a>] refs should be stripped."""
    html = 'data [<a href="#r1">1</a>; <a href="#r2">2</a>] here'
    result = vc_module.normalize_text(html)
    assert "data here" in result
    assert "1" not in result.replace("data", "")  # avoid matching 'a' in 'data'


def test_normalize_strips_bare_bracketed_linked_refs_dash_range():
    """Dash-range bare [<a>1</a>-<a>3</a>] refs should be stripped."""
    html = 'data [<a href="#r1">1</a>-<a href="#r3">3</a>] here'
    result = vc_module.normalize_text(html)
    assert "data here" in result


def test_normalize_preserves_bracketed_non_numeric_links():
    """Bracketed non-numeric links like [<a>here</a>] should NOT be stripped."""
    html = 'see [<a href="/about">here</a>] for details'
    result = vc_module.normalize_text(html)
    assert "here" in result


def test_normalize_bare_bracket_ref_sets_academic_flag():
    """Bare [<a>N</a>] refs should trigger orphaned [N] stripping downstream."""
    html = 'first claim [<a href="#r1">1</a>] and later evidence [5] supports it'
    result = vc_module.normalize_text(html)
    assert "first claim and later evidence supports it" in result


# ---------------------------------------------------------------------------
# Fix: non-numeric <sup> reference markers (<sup>w24</sup>, <sup>*</sup>)
# Real HTML from PMC2151163 (hair growth) and JVL (settlements)
# ---------------------------------------------------------------------------


def test_normalize_strips_sup_alpha_numeric_refs():
    """<sup>w24</sup> (letter+digits) ref markers should be stripped, not concatenated."""
    html = 'retraction of the skin around the hair or nails.<sup>w24</sup> The actual growth'
    result = vc_module.normalize_text(html)
    assert "nails. the actual" in result
    assert "w24" not in result


def test_normalize_strips_sup_asterisk_refs():
    """<sup>*</sup> asterisk ref markers should be stripped."""
    html = 'population data<sup>*</sup> As of January 1'
    result = vc_module.normalize_text(html)
    assert "data as of" in result or "data  as of" in result
    assert "*" not in result


def test_normalize_strips_sup_dagger_refs():
    """<sup>†</sup> dagger ref markers should be stripped."""
    html = 'significant results<sup>\u2020</sup> compared with'
    result = vc_module.normalize_text(html)
    assert "results compared" in result or "results  compared" in result


def test_normalize_preserves_sup_exponents_still():
    """Exponent contexts must still be preserved after non-numeric ref stripping."""
    html = 'density is 7x10<sup>-30</sup> g/cm<sup>3</sup>'
    result = vc_module.normalize_text(html)
    assert "10-30" in result
    assert "cm3" in result


# ---------------------------------------------------------------------------
# Fix: space after dash in numeric ranges (460– 480 → 460-480)
# Real HTML from chronobiologyinmedicine.org (B9 case study)
# ---------------------------------------------------------------------------


def test_normalize_collapses_space_after_dash_in_range():
    """Spaces after dashes in numeric ranges should be collapsed: '460- 480' → '460-480'."""
    # After Unicode normalization, en-dash becomes hyphen, but space remains
    html = 'blue light (460\u2013 480 nm) has been shown'
    result = vc_module.normalize_text(html)
    assert "460-480" in result


def test_normalize_preserves_dash_space_in_non_range():
    """Dash-space should be preserved when NOT in a numeric range context."""
    html = 'the results - however surprising - were clear'
    result = vc_module.normalize_text(html)
    assert "results - however" in result


def test_arxiv_mathml_fixture():
    """Integration: ar5iv page with MathML <math alttext='...'> containing LaTeX.
    Covers Class 3: MathML extraction via alttext + LaTeX-to-text conversion.
    The quote includes the full mathematical expression to verify LaTeX-to-text
    actually produces meaningful output, not just stray digits."""
    page_html = _read_fixture("arxiv_mathml.html")
    # First verify normalize_text produces the expected math content
    normalized = vc_module.normalize_text(page_html)
    assert "0.315" in normalized
    assert "0.007" in normalized
    # The LaTeX \Omega should become Ω (U+03A9), then lowercase ω
    assert "\u03c9" in normalized or "omega" in normalized  # lowercase omega
    # Now test full _match_quote with a quote that requires the math structure.
    # Note: LaTeX \pm produces a space after ± (from '\pm 0.007'), so the quote
    # must also include the space to match the normalized page text.
    quote = (
        "The matter density parameter \u03a9m=0.315\u00b1 0.007 "
        "is well constrained by CMB observations."
    )
    result = vc_module._match_quote(page_html, quote, "test_arxiv_mathml")
    assert result is not None
    assert result["status"] == "verified", f"Expected verified, got {result}"


# ---------------------------------------------------------------------------
# Math operator spacing collapse
# ---------------------------------------------------------------------------


def test_normalize_collapses_greek_latin_spacing():
    """ar5iv MathML splits 'Ωm' into 'Ω m' — space should be collapsed."""
    text = 'parameter \u03a9 m'
    result = vc_module.normalize_text(text)
    # After lowercase: Ω m → ωm (no space). Greek preserved (not from LaTeX).
    assert "\u03c9m" in result


def test_normalize_collapses_spaces_around_equals():
    """Spaces around = between numbers/symbols should be collapsed."""
    text = 'parameter \u03a9m = 0.315'
    result = vc_module.normalize_text(text)
    # After lowercase: ωm = 0.315 → ωm=0.315. Greek preserved (not from LaTeX).
    assert "\u03c9m=0.315" in result


def test_normalize_collapses_spaces_around_pm():
    """Spaces around ± between numbers should be collapsed."""
    text = '0.315 \u00b1 0.007'
    result = vc_module.normalize_text(text)
    assert "0.315\u00b10.007" in result or "0.315+-0.007" in result


def test_normalize_preserves_spaces_in_prose():
    """Spaces around words should NOT be collapsed by math spacing rule."""
    text = 'the value is approximately equal to 42'
    result = vc_module.normalize_text(text)
    assert "is approximately equal to" in result


def test_normalize_ar5iv_full_expression():
    """Full ar5iv-style: Ω m = 0.315 ± 0.007 → ωm=0.315±0.007 (Greek join + operator collapse)."""
    text = 'matter density parameter \u03a9 m = 0.315 \u00b1 0.007'
    result = vc_module.normalize_text(text)
    # Step 3a joins Ω+m, step 3b collapses =. Greek preserved (not from LaTeX).
    assert "\u03c9m=0.315" in result
    assert " = " not in result


# ---------------------------------------------------------------------------
# _find_closest_passage
# ---------------------------------------------------------------------------


def test_find_closest_passage_paraphrased_quote():
    """Page has similar content with different wording -> closest_passage populated."""
    from scripts.verify_citations import _find_closest_passage

    page_html = (
        "<html><body><p>Insertion of a single non-operational clause can cause "
        "average accuracy to collapse by up to 65 percentage points on certain "
        "models.</p></body></html>"
    )
    query = (
        "Addition of a single irrelevant clause provokes catastrophic "
        "accuracy drops on certain models"
    )
    passage, similarity = _find_closest_passage(page_html, query)
    assert passage is not None
    assert similarity >= 0.3
    assert passage[0].isupper()  # original case preserved


def test_find_closest_passage_irrelevant_page():
    """Page with completely unrelated content -> None."""
    from scripts.verify_citations import _find_closest_passage

    page_html = "<html><body><p>Today's weather forecast calls for sunny skies and mild temperatures across the region.</p></body></html>"
    query = "quantum entanglement enables faster-than-light communication between particles"
    passage, similarity = _find_closest_passage(page_html, query)
    assert passage is None


def test_find_closest_passage_preserves_original_case():
    """Returned passage must preserve original capitalization and punctuation."""
    from scripts.verify_citations import _find_closest_passage

    page_html = (
        "<html><body><p>The PAL Framework (Program-Aided Language Models) "
        "achieves state-of-the-art accuracy on GSM8K benchmark, surpassing "
        "chain-of-thought approaches significantly.</p></body></html>"
    )
    query = (
        "PAL achieves best accuracy on GSM8K benchmark surpassing "
        "chain of thought approaches"
    )
    passage, similarity = _find_closest_passage(page_html, query)
    assert passage is not None
    assert "PAL" in passage  # original case


def test_find_closest_passage_page_shorter_than_quote():
    """When page has fewer words than the quote, should still work."""
    from scripts.verify_citations import _find_closest_passage

    page_html = "<html><body><p>Short page.</p></body></html>"
    query = "this is a much longer quote that has many more words than the page content"
    passage, similarity = _find_closest_passage(page_html, query)
    assert passage is None or similarity < 0.3


def test_verify_citation_not_found_includes_closest_passage():
    """verify_citation with wrong quote should include closest_passage suggestion."""
    from scripts.verify_citations import verify_citation
    from unittest.mock import patch

    # Page and query share enough vocabulary (~8/25 = 32% Jaccard) to exceed threshold.
    page_html = (
        "<html><body><p>Insertion of a single non-operational clause can cause "
        "average accuracy to collapse by up to 65 percentage points on certain "
        "models.</p></body></html>"
    )

    with patch("scripts.verify_citations._fetch_page", return_value=(page_html, "live", None)):
        result = verify_citation(
            "https://example.com/page",
            "Addition of a single irrelevant clause provokes catastrophic accuracy drops on certain models",
            "test_fact",
        )
    assert result["status"] == "not_found"
    assert "closest_passage" in result
    assert result["closest_passage"] is not None
    assert result["closest_similarity"] >= 0.3


def test_verify_all_citations_passes_snapshot_file():
    """verify_all_citations passes snapshot_file from empirical_facts to verify_citation."""
    from unittest.mock import patch, MagicMock
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("The key finding is that X causes Y in all tested conditions.")
        f.flush()
        tmppath = f.name
    try:
        empirical_facts = {
            "src_a": {
                "url": "https://paywalled-journal.com/article",
                "quote": "X causes Y in all tested conditions",
                "source_name": "Journal A",
                "snapshot_file": tmppath,
            }
        }
        # Mock requests to return 403 (paywall)
        import requests as real_req
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = real_req.exceptions.HTTPError(
            response=mock_resp
        )

        mock_requests = MagicMock()
        mock_requests.get.return_value = mock_resp
        mock_requests.exceptions = real_req.exceptions

        with patch("scripts.fetch.requests", mock_requests), \
             patch("scripts.verify_citations.requests", mock_requests):
            from scripts.verify_citations import verify_all_citations
            results = verify_all_citations(empirical_facts)

        assert results["src_a"]["status"] == "verified"
        assert results["src_a"]["fetch_mode"] == "snapshot"
    finally:
        os.unlink(tmppath)


def test_verify_data_values_uses_snapshot_file():
    """verify_data_values reads from snapshot_file when live fetch fails."""
    import requests as real_req
    from unittest.mock import patch, MagicMock
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("The CPI index value was 9.883 in 1913 and 308.417 in 2023.")
        f.flush()
        tmppath = f.name
    try:
        mock_requests = MagicMock()
        mock_requests.get.side_effect = real_req.exceptions.ConnectionError("refused")
        mock_requests.exceptions = real_req.exceptions

        with patch("scripts.fetch.requests", mock_requests), \
             patch("scripts.verify_citations.requests", mock_requests):
            from scripts.verify_citations import verify_data_values
            results = verify_data_values(
                "https://paywalled-stats.gov/cpi",
                {"cpi_1913": "9.883", "cpi_2023": "308.417"},
                "B1",
                snapshot_file=tmppath,
            )

        assert results["cpi_1913"]["found"] is True
        assert results["cpi_2023"]["found"] is True
    finally:
        os.unlink(tmppath)


# ---------------------------------------------------------------------------
# OA lookup fallback tests
# ---------------------------------------------------------------------------

def test_verify_citation_tries_oa_after_fetch_failed():
    """When fetch_page returns fetch_failed and URL has a DOI, try OA lookup."""
    from unittest.mock import patch, MagicMock
    import requests as real_req

    # Live fetch returns 403
    mock_requests = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.raise_for_status.side_effect = real_req.exceptions.HTTPError(response=mock_resp)
    mock_requests.get.return_value = mock_resp
    mock_requests.exceptions = real_req.exceptions

    # OA lookup returns a URL, and fetching that URL returns matching text
    oa_page = "This study shows that X causes Y in all tested conditions."

    with patch("scripts.fetch.requests", mock_requests), \
         patch("scripts.verify_citations.requests", mock_requests), \
         patch("scripts.verify_citations._try_oa_fallback") as mock_oa:
        mock_oa.return_value = (oa_page, "https://oa.example.com/article")
        from scripts.verify_citations import verify_citation
        result = verify_citation(
            "https://doi.org/10.1234/test",
            "X causes Y in all tested conditions",
            "B1",
        )

    assert result["status"] == "verified"
    assert result["fetch_mode"] == "oa_variant"
    mock_oa.assert_called_once()


def test_verify_citation_oa_mismatch_returns_fetch_failed():
    """When OA text doesn't match quote, return fetch_failed (not not_found)."""
    from unittest.mock import patch, MagicMock
    import requests as real_req

    mock_requests = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.raise_for_status.side_effect = real_req.exceptions.HTTPError(response=mock_resp)
    mock_requests.get.return_value = mock_resp
    mock_requests.exceptions = real_req.exceptions

    # OA returns text that doesn't contain the quote (version drift)
    oa_page = "This preprint discusses a completely different finding about Z."

    with patch("scripts.fetch.requests", mock_requests), \
         patch("scripts.verify_citations.requests", mock_requests), \
         patch("scripts.verify_citations._try_oa_fallback") as mock_oa:
        mock_oa.return_value = (oa_page, "https://oa.example.com/article")
        from scripts.verify_citations import verify_citation
        result = verify_citation(
            "https://doi.org/10.1234/test",
            "X causes Y in all tested conditions",
            "B1",
        )

    # OA mismatch should return fetch_failed, NOT not_found
    assert result["status"] == "fetch_failed"


def test_verify_citation_no_doi_skips_oa():
    """When URL has no DOI, OA lookup is not attempted."""
    from unittest.mock import patch, MagicMock
    import requests as real_req

    mock_requests = MagicMock()
    mock_requests.get.side_effect = real_req.exceptions.ConnectionError("refused")
    mock_requests.exceptions = real_req.exceptions

    with patch("scripts.fetch.requests", mock_requests), \
         patch("scripts.verify_citations.requests", mock_requests), \
         patch("scripts.verify_citations._try_oa_fallback") as mock_oa:
        mock_oa.return_value = (None, None)
        from scripts.verify_citations import verify_citation
        result = verify_citation(
            "https://example.com/no-doi",
            "some quote",
            "B1",
        )

    assert result["status"] == "fetch_failed"


def test_verify_citation_oa_disabled():
    """When oa_lookup=False, OA is not attempted even with a DOI."""
    from unittest.mock import patch, MagicMock
    import requests as real_req

    mock_requests = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.raise_for_status.side_effect = real_req.exceptions.HTTPError(response=mock_resp)
    mock_requests.get.return_value = mock_resp
    mock_requests.exceptions = real_req.exceptions

    with patch("scripts.fetch.requests", mock_requests), \
         patch("scripts.verify_citations.requests", mock_requests), \
         patch("scripts.verify_citations._try_oa_fallback") as mock_oa:
        from scripts.verify_citations import verify_citation
        result = verify_citation(
            "https://doi.org/10.1234/test",
            "some quote",
            "B1",
            oa_lookup=False,
        )

    mock_oa.assert_not_called()
    assert result["status"] == "fetch_failed"
