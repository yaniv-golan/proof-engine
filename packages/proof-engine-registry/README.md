# proof-engine-registry

Protocol, client, and reference server for the Proof Registry — the JSON-over-HTTPS
layer that lets LLM wikis (and other tools) ask "is this claim already proven?"
and either use the existing proof or commission a new one.

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

    from proof_engine_registry import RegistryClient, load_registries
    client = RegistryClient(load_registries())
    hit = client.lookup("The sky is blue.")
    if hit:
        print(hit.proof_url)

## Self-host

    proof-registry serve ./my-proofs --port 8080 --token-env MY_TOKEN
