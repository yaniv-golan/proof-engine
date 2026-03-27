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
    elif not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

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
    elif not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

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
    # Pure-math: no citations, so no unverified-citation variants needed
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

## Qualitative Consensus Proof Template

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
import json
import sys

PROOF_ENGINE_ROOT = "..."  # LLM fills this with the actual path at proof-writing time
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

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

# 7. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "Searched for ...",
        "finding": "...",
        "breaks_proof": False,
    },
]

# 8. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    # "partial" counts toward the threshold but is NOT fully verified —
    # only "verified" is clean. This preserves the existing semantics where
    # partial/fragment matches trigger "with unverified citations" verdicts.
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif claim_holds and not any_unverified:
        verdict = "DISPROVED" if is_disproof else "PROVED"
    elif claim_holds and any_unverified:
        verdict = ("DISPROVED (with unverified citations)" if is_disproof
                   else "PROVED (with unverified citations)")
    elif not claim_holds:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = str(n_confirmed)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: for qualitative proofs, each B-type fact records citation status
    extractions = {}
    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        cr = citation_results.get(ef_key, {})
        extractions[fid] = {
            "value": cr.get("status", "unknown"),
            "value_in_quote": cr.get("status") in COUNTABLE_STATUSES,
            "quote_snippet": empirical_facts[ef_key]["quote"][:80],
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
        # For qualitative proofs, cross_checks documents that multiple independent
        # sources were consulted and how many were successfully verified.
        "cross_checks": [
            {
                "description": "Multiple independent sources consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": "Sources are from different publications/institutions",
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirmed": n_confirmed,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
```

### Disproof variant

To disprove a claim (e.g., "Humans only use 10% of their brain"):

1. Set `CLAIM_FORMAL["proof_direction"]` to `"disprove"` and `threshold` to `3`.
2. In `empirical_facts`, include authoritative sources that **reject** the claim. Choose quotes that clearly express the rejection — the quote must be verifiable on the source page.
3. `n_confirmed` counts sources whose quotes were verified on the live page.
4. `compare(3, ">=", 3)` returns `True`, so `claim_holds = True`.
5. The verdict block maps `claim_holds = True` → `DISPROVED` (via `proof_direction`).
6. In `adversarial_checks`, search for sources that **support** the claim.

No keyword selection is needed — the counting mechanism is citation verification, not keyword matching. The key requirement is that quotes are on-topic and verifiable.

### Adaptation notes

**Compound claims (X AND Y):** See the compound CLAIM_FORMAL variant below.

**Empirical consensus with numeric values:** When multiple sources agree on a specific number (e.g., "86 billion neurons"), use the Numeric/Table template instead — it handles numeric cross-checks better than keyword extraction.

**Citing structured/tabular data:** See the Numeric/Table Data template above. Key points:
- Quote verifies source authority; `data_values` hold the numbers
- Call `verify_data_values()` to confirm numbers appear on the source page
- Do NOT call `verify_extraction()` on data_values (circular)
- Use `cross_check()` with tolerance to compare across sources
- Use sub-IDs in extractions: `B1_val_1913`, `B1_val_2024`

### Compound CLAIM_FORMAL

For claims with multiple sub-claims joined by AND. Each sub-claim gets its own confirmation list, source count, and `compare()` evaluation. The compound verdict aggregates sub-claim results.

**When to use:** The claim contains AND or implies multiple independently verifiable conditions. Examples: "Israel withdrew from Gaza AND Hamas won the 2006 election," "Brain weight is 2% of body weight AND uses 20% of oxygen."

**Not supported:** Negated sub-claims (X BUT NOT Y) require per-sub-claim `proof_direction`, which this template doesn't model. For claims with negated parts, decompose into separate proofs — one affirmative, one disproof — using the qualitative template's `proof_direction` field.

```python
"""
Proof: [compound claim text]
Generated: [date]
"""
import json
import sys

PROOF_ENGINE_ROOT = "..."  # LLM fills with actual path
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 2, "operator_note": "..."},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 2, "operator_note": "..."},
    ],
    "compound_operator": "AND",  # only AND is supported; OR claims should be decomposed into separate proofs
    "operator_note": "All sub-claims must hold for the compound claim to be PROVED",
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

