"""
Proof: A venture capital fund investing $50 million in 25 startups at equal sizes
requires at least one 50x return and two 10x returns to achieve a 3x gross multiple.

Generated: 2026-04-08
"""
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date

from scripts.computations import compare, explain_calc, emit_proof_summary

# =============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# =============================================================================
CLAIM_NATURAL = (
    "A venture capital fund investing $50 million in 25 startups at equal sizes "
    "requires at least one 50x return and two 10x returns to achieve a 3x gross multiple."
)

CLAIM_FORMAL = {
    "subject": "A VC fund with $50M invested equally across 25 startups",
    "property": "whether 1×50x + 2×10x returns (others=0) achieves a 3x gross multiple",
    "operator": "==",
    "operator_note": (
        "Interpreted as a sufficiency claim: the stated returns (1 company at 50x, 2 at 10x, "
        "22 at 0x) are sufficient to achieve a 3x gross multiple. "
        "Per-company investment: $50M/25 = $2M. "
        "Required return for 3x gross: $50M × 3 = $150M. "
        "Actual return under claimed scenario: (1×50 + 2×10)×$2M = $140M. "
        "$140M < $150M, so the claim is false. "
        "The claim also fails as a necessity claim: 3x is reachable without any 50x return."
    ),
    "threshold": 3.0,
    "proof_direction": "disprove",
}

# =============================================================================
# 2. FACT REGISTRY — A-types only for pure math
# =============================================================================
FACT_REGISTRY = {
    "A1": {
        "label": "Per-company investment: $50M / 25 companies = $2M each",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "Total return under claimed scenario: (1×50 + 2×10) × $2M = $140M",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "Gross multiple achieved: $140M / $50M = 2.8x",
        "method": None,
        "result": None,
    },
    "A4": {
        "label": "Cross-check via direct portfolio sum: 1×$100M + 2×$20M + 22×$0M = $140M",
        "method": None,
        "result": None,
    },
    "A5": {
        "label": "Claim evaluation: gross_multiple == 3.0",
        "method": None,
        "result": None,
    },
}

# =============================================================================
# 3. COMPUTATION — primary method (Rule 7)
# =============================================================================
print("=" * 60)
print("COMPUTATION")
print("=" * 60)

# Fund parameters
fund_size_m = 50.0      # $50M total fund
n_companies = 25        # equal-size investments
required_multiple = 3.0 # claimed gross multiple

# Per-company investment
per_company_m = explain_calc(
    "fund_size_m / n_companies",
    {"fund_size_m": fund_size_m, "n_companies": n_companies},
    label="A1: per-company investment ($M)",
)
print(f"  -> ${per_company_m:.1f}M per company")

# Required total return for 3x gross
required_return_m = explain_calc(
    "fund_size_m * required_multiple",
    {"fund_size_m": fund_size_m, "required_multiple": required_multiple},
    label="Required total return for 3x gross ($M)",
)
print(f"  -> ${required_return_m:.0f}M needed")

# Returns under the claimed scenario: 1 company at 50x, 2 at 10x, 22 at 0x
n_50x = 1
n_10x = 2
multiple_50x = 50.0
multiple_10x = 10.0

winner_50x_return_m = explain_calc(
    "n_50x * multiple_50x * per_company_m",
    {"n_50x": n_50x, "multiple_50x": multiple_50x, "per_company_m": per_company_m},
    label="Return from 50x winner ($M)",
)
winner_10x_return_m = explain_calc(
    "n_10x * multiple_10x * per_company_m",
    {"n_10x": n_10x, "multiple_10x": multiple_10x, "per_company_m": per_company_m},
    label="Return from 10x winners ($M)",
)

total_return_m = explain_calc(
    "winner_50x_return_m + winner_10x_return_m",
    {"winner_50x_return_m": winner_50x_return_m, "winner_10x_return_m": winner_10x_return_m},
    label="A2: total return under claimed scenario ($M)",
)

# Gross multiple achieved
gross_multiple = explain_calc(
    "total_return_m / fund_size_m",
    {"total_return_m": total_return_m, "fund_size_m": fund_size_m},
    label="A3: gross multiple achieved",
)

shortfall_m = explain_calc(
    "required_return_m - total_return_m",
    {"required_return_m": required_return_m, "total_return_m": total_return_m},
    label="Shortfall from 3x target ($M)",
)
print(f"  -> The scenario falls ${shortfall_m:.0f}M short of the $150M needed for 3x")

# =============================================================================
# 4. CROSS-CHECK — mathematically independent method (Rule 6)
# =============================================================================
print("\n" + "=" * 60)
print("CROSS-CHECK")
print("=" * 60)

