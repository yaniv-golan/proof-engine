"""
Proof: Seed oils (canola, sunflower, soybean, corn oil) are toxic and a primary cause
       of modern chronic inflammation and disease.
Generated: 2026-03-28

Claim decomposition:
  SC1: Seed oils are toxic at normal dietary consumption levels.
  SC2: Seed oils are a primary cause of modern chronic inflammation and disease.

Proof direction: DISPROOF — gather authoritative sources that reject each sub-claim.
  SC1 is disproved if ≥3 independent authoritative sources state seed oils are NOT toxic.
  SC2 is disproved if ≥3 independent authoritative sources show seed oils do NOT drive
      chronic inflammation or disease as a primary cause.
"""
import json
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "Seed oils (canola, sunflower, soybean, corn oil) are toxic and a primary cause "
    "of modern chronic inflammation and disease."
)
CLAIM_FORMAL = {
    "subject": "seed oils (canola, sunflower, soybean, corn oil)",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "seed oils are toxic at normal dietary consumption levels",
            "operator": ">=",
            "threshold": 3,
            "proof_direction": "disprove",
            "operator_note": (
                "SC1 is DISPROVED if ≥3 independent authoritative sources explicitly state "
                "that seed oils are not toxic at normal dietary doses, or that scientific "
                "evidence does not support the 'toxic' characterization. "
                "'Toxic' is interpreted as causing direct cellular or systemic harm at "
                "ordinary dietary consumption levels — not extreme doses or specific industrial "
                "conditions (e.g., high-temperature frying). "
                "Threshold of 3 is conservative: requires multiple independent institutions."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "seed oils are a primary cause of modern chronic inflammation and disease"
            ),
            "operator": ">=",
            "threshold": 3,
            "proof_direction": "disprove",
            "operator_note": (
                "SC2 is DISPROVED if ≥3 independent authoritative sources show that dietary "
                "linoleic acid / n-6 PUFA from seed oils does NOT increase inflammatory markers, "
                "or that epidemiological/clinical evidence does not support seed oils as the "
                "primary driver of chronic disease. "
                "'Primary cause' means the dominant or leading causal factor — stronger than "
                "other well-established risk factors (excess calories, refined carbohydrates, "
                "smoking, physical inactivity, saturated fat). "
                "Threshold of 3 is conservative: requires multiple independent institutions."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "Both sub-claims must be disproved (each meeting its threshold) for the compound "
        "claim to receive verdict DISPROVED. "
        "If only one sub-claim is disproved, the verdict is PARTIALLY VERIFIED. "
        "The burden on the disproof is ≥3 independent authoritative sources rejecting each "
        "component claim."
    ),
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {
        "key": "sc1_source_a",
        "label": "SC1: Harvard T.H. Chan School of Public Health — scientists debunk seed oil 'toxic' claims",
    },
    "B2": {
        "key": "sc1_source_b",
        "label": "SC1: Stanford Medicine (Gardner) — omega-6s are not pro-inflammatory",
    },
    "B3": {
        "key": "sc1_source_c",
        "label": "SC1: PMC 11600290 (2024) — clinical trials: n-6 PUFA does not increase inflammation/oxidative stress",
    },
    "B4": {
        "key": "sc2_source_a",
        "label": "SC2: PMC 6179509 (Innes & Calder 2018) — RCT/obs. review: virtually no data support LA–inflammation hypothesis",
    },
    "B5": {
        "key": "sc2_source_b",
        "label": "SC2: ScienceDaily 2025 — 1,900-person study: linoleic acid linked to LOWER inflammation biomarkers",
    },
    "B6": {
        "key": "sc2_source_c",
        "label": "SC2: PMC 11600290 (2024) — higher PUFA intake associated with lower risk of CVD and type 2 diabetes",
    },
    "A1": {
        "label": "SC1: count of verified sources rejecting 'toxic' claim",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "SC2: count of verified sources rejecting 'primary cause of inflammation/disease' claim",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
# Sources that REJECT the compound claim's sub-claims (proof_direction = "disprove").
# Adversarial sources (those that support the original claim) are in adversarial_checks.
# ---------------------------------------------------------------------------
empirical_facts = {
    # --- SC1: Seed oils are NOT toxic ---
    "sc1_source_a": {
        "quote": (
            "While the internet may be full of posts stating that seed oils such as "
            "canola and soy are 'toxic,' scientific evidence does not support these claims."
        ),
        "url": "https://hsph.harvard.edu/news/scientists-debunk-seed-oil-health-risks/",
        "source_name": "Harvard T.H. Chan School of Public Health (2024)",
    },
    "sc1_source_b": {
        "quote": (
            "But somehow, this has been flipped into saying the omega-6s are "
            "pro-inflammatory. That isn't the case."
        ),
        "url": "https://med.stanford.edu/news/insights/2025/03/5-things-to-know-about-the-effects-of-seed-oils-on-health.html",
        "source_name": (
            "Stanford Medicine — Christopher Gardner, PhD, director of nutrition studies "
            "at Stanford Prevention Research Center (2025)"
        ),
    },
    "sc1_source_c": {
        "quote": (
            "Clinical trials show that increased n-6 PUFA (linoleic acid) intake does "
            "not increase markers of inflammation or oxidative stress."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11600290/",
        "source_name": (
            "PMC 11600290 — Perspective on the health effects of unsaturated fatty acids "
            "and commonly consumed plant oils high in unsaturated fat (2024)"
        ),
    },
    # --- SC2: Seed oils are NOT a primary cause of chronic inflammation/disease ---
    "sc2_source_a": {
        "quote": (
            "Based on the current evidence from RCT and observational studies there "
            "appears to be virtually no data available to support the hypothesis that "
            "LA in the diet increases markers of inflammation among healthy, non-infant humans."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6179509/",
        "source_name": (
            "PMC 6179509 — Linoleic Acid, Vegetable Oils & Inflammation "
            "(Innes & Calder, Prostaglandins Leukotrienes Essential Fatty Acids, 2018)"
        ),
    },
    "sc2_source_b": {
        "quote": (
            "higher linoleic acid in blood plasma was associated with lower levels of "
            "biomarkers of cardiometabolic risk, including those related to inflammation."
        ),
        "url": "https://www.sciencedaily.com/releases/2025/06/250621103446.htm",
        "source_name": (
            "ScienceDaily — Myth-busting study: seed oils reduce inflammation, "
            "based on ~1,900-person dataset (June 2025)"
        ),
    },
    "sc2_source_c": {
        "quote": (
            "Epidemiological evidence indicates that higher PUFA intake is associated "
            "with lower risk of incident CVD and type 2 diabetes mellitus (T2DM)."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11600290/",
        "source_name": (
            "PMC 11600290 — Perspective on the health effects of unsaturated fatty acids "
            "and commonly consumed plant oils high in unsaturated fat (2024)"
        ),
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
print("Verifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]

n_sc1 = sum(
    1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES
)
n_sc2 = sum(
    1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES
)

print(f"  SC1 confirmed sources: {n_sc1} / {len(sc1_keys)}")
print(f"  SC2 confirmed sources: {n_sc2} / {len(sc2_keys)}")

# ---------------------------------------------------------------------------
# 6. PER-SUB-CLAIM EVALUATION
# ---------------------------------------------------------------------------
sc1_holds = compare(
    n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
    label="SC1 disproof: verified sources rejecting 'seed oils are toxic'"
)
sc2_holds = compare(
    n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
    label="SC2 disproof: verified sources rejecting 'seed oils are primary cause of inflammation/disease'"
)

# ---------------------------------------------------------------------------
# 7. COMPOUND EVALUATION
# ---------------------------------------------------------------------------
n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(
    n_holding, "==", n_total,
    label="compound disproof: all sub-claims meet disproof threshold"
)

# ---------------------------------------------------------------------------
# 8. ADVERSARIAL CHECKS (Rule 5)
# These document evidence that SUPPORTS the original claim (the opposite of our disproof).
# They were gathered in Step 2 before writing this proof.
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Does the oxidized linoleic acid (OXLAM) hypothesis provide scientific support "
            "for seed oils causing cardiovascular disease?"
        ),
        "verification_performed": (
            "Searched PMC for 'oxidized linoleic acid hypothesis Ramsden'; found PMC6196963 "
            "(DiNicolantonio & O'Keefe, 2018) which proposes that oxidized LA metabolites "
            "promote atherosclerosis. Ramsden et al. also re-analyzed the Sydney Diet Heart "
            "Study (2013) finding increased mortality when saturated fat was replaced with LA. "
            "Reviewed the strength of this hypothesis against the broader literature."
        ),
        "finding": (
            "The OXLAM hypothesis is a minority scientific position, not the consensus. "
            "The Sydney Diet Heart re-analysis used partially recovered data from a single "
            "1960s trial with methodological limitations. The hypothesis has not been confirmed "
            "in large modern RCTs. Importantly, even proponents of this hypothesis (Ramsden et al.) "
            "do not use the word 'toxic' and do not claim seed oils are the 'primary cause' of "
            "chronic disease — they propose a specific mechanistic pathway for one disease outcome "
            "(CHD), which is far narrower than the original claim. This adversarial evidence does "
            "not break the disproof: the OXLAM hypothesis is contested and does not rise to "
            "scientific consensus."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do high-temperature cooking with seed oils produce harmful compounds (aldehydes) "
            "that could justify calling them 'toxic'?"
        ),
        "verification_performed": (
            "Searched for 'seed oil high heat aldehydes toxic cooking PUFAs'; found evidence "
            "that polyunsaturated fats can produce 4-HNE and other aldehydes at very high "
            "temperatures (smoke point or above, deep frying). This is a documented concern "
            "in food chemistry."
        ),
        "finding": (
            "High-heat degradation of PUFAs is a real but narrow concern. It does not support "
            "the original claim's framing that seed oils are broadly 'toxic' or a 'primary cause' "
            "of chronic disease. The claim does not specify high-heat cooking; it characterizes "
            "the oils themselves as toxic. Evidence-based guidance addresses this by recommending "
            "appropriate cooking temperatures, not avoiding seed oils entirely. This adversarial "
            "evidence is too narrow to rescue SC1 or SC2 as stated."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there an RCT showing that replacing seed oils in the diet improves inflammation "
            "or chronic disease outcomes, which would support the original claim?"
        ),
        "verification_performed": (
            "Searched for 'seed oil elimination diet RCT inflammation improvement'; reviewed "
            "recent dietary intervention literature. Found no large RCT demonstrating that "
            "eliminating seed oils specifically reduces inflammatory markers or chronic disease "
            "incidence in otherwise healthy populations. The PREDIMED trial (Mediterranean diet) "
            "and similar studies use olive oil but do not isolate seed oil elimination as the "
            "causal variable."
        ),
        "finding": (
            "No large, well-designed RCT demonstrates that eliminating seed oils specifically "
            "reduces inflammation or chronic disease. Absence of such evidence, combined with "
            "multiple RCTs showing no harmful effects from seed oil consumption, further "
            "undermines SC2. Does not break the disproof."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 9. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # "partial" counts toward threshold but is not fully verified.
    # Only "verified" is clean for the verdict qualifier.
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    # Determine proof direction
    is_disproof = all(
        sc.get("proof_direction") == "disprove"
        for sc in CLAIM_FORMAL["sub_claims"]
    )

    if any_breaks:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        # Mixed: at least one sub-claim disproved, others not
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "DISPROVED" if is_disproof else "PROVED"
    elif claim_holds and any_unverified:
        verdict = (
            "DISPROVED (with unverified citations)"
            if is_disproof
            else "PROVED (with unverified citations)"
        )
    else:
        # No sub-claims met threshold
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified sc1 citations) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1)
    FACT_REGISTRY["A2"]["method"] = f"count(verified sc2 citations) = {n_sc2}"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: each B-type fact records citation status
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
                "description": "SC1: independent sources rejecting 'seed oils are toxic'",
                "n_sources_consulted": len(sc1_keys),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in sc1_keys},
                "independence_note": (
                    "Sources are from different institutions: Harvard T.H. Chan School of "
                    "Public Health, Stanford Prevention Research Center, and a peer-reviewed "
                    "journal review (PMC 11600290)."
                ),
            },
            {
                "description": "SC2: independent sources rejecting 'seed oils are primary cause of inflammation/disease'",
                "n_sources_consulted": len(sc2_keys),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in sc2_keys},
                "independence_note": (
                    "Sources are from different publications: a 2018 systematic review of "
                    "RCTs and observational studies (PMC 6179509), a 2025 population-based "
                    "study (ScienceDaily), and a 2024 perspective paper (PMC 11600290). "
                    "Note: PMC 11600290 appears in both SC1 and SC2 with different quotes "
                    "addressing different aspects — it is one independent source that covers "
                    "both sub-claims."
                ),
            },
        ],
        "sub_claim_results": [
            {
                "id": "SC1",
                "property": CLAIM_FORMAL["sub_claims"][0]["property"],
                "proof_direction": "disprove",
                "n_confirming": n_sc1,
                "threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"],
                "holds": sc1_holds,
            },
            {
                "id": "SC2",
                "property": CLAIM_FORMAL["sub_claims"][1]["property"],
                "proof_direction": "disprove",
                "n_confirming": n_sc2,
                "threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"],
                "holds": sc2_holds,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_sc1_confirmed": n_sc1,
            "n_sc2_confirmed": n_sc2,
            "n_holding": n_holding,
            "n_total": n_total,
            "claim_holds": claim_holds,
            "sc1_holds": sc1_holds,
            "sc2_holds": sc2_holds,
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
