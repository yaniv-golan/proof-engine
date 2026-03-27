# Proof Templates

Read this at **Step 3** when writing proof code. Choose the template that matches your claim type.

## Empirical Proof Template (date/age claims)

A well-formed proof script has this structure. The structural elements (FACT_REGISTRY, JSON summary block, required JSON fields) are the contract. Variable names and specific logic are illustrative — adapt them to the claim being proved.

```python
"""
Proof: [claim text]
Generated: [date]
"""
import json
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
from scripts.computations import compare, explain_calc

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
        "verification_performed": "...",
        "finding": "...",
        "breaks_proof": False,
    },
]

# 11. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    if claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds:
        verdict = "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = "compute_age()"
    FACT_REGISTRY["A1"]["result"] = str(age)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": str(val_a),
            "value_in_quote": val_a_in_quote,
            "quote_snippet": empirical_facts["source_a"]["quote"][:80],
        },
        "B2": {
            "value": str(val_b),
            "value_in_quote": val_b_in_quote,
            "quote_snippet": empirical_facts["source_b"]["quote"][:80],
        },
    }

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {"description": "...", "values_compared": [str(val_a), str(val_b)], "agreement": val_a == val_b}
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "age": age,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
```

## Numeric/Table Data Proof Template (economic, statistical claims)

For proofs where the primary evidence is numeric data from HTML tables (CPI, GDP, population).
Uses `data_values` for table numbers and `verify_data_values()` to confirm they appear on the page.

```python
"""
Proof: [claim text]
Generated: [date]
"""
import json
import sys

PROOF_ENGINE_ROOT = "..."
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.smart_extract import normalize_unicode
from scripts.verify_citations import verify_all_citations, build_citation_detail, verify_data_values
from scripts.extract_values import parse_number_from_quote
from scripts.computations import compare, explain_calc, cross_check, compute_percentage_change

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
        "verification_performed": "Searched for ...",  # past tense — this is Step 2 research
        "finding": "...",
        "breaks_proof": False,
    },
]

# 11. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    if claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds:
        verdict = "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = "compute_percentage_change(mode='decline')"
    FACT_REGISTRY["A1"]["result"] = f"{decline_a:.4f}%"
    FACT_REGISTRY["A2"]["method"] = "compute_percentage_change(mode='decline') [cross-check]"
    FACT_REGISTRY["A2"]["result"] = f"{decline_b:.4f}%"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # For data_values proofs, extractions use sub-IDs and note the data source
    extractions = {
        "B1_val_1913": {"value": str(val_1913_a), "value_in_quote": True, "quote_snippet": "data_values['val_1913']"},
        "B1_val_2024": {"value": str(val_2024_a), "value_in_quote": True, "quote_snippet": "data_values['val_2024']"},
        "B2_val_1913": {"value": str(val_1913_b), "value_in_quote": True, "quote_snippet": "data_values['val_1913']"},
        "B2_val_2024": {"value": str(val_2024_b), "value_in_quote": True, "quote_snippet": "data_values['val_2024']"},
    }

    # Include data value verification results
    data_value_verification = {
        "B1": {k: v for k, v in dv_results_a.items()},
        "B2": {k: v for k, v in dv_results_b.items()},
    }

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "data_value_verification": data_value_verification,
        "cross_checks": [
            {"description": "1913 values", "values_compared": [str(val_1913_a), str(val_1913_b)],
             "agreement": True, "tolerance": "2% relative"},
            {"description": "2024 values", "values_compared": [str(val_2024_a), str(val_2024_b)],
             "agreement": True, "tolerance": "0.1% relative"},
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "decline_source_a": decline_a,
            "decline_source_b": decline_b,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
```

## Pure-Math Proof Template

For claims that are entirely mathematical (no empirical sources, no URLs, no citations).

```python
"""
Proof: [claim text]
Generated: [date]
"""
import json
import sys

PROOF_ENGINE_ROOT = "..."
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.computations import compare, explain_calc

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "property": "...",
    "operator": "==",
    "operator_note": "...",
    "threshold": ...,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {"label": "...", "method": None, "result": None},
    "A2": {"label": "...", "method": None, "result": None},
}

# 3. COMPUTATION — primary method
primary_result = ...

# 4. CROSS-CHECKS — mathematically independent methods (Rule 6)
crosscheck_result = ...
assert primary_result == crosscheck_result, (
    f"Cross-check failed: primary={primary_result}, crosscheck={crosscheck_result}"
)

# 5. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "...",
        "finding": "...",
        "breaks_proof": False,
    },
]

# 6. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    claim_holds = compare(primary_result, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"])
    verdict = "PROVED" if claim_holds else "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = "..."
    FACT_REGISTRY["A1"]["result"] = str(primary_result)
    FACT_REGISTRY["A2"]["method"] = "..."
    FACT_REGISTRY["A2"]["result"] = str(crosscheck_result)

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "cross_checks": [
            {
                "description": "...",
                "values_compared": [str(primary_result), str(crosscheck_result)],
                "agreement": primary_result == crosscheck_result,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "primary_result": primary_result,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
```

Key differences from the empirical template:
- No `empirical_facts`, `verify_all_citations`, `extract_values`, or `smart_extract` imports
- No `citations` or `extractions` keys in the JSON summary (omitted, not empty)
- Cross-checks use mathematically independent methods instead of independent sources
- `explain_calc()` is optional — use for scalar expressions; for aggregations over lists, use descriptive `print()` instead

## Adaptation Notes

### Empirical consensus proofs
For "multiple sources agree on a finding" (climate, economics): use `parse_number_from_quote`, `parse_percentage_from_quote`, `parse_range_from_quote`. Values are often ranges — use `parse_range_from_quote()`. Verdict often lands on "PROVED (with unverified citations)" because .gov sites block automated fetching.

### Qualitative consensus proofs
For "sources agree X is true" without a numeric threshold: use `verify_extraction("keyword", quote, fact_id)` to confirm key terms appear in each source. CLAIM_FORMAL threshold is a count: `"operator": ">=", "threshold": 3`.

### Citing structured/tabular data
See the Numeric/Table Data template above. Key points:
- Quote verifies source authority; `data_values` hold the numbers
- Call `verify_data_values()` to confirm numbers appear on the source page
- Do NOT call `verify_extraction()` on data_values (circular)
- Use `cross_check()` with tolerance to compare across sources
- Use sub-IDs in extractions: `B1_val_1913`, `B1_val_2024`
