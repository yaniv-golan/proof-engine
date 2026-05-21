# Compound CLAIM_FORMAL Template

> You are reading one template. See [proof-templates.md](proof-templates.md) for the full index and selection guidance.

For claims with multiple sub-claims joined by AND. Each sub-claim gets its own confirmation list, source count, and `compare()` evaluation. The compound verdict aggregates sub-claim results.

**When to use:** The claim contains AND or implies multiple independently verifiable conditions. Examples: "Israel withdrew from Gaza AND Hamas won the 2006 election," "Brain weight is 2% of body weight AND uses 20% of oxygen."

**Not supported:** Negated sub-claims (X BUT NOT Y) require per-sub-claim `proof_direction`, which this template doesn't model. For claims with negated parts, decompose into separate proofs — one affirmative, one disproof — using the qualitative template's `proof_direction` field.

```python
"""
Proof: [compound claim text]
Generated: [date]
"""
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        for _cand in (
            os.path.join(_d, "proof-engine", "skills", "proof-engine"),
            os.path.join(_d, "skills", "proof-engine"),
        ):
            if os.path.isdir(os.path.join(_cand, "scripts")):
                PROOF_ENGINE_ROOT = _cand
                break
        if PROOF_ENGINE_ROOT:
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 3, "operator_note": "..."},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 3, "operator_note": "..."},
    ],
    "compound_operator": "AND",  # only AND is supported; OR claims should be decomposed into separate proofs
    "operator_note": "All sub-claims must hold for the compound claim to be PROVED",
    # "subclaim_to_sources": {     # optional: add when using descriptive empirical_facts key names
    #     "SC1": ["source_key_a", "source_key_b"],  # list the empirical_facts keys for each sub-claim
    #     "SC2": ["source_key_c", "source_key_d"],
    # },
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "sc1_source_a", "label": "SC1 source A: ..."},
    "B2": {"key": "sc1_source_b", "label": "SC1 source B: ..."},
    "B3": {"key": "sc2_source_a", "label": "SC2 source A: ..."},
    "B4": {"key": "sc2_source_b", "label": "SC2 source B: ..."},
    "A1": {"label": "SC1 source count", "method": None, "result": None},
    "A2": {"label": "SC2 source count", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — grouped by sub-claim
empirical_facts = {
    "sc1_source_a": {"quote": "...", "url": "...", "source_name": "..."},
    "sc1_source_b": {"quote": "...", "url": "...", "source_name": "..."},
    "sc2_source_a": {"quote": "...", "url": "...", "source_name": "..."},
    "sc2_source_b": {"quote": "...", "url": "...", "source_name": "..."},
}

# 3b. SNAPSHOT FALLBACK — for sources that block automated fetches
# Two approaches depending on source access:
#
# PUBLIC sources that block bots (PMC, .gov with JS rendering):
#   Use inline "snapshot" — content is public, safe to commit.
#
# PAYWALLED sources (Nature, Springer, Elsevier, Wiley):
#   Use "snapshot_file" pointing to snapshots/ directory (.gitignored).
#   This keeps copyrighted content out of committed proof.py.
#   See environment-and-sources.md "Handling Paywalled Sources" for details.

_PROOF_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_snapshot(fname):
    fpath = os.path.join(_PROOF_DIR, fname)
    try:
        with open(fpath) as f:
            return f.read()
    except FileNotFoundError:
        return None

# Public source (PMC) — inline snapshot is fine:
#   "sc1_source_a": {
#       "quote": "...", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC...",
#       "source_name": "...",
#       "snapshot": _load_snapshot("pmc_source_a.html"),
#       "snapshot_source": "public:pre_fetched",
#   },
#
# Paywalled source — use snapshot_file (content stays in .gitignored snapshots/):
#   "sc1_source_b": {
#       "quote": "...", "url": "https://nature.com/articles/...",
#       "source_name": "...",
#       "snapshot_file": "snapshots/B2_snapshot.txt",
#       "snapshot_source": "paywalled:user_provided",
#   },

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

# 6. PER-SUB-CLAIM EVALUATION — each uses compare()
sc1_holds = compare(n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
                    label="SC1: " + CLAIM_FORMAL["sub_claims"][0]["property"])
sc2_holds = compare(n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
                    label="SC2: " + CLAIM_FORMAL["sub_claims"][1]["property"])

# 7. COMPOUND EVALUATION
n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# 8. COI FLAGS — per sub-claim, defined before verdict
sc1_coi_flags = [
    # Populate during proof writing. Empty list if no COI identified.
]
sc2_coi_flags = [
    # Populate during proof writing. Empty list if no COI identified.
]

# 9. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "Searched for ...",
        "finding": "...",  # If counter-evidence found AND breaks_proof=False: MUST include explicit rebuttal (Rule 5)
        "breaks_proof": False,  # If True, verdict forced to UNDETERMINED
    },
]

# 10. VERDICT — handles mixed results, proof direction, and unverified citations
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"

    # Per-sub-claim COI gate (Rule 6)
    sc1_confirmed_keys = {k for k in sc1_keys
                          if citation_results[k]["status"] in COUNTABLE_STATUSES}
    sc1_coi_favorable = {f["source_key"] for f in sc1_coi_flags
                         if f["direction"] == "favorable_to_subject"
                         and f["source_key"] in sc1_confirmed_keys}
    sc1_coi_unfavorable = {f["source_key"] for f in sc1_coi_flags
                           if f["direction"] == "unfavorable_to_subject"
                           and f["source_key"] in sc1_confirmed_keys}
    sc1_coi_majority = max(len(sc1_coi_favorable), len(sc1_coi_unfavorable)) if sc1_coi_flags else 0
    sc1_threshold = CLAIM_FORMAL["sub_claims"][0]["threshold"]
    sc1_coi_override = n_sc1 >= sc1_threshold and sc1_coi_majority > n_sc1 / 2

    sc2_confirmed_keys = {k for k in sc2_keys
                          if citation_results[k]["status"] in COUNTABLE_STATUSES}
    sc2_coi_favorable = {f["source_key"] for f in sc2_coi_flags
                         if f["direction"] == "favorable_to_subject"
                         and f["source_key"] in sc2_confirmed_keys}
    sc2_coi_unfavorable = {f["source_key"] for f in sc2_coi_flags
                           if f["direction"] == "unfavorable_to_subject"
                           and f["source_key"] in sc2_confirmed_keys}
    sc2_coi_majority = max(len(sc2_coi_favorable), len(sc2_coi_unfavorable)) if sc2_coi_flags else 0
    sc2_threshold = CLAIM_FORMAL["sub_claims"][1]["threshold"]
    sc2_coi_override = n_sc2 >= sc2_threshold and sc2_coi_majority > n_sc2 / 2

    any_coi_override = sc1_coi_override or sc2_coi_override

    # Contested qualifier override: SC1 holds + SC2 fails → DISPROVED
    # (assertion exists but the epistemic qualifier is not warranted).
    # For non-contested-qualifier compounds, set is_contested_qualifier = False
    # and this branch is skipped.
    is_contested_qualifier = "qualifier" in CLAIM_FORMAL.get("operator_note", "").lower()

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif any_coi_override:
        base_verdict = "UNDETERMINED"
    elif is_contested_qualifier and sc1_holds and not sc2_holds:
        base_verdict = "DISPROVED"
    elif not claim_holds and n_holding > 0:
        base_verdict = "PARTIALLY VERIFIED"
    elif claim_holds:
        base_verdict = "DISPROVED" if is_disproof else "PROVED"
    elif not claim_holds and n_holding == 0:
        base_verdict = "UNDETERMINED"
    else:
        base_verdict = "UNDETERMINED"  # defensive fallback
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        ef = empirical_facts[ef_key]
        cr = citation_results.get(ef_key, {})
        sub_claim = "SC1" if ef_key in sc1_keys else "SC2"
        builder.add_empirical_fact(
            fid,
            label=info["label"],
            source_name=ef["source_name"],
            source_url=ef["url"],
            source_quote=ef["quote"],
            sub_claim=sub_claim,
        )
        builder.set_verification(
            fid,
            status=cr.get("status", "unknown"),
            method=cr.get("method", "full_quote"),
            coverage_pct=cr.get("coverage_pct"),
            fetch_mode=cr.get("fetch_mode", "live"),
            credibility=cr.get("credibility", {}),
        )
        builder.set_extraction(
            fid,
            value=cr.get("status", "unknown"),
            value_in_quote=cr.get("status") in COUNTABLE_STATUSES,
            quote_snippet=ef["quote"][:80],
        )

    sc1_fact_ids = [fid for fid, info in FACT_REGISTRY.items()
                    if fid.startswith("B") and info["key"] in sc1_keys]
    sc2_fact_ids = [fid for fid, info in FACT_REGISTRY.items()
                    if fid.startswith("B") and info["key"] in sc2_keys]

    builder.add_computed_fact(
        "A1",
        label="SC1 source count",
        method=f"count(verified sc1 citations) = {n_sc1}",
        result=n_sc1,
        depends_on=sc1_fact_ids,
        sub_claim="SC1",
    )
    builder.add_computed_fact(
        "A2",
        label="SC2 source count",
        method=f"count(verified sc2 citations) = {n_sc2}",
        result=n_sc2,
        depends_on=sc2_fact_ids,
        sub_claim="SC2",
    )

    builder.add_cross_check(
        description="SC1: independent sources consulted",
        fact_ids=sc1_fact_ids,
        n_sources_consulted=len(sc1_keys),
        n_sources_verified=n_sc1,
        sources={k: citation_results[k]["status"] for k in sc1_keys},
        independence_note="Sources from different publications",
        coi_flags=sc1_coi_flags,
        agreement=sc1_holds,
    )
    builder.add_cross_check(
        description="SC2: independent sources consulted",
        fact_ids=sc2_fact_ids,
        n_sources_consulted=len(sc2_keys),
        n_sources_verified=n_sc2,
        sources={k: citation_results[k]["status"] for k in sc2_keys},
        independence_note="Sources from different publications",
        coi_flags=sc2_coi_flags,
        agreement=sc2_holds,
    )

    builder.add_sub_claim_result(
        id="SC1", n_confirming=n_sc1,
        threshold=CLAIM_FORMAL["sub_claims"][0]["threshold"], holds=sc1_holds,
    )
    builder.add_sub_claim_result(
        id="SC2", n_confirming=n_sc2,
        threshold=CLAIM_FORMAL["sub_claims"][1]["threshold"], holds=sc2_holds,
    )

    for ac in adversarial_checks:
        builder.add_adversarial_check(
            question=ac["question"],
            verification_performed=ac["verification_performed"],
            finding=ac["finding"],
            breaks_proof=ac["breaks_proof"],
        )

    builder.set_verdict(base_verdict, any_unverified=any_unverified)
    builder.set_key_results(
        n_holding=n_holding,
        n_total=n_total,
        claim_holds=claim_holds,
    )
    builder.emit()
```

