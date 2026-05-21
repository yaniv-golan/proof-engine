"""
verify_citations.py — Fetch URLs and verify that quoted text appears on the page.

Enforces Rule 2: Verify citations by fetching. LLMs hallucinate citations —
plausible-sounding quotes attributed to real institutions with real-looking URLs.
This script fetches each URL and checks for the quoted text.

The normalization pipeline handles real-world quirks discovered during testing:
  - Unicode mismatches: en-dashes vs hyphens, curly vs straight quotes, degree
    symbols (˚ vs °), non-breaking spaces, etc. (via smart_extract.normalize_unicode)
  - Inline HTML tags (e.g., <span class="tei-persname">Ben-Gurion</span>)
  - Extra whitespace from tag stripping
  - Spaces before punctuation after tag removal

Verification modes:
  - Live fetch (default): fetches the URL and verifies against the response
  - Snapshot fallback: if live fetch fails and a snapshot is provided, verifies
    against the pre-fetched page text
  - Wayback fallback (opt-in): if live and snapshot both fail, tries the
    Wayback Machine archive
  - PDF support: detects PDF responses and extracts text via pdfplumber/PyPDF2

Usage as module:
    from scripts.verify_citations import verify_citation, verify_all_citations

Usage as CLI:
    python scripts/verify_citations.py --url URL --quote "QUOTE TEXT"
    python scripts/verify_citations.py --facts facts.json
"""

import html
import math
import re
import sys
import json
from typing import Optional

try:
    import requests
except ImportError:
    requests = None

from proof_citations.normalize import normalize_unicode, diagnose_mismatch
from proof_citations.source_credibility import assess_credibility
from proof_citations.fetch import fetch_page as _fetch_page
from proof_citations.oa_lookup import extract_doi, lookup_oa_url
from proof_citations.latex_text import latex_to_text


# Greek-to-ASCII for LaTeX-derived text only.
# Scoped to inline LaTeX output — NOT applied globally in normalize_text()
# because scientific text uses Greek letters as distinct symbols (μm ≠ mm).
_LATEX_GREEK_MULTI = [
    ('\u0398', 'Th'), ('\u03b8', 'th'),  # Θ/θ -> Th/th
    ('\u03a0', 'Pi'), ('\u03c0', 'pi'),  # Π/π -> Pi/pi
    ('\u03a6', 'Ph'), ('\u03c6', 'ph'),  # Φ/φ -> Ph/ph
    ('\u03a7', 'Ch'), ('\u03c7', 'ch'),  # Χ/χ -> Ch/ch
    ('\u03a8', 'Ps'), ('\u03c8', 'ps'),  # Ψ/ψ -> Ps/ps
]
_LATEX_GREEK_SINGLE = str.maketrans(
    '\u0391\u0392\u0393\u0394\u0395\u0396\u0397\u0399\u039a\u039b'
    '\u039c\u039d\u039e\u039f\u03a1\u03a3\u03a4\u03a5\u03a9'
    '\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b9\u03ba\u03bb'
    '\u03bc\u03bd\u03be\u03bf\u03c1\u03c3\u03c4\u03c5\u03c9',
    'ABGDEZEIKLMNXORSTUO'
    'abgdezeiklmnxorstuo',
)


def _transliterate_latex_greek(text: str) -> str:
    """Convert Greek letters to ASCII equivalents in LaTeX-derived text."""
    for greek, ascii_eq in _LATEX_GREEK_MULTI:
        text = text.replace(greek, ascii_eq)
    return text.translate(_LATEX_GREEK_SINGLE)


# Inline HTML tags that should be stripped WITHOUT inserting spaces.
_INLINE_TAGS_RE = r'(?:span|sup|sub|a|em|strong|b|i|mark|small|code|abbr|cite|dfn|kbd|s|u|var|wbr)'


def _is_exponent_context(preceding_text: str) -> bool:
    """Determine if text preceding a bare <sup> suggests an exponent, not a reference.

    Deliberately conservative -- a preserved reference digit breaks full_quote
    containment in _match_quote() (hard false negative), while a missed exponent
    only degrades to fragment matching (soft failure). So we err on stripping.

    Heuristic:
    - Preceded by digit -> scientific notation (10^9)
    - Preceded by '/' -> unit denominator (cd/m^2, J/cm^2)
    - Preceded by alpha in a compound unit (token contains '/') -> exponent (cd/m^2)
    - Everything else -> reference footnote (strip)
    """
    if not preceding_text:
        return False
    last_char = preceding_text[-1]
    if last_char.isdigit():
        return True
    if last_char == '/':
        return True
    if last_char.isalpha():
        segments = preceding_text.split()
        last_token = segments[-1] if segments else ''
        return '/' in last_token
    return False


# ---------------------------------------------------------------------------
# Result builder
# ---------------------------------------------------------------------------

def _result(status, method=None, coverage_pct=None, fetch_error=None,
            fetch_mode="live", message="", credibility=None):
    """Build a structured citation verification result.

    Args:
        status: "verified" | "partial" | "not_found" | "fetch_failed"
        method: "full_quote" | "unicode_normalized" | "fragment" |
                "aggressive_normalization" | None
        coverage_pct: float for fragment matches, None otherwise
        fetch_error: string if fetch_failed, None otherwise
        fetch_mode: "live" | "snapshot" | "wayback"
        message: human-readable description (for inline output)
        credibility: source credibility assessment dict (from source_credibility.py)
    """
    result = {
        "status": status,
        "method": method,
        "coverage_pct": coverage_pct,
        "fetch_error": fetch_error,
        "fetch_mode": fetch_mode,
        "message": message,
    }
    if credibility is not None:
        result["credibility"] = credibility
    return result


# ---------------------------------------------------------------------------
# Light cleaning (for closest-passage original-text output)
# ---------------------------------------------------------------------------

# Inline tag pattern for _light_clean — compiled once at module level.
_LIGHT_CLEAN_INLINE_RE = r'(?:span|abbr|cite|code|dfn|em|kbd|mark|small|strong|var|wbr|a|b|i|s|u|sub|sup)(?=[\s>/])'

_NON_CONTENT_BLOCK_RE = re.compile(
    r'<(script|style|noscript|head)\b[^>]*>.*?</\1>',
    re.DOTALL | re.IGNORECASE,
)