# 8. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "Searched for ...",
        "finding": "...",
        "breaks_proof": False,
    },
]

# 9. VERDICT — handles mixed results and unverified citations
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        # Mixed: some sub-claims hold, others don't.
        # Citation status is noted in proof.md conclusion but doesn't change
        # the verdict label — PARTIALLY VERIFIED already signals incompleteness.
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds:
        # No sub-claims met threshold. For source-counting proofs,
        # this is insufficient evidence, not disproof.
        # Citation status is noted in proof.md conclusion.
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified sc1 citations) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1)
    FACT_REGISTRY["A2"]["method"] = f"count(verified sc2 citations) = {n_sc2}"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: each B-type fact records citation status
    extractions = {}
    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        cr = citation_results.get(ef_key, {})
        extractions[fid] = {
            "value": cr.get("status", "unknown"),
            "value_in_quote": cr.get("status") in COUNTABLE_STATUSES,
            "quote_snippet": empirical_facts[ef_key]["quote"][:80],
        }

    summary = {
        "fact_registry": {fid: dict(info) for fid, info in FACT_REGISTRY.items()},
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {"description": "SC1: independent sources consulted",
             "n_sources_consulted": len(sc1_keys), "n_sources_verified": n_sc1,
             "sources": {k: citation_results[k]["status"] for k in sc1_keys},
             "independence_note": "Sources from different publications"},
            {"description": "SC2: independent sources consulted",
             "n_sources_consulted": len(sc2_keys), "n_sources_verified": n_sc2,
             "sources": {k: citation_results[k]["status"] for k in sc2_keys},
             "independence_note": "Sources from different publications"},
        ],
        "sub_claim_results": [
            {"id": "SC1", "n_confirming": n_sc1,
             "threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"], "holds": sc1_holds},
            {"id": "SC2", "n_confirming": n_sc2,
             "threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"], "holds": sc2_holds},
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_holding": n_holding,
            "n_total": n_total,
            "claim_holds": claim_holds,
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
```

**Key design points:**
- `PARTIALLY VERIFIED` is checked BEFORE the `claim_holds` branches — mixed results short-circuit the verdict.
- `UNDETERMINED` when no sub-claims meet threshold — for source-counting proofs, insufficient evidence is not disproof.
- Per-sub-claim `compare()` calls use labels, so the computation trace is self-documenting.
- `any_unverified` modifies PROVED → PROVED (with unverified citations). For PARTIALLY VERIFIED and UNDETERMINED, citation status is documented in proof.md's Conclusion section rather than changing the verdict label — those verdicts already signal incompleteness.
- `sub_claim_results` in the JSON summary gives downstream tooling per-SC detail.
- Only `AND` compounds are supported. For OR claims ("X or Y is true"), decompose into separate proofs — an OR compound where either sub-claim suffices is just two independent proofs.

**Adapting for numeric compound claims:** Replace the citation-counting step with `parse_number_from_quote()` / `verify_data_values()` per the Numeric/Table template. The compound evaluation (steps 6-7) stays the same — only the per-sub-claim counting (step 5) changes.

**Sub-claims with no possible supporting sources:** Keep the sub-claim in `CLAIM_FORMAL["sub_claims"]` with its full structure — do not remove it from `n_total`. Set its `n_confirming` to 0 via an empty confirmations list (not a hardcoded literal). The compound verdict will naturally produce `PARTIALLY VERIFIED` (some hold, some don't) or `UNDETERMINED` (none hold). Removing a failing sub-claim from the denominator would change the claim's meaning and could turn a failing proof into a passing one. Document the sub-claim's failure and the evidence for it (e.g., adversarial findings) in the proof's adversarial_checks section.
