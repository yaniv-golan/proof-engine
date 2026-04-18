"""
Proof: The Pyramid of Giza was built by slaves.
Generated: 2026-03-29
Proof direction: DISPROVE — archaeological consensus contradicts the "slaves" narrative.
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
CLAIM_NATURAL = "The Pyramid of Giza was built by slaves."
CLAIM_FORMAL = {
    "subject": "Great Pyramid of Giza (Pyramid of Khufu)",
    "property": "primary workforce consisted of enslaved persons",
    "operator": ">=",
    "operator_note": (
        "The claim is interpreted as asserting that the primary labor force "
        "constructing the Great Pyramid was enslaved. We disprove this by "
        "showing that the archaeological and documentary consensus — including "
        "physical tombs, skeletal analysis, administrative papyri, and graffiti "
        "from named work gangs — uniformly identifies the builders as paid or "
        "conscripted free Egyptian laborers, not slaves. "
        "Threshold of 3 independently verified sources expressing this consensus "
        "is required to support disproof. A single source would be insufficient; "
        "three independent institutions/publications are required."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_cbs",
        "label": "CBS News: Zahi Hawass statement on workers' tombs proving non-slave status",
    },
    "B2": {
        "key": "source_aap",
        "label": "AAP Fact Check: Dr. Karin Sowada on Wadi el-Jarf papyri describing skilled non-slave workers",
    },
    "B3": {
        "key": "source_hawass_tombs",
        "label": "Guardians.net: Zahi Hawass official description of pyramid builders as conscripted peasants, not slaves",
    },
    "A1": {
        "label": "Verified source count (sources whose quotes appear on their cited page)",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS
# These sources all REJECT the "built by slaves" claim — they confirm the disproof's conclusion.
empirical_facts = {
    "source_cbs": {
        "quote": (
            "No way would they have been buried so honorably if they were slaves"
        ),
        "url": "https://www.cbsnews.com/news/more-evidence-slaves-didnt-build-pyramids/",
        "source_name": "CBS News — More Evidence Slaves Didn't Build Pyramids",
    },
    "source_aap": {
        "quote": (
            "But the pyramids were not built by slaves."
        ),
        "url": "https://www.aap.com.au/factcheck/the-pyramids-of-giza-were-not-built-by-slaves/",
        "source_name": "AAP FactCheck — The pyramids of Giza were not built by slaves",
    },
    "source_hawass_tombs": {
        "quote": (
            "The pyramid builders were not slaves but peasants conscripted on a rotating "
            "part-time basis, working under the supervision of skilled artisans and craftsmen "
            "who not only built the pyramid complexes for the kings and nobility, but also "
            "designed and constructed their own, more modest tombs."
        ),
        "url": "https://www.guardians.net/hawass/buildtomb.htm",
        "source_name": "Guardians.net — Zahi Hawass: Discovery of the Tombs of the Pyramid Builders",
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

# 6. CLAIM EVALUATION — uses compare(), per Rule 7 / template requirement
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified sources rejecting 'built by slaves' vs threshold",
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# These are sources/arguments that SUPPORT the "built by slaves" claim.
# Searched and investigated before writing this proof.
adversarial_checks = [
    {
        "question": (
            "Does any modern Egyptologist or peer-reviewed study support the "
            "hypothesis that the Great Pyramid was built primarily by slaves?"
        ),
        "verification_performed": (
            "Searched: 'Egyptologist peer-reviewed pyramid built by slaves' and "
            "'pyramid slave labor archaeology study'. Found no peer-reviewed study "
            "supporting slave labor at Giza. The consensus in academic Egyptology is "
            "uniformly against the slave hypothesis since the 1990 tomb discoveries."
        ),
        "finding": (
            "No modern Egyptologist or academic study supports the slave-labor hypothesis. "
            "Hawass, Lehner (Harvard), Sowada (Macquarie University), and the Egyptian "
            "Ministry of Antiquities all reject it."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does ancient Greek historian Herodotus directly say the pyramids were "
            "built by slaves, and is his account considered reliable?"
        ),
        "verification_performed": (
            "Searched: 'Herodotus pyramid slaves quote reliability'. Herodotus (c. 450 BCE) "
            "wrote that Khufu used 'a hundred thousand men' in rotating shifts but did not "
            "explicitly call them slaves — he describes an oppressed populace under a tyrant. "
            "His account predates modern Egyptology by 2,400 years, and archaeologists note "
            "that Herodotus visited Egypt roughly 2,000 years after the pyramids were built "
            "and was recording local oral tradition, not eyewitness testimony."
        ),
        "finding": (
            "Herodotus does not explicitly call the builders slaves, and his account is "
            "widely regarded by modern Egyptologists as unreliable on this point. The "
            "Wadi el-Jarf papyri (discovered 2013) — actual contemporary documentation — "
            "supersedes Herodotus as a primary source."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could some portion of the workforce have been slaves even if the "
            "majority were free workers?"
        ),
        "verification_performed": (
            "Searched: 'pyramid builders some slaves mixed workforce ancient Egypt'. "
            "Slavery did exist in ancient Egypt, primarily prisoners of war and debt bondage. "
            "However, no archaeological evidence places enslaved persons in the Giza "
            "workforce specifically. The workers' village, papyri, and tombs all point "
            "to a conscripted/paid free Egyptian labor force."
        ),
        "finding": (
            "While slavery existed in ancient Egypt, no evidence supports enslaved labor "
            "at Giza specifically. The claim under evaluation asserts the pyramid 'was "
            "built by slaves' — implying slaves as the primary workforce — which contradicts "
            "the archaeological record. The disproof addresses this interpretation."
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

    FACT_REGISTRY["A1"]["method"] = (
        f"count(verified citations rejecting 'built by slaves') = {n_confirmed}"
    )
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
                "description": "Multiple independent sources consulted from different institutions",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Source B1 is CBS News reporting on Egyptian government archaeology. "
                    "Source B2 is AAP FactCheck citing Dr. Karin Sowada (Macquarie University). "
                    "Source B3 is Zahi Hawass's own publication on the tomb discovery. "
                    "All three are independently published; B2 traces to an independent "
                    "academic source (Sowada) distinct from Hawass."
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