def _strip_non_content_blocks(html_text: str) -> str:
    """Drop <script>/<style>/<noscript>/<head> blocks (content + tags).

    Page HTML often carries megabytes of JS/CSS/metadata that never contain
    citation text but whose dense `$`, `<sup>`, and inline tag tokens make
    every downstream regex pass much more expensive. On a 2.1 MB Frontiers
    snapshot this single strip is a ~75x speedup for verify_citation().

    Linear in input length (single non-greedy pattern, no nested quantifiers).

    Never call this on `expected_quote` — a quote may legitimately contain
    literal substrings like '<script>' or '<style>' that must round-trip
    through normalize_text intact. Call it only on fetched page HTML.

    Regex is byte-tag-only: HTML-entity-encoded forms like &lt;script&gt;
    are not stripped. Real pages don't entity-encode their own block tags,
    so this is an acceptable limitation.
    """
    return _NON_CONTENT_BLOCK_RE.sub(' ', html_text)


def _light_clean(html_text: str) -> str:
    """Strip HTML tags and decode entities, but preserve original case and punctuation.

    This produces text suitable for returning as a closest-passage suggestion —
    good enough for the author to locate the right passage, though they should
    still copy the final quote from the rendered page or raw source.

    Mirrors normalize_text()'s inline-tag logic: inline formatting tags
    (span, em, strong, a, b, i, etc.) are removed WITHOUT inserting spaces,
    while block-level tags (div, p, li, etc.) are replaced with spaces.
    This avoids introducing fake word boundaries in the middle of phrases.
    """
    # 1. Remove <script> and <style> blocks entirely (contents + tags).
    #    On JS-rendered pages these contain app boilerplate that would otherwise
    #    pollute the closest-passage search with irrelevant matches.
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html_text,
                  flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text,
                  flags=re.IGNORECASE | re.DOTALL)
    # 2. Strip inline formatting tags without inserting spaces (same set as
    #    normalize_text step 1.6b).
    text = re.sub(r'</?' + _LIGHT_CLEAN_INLINE_RE + r'[^>]*>', '', text,
                  flags=re.IGNORECASE)
    # 3. Replace remaining tags (block-level) with spaces.
    text = re.sub(r'<[^>]+>', ' ', text)
    # 4. Decode HTML entities.
    text = html.unescape(text)
    # 5. Collapse whitespace.
    text = ' '.join(text.split())
    return text


