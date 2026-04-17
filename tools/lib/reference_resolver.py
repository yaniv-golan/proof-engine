"""Resolver — identifier → canonical metadata, per-proof JSON cache."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, unquote
from xml.etree import ElementTree as ET

import requests


_ARXIV_URL_RE = re.compile(
    r"^https?://(?:www\.)?(?:ar5iv\.labs\.)?arxiv\.org/(?:abs|html)/(\d{4}\.\d{4,5})(?:v\d+)?/?$"
)
_DOI_URL_RE = re.compile(r"^https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/\S+?)/?$")
_IOP_DOI_URL_RE = re.compile(r"^https?://iopscience\.iop\.org/article/(10\.\d{4,9}/\S+?)/?$")
_SWH_URL_RE = re.compile(r"^https?://archive\.softwareheritage\.org/(swh:1:[a-z]{3}:[0-9a-f]{40}(?:;[^/\s]*)?)/?$")


def identifier_from_url(url: Optional[str]) -> Optional[tuple[str, str]]:
    """Deterministically extract a (type, value) identifier from a URL.

    Returns None for empty/None input. Returns ("url", url) for URLs with no
    structured identifier shape.
    """
    if not url:
        return None
    url = url.strip()
    m = _ARXIV_URL_RE.match(url)
    if m:
        return ("arxiv", m.group(1))
    m = _DOI_URL_RE.match(url)
    if m:
        return ("doi", unquote(m.group(1)))
    m = _IOP_DOI_URL_RE.match(url)
    if m:
        return ("doi", unquote(m.group(1)))
    m = _SWH_URL_RE.match(url)
    if m:
        return ("swhid", m.group(1))
    return ("url", url)


@dataclass
class ResolvedReference:
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


_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
_CACHE_FILENAME = "depends_on_resolved.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch_with_retry(http, url: str, *, attempts: int = 3, base_delay: float = 1.0, headers: Optional[dict] = None):
    last_err = None
    for n in range(attempts):
        try:
            resp = http.get(url, timeout=20, headers=headers or {})
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            if status == 404:
                raise  # do not retry — caller handles fallback
            last_err = e
        except Exception as e:
            last_err = e
        if n < attempts - 1:
            time.sleep(base_delay * (2 ** n))
    raise RuntimeError(f"fetch failed after {attempts} attempts: {url}: {last_err}")


def _resolve_arxiv(value: str, http=None) -> ResolvedReference:
    http = http or requests
    url = f"https://export.arxiv.org/api/query?id_list={value}"
    resp = _fetch_with_retry(http, url)
    root = ET.fromstring(resp.text)
    entry = root.find("atom:entry", _ATOM_NS)
    if entry is None:
        raise LookupError(f"arxiv:{value} not found")
    title = (entry.findtext("atom:title", default="", namespaces=_ATOM_NS) or "").strip()
    published = entry.findtext("atom:published", default="", namespaces=_ATOM_NS) or ""
    year = int(published[:4]) if published[:4].isdigit() else None
    authors = [
        (a.findtext("atom:name", default="", namespaces=_ATOM_NS) or "").strip()
        for a in entry.findall("atom:author", _ATOM_NS)
    ]
    id_url = entry.findtext("atom:id", default="", namespaces=_ATOM_NS) or ""
    version = None
    m = re.search(r"v(\d+)$", id_url)
    if m:
        version = f"v{m.group(1)}"
    return ResolvedReference(
        identifier_type="arxiv",
        identifier_value=value,
        canonical_url=f"https://arxiv.org/abs/{value}",
        title=title,
        authors=authors,
        year=year,
        venue="arXiv preprint",
        version=version,
        resolved_at=_now_iso(),
        source_api="export.arxiv.org/api/query",
        raw={"atom_feed": resp.text},
    )


def _resolve_doi(value: str, http=None) -> ResolvedReference:
    http = http or requests
    datacite_url = f"https://api.datacite.org/dois/{value}"
    try:
        resp = _fetch_with_retry(http, datacite_url)
    except requests.exceptions.HTTPError as e:
        if getattr(e.response, "status_code", None) == 404:
            return _resolve_doi_crossref(value, http)
        raise
    data = resp.json()
    attrs = data.get("data", {}).get("attributes", {}) or {}
    titles = attrs.get("titles") or [{}]
    title = (titles[0].get("title") or "").strip()
    year = attrs.get("publicationYear")
    creators = attrs.get("creators") or []
    authors = []
    for c in creators:
        given = (c.get("givenName") or "").strip()
        family = (c.get("familyName") or "").strip()
        if given and family:
            authors.append(f"{given} {family}")
        elif family:
            authors.append(family)
        elif c.get("name"):
            authors.append(c["name"].strip())
    return ResolvedReference(
        identifier_type="doi",
        identifier_value=value,
        canonical_url=f"https://doi.org/{value}",
        title=title,
        authors=authors,
        year=int(year) if year else None,
        venue=attrs.get("publisher"),
        version=None,
        resolved_at=_now_iso(),
        source_api="api.datacite.org",
        raw={"datacite": data},
    )


def _resolve_doi_crossref(value: str, http=None) -> ResolvedReference:
    http = http or requests
    crossref_url = f"https://api.crossref.org/works/{value}"
    resp = _fetch_with_retry(http, crossref_url)
    data = resp.json()
    msg = data.get("message", {}) or {}
    title = (msg.get("title") or [""])[0]
    date_parts = ((msg.get("published-print") or msg.get("published-online") or {}).get("date-parts") or [[None]])
    year = date_parts[0][0] if date_parts and date_parts[0] else None
    authors = []
    for a in msg.get("author") or []:
        given = (a.get("given") or "").strip()
        family = (a.get("family") or "").strip()
        if given and family:
            authors.append(f"{given} {family}")
        elif family:
            authors.append(family)
    venue_list = msg.get("container-title") or []
    return ResolvedReference(
        identifier_type="doi",
        identifier_value=value,
        canonical_url=f"https://doi.org/{value}",
        title=title,
        authors=authors,
        year=int(year) if year else None,
        venue=venue_list[0] if venue_list else None,
        version=None,
        resolved_at=_now_iso(),
        source_api="api.crossref.org",
        raw={"crossref": data},
    )


_BACKENDS = {"arxiv": _resolve_arxiv, "doi": _resolve_doi}


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
    return backend(value, http=http or requests)


def load_cache(proof_dir: Path) -> dict[str, ResolvedReference]:
    path = Path(proof_dir) / _CACHE_FILENAME
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    out: dict[str, ResolvedReference] = {}
    for key, payload in data.items():
        out[key] = ResolvedReference(**payload)
    return out


def save_cache(proof_dir: Path, cache: dict[str, ResolvedReference]) -> None:
    path = Path(proof_dir) / _CACHE_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {k: asdict(v) for k, v in cache.items()}
    path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False) + "\n")
