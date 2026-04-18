"""
Proof: Nuclear power is the safest form of electricity generation with the lowest death rate per TWh produced.
Generated: 2026-04-01

Strategy: This is a superlative comparative claim. The primary data source (Our World in Data, OWID)
explicitly states that comparing nuclear, solar, and wind death rates is "misguided" because the
uncertainties are likely to overlap. Additionally, two independent nuclear death-rate estimates differ
by ~8x (Markandya & Wilkinson 2007: 0.074 deaths/TWh; Sovacool et al. 2016: 0.0097 deaths/TWh),
and even by the most favorable estimate, biofuels (0.0048 deaths/TWh) ranks lower than nuclear (0.0097).
Per proof-engine rules for comparative/superlative claims with source-acknowledged uncertainty,
uncertainty_override=True and the verdict is UNDETERMINED.
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

from scripts.verify_citations import verify_all_citations, build_citation_detail, verify_data_values
from scripts.extract_values import parse_number_from_quote
from scripts.computations import compare, explain_calc

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "Nuclear power is the safest form of electricity generation with the lowest "
    "death rate per TWh produced."
)
CLAIM_FORMAL = {
    "subject": "nuclear power",
    "property": (
        "death rate per TWh (deaths from accidents and air pollution) — "
        "rank among all electricity generation sources (1 = lowest/safest)"
    ),
    "operator": "==",
    "operator_note": (
        "'Safest with the lowest death rate per TWh' is operationalized as nuclear holding rank 1 "
        "(minimum death rate) among all electricity generation sources — coal, oil, gas, nuclear, "
        "hydro, solar, wind, and biofuels. "
        "Data from Our World in Data (OWID) is used, combining Markandya & Wilkinson (2007) for "
        "fossil fuels and Sovacool et al. (2016) for low-carbon sources. "
        "Two independent nuclear death-rate estimates exist and differ by ~8x: "
        "0.0097 deaths/TWh (Sovacool 2016, accidents only) and 0.074 deaths/TWh "
        "(Markandya & Wilkinson 2007, including some air-pollution effects). "
        "OWID explicitly cautions: 'the uncertainties around these values [nuclear/solar/wind] "
        "are likely to overlap' and calls comparing them 'misguided.' "
        "Per proof-engine rules for comparative/superlative claims with source-acknowledged "
        "overlapping uncertainty, uncertainty_override=True is set and the verdict is UNDETERMINED."
    ),
    "threshold": 1,  # nuclear must achieve rank 1 (lowest death rate) to prove the claim
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {
        "key": "owid_safest",
        "label": (
            "OWID 'What are the safest and cleanest sources of energy?' — "
            "uncertainty caveat: comparing nuclear/solar/wind is 'misguided' "
            "because uncertainties are likely to overlap"
        ),
    },
    "B2": {
        "key": "owid_data_table",
        "label": (
            "Our World in Data via Wikimedia Commons — death rates per TWh for all "
            "electricity sources (Markandya & Wilkinson 2007 + Sovacool et al. 2016)"
        ),
    },
    "A1": {
        "label": (
            "Nuclear rank by Sovacool 2016 death rate among all electricity sources "
            "(1 = lowest/safest)"
        ),
        "method": None,
        "result": None,
    },
    "A2": {
        "label": (
            "Coal-to-nuclear death rate ratio (coal M&W 2007 / nuclear Sovacool 2016): "
            "shows nuclear is dramatically safer than fossil fuels even if it is not THE lowest"
        ),
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
# ---------------------------------------------------------------------------
empirical_facts = {
    "owid_safest": {
        "quote": (
            "People often focus on the marginal differences at the bottom of the chart "
            "\u2014 between nuclear, solar, and wind. This comparison is misguided: the "
            "uncertainties around these values are likely to overlap."
        ),
        "url": "https://ourworldindata.org/safest-sources-of-energy",
        "source_name": (
            "Our World in Data \u2014 'What are the safest and cleanest sources of energy?' "
            "(Hannah Ritchie, 2020; updated July 2022)"
        ),
    },
    "owid_data_table": {
        "quote": (
            "Death rates from energy production is measured as the number of deaths by energy "
            "source per terawatt-hour (TWh) of production."
        ),
        "url": (
            "https://commons.wikimedia.org/wiki/Data:Deaths_per_TWh_energy_production,"
            "_all_sources_(Markandya_and_Wilkinson;_Sovacool_et_al.)_(OWID_4888).tab"
        ),
        "source_name": (
            "Our World in Data via Wikimedia Commons \u2014 deaths per TWh all sources "
            "(Markandya & Wilkinson 2007 + Sovacool et al. 2016)"
        ),
        "data_values": {
            "biofuels":         "0.0048",
            "nuclear_sovacool": "0.0097",
            "nuclear_mw2007":   "0.074",
            "solar":            "0.019",
            "wind":             "0.035",
            "hydro":            "0.0235",
            "coal":             "24.62",
            "oil":              "18.43",
            "gas":              "2.821",
        },
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. DATA VALUE VERIFICATION — confirm numbers appear on source page
# ---------------------------------------------------------------------------
dv_results = verify_data_values(
    empirical_facts["owid_data_table"]["url"],
    empirical_facts["owid_data_table"]["data_values"],
    "B2",
)

# ---------------------------------------------------------------------------
# 6. VALUE EXTRACTION — parse from data_values strings (Rule 1 via data_values)
# ---------------------------------------------------------------------------
nuclear_sovacool = parse_number_from_quote(
    empirical_facts["owid_data_table"]["data_values"]["nuclear_sovacool"],
    r"([\d.]+)", "B2_nuclear_sovacool"
)
nuclear_mw2007 = parse_number_from_quote(
    empirical_facts["owid_data_table"]["data_values"]["nuclear_mw2007"],
    r"([\d.]+)", "B2_nuclear_mw2007"
)
biofuels = parse_number_from_quote(
    empirical_facts["owid_data_table"]["data_values"]["biofuels"],
    r"([\d.]+)", "B2_biofuels"
)
solar = parse_number_from_quote(
    empirical_facts["owid_data_table"]["data_values"]["solar"],
    r"([\d.]+)", "B2_solar"
)
wind = parse_number_from_quote(
    empirical_facts["owid_data_table"]["data_values"]["wind"],
    r"([\d.]+)", "B2_wind"
)
hydro = parse_number_from_quote(
    empirical_facts["owid_data_table"]["data_values"]["hydro"],
    r"([\d.]+)", "B2_hydro"
)
coal = parse_number_from_quote(
    empirical_facts["owid_data_table"]["data_values"]["coal"],
    r"([\d.]+)", "B2_coal"
)
oil = parse_number_from_quote(
    empirical_facts["owid_data_table"]["data_values"]["oil"],
    r"([\d.]+)", "B2_oil"
)
gas = parse_number_from_quote(
    empirical_facts["owid_data_table"]["data_values"]["gas"],
    r"([\d.]+)", "B2_gas"
)

# ---------------------------------------------------------------------------
# 7. COMPUTATIONS (Rule 7)
# ---------------------------------------------------------------------------

# All electricity sources with death rates — using Sovacool 2016 for low-carbon,
# M&W 2007 for fossil fuels (the OWID composite dataset).
all_sources = {
    "biofuels":  biofuels,
    "nuclear":   nuclear_sovacool,
    "solar":     solar,
    "hydro":     hydro,
    "wind":      wind,
    "gas":       gas,
    "oil":       oil,
    "coal":      coal,
}

# Rank sources by death rate (ascending = safest first)
sorted_sources = sorted(all_sources.items(), key=lambda x: x[1])

print("\n--- Death rates per TWh, ranked lowest to highest ---")
print("    (Sovacool 2016 for low-carbon sources; M&W 2007 for fossil fuels)")
for rank, (src, rate) in enumerate(sorted_sources, 1):
    marker = "  <-- NUCLEAR" if src == "nuclear" else ""
    print(f"  Rank {rank:2d}: {src:<12s} {rate:.4f} deaths/TWh{marker}")

nuclear_rank = next(
    i + 1 for i, (src, _) in enumerate(sorted_sources) if src == "nuclear"
)
print(f"\nNuclear rank (Sovacool 2016): {nuclear_rank} of {len(sorted_sources)}")

# Is nuclear rank 1 (lowest = safest)?  — claim evaluation
claim_holds = compare(
    nuclear_rank, "==", CLAIM_FORMAL["threshold"],
    label="Nuclear rank == 1 (lowest death rate across all electricity sources)"
)

# Biofuels clearly below nuclear (confirming nuclear is not the global minimum)
compare(
    biofuels, "<", nuclear_sovacool,
    label="Biofuels (0.0048) < Nuclear/Sovacool (0.0097): biofuels has lower rate than nuclear"
)

# Coal-to-nuclear ratio (A2): nuclear is dramatically safer than fossil fuels
nuclear_vs_coal_ratio = explain_calc(
    "coal / nuclear_sovacool", locals(),
    label="A2: Coal / Nuclear (Sovacool 2016) death-rate ratio"
)

# Methodological comparison: M&W 2007 nuclear vs solar/wind (shows contradiction)
mw_nuclear_vs_solar = explain_calc(
    "nuclear_mw2007 / solar", locals(),
    label="Nuclear (M&W 2007) / Solar ratio [>1 means nuclear LESS safe than solar by M&W]"
)

# ---------------------------------------------------------------------------
# 8. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "If biofuels are excluded from 'electricity generation' sources, "
            "does nuclear then have the lowest death rate?"
        ),
        "verification_performed": (
            "Reviewed OWID methodology and Sovacool et al. 2016: 'biofuels' in the dataset "
            "covers biogas and biomass power plants used for electricity generation. OWID's "
            "'death rates from energy production' chart includes biofuels as an electricity "
            "generation source. Searched 'biofuels electricity generation death rate OWID "
            "Sovacool' to confirm scope."
        ),
        "finding": (
            "Even if biofuels were excluded, the uncertainty_override=True verdict applies "
            "regardless: OWID explicitly warns that comparing nuclear, solar, and wind is "
            "'misguided' because 'the uncertainties around these values are likely to overlap.' "
            "Nuclear (0.0097) < solar (0.019) and wind (0.035) by Sovacool 2016 point estimates, "
            "but OWID's caveat prevents a definitive superlative ranking."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the Markandya & Wilkinson (2007) nuclear estimate (0.074 deaths/TWh) "
            "contradict the claim that nuclear has the lowest death rate?"
        ),
        "verification_performed": (
            "Reviewed the OWID all-sources Wikimedia Commons dataset: it contains two entries "
            "for nuclear — 0.074 (M&W 2007) and 0.0097 (Sovacool 2016). These differ by ~8x. "
            "M&W 2007 includes occupational deaths and some air-pollution effects; Sovacool 2016 "
            "focuses on accident deaths (Chernobyl, Fukushima, other accidents). Searched "
            "'nuclear death rate Markandya Wilkinson 2007 vs Sovacool 2016 comparison' to confirm "
            "methodological basis of each estimate."
        ),
        "finding": (
            "The M&W 2007 nuclear estimate (0.074 deaths/TWh) directly contradicts the claim: "
            "nuclear would be LESS safe than solar (0.019) and wind (0.035) by point estimates. "
            "The 8x discrepancy between estimates reflects a fundamental methodological disagreement "
            "about what death categories to include; no consensus exists on which is 'correct.' "
            "Under M&W 2007, nuclear is not only not the safest — it is less safe than two major "
            "renewable sources. This counter-evidence breaks the proof."
        ),
        "breaks_proof": True,
    },
    {
        "question": (
            "Is there a consensus source that definitively establishes nuclear as "
            "having the single lowest death rate across all electricity generation sources?"
        ),
        "verification_performed": (
            "Searched 'nuclear lowest death rate electricity all sources 2024 definitive', "
            "'safest energy source peer reviewed 2023', and 'nuclear solar wind death rate "
            "definitive ranking'. Reviewed Our World in Data, Sovacool et al. 2016, "
            "Markandya & Wilkinson 2007, and WHO energy data."
        ),
        "finding": (
            "No authoritative source makes the unqualified claim that nuclear has the definitively "
            "lowest death rate per TWh across all electricity sources. OWID — the most widely cited "
            "source on this topic — explicitly cautions against making this comparison. "
            "Most sources describe nuclear as 'among the safest' or 'comparable to solar and wind,' "
            "not as definitively the lowest."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 9. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    # uncertainty_override: OWID explicitly states the comparison between nuclear, solar,
    # and wind is "misguided" because "the uncertainties around these values are likely to
    # overlap." Per proof-engine rules, this triggers UNDETERMINED for superlative claims.
    uncertainty_override = True  # source: OWID safest-sources page (B1)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif uncertainty_override:
        verdict = "UNDETERMINED"
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

    # Populate A-type fact results
    FACT_REGISTRY["A1"]["method"] = (
        f"sort(all_sources by death_rate)[nuclear] → rank {nuclear_rank}"
    )
    FACT_REGISTRY["A1"]["result"] = str(nuclear_rank)

    FACT_REGISTRY["A2"]["method"] = "coal / nuclear_sovacool"
    FACT_REGISTRY["A2"]["result"] = f"{nuclear_vs_coal_ratio:.1f}x"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: data_values parsed directly (no verify_extraction needed per template)
    extractions = {
        "B2_nuclear_sovacool": {
            "value": str(nuclear_sovacool),
            "value_in_quote": True,
            "quote_snippet": "data_values['nuclear_sovacool'] = '0.0097'",
        },
        "B2_nuclear_mw2007": {
            "value": str(nuclear_mw2007),
            "value_in_quote": True,
            "quote_snippet": "data_values['nuclear_mw2007'] = '0.074'",
        },
        "B2_biofuels": {
            "value": str(biofuels),
            "value_in_quote": True,
            "quote_snippet": "data_values['biofuels'] = '0.0048'",
        },
        "B2_solar": {
            "value": str(solar),
            "value_in_quote": True,
            "quote_snippet": "data_values['solar'] = '0.019'",
        },
        "B2_wind": {
            "value": str(wind),
            "value_in_quote": True,
            "quote_snippet": "data_values['wind'] = '0.035'",
        },
        "B2_coal": {
            "value": str(coal),
            "value_in_quote": True,
            "quote_snippet": "data_values['coal'] = '24.62'",
        },
        "B2_gas": {
            "value": str(gas),
            "value_in_quote": True,
            "quote_snippet": "data_values['gas'] = '2.821'",
        },
    }

    data_value_verification = {
        "B2": {k: v for k, v in dv_results.items()},
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
                "description": (
                    "Two independent nuclear death-rate estimates (methodological cross-check)"
                ),
                "values_compared": [str(nuclear_sovacool), str(nuclear_mw2007)],
                "agreement": False,
                "tolerance": "N/A — these are independent methodological estimates, not "
                             "independent measurements of the same quantity",
                "note": (
                    f"Sovacool 2016 (accidents only): {nuclear_sovacool} deaths/TWh; "
                    f"M&W 2007 (accidents + some air pollution): {nuclear_mw2007} deaths/TWh. "
                    f"Ratio: {nuclear_mw2007/nuclear_sovacool:.1f}x. "
                    "Disagreement reflects genuine methodological controversy, not measurement error."
                ),
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "nuclear_rank_sovacool_2016": nuclear_rank,
            "nuclear_rate_sovacool_2016": nuclear_sovacool,
            "nuclear_rate_mw2007": nuclear_mw2007,
            "biofuels_rate_sovacool_2016": biofuels,
            "solar_rate_sovacool_2016": solar,
            "wind_rate_sovacool_2016": wind,
            "coal_rate_mw2007": coal,
            "coal_to_nuclear_ratio": round(nuclear_vs_coal_ratio, 1),
            "threshold": CLAIM_FORMAL["threshold"],
            "claim_holds": claim_holds,
            "uncertainty_override": uncertainty_override,
            "breaks_proof_triggered": any_breaks,
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