def _find_closest_passage(page_text_raw: str, expected_quote: str,
                          threshold: float = 0.3) -> tuple[str | None, float]:
    """Find the page passage most similar to the expected quote.

    Operates on two representations: lightly-cleaned text (for output) and
    normalized text (for scoring). Returns original-case text.

    Args:
        page_text_raw: Raw HTML page text.
        expected_quote: The quote to find a match for.
        threshold: Minimum Jaccard similarity to return a suggestion.

    Returns:
        (passage, similarity) — passage is original-case text or None,
        similarity is 0-1 float.
    """
    def _word_set(text: str) -> set:
        """Extract word tokens, stripping punctuation so 'models.' == 'models'.

        Note: this strips ALL non-word non-space chars, so hyphenated terms
        like 'en-dash' become 'endash' and '1.5' becomes '15'. This is
        acceptable for Jaccard similarity on natural language — exact numeric
        matching is handled by normalize_text() in the main verification path.
        """
        return set(re.sub(r'[^\w\s]', '', text).split())

    cleaned = _light_clean(page_text_raw)
    cleaned_words = cleaned.split()

    norm_quote = normalize_text(expected_quote)
    quote_word_set = _word_set(norm_quote)
    quote_len = len(quote_word_set)

    if quote_len == 0 or len(cleaned_words) == 0:
        return None, 0.0

    window_size = len(norm_quote.split())
    if window_size > len(cleaned_words):
        # Page shorter than quote — compare whole page but cap output
        norm_page = normalize_text(cleaned)
        page_word_set = _word_set(norm_page)
        union = quote_word_set | page_word_set
        sim = len(quote_word_set & page_word_set) / len(union) if union else 0.0
        if sim >= threshold:
            # Cap to ~500 chars to avoid persisting entire short pages
            return cleaned[:500], sim
        return None, 0.0

    # When the page is short (< 3× the query length), sliding windows become
    # noisy: the query words are scattered across the whole page and no single
    # window covers them all.  In this regime, compare the full page word-set
    # against the query and return the full page text as the passage hint.
    if len(cleaned_words) < window_size * 3:
        norm_page = normalize_text(cleaned)
        page_word_set = _word_set(norm_page)
        union = quote_word_set | page_word_set
        sim = len(quote_word_set & page_word_set) / len(union) if union else 0.0
        if sim >= threshold:
            return cleaned[:500], sim
        return None, 0.0

    # Pre-normalize the full cleaned text once, then do word-level sliding
    # on the normalized version. This avoids calling normalize_text() per
    # window (~500 calls on long pages), which is expensive (15+ regex ops).
    norm_full = normalize_text(cleaned)
    norm_words = norm_full.split()

    stride = max(1, window_size // 2)
    best_passage = None
    best_sim = 0.0

    for start in range(0, len(cleaned_words) - window_size + 1, stride):
        # Use pre-normalized words for scoring, original words for output.
        norm_window_words = norm_words[start:start + window_size]
        window_word_set = _word_set(' '.join(norm_window_words))

        union = quote_word_set | window_word_set
        if not union:
            continue
        sim = len(quote_word_set & window_word_set) / len(union)

        if sim > best_sim:
            best_sim = sim
            best_passage = ' '.join(cleaned_words[start:start + window_size])

    if best_sim >= threshold:
        return best_passage, best_sim
    return None, 0.0


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

def normalize_text(text: str, *, preserve_ambiguous_sups: bool = False) -> str:
    """Normalize text for fragment matching.

    Args:
        text: The text to normalize (may contain HTML).
        preserve_ambiguous_sups: If True, preserve bare <sup>N</sup> content
            even when the preceding context is ambiguous. Used by _match_quote()
            for a liberal fallback pass.

    Steps performed IN ORDER (this sequence matters):
      0. Mojibake repair -- detect and fix double-encoded UTF-8 (Latin-1
         roundtrip). Servers that serve UTF-8 bytes decoded as Latin-1
         produce garbage like â\x80\x93 instead of en-dash.
      1. Unicode normalization -- NFKC + character substitution registry
         (en-dashes -> hyphens, curly quotes -> straight, degree -> degree, etc.)
      1.5. Strip inline reference elements -- <sup><a>N</a></sup>,
           <a class="xref">[N,M]</a>, and bare [<a>N</a>] (common in
           academic HTML like PMC). Linked, bracketed, or sup-wrapped refs.
      1.6a. Remove bare <sup>[N]</sup> bracketed refs (unambiguously references)
      1.7.  MathML extraction — replace <math alttext="..."> with LaTeX-to-text
            conversion. Must run before inline tag stripping.
      1.6b. Strip non-sup/sub inline tags (<span>, <a>, <em>, etc.) WITHOUT
            inserting spaces -- cleans preceding context for the sup heuristic
            and prevents CSS-styled spans from creating fake word boundaries.
      1.6b2. Strip non-numeric <sup> reference markers -- asterisks (*),
             daggers (†‡), letter+digit combos (w24). Unambiguously refs.
      1.6c. Context-dependent bare <sup>N</sup> handling -- definite exponents
            preserved (preceded by digit, '/', or alpha in compound unit with '/').
            Ambiguous cases (standalone alpha, punctuation) stripped by default,
            or preserved if preserve_ambiguous_sups=True (used by _match_quote
            liberal fallback). Runs after 1.6b so heuristic sees rendered text.
      1.6d. Strip remaining <sup>/<sub> tags -- non-numeric content (ordinals,
            chemical formulas) concatenates directly with surrounding text.
      2. Strip remaining (block-level) HTML tags -- <p>, <div>, <td>, etc. get
         replaced with spaces to create word boundaries.
      2a. Decode HTML entities -- &rsquo;, &nbsp;, &#8217;, &mdash;, etc.
      2b. Second Unicode normalization pass -- decoded entities may introduce
          curly quotes, em-dashes, etc. that need normalizing.
      2.5. Strip orphaned reference markers [N] -- ONLY if academic refs
           were detected in step 1.5 or 1.6a (avoids false positives)
      3. Remove spaces before punctuation -- fixes "Ben-Gurion ," artifacts
      4. Collapse whitespace -- multiple spaces become one
      4b. Collapse spaces after hyphens in numeric ranges -- "460- 480" -> "460-480"
      5. Lowercase -- case-insensitive matching

    This specific sequence was developed through real testing against NOAA
    (climate.gov), NASA (science.nasa.gov), the IPCC, the U.S. State
    Department (history.state.gov), PMC/NIH, Wikipedia, and ar5iv.
    """
    # 0. Repair mojibake (double-encoded UTF-8) — some servers serve UTF-8
    # bytes decoded as Latin-1 then re-encoded to UTF-8, producing garbage
    # like â\x80\x93 instead of an en-dash. Try latin-1 → utf-8 roundtrip.
    try:
        repaired = text.encode('latin-1').decode('utf-8')
        # Only use repaired text if it's shorter (mojibake inflates length)
        # and doesn't contain replacement characters
        if len(repaired) < len(text) and '\ufffd' not in repaired:
            text = repaired
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass  # Not mojibake — keep original

    # 1. Unicode normalization (handles en-dashes, curly quotes, degree symbols, etc.)
    text = normalize_unicode(text)
    # 1.5. Strip inline reference elements (common in academic HTML)
    _had_academic_refs = False

    # Pattern 0: <sup> with nested <span>/<a> combinations
    # Catches PMC variants: <sup><span class="ref"><a>1</a></span></sup>
    # Also handles comma-separated refs: <sup><a>5</a>,<a>6</a></sup>
    # Requires <a> inside (nested spans without links are formula exponents)
    #
    # All inner unbounded `*` quantifiers were bounded in v1.42.0 to prevent
    # catastrophic backtracking on large academic HTML (cowork sandbox hung
    # >25s on a 924KB Frontiers article). Real-world refs use \u22643 nested spans
    # and \u226430 comma-separated targets, so the caps are conservative.
    text, n0 = re.subn(
        r'<sup[^>]*>\s*(?:<span[^>]*>\s*){0,5}<a[^>]*>\s*(?:<span[^>]*>\s*)?\[?\d+(?:[,\-\u2013]\d+){0,10}\]?\s*(?:</span>\s*)?</a>\s*(?:</span>\s*){0,5}(?:,\s*(?:<span[^>]*>\s*){0,5}<a[^>]*>\s*(?:<span[^>]*>\s*)?\[?\d+(?:[,\-\u2013]\d+){0,10}\]?\s*(?:</span>\s*)?</a>\s*(?:</span>\s*){0,5}){0,40}</sup>',
        '', text, flags=re.IGNORECASE)

    # Pattern 1: simple linked refs -- requires <a> tag inside <sup>
    text, n1 = re.subn(
        r'<sup[^>]*>\s*<a[^>]*>\s*\[?\d+(?:[,\-\u2013]\d+)*\]?\s*</a>\s*</sup>',
        '', text, flags=re.IGNORECASE)

    # Pattern 2: xref links
    text, n2 = re.subn(
        r'<a[^>]*class="[^"]*xref[^"]*"[^>]*>\s*\[?\d+(?:[,\-\u2013]\d+)*\]?\s*</a>',
        '', text, flags=re.IGNORECASE)
    # Pattern 3: bare bracketed linked refs WITHOUT <sup> or xref class
    # Catches PMC variants: [<a href="#B32-ijerph">32</a>] and multi-refs
    # separated by commas, semicolons, or dashes: [<a>1</a>, <a>2</a>],
    # [<a>1</a>; <a>2</a>], [<a>1</a>-<a>3</a>].
    # Requires <a> inside brackets with numeric content.
    text, n3 = re.subn(
        r'\[\s*<a[^>]*>\s*\d+\s*</a>\s*(?:[,;\-\u2013]\s*<a[^>]*>\s*\d+\s*</a>\s*)*\]',
        '', text, flags=re.IGNORECASE)
    _had_academic_refs = (n0 + n1 + n2 + n3) > 0

    # 1.6a. Remove bare <sup> with bracketed content -- unambiguously references
    text, n_bracketed = re.subn(
        r'<sup[^>]*>\s*\[\d+(?:[,\-\u2013]\d+)*\]\s*</sup>',
        '', text, flags=re.IGNORECASE)
    if n_bracketed > 0:
        _had_academic_refs = True

    # 1.7. MathML extraction — replace <math> tags with alttext content.
    def _math_to_text(match):
        alt = re.search(r'alttext=["\']([^"\']+)["\']', match.group(0))
        if alt:
            return latex_to_text(alt.group(1))
        inner = re.sub(r'<math[^>]*>', '', match.group(0))
        inner = inner.replace('</math>', '')
        return inner
    text = re.sub(r'<math[^>]*>.*?</math>', _math_to_text, text, flags=re.DOTALL)

    # 1.8. Inline LaTeX stripping — replace $...$ with latex_to_text() output.
    # arXiv abstract pages contain raw LaTeX like $\Lambda$CDM, $H_0 = 67.4\pm 0.5$.
    # Also handles simple variable wrapping like $x$, $N$, $z$.
    # Must NOT match bare dollar signs in financial context ($100, $2.5M).
    #
    # Strategy: two-pass approach.
    # Pass A: Match $...$ containing a LaTeX command marker (backslash, _, ^).
    #         These are unambiguously LaTeX, not currency.
    # Pass B: Match $<single-letter>$ (e.g. $x$, $N$, $z$) — single alphabetic
    #         character between $ signs. Currency never wraps a single letter.
    # Pass C: Unadorned multi-letter all-alpha tokens (e.g. $pi$, $LCDM$, $CDM$)
    #         Currency never wraps bare words in $...$.
    def _inline_latex_to_text(match):
        return _transliterate_latex_greek(latex_to_text(match.group(1)))
    # Pass A: content with \, _, or ^ (complex LaTeX)
    text = re.sub(
        r'\$([^$]*(?:\\|_|\^)[^$]*)\$',
        _inline_latex_to_text, text)
    # Pass B: single alphabetic character (simple variable names)
    text = re.sub(
        r'\$([A-Za-z])\$',
        _inline_latex_to_text, text)
    # Pass C: unadorned multi-letter all-alpha tokens (e.g. $pi$, $LCDM$, $CDM$)
    # Negative lookaround for digits prevents matching currency like $USD$50.
    text = re.sub(
        r'(?<!\d)\$([A-Za-z]{2,})\$(?!\d)',
        _inline_latex_to_text, text)

    # 1.6b. Strip non-sup/sub inline formatting tags WITHOUT inserting spaces.
    # Uses (?=[\s>]) lookahead after tag name so 's' doesn't match 'sup'/'sub'.
    _NON_SUP_SUB_INLINE_RE = r'(?:span|abbr|cite|code|dfn|em|kbd|mark|small|strong|var|wbr|a|b|i|s|u)(?=[\s>/])'
    text = re.sub(r'</?' + _NON_SUP_SUB_INLINE_RE + r'[^>]*>', '', text, flags=re.IGNORECASE)

    # 1.6b2. Strip non-numeric <sup> reference markers — asterisks (*),
    # daggers (†‡), letter+digit combos (w24, a3), and section marks (§).
    # These are unambiguously reference markers, never exponents.
    # Must run after 1.6b so inner <a>/<span> tags are already gone.
    text, n_nonnumeric_sup = re.subn(
        r'<sup[^>]*>\s*(?:[*\u2020\u2021\u00a7]+|[a-z]\d+)\s*</sup>',
        '', text, flags=re.IGNORECASE)
    if n_nonnumeric_sup > 0:
        _had_academic_refs = True

    # 1.6c. Context-dependent handling of bare <sup>N</sup>
    def _bare_sup_handler(match):
        preceding = match.group(1)
        content = match.group(2)
        if _is_exponent_context(preceding):
            return preceding + content  # definite exponent: keep digit
        if preserve_ambiguous_sups:
            return preceding + content  # liberal mode: keep all
        return preceding  # conservative: strip ambiguous
    text = re.sub(
        r'(\S*)<sup[^>]*>\s*(\d+(?:[,\-\u2013]\d+)*)\s*</sup>',
        _bare_sup_handler, text, flags=re.IGNORECASE)

    # 1.6d. Strip remaining inline tags (<sup>, <sub>) that survived 1.6c.
    text = re.sub(r'</?(?:sup|sub)[^>]*>', '', text, flags=re.IGNORECASE)

    # 2. Strip remaining (block-level) HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # 2a. Decode HTML entities — AFTER tag stripping so escaped HTML like
    # &lt;sup&gt; doesn't become a real tag and get stripped. Remaining entities
    # (&rsquo;, &nbsp;, &#8217;, etc.) are safe text content to decode.
    text = html.unescape(text)
    # 2b. Second Unicode normalization pass — decoded entities may introduce
    # curly quotes, em-dashes, non-breaking spaces that need normalizing.
    text = normalize_unicode(text)
    # 2.5. Strip orphaned reference markers — ONLY in academic HTML
    if _had_academic_refs:
        text = re.sub(r'\[\d+(?:[,;\s\-\u2013]+\d+)*\]', '', text)
    # 2c. Unify quote characters — after Unicode normalization has already
    # converted curly quotes to straight, collapse double quotes to single
    # so 'toxic' matches "toxic". Done in normalize_text (matching) only,
    # not in normalize_unicode (extraction) where quote type matters.
    text = text.replace('"', "'")
    # 3. Remove spaces before punctuation
    text = re.sub(r'\s+([,.:;!?\)\]])', r'\1', text)
    # 3a. Collapse spaces between Greek letters and adjacent Latin letters
    # or digits.  ar5iv MathML rendering can produce "Ω m" instead of "Ωm".
    # Only applies when a Greek letter is directly adjacent to [a-zA-Z0-9].
    text = re.sub(
        r'([\u03b1-\u03c9\u0391-\u03a9])\s+([a-zA-Z0-9])', r'\1\2', text)
    text = re.sub(
        r'([a-zA-Z0-9])\s+([\u03b1-\u03c9\u0391-\u03a9])', r'\1\2', text)

    # 3b. Collapse spaces around math operators (=, ±, ×) when between
    # digits, Greek letters, or decimal points. Handles ar5iv MathML output
    # where LaTeX rendering inserts spaces: "0.315 ± 0.007".
    text = re.sub(r'(?<=[\d.\u03b1-\u03c9\u0391-\u03a9a-zA-Z])\s*([=\u00b1\u00d7])\s*(?=[\d.\u03b1-\u03c9\u0391-\u03a9])', r'\1', text)
    # 4. Collapse whitespace
    text = ' '.join(text.split())
    # 4b. Collapse spaces after hyphens in numeric ranges — handles
    # "460- 480" → "460-480" (common when source has "460– 480" and
    # the en-dash is normalized to hyphen but the space remains).
    text = re.sub(r'(\d)-\s+(\d)', r'\1-\2', text)
    # 5. Lowercase
    text = text.lower()
    return text


def _extract_fragment(quote: str, min_words: int = 6) -> str:
    """Extract a verification fragment from a normalized quote.

    Uses at least `min_words` words or half the quote, whichever is larger.
    """
    words = quote.split()
    length = max(min_words, len(words) // 2)
    return ' '.join(words[:length])


def _extract_fragments(quote: str) -> list:
    """Extract sliding-window verification fragments from a normalized quote.

    Returns a list of (fragment, word_count) tuples.
    """
    words = quote.split()
    total = len(words)
    if total < 4:
        return [(' '.join(words), total)]

    candidates = []
    seen = set()

    # Only use sliding windows for quotes >= 8 words
    MIN_SLIDING_TOTAL = 8

    if total >= MIN_SLIDING_TOTAL:
        # Primary: 80% window at every offset (for "verified" matches)
        win_len = math.ceil(total * 0.8)
        for offset in range(total - win_len + 1):
            frag = ' '.join(words[offset:offset + win_len])
            if frag not in seen:
                seen.add(frag)
                candidates.append((frag, win_len))

        # Secondary: 50% window slid across all offsets (for partial matches)
        half_len = max(4, math.ceil(total * 0.5))
        if half_len < win_len:
            for offset in range(total - half_len + 1):
                frag = ' '.join(words[offset:offset + half_len])
                if frag not in seen:
                    seen.add(frag)
                    candidates.append((frag, half_len))

    # Prefix fragments: preserves existing behavior for short quotes
    for min_w in [6, 5, 4]:
        length = max(min_w, total // 2)
        frag = ' '.join(words[:length])
        if frag not in seen:
            seen.add(frag)
            candidates.append((frag, length))

    return candidates


# ---------------------------------------------------------------------------
# Quote matching (shared logic for all fetch modes)
# ---------------------------------------------------------------------------

def _match_quote(page_text_raw: str, expected_quote: str, fact_id: str,
                 fetch_mode: str = "live") -> dict:
    """Try to match a quote against page text. Used by all verification modes.

    Args:
        page_text_raw: Raw page text (HTML or plain text, not yet normalized)
        expected_quote: The quote to find
        fact_id: Identifier for messages
        fetch_mode: "live" | "snapshot" | "wayback" — passed through to result

    Returns:
        A result dict, or None if no match found at any level.
    """
    page_text = normalize_text(page_text_raw)
    norm_quote = normalize_text(expected_quote)

    # 1. Try full quote match first -- this is the real guarantee
    if norm_quote in page_text:
        return _result("verified", "full_quote", fetch_mode=fetch_mode,
                        message=f"Full quote verified for {fact_id}")

    # 1b. Liberal fallback -- retry with ambiguous bare <sup> content preserved.
    page_text_liberal = normalize_text(page_text_raw, preserve_ambiguous_sups=True)
    if norm_quote in page_text_liberal:
        return _result("verified", "full_quote", fetch_mode=fetch_mode,
                        message=f"Full quote verified for {fact_id} (liberal sup handling)")

    # 2. Run diagnostics for aggressive normalization (Unicode edge cases)
    raw_page = re.sub(r'<[^>]+>', ' ', page_text_raw)
    raw_page = ' '.join(raw_page.split())
    diag = diagnose_mismatch(raw_page, expected_quote)

    if diag["found"] and diag["method"] == "unicode_normalization":
        return _result("verified", "unicode_normalized", fetch_mode=fetch_mode,
                        message=f"Full quote verified for {fact_id} (after Unicode normalization)")

    # 3. Fragment fallback — sliding window
    quote_words = norm_quote.split()
    total_words = len(quote_words)
    best_fragment_result = None
    for fragment, word_count in _extract_fragments(norm_quote):
        if fragment in page_text:
            coverage = word_count / total_words if total_words > 0 else 0
            coverage_pct = round(coverage * 100, 1)
            if coverage >= 0.8:
                return _result("verified", "fragment", coverage_pct=coverage_pct,
                                fetch_mode=fetch_mode,
                                message=f"Quote largely verified ({word_count}/{total_words} words matched) for {fact_id}")
            elif best_fragment_result is None or coverage_pct > best_fragment_result["coverage_pct"]:
                best_fragment_result = _result("partial", "fragment", coverage_pct=coverage_pct,
                                fetch_mode=fetch_mode,
                                message=f"Only {word_count}/{total_words} quote words matched for {fact_id} — partial verification only")

    if best_fragment_result is not None:
        return best_fragment_result

    if diag["found"]:
        return _result("partial", "aggressive_normalization", fetch_mode=fetch_mode,
                        message=f"Quote found via aggressive normalization ({diag['method']}) for {fact_id} — verify manually")

    return None  # No match at any level


# ---------------------------------------------------------------------------
# OA fallback helper
# ---------------------------------------------------------------------------

def _try_oa_fallback(url: str, doi: str = None, timeout: int = 15,
                     fact_id: str = "") -> tuple:
    """Try to find and fetch an OA version of a paywalled source.

    Args:
        url: Original citation URL (used for DOI extraction if doi not provided).
        doi: Explicit DOI from empirical_facts.
        timeout: Fetch timeout for the OA URL.
        fact_id: Identifier for log messages; cosmetic.

    Returns:
        (page_text, oa_url) — both None if no OA version found or fetch failed.

    Visibility: each step prints a one-line status. Without this, multi-minute
    OA latency looks like a silent hang (the cowork sandbox lost ~45s here
    with no output, see v1.42.0 release notes).
    """
    extracted_doi = extract_doi(url, doi=doi)
    if not extracted_doi:
        return None, None

    label = f" {fact_id}" if fact_id else ""
    print(f"  [?]{label}: live+snapshot+wayback failed — trying Unpaywall OA lookup for {extracted_doi}")
    oa_url = lookup_oa_url(extracted_doi, timeout=5)
    if not oa_url:
        print(f"  [?]{label}: no OA version found via Unpaywall")
        return None, None

    print(f"  [?]{label}: OA URL found ({oa_url}) — fetching")
    # Fetch the OA URL
    page_text, fetch_mode, _ = _fetch_page(
        oa_url, timeout=timeout,
        skip_live_fetch=(requests is None),
    )
    if page_text is not None:
        return page_text, oa_url
    print(f"  [?]{label}: OA fetch failed")
    return None, None


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------

def _compute_metadata_result(url: str, expected_metadata: Optional[dict]) -> Optional[dict]:
    """Run identifier extraction + metadata comparison for `verify_citation`.

    Returns:
        - `None` when `expected_metadata` is falsy (caller didn't ask).
        - A dict matching `verify_citation_record`'s return shape when a
          structured identifier was extracted from `url` and a registered
          backend exists.
        - A skip dict (`status="skipped_no_structured_identifier"`) when
          `identify(url)` returned no structured type — OG-extraction from
          arbitrary pages is too noisy to compare claimed metadata against.
        - A skip dict (`status="skipped_no_resolver"`) when a structured
          identifier was extracted but no resolver backend is registered for
          its type (e.g., a PMC ID before a PMC backend is added).

    Lazy-imported because the registry path is only used when the new
    `expected_metadata` kwarg is exercised — keeps cold-start cost on the
    quote-only legacy path identical to v1.39.x.
    """
    if not expected_metadata:
        return None

    from proof_citations.identify import identify
    from proof_citations.resolvers import get_backend
    from proof_citations.verify_record import verify_citation_record

    identifier = identify(url)
    if identifier is None or identifier[0] == "url":
        return {
            "status": "skipped_no_structured_identifier",
            "verdict": "skipped",
            "resolved": None,
            "field_matches": {},
            "mismatches": [],
            "title_similarity": None,
            "message": (
                "URL has no structured identifier (PMID/DOI/arXiv/...); "
                "metadata check skipped — OG-extraction from arbitrary pages "
                "is too noisy to compare against claimed bibliographic fields."
            ),
            "error": None,
        }

    if get_backend(identifier[0]) is None:
        return {
            "status": "skipped_no_resolver",
            "verdict": "skipped",
            "resolved": None,
            "field_matches": {},
            "mismatches": [],
            "title_similarity": None,
            "message": (
                f"Identifier type {identifier[0]!r} has no registered resolver "
                f"backend; metadata check skipped. Either install a backend or "
                f"call `register_backend('{identifier[0]}', ...)` first."
            ),
            "error": None,
        }

    return verify_citation_record(identifier, expected_metadata)


def verify_citation(
    url: str,
    expected_quote: str,
    fact_id: str,
    timeout: int = 15,
    snapshot: str = None,
    snapshot_file: str = None,
    snapshot_fetched_at: str = None,
    wayback_fallback: bool = False,
    oa_lookup: bool = True,
    doi: str = None,
    expected_metadata: Optional[dict] = None,
    skip_live_fetch: bool = False,
    prefer_snapshot: bool = False,
    snapshot_base_dir: str = None,
) -> dict:
    """Fetch a URL and check whether the expected quote appears on the page.

    Fallback chain: live fetch → snapshot → Wayback (if opted in).

    Also performs source credibility assessment and includes it in the result
    under the "credibility" key.

    When `expected_metadata` is provided AND the URL has a structured identifier
    (PMID, DOI, arXiv, …), the result also carries a `metadata_result` key with
    a full `verify_citation_record` response — catches the metadata-chimera
    fraud class (real identifier, forged journal/year/DOI) the quote-on-page
    check alone cannot see. The top-level `status` field continues to reflect
    the quote-on-page outcome only; combine `status == "verified"` with
    `metadata_result["verdict"] == "genuine"` if you want a joint pass.

    Args:
        url: The URL to fetch.
        expected_quote: The quote text to look for.
        fact_id: Identifier for messages.
        timeout: Fetch timeout in seconds.
        snapshot: Pre-fetched page text for offline verification.
        snapshot_fetched_at: ISO 8601 timestamp of when snapshot was captured.
        wayback_fallback: If True, try Wayback Machine when live+snapshot fail.
        expected_metadata: Optional dict with claimed bibliographic fields
            (title, journal, year, doi, authors, …). If provided, runs the
            metadata-chimera check in addition to the quote-on-page check.
            New in v1.40.0.
        skip_live_fetch: If True, skip the live HTTP fetch entirely and go
            straight to snapshot → snapshot_file → wayback. Use for sources
            known to serve anti-bot challenges. New in v1.42.0.
        prefer_snapshot: If True AND a snapshot is provided, use it before
            attempting a live fetch. Live fetch remains the fallback if the
            snapshot is unusable. New in v1.42.0.

    Returns:
        dict with keys: status, method, coverage_pct, fetch_error, fetch_mode,
                        message, credibility, metadata_result
        - status: "verified" | "partial" | "not_found" | "fetch_failed"
          (quote-on-page outcome only — meaning unchanged from prior versions)
        - method: "full_quote" | "unicode_normalized" | "fragment" |
                  "aggressive_normalization" | None
        - coverage_pct: float for fragment matches, None otherwise
        - fetch_error: string if fetch_failed, None otherwise
        - fetch_mode: "live" | "snapshot" | "wayback"
        - message: human-readable description
        - credibility: {domain, source_type, tier, flags, note}
        - metadata_result: `None` when `expected_metadata` is not provided;
          otherwise a `verify_citation_record`-shaped dict, OR a skip-shaped
          dict (`status` ∈ {"skipped_no_structured_identifier",
          "skipped_no_resolver"}) when the URL or backend doesn't support it.
          New in v1.40.0; key is ALWAYS present in the return dict.
    """
    # Assess source credibility (offline, no network call)
    credibility = assess_credibility(url)

    # Run the metadata check eagerly when requested; its outcome does not
    # depend on the quote-check, so this is independent and cacheable upstream.
    metadata_result = _compute_metadata_result(url, expected_metadata)

    def _with_credibility(result):
        """Attach credibility + metadata_result to any verification result."""
        result["credibility"] = credibility
        result["metadata_result"] = metadata_result
        return result

    # Fetch page text using fallback chain
    page_text, fetch_mode, fetch_error_msg = _fetch_page(
        url, timeout=timeout, snapshot=snapshot,
        snapshot_file=snapshot_file,
        wayback_fallback=wayback_fallback,
        skip_live_fetch=skip_live_fetch or (requests is None),
        prefer_snapshot=prefer_snapshot,
        snapshot_base_dir=snapshot_base_dir,
    )

    if page_text is not None:
        page_text = _strip_non_content_blocks(page_text)
        result = _match_quote(page_text, expected_quote, fact_id, fetch_mode=fetch_mode)
        if result is not None:
            if result["status"] == "partial":
                passage, sim = _find_closest_passage(page_text, expected_quote)
                if passage is not None:
                    result["closest_passage"] = passage
                    result["closest_similarity"] = sim
            return _with_credibility(result)
        # Page fetched but quote not found — suggest closest passage
        fragment = _extract_fragment(normalize_text(expected_quote), min_words=6)
        result = _result("not_found", fetch_mode=fetch_mode,
                        message=f"Quote NOT found for {fact_id}. Searched: '{fragment[:60]}...'")
        passage, sim = _find_closest_passage(page_text, expected_quote)
        if passage is not None:
            result["closest_passage"] = passage
            result["closest_similarity"] = sim
        return _with_credibility(result)

    # All fetch methods exhausted — try OA fallback before giving up
    if oa_lookup:
        oa_text, oa_url = _try_oa_fallback(url, doi=doi, timeout=timeout,
                                           fact_id=fact_id)
        if oa_text is not None:
            oa_text = _strip_non_content_blocks(oa_text)
            oa_result = _match_quote(oa_text, expected_quote, fact_id,
                                     fetch_mode="oa_variant")
            if oa_result is not None:
                return _with_credibility(oa_result)
            # OA text fetched but quote didn't match — version drift.
            # Return fetch_failed (not not_found) so interactive recovery
            # remains available. The mismatch is likely a version issue.

    return _with_credibility(_result("fetch_failed", fetch_error=fetch_error_msg,
                    message=f"Fetch failed for {fact_id}: {fetch_error_msg}"))


# ---------------------------------------------------------------------------
# Batch verification
# ---------------------------------------------------------------------------

def verify_all_citations(empirical_facts: dict, wayback_fallback: bool = False,
                         oa_lookup: bool = True,
                         oa_lookup_budget_seconds: Optional[float] = None,
                         skip_live_fetch: bool = False,
                         prefer_snapshot: bool = False,
                         snapshot_base_dir: str = None) -> dict:
    """Verify all empirical facts by fetching their citation URLs.

    Supports two formats per fact:
      - Single-source: {"url": "...", "quote": "...", "source_name": "...",
                        "snapshot": "...", "snapshot_fetched_at": "...",
                        "expected_metadata": {...}}        # v1.40.0+
      - Multi-source:  {"sources": [{"url": "...", "quote": "...",
                        "snapshot": "...", "snapshot_fetched_at": "...",
                        "expected_metadata": {...}}, ...]}  # v1.40.0+

    The optional per-fact `expected_metadata` dict is passed through to the
    underlying `verify_citation` call; when present, the result for that fact
    gains a `metadata_result` key carrying the metadata-chimera-check outcome.
    See `verify_citation` for the field semantics. New in v1.40.0.

    Args:
        empirical_facts: Dict of fact_id → fact data.
        wayback_fallback: If True, try Wayback Machine when live+snapshot fail.
        oa_lookup: If True (default), try Unpaywall OA fallback after a fetch
            failure when the URL carries a DOI. Set to False in sandboxed
            environments with strict overall time budgets — OA lookup can add
            ~10–15s per failed fact and is silent (cowork sandbox hit this).
        oa_lookup_budget_seconds: Total wall-clock budget (in seconds) for OA
            lookups across all facts in this call. Once exhausted, subsequent
            facts skip OA. None (default) means no budget. New in v1.42.0.
        skip_live_fetch: Forwarded to each verify_citation call. New in v1.42.0.
        prefer_snapshot: Forwarded to each verify_citation call. New in v1.42.0.

    Returns:
        dict of {check_id: result_dict} where result_dict has keys:
        status, method, coverage_pct, fetch_error, fetch_mode, message,
        credibility, metadata_result.
    """
    import time as _time
    results = {}
    oa_deadline = (
        _time.monotonic() + oa_lookup_budget_seconds
        if (oa_lookup and oa_lookup_budget_seconds is not None) else None
    )

    def _oa_allowed() -> bool:
        if not oa_lookup:
            return False
        if oa_deadline is None:
            return True
        return _time.monotonic() < oa_deadline

    for fact_id, fact in empirical_facts.items():
        if "sources" in fact:
            # Multi-source format
            for i, source in enumerate(fact["sources"]):
                check_id = f"{fact_id}_source_{i}"
                url = source.get("url", "")
                quote = source.get("quote", "")
                if not url or not quote:
                    results[check_id] = _result(
                        "fetch_failed",
                        fetch_error=f"Missing url or quote for {check_id}",
                        message=f"Missing url or quote for {check_id}",
                    )
                    _print_status(check_id, results[check_id])
                    continue
                result = verify_citation(
                    url, quote, check_id,
                    snapshot=source.get("snapshot"),
                    snapshot_file=source.get("snapshot_file"),
                    snapshot_fetched_at=source.get("snapshot_fetched_at"),
                    wayback_fallback=wayback_fallback,
                    oa_lookup=_oa_allowed(),
                    doi=source.get("doi"),
                    expected_metadata=source.get("expected_metadata"),
                    skip_live_fetch=skip_live_fetch,
                    prefer_snapshot=prefer_snapshot,
                    snapshot_base_dir=snapshot_base_dir,
                )
                results[check_id] = result
                _print_status(check_id, result)
        else:
            # Single-source format
            url = fact.get("url", "")
            quote = fact.get("quote", "")
            if not url or not quote:
                results[fact_id] = _result(
                    "fetch_failed",
                    fetch_error=f"Missing url or quote for {fact_id}",
                    message=f"Missing url or quote for {fact_id}",
                )
                _print_status(fact_id, results[fact_id])
                continue
            result = verify_citation(
                url, quote, fact_id,
                snapshot=fact.get("snapshot"),
                snapshot_file=fact.get("snapshot_file"),
                snapshot_fetched_at=fact.get("snapshot_fetched_at"),
                wayback_fallback=wayback_fallback,
                oa_lookup=_oa_allowed(),
                doi=fact.get("doi"),
                expected_metadata=fact.get("expected_metadata"),
                skip_live_fetch=skip_live_fetch,
                prefer_snapshot=prefer_snapshot,
                snapshot_base_dir=snapshot_base_dir,
            )
            results[fact_id] = result
            _print_status(fact_id, result)

    return results


def verify_data_values(url: str, data_values: dict, fact_id: str,
                       timeout: int = 15, snapshot: str = None,
                       snapshot_file: str = None,
                       wayback_fallback: bool = False) -> dict:
    """Verify that data_values strings appear on the source page.

    For table-sourced data, the quote verifies the source's authority, but
    the actual numeric values (stored in data_values) are never checked
    against the page. This function fills that gap — it fetches the page
    and confirms each value string appears in the page text.

    Args:
        url: The source URL to fetch.
        data_values: Dict of {key: value_string}, e.g. {"cpi_1913": "9.883"}.
        fact_id: Identifier for messages.
        timeout: Fetch timeout in seconds.
        snapshot: Pre-fetched page text for offline verification.
        snapshot_file: Path to a local snapshot file to use when live fetch fails.
        wayback_fallback: If True, try Wayback Machine as fallback.

    Returns:
        dict of {key: {"found": bool, "value": str, "fetch_mode": str}}
    """
    page_text, fetch_mode, fetch_error = _fetch_page(
        url, timeout=timeout, snapshot=snapshot,
        snapshot_file=snapshot_file,
        wayback_fallback=wayback_fallback,
    )

    if page_text is None:
        results = {}
        for key, val in data_values.items():
            results[key] = {"found": False, "value": val, "fetch_mode": "fetch_failed",
                            "error": fetch_error or "could not obtain page text"}
            print(f"  [?] {fact_id}.{key}: fetch failed — cannot verify '{val}' on page")
        return results

    # Normalize page text for matching
    norm_page = normalize_text(page_text)

    results = {}
    for key, val in data_values.items():
        val_str = str(val).strip()
        # Check if the value string appears in the normalized page
        found = val_str.lower() in norm_page
        results[key] = {"found": found, "value": val_str, "fetch_mode": fetch_mode}
        if found:
            print(f"  [✓] {fact_id}.{key}: '{val_str}' found on page [{fetch_mode}]")
        else:
            print(f"  [✗] {fact_id}.{key}: '{val_str}' NOT found on page [{fetch_mode}]")

    return results


def verify_search_registry(search_registry: dict, timeout: int = 15) -> dict:
    """Verify that search_url endpoints in a search registry are accessible.

    For absence-of-evidence proofs. Checks each search_url with HTTP GET.
    Does NOT verify result counts — those are author-reported.

    Returns dict of {key: {"status": str, "credibility": dict, "fetch_mode": str}}
    where status is "accessible" (200), "known" (403/451), or "unreachable".
    """
    # assess_credibility is already imported at module level with try/except fallback
    results = {}
    for key, entry in search_registry.items():
        search_url = entry.get("search_url", entry["url"])
        credibility = assess_credibility(entry["url"])

        if requests is None:
            results[key] = {
                "status": "unreachable",
                "credibility": credibility,
                "fetch_mode": "none",
                "message": "requests library not available",
            }
            continue

        try:
            resp = requests.get(
                search_url,
                timeout=timeout,
                headers={"User-Agent": "proof-engine/citation-verifier"},
                allow_redirects=True,
            )
            resp.raise_for_status()
            results[key] = {
                "status": "accessible",
                "credibility": credibility,
                "fetch_mode": "live",
            }
        except requests.exceptions.HTTPError as e:
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            if status_code in (403, 451):
                results[key] = {
                    "status": "known",
                    "credibility": credibility,
                    "fetch_mode": "live",
                    "message": f"HTTP {status_code}",
                }
            else:
                results[key] = {
                    "status": "unreachable",
                    "credibility": credibility,
                    "fetch_mode": "live",
                    "message": str(e),
                }
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            results[key] = {
                "status": "unreachable",
                "credibility": credibility,
                "fetch_mode": "live",
                "message": str(e),
            }

    return results


def build_citation_detail(fact_registry: dict, citation_results: dict,
                          empirical_facts: dict) -> dict:
    """Build the citation_detail dict for the JSON summary.

    Maps FACT_REGISTRY entries to their citation results.

    Single-source: one entry keyed by fact_id.
    Multi-source: one entry per sub-source keyed {fact_id}_source_{N},
    preserving the "one row per source — no aggregation" output contract.

    Args:
        fact_registry: The proof's FACT_REGISTRY dict.
        citation_results: Return value of verify_all_citations().
        empirical_facts: The proof's empirical_facts dict.

    Returns:
        dict of citation details for Type B facts.
    """
    detail = {}
    for fact_id, info in fact_registry.items():
        if not isinstance(info, dict):
            raise TypeError(
                f"FACT_REGISTRY['{fact_id}'] is a {type(info).__name__}, expected dict. "
                f"Use: {{'key': '...', 'label': '...'}} for B/S-type, "
                f"or {{'label': '...', 'method': None, 'result': None}} for A-type."
            )
        key = info.get("key")
        if not key:
            continue
        ef = empirical_facts.get(key, {})

        if key in citation_results:
            # Single-source: direct match
            cr = citation_results[key]
            detail[fact_id] = {
                "source_key": key,
                "source_name": ef.get("source_name", ""),
                "url": ef.get("url", ""),
                "quote": ef.get("quote", ""),
                "status": cr["status"],
                "method": cr.get("method", ""),
                "coverage_pct": cr.get("coverage_pct"),
                "fetch_mode": cr.get("fetch_mode", ""),
                "credibility": cr.get("credibility"),
            }
        else:
            # Multi-source: {key}_source_N keys from verify_all_citations()
            prefix = f"{key}_source_"
            sub_keys = []
            for k in citation_results:
                if k.startswith(prefix):
                    try:
                        idx = int(k[len(prefix):])
                        sub_keys.append((idx, k))
                    except ValueError:
                        continue
            sub_keys.sort(key=lambda pair: pair[0])
            if sub_keys:
                sources = ef.get("sources", [])
                source_name = ef.get("source_name", "")
                for idx, sk in sub_keys:
                    cr = citation_results[sk]
                    src = sources[idx] if idx < len(sources) else {}
                    detail[f"{fact_id}_source_{idx}"] = {
                        "source_key": sk,
                        "source_name": source_name,
                        "url": src.get("url", ""),
                        "quote": src.get("quote", ""),
                        "status": cr["status"],
                        "method": cr.get("method", ""),
                        "coverage_pct": cr.get("coverage_pct"),
                        "fetch_mode": cr.get("fetch_mode", ""),
                        "credibility": cr.get("credibility"),
                    }
    return detail


def _print_status(fact_id: str, result: dict):
    status = result["status"]
    msg = result["message"]
    mode = result.get("fetch_mode", "live")
    mode_tag = f" [{mode}]" if mode != "live" else ""
    cred = result.get("credibility")
    cred_tag = ""
    if cred:
        tier = cred.get("tier", "?")
        stype = cred.get("source_type", "unknown")
        cred_tag = f" (source: tier {tier}/{stype})"
        if cred.get("flags"):
            cred_tag += f" [{', '.join(cred['flags'])}]"
    if status == "verified":
        print(f"  [✓] {fact_id}{mode_tag}: {msg}{cred_tag}")
    elif status == "partial":
        print(f"  [~] {fact_id}{mode_tag}: {msg}{cred_tag}")
    elif status == "not_found":
        print(f"  [✗] {fact_id}{mode_tag}: {msg}{cred_tag}")
    else:  # fetch_failed
        print(f"  [?] {fact_id}{mode_tag}: {msg}{cred_tag}")
    cp = result.get("closest_passage")
    if cp:
        sim_pct = result.get("closest_similarity", 0) * 100
        print(f"        💡 Hint — closest match ({sim_pct:.0f}% similar): \"{cp[:120]}...\"")
        print(f"        ⚠️  Do not copy this directly — locate this text on the page and copy the rendered version.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify citation quotes against live URLs")
    parser.add_argument("--url", help="URL to fetch")
    parser.add_argument("--quote", help="Expected quote text")
    parser.add_argument("--facts", help="Path to JSON file with empirical_facts dict")
    parser.add_argument("--wayback", action="store_true", help="Enable Wayback Machine fallback")
    args = parser.parse_args()

    if args.facts:
        with open(args.facts) as f:
            facts = json.load(f)
        if not facts:
            print("ERROR: No empirical facts provided — nothing to verify.")
            sys.exit(1)
        results = verify_all_citations(facts, wayback_fallback=args.wayback)
        if not results:
            print("ERROR: No citations found in facts — nothing was verified.")
            sys.exit(1)
        all_ok = all(r["status"] == "verified" for r in results.values())
        has_partial = any(r["status"] == "partial" for r in results.values())
        if all_ok:
            print("\nAll citations verified.")
        elif has_partial:
            print("\nSome citations only partially verified.")
        else:
            print("\nSome citations failed.")
        sys.exit(0 if all_ok else 1)
    elif args.url and args.quote:
        result = verify_citation(args.url, args.quote, "cli",
                                  wayback_fallback=args.wayback)
        _print_status("cli", result)
        sys.exit(0 if result["status"] == "verified" else 1)
    else:
        parser.print_help()
        sys.exit(1)
