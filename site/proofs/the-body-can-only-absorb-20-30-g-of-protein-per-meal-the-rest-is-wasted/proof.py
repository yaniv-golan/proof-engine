"""
Proof: The body can only absorb 20-30 g of protein per meal; the rest is wasted.
Generated: 2026-04-01
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
CLAIM_NATURAL = "The body can only absorb 20-30 g of protein per meal; the rest is wasted."
CLAIM_FORMAL = {
    "subject": "Human protein absorption and utilization per meal",
    "property": (
        "Number of independent peer-reviewed sources establishing that "
        "(1) there is no fixed 20-30 g per-meal ceiling on protein absorption or utilization, "
        "AND (2) protein ingested above any such threshold is not simply 'wasted' (excreted unused)"
    ),
    "operator": ">=",
    "operator_note": (
        "The claim makes two assertions: (A) a hard 20-30 g per-meal protein absorption ceiling "
        "exists, and (B) protein above that ceiling is wasted. Both are tested together: a source "
        "qualifies as a rebuttal if it establishes that protein utilization or anabolism continues "
        "beyond 20-30 g/meal, or that excess amino acids are metabolized for energy/other purposes "
        "rather than excreted unused. Proof direction is 'disprove' — sources must REJECT the claim. "
        "Threshold of 3 independent peer-reviewed sources is required. "
        "Note: studies showing that MPS rates plateau around 20 g of whey protein in the "
        "short-term post-exercise window do NOT support the claim as stated, because "
        "they measure synthesis rate optimization, not absorption capacity, and do not show "
        "that excess protein is excreted unused."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "schoenfeld_aragon_2018", "label": "Schoenfeld & Aragon 2018 (JISSN) — protein dose-response review"},
    "B2": {"key": "trommelen_2023", "label": "Trommelen et al. 2023 (Cell Reports Medicine) — 100 g single-meal RCT"},
    "B3": {"key": "deutz_wolfe_2013", "label": "Deutz & Wolfe 2013 (Clinical Nutrition) — anabolic upper limit review"},
    "A1": {"label": "Verified source count (peer-reviewed sources rejecting the 20-30 g cap claim)", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it is false)
# These are all open-access PMC articles; quotes are from the abstract or main body.
empirical_facts = {
    "schoenfeld_aragon_2018": {
        "quote": (
            "the preponderance of data indicate that while consumption of higher protein doses "
            "(> 20 g) results in greater AA oxidation, this is not the fate for all the "
            "additional ingested AAs as some are utilized for tissue-building purposes"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5828430/",
        "source_name": (
            "Schoenfeld BJ, Aragon AA. How much protein can the body use in a single meal "
            "for muscle-building? Implications for daily protein distribution. "
            "J Int Soc Sports Nutr. 2018;15(1):10. PMC5828430."
        ),
    },
    "trommelen_2023": {
        "quote": (
            "The anabolic response to protein ingestion has no apparent upper limit in "
            "magnitude and duration in vivo in humans"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10772463/",
        "source_name": (
            "Trommelen J, van Lieshout GAA, Nyakayiru J, Holwerda AM, Smeets JSJ, "
            "Hendriks FK, van Kranenburg JMX, Zorenc AH, Senden JM, Goessens JPB, "
            "Gijsen AP, van Loon LJC. The anabolic response to protein ingestion during "
            "recovery from exercise has no upper limit in magnitude and duration in vivo "
            "in humans. Cell Rep Med. 2023;4(12):101324. PMC10772463."
        ),
    },
    "deutz_wolfe_2013": {
        "quote": (
            "There is no practical upper limit to the anabolic response to protein or "
            "amino acid intake in the context of a meal"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3595342/",
        "source_name": (
            "Deutz NE, Wolfe RR. Is there a maximal anabolic response to protein intake "
            "with a meal? Clin Nutr. 2013;32(2):309-313. PMC3595342."
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT VERIFIED SOURCES
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — uses compare(), never hardcoded
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="SC: peer-reviewed sources rejecting the 20-30 g absorption cap claim",
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# These check for evidence that *supports* the claim (sources searched during Step 2).
adversarial_checks = [
    {
        "question": (
            "Do peer-reviewed studies directly support a hard 20-30 g per-meal "
            "protein absorption ceiling?"
        ),
        "verification_performed": (
            "Searched PubMed and Google Scholar for 'protein absorption 20g per meal limit', "
            "'protein meal size muscle protein synthesis ceiling', and 'maximum protein per meal'. "
            "Found Moore et al. 2009 (Am J Clin Nutr 89:161-168) showing MPS plateaus around "
            "20 g of whey post-exercise, and Areta et al. 2013 (J Physiol 591:2319-2331) showing "
            "20 g every 3 hours was optimal for MPS during a 12-hour recovery window."
        ),
        "finding": (
            "Moore et al. 2009 and Areta et al. 2013 showed that 20 g of whey protein "
            "optimized MUSCLE PROTEIN SYNTHESIS RATES in acute, tightly-controlled post-exercise "
            "windows. Neither study measures gut absorption capacity, and neither claims protein "
            "above 20 g is excreted unused. Moore et al. used fast-digesting isolated whey; "
            "mixed meals with slower proteins extend the utilization window. Neither study "
            "addresses the 'wasted' claim. The Trommelen 2023 study (B2) directly tested 100 g "
            "in a single meal using isotope tracers and found protein incorporation into muscle "
            "continued for 12+ hours, refuting the ceiling interpretation."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the ISSN position stand endorse a hard 20-40 g per meal limit "
            "that would support the claim?"
        ),
        "verification_performed": (
            "Searched for ISSN protein exercise position stand; reviewed "
            "Jager et al. 2017 (J Int Soc Sports Nutr, PMC5477153) and the ISSN nutrient "
            "timing position stand (Kerksick et al. 2017, PMC5596471)."
        ),
        "finding": (
            "The ISSN position (Jager et al. 2017) frames 0.25 g/kg or 20-40 g per meal as "
            "a performance optimization recommendation for muscle protein synthesis. It does NOT "
            "claim protein above this amount is wasted or that intestinal absorption is capped. "
            "The recommendation is an ergogenic dosing target, not a physiological absorption limit."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there a meaningful distinction between gut 'absorption' and cellular 'utilization' "
            "that could rescue any part of the claim?"
        ),
        "verification_performed": (
            "Searched 'intestinal protein absorption capacity per meal physiology' and reviewed "
            "Boirie et al. 1997 (PNAS 94:14930) on fast vs slow proteins and Guadagni & Biolo "
            "2009 (Curr Opin Clin Nutr Metab Care 12:58) on protein kinetics. Also reviewed "
            "the discussion section of Schoenfeld & Aragon 2018."
        ),
        "finding": (
            "Gut absorption of dietary protein is essentially complete (>90%) for all common "
            "protein sources regardless of meal size — the intestine does not have a 20-30 g "
            "ceiling. What studies sometimes show is that MUSCLE PROTEIN SYNTHESIS STIMULATION "
            "has diminishing returns above ~20 g of fast whey in certain contexts. However, "
            "Schoenfeld & Aragon 2018 explicitly state that additional AAs go to tissue-building "
            "beyond 20 g, and Deutz & Wolfe 2013 note that higher protein also suppresses protein "
            "breakdown (net anabolism continues). Any rescue of the claim via this distinction "
            "would require redefining 'absorb' to mean 'maximally stimulate MPS from whey in "
            "isolation' — which is not the plain meaning of the claim."
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
                "description": "Multiple independent peer-reviewed sources consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from different research groups and journals: "
                    "Schoenfeld/Aragon (review, multiple US institutions, JISSN), "
                    "Trommelen et al. (RCT, Maastricht University, Cell Reports Medicine), "
                    "Deutz/Wolfe (review, Texas A&M/UT Medical Branch, Clinical Nutrition). "
                    "All published in different peer-reviewed journals."
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
