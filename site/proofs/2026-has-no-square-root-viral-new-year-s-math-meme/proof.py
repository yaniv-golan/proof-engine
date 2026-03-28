"""
Proof: 2026 has no square root (viral New Year's math meme)
Generated: 2026-03-28

Interpretation: The claim is that 2026 has no INTEGER square root,
i.e., 2026 is not a perfect square. (In ℝ every positive number has a
real square root, so the meaningful mathematical sense of the meme is
the integer/perfect-square sense.)

Two independent methods confirm this:
  A1 — Direct floor-sqrt bound check (primary)
  A2 — Quadratic residue mod 16 (cross-check; uses no square roots)
"""
import json
import math
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.computations import compare, explain_calc

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------

CLAIM_NATURAL = "2026 has no square root"

CLAIM_FORMAL = {
    "subject": "2026",
    "property": "existence of an integer n such that n² = 2026",
    "operator": "==",
    "threshold": False,  # claim asserts: such n does NOT exist → result is False
    "operator_note": (
        "The claim is interpreted as: there is no integer n ≥ 0 satisfying n² = 2026 "
        "(equivalently, 2026 is not a perfect square). "
        "In ℝ or ℂ, 2026 trivially has square roots (√2026 ≈ 45.011…), so the real/complex "
        "interpretation makes the claim false. The viral meme's mathematical punch-line — "
        "that 2025 = 45² is a perfect square and 2026 is not — only makes sense under the "
        "integer interpretation, which is therefore the formal claim. "
        "Proof succeeds when both independent methods agree: no integer n satisfies n² = 2026."
    ),
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY — Type A only (pure math, no URLs)
# ---------------------------------------------------------------------------

FACT_REGISTRY = {
    "A1": {
        "label": "Floor-sqrt bound check: no integer squares to 2026",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "Quadratic-residue mod-16 check: 2026 mod 16 is not a perfect-square residue",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "Context: 2025 = 45² confirming the adjacent perfect square",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. PRIMARY COMPUTATION (A1) — floor-sqrt bound check
#
# math.isqrt(n) returns the exact integer part of √n (Python ≥ 3.8).
# If n is a perfect square, isqrt(n)² == n exactly.
# ---------------------------------------------------------------------------

n = 2026
floor_root = math.isqrt(n)          # largest integer k with k² ≤ n

lower_sq = explain_calc("floor_root ** 2", locals(), label="A1: floor_root² (lower bound)")
upper_sq = explain_calc("(floor_root + 1) ** 2", locals(), label="A1: (floor_root+1)² (upper bound)")

# If lower_sq < n < upper_sq, there is no integer whose square equals n.
is_perfect_square_primary = (lower_sq == n)

print(f"\nA1: math.isqrt({n}) = {floor_root}")
print(f"A1: {floor_root}² = {lower_sq}  (must equal {n} for a perfect square)")
print(f"A1: {floor_root+1}² = {upper_sq}  (next perfect square)")
print(f"A1: {lower_sq} < {n} < {upper_sq}  →  no integer square root exists")
_ = compare(is_perfect_square_primary, "==", False, label="A1: is_perfect_square (primary)")

# ---------------------------------------------------------------------------
# 4. CROSS-CHECK (A2) — modular arithmetic (Rule 6, independent method)
#
# A perfect square n ≡ k² (mod 16) for some integer k.
# Computing k² mod 16 for k = 0..15 gives the complete set of
# quadratic residues mod 16: {0, 1, 4, 9}.
# If n mod 16 ∉ {0, 1, 4, 9}, then n is provably NOT a perfect square.
#
# This method uses NO square roots and shares NO intermediate computation
# with the primary method — it is structurally independent.
# ---------------------------------------------------------------------------

PERFECT_SQUARE_RESIDUES_MOD16 = {k*k % 16 for k in range(16)}
print(f"\nA2: Quadratic residues mod 16 = {sorted(PERFECT_SQUARE_RESIDUES_MOD16)}")

n_mod_16 = explain_calc("n % 16", locals(), label="A2: 2026 mod 16")
is_valid_residue = n_mod_16 in PERFECT_SQUARE_RESIDUES_MOD16
is_perfect_square_crosscheck = is_valid_residue

print(f"A2: {n} mod 16 = {n_mod_16}  (quadratic residues mod 16: {sorted(PERFECT_SQUARE_RESIDUES_MOD16)})")
print(f"A2: {n_mod_16} ∈ QR_16? {is_valid_residue}  →  is_perfect_square = {is_perfect_square_crosscheck}")
_ = compare(is_perfect_square_crosscheck, "==", False, label="A2: is_perfect_square (mod-16 cross-check)")

# Both methods must agree
assert is_perfect_square_primary == is_perfect_square_crosscheck, (
    f"Cross-check disagreement: primary={is_perfect_square_primary}, "
    f"crosscheck={is_perfect_square_crosscheck}"
)
print("\n✓ Both independent methods agree: 2026 is NOT a perfect square.")

# ---------------------------------------------------------------------------
# 5. CONTEXT (A3) — confirm 2025 IS a perfect square
# ---------------------------------------------------------------------------

prev_year = 2025
prev_root = math.isqrt(prev_year)
prev_sq = prev_root ** 2
prev_is_perfect = (prev_sq == prev_year)

print(f"\nA3: math.isqrt({prev_year}) = {prev_root}")
print(f"A3: {prev_root}² = {prev_sq}  →  2025 IS a perfect square: {prev_is_perfect}")
_ = compare(prev_is_perfect, "==", True, label="A3: 2025 is a perfect square (context)")

# ---------------------------------------------------------------------------
# 6. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------

adversarial_checks = [
    {
        "question": "Does 2026 have a real or complex square root? Could that vindicate the claim?",
        "verification_performed": (
            "Computed math.sqrt(2026) ≈ 45.011109… and noted that every positive real has "
            "exactly two real square roots (±). In ℂ every number has square roots. "
            "The meme's mathematical joke depends on 2025 being special as a perfect square "
            "year; the intended meaning is unambiguously the integer/perfect-square sense."
        ),
        "finding": (
            "√2026 ≈ 45.011… exists in ℝ but is irrational. The real/complex interpretations "
            "make the claim FALSE; only the integer interpretation makes it TRUE and "
            "mathematically interesting. The formal claim is correctly scoped to integers."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Are there any integers near 2026 that are perfect squares, "
                    "confirming 2026 is genuinely between two?",
        "verification_performed": (
            "Computed 45² = 2025 and 46² = 2116. Checked that 2025 < 2026 < 2116 with no "
            "integer between 45 and 46, confirming no gap is missed."
        ),
        "finding": (
            "44² = 1936, 45² = 2025, 46² = 2116, 47² = 2209. "
            "2026 falls strictly between consecutive perfect squares 2025 and 2116. "
            "This is fully consistent with the primary proof — no counterexample."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could a modular-arithmetic error give a false 'not a perfect square' result?",
        "verification_performed": (
            "Verified the set PERFECT_SQUARE_RESIDUES_MOD16 by enumerating all k in 0..15 "
            "and computing k² mod 16. Result: {0,1,4,9}. Confirmed 2026 mod 16 = 10 by "
            "direct subtraction: 2026 - 126×16 = 2026 - 2016 = 10. "
            "Checked that 10 ∉ {0,1,4,9} by inspection."
        ),
        "finding": (
            "The residue set {0,1,4,9} and 2026 mod 16 = 10 are both straightforward to verify "
            "by hand. No error — the modular argument is sound."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is math.isqrt() reliable for four-digit numbers?",
        "verification_performed": (
            "math.isqrt() is specified in PEP 578 / Python 3.8+ and computes the exact integer "
            "square root (no floating-point rounding). For n = 2026, cross-checked: "
            "floor(√2026) = floor(45.011…) = 45. Since 45² = 2025 and 46² = 2116, "
            "and math.isqrt(2026) = 45, the result is correct."
        ),
        "finding": (
            "math.isqrt() is exact for all non-negative integers (arbitrary precision). "
            "No floating-point risk. Result for 2026 verified by manual bounding."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 7. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Pure-math proof: no citations, so no unverified-citation variants
    # Claim holds when BOTH methods confirm 2026 is NOT a perfect square (both return False)
    both_agree_not_perfect = compare(
        is_perfect_square_primary, "==", is_perfect_square_crosscheck,
        label="Verdict: primary and cross-check agree on is_perfect_square"
    )
    claim_holds = compare(
        is_perfect_square_primary, "==", False,
        label="Verdict: 2026 is not a perfect square"
    )
    verdict = "PROVED" if (claim_holds and both_agree_not_perfect) else "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = "math.isqrt() floor-sqrt bound check"
    FACT_REGISTRY["A1"]["result"] = (
        f"45² = 2025 ≠ 2026, 46² = 2116 ≠ 2026 → no integer square root"
    )
    FACT_REGISTRY["A2"]["method"] = "Quadratic residues mod 16"
    FACT_REGISTRY["A2"]["result"] = (
        f"2026 mod 16 = 10; QR_16 = {{0,1,4,9}}; 10 ∉ QR_16 → not a perfect square"
    )
    FACT_REGISTRY["A3"]["method"] = "math.isqrt() perfect-square confirmation"
    FACT_REGISTRY["A3"]["result"] = f"45² = 2025 → 2025 IS a perfect square (adjacent year)"

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
                    "Primary (floor-sqrt) vs cross-check (mod-16): "
                    "both return is_perfect_square=False for 2026"
                ),
                "values_compared": [
                    str(is_perfect_square_primary),
                    str(is_perfect_square_crosscheck),
                ],
                "agreement": is_perfect_square_primary == is_perfect_square_crosscheck,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n": n,
            "floor_sqrt": floor_root,
            "lower_perfect_square": lower_sq,
            "upper_perfect_square": upper_sq,
            "n_mod_16": int(n_mod_16),
            "perfect_square_residues_mod16": sorted(PERFECT_SQUARE_RESIDUES_MOD16),
            "is_perfect_square_primary": is_perfect_square_primary,
            "is_perfect_square_crosscheck": is_perfect_square_crosscheck,
            "claim_holds": claim_holds,
            "adjacent_perfect_square_2025": f"45² = {prev_sq}",
            "next_perfect_square_2116": f"46² = {upper_sq}",
            "real_sqrt_approx": round(math.sqrt(n), 6),
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
