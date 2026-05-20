"""High-level entry point: verify a bibliographic claim.

`verify_citation_record(identifier, expected)` resolves the identifier via
the registry layer, runs `compare_metadata`, and returns a unified verdict.

This sits one level above the primitives:
- `proof_citations.identify` extracts an identifier from a URL or string
- `proof_citations.resolve` resolves an identifier to a `ResolvedRecord`
- `proof_citations.compare_metadata` compares the record against a claim

Most callers want the combined "is this citation real and correctly cited?"
question, which is what this function answers.
"""

from __future__ import annotations

from typing import Optional, Union

from proof_citations.compare import compare_metadata
from proof_citations.identify import identify
from proof_citations.registry import resolve
from proof_citations.registry.base import (
    Cache,
    HTTPSession,
    ResolutionError,
    ResolvedRecord,
)


def verify_citation_record(
    identifier: Union[tuple[str, str], str],
    expected: Optional[dict] = None,
    *,
    cache: Optional[Cache] = None,
    session: Optional[HTTPSession] = None,
) -> dict:
    """Resolve an identifier and compare against an expected metadata dict.

    Args:
        identifier: `(type, value)` tuple, `"type:value"` string, or a URL
            (passed through `identify()` for type extraction).
        expected: optional dict with claimed bibliographic fields. See
            `compare_metadata` for the supported keys. If `None` or empty,
            this function returns the resolved record with verdict `"resolved"`
            — useful when you just want structured metadata from the registry.
        cache: optional `Cache` for memoization across calls.
        session: optional `HTTPSession`; defaults to the shared polite session.

    Returns:
        A dict with keys:
        - status: "verified" | "metadata_chimera" | "title_chimera" |
                  "partial_match" | "resolved" | "unresolvable" | "fetch_failed"
        - verdict: the underlying `compare_metadata` verdict (or "no_expected"
                   when nothing was compared, or "unresolvable"/"fetch_failed"
                   when resolution failed).
        - resolved: the `ResolvedRecord` (or None if resolution failed).
        - field_matches: from `compare_metadata` (empty when no compare).
        - mismatches: from `compare_metadata`.
        - title_similarity: from `compare_metadata`.
        - message: human-readable summary.
        - error: `ResolutionError` instance (or None) if resolution failed.
    """
    # Allow callers to pass a URL directly; identify() extracts the typed pair.
    if isinstance(identifier, str) and identifier.lower().startswith(("http://", "https://")):
        parsed = identify(identifier)
        if parsed is None:
            return _failure_response(
                status="unresolvable",
                message=f"Could not extract an identifier from URL: {identifier}",
            )
        identifier = parsed

    try:
        record = resolve(identifier, cache=cache, session=session)
    except ResolutionError as e:
        return _failure_response(
            status="unresolvable" if e.kind == "not_found" else "fetch_failed",
            message=str(e),
            error=e,
        )
    except ValueError as e:
        return _failure_response(status="fetch_failed", message=str(e))

    if not expected:
        return {
            "status": "resolved",
            "verdict": "no_expected",
            "resolved": record,
            "field_matches": {},
            "mismatches": [],
            "title_similarity": None,
            "message": f"Resolved {record.identifier_type}:{record.identifier_value} but no expected metadata supplied.",
            "error": None,
        }

    cmp = compare_metadata(record, expected)
    status = _verdict_to_status(cmp["verdict"])
    return {
        "status": status,
        "verdict": cmp["verdict"],
        "resolved": record,
        "field_matches": cmp["field_matches"],
        "mismatches": cmp["mismatches"],
        "title_similarity": cmp["title_similarity"],
        "message": cmp["message"],
        "error": None,
    }


def _failure_response(*, status: str, message: str, error: Optional[Exception] = None) -> dict:
    """Build a uniform response for resolution failures."""
    return {
        "status": status,
        "verdict": status,  # unresolvable / fetch_failed
        "resolved": None,
        "field_matches": {},
        "mismatches": [],
        "title_similarity": None,
        "message": message,
        "error": error,
    }


def _verdict_to_status(verdict: str) -> str:
    """Map the comparator's verdict to the orchestrator's outward `status`.

    For backwards-compatibility with downstream callers reading `status` as
    a coarse pass/fail signal, map:
      genuine          → verified
      metadata_chimera → metadata_chimera (no legacy bucket; surface explicitly)
      title_chimera    → title_chimera
      partial_match    → partial_match
      no_expected      → resolved (the record was resolved; nothing to compare)
    """
    return {
        "genuine": "verified",
        "metadata_chimera": "metadata_chimera",
        "title_chimera": "title_chimera",
        "partial_match": "partial_match",
        "no_expected": "resolved",
    }.get(verdict, verdict)


__all__ = ["verify_citation_record"]
