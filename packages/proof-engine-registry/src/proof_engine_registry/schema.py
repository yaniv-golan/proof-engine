"""Dataclasses for Registry Protocol v0.1 payloads.

Single source of truth for the wire format. JSON schemas under ../schemas/
are generated from these and MUST stay in sync.
"""

from __future__ import annotations

import typing
from dataclasses import dataclass, asdict, fields, is_dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class Discovery:
    protocol_version: str
    name: str
    homepage: str
    publishes_supported: bool
    auth_required: bool
    proof_count: int
    generated_at: str  # ISO8601 UTC
    signing_key: Optional[str]  # reserved for future signed-registry use


@dataclass(frozen=True)
class IndexEntry:
    claim_hash: str          # sha256 hex, 64 chars
    slug: str
    claim: str
    verdict: str             # PROVED | DISPROVED | SUPPORTED | PARTIALLY VERIFIED | UNDETERMINED
    confidence: float        # 0.0–1.0
    doi: Optional[str]
    proof_url: str
    badge_url: str
    generated_at: str


@dataclass(frozen=True)
class Index:
    protocol_version: str
    generated_at: str
    entries: list[IndexEntry]


@dataclass(frozen=True)
class RegistryProof:
    """Full proof metadata — superset of IndexEntry."""
    claim_hash: str
    slug: str
    claim: str
    verdict: str
    confidence: float
    doi: Optional[str]
    proof_url: str
    badge_url: str
    generated_at: str
    fact_ids: list[str]      # e.g. ["B1", "A1", "S1"]
    source_urls: list[str]   # deduplicated URLs cited
    narrative_summary: Optional[str]


@dataclass(frozen=True)
class ErrorResponse:
    error: str
    message: str


def to_json(obj: Any) -> dict:
    """Dataclass → JSON-serializable dict. Recursive."""
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError(f"not a dataclass: {type(obj)}")


def from_json(cls: type, data: dict) -> Any:
    """JSON dict → dataclass instance. Recursive for nested dataclasses and lists."""
    if not is_dataclass(cls):
        raise TypeError(f"not a dataclass: {cls}")
    # Resolve PEP-563 string annotations once per class.
    hints = typing.get_type_hints(cls)
    kwargs: dict[str, Any] = {}
    for f in fields(cls):
        value = data.get(f.name)
        kwargs[f.name] = _coerce(hints.get(f.name, f.type), value)
    return cls(**kwargs)


def _coerce(annotation: Any, value: Any) -> Any:
    # Handle list[DataclassType]
    origin = typing.get_origin(annotation)
    if origin is list:
        args = typing.get_args(annotation)
        inner = args[0] if args else None
        if inner is not None and is_dataclass(inner):
            return [from_json(inner, v) for v in (value or [])]
        return list(value or [])
    # Handle nested dataclasses
    if is_dataclass(annotation) and isinstance(value, dict):
        return from_json(annotation, value)
    return value
