# Proposed integration: proof-engine-wiki + OmegaWiki

> **Status: design sketch, not a shipped integration.** No code in
> [OmegaWiki](https://github.com/skyllwt/OmegaWiki) currently invokes
> proof-engine-wiki. This document describes how a maintainer of either
> project (or a contributor) could wire the two together. If you're working
> on this, please open an issue or PR — we're happy to pair.

OmegaWiki ([github.com/skyllwt/OmegaWiki](https://github.com/skyllwt/OmegaWiki))
runs on Claude Code and has a first-class `claims` entity type with
`supports` / `contradicts` / `invalidates` relationships — a natural fit
for surfacing verified proofs alongside knowledge-graph claims.

A clean integration would plug in at two points:

## 1. Ingest hook (proposed)

After OmegaWiki processes a new source into draft pages, run:

    proof-engine-wiki ingest path/to/newly-ingested-page.md

This finds `{{prove: ...}}` markers in the draft, looks them up in
configured registries, and rewrites the page with inline link + badge for
each hit. Misses are reported as findings (no commissioning unless
explicitly enabled).

Suggested registry config in `~/.config/proof-engine/registries.toml`:

    [[registry]]
    name = "public"
    url = "https://proofengine.info"

    [[registry]]
    name = "omega-internal"
    url = "https://proofs.your-team.example"
    token_env = "OMEGA_PROOFS_TOKEN"
    publish = true

For OmegaWiki authors to mark claims, the system prompt would teach the
generation step to wrap claims warranting a proof in `{{prove: ...}}` —
and only those. (See the marker convention discussion in the
[llm_wiki proposal](./llm-wiki-integration.md#marker-convention).)

## 2. Lint hook (proposed)

Schedule a periodic lint pass:

    proof-engine-wiki lint wiki/ --json > lint-report.json

Each finding (`unresolved_marker`, `stale_proof`) could surface in
OmegaWiki's existing review queue, or — more interestingly — be
materialized as `claims` entities with their own relationships, so the
knowledge graph itself shows which pages need human attention.

## Registry-only mode

For teams that prefer to keep proof commissioning as a deliberate workflow
(not automatic on every ingest), add `--registry-only`. Misses surface as
`unresolved_marker` findings without consuming any LLM budget.

## What's missing for an actual integration

- An OmegaWiki contributor to wire `proof-engine-wiki ingest` into their
  pipeline (probably as a Claude skill that runs after document ingestion).
- A mapping from proof-engine-wiki findings → OmegaWiki `claims` entities,
  if the maintainers want findings to live in the knowledge graph rather
  than a separate review queue.
- Decisions about which registry(ies) to configure by default for the
  OmegaWiki user base.

If you're a maintainer or contributor, the marker contract and CLI surface
of `proof-engine-wiki` are stable as of v1.33.1 — happy to pair on a real
implementation. Open an issue at
[proof-engine](https://github.com/yaniv-golan/proof-engine/issues) or
mention the proof-engine-wiki package in an OmegaWiki issue.
