"""
Proof: The correlation between human brain volume and intelligence is r = 0.4
Generated: 2026-03-27

Two sub-claims are evaluated:
  SC1: The unconditional overall meta-analytic estimate is r ≈ 0.40
  SC2: The conditional estimate (healthy adults, high-quality tests) is r ≈ 0.40
"""
import json
from datetime import date
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.smart_extract import verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail, verify_data_values
from scripts.extract_values import parse_number_from_quote
from scripts.computations import compare, cross_check

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "The correlation between human brain volume and intelligence is r = 0.4"
CLAIM_FORMAL = {
    "subject": "Pearson r correlation between human brain volume (total in vivo, MRI) and intelligence (IQ/g)",
    "property": "meta-analytic correlation coefficient",
    "operator": "within",
    "operator_note": (
        "r = 0.4 is interpreted as r within ±0.05 of 0.40 (i.e., 0.35 ≤ r ≤ 0.45). "
        "This is a standard rounding tolerance for meta-analytic correlations. "
        "Two sub-claims are evaluated: "
        "SC1 tests whether the unconditional overall meta-analytic estimate equals r ≈ 0.40 "
        "(this would be false if major meta-analyses converge on r ≈ 0.24). "
        "SC2 tests whether the conditional estimate—restricted to healthy adults using "
        "high-quality intelligence tests—equals r ≈ 0.40. "
        "'Brain volume' means total in vivo brain volume via MRI. "
        "'Intelligence' means psychometric IQ or g-factor test scores."
    ),
    "threshold": 0.40,
    "tolerance": 0.05,
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "pietschnig_2015", "label": "Pietschnig et al. (2015): 88 studies, 8000+ subjects; weighted r = .24"},
    "B2": {"key": "pmc_2022",        "label": "Nave et al. (2022): largest meta-analysis (N=26k+); r = 0.24, range 0.10–0.37"},
    "B3": {"key": "wiki_conditional","label": "Wikipedia Neuroscience & Intelligence: r ≈ 0.4 for healthy adults, high-quality tests"},
    "A1": {"label": "SC1-A: |r_Pietschnig - 0.40|", "method": None, "result": None},
    "A2": {"label": "SC1-B: |r_PMC2022 - 0.40|",    "method": None, "result": None},
    "A3": {"label": "SC2:   |r_conditional - 0.40|", "method": None, "result": None},
    "A4": {"label": "Cross-check: Pietschnig 2015 vs PMC 2022 overall r agreement", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS
# SC1 sources: Pietschnig 2015 and PMC 2022 — both report the unconditional overall r
# SC2 source:  Wikipedia summarising Gignac & Bates (2017) — conditional r ≈ 0.4
empirical_facts = {
    "pietschnig_2015": {
        "quote": (
            "Our results showed significant positive associations of brain volume and IQ (r=.24, "
            "R(2)=.06) that generalize over age (children vs. adults), IQ domain (full-scale, "
            "performance, and verbal IQ), and sex."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/26449760/",
        "source_name": "Pietschnig et al. (2015), Neuroscience & Biobehavioral Reviews — PubMed",
        "data_values": {"r_overall": ".24"},
    },
    "pmc_2022": {
        "quote": (
            "Brain size and IQ associations yielded r = 0.24, with the strongest effects observed "
            "for more g-loaded tests and in healthy samples that generalize across participant sex "
            "and age bands."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9096623/",
        "source_name": "Nave et al. (2022), Royal Society Open Science — PMC",
        "data_values": {"r_overall": "0.24"},
    },
    "wiki_conditional": {
        "quote": (
            "In healthy adults, the correlation of total brain volume and IQ is approximately "
            "0.4 when high-quality tests are used."
        ),
        "url": "https://en.wikipedia.org/wiki/Neuroscience_and_intelligence",
        "source_name": "Wikipedia — Neuroscience and intelligence",
        "data_values": {"r_conditional": "0.4"},
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. DATA VALUE VERIFICATION
dv_results_pietschnig = verify_data_values(
    empirical_facts["pietschnig_2015"]["url"],
    empirical_facts["pietschnig_2015"]["data_values"],
    "B1",
)
dv_results_pmc = verify_data_values(
    empirical_facts["pmc_2022"]["url"],
    empirical_facts["pmc_2022"]["data_values"],
    "B2",
)
dv_results_wiki = verify_data_values(
    empirical_facts["wiki_conditional"]["url"],
    empirical_facts["wiki_conditional"]["data_values"],
    "B3",
)

# 6. VALUE EXTRACTION (Rule 1) — parse r values from data_values strings
r_pietschnig = parse_number_from_quote(
    empirical_facts["pietschnig_2015"]["data_values"]["r_overall"],
    r"([.\d]+)", "B1_r_overall"
)
r_pmc2022 = parse_number_from_quote(
    empirical_facts["pmc_2022"]["data_values"]["r_overall"],
    r"([.\d]+)", "B2_r_overall"
)
r_conditional = parse_number_from_quote(
    empirical_facts["wiki_conditional"]["data_values"]["r_conditional"],
    r"([.\d]+)", "B3_r_conditional"
)

# Verify key terms appear in quotes (Rule 1 keyword check)
verify_extraction(".24", empirical_facts["pietschnig_2015"]["quote"], "B1")
verify_extraction("0.24", empirical_facts["pmc_2022"]["quote"], "B2")
verify_extraction("0.4", empirical_facts["wiki_conditional"]["quote"], "B3")

# 7. CROSS-CHECK (Rule 6): Two independent meta-analyses on the unconditional overall r
cross_check(r_pietschnig, r_pmc2022, tolerance=0.01, mode="absolute",
            label="SC1 cross-check: Pietschnig 2015 vs PMC 2022 overall r")

# 8. SUB-CLAIM EVALUATIONS
THRESHOLD = CLAIM_FORMAL["threshold"]   # 0.40
TOLERANCE = CLAIM_FORMAL["tolerance"]   # 0.05

# SC1: Is the unconditional meta-analytic r within ±0.05 of 0.40?
sc1_deviation_a = abs(r_pietschnig - THRESHOLD)
print(f"\n  SC1-A: |r_Pietschnig({r_pietschnig:.2f}) - threshold({THRESHOLD:.2f})| = {sc1_deviation_a:.4f}")
sc1_holds_a = compare(sc1_deviation_a, "<=", TOLERANCE,
                      label="SC1-A: Pietschnig r within ±0.05 of 0.40")

sc1_deviation_b = abs(r_pmc2022 - THRESHOLD)
print(f"\n  SC1-B: |r_PMC2022({r_pmc2022:.2f}) - threshold({THRESHOLD:.2f})| = {sc1_deviation_b:.4f}")
sc1_holds_b = compare(sc1_deviation_b, "<=", TOLERANCE,
                      label="SC1-B: PMC 2022 r within ±0.05 of 0.40")

sc1_max_deviation = max(sc1_deviation_a, sc1_deviation_b)
sc1_holds = compare(sc1_max_deviation, "<=", TOLERANCE,
                    label="SC1: max unconditional r deviation within ±0.05 of 0.40")

# SC2: Is the conditional r (healthy adults, quality tests) within ±0.05 of 0.40?
sc2_deviation = abs(r_conditional - THRESHOLD)
print(f"\n  SC2:   |r_conditional({r_conditional:.2f}) - threshold({THRESHOLD:.2f})| = {sc2_deviation:.4f}")
sc2_holds = compare(sc2_deviation, "<=", TOLERANCE,
                    label="SC2: conditional r within ±0.05 of 0.40")

# 9. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Does any major unconditional meta-analysis report r = 0.40 for brain volume vs. IQ?",
        "verification_performed": (
            "Searched for 'brain volume IQ meta-analysis r = 0.4 overall' and reviewed "
            "McDaniel (2005), Pietschnig et al. (2015), and Nave et al. (2022). "
            "McDaniel (2005) found r = 0.33 overall (37 samples, n = 1,530). "
            "Pietschnig et al. (2015) found r = .24 (88 studies, 8,000+ subjects). "
            "Nave et al. (2022) found r = 0.24 (86 studies, N = 26,000+, range 0.10–0.37). "
            "Gignac & Bates (2017) concluded r ≈ 0.40 only as a conditional estimate "
            "(excellent-quality tests), not unconditionally."
        ),
        "finding": (
            "No major meta-analysis reports r = 0.40 as the unconditional overall estimate. "
            "The three principal meta-analyses converge on r = 0.24–0.33."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could publication bias be deflating the estimates below 0.40?",
        "verification_performed": (
            "Examined publication bias analysis in Pietschnig et al. (2015) and Nave et al. (2022). "
            "PMC 2022 abstract states: 'Summary effects appeared to be somewhat inflated due to "
            "selective reporting, and cross-temporally decreasing effect sizes indicated a confounding "
            "decline effect.' Pietschnig 2015 similarly found 'strong and positive correlation "
            "coefficients have been reported frequently in the literature whilst small and "
            "non-significant associations appear to have been often omitted from reports.'"
        ),
        "finding": (
            "Publication bias INFLATES reported r values, not deflates them. After bias correction, "
            "estimates remain around r = 0.24. The true unconditional r is likely at or below 0.24, "
            "not at 0.40."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is the Wikipedia source for SC2 citing a credible peer-reviewed finding?",
        "verification_performed": (
            "Wikipedia's claim (r ≈ 0.4 for healthy adults, high-quality tests) cites Gignac & Bates "
            "(2017), published in Intelligence (Elsevier). That paper found corrected correlations of "
            ".23 (fair quality), .32 (good quality), .39 (excellent quality) and concluded the "
            "association is 'arguably best characterised as r ≈ .40.' This is a published peer-reviewed "
            "finding, though it applies only to healthy adult samples using the best IQ tests."
        ),
        "finding": (
            "SC2 is supported by peer-reviewed research. The conditional r ≈ 0.40 is a credible "
            "finding, not a fringe estimate. However, it requires specifying the condition "
            "(excellent-quality tests, healthy adults)."
        ),
        "breaks_proof": False,
    },
]

# 10. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif sc1_holds and sc2_holds and not any_unverified:
        verdict = "PROVED"
    elif sc1_holds and sc2_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not sc1_holds and sc2_holds:
        # SC1 disproved: unconditional r ≈ 0.24, not 0.40
        # SC2 proved:    conditional r ≈ 0.40 (healthy adults, quality tests)
        verdict = "PARTIALLY VERIFIED"
    else:
        verdict = "DISPROVED (with unverified citations)" if any_unverified else "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = f"abs({r_pietschnig:.2f} - {THRESHOLD:.2f})"
    FACT_REGISTRY["A1"]["result"] = f"{sc1_deviation_a:.4f}"
    FACT_REGISTRY["A2"]["method"] = f"abs({r_pmc2022:.2f} - {THRESHOLD:.2f})"
    FACT_REGISTRY["A2"]["result"] = f"{sc1_deviation_b:.4f}"
    FACT_REGISTRY["A3"]["method"] = f"abs({r_conditional:.2f} - {THRESHOLD:.2f})"
    FACT_REGISTRY["A3"]["result"] = f"{sc2_deviation:.4f}"
    FACT_REGISTRY["A4"]["method"] = (
        f"cross_check({r_pietschnig:.2f}, {r_pmc2022:.2f}, tol=0.01, mode='absolute')"
    )
    FACT_REGISTRY["A4"]["result"] = (
        "Agreement" if abs(r_pietschnig - r_pmc2022) <= 0.01 else "Disagreement"
    )

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": str(r_pietschnig),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["pietschnig_2015"]["quote"][:80],
        },
        "B2": {
            "value": str(r_pmc2022),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["pmc_2022"]["quote"][:80],
        },
        "B3": {
            "value": str(r_conditional),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["wiki_conditional"]["quote"][:80],
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
        "data_value_verification": {
            "B1": dv_results_pietschnig,
            "B2": dv_results_pmc,
            "B3": dv_results_wiki,
        },
        "cross_checks": [
            {
                "description": "SC1: Pietschnig 2015 vs PMC 2022 unconditional r (two independent meta-analyses)",
                "values_compared": [str(r_pietschnig), str(r_pmc2022)],
                "agreement": abs(r_pietschnig - r_pmc2022) <= 0.01,
                "tolerance": "0.01 absolute",
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "r_overall_pietschnig_2015": r_pietschnig,
            "r_overall_pmc_2022": r_pmc2022,
            "r_conditional_wiki": r_conditional,
            "threshold": THRESHOLD,
            "tolerance": TOLERANCE,
            "sc1_holds": sc1_holds,
            "sc2_holds": sc2_holds,
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
