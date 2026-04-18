"""
Proof: You must eat animal protein to meet daily protein needs effectively.
Generated: 2026-03-28

Proof direction: DISPROVE
The claim asserts an absolute necessity ("must") for animal protein to meet
daily protein needs. This proof shows that authoritative sources confirm
plant-based diets can adequately meet all protein requirements, negating the
absolute "must" assertion.
"""
import json
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        if os.path.isdir(os.path.join(_d, "proof-engine", "skills", "proof-engine", "scripts")):
            PROOF_ENGINE_ROOT = os.path.join(_d, "proof-engine", "skills", "proof-engine")
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "You must eat animal protein to meet daily protein needs effectively."
CLAIM_FORMAL = {
    "subject": "Animal protein",
    "property": "necessity for meeting daily protein needs",
    "operator": ">=",
    "operator_note": (
        "The claim asserts an absolute requirement ('must'): that animal protein is "
        "necessary and cannot be substituted to meet daily protein needs. "
        "Interpretation: no well-planned plant-based diet can adequately provide all "
        "protein needs without animal sources. "
        "Proof direction: DISPROVE. We show that >= 3 independent authoritative sources "
        "confirm plant-based diets CAN meet daily protein needs without animal protein, "
        "which directly negates the absolute 'must' claim. "
        "A single verified exception (a well-planned plant-based diet meeting protein needs) "
        "is logically sufficient to disprove any 'must' claim — the source threshold of 3 "
        "establishes consensus, not merely a single outlier observation."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_and",
        "label": "Academy of Nutrition and Dietetics 2016 Position Paper on Vegetarian Diets (PubMed PMID 27886704)",
    },
    "B2": {
        "key": "source_pmc_review",
        "label": "Peer-reviewed review: Dietary Protein and Amino Acids in Vegetarian Diets (PMC6893534, Nutrients 2019)",
    },
    "B3": {
        "key": "source_cleveland",
        "label": "Cleveland Clinic: Do I Need to Worry About Eating Complete Proteins?",
    },
    "A1": {"label": "Count of authoritative sources confirmed by citation verification", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS
# These are sources that REJECT the claim (confirm plant protein is sufficient),
# as required by proof_direction="disprove".
empirical_facts = {
    "source_and": {
        "quote": (
            "It is the position of the Academy of Nutrition and Dietetics that "
            "appropriately planned vegetarian, including vegan, diets are healthful, "
            "nutritionally adequate, and may provide health benefits for the prevention "
            "and treatment of certain diseases. These diets are appropriate for all "
            "stages of the life cycle, including pregnancy, lactation, infancy, "
            "childhood, adolescence, older adulthood, and for athletes."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/27886704/",
        "source_name": "Journal of the Academy of Nutrition and Dietetics, Melina et al. 2016 (PMID 27886704)",
    },
    "source_pmc_review": {
        "quote": (
            "there is no evidence of protein deficiency in vegetarian populations in western countries"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6893534/",
        "source_name": "Nutrients 2019: Dietary Protein and Amino Acids in Vegetarian Diets — A Review (PMC6893534)",
    },
    "source_cleveland": {
        "quote": (
            "mixing and matching those protein sources can get you all the amino acids your body needs"
        ),
        "url": "https://health.clevelandclinic.org/do-i-need-to-worry-about-eating-complete-proteins",
        "source_name": "Cleveland Clinic Health Essentials: Complete Proteins",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
print("Verifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION (Rule 4 / Rule 7: must use compare(), never hardcode)
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified source count vs threshold (proof_direction=disprove)",
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# For a disproof, adversarial checks look for evidence SUPPORTING the original claim
# (i.e., sources arguing animal protein is genuinely necessary).
adversarial_checks = [
    {
        "question": (
            "Does any meta-analysis or systematic review conclude that plant protein "
            "CANNOT meet protein needs, or that animal protein is physiologically required?"
        ),
        "verification_performed": (
            "Searched PubMed and Google Scholar for 'animal protein required necessary "
            "protein deficiency vegan vegetarian meta-analysis systematic review'. "
            "Reviewed PMC7926405 (meta-analysis on animal vs plant protein for lean mass, 2021) "
            "and Nutrition Reviews 2025 (plant protein and muscle). "
            "No study concludes that protein needs cannot be met on plant-based diets. "
            "PMC7926405 found animal protein has a modest lean mass advantage in younger adults "
            "but states the result 'does not significantly impact gains in lean mass or muscle "
            "strength following resistance type exercise training' overall."
        ),
        "finding": (
            "No peer-reviewed meta-analysis or systematic review claims plant-based diets "
            "cannot meet protein needs. Studies note animal protein has higher bioavailability "
            "and leucine content, but none conclude plant protein is insufficient if adequate "
            "variety and quantity is consumed."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there scientific evidence that athletes or specific populations CANNOT meet "
            "protein needs on plant-only diets?"
        ),
        "verification_performed": (
            "Searched for 'vegan athlete protein deficiency impossible' and 'plant-based "
            "diet protein inadequacy athletes systematic review'. "
            "The Gatorade Sports Science Institute review found: 'Muscle conditioning in "
            "athletes does not need to be compromised when adopting a plant-based diet as "
            "long as sufficient protein is consumed from a large variety of different "
            "plant-based protein sources.' "
            "The Academy of Nutrition and Dietetics explicitly states plant-based diets are "
            "appropriate 'for athletes'."
        ),
        "finding": (
            "Athletes can meet protein needs on plant-based diets. Sports science literature "
            "confirms adequacy with sufficient quantity and variety, negating any claim that "
            "animal protein is required even for high-demand populations."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the claim have merit if interpreted narrowly — e.g., does animal protein "
            "have bioavailability or amino acid score (DIAAS) advantages that make plant "
            "protein 'ineffective' for meeting needs?"
        ),
        "verification_performed": (
            "Searched for 'DIAAS plant protein inadequate protein needs'. "
            "Animal proteins do generally score higher on the Digestible Indispensable Amino "
            "Acid Score (DIAAS). However, the Academy of Nutrition and Dietetics notes: "
            "'Protein from a variety of plant foods, eaten during the course of a day, "
            "supplies enough of all indispensable (essential) amino acids when caloric "
            "requirements are met.' The terms 'complete' and 'incomplete' protein are "
            "described as 'misleading' in this context. "
            "The PMC6893534 review found lysine intakes in vegetarians were '58 and 43 mg/kg, "
            "respectively, largely higher than the 30 mg/kg estimated average requirement.'"
        ),
        "finding": (
            "Animal protein has higher DIAAS scores, but plant proteins consumed in adequate "
            "variety and quantity meet all amino acid requirements in practice. Bioavailability "
            "differences do not render plant protein 'ineffective' for meeting daily protein "
            "needs — they may require slightly larger total intake. The 'must' framing remains "
            "false: plant protein can effectively meet protein needs."
        ),
        "breaks_proof": False,
    },
]

# 8. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    # "partial" counts toward threshold but triggers "with unverified citations" variant
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
            "DISPROVED (with unverified citations)"
            if is_disproof
            else "PROVED (with unverified citations)"
        )
    elif not claim_holds:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(citation_results[key]['status'] in {COUNTABLE_STATUSES})"
    FACT_REGISTRY["A1"]["result"] = f"{n_confirmed} of {len(empirical_facts)} sources confirmed"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Qualitative proof: extractions record citation status per B-type fact
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
                "description": "Multiple independent authoritative sources consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from three independent institutions: "
                    "(1) Academy of Nutrition and Dietetics (professional dietetics body), "
                    "(2) an independent peer-reviewed journal review (Nutrients/PMC), "
                    "(3) Cleveland Clinic (major academic medical center). "
                    "These sources represent independent research and expert consensus, "
                    "not a single institution cited multiple times."
                ),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirmed": n_confirmed,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "proof_direction": CLAIM_FORMAL["proof_direction"],
            "claim_holds": claim_holds,
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
