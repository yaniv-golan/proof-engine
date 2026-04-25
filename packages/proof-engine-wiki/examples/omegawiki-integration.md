# Integrating proof-engine-wiki with OmegaWiki

OmegaWiki runs on Claude Code and has a first-class `claims` entity type with
`supports`/`contradicts`/`invalidates` relationships. The adapter plugs in at
two points:

## 1. Ingest hook

Add a post-ingest step to the OmegaWiki ingest pipeline that invokes:

    proof-engine-wiki ingest path/to/newly-ingested-page.md

Configure one or more registries in `~/.config/proof-engine/registries.toml` —
typically `proofengine.info` as a read-only public source and your team's
internal registry as the publish target:

    [[registry]]
    name = "public"
    url = "https://proofengine.info"

    [[registry]]
    name = "omega-internal"
    url = "https://proofs.your-team.example"
    token_env = "OMEGA_PROOFS_TOKEN"
    publish = true

## 2. Lint hook

Schedule a periodic lint:

    proof-engine-wiki lint wiki/ --json > lint-report.json

Feed `lint-report.json` back into OmegaWiki as `claims` with
`verdict: unresolved` or `stale_proof` — the relationship graph then shows
which pages need human attention.

## Registry-only mode

If your team treats proof commissioning as a dedicated workflow (not part of
ingest), add `--registry-only` to every ingest call. Misses surface as
`LintFinding` items with `kind=unresolved_marker`, which OmegaWiki's
existing review queue can handle.
