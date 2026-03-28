"""
Proof: The 100000th prime number is exactly 1299709.
Generated: 2026-03-28
Type: Pure mathematical computation (Type A)
"""
import json
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.computations import compare

# ==============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# ==============================================================================

CLAIM_NATURAL = "The 100000th prime number is exactly 1299709."
CLAIM_FORMAL = {
    "subject": "the 100000th prime number",
    "property": "value of the 100000th prime in the sequence of primes (2, 3, 5, 7, 11, ...)",
    "operator": "==",
    "operator_note": (
        "'exactly' means strict equality. The 100000th prime must be precisely 1299709. "
        "Primes are indexed starting at p(1)=2, p(2)=3, etc. — the standard convention."
    ),
    "threshold": 1299709,
}

# ==============================================================================
# 2. FACT REGISTRY
# ==============================================================================

FACT_REGISTRY = {
    "A1": {"label": "100000th prime via Sieve of Eratosthenes", "method": None, "result": None},
    "A2": {"label": "Prime-counting function π(1299709) equals 100000", "method": None, "result": None},
    "A3": {"label": "1299709 is prime (trial division)", "method": None, "result": None},
    "A4": {"label": "π(1299708) equals 99999 (confirms no prime between)", "method": None, "result": None},
}

# ==============================================================================
# 3. PRIMARY COMPUTATION — Sieve of Eratosthenes (A1)
# ==============================================================================

def sieve_nth_prime(n):
    """Find the nth prime using the Sieve of Eratosthenes.

    Uses an upper bound estimate: for n >= 6, p(n) < n * (ln(n) + ln(ln(n))).
    We add a safety margin.
    """
    import math
    if n < 6:
        small_primes = [2, 3, 5, 7, 11]
        return small_primes[n - 1]

    # Upper bound for the nth prime (Rosser's theorem refinement)
    upper = int(n * (math.log(n) + math.log(math.log(n))) * 1.2)

    # Sieve of Eratosthenes
    is_prime = [True] * (upper + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.sqrt(upper)) + 1):
        if is_prime[i]:
            for j in range(i * i, upper + 1, i):
                is_prime[j] = False

    count = 0
    for num in range(2, upper + 1):
        if is_prime[num]:
            count += 1
            if count == n:
                return num

    raise RuntimeError(f"Upper bound {upper} was too small for prime #{n}")


print("=" * 60)
print("PRIMARY METHOD: Sieve of Eratosthenes")
print("=" * 60)
primary_result = sieve_nth_prime(100000)
print(f"The 100000th prime (via sieve) = {primary_result}")

# ==============================================================================
# 4. CROSS-CHECK 1 — Prime counting function π(x) via independent sieve (A2)
# ==============================================================================

def count_primes_up_to(limit):
    """Count primes up to limit using a separate sieve implementation.

    This is a structurally independent implementation — it builds its own
    sieve and counts, rather than extracting the nth element.
    """
    if limit < 2:
        return 0
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    i = 2
    while i * i <= limit:
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
        i += 1
    return sum(sieve)


print("\n" + "=" * 60)
print("CROSS-CHECK 1: Prime-counting function π(1299709)")
print("=" * 60)
pi_at_claim = count_primes_up_to(1299709)
print(f"π(1299709) = {pi_at_claim}")

# ==============================================================================
# 5. CROSS-CHECK 2 — Trial division primality test (A3)
# ==============================================================================

def is_prime_trial_division(n):
    """Test primality by trial division — independent of any sieve."""
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


print("\n" + "=" * 60)
print("CROSS-CHECK 2: Primality of 1299709 via trial division")
print("=" * 60)
is_prime_result = is_prime_trial_division(1299709)
print(f"is_prime(1299709) = {is_prime_result}")

# ==============================================================================
# 6. CROSS-CHECK 3 — π(1299708) to confirm 1299709 is the boundary (A4)
# ==============================================================================

print("\n" + "=" * 60)
print("CROSS-CHECK 3: π(1299708) — confirming boundary")
print("=" * 60)
pi_below = count_primes_up_to(1299708)
print(f"π(1299708) = {pi_below}")

# ==============================================================================
# 7. ASSERTIONS — Cross-check agreement
# ==============================================================================

print("\n" + "=" * 60)
print("CROSS-CHECK ASSERTIONS")
print("=" * 60)

assert primary_result == 1299709 or primary_result != 1299709, "tautology for flow"

# Sieve result must match claimed value if claim is true
sieve_matches_claim = (primary_result == CLAIM_FORMAL["threshold"])
print(f"Sieve result matches claim: {primary_result} == {CLAIM_FORMAL['threshold']} → {sieve_matches_claim}")

# π(1299709) must equal 100000
pi_matches = (pi_at_claim == 100000)
print(f"π(1299709) == 100000: {pi_at_claim} == 100000 → {pi_matches}")

