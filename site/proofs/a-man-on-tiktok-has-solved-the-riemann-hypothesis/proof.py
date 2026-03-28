"""
Proof: A man on TikTok has solved the Riemann Hypothesis after one week of work.
Generated: 2026-03-28
"""
import json
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "A man on TikTok has solved the Riemann Hypothesis after one week of work."
CLAIM_FORMAL = {
    "subject": "Riemann Hypothesis — solved status",
    "property": "whether a valid proof has been accepted by the mathematical community",
    "operator": "==",
    "threshold": True,
    "claim_type": "compound_empirical",
    "operator_note": (
        "The claim asserts the Riemann Hypothesis has been 'solved'. "
        "For this to be true, a correct proof must exist and have been accepted by the "
        "mathematical community. The Clay Mathematics Institute (CMI) administers a $1 million "
        "Millennium Prize for a correct solution; non-award of this prize is treated as "
        "authoritative evidence the hypothesis remains unsolved. "
        "The claim has three sub-claims: (SC1) the solver is a man on TikTok; "
        "(SC2) the work took ~1 week; (SC3) the solution is mathematically valid. "
        "SC3 is decisive — if SC3 is false, the whole claim is false regardless of SC1/SC2. "
        "This proof focuses on disproving SC3 via authoritative independent sources."
    ),
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_wikipedia_rh",
        "label": "Wikipedia: Riemann Hypothesis — 2026 survey confirms no proof is known",
    },
    "B2": {
        "key": "source_wikipedia_mpp",
        "label": "Wikipedia: Millennium Prize Problems — RH listed among six remaining unsolved problems",
    },
    "B3": {
        "key": "source_clay",
        "label": "Clay Mathematics Institute — official Millennium Prize page for Riemann Hypothesis",
    },
    "A1": {
        "label": "Logical conclusion: if RH is unsolved per authoritative sources, no TikTok claim can constitute a valid solution",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS
empirical_facts = {
    "source_wikipedia_rh": {
        "quote": (
            "According to a 2026 survey, there is overwhelming numerical evidence "
            "for the hypothesis, but no proof is known."
        ),
        "url": "https://en.wikipedia.org/wiki/Riemann_hypothesis",
        "source_name": "Wikipedia: Riemann Hypothesis",
    },
    "source_wikipedia_mpp": {
        "quote": (
            "The other six Millennium Prize Problems remain unsolved, despite a large number "
            "of unsatisfactory proofs by both amateur and professional mathematicians."
        ),
        "url": "https://en.wikipedia.org/wiki/Millennium_Prize_Problems",
        "source_name": "Wikipedia: Millennium Prize Problems",
    },
    "source_clay": {
        "quote": (
            "The Riemann hypothesis asserts that all the "
            "\u2018non-obvious\u2019 zeros of the zeta function are complex numbers "
            "with real part 1/2."
        ),
        "url": "https://www.claymath.org/millennium/riemann-hypothesis/",
        "source_name": "Clay Mathematics Institute: Riemann Hypothesis (Millennium Prize)",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. CROSS-CHECK (Rule 6)
# B1 (Wikipedia RH article) and B2 (Wikipedia Millennium Prize Problems article) are
# independently authored pages with separate editorial histories. Both confirm the
# Riemann Hypothesis has no accepted proof as of 2026.
b1_confirmed = citation_results.get("source_wikipedia_rh", {}).get("status") in ("verified", "partial")
b2_confirmed = citation_results.get("source_wikipedia_mpp", {}).get("status") in ("verified", "partial")
cross_check_agreement = b1_confirmed and b2_confirmed

# 6. SYSTEM TIME (Rule 3) — anchor proof to current date for reproducibility
PROOF_GENERATION_DATE = date(2026, 3, 28)
today = date.today()
if today == PROOF_GENERATION_DATE:
    date_note = "System date matches proof generation date."
else:
    date_note = f"Proof generated on {PROOF_GENERATION_DATE}; running on {today}."

# 7. CLAIM EVALUATION
# The Riemann Hypothesis is still officially unsolved per B1 and B2.
# The claim requires rh_is_solved == True; evidence establishes rh_is_solved = False.
rh_is_solved = False  # established by B1 ("no proof is known") and B2 ("remain unsolved")
claim_holds = compare(
    rh_is_solved, "==", True,
    label="SC3: Riemann Hypothesis is validly solved"
)

# 8. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": (
            "Has any TikTok-based claimed solution been evaluated as credible by mathematicians?"
        ),
        "verification_performed": (
            "Searched 'Riemann Hypothesis TikTok viral claim debunked mathematician response 2024 2025'. "
            "Found TikTok discovery pages showing many users claiming to solve RH. "
            "Found a video by @blitzphd explicitly debunking one such claim: "
            "'Dude didn't solve the Riemann hypothesis'. "
            "Found no credible mathematical evaluation of any TikTok-originating claimed solution."
        ),
        "finding": (
            "No TikTok-based claimed solution has been verified or accepted by the mathematical "
            "community. The pattern of amateur claimed proofs is consistent with Wikipedia's "
            "statement that 'a large number of unsatisfactory proofs by both amateur and "
            "professional mathematicians' have been submitted over the years."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could a valid proof have been very recently submitted and not yet reviewed "
            "by the Clay Institute or wider community?"
        ),
        "verification_performed": (
            "Searched 'Riemann Hypothesis solved 2025 2026 Clay Mathematics Institute status'. "
            "Found a 2026 status report (mathlumen.com) stating: "
            "'In 2026, after 167 years, the Riemann Hypothesis remains open.' "
            "Noted that high-profile claimed proofs (e.g., Michael Atiyah, 2018) are evaluated "
            "by the global mathematical community within days of submission. "
            "No pending proof evaluation found."
        ),
        "finding": (
            "The mathematical community responds rapidly to claimed proofs of famous problems. "
            "The Clay Institute's 2026 Millennium Prize page still lists RH as unsolved and "
            "the $1M prize is still available. No lag in review could explain the complete "
            "absence of any accepted or even actively-evaluated proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Has any Millennium Prize Problem ever been solved through social media or "
            "by an amateur working alone for one week?"
        ),
        "verification_performed": (
            "Reviewed history of solved Millennium Prize Problems. "
            "The only solved problem, the Poincare conjecture, was proved by Grigori Perelman "
            "over several years through peer-reviewed academic papers — not social media. "
            "Wikipedia MPP states the remaining six 'remain unsolved, despite a large number "
            "of unsatisfactory proofs by both amateur and professional mathematicians.'"
        ),
        "finding": (
            "No Millennium Prize Problem has ever been solved through social media or "
            "by informal one-week effort. All serious claimed proofs have come through "
            "peer-reviewed academic channels. The claim's social-media origin and one-week "
            "timeframe are inconsistent with the depth of work the Riemann Hypothesis requires, "
            "though the decisive disproof is the Clay Institute's current 'unsolved' designation."
        ),
        "breaks_proof": False,
    },
]

# 9. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    if not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = "compare(rh_is_solved, '==', True)"
    FACT_REGISTRY["A1"]["result"] = (
        f"False — rh_is_solved={rh_is_solved}, claim requires True. "
        f"Two independent sources (B1, B2) confirm no proof is known."
    )

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # No value extraction in this qualitative proof (Rule 1 auto-passes)
    extractions = {}

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
                    "B1 (Wikipedia RH article) and B2 (Wikipedia MPP article) independently "
                    "confirm the Riemann Hypothesis is unsolved as of 2026 — different pages, "
                    "different editorial histories, same conclusion."
                ),
                "values_compared": [
                    citation_results.get("source_wikipedia_rh", {}).get("status", "unknown"),
                    citation_results.get("source_wikipedia_mpp", {}).get("status", "unknown"),
                ],
                "agreement": cross_check_agreement,
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "rh_is_solved": rh_is_solved,
            "claim_requires_solved": True,
            "claim_holds": claim_holds,
            "sources_confirming_unsolved": 2,
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
