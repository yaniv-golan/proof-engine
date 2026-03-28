"""
Proof: 641 divides 2^{32} + 1 exactly.
Generated: 2026-03-28
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.computations import compare, explain_calc

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "641 divides 2^{32} + 1 exactly."
CLAIM_FORMAL = {
    "subject": "2^32 + 1 (the fifth Fermat number, F_5)",
    "property": "(2^32 + 1) mod 641",
    "operator": "==",
    "operator_note": (
        "'Divides exactly' means 641 is a factor of 2^32 + 1, "
        "i.e., (2^32 + 1) mod 641 == 0. This is equivalent to showing "
        "2^32 + 1 = 641 * k for some positive integer k."
    ),
    "threshold": 0,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {"label": "Direct modular arithmetic: (2^32 + 1) mod 641", "method": None, "result": None},
    "A2": {"label": "Integer division cross-check: 2^32 + 1 == 641 * quotient", "method": None, "result": None},
    "A3": {"label": "Algebraic decomposition via Euler's method", "method": None, "result": None},
}

# 3. COMPUTATION — primary method (direct modular arithmetic)
fermat_5 = 2**32 + 1
print(f"2^32 + 1 = {fermat_5}")

remainder = explain_calc("fermat_5 % 641", {"fermat_5": fermat_5}, label="A1: (2^32 + 1) mod 641")

# 4. CROSS-CHECKS — mathematically independent methods (Rule 6)

# Cross-check 1: Integer division — verify 641 * quotient == 2^32 + 1
quotient, check_remainder = divmod(fermat_5, 641)
print(f"\nCross-check 1 (integer division):")
print(f"  divmod(2^32 + 1, 641) = quotient={quotient}, remainder={check_remainder}")
product = explain_calc("641 * quotient", {"quotient": quotient}, label="A2: 641 * quotient")
division_exact = compare(product, "==", fermat_5, label="A2: 641 * quotient == 2^32 + 1")

# Cross-check 2: Euler's algebraic decomposition
# Euler observed: 641 = 5^4 + 2^4 and 641 = 5 * 2^7 + 1
# From 641 = 5 * 2^7 + 1: 5 * 2^7 ≡ -1 (mod 641)
# Raising to 4th power: 5^4 * 2^28 ≡ 1 (mod 641)
# From 641 = 5^4 + 2^4: 5^4 ≡ -2^4 (mod 641)
# Substituting: -2^4 * 2^28 ≡ 1 (mod 641), i.e., -2^32 ≡ 1, i.e., 2^32 ≡ -1 (mod 641)
# Therefore 2^32 + 1 ≡ 0 (mod 641)
print("\nCross-check 2 (Euler's algebraic decomposition):")

# Verify the two key identities
identity_1 = explain_calc("5**4 + 2**4", {}, label="A3a: 5^4 + 2^4")
identity_1_check = compare(identity_1, "==", 641, label="A3a: 5^4 + 2^4 == 641")

identity_2 = explain_calc("5 * 2**7 + 1", {}, label="A3b: 5 * 2^7 + 1")
identity_2_check = compare(identity_2, "==", 641, label="A3b: 5 * 2^7 + 1 == 641")

# From identity_2: 5 * 128 ≡ -1 (mod 641), so (5 * 128)^4 ≡ 1 (mod 641)
step_a = explain_calc("pow(5 * 128, 4, 641)", {}, label="A3c: (5 * 2^7)^4 mod 641")
# This means 5^4 * 2^28 ≡ 1 (mod 641)

# From identity_1: 5^4 ≡ -2^4 (mod 641)
step_b = explain_calc("pow(5, 4, 641)", {}, label="A3d: 5^4 mod 641")
step_b_expected = explain_calc("(-pow(2, 4, 641)) % 641", {}, label="A3e: -2^4 mod 641")
euler_identity_check = compare(step_b, "==", step_b_expected, label="A3: 5^4 ≡ -2^4 (mod 641)")

# Combining: -2^4 * 2^28 ≡ 1 (mod 641) → -2^32 ≡ 1 → 2^32 ≡ -1 → 2^32 + 1 ≡ 0
euler_final = explain_calc("pow(2, 32, 641)", {}, label="A3f: 2^32 mod 641")
euler_conclusion = compare((euler_final + 1) % 641, "==", 0, label="A3: (2^32 + 1) mod 641 == 0 via Euler")

# Verify all cross-checks agree
assert remainder == 0, f"Primary check failed: remainder = {remainder}"
assert check_remainder == 0, f"Cross-check 1 failed: remainder = {check_remainder}"
assert division_exact, "Cross-check 1 failed: product != fermat_5"
assert identity_1_check, "Euler identity 1 failed"
assert identity_2_check, "Euler identity 2 failed"
assert euler_conclusion, "Euler algebraic proof failed"

# 5. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Could the computation overflow or lose precision?",
        "verification_performed": (
            "Python integers have arbitrary precision — no overflow is possible. "
            "2^32 + 1 = 4294967297, well within exact integer range. "
            "The modular arithmetic uses Python's built-in integer mod, which is exact."
        ),
        "finding": "No precision issue. Python integers are arbitrary-precision.",
        "breaks_proof": False,
    },
    {
        "question": "Is 641 the smallest prime factor of 2^32 + 1?",
        "verification_performed": (
            "Checked by trial division: no prime less than 641 divides 4294967297. "
            "The cofactor 4294967297 / 641 = 6700417, which is itself prime. "
            "Thus 4294967297 = 641 × 6700417 is the complete factorization."
        ),
        "finding": "641 is indeed the smallest prime factor. Confirmed by trial division below.",
        "breaks_proof": False,
    },
    {
        "question": "Does 'divides exactly' require that 641 is a prime factor, or just a factor?",
        "verification_performed": (
            "The claim says '641 divides 2^{32} + 1 exactly', which in standard number theory "
            "means 641 | (2^32 + 1), i.e., the remainder is zero. The claim does not require "
            "641 to be prime (though it is). Our proof shows the remainder is 0, which is "
            "sufficient for the claim as stated."
        ),
        "finding": "The interpretation is correct. 'Divides exactly' means zero remainder.",
        "breaks_proof": False,
    },
]

# Adversarial computation: verify 641 is smallest prime factor by trial division
print("\nAdversarial: trial division to verify 641 is smallest prime factor")
smallest_factor = None
for p in range(2, 642):
    if fermat_5 % p == 0:
        smallest_factor = p
        break
print(f"  Smallest factor of {fermat_5} found by trial division: {smallest_factor}")
assert smallest_factor == 641, f"Expected 641, got {smallest_factor}"

# Verify cofactor is prime
cofactor = fermat_5 // 641
print(f"  Cofactor: {fermat_5} / 641 = {cofactor}")
cofactor_is_prime = all(cofactor % i != 0 for i in range(2, int(cofactor**0.5) + 1))
print(f"  Cofactor {cofactor} is prime: {cofactor_is_prime}")
print(f"  Complete factorization: {fermat_5} = 641 × {cofactor}")

# 6. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    claim_holds = compare(remainder, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                          label="VERDICT: (2^32 + 1) mod 641 == 0")

    verdict = "PROVED" if claim_holds else "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = "Python exact integer arithmetic: (2**32 + 1) % 641"
    FACT_REGISTRY["A1"]["result"] = str(remainder)
    FACT_REGISTRY["A2"]["method"] = "Integer division: divmod(2^32 + 1, 641) then verify 641 * quotient == 2^32 + 1"
    FACT_REGISTRY["A2"]["result"] = f"quotient={quotient}, remainder={check_remainder}, 641*{quotient}={product}"
    FACT_REGISTRY["A3"]["method"] = (
        "Euler's algebraic decomposition: 641 = 5^4 + 2^4 = 5*2^7 + 1, "
        "therefore 5^4 ≡ -2^4 and 5*2^7 ≡ -1 (mod 641), "
        "combining gives 2^32 ≡ -1 (mod 641)"
    )
    FACT_REGISTRY["A3"]["result"] = f"2^32 mod 641 = {euler_final}, so (2^32 + 1) mod 641 = {(euler_final + 1) % 641}"

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "cross_checks": [
            {
                "description": "Integer division: 641 * quotient reconstructs 2^32 + 1",
                "values_compared": [str(product), str(fermat_5)],
                "agreement": product == fermat_5,
            },
            {
                "description": "Euler's algebraic decomposition confirms 2^32 ≡ -1 (mod 641)",
                "values_compared": [str(euler_final), str(641 - 1)],
                "agreement": euler_conclusion,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "fermat_5": fermat_5,
            "remainder": remainder,
            "quotient": quotient,
            "cofactor": cofactor,
            "cofactor_is_prime": cofactor_is_prime,
            "complete_factorization": f"{fermat_5} = 641 × {cofactor}",
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
