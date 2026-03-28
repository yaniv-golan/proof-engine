"""
Proof: The Great Wall of China is the only man-made object visible from space with the naked eye.
Generated: 2026-03-28

This is a compound claim with two sub-claims:
  SC1: The Great Wall of China is visible from space with the naked eye.
  SC2: It is the ONLY man-made object so visible.

Both sub-claims are false. The claim is DISPROVED.
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
CLAIM_NATURAL = "The Great Wall of China is the only man-made object visible from space with the naked eye."
CLAIM_FORMAL = {
    "subject": "The Great Wall of China",
    "property": "number of independent authoritative sources confirming the claim is false",
    "operator": ">=",
    "operator_note": (
        "This is a compound claim: (SC1) the Great Wall is visible from space with the naked eye, "
        "AND (SC2) it is the ONLY man-made object so visible. For disproof, we need authoritative "
        "sources confirming EITHER sub-claim is false. In fact, both sub-claims are false: "
        "SC1 is contradicted by NASA and multiple astronauts who confirm the wall is NOT visible "
        "with the naked eye from space; SC2 is contradicted by the fact that many other man-made "
        "structures (highways, cities, dams, greenhouses) ARE visible from low Earth orbit. "
        "'Space' is interpreted as low Earth orbit (~200-400 km altitude, e.g. ISS), the most "
        "favorable interpretation for the claim. Even at this altitude, the wall is not visible. "
        "Threshold of 3 sources required for disproof, following standard consensus guidance."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "nasa_great_wall", "label": "NASA official statement: wall not visible without high-powered lenses"},
    "B2": {"key": "sci_am_astronaut", "label": "Scientific American: astronaut Jeffrey Hoffman confirms wall not visible"},
    "B3": {"key": "britannica_wall", "label": "Britannica: Great Wall not visible with naked eye from space"},
    "B4": {"key": "wikipedia_structures", "label": "Wikipedia: highways, dams, and cities visible from space without magnification"},
    "A1": {"label": "Verified source count for disproof", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it's false)
empirical_facts = {
    "nasa_great_wall": {
        "quote": (
            "Despite myths to the contrary, the wall isn't visible from the moon, "
            "and is difficult or impossible to see from Earth orbit without the "
            "high-powered lenses used for this photo."
        ),
        "url": "https://www.nasa.gov/image-article/great-wall/",
        "source_name": "NASA",
    },
    "sci_am_astronaut": {
        "quote": (
            "I have spent a lot of time looking at the Earth from space, including "
            "numerous flights over China, and I never saw the wall"
        ),
        "url": "https://www.scientificamerican.com/article/is-chinas-great-wall-visible-from-space/",
        "source_name": "Scientific American (quoting NASA astronaut Jeffrey Hoffman)",
    },
    "britannica_wall": {
        "quote": (
            "You typically can't see the Great Wall of China from space"
        ),
        "url": "https://www.britannica.com/question/Can-you-see-the-Great-Wall-of-China-from-space",
        "source_name": "Encyclopaedia Britannica",
    },
    "wikipedia_structures": {
        "quote": (
            "Artificial structures visible from space without magnification include "
            "highways, dams, and cities"
        ),
        "url": "https://en.wikipedia.org/wiki/Artificial_structures_visible_from_space",
        "source_name": "Wikipedia: Artificial structures visible from space",
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
                      label="verified source count vs threshold for disproof")

# 7. ADVERSARIAL CHECKS (Rule 5) — search for sources that SUPPORT the claim
adversarial_checks = [
    {
        "question": "Are there credible sources that say the Great Wall IS visible from space with the naked eye?",
        "verification_performed": (
            "Searched for 'Great Wall of China visible from space confirmed' and "
            "'astronauts who saw Great Wall from space'. Found that astronauts Eugene Cernan "
            "and Ed Lu reported seeing the wall under specific lighting conditions (low sun angle "
            "creating shadows), but these observations are disputed and may involve camera-assisted "
            "viewing. NASA's official position remains that it is not visible with the naked eye."
        ),
        "finding": (
            "A small number of astronauts claim to have seen the wall under very specific "
            "lighting conditions, but these reports are disputed. China's first astronaut Yang Liwei "
            "could not see it, and Canadian astronaut Chris Hadfield explicitly stated it is not visible. "
            "NASA's official page states it is 'difficult or impossible to see from Earth orbit without "
            "high-powered lenses.' The scientific consensus is clearly against visibility."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is there any basis for the claim that no OTHER man-made objects are visible from space?",
        "verification_performed": (
            "Searched for 'only man-made structure visible from space' and reviewed multiple sources. "
            "Every credible source lists numerous structures visible from low Earth orbit including "
            "highways, cities at night, dams, greenhouses in Almeria Spain, airports, and the "
            "Bingham Canyon Mine. The Scientific American article notes that 'the Houston airport is "
            "visible long before the Great Wall of China.'"
        ),
        "finding": (
            "No credible source supports the claim that the Great Wall is the only visible structure. "
            "Multiple man-made structures are routinely visible from space, making this sub-claim "
            "completely false."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does the definition of 'space' matter — could the claim be true at some altitude?",
        "verification_performed": (
            "Reviewed definitions of 'space' (Karman line at 100km, ISS at ~400km, Moon at ~384,000km). "
            "At no altitude is the Great Wall the only visible structure. At ISS altitude, many structures "
            "are visible. At lunar distance, NO man-made structures are visible at all, including the wall."
        ),
        "finding": (
            "At any reasonable definition of 'space', the claim fails. At low orbit: many structures "
            "are visible, the wall generally is not. At lunar distance: nothing man-made is visible."
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
                "description": "Multiple independent sources consulted for disproof",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from different institutions: NASA (government space agency), "
                    "Scientific American (science journalism), Encyclopaedia Britannica (reference), "
                    "and Wikipedia (encyclopedic summary of multiple sources). Each represents an "
                    "independent editorial decision to publish the same conclusion."
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
            "sc1_status": "FALSE — Great Wall not visible from space with naked eye (NASA, astronauts)",
            "sc2_status": "FALSE — many man-made structures visible from space (highways, cities, dams)",
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
