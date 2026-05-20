"""Shared types and infrastructure for `proof_citations.registry` backends.

This module defines:

* `Author` — structured author record (given, family, orcid, raw) so callers
  can do family-name comparison without re-parsing strings.
* `ResolvedRecord` — the lingua franca every backend returns. Includes
  cross-reference fields (`pmid`, `doi`) so a Crossref-resolved DOI can still
  report the corresponding PMID and vice-versa, and an `update_status` field
  for retraction / corrigendum / withdrawn-preprint signals.
* `Cache` — protocol for callers to plug in their own caching strategy.
* `InMemoryCache` and `FileCache` — sensible defaults so external users
  aren't forced to roll their own (or, worse, hammer rate-limited APIs).
* `HTTPSession` and `get_default_session()` — centralized polite HTTP client
  with retries and a `User-Agent` that respects the registrars' politeness
  conventions (Crossref's `mailto`, NCBI's `tool=` / `email=`).
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Protocol


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ResolutionError(Exception):
    """A registry backend failed to resolve an identifier.

    Distinguishes between "identifier does not exist" (e.g., Crossref 404),
    "transient network failure" (after retries exhausted), and "response
    malformed". Inspect `.kind` for the specific failure mode.
    """

    KINDS = frozenset({"not_found", "fetch_failed", "malformed_response", "rate_limited"})

    def __init__(self, message: str, *, kind: str = "fetch_failed", details: Optional[dict] = None):
        super().__init__(message)
        if kind not in self.KINDS:
            raise ValueError(f"kind must be one of {self.KINDS}, got {kind!r}")
        self.kind = kind
        self.details = details or {}


# ---------------------------------------------------------------------------
# Author
# ---------------------------------------------------------------------------

@dataclass
class Author:
    """Structured author record.

    Backends populate `given` and `family` separately where possible. `raw`
    preserves whatever the backend returned in case downstream code needs
    fields the abstraction doesn't surface (affiliations, sequence position,
    co-author markers, etc.).
    """
    family: str = ""
    given: str = ""
    orcid: Optional[str] = None
    raw: dict = field(default_factory=dict)

    def display(self) -> str:
        """Human-readable rendering — 'Family, G.' if both present, else family."""
        if self.given:
            initials = "".join(t[0] + "." for t in self.given.split() if t)
            return f"{self.family}, {initials}" if self.family else self.given
        return self.family

    def matches(self, query: str) -> bool:
        """Loose match — query string contains family name (case-insensitive)."""
        if not self.family:
            return False
        return self.family.lower() in query.lower()

    @classmethod
    def from_full_name(cls, name: str, *, orcid: Optional[str] = None, raw: Optional[dict] = None) -> "Author":
        """Best-effort parse of 'Family Given' or 'Given Family' into the struct.

        Heuristic: if the string is 'A B C' and the last token looks like a
        word (no commas), treat last as family. If 'Family, Given', split on
        comma. Backends that have already-structured data should NOT use this
        — they should set `family` and `given` directly.
        """
        name = name.strip()
        if not name:
            return cls(raw=raw or {})
        if "," in name:
            parts = name.split(",", 1)
            return cls(family=parts[0].strip(), given=parts[1].strip(), orcid=orcid, raw=raw or {})
        tokens = name.split()
        if len(tokens) == 1:
            return cls(family=tokens[0], orcid=orcid, raw=raw or {})
        # Last token = family, rest = given (heuristic; western convention)
        return cls(family=tokens[-1], given=" ".join(tokens[:-1]), orcid=orcid, raw=raw or {})


# ---------------------------------------------------------------------------
# ResolvedRecord — the lingua franca
# ---------------------------------------------------------------------------

@dataclass
class ResolvedRecord:
    """Canonical bibliographic record from any registry backend.

    Field guarantees:
    - `identifier_type` and `identifier_value` always populated.
    - `canonical_url` always populated (the URL that authoritatively represents
      this identifier — e.g. `https://pubmed.ncbi.nlm.nih.gov/{pmid}/`).
    - All other fields are best-effort. Compare logic must treat absence as
      "not asserted," NOT "asserted to be missing."
    - `resolved_at` is ISO-8601 UTC timestamp of when the resolution happened.
    - `source_api` identifies which backend produced this (e.g.,
      `eutils.ncbi.nlm.nih.gov` or `api.crossref.org`).
    - `raw` preserves the original API response payload. Persisters MAY drop
      this to keep on-disk caches small.

    Backwards-compat policy:
    - Fields may only be ADDED in future versions, never removed or renamed.
    - New fields must have safe defaults so `ResolvedRecord(**old_dict)` keeps
      working when older caches are deserialized.
    """
    identifier_type: str
    identifier_value: str
    canonical_url: str
    title: Optional[str] = None
    authors: list[Author] = field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    publisher: Optional[str] = None
    publication_type: Optional[str] = None  # "journal-article", "preprint", "dataset", "book", …
    published_date: Optional[str] = None    # ISO-8601 date string, e.g. "2013-02-15"
    issn: Optional[str] = None
    doi: Optional[str] = None               # cross-reference if known
    pmid: Optional[str] = None              # cross-reference if known
    arxiv_id: Optional[str] = None          # cross-reference if known
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    language: Optional[str] = None
    update_status: Optional[str] = None     # "retracted", "expression_of_concern", "corrigendum", …
    update_refs: list[str] = field(default_factory=list)  # DOIs of update notices
    resolved_at: str = ""
    source_api: str = ""
    raw: dict = field(default_factory=dict)

    def cache_key(self) -> str:
        return f"{self.identifier_type}:{self.identifier_value}"

    def to_dict(self, *, include_raw: bool = True) -> dict:
        """Serialize for caching or JSON output.

        `include_raw=False` drops the raw payload — useful for committed
        caches (`depends_on_resolved.json`) where you want a compact record,
        not the full Atom feed / Crossref response.
        """
        d = asdict(self)
        if not include_raw:
            d.pop("raw", None)
        # Authors round-trip through their own asdict; that's fine
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ResolvedRecord":
        """Deserialize from a dict. Unknown keys are silently dropped so
        future-version caches read by older code don't crash."""
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in d.items() if k in known}
        # Reconstruct authors
        if "authors" in filtered and filtered["authors"]:
            filtered["authors"] = [
                Author(**a) if isinstance(a, dict) else Author.from_full_name(str(a))
                for a in filtered["authors"]
            ]
        return cls(**filtered)


