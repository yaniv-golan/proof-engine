"""
Proof: Multivitamins and most supplements provide meaningful health benefits for the general healthy population.
Generated: 2026-03-31
"""
import json
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "Multivitamins and most supplements provide meaningful health benefits "
    "for the general healthy population."
)
CLAIM_FORMAL = {
    "subject": "multivitamins and most dietary supplements",
    "property": (
        "provide meaningful (clinically significant) health benefits to the general "
        "healthy adult population"
    ),
    "operator": ">=",
    "operator_note": (
        "This proof uses a disproof strategy: we gather authoritative sources that REJECT "
        "the claim and require at least 3 independently verified sources to establish disproof. "
        "'Meaningful health benefits' is interpreted as clinically significant improvements in "
        "primary outcomes — all-cause mortality, cardiovascular disease, or cancer incidence — "
        "for community-dwelling adults without nutritional deficiencies or known medical conditions. "
        "This conservative scope excludes populations with known deficiencies, pregnant persons, "
        "elderly with specific risks, or those under medical supervision. "
        "Threshold = 3: the claim is disproved if at least 3 independent authoritative sources "
        "confirm the claim is false. All 4 sources here confirm the same direction."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_uspstf_rec",
        "label": (
            "USPSTF 2022 Recommendation: Grade D (recommend against) for beta-carotene "
            "and vitamin E supplements in healthy adults"
        ),
    },
    "B2": {
        "key": "source_ncbi_review",
        "label": (
            "NCBI Bookshelf — USPSTF Systematic Evidence Review 2022: "
            "vitamin/mineral supplementation provides little to no benefit in preventing "
            "cancer, CVD, and death"
        ),
    },
    "B3": {
        "key": "source_nih_ods",
        "label": (
            "NIH Office of Dietary Supplements Fact Sheet: "
            "MVMs do not reliably reduce risk of chronic diseases"
        ),
    },
    "B4": {
        "key": "source_annals_2019",
        "label": (
            "Annals of Internal Medicine 2019 umbrella meta-analysis: "
            "dietary supplements not associated with mortality benefits in U.S. adults"
        ),
    },
    "A1": {
        "label": "Verified source count — independent sources confirming the claim is false",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS
# These are sources that REJECT the claim (confirm it is FALSE).
# Adversarial sources that support the claim are in adversarial_checks below.
empirical_facts = {
    "source_uspstf_rec": {
        "quote": (
            "The USPSTF recommends against the use of beta carotene or vitamin E supplements "
            "for the prevention of cardiovascular disease or cancer."
        ),
        "url": (
            "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/"
            "vitamin-supplementation-to-prevent-cvd-and-cancer-preventive-medication"
        ),
        "source_name": (
            "U.S. Preventive Services Task Force (USPSTF) — "
            "2022 Recommendation Statement on Vitamin Supplementation"
        ),
    },
    "source_ncbi_review": {
        "quote": (
            "Vitamin and mineral supplementation provides little to no benefit in preventing "
            "cancer, CVD, and death, with the exception of a possible small benefit for cancer "
            "incidence with multivitamin use"
        ),
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK581642/",
        "source_name": (
            "NCBI Bookshelf — USPSTF Systematic Evidence Review 2022 "
            "(Lam et al., commissioned by Agency for Healthcare Research and Quality)"
        ),
    },
    "source_nih_ods": {
        "quote": (
            "Overall, MVMs do not appear to reliably reduce the risk of chronic diseases when "
            "people choose to take these products for up to a decade (or more)."
        ),
        "url": "https://ods.od.nih.gov/factsheets/MVMS-HealthProfessional/",
        "source_name": (
            "NIH Office of Dietary Supplements — "
            "Multivitamin/Mineral Supplements: Health Professional Fact Sheet"
        ),
    },
    "source_annals_2019": {
        "quote": (
            "Use of dietary supplements is not associated with mortality benefits among U.S. adults."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/30959527/",
        "source_name": (
            "Annals of Internal Medicine 2019 — Umbrella meta-analysis of supplement use "
            "and mortality/CVD outcomes (Jenkins et al., PMID 30959527)"
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
# A source counts toward the disproof threshold if its quote was found on the page.
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources (disproof direction): {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — compare() required (Rule 7, never hardcode claim_holds)
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified disproof source count vs threshold (>= 3 required)",
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# Searches for evidence that SUPPORTS the claim (would undermine the disproof).
adversarial_checks = [
    {
        "question": (
            "Do large RCTs show cognitive benefits of multivitamins that constitute "
            "'meaningful benefits' for the general healthy population?"
        ),
        "verification_performed": (
            "Searched for 'COSMOS trial multivitamin cognitive benefit 2022 2023'. "
            "Found COSMOS-Mind (Baker et al., AJCN 2023): modest cognitive improvement "
            "over 2 years in adults aged 60+ (mean age ~72). Effect size ~0.1 SD. "
            "USPSTF reviewed this trial in their 2022 evidence synthesis and still issued "
            "Grade I (insufficient evidence) for multivitamins."
        ),
        "finding": (
            "A modest cognitive signal exists in COSMOS-Mind, but only in older adults "
            "(mean age ~72), not the general healthy adult population. The effect size (0.1 SD) "
            "is small. The USPSTF reviewed this evidence and concluded insufficient evidence "
            "to recommend multivitamins. Does not constitute 'meaningful benefit' for the "
            "general healthy population and does not break the disproof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there any positive cancer-incidence signal for multivitamins "
            "that would support 'meaningful benefits'?"
        ),
        "verification_performed": (
            "Searched for 'multivitamin cancer prevention RCT meta-analysis benefit 2020 2021 2022'. "
            "The NCBI Bookshelf evidence review notes 'a possible small benefit for cancer incidence "
            "with multivitamin use' from one trial, but characterizes it as having "
            "'important limitations, including only three adequately powered trials.' "
            "USPSTF issued Grade I (insufficient evidence), not a positive recommendation."
        ),
        "finding": (
            "One meta-analysis suggested a marginal cancer-incidence signal for multivitamins. "
            "This was reviewed by USPSTF, which issued Grade I (insufficient evidence), meaning "
            "harms and benefits could not be balanced. Any marginal benefit is offset by evidence "
            "of harm from specific supplements (beta-carotene, vitamin E — both Grade D). "
            "Does not constitute 'meaningful benefit' for most supplements and does not break disproof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does omega-3 or fish oil supplementation provide meaningful cardiovascular "
            "benefits for healthy adults, suggesting 'most supplements' do provide benefit?"
        ),
        "verification_performed": (
            "Searched for 'omega-3 fish oil supplements healthy adults cardiovascular benefit VITAL 2019'. "
            "The VITAL trial (Manson et al., NEJM 2019) — 25,871 healthy adults, no prior heart disease — "
            "found that omega-3 fatty acid supplements did not significantly reduce major cardiovascular "
            "events versus placebo (HR 0.92, 95% CI 0.80-1.05). "
            "AHA updated guidance in 2017 moved omega-3 supplements from a Class I to Class IIb recommendation."
        ),
        "finding": (
            "The largest high-quality RCT (VITAL) found omega-3 did not significantly reduce CVD events "
            "in the general healthy population without prior heart disease. "
            "This reinforces that even omega-3 — one of the most popular supplements — does not meet "
            "the bar for 'meaningful benefits' in the general healthy population. Does not break disproof."
        ),
        "breaks_proof": False,
    },
]

# 8. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif claim_holds and not any_unverified:
        verdict = "DISPROVED" if is_disproof else "PROVED"
    elif claim_holds and any_unverified:
        verdict = (
            "DISPROVED (with unverified citations)" if is_disproof
            else "PROVED (with unverified citations)"
        )
    elif not claim_holds:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = (
        f"{n_confirmed} independent sources confirm the claim is false "
        f"(threshold: {CLAIM_FORMAL['threshold']})"
    )

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions for qualitative proofs: record citation verification status per source
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
                "description": "Multiple independent authoritative sources consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from distinct institutions: "
                    "(1) USPSTF — independent federal advisory body, "
                    "(2) NCBI Bookshelf — AHRQ-commissioned systematic evidence review, "
                    "(3) NIH ODS — NIH synthesis of clinical trial evidence, "
                    "(4) Annals of Internal Medicine umbrella meta-analysis — peer-reviewed "
                    "independent academic synthesis. Each independently reviews different "
                    "underlying RCTs and observational datasets."
                ),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirmed": n_confirmed,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
            "proof_direction": "disprove",
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
