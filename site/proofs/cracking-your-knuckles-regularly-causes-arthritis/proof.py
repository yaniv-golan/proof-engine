"""
Proof: Cracking your knuckles regularly causes arthritis later in life.
Generated: 2026-03-28
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "Cracking your knuckles regularly causes arthritis later in life."
CLAIM_FORMAL = {
    "subject": "habitual knuckle cracking",
    "property": "causal relationship with arthritis (osteoarthritis of the hand)",
    "operator": ">=",
    "operator_note": (
        "This is a disproof by scientific consensus. The claim asserts a causal link "
        "between habitual knuckle cracking and arthritis. To disprove, we need >= 3 "
        "independent authoritative sources (peer-reviewed studies, major medical institutions) "
        "that explicitly find no such causal relationship. The threshold of 3 is appropriate "
        "given the abundance of published research on this topic."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "harvard_health", "label": "Harvard Health: no arthritis risk from knuckle cracking"},
    "B2": {"key": "jabfm_deweber_2011", "label": "Deweber et al. 2011 (JABFM): no association between KC and hand OA"},
    "B3": {"key": "castellanos_1990", "label": "Castellanos & Axelrod 1990 (PMC): no increased arthritis in crackers"},
    "B4": {"key": "hopkins_arthritis", "label": "Johns Hopkins Arthritis Center: no evidence KC causes arthritis"},
    "A1": {"label": "Verified source count", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it's false)
empirical_facts = {
    "harvard_health": {
        "quote": "Cracking your knuckles may aggravate the people around you, but it probably won't raise your risk for arthritis.",
        "url": "https://www.health.harvard.edu/pain/does-cracking-knuckles-cause-arthritis",
        "source_name": "Harvard Health Publishing",
    },
    "jabfm_deweber_2011": {
        "quote": "A history of habitual KC does not seem to be a risk factor for hand OA.",
        "url": "https://www.jabfm.org/content/24/2/169",
        "source_name": "Journal of the American Board of Family Medicine (Deweber et al. 2011)",
    },
    "castellanos_1990": {
        "quote": "There was no increased preponderance of arthritis of the hand in either group",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC1004074/",
        "source_name": "Annals of the Rheumatic Diseases (Castellanos & Axelrod 1990)",
    },
    "hopkins_arthritis": {
        "quote": "There is no evidence that cracking knuckles causes any damage such as arthritis in the joints.",
        "url": "https://www.hopkinsarthritis.org/arthritis-news/knuckle-cracking-q-a-from/",
        "source_name": "Johns Hopkins Arthritis Center",
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
claim_holds = compare(n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                      label="verified source count vs threshold")

# 7. ADVERSARIAL CHECKS (Rule 5) — search for sources SUPPORTING the claim
adversarial_checks = [
    {
        "question": "Are there any peer-reviewed studies that found knuckle cracking causes arthritis?",
        "verification_performed": (
            "Searched PubMed and Google Scholar for 'knuckle cracking causes arthritis' "
            "and 'knuckle cracking osteoarthritis positive association'. Reviewed all "
            "returned studies."
        ),
        "finding": (
            "No peer-reviewed study was found that establishes a causal link between "
            "knuckle cracking and arthritis. Every study that examined this question "
            "found no association."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does the Castellanos 1990 study's finding of reduced grip strength suggest joint damage leading to arthritis?",
        "verification_performed": (
            "Reviewed the Castellanos & Axelrod 1990 study findings. The study found "
            "hand swelling and lower grip strength in habitual crackers but explicitly "
            "stated there was no increased preponderance of arthritis."
        ),
        "finding": (
            "Reduced grip strength and hand swelling are functional effects, not evidence "
            "of arthritis. The same study that found these effects explicitly ruled out "
            "an arthritis association. Grip strength loss is not a precursor to osteoarthritis."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the mechanism of knuckle cracking (cavitation bubbles in synovial fluid) theoretically damage cartilage?",
        "verification_performed": (
            "Searched for 'knuckle cracking cavitation cartilage damage mechanism'. "
            "Reviewed biomechanical literature."
        ),
        "finding": (
            "The sound is caused by gas bubble formation/collapse in synovial fluid. "
            "No study has demonstrated that this process damages articular cartilage "
            "or leads to degenerative joint changes. The forces involved are well below "
            "the threshold for cartilage injury."
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
        verdict = ("DISPROVED (with unverified citations)" if is_disproof
                   else "PROVED (with unverified citations)")
    elif not claim_holds:
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
                "description": "Multiple independent sources consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from different institutions: Harvard Medical School, "
                    "Journal of the American Board of Family Medicine (peer-reviewed study), "
                    "Annals of the Rheumatic Diseases (peer-reviewed study via PMC), and "
                    "Johns Hopkins Arthritis Center. These represent independent research "
                    "groups and editorial boards — not republications of the same study."
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
