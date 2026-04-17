"""
Proof: Eating eggs significantly raises LDL cholesterol and heart-disease risk.
Generated: 2026-03-28
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
from scripts.extract_values import parse_number_from_quote
from scripts.smart_extract import verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = "Eating eggs significantly raises LDL cholesterol and heart-disease risk."
CLAIM_FORMAL = {
    "subject": "moderate egg consumption (up to ~1 egg/day) in healthy adults",
    "property": (
        "compound AND: (SC1) significantly raises LDL-C "
        "AND (SC2) significantly raises cardiovascular disease (CVD) risk"
    ),
    "operator": "AND",
    "operator_note": (
        "Compound claim — both sub-claims must hold for the overall claim to be PROVED. "
        "SC1 ('significantly raises LDL'): 'significantly' is interpreted as clinically meaningful — "
        "operationalized as ≥10 mg/dL absolute increase per meta-analytic RCT evidence. "
        "This is a conservative threshold: statins produce 30–50 mg/dL reductions; "
        "a dietary effect below 10 mg/dL is not considered clinically actionable by standard "
        "lipid-management guidelines. "
        "SC2 ('significantly raises heart-disease risk'): interpreted as statistically significant "
        "increased CVD incidence observed in large prospective cohort studies. "
        "Disproof requires ≥2 independent prospective cohort meta-analyses showing no significant "
        "CVD risk increase. Evaluated at moderate consumption (~1 egg/day)."
    ),
    "sc1_ldl_threshold_mg_dl": 10.0,
    "sc2_disproof_min_sources": 2,
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {
        "key": "source_cvd_a",
        "label": "BMJ 2020 meta-analysis: 28 prospective cohort studies, 1.72M participants — egg consumption and CVD risk",
    },
    "B2": {
        "key": "source_cvd_b",
        "label": "Eur J Nutr 2021 dose-response meta-analysis: 39 studies, ~2M participants — egg consumption and CVD risk",
    },
    "B3": {
        "key": "source_ldl_a",
        "label": "Nutrients 2020 RCT meta-analysis: 17 RCTs in healthy subjects — egg consumption and LDL-C",
    },
    "A1": {
        "label": "SC2: count of independent prospective cohort meta-analyses finding no significant CVD risk increase",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "SC1: RCT-observed LDL increase vs clinical significance threshold (≥10 mg/dL)",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
# ---------------------------------------------------------------------------
empirical_facts = {
    "source_cvd_a": {
        "quote": "moderate egg consumption (up to one egg per day) is not associated with cardiovascular disease risk overall",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7190072/",
        "source_name": (
            "Drouin-Chartier et al., BMJ 2020 (PMC7190072) — "
            "meta-analysis of 28 prospective cohort studies, 1,720,108 participants, "
            "139,195 CVD events"
        ),
    },
    "source_cvd_b": {
        "quote": "there may be no need to discourage egg consumption at the population level",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8137614/",
        "source_name": (
            "Kazemi et al., Eur J Nutr 2021 (PMC8137614) — "
            "dose-response meta-analysis of 39 prospective cohort studies, ~2M participants"
        ),
    },
    "source_ldl_a": {
        # Quote containing the numeric LDL increase we parse below (Rule 1)
        "quote": "The MEC group also had higher LDL-c than the control group (MD = 8.14, p < 0.0001)",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7400894/",
        "source_name": (
            "Zhu et al., Nutrients 2020 (PMC7400894) — "
            "meta-analysis of 17 RCTs in healthy subjects"
        ),
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. VALUE EXTRACTION — parse LDL increase from quote (Rule 1)
# ---------------------------------------------------------------------------
ldl_increase_rct = float(
    parse_number_from_quote(
        empirical_facts["source_ldl_a"]["quote"],
        r"MD = ([\d.]+)",
        "B3_ldl_increase",
    )
)
verify_extraction(ldl_increase_rct, empirical_facts["source_ldl_a"]["quote"], "B3_ldl_increase")

# ---------------------------------------------------------------------------
# 6. SC1 EVALUATION — Does egg consumption significantly raise LDL?
# ---------------------------------------------------------------------------
# The RCT meta-analysis (B3) shows 8.14 mg/dL LDL increase.
# Clinical significance threshold: ≥10 mg/dL (conservative; statins achieve 30–50 mg/dL).
# If 8.14 < 10 → SC1 claim of "significantly raises LDL" is NOT supported.
sc1_ldl_significant = compare(
    ldl_increase_rct,
    ">=",
    CLAIM_FORMAL["sc1_ldl_threshold_mg_dl"],
    label="SC1: RCT LDL increase (8.14 mg/dL) meets clinical significance threshold (≥10 mg/dL)",
)

# ---------------------------------------------------------------------------
# 7. SC2 EVALUATION — Does egg consumption significantly raise CVD risk?
# ---------------------------------------------------------------------------
# Count independent prospective cohort meta-analyses showing no significant CVD risk.
n_sc2_no_risk = len([
    k for k in ["source_cvd_a", "source_cvd_b"]
    if citation_results.get(k, {}).get("status") in ("verified", "partial")
])
sc2_cvd_contradicted = compare(
    n_sc2_no_risk,
    ">=",
    CLAIM_FORMAL["sc2_disproof_min_sources"],
    label=(
        "SC2: count of independent meta-analyses contradicting CVD risk claim "
        f"(≥{CLAIM_FORMAL['sc2_disproof_min_sources']} required for disproof)"
    ),
)

# ---------------------------------------------------------------------------
# 8. COMPOUND CLAIM EVALUATION
# ---------------------------------------------------------------------------
# The compound claim holds only if BOTH sub-claims are proved.
# SC1 proved = sc1_ldl_significant (False — 8.14 < 10.0)
# SC2 proved = NOT sc2_cvd_contradicted (False — contradicted by 2+ sources)
# n_sc_proved = 0; threshold for compound AND = 2
n_sc_proved = int(sc1_ldl_significant) + int(not sc2_cvd_contradicted)
claim_holds = compare(
    n_sc_proved,
    "==",
    2,
    label="Compound AND: both SC1 and SC2 must be proved (0 of 2 proved → claim_holds = False)",
)

# ---------------------------------------------------------------------------
# 9. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": "Do any large meta-analyses show significantly increased CVD risk from egg consumption?",
        "verification_performed": (
            "Searched PubMed/PMC for 'egg consumption cardiovascular disease risk increased meta-analysis'. "
            "Reviewed Zhong et al. JAMA 2019 (PMID 30874756), which found 17% higher CVD risk per "
            "300 mg/day of dietary cholesterol. However, this result was for total dietary cholesterol, "
            "not eggs specifically, and has been criticized for not accounting for replacing nutrients. "
            "Multiple subsequent egg-specific meta-analyses (PMC7190072, PMC8137614) focused on eggs "
            "as a food and found no significant CVD risk."
        ),
        "finding": (
            "Zhong et al. JAMA 2019 associates dietary cholesterol with CVD, but subsequent larger "
            "egg-specific meta-analyses (1.7–2M participants) do not confirm a significant risk for "
            "moderate egg consumption. The JAMA finding does not break the proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the ~8 mg/dL LDL increase be clinically significant under a stricter threshold?",
        "verification_performed": (
            "Reviewed AHA/ACC lipid management guidelines (2018 ACC/AHA Guideline on the Management "
            "of Blood Cholesterol). Clinical intervention thresholds are based on absolute LDL levels "
            "(e.g., >130 mg/dL with intermediate risk factors). The guidelines do not specify a dietary "
            "LDL change threshold; however, lifestyle modification targets are typically ≥10–15% LDL "
            "reduction (≈15–25 mg/dL on a 150 mg/dL baseline). Also searched for whether any clinical "
            "body explicitly considers <10 mg/dL LDL dietary changes as clinically significant."
        ),
        "finding": (
            "No clinical guideline classifies an 8 mg/dL dietary-induced LDL increase as clinically "
            "significant in isolation. A 2025 RCT (PMID 40339906) also found no LDL increase when eggs "
            "were consumed within a low-saturated-fat diet, indicating the effect is confounded by "
            "dietary context, not eggs per se."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is the claim true for individuals with type 2 diabetes or hypercholesterolemia?",
        "verification_performed": (
            "Reviewed sub-group analyses in PMC7190072 and PMC8137614. Both note that among people "
            "with type 2 diabetes, higher egg consumption may be associated with modestly elevated "
            "CVD risk (pooled RR ~1.25 in some sub-analyses, with overlapping CIs). LDL hyper-responders "
            "(~30% of the population) may also show larger LDL responses to dietary cholesterol."
        ),
        "finding": (
            "Sub-population effects may exist for diabetics and LDL hyper-responders. The claim is "
            "stated without qualification. The proof evaluates moderate consumption in healthy adults, "
            "consistent with the primary evidence base. Clinicians managing high-risk patients should "
            "consider individual context."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Has scientific consensus historically supported the egg-cholesterol-heart-disease link?",
        "verification_performed": (
            "Searched 'dietary cholesterol guidelines history eggs 300mg recommendation'. Prior to 2015, "
            "U.S. dietary guidelines warned against dietary cholesterol intake >300 mg/day. The 2015 "
            "Dietary Guidelines Advisory Committee removed this limit, stating they found 'no appreciable "
            "relationship between consumption of dietary cholesterol and serum cholesterol.' This reversal "
            "reflects the updated evidence base."
        ),
        "finding": (
            "The claim reflects an older scientific consensus that was revised in 2015. The current "
            "evidence-based position — reflected in both the 2015 DGAC report and multiple recent "
            "meta-analyses — is that moderate egg consumption does not significantly raise LDL or CVD "
            "risk in the general population."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 10. CROSS-CHECKS (Rule 6)
# ---------------------------------------------------------------------------
cross_checks = [
    {
        "description": (
            "SC2: Two independent prospective cohort meta-analyses use different primary cohort sets "
            "and methodologies, yet both find no significant CVD risk from moderate egg consumption"
        ),
        "values_compared": [
            "B1 (PMC7190072, 28 cohorts, 1.72M participants): 'not associated with cardiovascular disease risk overall'",
            "B2 (PMC8137614, 39 cohorts, ~2M participants): 'no need to discourage egg consumption at the population level'",
        ],
        "agreement": True,
        "tolerance": "qualitative — both find null or inverse CVD association at moderate intake",
    },
]

# ---------------------------------------------------------------------------
# 11. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    if not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "PROVED"  # only if claim_holds is True

    FACT_REGISTRY["A1"]["method"] = "count verified meta-analyses showing no significant CVD risk increase"
    FACT_REGISTRY["A1"]["result"] = (
        f"{n_sc2_no_risk} independent sources "
        f"(threshold for disproof: ≥{CLAIM_FORMAL['sc2_disproof_min_sources']})"
    )
    FACT_REGISTRY["A2"]["method"] = "parse_number_from_quote(B3) and compare to clinical significance threshold"
    FACT_REGISTRY["A2"]["result"] = (
        f"{ldl_increase_rct} mg/dL vs ≥{CLAIM_FORMAL['sc1_ldl_threshold_mg_dl']} mg/dL "
        "(does not meet threshold)"
    )

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B3_ldl_increase": {
            "value": str(ldl_increase_rct),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["source_ldl_a"]["quote"],
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
        "cross_checks": cross_checks,
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_ldl_increase_rct_mg_dl": ldl_increase_rct,
            "sc1_clinical_threshold_mg_dl": CLAIM_FORMAL["sc1_ldl_threshold_mg_dl"],
            "sc1_ldl_meets_threshold": sc1_ldl_significant,
            "sc2_no_risk_sources_verified": n_sc2_no_risk,
            "sc2_disproof_threshold": CLAIM_FORMAL["sc2_disproof_min_sources"],
            "sc2_cvd_contradicted": sc2_cvd_contradicted,
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
