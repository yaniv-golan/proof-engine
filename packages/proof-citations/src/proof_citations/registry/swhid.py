"""Software Heritage backend — archive.softwareheritage.org/api/1/resolve/."""

from __future__ import annotations

import re

from proof_citations.registry.base import (
    HTTPSession,
    ResolutionError,
    ResolvedRecord,
    now_iso,
)


SWH_RESOLVE_URL = "https://archive.softwareheritage.org/api/1/resolve/{swhid}/"
SWH_VIEW_URL = "https://archive.softwareheritage.org/{swhid}"

_SWHID_RE = re.compile(r"^swh:1:[a-z]{3}:[0-9a-f]{40}(?:;[^/\s]*)?$")


def resolve_swhid(swhid: str, *, session: HTTPSession) -> ResolvedRecord:
    swhid = (swhid or "").strip()
    if not _SWHID_RE.match(swhid):
        raise ValueError(f"SWHID must match swh:1:type:hex40, got {swhid!r}")

    url = SWH_RESOLVE_URL.format(swhid=swhid)
    try:
        resp = session.get(url)
    except Exception as exc:
        raise ResolutionError(f"Software Heritage fetch failed: {exc}", kind="fetch_failed") from exc

    if resp.status_code == 404:
        raise ResolutionError(f"SWHID {swhid} not found", kind="not_found")
    if resp.status_code != 200:
        raise ResolutionError(f"SWH HTTP {resp.status_code}", kind="fetch_failed")

    try:
        data = resp.json()
    except ValueError as exc:
        raise ResolutionError(f"SWH returned non-JSON: {exc}", kind="malformed_response") from exc

    origin = data.get("origin_url") or ""
    title = origin or f"SWHID {swhid}"

    return ResolvedRecord(
        identifier_type="swhid",
        identifier_value=swhid,
        canonical_url=SWH_VIEW_URL.format(swhid=swhid),
        title=title,
        year=None,
        venue="Software Heritage Archive",
        publication_type="software",
        resolved_at=now_iso(),
        source_api="archive.softwareheritage.org/api/1/resolve",
        raw={"swh": data},
    )


__all__ = ["resolve_swhid", "SWH_RESOLVE_URL"]
