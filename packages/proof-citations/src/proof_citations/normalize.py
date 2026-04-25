"""Unicode normalization for citation verification.

Handles the real-world quirks discovered during proof-engine field testing:
en-dashes vs hyphens, curly vs straight quotes, degree symbols, non-breaking
spaces, etc. Does NOT transliterate Greek letters — they are distinct symbols
in scientific text (e.g., μm ≠ mm).
"""

import re
import unicodedata


# ---------------------------------------------------------------------------
# Unicode normalization registry
# ---------------------------------------------------------------------------

# These substitutions handle the most common mismatches between how text appears
# in a browser (and how an LLM transcribes it) vs. how it appears in raw HTML.
# Each entry: (from_char_or_pattern, to_char, description)
UNICODE_NORMALIZATIONS = [
    # Dashes
    ("\u2013", "-", "en-dash → hyphen"),
    ("\u2014", "-", "em-dash → hyphen"),
    ("\u2012", "-", "figure dash → hyphen"),
    ("\u2010", "-", "hyphen character → ASCII hyphen"),
    # Quotes
    ("\u2018", "'", "left single curly quote → straight"),
    ("\u2019", "'", "right single curly quote → straight"),
    ("\u201C", '"', "left double curly quote → straight"),
    ("\u201D", '"', "right double curly quote → straight"),
    # Degree symbols
    ("\u02DA", "°", "ring above → degree sign"),  # ˚ vs °
    # Spaces
    ("\u00A0", " ", "non-breaking space → space"),
    ("\u2009", " ", "thin space → space"),
    # Math/typography symbols that should normalize to ASCII equivalents
    ("\u2212", "-", "minus sign → ASCII hyphen"),
    # Invisible characters (zero-width / formatting)
    ("\u00AD", "", "soft hyphen → removed"),
    ("\u200B", "", "zero-width space → removed"),
    ("\u200C", "", "zero-width non-joiner → removed"),
    ("\u200D", "", "zero-width joiner → removed"),
    ("\u2060", "", "word joiner → removed"),
    ("\uFEFF", "", "BOM / zero-width no-break space → removed"),
    # Other common web characters
    ("\u2026", "...", "ellipsis → three dots"),
    ("\u00D7", "x", "multiplication sign → x"),
    ("\u221E", "infinity", "infinity symbol → word"),
]


def normalize_unicode(text: str) -> str:
    """Apply all known Unicode normalizations.

    This handles common mismatches between browser-rendered text (which an LLM
    transcribes) and the raw characters in HTML (which verify_citations fetches).

    Steps:
      1. Apply the character substitution registry FIRST (before NFKC can
         decompose characters like ˚ into combining forms we can't match)
      2. NFKC normalization (canonical decomposition + compatibility composition)
      3. Apply substitutions again (NFKC may produce new matchable characters)
      4. Collapse whitespace

    Returns the normalized text. Does NOT lowercase (that's for matching, not extraction).
    """
    # 1. Apply registered substitutions FIRST — some characters (like ˚ U+02DA)
    # get decomposed by NFKC into combining forms we can't easily match
    for from_char, to_char, _desc in UNICODE_NORMALIZATIONS:
        text = text.replace(from_char, to_char)

    # 2. NFKC handles many decomposition issues (e.g., ﬁ → fi, ² → 2)
    text = unicodedata.normalize("NFKC", text)

    # 3. Apply substitutions again in case NFKC produced new matchable characters
    for from_char, to_char, _desc in UNICODE_NORMALIZATIONS:
        text = text.replace(from_char, to_char)

    # 4. Collapse whitespace (but preserve newlines)
    text = re.sub(r'[^\S\n]+', ' ', text)

    return text


def diagnose_mismatch(page_text: str, quote: str, context_chars: int = 200) -> dict:
    """Diagnose why a quote isn't found on a page.

    Performs progressively aggressive normalization and searching to find where
    the quote (or fragments of it) actually appears, and reports what character
    differences cause the mismatch.

    Returns a dict with:
      - found: bool — whether the quote was found after normalization
      - method: str — what normalization was needed
      - char_diffs: list — specific character differences found
      - page_fragment: str — the matching fragment from the page (if found)
      - suggestion: str — a suggested normalization approach
    """
    result = {
        "found": False,
        "method": None,
        "char_diffs": [],
        "page_fragment": None,
        "suggestion": None,
    }

    # Try 1: Exact match after Unicode normalization
    norm_page = normalize_unicode(page_text).lower()
    norm_quote = normalize_unicode(quote).lower()

    if norm_quote in norm_page:
        result["found"] = True
        result["method"] = "unicode_normalization"
        result["suggestion"] = "Use normalize_unicode() before matching"
        return result

    # Try 2: Strip ALL non-alphanumeric characters and match
    stripped_page = re.sub(r'[^a-z0-9]', '', norm_page)
    stripped_quote = re.sub(r'[^a-z0-9]', '', norm_quote)

    if stripped_quote in stripped_page:
        result["found"] = True
        result["method"] = "alphanumeric_only"

        # Find which characters differ
        _find_char_diffs(page_text, quote, result)

        result["suggestion"] = (
            "Quote found after stripping punctuation. "
            "Write a custom normalizer that handles the specific character differences."
        )
        return result

    # Try 3: Look for significant fragments (first 5 words, last 5 words)
    words = norm_quote.split()
    for length in [8, 6, 4, 3]:
        if len(words) >= length:
            fragment = ' '.join(words[:length])
            if fragment in norm_page:
                idx = norm_page.index(fragment)
                result["found"] = True
                result["method"] = f"fragment_match ({length} words)"
                result["page_fragment"] = page_text[max(0,idx-20):idx+context_chars]
                _find_char_diffs(page_text[idx:idx+len(quote)+50], quote, result)
                result["suggestion"] = (
                    f"First {length} words match. Write a custom extraction "
                    f"that targets this fragment and handles: {result['char_diffs']}"
                )
                return result

    result["suggestion"] = (
        "Quote not found even as fragments. Verify the URL is correct "
        "and the quote is accurately transcribed."
    )
    return result


def _find_char_diffs(page_fragment: str, quote: str, result: dict):
    """Compare characters between page and quote to find specific differences."""
    diffs = []
    norm_q = normalize_unicode(quote)
    # Try to align by finding common starting substring
    for i, (pc, qc) in enumerate(zip(page_fragment.lower(), norm_q.lower())):
        if pc != qc:
            diffs.append({
                "position": i,
                "page_char": repr(pc),
                "page_ord": f"U+{ord(pc):04X}",
                "quote_char": repr(qc),
                "quote_ord": f"U+{ord(qc):04X}",
            })
            if len(diffs) >= 10:
                break
    result["char_diffs"] = diffs
