"""
Proof: All ultra-processed foods are inherently unhealthy and should be avoided completely.
Generated: 2026-03-28

Claim type: Compound qualitative claim — two sub-claims joined by AND.
Proof direction: DISPROVE (both sub-claims).

SC1: "All ultra-processed foods are inherently unhealthy" — universal claim,
     disprovable by counterexample or by authoritative rejection of the universal framing.
SC2: "Should be avoided completely" — absolute recommendation claim,
     disprovable by showing major health bodies recommend reduction, not elimination.
"""
import json
import sys
import os

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "All ultra-processed foods are inherently unhealthy and should be avoided completely."
)
CLAIM_FORMAL = {
    "subject": "Ultra-processed foods (NOVA Group 4 classification)",
    "proof_direction": "disprove",
    "sub_claims": [
        {
            "id": "SC1",
            "property": (
                "Every food classified as ultra-processed (NOVA Group 4) is inherently harmful "
                "regardless of context, quantity, or individual nutrient composition"
            ),
            "operator": ">=",
            "threshold": 3,
            "proof_direction": "disprove",
            "operator_note": (
                "'All UPFs are inherently unhealthy' is a universal claim: every NOVA Group 4 "
                "food is harmful by its nature. Logically, one credible counterexample disproves "
                "a universal. Threshold set to 3 (≥3 independent authoritative sources that "
                "explicitly reject this universal framing or identify UPFs acceptable in a healthy "
                "diet) to require genuine multi-source consensus, not isolated dissent."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "Authoritative health bodies recommend complete avoidance of all ultra-processed foods "
                "(i.e., no UPF should ever be consumed by anyone)"
            ),
            "operator": ">=",
            "threshold": 3,
            "proof_direction": "disprove",
            "operator_note": (
                "'Should be avoided completely' is read as an absolute, context-free recommendation. "
                "To disprove it, we need ≥3 independent authoritative health bodies or peer-reviewed "
                "sources whose actual guidance is reduction or limitation — not elimination — and/or "
                "that explicitly allow some UPFs in a healthy diet. "
                "If major health bodies consistently say 'eat less,' 'limit,' or 'some UPFs can be "
                "included in a healthy diet,' the absolute avoidance claim is refuted."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "The original claim is compound: (SC1 AND SC2). Both must hold for the claim to be true. "
        "To disprove the compound AND claim, disproving either SC1 or SC2 is logically sufficient. "
        "This proof disproves both sub-claims independently."
    ),
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {"key": "sc1_nhs",     "label": "SC1: NHS — explicitly names UPFs acceptable in a healthy diet"},
    "B2": {"key": "sc1_harvard", "label": "SC1: Harvard T.H. Chan Nutrition Source — some UPFs may be useful"},
    "B3": {"key": "sc1_gibney",  "label": "SC1: Gibney 2019 (Curr Dev Nutr) — no good/bad foods, only diets"},
    "B4": {"key": "sc2_nhs",     "label": "SC2: NHS — recommends 'eating less' not complete avoidance"},
    "B5": {"key": "sc2_who",     "label": "SC2: WHO Healthy Diet fact sheet — 'limit' not 'avoid completely'"},
    "B6": {"key": "sc2_harvard", "label": "SC2: Harvard — UPF use is consumer choice, pros and cons"},
    "A1": {"label": "SC1 verified disproof source count", "method": None, "result": None},
    "A2": {"label": "SC2 verified disproof source count", "method": None, "result": None},
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
#    SC1 keys: sources that reject "all UPFs are inherently unhealthy"
#    SC2 keys: sources that use reduction language, not complete-avoidance language
#    Adversarial sources (supporting the claim) go in adversarial_checks only.
# ---------------------------------------------------------------------------
empirical_facts = {
    # --- SC1 disproof ---
    "sc1_nhs": {
        "quote": (
            "Some ultra-processed foods can be included in a healthy diet "
            "\u2013 such as wholemeal sliced bread, wholegrain or higher fibre "
            "breakfast cereals or baked beans."
        ),
        "url": "https://www.nhs.uk/live-well/eat-well/how-to-eat-a-balanced-diet/what-are-processed-foods/",
        "source_name": "NHS (UK National Health Service) \u2014 What are processed foods?",
    },
    "sc1_harvard": {
        "quote": "some products may be a useful addition to a healthful diet",
        "url": "https://nutritionsource.hsph.harvard.edu/processed-foods/",
        "source_name": (
            "Harvard T.H. Chan School of Public Health \u2014 "
            "The Nutrition Source: Processed Foods"
        ),
    },
    "sc1_gibney": {
        "quote": "there are good and bad diets, not good and bad foods",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6389637/",
        "source_name": (
            "Gibney MJ (2019), Ultra-Processed Foods: Definitions and Policy Issues, "
            "Current Developments in Nutrition, PMC6389637"
        ),
    },
    # --- SC2 disproof ---
    "sc2_nhs": {
        "quote": (
            "Most people would probably benefit from eating less ultra-processed foods "
            "that are high in saturated fat, salt or sugar."
        ),
        "url": "https://www.nhs.uk/live-well/eat-well/how-to-eat-a-balanced-diet/what-are-processed-foods/",
        "source_name": "NHS (UK National Health Service) \u2014 What are processed foods?",
    },
    "sc2_who": {
        "quote": "Foods high in unhealthy fats, free sugars and sodium should be limited.",
        "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
        "source_name": "World Health Organization \u2014 Healthy Diet Fact Sheet",
    },
    "sc2_harvard": {
        "quote": (
            "the use of processed and even ultra-processed foods is the choice of the consumer, "
            "and there are pros and cons that come with each type"
        ),
        "url": "https://nutritionsource.hsph.harvard.edu/processed-foods/",
        "source_name": (
            "Harvard T.H. Chan School of Public Health \u2014 "
            "The Nutrition Source: Processed Foods"
        ),
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
# ---------------------------------------------------------------------------
SC1_KEYS = ["sc1_nhs", "sc1_harvard", "sc1_gibney"]
SC2_KEYS = ["sc2_nhs", "sc2_who", "sc2_harvard"]
COUNTABLE_STATUSES = ("verified", "partial")

n_sc1 = sum(1 for k in SC1_KEYS if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in SC2_KEYS if citation_results[k]["status"] in COUNTABLE_STATUSES)

print(f"  SC1 confirmed sources: {n_sc1} / {len(SC1_KEYS)}")
print(f"  SC2 confirmed sources: {n_sc2} / {len(SC2_KEYS)}")

# ---------------------------------------------------------------------------
# 6. CLAIM EVALUATION — MUST use compare(), never hardcode (Rule 7)
# ---------------------------------------------------------------------------
sc1_threshold = CLAIM_FORMAL["sub_claims"][0]["threshold"]
sc2_threshold = CLAIM_FORMAL["sub_claims"][1]["threshold"]

sc1_disproved = compare(
    n_sc1, ">=", sc1_threshold,
    label="SC1 disproof: verified sources rejecting 'all UPFs inherently unhealthy'"
)
sc2_disproved = compare(
    n_sc2, ">=", sc2_threshold,
    label="SC2 disproof: verified sources rejecting 'should be avoided completely'"
)

# Compound AND claim: disproved if EITHER sub-claim is disproved.
# We expect both to be disproved.
compound_disproved = sc1_disproved or sc2_disproved
both_disproved = sc1_disproved and sc2_disproved

# ---------------------------------------------------------------------------
# 7. ADVERSARIAL CHECKS (Rule 5)
#    Searching for evidence that SUPPORTS the original claim.
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Do any major health authorities support complete avoidance of all UPFs?"
        ),
        "verification_performed": (
            "Searched for 'WHO ultra-processed foods avoid completely,' "
            "'NHS avoid all ultra-processed foods,' "
            "'USDA dietary guidelines ultra-processed avoid completely,' "
            "and reviewed Brazil 2014 Dietary Guidelines (origin of NOVA classification). "
            "Also checked AAP (American Academy of Pediatrics) infant formula guidance."
        ),
        "finding": (
            "No major health authority (WHO, NHS, CDC, USDA, AAP, BNF) recommends complete "
            "avoidance of all UPFs. Brazil's 2014 Dietary Guidelines say 'Avoid ultra-processed "
            "foods' but this is primarily a cultural/culinary preference statement and is "
            "explicitly contested by other nutrition bodies. The AAP continues to recommend "
            "infant formula (NOVA Group 4) for infants who cannot breastfeed, directly "
            "contradicting any universal avoidance directive."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do observational studies show ALL UPF consumption is harmful, even at low levels?"
        ),
        "verification_performed": (
            "Reviewed Rico-Campà et al. (BMJ 2019, PMC6538973) — largest-cited UPF mortality "
            "cohort study. Searched for 'ultra-processed food dose-response mortality low "
            "consumption' and 'ultra-processed food health benefit study.' "
            "Also reviewed Elizabeth et al. (Nutrients 2020, PMC7399967) systematic review."
        ),
        "finding": (
            "Rico-Campà et al. (BMJ 2019) found higher all-cause mortality in the highest "
            "quartile (≥4 servings/day) vs lowest quartile — a dose-dependent, not absolute, "
            "association. The lowest-quartile group had best outcomes while still consuming "
            "some UPFs. Authors explicitly note inability to rule out residual confounding. "
            "Elizabeth et al. (Nutrients 2020) reviewed 43 studies; all associations were at "
            "population/dietary-pattern level, not individual-product level. No peer-reviewed "
            "study demonstrates that any dose of any UPF is inherently harmful."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is the NOVA 'ultra-processed' category scientifically coherent enough to support "
            "a universal health claim?"
        ),
        "verification_performed": (
            "Searched 'NOVA classification criticism reliability,' 'ultra-processed food "
            "definition controversy,' and reviewed Gibney 2019 (PMC6389637). "
            "Checked whether infant formula is classified as UPF under NOVA."
        ),
        "finding": (
            "Gibney 2019 (PMC6389637) documents that NOVA classifies all commercially produced "
            "infant formula as ultra-processed and 'to be avoided,' yet 'no study has been "
            "undertaken to explore the implications of such a policy for this vulnerable group.' "
            "Harvard Nutrition Source states 'NOVA has been criticized for being too general in "
            "classifying certain foods, causing confusion.' The NOVA Group 4 category spans diet "
            "sodas, iron-fortified infant cereals, wholemeal sliced bread, and infant formula — "
            "a heterogeneous group that undermines any universal health claim."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do NOVA originators themselves claim all UPFs are 'inherently' harmful?"
        ),
        "verification_performed": (
            "Reviewed Monteiro et al. 2018 NOVA food classification paper and PAHO/WHO-aligned "
            "guidance. Searched 'Monteiro ultra-processed inherently unhealthy.'"
        ),
        "finding": (
            "NOVA proponents (Monteiro et al.) argue that processing itself may cause harm "
            "beyond nutrient composition and advocate strong policy restrictions. However, "
            "their peer-reviewed papers phrase findings as population-level associations, "
            "not absolute per-food determinations. The 'inherently unhealthy' framing — "
            "implying harm regardless of quantity or context — exceeds what even the strongest "
            "pro-NOVA researchers assert in the literature."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 8. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    any_unverified = any(
        citation_results[k]["status"] != "verified"
        for k in list(SC1_KEYS) + list(SC2_KEYS)
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif compound_disproved and not any_unverified:
        verdict = "DISPROVED"
    elif compound_disproved and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(SC1 verified disproof citations >= {sc1_threshold})"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1)
    FACT_REGISTRY["A2"]["method"] = f"count(SC2 verified disproof citations >= {sc2_threshold})"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: for qualitative proofs, record citation verification status
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
                "description": "SC1 disproof: multiple independent authoritative sources consulted",
                "n_sources_consulted": len(SC1_KEYS),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in SC1_KEYS},
                "independence_note": (
                    "NHS (UK government health body), Harvard T.H. Chan (US academic), "
                    "Gibney 2019 in peer-reviewed journal (Current Developments in Nutrition) "
                    "— independent institutions across different countries and sectors."
                ),
            },
            {
                "description": "SC2 disproof: multiple independent authoritative sources consulted",
                "n_sources_consulted": len(SC2_KEYS),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in SC2_KEYS},
                "independence_note": (
                    "NHS (UK), WHO (international UN agency), Harvard T.H. Chan (US academic) "
                    "— three independent institutions across jurisdictions and sectors."
                ),
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_n_confirmed": n_sc1,
            "sc1_threshold": sc1_threshold,
            "sc1_disproved": sc1_disproved,
            "sc2_n_confirmed": n_sc2,
            "sc2_threshold": sc2_threshold,
            "sc2_disproved": sc2_disproved,
            "both_sub_claims_disproved": both_disproved,
            "compound_claim_disproved": compound_disproved,
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
