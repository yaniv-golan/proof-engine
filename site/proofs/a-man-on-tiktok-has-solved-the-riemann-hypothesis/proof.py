"""
Proof: A man on TikTok has solved the Riemann Hypothesis after one week of work.
Generated: 2026-04-07
"""
import json
import os
import sys
from datetime import date

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

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "A man on TikTok has solved the Riemann Hypothesis after one week of work."
CLAIM_FORMAL = {
    "subject": "Riemann Hypothesis \u2014 solved status",
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
        "SC3 is decisive \u2014 if SC3 is false, the whole claim is false regardless of SC1/SC2. "
        "This proof focuses on disproving SC3 via authoritative independent sources. "
        "Formalization scope: 'solved' is operationalized as 'accepted by the mathematical "
        "community,' which does not logically exclude the bare possibility of a valid proof "
        "that has not yet been recognized. However, the claim's public framing ('a man on "
        "TikTok') implies public knowledge and community awareness, making this operationalization "
        "appropriate for the claim as stated."
    ),
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_wikipedia_rh",
        "label": "Wikipedia: Riemann Hypothesis \u2014 2026 survey confirms no proof is known",
    },
    "B2": {
        "key": "source_wikipedia_mpp",
        "label": "Wikipedia: Millennium Prize Problems \u2014 RH listed among six remaining unsolved problems",
    },
    "B3": {
        "key": "source_clay",
        "label": "Clay Mathematics Institute \u2014 official problem status: Unsolved",
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
        "quote": "Unsolved",
        "url": "https://www.claymath.org/millennium/riemann-hypothesis/",
        "source_name": "Clay Mathematics Institute: Riemann Hypothesis (Millennium Prize)",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. CROSS-CHECK (Rule 6)
# B1 (Wikipedia RH article) and B2 (Wikipedia Millennium Prize Problems article) are
# independently authored pages with separate editorial histories. B3 (Clay Mathematics
# Institute) is the authoritative prize administrator. All three confirm the RH is unsolved.
COUNTABLE_STATUSES = ("verified", "partial")
b1_confirmed = citation_results.get("source_wikipedia_rh", {}).get("status") in COUNTABLE_STATUSES
b2_confirmed = citation_results.get("source_wikipedia_mpp", {}).get("status") in COUNTABLE_STATUSES
b3_confirmed = citation_results.get("source_clay", {}).get("status") in COUNTABLE_STATUSES
cross_check_agreement = b1_confirmed and b2_confirmed

# 6. SYSTEM TIME (Rule 3)
PROOF_GENERATION_DATE = date(2026, 4, 7)
today = date.today()
if today == PROOF_GENERATION_DATE:
    date_note = "System date matches proof generation date."
else:
    date_note = f"Proof generated on {PROOF_GENERATION_DATE}; running on {today}."

# 7. CLAIM EVALUATION
# Derive rh_is_solved from citation verification results — not hardcoded.
# B1 says "no proof is known"; B2 says problems "remain unsolved"; B3 says "Unsolved".
# If at least two of three sources are confirmed, the evidence establishes RH is unsolved.
n_sources_confirming_unsolved = sum([b1_confirmed, b2_confirmed, b3_confirmed])
rh_is_solved = compare(
    n_sources_confirming_unsolved, "<", 2,
    label="SC3: fewer than 2 sources confirm RH unsolved (would mean solved)"
)
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
            "The Clay Institute's 2026 Millennium Prize page still designates RH as 'Unsolved' "
            "and the $1M prize is still available. No lag in review could explain the complete "
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
            "over several years through peer-reviewed academic papers \u2014 not social media. "
            "Wikipedia MPP states the remaining six 'remain unsolved, despite a large number "
            "of unsatisfactory proofs by both amateur and professional mathematicians.'"
        ),
        "finding": (
            "No Millennium Prize Problem has ever been solved through social media or "
            "by informal one-week effort. All serious claimed proofs have come through "
            "peer-reviewed academic channels. The claim's social-media origin and one-week "
            "timeframe are inconsistent with the depth of work the Riemann Hypothesis requires, "
            "though the decisive disproof is the Clay Institute's current 'Unsolved' designation."
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

    FACT_REGISTRY["A1"]["method"] = (
        "compare(n_sources_confirming_unsolved, '<', 2) => rh_is_solved; "
        "compare(rh_is_solved, '==', True)"
    )
    FACT_REGISTRY["A1"]["result"] = (
        f"False \u2014 {n_sources_confirming_unsolved} of 3 sources confirm RH unsolved, "
        f"so rh_is_solved=False. Claim requires True."
    )

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

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
                    "B1 (Wikipedia RH article), B2 (Wikipedia MPP article), and B3 (Clay "
                    "Mathematics Institute) independently confirm the Riemann Hypothesis is "
                    "unsolved as of 2026."
                ),
                "values_compared": [
                    citation_results.get("source_wikipedia_rh", {}).get("status", "unknown"),
                    citation_results.get("source_wikipedia_mpp", {}).get("status", "unknown"),
                    citation_results.get("source_clay", {}).get("status", "unknown"),
                ],
                "agreement": cross_check_agreement,
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "rh_is_solved": rh_is_solved,
            "n_sources_confirming_unsolved": n_sources_confirming_unsolved,
            "claim_requires_solved": True,
            "claim_holds": claim_holds,
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
