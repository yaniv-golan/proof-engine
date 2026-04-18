"""
Proof: Alkaline water or alkaline diets meaningfully improve health by counteracting body acidity
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
    "Alkaline water or alkaline diets meaningfully improve health by counteracting body acidity"
)
CLAIM_FORMAL = {
    "subject": "Alkaline water and alkaline diets",
    "sub_claims": [
        {
            "id": "SC1",
            "property": (
                "counteracts body acidity by producing a meaningful, sustained change in blood pH"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC1 tests the mechanistic premise of the claim: that alkaline water or alkaline "
                "diets can alter blood pH in a clinically meaningful way. To DISPROVE SC1, we "
                "count authoritative sources (major medical institutions, peer-reviewed reviews) "
                "that confirm blood pH is tightly regulated by the kidneys and lungs and is NOT "
                "meaningfully altered by diet or alkaline water consumption in healthy individuals. "
                "A threshold of 3 requires institutional consensus across independent sources."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "produces meaningful health improvements beyond those attributable to diet quality alone"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC2 tests the health outcome claim. To DISPROVE SC2, we count authoritative "
                "sources (systematic reviews, major cancer and medical centers) finding no "
                "significant health benefits from alkaline water or alkaline diets beyond what is "
                "explained by general diet quality (e.g., increased fruit and vegetable intake). "
                "A threshold of 3 requires multi-source convergent rejection of the health claim."
            ),
        },
    ],
    "compound_operator": "AND",
    "proof_direction": "disprove",
    "operator_note": (
        "The claim uses OR to name two interventions (alkaline water, alkaline diets), both claimed "
        "to work through the same mechanism ('counteracting body acidity'). Disproving an OR claim "
        "requires showing that NEITHER intervention achieves the stated mechanism (SC1) nor produces "
        "meaningful health improvements (SC2). The compound claim is DISPROVED when both sub-claims "
        "individually meet their disproof thresholds."
    ),
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "sc1_source_a", "label": "SC1: Harvard Health — alkaline water cannot durably change blood pH"},
    "B2": {"key": "sc1_source_b", "label": "SC1: MD Anderson Cancer Center — dietary changes don't affect blood pH"},
    "B3": {"key": "sc1_source_c", "label": "SC1: PMC/Schwalfenberg 2011 — body maintains steady blood pH via renal and respiratory mechanisms"},
    "B4": {"key": "sc2_source_a", "label": "SC2: De Gruyter systematic review 2023 — no additional health effects of alkaline water vs mineral water"},
    "B5": {"key": "sc2_source_b", "label": "SC2: British Journal of Nutrition / Fenton & Huang 2016 — alkaline promotion not justified for cancer"},
    "B6": {"key": "sc2_source_c", "label": "SC2: PMC/Schwalfenberg 2011 — no substantial evidence alkaline diet improves bone health"},
    "A1": {"label": "SC1 verified disproof source count", "method": None, "result": None},
    "A2": {"label": "SC2 verified disproof source count", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS
# SC1 disproof sources: authoritative institutions confirming blood pH is NOT changed by
#   diet or alkaline water in healthy individuals.
# SC2 disproof sources: systematic reviews and major medical centers finding no meaningful
#   health benefits from alkaline water/diet.
# IMPORTANT: adversarial sources (studies with limited positive findings) go in
#   adversarial_checks, NOT here.
empirical_facts = {
    "sc1_source_a": {
        "quote": (
            "Even if you drank enough alkaline water to slightly raise the pH of your blood, "
            "your kidneys would quickly go into action to rebalance your blood pH."
        ),
        "url": "https://www.health.harvard.edu/staying-healthy/is-alkaline-water-better",
        "source_name": "Harvard Health Publishing",
    },
    "sc1_source_b": {
        "quote": "dietary changes will not impact the pH level of your blood",
        "url": "https://www.mdanderson.org/cancerwise/alkaline-diet--what-cancer-patients-should-know.h00-159223356.html",
        "source_name": "MD Anderson Cancer Center",
    },
    "sc1_source_c": {
        "quote": (
            "The human body has an amazing ability to maintain a steady pH in the blood "
            "with the main compensatory mechanisms being renal and respiratory."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3195546/",
        "source_name": "PMC — Schwalfenberg 2011, The Alkaline Diet, Journal of Environmental and Public Health",
    },
    "sc2_source_a": {
        "quote": (
            "Recent evidences do not prove any additional health effects of alkaline, oxygenated, "
            "or demineralized water compared to mineral water."
        ),
        "url": "https://www.degruyterbrill.com/document/doi/10.1515/reveh-2022-0057/html?lang=en",
        "source_name": "De Gruyter — systematic review, Reviews on Environmental Health 2023",
    },
    "sc2_source_b": {
        "quote": (
            "Promotion of alkaline diet and alkaline water to the public for cancer prevention "
            "or treatment is not justified"
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/27297008/",
        "source_name": "PubMed — Fenton & Huang 2016, British Journal of Nutrition (systematic review)",
    },
    "sc2_source_c": {
        "quote": "There is no substantial evidence that this improves bone health or protects from osteoporosis.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3195546/",
        "source_name": "PMC — Schwalfenberg 2011, The Alkaline Diet, Journal of Environmental and Public Health",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
print("Verifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)
for key, result in citation_results.items():
    print(f"  {key}: {result['status']}")

# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

print(f"\n  SC1 confirmed disproof sources: {n_sc1} / {len(sc1_keys)}")
print(f"  SC2 confirmed disproof sources: {n_sc2} / {len(sc2_keys)}")

# 6. PER-SUB-CLAIM EVALUATION (Rule 7 — use compare(), never hardcode claim_holds)
sc1_holds = compare(n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
                    label="SC1: sources confirming blood pH not changed by alkaline water/diet")
sc2_holds = compare(n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
                    label="SC2: sources rejecting meaningful health benefits from alkaline water/diet")

# 7. COMPOUND EVALUATION
n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: both sub-claims meet disproof threshold")

# 8. ADVERSARIAL CHECKS (Rule 5)
# These searches were performed before writing the proof code. We looked for evidence that
# SUPPORTS the claim — studies showing alkaline water or diet has health benefits or changes pH.
adversarial_checks = [
    {
        "question": (
            "Do any randomized controlled trials demonstrate meaningful health benefits "
            "from alkaline water or alkaline diet?"
        ),
        "verification_performed": (
            "Searched PubMed and Google Scholar for 'alkaline water RCT health benefits', "
            "'alkaline diet randomized controlled trial outcomes'. Found the De Gruyter 2023 "
            "systematic review explicitly concluding no RCT evidence of benefit. The IJAHS "
            "systematic review (2022) noted that the majority of studies are animal models, "
            "in vitro work, or small exploratory human trials — not large-scale RCTs."
        ),
        "finding": (
            "No large-scale RCTs demonstrate meaningful health benefits. The 2023 De Gruyter "
            "systematic review, after reviewing available controlled studies, found no significant "
            "difference in blood parameters, gut microbiota, or fitness between alkaline water "
            "and mineral water groups. This finding is consistent with SC2 disproof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does alkaline water show benefits for specific conditions like acid reflux (GERD)?"
        ),
        "verification_performed": (
            "Searched for 'alkaline water GERD acid reflux clinical evidence'. Found a 2012 "
            "in vitro study (Koufman & Johnston) showing alkaline water (pH 8.8) may inactivate "
            "pepsin, and a small 2016 observational study. Also found the American College of "
            "Gastroenterology does not list alkaline water in GERD treatment guidelines."
        ),
        "finding": (
            "There is limited in vitro and small observational evidence suggesting alkaline water "
            "may reduce pepsin activity relevant to laryngopharyngeal reflux. However: (a) this is "
            "a specific condition, not 'meaningful health improvement' in general; (b) the evidence "
            "is not from large RCTs; (c) even this narrow claim does not involve 'counteracting body "
            "acidity' (blood pH) — it acts locally in the esophagus/stomach. This does not restore "
            "the mechanistic premise (SC1) or generalize to the broad health claim (SC2)."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does observational evidence show alkaline water consumers have better health outcomes?"
        ),
        "verification_performed": (
            "Searched for 'alkaline water observational study health outcomes'. Found the PLOS One "
            "2022 cross-sectional study (PMC9621423) on postmenopausal women showing lower fasting "
            "blood glucose and triglycerides in alkaline water consumers."
        ),
        "finding": (
            "The PLOS One 2022 cross-sectional study found lower fasting blood glucose and "
            "triglycerides in alkaline water drinkers among postmenopausal women. However: "
            "(a) cross-sectional studies cannot establish causation; (b) alkaline water consumers "
            "may differ systematically in lifestyle (healthier diet, more exercise) — confounding "
            "is not controlled; (c) this single observational study is outweighed by the systematic "
            "reviews finding no significant effects in controlled studies. This does not break SC2 "
            "disproof, which is based on systematic review consensus, not isolated observational data."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the alkaline diet have health benefits, even if not through pH change? "
            "Does this support the original claim?"
        ),
        "verification_performed": (
            "Searched for 'alkaline diet health benefits mechanism'. Found MD Anderson and the "
            "PMC 2011 Schwalfenberg review both acknowledging that alkaline diets (rich in fruits, "
            "vegetables, nuts, legumes) may have health benefits — but attributing these to "
            "antioxidants, phytochemicals, and the K/Na ratio, NOT to alkalizing the blood."
        ),
        "finding": (
            "The alkaline diet may have health benefits, but these are attributed to increased "
            "fruit and vegetable intake and reduced processed food — not to any pH-changing effect. "
            "MD Anderson states: 'these benefits are not caused by alkalizing the body.' "
            "Since the original claim specifically asserts the mechanism 'by counteracting body "
            "acidity,' and the actual mechanism (SC1) is disproved, the existence of diet-quality "
            "benefits does not rescue the claim as stated."
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

    if any_breaks:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "DISPROVED" if is_disproof else "PROVED"
    elif claim_holds and any_unverified:
        verdict = ("DISPROVED (with unverified citations)" if is_disproof
                   else "PROVED (with unverified citations)")
    elif not claim_holds and n_holding == 0:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified SC1 disproof citations) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1)
    FACT_REGISTRY["A2"]["method"] = f"count(verified SC2 disproof citations) = {n_sc2}"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # For qualitative proofs, extractions record citation status per source
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
                "description": "SC1: independent disproof sources consulted",
                "n_sources_consulted": len(sc1_keys),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in sc1_keys},
                "independence_note": (
                    "Harvard Health Publishing, MD Anderson Cancer Center, and "
                    "Schwalfenberg 2011 (PMC) are independently published by different institutions."
                ),
            },
            {
                "description": "SC2: independent disproof sources consulted",
                "n_sources_consulted": len(sc2_keys),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in sc2_keys},
                "independence_note": (
                    "De Gruyter systematic review (2023), Fenton & Huang 2016 "
                    "(British Journal of Nutrition), and Schwalfenberg 2011 (PMC) are independently "
                    "published. Note: Schwalfenberg 2011 appears in both SC1 and SC2 for different "
                    "facts; each SC has two additional independent institutional sources."
                ),
            },
        ],
        "sub_claim_results": [
            {
                "id": "SC1",
                "n_confirming": n_sc1,
                "threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"],
                "holds": sc1_holds,
                "description": "mechanism (blood pH not changed by alkaline water/diet)",
            },
            {
                "id": "SC2",
                "n_confirming": n_sc2,
                "threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"],
                "holds": sc2_holds,
                "description": "health benefit (no meaningful improvement shown in systematic reviews)",
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
            "is_disproof": is_disproof,
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
