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

Usage as module:
    from scripts.verify_citations import verify_citation, verify_all_citations

Usage as CLI:
    python scripts/verify_citations.py --url URL --quote "QUOTE TEXT"
    python scripts/verify_citations.py --facts facts.json
"""

import re
import sys
import json

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

# Import Unicode normalization from smart_extract
try:
    from scripts.smart_extract import normalize_unicode, diagnose_mismatch
except ImportError:
    from smart_extract import normalize_unicode, diagnose_mismatch


def normalize_text(text: str) -> str:
    """Normalize text for fragment matching.

    Steps performed IN ORDER (this sequence matters):
      1. Unicode normalization — NFKC + character substitution registry
         (en-dashes → hyphens, curly quotes → straight, ˚ → °, etc.)
      2. Strip HTML tags  — handles inline markup like <span>...</span>
      3. Remove spaces before punctuation — fixes "Ben-Gurion ," artifacts
      4. Collapse whitespace — multiple spaces become one
      5. Lowercase — case-insensitive matching

    This specific sequence was developed through real testing against NOAA
    (climate.gov), NASA (science.nasa.gov), the IPCC, and the U.S. State
    Department (history.state.gov).
    """
    # 1. Unicode normalization (handles en-dashes, curly quotes, degree symbols, etc.)
    text = normalize_unicode(text)
    # 2. Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # 3. Remove spaces before punctuation
    text = re.sub(r'\s+([,.:;!?\)\]])', r'\1', text)
    # 4. Collapse whitespace
    text = ' '.join(text.split())
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


def verify_citation(
    url: str,
    expected_quote: str,
    fact_id: str,
    timeout: int = 15,
) -> tuple:
    """Fetch a URL and check whether the expected quote appears on the page.

    Returns:
        (True,      message) — full quote (or >=80% of words) found in page text
        ("partial", message) — only a fragment matched; not full verification
        (False,     message) — page fetched successfully but quote not found
        (None,      message) — fetch failed (network error, HTTP error, timeout)
    """
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "proof-engine/1.0"},
            allow_redirects=True,
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        return (None, f"Fetch failed for {fact_id}: Timeout after {timeout}s on {url}")
    except requests.exceptions.ConnectionError as e:
        return (None, f"Fetch failed for {fact_id}: Connection error on {url}: {e}")
    except requests.exceptions.HTTPError as e:
        return (None, f"Fetch failed for {fact_id}: HTTP {resp.status_code} on {url}")
    except requests.exceptions.RequestException as e:
        return (None, f"Fetch failed for {fact_id}: {e}")

    page_text = normalize_text(resp.text)
    norm_quote = normalize_text(expected_quote)

    # 1. Try full quote match first — this is the real guarantee
    if norm_quote in page_text:
        return (True, f"Full quote verified for {fact_id}")

    # 2. Run diagnostics for aggressive normalization (Unicode edge cases)
    raw_page = re.sub(r'<[^>]+>', ' ', resp.text)  # strip HTML for diagnosis
    raw_page = ' '.join(raw_page.split())
    diag = diagnose_mismatch(raw_page, expected_quote)

    if diag["found"] and diag["method"] == "unicode_normalization":
        return (True, f"Full quote verified for {fact_id} (after Unicode normalization)")

    # 3. Fragment fallback — explicitly reports partial match, does NOT claim full verification
    quote_words = norm_quote.split()
    total_words = len(quote_words)
    for min_w in [6, 5, 4]:
        fragment = _extract_fragment(norm_quote, min_words=min_w)
        if fragment in page_text:
            word_count = len(fragment.split())
            coverage = word_count / total_words if total_words > 0 else 0
            if coverage >= 0.8:
                return (True, f"Quote largely verified ({word_count}/{total_words} words matched) for {fact_id}")
            else:
                return ("partial", f"Only {word_count}/{total_words} quote words matched for {fact_id} — partial verification only")

    if diag["found"]:
        return ("partial", f"Quote found via aggressive normalization ({diag['method']}) for {fact_id} — verify manually")

    fragment = _extract_fragment(norm_quote, min_words=6)
    diag_hint = f" Suggestion: {diag['suggestion']}" if diag.get("suggestion") else ""
    return (False, f"Quote NOT found for {fact_id}. Searched: '{fragment[:60]}...'{diag_hint}")


def verify_all_citations(empirical_facts: dict) -> dict:
    """Verify all empirical facts by fetching their citation URLs.

    Supports two formats per fact:
      - Single-source: {"url": "...", "quote": "...", "source_name": "..."}
      - Multi-source:  {"sources": [{"url": "...", "quote": "..."}, ...]}

    Returns:
        dict of {check_id: {"verified": True/False/None, "message": str}}
    """
    results = {}

    for fact_id, fact in empirical_facts.items():
        if "sources" in fact:
            # Multi-source format
            for i, source in enumerate(fact["sources"]):
                check_id = f"{fact_id}_source_{i}"
                url = source.get("url", "")
                quote = source.get("quote", "")
                if not url or not quote:
                    results[check_id] = {
                        "verified": None,
                        "message": f"Missing url or quote for {check_id}",
                    }
                    continue
                verified, message = verify_citation(url, quote, check_id)
                results[check_id] = {"verified": verified, "message": message}
                _print_status(check_id, verified, message)
        else:
            # Single-source format
            url = fact.get("url", "")
            quote = fact.get("quote", "")
            if not url or not quote:
                results[fact_id] = {
                    "verified": None,
                    "message": f"Missing url or quote for {fact_id}",
                }
                continue
            verified, message = verify_citation(url, quote, fact_id)
            results[fact_id] = {"verified": verified, "message": message}
            _print_status(fact_id, verified, message)

    return results


def _print_status(fact_id: str, verified, message: str):
    if verified is True:
        print(f"  [✓] {fact_id}: {message}")
    elif verified == "partial":
        print(f"  [~] {fact_id}: {message}")
    elif verified is False:
        print(f"  [✗] {fact_id}: {message}")
    else:
        print(f"  [?] {fact_id}: {message}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify citation quotes against live URLs")
    parser.add_argument("--url", help="URL to fetch")
    parser.add_argument("--quote", help="Expected quote text")
    parser.add_argument("--facts", help="Path to JSON file with empirical_facts dict")
    args = parser.parse_args()

    if args.facts:
        with open(args.facts) as f:
            facts = json.load(f)
        if not facts:
            print("ERROR: No empirical facts provided — nothing to verify.")
            sys.exit(1)
        results = verify_all_citations(facts)
        if not results:
            print("ERROR: No citations found in facts — nothing was verified.")
            sys.exit(1)
        all_ok = all(r["verified"] is True for r in results.values())
        has_partial = any(r["verified"] == "partial" for r in results.values())
        if all_ok:
            print("\nAll citations verified.")
        elif has_partial:
            print("\nSome citations only partially verified.")
        else:
            print("\nSome citations failed.")
        sys.exit(0 if all_ok else 1)
    elif args.url and args.quote:
        verified, message = verify_citation(args.url, args.quote, "cli")
        _print_status("cli", verified, message)
        sys.exit(0 if verified else 1)
    else:
        parser.print_help()
        sys.exit(1)
