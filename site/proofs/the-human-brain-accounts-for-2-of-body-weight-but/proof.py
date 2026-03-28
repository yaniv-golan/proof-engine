"""
Proof: The human brain accounts for 2% of body weight but uses 20% of the body's oxygen at rest.
Generated: 2026-03-27

Two sub-claims:
  SC1: Human brain is ~2% of adult body weight (by mass)
  SC2: Human brain uses ~20% of the body's oxygen at rest

Both sub-claims are Type B (empirical), verified against two independent authoritative sources:
  - Raichle & Gusnard (2002) PNAS "Appraising the brain's energy budget" via PMC
  - Basic Neurochemistry (NCBI Bookshelf) "Regulation of Cerebral Metabolic Rate"
"""
import json
from datetime import date
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.smart_extract import verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.extract_values import parse_percentage_from_quote
from scripts.computations import compare, cross_check

# =============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# =============================================================================
CLAIM_NATURAL = (
    "The human brain accounts for 2% of body weight but uses 20% of the body's oxygen at rest."
)
CLAIM_FORMAL = {
    "subject": "human brain (adult)",
    "sub_claims": {
        "SC1": {
            "property": "brain mass as fraction of total adult human body weight",
            "operator": "within ±0.5pp of 2.0",
            "threshold_pct": 2.0,
            "operator_note": (
                "The claim states '2%' — an explicitly rounded figure used throughout "
                "the neuroscience literature. Proof checks whether cited sources report "
                "a value within ±0.5 percentage points of 2.0%. This is the conservative "
                "interpretation: a value of 1.5% or 2.5% would still satisfy the claim; "
                "a value of 1.0% or 3.0% would not. Both sources in fact report exactly 2%."
            ),
        },
        "SC2": {
            "property": "brain share of resting whole-body O2 consumption",
            "operator": "within ±2pp of 20.0",
            "threshold_pct": 20.0,
            "operator_note": (
                "The claim states '20%' — a well-established rounded figure. Proof checks "
                "whether cited sources report a value within ±2 percentage points of 20%. "
                "This is generous enough to accommodate natural rounding (e.g., 18-22%), "
                "while being narrow enough to distinguish '~20%' from competing claims "
                "like '25%' or '15%'. Both sources in fact report exactly 20%."
            ),
        },
    },
    "condition": "at rest (basal metabolic state)",
}

# =============================================================================
# 2. FACT REGISTRY
# =============================================================================
FACT_REGISTRY = {
    "B1": {"key": "pnas_weight",  "label": "PNAS 2002: brain = ~2% of body weight"},
    "B2": {"key": "pnas_oxygen",  "label": "PNAS 2002: brain = ~20% of resting O2"},
    "B3": {"key": "ncbi_weight",  "label": "NCBI Basic Neurochemistry: brain = ~2% body weight"},
    "B4": {"key": "ncbi_oxygen",  "label": "NCBI Basic Neurochemistry: brain = 20% resting O2"},
    "A1": {"label": "SC1: extracted brain weight % lies within ±0.5pp of 2%", "method": None, "result": None},
    "A2": {"label": "SC2: extracted brain O2 % lies within ±2pp of 20%",       "method": None, "result": None},
}

# =============================================================================
# 3. EMPIRICAL FACTS (Rule 1 — values parsed from quotes, not hand-typed)
# =============================================================================
empirical_facts = {
    # --- SC1 sources ---
    "pnas_weight": {
        "quote": "In the average adult human, the brain represents about 2% of the body weight.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC124895/",
        "source_name": "Raichle & Gusnard 2002 'Appraising the brain's energy budget' PNAS (via PMC)",
    },
    "ncbi_weight": {
        "quote": "the brain, which represents only about 2% of total body weight",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK28194/",
        "source_name": "Basic Neurochemistry (NCBI Bookshelf): Regulation of Cerebral Metabolic Rate",
    },
    # --- SC2 sources ---
    "pnas_oxygen": {
        "quote": "the brain accounts for about 20% of the oxygen and, hence, calories consumed by the body",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC124895/",
        "source_name": "Raichle & Gusnard 2002 'Appraising the brain's energy budget' PNAS (via PMC)",
    },
    "ncbi_oxygen": {
        "quote": "accounts for 20% of the resting total body O2 consumption",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK28194/",
        "source_name": "Basic Neurochemistry (NCBI Bookshelf): Regulation of Cerebral Metabolic Rate",
    },
}

