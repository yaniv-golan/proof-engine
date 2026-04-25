# ADR-0001: Registry error response shape

- **Status:** accepted, scoped to protocol v0.1
- **Date:** 2026-04-25 (decision flipped from an earlier draft same day)

## Context

The Registry Protocol's error responses initially used a bespoke
`{error, message}` JSON shape:

```json
{ "error": "not_found", "message": "no proof with that claim_hash" }
```

[RFC 7807 (Problem Details for HTTP APIs)](https://datatracker.ietf.org/doc/html/rfc7807)
defines a standard shape for HTTP API error bodies under
`application/problem+json`:

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{ "type": "https://...", "status": 404, "title": "...", "detail": "..." }
```

The protocol is at v0.1. Packages are not yet on PyPI. The only
consumers are this repo's bundled tests. The choice is genuinely free —
no deployed clients constrain us.

## Decision

**Adopt RFC 7807 Problem Details for all JSON error responses, in
place, at protocol version v0.1.** No version bump; the wire format
of v0.1 IS Problem Details going forward.

## Rationale

- RFC 7807 is the IETF-standard shape for HTTP API error bodies. Public
  scrutiny of the protocol will expect it; adopting up-front avoids a
  later migration debate.
- Migration cost is small: the protocol has zero external consumers
  today (verified — the packages are not yet on PyPI). The only callers
  of the error shape are tests in this repository, all updated in the
  same release.
- The legacy `{error, message}` shape carried less information than the
  RFC 7807 shape (no stable `type` URI, no embedded status). Keeping it
  would have meant defending a less-rich shape against a more-standard
  one.
- The legacy machine-readable short key (`error`) is preserved as a
  non-standard `code` extension on every Problem body — RFC 7807 §3.2
  explicitly allows additional members. Log-aggregation tooling that
  keys on the short code keeps working without changes.

## Why not bump to protocol v0.2?

An earlier draft of this ADR proposed deferring the change to a
hypothetical v0.2 with a content-negotiation migration, citing
"v0.1 has already shipped to consumers." That was wrong: v0.1 ships in
the same release as this ADR, and nothing external binds to its
previous wire format. Since there is no shipped consumer to break, the
honest call is to make v0.1 emit Problem Details from day one rather
than carrying a deprecated shape into v0.2.

## Implementation summary

| File                                                                                     | Change                                                              |
|------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| `packages/proof-engine-registry/src/proof_engine_registry/problems.py` (new)             | Catalog of (code, status, type-path, title) tuples per error class. |
| `packages/proof-engine-registry/src/proof_engine_registry/schema.py`                     | `Problem` dataclass replaces `ErrorResponse`.                       |
| `packages/proof-engine-registry/schemas/registry-problem.schema.json` (new)              | Draft 2020-12 schema for the Problem shape.                         |
| `packages/proof-engine-registry/src/proof_engine_registry/server.py`                     | `_serve_error` emits `application/problem+json` from the catalog.   |
| `docs/registry-protocol.md` §Error shapes                                                | Spec rewritten; canonical-error table added.                        |
| `packages/proof-engine-registry/tests/{test_problems,test_schema,test_server,test_conformance}.py` | New + updated tests pinning the new shape.                  |

Total: 7 catalog entries, 5 new server tests, 1 conformance test, 2
new schema-shape tests. 80 tests pass post-adoption (was 65 pre-).

## Triggers to revisit

The decision is self-contained — RFC 7807 is the canonical shape; no
foreseeable reason to revisit. If a future v0.x brings the protocol
to formal IANA registration, the Problem Details adoption is a
prerequisite, not a question.

## Notes

An earlier draft framed the choice as "defer RFC 7807 to v0.2 because
v0.1 has shipped to consumers." That premise was factually wrong —
v0.1 had not shipped externally — and the user flagged it. This ADR
records the corrected analysis and the resulting flip to in-place
adoption.
