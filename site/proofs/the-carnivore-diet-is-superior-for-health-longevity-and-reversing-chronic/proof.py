"""
Proof: The carnivore diet is superior for health, longevity, and reversing
       chronic disease compared to plant-inclusive diets.
Generated: 2026-03-31
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
CLAIM_NATURAL = (
    "The carnivore diet is superior for health, longevity, and reversing chronic "
    "disease compared to plant-inclusive diets."
)
CLAIM_FORMAL = {
    "subject": "carnivore diet",
    "property": (
        "demonstrably superior to plant-inclusive diets for health, longevity, "
        "and chronic disease reversal, as established by the scientific evidence base"
    ),
    "operator": ">=",
    "operator_note": (
        "'Superior' requires measurably better outcomes compared to plant-inclusive diets "
        "across all three stated dimensions: (1) general health, (2) longevity, and "
        "(3) chronic disease reversal. This is a DISPROOF: we establish the claim is false "
        "by showing (a) the carnivore diet evidence base is insufficient to support any "
        "superiority claim, and (b) substantial scientific evidence points in the opposite "
        "direction for longevity and long-term health. "
        "Threshold: 3 independently verified authoritative sources that contradict or "
        "fail to support the superiority claim. "
        "Note: some studies report short-term carnivore benefits (weight loss, satiety, "
        "anecdotal disease remission), but none establish superiority over plant-inclusive "
        "diets in head-to-head controlled trials across the three claimed dimensions."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "pmcreview",
        "label": (
            "PMC/Nutrients Scoping Review (2025): carnivore diet evidence quality rated "
            "very limited; long-term adherence cannot be recommended"
        ),
    },
    "B2": {
        "key": "bluezones",
        "label": (
            "Blue Zones / Adventist Health Study: plant-eating populations outlive "
            "meat-eating counterparts by up to eight years"
        ),
    },
    "B3": {
        "key": "who",
        "label": (
            "WHO Healthy Diet Fact Sheet: recommends shift toward plant-based protein "
            "away from red meat for health benefits"
        ),
    },
    "B4": {
        "key": "nutritionstudies",
        "label": (
            "T. Colin Campbell Center for Nutrition Studies: large-scale observational "
            "studies associate plant-predominant diets with lower chronic disease incidence"
        ),
    },
    "A1": {
        "label": "Verified source count: authoritative sources contradicting carnivore superiority claim",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS
# These sources REJECT or fail to support the carnivore superiority claim.
# For disproof variant: sources establish the claim is scientifically unsubstantiated
# and that plant-inclusive diets show superior or equivalent long-term outcomes.
empirical_facts = {
    "pmcreview": {
        "quote": (
            "the quality of evidence is very limited due to small sample sizes, "
            "short study durations, and the absence of control groups"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12845189/",
        "source_name": (
            "Nutrients (MDPI) / PMC — Carnivore Diet: A Scoping Review of the Current "
            "Evidence, Potential Benefits and Risks (2025)"
        ),
    },
    "bluezones": {
        "quote": (
            "Research suggests that 30-year-old vegetarian Adventists will likely outlive "
            "their meat-eating counterparts by as many as eight years."
        ),
        "url": "https://www.bluezones.com/2020/07/blue-zones-diet-food-secrets-of-the-worlds-longest-lived-people/",
        "source_name": (
            "Blue Zones — Blue Zones Diet: Food Secrets of the World's Longest-Lived People "
            "(reporting on Adventist Health Study findings)"
        ),
    },
    "who": {
        "quote": (
            "For many adults, a shift towards more plant-based sources of protein may bring "
            "health benefits, particularly when the shift is away from red meat."
        ),
        "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
        "source_name": "World Health Organization — Healthy Diet Fact Sheet",
    },
    "nutritionstudies": {
        "quote": (
            "countless large-scale observational studies consistently show that plant-predominant "
            "diets are associated with a lower incidence and mortality of numerous chronic diseases"
        ),
        "url": "https://nutritionstudies.org/the-carnivore-diet-what-does-the-evidence-say/",
        "source_name": (
            "T. Colin Campbell Center for Nutrition Studies — "
            "The Carnivore Diet: What Does the Evidence Say?"
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
# A source counts toward the disproof threshold if its quote was found on the page
# (status = "verified" or "partial"). Each verified source independently rejects
# the carnivore superiority claim.
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION (Rule 7 — use compare(), not hardcoded bool)
# claim_holds = True means the DISPROOF threshold is met
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified sources rejecting carnivore superiority vs threshold",
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# These document sources that could SUPPORT the carnivore diet claim —
# adversarial to the disproof.
adversarial_checks = [
    {
        "question": (
            "Do self-report surveys of carnivore dieters report significant health benefits "
            "that might support the superiority claim?"
        ),
        "verification_performed": (
            "Reviewed Baker et al. (2021, PMC8684475): a survey of 2,029 adults consuming "
            "a carnivore diet. Participants self-reported improvements in obesity, diabetes, "
            "and autoimmune conditions; 93% rated themselves satisfied or very satisfied."
        ),
        "finding": (
            "Self-report data shows satisfaction and perceived improvements. However, the "
            "study has no control group, relies on self-selection and recall bias, and does "
            "not compare outcomes against plant-inclusive diets. "
            "It cannot establish superiority over any alternative dietary pattern. "
            "Does not break the disproof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Are there clinical studies showing carnivore diet reverses specific chronic "
            "diseases more effectively than plant-inclusive diets?"
        ),
        "verification_performed": (
            "Found Frontiers in Nutrition (2024) case series of 10 IBD patients achieving "
            "remission on carnivore-ketogenic diet (PMC11409203). Searched for head-to-head "
            "RCTs comparing carnivore vs. plant-inclusive diets for chronic disease reversal."
        ),
        "finding": (
            "Case series data (n=10) shows promising signals for IBD, but these are "
            "case reports with no randomization, no control arm, and no comparison to "
            "plant-inclusive diets. No head-to-head RCT establishing carnivore superiority "
            "for any chronic disease was found. Does not break the disproof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do any systematic reviews or meta-analyses conclude carnivore diet is superior "
            "to plant-inclusive diets across health, longevity, or chronic disease reversal?"
        ),
        "verification_performed": (
            "Searched PubMed and Google Scholar for systematic reviews comparing carnivore "
            "diet directly to plant-inclusive diets on health outcomes, lifespan, and "
            "chronic disease. Reviewed the 2025 PMC scoping review (PMC12845189) and "
            "Palmer 2025 (Sage Journals doi:10.1177/02601060251314575) on red meat's "
            "long-term hypertrophy vs. longevity tradeoffs."
        ),
        "finding": (
            "No systematic review or meta-analysis has concluded carnivore diet is superior "
            "to plant-inclusive diets for health, longevity, or chronic disease reversal. "
            "The 2025 PMC scoping review concluded 'long-term adherence to a CD cannot be "
            "recommended' due to insufficient evidence quality. Palmer (2025) found that "
            "long-term adverse effects of red/processed meat outweigh short-term benefits. "
            "Does not break the disproof."
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
            "DISPROVED (with unverified citations)"
            if is_disproof
            else "PROVED (with unverified citations)"
        )
    elif not claim_holds:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = str(n_confirmed)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: qualitative proof — each B fact records citation verification status
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
                    "Sources span: peer-reviewed journal (PMC/Nutrients scoping review), "
                    "population longevity research (Blue Zones / Adventist Health Study), "
                    "international health authority (WHO), and nutrition research institution "
                    "— representing distinct methodologies, institutions, and datasets."
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
