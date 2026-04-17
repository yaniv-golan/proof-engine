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


def _resolve_swhid(value: str, http=None) -> ResolvedReference:
    http = http or requests
    url = f"https://archive.softwareheritage.org/api/1/resolve/{value}/"
    resp = _fetch_with_retry(http, url)
    data = resp.json()
    origin = data.get("origin_url") or ""
    title = origin or f"SWHID {value}"
    return ResolvedReference(
        identifier_type="swhid",
        identifier_value=value,
        canonical_url=f"https://archive.softwareheritage.org/{value}",
        title=title,
        authors=[],
        year=None,
        venue="Software Heritage Archive",
        version=None,
        resolved_at=_now_iso(),
        source_api="archive.softwareheritage.org/api/1/resolve",
        raw={"swh": data},
    )


def _resolve_handle(value: str, http=None) -> ResolvedReference:
    http = http or requests
    url = f"https://hdl.handle.net/api/handles/{value}"
    resp = _fetch_with_retry(http, url)
    data = resp.json()
    return ResolvedReference(
        identifier_type="handle", identifier_value=value,
        canonical_url=f"https://hdl.handle.net/{value}",
        title=f"Handle {value}", authors=[], year=None,
        venue=None, version=None, resolved_at=_now_iso(),
        source_api="hdl.handle.net", raw={"handle": data},
    )


def _resolve_isbn(value: str, http=None) -> ResolvedReference:
    http = http or requests
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{value}&format=json&jscmd=data"
    resp = _fetch_with_retry(http, url)
    data = resp.json()
    entry = data.get(f"ISBN:{value}", {})
    title = entry.get("title", f"ISBN {value}")
    authors = [a.get("name", "") for a in entry.get("authors", []) if a.get("name")]
    pub_date = entry.get("publish_date", "")
    year = None
    m = re.search(r"\b(19|20)\d{2}\b", pub_date)
    if m:
        year = int(m.group(0))
    publishers = entry.get("publishers") or []
    venue = publishers[0].get("name") if publishers else None
    return ResolvedReference(
        identifier_type="isbn", identifier_value=value,
        canonical_url=f"https://openlibrary.org/isbn/{value}",
        title=title, authors=authors, year=year,
        venue=venue, version=None, resolved_at=_now_iso(),
        source_api="openlibrary.org", raw={"openlibrary": data},
    )


_OG_RE = re.compile(
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


def _resolve_url(value: str, http=None) -> ResolvedReference:
    http = http or requests
    resp = _fetch_with_retry(http, value)
    html = resp.text
    title = (_OG_RE.search(html) or _TITLE_RE.search(html))
    title_str = title.group(1).strip() if title else value
    authors = [a.strip() for a in _OG_AUTHOR_RE.findall(html) if a.strip()]
    pub = _OG_PUB_RE.search(html)
    year = None
    if pub:
        m = re.search(r"\b(19|20)\d{2}\b", pub.group(1))
        if m:
            year = int(m.group(0))
    return ResolvedReference(
        identifier_type="url", identifier_value=value,
        canonical_url=value, title=title_str, authors=authors,
        year=year, venue=None, version=None, resolved_at=_now_iso(),
        source_api="og_extraction", raw={"html_len": len(html)},
    )


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

    Sources: meta.yaml `depends_on[*].identifiers` (excluding `slug`) +
    proof.json `evidence[*].source.url` passed through `identifier_from_url`.
    Deduplicated; order preserved.
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
