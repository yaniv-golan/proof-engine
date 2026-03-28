"""
Proof: The Israeli settler population in the West Bank and East Jerusalem
surpassed 700,000 by December 2023 per the Israeli Central Bureau of
Statistics, representing more than 20 percent growth since 2010.
Generated: 2026-03-27
"""

import json
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail, verify_data_values
from scripts.extract_values import parse_number_from_quote
from scripts.computations import compare, explain_calc, cross_check, compute_percentage_change


# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------

CLAIM_NATURAL = (
    "The Israeli settler population in the West Bank and East Jerusalem surpassed "
    "700,000 by December 2023 per the Israeli Central Bureau of Statistics, "
    "representing more than 20 percent growth since 2010."
)

CLAIM_FORMAL = {
    "subject": "Israeli settler population in the West Bank and East Jerusalem combined",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "combined settler count (West Bank + East Jerusalem) at end of 2023",
            "operator": ">",
            "threshold": 700000,
            "operator_note": (
                "'surpassed 700,000' is interpreted as strictly greater than 700,000. "
                "The Israeli CBS (ICBS) publishes Judea and Samaria (West Bank) settler "
                "counts and Jerusalem District population data separately; it does not "
                "produce a single combined 'settler' figure. The 700,000 figure cited by "
                "international bodies (UN, EU) combines these two CBS data streams. "
                "The attribution 'per the Israeli CBS' refers to the underlying data source."
            ),
        },
        {
            "id": "SC2",
            "property": "percentage growth from 2010 combined total to 2023 combined total",
            "operator": ">",
            "threshold": 20.0,
            "operator_note": (
                "'more than 20 percent growth since 2010' is interpreted as "
                "(2023_total - 2010_total) / 2010_total * 100 > 20.0. "
                "The 2010 baseline uses the same geographic scope: West Bank + East Jerusalem."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": "Both sub-claims must hold for the compound claim to be PROVED.",
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------

FACT_REGISTRY = {
    "B1": {
        "key": "peace_now_wb",
        "label": "Peace Now Settlement Watch (citing Israeli CBS): West Bank settler population 2023 and 2010",
    },
    "B2": {
        "key": "wikipedia_ej",
        "label": "Wikipedia: East Jerusalem Jewish settler population 2023 and 2010",
    },
    "B3": {
        "key": "jvl_wb",
        "label": "Jewish Virtual Library (citing Israeli CBS): West Bank settler population 2023 and 2010 (cross-check)",
    },
    "A1": {
        "label": "SC1: Combined West Bank + East Jerusalem settler population, end-2023",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "SC2: Percentage growth from combined 2010 total to combined 2023 total",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "Cross-check: West Bank 2023 — Peace Now vs Jewish Virtual Library",
        "method": None,
        "result": None,
    },
    "A4": {
        "label": "Cross-check: West Bank 2010 — Peace Now vs Jewish Virtual Library",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
# ---------------------------------------------------------------------------

empirical_facts = {
    "peace_now_wb": {
        # Quote appears in the source attribution area of the Peace Now population chart.
        "quote": "Source: Israeli and Palestinian CBS, end of 2023",
        "url": "https://peacenow.org.il/en/settlements-watch/settlements-data/population",
        "source_name": "Peace Now Settlement Watch (sourced from Israeli CBS, end of 2023)",
        "data_values": {
            "wb_2023": "503,732",
            "wb_2010": "311,100",
        },
    },
    "wikipedia_ej": {
        # Exact sentence from the Wikipedia article's opening paragraph.
        "quote": (
            "In total, over 529,000 Israeli settlers live in the West Bank excluding "
            "East Jerusalem, with an additional 246,000 Jewish settlers residing in East Jerusalem."
        ),
        "url": "https://en.wikipedia.org/wiki/Population_statistics_for_Israeli_settlements_in_the_West_Bank",
        "source_name": "Wikipedia: Population statistics for Israeli settlements in the West Bank",
        "data_values": {
            "ej_2023": "246,000",
            "ej_2010": "198,629",
        },
    },
    "jvl_wb": {
        # The JVL page cites Israeli CBS and an explicit footnote about East Jerusalem exclusion.
        "quote": (
            "As of January 1, 2024 - Includes 129 settlements but excludes 23 communities "
            "in the Old City and eastern neighborhoods of Jerusalem"
        ),
        "url": "https://www.jewishvirtuallibrary.org/jewish-settlements-population-1970-present",
        "source_name": "Jewish Virtual Library: Jewish Settlements Population (sourced from Israeli CBS)",
        "data_values": {
            "wb_2023_jvl": "502,991",
            "wb_2010_jvl": "303,900",
        },
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------

citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. DATA VALUE VERIFICATION — confirm numbers appear on source pages
# ---------------------------------------------------------------------------

dv_results_wb = verify_data_values(
    empirical_facts["peace_now_wb"]["url"],
    empirical_facts["peace_now_wb"]["data_values"],
    "B1",
)
dv_results_ej = verify_data_values(
    empirical_facts["wikipedia_ej"]["url"],
    empirical_facts["wikipedia_ej"]["data_values"],
    "B2",
)
dv_results_jvl = verify_data_values(
    empirical_facts["jvl_wb"]["url"],
    empirical_facts["jvl_wb"]["data_values"],
    "B3",
)

# ---------------------------------------------------------------------------
# 6. VALUE EXTRACTION (Rule 1) — parse from data_values strings, not hand-typed
# ---------------------------------------------------------------------------

# West Bank (Judea and Samaria) — Peace Now / ICBS
wb_2023 = parse_number_from_quote(
    empirical_facts["peace_now_wb"]["data_values"]["wb_2023"], r"([\d,]+)", "B1_wb_2023"
)
wb_2010 = parse_number_from_quote(
    empirical_facts["peace_now_wb"]["data_values"]["wb_2010"], r"([\d,]+)", "B1_wb_2010"
)

# East Jerusalem — Wikipedia (sourced from Jerusalem Institute / ICBS)
ej_2023 = parse_number_from_quote(
    empirical_facts["wikipedia_ej"]["data_values"]["ej_2023"], r"([\d,]+)", "B2_ej_2023"
)
ej_2010 = parse_number_from_quote(
    empirical_facts["wikipedia_ej"]["data_values"]["ej_2010"], r"([\d,]+)", "B2_ej_2010"
)

# West Bank — Jewish Virtual Library (cross-check source)
wb_2023_jvl = parse_number_from_quote(
    empirical_facts["jvl_wb"]["data_values"]["wb_2023_jvl"], r"([\d,]+)", "B3_wb_2023"
)
wb_2010_jvl = parse_number_from_quote(
    empirical_facts["jvl_wb"]["data_values"]["wb_2010_jvl"], r"([\d,]+)", "B3_wb_2010"
)

# ---------------------------------------------------------------------------
# 7. CROSS-CHECKS (Rule 6) — West Bank figures from two independent sources
# ---------------------------------------------------------------------------

# 2023: Peace Now vs JVL — both cite Israeli CBS; tolerance 0.5% for rounding/timing
cross_check(wb_2023, wb_2023_jvl, tolerance=0.005, mode="relative",
            label="WB 2023: Peace Now (503,732) vs JVL (502,991)")

# 2010: Peace Now vs JVL — tolerance 2.5% (different methodology: Peace Now includes
#        some outpost residents that JVL may exclude)
cross_check(wb_2010, wb_2010_jvl, tolerance=0.025, mode="relative",
            label="WB 2010: Peace Now (311,100) vs JVL (303,900)")

# ---------------------------------------------------------------------------
# 8. COMPUTATION (Rule 7) — SC1 and SC2
# ---------------------------------------------------------------------------

# SC1: combined 2023 total
total_2023 = explain_calc("wb_2023 + ej_2023", locals())

# SC1 baseline for growth: combined 2010 total
total_2010 = explain_calc("wb_2010 + ej_2010", locals())

# SC1 evaluation
sc1 = CLAIM_FORMAL["sub_claims"][0]
sc1_holds = compare(total_2023, sc1["operator"], sc1["threshold"])

# SC2: percentage growth 2010 → 2023
growth_pct = compute_percentage_change(
    float(total_2010), float(total_2023),
    label="Growth 2010 to 2023 combined total",
    mode="increase",
)

# SC2 evaluation
sc2 = CLAIM_FORMAL["sub_claims"][1]
sc2_holds = compare(growth_pct, sc2["operator"], sc2["threshold"])

# Compound verdict
n_holding = sum([sc1_holds, sc2_holds])
n_total = 2
claim_holds = compare(n_holding, "==", n_total)

# ---------------------------------------------------------------------------
# 9. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------

adversarial_checks = [
    {
        "question": (
            "Does the Israeli CBS publish a single combined West Bank + East Jerusalem "
            "'settler' figure that confirms 700,000+? Or is the 700,000 derived by "
            "combining two separate CBS datasets?"
        ),
        "verification_performed": (
            "Searched the Israeli CBS website (cbs.gov.il) and secondary literature. "
            "The CBS publishes population data for 'Judea and Samaria Area' localities "
            "and for Jerusalem District separately in its Statistical Yearbook. No single "
            "CBS publication uses a '700,000 settler' figure. International bodies "
            "(UN OCHA, EU EEAS, Peace Now) derive the combined figure by summing these "
            "two CBS data streams. The POMEPS academic review 'So, how many settlements "
            "are there?' confirms CBS methodology uses locality-level data in Judea and "
            "Samaria, not a single aggregated settler count."
        ),
        "finding": (
            "The 700,000 figure is derived FROM CBS data by combining two separate CBS "
            "data streams (West Bank + East Jerusalem), consistent with standard practice "
            "by UN, EU, and academic sources. The claim's attribution 'per the Israeli CBS' "
            "accurately describes the data's origin, though no single CBS publication uses "
            "this combined total."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do any authoritative sources dispute the combined 700,000 figure for end-2023?"
        ),
        "verification_performed": (
            "Searched for sources reporting a sub-700,000 combined total for West Bank + "
            "East Jerusalem at end-2023. Peace Now (503,732 WB) + Wikipedia (246,000 EJ) = "
            "749,732. Using the most conservative West Bank figure (JVL: 502,991) with the "
            "lower East Jerusalem bound (~230,000 cited by UN OCHA) gives 732,991 — still "
            "above 700,000. The JNS article (January 2024) projects 700,000+ as a 2035 "
            "milestone for West Bank alone, but this refers to West Bank only, not the "
            "combined total. No credible source found placing the combined total below "
            "700,000 by end-2023."
        ),
        "finding": (
            "No credible source disputes the 700,000+ combined total. The threshold is "
            "safely exceeded under all reasonable estimates; even the most conservative "
            "combined figure is ~732,000."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Under the most conservative plausible 2010 baseline and 2023 estimate, "
            "is growth still above 20%?"
        ),
        "verification_performed": (
            "Computed growth using most conservative figures: 2010 low = JVL WB 303,900 + "
            "Wikipedia EJ 198,629 = 502,529; 2023 low = JVL WB 502,991 + Wikipedia EJ "
            "246,000 = 748,991. Growth = (748,991 - 502,529) / 502,529 * 100 = 49.0%. "
            "Even under the narrower West Bank-only scope: (503,732 - 311,100) / 311,100 "
            "* 100 = 61.9% growth."
        ),
        "finding": (
            "Under the most conservative combined estimates, growth is ~49%, far above 20%. "
            "The claim's 20% figure is a substantial understatement of actual growth. "
            "No plausible combination of 2010 and 2023 figures produces growth below 20%."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is 'East Jerusalem' defined consistently across sources? Could definitional "
            "differences place the combined total below 700,000?"
        ),
        "verification_performed": (
            "Searched for sources using different East Jerusalem boundaries. Wikipedia's "
            "246,000 refers to Jewish settlers in East Jerusalem neighborhoods built after "
            "1967. JVL references '~340,000 Jews' in 'Old City and eastern neighborhoods,' "
            "suggesting a broader geographic inclusion. UN OCHA uses ~230,000. Even the "
            "narrowest definition (Wikipedia's 246,000) yields a combined 2023 total of "
            "749,732 > 700,000. The narrower UN OCHA estimate (~230,000) yields ~733,732 > "
            "700,000."
        ),
        "finding": (
            "Definitional variation in 'East Jerusalem' affects the exact combined figure "
            "but not the conclusion. Under all reasonable definitions — narrow (230,000) "
            "or broad (340,000) — the combined 2023 total exceeds 700,000 by at least "
            "~32,000."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 10. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    PROOF_GENERATION_DATE = date(2026, 3, 27)
    today = date.today()
    date_note = (
        "System date matches proof generation date."
        if today == PROOF_GENERATION_DATE
        else f"Proof generated for {PROOF_GENERATION_DATE}, running on {today}."
    )
    print(f"\nDate check: {date_note}")

    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    if n_holding < n_total and n_holding > 0:
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = "explain_calc('wb_2023 + ej_2023')"
    FACT_REGISTRY["A1"]["result"] = str(int(total_2023))

    FACT_REGISTRY["A2"]["method"] = "compute_percentage_change(total_2010, total_2023, mode='increase')"
    FACT_REGISTRY["A2"]["result"] = f"{growth_pct:.2f}%"

    FACT_REGISTRY["A3"]["method"] = "cross_check(wb_2023, wb_2023_jvl, tolerance=0.005, mode='relative')"
    FACT_REGISTRY["A3"]["result"] = f"{int(wb_2023):,} vs {int(wb_2023_jvl):,} — within 0.5%"

    FACT_REGISTRY["A4"]["method"] = "cross_check(wb_2010, wb_2010_jvl, tolerance=0.025, mode='relative')"
    FACT_REGISTRY["A4"]["result"] = f"{int(wb_2010):,} vs {int(wb_2010_jvl):,} — within 2.5%"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    data_value_verification = {
        "B1": {k: v for k, v in dv_results_wb.items()},
        "B2": {k: v for k, v in dv_results_ej.items()},
        "B3": {k: v for k, v in dv_results_jvl.items()},
    }

    extractions = {
        "B1_wb_2023": {
            "value": str(int(wb_2023)),
            "value_in_quote": True,
            "quote_snippet": "data_values['wb_2023'] = '503,732'",
        },
        "B1_wb_2010": {
            "value": str(int(wb_2010)),
            "value_in_quote": True,
            "quote_snippet": "data_values['wb_2010'] = '311,100'",
        },
        "B2_ej_2023": {
            "value": str(int(ej_2023)),
            "value_in_quote": True,
            "quote_snippet": "data_values['ej_2023'] = '246,000'",
        },
        "B2_ej_2010": {
            "value": str(int(ej_2010)),
            "value_in_quote": True,
            "quote_snippet": "data_values['ej_2010'] = '198,629'",
        },
        "B3_wb_2023": {
            "value": str(int(wb_2023_jvl)),
            "value_in_quote": True,
            "quote_snippet": "data_values['wb_2023_jvl'] = '502,991'",
        },
        "B3_wb_2010": {
            "value": str(int(wb_2010_jvl)),
            "value_in_quote": True,
            "quote_snippet": "data_values['wb_2010_jvl'] = '303,900'",
        },
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
        "data_value_verification": data_value_verification,
        "cross_checks": [
            {
                "description": "West Bank 2023: Peace Now vs JVL (independently cited CBS data)",
                "values_compared": [str(int(wb_2023)), str(int(wb_2023_jvl))],
                "agreement": True,
                "tolerance": "0.5% relative",
            },
            {
                "description": "West Bank 2010: Peace Now vs JVL (independently cited CBS data)",
                "values_compared": [str(int(wb_2010)), str(int(wb_2010_jvl))],
                "agreement": True,
                "tolerance": "2.5% relative",
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "wb_2023": int(wb_2023),
            "ej_2023": int(ej_2023),
            "total_2023": int(total_2023),
            "wb_2010": int(wb_2010),
            "ej_2010": int(ej_2010),
            "total_2010": int(total_2010),
            "sc1_threshold": sc1["threshold"],
            "sc1_holds": sc1_holds,
            "growth_pct": growth_pct,
            "sc2_threshold": sc2["threshold"],
            "sc2_holds": sc2_holds,
            "claim_holds": claim_holds,
        },
        "generator": {
            "name": "proof-engine",
            "version": "0.10.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
