"""
Proof: Electric vehicles have a larger lifetime carbon footprint than gasoline cars
when manufacturing and battery disposal are included.
Generated: 2026-03-29
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
CLAIM_NATURAL = (
    "Electric vehicles have a larger lifetime carbon footprint than gasoline cars "
    "when manufacturing and battery disposal are included."
)
CLAIM_FORMAL = {
    "subject": "Electric vehicles (battery electric vehicles, BEVs)",
    "property": "Whether authoritative lifecycle analyses find BEVs have HIGHER total "
                "lifetime GHG emissions than comparable gasoline ICE vehicles, "
                "including manufacturing, use-phase, and end-of-life (battery disposal/recycling)",
    "operator": ">=",
    "operator_note": (
        "This is a disproof by consensus: we collect authoritative sources that explicitly "
        "state EVs have LOWER lifetime emissions than gasoline cars even including manufacturing. "
        "If >= 3 independent verified sources reject the claim, we conclude DISPROVED. "
        "The claim uses 'larger' without qualification, so any authoritative LCA showing EVs "
        "have lower lifetime emissions (even by a small margin) constitutes a rejection."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "epa", "label": "U.S. EPA: EV lifetime emissions lower even accounting for manufacturing"},
    "B2": {"key": "factcheck_icct", "label": "FactCheck.org (citing ICCT): EV lifetime emissions 60-69% lower than gasoline"},
    "B3": {"key": "recurrent", "label": "Recurrent Auto: Gasoline car 76 tonnes CO2 lifetime vs EV 37 tonnes"},
    "B4": {"key": "eurekalert_study", "label": "2025 peer-reviewed study: EVs outperform gasoline cars in lifetime impact"},
    "A1": {"label": "Verified source count meeting disproof threshold", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm EVs have lower lifetime emissions)
empirical_facts = {
    "epa": {
        "quote": (
            "The greenhouse gas emissions associated with an electric vehicle over its "
            "lifetime are typically lower than those from an average gasoline-powered "
            "vehicle, even when accounting for manufacturing."
        ),
        "url": "https://www.epa.gov/greenvehicles/electric-vehicle-myths",
        "source_name": "U.S. Environmental Protection Agency",
    },
    "factcheck_icct": {
        "quote": (
            "the lifetime emissions of an average medium-size electric car were lower "
            "compared with a gasoline-powered car by 66%-69% in Europe, 60%-68% in the "
            "United States, 37%-45% in China, and 19%-34% in India."
        ),
        "url": "https://www.factcheck.org/2024/02/electric-vehicles-contribute-fewer-emissions-than-gasoline-powered-cars-over-their-lifetimes/",
        "source_name": "FactCheck.org (citing ICCT global lifecycle analysis)",
    },
    "recurrent": {
        "quote": (
            "Over the course of its life, a new gasoline car will produce an average of "
            "410 grams of carbon dioxide per mile. A new electric car will produce only "
            "110 grams."
        ),
        "url": "https://www.recurrentauto.com/research/just-how-dirty-is-your-ev",
        "source_name": "Recurrent Auto (EV research and analytics)",
    },
    "eurekalert_study": {
        "quote": (
            "Electric vehicles outperform gasoline cars in lifetime environmental impact"
        ),
        "url": "https://www.eurekalert.org/news-releases/1102315",
        "source_name": "EurekAlert / AAAS (2025 peer-reviewed study)",
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
                      label="verified source count vs disproof threshold")

# 7. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Are there credible lifecycle analyses showing EVs have HIGHER lifetime emissions than gasoline cars?",
        "verification_performed": (
            "Searched for 'EV larger carbon footprint than gasoline car lifecycle analysis', "
            "'electric vehicle worse for environment than gas car study', and "
            "'EV carbon footprint debunked'. Reviewed results from EPA, MIT Climate Portal, "
            "ICCT, FactCheck.org, NPR, and Recurrent Auto."
        ),
        "finding": (
            "No credible peer-reviewed lifecycle analysis was found showing EVs have higher "
            "lifetime emissions than gasoline cars. While EV manufacturing (especially battery "
            "production) creates 40-80% more emissions than ICE manufacturing, this deficit is "
            "recovered within 1.5-2 years of typical driving. Every major LCA reviewed — "
            "including ICCT (2022, 2025), MIT, EPA, and DOE — concludes EVs have significantly "
            "lower lifetime emissions."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could extremely coal-heavy grids make EVs worse than gasoline cars over a full lifetime?",
        "verification_performed": (
            "Searched for 'EV emissions coal heavy grid lifecycle worse than gasoline'. "
            "Reviewed ICCT regional data and MIT Climate Portal analysis."
        ),
        "finding": (
            "Even in regions with the most carbon-intensive grids (India), the ICCT finds "
            "EVs have 19-34% lower lifetime emissions than gasoline cars. No region studied "
            "shows EVs with higher lifetime emissions. The MIT Climate Portal states: "
            "'In general, electric vehicles generate fewer carbon emissions than "
            "gasoline cars, even when accounting for the electricity used for charging.'"
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does battery disposal/recycling add enough emissions to flip the comparison?",
        "verification_performed": (
            "Searched for 'EV battery disposal recycling emissions lifecycle impact'. "
            "Reviewed NPR reporting and Recurrent Auto analysis."
        ),
        "finding": (
            "Battery end-of-life emissions are already included in the lifecycle analyses cited. "
            "NPR reports that while EV batteries have environmental impact, 'Gas cars are still "
            "worse' over the full lifecycle. Battery recycling is improving and second-life "
            "applications further reduce net impact. No source found where including disposal "
            "flips the lifetime comparison."
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
    FACT_REGISTRY["A1"]["result"] = f"{n_confirmed} sources confirmed EVs have lower lifetime emissions"

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
                "description": "Multiple independent sources consulted from different institutions",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources span U.S. government (EPA), international research (ICCT via FactCheck.org), "
                    "industry analytics (Recurrent Auto), and peer-reviewed academic research (EurekAlert/AAAS). "
                    "Each represents an independent institution with its own methodology."
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
            "manufacturing_offset": "EV manufacturing produces 40-80% more emissions, but offset within 1.5-2 years of driving",
            "lifetime_reduction": "EVs produce 60-69% lower lifetime emissions in the US (ICCT)",
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