# Independent method: list each company's return explicitly and sum
# Company 1: 50x on $2M = $100M
# Companies 2-3: 10x on $2M each = $20M each = $40M total
# Companies 4-25: 0x on $2M each = $0
company_returns = (
    [n_50x * multiple_50x * per_company_m]       # 1 company at 50x
    + [multiple_10x * per_company_m] * n_10x     # 2 companies at 10x
    + [0.0] * (n_companies - n_50x - n_10x)      # 22 companies at 0x
)
print(f"  Portfolio breakdown: {len(company_returns)} companies")
print(f"    Company 1 (50x): ${company_returns[0]:.1f}M")
print(f"    Companies 2-3 (10x each): ${company_returns[1]:.1f}M, ${company_returns[2]:.1f}M")
print(f"    Companies 4-25 (0x): $0.0M each")

crosscheck_total_m = sum(company_returns)
crosscheck_multiple = crosscheck_total_m / fund_size_m
print(f"  A4: Sum of all company returns = ${crosscheck_total_m:.1f}M")
print(f"  Cross-check gross multiple: ${crosscheck_total_m:.1f}M / ${fund_size_m:.0f}M = {crosscheck_multiple:.4f}x")

assert abs(gross_multiple - crosscheck_multiple) < 1e-9, (
    f"Cross-check failed: primary={gross_multiple}, crosscheck={crosscheck_multiple}"
)
print(f"  Cross-check: {gross_multiple:.4f}x == {crosscheck_multiple:.4f}x [AGREE]")

# =============================================================================
# 5. ADVERSARIAL CHECKS (Rule 5)
# =============================================================================
print("\n" + "=" * 60)
print("ADVERSARIAL CHECKS")
print("=" * 60)

# Alternative scenario 1: can 3x be achieved WITHOUT a 50x return?
# E.g., 15 companies at 5x each: 15 × 5 × $2M = $150M → 3x gross
alt1_n = 15
alt1_multiple = 5.0
alt1_return_m = alt1_n * alt1_multiple * per_company_m
alt1_gross = alt1_return_m / fund_size_m
print(f"\nAdversarial check 1: Can 3x be achieved without any 50x return?")
print(f"  Alternative: {alt1_n} companies at {alt1_multiple}x each")
print(f"  Return: {alt1_n} × {alt1_multiple} × ${per_company_m:.1f}M = ${alt1_return_m:.1f}M")
print(f"  Gross multiple: ${alt1_return_m:.1f}M / ${fund_size_m:.0f}M = {alt1_gross:.2f}x")

# Alternative scenario 2: 5 companies at 15x each
alt2_n = 5
alt2_multiple = 15.0
alt2_return_m = alt2_n * alt2_multiple * per_company_m
alt2_gross = alt2_return_m / fund_size_m
print(f"\n  Alternative: {alt2_n} companies at {alt2_multiple}x each")
print(f"  Return: {alt2_n} × {alt2_multiple} × ${per_company_m:.1f}M = ${alt2_return_m:.1f}M")
print(f"  Gross multiple: ${alt2_return_m:.1f}M / ${fund_size_m:.0f}M = {alt2_gross:.2f}x")

# Alternative scenario 3: what if the fund had 20 companies instead of 25?
alt3_fund = 50.0
alt3_n = 20
alt3_per_co = alt3_fund / alt3_n   # $2.5M each
alt3_return = (1 * 50 + 2 * 10) * alt3_per_co   # same pattern, larger checks
alt3_gross = alt3_return / alt3_fund
print(f"\nAdversarial check 2: What if 20 companies instead of 25 (same portfolio pattern)?")
print(f"  Per-company: $50M / 20 = ${alt3_per_co:.1f}M")
print(f"  Return: (1×50 + 2×10) × ${alt3_per_co:.1f}M = ${alt3_return:.1f}M")
print(f"  Gross multiple: ${alt3_return:.1f}M / ${alt3_fund:.0f}M = {alt3_gross:.2f}x")
print(f"  Still < 3.0x? {alt3_gross < 3.0}")

