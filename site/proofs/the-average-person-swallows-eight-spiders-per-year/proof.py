"""
Proof: The average person swallows eight spiders per year while sleeping.
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
CLAIM_NATURAL = "The average person swallows eight spiders per year while sleeping."
CLAIM_FORMAL = {
    "subject": "the average person",
    "property": "number of spiders swallowed per year while sleeping",
    "operator": ">=",
    "operator_note": (
        "The claim asserts a specific rate of 8 spiders/year. To disprove it, we seek "
        "authoritative sources confirming the claim is a myth with no scientific basis. "
        "Using the qualitative consensus disproof template: if >= 3 independent "
        "authoritative sources confirm the claim is false, verdict is DISPROVED. "
        "Threshold of 3 chosen because this is a widely-addressed myth with many "
        "authoritative sources available."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "scientific_american", "label": "Scientific American: spider-swallowing myth debunked"},
    "B2": {"key": "burke_museum", "label": "Burke Museum (arachnology dept): no formal record of spider ingestion"},
    "B3": {"key": "britannica", "label": "Britannica: we swallow no spiders at all"},
    "B4": {"key": "sleep_foundation", "label": "Sleep Foundation: no proof spiders crawl into mouths"},
    "A1": {"label": "Verified source count meets disproof threshold", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it's false)
empirical_facts = {
    "scientific_american": {
        "quote": "The myth flies in the face of both spider and human biology, which makes it highly unlikely that a spider would ever end up in your mouth.",
        "url": "https://www.scientificamerican.com/article/fact-or-fiction-people-swallow-8-spiders-a-year-while-they-sleep1/",
        "source_name": "Scientific American",
    },
    "burke_museum": {
        "quote": "For a sleeping person to swallow even one live spider would involve so many highly unlikely circumstances that for practical purposes we can rule out the possibility.",
        "url": "https://www.burkemuseum.org/collections-and-research/biology/arachnology-and-entomology/spider-myths/myth-you-swallow-spiders",
        "source_name": "Burke Museum — Arachnology & Entomology",
    },
    "britannica": {
        "quote": "The reality, however, is quite different: we swallow no spiders at all.",
        "url": "https://www.britannica.com/story/do-we-really-swallow-spiders-in-our-sleep",
        "source_name": "Encyclopaedia Britannica",
    },
    "sleep_foundation": {
        "quote": "There is no proof that spiders crawl into people's mouths while they are sleeping.",
        "url": "https://www.sleepfoundation.org/sleep-faqs/how-many-spiders-do-you-eat-in-your-sleep",
        "source_name": "Sleep Foundation",
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
        "question": "Is there any scientific study that confirms people swallow spiders in their sleep?",
        "verification_performed": (
            "Searched for: 'swallow spiders sleep scientific study evidence confirmed'. "
            "Reviewed results from Scientific American, Burke Museum, Britannica, "
            "Sleep Foundation, HowStuffWorks, Discover Magazine, and ScienceDirect. "
            "Also found a ScienceDirect paper titled 'Believing that Humans Swallow "
            "Spiders in Their Sleep: False Beliefs as Side Effects of the Processes "
            "that Support Accurate Knowledge' — which studies the myth's persistence, "
            "not its truth."
        ),
        "finding": (
            "No scientific study, medical record, or sleep research study has ever "
            "documented a case of a person swallowing a spider while sleeping. "
            "Every source found unanimously debunks the claim."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the claim have a legitimate scientific origin that was later misrepresented?",
        "verification_performed": (
            "Searched for the origin of the claim. Multiple sources (Snopes, Britannica, "
            "Scientific American) trace it to a 1993 PC Professional magazine column by "
            "Lisa Holst, who deliberately included it as an example of ridiculous 'facts' "
            "that people would uncritically believe. However, Snopes later noted that the "
            "Lisa Holst origin story itself may be apocryphal — the magazine article has "
            "never been independently located."
        ),
        "finding": (
            "Regardless of whether the Lisa Holst origin is real, no legitimate "
            "scientific study has ever supported the claim. The origin is either "
            "a deliberate fabrication to illustrate gullibility, or an untraceable "
            "piece of folklore. Neither constitutes scientific evidence."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is it biologically plausible that spiders would enter a sleeping person's mouth?",
        "verification_performed": (
            "Reviewed entomological explanations from Scientific American and Burke Museum. "
            "Rod Crawford (Burke Museum arachnologist) and other experts explain that "
            "spiders are sensitive to vibrations from breathing, heartbeat, and snoring; "
            "sleeping humans are warm, moist, and create air currents — all things spiders "
            "avoid. Spiders have no biological incentive to enter a mouth."
        ),
        "finding": (
            "Spider biology and behavior make it extremely unlikely a spider would "
            "approach a sleeping human's mouth. Vibrations, warmth, moisture, and "
            "air currents all deter spiders. Experts consider it practically impossible."
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
                    "Sources are from different institutions: Scientific American "
                    "(science journalism), Burke Museum (academic museum / arachnology), "
                    "Encyclopaedia Britannica (reference encyclopedia), and Sleep Foundation "
                    "(health/sleep nonprofit). Each independently debunks the claim."
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
