"""proof_citations.registry — identifier-to-metadata resolution.

Each submodule implements one backend (PubMed, Crossref, arXiv, …) behind a
common interface: take an identifier value, return a `ResolvedRecord` with
canonical metadata. Backends are stateless; dispatch lives here.

Public API:
    resolve(identifier, *, cache=None, session=None) -> ResolvedRecord
    register_backend(type_name, resolver_fn)
    Backend signatures match: (value: str, *, session: HTTPSession) -> ResolvedRecord
"""

from typing import Callable, Optional, Union

from proof_citations.registry.base import (
    Author,
    ResolvedRecord,
    Cache,
    InMemoryCache,
    FileCache,
    HTTPSession,
    get_default_session,
    ResolutionError,
)

# Backend registry: identifier_type -> resolver function
_BACKENDS: dict[str, Callable] = {}


def register_backend(type_name: str, resolver_fn: Callable) -> None:
    """Register a resolver function for an identifier type.

    The resolver is called as `resolver_fn(value, session=session)` and must
    return a `ResolvedRecord`. Raises `ResolutionError` on hard failure.
    """
    _BACKENDS[type_name] = resolver_fn


def get_backend(type_name: str) -> Optional[Callable]:
    return _BACKENDS.get(type_name)


def resolve(
    identifier: Union[tuple[str, str], str],
    *,
    cache: Optional[Cache] = None,
    session: Optional[HTTPSession] = None,
) -> ResolvedRecord:
    """Resolve an identifier to a `ResolvedRecord`.

    Args:
        identifier: Either a `(type, value)` tuple or a string like `"pmid:12345"`,
            `"doi:10.x/y"`, `"arxiv:2106.09685"`.
        cache: Optional cache; if provided, hits the cache first and stores
            new results on miss. Implementations: `InMemoryCache`, `FileCache`.
        session: Optional HTTP session. Defaults to `get_default_session()`.

    Returns:
        ResolvedRecord with whatever fields the backend could populate.

    Raises:
        ResolutionError: backend reports a hard failure (identifier doesn't
            exist, network error after retries, parsed response was malformed).
        ValueError: identifier_type is not registered.
    """
    if isinstance(identifier, str):
        if ":" not in identifier:
            raise ValueError(f"identifier string must be 'type:value', got {identifier!r}")
        type_name, value = identifier.split(":", 1)
    else:
        type_name, value = identifier

    if cache is not None:
        cache_key = f"{type_name}:{value}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    backend = _BACKENDS.get(type_name)
    if backend is None:
        raise ValueError(
            f"no backend registered for identifier type {type_name!r}; "
            f"registered: {sorted(_BACKENDS)}"
        )

    session = session or get_default_session()
    record = backend(value, session=session)

    if cache is not None:
        cache.put(f"{type_name}:{value}", record)

    return record


# Auto-register built-in backends at import time
def _autoregister() -> None:
    from proof_citations.registry import pubmed
    register_backend("pmid", pubmed.resolve_pmid)


_autoregister()


__all__ = [
    "Author",
    "ResolvedRecord",
    "Cache",
    "InMemoryCache",
    "FileCache",
    "HTTPSession",
    "ResolutionError",
    "resolve",
    "register_backend",
    "get_backend",
    "get_default_session",
]
