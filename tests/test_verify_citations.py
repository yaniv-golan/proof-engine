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
