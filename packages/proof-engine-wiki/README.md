# proof-engine-wiki

Attach Proof Engine proofs to LLM-wiki claims.

## Install

    pip install proof-engine-wiki

## Marker syntax

Authors mark claims they want proven:

    The US dollar has {{prove: lost 15% of its purchasing power since 2020}}.

## Ingest

    proof-engine-wiki ingest PAGE.md

Extracts all `{{prove:}}` markers, looks up configured registries,
commissions a new proof only for misses, rewrites the file with inline
badges and links.

## Lint

    proof-engine-wiki lint WIKI_DIR/

Scans every `.md` file under the directory and reports:

- `unresolved_marker` — `{{prove:}}` markers in the page that haven't
  been resolved yet (run `ingest` to resolve them).
- `stale_proof` — embedded proof URLs that no longer respond to a HEAD
  request (the proof was retracted or the registry moved).

Pass `--skip-network` to suppress URL reachability checks (faster CI;
catches only `unresolved_marker`).

## Registry-only mode

Add `--registry-only` to `ingest` to skip new-proof commissioning
entirely. Useful for CI: if every `{{prove:}}` claim already has a
registered proof, ingest runs offline and quickly. Misses are reported,
not commissioned.
