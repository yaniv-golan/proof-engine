"""CNRI Handle backend — hdl.handle.net/api/handles/."""

from __future__ import annotations

from proof_citations.resolvers.base import (
    HTTPSession,
    ResolutionError,
    ResolvedRecord,
    now_iso,
)


HDL_API_URL = "https://hdl.handle.net/api/handles/{value}"


def resolve_handle(value: str, *, session: HTTPSession) -> ResolvedRecord:
    value = (value or "").strip()
    if not value or "/" not in value:
        raise ValueError(f"Handle must contain a '/', got {value!r}")

    url = HDL_API_URL.format(value=value)
    try:
        resp = session.get(url)
    except Exception as exc:
        raise ResolutionError(f"Handle fetch failed: {exc}", kind="fetch_failed") from exc

    if resp.status_code == 404:
        raise ResolutionError(f"Handle {value} not found", kind="not_found")
    if resp.status_code != 200:
        raise ResolutionError(f"Handle HTTP {resp.status_code}", kind="fetch_failed")

    try:
        data = resp.json()
    except ValueError as exc:
        raise ResolutionError(f"Handle returned non-JSON: {exc}", kind="malformed_response") from exc

    return ResolvedRecord(
        identifier_type="handle",
        identifier_value=value,
        canonical_url=f"https://hdl.handle.net/{value}",
        title=f"Handle {value}",
        resolved_at=now_iso(),
        source_api="hdl.handle.net",
        raw={"handle": data},
    )


__all__ = ["resolve_handle", "HDL_API_URL"]
