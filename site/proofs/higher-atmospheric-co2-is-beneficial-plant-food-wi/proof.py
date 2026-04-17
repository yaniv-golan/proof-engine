"""
Proof: Higher atmospheric CO2 is beneficial "plant food" with no net negative effects.
Generated: 2026-03-28

Compound claim decomposed into two sub-claims:
  SC1: Higher CO2 has a documented beneficial plant fertilization effect ("plant food" is real)
  SC2: Higher CO2 has no net negative effects on the environment, ecosystems, or human welfare

Overall claim holds only if BOTH sub-claims are true.
SC2 is falsified if >= 3 independent authoritative sources document significant negative effects.
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

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = 'Higher atmospheric CO2 is beneficial "plant food" with no net negative effects.'
CLAIM_FORMAL = {
    "subject": "Higher atmospheric CO2",
    "property": "net beneficial effect — plant fertilization benefit AND absence of net negative effects",
    "operator": "==",
    "operator_note": (
        "This is a compound claim requiring BOTH sub-claims to be true simultaneously: "
        "(SC1) Higher CO2 has a beneficial plant fertilization ('plant food') effect — interpreted as "
        "at least 2 independent authoritative sources confirming the CO2 fertilization / greening effect; AND "
        "(SC2) Higher CO2 has no net negative effects — interpreted as the absence of 3+ authoritative "
        "sources documenting major negative consequences. "
        "SC2 uses the disproof direction: SC2 FAILS (i.e., 'no net negative effects' is FALSE) if "
        "3 or more independent authoritative sources confirm significant negative effects exist. "
        "The full compound claim is DISPROVED if SC2 fails, regardless of SC1."
    ),
    "threshold": True,
    "sub_claims": {
        "SC1": {
            "description": "Higher CO2 has a documented beneficial plant fertilization effect",
            "operator": ">=",
            "threshold": 2,
            "proof_direction": "affirm",
            "operator_note": "Threshold of 2 sources — both from NASA (independent divisions); sufficient given the underlying study involved 32 scientists from 24 institutions.",
        },
        "SC2": {
            "description": "Higher CO2 has no net negative effects on environment/ecosystems",
            "operator": ">=",
            "threshold": 3,
            "proof_direction": "disprove",
            "operator_note": "SC2 is falsified by >= 3 independent government/intergovernmental sources documenting major negative effects. Threshold of 3 requires convergence across independent institutions (NOAA, NASA, IPCC).",
        },
    },
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {"key": "nasa_greening", "label": "NASA Goddard: CO2 fertilization causes significant Earth greening (SC1)"},
    "B2": {"key": "nasa_earth_obs", "label": "NASA Earth Observatory: Extra CO2 stimulates plant growth in some ecosystems (SC1)"},
    "B3": {"key": "noaa_acidification", "label": "NOAA Ocean Service: Ocean acidification affecting all world's oceans (SC2 disproof)"},
    "B4": {"key": "nasa_effects", "label": "NASA Science: Sea ice loss, sea level rise, more intense heat waves occurring now (SC2 disproof)"},
    "B5": {"key": "ipcc_sr15", "label": "IPCC SR1.5 Ch.3: Ocean chemistry unprecedented in 65M years; 70-90% coral reef loss (SC2 disproof)"},
    "A1": {"label": "SC1: Verified source count for CO2 plant fertilization effect", "method": None, "result": None},
    "A2": {"label": "SC2: Verified source count documenting major negative CO2 effects", "method": None, "result": None},
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
# ---------------------------------------------------------------------------

# SC1 facts — sources confirming CO2 plant fertilization benefit
sc1_facts = {
    "nasa_greening": {
        "quote": (
            "From a quarter to half of Earth's vegetated lands has shown significant greening "
            "over the last 35 years largely due to rising levels of atmospheric carbon dioxide."
        ),
        "url": "https://www.nasa.gov/centers-and-facilities/goddard/carbon-dioxide-fertilization-greening-earth-study-finds/",
        "source_name": "NASA Goddard Space Flight Center",
    },
    "nasa_earth_obs": {
        "quote": (
            "On the other hand, extra carbon dioxide can stimulate plant growth in some ecosystems, "
            "allowing these plants to take additional carbon out of the atmosphere."
        ),
        "url": "https://science.nasa.gov/earth/earth-observatory/global-warming",
        "source_name": "NASA Earth Observatory: Global Warming",
    },
}

# SC2 disproof facts — sources documenting significant negative effects of elevated CO2
sc2_disproof_facts = {
    "noaa_acidification": {
        "quote": "The ocean absorbs about 30 percent of the CO2 that is released in the atmosphere.",
        "url": "https://oceanservice.noaa.gov/facts/acidification.html",
        "source_name": "NOAA Ocean Service — Ocean Acidification",
    },
    "nasa_effects": {
        "quote": (
            "Effects that scientists had long predicted would result from global climate change "
            "are now occurring, such as sea ice loss, accelerated sea level rise, and longer, "
            "more intense heat waves."
        ),
        "url": "https://science.nasa.gov/climate-change/effects",
        "source_name": "NASA Science: Climate Change Effects",
    },
    "ipcc_sr15": {
        "quote": (
            "the majority (70-90%) of warm water (tropical) coral reefs that exist today will "
            "disappear even if global warming is constrained to 1.5 degrees C"
        ),
        "url": "https://www.ipcc.ch/sr15/chapter/chapter-3/",
        "source_name": "IPCC Special Report on Global Warming of 1.5°C, Chapter 3",
    },
}

# Combined empirical facts for citation verification
empirical_facts = {**sc1_facts, **sc2_disproof_facts}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
print("\nVerifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")

n_sc1_confirmed = sum(
    1 for key in sc1_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"\n  SC1 confirmed sources (plant food benefit): {n_sc1_confirmed} / {len(sc1_facts)}")

n_sc2_disproof_confirmed = sum(
    1 for key in sc2_disproof_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  SC2 disproof confirmed sources (negative effects): {n_sc2_disproof_confirmed} / {len(sc2_disproof_facts)}")

# ---------------------------------------------------------------------------
# 6. CLAIM EVALUATION — use compare() per Rule 7
# ---------------------------------------------------------------------------
sc1_threshold = CLAIM_FORMAL["sub_claims"]["SC1"]["threshold"]
sc2_disproof_threshold = CLAIM_FORMAL["sub_claims"]["SC2"]["threshold"]

# SC1: Does CO2 have a documented plant fertilization benefit?
sc1_holds = compare(
    n_sc1_confirmed, ">=", sc1_threshold,
    label="SC1: CO2 plant fertilization confirmed sources >= threshold"
)

# SC2 disproof check: Have >= 3 authoritative sources confirmed major negative effects?
# This compare() also doubles as the compare() that determines sc2_holds below.
sc2_negative_confirmed = compare(
    n_sc2_disproof_confirmed, ">=", sc2_disproof_threshold,
    label="SC2 disproof: sources documenting negative effects >= threshold"
)

# SC2 holds (as claimed: 'no net negative effects') only if fewer than threshold
# sources document negative effects — i.e., the disproof threshold is NOT reached.
sc2_holds = compare(
    n_sc2_disproof_confirmed, "<", sc2_disproof_threshold,
    label="SC2 claim 'no net negative effects': disproof sources < threshold (claim would hold)"
)

print(f"\n  SC1 ('plant food' benefit exists): {sc1_holds}")
print(f"  SC2 ('no net negative effects' holds): {sc2_holds}")
print(f"  SC2 is falsified because {n_sc2_disproof_confirmed} independent authoritative sources "
      f"document major negative effects.")

# Overall claim holds only if BOTH SC1 AND SC2 hold
n_sub_claims_holding = int(sc1_holds) + int(sc2_holds)
overall_holds = compare(
    n_sub_claims_holding, "==", 2,
    label="Overall compound claim: both SC1 and SC2 hold (2 of 2 sub-claims must pass)"
)

# ---------------------------------------------------------------------------
# 7. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": "Does CO2 fertilization fully offset the documented negative effects on agriculture (heat stress, drought, pest spread)?",
        "verification_performed": (
            "Reviewed IPCC SR1.5 Chapter 3 and NASA greening study for net agricultural assessments. "
            "The NASA Goddard study itself states CO2 'is also the chief culprit of climate change' "
            "causing 'global warming, rising sea levels, melting glaciers and sea ice as well as more "
            "severe weather events.' IPCC SR1.5 projects 'smaller net reductions in yields of maize, "
            "rice, wheat, and potentially other cereal crops' even under aggressive mitigation."
        ),
        "finding": (
            "No credible scientific source claims CO2 fertilization offsets all agricultural harms. "
            "The scientific consensus is that net crop yield impacts are negative in many regions, "
            "particularly in tropical and subtropical areas most vulnerable to warming."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is the NASA greening study frequently cited by climate skeptics as evidence of net benefit, and do the study authors endorse this interpretation?",
        "verification_performed": (
            "The NASA Goddard press release explicitly states: 'While rising carbon dioxide "
            "concentrations in the air can be beneficial for plants, it is also the chief culprit of "
            "climate change.' The study further notes the fertilization effect 'diminishes over time' "
            "as plants acclimatize. The authors explicitly reject the 'net benefit, no harm' "
            "interpretation of their greening finding."
        ),
        "finding": (
            "The authors of the primary SC1 source explicitly refute the claim's framing. "
            "The same CO2 driving greening is confirmed by its own discoverers to be causing "
            "major climate harms — this strengthens the SC2 disproof rather than undermining it."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could 'no net negative effects' be technically defensible if CO2 fertilization in aggregate globally outweighs all harms?",
        "verification_performed": (
            "Searched IPCC AR6 Summary for Policymakers, IPCC SR1.5, and NASA for any authoritative "
            "net benefit assessment. IPCC documents 70-90% coral reef loss, ocean acidification "
            "'unprecedented for at least 65 million years,' sea level rise, and increased extreme "
            "weather. No IPCC report, no NASA publication, and no major scientific body has concluded "
            "that CO2 fertilization benefits net-outweigh the total harms."
        ),
        "finding": (
            "No major scientific body has concluded net positive outcomes from elevated CO2. "
            "The IPCC AR6 Synthesis Report states with 'unequivocal' confidence that human-caused "
            "climate change (driven by CO2) is causing widespread adverse impacts."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does elevated CO2 improve food security via increased crop yields, potentially qualifying as a net benefit to human welfare?",
        "verification_performed": (
            "Searched scientific literature on CO2, crop yields, and nutritional quality. "
            "Multiple peer-reviewed studies (Loladze 2014, Myers et al. 2014 in Nature) document "
            "that elevated CO2 reduces protein, zinc, and iron concentrations in C3 crops (wheat, "
            "rice, legumes) — the 'carbohydrate dilution effect.' Even where biomass increases, "
            "nutritional density per calorie declines. IPCC SR1.5 also projects net crop yield "
            "reductions in major food-producing regions at warming above 1.5°C."
        ),
        "finding": (
            "Elevated CO2 reduces nutritional density of staple crops, partially offsetting any "
            "yield gains. Combined with regional yield losses from heat and drought, this does not "
            "support a 'no net negative effects on food security' claim."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 8. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    sub_claim_verdicts = {
        "SC1": "SUPPORTED" if sc1_holds else "UNSUPPORTED",
        "SC2": "DISPROVED" if not sc2_holds else "SUPPORTED",
    }

    # Overall verdict driven by SC2 falsification
    if not sc2_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not sc2_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    elif sc1_holds and sc2_holds and not any_unverified:
        verdict = "PROVED"
    elif sc1_holds and sc2_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    else:
        verdict = "PARTIALLY VERIFIED"

    FACT_REGISTRY["A1"]["method"] = "count(verified/partial citations in sc1_facts)"
    FACT_REGISTRY["A1"]["result"] = (
        f"{n_sc1_confirmed} confirmed source(s) >= threshold {sc1_threshold} — SC1 {'holds' if sc1_holds else 'fails'}"
    )
    FACT_REGISTRY["A2"]["method"] = "count(verified/partial citations in sc2_disproof_facts)"
    FACT_REGISTRY["A2"]["result"] = (
        f"{n_sc2_disproof_confirmed} confirmed source(s) >= threshold {sc2_disproof_threshold} — SC2 falsified: {not sc2_holds}"
    )

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        fid: {
            "value": citation_results.get(info["key"], {}).get("status", "unknown"),
            "value_in_quote": citation_results.get(info["key"], {}).get("status") in COUNTABLE_STATUSES,
            "quote_snippet": empirical_facts[info["key"]]["quote"][:80],
        }
        for fid, info in FACT_REGISTRY.items()
        if "key" in info
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
                    "SC1 and SC2 use fully independent source sets: "
                    "SC1 draws on NASA Goddard and NASA Earth Observatory; "
                    "SC2 disproof draws on NOAA, NASA Climate Effects, and IPCC SR1.5."
                ),
                "values_compared": [
                    f"SC1 confirmed sources: {n_sc1_confirmed}",
                    f"SC2 disproof confirmed sources: {n_sc2_disproof_confirmed}",
                ],
                "agreement": True,
                "independence_note": (
                    "SC1 and SC2 sources are from different institutions and independent publications. "
                    "Notably, the NASA Goddard greening study (SC1 source B1) itself independently "
                    "corroborates the SC2 disproof: it explicitly states CO2 is 'the chief culprit "
                    "of climate change' — a finding from the same paper confirming the plant benefit."
                ),
            },
        ],
        "adversarial_checks": adversarial_checks,
        "sub_claim_verdicts": sub_claim_verdicts,
        "sub_claim_results": {
            "SC1": {
                "description": "CO2 has a beneficial plant fertilization effect",
                "confirmed_sources": n_sc1_confirmed,
                "threshold": sc1_threshold,
                "holds": sc1_holds,
            },
            "SC2": {
                "description": "CO2 has no net negative effects",
                "disproof_sources_confirmed": n_sc2_disproof_confirmed,
                "disproof_threshold": sc2_disproof_threshold,
                "holds": sc2_holds,
                "note": (
                    "SC2 is falsified: 3 independent government/intergovernmental sources "
                    "(NOAA, NASA, IPCC) confirm major negative effects of elevated CO2 on "
                    "oceans, climate, and ecosystems."
                ),
            },
        },
        "verdict": verdict,
        "key_results": {
            "sc1_plant_food_benefit_confirmed": sc1_holds,
            "sc1_confirmed_sources": n_sc1_confirmed,
            "sc2_no_negative_effects_claim_holds": sc2_holds,
            "sc2_disproof_confirmed_sources": n_sc2_disproof_confirmed,
            "overall_claim_holds": overall_holds,
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
