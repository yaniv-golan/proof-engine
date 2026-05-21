"""
fetch.py — HTTP fetching with fallback chain for proof-engine.

Handles: live fetch -> snapshot -> Wayback Machine fallback.
Also handles PDF text extraction and GitHub raw README fallback.

Extracted from verify_citations.py to separate transport from matching logic.
"""

import os
import re

try:
    import requests
except ImportError:
    requests = None


# ---------------------------------------------------------------------------
# Anti-bot / block-page detection
# ---------------------------------------------------------------------------

# Many anti-bot middlewares respond HTTP 200 with a JS challenge / CAPTCHA
# page instead of the requested article. Without explicit detection, the
# fallback chain treats these as a successful fetch — quote verification
# then fails with "not_found" instead of falling through to snapshot/Wayback.
# Each pattern matches a marker that's distinctive to a particular middleware
# and very unlikely to appear in legitimate content. Conservative on purpose:
# a false positive here would skip a real page in favor of a snapshot, which
# is a survivable failure mode; a false negative is the bug we're fixing.
_BLOCK_PAGE_PATTERNS = [
    # Google reCAPTCHA
    (re.compile(r'\bg-recaptcha\b', re.IGNORECASE), "g-recaptcha"),
    (re.compile(
        r'<script\b[^>]*\bsrc\s*=\s*["\'][^"\']*recaptcha/api\.js',
        re.IGNORECASE), "recaptcha-api.js"),
    # Cloudflare browser challenge
    (re.compile(r'\bcf-browser-verification\b', re.IGNORECASE), "cf-browser-verification"),
    (re.compile(r'\b__cf_chl_tk\b', re.IGNORECASE), "cf-challenge-token"),
    (re.compile(r'\bcf_chl_opt\b', re.IGNORECASE), "cf-challenge-options"),
    (re.compile(
        r'<title[^>]*>\s*Just a moment\.\.\.\s*</title>',
        re.IGNORECASE), "cloudflare-just-a-moment"),
    (re.compile(
        r'<title[^>]*>\s*Attention Required!\s*\|\s*Cloudflare\s*</title>',
        re.IGNORECASE), "cloudflare-attention-required"),
    # Imperva / Incapsula
    (re.compile(r'\b_Incapsula_Resource\b', re.IGNORECASE), "incapsula"),
    (re.compile(r'\bincap_ses_\b', re.IGNORECASE), "incapsula-session"),
    # DataDome
    (re.compile(
        r'<title[^>]*>\s*Pardon Our Interruption\s*</title>',
        re.IGNORECASE), "datadome"),
    # Akamai Bot Manager
    (re.compile(r'\b_abck\b', re.IGNORECASE), "akamai-abck"),
    # Generic
    (re.compile(
        r'<title[^>]*>\s*Access Denied\s*</title>',
        re.IGNORECASE), "access-denied-title"),
]


