"""
Proof: VC fund vintage 2012-2016 median net IRR — Cambridge 16.8% vs Preqin 18.2%

Claim: Venture capital funds vintage 2012-2016 have a median net IRR of 16.8%
according to Cambridge Associates but 18.2% according to Preqin.

Generated: 2026-04-08
"""
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.computations import compare, emit_proof_summary
from scripts.verify_citations import verify_all_citations

# =============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# =============================================================================
CLAIM_NATURAL = (
    "Venture capital funds vintage 2012-2016 have a median net IRR of 16.8% "
    "according to Cambridge Associates but 18.2% according to Preqin."
)

CLAIM_FORMAL = {
    "subject": "Median net IRR of US venture capital funds with vintage years 2012-2016",
    "property": "Median net Internal Rate of Return as reported by two specific benchmarking firms",
    "operator": "==",
    "operator_note": (
        "The claim asserts two specific empirical figures from two specific named sources: "
        "(SC1) Cambridge Associates reports a median net IRR of 16.8% for VC vintage 2012-2016, "
        "and (SC2) Preqin reports 18.2% for the same cohort. "
        "'Net IRR' means after management fees and carried interest. "
        "'Vintage year' refers to the year a fund made its first investment. "
        "Both Cambridge Associates and Preqin are subscription-only benchmarking databases; "
        "their full benchmark tables are not publicly accessible. "
        "Verification requires either: (a) a paid subscription to these databases, "
        "(b) a publicly available press release or summary report citing these exact figures, "
        "or (c) an academic paper reproducing these specific data points with attribution."
    ),
    "threshold": 2,  # sub-claims
    "compound_operator": "AND",
}

# =============================================================================
# 2. EMPIRICAL FACTS — Sub-claim SC1: Cambridge Associates 16.8%
# =============================================================================
# No verified public source found for this specific figure.
# Searched: Cambridge Associates public benchmark page (cambridgeassociates.com/research/),
# CA public PDF reports (Q3 2025 benchmarks — image-based, no per-vintage tables),
# academic papers citing CA data, news coverage, institutional investor articles.
# All benchmark data is behind a subscription paywall.

empirical_facts_sc1 = {}  # No verified sources
n_confirmed_sc1 = 0
sc1_threshold = 1

# =============================================================================
# 3. EMPIRICAL FACTS — Sub-claim SC2: Preqin 18.2%
# =============================================================================
# No verified public source found for this specific figure.
# Searched: Preqin benchmarks landing page (preqin.com/benchmarks),
# Preqin press releases, Alternatives Watch, Institutional Investor,
# Bain and McKinsey PE/VC annual reports citing Preqin figures,
# SSRN academic papers referencing Preqin VC IRR vintage data.
# All Preqin benchmark data is behind a subscription paywall.

empirical_facts_sc2 = {}  # No verified sources
n_confirmed_sc2 = 0
sc2_threshold = 1

# =============================================================================
# 4. SUB-CLAIM VERDICTS
# =============================================================================
citation_results = verify_all_citations({})  # No public sources available
sc1_holds = compare(n_confirmed_sc1, ">=", sc1_threshold,
                    label="SC1: Cambridge 16.8% sources confirmed")
sc2_holds = compare(n_confirmed_sc2, ">=", sc2_threshold,
                    label="SC2: Preqin 18.2% sources confirmed")

all_sc_hold = sc1_holds and sc2_holds

# =============================================================================
# 5. ADVERSARIAL CHECKS (Rule 5)
# =============================================================================
adversarial_checks = [
    {
        "description": "Are Cambridge Associates benchmark figures publicly available at all?",
        "verification_performed": (
            "Searched cambridgeassociates.com/research/ — the benchmark landing page confirms "
            "they publish US PE and VC benchmarks but requires a subscription or institutional "
            "access. The Q3 2025 public PDF (ca.com) contains only aggregate 5/10/20-year "
            "horizon returns, not per-vintage-year median net IRR tables. "
            "No public summary report containing '16.8%' for VC vintage 2012-2016 was found "
            "in over 30 URL attempts across CA's site, academic databases (SSRN, NBER), "
            "and financial news outlets."
        ),
        "breaks_proof": True,
    },
    {
        "description": "Are Preqin benchmark figures publicly available at all?",
        "verification_performed": (
            "Searched preqin.com/benchmarks — requires login. Searched Preqin press releases "
            "and the Preqin Global Alternatives Reports (annual public PDFs): these cite "
            "aggregate venture return quartiles but not the specific 18.2% vintage 2012-2016 "
            "median net IRR figure. Searched 'Preqin venture 2012 2016 IRR 18.2' in Google "
            "and academic databases — no match found. No public source contains this figure."
        ),
        "breaks_proof": True,
    },
    {
        "description": "Do the two figures (16.8% vs 18.2%) appear in any secondary source?",
        "verification_performed": (
            "Searched for the specific pairing '16.8% Cambridge Associates' and '18.2% Preqin' "
            "in financial literature. No secondary source reproduces both figures together for "
            "VC vintage 2012-2016. The figures may be correct but originate from proprietary "
            "database downloads that are not publicly citable. The 1.4 percentage-point gap "
            "is plausible given known methodology differences (CA uses cash-on-cash timing; "
            "Preqin uses its own fund database with different fund universe and valuation timing)."
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
    "SC1": {"label": "Cambridge Associates: median net IRR for VC vintage 2012-2016 = 16.8% — no public source found"},
    "SC2": {"label": "Preqin: median net IRR for VC vintage 2012-2016 = 18.2% — no public source found"},
}

# =============================================================================
# 8. JSON SUMMARY
# =============================================================================
if __name__ == "__main__":
    summary = {
        "claim_natural": CLAIM_NATURAL,
        "claim_formal": CLAIM_FORMAL,
        "fact_registry": FACT_REGISTRY,
        "sub_claim_results": {
            "sc1": {
                "description": "Cambridge Associates reports 16.8% median net IRR for VC vintage 2012-2016",
                "n_confirmed": n_confirmed_sc1,
                "threshold": sc1_threshold,
                "holds": sc1_holds,
            },
            "sc2": {
                "description": "Preqin reports 18.2% median net IRR for VC vintage 2012-2016",
                "n_confirmed": n_confirmed_sc2,
                "threshold": sc2_threshold,
                "holds": sc2_holds,
            },
        },
        "adversarial_checks": adversarial_checks,
        "verdict": VERDICT,
                "verdict_reason": (
            "Both sub-claims rely on proprietary subscription-only databases "
            "(Cambridge Associates and Preqin). No publicly accessible source was found "
            "that reproduces the specific figures (16.8% and 18.2%) for VC vintage 2012-2016. "
            "Verification would require paid access to these benchmarking services."
        ),
        "key_results": {
            "sc1_cambridge_confirmed": sc1_holds,
            "sc2_preqin_confirmed": sc2_holds,
            "claim_holds": all_sc_hold and not any_breaks,
        },
        "generator": {
            "name": "proof-engine",
            "version": "1.11.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-04-08",
        },
    }
    emit_proof_summary(summary)
