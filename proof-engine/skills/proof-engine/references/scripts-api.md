# Bundled Scripts API Reference

Detailed signatures for the most commonly-used functions in `scripts/`. Read at **Step 3** (Write the Proof Code) when you need exact argument names, return types, or modes.

For high-level purpose and which script handles which Hardening Rule, see the Bundled Scripts table in [SKILL.md](../SKILL.md#bundled-scripts).

## Import pattern

Every proof script begins with:

```python
import os
import sys

_SKILL_EXCLUDED_DIRS = {".git", ".venv", "venv", ".tox", ".worktrees",
                        ".cache", ".idea", ".vscode", "node_modules",
                        "__pycache__", "site-packages", "dist", "build"}

def _is_valid_skill_root(p):
    return (os.path.isfile(os.path.join(p, "scripts", "verify_citations.py"))
            and os.path.isfile(os.path.join(p, "SKILL.md")))

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        for _cand in (
            os.path.join(_d, "proof-engine", "skills", "proof-engine"),
            os.path.join(_d, "skills", "proof-engine"),
        ):
            if _is_valid_skill_root(_cand):
                PROOF_ENGINE_ROOT = _cand
                break
        if PROOF_ENGINE_ROOT:
            break
        try:
            for _sib in os.listdir(_d):
                if _sib in _SKILL_EXCLUDED_DIRS:
                    continue
                _sib_path = os.path.join(_d, _sib)
                if not os.path.isdir(_sib_path):
                    continue
                for _cand in (
                    os.path.join(_sib_path, "skills", "proof-engine"),
                    os.path.join(_sib_path, "proof-engine", "skills", "proof-engine"),
                ):
                    if _is_valid_skill_root(_cand):
                        PROOF_ENGINE_ROOT = _cand
                        break
                if PROOF_ENGINE_ROOT:
                    break
                if _sib.startswith("."):
                    try:
                        for _sub in os.listdir(_sib_path):
                            if _sub in _SKILL_EXCLUDED_DIRS:
                                continue
                            _cand = os.path.join(_sib_path, _sub, "skills", "proof-engine")
                            if _is_valid_skill_root(_cand):
                                PROOF_ENGINE_ROOT = _cand
                                break
                    except OSError:
                        pass
                    if PROOF_ENGINE_ROOT:
                        break
        except OSError:
            pass
        if PROOF_ENGINE_ROOT:
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError(
            "PROOF_ENGINE_ROOT not set and skill dir not found via walk-up "
            f"or sibling search from {os.path.dirname(os.path.abspath(__file__))}. "
            "Set the env var explicitly: "
            "export PROOF_ENGINE_ROOT=/path/to/skills/proof-engine"
        )
sys.path.insert(0, PROOF_ENGINE_ROOT)
```

**Resolution order:**
1. **Env var:** `PROOF_ENGINE_ROOT` if set — Binder and site-publishing tools set it explicitly.
2. **Walk-up:** at each ancestor of `proof.py`, check `<ancestor>/proof-engine/skills/proof-engine/` (dev-repo layout) and `<ancestor>/skills/proof-engine/` (plugin install layout).
3. **Sibling search:** at each walk-up step, also descend each non-excluded sibling directory to depth 1; dotted siblings (e.g., `.remote-plugins`, `.devcontainer`) are descended to depth 2. This handles plugin/host layouts where `proof.py` (in `outputs/`) and the skill (in `.remote-plugins/<plugin_id>/skills/proof-engine`) sit in sibling trees, never above each other.
4. **Sentinel files:** a candidate is accepted only if it contains BOTH `scripts/verify_citations.py` AND `SKILL.md`. This keeps broad descent safe against false positives (vendored pip packages, git worktrees).
5. **Excluded dirs:** `.git`, `.venv`, `venv`, `.tox`, `.worktrees`, `.cache`, `.idea`, `.vscode`, `node_modules`, `__pycache__`, `site-packages`, `dist`, `build` are always skipped.
6. **Failure:** raise a `RuntimeError` with explicit `export PROOF_ENGINE_ROOT=...` instructions.

Do NOT replace the block with a hardcoded absolute path — it leaks the generating agent's filesystem and doesn't work anywhere else.

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
verify_all_citations(empirical_facts, *,
                     wayback_fallback=False,
                     oa_lookup=True,
                     oa_lookup_budget_seconds=None,
                     skip_live_fetch=False,
                     prefer_snapshot=False) -> dict
#   Batch-verify every fact in empirical_facts. Returns
#   {fact_key: result_dict}. See verify_citation() docstring in
#   packages/proof-citations/src/proof_citations/verify.py for the
#   full per-fact result shape (status/method/coverage_pct/fetch_mode/
#   credibility/metadata_result).

build_citation_detail(fact_registry, citation_results, empirical_facts) -> dict
#   Stitches FACT_REGISTRY + verification results + empirical_facts entries
#   into the evidence block expected by ProofSummaryBuilder.

verify_data_values(url, data_values, fact_id, timeout=15, snapshot=None) -> dict
#   Fetches page and confirms each value string appears.
#   Returns {key: {found, value, fetch_mode}}.
```

### Snapshot-only fast path

The kwargs above shape how `verify_all_citations()` handles citations whose
source pages either block automated fetches or are paywalled. By default each
citation tries live fetch → snapshot → snapshot_file → Wayback Machine → OA
fallback (Unpaywall DOI lookup + variant fetch). For all-snapshot proofs
backed by blocked or paywalled domains, the default path wastes minutes per
fact on doomed live-fetch + OA-lookup attempts. Tune as follows:

| Kwarg | Effect | When to use |
|-------|--------|-------------|
| `skip_live_fetch=True` | Skip live fetch entirely; go straight to snapshot → snapshot_file → wayback. | Every citation in the proof has a snapshot; live domain is known to block bots. |
| `prefer_snapshot=True` | Try snapshot before live fetch; live remains the fallback if snapshot is empty. | Mixed — some citations might have snapshots, live works as a backup. |
| `oa_lookup=False` | Skip the Unpaywall OA-variant lookup entirely. | All snapshots are intact; no need to chase OA mirrors. |
| `oa_lookup_budget_seconds=N` | Cap total time across all OA fallback attempts. After N seconds, subsequent facts skip OA. | Mixed proofs where OA is occasionally useful but you don't want one slow lookup to dominate runtime. |

**Recipes:**

```python
# All-snapshot proof against blocked/paywalled domains (PMC, Nature, Frontiers):
citation_results = verify_all_citations(
    empirical_facts,
    skip_live_fetch=True,
    oa_lookup=False,
)
```

```python
# Snapshot-preferred with live fetch as fallback; bound total OA budget:
citation_results = verify_all_citations(
    empirical_facts,
    prefer_snapshot=True,
    oa_lookup_budget_seconds=30,
)
```

The same four kwargs are accepted by the per-call `verify_citation()`. The canonical signatures live in the function docstrings at `packages/proof-citations/src/proof_citations/verify.py` — keep that as source of truth; this section summarizes the practical recipes.

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
| Verify quote AND that the cited identifier resolves to the claimed paper | `verify_citation(url, quote, fact_id, expected_metadata={...})` |
| Verify only that an identifier resolves to the claimed paper (no quote) | `verify_citation_record(("pmid", "12345"), expected={...})` |
| Get the canonical bibliographic record for an identifier | `resolve(("pmid", "12345"))` |
| Batch-audit a list of references for citation fabrication | `proof-citations verify-records --input refs.json` (CLI) |

See [`packages/proof-citations/README.md`](../../../../packages/proof-citations/README.md)
for full signatures, return shapes, error model, and worked examples.
