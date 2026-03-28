"""
Proof: UN Resolution 181 allocated 56 percent of Mandatory Palestine to the proposed
Jewish state while Jews constituted less than 33 percent of the population according
to 1947 British population statistics.
Generated: 2026-03-27
"""
import json
from datetime import date
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail, verify_data_values
from scripts.extract_values import parse_number_from_quote
from scripts.computations import compare, explain_calc, cross_check

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "The UN Partition Plan Resolution 181 allocated 56 percent of Mandatory Palestine "
    "to the proposed Jewish state while Jews constituted less than 33 percent of the "
    "population according to the 1947 British census."
)
CLAIM_FORMAL = {
    "subject": "UN General Assembly Resolution 181 (November 29, 1947)",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "Percentage of Mandatory Palestine territory allocated to proposed Jewish state",
            "operator": ">=",
            "threshold": 56.0,
            "operator_note": (
                "'56 percent' interpreted as >= 56.0 (at least 56 percent). "
                "The actual figure is 56.47%, which meets this threshold. "
                "The claim would be FALSE only if the Jewish state received < 56% of total territory."
            ),
        },
        {
            "id": "SC2",
            "property": "Jewish population as percentage of total Mandatory Palestine population circa 1947",
            "operator": "<",
            "threshold": 33.0,
            "operator_note": (
                "'less than 33 percent' interpreted strictly as < 33.0. "
                "TERMINOLOGY NOTE: The claim refers to a '1947 British census' but no formal "
                "census was conducted in 1947 — the last British census of Palestine was 1931. "
                "Population figures for Resolution 181 were based on British Mandate estimates "
                "derived from the 1931 census, updated via immigration records and the Village "
                "Statistics 1945 survey. SC2 is evaluated using 1946 British Mandate estimates "
                "(608,225 Jews / 1,845,559 total = 32.96%), which are the figures cited in "
                "historical sources as the demographic context for Resolution 181."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": "Both SC1 and SC2 must hold for the compound claim to be PROVED.",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "source_land_britannica", "label": "Britannica: Jewish state = 15,264 km\u00b2 (56.47%) under Resolution 181"},
    "B2": {"key": "source_land_wiki", "label": "Wikipedia (Partition Plan): Jewish state territory and percentage (independent source)"},
    "B3": {"key": "source_pop_wiki", "label": "Wikipedia (Partition Plan): 1946 population total 1,845,559; Jewish 608,225"},
    "B4": {"key": "source_pop_demog", "label": "Wikipedia (Demographic history of Palestine): 1946 Jewish population 608,225"},
    "A1": {"label": "SC1 \u2014 Jewish state land allocation percentage (from B1/B2)", "method": None, "result": None},
    "A2": {"label": "SC2 \u2014 Jewish population percentage computed from raw counts (B3)", "method": None, "result": None},
    "A3": {"label": "Cross-check: land percentage B1 vs B2 agreement", "method": None, "result": None},
    "A4": {"label": "Cross-check: Jewish population count B3 vs B4 agreement", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS
empirical_facts = {
    "source_land_britannica": {
        "quote": (
            "The Arab state was to have a territory of 11,592 square kilometres, or 42.88 percent "
            "of the Mandate's territory, and the Jewish state a territory of 15,264 square kilometres, "
            "or 56.47 percent."
        ),
        "url": "https://www.britannica.com/topic/United-Nations-Resolution-181",
        "source_name": "Encyclopaedia Britannica: United Nations Resolution 181",
        "data_values": {
            "jewish_km2_b1": "15,264",
            "jewish_pct_b1": "56.47",
        },
    },
    "source_land_wiki": {
        "quote": "15,264",
        "url": "https://en.wikipedia.org/wiki/United_Nations_Partition_Plan_for_Palestine",
        "source_name": "Wikipedia: United Nations Partition Plan for Palestine (territorial allocation)",
        "data_values": {
            "jewish_km2_b2": "15,264",
            "jewish_pct_b2": "56.47",
        },
    },
    "source_pop_wiki": {
        "quote": "608,225",
        "url": "https://en.wikipedia.org/wiki/United_Nations_Partition_Plan_for_Palestine",
        "source_name": "Wikipedia: United Nations Partition Plan for Palestine (1946 population section)",
        "data_values": {
            "jewish_pop_b3": "608,225",
            "total_pop_b3": "1,845,559",
        },
    },
    "source_pop_demog": {
        "quote": "1,076,783 Muslim Arabs, 608,225 Jews",
        "url": "https://en.wikipedia.org/wiki/Demographic_history_of_Palestine_(region)",
        "source_name": "Wikipedia: Demographic history of Palestine region (1946 figures)",
        "data_values": {
            "jewish_pop_b4": "608,225",
        },
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. DATA VALUE VERIFICATION — confirm numbers appear on source pages
dv_results_b1 = verify_data_values(
    empirical_facts["source_land_britannica"]["url"],
    empirical_facts["source_land_britannica"]["data_values"],
    "B1",
)
dv_results_b2 = verify_data_values(
    empirical_facts["source_land_wiki"]["url"],
    empirical_facts["source_land_wiki"]["data_values"],
    "B2",
)
dv_results_b3 = verify_data_values(
    empirical_facts["source_pop_wiki"]["url"],
    empirical_facts["source_pop_wiki"]["data_values"],
    "B3",
)
dv_results_b4 = verify_data_values(
    empirical_facts["source_pop_demog"]["url"],
    empirical_facts["source_pop_demog"]["data_values"],
    "B4",
)

# 6. VALUE EXTRACTION (Rule 1) — parse from data_values strings, never hand-type
# SC1: land allocation percentages
jewish_pct_b1 = parse_number_from_quote(
    empirical_facts["source_land_britannica"]["data_values"]["jewish_pct_b1"],
    r"([\d.]+)", "B1_pct"
)
jewish_pct_b2 = parse_number_from_quote(
    empirical_facts["source_land_wiki"]["data_values"]["jewish_pct_b2"],
    r"([\d.]+)", "B2_pct"
)
# SC2: population counts — strip commas before parsing
jewish_pop_b3 = int(float(
    empirical_facts["source_pop_wiki"]["data_values"]["jewish_pop_b3"].replace(",", "")
))
total_pop_b3 = int(float(
    empirical_facts["source_pop_wiki"]["data_values"]["total_pop_b3"].replace(",", "")
))
jewish_pop_b4 = int(float(
    empirical_facts["source_pop_demog"]["data_values"]["jewish_pop_b4"].replace(",", "")
))

# 7. CROSS-CHECKS (Rule 6)
# SC1 cross-check: land percentage must agree between Britannica (B1) and Wikipedia (B2)
cc_land = cross_check(
    jewish_pct_b1, jewish_pct_b2,
    tolerance=0.01, mode="absolute",
    label="SC1 land percentage: B1 (Britannica) vs B2 (Wikipedia)"
)
# SC2 cross-check: Jewish population count must agree between B3 and B4
cc_pop = cross_check(
    jewish_pop_b3, jewish_pop_b4,
    tolerance=0, mode="absolute",
    label="SC2 Jewish population count: B3 vs B4"
)

# 8. COMPUTATION (Rule 7)
# SC1: Jewish state land allocation percentage (use B1 as primary)
sc1_pct = jewish_pct_b1
print(f"\nSC1 — Land allocation: jewish_pct_b1 = {sc1_pct}")
sc1_holds = compare(sc1_pct, CLAIM_FORMAL["sub_claims"][0]["operator"],
                    CLAIM_FORMAL["sub_claims"][0]["threshold"])
print(f"SC1 holds ({sc1_pct} >= 56.0): {sc1_holds}")

# SC2: Jewish population percentage computed from raw counts
jewish_pop = jewish_pop_b3
total_pop = total_pop_b3
sc2_pct = explain_calc("jewish_pop / total_pop * 100", locals())
sc2_holds = compare(sc2_pct, CLAIM_FORMAL["sub_claims"][1]["operator"],
                    CLAIM_FORMAL["sub_claims"][1]["threshold"])
print(f"SC2 holds ({sc2_pct:.4f}% < 33.0%): {sc2_holds}")

# 9. COMPOUND CLAIM EVALUATION
sc_results = [sc1_holds, sc2_holds]
n_holding = sum(sc_results)
n_total = len(sc_results)
claim_holds = compare(n_holding, "==", n_total)
print(f"\nSub-claims holding: {n_holding}/{n_total}")

# 10. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": (
            "Does the 56% figure change if desert areas are excluded, "
            "or if alternative territorial boundaries are used?"
        ),
        "verification_performed": (
            "Searched for alternative land allocation figures for Resolution 181 that use "
            "different boundary definitions or exclude the Negev desert. Found that some "
            "analyses distinguish 'cultivated land' from total land (Jewish ownership was ~7%), "
            "but this is a separate figure from territorial allocation. All authoritative sources "
            "(Britannica, UN documents, Wikipedia) consistently cite 56.47% as the total "
            "territorial allocation to the Jewish state under Resolution 181."
        ),
        "finding": (
            "The 56.47% refers to total land area including the Negev desert, which comprised "
            "a large portion of the Jewish state allocation. Jewish-owned land at the time was "
            "only ~7% of total Palestine — a distinct figure from territorial allocation. "
            "No credible source disputes the 56.47% territorial allocation figure."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Was Jewish population share at or above 33% by November 1947, "
            "due to post-WWII immigration?"
        ),
        "verification_performed": (
            "Searched for Jewish population figures for late 1947 specifically. Found that "
            "post-WWII 'aliyah bet' immigration brought significant numbers to Palestine in "
            "1946-1947. UNSCOP (1947 UN Special Committee on Palestine) used the 1946 British "
            "Mandate estimates (608,225 Jews, 1,845,559 total = 32.96%) in its August 1947 "
            "report that preceded Resolution 181. Some sources cite approximately 630,000 Jews "
            "by late 1947. Using 630,000 / 1,900,000 gives ~33.2%, which would exceed 33%."
        ),
        "finding": (
            "The population percentage is borderline. The official 1946 British Mandate estimate "
            "of 32.96% is what historical sources cite in the context of Resolution 181. "
            "Some 1947-specific estimates could put the figure at or slightly above 33%, "
            "but most scholarly sources cite 'approximately 31-33%' or '32%' for the Jewish "
            "population proportion in the 1947 Mandatory Palestine context. The claim's 'less than "
            "33%' is supported by the official figures used by UNSCOP and cited in encyclopedias."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is there any authoritative source placing Jewish population at 33% or above?",
        "verification_performed": (
            "Searched academic and encyclopedia sources for the Jewish population percentage "
            "in 1947 Mandatory Palestine. Multiple sources (Britannica, UNSCOP report, Wikipedia) "
            "consistently cite approximately 32-33% Jewish, 67-68% Arab. The rounding of 32.96% "
            "to '33%' in many sources does not imply it was >= 33%; it reflects imprecision in "
            "popular summaries."
        ),
        "finding": (
            "Most sources round the Jewish population to '33%' or 'approximately one-third.' "
            "The precise British Mandate figure of 32.96% (< 33%) is consistent with this rounding. "
            "No source credibly places Jews at significantly above 33% before November 1947. "
            "The claim's 'less than 33%' is a precise statement that holds on the official data."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Was there actually a '1947 British census' as the claim states?",
        "verification_performed": (
            "Searched for '1947 Palestine census British Mandate.' Found that the last formal "
            "British census of Palestine was conducted in 1931. No census was conducted in 1947. "
            "The CJPME (Canadians for Justice and Peace in the Middle East) Factsheet 007 "
            "explicitly states: 'all figures following 1931 are estimates.' Population data "
            "for 1946-1947 came from estimates based on the 1931 census updated with immigration "
            "and vital statistics records, plus the Village Statistics 1945 survey."
        ),
        "finding": (
            "There was no '1947 British census.' The claim contains a factual inaccuracy about "
            "the data source. However, the underlying population figure ('less than 33%') is "
            "supported by the actual British Mandate population estimates for the period, "
            "which is what all authoritative historical sources use in the context of Resolution 181. "
            "This inaccuracy does not invalidate SC2 numerically, but readers should be aware "
            "that the data point is an estimate, not a census."
        ),
        "breaks_proof": False,
    },
]

# 11. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    # Compound claim verdict
    if n_holding == n_total and not any_unverified:
        verdict = "PROVED"
    elif n_holding == n_total and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif 0 < n_holding < n_total:
        # Mixed — some sub-claims hold, some don't
        verdict = "PARTIALLY VERIFIED"
    elif n_holding == 0 and not any_unverified:
        verdict = "DISPROVED"
    elif n_holding == 0 and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

    # Update fact registry with computed results
    FACT_REGISTRY["A1"]["method"] = f"jewish_pct_b1 = {sc1_pct} (from B1 data_values)"
    FACT_REGISTRY["A1"]["result"] = f"{sc1_pct}%"
    FACT_REGISTRY["A2"]["method"] = "jewish_pop / total_pop * 100 (B3 raw counts)"
    FACT_REGISTRY["A2"]["result"] = f"{sc2_pct:.4f}%"
    FACT_REGISTRY["A3"]["method"] = f"cross_check({jewish_pct_b1}, {jewish_pct_b2}, tol=0.01, mode=absolute)"
    FACT_REGISTRY["A3"]["result"] = str(cc_land)
    FACT_REGISTRY["A4"]["method"] = f"cross_check({jewish_pop_b3}, {jewish_pop_b4}, tol=0, mode=absolute)"
    FACT_REGISTRY["A4"]["result"] = str(cc_pop)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1_pct": {
            "value": str(jewish_pct_b1),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["source_land_britannica"]["data_values"]["jewish_pct_b1"],
        },
        "B2_pct": {
            "value": str(jewish_pct_b2),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["source_land_wiki"]["data_values"]["jewish_pct_b2"],
        },
        "B3_pop_jewish": {
            "value": str(jewish_pop_b3),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["source_pop_wiki"]["data_values"]["jewish_pop_b3"],
        },
        "B3_pop_total": {
            "value": str(total_pop_b3),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["source_pop_wiki"]["data_values"]["total_pop_b3"],
        },
        "B4_pop_jewish": {
            "value": str(jewish_pop_b4),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["source_pop_demog"]["data_values"]["jewish_pop_b4"],
        },
    }

    data_value_verification = {
        "B1": dv_results_b1,
        "B2": dv_results_b2,
        "B3": dv_results_b3,
        "B4": dv_results_b4,
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
                "description": "SC1 land percentage: Britannica (B1) vs Wikipedia (B2)",
                "values_compared": [str(jewish_pct_b1), str(jewish_pct_b2)],
                "agreement": cc_land,
                "tolerance": "0.01 absolute",
            },
            {
                "description": "SC2 Jewish population count: Wikipedia Partition Plan (B3) vs Demographic History (B4)",
                "values_compared": [str(jewish_pop_b3), str(jewish_pop_b4)],
                "agreement": cc_pop,
                "tolerance": "0 absolute",
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_jewish_state_land_pct": sc1_pct,
            "sc1_threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"],
            "sc1_operator": CLAIM_FORMAL["sub_claims"][0]["operator"],
            "sc1_holds": sc1_holds,
            "sc2_jewish_pop_pct": round(sc2_pct, 4),
            "sc2_threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"],
            "sc2_operator": CLAIM_FORMAL["sub_claims"][1]["operator"],
            "sc2_holds": sc2_holds,
            "n_sub_claims_holding": n_holding,
            "n_sub_claims_total": n_total,
            "claim_holds": claim_holds,
            "census_note": "No 1947 British census existed; figures are 1946 British Mandate estimates",
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
