"""
Proof: "Calories in, calories out" is the ONLY thing that matters for sustainable weight loss.
Direction: DISPROOF — multiple independent peer-reviewed research domains establish that
factors beyond caloric arithmetic materially affect sustainable weight loss outcomes.
Generated: 2026-03-28
"""
import json
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    '"Calories in, calories out" is the ONLY thing that matters for sustainable weight loss.'
)
CLAIM_FORMAL = {
    "subject": "Energy balance (caloric intake minus expenditure)",
    "property": "sole sufficient determinant of sustainable weight loss",
    "operator": ">=",
    "operator_note": (
        "The claim asserts caloric arithmetic is both necessary AND sufficient for sustainable "
        "weight loss — i.e., no other variable independently affects long-term weight loss "
        "outcomes. The word 'only' is interpreted strictly: any factor that materially affects "
        "sustainable weight loss outcomes independently of simple caloric accounting falsifies "
        "the claim. 'Sustainable' is interpreted as weight loss that preserves metabolically "
        "active lean mass and is maintainable long-term (not just short-term scale weight). "
        "We prove the NEGATION: at least 3 independent peer-reviewed research bodies each "
        "demonstrate a factor that materially affects sustainable weight loss beyond caloric "
        "arithmetic alone. Threshold = 3 verified sources across distinct research domains."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_sleep",
        "label": (
            "PMC8591680: Sleep restriction shifts body composition at identical caloric deficits "
            "(more muscle lost, less fat lost)"
        ),
    },
    "B2": {
        "key": "source_thermogenesis",
        "label": (
            "PMC3673773: Adaptive thermogenesis reduces energy expenditure 10-15% beyond "
            "predictions, persisting 6 months to 7 years after weight loss"
        ),
    },
    "B3": {
        "key": "source_microbiome",
        "label": (
            "PMC3127503: Gut microbiome composition changes effective caloric extraction "
            "by ~150 kcal/day from identical food intake"
        ),
    },
    "B4": {
        "key": "source_metabolic",
        "label": (
            "PMC11676201: Caloric restriction invokes hormonal/metabolic adaptations "
            "(thermogenesis, appetite hormones, metabolic profiles) that independently "
            "alter weight outcomes"
        ),
    },
    "A1": {
        "label": "Count of independently verified peer-reviewed sources rejecting CICO sufficiency",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS
# Each source is from a distinct research domain and confirms that a factor beyond
# simple caloric arithmetic materially affects sustainable weight loss outcomes.
empirical_facts = {
    # Domain 1: Sleep science — same caloric deficit, different body composition
    "source_sleep": {
        "quote": (
            "less loss of total mass as fat when sleep was shorter"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8591680/",
        "source_name": (
            "Influence of Sleep Restriction on Weight Loss Outcomes Associated with "
            "Caloric Restriction — PMC (Sleep, 2022)"
        ),
    },
    # Domain 2: Energy expenditure physiology — metabolic adaptation undermines CICO predictions
    "source_thermogenesis": {
        "quote": (
            "the reduction in twenty four hour energy expenditure (TEE) persists in subjects "
            "who have sustained weight loss for extended periods of time (6 months \u2013 7 years)"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3673773/",
        "source_name": (
            "Adaptive thermogenesis in humans — PMC (International Journal of Obesity, 2013)"
        ),
    },
    # Domain 3: Gut microbiome research — effective calories in varies between individuals
    "source_microbiome": {
        "quote": (
            "a 20% increase in Firmicutes and a corresponding decrease in Bacteroidetes "
            "were associated with an increased energy harvest of"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3127503/",
        "source_name": (
            "Energy-balance studies reveal associations between gut microbes, caloric load, "
            "and nutrient absorption in humans — PMC (American Journal of Clinical Nutrition, 2011)"
        ),
    },
    # Domain 4: Hormonal/metabolic medicine — multi-mechanism review
    "source_metabolic": {
        "quote": (
            "Caloric restriction invokes a suite of adaptive mechanisms involving adaptive "
            "thermogenesis, changes in appetite, alterations in hormonal and metabolic profiles, "
            "and changes in body composition."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11676201/",
        "source_name": (
            "Beyond Calories: Individual Metabolic and Hormonal Adaptations Driving Variability "
            "in Weight Management — PMC (Nutrients, 2024)"
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
print("\n--- Citation Verification ---")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — must use compare()
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified counter-sources vs threshold (>=3 needed to disprove)",
)

# 7. ADVERSARIAL CHECKS (Rule 5) — searching for evidence SUPPORTING the CICO claim
adversarial_checks = [
    {
        "question": (
            "Do CICO proponents argue that sleep, hormones, and gut microbiome all operate "
            "*through* CICO — i.e., they affect 'calories in' or 'calories out' and therefore "
            "CICO remains the 'only' mechanism?"
        ),
        "verification_performed": (
            "Searched 'calories in calories out all factors funnel through CICO argument'; "
            "reviewed Precision Nutrition and ACE Fitness articles arguing CICO is the final "
            "common pathway. This is the strongest pro-CICO argument."
        ),
        "finding": (
            "This semantic argument is valid at a definitional level: sleep affects hormones "
            "that affect appetite ('calories in'), and adaptive thermogenesis reduces resting "
            "metabolic rate ('calories out'). However, the sleep study (B1) directly refutes "
            "the practical claim: at the SAME measured caloric deficit (same calories in AND "
            "same calories out), sleep-restricted dieters lost only 58% of weight as fat vs "
            "83% in well-rested dieters. Body composition at the same deficit differs "
            "significantly — a factor that is invisible to simple caloric accounting but "
            "critical for 'sustainable' weight loss (muscle loss reduces future metabolic rate, "
            "driving rebound weight gain)."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is adaptive thermogenesis large enough to matter practically, or is it a "
            "negligible 1-2% effect that dieters can ignore?"
        ),
        "verification_performed": (
            "Reviewed PMC3673773 for specific magnitudes. Also searched "
            "'adaptive thermogenesis magnitude practical significance weight loss'."
        ),
        "finding": (
            "PMC3673773 documents a 10-15% decline in 24-hour energy expenditure beyond "
            "what weight loss alone predicts, plus a ~20% increase in skeletal muscle work "
            "efficiency. At a 2000 kcal/day baseline, 10-15% is 200-300 kcal/day — equivalent "
            "to 20-30 minutes of brisk walking. This is not negligible: it means a dieter "
            "maintaining a calculated 500 kcal deficit is actually maintaining a 200-300 kcal "
            "deficit, explaining why weight loss stalls and regain occurs despite 'following "
            "the math.' The effect persists 6 months to 7 years (B2)."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is the gut microbiome effect (~150 kcal/day from Firmicutes changes) robust enough "
            "to be clinically significant, or is it a weak association from a single study?"
        ),
        "verification_performed": (
            "Searched 'gut microbiome energy harvest 150 kcal replication'; reviewed "
            "PMC3601187, PMC10334151, and Nature Communications 2023 (s41467-023-38778-x) "
            "for independent confirmation."
        ),
        "finding": (
            "Multiple independent studies confirm microbiome-energy harvest associations. "
            "The 150 kcal/day figure from PMC3127503 is widely cited. A 2023 Nature "
            "Communications RCT (s41467-023-38778-x) showed that dietary-induced microbiome "
            "changes altered energy balance in a controlled setting. PMC3601187 confirms "
            "microbes enable absorption of energy that would otherwise pass undigested. "
            "The effect is real but the 150 kcal estimate has wide confidence intervals; "
            "the broader point — that identical food produces different effective caloric "
            "intake across individuals due to microbiome variation — is well-supported."
        ),
        "breaks_proof": False,
    },
]

# 8. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
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
        verdict = (
            "DISPROVED (with unverified citations)" if is_disproof
            else "PROVED (with unverified citations)"
        )
    elif not claim_holds:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(citations with status in {COUNTABLE_STATUSES})"
    FACT_REGISTRY["A1"]["result"] = f"{n_confirmed} verified counter-sources (threshold: 3)"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

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
        "cross_checks": [
            {
                "description": (
                    "Four independently sourced peer-reviewed citations from distinct research "
                    "domains (sleep science, energy expenditure physiology, gut microbiome "
                    "research, hormonal/metabolic medicine)"
                ),
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Each source addresses a mechanistically distinct pathway by which factors "
                    "beyond caloric arithmetic affect weight loss: (B1) sleep → body composition "
                    "at fixed deficit; (B2) metabolic adaptation → reduced energy expenditure; "
                    "(B3) gut microbiome → variable caloric extraction from identical food; "
                    "(B4) hormonal cascade → multi-mechanism adaptive response. None of the "
                    "four sources relies on the same underlying study or research group."
                ),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirmed": n_confirmed,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
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
