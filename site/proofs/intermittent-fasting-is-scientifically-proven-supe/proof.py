"""
Proof: Intermittent fasting is scientifically proven superior to other diets for fat loss and longevity.
Generated: 2026-03-28
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "Intermittent fasting is scientifically proven superior to other diets "
    "for fat loss and longevity."
)
CLAIM_FORMAL = {
    "subject": "Intermittent fasting",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "scientifically proven superior to other diets for fat loss",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC1 is proved (for disproof purposes) when at least 2 independent "
                "peer-reviewed systematic reviews or meta-analyses conclude that IF does "
                "NOT significantly outperform isocaloric continuous caloric restriction "
                "for fat loss. A source counts if its verified quote expresses "
                "'no significant difference,' 'not superior,' or equivalent. "
                "Threshold of 2 provides independent confirmation from separate publications."
            ),
        },
        {
            "id": "SC2",
            "property": "scientifically proven superior to other diets for longevity in humans",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC2 is proved (for disproof purposes) when at least 2 independent "
                "sources — peer-reviewed reviews or major clinical/scientific bodies — "
                "explicitly state that evidence for IF's longevity benefit in humans is "
                "lacking, insufficient, or unproven, OR that IF was not associated with "
                "longer lifespan in human observational data. "
                "Threshold of 2 provides independent confirmation."
            ),
        },
    ],
    "compound_operator": "AND",
    "proof_direction": "disprove",
    "operator_note": (
        "The original claim asserts BOTH (a) proven fat loss superiority AND "
        "(b) proven longevity superiority. An AND claim is false if either conjunct is "
        "false. This proof shows both conjuncts fail: (a) meta-analyses show IF produces "
        "equivalent — not superior — fat loss vs. matched caloric restriction, and "
        "(b) no adequate human evidence exists for longevity superiority. "
        "proof_direction='disprove': empirical_facts sources REJECT each sub-claim; "
        "claim_holds=True triggers verdict DISPROVED (not PROVED)."
    ),
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "sc1_source_a",
        "label": (
            "SC1-A: Systematic review & meta-analysis of IF vs. caloric restriction "
            "(PMC11930668, 2025) — weight loss difference not statistically significant"
        ),
    },
    "B2": {
        "key": "sc1_source_b",
        "label": (
            "SC1-B: Meta-analysis of IF vs. caloric restriction in humans "
            "(PMC9108547, 2022) — IF outcomes did not differ from CR"
        ),
    },
    "B3": {
        "key": "sc2_source_a",
        "label": (
            "SC2-A: Review of IF health benefits (PMC11262566, 2024) — "
            "human longevity studies are short-duration with high variability"
        ),
    },
    "B4": {
        "key": "sc2_source_b",
        "label": (
            "SC2-B: American Heart Association newsroom, 2024 — "
            "time-restricted eating not associated with living longer"
        ),
    },
    "A1": {"label": "SC1: count of verified rejection sources for fat loss superiority", "method": None, "result": None},
    "A2": {"label": "SC2: count of verified rejection sources for longevity superiority", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS
# These sources REJECT the claim (disproof direction).
# For SC1: peer-reviewed meta-analyses concluding IF is not significantly superior for fat loss.
# For SC2: evidence that IF has no proven longevity benefit in humans.
empirical_facts = {
    "sc1_source_a": {
        "quote": (
            "IF resulted in a slightly greater, but statistically nonsignificant, "
            "decrease in weight"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11930668/",
        "source_name": (
            "Evaluation of the effectiveness of intermittent fasting versus caloric "
            "restriction in weight loss and improving cardiometabolic health: "
            "A systematic review and meta-analysis (PMC, 2025)"
        ),
    },
    "sc1_source_b": {
        "quote": "IF outcomes did not differ from CR except for reduced WC",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9108547/",
        "source_name": (
            "Effects of Intermittent Fasting in Human Compared to a Non-intervention "
            "Diet and Caloric Restriction: A Meta-Analysis of Randomized Controlled "
            "Trials (PMC, 2022)"
        ),
    },
    "sc2_source_a": {
        "quote": (
            "reported human studies have been of short duration, and the baseline "
            "parameters of the study populations are highly variable"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11262566/",
        "source_name": (
            "Review Article: Health Benefits of Intermittent Fasting (PMC, 2024)"
        ),
    },
    "sc2_source_b": {
        "quote": (
            "Limiting food intake to less than 8 hours per day was not associated "
            "with living longer"
        ),
        "url": "https://newsroom.heart.org/news/8-hour-time-restricted-eating-linked-to-a-91-higher-risk-of-cardiovascular-death",
        "source_name": (
            "American Heart Association newsroom: 8-hour time-restricted eating "
            "linked to a 91% higher risk of cardiovascular death (AHA, 2024)"
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
print(f"  SC1 confirmed rejection sources: {n_sc1} / {len(sc1_keys)}")
print(f"  SC2 confirmed rejection sources: {n_sc2} / {len(sc2_keys)}")

# 6. PER-SUB-CLAIM EVALUATION (Rule 7 — compare() not hardcoded)
sc1_holds = compare(
    n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
    label="SC1: verified sources showing IF NOT proven superior for fat loss",
)
sc2_holds = compare(
    n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
    label="SC2: verified sources showing IF NOT proven superior for longevity",
)

# 7. COMPOUND EVALUATION
n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# 8. ADVERSARIAL CHECKS (Rule 5)
# Searched for evidence that would break the disproof — i.e., evidence supporting
# the original claim of proven superiority.
adversarial_checks = [
    {
        "question": (
            "Do any meta-analyses clearly show IF is significantly and clinically "
            "superiorly effective for fat loss vs. calorie-matched CCR?"
        ),
        "verification_performed": (
            "Searched: 'intermittent fasting significantly superior fat loss meta-analysis'; "
            "'IF vs caloric restriction fat mass randomized controlled trial superiority'. "
            "Reviewed Nutrients 2024 (PMID 39458528), PMC11930668 (2025), PMC9099935 (2022), "
            "PMC9108547 (2022), and Lancet eClinicalMedicine umbrella review (2024)."
        ),
        "finding": (
            "Some meta-analyses find modest statistically significant advantages in specific "
            "metrics (e.g., BMI in one study, insulin sensitivity in another), but no "
            "meta-analysis concludes IF is clearly clinically superior for overall fat loss. "
            "Nutrients 2024: 'FBS did not show superior long-term outcomes compared to CCR.' "
            "PMC11930668 2025: weight loss difference 'statistically nonsignificant.' "
            "The scientific literature consistently describes IF as equivalent — not "
            "proven superior — to matched caloric restriction for fat loss."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there any human randomized controlled trial demonstrating that "
            "IF significantly extends lifespan or healthspan beyond other diets?"
        ),
        "verification_performed": (
            "Searched: 'intermittent fasting human lifespan RCT randomized controlled trial'; "
            "'time-restricted eating longevity humans clinical trial'; "
            "'IF longevity human evidence 2022 2023 2024'. "
            "Reviewed PMC11262566, PMC8932957, ScienceDirect S1568163724000928."
        ),
        "finding": (
            "No such RCT exists. All evidence for IF extending lifespan comes from animal "
            "models (C. elegans, Drosophila, mice). Human studies measure short-term "
            "metabolic proxies (weight, insulin, lipids), not lifespan. "
            "PMC11262566: 'reported human studies have been of short duration.' "
            "The most recent large observational study (AHA 2024, n>20,000) found that "
            "time-restricted eating was NOT associated with longer life, and was linked "
            "to 91% higher cardiovascular mortality."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is the AHA 2024 study on TRE and cardiovascular mortality robust enough "
            "to count as evidence against longevity claims?"
        ),
        "verification_performed": (
            "Searched: 'time-restricted eating AHA 2024 cardiovascular mortality limitations "
            "observational study confounders'; 'TRE longevity criticism 2024'. "
            "Reviewed Science Media Centre expert reactions and TCTMD debate coverage."
        ),
        "finding": (
            "The AHA 2024 abstract has limitations: it was observational (not an RCT), "
            "relied on only 2 days of dietary recall, and may have reverse causation "
            "(sick people may eat within a shorter window). However, for SC2 the key point "
            "is not that IF harms longevity, but that IF has NOT been proven to extend "
            "human lifespan. Even discounting the AHA study, SC2 source A (PMC11262566) "
            "independently establishes insufficient human longevity evidence."
        ),
        "breaks_proof": False,
    },
]

# 9. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"

    if any_breaks:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        # Mixed: some sub-claims have enough evidence, others don't.
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "DISPROVED" if is_disproof else "PROVED"
    elif claim_holds and any_unverified:
        verdict = (
            "DISPROVED (with unverified citations)"
            if is_disproof
            else "PROVED (with unverified citations)"
        )
    else:
        # No sub-claims met threshold — insufficient evidence.
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified SC1 rejection sources) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1)
    FACT_REGISTRY["A2"]["method"] = f"count(verified SC2 rejection sources) = {n_sc2}"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: for qualitative proofs, record citation status per source
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
            {
                "description": "SC1: independent peer-reviewed sources consulted on fat loss",
                "n_sources_consulted": len(sc1_keys),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in sc1_keys},
                "independence_note": (
                    "Sources are from separate publications (2022 meta-analysis PMC9108547 "
                    "and 2025 systematic review PMC11930668) with different author teams "
                    "and data sets."
                ),
            },
            {
                "description": "SC2: independent sources consulted on human longevity evidence",
                "n_sources_consulted": len(sc2_keys),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in sc2_keys},
                "independence_note": (
                    "Sources are from separate institutions: a 2024 PMC review article "
                    "(PMC11262566) and the American Heart Association newsroom reporting on "
                    "a 2024 observational study of >20,000 US adults."
                ),
            },
        ],
        "sub_claim_results": [
            {
                "id": "SC1",
                "n_confirming": n_sc1,
                "threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"],
                "holds": sc1_holds,
            },
            {
                "id": "SC2",
                "n_confirming": n_sc2,
                "threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"],
                "holds": sc2_holds,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_holding": n_holding,
            "n_total": n_total,
            "claim_holds": claim_holds,
            "sc1_holds": sc1_holds,
            "sc2_holds": sc2_holds,
            "proof_direction": "disprove",
        },
        "generator": {
            "name": "proof-engine",
            "version": open(os.path.join(PROOF_ENGINE_ROOT, "VERSION")).read().strip(),
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
