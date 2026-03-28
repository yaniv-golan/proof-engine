"""
Proof: Bulls charge because they are enraged by the color red.
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
CLAIM_NATURAL = "Bulls charge because they are enraged by the color red."
CLAIM_FORMAL = {
    "subject": "Bulls (Bos taurus, particularly fighting bulls)",
    "property": "Whether charging behavior is caused by rage triggered by the color red",
    "operator": ">=",
    "operator_note": (
        "This is a causal claim with two components: (1) bulls perceive and are enraged by red, "
        "and (2) this rage causes their charging behavior. Scientific evidence shows cattle are "
        "dichromatic and cannot distinguish red from green, and that movement — not color — "
        "triggers charging. We disprove by finding >= 3 independent authoritative sources that "
        "reject the claim. The threshold of 3 reflects strong scientific consensus."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "source_a", "label": "Peer-reviewed study: cattle have dichromatic vision (two cone types, no red receptor)"},
    "B2": {"key": "source_b", "label": "University science Q&A: red does not make bulls angry, they lack red retina receptor"},
    "B3": {"key": "source_c", "label": "Science publication: bulls respond to movement of cape, not its color"},
    "A1": {"label": "Verified source count meeting disproof threshold", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it's false)
empirical_facts = {
    "source_a": {
        "quote": (
            "Electroretinogram (ERG) flicker photometry was used to measure the spectral "
            "properties of cones in three common ungulates-cattle (Bos taurus), goats "
            "(Capra hircus), and sheep (Ovis aries). Two cone mechanisms were identified "
            "in each species."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/9685209/",
        "source_name": "Jacobs et al. 1998, Visual Neuroscience (PubMed)",
    },
    "source_b": {
        "quote": (
            "The color red does not make bulls angry. "
            "Cattle lack the red retina receptor and can only see yellow, green, blue, and violet colors."
        ),
        "url": "https://www.wtamu.edu/~cbaird/sq/2012/12/12/what-is-it-about-red-that-makes-bulls-so-angry/",
        "source_name": "West Texas A&M University — Science Questions with Surprising Answers",
    },
    "source_c": {
        "quote": (
            "It's not the color, but rather the movement of the cape and the bullfighter "
            "that makes bulls so angry."
        ),
        "url": "https://www.scienceabc.com/nature/animals/do-bulls-really-hate-red-colour-blind.html",
        "source_name": "ScienceABC — Do Bulls Really Hate the Color Red?",
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
                      label="verified source count vs disproof threshold")

# 7. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Is there any scientific study showing bulls can perceive red or are trichromatic?",
        "verification_performed": (
            "Searched for 'cattle trichromatic vision' and 'bulls see red color scientific evidence'. "
            "All results confirm cattle are dichromatic with two cone types (S-cone ~444-455nm, "
            "M/L-cone ~552-555nm). No peer-reviewed study was found claiming cattle have a red "
            "cone receptor or trichromatic vision."
        ),
        "finding": "No credible source supports cattle having red color perception. Jacobs et al. (1998) is the definitive photopigment study.",
        "breaks_proof": False,
    },
    {
        "question": "Is there any experimental evidence that red specifically triggers aggression in bulls more than other colors?",
        "verification_performed": (
            "Searched for 'bulls actually do see red color evidence support myth true'. "
            "Found MythBusters (Discovery Channel, 2007) ran controlled experiments: "
            "(1) stationary red, blue, and white flags received equal attacks; "
            "(2) a moving blue flag was charged while a stationary red flag was ignored; "
            "(3) a motionless person in red was ignored while moving bullfighters were charged. "
            "No source was found showing red triggers more aggression than other colors."
        ),
        "finding": "All experimental evidence confirms movement, not color, triggers charging. No counter-evidence found.",
        "breaks_proof": False,
    },
    {
        "question": "Could the traditional use of red capes indicate that matadors observed a real color preference?",
        "verification_performed": (
            "Searched for 'why matadors use red cape history bullfighting muleta'. "
            "Multiple sources explain the red muleta is used in the final stage (tercio de muerte) "
            "to mask blood splatters from the audience. The earlier stages use a larger magenta-and-yellow "
            "capote. The color choice is for human spectators, not the bull."
        ),
        "finding": "Red cape tradition is for masking blood from audience, not based on bull color preference.",
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
                "description": "Multiple independent sources consulted from different domains",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Source A is a peer-reviewed neuroscience paper (Jacobs et al. 1998, Visual Neuroscience). "
                    "Source B is a university physics department Q&A (West Texas A&M). "
                    "Source C is a science education publication (ScienceABC). "
                    "These represent independent publications from different institutions and domains "
                    "(primary research, academic outreach, science journalism)."
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