def now_iso() -> str:
    """ISO-8601 UTC timestamp with no microseconds. Use as default for
    `resolved_at`. Module-level so backends can call it consistently."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ---------------------------------------------------------------------------
# Cache protocol + implementations
# ---------------------------------------------------------------------------

class Cache(Protocol):
    """Storage protocol for resolved records.

    Implementations decide their own keying, persistence, TTL. The library
    only requires `get(key) -> ResolvedRecord | None` and `put(key, record)`.

    Keys are strings of the form `"{identifier_type}:{identifier_value}"`.
    """

    def get(self, key: str) -> Optional[ResolvedRecord]: ...
    def put(self, key: str, record: ResolvedRecord) -> None: ...


class InMemoryCache:
    """Simple dict-backed cache. Thread-safe for individual get/put calls.

    Useful in tests and short-lived scripts. Not persisted.
    """

    def __init__(self) -> None:
        self._data: dict[str, ResolvedRecord] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[ResolvedRecord]:
        with self._lock:
            return self._data.get(key)

    def put(self, key: str, record: ResolvedRecord) -> None:
        with self._lock:
            self._data[key] = record

    def __len__(self) -> int:
        return len(self._data)


class FileCache:
    """JSON-file cache. Single file holds all records as
    `{"records": {key: record_dict, ...}}`.

    Atomic writes via tempfile + rename. Concurrent processes that both write
    will have one's write win — not a problem in practice because cached records
    are deterministic (same input → same registry response).

    The default location is `~/.cache/proof-citations/cache.json`. Pass an
    explicit `path` to override.

    `include_raw` controls whether the registry's raw API response is persisted.
    Default `False` keeps committed caches small; pass `True` if you need to
    re-process raw payloads from cache without re-fetching.
    """

    def __init__(self, path: Optional[Path] = None, *, include_raw: bool = False) -> None:
        if path is None:
            cache_root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
            path = cache_root / "proof-citations" / "cache.json"
        self.path = Path(path)
        self.include_raw = include_raw
        self._lock = threading.Lock()
        self._data: Optional[dict[str, ResolvedRecord]] = None

    def _load(self) -> dict[str, ResolvedRecord]:
        if self._data is not None:
            return self._data
        if not self.path.exists():
            self._data = {}
            return self._data
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # Corrupt cache → treat as empty rather than fail.
            self._data = {}
            return self._data
        records = payload.get("records", {})
        self._data = {k: ResolvedRecord.from_dict(v) for k, v in records.items()}
        return self._data

    def get(self, key: str) -> Optional[ResolvedRecord]:
        with self._lock:
            return self._load().get(key)

    def put(self, key: str, record: ResolvedRecord) -> None:
        with self._lock:
            data = self._load()
            data[key] = record
            self._write(data)

    def _write(self, data: dict[str, ResolvedRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "records": {k: v.to_dict(include_raw=self.include_raw) for k, v in data.items()},
        }
        # Atomic write
        with tempfile.NamedTemporaryFile(
            "w", dir=self.path.parent, delete=False, encoding="utf-8", prefix=".cache_", suffix=".tmp",
        ) as tmp:
            json.dump(payload, tmp, indent=2, ensure_ascii=False, default=str)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, self.path)


# ---------------------------------------------------------------------------
# HTTP session with polite-pool defaults and retries
# ---------------------------------------------------------------------------

try:
    import requests  # type: ignore[import-not-found]
    from requests.adapters import HTTPAdapter
    try:
        from urllib3.util.retry import Retry
    except ImportError:
        # Older urllib3 has it elsewhere
        from urllib3.util import Retry  # type: ignore[no-redef]
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False
    requests = None  # type: ignore[assignment]


class HTTPSession:
    """Polite HTTP client wrapping `requests.Session` with backoff retries.

    The `User-Agent` is `proof-citations/{version} (https://proofengine.info/;
    mailto={contact_email})` — this satisfies Crossref's polite-pool policy,
    NCBI's `tool=` recommendation, and standard scholarly-API etiquette.

    Per-host rate limiting is NOT enforced here — backends are expected to
    respect each registrar's limits in their own logic (or rely on the
    registrar's 429 + retry-after, which our Retry config honors).

    Pass `contact_email` to override the default placeholder; environment
    variable `PROOF_CITATIONS_CONTACT` is also honored.
    """

    DEFAULT_UA_FORMAT = (
        "proof-citations/{version} (https://proofengine.info/; mailto={email})"
    )

    def __init__(
        self,
        *,
        contact_email: Optional[str] = None,
        timeout: float = 15.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        if not _HAS_REQUESTS:
            raise RuntimeError(
                "proof_citations.registry requires the `requests` package. "
                "Install with: pip install proof-citations[registry] (or `pip install requests`)."
            )
        from proof_citations import __version__

        email = (
            contact_email
            or os.environ.get("PROOF_CITATIONS_CONTACT")
            or "anonymous@example.org"
        )
        self.user_agent = self.DEFAULT_UA_FORMAT.format(version=__version__, email=email)
        self.timeout = timeout

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.user_agent, "Accept": "*/*"})

        retry = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "HEAD"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def get(self, url: str, *, headers: Optional[dict] = None, params: Optional[dict] = None, timeout: Optional[float] = None) -> Any:
        """GET with the session's defaults; returns the `requests.Response`."""
        return self._session.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout if timeout is not None else self.timeout,
        )


_DEFAULT_SESSION: Optional[HTTPSession] = None
_DEFAULT_SESSION_LOCK = threading.Lock()


def get_default_session() -> HTTPSession:
    """Lazy-construct a single shared default session.

    Reuses the same TCP pool across backends; honors `PROOF_CITATIONS_CONTACT`
    env var for the polite-pool email.
    """
    global _DEFAULT_SESSION
    with _DEFAULT_SESSION_LOCK:
        if _DEFAULT_SESSION is None:
            _DEFAULT_SESSION = HTTPSession()
        return _DEFAULT_SESSION


__all__ = [
    "Author",
    "ResolvedRecord",
    "Cache",
    "InMemoryCache",
    "FileCache",
    "HTTPSession",
    "ResolutionError",
    "get_default_session",
    "now_iso",
]
