"""Problem Details catalog (RFC 7807) for the Registry Protocol.

Every error condition the server emits has exactly one entry here. Each entry
maps to the four RFC 7807 fields:

  - type:   absolute URI identifying the problem class (stable; safe to
            consume programmatically as a discriminator).
  - status: the HTTP status code emitted with this problem.
  - title:  short, human-readable summary; constant per type.
  - code:   the legacy short code retained as an additional non-standard
            field (`code`) on the Problem body — preserves greppability for
            log-aggregation tooling that already keys on it.

`detail` (the per-instance human description) is supplied by the caller at
emit time, NOT in this catalog — it varies per occurrence.
"""

from __future__ import annotations

from dataclasses import dataclass

# Base URI for the type field. Self-hosted registries SHOULD override this
# at construction time so their type URIs point at their own docs, but the
# default is fine for static-JSON deployments and dev work.
DEFAULT_TYPE_BASE = "https://proofengine.info/errors"


@dataclass(frozen=True)
class ProblemSpec:
    code: str         # e.g. "not_found"
    status: int       # e.g. 404
    title: str        # e.g. "Resource not found"
    type_path: str    # e.g. "/not-found" — appended to the base URI

    def type_uri(self, base: str = DEFAULT_TYPE_BASE) -> str:
        return f"{base.rstrip('/')}{self.type_path}"


# Catalog. Order is intentional (status code ascending, then alpha) so the
# generated documentation table reads naturally.
CATALOG: dict[str, ProblemSpec] = {
    "bad_request":         ProblemSpec("bad_request",         400, "Bad request",                  "/bad-request"),
    "unauthorized":        ProblemSpec("unauthorized",        401, "Authentication required",      "/unauthorized"),
    "forbidden":           ProblemSpec("forbidden",           403, "Forbidden",                    "/forbidden"),
    "not_found":           ProblemSpec("not_found",           404, "Resource not found",           "/not-found"),
    "conflict":            ProblemSpec("conflict",            409, "Conflict with existing state", "/conflict"),
    "too_large":           ProblemSpec("too_large",           413, "Payload too large",            "/payload-too-large"),
    "unsupported_version": ProblemSpec("unsupported_version", 426, "Protocol version mismatch",    "/unsupported-version"),
    "rebuild_failed":      ProblemSpec("rebuild_failed",      500, "Internal: registry rebuild failed", "/rebuild-failed"),
}


def problem(code: str) -> ProblemSpec:
    """Look up a ProblemSpec by code. Raises KeyError on unknown codes —
    this is intentional: every error path the server can take MUST have a
    catalog entry, otherwise we emit malformed Problem Details."""
    return CATALOG[code]
