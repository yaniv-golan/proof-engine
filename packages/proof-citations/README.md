# proof-citations

Verify scholarly citations: fetch URLs, resolve identifiers, compare bibliographic claims against authoritative registries, and confirm quoted text appears on the cited page.

Extracted from [Proof Engine](https://proofengine.info) — the same engine that powers the proof corpus on `proofengine.info`.

## Install

```bash
pip install proof-citations
```

Python 3.10+. Single hard dependency on `requests`; `pdfplumber` / `PyPDF2` are pulled in for PDF citations.

## What it does

LLMs (and humans) hallucinate citations. Real citation fraud is now sophisticated — papers cite a real PMID that resolves to a real paper, but the claimed journal/year/volume are forged. This package handles three tiers of verification:

| Tier | API | Catches |
|---|---|---|
| **Quote-on-page** | `verify_citation(url, quote)` | The quoted text isn't actually on the cited page (paraphrased, fabricated, retracted). |
| **Identifier resolution** | `resolve("pmid:12345")` | The identifier doesn't exist. |
| **Metadata comparison** | `verify_citation_record(identifier, expected)` | The identifier resolves to a *different* paper than the claim describes ("metadata chimera" fraud). |

All three return structured Python dicts and emit JSON for batch pipelines.

## Quick start

### Verify a quote on a page

```python
from proof_citations import verify_citation

r = verify_citation(
    "https://www.ncbi.nlm.nih.gov/pubmed/33538338",
    "Global Cancer Statistics 2020",
    fact_id="B1",
)
print(r["status"])  # "verified" | "partial" | "not_found" | "fetch_failed"
```

### Resolve an identifier to structured bibliographic metadata

```python
from proof_citations import resolve

record = resolve(("pmid", "33538338"))
print(record.title)         # "Global Cancer Statistics 2020..."
print(record.venue)         # "CA: a cancer journal for clinicians"
print(record.year)          # 2021
print(record.doi)           # "10.3322/caac.21660"
print(record.update_status) # None | "retracted" | "expression_of_concern" | "corrigendum"
```

Supported identifier types out of the box: `pmid`, `pmc`, `doi`, `arxiv`, `isbn`, `swhid`, `handle`, `url`. PubMed and PubMed Central both use the NCBI E-utilities JSON API (set `NCBI_API_KEY` for ~10 req/sec; default ~3). `pmc` resolves via `db=pmc` esummary; because that endpoint omits `pubtype` / `issn` / `lang`, the backend makes a best-effort follow-up `db=pubmed` call when an `articleids` PMID cross-reference is present, to enrich retraction status, ISSN, and language. DOIs route through DataCite first, Crossref on 404. arXiv and Open Library handled natively.

### Catch metadata-chimera fraud

```python
from proof_citations import verify_citation_record

r = verify_citation_record(("pmid", "23260561"), expected={
    "title": "Ureteroenteric anastomotic strictures after radical cystectomy",
    "journal": "J Urol",
    "year": 2023,                                 # ← forged: real year is 2013
    "doi": "10.1016/j.juro.2012.11.001",          # ← forged
})

print(r["status"])      # "metadata_chimera"
print(r["verdict"])     # "metadata_chimera"
for m in r["mismatches"]:
    print(f"  {m['field']}: claimed={m['claimed']!r} resolved={m['resolved']!r}")
# year: claimed=2023 resolved=2013
# doi:  claimed='10.1016/j.juro.2012.11.001' resolved='10.1016/j.juro.2012.09.034'
```

The pure comparator is also exposed:

```python
from proof_citations import compare_metadata, resolve

record = resolve(("pmid", "23260561"))
result = compare_metadata(record, expected={"title": "...", "year": 2023})
# result["verdict"] ∈ {"genuine", "metadata_chimera", "title_chimera", "partial_match", "no_expected"}
```

### Batch-audit a reference list (CLI)

```bash
proof-citations verify-records --input audit.json --output report.json --pretty
```

Input shape:

```json
{
  "references": [
    {"ref_id": "B1",
     "identifier": "pmid:33538338",
     "expected": {"title": "...", "journal": "...", "year": 2021, "doi": "..."}}
  ]
}
```

Emits per-reference verdicts plus a summary block (`total`, `by_status`, `verified`, `chimeras`, `unresolvable`). Exit code is 1 if any reference is anything other than `verified` or `resolved`. The CLI is the canonical entry point for batch audits — manuscript review, automated reference-list checks, post-publication audits.

### Verify a quote AND its bibliographic claim in one call (v1.40.0+)

For single facts where you have both a URL with structured identifier (PMID / DOI / arXiv) AND a quote, pass `expected_metadata` to `verify_citation` to run both checks:

```python
r = verify_citation(
    "https://pubmed.ncbi.nlm.nih.gov/33538338/",
    "Global Cancer Statistics 2020",
    fact_id="B1",
    expected_metadata={
        "title": "Global Cancer Statistics 2020",
        "journal": "CA: a cancer journal for clinicians",
        "year": 2021,
        "doi": "10.3322/caac.21660",
    },
)

# `status` continues to reflect the quote-on-page outcome only — meaning preserved from v1.34.x.
assert r["status"] == "verified"

# `metadata_result` (new in v1.40.0) carries the metadata-chimera check.
# Key is ALWAYS present in the return dict — value is None when expected_metadata isn't passed.
assert r["metadata_result"]["verdict"] == "genuine"

# Joint pass: compose explicitly when you want it.
joint_pass = r["status"] == "verified" and r["metadata_result"]["verdict"] == "genuine"
```

When the URL has no structured identifier (e.g., a plain blog URL), `metadata_result["status"]` is `"skipped_no_structured_identifier"` — OG-extraction from arbitrary pages is too noisy to compare against claimed bibliographic fields. Similarly, identifier types without a registered resolver backend yield `"skipped_no_resolver"`.

`verify_all_citations(empirical_facts, ...)` accepts `expected_metadata` as an optional per-fact dict field, with the same semantics.

**CLI policy:** the `proof-citations verify` subcommand stays quote-only; for batch metadata audits use `proof-citations verify-records --input audit.json` (the canonical batch path).

## Caching

Identifier resolution hits authoritative APIs that rate-limit (NCBI ~3 req/sec, Crossref polite-pool requires `mailto`, arXiv ≤1 req/3s). Two caches ship in the box:

```python
from proof_citations import resolve, FileCache, InMemoryCache

# Persistent file cache (default location: ~/.cache/proof-citations/cache.json)
cache = FileCache()
record = resolve(("pmid", "33538338"), cache=cache)

# In-memory cache (for tests, short-lived scripts)
record = resolve(("pmid", "33538338"), cache=InMemoryCache())
```

Caches implement a tiny `Cache` protocol (`get`, `put`) — bring your own if neither default fits.

## Polite HTTP

A shared `HTTPSession` is used by all backends. It sets a polite `User-Agent` (`proof-citations/{version} (https://proofengine.info/; mailto={email})` — satisfies Crossref's polite-pool policy and NCBI's `tool=` recommendation), honors `Retry-After` on 429s, and reuses a single TCP pool. Contact email comes from `PROOF_CITATIONS_CONTACT` env var; falls back to a placeholder.

```bash
export PROOF_CITATIONS_CONTACT=you@example.org
proof-citations verify-records --input audit.json
```

## Compatibility — what landed when

For min-version pinning. Each capability landed in a specific release:

| Capability | Since |
|---|---|
| `verify_citation(url, quote)` quote-on-page check | v1.28.0 (initial extraction) |
| `verify_all_citations(facts)` batch quote-on-page | v1.28.0 |
| `proof_citations.resolvers.*` identifier resolution (PMID, DOI, arXiv, ISBN, SWHID, Handle, URL) | v1.35.0 (called `.registry` until v1.39.0) |
| `ResolvedRecord`, `Author`, `Cache`/`FileCache`/`InMemoryCache`, `HTTPSession`, `ResolutionError`, `identify()` | v1.35.0 |
| `compare_metadata(resolved, expected)`, `verify_citation_record(identifier, expected)` | v1.36.0 |
| `proof-citations verify-records --input audit.json` CLI | v1.36.0 |
| `verify_citation(..., expected_metadata=...)` integrated path; `metadata_result` key in return dict | v1.40.0 |

If you're writing new code: pin `proof-citations>=1.40.0` to get all of the above.

## Public API surface

Top-level imports (the stable contract):

```python
from proof_citations import (
    # Quote-on-page verification (v1.28.0+ semantics preserved; v1.40.0 added optional expected_metadata=)
    verify_citation, verify_all_citations,
    # Identifier → ResolvedRecord
    resolve, identify,
    # Bibliographic-claim verification
    verify_citation_record, compare_metadata,
    # Types
    Author, ResolvedRecord, Cache, InMemoryCache, FileCache, HTTPSession,
    ResolutionError,
    # Backend extension
    register_backend,
)
```

**`verify_all_citations` vs `verify-records`** — both do "batch verification," but at different layers and via different inputs:

- `verify_all_citations(empirical_facts)` is the **library function** for batch quote-on-page verification (optionally with `expected_metadata` per fact). Inputs are a Python dict of `{fact_id: {url, quote, expected_metadata?, …}}`. Used inside proof scripts (`proof.py`) and as a programmatic API.
- `proof-citations verify-records --input audit.json` is the **CLI subcommand** for batch *bibliographic-claim* audits. Inputs are a JSON file with `{references: [{ref_id, identifier, expected: {…}}]}`. No quote-on-page check — pure metadata-comparison. Used for manuscript review / post-publication audits where the goal is "are these citations real?"

Backend submodules (`proof_citations.resolvers.pubmed` — covers both `pmid` and `pmc` — `.doi`, `.arxiv`, `.isbn`, `.swhid`, `.handle`, `.url`) are accessible for direct use but the dispatch via `resolve()` is the supported entry point.

## Adding a custom backend

```python
from proof_citations import register_backend, ResolvedRecord
from proof_citations.resolvers.base import now_iso

def resolve_my_thing(value, *, session):
    resp = session.get(f"https://my.registry.invalid/api/{value}")
    return ResolvedRecord(
        identifier_type="my_thing", identifier_value=value,
        canonical_url=f"https://my.registry.invalid/{value}",
        title=resp.json()["title"],
        resolved_at=now_iso(),
        source_api="my.registry.invalid",
    )

register_backend("my_thing", resolve_my_thing)
record = resolve(("my_thing", "abc"))
```

## A note on naming — `resolvers` vs. "Registry Protocol"

There are two unrelated "registry" things in the Proof Engine ecosystem; this package's submodule used to be one of them and was renamed in v1.39.0 to remove the collision:

- **`proof_citations.resolvers`** (this package) — Python module for resolving identifiers (PMID/DOI/arXiv/…) to bibliographic records via authoritative APIs. Returns `ResolvedRecord` dataclasses.
- **Registry Protocol** — JSON-over-HTTPS spec (`docs/registry-protocol.md` in the parent repo) for a *catalog of proofs*. Implemented by the separately-published [`proof-engine-registry`](https://pypi.org/project/proof-engine-registry/) package and the `proof-registry serve` CLI. Returns proof verdicts + DOIs.

Different concepts, different packages, no shared code. The asymmetry in the names is intentional after the v1.39.0 rename.

## Errors

`ResolutionError` carries a `kind` attribute so downstream code can branch on failure mode without parsing exception messages:

```python
from proof_citations import resolve, ResolutionError

try:
    record = resolve(("pmid", "99999999"))
except ResolutionError as e:
    if e.kind == "not_found":     # identifier doesn't exist
        ...
    elif e.kind == "rate_limited": # 429 — back off and retry with NCBI_API_KEY
        ...
    elif e.kind == "fetch_failed": # network/timeout, retries exhausted
        ...
    elif e.kind == "malformed_response":
        ...
```

## Status

Used by the Proof Engine to verify the proof corpus at `proofengine.info`, and as a standalone audit tool for external reference-list audits (manuscripts, post-publication reviews of LLM-generated bibliographies). See the [Proof Engine repo](https://github.com/yaniv-golan/proof-engine) for the parent project.

## License

MIT.
