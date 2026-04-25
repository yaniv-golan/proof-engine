# ADR-0001: Registry error response shape

- **Status:** accepted, scoped to protocol v0.1
- **Date:** 2026-04-25
- **Decision driver:** public-OSS readiness review (item 9)

## Context

The Registry Protocol v0.1 emits error responses as:

```json
{ "error": "not_found", "message": "no proof with that claim_hash" }
```

[RFC 7807 (Problem Details for HTTP APIs)](https://datatracker.ietf.org/doc/html/rfc7807)
defines a standard shape for HTTP API error bodies:

```http
Content-Type: application/problem+json

{ "type": "https://...", "title": "...", "status": 404, "detail": "..." }
```

Most modern public APIs follow RFC 7807. Reviewers fluent in REST will
expect it.

## Decision

**Defer RFC 7807 migration to protocol v0.2.** Keep v0.1 as-is.

## Rationale

- v0.1 has already shipped to consumers. Changing the error shape now
  would force every existing client to add new code paths.
- The current shape carries the same information as Problem Details
  (status code, machine-readable code, human message). It's just under
  different field names.
- A protocol minor bump is the right place to introduce a parallel
  RFC-7807-shaped response, with content negotiation via the `Accept`
  header (`application/json` → current shape; `application/problem+json`
  → new shape).
- Conformance suite already pins the current shape; v0.2 must add
  parametrized tests for both.

## Migration plan (when v0.2 lands)

1. Server: emit RFC 7807 when client sends `Accept: application/problem+json`;
   keep current shape on `Accept: application/json` or no Accept header.
2. Client: prefer Problem Details when speaking to a v0.2+ registry
   (advertised via discovery).
3. Conformance: parametrize all error tests over both shapes.
4. Deprecation period: ≥1 minor version before removing the legacy shape.

## Alternatives considered

- **Migrate immediately.** Breaks every existing client. No acceptable.
- **Adopt RFC 7807 only on the public registry.** Asymmetric across
  conformant implementations defeats the protocol-level guarantee.
