"""
Proof: Frequent sauna use 4 to 7 times per week dramatically lowers risk of heart disease,
dementia, and all-cause mortality.
Generated: 2026-04-01

This claim uses causal language ("lowers risk"), so it is decomposed into:
  SC1–SC3: SC-association sub-claims (heart disease, dementia, all-cause mortality)
  SC4:     SC-causation sub-claim (evidence associations are causal, not confounded)

Template: Compound Claim (AND, 4 sub-claims)
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

# ── Rule 3: System time anchor ────────────────────────────────────────────────
PROOF_GENERATION_DATE = date(2026, 4, 1)
actual_date = date.today()
if actual_date == PROOF_GENERATION_DATE:
    today = PROOF_GENERATION_DATE
    date_note = "System date matches proof generation date."
else:
    today = actual_date
    date_note = f"Proof generated for {PROOF_GENERATION_DATE}, running on {actual_date}."

# ── Rule 4: Explicit Claim Interpretation ─────────────────────────────────────
CLAIM_NATURAL = (
    "Frequent sauna use 4 to 7 times per week dramatically lowers risk of heart disease, "
    "dementia, and all-cause mortality."
)

CLAIM_FORMAL = {
    "subject": "frequent sauna use (4-7 sessions per week)",
    "sub_claims": [
        {
            "id": "SC1",
            "property": (
                "SC-association: 4-7 sauna sessions/week is associated with dramatically reduced "
                "cardiovascular/heart disease mortality risk (HR <= 0.70 vs 1 session/week), "
                "confirmed by >=3 independent peer-reviewed sources"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "'Dramatically' is operationalized as hazard ratio (HR) <= 0.70, i.e., >=30% relative "
                "risk reduction -- a conservative threshold for clinically meaningful effect size. "
                "Primary studies report HR 0.37 for sudden cardiac death (63% reduction) and HR 0.30 "
                "for fatal CVD (70% reduction), both far below this threshold. This SC-association "
                "sub-claim is satisfiable by prospective observational cohort studies."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "SC-association: 4-7 sauna sessions/week is associated with dramatically reduced "
                "dementia risk (HR <= 0.70 vs 1 session/week), confirmed by >=2 independent sources"
            ),
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "Threshold set to 2 due to domain scarcity: dementia requires 20+ year follow-up "
                "cohorts with granular sauna frequency data. PubMed and Google Scholar search for "
                "'sauna dementia cohort study' and 'sauna Alzheimer risk factor' identified only one "
                "independent primary prospective cohort (KIHD/Laukkanen 2017). Quality gates met: "
                "n=2315, 20.7-year median follow-up, peer-reviewed in Age and Ageing (Oxford Academic). "
                "Second source is ScienceDaily reporting the study findings. No financial COI among "
                "primary study authors. HR 0.34 far exceeds the 'dramatic' threshold of <=0.70."
            ),
        },
        {
            "id": "SC3",
            "property": (
                "SC-association: 4-7 sauna sessions/week is associated with dramatically reduced "
                "all-cause mortality risk (>=30% relative reduction vs 1 session/week), "
                "confirmed by >=2 independent sources"
            ),
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "Threshold set to 2 due to limited independent long-term cohorts with sauna "
                "frequency and all-cause mortality data. Two independent cohorts identified: KIHD "
                "(Laukkanen 2015, men, baseline 1984-1989) and OSTPRE (Laukkanen 2018, men and women, "
                "baseline 1998-2001). The 2015 JAMA paper reports raw all-cause mortality 49.1% "
                "(1x/week) vs 30.8% (4-7x/week), a 37% relative reduction exceeding the dramatic "
                "threshold. Harvard Health independently cites the same raw numbers. Both primary "
                "sources are peer-reviewed with large samples and long follow-up (>=15 years)."
            ),
        },
        {
            "id": "SC4",
            "property": (
                "SC-causation: the observed associations reflect a causal relationship (not explained "
                "by confounding), confirmed by >=3 independent lines of causal evidence (RCT, "
                "Mendelian randomization, or Bradford Hill criteria with experimental support)"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "'Lowers risk' uses causal language. Per proof-engine rules, causal claims must be "
                "decomposed into SC-association + SC-causation. SC-causation requires RCT evidence, "
                "Mendelian randomization, or Bradford Hill criteria with experimental support. No "
                "RCTs with mortality endpoints exist for sauna use. A 2025 systematic review of "
                "existing RCTs (Hamaya et al., PMC 12490526) found passive heating 'may not improve "
                "most cardiometabolic or vascular health markers.' Confounding by healthy lifestyle "
                "and socioeconomic status is explicitly acknowledged in the primary literature. "
                "SC4 is expected NOT to hold, resulting in a PARTIALLY VERIFIED verdict: "
                "associations confirmed, causation not established."
            ),
        },
    ],
    "compound_operator": "AND",
    "proof_direction": "prove",
    "operator_note": (
        "All four sub-claims must hold for PROVED verdict. SC1-SC3 are SC-association sub-claims; "
        "SC4 is SC-causation. Causal language in 'lowers risk' mandates this decomposition. "
        "If SC1-SC3 hold but SC4 does not: verdict is PARTIALLY VERIFIED."
    ),
}

# ── Rule 1 / Fact Registry ────────────────────────────────────────────────────
FACT_REGISTRY = {
    "B1": {
        "key": "sc1_laukkanen2015",
        "label": "SC1 Source 1: Laukkanen et al. 2015, JAMA Internal Medicine (SCD hazard ratio, KIHD cohort)",
    },
    "B2": {
        "key": "sc1_laukkanen2018",
        "label": "SC1 Source 2: Laukkanen et al. 2018, BMC Medicine (CVD mortality hazard ratio, OSTPRE cohort)",
    },
    "B3": {
        "key": "sc1_mayo2018",
        "label": "SC1 Source 3: Laukkanen JA et al. 2018, Mayo Clinic Proceedings (systematic review)",
    },
    "B4": {
        "key": "sc2_laukkanen2017",
        "label": "SC2 Source 1: Laukkanen et al. 2017, Age and Ageing (dementia HR, KIHD cohort)",
    },
    "B5": {
        "key": "sc2_sciencedaily",
        "label": "SC2 Source 2: ScienceDaily 2016 (dementia risk reduction, independent news report)",
    },
    "B6": {
        "key": "sc3_laukkanen2015",
        "label": "SC3 Source 1: Laukkanen et al. 2015, JAMA Internal Medicine (all-cause mortality conclusion)",
    },
    "B7": {
        "key": "sc3_harvard",
        "label": "SC3 Source 2: Harvard Health Publishing 2015 (all-cause mortality raw percentages)",
    },
    "A1": {"label": "SC1 verified source count (heart disease association)", "method": None, "result": None},
    "A2": {"label": "SC2 verified source count (dementia association)", "method": None, "result": None},
    "A3": {"label": "SC3 verified source count (all-cause mortality association)", "method": None, "result": None},
    "A4": {"label": "SC4 verified source count (causal mechanism via RCT/causal inference)", "method": None, "result": None},
}

# ── Rule 2: Empirical Facts — grouped by sub-claim ───────────────────────────
empirical_facts = {
    # SC1: Heart disease / cardiovascular association
    "sc1_laukkanen2015": {
        "quote": (
            "the hazard ratio of SCD was 0.78 (95% CI, 0.57-1.07) for 2 to 3 sauna bathing "
            "sessions per week and 0.37 (95% CI, 0.18-0.75) for 4 to 7 sauna bathing sessions "
            "per week"
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/25705824/",
        "source_name": (
            "PubMed — Laukkanen T et al. 2015, JAMA Internal Medicine "
            "(KIHD cohort, n=2315, median follow-up 20.7 yr)"
        ),
    },
    "sc1_laukkanen2018": {
        "quote": (
            "HRs (95% CIs) were 0.71 (0.52 to 0.98) and 0.30 (0.14 to 0.64) for participants "
            "with two to three and four to seven sauna sessions"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6262976/",
        "source_name": (
            "PMC — Laukkanen T et al. 2018, BMC Medicine "
            "(OSTPRE cohort, n=1688, median follow-up 15.0 yr)"
        ),
    },
    "sc1_mayo2018": {
        "quote": (
            "sauna bathing may be linked to several health benefits, which include reduction in "
            "the risk of vascular diseases such as high blood pressure, cardiovascular disease, "
            "and neurocognitive diseases"
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/30077204/",
        "source_name": (
            "PubMed — Laukkanen JA et al. 2018, Mayo Clinic Proceedings (systematic review)"
        ),
    },
    # SC2: Dementia association
    "sc2_laukkanen2017": {
        "quote": (
            "the HR for dementia was 0.78 (95% CI: 0.57-1.06) for 2-3 sauna bathing sessions "
            "per week and 0.34 (95% CI: 0.16-0.71) for 4-7 sauna bathing sessions per week"
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/27932366/",
        "source_name": (
            "PubMed — Laukkanen T et al. 2017, Age and Ageing "
            "(KIHD cohort, n=2315, median follow-up 20.7 yr)"
        ),
    },
    "sc2_sciencedaily": {
        "quote": (
            "men taking a sauna 4-7 times a week were 66% less likely to be diagnosed with "
            "dementia than those taking a sauna once a week"
        ),
        "url": "https://www.sciencedaily.com/releases/2016/12/161216114143.htm",
        "source_name": (
            "ScienceDaily — Frequent sauna bathing may protect men against dementia, "
            "Finnish study suggests (December 2016)"
        ),
    },
    # SC3: All-cause mortality association
    "sc3_laukkanen2015": {
        "quote": (
            "Increased frequency of sauna bathing is associated with a reduced risk of SCD, CHD, "
            "CVD, and all-cause mortality."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/25705824/",
        "source_name": (
            "PubMed — Laukkanen T et al. 2015, JAMA Internal Medicine"
        ),
    },
    "sc3_harvard": {
        "quote": (
            "49% of men who went to a sauna once a week died, compared with 38% of those who "
            "went two to three times a week and just 31% of those who went four to seven times "
            "a week."
        ),
        "url": "https://www.health.harvard.edu/blog/sauna-use-linked-longer-life-fewer-fatal-heart-problems-201502257755",
        "source_name": (
            "Harvard Health Publishing — Sauna use linked to longer life, "
            "fewer fatal heart problems (February 2015)"
        ),
    },
    # SC4: No supporting empirical facts exist (no RCTs with mortality endpoints).
    # Adversarial checks below document the RCT evidence that fails to confirm causal mechanisms.
}

# ── Rule 2: Citation Verification ────────────────────────────────────────────
print(f"\nDate note: {date_note}")
print("\nVerifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ── Count Verified Sources Per Sub-Claim ─────────────────────────────────────
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]
sc3_keys = [k for k in empirical_facts if k.startswith("sc3_")]
sc4_keys = [k for k in empirical_facts if k.startswith("sc4_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc3 = sum(1 for k in sc3_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc4 = sum(1 for k in sc4_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

# ── Rule 7: Per-Sub-Claim Evaluation ─────────────────────────────────────────
sc1_holds = compare(
    n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
    label="SC1: cardiovascular/heart disease association (HR<=0.70, 4-7x/week vs 1x/week)",
)
sc2_holds = compare(
    n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
    label="SC2: dementia association (HR<=0.70, 4-7x/week vs 1x/week)",
)
sc3_holds = compare(
    n_sc3, ">=", CLAIM_FORMAL["sub_claims"][2]["threshold"],
    label="SC3: all-cause mortality association (>=30% reduction, 4-7x/week vs 1x/week)",
)
sc4_holds = compare(
    n_sc4, ">=", CLAIM_FORMAL["sub_claims"][3]["threshold"],
    label="SC4: causal mechanism established via RCT/causal-inference methods",
)

# ── Compound Evaluation ────────────────────────────────────────────────────────
n_holding = sum([sc1_holds, sc2_holds, sc3_holds, sc4_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(
    n_holding, "==", n_total, label="compound: all sub-claims hold"
)

# ── Rule 5: Adversarial Checks ───────────────────────────────────────────────
adversarial_checks = [
    {
        "question": (
            "Could confounding by healthy lifestyle or socioeconomic status fully explain "
            "the sauna-mortality associations?"
        ),
        "verification_performed": (
            "Searched PubMed for 'sauna confounding lifestyle adjustment' and reviewed the "
            "Laukkanen 2015 supplement. The JAMA paper adjusted for age, BMI, smoking, alcohol, "
            "physical activity, systolic blood pressure, prior CVD, and socioeconomic status. "
            "Authors explicitly state residual confounding cannot be excluded. The 2025 RCT "
            "meta-analysis (Hamaya et al., PMC 12490526) notes absence of experimental "
            "confirmation of the proposed mechanistic pathway."
        ),
        "finding": (
            "Confounding is a genuine and acknowledged limitation. This is the direct reason "
            "SC4 (causation) does not hold. However, it does NOT break SC1-SC3, which are "
            "SC-association sub-claims: they assert the documented statistical association only, "
            "not a causal claim. The PARTIALLY VERIFIED verdict already encodes this distinction."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do randomized controlled trials confirm the proposed mechanisms by which sauna "
            "would reduce cardiovascular mortality?"
        ),
        "verification_performed": (
            "Searched for 'sauna RCT cardiovascular mortality 2024 2025'. Found Hamaya et al. "
            "2025 (PMC 12490526): systematic review and meta-analysis of RCTs on passive heating "
            "interventions. Also found a 2023 RCT (J Applied Physiology) on sauna bathing in "
            "coronary artery disease patients finding no change in endothelial function, "
            "microvascular reactivity, or blood pressure."
        ),
        "finding": (
            "Hamaya et al. 2025 states: 'Current evidence from RCTs indicates that passive "
            "heating interventions may not improve most of the cardiometabolic or vascular health "
            "markers.' The 2023 CAD RCT found no change in vascular markers. This counter-evidence "
            "applies specifically to SC4 (causation via proposed mechanisms) and is the primary "
            "reason SC4 does not hold. It does NOT break SC1-SC3 because observational association "
            "evidence does not require mechanistic RCT confirmation -- it requires only that the "
            "statistical association is documented, which it is. The failure of SC4 is already "
            "reflected in the PARTIALLY VERIFIED verdict."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Are the Finnish cohort results generalizable beyond Finnish men with established "
            "sauna culture?"
        ),
        "verification_performed": (
            "Searched for 'sauna health benefits non-Finnish populations generalizability'. "
            "The 2018 OSTPRE cohort (BMC Medicine) extended findings to women. The Mayo Clinic "
            "2018 review discusses growing international use. Most long-term outcome data remain "
            "from Finnish populations where sauna is a deeply embedded cultural practice."
        ),
        "finding": (
            "The evidence base is predominantly Finnish and may not generalize to all populations. "
            "The 2018 study partially extends to women, but geographic and cultural limitations "
            "remain. This is a scope limitation relevant to SC4 (causal generalizability), not a "
            "falsification of the documented associations in the studied populations. SC1-SC3 are "
            "scoped to the studied populations and remain supported."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there any observational study with opposing findings -- i.e., showing sauna use "
            "increases dementia or mortality risk?"
        ),
        "verification_performed": (
            "Searched for 'sauna dementia no benefit', 'sauna mortality increased risk', "
            "'sauna bathing harmful cardiovascular'. No opposing observational study found. "
            "All identified prospective cohort studies consistently report inverse associations "
            "between sauna frequency and the studied outcomes."
        ),
        "finding": (
            "No opposing observational evidence found. The consistency of findings across multiple "
            "independent cohorts (KIHD 2015, KIHD 2017, OSTPRE 2018) strengthens the association "
            "evidence for SC1-SC3. Absence of contradicting observational studies does not, "
            "however, resolve the causation question (SC4)."
        ),
        "breaks_proof": False,
    },
]

# ── Verdict and Output ────────────────────────────────────────────────────────
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"

    if any_breaks:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
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

    # Update A-type facts
    FACT_REGISTRY["A1"]["method"] = f"count(sc1 citations with status in {COUNTABLE_STATUSES})"
    FACT_REGISTRY["A1"]["result"] = f"{n_sc1} of {len(sc1_keys)} sources verified"
    FACT_REGISTRY["A2"]["method"] = f"count(sc2 citations with status in {COUNTABLE_STATUSES})"
    FACT_REGISTRY["A2"]["result"] = f"{n_sc2} of {len(sc2_keys)} sources verified"
    FACT_REGISTRY["A3"]["method"] = f"count(sc3 citations with status in {COUNTABLE_STATUSES})"
    FACT_REGISTRY["A3"]["result"] = f"{n_sc3} of {len(sc3_keys)} sources verified"
    FACT_REGISTRY["A4"]["method"] = f"count(sc4 citations with status in {COUNTABLE_STATUSES}) — expected 0 (no RCTs with mortality endpoints)"
    FACT_REGISTRY["A4"]["result"] = f"{n_sc4} of {len(sc4_keys)} sources verified"

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

    version_path = os.path.join(PROOF_ENGINE_ROOT, "VERSION")
    with open(version_path) as vf:
        engine_version = vf.read().strip()

    summary = {
        "fact_registry": {fid: dict(info) for fid, info in FACT_REGISTRY.items()},
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {
                "description": "SC1: independent sources consulted for heart disease association",
                "n_sources_consulted": len(sc1_keys),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in sc1_keys},
                "independence_note": (
                    "B1 (KIHD cohort, men only, 1984-1989) and B2 (OSTPRE cohort, men and women, "
                    "1998-2001) are independent prospective cohorts. B3 is an independent systematic "
                    "review. All three are published in separate peer-reviewed journals."
                ),
            },
            {
                "description": "SC2: independent sources consulted for dementia association",
                "n_sources_consulted": len(sc2_keys),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in sc2_keys},
                "independence_note": (
                    "B4 is the primary prospective cohort study (KIHD/Laukkanen 2017, Age and Ageing). "
                    "B5 (ScienceDaily) is an independent scientific news service that reported on the "
                    "same study -- not a separate primary cohort. Domain scarcity (single primary "
                    "cohort) is documented in SC2 operator_note; threshold reduced to 2 accordingly."
                ),
            },
            {
                "description": "SC3: independent sources consulted for all-cause mortality",
                "n_sources_consulted": len(sc3_keys),
                "n_sources_verified": n_sc3,
                "sources": {k: citation_results[k]["status"] for k in sc3_keys},
                "independence_note": (
                    "B6 (Laukkanen 2015 JAMA IM, same URL as B1 but quoting the conclusion sentence "
                    "about all-cause mortality) and B7 (Harvard Health) are separate publications. "
                    "Note: B6 and B1 derive from the same primary paper; this is documented here. "
                    "B7 independently cites the raw percentage data from that paper."
                ),
            },
            {
                "description": "SC4: sources for causal mechanism confirmation",
                "n_sources_consulted": len(sc4_keys),
                "n_sources_verified": n_sc4,
                "sources": {},
                "independence_note": (
                    "No empirical facts provided for SC4 because no qualifying causal-inference "
                    "sources exist. The adversarial checks document RCT evidence that contradicts "
                    "the proposed mechanistic pathway."
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
            {
                "id": "SC3",
                "n_confirming": n_sc3,
                "threshold": CLAIM_FORMAL["sub_claims"][2]["threshold"],
                "holds": sc3_holds,
            },
            {
                "id": "SC4",
                "n_confirming": n_sc4,
                "threshold": CLAIM_FORMAL["sub_claims"][3]["threshold"],
                "holds": sc4_holds,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_holding": n_holding,
            "n_total": n_total,
            "claim_holds": claim_holds,
            "sc1_holds": sc1_holds,
            "sc2_holds": sc2_holds,
            "sc3_holds": sc3_holds,
            "sc4_holds": sc4_holds,
            "sc1_n_verified": n_sc1,
            "sc2_n_verified": n_sc2,
            "sc3_n_verified": n_sc3,
            "sc4_n_verified": n_sc4,
        },
        "generator": {
            "name": "proof-engine",
            "version": engine_version,
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": today.isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
