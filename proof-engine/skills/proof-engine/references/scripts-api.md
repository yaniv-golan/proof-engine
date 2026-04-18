# Bundled Scripts API Reference

Detailed signatures for the most commonly-used functions in `scripts/`. Read at **Step 3** (Write the Proof Code) when you need exact argument names, return types, or modes.

For high-level purpose and which script handles which Hardening Rule, see the Bundled Scripts table in [SKILL.md](../SKILL.md#bundled-scripts).

## Import pattern

Every proof script begins with:

```python
import os
import sys
PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT", "${CLAUDE_SKILL_DIR}")  # hardcoded fallback replaced with actual path at proof-writing time
sys.path.insert(0, PROOF_ENGINE_ROOT)
```

The hardcoded fallback is the absolute path at proof-writing time (resolves at generation). The env-var override lets the Binder launcher and other re-runners set the correct path for their environment without touching the published proof.

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
