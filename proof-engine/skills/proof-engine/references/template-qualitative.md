# Qualitative Consensus Proof Template

> You are reading one template. See [proof-templates.md](proof-templates.md) for the full index and selection guidance.

For claims where evidence is qualitative ("sources agree X is true") rather than numeric. Uses citation verification status as the counting mechanism: a source counts as "confirmed" if its citation was successfully verified (status = `verified` or `partial`).

**When to use:** The claim's truth depends on expert/source agreement, not a numeric comparison. Examples: "The adult brain generates new neurons," "Humans only use 10% of their brain," "Coffee reduces diabetes risk."

**Key differences from numeric templates:**
- Source count is based on citation verification status, not keyword extraction
- `claim_holds` MUST use `compare()` — never hardcode `True` or `False`
- Adversarial sources go in `adversarial_checks` only — NOT in `empirical_facts`

```python
"""
Proof: [claim text]
Generated: [date]
"""
import os
import sys

PROOF_ENGINE_ROOT = "..."  # LLM fills this with the actual path at proof-writing time
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "property": "...",
    "operator": ">=",
    "operator_note": "...",
    "threshold": 3,            # min verified sources needed (see threshold guidance below)
    "proof_direction": "affirm",  # "affirm" or "disprove"
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "source_a", "label": "..."},
    "B2": {"key": "source_b", "label": "..."},
    "B3": {"key": "source_c", "label": "..."},
    "A1": {"label": "Verified source count", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that confirm the proof's conclusion
# For affirmative proofs: sources that AGREE with the claim
# For disproofs: sources that REJECT the claim (confirm it's false)
# IMPORTANT: adversarial sources go in adversarial_checks, NOT here.
empirical_facts = {
    "source_a": {
        "quote": "...", "url": "...", "source_name": "...",
    },
    "source_b": {
        "quote": "...", "url": "...", "source_name": "...",
    },
    "source_c": {
        "quote": "...", "url": "...", "source_name": "...",
    },
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
#   "source_a": {
#       "quote": "...", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC...",
#       "source_name": "...",
#       "snapshot": _load_snapshot("pmc_source_a.html"),
#       "snapshot_source": "public:pre_fetched",
#   },
#
# Paywalled source — use snapshot_file (content stays in .gitignored snapshots/):
#   "source_b": {
#       "quote": "...", "url": "https://nature.com/articles/...",
#       "source_name": "...",
#       "snapshot_file": "snapshots/B2_snapshot.txt",
#       "snapshot_source": "paywalled:user_provided",
#   },

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
# A source counts toward the threshold if its quote was found on the page
# (status = "verified" or "partial"). Sources with "not_found" or "fetch_failed"
# are excluded — we can't confirm the quote exists.
# Note: "partial" counts toward the threshold but still triggers the
# "with unverified citations" verdict variant (it's not fully verified).
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — MUST use compare(), never hardcode claim_holds
claim_holds = compare(n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                      label="verified source count vs threshold")

# 7. COI FLAGS — authored data, defined before verdict (like adversarial_checks)
# Populate during proof writing. Empty list if no COI identified.
coi_flags = [
    # Example:
    # {"source_key": "source_a", "coi_type": "organizational",
    #  "relationship": "Source is a subsidiary of the claim's subject",
    #  "direction": "favorable_to_subject", "severity": "direct"},
]

# 8. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "Searched for ...",
        "finding": "...",  # If counter-evidence found AND breaks_proof=False: MUST include explicit rebuttal (Rule 5)
        "breaks_proof": False,  # If True, verdict forced to UNDETERMINED
    },
]

# 9. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    # "partial" counts toward the threshold but is NOT fully verified —
    # only "verified" is clean. This preserves the existing semantics where
    # partial/fragment matches trigger "with unverified citations" verdicts.
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    # COI GATE (Rule 6) — after counting, before verdict
    confirmed_keys = {k for k in empirical_facts
                      if citation_results[k]["status"] in COUNTABLE_STATUSES}
    coi_favorable = {f["source_key"] for f in coi_flags
                     if f["direction"] == "favorable_to_subject"
                     and f["source_key"] in confirmed_keys}
    coi_unfavorable = {f["source_key"] for f in coi_flags
                       if f["direction"] == "unfavorable_to_subject"
                       and f["source_key"] in confirmed_keys}
    coi_majority = max(len(coi_favorable), len(coi_unfavorable)) if coi_flags else 0
    coi_override = n_confirmed >= CLAIM_FORMAL["threshold"] and coi_majority > n_confirmed / 2

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif coi_override:
        base_verdict = "UNDETERMINED"
    elif claim_holds:
        base_verdict = "DISPROVED" if is_disproof else "PROVED"
    else:
        base_verdict = "UNDETERMINED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        ef = empirical_facts[ef_key]
        cr = citation_results.get(ef_key, {})
        builder.add_empirical_fact(
            fid,
            label=info["label"],
            source_name=ef["source_name"],
            source_url=ef["url"],
            source_quote=ef["quote"],
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

    builder.add_computed_fact(
        "A1",
        label="Verified source count",
        method=f"count(verified citations) = {n_confirmed}",
        result=n_confirmed,
        depends_on=[fid for fid in FACT_REGISTRY if fid.startswith("B")],
    )

    # For qualitative proofs, cross_checks documents that multiple independent
    # sources were consulted and how many were successfully verified.
    builder.add_cross_check(
        description="Multiple independent sources consulted",
        fact_ids=[fid for fid in FACT_REGISTRY if fid.startswith("B")],
        n_sources_consulted=len(empirical_facts),
        n_sources_verified=n_confirmed,
        sources={k: citation_results[k]["status"] for k in empirical_facts},
        independence_note="Sources are from different publications/institutions",
        coi_flags=coi_flags,
        agreement=claim_holds,
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
        n_confirmed=n_confirmed,
        threshold=CLAIM_FORMAL["threshold"],
        operator=CLAIM_FORMAL["operator"],
        claim_holds=claim_holds,
    )
    builder.emit()
```

