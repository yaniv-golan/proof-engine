# Empirical Proof Template (Date/Age Claims)

> You are reading one template. See [proof-templates.md](proof-templates.md) for the full index and selection guidance.

A well-formed proof script has this structure. The structural elements (FACT_REGISTRY, JSON summary block, required JSON fields) are the contract. Variable names and specific logic are illustrative — adapt them to the claim being proved.

```python
"""
Proof: [claim text]
Generated: [date]
"""
import os
import sys

# Path to proof-engine scripts directory (the directory containing SKILL.md).
# In Claude Code, replace with the resolved value of ${CLAUDE_SKILL_DIR}.
# In standalone use, set to the absolute path of the skills/proof-engine directory.
PROOF_ENGINE_ROOT = "..."  # LLM fills this with the actual path at proof-writing time
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

# --- STRUCTURAL IMPORTS (always needed) ---
from scripts.smart_extract import normalize_unicode, verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail, verify_data_values
from scripts.computations import compare, explain_calc, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# --- CLAIM-SPECIFIC IMPORTS (adapt to your proof) ---
from scripts.extract_values import parse_date_from_quote
from scripts.computations import compute_age, DAYS_PER_GREGORIAN_YEAR, days_to_years

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "property": "...",
    "operator": ">",
    "operator_note": "...",
    "threshold": ...,
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "source_a", "label": "...one-line description..."},
    "B2": {"key": "source_b", "label": "...one-line description..."},
    "A1": {"label": "...one-line description...", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS
empirical_facts = {
    "source_a": {
        "quote": "...", "url": "...", "source_name": "...",
    },
    "source_b": {
        "quote": "...", "url": "...", "source_name": "...",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. VALUE EXTRACTION (Rule 1) — parse + verify_extraction
val_a = parse_date_from_quote(empirical_facts["source_a"]["quote"], "source_a")
val_a_in_quote = verify_extraction(val_a, empirical_facts["source_a"]["quote"], "B1")
val_b = parse_date_from_quote(empirical_facts["source_b"]["quote"], "source_b")
val_b_in_quote = verify_extraction(val_b, empirical_facts["source_b"]["quote"], "B2")

# 6. CROSS-CHECK (Rule 6)
assert val_a == val_b, f"Sources disagree: {val_a} vs {val_b}"

# 7. SYSTEM TIME (Rule 3)
PROOF_GENERATION_DATE = date(...)
today = date.today()

# 8. COMPUTATION (Rule 7)
age = compute_age(val_a, today)
approx_years = explain_calc("(today - val_a).days / DAYS_PER_GREGORIAN_YEAR", locals())

# 9. CLAIM EVALUATION
claim_holds = compare(age, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"])

# 10. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "Searched for ...",
        "finding": "...",  # If counter-evidence found AND breaks_proof=False: MUST include explicit rebuttal (Rule 5)
        "breaks_proof": False,  # If True, verdict forced to UNDETERMINED
    },
]

# 11. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    # Set to True if the source itself flags overlapping uncertainty ranges
    # for a comparative/superlative claim. See SKILL.md "Comparative claims
    # with source-acknowledged uncertainty."
    uncertainty_override = False  # change to True with documented reason if applicable

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif uncertainty_override:
        base_verdict = "UNDETERMINED"
    elif claim_holds:
        base_verdict = "PROVED"
    else:
        base_verdict = "DISPROVED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    builder.add_empirical_fact(
        "B1",
        label=FACT_REGISTRY["B1"]["label"],
        source_name=empirical_facts["source_a"]["source_name"],
        source_url=empirical_facts["source_a"]["url"],
        source_quote=empirical_facts["source_a"]["quote"],
    )
    cr_a = citation_results["source_a"]
    builder.set_verification(
        "B1",
        status=cr_a["status"],
        method=cr_a.get("method", "full_quote"),
        coverage_pct=cr_a.get("coverage_pct"),
        fetch_mode=cr_a.get("fetch_mode", "live"),
        credibility=cr_a.get("credibility", {}),
    )
    builder.set_extraction(
        "B1",
        value=str(val_a),
        value_in_quote=val_a_in_quote,
        quote_snippet=empirical_facts["source_a"]["quote"][:80],
    )

    builder.add_empirical_fact(
        "B2",
        label=FACT_REGISTRY["B2"]["label"],
        source_name=empirical_facts["source_b"]["source_name"],
        source_url=empirical_facts["source_b"]["url"],
        source_quote=empirical_facts["source_b"]["quote"],
    )
    cr_b = citation_results["source_b"]
    builder.set_verification(
        "B2",
        status=cr_b["status"],
        method=cr_b.get("method", "full_quote"),
        coverage_pct=cr_b.get("coverage_pct"),
        fetch_mode=cr_b.get("fetch_mode", "live"),
        credibility=cr_b.get("credibility", {}),
    )
    builder.set_extraction(
        "B2",
        value=str(val_b),
        value_in_quote=val_b_in_quote,
        quote_snippet=empirical_facts["source_b"]["quote"][:80],
    )

    builder.add_computed_fact(
        "A1",
        label=FACT_REGISTRY["A1"]["label"],
        method="compute_age()",
        result=age,
        depends_on=["B1"],
    )

    builder.add_cross_check(
        description="...",
        fact_ids=["B1", "B2"],
        values_compared=[str(val_a), str(val_b)],
        agreement=val_a == val_b,
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
        age=age,
        threshold=CLAIM_FORMAL["threshold"],
        operator=CLAIM_FORMAL["operator"],
        claim_holds=claim_holds,
    )
    builder.emit()
```
