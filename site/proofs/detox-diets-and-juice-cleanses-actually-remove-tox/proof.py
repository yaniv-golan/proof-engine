"""
Proof: Detox diets and juice cleanses actually remove toxins from the body.
Generated: 2026-03-28
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
CLAIM_NATURAL = "Detox diets and juice cleanses actually remove toxins from the body."
CLAIM_FORMAL = {
    "subject": "Detox diets and juice cleanses",
    "property": "actually remove toxins from the body beyond what normal organ function achieves",
    "operator": ">=",
    "operator_note": (
        "The claim asserts that commercial detox diets and juice cleanses have a real, "
        "measurable effect on removing toxins — beyond what the liver, kidneys, and other "
        "organs already do. We disprove this by showing that 3 or more independent authoritative "
        "medical/scientific sources explicitly state there is no clinical evidence for this mechanism. "
        "threshold=3 applies the standard consensus bar: three independently verified sources from "
        "different institutions must confirm the disproof."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "urmc", "label": "URMC: detoxing through diet is a myth"},
    "B2": {"key": "pubmed_review", "label": "PubMed review: no compelling clinical evidence for detox diet toxin elimination"},
    "B3": {"key": "harvard_health", "label": "Harvard Health: cannot cleanse body through diet, per scientific reality"},
    "B4": {"key": "cleveland_clinic", "label": "Cleveland Clinic: no scientific research proving cleanses offer claimed health benefits"},
    "A1": {"label": "Verified source count", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it is false)
empirical_facts = {
    "urmc": {
        "quote": "No. The concept of detoxing by eating or drinking certain diets is a myth.",
        "url": "https://www.urmc.rochester.edu/news/publications/health-matters/do-juice-cleanses-detox-the-body",
        "source_name": "University of Rochester Medical Center — Do Juice Cleanses Detox the Body?",
    },
    "pubmed_review": {
        "quote": "there is very little clinical evidence to support the use of these diets",
        "url": "https://pubmed.ncbi.nlm.nih.gov/25522674/",
        "source_name": "PubMed — Detox diets for toxin elimination and weight management: a critical review of the evidence (2015)",
    },
    "harvard_health": {
        "quote": 'Searching the medical literature for "detox diets" or "cleanse diets" yields almost no relevant, high-quality medical evidence demonstrating health benefits.',
        "url": "https://www.health.harvard.edu/blog/harvard-health-ad-watch-whats-being-cleansed-in-a-detox-cleanse-2020032519294",
        "source_name": "Harvard Health — Harvard Health Ad Watch: What's being cleansed in a detox cleanse?",
    },
    "cleveland_clinic": {
        "quote": "Research doesn't support many health claims linked to detoxification programs",
        "url": "https://health.clevelandclinic.org/detox-cleanse",
        "source_name": "Cleveland Clinic — Detox or Cleanse? What To Know Before You Start",
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
        "question": "Are there any clinical studies showing detox diets effectively remove toxins?",
        "verification_performed": (
            "Searched PubMed and Google Scholar for clinical studies showing that commercial detox "
            "diets or juice cleanses measurably remove toxins. The 2015 systematic review (B2) "
            "acknowledged that 'a handful of clinical studies have shown that commercial detox diets "
            "enhance liver detoxification and eliminate persistent organic pollutants from the body,' "
            "but explicitly concluded these studies are 'hampered by flawed methodologies and small "
            "sample sizes' and that 'no randomised controlled trials have been conducted to assess "
            "the effectiveness of commercial detox diets in humans.' No high-quality RCT evidence was found."
        ),
        "finding": (
            "A small number of low-quality studies with positive results exist, but the peer-reviewed "
            "consensus (B2) is that these are methodologically flawed and no RCTs have been conducted. "
            "The existence of weak, flawed studies does not constitute credible clinical evidence and "
            "does not break the disproof."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could 'detox' refer to a clinically recognized process that some diets support?",
        "verification_performed": (
            "Searched for medical definitions of 'detoxification' in the context of diet. URMC (B1) "
            "states 'The liver and kidneys remove toxins and waste. If we were holding onto toxins, "
            "we wouldn't be alive.' Cleveland Clinic (B4) states the body's digestive tract, liver, "
            "kidneys, and skin break down toxins daily without special cleanses. Harvard Health (B3) "
            "notes 'it's not even clear what toxin or toxins a cleanse is supposed to remove.' "
            "The term 'toxins' in detox marketing is consistently found to be undefined and unverifiable."
        ),
        "finding": (
            "Medical authorities confirm the body performs toxin elimination via liver/kidneys continuously. "
            "The term 'toxins' in commercial detox marketing is undefined and no specific toxin has been "
            "shown to be measurably reduced by detox diets. Does not break the disproof."
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
                "description": "Multiple independent sources from different institutions consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from four different institutions: "
                    "University of Rochester Medical Center, PubMed/academic peer review, "
                    "Harvard Medical School, and Cleveland Clinic — all independently rejecting the claim."
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
