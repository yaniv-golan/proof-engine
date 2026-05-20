"""arXiv backend — fetches the Atom feed from `export.arxiv.org/api/query`."""

from __future__ import annotations

import re
from xml.etree import ElementTree as ET

from proof_citations.registry.base import (
    Author,
    HTTPSession,
    ResolutionError,
    ResolvedRecord,
    now_iso,
)


ARXIV_QUERY_URL = "https://export.arxiv.org/api/query?id_list={value}"
ARXIV_ABS_URL = "https://arxiv.org/abs/{value}"

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def resolve_arxiv(value: str, *, session: HTTPSession) -> ResolvedRecord:
    """Resolve an arXiv ID (e.g. `2106.09685` or `2106.09685v2`).

    `value` may include a version suffix; the version is captured separately
    in the `raw.version` field.
    """
    value = (value or "").strip().lstrip("arxiv:").strip()
    if not re.match(r"^\d{4}\.\d{4,5}(?:v\d+)?$", value) and not re.match(r"^[a-z\-]+/\d{7}$", value):
        raise ValueError(f"arXiv ID must be NNNN.NNNNN[vN] or category/NNNNNNN, got {value!r}")

    url = ARXIV_QUERY_URL.format(value=value)
    try:
        resp = session.get(url)
    except Exception as exc:
        raise ResolutionError(f"arXiv fetch failed: {exc}", kind="fetch_failed") from exc

    if resp.status_code != 200:
        raise ResolutionError(
            f"arXiv returned HTTP {resp.status_code}",
            kind="fetch_failed",
            details={"status": resp.status_code},
        )

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as exc:
        raise ResolutionError(f"arXiv response not parseable XML: {exc}", kind="malformed_response") from exc

    entry = root.find("atom:entry", _NS)
    if entry is None:
        raise ResolutionError(f"arxiv:{value} not found (no entry in Atom feed)", kind="not_found")

    title = (entry.findtext("atom:title", default="", namespaces=_NS) or "").strip() or None
    published = entry.findtext("atom:published", default="", namespaces=_NS) or ""
    year = int(published[:4]) if published[:4].isdigit() else None
    published_date = published[:10] if len(published) >= 10 else None

    authors: list[Author] = []
    for a in entry.findall("atom:author", _NS):
        name = (a.findtext("atom:name", default="", namespaces=_NS) or "").strip()
        if name:
            authors.append(Author.from_full_name(name))

    # arXiv DOI cross-reference, if assigned
    arxiv_doi = entry.findtext("arxiv:doi", namespaces=_NS) or None

    id_url = entry.findtext("atom:id", default="", namespaces=_NS) or ""
    version = None
    m = re.search(r"v(\d+)$", id_url)
    if m:
        version = f"v{m.group(1)}"

    primary_cat = entry.find("arxiv:primary_category", _NS)
    publication_type = "preprint"
    if primary_cat is not None:
        publication_type = f"preprint-{primary_cat.get('term', 'unknown')}"

    return ResolvedRecord(
        identifier_type="arxiv",
        identifier_value=value,
        canonical_url=ARXIV_ABS_URL.format(value=value),
        title=title,
        authors=authors,
        year=year,
        venue="arXiv",
        publication_type=publication_type,
        published_date=published_date,
        doi=arxiv_doi,
        arxiv_id=value,
        resolved_at=now_iso(),
        source_api="export.arxiv.org/api/query",
        raw={"atom_feed_len": len(resp.text), "version": version},
    )


__all__ = ["resolve_arxiv", "ARXIV_QUERY_URL", "ARXIV_ABS_URL"]