def looks_like_block_page(text: str) -> str | None:
    """Return the matched marker name if text looks like an anti-bot / CAPTCHA
    challenge page, else None.

    Detection is intentionally conservative: only fires on markers distinctive
    to specific anti-bot middlewares (Google reCAPTCHA, Cloudflare, Imperva,
    DataDome, Akamai). Scans only the first 64KB — challenge pages are tiny
    and the markers always appear in <head> or top of <body>, so this keeps
    the check ~O(1) even on multi-megabyte snapshots.
    """
    if not text:
        return None
    sample = text[:65536]
    for pattern, name in _BLOCK_PAGE_PATTERNS:
        if pattern.search(sample):
            return name
    return None


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
               skip_live_fetch: bool = False,
               snapshot_file: str = None,
               prefer_snapshot: bool = False,
               snapshot_base_dir: str = None) -> tuple[str | None, str, str | None]:
    """Fetch page text using the standard fallback chain.

    Args:
        url: The URL to fetch.
        timeout: Fetch timeout in seconds.
        snapshot: Pre-fetched page text for offline verification (inline).
        wayback_fallback: If True, try Wayback Machine as last resort.
        skip_live_fetch: If True, skip live HTTP fetch entirely (snapshot →
            snapshot_file → wayback only). Set this for domains known to
            serve anti-bot challenges to scripted requests.
        snapshot_file: Path to a local file containing pre-fetched page text.
            Used for paywalled content that cannot be embedded inline. Inline
            snapshot takes precedence over snapshot_file. If relative AND
            snapshot_base_dir is provided, the path is resolved against
            snapshot_base_dir; otherwise it resolves against the CWD.
        prefer_snapshot: If True AND a snapshot (inline or file) is provided,
            use it before attempting a live fetch. Live fetch is still tried
            as a fallback if the snapshot is unusable. Use this for known-
            blocked sources without giving up the live-fetch fallback entirely.
        snapshot_base_dir: Directory to resolve relative snapshot_file paths
            against. Proof templates pass the proof.py directory so the
            published proof.py can be re-run from any CWD without breaking
            paywalled-content lookups. If None or absolute, snapshot_file
            is used as-is (back-compat with callers that pre-resolve paths).

    Returns:
        (page_text, fetch_mode, error_message)
        - page_text: The page text, or None if all methods failed
        - fetch_mode: "live", "snapshot", "wayback", "github_raw", or "fetch_failed"
        - error_message: Error description if failed, else None
    """
    fetch_error_msg = None

    if snapshot_file and snapshot_base_dir and not os.path.isabs(snapshot_file):
        snapshot_file = os.path.join(snapshot_base_dir, snapshot_file)

    # --- 0. Snapshot-first short-circuit ---
    # When the caller has reason to believe the live URL is blocked, taking
    # the snapshot first avoids burning the live-fetch timeout. Falls through
    # to live fetch if the snapshot is empty/missing.
    if prefer_snapshot:
        if snapshot:
            return snapshot, "snapshot", None
        if snapshot_file and os.path.isfile(snapshot_file):
            try:
                with open(snapshot_file, "r", encoding="utf-8") as f:
                    return f.read(), "snapshot", None
            except (OSError, UnicodeDecodeError) as exc:
                fetch_error_msg = (
                    f"prefer_snapshot=True but snapshot_file "
                    f"'{snapshot_file}' could not be read: {exc}"
                )

    # --- 1. Try live fetch ---
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
                # --- 1.4. Anti-bot / CAPTCHA block-page detection ---
                # PMC, Frontiers, Springer, and other publishers serve HTTP 200
                # with a Google reCAPTCHA / Cloudflare challenge page when the
                # request fingerprint looks bot-like. Treat these as fetch
                # failures so the snapshot/Wayback fallback chain still triggers.
                block_marker = looks_like_block_page(page_text)
                if block_marker is not None:
                    fetch_error_msg = (
                        f"live fetch returned an anti-bot challenge page "
                        f"({block_marker}); falling back to snapshot/Wayback"
                    )
                else:
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

    # --- 2b. Try snapshot_file fallback ---
    if snapshot_file:
        if os.path.isfile(snapshot_file):
            try:
                with open(snapshot_file, "r", encoding="utf-8") as f:
                    return f.read(), "snapshot", None
            except (OSError, UnicodeDecodeError) as exc:
                read_err = f"snapshot_file '{snapshot_file}' could not be read: {exc}"
                fetch_error_msg = f"{fetch_error_msg}; {read_err}" if fetch_error_msg else read_err
        else:
            # Record the missing file but continue to next fallback
            snapshot_file_msg = f"snapshot_file '{snapshot_file}' not found (paywalled content stored locally only)"
            if fetch_error_msg:
                fetch_error_msg = f"{fetch_error_msg}; {snapshot_file_msg}"
            else:
                fetch_error_msg = snapshot_file_msg

    # --- 3. Try Wayback Machine ---
    if wayback_fallback:
        wayback_text = try_wayback(url, timeout)
        if wayback_text is not None:
            return wayback_text, "wayback", None

    # --- 4. All methods exhausted ---
    return None, "fetch_failed", fetch_error_msg