**Key design points:**
- `PARTIALLY VERIFIED` is checked BEFORE the `claim_holds` branches — mixed results short-circuit the verdict.
- For **contested qualifier** claims: `is_contested_qualifier` auto-detects from `operator_note` and inserts a `sc1_holds and not sc2_holds → DISPROVED` branch before `PARTIALLY VERIFIED`. This ensures "assertion exists but qualifier is unwarranted" produces DISPROVED, not PARTIALLY VERIFIED. Standard compound claims are unaffected.
- `UNDETERMINED` when no sub-claims meet threshold — for source-counting proofs, insufficient evidence is not disproof.
- Per-sub-claim `compare()` calls use labels, so the computation trace is self-documenting.
- `any_unverified` modifies PROVED → PROVED (with unverified citations). For PARTIALLY VERIFIED and UNDETERMINED, citation status is documented in proof.md's Conclusion section rather than changing the verdict label — those verdicts already signal incompleteness.
- `sub_claim_results` in the JSON summary gives downstream tooling per-SC detail.
- Only `AND` compounds are supported. For OR claims ("X or Y is true"), decompose into separate proofs — an OR compound where either sub-claim suffices is just two independent proofs.

**Adapting for numeric compound claims:** Replace the citation-counting step with `parse_number_from_quote()` / `verify_data_values()` per the Numeric/Table template. The compound evaluation (steps 6-7) stays the same — only the per-sub-claim counting (step 5) changes.

