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

Scans a wiki directory. Re-verifies Type B citations (URLs rot). Flags
contradictions between wiki prose and registry verdicts. Reports stale
proofs (Confidence below threshold, or generated more than N days ago).

## Registry-only mode

Add `--registry-only` to both commands to skip generation entirely.
Useful for CI: if every `{{prove:}}` claim already has a registered proof,
ingest/lint runs offline and quickly.
