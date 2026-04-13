# Numeric/Table Data Proof Template

> You are reading one template. See [proof-templates.md](proof-templates.md) for the full index and selection guidance.

For proofs where the primary evidence is numeric data from HTML tables (CPI, GDP, population).
Uses `data_values` for table numbers and `verify_data_values()` to confirm they appear on the page.

**Do NOT do this** — pseudo-quote fields with bare numeric literals are circular verification:
```python
# BAD — validator will reject this
empirical_facts = {
    "source_a": {
        "quote": "CPI data is published by the BLS.",
        "url": "...",
        "cpi_1913_quote": "9.883",      # authored literal, not a real quote
        "cpi_2024_quote": "313.689",     # authored literal, not a real quote
    },
}
val = parse_number_from_quote(empirical_facts["source_a"]["cpi_1913_quote"], ...)
verify_extraction(val, empirical_facts["source_a"]["cpi_1913_quote"], ...)  # circular!
```

Instead, use `data_values` + `verify_data_values()` as shown below:

```python
"""
Proof: [claim text]
Generated: [date]
"""
import os
import sys

PROOF_ENGINE_ROOT = "..."
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.smart_extract import normalize_unicode
from scripts.verify_citations import verify_all_citations, build_citation_detail, verify_data_values
from scripts.extract_values import parse_number_from_quote
from scripts.computations import compare, explain_calc, cross_check, compute_percentage_change, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

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
    "B1": {"key": "source_a", "label": "Source A: [description] ([site] sourced from [authority])"},
    "B2": {"key": "source_b", "label": "Source B: [description] ([site] sourced from [authority])"},
    "A1": {"label": "[computation description]", "method": None, "result": None},
    "A2": {"label": "[cross-check computation]", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — quote verifies source authority, data_values hold the numbers
empirical_facts = {
    "source_a": {
        "quote": "...",  # prose that confirms this source publishes the data
        "url": "...",
        "source_name": "... (sourced from [authority])",
        "data_values": {"val_1913": "9.883", "val_2024": "313.689"},
    },
    "source_b": {
        "quote": "...",
        "url": "...",
        "source_name": "... (sourced from [authority])",
        "data_values": {"val_1913": "9.9", "val_2024": "313.689"},
    },
}

# 4. CITATION VERIFICATION (Rule 2) — verifies quotes
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. DATA VALUE VERIFICATION — confirms numbers appear on page
dv_results_a = verify_data_values(
    empirical_facts["source_a"]["url"],
    empirical_facts["source_a"]["data_values"],
    "B1",
)
dv_results_b = verify_data_values(
    empirical_facts["source_b"]["url"],
    empirical_facts["source_b"]["data_values"],
    "B2",
)

# 6. VALUE EXTRACTION — parse from data_values strings (no verify_extraction needed)
val_1913_a = parse_number_from_quote(empirical_facts["source_a"]["data_values"]["val_1913"], r"([\d.]+)", "B1_val_1913")
val_2024_a = parse_number_from_quote(empirical_facts["source_a"]["data_values"]["val_2024"], r"([\d.]+)", "B1_val_2024")
val_1913_b = parse_number_from_quote(empirical_facts["source_b"]["data_values"]["val_1913"], r"([\d.]+)", "B2_val_1913")
val_2024_b = parse_number_from_quote(empirical_facts["source_b"]["data_values"]["val_2024"], r"([\d.]+)", "B2_val_2024")

# 7. CROSS-CHECK (Rule 6) — independent sources must agree within tolerance
# Use mode="relative" when comparing values that may be rounded differently
cross_check(val_1913_a, val_1913_b, tolerance=0.02, mode="relative", label="1913 value cross-check")
cross_check(val_2024_a, val_2024_b, tolerance=0.001, mode="relative", label="2024 value cross-check")

# 8. COMPUTATION (Rule 7)
# For purchasing power / inflation: use compute_percentage_change(old, new, mode="decline")
# For growth rates: use compute_percentage_change(old, new) (default mode="increase")
decline_a = compute_percentage_change(val_1913_a, val_2024_a, mode="decline", label="decline_source_a")
decline_b = compute_percentage_change(val_1913_b, val_2024_b, mode="decline", label="decline_source_b")

# 9. CLAIM EVALUATION
claim_holds = compare(decline_a, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"])

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
        value=f"val_1913={val_1913_a}, val_2024={val_2024_a}",
        value_in_quote=True,
        data_values_verified=all(v.get("found") for v in dv_results_a.values()),
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
        value=f"val_1913={val_1913_b}, val_2024={val_2024_b}",
        value_in_quote=True,
        data_values_verified=all(v.get("found") for v in dv_results_b.values()),
    )

    builder.add_computed_fact(
        "A1",
        label=FACT_REGISTRY["A1"]["label"],
        method="compute_percentage_change(mode='decline')",
        result=f"{decline_a:.4f}%",
        depends_on=["B1"],
    )
    builder.add_computed_fact(
        "A2",
        label=FACT_REGISTRY["A2"]["label"],
        method="compute_percentage_change(mode='decline') [cross-check]",
        result=f"{decline_b:.4f}%",
        depends_on=["B2"],
    )

    builder.add_cross_check(
        description="1913 values",
        fact_ids=["B1", "B2"],
        values_compared=[str(val_1913_a), str(val_1913_b)],
        agreement=True,
        tolerance="2% relative",
    )
    builder.add_cross_check(
        description="2024 values",
        fact_ids=["B1", "B2"],
        values_compared=[str(val_2024_a), str(val_2024_b)],
        agreement=True,
        tolerance="0.1% relative",
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
        decline_source_a=decline_a,
        decline_source_b=decline_b,
        threshold=CLAIM_FORMAL["threshold"],
        operator=CLAIM_FORMAL["operator"],
        claim_holds=claim_holds,
    )
    builder.emit()
```
