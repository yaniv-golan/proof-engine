# Proof Registry Protocol v0.1

JSON-over-HTTPS protocol for querying and (optionally) publishing verified proofs.
Public and private self-hosted registries implement this same protocol.

## Discovery

    GET /.well-known/proof-registry.json

Response:

```json
{
  "protocol_version": "0.1",
  "name": "Proof Engine Public Registry",
  "homepage": "https://proofengine.info",
  "publishes_supported": false,
  "auth_required": false,
  "proof_count": 132,
  "generated_at": "2026-04-25T00:00:00Z",
  "signing_key": null
}
```

A client MUST fetch this first and MUST refuse to proceed if `protocol_version`'s
major component exceeds what the client supports. Clients SHOULD cache the
discovery doc for up to one hour.

## Read endpoints

### `GET /index.json`

Returns the complete claim index.

```json
{
  "protocol_version": "0.1",
  "generated_at": "2026-04-24T00:00:00Z",
  "entries": [
    {
      "claim_hash": "6b2c...",
      "slug": "purchasing-power-decline",
      "claim": "The US dollar has lost X% of its purchasing power since Y",
      "verdict": "SUPPORTED",
      "confidence": 0.92,
      "doi": "10.5281/zenodo.1234567",
      "proof_url": "https://proofengine.info/proofs/purchasing-power-decline/",
      "badge_url": "https://proofengine.info/proofs/purchasing-power-decline/badge.json",
      "generated_at": "2026-04-17T12:00:00Z"
    }
  ]
}
```

### `GET /claims/{claim_hash}.json`

Lookup by claim hash. 200 if found, 404 if not.

Response body is a single index entry (same shape as elements of
`entries` above), OR 404 with `{"error": "not_found"}`.

### `GET /proofs/{slug}.json`

Full proof metadata — superset of the index entry. Includes fact list,
source URLs, computation summary, links to artifacts.

### `GET /proofs/{slug}/badge.json`

Compact badge payload. Shape:

```json
{
  "schema_version": "1.0",
  "slug": "...",
  "claim": "...",
  "verdict": "SUPPORTED",
  "confidence": 0.87,
  "doi": null,
  "proof_url": "...",
  "badge_svg_url": "...",
  "generated_at": "...",
  "colors": { "verdict_bg": "#5eb88a", "verdict_fg": "#ffffff" }
}
```

### `GET /proofs/{slug}/badge.svg`

Inline SVG rendering of the badge. Deterministic — byte-identical across builds
for identical inputs. Safe to cache indefinitely against the proof's
`generated_at` timestamp.

## Write endpoints (optional)

### `POST /proofs`

Publish a new proof.

Request:

```http
POST /proofs HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "slug": "...",
  "claim": "...",
  "proof_json": { ... },
  "artifacts": {
    "proof_py": "<base64>",
    "proof_md": "<base64>",
    "proof_audit_md": "<base64>",
    "proof_narrative_md": "<base64>"
  }
}
```

Responses:
- 201 Created — body is the new `/proofs/{slug}.json`.
- 409 Conflict — slug already exists. Use `PUT` to update.
- 401 Unauthorized — missing or bad token.
- 413 Payload Too Large — server-enforced limit.

### `PUT /proofs/{slug}`

Update. Same body as POST minus `slug` (which is in the URL).

## HTTP methods

