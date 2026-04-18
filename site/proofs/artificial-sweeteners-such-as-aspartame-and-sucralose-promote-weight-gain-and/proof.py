"""
Proof: Artificial sweeteners such as aspartame and sucralose promote weight gain and metabolic disease.
Generated: 2026-04-01

Claim type: Causal compound claim (SC-association + SC-causation).
"Promote" implies causation, not mere correlation. Decomposed per skill instructions.
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
    "Artificial sweeteners such as aspartame and sucralose promote weight gain "
    "and metabolic disease."
)
CLAIM_FORMAL = {
    "subject": "artificial sweeteners, specifically aspartame and sucralose",
    "sub_claims": [
        {
            "id": "SC1",
            "property": (
                "associated with weight gain and metabolic disease "
                "in human observational studies"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC-association: at least 3 independent peer-reviewed sources must document "
                "a statistically significant positive association between artificial sweetener "
                "consumption and weight gain or metabolic disease markers (obesity, T2D, "
                "cardiovascular disease, metabolic syndrome, impaired glucose tolerance) "
                "in human populations. Observational study designs (cohort, cross-sectional) "
                "are sufficient for SC1."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "causal relationship established via RCTs or equivalent causal "
                "inference methods in humans"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC-causation: the word 'promote' in the claim implies causation, not mere "
                "correlation. At least 3 independent sources must establish a causal (not "
                "merely associational) relationship using RCTs, Mendelian randomization, "
                "Bradford Hill criteria assessment, or equivalent causal inference methods. "
                "Purely observational sources do not satisfy SC2 regardless of sample size. "
                "Mechanistic evidence from animal studies does not satisfy SC2 in the absence "
                "of confirming human RCT or causal inference data."
            ),
        },
    ],
    "compound_operator": "AND",
    "proof_direction": "affirm",
    "operator_note": (
        "Both sub-claims must hold for the compound claim to be PROVED. "
        "SC1 (association) and SC2 (causation) are logically independent: an association "
        "can hold in observational data without establishing causation. The dominant "
        "confound in observational studies is reverse causality — people who are already "
        "overweight or at metabolic risk preferentially choose diet/low-calorie products, "
        "producing a spurious association without any causal mechanism operating from "
        "sweetener to disease. If only SC1 holds, the verdict is PARTIALLY VERIFIED "
        "with the notation that association is documented but causation is not established."
    ),
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "sc1_source_a",
        "label": (
            "Azad et al. 2017 CMAJ — systematic review/meta-analysis finding observational "
            "association between NNS consumption and weight gain plus metabolic outcomes "
            "across 30 cohort studies (405,907 participants)"
        ),
    },
    "B2": {
        "key": "sc1_source_b",
        "label": (
            "Steffen et al. 2023 Int J Obesity (CARDIA Study) — 25-year prospective cohort "
            "(N=3,088), aspartame and saccharin positively associated with adipose tissue "
            "volumes and incident obesity"
        ),
    },
    "B3": {
        "key": "sc1_source_c",
        "label": (
            "Kuk & Brown 2016 APNM — NHANES III cross-sectional study (N=2,856), "
            "aspartame consumption associated with greater obesity-related glucose intolerance"
        ),
    },
    "B4": {
        "key": "sc2_source_a",
        "label": (
            "Suez et al. 2014 Nature — proposed gut-microbiome mechanism for NAS-induced "
            "glucose intolerance (primarily mouse model, limited human data; "
            "insufficient for SC2 causal threshold)"
        ),
    },
    "A1": {"label": "SC1 confirmed source count", "method": None, "result": None},
    "A2": {"label": "SC2 confirmed source count", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — grouped by sub-claim
empirical_facts = {
    # SC1 sources: observational evidence of association
    "sc1_source_a": {
        "quote": (
            "consumption of nonnutritive sweeteners was associated with increases in weight "
            "and waist circumference, and higher incidence of obesity, hypertension, metabolic "
            "syndrome, type 2 diabetes and cardiovascular events"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5515645/",
        "source_name": "Azad et al. 2017, CMAJ — Nonnutritive sweeteners and cardiometabolic health (PMC)",
    },
    "sc1_source_b": {
        "quote": (
            "ArtSw, including diet soda, was associated with greater risks of incident obesity"
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/37443272/",
        "source_name": (
            "Steffen et al. 2023, International Journal of Obesity (CARDIA Study) — "
            "Long-term artificial sweetener intake and adiposity (PubMed)"
        ),
    },
    "sc1_source_c": {
        "quote": (
            "consumption of aspartame is associated with greater obesity-related impairments "
            "in glucose tolerance"
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/27216413/",
        "source_name": (
            "Kuk & Brown 2016, Applied Physiology Nutrition and Metabolism — "
            "Aspartame intake and glucose tolerance in NHANES III (PubMed)"
        ),
    },
    # SC2 source: proposed causal mechanism — insufficient on its own to establish causation in humans
    "sc2_source_a": {
        "quote": (
            "consumption of commonly used NAS formulations drives the development of glucose "
            "intolerance through induction of compositional and functional alterations to the "
            "intestinal microbiota"
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/25231862/",
        "source_name": (
            "Suez et al. 2014, Nature — Artificial sweeteners induce glucose intolerance by "
            "altering the gut microbiota (PubMed)"
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

# 6. PER-SUB-CLAIM EVALUATION — each uses compare()
sc1_holds = compare(
    n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
    label="SC1: association with weight gain and metabolic disease"
)
sc2_holds = compare(
    n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
    label="SC2: causation established via RCTs or causal inference"
)

# 7. COMPOUND EVALUATION
n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# 8. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": (
            "Do RCTs show that artificial sweeteners CAUSE weight gain or metabolic disease?"
        ),
        "verification_performed": (
            "Searched 'artificial sweeteners RCT weight gain randomized controlled trial meta-analysis'. "
            "Reviewed Miller & Perez 2014 (AJCN, 15 RCTs), McGlynn et al. 2022 (JAMA Network Open, "
            "network meta-analysis), Qin et al. 2025 (Frontiers in Nutrition, 9 RCTs, 1,457 participants), "
            "and Toews et al. 2019 (BMJ, pre-specified WHO systematic review)."
        ),
        "finding": (
            "Multiple meta-analyses of RCTs — the gold standard for causal inference — show no weight "
            "gain and no metabolic harm from artificial sweeteners: Miller & Perez 2014 found a modest "
            "weight DECREASE (−0.80 kg; 95% CI: −1.17, −0.43) from low-calorie sweetener use across "
            "15 RCTs; McGlynn et al. 2022 found low/no-calorie sweetened beverages perform comparably "
            "to water when substituted for sugar-sweetened beverages; Qin et al. 2025 found no "
            "statistically significant differences in body weight, waist circumference, fasting blood "
            "glucose, HbA1c, insulin resistance, or blood pressure across 9 RCTs. This is strong "
            "counter-evidence against SC2 (causation) and is why SC2 fails to meet its threshold. "
            "SC1 (observational association) still holds independently."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is the observational association confounded by reverse causality "
            "(overweight/at-risk people choosing diet products)?"
        ),
        "verification_performed": (
            "Searched 'artificial sweeteners reverse causality confounding observational studies'. "
            "Reviewed Azad et al. 2017 CMAJ limitations section, WHO 2023 guideline evidence grade, "
            "and Toews et al. 2019 BMJ on confounding."
        ),
        "finding": (
            "Reverse causality is the dominant competing explanation for all observational associations. "
            "Azad et al. 2017 explicitly acknowledges: 'The cohort results may reflect confounding by "
            "indication, as people who are overweight or at risk of metabolic disease may choose "
            "nonnutritive sweeteners.' The WHO 2023 guideline classifies its recommendation as "
            "'conditional' — the weakest WHO guidance tier — specifically because the evidence is "
            "predominantly observational and subject to this confound. This confirms why SC1 "
            "(association documented) does not imply SC2 (causation established), and is consistent "
            "with the PARTIALLY VERIFIED verdict."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the evidence apply equally to both aspartame AND sucralose as named in the claim?"
        ),
        "verification_performed": (
            "Searched 'sucralose weight gain adiposity evidence' and reviewed Steffen et al. 2023 "
            "(CARDIA) per-sweetener results for sucralose specifically."
        ),
        "finding": (
            "The CARDIA 2023 study found that sucralose showed 'all ptrend > 0.05' — no significant "
            "association with adipose tissue volumes or incident obesity — while aspartame and saccharin "
            "showed significant positive associations. The observational association documented in SC1 "
            "is primarily driven by aspartame and saccharin, not sucralose. The claim names both "
            "aspartame and sucralose, but SC1 as verified is stronger for aspartame than sucralose. "
            "SC2 (causation) is not established for either compound. This weakens the claim's "
            "specificity for sucralose but does not break SC1 overall, which treats the class level "
            "association as confirmed by multiple independent studies."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the WHO 2023 guideline establish that sweeteners CAUSE weight gain?"
        ),
        "verification_performed": (
            "Reviewed the WHO May 2023 news release directly. Checked the evidence grade assigned. "
            "Also reviewed Harvard T.H. Chan School commentary (June 2023) on the WHO evidence review."
        ),
        "finding": (
            "The WHO 2023 guideline recommends against NSS use for weight control but explicitly "
            "classifies this as a 'conditional' — not 'strong' — recommendation due to the "
            "predominantly observational evidence base. The WHO news page states: 'potential "
            "undesirable effects from long-term use of NSS, such as an increased risk of type 2 "
            "diabetes, cardiovascular diseases, and mortality in adults' — which is associational "
            "language, not causal. Harvard experts additionally noted that the WHO meta-analysis "
            "excluded large studies (>100,000 participants) showing beneficial substitution effects. "
            "The guideline does not establish causation and does not contradict the PARTIALLY "
            "VERIFIED verdict."
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

    if any_breaks or uncertainty_override:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        # Mixed: SC1 holds, SC2 does not — partially verified
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

    # Extractions: for qualitative/consensus proofs, each B-type fact records citation status
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
                "description": "SC1: independent sources consulted for association evidence",
                "n_sources_consulted": len(sc1_keys),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in sc1_keys},
                "independence_note": (
                    "Sources are from different research groups, institutions, and study designs: "
                    "Azad 2017 (Canadian meta-analysis), Steffen 2023 (US CARDIA cohort), "
                    "Kuk 2016 (US NHANES cross-sectional). Different populations, methods, "
                    "and outcome measures."
                ),
            },
            {
                "description": "SC2: independent sources consulted for causal evidence",
                "n_sources_consulted": len(sc2_keys),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in sc2_keys},
                "independence_note": (
                    "Only 1 SC2 source was identified (Suez 2014); it proposes a gut-microbiome "
                    "mechanism but is primarily mouse-model data with a small human intervention "
                    "(n=7). No RCTs, Mendelian randomization studies, or Bradford Hill analyses "
                    "establishing causation in human populations were found. RCT meta-analyses "
                    "(Miller 2014, McGlynn 2022, Qin 2025) actively contradict the causal claim."
                ),
            },
        ],
        "sub_claim_results": [
            {
                "id": "SC1",
                "n_confirming": n_sc1,
                "threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"],
                "holds": sc1_holds,
            },
            {
                "id": "SC2",
                "n_confirming": n_sc2,
                "threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"],
                "holds": sc2_holds,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_n_confirming": n_sc1,
            "sc1_threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"],
            "sc1_holds": sc1_holds,
            "sc2_n_confirming": n_sc2,
            "sc2_threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"],
            "sc2_holds": sc2_holds,
            "n_holding": n_holding,
            "n_total": n_total,
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
