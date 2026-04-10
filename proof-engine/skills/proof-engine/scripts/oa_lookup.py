"""
oa_lookup.py — DOI extraction and open-access URL discovery via Unpaywall.

Used by verify_citation() as a fallback when fetch_page() returns fetch_failed
and the citation URL contains a DOI. OA lookup is non-terminal: if the OA
version's text doesn't match the quoted text, the result falls through to
fetch_failed so interactive recovery remains available.
"""

import os
import re

try:
    import requests
except ImportError:
    requests = None


# ---------------------------------------------------------------------------
# DOI extraction
# ---------------------------------------------------------------------------

_DOI_URL_RE = re.compile(r'https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/[^\s]+)')


def extract_doi(url: str, doi: str = None) -> str | None:
    """Extract a DOI from a URL or explicit field.

    Args:
        url: Citation URL (may contain doi.org/10.xxx pattern).
        doi: Explicit DOI from empirical_facts metadata. Takes precedence.

    Returns:
        DOI string (e.g., "10.1234/example") or None.
    """
    if doi:
        return doi
    m = _DOI_URL_RE.match(url)
    if m:
        return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Unpaywall OA lookup
# ---------------------------------------------------------------------------

def lookup_oa_url(doi: str, email: str = None) -> str | None:
    """Query Unpaywall for an open-access URL for the given DOI.

    Args:
        doi: The DOI to look up.
        email: Contact email required by Unpaywall API terms.
            If None, reads from PROOF_ENGINE_UNPAYWALL_EMAIL env var.
            If still None, returns None (API requires email).

    Returns:
        OA URL string, or None if no OA version found or API error.
        Prefers landing page URL over PDF URL.
    """
    if requests is None:
        return None
    if email is None:
        email = os.environ.get("PROOF_ENGINE_UNPAYWALL_EMAIL")
    if not email:
        return None

    api_url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    try:
        resp = requests.get(api_url, timeout=10,
                            headers={"User-Agent": "proof-engine/1.0"})
        resp.raise_for_status()
        data = resp.json()
        best = data.get("best_oa_location")
        if not best:
            return None
        # Prefer landing page (HTML, easier to match quotes) over PDF
        return best.get("url_for_landing_page") or best.get("url_for_pdf")
    except (requests.exceptions.RequestException, ValueError, KeyError):
        return None