**Sub-claims with no possible supporting sources:** Keep the sub-claim in `CLAIM_FORMAL["sub_claims"]` with its full structure — do not remove it from `n_total`. Set its `n_confirming` to 0 via an empty confirmations list (not a hardcoded literal). The compound verdict will naturally produce `PARTIALLY VERIFIED` (some hold, some don't) or `UNDETERMINED` (none hold). Removing a failing sub-claim from the denominator would change the claim's meaning and could turn a failing proof into a passing one. Document the sub-claim's failure and the evidence for it (e.g., adversarial findings) in the proof's adversarial_checks section.

### Adaptation: Contested Qualifier Claims

When a claim bundles a factual assertion with an epistemic qualifier ("verified," "confirmed," "proven," "established," "debunked"), decompose into:

- **SC1 (provenance):** Do the underlying assertions exist and originate from an identifiable source? SC1 means "the assertion exists and can be traced to an identifiable source" — NOT "the assertion is true."
- **SC2 (epistemic):** Has the assertion been independently verified/confirmed/etc. as claimed? SC2 is a meta-claim requiring different sources than SC1: independent audits, judicial findings, investigative bodies — entities that *evaluated* the evidence, not just reported it.

**Empty SC2 is expected.** For many contested qualifier claims, no sources exist that *confirm* independent verification — the qualifier simply hasn't been warranted. In this case, `sc2_keys` is empty and `n_sc2 = 0`, which causes SC2 to fail naturally. This is the normal pattern, not an error. Sources that *reject* the qualifier (e.g., an independent review finding "claims not substantiated") belong in `adversarial_checks`, not in SC2's `empirical_facts` — they are counter-evidence, not confirming sources.

**COI gate and provenance (SC1).** COI does not undermine provenance sources — a biased or interested party can still confirm that an allegation was made. For SC1 (provenance), bypass the COI gate:

```python
# In the COI gate section, replace the standard sc1_coi_override line with:
sc1_coi_override = False  # Provenance: COI does not invalidate "allegation was made"
```

COI is especially critical for SC2 — apply Rule 6 COI check rigorously.

**Verdict mapping** follows the compound template's existing logic:

| SC1 | SC2 | Verdict |
|-----|-----|---------|
| holds | holds | PROVED (assertion exists and qualifier is warranted) |
| holds | fails | DISPROVED (assertion exists but qualifier is false) |
| fails | fails | UNDETERMINED (insufficient evidence either way) |

Note: SC1-fails/SC2-holds is not a realistic state for this pattern — if the assertion's provenance can't be established (SC1 fails), there's nothing for SC2 to verify. The compound template's standard `n_holding > 0` → PARTIALLY VERIFIED branch handles this edge case if it ever arises, but no special logic is needed.

If SC1 fails because sources actively deny the assertion was ever made (not just absence of evidence), document this in `adversarial_checks` with `breaks_proof: True`. The `any_breaks` check at the top of the verdict block will force UNDETERMINED, and the proof.md Conclusion section should explain that the assertion's provenance itself is disputed.

**Example CLAIM_FORMAL:**

```python
CLAIM_FORMAL = {
    "subject": "...",
    "sub_claims": [
        {"id": "SC1", "property": "assertion originates from identifiable source",
         "operator": ">=", "threshold": 2,
         "operator_note": "SC1 checks provenance — does the assertion exist?"},
        {"id": "SC2", "property": "assertion independently verified as claimed",
         "operator": ">=", "threshold": 3,
         "operator_note": "SC2 checks the epistemic qualifier — was it independently verified?"},
    ],
    "compound_operator": "AND",
    "operator_note": (
        "The claim uses the qualifier '[qualifier]'. SC1 checks provenance "
        "(the assertion exists), SC2 checks the qualifier (independently verified). "
        "Both must hold for the claim to be PROVED."
    ),
}
```
