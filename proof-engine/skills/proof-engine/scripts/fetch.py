"""
fetch.py — HTTP fetching with fallback chain for proof-engine.

Handles: live fetch -> snapshot -> Wayback Machine fallback.
Also handles PDF text extraction and GitHub raw README fallback.

Extracted from verify_citations.py to separate transport from matching logic.
"""

import re

try:
    import requests
except ImportError:
    requests = None


# ---------------------------------------------------------------------------
# PDF text extraction
# ---------------------------------------------------------------------------

def extract_pdf_text(content: bytes) -> str | None:
    """Extract text from PDF bytes. Tries pdfplumber first, then PyPDF2.

    Returns None if no PDF library is available or if extraction fails.
    """
    try:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        pass
    except Exception:
        pass
    try:
        import PyPDF2
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        pass
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Wayback Machine fallback
# ---------------------------------------------------------------------------

def try_wayback(url: str, timeout: int = 15) -> str | None:
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
# GitHub raw README fallback
# ---------------------------------------------------------------------------

_GITHUB_REPO_RE = re.compile(r'^https?://github\.com/([^/]+)/([^/]+)/?$')


_README_CANDIDATES = ["README.md", "README.rst", "README.txt", "README", "readme.md"]


def try_github_raw(url: str, timeout: int = 15) -> str | None:
    """Try fetching a GitHub repo's raw README. Returns text or None.

    Only applies to bare repo URLs (github.com/owner/repo). URLs with
    file paths are not rewritten. GitHub renders repo pages via JavaScript,
    so requests.get() gets a React shell instead of the README content.

    Tries multiple README filenames (README.md, README.rst, README.txt,
    README, readme.md) since repos vary in naming convention.
    """
    if requests is None:
        return None
    m = _GITHUB_REPO_RE.match(url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    for readme_name in _README_CANDIDATES:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{readme_name}"
        try:
            resp = requests.get(raw_url, timeout=timeout,
                                headers={"User-Agent": "proof-engine/1.0"},
                                allow_redirects=True)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException:
            continue
    return None


# ---------------------------------------------------------------------------
# Page fetching with fallback chain
# ---------------------------------------------------------------------------

def fetch_page(url: str, timeout: int = 15, snapshot: str = None,
               wayback_fallback: bool = False,
               skip_live_fetch: bool = False) -> tuple[str | None, str, str | None]:
    """Fetch page text using the standard fallback chain.

    Args:
        url: The URL to fetch.
        timeout: Fetch timeout in seconds.
        snapshot: Pre-fetched page text for offline verification.
        wayback_fallback: If True, try Wayback Machine as last resort.
        skip_live_fetch: If True, skip live HTTP fetch (e.g., when requests
            is unavailable in the calling module).

    Returns:
        (page_text, fetch_mode, error_message)
        - page_text: The page text, or None if all methods failed
        - fetch_mode: "live", "snapshot", "wayback", "github_raw", or "fetch_failed"
        - error_message: Error description if failed, else None
    """
    # --- 1. Try live fetch ---
    fetch_error_msg = None
    if requests is not None and not skip_live_fetch:
        try:
            resp = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "proof-engine/1.0"},
                allow_redirects=True,
            )
            resp.raise_for_status()

            content_type = resp.headers.get("Content-Type", "")
            is_pdf = "application/pdf" in content_type or url.lower().endswith(".pdf")

            if is_pdf:
                pdf_text = extract_pdf_text(resp.content)
                if pdf_text is None:
                    fetch_error_msg = "PDF detected but no extraction library available (pip install pdfplumber)"
                else:
                    return pdf_text, "live", None
            else:
                page_text = resp.text
                # --- 1.5. GitHub raw README fallback ---
                # Only try if live fetch returned an empty/JS-shell page (< 500 chars of
                # visible text after tag stripping) for a bare GitHub repo URL.
                # This preserves quotes about repo metadata that appears on the rendered
                # github.com page, falling back to raw README only when the live page
                # didn't contain useful content.
                if len(re.sub(r'<[^>]+>', '', page_text).strip()) < 500:
                    github_text = try_github_raw(url, timeout)
                    if github_text is not None:
                        return github_text, "github_raw", None
                return page_text, "live", None

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

    # --- 1.5b. GitHub raw README fallback (when live fetch failed entirely) ---
    if 'github.com' in url:
        github_text = try_github_raw(url, timeout)
        if github_text is not None:
            return github_text, "github_raw", None

    # --- 2. Try snapshot fallback ---
    if snapshot:
        return snapshot, "snapshot", None

    # --- 3. Try Wayback Machine ---
    if wayback_fallback:
        wayback_text = try_wayback(url, timeout)
        if wayback_text is not None:
            return wayback_text, "wayback", None

    # --- 4. All methods exhausted ---
    return None, "fetch_failed", fetch_error_msg
