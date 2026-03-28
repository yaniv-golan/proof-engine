"""
Proof: Fewer than 20 percent of the positive integers from 1 to 1000 are prime.
Generated: 2026-03-28
Type: Pure Math (Type A)
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.computations import compare, explain_calc

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "Fewer than 20 percent of the positive integers from 1 to 1000 are prime."
CLAIM_FORMAL = {
    "subject": "positive integers from 1 to 1000",
    "property": "percentage that are prime",
    "operator": "<",
    "operator_note": (
        "'Fewer than 20 percent' means the count of primes in [1, 1000] divided by 1000, "
        "multiplied by 100, must be strictly less than 20. Equivalently, the prime count "
        "must be strictly less than 200."
    ),
    "threshold": 20,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {"label": "Prime count via Sieve of Eratosthenes", "method": None, "result": None},
    "A2": {"label": "Prime count via trial division (independent cross-check)", "method": None, "result": None},
    "A3": {"label": "Percentage of primes in [1, 1000]", "method": None, "result": None},
}

# 3. COMPUTATION — primary method: Sieve of Eratosthenes
N = 1000

def sieve_of_eratosthenes(n):
    """Return list of primes up to n using the Sieve of Eratosthenes."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

primes_sieve = sieve_of_eratosthenes(N)
prime_count_sieve = len(primes_sieve)
print(f"Sieve of Eratosthenes: found {prime_count_sieve} primes in [1, {N}]")
print(f"  First 10: {primes_sieve[:10]}")
print(f"  Last 10:  {primes_sieve[-10:]}")

# 4. CROSS-CHECK — trial division (Rule 6)
def is_prime_trial(n):
    """Check primality by trial division."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

primes_trial = [i for i in range(1, N + 1) if is_prime_trial(i)]
prime_count_trial = len(primes_trial)
print(f"\nTrial division: found {prime_count_trial} primes in [1, {N}]")

# Verify both methods produce identical lists
assert primes_sieve == primes_trial, (
    f"Cross-check failed: sieve produced {prime_count_sieve} primes, "
    f"trial division produced {prime_count_trial} primes"
)
print(f"Cross-check: both methods agree — {prime_count_sieve} primes")

# 5. PERCENTAGE COMPUTATION (Rule 7)
percentage = explain_calc(
    "prime_count_sieve / N * 100",
    {"prime_count_sieve": prime_count_sieve, "N": N},
    label="percentage of primes in [1, 1000]"
)

# 6. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Could the sieve or trial division have a bug that undercounts primes?",
        "verification_performed": (
            "Cross-checked two independent algorithms (Sieve of Eratosthenes and trial division). "
            "Both produce identical prime lists. Additionally, the result of 168 primes up to 1000 "
            "is a well-known value in number theory, denoted π(1000) = 168."
        ),
        "finding": "Both methods agree on 168 primes. This matches the known value π(1000) = 168.",
        "breaks_proof": False,
    },
    {
        "question": "Is there an interpretation where '20 percent' could mean something other than 200 out of 1000?",
        "verification_performed": (
            "Considered whether 'fewer than 20 percent' could be non-strict (≤ vs <). "
            "The phrase 'fewer than' is unambiguously strict inequality. Even under ≤, "
            "168 ≤ 200 holds, so the claim would still be true."
        ),
        "finding": "No alternative interpretation changes the result. 168 < 200 under any reading.",
        "breaks_proof": False,
    },
]

# 7. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    claim_holds = compare(percentage, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                          label="prime percentage < 20%")

    # Pure-math: no citations
    verdict = "PROVED" if claim_holds else "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = "Sieve of Eratosthenes"
    FACT_REGISTRY["A1"]["result"] = str(prime_count_sieve)
    FACT_REGISTRY["A2"]["method"] = "Trial division"
    FACT_REGISTRY["A2"]["result"] = str(prime_count_trial)
    FACT_REGISTRY["A3"]["method"] = "prime_count / 1000 * 100"
    FACT_REGISTRY["A3"]["result"] = f"{percentage}%"

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "cross_checks": [
            {
                "description": "Sieve of Eratosthenes vs trial division prime count",
                "values_compared": [str(prime_count_sieve), str(prime_count_trial)],
                "agreement": prime_count_sieve == prime_count_trial,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "prime_count": prime_count_sieve,
            "total_integers": N,
            "percentage": percentage,
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
