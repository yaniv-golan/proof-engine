"""
Proof: You need to drink at least 8 glasses of water daily for optimal health regardless of thirst.
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
CLAIM_NATURAL = "You need to drink at least 8 glasses of water daily for optimal health regardless of thirst."
CLAIM_FORMAL = {
    "subject": "healthy adults",
    "property": (
        "whether drinking at least 8 glasses (~2 L) of water per day is required "
        "for optimal health, with thirst signals irrelevant to that requirement"
    ),
    "operator": ">=",
    "operator_note": (
        "The claim makes two separable assertions: "
        "(SC1) a universal fixed minimum of 8 glasses/day is required for optimal health; "
        "(SC2) this requirement applies regardless of thirst — i.e., thirst is an unreliable guide. "
        "This proof DISPROVES both sub-claims by assembling at least 3 authoritative independent "
        "sources that contradict the claim as stated. "
        "threshold=3: three independently verified source rejections are required for disproof. "
        "proof_direction='disprove': claim_holds=True triggers verdict DISPROVED. "
        "Scope: healthy adults under ordinary (non-extreme) conditions. "
        "The claim includes no caveats; the proof interprets it as applying universally. "
        "Note on the 'glasses' unit: the conventional '8x8' rule means eight 8-oz (~240 mL) "
        "glasses = ~1.9 L of water; this is the interpretation used here."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "valtin_2002",
        "label": "Valtin (2002) — peer-reviewed review finds no scientific proof for 8x8 rule",
    },
    "B2": {
        "key": "national_academies",
        "label": "National Academies (IOM DRI) — thirst is an adequate guide for healthy adults",
    },
    "B3": {
        "key": "tufts_medicine",
        "label": "Tufts Medicine (2022) — '8 glasses/day' is not a universal requirement",
    },
    "A1": {
        "label": "Verified disproof source count",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (disproof sources)
# Adversarial sources that support the claim go in adversarial_checks, not here.
empirical_facts = {
    "valtin_2002": {
        "quote": (
            "Despite the seemingly ubiquitous admonition to 'drink at least eight "
            "8-oz glasses of water a day' (with an accompanying reminder that beverages "
            "containing caffeine and alcohol do not count), rigorous proof for this "
            "counsel appears to be lacking."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/12376390/",
        "source_name": (
            "PubMed — Valtin H. (2002) 'Drink at least eight glasses of water a day.' "
            "Really? Am J Physiol Regul Integr Comp Physiol 283(5):R993–R1004"
        ),
    },
    "national_academies": {
        "quote": (
            "The vast majority of healthy people adequately meet their daily hydration "
            "needs by letting thirst be their guide"
        ),
        "url": (
            "https://www.nationalacademies.org/news/report-sets-dietary-intake-levels"
            "-for-water-salt-and-potassium-to-maintain-health-and-reduce-chronic-disease-risk"
        ),
        "source_name": (
            "National Academies of Sciences, Engineering, and Medicine — "
            "Dietary Reference Intakes for Water, Salt, and Potassium press release"
        ),
    },
    "tufts_medicine": {
        "quote": (
            "The short answer is 'no.' The more complicated answer, according to "
            "Registered Dietitian Caroline Fox, is that the actual recommended amount "
            "differs for everyone."
        ),
        "url": "https://www.tuftsmedicine.org/about-us/news/medical-myths-drink-8-glasses-water-each-day",
        "source_name": (
            "Tufts Medicine — Medical Myths: Drink 8 Glasses of Water Each Day (2022)"
        ),
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

# 6. CLAIM EVALUATION — uses compare() as required (Rule 7)
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified disproof source count vs threshold",
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# These check whether any evidence SUPPORTS the claim (would break the disproof).
adversarial_checks = [
    {
        "question": (
            "Does any major international health authority (WHO, CDC, NHS) "
            "endorse a universal '8 glasses a day regardless of thirst' rule?"
        ),
        "verification_performed": (
            "Searched: 'WHO CDC NHS 8 glasses water day recommendation'; "
            "reviewed CDC water/healthful beverages page; WHO drinking-water guidelines; "
            "NHS 'How much water should I drink?' page."
        ),
        "finding": (
            "No major international health authority endorses a universal 8-glasses/day "
            "minimum regardless of thirst. The CDC recommends water as a healthy beverage "
            "choice without specifying 8 glasses. The NHS advises approximately 6–8 cups "
            "of fluid per day but explicitly includes all fluids and ties it to thirst and "
            "activity. WHO sets no universal fixed daily amount for healthy adults."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Are there healthy-adult sub-populations (athletes, hot-climate workers) "
            "for whom 8 glasses regardless of thirst is the recommended standard?"
        ),
        "verification_performed": (
            "Searched: 'athletes hydration regardless of thirst recommendation'; "
            "reviewed ACSM (American College of Sports Medicine) hydration position statement; "
            "reviewed heat-exposure hydration protocols for occupational settings."
        ),
        "finding": (
            "Athletes and individuals in extreme heat may require more than 8 glasses, "
            "but guidance is always individualized to sweat rate, exercise intensity, and "
            "ambient conditions — not a fixed 'regardless of thirst' rule. The ACSM "
            "recommends thirst-guided drinking as an acceptable strategy during exercise "
            "for most athletes. The claim as stated applies universally with no caveats; "
            "no authority supports that framing."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there peer-reviewed evidence that thirst-guided drinking leads to "
            "clinically significant dehydration or health harm in healthy adults "
            "under normal everyday conditions?"
        ),
        "verification_performed": (
            "Searched: 'thirst unreliable dehydration healthy adults evidence'; "
            "reviewed Millard-Stafford et al. (2012) Nutr Rev 70(S2):S147–51 (PMID 23121351); "
            "reviewed Cotter et al. (2014) Extreme Physiol Med (PMC4212586)."
        ),
        "finding": (
            "Thirst reliability is more nuanced in older adults (>65) and during vigorous "
            "exercise, where the thirst response can lag behind actual fluid needs. "
            "However, neither paper — nor any study found — documents clinically significant "
            "harm from thirst-guided drinking in healthy non-elderly adults under normal "
            "everyday (non-extreme) conditions. The National Academies DRI explicitly "
            "names thirst as an adequate guide for healthy people. The Valtin (2002) review "
            "found no evidence that any amount above ad libitum (thirst-driven) intake "
            "improves health in healthy adults."
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
    FACT_REGISTRY["A1"]["result"] = f"{n_confirmed} independent disproof sources confirmed"

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
                "description": "Multiple independent institutions independently reject the claim",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Three distinct institutional sources are used: "
                    "(1) a peer-reviewed journal review article (Valtin 2002, Am J Physiol), "
                    "(2) the National Academies of Sciences, Engineering, and Medicine "
                    "(IOM Dietary Reference Intakes — the authoritative US nutrition body), "
                    "(3) Tufts Medical Center clinical dietitian expertise. "
                    "These are independent in authorship, institutional affiliation, and "
                    "methodology; all three converge on the same conclusion."
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
