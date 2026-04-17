"""
Proof: Extreme weather events (hurricanes, wildfires, floods) have become dramatically
more frequent and intense solely because of climate change.
Generated: 2026-03-28

Claim structure: This is a conjunction of four sub-claims:
  SC1: Extreme weather events have become more frequent
  SC2: Extreme weather events have become more intense
  SC3: The change is "dramatic"
  SC4: Climate change is the *sole* cause

A conjunction is false if any conjunct is false. This proof focuses on falsifying SC4,
which is the most clearly contradicted by scientific literature. SC1 is also only
partially true (global hurricane frequency has not clearly increased).
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "Extreme weather events (hurricanes, wildfires, floods) have become dramatically "
    "more frequent and intense solely because of climate change."
)
CLAIM_FORMAL = {
    "subject": "Extreme weather events (hurricanes, wildfires, floods)",
    "property": "causal attribution of increased frequency and intensity",
    "operator": ">=",
    "operator_note": (
        "The claim is a conjunction of four sub-claims: "
        "(SC1) extreme weather events have increased in frequency; "
        "(SC2) they have increased in intensity; "
        "(SC3) the change is 'dramatic'; "
        "(SC4) climate change is the *sole* cause. "
        "A conjunction is false when any conjunct is false. SC4 is the clearest falsifier: "
        "if scientific literature identifies ANY non-climate factor as a contributing cause, "
        "the claim is disproved. "
        "This proof tests SC4 by counting independent authoritative sources that explicitly "
        "document non-climate drivers of extreme weather (aerosol forcing, urbanization, "
        "land use change, fire suppression history). "
        "Threshold: 3 independent sources confirming non-climate drivers suffices to disprove SC4. "
        "SC1 is also only partially true: global hurricane frequency has not clearly increased "
        "(NOAA GFDL). SC2 and SC3 have stronger support for some event types."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "source_gfdl",     "label": "NOAA GFDL: Atlantic hurricane frequency partly driven by aerosol changes, not solely greenhouse gases"},
    "B2": {"key": "source_usgs",     "label": "USGS: urbanization independently increases the size and frequency of floods"},
    "B3": {"key": "source_pnasnexus","label": "PNAS Nexus: wildfire risk is a confluence of climate change AND development (WUI expansion)"},
    "B4": {"key": "source_ipcc",     "label": "IPCC AR6 Ch.11: attribution cites greenhouse gases, aerosol emissions, AND land-use changes as separate human influences"},
    "A1": {"label": "Count of independent sources confirming non-climate drivers of extreme weather", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources confirming the claim is FALSE (non-climate drivers documented)
# proof_direction = "disprove": these sources confirm that non-climate factors exist,
# thereby falsifying the "solely because of climate change" qualifier in SC4.
empirical_facts = {
    "source_gfdl": {
        "quote": (
            "the increase in tropical storm frequency in the Atlantic basin since the 1970s "
            "has been at least partly driven by decreases in aerosols from human activity "
            "and volcanic forcing."
        ),
        "url": "https://www.gfdl.noaa.gov/global-warming-and-hurricanes/",
        "source_name": "NOAA Geophysical Fluid Dynamics Laboratory (GFDL) — Global Warming and Hurricanes",
    },
    "source_usgs": {
        "quote": (
            "Urbanization generally increases the size and frequency of floods and may "
            "expose communities to increasing flood hazards."
        ),
        "url": "https://pubs.usgs.gov/fs/fs07603/",
        "source_name": "U.S. Geological Survey (USGS) Fact Sheet FS-076-03 — Effects of Urban Development on Floods",
    },
    "source_pnasnexus": {
        "quote": (
            "Wildfire risk lies in the confluence of climate change and development in the WUI"
        ),
        "url": "https://academic.oup.com/pnasnexus/article/3/5/pgae151/7665998",
        "source_name": "PNAS Nexus — Wildfire risk management in the era of climate change (2024)",
    },
    "source_ipcc": {
        "quote": (
            "Evidence of observed changes in extremes and their attribution to human influence "
            "(including greenhouse gas and aerosol emissions and land-use changes) has strengthened "
            "since AR5"
        ),
        "url": "https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-11/",
        "source_name": "IPCC Sixth Assessment Report (AR6) Working Group I — Chapter 11: Weather and Climate Extreme Events",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS (supporting the disproof)
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources (non-climate drivers documented): {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — MUST use compare()
# claim_holds=True means we have confirmed enough sources documenting non-climate drivers,
# which (combined with proof_direction="disprove") yields a DISPROVED verdict.
claim_holds = compare(n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                      label="SC4 disproof: verified sources confirming non-climate drivers >= 3")

# 7. ADVERSARIAL CHECKS (Rule 5)
# For a disproof proof: adversarial checks search for sources *supporting* the original claim
# (i.e., claiming climate change is the sole cause). Finding strong support would weaken the disproof.
adversarial_checks = [
    {
        "question": "Does any mainstream scientific organization claim climate change is the *sole* cause of extreme weather?",
        "verification_performed": (
            "Searched IPCC AR6 Chapter 11, NOAA, NASA, and WMO statements for language claiming "
            "'solely', 'only', or 'exclusively' climate change drives extreme weather. "
            "IPCC AR6 consistently lists 'greenhouse gas and aerosol emissions and land-use changes' "
            "as separate contributing human influences. NOAA GFDL explicitly names aerosol changes "
            "and natural variability as distinct factors. No mainstream scientific body uses the "
            "word 'solely' in attributing extreme weather to climate change alone."
        ),
        "finding": (
            "No major scientific organization claims climate change is the sole cause. "
            "All authoritative sources identify multiple drivers. This confirms SC4 is false "
            "and strengthens the disproof."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is SC1 (frequency increase) fully true for all three event types?",
        "verification_performed": (
            "Reviewed NOAA GFDL on global hurricane frequency: "
            "'global tropical cyclone frequency timeseries do not show evidence for significant "
            "rising trends.' Also: 'after adjusting for a likely under-count of hurricanes in the "
            "pre-satellite era there is essentially no long-term trend in hurricane counts.' "
            "IPCC AR6 confirms heavy precipitation and heat extremes have increased globally. "
            "Wildfire burned area has increased in western US and globally. "
            "Flood frequency shows regional variation with urbanization as a major driver."
        ),
        "finding": (
            "SC1 is only partially true. Global hurricane COUNT has NOT clearly increased — "
            "a direct contradiction of 'more frequent' for that event type. "
            "Heat extremes, heavy precipitation, and wildfire area have increased. "
            "This is an additional reason the claim fails beyond SC4."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could 'solely' be charitably interpreted as 'primarily' rather than 'exclusively'?",
        "verification_performed": (
            "Linguistic analysis: 'solely' in standard English means 'only' or 'exclusively'. "
            "Example: 'I did this solely for you' means no other motive exists. "
            "Merriam-Webster: 'solely' = 'without another; only'. "
            "The claim says events became more frequent/intense 'solely because of climate change', "
            "leaving no room for other causes under any standard reading."
        ),
        "finding": (
            "Even the most charitable reading of 'solely' means 'exclusively.' "
            "Reinterpreting it as 'primarily' would change the claim's content, not clarify it. "
            "The disproof stands under any standard linguistic interpretation."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could aerosol forcing and land-use changes themselves be caused by climate change, making them indirect effects rather than separate causes?",
        "verification_performed": (
            "Examined the logical structure: aerosol reductions (clean air regulations), "
            "urbanization, and WUI expansion are human socioeconomic and policy choices independent "
            "of greenhouse gas warming. NOAA GFDL explicitly lists 'aerosols from human activity' "
            "as a separate forcing distinct from greenhouse gas warming. Urbanization is driven by "
            "population growth and economic development. These are not consequences of climate change."
        ),
        "finding": (
            "Aerosol policy changes, urbanization, and WUI development are independent human "
            "activities not caused by greenhouse gas warming. They are genuinely separate causal "
            "factors, not indirect effects of climate change. The 'solely' qualifier remains falsified."
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
    elif claim_holds and not any_unverified and is_disproof:
        verdict = "DISPROVED"
    elif claim_holds and any_unverified and is_disproof:
        verdict = "DISPROVED (with unverified citations)"
    elif not claim_holds:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(citations with status in {COUNTABLE_STATUSES}) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = str(n_confirmed)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: for qualitative proofs, record citation verification status per source
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
                "description": "Multiple independent institutions consulted (NOAA, USGS, PNAS Nexus, IPCC)",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from four distinct institutions: NOAA (federal agency), "
                    "USGS (federal agency), PNAS Nexus (peer-reviewed journal), and "
                    "IPCC (intergovernmental scientific body). Each addresses a different "
                    "event type (hurricanes, floods, wildfires, general attribution), "
                    "confirming the finding is not institution-specific."
                ),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirmed_non_climate_sources": n_confirmed,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
            "sc4_falsified": claim_holds,
            "sc1_frequency_fully_true": False,
            "sc1_note": "Global hurricane frequency has not clearly increased (NOAA GFDL)",
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
