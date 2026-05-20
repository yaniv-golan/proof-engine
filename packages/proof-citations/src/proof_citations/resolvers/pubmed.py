"""PubMed backend via NCBI E-utilities `esummary`.

The `esummary` JSON response carries every field we need: title, source/journal,
publication date, volume, issue, pages, authors, DOI (via `articleids`).
No HTML scraping, no body-text extraction failures.

Rate limiting: NCBI allows ~3 req/sec unauthenticated, ~10 with an API key in
the `NCBI_API_KEY` environment variable. The shared HTTPSession's retry adapter
handles transient 429s. For higher-volume use, set `NCBI_API_KEY` and call
with a cache to avoid re-fetching.

Reference: https://www.ncbi.nlm.nih.gov/books/NBK25500/
"""

from __future__ import annotations

import os
import re
from typing import Optional

from proof_citations.resolvers.base import (
    Author,
    ResolutionError,
    ResolvedRecord,
    HTTPSession,
    now_iso,
)


ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PUBMED_VIEW_URL = "https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

_PMID_RE = re.compile(r"^\d+$")


def _build_params(pmid: str) -> dict:
    params = {"db": "pubmed", "id": pmid, "retmode": "json", "tool": "proof-citations"}
    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        params["api_key"] = api_key
    contact = os.environ.get("PROOF_CITATIONS_CONTACT")
    if contact:
        params["email"] = contact
    return params


def _parse_year(pubdate: str) -> Optional[int]:
    """PubMed pubdate strings look like '2013 Feb', '2021', '2024 Jan 15'.
    Extract the leading 4-digit year if present."""
    if not pubdate:
        return None
    m = re.match(r"(\d{4})", pubdate.strip())
    return int(m.group(1)) if m else None


def _parse_published_date(pubdate: str) -> Optional[str]:
    """Best-effort ISO-8601 date. '2013 Feb' → '2013-02', '2013 Feb 15' → '2013-02-15',
    '2013' → '2013'. Returns the raw string if it doesn't parse to a recognized shape."""
    if not pubdate:
        return None
    pubdate = pubdate.strip()
    months = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
        "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
    }
    m = re.match(r"(\d{4})(?:\s+(\w{3}))?(?:\s+(\d{1,2}))?", pubdate)
    if not m:
        return pubdate
    year, mon, day = m.groups()
    parts = [year]
    if mon and mon in months:
        parts.append(months[mon])
        if day:
            parts.append(f"{int(day):02d}")
    return "-".join(parts)


def _parse_authors(raw_authors: list) -> list[Author]:
    """E-utilities returns `authors: [{name, authtype, clusterid}, ...]` where
    `name` is 'Anderson CB' style (family + initials). Split conservatively.
    """
    out: list[Author] = []
    for a in raw_authors or []:
        if not isinstance(a, dict):
            continue
        if a.get("authtype") and a["authtype"] != "Author":
            continue  # skip collective authors, editors, etc.
        name = (a.get("name") or "").strip()
        if not name:
            continue
        # 'Anderson CB' — last token is initials; rest is family.
        tokens = name.rsplit(" ", 1)
        if len(tokens) == 2 and re.fullmatch(r"[A-Z]+", tokens[1]):
            family, initials = tokens
            given = " ".join(initials)  # 'CB' → 'C B' so display() reconstructs cleanly
        else:
            family, given = name, ""
        out.append(Author(family=family, given=given, raw=a))
    return out


def _extract_doi(articleids: list) -> Optional[str]:
    for aid in articleids or []:
        if isinstance(aid, dict) and aid.get("idtype") == "doi":
            return (aid.get("value") or "").strip() or None
    return None


