"""
Proof: You must wait at least 30 minutes after eating before swimming or you will suffer dangerous cramps.
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
CLAIM_NATURAL = "You must wait at least 30 minutes after eating before swimming or you will suffer dangerous cramps."
CLAIM_FORMAL = {
    "subject": "swimming after eating",
    "property": "whether swimming within 30 minutes of eating causes dangerous cramps",
    "operator": ">=",
    "operator_note": (
        "This is a disproof. The claim asserts a causal link: eating + swimming within 30 min = "
        "dangerous cramps. 'Dangerous' implies cramps severe enough to cause drowning or serious "
        "injury. We seek >= 3 independent authoritative sources that reject this causal claim. "
        "The claim is a compound assertion: (1) swimming after eating causes cramps, AND "
        "(2) those cramps are dangerous. If either sub-claim is rejected by medical consensus, "
        "the overall claim is disproved."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "duke_health", "label": "Duke Health: myth that blood diversion causes dangerous cramps is unfounded"},
    "B2": {"key": "uams_health", "label": "UAMS Health: no medical evidence supports the myth"},
    "B3": {"key": "britannica", "label": "Britannica: science does not support the food-drowning link"},
    "B4": {"key": "ilsf", "label": "International Life Saving Federation: no evidence eating before swimming increases drowning risk"},
    "A1": {"label": "Verified source count meeting disproof threshold", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it's false)
empirical_facts = {
    "duke_health": {
        "quote": "the blood going to your digestive tract after eating steals the blood needed to keep your arms and legs pumping during swimming is unfounded",
        "url": "https://www.dukehealth.org/blog/myth-or-fact-should-you-wait-swim-after-eating",
        "source_name": "Duke Health (Duke University Health System)",
    },
    "uams_health": {
        "quote": "there is no medical evidence to support the myth",
        "url": "https://uamshealth.com/medical-myths/do-you-have-to-wait-30-minutes-after-eating-before-swimming/",
        "source_name": "UAMS Health (University of Arkansas for Medical Sciences)",
    },
    "britannica": {
        "quote": "The chances of suffering a stomach cramp while swimming are remote, regardless of when the swimmer last ate",
        "url": "https://www.britannica.com/story/is-it-really-dangerous-to-swim-after-eating",
        "source_name": "Encyclopaedia Britannica",
    },
    "ilsf": {
        "quote": "eating before swimming does not increase the risk of drowning",
        "url": "https://www.ilsf.org/wp-content/uploads/2018/11/MPS-18-2014-Eating-before-Swimming.pdf",
        "source_name": "International Life Saving Federation (ILSF)",
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
        "question": "Is there any peer-reviewed study showing that eating before swimming causes dangerous cramps or drowning?",
        "verification_performed": (
            "Searched for 'eating before swimming cramps dangerous evidence support' across "
            "medical databases and general web. Reviewed results from Duke Health, UAMS, Mayo Clinic, "
            "Red Cross, Britannica, ILSF, and multiple other medical sources."
        ),
        "finding": (
            "No peer-reviewed study was found that supports the claim. Multiple sources explicitly "
            "state that no documented case of drowning caused by swimming on a full stomach has ever "
            "been recorded in medical literature."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Do any major medical or safety organizations recommend waiting 30 minutes after eating before swimming?",
        "verification_performed": (
            "Searched for current recommendations from American Academy of Pediatrics, American Red Cross, "
            "International Life Saving Federation, and Mayo Clinic regarding eating and swimming."
        ),
        "finding": (
            "Neither the American Academy of Pediatrics nor the American Red Cross makes any specific "
            "recommendation about waiting after eating before swimming. The ILSF explicitly states "
            "the recommendation is unfounded. The 2011 Red Cross Scientific Advisory Council review "
            "found no evidence of danger."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could strenuous competitive swimming after a large meal pose some risk, even if recreational swimming does not?",
        "verification_performed": (
            "Searched for 'competitive swimming eating cramps exercise intensity' to check if the "
            "claim has any validity for extreme exercise conditions."
        ),
        "finding": (
            "Some sources note mild discomfort (nausea, minor cramps) is possible during vigorous "
            "exercise after eating, but characterize this as inconvenient, not dangerous. No source "
            "describes exercise-associated cramps after eating as a drowning risk. The claim specifies "
            "'dangerous cramps,' which is not supported even for strenuous swimming."
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
                    "Sources are from different institutions: Duke University Health System, "
                    "University of Arkansas for Medical Sciences, Encyclopaedia Britannica, "
                    "and the International Life Saving Federation. These represent independent "
                    "medical, academic, and reference organizations."
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
