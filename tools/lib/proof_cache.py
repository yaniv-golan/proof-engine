"""Per-proof cache of resolved-identifier metadata.

Site-specific module owning two concerns the pip-installable `proof_citations`
package deliberately does NOT impose:

1. The shape of the on-disk cache (`depends_on_resolved.json` next to each
   proof) and its legacy `ResolvedReference` dataclass with `authors: list[str]`.
   132 committed cache files use this shape; 9 site callers
   (`cite_expander`, `prose_reference_scan`, `proof-site.py`, etc.) operate on
   `authors[0]` as a string. Preserving the shape keeps both populations
   working without migration.
2. Read/write semantics tailored to publish-pipeline gates (`collect_identifiers`
   walks `meta.yaml depends_on` plus `proof.json evidence`, both of which are
   conventions of THIS repo, not generic capabilities).

This module is the glue: it consumes `proof_citations.registry` for the actual
identifier resolution, translates the new `ResolvedRecord` back to the legacy
`ResolvedReference` shape via `_record_to_reference()`, and persists the
result.

Renamed from `tools/lib/reference_resolver.py` in v1.38.0 (the registry
layer is in `proof_citations`; what stays here is *cache*, not *resolver*).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import unquote

# The pip package owns identifier extraction and registry backends now.
from proof_citations import identify as _pc_identify
from proof_citations import resolve as _pc_resolve
from proof_citations.registry.base import (
    Author,
    ResolutionError,
    ResolvedRecord,
    HTTPSession,
    get_default_session,
)


def identifier_from_url(url: Optional[str]) -> Optional[tuple[str, str]]:
    """Deterministically extract a (type, value) identifier from a URL.

    Backwards-compat alias for `proof_citations.identify`. Site callers that
    used the legacy return shape continue to work: `("url", url)` is still
    returned for unrecognized URLs.
    """
    return _pc_identify(url)


@dataclass
class ResolvedReference:
    """Site-specific cache record.

    Legacy `authors: list[str]` shape preserved for compatibility with the
    132 committed `depends_on_resolved.json` files and the 9 callers in
    `tools/lib/` (cite_expander, prose_reference_scan) that operate on
    `authors[0]` as a string.

    For new code, prefer `proof_citations.ResolvedRecord` which has
    structured `Author` records, cross-reference identifiers, and richer
    update-status / publication-type fields.
    """
    identifier_type: str
    identifier_value: str
    canonical_url: str
    title: str
    authors: list[str]
    year: Optional[int]
    venue: Optional[str]
    version: Optional[str]
    resolved_at: str
    source_api: str
    raw: dict = field(default_factory=dict)

    def cache_key(self) -> str:
        return f"{self.identifier_type}:{self.identifier_value}"


_CACHE_FILENAME = "depends_on_resolved.json"


def _author_to_string(a) -> str:
    """Convert an `Author` (or string fallback) to the legacy `list[str]` shape.

    Crossref / DataCite gave 'Given Family' historically; preserve that.
    Single-name authors round-trip cleanly.
    """
    if isinstance(a, Author):
        if a.given and a.family:
            return f"{a.given} {a.family}".strip()
        return a.family or a.given or ""
    if isinstance(a, str):
        return a
    return str(a)


def _record_to_reference(record: ResolvedRecord) -> ResolvedReference:
    """Translate a v1.35.0+ `ResolvedRecord` into a legacy `ResolvedReference`.

    Used to keep site callers and committed caches working unchanged while
    the underlying resolution work is shared with the pip package.
    """
    # The legacy `version` field maps loosely; arXiv stores it in `raw.version`.
    version = None
    if record.identifier_type == "arxiv":
        version = (record.raw or {}).get("version")

    # Legacy `venue` for arXiv was "arXiv preprint" — preserve that.
    venue = record.venue
    if record.identifier_type == "arxiv":
        venue = "arXiv preprint"
    # DataCite legacy populated `venue` from `publisher`; the new record
    # exposes both — fall back to publisher if venue is empty.
    if not venue and record.publisher:
        venue = record.publisher

    return ResolvedReference(
        identifier_type=record.identifier_type,
        identifier_value=record.identifier_value,
        canonical_url=record.canonical_url,
        title=record.title or "",
        authors=[_author_to_string(a) for a in record.authors],
        year=record.year,
        venue=venue,
        version=version,
        resolved_at=record.resolved_at,
        source_api=record.source_api,
        raw=record.raw or {},
    )


def _resolve_one(ident_type: str, value: str, *, http=None) -> ResolvedReference:
    """Call the appropriate `proof_citations.registry` backend, translate."""
    session: Optional[HTTPSession]
    if http is None:
        session = get_default_session()
    else:
        # Legacy callers might pass a `requests` module or a custom session;
        # we no longer route those through the pip package's polite session.
        # For the rare custom-http case, fall through to the default session.
        # (No existing site caller passes a non-default http; the parameter
        # is preserved for API compatibility.)
        session = get_default_session()

    try:
        record = _pc_resolve((ident_type, value), session=session)
    except ResolutionError as e:
        # Translate to a legacy exception shape the site callers may handle.
        if e.kind == "not_found":
            raise LookupError(f"{ident_type}:{value} not found") from e
        raise RuntimeError(str(e)) from e
    except ValueError:
        raise

    return _record_to_reference(record)


# Per-backend wrappers kept for any caller that imports them by name.
def _resolve_arxiv(value: str, http=None) -> ResolvedReference:
    return _resolve_one("arxiv", value, http=http)


def _resolve_doi(value: str, http=None) -> ResolvedReference:
    return _resolve_one("doi", value, http=http)


def _resolve_swhid(value: str, http=None) -> ResolvedReference:
    return _resolve_one("swhid", value, http=http)


def _resolve_handle(value: str, http=None) -> ResolvedReference:
    return _resolve_one("handle", value, http=http)


def _resolve_isbn(value: str, http=None) -> ResolvedReference:
    return _resolve_one("isbn", value, http=http)


def _resolve_url(value: str, http=None) -> ResolvedReference:
    return _resolve_one("url", value, http=http)


_BACKENDS = {
    "arxiv": _resolve_arxiv,
    "doi": _resolve_doi,
    "swhid": _resolve_swhid,
    "handle": _resolve_handle,
    "isbn": _resolve_isbn,
    "url": _resolve_url,
}


def collect_identifiers(proof_dir: Path) -> list[tuple[str, str]]:
    """Collect every (type, value) identifier this proof declares.

    Sources: `meta.yaml depends_on[*].identifiers` (excluding `slug`) +
    `proof.json evidence[*].source.url` passed through `identifier_from_url`.
    Deduplicated; order preserved.

    Stays site-specific: it reads the proof's schema (meta.yaml + proof.json),
    which is a convention of THIS repo, not a generic capability.
    """
    import yaml
    proof_dir = Path(proof_dir)
    seen: list[tuple[str, str]] = []

    meta_path = proof_dir / "meta.yaml"
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text()) or {}
        for entry in meta.get("depends_on") or []:
            for ident in entry.get("identifiers") or []:
                t, v = ident.get("type"), ident.get("value")
                if t and v and t != "slug":
                    pair = (t, str(v))
                    if pair not in seen:
                        seen.append(pair)

    proof_json = proof_dir / "proof.json"
    if proof_json.exists():
        data = json.loads(proof_json.read_text())
        evidence = data.get("evidence") or {}
        if isinstance(evidence, dict):
            iterable = evidence.values()
        elif isinstance(evidence, list):
            iterable = evidence
        else:
            iterable = []
        for ev in iterable:
            url = ((ev or {}).get("source") or {}).get("url")
            pair = identifier_from_url(url)
            if pair and pair not in seen:
                seen.append(pair)

    return seen


def resolve(
    ident_type: str,
    value: str,
    *,
    refresh: bool = False,
    cache_dir: Optional[Path] = None,
    http=None,
) -> ResolvedReference:
    """Resolve one identifier.

    refresh=True -> re-fetch from registry, rewrite cache.
    refresh=False -> must find in cache; missing entry raises KeyError.
    """
    key = f"{ident_type}:{value}"
    if cache_dir is not None and not refresh:
        cache = load_cache(cache_dir)
        if key in cache:
            return cache[key]
        raise KeyError(
            f"no resolved metadata for {key}; run proof-site.py resolve-deps --refresh"
        )
    backend = _BACKENDS.get(ident_type)
    if backend is None:
        raise ValueError(f"no resolver backend for type: {ident_type}")
    return backend(value, http=http)


def load_cache(proof_dir: Path) -> dict[str, ResolvedReference]:
    path = Path(proof_dir) / _CACHE_FILENAME
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    out: dict[str, ResolvedReference] = {}
    for key, payload in data.items():
        # Forward-compat: silently drop unknown keys so newer caches written
        # by future code don't break older readers.
        known = {f for f in ResolvedReference.__dataclass_fields__}
        filtered = {k: v for k, v in payload.items() if k in known}
        out[key] = ResolvedReference(**filtered)
    return out


def save_cache(proof_dir: Path, cache: dict[str, ResolvedReference]) -> None:
    path = Path(proof_dir) / _CACHE_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {k: asdict(v) for k, v in cache.items()}
    path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False) + "\n")
