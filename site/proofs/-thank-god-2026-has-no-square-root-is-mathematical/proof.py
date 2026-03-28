"""
Proof: "Thank God 2026 has no square root" is mathematically meaningful
Generated: 2026-03-28

The colloquial phrase "has no square root" is interpreted as "is not a perfect square"
(no positive integer n satisfies n² = 2026). The proof establishes this claim is TRUE,
making the statement precisely and verifiably meaningful in mathematics.
"""
import json
import math
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.computations import compare, explain_calc

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    '"Thank God 2026 has no square root" is mathematically meaningful'
)
CLAIM_FORMAL = {
    "subject": "2026",
    "property": (
        "count of positive integers n such that n² = 2026 "
        "(equivalently: is 2026 a perfect square?)"
    ),
    "operator": "==",
    "threshold": 0,
    "operator_note": (
        "The phrase 'has no square root' is a colloquial way of saying '2026 is not "
        "a perfect square' — i.e., no positive integer n satisfies n² = 2026. "
        "The claim is 'mathematically meaningful' if and only if it makes a precise, "
        "true mathematical assertion. We formalise this as: the count of such n equals 0. "
        "The claim would be FALSE (and thus not supported) if any n ∈ ℤ⁺ existed with n²=2026. "
        "Context: 2025 = 45² is a perfect square, so the 'relief' that 2026 escapes this "
        "property is mathematically grounded. "
        "Note: every positive real has a real-valued square root (√2026 ≈ 45.011...); "
        "the meaningful assertion concerns integer square roots only."
    ),
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {
        "label": "isqrt(2026)² ≠ 2026 (primary: no integer square root)",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "Prime factorisation of 2026 has no repeated factors (cross-check)",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "45² = 2025 (predecessor year is a perfect square — context)",
        "method": None,
        "result": None,
    },
    "A4": {
        "label": "√2026 is irrational (consequence of A1/A2)",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. PRIMARY COMPUTATION: integer square root floor check
# ---------------------------------------------------------------------------
print("=== PRIMARY: integer square root check ===")
n = 2026

isqrt_n = math.isqrt(n)  # largest integer k with k² ≤ n
print(f"math.isqrt({n}) = {isqrt_n}")

sq_floor = explain_calc("isqrt_n * isqrt_n", locals(), label="floor_sq = isqrt(2026)²")
sq_ceil = explain_calc("(isqrt_n + 1) * (isqrt_n + 1)", locals(), label="ceil_sq  = (isqrt(2026)+1)²")

floor_is_not_n = compare(sq_floor, "!=", n, label="A1a: 45² ≠ 2026")
ceil_is_not_n  = compare(sq_ceil,  "!=", n, label="A1b: 46² ≠ 2026")

a1_holds = compare(
    int(floor_is_not_n and ceil_is_not_n), "==", 1,
    label="A1: both 45² ≠ 2026 AND 46² ≠ 2026 → no integer square root",
)

# ---------------------------------------------------------------------------
# 4. CROSS-CHECK: prime factorisation
#    A number is a perfect square iff every prime factor appears to an even power.
# ---------------------------------------------------------------------------
print("\n=== CROSS-CHECK: prime factorisation ===")

def prime_factors(m):
    """Return sorted list of (prime, exponent) pairs for m."""
    factors = {}
    d = 2
    while d * d <= m:
        while m % d == 0:
            factors[d] = factors.get(d, 0) + 1
            m //= d
        d += 1
    if m > 1:
        factors[m] = factors.get(m, 0) + 1
    return sorted(factors.items())

factors_2026 = prime_factors(n)
print(f"Prime factorisation of {n}: " + " × ".join(f"{p}^{e}" for p, e in factors_2026))

# Verify factorisation is correct
product_check = 1
for p, e in factors_2026:
    product_check *= p ** e
assert product_check == n, f"Factorisation product mismatch: {product_check} ≠ {n}"
print(f"Factorisation product verified: {product_check} = {n} ✓")

# Perfect square iff all exponents are even
odd_exponent_primes = [(p, e) for p, e in factors_2026 if e % 2 != 0]
print(f"Primes with odd exponents: {odd_exponent_primes}")

a2_holds = compare(
    len(odd_exponent_primes), ">=", 1,
    label="A2: at least one prime with odd exponent → not a perfect square",
)

# Cross-check agreement: A1 and A2 must agree
assert a1_holds == a2_holds, (
    f"Cross-check failed: A1 (isqrt method) says {a1_holds}, "
    f"A2 (factorisation method) says {a2_holds}"
)
print("Cross-check A1 vs A2: AGREE ✓")

# ---------------------------------------------------------------------------
# 5. CONTEXT: predecessor year 2025 is a perfect square
# ---------------------------------------------------------------------------
print("\n=== CONTEXT: 2025 is a perfect square ===")
year_before = 2025
isqrt_2025 = math.isqrt(year_before)
sq_2025 = explain_calc("isqrt_2025 * isqrt_2025", locals(), label="A3: isqrt(2025)²")
a3_holds = compare(sq_2025, "==", year_before, label="A3: 2025 is a perfect square")
print(f"isqrt(2025) = {isqrt_2025}, so 2025 = {isqrt_2025}²  → perfect square: {a3_holds}")

# ---------------------------------------------------------------------------
# 6. IRRATIONALITY of √2026
#    If √2026 = p/q (reduced fraction), then p² = 2026 q².
#    From factorisation: 2026 = 2¹ × 1013¹.  The prime 2 appears to odd power (1) in 2026.
#    For p² = 2026 q², v₂(p²) must equal v₂(2026 q²) = 1 + 2·v₂(q),
#    which is always odd. But v₂(p²) = 2·v₂(p) is always even. Contradiction.
# ---------------------------------------------------------------------------
print("\n=== IRRATIONALITY of √2026 ===")

# Verify: 2 appears to power 1 in 2026 (odd)
v2_2026 = next(e for p, e in factors_2026 if p == 2)
print(f"v₂(2026) = {v2_2026}  (exponent of 2 in prime factorisation of 2026)")
a4_holds = compare(v2_2026 % 2, "==", 1, label="A4: v₂(2026) is odd → √2026 irrational")
print(
    f"A4 (√2026 irrational): {a4_holds}  "
    f"[if √2026 = p/q then 2·v₂(p) = {v2_2026} + 2·v₂(q), "
    f"but LHS is even and RHS is odd — contradiction]"
)

# ---------------------------------------------------------------------------
# 7. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": "Does 2026 have an integer square root that was overlooked?",
        "verification_performed": (
            "Computed math.isqrt(2026) = 45; verified 45² = 2025 and 46² = 2116. "
            "Also verified via exhaustive search: no n in [1, 2026] satisfies n² = 2026."
        ),
        "finding": (
            "Exhaustive check confirms no integer n satisfies n² = 2026. "
            "The nearest perfect squares are 45² = 2025 (one below) and 46² = 2116 (next above)."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could 'no square root' mean something other than 'not a perfect square'?",
        "verification_performed": (
            "Considered three interpretations: "
            "(1) no real square root — FALSE, √2026 ≈ 45.011 exists in ℝ; "
            "(2) no rational square root — TRUE, proved via valuation argument (A4); "
            "(3) no integer square root — TRUE, proved via isqrt and factorisation (A1, A2). "
            "The colloquial use in the context of year-numbering most naturally refers to "
            "interpretation (3), consistent with 2025 = 45² being called 'a perfect square year'."
        ),
        "finding": (
            "Under the natural 'year context' interpretation (integer square root), the claim "
            "is TRUE. Under the rational interpretation it is also TRUE. "
            "Only under interpretation (1) — real square root — is it false, but that "
            "reading is inconsistent with the celebratory framing ('Thank God'). "
            "The claim is therefore unambiguously mathematically meaningful."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is 2026 perhaps a perfect power of some other kind that could confuse the claim?",
        "verification_performed": (
            "Checked whether 2026 is a perfect cube, 4th power, or any perfect power. "
            "2026 = 2 × 1013 (both primes); for a perfect k-th power all exponents must be "
            "divisible by k. Since 2026 has exponents {2:1, 1013:1}, it is a perfect power "
            "only for k=1 (trivially). Not a perfect square, cube, or any higher power."
        ),
        "finding": "2026 is not a perfect power for any exponent k ≥ 2. The claim is specific to squares.",
        "breaks_proof": False,
    },
    {
        "question": "Is 1013 actually prime? (needed for the factorisation cross-check)",
        "verification_performed": (
            "Trial division up to √1013 ≈ 31.8: tested all primes ≤ 31 "
            "(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31). None divide 1013. "
            "Therefore 1013 is prime."
        ),
        "finding": "1013 is prime. Factorisation 2026 = 2 × 1013 is correct.",
        "breaks_proof": False,
    },
]

# Exhaustive search (adversarial check 1 — machine-verified)
print("\n=== ADVERSARIAL: exhaustive n² = 2026 search ===")
counterexamples = [nn for nn in range(1, n + 1) if nn * nn == n]
compare(len(counterexamples), "==", 0, label="Exhaustive search: no n with n²=2026")

# Primality of 1013 (adversarial check 4 — machine-verified)
print("\n=== ADVERSARIAL: primality of 1013 ===")
p1013 = 1013
divisors_of_1013 = [d for d in range(2, math.isqrt(p1013) + 1) if p1013 % d == 0]
compare(len(divisors_of_1013), "==", 0, label="1013 has no divisors in [2, floor(√1013)]")
print(f"1013 is prime: {len(divisors_of_1013) == 0}")

# ---------------------------------------------------------------------------
# 8. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # The proof's primary claim: count of integer square roots of 2026 = 0
    integer_sqrt_count = len([nn for nn in range(1, n + 1) if nn * nn == n])
    claim_holds = compare(
        integer_sqrt_count,
        CLAIM_FORMAL["operator"],
        CLAIM_FORMAL["threshold"],
        label="Primary claim: 2026 is not a perfect square",
    )
    verdict = "PROVED" if (claim_holds and a1_holds and a2_holds and a3_holds and a4_holds) else "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = (
        "math.isqrt(2026) = 45; verified 45² = 2025 ≠ 2026 and 46² = 2116 ≠ 2026"
    )
    FACT_REGISTRY["A1"]["result"] = str(a1_holds)

    FACT_REGISTRY["A2"]["method"] = (
        "Prime factorisation: 2026 = 2¹ × 1013¹; "
        "both exponents are odd → not a perfect square (cross-check)"
    )
    FACT_REGISTRY["A2"]["result"] = str(a2_holds)

    FACT_REGISTRY["A3"]["method"] = (
        "math.isqrt(2025) = 45; verified 45² = 2025 (context: predecessor year is a perfect square)"
    )
    FACT_REGISTRY["A3"]["result"] = str(a3_holds)

    FACT_REGISTRY["A4"]["method"] = (
        "Valuation argument: v₂(2026) = 1 (odd); "
        "if √2026 = p/q then 2·v₂(p) = 1 + 2·v₂(q) — even = odd, contradiction"
    )
    FACT_REGISTRY["A4"]["result"] = str(a4_holds)

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
                    "A1 (isqrt floor/ceil method) vs A2 (prime factorisation method): "
                    "both independently establish 2026 is not a perfect square"
                ),
                "values_compared": [str(a1_holds), str(a2_holds)],
                "agreement": a1_holds == a2_holds,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n": n,
            "isqrt_n": isqrt_n,
            "isqrt_n_squared": int(sq_floor),
            "next_perfect_square": int(sq_ceil),
            "factorisation": {str(p): e for p, e in factors_2026},
            "odd_exponent_primes": odd_exponent_primes,
            "predecessor_year_is_perfect_square": a3_holds,
            "predecessor_year_sqrt": isqrt_2025,
            "sqrt_2026_is_irrational": a4_holds,
            "integer_sqrt_count": integer_sqrt_count,
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
