"""Extract typed identifiers from URLs and free-text strings.

Public API:
    identify(url_or_string) -> tuple[str, str] | None

Recognized identifier types:
    pmid    — PubMed ID (pubmed.ncbi.nlm.nih.gov/{pmid}/, ncbi.nlm.nih.gov/pubmed/{pmid})
    pmc     — PubMed Central ID
    doi     — DOI (doi.org/{doi}, dx.doi.org/{doi}, iopscience.iop.org/article/{doi})
    arxiv   — arXiv ID (arxiv.org/abs/{id}, arxiv.org/html/{id}, ar5iv.labs.arxiv.org/html/{id})
    swhid   — Software Heritage ID
    url     — fallback for URLs that don't match any structured identifier

Returns None for empty input. Always returns a `(type, value)` tuple
otherwise — `("url", url)` for unrecognized URLs so callers can still pass
the result to a URL-fallback backend.
"""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import unquote


# PubMed: pubmed.ncbi.nlm.nih.gov/{pmid} or pubmed.ncbi.nlm.nih.gov/{pmid}/
# Also the legacy ncbi.nlm.nih.gov/pubmed/{pmid} URL shape.
_PMID_URL_RE = re.compile(
    r"^https?://(?:www\.)?(?:pubmed\.ncbi\.nlm\.nih\.gov|ncbi\.nlm\.nih\.gov/pubmed)/(\d+)/?(?:\?.*)?$"
)

# PMC ID: pmc.ncbi.nlm.nih.gov/articles/PMC1234567 or ncbi.nlm.nih.gov/pmc/articles/PMC1234567
_PMC_URL_RE = re.compile(
    r"^https?://(?:www\.)?(?:pmc\.ncbi\.nlm\.nih\.gov/articles|ncbi\.nlm\.nih\.gov/pmc/articles)/(PMC\d+)/?(?:\?.*)?$"
)

_ARXIV_URL_RE = re.compile(
    r"^https?://(?:www\.)?(?:ar5iv\.labs\.)?arxiv\.org/(?:abs|html|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?/?(?:\?.*)?$"
)

_DOI_URL_RE = re.compile(
    r"^https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/\S+?)/?$"
)

_IOP_DOI_URL_RE = re.compile(
    r"^https?://iopscience\.iop\.org/article/(10\.\d{4,9}/\S+?)/?$"
)

_SWH_URL_RE = re.compile(
    r"^https?://archive\.softwareheritage\.org/(swh:1:[a-z]{3}:[0-9a-f]{40}(?:;[^/\s]*)?)/?$"
)

# Bare-identifier shapes for non-URL inputs
_BARE_PMID_RE = re.compile(r"^(?:PMID:)?\s*(\d+)$", re.IGNORECASE)
_BARE_PMC_RE = re.compile(r"^(PMC\d+)$", re.IGNORECASE)
_BARE_DOI_RE = re.compile(r"^(?:doi:)?\s*(10\.\d{4,9}/\S+)$", re.IGNORECASE)
_BARE_ARXIV_RE = re.compile(r"^(?:arxiv:)?\s*(\d{4}\.\d{4,5})(?:v\d+)?$", re.IGNORECASE)


def identify(url_or_string: Optional[str]) -> Optional[tuple[str, str]]:
    """Extract a `(type, value)` identifier.

    Accepts a URL or a bare identifier string. Returns None for empty input,
    `("url", original)` for unrecognized URLs so callers can route to a URL
    fallback backend.

    Examples:
        identify("https://pubmed.ncbi.nlm.nih.gov/23260561/") -> ("pmid", "23260561")
        identify("https://doi.org/10.1016/j.x.2021.001") -> ("doi", "10.1016/j.x.2021.001")
        identify("arxiv:2106.09685") -> ("arxiv", "2106.09685")
        identify("PMID: 12345") -> ("pmid", "12345")
        identify("10.3322/caac.21660") -> ("doi", "10.3322/caac.21660")
        identify("https://example.com/some/page") -> ("url", "https://example.com/some/page")
        identify(None) -> None
        identify("") -> None
    """
    if not url_or_string:
        return None
    s = url_or_string.strip()
    if not s:
        return None

    # URL shapes
    if s.lower().startswith(("http://", "https://")):
        for pattern, ident_type in (
            (_PMID_URL_RE, "pmid"),
            (_PMC_URL_RE, "pmc"),
            (_ARXIV_URL_RE, "arxiv"),
            (_DOI_URL_RE, "doi"),
            (_IOP_DOI_URL_RE, "doi"),
            (_SWH_URL_RE, "swhid"),
        ):
            m = pattern.match(s)
            if m:
                return (ident_type, unquote(m.group(1)))
        return ("url", s)

    # Bare-identifier shapes
    m = _BARE_PMID_RE.match(s)
    if m:
        return ("pmid", m.group(1))
    m = _BARE_PMC_RE.match(s)
    if m:
        return ("pmc", m.group(1).upper())
    m = _BARE_DOI_RE.match(s)
    if m:
        return ("doi", m.group(1))
    m = _BARE_ARXIV_RE.match(s)
    if m:
        return ("arxiv", m.group(1))

    # Strings that look like typed identifiers but didn't match a regex
    if ":" in s and s.lower().startswith(("pmid:", "pmc:", "doi:", "arxiv:", "swhid:")):
        type_name, _, value = s.partition(":")
        return (type_name.lower(), value.strip())

    return None


__all__ = ["identify"]
