"""
Proof: Adult neurogenesis occurs in the human neocortex.
Generated: 2026-03-27

Proof direction: DISPROOF
This proof collects independent scientific sources that explicitly reject the claim
that new neurons are generated in the adult human neocortex at a detectable level.
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
CLAIM_NATURAL = "Adult neurogenesis occurs in the human neocortex."
CLAIM_FORMAL = {
    "subject": "human neocortex",
    "property": (
        "presence of adult neurogenesis — generation of new neurons in the mature "
        "human brain's neocortical regions at a detectable level"
    ),
    "operator": ">=",
    "operator_note": (
        "The claim asserts that new neurons ARE generated in the adult human neocortex. "
        "Proof direction is 'disprove': we count independent peer-reviewed sources that "
        "explicitly REJECT this claim. A threshold of 3 independent rejection sources is "
        "required for DISPROVED. 'Neocortex' is interpreted as the layered cerebral cortex "
        "(prefrontal, temporal, parietal, occipital regions), explicitly excluding the "
        "hippocampal dentate gyrus and olfactory bulb, which are anatomically and functionally "
        "distinct structures where adult neurogenesis is a separate ongoing debate. "
        "The claim is assessed against the most rigorous available evidence — C14 radiocarbon "
        "bomb-pulse dating, which directly measures neuronal birth dates without relying on "
        "cell-division markers that can label non-dividing cells."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "bhardwaj_2006",
        "label": (
            "Bhardwaj et al. 2006 (PNAS) — C14 bomb-pulse dating + BrdU study shows "
            "no adult neocortical neurogenesis in humans (direct human tissue study)"
        ),
    },
    "B2": {
        "key": "kornack_rakic_2001",
        "label": (
            "Kornack & Rakic 2001 (Science) — triple-label BrdU immunofluorescence finds "
            "no neurogenesis in adult primate neocortex; fails to replicate Gould 1999 claim"
        ),
    },
    "B3": {
        "key": "rakic_2002",
        "label": (
            "Rakic 2002 (Nature Reviews Neuroscience) — authoritative review questions "
            "the scientific basis of claims of adult primate neocortical neurogenesis"
        ),
    },
    "A1": {
        "label": "Count of independent peer-reviewed sources rejecting adult neocortical neurogenesis",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (disproof template)
# Adversarial sources (those that SUPPORT the claim) go in adversarial_checks only.
empirical_facts = {
    "bhardwaj_2006": {
        "quote": (
            "neurons in the human cerebral neocortex are not generated in adulthood "
            "at detectable levels but are generated perinatally."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/16901981/",
        "source_name": (
            "Bhardwaj et al. 2006 — Neocortical neurogenesis in humans is restricted "
            "to development. Proc Natl Acad Sci USA 103(33):12564-12568 (PubMed abstract)"
        ),
    },
    "kornack_rakic_2001": {
        "quote": (
            "our results do not substantiate the claim of neurogenesis in normal adult "
            "primate neocortex."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/11739948/",
        "source_name": (
            "Kornack & Rakic 2001 — Cell Proliferation Without Neurogenesis in Adult "
            "Primate Neocortex. Science 294:2127-2130 (PubMed abstract)"
        ),
    },
    "rakic_2002": {
        "quote": (
            "Here, I review the available evidence, and question the scientific basis "
            "of this claim."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/11823806/",
        "source_name": (
            "Rakic 2002 — Neurogenesis in adult primate neocortex: an evaluation of the "
            "evidence. Nature Reviews Neuroscience 3:65-71 (PubMed abstract)"
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. KEYWORD EXTRACTION — verify rejection keywords appear in each quote (Rule 1)
# For disproof: keywords that signal the source REJECTS the claim.
confirmations = []
confirmations.append(
    verify_extraction("not generated in adulthood", empirical_facts["bhardwaj_2006"]["quote"], "B1")
)
confirmations.append(
    verify_extraction("do not substantiate", empirical_facts["kornack_rakic_2001"]["quote"], "B2")
)
confirmations.append(
    verify_extraction("question the scientific basis", empirical_facts["rakic_2002"]["quote"], "B3")
)

# 6. SOURCE COUNT — number of rejection sources whose keyword confirmed
n_confirming = sum(1 for c in confirmations if c)

# 7. CLAIM EVALUATION — MUST use compare(), never hardcode claim_holds (Rule 7)
# claim_holds=True here means "the disproof holds" (3+ rejection sources found)
claim_holds = compare(
    n_confirming,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="SC1: rejection source count >= threshold",
)

# 8. ADVERSARIAL CHECKS (Rule 5)
# For disproof: search for sources that SUPPORT the claim (would break the disproof).
# Adversarial work done in Step 2; these records document the findings.
adversarial_checks = [
    {
        "question": (
            "Does Gould et al. 1999 (Science) provide credible unrebutted evidence of "
            "adult neocortical neurogenesis in primates?"
        ),
        "verification_performed": (
            "Read Gould et al. 1999 (PMID 10521353) and subsequent replies. The paper used "
            "BrdU labeling in adult macaques and claimed new neurons in prefrontal, temporal, "
            "and parietal cortex. Searched PubMed for replications and critiques."
        ),
        "finding": (
            "Gould et al. 1999 was immediately contested. Kornack & Rakic 2001 (B2) used the "
            "identical BrdU method in macaques and found zero new neurons in neocortex. "
            "Nowakowski & Hayes 2000 (Science 288:771) published a formal critique. Bhardwaj "
            "et al. 2006 (B1) used C14 bomb-pulse dating — a method immune to BrdU artifacts "
            "(BrdU can label DNA-repair in non-dividing cells and dying cells) — and found no "
            "adult neocortical neurogenesis in human tissue. The Gould 1999 findings are now "
            "regarded as methodological artifacts by the field."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could any post-2006 study have demonstrated neocortical neurogenesis in humans "
            "using improved methods, rebutting Bhardwaj 2006?"
        ),
        "verification_performed": (
            "Searched PubMed and Google Scholar for 'adult human neocortical neurogenesis' "
            "2010-2025, 'human cortex new neurons adult', 'neocortex neurogenesis human 2020'. "
            "Read review articles PMC10665662 (2023) and PMC6852840 (2019)."
        ),
        "finding": (
            "No post-2006 study using C14 dating has found neocortical neurogenesis in humans. "
            "The 2018-2024 debate concerns the hippocampal dentate gyrus only (Sorrells 2018 "
            "vs Boldrini 2018). Reviews through 2023 continue to state that cortical neurons "
            "are not generated locally in adulthood. Bhardwaj 2006 remains unrebutted for the "
            "neocortex specifically."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is the neocortex claim contaminated by the hippocampal adult neurogenesis "
            "controversy — i.e., does uncertainty about the hippocampus extend to the neocortex?"
        ),
        "verification_performed": (
            "Read review articles distinguishing hippocampal from neocortical neurogenesis. "
            "Checked whether Sorrells et al. 2018 or Boldrini et al. 2018 addressed the neocortex."
        ),
        "finding": (
            "The 2018-2024 debate is confined to the hippocampus. All parties in that debate "
            "treat the neocortex as a settled negative. Bhardwaj 2006 covers both structures "
            "with the same C14 method and reaches the same negative conclusion for the neocortex "
            "independent of the hippocampal results. The hippocampal controversy does not rescue "
            "the neocortical claim."
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
        verdict = "DISPROVED (with unverified citations)" if is_disproof else "PROVED (with unverified citations)"
    elif not claim_holds and not any_unverified:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = "sum(verify_extraction confirmations)"
    FACT_REGISTRY["A1"]["result"] = str(n_confirming)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": "not generated in adulthood",
            "value_in_quote": confirmations[0],
            "quote_snippet": empirical_facts["bhardwaj_2006"]["quote"][:80],
        },
        "B2": {
            "value": "do not substantiate",
            "value_in_quote": confirmations[1],
            "quote_snippet": empirical_facts["kornack_rakic_2001"]["quote"][:80],
        },
        "B3": {
            "value": "question the scientific basis",
            "value_in_quote": confirmations[2],
            "quote_snippet": empirical_facts["rakic_2002"]["quote"][:80],
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
        "cross_checks": [
            {
                "description": (
                    "Bhardwaj 2006 (human tissue, C14 dating) and Kornack & Rakic 2001 "
                    "(macaque, BrdU immunofluorescence) use independent methodologies on "
                    "independent subjects and independently reach the same conclusion: "
                    "no neurogenesis in adult primate/human neocortex."
                ),
                "values_compared": [
                    "not generated in adulthood (human, C14+BrdU, Bhardwaj 2006)",
                    "do not substantiate neurogenesis claim (macaque, BrdU, Kornack 2001)",
                ],
                "agreement": True,
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirming": n_confirming,
            "n_required": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
            "proof_direction": "disprove",
            "any_unverified_citations": any_unverified,
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
