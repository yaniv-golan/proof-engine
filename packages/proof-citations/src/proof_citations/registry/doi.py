"""DOI backend — tries DataCite (datasets, Zenodo) then Crossref (journal articles).

DOIs are issued by multiple registration agencies. DataCite serves data /
software / preprint DOIs (10.5281/zenodo.*, 10.6084/figshare.*, 10.7910/dvn.*,
etc.); Crossref serves the vast majority of scholarly-article DOIs. We try
DataCite first because its API explicitly returns 404 for non-DataCite DOIs,
which makes the fallback to Crossref cheap. The reverse (Crossref-first)
would return success for many DOIs that are actually registered with both
registrars but where DataCite carries richer dataset metadata.
"""

from __future__ import annotations

import time
from typing import Optional

from proof_citations.registry.base import (
    Author,
    HTTPSession,
    ResolutionError,
    ResolvedRecord,
    now_iso,
)

DATACITE_URL = "https://api.datacite.org/dois/{doi}"
CROSSREF_URL = "https://api.crossref.org/works/{doi}"


def resolve_doi(doi: str, *, session: HTTPSession) -> ResolvedRecord:
    """Resolve a DOI by trying DataCite first, then Crossref on 404."""
    doi = (doi or "").strip().lstrip("doi:").strip()
    if not doi or not doi.lower().startswith("10."):
        raise ValueError(f"DOI must start with '10.', got {doi!r}")

    # Try DataCite
    try:
        return _resolve_via_datacite(doi, session=session)
    except ResolutionError as e:
        if e.kind != "not_found":
            # Hard failure on DataCite — propagate (don't accidentally hide
            # network errors as Crossref attempts)
            raise

    # Fallback to Crossref
    return _resolve_via_crossref(doi, session=session)


def _resolve_via_datacite(doi: str, *, session: HTTPSession) -> ResolvedRecord:
    url = DATACITE_URL.format(doi=doi)
    try:
        resp = session.get(url)
    except Exception as exc:
        raise ResolutionError(f"DataCite fetch failed: {exc}", kind="fetch_failed") from exc

    if resp.status_code == 404:
        raise ResolutionError(f"DOI {doi} not in DataCite", kind="not_found")
    if resp.status_code == 429:
        raise ResolutionError(f"DataCite rate-limited for {doi}", kind="rate_limited")
    if resp.status_code != 200:
        raise ResolutionError(
            f"DataCite HTTP {resp.status_code} for {doi}",
            kind="fetch_failed",
            details={"status": resp.status_code},
        )

    try:
        data = resp.json()
    except ValueError as exc:
        raise ResolutionError(f"DataCite returned non-JSON for {doi}", kind="malformed_response") from exc

    attrs = data.get("data", {}).get("attributes", {}) or {}
    titles = attrs.get("titles") or [{}]
    title = (titles[0].get("title") or "").strip() or None
    year = attrs.get("publicationYear")

    authors: list[Author] = []
    for c in attrs.get("creators") or []:
        if not isinstance(c, dict):
            continue
        given = (c.get("givenName") or "").strip()
        family = (c.get("familyName") or "").strip()
        if not (given or family) and c.get("name"):
            authors.append(Author.from_full_name(c["name"].strip(), raw=c))
        else:
            authors.append(Author(family=family, given=given, raw=c))

    # DataCite uses `types.resourceTypeGeneral` for high-level type
    types = attrs.get("types") or {}
    pubtype = (types.get("resourceTypeGeneral") or types.get("resourceType") or "").lower() or None

    return ResolvedRecord(
        identifier_type="doi",
        identifier_value=doi,
        canonical_url=f"https://doi.org/{doi}",
        title=title,
        authors=authors,
        year=int(year) if year else None,
        venue=attrs.get("publisher"),
        publisher=attrs.get("publisher"),
        publication_type=pubtype,
        published_date=attrs.get("registered") or None,
        doi=doi,
        resolved_at=now_iso(),
        source_api="api.datacite.org",
        raw={"datacite": data},
    )


def _resolve_via_crossref(doi: str, *, session: HTTPSession) -> ResolvedRecord:
    url = CROSSREF_URL.format(doi=doi)
    try:
        resp = session.get(url)
    except Exception as exc:
        raise ResolutionError(f"Crossref fetch failed: {exc}", kind="fetch_failed") from exc

    if resp.status_code == 404:
        raise ResolutionError(f"DOI {doi} not found in Crossref either", kind="not_found")
    if resp.status_code == 429:
        raise ResolutionError(f"Crossref rate-limited for {doi}", kind="rate_limited")
    if resp.status_code != 200:
        raise ResolutionError(
            f"Crossref HTTP {resp.status_code} for {doi}",
            kind="fetch_failed",
            details={"status": resp.status_code},
        )

    try:
        data = resp.json()
    except ValueError as exc:
        raise ResolutionError(f"Crossref returned non-JSON for {doi}", kind="malformed_response") from exc

    msg = data.get("message") or {}
    title = (msg.get("title") or [""])[0] or None

    # published-print preferred; fall back to published-online or issued
    date_block = msg.get("published-print") or msg.get("published-online") or msg.get("issued") or {}
    date_parts = date_block.get("date-parts") or [[None]]
    year = date_parts[0][0] if date_parts and date_parts[0] else None
    month = date_parts[0][1] if date_parts and len(date_parts[0]) >= 2 else None
    day = date_parts[0][2] if date_parts and len(date_parts[0]) >= 3 else None
    published_date = None
    if year:
        parts = [str(year)]
        if month:
            parts.append(f"{int(month):02d}")
            if day:
                parts.append(f"{int(day):02d}")
        published_date = "-".join(parts)

    authors: list[Author] = []
    for a in msg.get("author") or []:
        if not isinstance(a, dict):
            continue
        family = (a.get("family") or "").strip()
        given = (a.get("given") or "").strip()
        orcid = a.get("ORCID")
        authors.append(Author(family=family, given=given, orcid=orcid, raw=a))

    container = (msg.get("container-title") or [])
    venue = container[0] if container else None
    issn_list = msg.get("ISSN") or []
    issn = issn_list[0] if issn_list else None

    pages = msg.get("page")
    volume = msg.get("volume")
    issue = msg.get("issue")
    publication_type = msg.get("type") or None

    # Crossref's update-to carries retraction / corrigendum metadata
    update_status = None
    update_refs: list[str] = []
    for upd in msg.get("update-to") or []:
        ulabel = (upd.get("label") or "").lower()
        if "retraction" in ulabel:
            update_status = "retracted"
        elif "expression of concern" in ulabel:
            update_status = update_status or "expression_of_concern"
        elif "correction" in ulabel or "erratum" in ulabel or "corrigendum" in ulabel:
            update_status = update_status or "corrigendum"
        if upd.get("DOI"):
            update_refs.append(upd["DOI"])

    return ResolvedRecord(
        identifier_type="doi",
        identifier_value=doi,
        canonical_url=f"https://doi.org/{doi}",
        title=title,
        authors=authors,
        year=int(year) if year else None,
        venue=venue,
        publisher=msg.get("publisher") or None,
        publication_type=publication_type,
        published_date=published_date,
        issn=issn,
        doi=doi,
        volume=volume,
        issue=issue,
        pages=pages,
        update_status=update_status,
        update_refs=update_refs,
        resolved_at=now_iso(),
        source_api="api.crossref.org",
        raw={"crossref": data},
    )


__all__ = ["resolve_doi", "DATACITE_URL", "CROSSREF_URL"]
