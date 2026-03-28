"""
Proof: The phrase "rule of thumb" originated from an old English law that
allowed a man to beat his wife with a stick no thicker than his thumb.
Generated: 2026-03-28
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    'The phrase "rule of thumb" originated from an old English law that allowed '
    "a man to beat his wife with a stick no thicker than his thumb."
)
CLAIM_FORMAL = {
    "subject": 'The phrase "rule of thumb"',
    "property": "etymological origin linked to a specific English law permitting wife-beating",
    "operator": ">=",
    "operator_note": (
        "This is a compound claim: (1) an old English law existed permitting a man to beat "
        "his wife with a stick no thicker than his thumb, AND (2) this law is the origin of "
        'the phrase "rule of thumb." Both sub-claims must be true for the claim to hold. '
        "We attempt to disprove by finding >= 3 independent authoritative sources that reject "
        "these sub-claims. Sources must be from different institutions/publications."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "wikipedia", "label": "Wikipedia: no such law ever existed"},
    "B2": {"key": "phrases_org", "label": "Phrases.org.uk: no printed records associate phrase with domestic violence until 1970s"},
    "B3": {"key": "uoregon", "label": "U. Oregon legal scholar: no truth in the legend"},
    "B4": {"key": "allthatsinteresting", "label": "All That's Interesting: no evidence Buller said anything of the sort"},
    "A1": {"label": "Verified source count rejecting the claim", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (disproof direction)
empirical_facts = {
    "wikipedia": {
        "quote": (
            "A modern folk etymology holds that the phrase is derived from the maximum "
            "width of a stick allowed for wife-beating under English common law, but "
            "no such law ever existed."
        ),
        "url": "https://en.wikipedia.org/wiki/Rule_of_thumb",
        "source_name": "Wikipedia — Rule of thumb",
    },
    "phrases_org": {
        "quote": (
            "Despite the phrase being in common use since the 17th century and "
            "appearing many thousands of times in print, there are no printed records "
            "that associate it with domestic violence until the 1970s"
        ),
        "url": "https://phrases.org.uk/meanings/rule-of-thumb.html",
        "source_name": "Phrases.org.uk — Rule of Thumb meaning and origin",
    },
    "uoregon": {
        "quote": (
            "there is probably no truth whatever in the legend that he was permitted "
            "to beat her with a stick no thicker than his thumb"
        ),
        "url": "https://dynamic.uoregon.edu/jjf/essays/ruleofthumb.html",
        "source_name": "University of Oregon — Rule of Thumb essay (Prof. J.J. Freund)",
    },
    "allthatsinteresting": {
        "quote": (
            "There is no evidence that Buller actually said anything of the sort, "
            "but he was mocked in the press."
        ),
        "url": "https://allthatsinteresting.com/rule-of-thumb-origin",
        "source_name": "All That's Interesting — Rule of Thumb Origin",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — MUST use compare()
claim_holds = compare(n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                      label="verified source count vs threshold")

# 7. ADVERSARIAL CHECKS (Rule 5)
# These document Step 2 research — searching for evidence that SUPPORTS the claim.
adversarial_checks = [
    {
        "question": "Was there ever an actual English law specifying a thumb-width stick for wife-beating?",
        "verification_performed": (
            "Searched for 'rule of thumb wife beating law evidence historical support Buller ruling'. "
            "Reviewed Wikipedia, Phrases.org.uk, University of Oregon essay, and allthatsinteresting.com. "
            "Also reviewed the Sir Francis Buller / Judge Thumb incident of 1782."
        ),
        "finding": (
            "No such law was ever codified in English common law. Sir Francis Buller was rumored "
            "in 1782 to have stated a husband could beat his wife with a stick no wider than his "
            "thumb, but there is no record he actually made this ruling. He was satirized as "
            "'Judge Thumb.' Some 19th-century American courts referenced a supposed common-law "
            "doctrine, but legal scholars (including Henry Ansgar Kelly) confirm no such law existed."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the phrase have originated from the wife-beating association even without a formal law?",
        "verification_performed": (
            "Searched for earliest documented uses of 'rule of thumb' and when the wife-beating "
            "association first appeared. Checked multiple etymology sources."
        ),
        "finding": (
            "The phrase first appeared in print in 1658/1685 (James Durham's sermons), referring to "
            "rough practical measurement. The first recorded link between the phrase and wife-beating "
            "appeared only in 1976, in a report by women's-rights advocate Del Martin. The phrase "
            "predates the false association by roughly 300 years, ruling out this etymology."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Are the three disproof sources truly independent?",
        "verification_performed": (
            "Checked source independence: Wikipedia cites multiple scholarly references; "
            "Phrases.org.uk is an independent etymology reference site; University of Oregon "
            "essay is an academic source citing legal historian Henry Ansgar Kelly's research."
        ),
        "finding": (
            "Sources are from different institutions (Wikimedia Foundation, Gary Martin's "
            "Phrases.org.uk, University of Oregon). While they cite overlapping primary research "
            "(e.g., Kelly's work), they are independently published and maintained."
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
        verdict = ("DISPROVED (with unverified citations)" if is_disproof
                   else "PROVED (with unverified citations)")
    elif not claim_holds:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = str(n_confirmed)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: for qualitative proofs, each B-type fact records citation status
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
                "description": "Multiple independent sources consulted to reject the claim",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from different institutions: Wikimedia Foundation (Wikipedia), "
                    "Gary Martin's Phrases.org.uk, University of Oregon academic essay. "
                    "While they cite overlapping primary research, they are independently "
                    "published and maintained."
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
