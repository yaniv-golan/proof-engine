"""
Proof: Lightning never strikes the same place twice.
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
CLAIM_NATURAL = "Lightning never strikes the same place twice."
CLAIM_FORMAL = {
    "subject": "Lightning",
    "property": "whether lightning can strike the same location more than once",
    "operator": ">=",
    "operator_note": (
        "The claim asserts lightning NEVER strikes the same place twice — an absolute "
        "universal negative. To DISPROVE this, we need authoritative sources confirming "
        "that lightning DOES strike the same place repeatedly. A threshold of 3 independent "
        "authoritative sources confirming repeated strikes is used. The claim is disproved "
        "if >= 3 sources confirm it is false."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "nws_myths", "label": "NWS Lightning Myths page: lightning often strikes same place repeatedly"},
    "B2": {"key": "nssl_faq", "label": "NOAA NSSL FAQ: lightning does hit the same spot more than once"},
    "B3": {"key": "nasa_spinoff", "label": "NASA Spinoff: lightning often strikes the same place twice"},
    "B4": {"key": "britannica", "label": "Britannica: lightning can and will strike the same place twice"},
    "A1": {"label": "Verified source count confirming claim is false", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it is false)
empirical_facts = {
    "nws_myths": {
        "quote": "Lightning often strikes the same place repeatedly, especially if it's a tall, pointy, isolated object. The Empire State Building is hit an average of 23 times a year",
        "url": "https://www.weather.gov/safety/lightning-myths",
        "source_name": "National Weather Service (NWS)",
        "snapshot": (
            "Lightning Myths. Myth: Lightning never strikes the same place twice. "
            "Fact: Lightning often strikes the same place repeatedly, especially if "
            "it's a tall, pointy, isolated object. The Empire State Building is hit "
            "an average of 23 times a year."
        ),
    },
    "nssl_faq": {
        "quote": "Lightning does hit the same spot (or almost the same spot) more than once, contrary to folk wisdom",
        "url": "https://www.nssl.noaa.gov/education/svrwx101/lightning/faq/",
        "source_name": "NOAA National Severe Storms Laboratory (NSSL)",
        "snapshot": (
            "Does lightning strike the same place twice? "
            "Lightning does hit the same spot (or almost the same spot) more than once, "
            "contrary to folk wisdom. It can happen by statistical chance or because "
            "something about the site makes it somewhat more likely to be struck. "
            "Taller objects are more likely than shorter objects to produce the upward "
            "channel."
        ),
    },
    "nasa_spinoff": {
        "quote": "Contrary to popular misconception, lightning often strikes the same place twice",
        "url": "https://spinoff.nasa.gov/Spinoff2005/ps_3.html",
        "source_name": "NASA Spinoff",
    },
    "britannica": {
        "quote": "lightning can and will strike the same place twice, whether it be during the same storm or even centuries later",
        "url": "https://www.britannica.com/story/can-lightning-strike-the-same-place-twice",
        "source_name": "Encyclopaedia Britannica",
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

# 7. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Is there any scientific evidence supporting the claim that lightning never strikes the same place twice?",
        "verification_performed": (
            "Searched for 'lightning never strikes same place twice any truth defense of saying'. "
            "Reviewed results from Britannica, NWS, NOAA, Merriam-Webster, and multiple science "
            "education sites."
        ),
        "finding": (
            "No scientific source supports the literal claim. Every authoritative meteorological "
            "source explicitly identifies it as a myth. The phrase is recognized only as a "
            "metaphorical/idiomatic expression (Merriam-Webster defines it as meaning "
            "'an unusual event is not likely to happen again to the same person or in the same place')."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the claim be interpreted in a more defensible way (e.g., exact same microscopic point)?",
        "verification_performed": (
            "Analyzed whether lightning could be said to never strike the exact same molecular "
            "coordinates. Reviewed NSSL FAQ on lightning strike precision."
        ),
        "finding": (
            "Even under the most charitable interpretation, the claim fails. The NSSL notes "
            "lightning hits 'the same spot (or almost the same spot)' repeatedly. Lightning "
            "channels are meters wide, and the same structures (buildings, towers, trees) are "
            "struck thousands of times over their lifetimes. The claim cannot be salvaged by "
            "appealing to microscopic precision."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Are the sources independently authored or do they all cite the same study?",
        "verification_performed": (
            "Checked provenance of each source: NWS (federal weather safety page), "
            "NSSL (federal severe storms research lab), NASA (space technology spinoff article), "
            "Britannica (independent encyclopedia). Each is authored by a different organization "
            "with independent editorial processes."
        ),
        "finding": (
            "All four sources are from different institutions with independent editorial authority. "
            "NWS and NSSL are both NOAA entities but have separate missions and publication pipelines. "
            "NASA and Britannica are fully independent."
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
                "description": "Multiple independent sources consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from 4 different institutions: NWS, NSSL, NASA, Britannica. "
                    "NWS and NSSL are both NOAA entities but have separate editorial pipelines. "
                    "NASA and Britannica are fully independent organizations."
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
