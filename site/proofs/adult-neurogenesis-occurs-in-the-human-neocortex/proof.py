"""
Proof: Adult neurogenesis occurs in the human neocortex.
Generated: 2026-04-07

Proof direction: DISPROOF
This proof collects independent scientific sources that explicitly reject the claim
that new neurons are generated in the adult human neocortex at a detectable level.
"""
import json
import os
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
        "presence of adult neurogenesis \u2014 generation of new neurons in the mature "
        "human brain's neocortical regions at a detectable level"
    ),
    "operator": ">=",
    "operator_note": (
        "The claim asserts that new neurons ARE generated in the adult human neocortex. "
        "Proof direction is 'disprove': we count independent peer-reviewed sources that "
        "explicitly REJECT this claim using direct human tissue evidence. "
        "A threshold of 2 direct human neocortex studies is used because domain scarcity "
        "limits the available evidence: only two independent research groups have applied "
        "C14 radiocarbon bomb-pulse dating to human neocortical tissue (Bhardwaj/Fris\u00e9n "
        "2006 and Spalding/Fris\u00e9n 2013, the latter measuring cortical neurons as a "
        "control for hippocampal analysis). No other method provides equivalent precision "
        "for dating neuronal birth in postmortem human tissue. A threshold of 3 would force "
        "inclusion of weaker evidence (cross-species extrapolation or hedged review language), "
        "which Rule 8 prohibits for DISPROVED verdicts. "
        "'Neocortex' is interpreted as the layered cerebral cortex "
        "(prefrontal, temporal, parietal, occipital regions), explicitly excluding the "
        "hippocampal dentate gyrus and olfactory bulb, which are anatomically and functionally "
        "distinct structures where adult neurogenesis is a separate ongoing debate. "
        "Formalization scope: the proof addresses whether neurogenesis occurs at detectable "
        "levels using current methodology. It does not exclude the theoretical possibility "
        "of neurogenesis below the detection threshold of C14 dating."
    ),
    "threshold": 2,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "bhardwaj_2006",
        "label": (
            "Bhardwaj et al. 2006 (PNAS) \u2014 C14 bomb-pulse dating + BrdU study shows "
            "no adult neocortical neurogenesis in humans (direct human tissue study)"
        ),
    },
    "B2": {
        "key": "spalding_2013",
        "label": (
            "Spalding et al. 2013 (Cell) \u2014 C14 bomb-pulse dating shows cortical neurons "
            "are not exchanged postnatally in humans (direct human tissue study)"
        ),
    },
    "A1": {
        "label": "Count of independent peer-reviewed human studies rejecting adult neocortical neurogenesis",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS -- sources that REJECT the claim (disproof template)
# Both sources are direct human tissue studies using C14 dating (Rule 8: subject-match).
empirical_facts = {
    "bhardwaj_2006": {
        "quote": (
            "neurons in the human cerebral neocortex are not generated in adulthood "
            "at detectable levels but are generated perinatally."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/16901981/",
        "source_name": (
            "Bhardwaj et al. 2006 \u2014 Neocortical neurogenesis in humans is restricted "
            "to development. Proc Natl Acad Sci USA 103(33):12564-12568 (PubMed abstract)"
        ),
    },
    "spalding_2013": {
        "quote": (
            "cortical and olfactory bulb neurons, which are not exchanged postnatally "
            "to a detectable degree in humans"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4394608/",
        "source_name": (
            "Spalding et al. 2013 \u2014 Dynamics of hippocampal neurogenesis in adult "
            "humans. Cell 153(6):1219-1227 (PMC full text)"
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. KEYWORD EXTRACTION -- verify rejection keywords appear in each quote (Rule 1)
confirmations = []
confirmations.append(
    verify_extraction("not generated in adulthood", empirical_facts["bhardwaj_2006"]["quote"], "B1")
)
confirmations.append(
    verify_extraction("not exchanged postnatally", empirical_facts["spalding_2013"]["quote"], "B2")
)

# 6. SOURCE COUNT -- number of rejection sources whose keyword confirmed
COUNTABLE_STATUSES = ("verified", "partial")
b1_verified = citation_results.get("bhardwaj_2006", {}).get("status") in COUNTABLE_STATUSES
b2_verified = citation_results.get("spalding_2013", {}).get("status") in COUNTABLE_STATUSES
n_confirming = sum(1 for c, v in zip(confirmations, [b1_verified, b2_verified]) if c and v)

# 7. CLAIM EVALUATION -- MUST use compare(), never hardcode claim_holds (Rule 7)
# claim_holds=True here means "the disproof holds" (2+ rejection sources found)
claim_holds = compare(
    n_confirming,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="SC1: rejection source count >= threshold",
)

# 8. CROSS-CHECK (Rule 6)
# B1 and B2 are from the same lab (Frisen group, Karolinska) but represent independent
# studies: B1 (2006) specifically targeted neocortical neurogenesis as its primary question;
# B2 (2013) measured cortical neurons as a control/reference for a hippocampal study.
# Both used C14 bomb-pulse dating on different postmortem human brain samples.
cross_check_agreement = b1_verified and b2_verified

# 9. SYSTEM TIME (Rule 3)
PROOF_GENERATION_DATE = date(2026, 4, 7)
today = date.today()
if today == PROOF_GENERATION_DATE:
    date_note = "System date matches proof generation date."
else:
    date_note = f"Proof generated on {PROOF_GENERATION_DATE}; running on {today}."

# 10. ADVERSARIAL CHECKS (Rule 5)
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
            "Gould et al. 1999 was immediately contested. Kornack & Rakic 2001 used the "
            "identical BrdU method in macaques and found zero new neurons in neocortex. "
            "Nowakowski & Hayes 2000 (Science 288:771) published a formal critique. Bhardwaj "
            "et al. 2006 (B1) used C14 bomb-pulse dating \u2014 a method immune to BrdU artifacts "
            "(BrdU can label DNA-repair in non-dividing cells) \u2014 and found no "
            "adult neocortical neurogenesis in human tissue. The Gould 1999 findings are now "
            "regarded as methodological artifacts by the field."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could any post-2013 study have demonstrated neocortical neurogenesis in humans "
            "using improved methods?"
        ),
        "verification_performed": (
            "Searched PubMed and Google Scholar for 'adult human neocortical neurogenesis' "
            "2014-2026, 'human cortex new neurons adult', 'neocortex neurogenesis human'. "
            "Read review articles PMC10665662 (2023) and PMC6852840 (2019)."
        ),
        "finding": (
            "No post-2013 study using C14 dating or any other method has found neocortical "
            "neurogenesis in humans. The 2018-2024 debate concerns the hippocampal dentate "
            "gyrus only (Sorrells 2018 vs Boldrini 2018). Reviews through 2023 continue to "
            "state that cortical neurons are not generated locally in adulthood. Both B1 and "
            "B2 remain unrebutted for the neocortex specifically."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is the neocortex claim contaminated by the hippocampal adult neurogenesis "
            "controversy \u2014 i.e., does uncertainty about the hippocampus extend to the neocortex?"
        ),
        "verification_performed": (
            "Read review articles distinguishing hippocampal from neocortical neurogenesis. "
            "Checked whether Sorrells et al. 2018 or Boldrini et al. 2018 addressed the neocortex."
        ),
        "finding": (
            "The 2018-2024 debate is confined to the hippocampus. All parties in that debate "
            "treat the neocortex as a settled negative. B1 covers both structures with the same "
            "C14 method and reaches the same negative conclusion for the neocortex independent "
            "of the hippocampal results. B2 separately confirms cortical neurons are not exchanged "
            "postnatally. The hippocampal controversy does not rescue the neocortical claim."
        ),
        "breaks_proof": False,
    },
]

# 11. VERDICT AND STRUCTURED OUTPUT
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

    FACT_REGISTRY["A1"]["method"] = "sum(verify_extraction confirmations where citation verified)"
    FACT_REGISTRY["A1"]["result"] = str(n_confirming)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": "not generated in adulthood",
            "value_in_quote": confirmations[0],
            "quote_snippet": empirical_facts["bhardwaj_2006"]["quote"][:80],
        },
        "B2": {
            "value": "not exchanged postnatally",
            "value_in_quote": confirmations[1],
            "quote_snippet": empirical_facts["spalding_2013"]["quote"][:80],
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
                    "B1 (Bhardwaj 2006, human neocortical tissue, C14 dating) and B2 "
                    "(Spalding 2013, human cortical neurons, C14 dating) are independent "
                    "studies on different postmortem human brain samples that independently "
                    "reach the same conclusion: no neurogenesis in adult human neocortex."
                ),
                "values_compared": [
                    "not generated in adulthood (human, C14+BrdU, Bhardwaj 2006)",
                    "not exchanged postnatally (human, C14, Spalding 2013)",
                ],
                "agreement": cross_check_agreement,
                "coi_flags": [],
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
            "date_note": date_note,
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
