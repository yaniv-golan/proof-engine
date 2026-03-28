"""
Proof: Napoleon Bonaparte stood shorter than the average Frenchman of his era.
Generated: 2026-03-28
"""
import json
import os
import re
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

# --- STRUCTURAL IMPORTS ---
from scripts.verify_citations import verify_all_citations, build_citation_detail, verify_data_values
from scripts.computations import compare, explain_calc, cross_check
from scripts.extract_values import parse_number_from_quote

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "Napoleon Bonaparte stood shorter than the average Frenchman of his era."
CLAIM_FORMAL = {
    "subject": "Napoleon Bonaparte's height",
    "property": "comparison of Napoleon's height to average French male height of his era (late 18th/early 19th century)",
    "operator": "<",
    "operator_note": (
        "'stood shorter than' is interpreted as strictly less than: Napoleon's height < average French male height. "
        "Napoleon lived 1769-1821; 'his era' is interpreted as the late 18th to early 19th century. "
        "Heights are compared in centimeters. If Napoleon's height is equal to or greater than the average, "
        "the claim is DISPROVED."
    ),
    "threshold": "average French male height (~164-165 cm)",
    "measurement_note": (
        "Napoleon's height was recorded in pre-metric French units (pieds and pouces). "
        "The French pouce (inch) was 2.71 cm vs the English inch at 2.54 cm. "
        "His recorded '5 pieds 2 pouces' translates to approximately 168-170 cm in modern units, "
        "not the 157 cm that a naive English conversion would yield."
    ),
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "britannica_height", "label": "Britannica: Napoleon's height at death (~1.68m) and average French male height in 1820 (~1.65m)"},
    "B2": {"key": "history_com", "label": "History.com: Napoleon's height ~1.67m, above average for early 1800s French men"},
    "B3": {"key": "napoleon_series", "label": "Napoleon Series: Average French male height 1800-1820 was 164.1 cm"},
    "B4": {"key": "britannica_story", "label": "Britannica: Napoleon average or taller, most Frenchmen 5'2\"-5'6\""},
    "A1": {"label": "Comparison: Napoleon's height vs average French male height", "method": None, "result": None},
    "A2": {"label": "Cross-check: Napoleon's height vs average using second source pair", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS
empirical_facts = {
    "britannica_height": {
        "quote": "At the time of his death in 1821, Napoleon measured about 5 feet 7 inches (roughly 1.68 meters) tall.",
        "url": "https://www.britannica.com/question/Was-Napoleon-short",
        "source_name": "Encyclopaedia Britannica",
        "data_values": {
            "napoleon_height_m": "1.68",
            "avg_french_height_m": "1.65",
        },
    },
    "history_com": {
        "quote": "Three French sources—his valet Constant, General Gourgaud, and his personal physician Francesco Antommarchi—said that Napoleon's height was just over 5 pieds 2 pouces (5'2\"). Applying the French measurements of the time, that equals around 1.67 meters, or just under 5'6\", which is a little above average for a French man in the early 1800s.",
        "url": "https://www.history.com/articles/napoleon-complex-short",
        "source_name": "History.com (A&E Networks)",
        "data_values": {
            "napoleon_height_m": "1.67",
        },
    },
    "napoleon_series": {
        "quote": "France 1800 - 1820 164.1",
        "url": "https://www.napoleon-series.org/research/abstract/population/vital/c_heights1.html",
        "source_name": "The Napoleon Series (anthropometric data compilation)",
        "data_values": {
            "avg_french_height_cm": "164.1",
        },
    },
    "britannica_story": {
        "quote": "most Frenchmen stood between 5'2\" and 5'6\" (1.58 and 1.68 meters) tall",
        "url": "https://www.britannica.com/story/was-napoleon-short",
        "source_name": "Encyclopaedia Britannica",
        "data_values": {
            "french_range_low_m": "1.58",
            "french_range_high_m": "1.68",
        },
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. DATA VALUE VERIFICATION
dv_results_b1 = verify_data_values(
    empirical_facts["britannica_height"]["url"],
    empirical_facts["britannica_height"]["data_values"],
    "B1",
)
dv_results_b2 = verify_data_values(
    empirical_facts["history_com"]["url"],
    empirical_facts["history_com"]["data_values"],
    "B2",
)
dv_results_b3 = verify_data_values(
    empirical_facts["napoleon_series"]["url"],
    empirical_facts["napoleon_series"]["data_values"],
    "B3",
)
dv_results_b4 = verify_data_values(
    empirical_facts["britannica_story"]["url"],
    empirical_facts["britannica_story"]["data_values"],
    "B4",
)

# 6. VALUE EXTRACTION (Rule 1) — parse from data_values
napoleon_height_b1 = parse_number_from_quote(
    empirical_facts["britannica_height"]["data_values"]["napoleon_height_m"],
    r"([\d.]+)", "B1_napoleon_height"
)
avg_french_b1 = parse_number_from_quote(
    empirical_facts["britannica_height"]["data_values"]["avg_french_height_m"],
    r"([\d.]+)", "B1_avg_french"
)
napoleon_height_b2 = parse_number_from_quote(
    empirical_facts["history_com"]["data_values"]["napoleon_height_m"],
    r"([\d.]+)", "B2_napoleon_height"
)
avg_french_b3_cm = parse_number_from_quote(
    empirical_facts["napoleon_series"]["data_values"]["avg_french_height_cm"],
    r"([\d.]+)", "B3_avg_french_cm"
)

# Convert Napoleon Series cm to meters for comparison
avg_french_b3 = explain_calc("avg_french_b3_cm / 100", locals(), label="Average French height (B3) in meters")

# 7. CROSS-CHECK (Rule 6) — independent sources must agree
# Napoleon's height: B1 (1.68m) vs B2 (1.67m) — should be within 0.02m
print("\n--- Cross-checks ---")
napoleon_cross = cross_check(
    napoleon_height_b1, napoleon_height_b2,
    tolerance=0.02, mode="absolute",
    label="Napoleon height cross-check (B1 vs B2)"
)

# Average French height: B1 (1.65m) vs B3 (1.641m) — should be within 0.02m
avg_cross = cross_check(
    avg_french_b1, avg_french_b3,
    tolerance=0.02, mode="absolute",
    label="Average French height cross-check (B1 vs B3)"
)

# 8. COMPUTATION (Rule 7)
print("\n--- Claim evaluation ---")
# Use conservative estimates: lowest Napoleon height (1.67m from B2) vs highest average (1.65m from B1)
napoleon_conservative = explain_calc(
    "min(napoleon_height_b1, napoleon_height_b2)",
    locals(),
    label="Conservative Napoleon height (lower of two sources)"
)
avg_french_generous = explain_calc(
    "max(avg_french_b1, avg_french_b3)",
    locals(),
    label="Generous average French height (higher of two sources)"
)

# The claim says Napoleon was SHORTER. Compare Napoleon < average
difference_cm = explain_calc(
    "(napoleon_conservative - avg_french_generous) * 100",
    locals(),
    label="Napoleon minus average French male (cm)"
)

# 9. CLAIM EVALUATION
# The claim is that Napoleon < average. We test this:
claim_holds = compare(
    napoleon_conservative, "<", avg_french_generous,
    label="Napoleon height < average French male height"
)

# 10. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Are there any credible historical sources that place Napoleon's height below the French average?",
        "verification_performed": (
            "Searched for 'Napoleon shorter than average evidence sources claiming Napoleon was genuinely short'. "
            "Reviewed results from History.com, Britannica, National Geographic, Washington Post, and Wikipedia. "
            "All sources consistently state Napoleon was average height or above for his era."
        ),
        "finding": (
            "No credible source claims Napoleon was below average height. The 'short Napoleon' myth is universally "
            "attributed to: (1) confusion between French and English measurement units, and (2) British propaganda "
            "cartoons by James Gillray."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the French measurement conversion be wrong, making Napoleon actually shorter?",
        "verification_performed": (
            "Checked multiple sources on the French pouce (inch) conversion. The French pouce was 2.71 cm vs "
            "the English inch at 2.54 cm. Napoleon's '5 pieds 2 pouces' converts to ~168 cm, not 157 cm. "
            "This conversion is well-established in metrology."
        ),
        "finding": (
            "The conversion is consistent across all scholarly sources. Napoleon at 5 pieds 2 pouces = "
            "approximately 168 cm. There is no credible dispute about this conversion factor."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the average French male height have been higher than 164-165 cm, making Napoleon relatively shorter?",
        "verification_performed": (
            "Consulted Napoleon Series anthropometric data and Britannica. The Napoleon Series gives 164.1 cm "
            "for 1800-1820 French males. Britannica gives ~1.65m. Academic anthropometric studies by Komlos "
            "confirm these ranges. No source suggests the average exceeded 166 cm."
        ),
        "finding": (
            "Average French male height in Napoleon's era was consistently reported as 164-165 cm across "
            "independent sources. Even at the generous upper bound of 165 cm, Napoleon (167-170 cm) was still taller."
        ),
        "breaks_proof": False,
    },
]

# 11. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    # The claim says Napoleon was SHORTER. Evidence shows he was TALLER.
    if claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = "compare(napoleon_conservative, '<', avg_french_generous)"
    FACT_REGISTRY["A1"]["result"] = f"Napoleon ({napoleon_conservative}m) vs avg French ({avg_french_generous}m): claim_holds={claim_holds}"
    FACT_REGISTRY["A2"]["method"] = "cross_check() on independent sources"
    FACT_REGISTRY["A2"]["result"] = f"Napoleon heights agree ({napoleon_height_b1}m vs {napoleon_height_b2}m), avg heights agree ({avg_french_b1}m vs {avg_french_b3}m)"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1_napoleon_height": {
            "value": str(napoleon_height_b1),
            "value_in_quote": True,
            "quote_snippet": "data_values['napoleon_height_m']",
        },
        "B1_avg_french": {
            "value": str(avg_french_b1),
            "value_in_quote": True,
            "quote_snippet": "data_values['avg_french_height_m']",
        },
        "B2_napoleon_height": {
            "value": str(napoleon_height_b2),
            "value_in_quote": True,
            "quote_snippet": "data_values['napoleon_height_m']",
        },
        "B3_avg_french_cm": {
            "value": str(avg_french_b3_cm),
            "value_in_quote": True,
            "quote_snippet": "data_values['avg_french_height_cm']",
        },
    }

    data_value_verification = {
        "B1": {k: v for k, v in dv_results_b1.items()},
        "B2": {k: v for k, v in dv_results_b2.items()},
        "B3": {k: v for k, v in dv_results_b3.items()},
        "B4": {k: v for k, v in dv_results_b4.items()},
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
                "description": "Napoleon height: Britannica vs History.com",
                "values_compared": [str(napoleon_height_b1), str(napoleon_height_b2)],
                "agreement": napoleon_cross,
                "tolerance": "0.02m absolute",
            },
            {
                "description": "Average French male height: Britannica vs Napoleon Series",
                "values_compared": [str(avg_french_b1), str(avg_french_b3)],
                "agreement": avg_cross,
                "tolerance": "0.02m absolute",
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "napoleon_height_conservative_m": napoleon_conservative,
            "avg_french_height_generous_m": avg_french_generous,
            "difference_cm": difference_cm,
            "claim_holds": claim_holds,
            "napoleon_was_taller_by_cm": difference_cm,
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