# =============================================================================
# 4. CITATION VERIFICATION (Rule 2)
# =============================================================================
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# =============================================================================
# 5. VALUE EXTRACTION (Rule 1 — parse from quote text, never hand-typed)
# =============================================================================
print("\n--- Value extraction ---")
weight_pct_pnas = parse_percentage_from_quote(empirical_facts["pnas_weight"]["quote"], "B1/pnas_weight")
weight_pct_pnas_in_quote = verify_extraction(weight_pct_pnas, empirical_facts["pnas_weight"]["quote"], "B1")

weight_pct_ncbi = parse_percentage_from_quote(empirical_facts["ncbi_weight"]["quote"], "B3/ncbi_weight")
weight_pct_ncbi_in_quote = verify_extraction(weight_pct_ncbi, empirical_facts["ncbi_weight"]["quote"], "B3")

oxygen_pct_pnas = parse_percentage_from_quote(empirical_facts["pnas_oxygen"]["quote"], "B2/pnas_oxygen")
oxygen_pct_pnas_in_quote = verify_extraction(oxygen_pct_pnas, empirical_facts["pnas_oxygen"]["quote"], "B2")

oxygen_pct_ncbi = parse_percentage_from_quote(empirical_facts["ncbi_oxygen"]["quote"], "B4/ncbi_oxygen")
oxygen_pct_ncbi_in_quote = verify_extraction(oxygen_pct_ncbi, empirical_facts["ncbi_oxygen"]["quote"], "B4")

# =============================================================================
# 6. CROSS-CHECKS (Rule 6 — independently sourced values must agree)
# =============================================================================
print("\n--- Cross-checks (Rule 6) ---")
weight_sources_agree = cross_check(
    weight_pct_pnas, weight_pct_ncbi,
    tolerance=0.5, mode="absolute",
    label="SC1: brain weight % — PNAS vs NCBI Bookshelf",
)
oxygen_sources_agree = cross_check(
    oxygen_pct_pnas, oxygen_pct_ncbi,
    tolerance=2.0, mode="absolute",
    label="SC2: brain O2 % — PNAS vs NCBI Bookshelf",
)

# =============================================================================
# 7. CLAIM EVALUATION (Rule 7 — compare() instead of inline logic)
# =============================================================================
print("\n--- Claim evaluation ---")
# SC1: brain weight must be within ±0.5pp of 2%
sc1_low  = compare(weight_pct_pnas, ">=", 1.5, label="SC1a: brain weight >= 1.5% (lower bound)")
sc1_high = compare(weight_pct_pnas, "<=", 2.5, label="SC1b: brain weight <= 2.5% (upper bound)")
sc1_holds = sc1_low and sc1_high

# SC2: brain O2 use must be within ±2pp of 20%
sc2_low  = compare(oxygen_pct_pnas, ">=", 18.0, label="SC2a: brain O2 use >= 18% (lower bound)")
sc2_high = compare(oxygen_pct_pnas, "<=", 22.0, label="SC2b: brain O2 use <= 22% (upper bound)")
sc2_holds = sc2_low and sc2_high

claim_holds = sc1_holds and sc2_holds and weight_sources_agree and oxygen_sources_agree