def resolve_pmid(pmid: str, *, session: HTTPSession) -> ResolvedRecord:
    """Resolve a PubMed identifier (PMID) to a `ResolvedRecord`.

    Args:
        pmid: numeric PubMed ID as a string. Whitespace and leading/trailing
            punctuation are stripped; non-numeric input raises ValueError.
        session: the polite HTTP session.

    Raises:
        ValueError: pmid is not numeric.
        ResolutionError: E-utilities returned an error, the PMID doesn't exist,
            or the response shape is unexpected.
    """
    pmid = (pmid or "").strip().lstrip("PMID:").strip()
    if not _PMID_RE.match(pmid):
        raise ValueError(f"PMID must be numeric, got {pmid!r}")

    try:
        resp = session.get(ESUMMARY_URL, params=_build_params(pmid))
    except Exception as exc:
        raise ResolutionError(
            f"PubMed fetch failed for PMID {pmid}: {exc}",
            kind="fetch_failed",
            details={"pmid": pmid, "underlying": str(exc)},
        ) from exc

    if resp.status_code == 429:
        raise ResolutionError(
            f"PubMed rate-limited for PMID {pmid} (HTTP 429). "
            "Set NCBI_API_KEY for higher quota.",
            kind="rate_limited",
            details={"pmid": pmid, "status": 429},
        )
    if resp.status_code != 200:
        raise ResolutionError(
            f"PubMed returned HTTP {resp.status_code} for PMID {pmid}",
            kind="fetch_failed",
            details={"pmid": pmid, "status": resp.status_code, "body": resp.text[:200]},
        )

    try:
        payload = resp.json()
    except ValueError as exc:
        raise ResolutionError(
            f"PubMed response for PMID {pmid} was not JSON: {exc}",
            kind="malformed_response",
            details={"pmid": pmid, "body": resp.text[:200]},
        ) from exc

    # E-utilities idiosyncrasy: errors come back as either top-level `error` or
    # per-record `error` inside `result[pmid]`.
    if "error" in payload:
        raise ResolutionError(
            f"PubMed reported error for PMID {pmid}: {payload['error']}",
            kind="not_found",
            details={"pmid": pmid, "error": payload["error"]},
        )

    result = payload.get("result", {})
    record_data = result.get(pmid)
    if record_data is None:
        raise ResolutionError(
            f"PubMed response for PMID {pmid} missing the expected record",
            kind="malformed_response",
            details={"pmid": pmid, "keys": list(result.keys())},
        )
    if "error" in record_data:
        raise ResolutionError(
            f"PubMed reports PMID {pmid} as not found: {record_data['error']}",
            kind="not_found",
            details={"pmid": pmid, "error": record_data["error"]},
        )

    title = (record_data.get("title") or "").rstrip(".") or None
    pubdate = record_data.get("pubdate") or ""
    venue = record_data.get("fulljournalname") or record_data.get("source") or None
    issn = record_data.get("issn") or record_data.get("essn") or None
    doi = _extract_doi(record_data.get("articleids", []))
    pubtype = record_data.get("pubtype") or []
    publication_type = pubtype[0].lower().replace(" ", "-") if pubtype else None

    # Retraction signal — PubMed surfaces this in `pubtype` (e.g.,
    # "Retraction of Publication", "Retracted Publication", "Expression of Concern").
    update_status: Optional[str] = None
    pubtype_lower = [p.lower() for p in pubtype]
    if any("retract" in p for p in pubtype_lower):
        update_status = "retracted"
    elif any("expression of concern" in p for p in pubtype_lower):
        update_status = "expression_of_concern"
    elif any("corrigendum" in p or "erratum" in p for p in pubtype_lower):
        update_status = "corrigendum"

    return ResolvedRecord(
        identifier_type="pmid",
        identifier_value=pmid,
        canonical_url=PUBMED_VIEW_URL.format(pmid=pmid),
        title=title,
        authors=_parse_authors(record_data.get("authors", [])),
        year=_parse_year(pubdate),
        venue=venue,
        publication_type=publication_type,
        published_date=_parse_published_date(pubdate),
        issn=issn or None,
        doi=doi,
        pmid=pmid,
        volume=record_data.get("volume") or None,
        issue=record_data.get("issue") or None,
        pages=record_data.get("pages") or None,
        language=(record_data.get("lang") or [None])[0]
        if isinstance(record_data.get("lang"), list)
        else record_data.get("lang"),
        update_status=update_status,
        resolved_at=now_iso(),
        source_api="eutils.ncbi.nlm.nih.gov",
        raw={"eutils": record_data},
    )


__all__ = ["resolve_pmid", "ESUMMARY_URL", "PUBMED_VIEW_URL"]