Conformant servers MUST implement `GET` for all read endpoints. They MUST
also implement `HEAD` — returning the same status and headers as `GET` but
no body. HEAD support is required because downstream tools (e.g., the wiki
adapter's lint step) issue `HEAD` to check proof-URL reachability; a 501
would be indistinguishable from a rotted link.

## Cross-origin access (CORS)

Conformant servers MUST emit `Access-Control-Allow-Origin: *` on all read
responses (`GET` and `HEAD` for the discovery, index, claim, proof, and
badge endpoints). The protocol exposes only public read data; without
`*`, browser-based wiki tools cannot consume the registry from a page
served from a different origin.

For private registries that require auth on reads, servers MAY restrict
CORS instead by emitting a specific origin (e.g., the consuming wiki's
origin) and adding `Vary: Origin`. Servers SHOULD respond to `OPTIONS`
preflight requests for `Authorization`-bearing reads with
`Access-Control-Allow-Headers: Authorization` and
`Access-Control-Allow-Methods: GET, HEAD`.

Static-JSON deployments (e.g., the public site on GitHub Pages /
Cloudflare Pages) typically already emit `*` by default; verify with
`curl -I` after deployment.

## Caching

Read endpoints serve content that changes only at registry rebuild time.
Conformant servers SHOULD emit `Cache-Control: public, max-age=300` on
read responses (5 minutes — short enough to pick up new proofs quickly,
long enough to amortize CDN traffic). The discovery doc MAY use a longer
TTL since its `proof_count` is the only field that drifts.

Servers SHOULD also emit `ETag` headers derived from the registry's
`generated_at` timestamp so clients can revalidate via
`If-None-Match`.

Clients SHOULD honor `Cache-Control` and SHOULD NOT cache 4xx responses.

## Production deployment (TLS)

The protocol is JSON-over-HTTPS. The bundled `proof-registry serve`
reference server uses plain stdlib HTTP and binds to `127.0.0.1` by
default — suitable for development and local team use, but NOT suitable
for direct exposure to the public internet.

Production self-hosted deployments MUST front the reference server with
a TLS-terminating reverse proxy (nginx, Caddy, Cloudflare, AWS ALB,
etc.) and route only encrypted traffic from the proxy to the server.
The reference server MUST NOT be reachable directly from outside the
deployment perimeter — bearer tokens travel in the `Authorization`
header and would be exposed in cleartext otherwise.

Static-JSON deployments inherit TLS from their hosting platform
(GitHub Pages, Cloudflare Pages, S3 + CloudFront, etc.) — no separate
proxy needed.

## Rate limiting

The protocol does not specify rate limits — they're a deployment
concern. Public deployments SHOULD enforce limits at the CDN/proxy
layer (Cloudflare's free tier offers per-path rate limits;
nginx's `limit_req` directive is the classic approach).

Private registries with publish enabled SHOULD additionally rate-limit
the `POST /proofs` and `PUT /proofs/{slug}` endpoints — proof generation
is expensive and a runaway client could exhaust the publish-target
disk or the bearer token's API budget.

## Authentication

Bearer token in `Authorization` header. Private registries MAY require auth on
all endpoints, including reads. The discovery endpoint SHOULD still be
accessible with auth so clients can confirm they're talking to a real registry
before sending their token elsewhere.

## Claim hashing

```
normalize(claim):
  claim = unicodedata.normalize("NFC", claim)
  claim = claim.lower()
  claim = re.sub(r"\s+", " ", claim).strip()
  claim = claim.rstrip(".!?")
  return claim

claim_hash = sha256(normalize(claim).encode("utf-8")).hexdigest()
```

Test vectors:

| Input                                  | Normalized                        | Hash (first 16) |
|----------------------------------------|-----------------------------------|-----------------|
| `"The sky is blue."`                   | `"the sky is blue"`               | `da11…`         |
| `"THE   SKY IS BLUE!"`                 | `"the sky is blue"`               | `da11…`         |
| `"The sky is blue"` (no terminal)      | `"the sky is blue"`               | `da11…`         |

(The exact 16-char prefix is pinned by `test_hashing.py`.)

## Error shapes

JSON error responses MUST be [RFC 7807 Problem Details](https://datatracker.ietf.org/doc/html/rfc7807),
served with `Content-Type: application/problem+json`:

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json
Cache-Control: no-store

{
  "type": "https://proofengine.info/errors/not-found",
  "status": 404,
  "title": "Resource not found",
  "detail": "no proof with that claim_hash",
  "code": "not_found"
}
```

Required fields:

- `type` — absolute URI identifying the problem class. Stable across
  releases; safe to consume programmatically as a discriminator.
  Self-hosted registries MAY emit a different base (e.g., point at
  internal docs); the path component (e.g. `/not-found`) is the
  canonical identifier.
- `status` — HTTP status code, mirrored from the response status line
  per RFC 7807 §3.1.
- `title` — short, human-readable summary; constant per type.
- `detail` — per-occurrence human description with specific information
  about this instance. MUST NOT include the request body, the
  `Authorization` header value, or any internal stack trace.

Optional / extension fields (RFC 7807 §3.2 allows additional members):

- `code` — short machine-readable error key matching the catalog (e.g.
  `not_found`). This is a non-standard extension preserved from
  protocol v0.1 for log-aggregation tooling.

Standard codes and their canonical (status, title, type-path) tuples:

| `code`                | Status | Title                              | Type path              |
|-----------------------|--------|------------------------------------|------------------------|
| `bad_request`         | 400    | Bad request                        | `/bad-request`         |
| `unauthorized`        | 401    | Authentication required            | `/unauthorized`        |
| `forbidden`           | 403    | Forbidden                          | `/forbidden`           |
| `not_found`           | 404    | Resource not found                 | `/not-found`           |
| `conflict`            | 409    | Conflict with existing state       | `/conflict`            |
| `too_large`           | 413    | Payload too large                  | `/payload-too-large`   |
| `unsupported_version` | 426    | Protocol version mismatch          | `/unsupported-version` |
| `rebuild_failed`      | 500    | Internal: registry rebuild failed  | `/rebuild-failed`      |

The full type URI is `<type_base><type_path>` where `<type_base>` defaults
to `https://proofengine.info/errors`.

### Static deployments are exempt from the body shape

Static-JSON deployments (e.g., the public site on GitHub Pages /
Cloudflare Pages) cannot customize the host's default 404 body — those
hosts return their own `text/html` error pages. Such deployments are
treated as opaque-error servers: clients MUST rely on the HTTP status
code only and MUST NOT attempt to parse the body. A deployment
returning a JSON error body MUST emit Problem Details; emitting a
non-Problem JSON body (e.g., the legacy `{error, message}`) is a
protocol violation as of v0.2.


## Versioning

- Additive changes (new optional fields, new endpoints) → minor bump.
- Breaking changes to response shapes → major bump.
- Clients refuse to speak to registries with a higher major version than they
  support.

## Reference implementations

- **Public static (read-only):** `proofengine.info` — served by GitHub Pages
  from static JSON written by `tools/build-site.py`.
- **Reference server (read + publish):** `proof-registry serve <proofs-dir>`
  from the `proof-engine-registry` package. Stdlib HTTP server, bearer-token
  auth. Suitable for team/private deployments.
- **Conformance suite:** `pytest packages/proof-engine-registry/tests/test_conformance.py`
  — runs against any implementation.