# =============================================================================
# 8. ADVERSARIAL CHECKS (Rule 5)
# =============================================================================
adversarial_checks = [
    {
        "question": "Do any authoritative sources give a significantly different brain weight percentage (not ~2%)?",
        "verification_performed": (
            "Searched web for 'human brain percentage body weight NOT 2 percent disputed alternative'. "
            "Also computed: adult brain ~1,400 g / reference body 70 kg = 2.0% exactly. "
            "Some sources note range 1.3-1.5 kg for brain mass and 60-80 kg for body weight, "
            "yielding 1.6-2.5% — always rounding to ~2%."
        ),
        "finding": (
            "No credible source disputes ~2%. Minor variation (1.6-2.5%) reflects "
            "different reference body weights and brain masses across sexes and ages, "
            "but all sources describe the rounded figure as 'about 2%'."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Do any sources give a substantially different brain O2 percentage at rest (not ~20%)?",
        "verification_performed": (
            "Searched web for 'human brain oxygen consumption NOT 20 percent disputed cerebral metabolic rate'. "
            "Independently verified via published CMRO2 data: normal CMRO2 = 3.5 mL O2/100g/min; "
            "for 1,400g brain = 49 mL O2/min. Average resting VO2 = ~250 mL/min. "
            "49/250 = 19.6% ≈ 20%. Some sources say '20-25%' for active brain but consistently "
            "cite ~20% at rest."
        ),
        "finding": (
            "No credible counter-evidence found. Independent numerical derivation from "
            "CMRO2 values confirms ~20%: (3.5 mL/100g/min × 14 dL) / 250 mL/min ≈ 19.6%. "
            "Any variation (18-22%) rounds to '20%' as claimed."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does the '20% at rest' qualifier matter — would the claim be false if measuring during activity?",
        "verification_performed": (
            "Searched for 'brain oxygen consumption increase during cognitive task vs rest'. "
            "Neuroimaging studies (fMRI/PET) show that local blood flow increases 30-50% during "
            "specific tasks, but whole-brain O2 consumption increases only ~1-5% above baseline. "
            "The claim explicitly says 'at rest', which matches the cited sources."
        ),
        "finding": (
            "The 'at rest' qualifier is accurate and important: during vigorous mental activity "
            "the brain's share remains near 20% because both brain and body metabolism increase. "
            "The claim is correctly qualified."
        ),
        "breaks_proof": False,
    },
]

# =============================================================================
# 9. VERDICT AND STRUCTURED OUTPUT
# =============================================================================
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
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = "compare(weight_pct_pnas, within ±0.5pp of 2.0)"
    FACT_REGISTRY["A1"]["result"] = str(sc1_holds)
    FACT_REGISTRY["A2"]["method"] = "compare(oxygen_pct_pnas, within ±2pp of 20.0)"
    FACT_REGISTRY["A2"]["result"] = str(sc2_holds)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": str(weight_pct_pnas),
            "value_in_quote": weight_pct_pnas_in_quote,
            "quote_snippet": empirical_facts["pnas_weight"]["quote"][:80],
        },
        "B2": {
            "value": str(oxygen_pct_pnas),
            "value_in_quote": oxygen_pct_pnas_in_quote,
            "quote_snippet": empirical_facts["pnas_oxygen"]["quote"][:80],
        },
        "B3": {
            "value": str(weight_pct_ncbi),
            "value_in_quote": weight_pct_ncbi_in_quote,
            "quote_snippet": empirical_facts["ncbi_weight"]["quote"][:80],
        },
        "B4": {
            "value": str(oxygen_pct_ncbi),
            "value_in_quote": oxygen_pct_ncbi_in_quote,
            "quote_snippet": empirical_facts["ncbi_oxygen"]["quote"][:80],
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
            {
                "description": "SC1: brain weight % — PNAS vs NCBI (independently sourced)",
                "values_compared": [str(weight_pct_pnas), str(weight_pct_ncbi)],
                "agreement": weight_sources_agree,
            },
            {
                "description": "SC2: brain O2 % — PNAS vs NCBI (independently sourced)",
                "values_compared": [str(oxygen_pct_pnas), str(oxygen_pct_ncbi)],
                "agreement": oxygen_sources_agree,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_brain_weight_pct_reported": weight_pct_pnas,
            "sc1_threshold_pct": 2.0,
            "sc1_holds": sc1_holds,
            "sc2_brain_oxygen_pct_reported": oxygen_pct_pnas,
            "sc2_threshold_pct": 20.0,
            "sc2_holds": sc2_holds,
            "sources_cross_checked": weight_sources_agree and oxygen_sources_agree,
            "claim_holds": claim_holds,
        },
        "generator": {
            "name": "proof-engine",
            "version": "0.10.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
