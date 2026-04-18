"""
Proof: Eating the same calories late at night leads to significantly more weight
gain and fat storage than earlier in the day.
Generated: 2026-04-01
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
    "Eating the same calories late at night leads to significantly more weight "
    "gain and fat storage than earlier in the day."
)
CLAIM_FORMAL = {
    "subject": "Late-night caloric intake (same total calories as daytime eating)",
    "sub_claims": [
        {
            "id": "SC1",
            "property": (
                "Late eating (same total calories) measurably increases fat storage "
                "and reduces fat oxidation compared to earlier eating — confirmed by "
                "independent RCTs and controlled studies"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC1 requires at least 3 independently verified sources confirming that "
                "same-calorie late eating causes measurable changes in fat metabolism "
                "(reduced fat oxidation or increased fat storage markers). "
                "Three sources needed to establish scientific consensus per engine rules."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "Late eating (same total calories) causes significantly more overall "
                "weight gain over time — both statistically and clinically meaningful "
                "— compared to earlier eating"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "'Significantly' in the original claim is interpreted as both statistically "
                "significant (p < 0.05) AND clinically meaningful. If the best available "
                "meta-analysis of 29 RCTs describes the weight difference as 'small and of "
                "uncertain clinical importance' and 'not clinically significant (<5%)', "
                "SC2 is not established even if the difference is statistically non-zero. "
                "SC2 requires 3 independent sources confirming clinically meaningful weight "
                "differences from same-calorie late eating."
            ),
        },
    ],
    "compound_operator": "AND",
    "proof_direction": "affirm",
    "operator_note": (
        "The claim uses causal language ('leads to') requiring decomposition into "
        "SC-association/causation sub-claims per engine rules. SC1 covers fat storage "
        "and fat oxidation effects — established if 3+ RCTs and controlled studies confirm "
        "with same-calorie intake. SC2 covers the 'significantly more weight gain' component "
        "— established only if 3+ independent sources confirm clinically meaningful weight "
        "differences under controlled calorie conditions. Both must hold for PROVED. "
        "SC2's failure yields PARTIALLY VERIFIED (SC1 established, SC2 not established)."
    ),
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "sc1_source_a",
        "label": "SC1: Gu et al. 2020 RCT — late dinner reduces dietary fat oxidation by ~10 percentage points (P=.02)",
    },
    "B2": {
        "key": "sc1_source_b",
        "label": "SC1: McHill et al. 2017 — circadian food timing associated with body fat independent of calories and activity",
    },
    "B3": {
        "key": "sc1_source_c",
        "label": "SC1: Harvard Gazette 2022 — Vujovic et al. RCT: late eating shifts adipose gene expression toward fat accumulation",
    },
    "B4": {
        "key": "sc2_source_a",
        "label": "SC2: Liu et al. 2024 JAMA meta-analysis — 29 RCTs: earlier eating produces 1.75 kg more weight loss, but effect 'small and of uncertain clinical importance'",
    },
    "A1": {"label": "SC1 verified source count (fat storage effects)", "method": None, "result": None},
    "A2": {"label": "SC2 verified source count (clinically significant weight gain)", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — grouped by sub-claim
empirical_facts = {
    # SC1: Fat storage / fat oxidation effects (same-calorie conditions)
    "sc1_source_a": {
        "quote": (
            "total palmitate oxidized was lower for LD (74.5% ± 5.7%) "
            "than RD (84.5% ± 5.2%, P = .02)"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7337187/",
        "source_name": (
            "Gu et al. (2020) J Clin Endocrinol Metab — "
            "'Metabolic Effects of Late Dinner in Healthy Volunteers' (PMC/NIH)"
        ),
    },
    "sc1_source_b": {
        "quote": (
            "the consumption of food during the circadian evening and/or night, "
            "independent of more traditional risk factors such as amount or content "
            "of food intake and activity level, plays an important role in body composition"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5657289/",
        "source_name": (
            "McHill et al. (2017) Am J Clin Nutr — "
            "'Later circadian timing of food intake is associated with increased body fat' "
            "(PMC/NIH)"
        ),
    },
    "sc1_source_c": {
        "quote": (
            "adipose tissue gene expression toward increased adipogenesis and "
            "decreased lipolysis, which promote fat growth"
        ),
        "url": "https://news.harvard.edu/gazette/story/2022/10/study-looks-at-why-late-night-eating-increases-obesity-risk/",
        "source_name": (
            "Harvard Gazette (2022) — reporting Vujovic et al. 2022 Cell Metabolism "
            "isocaloric crossover RCT"
        ),
    },
    # SC2: Significantly greater weight gain over time
    "sc2_source_a": {
        "quote": (
            "consuming the majority of calories earlier in the day resulted in more "
            "weight loss compared with consuming them later in the day "
            "(MD, -1.75 kg; 95% CI, -2.37 to -1.13 kg)"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11530941/",
        "source_name": (
            "Liu et al. (2024) JAMA Network Open — "
            "'Meal Timing and Anthropometric and Metabolic Outcomes' "
            "systematic review and meta-analysis of 29 RCTs (PMC/NIH)"
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

print(f"  SC1 confirmed sources: {n_sc1} / {len(sc1_keys)}")
print(f"  SC2 confirmed sources: {n_sc2} / {len(sc2_keys)}")

# 6. PER-SUB-CLAIM EVALUATION (Rule 7: use compare())
sc1_holds = compare(
    n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
    label="SC1: fat storage/fat oxidation effects confirmed",
)
sc2_holds = compare(
    n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
    label="SC2: clinically significant weight gain confirmed",
)

# 7. COMPOUND EVALUATION
n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# 8. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": (
            "Do high-quality RCTs with gold-standard energy expenditure measurement "
            "show no metabolic difference between morning and evening calorie loading?"
        ),
        "verification_performed": (
            "Searched for 'meal timing energy expenditure RCT doubly labeled water' and "
            "'calorie timing no effect metabolism controlled trial'. Found Ruddick-Collins "
            "et al. 2022 (Cell Metabolism, PMC9605877): 30-subject 4-week crossover RCT "
            "using doubly-labeled water (gold standard). Found no difference in TDEE "
            "between morning-loaded and evening-loaded groups (2,871 vs 2,846 kcal/day, "
            "p=0.184). Conclusion: 'calorie utilization does not vary with time of day'."
        ),
        "finding": (
            "Ruddick-Collins et al. 2022 found no significant difference in total daily "
            "energy expenditure between morning and evening calorie-loading groups using "
            "doubly-labeled water (the gold standard for TDEE measurement). This directly "
            "contradicts the SC2 claim of 'significantly more weight gain.' This "
            "counter-evidence is already captured by SC2 failing to reach its source "
            "threshold: only 1 of 3 required sources supports SC2, and that source "
            "(JAMA 2024 meta-analysis) qualifies the weight difference as 'small and of "
            "uncertain clinical importance.' SC1's fat storage markers (fat oxidation, "
            "adipose gene expression) measure different endpoints than TDEE and are not "
            "undermined by this counter-evidence."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the TREAT randomized clinical trial show no significant between-group "
            "weight difference for time-restricted vs unrestricted eating?"
        ),
        "verification_performed": (
            "Searched for 'TREAT trial time restricted eating weight loss RCT'. Found "
            "Lowe et al. 2020 (JAMA Internal Medicine, PMID 32986097): 116 participants, "
            "12-week RCT comparing 16:8 TRE (eating 12pm-8pm) vs unrestricted eating. "
            "Between-group weight difference: -0.26 kg (95% CI -1.30 to 0.78, P=0.63). "
            "Conclusion: 'Time-restricted eating, in the absence of other interventions, "
            "is not more effective in weight loss than eating throughout the day.'"
        ),
        "finding": (
            "The TREAT trial found no significant between-group weight difference "
            "(P=0.63) over 12 weeks, directly contradicting SC2's 'significantly more "
            "weight gain' claim. This is a well-powered trial (n=116) in overweight/obese "
            "adults. This counter-evidence is already reflected in SC2 failing to reach "
            "threshold — the TREAT trial is one of the studies contributing to the JAMA "
            "2024 meta-analysis finding that effects are 'small and of uncertain clinical "
            "importance.' The TREAT trial does not address SC1's fat oxidation and adipose "
            "gene expression endpoints, which are established by separate RCTs."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the JAMA 2024 meta-analysis itself describe the weight difference as "
            "clinically unimportant, undermining the 'significantly' qualifier in SC2?"
        ),
        "verification_performed": (
            "Fetched PMC11530941 (Liu et al. 2024 JAMA Network Open, meta-analysis of "
            "29 RCTs, 2,485 participants). Authors state: 'the effect sizes found were "
            "small and of uncertain clinical importance.' They further note 'weight loss "
            "was not clinically significant (<5%).' The 1.75 kg mean difference has a "
            "95% CI not crossing zero (statistically significant) but the authors "
            "explicitly classify it as below clinical significance thresholds."
        ),
        "finding": (
            "The best available synthesis of evidence (29 RCTs, 2,485 participants) finds "
            "a statistically significant but clinically small weight difference (~1.75 kg) "
            "favoring earlier eating. The study authors explicitly describe this as 'small "
            "and of uncertain clinical importance.' Under the proof's interpretation of "
            "'significantly' as requiring both statistical and clinical meaningfulness, "
            "this meta-analysis does not support SC2. This is the primary reason SC2 fails "
            "to reach its source threshold — the evidence shows an effect exists but is "
            "not 'significant' in the clinically meaningful sense claimed."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Are the SC1 fat storage biomarker changes (fat oxidation, adipose gene "
            "expression) short-term surrogate endpoints that may not translate to actual "
            "long-term weight gain?"
        ),
        "verification_performed": (
            "Searched for 'fat oxidation surrogate endpoint weight gain clinical relevance' "
            "and 'circadian eating fat storage long-term outcomes'. The Gu et al. 2020 "
            "authors themselves note: 'If these changes occur on a chronic basis, they may "
            "contribute to the development of obesity' — hedged language. The Vujovic "
            "et al. 2022 study measured adipose gene expression changes over ~2 weeks, "
            "not actual weight gain. No RCT has demonstrated that the ~10 percentage-point "
            "fat oxidation reduction from a single late dinner directly produces clinically "
            "significant weight gain over months of identical caloric intake."
        ),
        "finding": (
            "The SC1 fat storage biomarker changes are biologically plausible mechanistic "
            "intermediaries but have not been shown in controlled trials to produce "
            "clinically significant long-term weight gain. Study authors use hedged "
            "language ('may contribute'). This is consistent with the PARTIALLY VERIFIED "
            "verdict: SC1 (fat metabolism affected by meal timing) is established; SC2 "
            "(clinically significant weight gain) is not established because bridging "
            "RCTs with long-term weight outcomes under identical calorie conditions have "
            "not demonstrated this effect."
        ),
        "breaks_proof": False,
    },
]

# 9. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
    uncertainty_override = False

    if any_breaks:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        # Mixed: SC1 holds but SC2 does not
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "DISPROVED" if is_disproof else "PROVED"
    elif claim_holds and any_unverified:
        verdict = (
            "DISPROVED (with unverified citations)"
            if is_disproof
            else "PROVED (with unverified citations)"
        )
    elif not claim_holds and n_holding == 0:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified sc1 citations) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1)
    FACT_REGISTRY["A2"]["method"] = f"count(verified sc2 citations) = {n_sc2}"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2)

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
        "fact_registry": {fid: dict(info) for fid, info in FACT_REGISTRY.items()},
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {
                "description": "SC1: independent sources consulted for fat storage effects",
                "n_sources_consulted": len(sc1_keys),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in sc1_keys},
                "independence_note": (
                    "Sources are from different independent research groups and publications: "
                    "Gu et al. (J Clin Endocrinol Metab, 2020), McHill et al. (Am J Clin Nutr, "
                    "2017), and Vujovic et al. (Cell Metabolism, 2022, via Harvard Gazette). "
                    "All three are peer-reviewed and measure fat storage/oxidation under "
                    "controlled or calorie-adjusted conditions."
                ),
            },
            {
                "description": "SC2: independent sources consulted for significant weight gain",
                "n_sources_consulted": len(sc2_keys),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in sc2_keys},
                "independence_note": (
                    "Only 1 source found for SC2 (JAMA 2024 meta-analysis of 29 RCTs). "
                    "This source confirms a statistically significant but clinically modest "
                    "weight difference (1.75 kg), which the authors themselves describe as "
                    "'small and of uncertain clinical importance.' Multiple high-quality "
                    "RCTs (Ruddick-Collins 2022, TREAT trial 2020) directly contradict SC2."
                ),
            },
        ],
        "sub_claim_results": [
            {
                "id": "SC1",
                "n_confirming": n_sc1,
                "threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"],
                "holds": sc1_holds,
                "description": "Fat storage/fat oxidation effects from same-calorie late eating",
            },
            {
                "id": "SC2",
                "n_confirming": n_sc2,
                "threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"],
                "holds": sc2_holds,
                "description": "Clinically significant weight gain from same-calorie late eating",
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_holding": n_holding,
            "n_total": n_total,
            "sc1_holds": sc1_holds,
            "sc2_holds": sc2_holds,
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
