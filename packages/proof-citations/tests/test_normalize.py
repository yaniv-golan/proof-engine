from proof_citations.normalize import normalize_unicode, diagnose_mismatch


def test_normalize_en_dash_to_hyphen():
    # U+2013 EN DASH → ASCII hyphen
    assert normalize_unicode("1990\u20132000") == "1990-2000"


def test_normalize_curly_quotes_to_straight():
    assert normalize_unicode("\u201chello\u201d") == '"hello"'
    assert normalize_unicode("it\u2019s") == "it's"


def test_normalize_non_breaking_space():
    assert normalize_unicode("a\u00a0b") == "a b"


def test_normalize_degree_symbol_variant():
    # U+02DA RING ABOVE vs U+00B0 DEGREE SIGN
    assert normalize_unicode("72\u02daF") == normalize_unicode("72\u00b0F")


def test_normalize_preserves_greek_in_scientific_text():
    # Greek letters (μ, π, etc.) are distinct symbols in scientific text
    # and MUST NOT be transliterated at this layer.
    assert "\u03bc" in normalize_unicode("10 \u03bcm particle size")


def test_diagnose_mismatch_reports_not_found():
    # Real signature: diagnose_mismatch(page_text, quote, context_chars=200) -> dict
    # Returns {found, method, char_diffs, page_fragment, suggestion}.
    # When the quote is nowhere on the page after aggressive normalization,
    # `found` is False.
    diag = diagnose_mismatch("hello", "completely different text nowhere present")
    assert isinstance(diag, dict)
    assert diag["found"] is False


def test_diagnose_mismatch_finds_with_unicode_normalization():
    # Quote with smart quotes; page has ASCII — diagnose should recover the
    # match via unicode normalization and report the method.
    diag = diagnose_mismatch(
        'she said "hello world" softly',
        'she said \u201chello world\u201d softly',
    )
    assert diag["found"] is True
    assert diag["method"] in {"unicode_normalization", "alphanumeric_only"}
