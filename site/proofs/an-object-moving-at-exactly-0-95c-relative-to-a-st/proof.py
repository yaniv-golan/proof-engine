"""
Proof: An object moving at exactly 0.95c relative to a stationary observer
experiences a Lorentz factor γ greater than 3.2.
Generated: 2026-03-28
"""
import json
import os
import sys
from math import sqrt
from decimal import Decimal, getcontext

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.computations import compare, explain_calc, cross_check

# ============================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# ============================================================
CLAIM_NATURAL = (
    "An object moving at exactly 0.95c relative to a stationary observer "
    "experiences a Lorentz factor γ greater than 3.2."
)
CLAIM_FORMAL = {
    "subject": "Lorentz factor γ for an object at v = 0.95c",
    "property": "γ = 1 / sqrt(1 - β²) where β = v/c = 0.95",
    "operator": ">",
    "operator_note": (
        "'greater than 3.2' is interpreted as strictly greater than (>). "
        "The Lorentz factor γ is a standard definition from special relativity: "
        "γ = 1 / sqrt(1 - v²/c²). With v/c = 0.95 (exact), this is a pure "
        "mathematical computation with no empirical ambiguity. "
        "If γ were exactly 3.2, the claim would be FALSE."
    ),
    "threshold": 3.2,
}

# ============================================================
# 2. FACT REGISTRY — A-types only for pure math
# ============================================================
FACT_REGISTRY = {
    "A1": {
        "label": "Primary computation of γ via direct formula",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "Cross-check via high-precision decimal arithmetic",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "Cross-check via algebraic simplification γ² = 1/(1-β²)",
        "method": None,
        "result": None,
    },
}

# ============================================================
# 3. COMPUTATION — primary method (float arithmetic)
# ============================================================
beta = 0.95  # v/c, exact by claim

beta_squared = explain_calc("beta ** 2", {"beta": beta}, label="β²")
one_minus_beta_sq = explain_calc(
    "1 - beta_squared", {"beta_squared": beta_squared}, label="1 - β²"
)
gamma_primary = explain_calc(
    "1 / sqrt(one_minus_beta_sq)",
    {"one_minus_beta_sq": one_minus_beta_sq, "sqrt": sqrt},
    label="γ (primary, float)",
)

# ============================================================
# 4. CROSS-CHECK 1 — Decimal arithmetic (independent precision path)
# ============================================================
getcontext().prec = 50  # high precision
beta_dec = Decimal("0.95")
beta_sq_dec = beta_dec ** 2
one_minus_dec = Decimal("1") - beta_sq_dec
gamma_decimal = Decimal("1") / one_minus_dec.sqrt()
gamma_crosscheck1 = float(gamma_decimal)

print(f"\nCross-check 1 (Decimal, 50-digit precision): γ = {gamma_decimal}")
cross_check(
    gamma_primary,
    gamma_crosscheck1,
    tolerance=1e-10,
    mode="absolute",
    label="Primary (float) vs Decimal arithmetic",
)

# ============================================================
# 5. CROSS-CHECK 2 — Algebraic: γ² = 1/(1-β²), then sqrt
# ============================================================
# β = 95/100 = 19/20, so β² = 361/400, 1-β² = 39/400, γ² = 400/39
# This uses exact rational arithmetic — structurally independent from
# floating-point or Decimal square root.
from fractions import Fraction

beta_frac = Fraction(19, 20)  # 0.95 = 19/20 exactly
beta_sq_frac = beta_frac ** 2  # 361/400
one_minus_frac = Fraction(1) - beta_sq_frac  # 39/400
gamma_sq_frac = Fraction(1) / one_minus_frac  # 400/39

# γ² = 400/39. We need γ > 3.2, i.e., γ² > 10.24
# 400/39 ≈ 10.2564..., and 3.2² = 10.24
# So we can verify γ > 3.2 by verifying γ² > 3.2²
threshold_sq = Fraction(32, 10) ** 2  # (3.2)² = 1024/100 = 256/25

gamma_sq_exceeds = gamma_sq_frac > threshold_sq
print(f"\nCross-check 2 (exact rational): γ² = {gamma_sq_frac} = {float(gamma_sq_frac):.10f}")
print(f"  threshold² = {threshold_sq} = {float(threshold_sq):.10f}")
print(f"  γ² > threshold²: {gamma_sq_exceeds}")

