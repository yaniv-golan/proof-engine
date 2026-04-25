# proof-engine-registry

Protocol, client, and reference server for the Proof Registry — the
JSON-over-HTTPS layer that lets LLM wikis (and other tools) ask
"is this claim already proven?" and either use the existing proof or
commission a new one.

Spec: [`docs/registry-protocol.md`](../../docs/registry-protocol.md).

## Install

    pip install proof-engine-registry

## Config

    ~/.config/proof-engine/registries.toml

```toml
[[registry]]
name = "public"
url = "https://proofengine.info"

[[registry]]
name = "acme-internal"
url = "https://proofs.acme.com"
token_env = "ACME_PROOFS_TOKEN"
publish = true
```

## Client

```python
from proof_engine_registry import RegistryClient, load_registries
client = RegistryClient(load_registries())
hit = client.lookup("The sky is blue.")
if hit:
    print(hit.proof_url)
```

## Self-host

    proof-registry serve ./my-proofs --port 8080 --token-env MY_TOKEN

Useful flags:

| Flag                  | Default                              | Purpose                                                                                              |
|-----------------------|--------------------------------------|------------------------------------------------------------------------------------------------------|
| `--token-env`         | (none)                               | Env var holding the bearer token required for `POST /proofs`. Omit to disable publishing.            |
| `--cors-origin`       | `*`                                  | Value for `Access-Control-Allow-Origin` on read responses. Use a specific origin to restrict access. |
| `--log-json`          | off                                  | Emit one JSON access record per request to stderr. Authorization headers are never logged.           |
| `--problem-type-base` | `https://proofengine.info/errors`    | Base URI for `type` fields in RFC 7807 error bodies. Override to point at your own docs.             |

### Production deployment

The reference server uses plain stdlib HTTP and binds to `127.0.0.1` by
default. Suitable for development and local team use. **For public
exposure over the open internet**, front the server with a TLS-terminating
reverse proxy (nginx, Caddy, Cloudflare, AWS ALB) and route only
encrypted traffic from the proxy to the server. Bearer tokens MUST NOT
travel the network in cleartext.

## Errors

JSON error responses follow [RFC 7807 Problem Details](https://datatracker.ietf.org/doc/html/rfc7807):

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://proofengine.info/errors/not-found",
  "status": 404,
  "title": "Resource not found",
  "detail": "no proof with that claim_hash",
  "code": "not_found"
}
```

The `code` field preserves the legacy short machine key for
log-aggregation tooling. Full canonical-error table in the
[protocol spec](../../docs/registry-protocol.md).

## Conformance

A protocol-version-aware conformance suite ships with the package:

    cd packages/proof-engine-registry && python -m pytest tests/test_conformance.py -v

It runs against both the static-JSON emit and the reference server.
Any third-party server claiming to speak the protocol can run the same
suite.
