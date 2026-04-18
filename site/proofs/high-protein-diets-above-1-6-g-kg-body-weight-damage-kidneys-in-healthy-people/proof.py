"""
Proof: High-protein diets above 1.6 g/kg body weight damage kidneys in healthy people.
Generated: 2026-03-31
"""
import json
import os
import sys

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
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "High-protein diets above 1.6 g/kg body weight damage kidneys in healthy people."
CLAIM_FORMAL = {
    "subject": "High-protein diet above 1.6 g/kg body weight per day",
    "property": (
        "whether it causes measurable kidney damage (GFR decline, proteinuria, or CKD "
        "development) in adults without pre-existing kidney disease"
    ),
    "operator": ">=",
    "operator_note": (
        "The claim is DISPROVED if >=3 independent systematic reviews or meta-analyses "
        "confirm that high-protein intake does NOT damage kidneys in healthy adults. "
        "'Damage' is interpreted as measurable adverse change in kidney function markers "
        "(GFR decline, increased proteinuria, or elevated creatinine). "
        "The 1.6 g/kg threshold cited in the claim is not a clinically established "
        "kidney-safety boundary; it is commonly cited in sports nutrition literature "
        "(Morton et al. 2018) as an approximate upper limit for muscle protein synthesis "
        "optimization. The meta-analyses used here study protein intakes >=1.5 g/kg or "
        "'above the US RDA (0.8 g/kg)' -- both categories encompass the >1.6 g/kg range "
        "in the claim. This is a disproof (proof_direction='disprove'): the sources in "
        "empirical_facts reject the claim; sources supporting the claim are in "
        "adversarial_checks."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "devries_2018",
        "label": (
            "Devries et al. (2018) Journal of Nutrition — meta-analysis of 28 RCTs, "
            "1358 healthy adults: HP intakes do not adversely influence GFR"
        ),
    },
    "B2": {
        "key": "van_elswyk_2018",
        "label": (
            "Van Elswyk et al. (2018) Advances in Nutrition — systematic review of RCTs "
            "and observational studies: higher protein consistent with normal kidney function"
        ),
    },
    "B3": {
        "key": "cheng_2024",
        "label": (
            "Cheng et al. (2024) Frontiers in Nutrition — meta-analysis of 6 cohort "
            "studies, 148,051 participants: higher protein associated with lower CKD risk"
        ),
    },
    "A1": {"label": "Verified source count (sources rejecting the claim)", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it is false)
empirical_facts = {
    "devries_2018": {
        "quote": (
            "Our analysis indicates that HP intakes do not adversely influence "
            "kidney function on GFR in healthy adults."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/30383278/",
        "source_name": (
            "Devries MC et al. (2018) Changes in Kidney Function Do Not Differ "
            "between Healthy Adults Consuming Higher- Compared with Lower- or "
            "Normal-Protein Diets: A Systematic Review and Meta-Analysis. "
            "Journal of Nutrition, 148(11):1760-1775. DOI:10.1093/jn/nxy197"
        ),
    },
    "van_elswyk_2018": {
        "quote": (
            "These data further indicate that, at least in the short term, higher "
            "protein intake within the range of recommended intakes for protein is "
            "consistent with normal kidney function in healthy individuals."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6054213/",
        "source_name": (
            "Van Elswyk ME et al. (2018) A Systematic Review of Renal Health in "
            "Healthy Individuals Associated with Protein Intake above the US "
            "Recommended Daily Allowance in Randomized Controlled Trials and "
            "Observational Studies. Advances in Nutrition, 9(4):404-418. "
            "DOI:10.1093/advances/nmy026"
        ),
    },
    "cheng_2024": {
        "quote": (
            "The data showed a lower CKD risk significantly associated higher-level "
            "dietary total, plant or animal protein (especially for fish and seafood) "
            "intake."
        ),
        "url": "https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2024.1408424/full",
        "source_name": (
            "Cheng Y et al. (2024) Association between dietary protein intake and risk "
            "of chronic kidney disease: a systematic review and meta-analysis. "
            "Frontiers in Nutrition, 11:1408424. DOI:10.3389/fnut.2024.1408424"
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — MUST use compare(), never hardcode claim_holds
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified source count vs threshold (disproof: sources rejecting the claim)",
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# These are sources that SUPPORT the claim (i.e., argue high protein DOES harm kidneys).
# Searched for counter-evidence before writing this proof.
adversarial_checks = [
    {
        "question": (
            "Is there evidence that high-protein diets cause rapid kidney function "
            "decline in healthy adults?"
        ),
        "verification_performed": (
            "Searched 'high protein diet rapid GFR decline healthy adults' and "
            "'high protein kidney function decline cohort study'; found Jhee et al. "
            "(2019, Nephrology Dialysis Transplantation), a Korean community-based "
            "prospective cohort of 9,226 adults without kidney disease, reporting that "
            "the highest protein intake quartile had 1.32x higher odds of rapid eGFR "
            "decline vs the lowest quartile."
        ),
        "finding": (
            "Jhee et al. (2019) is an observational association study, not an RCT. "
            "Observational findings cannot establish causation due to confounding "
            "(high animal protein often co-occurs with high sodium, red meat, etc.). "
            "The RCT meta-analysis by Devries et al. (2018) — the highest level of "
            "evidence — found no adverse GFR change when protein intake was "
            "experimentally manipulated in controlled trials. The observational "
            "association does not override the controlled trial evidence."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does glomerular hyperfiltration from high protein intake cause long-term "
            "kidney damage in healthy people?"
        ),
        "verification_performed": (
            "Searched 'glomerular hyperfiltration high protein long-term damage healthy "
            "kidneys'; reviewed Ko et al. (2020, JASN, PMC7460905) and Kalantar-Zadeh "
            "et al. (2020, Nephrology Dialysis Transplantation, doi:10.1093/ndt/gfz216). "
            "Ko et al. state in the abstract that 'evidence suggests that worsening renal "
            "function may occur in individuals with and perhaps without impaired kidney "
            "function' and note 'It is possible that long-term high protein intake may "
            "lead to de novo CKD.' Kalantar-Zadeh et al. argue protein restriction is "
            "warranted for vulnerable populations."
        ),
        "finding": (
            "Both papers acknowledge the hyperfiltration mechanism but qualify their "
            "concerns for healthy people. Ko et al. (2020) also note that 'long-term "
            "trials have not observed an increase in proteinuria' in those without kidney "
            "disease. Kalantar-Zadeh et al. (2020) explicitly state 'persons with healthy "
            "intact kidneys may not be affected by this harmful impact.' The concerns are "
            "speculative for healthy individuals; no RCT has demonstrated actual kidney "
            "damage (not just adaptive hyperfiltration) in healthy adults."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is 1.6 g/kg body weight a clinically established kidney safety limit?"
        ),
        "verification_performed": (
            "Searched '1.6 g/kg protein kidney safety limit' and '1.6 g/kg protein "
            "kidney damage threshold'; searched National Kidney Foundation guidelines "
            "and nephrology clinical guidelines."
        ),
        "finding": (
            "The 1.6 g/kg figure originates in sports nutrition literature as the upper "
            "bound for muscle protein synthesis optimization (Morton et al. 2018, Br J "
            "Sports Med), not as a nephrology safety threshold. Clinical nephrology "
            "guidelines (National Kidney Foundation, KDIGO) address protein restriction "
            "for people WITH CKD; they do not identify 1.6 g/kg as a risk cutoff for "
            "healthy adults. There is no established clinical threshold beyond which "
            "healthy kidneys are damaged by protein intake."
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
                "description": "Multiple independent systematic reviews consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "B1 (Devries 2018) and B2 (Van Elswyk 2018) are independent "
                    "systematic reviews published simultaneously in different journals "
                    "(Journal of Nutrition and Advances in Nutrition). B3 (Cheng 2024) "
                    "is a more recent independent meta-analysis from a different "
                    "author group. All three draw on overlapping but not identical "
                    "underlying study pools."
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