# Also compute γ from the fraction for numerical cross-check
gamma_crosscheck2 = float(gamma_sq_frac) ** 0.5
cross_check(
    gamma_primary,
    gamma_crosscheck2,
    tolerance=1e-10,
    mode="absolute",
    label="Primary (float) vs Rational arithmetic",
)

# ============================================================
# 6. ADVERSARIAL CHECKS (Rule 5)
# ============================================================
adversarial_checks = [
    {
        "question": "Is there any alternative definition of the Lorentz factor that would yield a different value?",
        "verification_performed": (
            "Reviewed standard physics references. The Lorentz factor γ = 1/√(1-v²/c²) "
            "is the universal definition in special relativity. There is no competing "
            "definition. The reciprocal 1/γ is sometimes used but is clearly distinct."
        ),
        "finding": "No alternative definition exists that would change the computed value.",
        "breaks_proof": False,
    },
    {
        "question": "Could floating-point representation of 0.95 introduce enough error to change the comparison?",
        "verification_performed": (
            "Computed γ via three independent methods: IEEE 754 float, 50-digit Decimal, "
            "and exact rational (Fraction) arithmetic. All agree to >10 decimal places. "
            "The exact rational computation confirms γ² = 400/39 > 256/25 = 3.2² with "
            "no floating-point involved."
        ),
        "finding": "Floating-point representation cannot affect the verdict; exact rational arithmetic confirms γ > 3.2.",
        "breaks_proof": False,
    },
    {
        "question": "Is the margin above 3.2 so small that rounding could flip the result?",
        "verification_performed": (
            "γ ≈ 3.2026 and threshold is 3.2. The margin is ~0.0026, which is well above "
            "any floating-point uncertainty. Additionally, the exact rational proof shows "
            "γ² = 400/39 ≈ 10.2564 vs 3.2² = 10.24, a margin of ~0.0164 in the squared domain."
        ),
        "finding": "The margin is small but unambiguous — confirmed by exact arithmetic.",
        "breaks_proof": False,
    },
]

# ============================================================
# 7. VERDICT AND STRUCTURED OUTPUT
# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CLAIM EVALUATION")
    print("=" * 60)

    claim_holds = compare(
        gamma_primary, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
        label="γ > 3.2"
    )

    # Pure-math: no citations
    verdict = "PROVED" if claim_holds else "DISPROVED"

    print(f"\nVerdict: {verdict}")

    # Update fact registry
    FACT_REGISTRY["A1"]["method"] = "Direct float computation: γ = 1/√(1 - 0.95²)"
    FACT_REGISTRY["A1"]["result"] = f"{gamma_primary:.10f}"
    FACT_REGISTRY["A2"]["method"] = "50-digit Decimal arithmetic"
    FACT_REGISTRY["A2"]["result"] = f"{gamma_crosscheck1:.10f}"
    FACT_REGISTRY["A3"]["method"] = "Exact rational: γ² = 400/39, verify γ² > (3.2)² = 256/25"
    FACT_REGISTRY["A3"]["result"] = f"γ² = 400/39 ≈ {float(gamma_sq_frac):.10f}, γ ≈ {gamma_crosscheck2:.10f}"

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "cross_checks": [
            {
                "description": "Float vs 50-digit Decimal arithmetic",
                "values_compared": [f"{gamma_primary:.10f}", f"{gamma_crosscheck1:.10f}"],
                "agreement": abs(gamma_primary - gamma_crosscheck1) < 1e-10,
            },
            {
                "description": "Float vs exact rational (Fraction) arithmetic",
                "values_compared": [f"{gamma_primary:.10f}", f"{gamma_crosscheck2:.10f}"],
                "agreement": abs(gamma_primary - gamma_crosscheck2) < 1e-10,
            },
            {
                "description": "Exact rational squared comparison: γ² = 400/39 > 256/25 = (3.2)²",
                "values_compared": [str(gamma_sq_frac), str(threshold_sq)],
                "agreement": gamma_sq_exceeds,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "gamma": gamma_primary,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
            "beta": beta,
            "gamma_exact_rational_squared": str(gamma_sq_frac),
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
