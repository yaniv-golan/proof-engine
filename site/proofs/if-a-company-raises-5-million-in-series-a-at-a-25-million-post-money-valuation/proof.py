"""
Proof: Series A IRR on $5M → $500M exit in 7 years (no dilution)

Claim: If a company raises $5 million in Series A at a $25 million post-money
valuation and exits at $500 million seven years later, the annualized return
to the Series A investor exceeds 40% before dilution.

Generated: 2026-04-08
"""
import os
import sys

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

import sympy as sp
from scipy.optimize import brentq
from scripts.computations import compare, explain_calc, cross_check, emit_proof_summary

# =============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# =============================================================================
CLAIM_NATURAL = (
    "If a company raises $5 million in Series A at a $25 million post-money "
    "valuation and exits at $500 million seven years later, the annualized "
    "return to the Series A investor exceeds 40% before dilution."
)

CLAIM_FORMAL = {
    "subject": "Annualized return (CAGR) to Series A investor in described scenario",
    "property": "CAGR over 7-year hold period, before dilution",
    "operator": ">",
    "operator_note": (
        "'Before dilution' means the investor retains the full ownership stake "
        "from Series A through exit — no intermediate rounds are modeled. "
        "Ownership = invested / post-money = $5M / $25M = 20.0%. "
        "Exit proceeds = ownership × exit_value = 20% × $500M = $100M. "
        "MOIC = exit_proceeds / invested = $100M / $5M = 20x. "
        "CAGR = MOIC^(1/years) - 1 = 20^(1/7) - 1. "
        "Threshold is 0.40 (40%). The claim is TRUE if CAGR > 0.40."
    ),
    "threshold": 0.40,
}

# =============================================================================
# 2. COMPUTATIONS (Type A — pure math)
# =============================================================================

INVESTED = 5_000_000       # $5M Series A investment
POST_MONEY = 25_000_000    # $25M post-money valuation
EXIT_VALUE = 500_000_000   # $500M exit valuation
HOLD_YEARS = 7             # 7-year hold period

ownership = explain_calc(
    "INVESTED / POST_MONEY",
    {"INVESTED": INVESTED, "POST_MONEY": POST_MONEY},
    label="A1: Series A ownership stake",
)

exit_proceeds = explain_calc(
    "ownership * EXIT_VALUE",
    {"ownership": ownership, "EXIT_VALUE": EXIT_VALUE},
    label="A2: Exit proceeds (no dilution)",
)

moic = explain_calc(
    "exit_proceeds / INVESTED",
    {"exit_proceeds": exit_proceeds, "INVESTED": INVESTED},
    label="A3: MOIC (multiple on invested capital)",
)

# Primary computation: sympy exact symbolic solve
r_sym = sp.Symbol("r", positive=True)
cagr_sympy = float(
    sp.solve(sp.Eq((1 + r_sym) ** HOLD_YEARS, moic), r_sym)[0]
)
print(f"A4: CAGR (sympy exact symbolic): {cagr_sympy:.8f} = {cagr_sympy * 100:.6f}%")

# Cross-check: scipy brentq — independent NPV=0 solve
def npv_func(r):
    return -INVESTED + exit_proceeds / (1 + r) ** HOLD_YEARS

cagr_scipy = brentq(npv_func, 0.001, 5.0, xtol=1e-12)
print(f"A4-xcheck: CAGR (scipy brentq NPV=0): {cagr_scipy:.8f} = {cagr_scipy * 100:.6f}%")

cross_check(
    cagr_sympy, cagr_scipy,
    tolerance=1e-8,
    mode="absolute",
    label="A4 cross-check: sympy vs scipy CAGR agreement",
)

# =============================================================================
# 3. VERDICT
# =============================================================================
verdict_holds = compare(
    cagr_sympy, ">", CLAIM_FORMAL["threshold"],
    label="CAGR > 40% threshold",
)

VERDICT = "PROVED" if verdict_holds else "DISPROVED"

# =============================================================================
# 4. ADVERSARIAL CHECKS (Rule 5)
# =============================================================================
adversarial_checks = [
    {
        "description": "Post-money vs pre-money valuation interpretation",
        "verification_performed": (
            "Confirmed 'post-money valuation' is the standard VC term meaning valuation "
            "AFTER the investment closes. Pre-money = $25M - $5M = $20M. "
            "Investor ownership = $5M / $25M = 20.0%. No alternative interpretation "
            "of 'post-money' exists in standard VC practice."
        ),
        "breaks_proof": False,
    },
    {
        "description": "Effect of dilution if 'before dilution' caveat removed",
        "verification_performed": (
            "Modeled 3 subsequent rounds at 20% dilution each: ownership → "
            "20% × 0.80^3 ≈ 10.24%. Exit proceeds → $51.2M. MOIC → 10.24x. "
            "CAGR → 10.24^(1/7) - 1 ≈ 39.5% < 40%. "
            "The 'before dilution' qualifier is therefore load-bearing: "
            "typical dilution would push the IRR near or below 40%. "
            "The claim is mathematically correct for the stated (no-dilution) scenario."
        ),
        "breaks_proof": False,
    },
    {
        "description": "Is CAGR the correct measure for 'annualized return'?",
        "verification_performed": (
            "CAGR (compound annual growth rate) is the standard measure of annualized "
            "return for a single lump-sum investment with a single exit. It is equivalent "
            "to IRR when there are only two cash flows (initial investment and final exit). "
            "No alternative annualized return formula would change the result for this "
            "simple two-cashflow scenario."
        ),
        "breaks_proof": False,
    },
]

# =============================================================================
# 5. FACT REGISTRY
# =============================================================================
FACT_REGISTRY = {
    "A1": {"label": "ownership — Series A ownership stake", "method": None, "result": None},
    "A2": {"label": "exit_proceeds — exit proceeds with no dilution", "method": None, "result": None},
    "A3": {"label": "moic — multiple on invested capital", "method": None, "result": None},
    "A4": {"label": "cagr_sympy — annualized return (CAGR) via sympy exact solve", "method": None, "result": None},
}

# =============================================================================
# 6. JSON SUMMARY
# =============================================================================
if __name__ == "__main__":
    summary = {
        "claim_natural": CLAIM_NATURAL,
        "claim_formal": CLAIM_FORMAL,
        "fact_registry": FACT_REGISTRY,
        "cross_checks": [
            {
                "description": "sympy exact symbolic vs scipy brentq NPV=0",
                "value_a": round(cagr_sympy, 8),
                "value_b": round(cagr_scipy, 8),
                "tolerance": 1e-8,
                "passed": abs(cagr_sympy - cagr_scipy) <= 1e-8,
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": VERDICT,
                "key_results": {
            "ownership_pct": round(ownership * 100, 4),
            "moic": round(moic, 6),
            "cagr_pct": round(cagr_sympy * 100, 4),
            "threshold_pct": CLAIM_FORMAL["threshold"] * 100,
            "claim_holds": cagr_sympy > CLAIM_FORMAL["threshold"],
        },
        "generator": {
            "name": "proof-engine",
            "version": "1.11.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-04-08",
        },
    }
    emit_proof_summary(summary)
