# Bundled Scripts API Reference

Detailed signatures for the most commonly-used functions in `scripts/`. Read at **Step 3** (Write the Proof Code) when you need exact argument names, return types, or modes.

For high-level purpose and which script handles which Hardening Rule, see the Bundled Scripts table in [SKILL.md](../SKILL.md#bundled-scripts).

## Import pattern

Every proof script begins with:

```python
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        if os.path.isdir(os.path.join(_d, "proof-engine", "skills", "proof-engine", "scripts")):
            PROOF_ENGINE_ROOT = os.path.join(_d, "proof-engine", "skills", "proof-engine")
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")
sys.path.insert(0, PROOF_ENGINE_ROOT)
```

**Resolution order:** (1) `PROOF_ENGINE_ROOT` env var if set — Binder and site-publishing tools set it explicitly; (2) walk up from proof.py's directory until `proof-engine/skills/proof-engine/scripts/` is found — makes the published proof portable to any clone of the repo; (3) raise a clear `RuntimeError`. Do NOT replace the block with a hardcoded absolute path — it leaks the generating agent's filesystem and doesn't work anywhere else.

## computations.py

```python
cross_check(value_a, value_b, tolerance=0.01, mode="absolute", label=None) -> bool
#   mode="absolute": |a - b| <= tolerance
#   mode="relative": |a - b| / max(|a|, |b|) <= tolerance

compute_percentage_change(old_value, new_value, label=None, mode="increase") -> float
#   mode="increase": (new - old) / old * 100
#   mode="decline":  (1 - old / new) * 100   (purchasing-power decline)

explain_calc(expr_str, scope, label=None) -> object
#   Prints symbolic -> substituted -> result. RETURNS the computed value.

compare(value, op_str, threshold, label=None) -> bool
#   Prints "{label}: {value} {op_str} {threshold} = {result}".
#   Label defaults to "compare".

apply_verdict_qualifier(base_verdict, any_unverified) -> str
#   Validates base_verdict, applies "(with unverified citations)" only to
#   PROVED, DISPROVED, SUPPORTED. PARTIALLY VERIFIED and UNDETERMINED pass through.
```

## proof_summary.py

`ProofSummaryBuilder` is the **primary path** for building `proof.json`. It produces `format_version: 3`, validates against the JSON schema, and emits the `=== PROOF SUMMARY (JSON) ===` marker.

```python
ProofSummaryBuilder(claim_natural, claim_formal, generator=None)

builder.add_empirical_fact(fact_id, label=, source_name=, source_url=, source_quote=)
builder.set_verification(fact_id, status=, method=, ...)
builder.set_extraction(fact_id, value=, value_in_quote=, ...)
builder.add_computed_fact(fact_id, label=, method=, result=, depends_on=[])
builder.add_cross_check(description=, fact_ids=, agreement=)
builder.add_adversarial_check(question=, verification_performed=, finding=, breaks_proof=)
builder.set_verdict(base_verdict, any_unverified=False, reason=None)
builder.set_key_results(**kwargs)
builder.emit()  # validates and prints JSON
```

The older `emit_proof_summary()` in `computations.py` is a legacy fallback that produces v2-shape JSON — do not use it for new proofs.

## verify_citations.py

```python
build_citation_detail(fact_registry, citation_results, empirical_facts) -> dict
#   Stitches FACT_REGISTRY + verification results + empirical_facts entries
#   into the citations[] block expected by ProofSummaryBuilder.

verify_data_values(url, data_values, fact_id, timeout=15, snapshot=None) -> dict
#   Fetches page and confirms each value string appears.
#   Returns {key: {found, value, fetch_mode}}.
```

## v1.35+ APIs in the `proof_citations` package

The bundled `scripts/` above are skill-internal shims preserved for backwards
compatibility. The
[`proof-citations` package](https://pypi.org/project/proof-citations/) exposes
a richer set of APIs directly — reach for these when writing new proofs that
cite identifier-bearing sources (PMID, DOI, arXiv, …):

```python
from proof_citations import (
    identify,                    # URL/string → ("pmid", "12345") / ("doi", "10.x/y") / …
    resolve,                     # identifier → ResolvedRecord (canonical bibliographic record)
    compare_metadata,            # ResolvedRecord vs claimed dict → per-field verdict
    verify_citation_record,      # high-level: resolve + compare in one call
    verify_citation,             # quote-on-page; v1.40+ accepts expected_metadata= for joint check
    ResolvedRecord, Author,      # types
    InMemoryCache, FileCache,    # default caches; resolve(..., cache=cache)
    ResolutionError,             # with `.kind` ∈ {not_found, fetch_failed, rate_limited, malformed_response}
)
```

When to use which:

| Goal | API |
|---|---|
| Verify a quoted passage on a cited page | `verify_citation(url, quote, fact_id)` (existing) |
| Verify quote AND that the cited identifier resolves to the claimed paper | `verify_citation(url, quote, fact_id, expected_metadata={...})` (v1.40+) |
| Verify only that an identifier resolves to the claimed paper (no quote) | `verify_citation_record(("pmid", "12345"), expected={...})` |
| Get the canonical bibliographic record for an identifier | `resolve(("pmid", "12345"))` |
| Batch-audit a list of references for citation fabrication | `proof-citations verify-records --input refs.json` (CLI) |

See [`packages/proof-citations/README.md`](../../../../packages/proof-citations/README.md)
for full signatures, return shapes, error model, and worked examples.
