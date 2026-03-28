"""
Proof: The integer 1 is a prime number.
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
CLAIM_NATURAL = "The integer 1 is a prime number."
CLAIM_FORMAL = {
    "subject": "the integer 1",
    "property": "whether 1 satisfies the definition of a prime number",
    "operator": "==",
    "operator_note": (
        "A prime number is defined as a natural number greater than 1 "
        "whose only positive divisors are 1 and itself. For 1 to be prime, "
        "it must satisfy BOTH conditions: (1) greater than 1, and (2) exactly "
        "two distinct positive divisors. We check whether 1 meets these criteria. "
        "The claim asserts 1 IS prime (== True); disproof requires showing "
        "it fails at least one definitional criterion."
    ),
    "threshold": True,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {
        "label": "Positive divisors of 1 (exhaustive enumeration)",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "Count of positive divisors of 1",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "Whether 1 > 1 (greater-than-1 criterion)",
        "method": None,
        "result": None,
    },
    "A4": {
        "label": "Cross-check: trial division primality test",
        "method": None,
        "result": None,
    },
    "A5": {
        "label": "Cross-check: sympy.isprime(1)",
        "method": None,
        "result": None,
    },
}

# 3. COMPUTATION — primary method: definitional check

# A1: Find all positive divisors of 1
n = 1
divisors_of_1 = [d for d in range(1, n + 1) if n % d == 0]
print(f"A1: Positive divisors of {n}: {divisors_of_1}")

# A2: Count divisors — a prime must have exactly 2 (1 and itself)
num_divisors = explain_calc("len(divisors_of_1)", locals(), label="A2: number of positive divisors of 1")

# A3: Check greater-than-1 criterion
gt_one = compare(n, ">", 1, label="A3: is 1 > 1?")
print(f"    1 > 1 is {gt_one}")

# Primary determination: 1 is prime iff it has exactly 2 divisors AND is > 1
has_exactly_two_divisors = compare(num_divisors, "==", 2, label="A2: divisor count == 2?")
is_prime_by_definition = has_exactly_two_divisors and gt_one
print(f"\nPrimary method: 1 is prime = {is_prime_by_definition}")
print(f"  Fails criterion 1 (n > 1): 1 > 1 is {gt_one}")
print(f"  Fails criterion 2 (exactly 2 divisors): has {num_divisors} divisor(s), need 2")

# 4. CROSS-CHECKS — mathematically independent methods (Rule 6)

# Cross-check A: Trial division primality test (independent algorithm)
def is_prime_trial_division(n):
    """Standard trial division: n must be > 1 and have no divisors in [2, sqrt(n)]."""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

crosscheck_trial = is_prime_trial_division(1)
print(f"\nA4 cross-check (trial division): is_prime(1) = {crosscheck_trial}")

# Cross-check B: sympy's isprime (independent implementation)
try:
    from sympy import isprime as sympy_isprime
    crosscheck_sympy = sympy_isprime(1)
    sympy_available = True
    print(f"A5 cross-check (sympy.isprime): isprime(1) = {crosscheck_sympy}")
except ImportError:
    crosscheck_sympy = False
    sympy_available = False
    print("A5 cross-check (sympy): not available, skipping")

# All methods must agree: 1 is NOT prime
assert is_prime_by_definition == crosscheck_trial, (
    f"Cross-check failed: definition={is_prime_by_definition}, trial_division={crosscheck_trial}"
)
if sympy_available:
    assert is_prime_by_definition == crosscheck_sympy, (
        f"Cross-check failed: definition={is_prime_by_definition}, sympy={crosscheck_sympy}"
    )

# 5. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Was 1 ever historically considered a prime number?",
        "verification_performed": (
            "Researched the history of primality of 1. Until the mid-19th century, "
            "many mathematicians (including Goldbach, Euler, and Lebesgue) considered "
            "1 to be prime. The modern convention excluding 1 was formalized to preserve "
            "the Fundamental Theorem of Arithmetic (unique prime factorization). "
            "The modern definition (ISO 80000-2, Hardy & Wright, etc.) explicitly "
            "requires primes to be > 1."
        ),
        "finding": (
            "Historically, 1 was sometimes considered prime, but the modern standard "
            "mathematical definition (universally adopted since ~1899) excludes 1. "
            "The claim is evaluated against the current standard definition."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is there any modern mathematical authority that defines 1 as prime?",
        "verification_performed": (
            "Checked ISO 80000-2 (international standard for mathematical notation), "
            "major textbooks (Hardy & Wright, Niven Zuckerman & Montgomery, "
            "Ireland & Rosen), and computational references (OEIS A000040). "
            "All define primes as integers greater than 1."
        ),
        "finding": (
            "No modern mathematical authority defines 1 as prime. The exclusion is "
            "universal in contemporary mathematics."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does the Fundamental Theorem of Arithmetic break if 1 is prime?",
        "verification_performed": (
            "The FTA states every integer > 1 has a unique prime factorization "
            "(up to order). If 1 were prime, factorizations would not be unique: "
            "e.g., 6 = 2 × 3 = 1 × 2 × 3 = 1 × 1 × 2 × 3. "
            "This is the key mathematical reason 1 is excluded from primes."
        ),
        "finding": (
            "Including 1 as prime would destroy unique factorization, confirming "
            "that the modern exclusion is mathematically necessary, not arbitrary."
        ),
        "breaks_proof": False,
    },
]

# 6. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    claim_holds = compare(is_prime_by_definition, "==", CLAIM_FORMAL["threshold"],
                          label="Claim evaluation: is 1 prime?")

    # Pure-math: no citations
    verdict = "PROVED" if claim_holds else "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = "Exhaustive enumeration of divisors d in [1, n] where n % d == 0"
    FACT_REGISTRY["A1"]["result"] = str(divisors_of_1)
    FACT_REGISTRY["A2"]["method"] = "len(divisors_of_1)"
    FACT_REGISTRY["A2"]["result"] = str(num_divisors)
    FACT_REGISTRY["A3"]["method"] = "compare(1, '>', 1)"
    FACT_REGISTRY["A3"]["result"] = str(gt_one)
    FACT_REGISTRY["A4"]["method"] = "Trial division primality test (independent algorithm)"
    FACT_REGISTRY["A4"]["result"] = str(crosscheck_trial)
    FACT_REGISTRY["A5"]["method"] = "sympy.isprime(1)" if sympy_available else "sympy not available"
    FACT_REGISTRY["A5"]["result"] = str(crosscheck_sympy) if sympy_available else "skipped"

    cross_checks = [
        {
            "description": "Definitional check vs trial division",
            "values_compared": [str(is_prime_by_definition), str(crosscheck_trial)],
            "agreement": is_prime_by_definition == crosscheck_trial,
        },
    ]
    if sympy_available:
        cross_checks.append({
            "description": "Definitional check vs sympy.isprime",
            "values_compared": [str(is_prime_by_definition), str(crosscheck_sympy)],
            "agreement": is_prime_by_definition == crosscheck_sympy,
        })

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "cross_checks": cross_checks,
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n": 1,
            "divisors": divisors_of_1,
            "num_divisors": num_divisors,
            "greater_than_1": gt_one,
            "is_prime": is_prime_by_definition,
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
