"""
Proof: The human brain does not generate new neurons in adulthood.
Generated: 2026-03-27

PROOF DIRECTION: DISPROVE
We prove the claim is FALSE by demonstrating that the human brain DOES generate
new neurons in adulthood. This is established through three independent peer-reviewed
sources confirming adult hippocampal neurogenesis (AHN) in humans.

The adversarial check addresses the strongest counter-evidence: Sorrells et al. 2018
(Nature), which found neurogenesis undetectable in adult humans, and explains why the
scientific consensus has not adopted that finding as definitive.
"""
import json
from datetime import date
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.smart_extract import verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "The human brain does not generate new neurons in adulthood."
CLAIM_FORMAL = {
    "subject": "The human brain",
    "property": "generates new neurons in adulthood (adult hippocampal neurogenesis, AHN)",
    "operator": ">=",
    "operator_note": (
        "The claim asserts that adult neurogenesis does NOT occur (zero occurrence). "
        "We DISPROVE it by counting independent peer-reviewed sources that directly confirm "
        "adult neurogenesis in humans. proof_direction='disprove': n_confirming counts sources "
        "REJECTING the claim (i.e., confirming AHN exists). "
        "If n_confirming >= 3 (threshold), claim_holds=True means the disproof succeeds => verdict=DISPROVED. "
        "The threshold of 3 independent sources was chosen as a conservative minimum for scientific consensus."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "moreno_jimenez_2019",
        "label": (
            "Moreno-Jiménez et al. 2019, Nature Medicine — primary research article: "
            "identified thousands of immature neurons in the dentate gyrus of healthy humans up to the 9th decade"
        ),
    },
    "B2": {
        "key": "kempermann_2018",
        "label": (
            "Kempermann et al. 2018, Cell Stem Cell — 18-author consensus review: "
            "no reason to abandon the idea that adult-generated neurons contribute across the human life span"
        ),
    },
    "B3": {
        "key": "llorens_martin_2021",
        "label": (
            "Llorens-Martín et al. 2021, Journal of Neuroscience — primary research article: "
            "demonstrates AHN is a robust phenomenon in the human hippocampus during physiological and pathologic aging"
        ),
    },
    "A1": {
        "label": "Count of independent sources confirming adult neurogenesis in humans (rejecting the claim)",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS
# Sources that REJECT the claim (confirm the brain DOES generate new neurons in adulthood).
# Adversarial sources that SUPPORT the claim go in adversarial_checks below, not here.
empirical_facts = {
    "moreno_jimenez_2019": {
        "quote": (
            "we identified thousands of immature neurons in the DG of neurologically healthy "
            "human subjects up to the ninth decade of life"
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/30911133/",
        "source_name": "Moreno-Jiménez et al. 2019, Nature Medicine (PubMed abstract)",
    },
    "kempermann_2018": {
        "quote": (
            "there is currently no reason to abandon the idea that adult-generated neurons "
            "make important functional contributions to neural plasticity and cognition "
            "across the human life span"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6035081/",
        "source_name": "Kempermann et al. 2018, Cell Stem Cell (PMC)",
    },
    "llorens_martin_2021": {
        "quote": (
            "adult neurogenesis is a robust phenomenon that occurs in the human hippocampus "
            "during physiological and pathologic aging"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8018741/",
        "source_name": "Llorens-Martín et al. 2021, Journal of Neuroscience (PMC)",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. KEYWORD EXTRACTION (Rule 1)
# verify_extraction checks that a key term appears in the quote string itself.
# For disproof proofs, keywords confirm the source REJECTS the claim.
confirmations = []
confirmations.append(
    verify_extraction("immature neurons", empirical_facts["moreno_jimenez_2019"]["quote"], "B1")
)
confirmations.append(
    verify_extraction("adult-generated neurons", empirical_facts["kempermann_2018"]["quote"], "B2")
)
confirmations.append(
    verify_extraction("adult neurogenesis", empirical_facts["llorens_martin_2021"]["quote"], "B3")
)

# 6. SOURCE COUNT
n_confirming = sum(1 for c in confirmations if c)

# 7. CLAIM EVALUATION — use compare(), never hardcode claim_holds
# proof_direction='disprove': n_confirming = sources REJECTING the claim
# n_confirming >= 3 => claim_holds = True => verdict = DISPROVED (claim is false)
claim_holds = compare(n_confirming, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"])

# 8. ADVERSARIAL CHECKS (Rule 5)
# For a disproof: search for sources SUPPORTING the claim (i.e., denying adult neurogenesis).
# breaks_proof=True if a credible supporting source was found that cannot be dismissed.
adversarial_checks = [
    {
        "question": (
            "Is there credible peer-reviewed evidence that adult human neurogenesis does NOT occur? "
            "(Sources supporting the claim.)"
        ),
        "verification_performed": (
            "Searched: 'Sorrells 2018 adult neurogenesis humans no evidence'. "
            "Found: Sorrells et al. 2018 (Nature 555:377-381) concluded 'neurogenesis in the dentate "
            "gyrus does not continue, or is extremely rare, in adult humans' based on 17 post-mortem "
            "controls (18-77 years) and 12 epilepsy surgical resections. "
            "This is the strongest counter-evidence in the literature."
        ),
        "finding": (
            "The Sorrells 2018 finding is attributed by the field to a methodological artifact: "
            "postmortem delay (PMD). DCX (doublecortin), the key marker for immature neurons, "
            "degrades rapidly after death. Sorrells samples had PMDs up to 48 hours; Boldrini et al. "
            "2018 (Cell Stem Cell) used PMDs ≤26 hours and found persistent neurogenesis. "
            "Moreno-Jiménez et al. 2019 used tightly controlled PMDs (<4 hours) and found thousands "
            "of immature neurons per mm². The 18-author Kempermann et al. 2018 consensus review "
            "explicitly addressed the Sorrells controversy and concluded adult neurogenesis persists. "
            "Sorrells 2018 does not break the proof: its negative result reflects tissue fixation "
            "problems, not the absence of adult neurogenesis."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is adult neurogenesis confirmed only in rodents, not specifically in humans? "
            "(Species-specificity challenge.)"
        ),
        "verification_performed": (
            "Searched: 'adult neurogenesis absent humans but present rodents species-specific'. "
            "Reviewed: Eriksson et al. 1998 (Nature Medicine) — first human study using BrdU "
            "incorporation in post-mortem cancer patients, confirmed new neurons in adult human "
            "dentate gyrus. Spalding et al. 2013 (Cell) — used radiocarbon (14C) retrospective "
            "birthdating, confirmed new neurons in adult human hippocampus independently of any "
            "immunohistochemical markers."
        ),
        "finding": (
            "Human-specific studies using three independent methodologies — BrdU labeling (Eriksson 1998), "
            "14C retrospective birthdating (Spalding 2013), and controlled-PMD immunohistochemistry "
            "(Moreno-Jiménez 2019, Llorens-Martín 2021) — all confirm adult neurogenesis in humans. "
            "No species-specific exclusion argument is credible."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could 'adulthood' be interpreted such that neurogenesis tapers off before "
            "conventional adult ages (e.g., only persisting into early 20s)?"
        ),
        "verification_performed": (
            "Searched: 'adult neurogenesis human age range decline decades'. "
            "Reviewed Moreno-Jiménez 2019 subject ages: 43–87 years. "
            "Reviewed Llorens-Martín 2021 which states persistence 'until the 10th decade of human life'. "
            "Boldrini et al. 2018 (Cell Stem Cell) found neurogenesis in subjects up to age 79."
        ),
        "finding": (
            "Neurogenesis is confirmed in subjects aged 43–87 (Moreno-Jiménez 2019) and up to "
            "the 10th decade (Llorens-Martín 2021). Even under any reasonable definition of "
            "'adulthood' (post-18, post-25, etc.), neurogenesis persists. "
            "This adversarial challenge fails."
        ),
        "breaks_proof": False,
    },
]

# 9. VERDICT AND STRUCTURED OUTPUT
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
            "DISPROVED (with unverified citations)"
            if is_disproof
            else "PROVED (with unverified citations)"
        )
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"sum(confirmations) = {n_confirming}"
    FACT_REGISTRY["A1"]["result"] = str(n_confirming)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        f"B{i+1}": {
            "value": "keyword confirmed" if c else "keyword not found",
            "value_in_quote": c,
            "quote_snippet": list(empirical_facts.values())[i]["quote"][:80],
        }
        for i, c in enumerate(confirmations)
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
                "description": "Independent source agreement: all three sources confirm adult neurogenesis in humans",
                "n_sources": len(confirmations),
                "n_confirming": n_confirming,
                "agreement": n_confirming == len(confirmations),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirming": n_confirming,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
            "proof_direction": CLAIM_FORMAL["proof_direction"],
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
