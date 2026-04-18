"""
Proof: Current global warming is primarily driven by natural climate cycles rather than human CO2 emissions.
Generated: 2026-03-28
Strategy: Qualitative Consensus Proof — Disproof variant.
  Collect 3+ authoritative scientific sources explicitly stating that human CO2 emissions,
  not natural climate cycles, are the primary driver of current warming. If those sources
  are verified, the claim is DISPROVED.
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
CLAIM_NATURAL = (
    "Current global warming is primarily driven by natural climate cycles "
    "rather than human CO2 emissions."
)
CLAIM_FORMAL = {
    "subject": "Current global warming",
    "property": "primary driver is natural climate cycles (not human CO2 emissions)",
    "operator": ">=",
    "operator_note": (
        "The claim asserts natural climate cycles are the PRIMARY driver of current warming — "
        "meaning they account for more than 50% (or more than human CO2) of observed warming. "
        "This is the disproof variant: we collect authoritative scientific sources that explicitly "
        "state the opposite — that human greenhouse gas emissions, not natural cycles, are the "
        "dominant driver. Threshold = 3 independent authoritative sources confirming this counter-position. "
        "'Primary' interpreted as dominant/main driver contributing more than any other single factor. "
        "Sources from two independent U.S. government agencies (NOAA, NASA) plus IPCC-aligned statements."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_noaa_humans",
        "label": "NOAA Climate.gov: Are humans causing global warming? — scientific consensus statement",
    },
    "B2": {
        "key": "source_noaa_evidence",
        "label": "NOAA Climate.gov: What evidence exists that humans are the main cause? — ruling out natural factors",
    },
    "B3": {
        "key": "source_nasa_sun",
        "label": "NASA Science FAQ: Is the Sun causing global warming? — solar vs human attribution",
    },
    "A1": {
        "label": "Count of verified sources rejecting natural-cycle-primacy claim",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS
# Each source REJECTS the claim (confirms human CO2 is the primary driver, not natural cycles).
# Adversarial sources (supporting the claim) go in adversarial_checks below.
empirical_facts = {
    "source_noaa_humans": {
        "quote": (
            "Virtually all climate scientists agree that this increase in heat-trapping gases "
            "is the main reason for the 1.8\u00b0F (1.0\u00b0C) rise in global average temperature "
            "since the late nineteenth century."
        ),
        "url": "https://www.climate.gov/news-features/climate-qa/are-humans-causing-or-contributing-global-warming",
        "source_name": "NOAA Climate.gov — Are humans causing or contributing to global warming?",
    },
    "source_noaa_evidence": {
        "quote": (
            "no other known climate influences have changed enough to account for the observed warming trend"
        ),
        "url": "https://www.climate.gov/news-features/climate-qa/what-evidence-exists-earth-warming-and-humans-are-main-cause",
        "source_name": "NOAA Climate.gov — What evidence exists that Earth is warming and humans are the main cause?",
    },
    "source_nasa_sun": {
        "quote": (
            "It is therefore extremely unlikely that the Sun has caused the observed global temperature "
            "warming trend over the past half-century."
        ),
        "url": "https://science.nasa.gov/climate-change/faq/is-the-sun-causing-global-warming/",
        "source_name": "NASA Science — Is the Sun causing global warming?",
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
for key, result in citation_results.items():
    print(f"    {key}: {result['status']}")

# 6. CLAIM EVALUATION (Rule 4 — use compare(), never hardcode)
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified source count vs threshold",
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# These were gathered via web search BEFORE writing the proof code.
adversarial_checks = [
    {
        "question": (
            "Do any credible peer-reviewed papers argue that solar or natural cycles are "
            "the PRIMARY driver of recent warming (>50% attribution)?"
        ),
        "verification_performed": (
            "Searched 'solar cycles primary cause global warming peer-reviewed 2020 2021 2022 2023' "
            "and 'natural climate cycles primary cause warming attribution science'. "
            "Found Connolly et al. (2023, ScienceDirect) arguing solar forcing may be underestimated "
            "and Heritage Foundation (2023) questioning temperature record reliability. "
            "Examined NASA, NOAA, IPCC, WMO, American Meteorological Society, and Royal Society positions."
        ),
        "finding": (
            "No peer-reviewed paper from a major scientific institution credibly claims natural cycles "
            "account for >50% of post-1950 warming. Connolly et al. (2023) argue for a larger-than-IPCC "
            "solar contribution but still treat it as a secondary factor; Heritage Foundation is a political "
            "advocacy organization, not a scientific institution. "
            "NASA states the greenhouse gas warming forcing is 'over 270 times greater than the slight extra "
            "warming coming from the Sun itself over that same time interval' (since 1750). "
            "This adversarial check does NOT break the proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could internal variability (AMO, PDO, ENSO) account for most of the observed long-term warming trend?"
        ),
        "verification_performed": (
            "Searched IPCC AR6 attribution findings on internal variability and reviewed attribution literature. "
            "IPCC AR6 SPM quantifies: natural (solar + volcanic) drivers changed temperature by -0.1°C to +0.1°C "
            "from 1850-1900 to 2010-2019; human drivers caused 0.8°C to 1.3°C (best estimate 1.07°C). "
            "Reviewed literature on AMO, PDO, and multi-decadal variability as alternative explanations."
        ),
        "finding": (
            "IPCC AR6 attributes -0.1°C to +0.1°C to natural (solar + volcanic) drivers vs 0.8°C-1.3°C "
            "to human drivers over the industrial era. Internal oscillations (AMO, PDO) produce multi-decadal "
            "fluctuations but cannot produce a sustained, monotonically increasing century-scale warming trend — "
            "they are zero-sum over long periods. Attribution studies consistently show these cannot explain "
            "the long-term trend. This adversarial check does NOT break the proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there disagreement within the scientific community about whether CO2 or natural cycles "
            "drive current warming, such that the claim could be considered contested?"
        ),
        "verification_performed": (
            "Reviewed consensus surveys: Cook et al. (2013) found 97% of climate scientists endorsing "
            "human-caused warming consensus; Lynas et al. (2021) found 99.9% consensus in a literature survey. "
            "Reviewed positions of all major scientific organizations worldwide. "
            "Searched for any national academy of sciences or major meteorological organization "
            "that disputes human-forcing primacy."
        ),
        "finding": (
            "Multiple independent surveys of the peer-reviewed literature find 97-99.9% consensus that "
            "human activities are the dominant cause of recent warming. No national academy of sciences, "
            "meteorological organization, or major climate research institution supports the natural-cycle-primacy "
            "claim. The scientific debate concerns quantification details (exact percentages, cloud feedbacks, "
            "aerosol forcing magnitudes), not the direction of attribution. This adversarial check does NOT break the proof."
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
                "description": (
                    "Two independent U.S. government agencies (NOAA and NASA) with separate research programs "
                    "both explicitly reject natural-cycle primacy and attribute current warming to human emissions."
                ),
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "NOAA (National Oceanic and Atmospheric Administration) and NASA (National Aeronautics and "
                    "Space Administration) are independent agencies with separate research budgets, staff, and "
                    "measurement programs. Both positions are independently consistent with IPCC AR6 findings."
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
            "interpretation": (
                "claim_holds=True means enough authoritative sources REJECT the claim, "
                "yielding verdict=DISPROVED."
            ),
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
