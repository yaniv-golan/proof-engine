"""
Proof: Humans use only 10% of their brain at any one time.
Generated: 2026-03-27
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
CLAIM_NATURAL = "Humans use only 10% of their brain at any one time."
CLAIM_FORMAL = {
    "subject": "human brain usage",
    "property": (
        "Whether scientific consensus holds that only 10% of the brain "
        "is active at any given moment"
    ),
    "operator": ">=",
    "operator_note": (
        "This proof proceeds by disproof: the claim is adjudicated FALSE if 3 or more "
        "independent authoritative sources explicitly characterize it as a myth, "
        "misconception, or scientifically unsupported belief. "
        "The threshold of 3 sources reflects the standard for established scientific consensus "
        "in the qualitative consensus template. "
        "If the threshold is not met, the verdict is UNDETERMINED (not PROVED), "
        "because failing to find enough rejection sources does not validate the claim."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_mit",
        "label": "MIT McGovern Institute for Brain Research: labels the 10% claim a myth",
    },
    "B2": {
        "key": "source_britannica",
        "label": "Encyclopaedia Britannica: states entire brain is in use at all times",
    },
    "B3": {
        "key": "source_sciam",
        "label": "Scientific American: characterizes the 10-percent claim as a myth",
    },
    "A1": {
        "label": "Source count: independent authoritative sources rejecting the 10% claim",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS
# All three sources REJECT the claim — confirming it is a myth.
# (Sources that support the claim, if any, would go in adversarial_checks only.)
empirical_facts = {
    "source_mit": {
        "quote": (
            "But the idea that we use 10 percent of our brain is 100 percent a myth."
        ),
        "url": "https://mcgovern.mit.edu/2024/01/26/do-we-use-only-10-percent-of-our-brain/",
        "source_name": "MIT McGovern Institute for Brain Research",
    },
    "source_britannica": {
        "quote": (
            "But the truth is that we use all of our brain all of the time."
        ),
        "url": "https://www.britannica.com/story/do-we-really-use-only-10-percent-of-our-brain",
        "source_name": "Encyclopaedia Britannica",
    },
    "source_sciam": {
        "quote": (
            "the 10-percent myth is one of those hopeful shibboleths that refuses to die"
        ),
        "url": "https://www.scientificamerican.com/article/do-we-really-use-only-10/",
        "source_name": "Scientific American",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. KEYWORD EXTRACTION (Rule 1)
# For disproof: keywords confirm each source REJECTS the claim.
# "myth" and "all of our brain" appear only in quotes that treat the claim as false.
confirmations = []
confirmations.append(verify_extraction("myth", empirical_facts["source_mit"]["quote"], "B1"))
confirmations.append(verify_extraction("all of our brain", empirical_facts["source_britannica"]["quote"], "B2"))
confirmations.append(verify_extraction("myth", empirical_facts["source_sciam"]["quote"], "B3"))

# 6. SOURCE COUNT
n_confirming = sum(1 for c in confirmations if c)

# 7. CLAIM EVALUATION — must use compare(), never hardcode (Rule 7)
# claim_holds=True means "the disproof holds" (3+ sources reject the claim).
# The verdict block below maps claim_holds=True → DISPROVED (not PROVED).
claim_holds = compare(n_confirming, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"])

# 8. ADVERSARIAL CHECKS (Rule 5)
# For disproof: searched for any credible source that SUPPORTS the 10% claim.
adversarial_checks = [
    {
        "question": (
            "Does any peer-reviewed neuroscience study support that only 10% of "
            "the brain is active at any given moment?"
        ),
        "verification_performed": (
            "Searched: 'scientific evidence supporting 10 percent brain usage theory peer reviewed'. "
            "All results were debunking articles or consensus statements. "
            "No peer-reviewed study was found that supports the 10% claim."
        ),
        "finding": (
            "No peer-reviewed neuroscience study supports the 10% claim. "
            "fMRI and PET imaging studies consistently show substantially more than 10% "
            "of brain regions active at any given time. The claim has no empirical basis."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could 'sparse coding' — the fact that not all neurons fire simultaneously — "
            "give the 10% claim any scientific grounding?"
        ),
        "verification_performed": (
            "Searched: 'neuroscience sparse coding 10 percent neurons firing simultaneously'. "
            "Reviewed neuroscience discussions on neural efficiency and sparse representation."
        ),
        "finding": (
            "Sparse coding means individual neurons fire selectively, not that only 10% of "
            "brain REGIONS are active. fMRI BOLD signal shows that even simple tasks engage "
            "many distributed brain regions simultaneously. Sparse neuron firing is "
            "fundamentally different from 10% brain usage and does not rescue the claim."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could the qualifier 'at any one time' narrow the claim to something defensible — "
            "e.g., only a fraction of the brain fires in any single millisecond?"
        ),
        "verification_performed": (
            "Reviewed neuroscience literature on neural synchrony, BOLD signal interpretation, "
            "and metabolic baseline activity. Considered whether any temporal interpretation "
            "makes the claim valid."
        ),
        "finding": (
            "Even under the most favorable temporal interpretation the claim fails. "
            "The brain's metabolic baseline — consuming 20% of the body's energy despite "
            "being 2% of body mass — requires continuous activity across many regions "
            "at all times, including during sleep. There is no timescale at which "
            "only 10% of brain regions are active while the rest are truly idle."
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
    elif not claim_holds:
        verdict = "UNDETERMINED"
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
                "description": "Independent source agreement on claim rejection",
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