adversarial_checks = [
    {
        "question": (
            "Can a 3x gross multiple be achieved without any 50x return? "
            "If yes, the 'necessity' reading of the claim is also false."
        ),
        "verification_performed": (
            "Computed two alternative portfolios: "
            "(a) 15 companies at 5x each: 15 × 5 × $2M = $150M → 3.0x gross. "
            "(b) 5 companies at 15x each: 5 × 15 × $2M = $150M → 3.0x gross. "
            "Both achieve exactly 3x without any 50x return."
        ),
        "finding": (
            f"3x gross is achievable without any 50x return. "
            f"Example: {alt1_n} companies at {alt1_multiple}x each yields {alt1_gross:.1f}x gross; "
            f"{alt2_n} companies at {alt2_multiple}x each yields {alt2_gross:.1f}x gross. "
            "The claim fails as a necessity condition as well as a sufficiency condition."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "What if the fund has fewer companies (e.g., 20 instead of 25), "
            "keeping the same 1×50x + 2×10x pattern? Does the gross multiple change?"
        ),
        "verification_performed": (
            f"Computed: $50M / 20 companies = $2.5M each. "
            f"Return: (1×50 + 2×10) × $2.5M = ${alt3_return:.1f}M. "
            f"Gross multiple: ${alt3_return:.1f}M / $50M = {alt3_gross:.2f}x."
        ),
        "finding": (
            f"With 20 equal-size investments, the same 1×50x + 2×10x pattern yields "
            f"{alt3_gross:.2f}x gross — which exceeds 3x. "
            "This shows the number of companies matters critically: "
            "the minimum required per-company investment to reach 3x with 1×50x + 2×10x "
            "is $150M / 70 = $2.143M, which requires ≤ 23 companies in a $50M fund. "
            "The claim specifies 25 companies ($2M each), which is too many to hit 3x with this pattern."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the claim hold if 'gross multiple' refers to a return ON INVESTED capital "
            "rather than total value returned (i.e., 2.8x TVPI vs. 3x MOIC interpretation)?"
        ),
        "verification_performed": (
            "Confirmed standard VC terminology: gross multiple = TVPI (total value to paid-in), "
            "which is total proceeds divided by total invested capital. "
            "MOIC (multiple on invested capital) is computed identically at the fund level. "
            "Both give 2.8x for this scenario."
        ),
        "finding": (
            "Both TVPI and MOIC yield 2.8x for this scenario. "
            "No alternative definition of 'gross multiple' changes the arithmetic. "
            "The claim is false under any standard VC accounting convention."
        ),
        "breaks_proof": False,
    },
]

for i, check in enumerate(adversarial_checks):
    print(f"\nAdversarial check {i+1}: {check['question'][:80]}...")
    print(f"  Breaks proof: {check['breaks_proof']}")

# =============================================================================
# 6. VERDICT AND STRUCTURED OUTPUT
# =============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("VERDICT DETERMINATION")
    print("=" * 60)

    # For disproof: claim holds only if gross_multiple == required_multiple (3.0x)
    claim_holds = compare(
        gross_multiple,
        CLAIM_FORMAL["operator"],
        CLAIM_FORMAL["threshold"],
        label="A5: gross_multiple == 3.0",
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    # Pure-math disproof: no citations, no unverified-citation variants
    if any_breaks:
        verdict = "UNDETERMINED"
    else:
        verdict = "PROVED" if claim_holds else "DISPROVED"

    print(f"\nVerdict: {verdict}")
    print(f"  Gross multiple achieved: {gross_multiple:.4f}x")
    print(f"  Required (claimed): {CLAIM_FORMAL['threshold']}x")
    print(f"  Shortfall: ${shortfall_m:.1f}M ({required_multiple - gross_multiple:.4f}x)")

    # Populate Type A method/result
    FACT_REGISTRY["A1"]["method"] = "fund_size_m / n_companies"
    FACT_REGISTRY["A1"]["result"] = f"${per_company_m:.1f}M"
    FACT_REGISTRY["A2"]["method"] = "(n_50x × multiple_50x + n_10x × multiple_10x) × per_company_m"
    FACT_REGISTRY["A2"]["result"] = f"${total_return_m:.1f}M"
    FACT_REGISTRY["A3"]["method"] = "total_return_m / fund_size_m"
    FACT_REGISTRY["A3"]["result"] = f"{gross_multiple:.4f}x"
    FACT_REGISTRY["A4"]["method"] = "sum([50x×$2M, 10x×$2M, 10x×$2M, 0x×$2M × 22])"
    FACT_REGISTRY["A4"]["result"] = f"${crosscheck_total_m:.1f}M → {crosscheck_multiple:.4f}x"
    FACT_REGISTRY["A5"]["method"] = f"compare({gross_multiple:.4f}, '==', {CLAIM_FORMAL['threshold']})"
    FACT_REGISTRY["A5"]["result"] = str(claim_holds)

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "cross_checks": [
            {
                "description": (
                    "Independent computation: explicit per-company list sum "
                    "vs. algebraic formula"
                ),
                "values_compared": [f"{gross_multiple:.4f}x", f"{crosscheck_multiple:.4f}x"],
                "agreement": abs(gross_multiple - crosscheck_multiple) < 1e-9,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "fund_size_m": fund_size_m,
            "n_companies": n_companies,
            "per_company_m": per_company_m,
            "total_return_m": total_return_m,
            "gross_multiple": round(gross_multiple, 4),
            "required_multiple": required_multiple,
            "shortfall_m": shortfall_m,
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

    emit_proof_summary(summary)
