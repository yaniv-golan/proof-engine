"""
Proof: The twin paradox in special relativity can be resolved only by invoking
general relativity and the acceleration of the traveling twin.
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

# =============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# =============================================================================
CLAIM_NATURAL = (
    "The twin paradox in special relativity can be resolved only by invoking "
    "general relativity and the acceleration of the traveling twin."
)
CLAIM_FORMAL = {
    "subject": "Resolution of the twin paradox",
    "property": "Whether general relativity is required for resolution",
    "operator": ">=",
    "operator_note": (
        "The claim asserts that GR is REQUIRED (the word 'only'). To disprove this, "
        "we need >= 3 independent authoritative physics sources that explicitly state "
        "the twin paradox can be resolved within special relativity alone, without "
        "invoking general relativity. The 'only' makes this a strong exclusivity claim: "
        "finding that SR suffices is a direct counterexample. Note: the claim conflates "
        "two ideas — (a) GR is required, and (b) acceleration is the key. The physics "
        "consensus is that (a) is false and (b) is partially true but misleading: "
        "acceleration marks the asymmetry but the resolution uses SR's relativity of "
        "simultaneity, not GR's equivalence principle."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# =============================================================================
# 2. FACT REGISTRY
# =============================================================================
FACT_REGISTRY = {
    "B1": {"key": "ucr_physics_faq", "label": "UCR Physics FAQ states GR is not required"},
    "B2": {"key": "wikipedia_twin", "label": "Wikipedia states SR alone resolves the paradox"},
    "B3": {"key": "scientific_american", "label": "Scientific American states SR suffices"},
    "B4": {"key": "unsw_einstein_light", "label": "UNSW Einstein Light states GR is unnecessary"},
    "A1": {"label": "Verified source count meeting disproof threshold", "method": None, "result": None},
}

# =============================================================================
# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it is false)
# =============================================================================
empirical_facts = {
    "ucr_physics_faq": {
        "quote": (
            "Some people claim that the twin paradox can or even must be resolved "
            "only by invoking General Relativity (which is built on the Equivalence "
            "Principle). This is not true"
        ),
        "url": "https://math.ucr.edu/home/baez/physics/Relativity/SR/TwinParadox/twin_intro.html",
        "source_name": "UCR Physics FAQ (maintained by John Baez)",
    },
    "wikipedia_twin": {
        "quote": (
            "this scenario can be resolved within the standard framework of special "
            "relativity: the travelling twin's trajectory involves two different "
            "inertial frames"
        ),
        "url": "https://en.wikipedia.org/wiki/Twin_paradox",
        "source_name": "Wikipedia — Twin paradox",
    },
    "scientific_american": {
        "quote": (
            "The paradox can be unraveled by special relativity alone, and the "
            "accelerations incurred by the traveler are incidental"
        ),
        "url": "https://www.scientificamerican.com/article/how-does-relativity-theor/",
        "source_name": "Scientific American",
    },
    "unsw_einstein_light": {
        "quote": (
            "appealing to General Relativity is not necessary to resolve the paradox"
        ),
        "url": "https://www.phys.unsw.edu.au/einsteinlight/jw/module4_twin_paradox.htm",
        "source_name": "UNSW School of Physics — Einstein Light",
    },
}

# =============================================================================
# 4. CITATION VERIFICATION (Rule 2)
# =============================================================================
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# =============================================================================
# 5. COUNT SOURCES WITH VERIFIED CITATIONS
# =============================================================================
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# =============================================================================
# 6. CLAIM EVALUATION — MUST use compare()
# =============================================================================
claim_holds = compare(
    n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
    label="verified source count vs disproof threshold"
)

# =============================================================================
# 7. ADVERSARIAL CHECKS (Rule 5)
# =============================================================================
adversarial_checks = [
    {
        "question": "Are there credible sources that claim GR IS required to resolve the twin paradox?",
        "verification_performed": (
            "Searched for: '\"twin paradox\" \"requires general relativity\"'. Found "
            "Britannica states: 'A full treatment requires general relativity, which "
            "shows that there would be an asymmetrical change in time between the two "
            "sisters.' However, this is contradicted by multiple authoritative physics "
            "sources (UCR Physics FAQ, Scientific American, UNSW, Wikipedia) which "
            "explicitly state GR is not required. The Britannica article appears to "
            "conflate the need to handle non-inertial frames (which SR can do) with "
            "the need for GR (which is about curved spacetime/gravity). The UCR FAQ "
            "directly addresses and refutes this common misconception."
        ),
        "finding": (
            "One general encyclopedia (Britannica) makes this claim, but it is "
            "contradicted by multiple specialist physics sources. The physics consensus "
            "is that SR alone suffices."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Can the twin paradox be formulated without any acceleration at all?",
        "verification_performed": (
            "Searched for twin paradox relay version / no-acceleration variant. "
            "Wikipedia confirms: 'it has been proven that neither general relativity, "
            "nor even acceleration, are necessary to explain the effect, as the effect "
            "still applies if two astronauts pass each other at the turnaround point.' "
            "This is the 'relay' or 'triplet' version where no single clock accelerates "
            "but time dilation still occurs, showing acceleration is not the cause."
        ),
        "finding": (
            "The relay version of the twin paradox demonstrates that even acceleration "
            "is not required — only the change of inertial frame matters. This further "
            "undermines the claim that GR (which handles acceleration via the equivalence "
            "principle) is needed."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Did Einstein himself believe GR was needed for the twin paradox?",
        "verification_performed": (
            "Searched for Einstein's own analysis. The UCR FAQ's Equivalence Principle "
            "page notes: 'The Equivalence Principle analysis of the twin paradox does "
            "not use any real gravity, and so does not use any General Relativity.' "
            "Einstein did analyze the twin paradox using the equivalence principle in "
            "1918, but modern physics recognizes this as a pedagogical choice, not a "
            "theoretical necessity. The FAQ states: 'no one ever needs to, to analyse "
            "the paradox.'"
        ),
        "finding": (
            "While Einstein used GR concepts in his 1918 analysis, modern physics "
            "consensus holds this was not necessary. The equivalence principle analysis "
            "is supplementary, not required."
        ),
        "breaks_proof": False,
    },
]

# =============================================================================
# 8. VERDICT AND STRUCTURED OUTPUT
# =============================================================================
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
                    "Sources span: a curated physics FAQ (UCR/Baez), a general "
                    "encyclopedia (Wikipedia), a science magazine (Scientific American), "
                    "and a university physics department (UNSW). These are independent "
                    "publications from different institutions and authors."
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
