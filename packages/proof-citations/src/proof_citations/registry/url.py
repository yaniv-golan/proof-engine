"""URL fallback — extracts OpenGraph and `<title>` metadata from arbitrary HTML.

This is the lowest-fidelity backend; use it only when an identifier-specific
backend isn't available. Catches the most common case: a publisher landing
page with `<meta property="og:title">`, `<meta property="article:author">`,
`<meta property="article:published_time">`. Falls back to `<title>` if no OG
metadata is present.

Wayback fallback: when the live fetch fails (publisher blocks, Cloudflare bot
challenge, university WAF), retries via `web.archive.org/web/`. Same fallback
chain `verify_citation` uses for quote-on-page verification.
"""

from __future__ import annotations

import re

from proof_citations.registry.base import (
    Author,
    HTTPSession,
    ResolutionError,
    ResolvedRecord,
    now_iso,
)


_OG_TITLE_RE = re.compile(
    r'<meta\s+[^>]*?property=["\']og:title["\'][^>]*?content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
_OG_AUTHOR_RE = re.compile(
    r'<meta\s+[^>]*?property=["\'](?:og:)?article:author["\'][^>]*?content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
_OG_PUB_RE = re.compile(
    r'<meta\s+[^>]*?property=["\']article:published_time["\'][^>]*?content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
_TITLE_RE = re.compile(r"<title>([^<]+)</title>", re.IGNORECASE)


def resolve_url(value: str, *, session: HTTPSession) -> ResolvedRecord:
    """Fetch `value` (or its Wayback archive) and extract OG / <title> metadata."""
    value = (value or "").strip()
    if not value.lower().startswith(("http://", "https://")):
        raise ValueError(f"URL must start with http:// or https://, got {value!r}")

    source_api = "og_extraction"
    html: str
    try:
        resp = session.get(value)
        if resp.status_code != 200:
            raise ResolutionError(
                f"URL returned HTTP {resp.status_code}",
                kind="fetch_failed",
                details={"status": resp.status_code},
            )
        html = resp.text
    except (ResolutionError, Exception) as live_err:
        # Try Wayback Machine. We use the without-timestamp form so Wayback
        # picks the most recent snapshot.
        wb_url = f"https://web.archive.org/web/{value}"
        try:
            resp = session.get(wb_url)
            if resp.status_code != 200:
                raise ResolutionError(
                    f"live and Wayback fetch failed for {value}",
                    kind="fetch_failed",
                ) from live_err if isinstance(live_err, Exception) else None
            html = resp.text
            source_api = "og_extraction_wayback"
        except Exception:
            if isinstance(live_err, ResolutionError):
                raise live_err
            raise ResolutionError(
                f"URL fetch failed (live + wayback): {live_err}",
                kind="fetch_failed",
            ) from live_err

    title_match = _OG_TITLE_RE.search(html) or _TITLE_RE.search(html)
    title_str = title_match.group(1).strip() if title_match else value

    authors = [
        Author.from_full_name(a.strip())
        for a in _OG_AUTHOR_RE.findall(html)
        if a.strip()
    ]

    year = None
    pub = _OG_PUB_RE.search(html)
    if pub:
        m = re.search(r"\b(19|20)\d{2}\b", pub.group(1))
        if m:
            year = int(m.group(0))

    return ResolvedRecord(
        identifier_type="url",
        identifier_value=value,
        canonical_url=value,
        title=title_str,
        authors=authors,
        year=year,
        resolved_at=now_iso(),
        source_api=source_api,
        raw={"html_len": len(html)},
    )


__all__ = ["resolve_url"]
