"""ISBN backend — Open Library API."""

from __future__ import annotations

import re

from proof_citations.registry.base import (
    Author,
    HTTPSession,
    ResolutionError,
    ResolvedRecord,
    now_iso,
)


OPENLIBRARY_URL = "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"


def resolve_isbn(isbn: str, *, session: HTTPSession) -> ResolvedRecord:
    isbn = (isbn or "").strip().replace("-", "").replace(" ", "")
    if not re.match(r"^\d{9}[\dXx]$|^\d{13}$", isbn):
        raise ValueError(f"ISBN must be 10 or 13 digits, got {isbn!r}")

    url = OPENLIBRARY_URL.format(isbn=isbn)
    try:
        resp = session.get(url)
    except Exception as exc:
        raise ResolutionError(f"Open Library fetch failed: {exc}", kind="fetch_failed") from exc

    if resp.status_code != 200:
        raise ResolutionError(f"Open Library HTTP {resp.status_code}", kind="fetch_failed")

    try:
        data = resp.json()
    except ValueError as exc:
        raise ResolutionError(f"Open Library returned non-JSON: {exc}", kind="malformed_response") from exc

    key = f"ISBN:{isbn}"
    entry = data.get(key) or {}
    if not entry:
        raise ResolutionError(f"ISBN {isbn} not in Open Library", kind="not_found")

    title = entry.get("title") or None
    authors = [
        Author.from_full_name(a.get("name", "").strip())
        for a in entry.get("authors", [])
        if a.get("name")
    ]

    year = None
    m = re.search(r"\b(19|20)\d{2}\b", entry.get("publish_date") or "")
    if m:
        year = int(m.group(0))

    publishers = entry.get("publishers") or []
    publisher = publishers[0].get("name") if publishers else None

    return ResolvedRecord(
        identifier_type="isbn",
        identifier_value=isbn,
        canonical_url=f"https://openlibrary.org/isbn/{isbn}",
        title=title,
        authors=authors,
        year=year,
        venue=publisher,
        publisher=publisher,
        publication_type="book",
        resolved_at=now_iso(),
        source_api="openlibrary.org",
        raw={"openlibrary": data},
    )


__all__ = ["resolve_isbn", "OPENLIBRARY_URL"]
