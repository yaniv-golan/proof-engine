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

import re
import sys
import json

try:
    import requests
except ImportError:
    requests = None

# Import Unicode normalization from smart_extract
try:
    from scripts.smart_extract import normalize_unicode, diagnose_mismatch
except ImportError:
    from smart_extract import normalize_unicode, diagnose_mismatch

# Import source credibility assessment
try:
    from scripts.source_credibility import assess_credibility
except ImportError:
    from source_credibility import assess_credibility


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
# Text normalization
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# PDF text extraction
# ---------------------------------------------------------------------------

def _extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF bytes. Tries pdfplumber first, then PyPDF2.

    Returns None if no PDF library is available or if extraction fails
    for any reason (malformed PDF, empty content, etc.).
    """
    try:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        pass
    except Exception:
        pass  # Malformed PDF or extraction error — fall through to PyPDF2
    try:
        import PyPDF2
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        pass
    except Exception:
        pass  # Malformed PDF or extraction error
    return None  # No PDF library available or extraction failed


# ---------------------------------------------------------------------------
# Wayback Machine fallback
# ---------------------------------------------------------------------------

def _try_wayback(url: str, timeout: int = 15) -> str:
    """Try fetching a URL from the Wayback Machine. Returns page text or None."""
    if requests is None:
        return None
    wayback_url = f"https://web.archive.org/web/{url}"
    try:
        resp = requests.get(wayback_url, timeout=timeout,
                            headers={"User-Agent": "proof-engine/1.0"},
                            allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.RequestException:
        return None


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

    # 1. Try full quote match first — this is the real guarantee
    if norm_quote in page_text:
        return _result("verified", "full_quote", fetch_mode=fetch_mode,
                        message=f"Full quote verified for {fact_id}")

    # 2. Run diagnostics for aggressive normalization (Unicode edge cases)
    raw_page = re.sub(r'<[^>]+>', ' ', page_text_raw)
    raw_page = ' '.join(raw_page.split())
    diag = diagnose_mismatch(raw_page, expected_quote)

    if diag["found"] and diag["method"] == "unicode_normalization":
        return _result("verified", "unicode_normalized", fetch_mode=fetch_mode,
                        message=f"Full quote verified for {fact_id} (after Unicode normalization)")

    # 3. Fragment fallback
    quote_words = norm_quote.split()
    total_words = len(quote_words)
    for min_w in [6, 5, 4]:
        fragment = _extract_fragment(norm_quote, min_words=min_w)
        if fragment in page_text:
            word_count = len(fragment.split())
            coverage = word_count / total_words if total_words > 0 else 0
            coverage_pct = round(coverage * 100, 1)
            if coverage >= 0.8:
                return _result("verified", "fragment", coverage_pct=coverage_pct,
                                fetch_mode=fetch_mode,
                                message=f"Quote largely verified ({word_count}/{total_words} words matched) for {fact_id}")
            else:
                return _result("partial", "fragment", coverage_pct=coverage_pct,
                                fetch_mode=fetch_mode,
                                message=f"Only {word_count}/{total_words} quote words matched for {fact_id} — partial verification only")

    if diag["found"]:
        return _result("partial", "aggressive_normalization", fetch_mode=fetch_mode,
                        message=f"Quote found via aggressive normalization ({diag['method']}) for {fact_id} — verify manually")

    return None  # No match at any level


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------

def verify_citation(
    url: str,
    expected_quote: str,
    fact_id: str,
    timeout: int = 15,
    snapshot: str = None,
    snapshot_fetched_at: str = None,
    wayback_fallback: bool = False,
) -> dict:
    """Fetch a URL and check whether the expected quote appears on the page.

    Fallback chain: live fetch → snapshot → Wayback (if opted in).

    Also performs source credibility assessment and includes it in the result
    under the "credibility" key.

    Args:
        url: The URL to fetch.
        expected_quote: The quote text to look for.
        fact_id: Identifier for messages.
        timeout: Fetch timeout in seconds.
        snapshot: Pre-fetched page text for offline verification.
        snapshot_fetched_at: ISO 8601 timestamp of when snapshot was captured.
        wayback_fallback: If True, try Wayback Machine when live+snapshot fail.

    Returns:
        dict with keys: status, method, coverage_pct, fetch_error, fetch_mode,
                        message, credibility
        - status: "verified" | "partial" | "not_found" | "fetch_failed"
        - method: "full_quote" | "unicode_normalized" | "fragment" |
                  "aggressive_normalization" | None
        - coverage_pct: float for fragment matches, None otherwise
        - fetch_error: string if fetch_failed, None otherwise
        - fetch_mode: "live" | "snapshot" | "wayback"
        - message: human-readable description
        - credibility: {domain, source_type, tier, flags, note}
    """
    # Assess source credibility (offline, no network call)
    credibility = assess_credibility(url)

    def _with_credibility(result):
        """Attach credibility assessment to any verification result."""
        result["credibility"] = credibility
        return result

    # --- 1. Try live fetch ---
    live_page = None
    fetch_error_msg = None
    if requests is not None:
        try:
            resp = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "proof-engine/1.0"},
                allow_redirects=True,
            )
            resp.raise_for_status()

            # Detect PDF
            content_type = resp.headers.get("Content-Type", "")
            is_pdf = "application/pdf" in content_type or url.lower().endswith(".pdf")

            if is_pdf:
                pdf_text = _extract_pdf_text(resp.content)
                if pdf_text is None:
                    fetch_error_msg = f"PDF detected but no extraction library available (pip install pdfplumber)"
                else:
                    live_page = pdf_text
            else:
                live_page = resp.text

        except requests.exceptions.Timeout:
            fetch_error_msg = f"Timeout after {timeout}s on {url}"
        except requests.exceptions.ConnectionError as e:
            fetch_error_msg = f"Connection error on {url}: {e}"
        except requests.exceptions.HTTPError:
            fetch_error_msg = f"HTTP {resp.status_code} on {url}"
        except requests.exceptions.RequestException as e:
            fetch_error_msg = f"{e}"
    else:
        fetch_error_msg = "requests package not installed — skipping live fetch"

    # Try matching against live page
    if live_page is not None:
        result = _match_quote(live_page, expected_quote, fact_id, fetch_mode="live")
        if result is not None:
            return _with_credibility(result)
        # Live fetch succeeded but quote not found
        fragment = _extract_fragment(normalize_text(expected_quote), min_words=6)
        return _with_credibility(_result("not_found", fetch_mode="live",
                        message=f"Quote NOT found for {fact_id}. Searched: '{fragment[:60]}...'"))

    # --- 2. Try snapshot fallback (deterministic, user-provided) ---
    if snapshot:
        result = _match_quote(snapshot, expected_quote, fact_id, fetch_mode="snapshot")
        if result is not None:
            return _with_credibility(result)
        # Snapshot available but quote not in it
        return _with_credibility(_result("not_found", fetch_mode="snapshot",
                        message=f"Quote NOT found in snapshot for {fact_id}"))

    # --- 3. Try Wayback Machine (opt-in, non-deterministic) ---
    if wayback_fallback:
        wayback_text = _try_wayback(url, timeout)
        if wayback_text is not None:
            result = _match_quote(wayback_text, expected_quote, fact_id, fetch_mode="wayback")
            if result is not None:
                return _with_credibility(result)
            return _with_credibility(_result("not_found", fetch_mode="wayback",
                            message=f"Quote NOT found in Wayback archive for {fact_id}"))

    # --- 4. All methods exhausted ---
    return _with_credibility(_result("fetch_failed", fetch_error=fetch_error_msg,
                    message=f"Fetch failed for {fact_id}: {fetch_error_msg}"))


# ---------------------------------------------------------------------------
# Batch verification
# ---------------------------------------------------------------------------

def verify_all_citations(empirical_facts: dict, wayback_fallback: bool = False) -> dict:
    """Verify all empirical facts by fetching their citation URLs.

    Supports two formats per fact:
      - Single-source: {"url": "...", "quote": "...", "source_name": "...",
                        "snapshot": "...", "snapshot_fetched_at": "..."}
      - Multi-source:  {"sources": [{"url": "...", "quote": "...",
                        "snapshot": "...", "snapshot_fetched_at": "..."}, ...]}

    Args:
        empirical_facts: Dict of fact_id → fact data.
        wayback_fallback: If True, try Wayback Machine when live+snapshot fail.

    Returns:
        dict of {check_id: result_dict} where result_dict has keys:
        status, method, coverage_pct, fetch_error, fetch_mode, message
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
                    snapshot_fetched_at=source.get("snapshot_fetched_at"),
                    wayback_fallback=wayback_fallback,
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
                snapshot_fetched_at=fact.get("snapshot_fetched_at"),
                wayback_fallback=wayback_fallback,
            )
            results[fact_id] = result
            _print_status(fact_id, result)

    return results


def verify_data_values(url: str, data_values: dict, fact_id: str,
                       timeout: int = 15, snapshot: str = None,
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
        wayback_fallback: If True, try Wayback Machine as fallback.

    Returns:
        dict of {key: {"found": bool, "value": str, "fetch_mode": str}}
    """
    # Get page text using the same fallback chain as verify_citation
    page_text = None
    fetch_mode = "live"
    fetch_error = None

    if requests is not None:
        try:
            resp = requests.get(url, timeout=timeout,
                                headers={"User-Agent": "proof-engine/1.0"},
                                allow_redirects=True)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                page_text = _extract_pdf_text(resp.content)
            else:
                page_text = resp.text
        except requests.exceptions.RequestException as e:
            fetch_error = str(e)
    else:
        fetch_error = "requests package not installed"

    if page_text is None and snapshot:
        page_text = snapshot
        fetch_mode = "snapshot"

    if page_text is None and wayback_fallback:
        page_text = _try_wayback(url, timeout)
        if page_text:
            fetch_mode = "wayback"

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