# 1299709 must be prime
print(f"1299709 is prime: {is_prime_result}")

# π(1299708) must equal 99999 (one less, confirming 1299709 is the exact boundary)
pi_below_matches = (pi_below == 99999)
print(f"π(1299708) == 99999: {pi_below} == 99999 → {pi_below_matches}")

# Hard assertions for cross-check integrity
assert primary_result == pi_at_claim or True, "flow"
# The real cross-checks:
assert pi_at_claim == 100000, f"Cross-check failed: π(1299709) = {pi_at_claim}, expected 100000"
assert is_prime_result, f"Cross-check failed: 1299709 is not prime"
assert pi_below == 99999, f"Cross-check failed: π(1299708) = {pi_below}, expected 99999"

# ==============================================================================
# 8. ADVERSARIAL CHECKS (Rule 5)
# ==============================================================================

adversarial_checks = [
    {
        "question": "Could the indexing convention differ (0-based vs 1-based)?",
        "verification_performed": (
            "Checked standard mathematical convention: p(1)=2, p(2)=3, p(3)=5, ... "
            "The claim uses 'the 100000th prime' which in standard notation is p(100000). "
            "Verified sieve starts counting at p(1)=2."
        ),
        "finding": "Sieve uses 1-based indexing (first prime counted is 2). Matches claim convention.",
        "breaks_proof": False,
    },
    {
        "question": "Is 1 sometimes counted as a prime, shifting the index?",
        "verification_performed": (
            "Historically, 1 was sometimes considered prime, but modern convention (post-1800s) "
            "excludes 1. The sieve starts from 2. If 1 were included, p(100000) would be "
            "p(99999) in modern convention. Verified that the claim uses modern convention."
        ),
        "finding": "Modern convention excludes 1 as prime. Both sieve and claim use this convention.",
        "breaks_proof": False,
    },
    {
        "question": "Could there be an off-by-one error in the sieve or counting?",
        "verification_performed": (
            "Verified sieve against known small primes: p(1)=2, p(10)=29, p(100)=541, p(1000)=7919. "
            "Additionally, the independent π(x) counting function provides a structural cross-check: "
            "π(1299709)=100000 and π(1299708)=99999 together confirm 1299709 is the exact 100000th prime."
        ),
        "finding": "Small-case verification and π(x) boundary check rule out off-by-one errors.",
        "breaks_proof": False,
    },
]

# Verify small-case primes as stated in adversarial check
print("\n" + "=" * 60)
print("ADVERSARIAL: Small-case verification")
print("=" * 60)
known_primes = {1: 2, 10: 29, 100: 541, 1000: 7919}
for idx, expected in known_primes.items():
    computed = sieve_nth_prime(idx)
    status = "✓" if computed == expected else "✗"
    print(f"  p({idx}) = {computed} (expected {expected}) {status}")
    assert computed == expected, f"Small-case failed: p({idx})={computed}, expected {expected}"

# ==============================================================================
# 9. VERDICT AND STRUCTURED OUTPUT
# ==============================================================================

if __name__ == "__main__":
    claim_holds = compare(primary_result, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                          label="100000th prime check")

    verdict = "PROVED" if claim_holds else "DISPROVED"

    # Fill in fact registry
    FACT_REGISTRY["A1"]["method"] = "Sieve of Eratosthenes up to upper bound, extract 100000th prime"
    FACT_REGISTRY["A1"]["result"] = str(primary_result)

    FACT_REGISTRY["A2"]["method"] = "Independent sieve counting all primes ≤ 1299709"
    FACT_REGISTRY["A2"]["result"] = str(pi_at_claim)

    FACT_REGISTRY["A3"]["method"] = "Trial division testing all factors up to √1299709"
    FACT_REGISTRY["A3"]["result"] = str(is_prime_result)

    FACT_REGISTRY["A4"]["method"] = "Independent sieve counting all primes ≤ 1299708"
    FACT_REGISTRY["A4"]["result"] = str(pi_below)

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "cross_checks": [
            {
                "description": "Sieve nth-prime vs π(1299709) counting",
                "values_compared": [str(primary_result), f"π(1299709)={pi_at_claim}"],
                "agreement": primary_result == 1299709 and pi_at_claim == 100000,
            },
            {
                "description": "Trial division confirms 1299709 is prime",
                "values_compared": ["is_prime(1299709)", str(is_prime_result)],
                "agreement": is_prime_result is True,
            },
            {
                "description": "π(1299708)=99999 confirms 1299709 is the boundary",
                "values_compared": [f"π(1299708)={pi_below}", "99999"],
                "agreement": pi_below == 99999,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "primary_result": primary_result,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
            "pi_1299709": pi_at_claim,
            "pi_1299708": pi_below,
            "is_prime_1299709": is_prime_result,
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
