"""
Proof: Hair and fingernails continue to grow for days after a person dies.
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
CLAIM_NATURAL = "Hair and fingernails continue to grow for days after a person dies."
CLAIM_FORMAL = {
    "subject": "Human hair and fingernails",
    "property": "post-mortem biological growth",
    "operator": ">=",
    "operator_note": (
        "This is a disproof: we seek >= 3 independent authoritative sources that "
        "explicitly reject the claim that hair and nails grow after death. The claim "
        "asserts active biological growth continues for days post-mortem. Sources must "
        "confirm that (a) growth requires living cellular processes (glucose, oxygen, "
        "hormonal regulation) that cease at death, and (b) the appearance of growth "
        "is an optical illusion caused by skin dehydration and retraction."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "source_pmc", "label": "BMJ 'Medical Myths' peer-reviewed article (PMC/NCBI)"},
    "B2": {"key": "source_uams", "label": "UAMS Health (University of Arkansas Medical Sciences)"},
    "B3": {"key": "source_factmyth", "label": "FactMyth.com science reference"},
    "A1": {"label": "Verified source count meeting disproof threshold", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it is false)
empirical_facts = {
    "source_pmc": {
        "quote": (
            "Dehydration of the body after death and drying or desiccation may lead "
            "to retraction of the skin around the hair or nails. The actual growth of "
            "hair and nails, however, requires a complex hormonal regulation not "
            "sustained after death."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2151163/",
        "source_name": "BMJ Medical Myths (Vreeman & Carroll, 2007) via PMC/NCBI",
    },
    "source_uams": {
        "quote": (
            "Hair and fingernails may appear longer after death, but not because they "
            "are still growing. After death, dehydration causes the skin and other "
            "soft tissues to shrink. This occurs while the hair and nails remain the "
            "same length. This change in the body creates the optical illusion of "
            "growth people observe."
        ),
        "url": "https://uamshealth.com/medical-myths/do-a-persons-hair-and-fingernails-continue-to-grow-after-death/",
        "source_name": "University of Arkansas for Medical Sciences (UAMS Health)",
    },
    "source_factmyth": {
        "quote": (
            "Hair and nail growth requires active, living cells. When a person dies, "
            "their heart stops pumping blood, meaning the hair follicles no longer "
            "receive the necessary nutrients and oxygen for cell division."
        ),
        "url": "https://factmyth.com/factoids/hair-and-nails-continue-to-grow-after-death/",
        "source_name": "FactMyth.com",
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

# 6. CLAIM EVALUATION — MUST use compare()
claim_holds = compare(n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                      label="verified source count vs disproof threshold")

# 7. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Is there any credible scientific evidence that hair or nails actually grow after death?",
        "verification_performed": (
            "Searched for: 'scientific evidence hair nails DO grow after death cells "
            "continue dividing briefly'. Reviewed results from PMC, Live Science, "
            "Washington Post, BBC Science Focus, Quora, and multiple science sites."
        ),
        "finding": (
            "No credible scientific source supports the claim. Every authoritative "
            "source (BMJ, university medical centers, forensic science references) "
            "confirms it is a myth. One nuance noted: death is not instantaneous, "
            "and some cells survive briefly after cardiac arrest, but this does not "
            "include the complex cellular division and protein synthesis required "
            "for measurable hair or nail growth."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could brief post-mortem cellular activity produce any measurable hair or nail growth?",
        "verification_performed": (
            "Searched for: 'post mortem cellular activity hair growth brief'. "
            "Reviewed forensic pathology explanations."
        ),
        "finding": (
            "While some cells (e.g., skin cells) can survive briefly after cardiac "
            "arrest due to residual oxygen, hair and nail growth specifically requires "
            "sustained glucose supply, hormonal regulation, and blood circulation. "
            "No forensic or medical source documents any measurable post-mortem growth. "
            "The BMJ article explicitly states the 'complex hormonal regulation' is "
            "'not sustained after death.'"
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is the 'skin retraction' explanation itself contested in forensic literature?",
        "verification_performed": (
            "Searched for: 'post mortem skin retraction dehydration forensic science "
            "mechanism'. Reviewed forensic pathology descriptions."
        ),
        "finding": (
            "The dehydration/skin retraction mechanism is universally accepted in "
            "forensic pathology. It is described consistently across medical, academic, "
            "and forensic sources as the explanation for the apparent 'growth' illusion. "
            "No credible source contests this mechanism."
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
        "cross_checks": [
            {
                "description": "Multiple independent sources consulted to disprove the claim",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from independent institutions: BMJ (peer-reviewed journal "
                    "via PMC), UAMS (university medical center), and FactMyth (science "
                    "reference). Each independently explains the myth using the same "
                    "underlying biology (dehydration/retraction), which strengthens the "
                    "disproof — independent sources converge on the same explanation."
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
