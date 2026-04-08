"""
Proof: SaaS VC exit multiple 8.5x invested capital vs consumer internet

Claim: The average exit multiple for SaaS venture-backed companies is 8.5x
invested capital, higher than for consumer internet companies.

Generated: 2026-04-08
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.computations import compare
from scripts.verify_citations import verify_all_citations

# =============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# =============================================================================
CLAIM_NATURAL = (
    "The average exit multiple for SaaS venture-backed companies is 8.5x "
    "invested capital, higher than for consumer internet companies."
)

CLAIM_FORMAL = {
    "subject": "Average exit multiple for SaaS venture-backed companies",
    "property": "Multiple of invested capital (MOIC) at exit, compared to consumer internet",
    "operator": "==",
    "operator_note": (
        "The claim asserts two things: (SC1) the average SaaS exit multiple is 8.5× invested "
        "capital (MOIC — not EV/Revenue), and (SC2) this exceeds the consumer internet average. "
        "'Multiple of invested capital' (MOIC or TVPI) measures (total exit value) / "
        "(total capital invested), the standard VC return metric. "
        "This is distinct from EV/Revenue multiples (valuation relative to annual revenue), "
        "which is a separate measure used in M&A pricing. "
        "Public SaaS M&A data typically reports EV/Revenue, not MOIC. "
        "MOIC data by sector requires access to proprietary VC fund databases "
        "(PitchBook, CB Insights premium, Carta). "
        "No public source was found providing average MOIC by sector for VC-backed exits."
    ),
    "threshold": 2,
    "compound_operator": "AND",
}

# =============================================================================
# 2. EMPIRICAL FACTS — SC1: SaaS average exit MOIC = 8.5×
# =============================================================================
# Searched extensively for public MOIC data on SaaS VC-backed exits.
# Public sources (Aventis Advisors 543-deal SaaS M&A study, SaaS Capital annual surveys,
# PitchBook SaaS research) report EV/Revenue multiples (median ~4.5x, top quartile ~8.1x),
# NOT MOIC. No public aggregate SaaS MOIC figure was found.
# The "8.5x" figure as EV/Revenue would represent top-quartile, not average.

empirical_facts_sc1 = {}
n_confirmed_sc1 = 0
sc1_threshold = 2

# =============================================================================
# 3. EMPIRICAL FACTS — SC2: SaaS MOIC > consumer internet MOIC
# =============================================================================
# No public source provides both SaaS MOIC and consumer internet MOIC for comparison.
# Without SC1 being verified, SC2 (the comparison) also cannot be established.

empirical_facts_sc2 = {}
n_confirmed_sc2 = 0
sc2_threshold = 2

# =============================================================================
# 4. SUB-CLAIM VERDICTS
# =============================================================================
citation_results = verify_all_citations({})  # No public sources available
sc1_holds = compare(n_confirmed_sc1, ">=", sc1_threshold,
                    label="SC1: SaaS 8.5x MOIC confirmed by public sources")
sc2_holds = compare(n_confirmed_sc2, ">=", sc2_threshold,
                    label="SC2: SaaS MOIC > consumer internet MOIC confirmed")

all_sc_hold = sc1_holds and sc2_holds

# =============================================================================
# 5. ADVERSARIAL CHECKS (Rule 5)
# =============================================================================
adversarial_checks = [
    {
        "description": "Is the 8.5x figure actually EV/Revenue rather than MOIC?",
        "verification_performed": (
            "Searched for '8.5x SaaS' in financial literature. Found: Aventis Advisors "
            "(543 SaaS M&A deals, 2015-2026) reports top-quartile EV/Revenue above 8.1× "
            "and median EV/Revenue at 4.5×. SaaS Capital annual private SaaS surveys report "
            "EV/NTM Revenue medians ranging 3.3×-6.4× depending on year. "
            "The 8.5× figure, if it exists, almost certainly refers to EV/Revenue "
            "(enterprise value as a multiple of annual revenue), not MOIC "
            "(exit value as a multiple of capital invested). These are fundamentally "
            "different metrics and not interchangeable."
        ),
        "breaks_proof": True,
    },
    {
        "description": "Is MOIC data by sector publicly available from any source?",
        "verification_performed": (
            "Searched PitchBook, CB Insights, Carta, NVCA, and academic databases for "
            "sector-level MOIC data on VC-backed exits. All primary MOIC databases require "
            "paid subscriptions. The Kauffman Foundation and NVCA publish aggregate VC "
            "return data but not sector breakdowns by MOIC. No public source provides "
            "average MOIC for SaaS specifically."
        ),
        "breaks_proof": True,
    },
    {
        "description": "Are there any academic papers reporting SaaS vs consumer internet MOIC?",
        "verification_performed": (
            "Searched SSRN, NBER, and Google Scholar for VC exit multiples by sector. "
            "Found papers on VC returns generally (Gompers, Kaplan, Metrick) but none "
            "that isolate SaaS vs consumer internet MOIC with a 8.5× benchmark. "
            "The SaaS category as a distinct VC sector is relatively recent (<2015 mainstream) "
            "and longitudinal MOIC data is sparse even in academic literature."
        ),
        "breaks_proof": True,
    },
]

any_breaks = any(c["breaks_proof"] for c in adversarial_checks)

# =============================================================================
# 6. VERDICT
# =============================================================================
if any_breaks or not all_sc_hold:
    VERDICT = "UNDETERMINED"
else:
    VERDICT = "PROVED"

verdict_holds = compare(int(all_sc_hold and not any_breaks), ">=", 1,
                        label="Overall verdict holds")

# =============================================================================
# 7. FACT REGISTRY
# =============================================================================
FACT_REGISTRY = {
    "SC1": {"label": "SaaS average exit MOIC = 8.5× — no public source found; 8.5× EV/Revenue found but is a different metric"},
    "SC2": {"label": "SaaS MOIC > consumer internet MOIC — no public comparable data found"},
}

# =============================================================================
# 8. JSON SUMMARY
# =============================================================================
if __name__ == "__main__":
    summary = {
        "claim_natural": CLAIM_NATURAL,
        "claim_formal": CLAIM_FORMAL,
        "fact_registry": FACT_REGISTRY,
        "sub_claims": {
            "sc1": {
                "description": "Average SaaS exit multiple is 8.5× invested capital (MOIC)",
                "n_confirmed": n_confirmed_sc1,
                "threshold": sc1_threshold,
                "holds": sc1_holds,
            },
            "sc2": {
                "description": "SaaS exit multiple exceeds consumer internet exit multiple",
                "n_confirmed": n_confirmed_sc2,
                "threshold": sc2_threshold,
                "holds": sc2_holds,
            },
        },
        "adversarial_checks": adversarial_checks,
        "verdict": VERDICT,
        "verdict_holds": verdict_holds,
        "verdict_reason": (
            "The specific metric in the claim (MOIC — multiple of invested capital) is not "
            "publicly available by sector. Public sources report EV/Revenue multiples for SaaS, "
            "which is a different metric. No public source provides average MOIC for SaaS "
            "or a SaaS vs consumer internet MOIC comparison."
        ),
        "key_results": {
            "n_confirmed_sc1": n_confirmed_sc1,
            "n_confirmed_sc2": n_confirmed_sc2,
            "any_breaks": any_breaks,
            "claim_holds": all_sc_hold and not any_breaks,
        },
        "generator": {
            "name": "proof-engine",
            "version": "1.11.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-04-08",
        },
    }
    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2))
