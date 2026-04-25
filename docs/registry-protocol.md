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
  "proof_count": 133,
  "generated_at": "2026-04-24T00:00:00Z",
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

All error responses are JSON:

```json
{ "error": "not_found", "message": "no proof with that claim_hash" }
```

Standard codes: `not_found`, `unauthorized`, `forbidden`, `too_large`, `conflict`,
`unsupported_version`, `bad_request`.

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
