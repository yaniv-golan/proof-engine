# ADR-0001: Registry error response shape

- **Status:** accepted, scoped to protocol v0.1
- **Date:** 2026-04-25

## Context

The Registry Protocol v0.1 emits error responses as:

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{ "error": "not_found", "message": "no proof with that claim_hash" }
```

[RFC 7807 (Problem Details for HTTP APIs)](https://datatracker.ietf.org/doc/html/rfc7807)
defines a standard shape for HTTP API error bodies under
`application/problem+json`:

```json
{ "type": "https://...", "title": "...", "status": 404, "detail": "..." }
```

RFC 7807 is widely recognized but not universal — Stripe, Slack, Linear,
GitHub, Airtable, and many other quality public APIs use bespoke error
shapes similar to ours.

The protocol is at v0.1. Packages are not yet on PyPI. The only
consumers are this repo's bundled tests. The choice is genuinely free —
no deployed clients constrain us.

## Decision

**Keep the current `{error, message}` shape for v0.1.**

## Rationale

- The current shape carries the same information RFC 7807 carries:
  HTTP status (in the response line), a machine-readable code (`error`),
  and a human-readable description (`message`). The only thing missing
  is the optional `type` URI for cross-API uniqueness — useful for
  aggregation tools but not required for our use case.
- The current shape is implemented, tested by the conformance suite,
  and documented in the protocol spec.
- Migrating later via content negotiation (`Accept: application/problem+json`)
  is non-breaking and small; there's no path-dependence cost to deferring.
- The refactor effort (spec + server + tests + schemas) has marginal
  payoff at this stage; engineering attention is better spent on items
  with larger leverage (e.g., conformance test coverage of edge cases).

## Triggers to revisit

Adopt RFC 7807 (probably as a parallel shape via content negotiation,
not a replacement) when any of the following holds:

- A real consumer asks for it (issue or PR).
- We're bumping the protocol to v0.2 for unrelated reasons — cheap to bundle.
- The bundled spec needs to support API gateways or error-monitoring
  systems that auto-parse Problem Details.

## Migration plan (if/when adopted)

1. Server: emit `application/problem+json` when client sends
   `Accept: application/problem+json`; keep current shape on
   `Accept: application/json` or no Accept header.
2. Discovery doc: advertise `problem_details_supported: true` so clients
   can select the preferred format.
3. Conformance suite: parametrize error tests across both shapes.
4. Mark the legacy shape DEPRECATED for ≥1 minor protocol version
   before considering removal.

## Notes

An earlier draft of this ADR justified the current shape by claiming
"v0.1 has already shipped to consumers." That was incorrect — v0.1
ships in v1.32.0 alongside this ADR; nothing external consumes it yet.
The decision still stands, but on the rationale above, not on a false
shipping constraint.