### Disproof variant

To disprove a claim (e.g., "Humans only use 10% of their brain"), use `proof_direction: "disprove"`. The counting logic is identical, but the semantic meaning of each collection **inverts**:

```python
CLAIM_FORMAL = {
    "subject": "...",
    "property": "...",
    "operator": ">=",
    "operator_note": "Claim is disproved when ≥ threshold authoritative sources reject it",
    "threshold": 3,
    "proof_direction": "disprove",   # "affirm" → "disprove"
}

# empirical_facts: sources that REJECT the claim (confirm it is false)
# e.g. for "humans use only 10% of their brain": include neuroscience sources
# that state the brain is active throughout, not just 10%.
empirical_facts = {
    "source_a": {
        "quote": "...",
        "rejection_statement": "...",  # verbatim phrase from quote that rejects the claim
        "url": "...",
        "source_name": "...",
    },
    "source_b": {
        "quote": "...",
        "rejection_statement": "...",
        "url": "...",
        "source_name": "...",
    },
    "source_c": {
        "quote": "...",
        "rejection_statement": "...",
        "url": "...",
        "source_name": "...",
    },
}
```

`n_confirmed` counts verified rejection sources. `compare(n_confirmed, ">=", 3)` returns `True` → `claim_holds = True` → verdict maps to **DISPROVED** (via `proof_direction`).

**Adversarial direction inverts too:** In `adversarial_checks`, search for sources that **support** the claim (i.e., sources arguing it might be true). For an affirmative proof you search for evidence against; for a disproof you search for evidence *for*. The question to ask: "Is there credible support for the claim I'm disproving?"

No keyword selection is needed — citation verification status is the counting mechanism.

**`rejection_statement` (required for disproof):** For each entry in `empirical_facts`, add a `rejection_statement` field containing the verbatim phrase from the quote that explicitly rejects the claim. Copy it character-for-character — do not paraphrase. Example: if the quote is *"There is no scientific evidence that humans eat spiders while sleeping,"* set `rejection_statement: "no scientific evidence"`. `validate_proof.py` warns when `rejection_statement` is absent and raises an issue when it is present but does not appear verbatim in the quote. If no phrase in the quote explicitly rejects the claim, the quote itself is too weak — find a different quote from the same page.

**Threshold and COI rules apply identically to disproof:** All threshold rules (including the `threshold: 1` prohibition and the conditions for reducing to `threshold: 2`) and all COI majority checks from the affirmative variant apply equally to disproof proofs. The proof direction does not relax these requirements — see the threshold and COI guidance in the affirmative variant section above.

### Adaptation notes

**Compound claims (X AND Y):** See the compound CLAIM_FORMAL variant below.

**Empirical consensus with numeric values:** When multiple sources agree on a specific number (e.g., "86 billion neurons"), use the Numeric/Table template instead — it handles numeric cross-checks better than keyword extraction.

**Citing structured/tabular data:** See the Numeric/Table Data template above. Key points:
- Quote verifies source authority; `data_values` hold the numbers
- Call `verify_data_values()` to confirm numbers appear on the source page
- Do NOT call `verify_extraction()` on data_values (circular)
- Use `cross_check()` with tolerance to compare across sources
- Use sub-IDs in extractions: `B1_val_1913`, `B1_val_2024`
