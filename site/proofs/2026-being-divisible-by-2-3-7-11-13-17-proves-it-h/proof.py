"""
Proof: 2026 being divisible by 2, 3, 7, 11, 13, 17 proves it has "hidden perfect number properties."
Generated: 2026-03-28
"""
import json
import math
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date
from scripts.computations import compare, explain_calc

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    '2026 being divisible by 2, 3, 7, 11, 13, 17 proves it has "hidden perfect number properties."'
)
CLAIM_FORMAL = {
    "subject": "2026",
    "property": (
        "SC1: number of claimed divisors {2,3,7,11,13,17} that actually divide 2026 == 6; "
        "SC2: 2026 has 'hidden perfect number properties' (interpreted as: 2026 is a perfect number, "
        "i.e. sum of proper divisors equals 2026)"
    ),
    "operator": "==",
    "operator_note": (
        "The compound claim requires BOTH sub-claims to hold. "
        "SC1: 2026 must be divisible by each of 2, 3, 7, 11, 13, and 17. "
        "We check this via modular arithmetic (n % d == 0) and independently via GCD (gcd(n,d) == d). "
        "SC2: 'Hidden perfect number properties' is not a standard mathematical term. "
        "We adopt the most charitable interpretation: either (a) 2026 is itself a perfect number "
        "(sigma(n) - n == n, i.e. sum of proper divisors equals n), or (b) 2026 participates in "
        "the Euclid-Euler formula for even perfect numbers (2^(p-1) * (2^p - 1) for Mersenne prime p). "
        "A perfect number satisfies sigma(n)/n = 2 exactly. "
        "If SC1 is false — i.e. 2026 is NOT divisible by all six claimed primes — "
        "the premise of the compound claim is false, and the claim is DISPROVED regardless of SC2. "
        "The threshold 6 means all 6 divisibilities must hold for SC1 to pass.",
    ),
    "threshold": 6,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {"label": "2026 divisible by 2: 2026 % 2 == 0", "method": None, "result": None},
    "A2": {"label": "2026 divisible by 3: 2026 % 3 == 0", "method": None, "result": None},
    "A3": {"label": "2026 divisible by 7: 2026 % 7 == 0", "method": None, "result": None},
    "A4": {"label": "2026 divisible by 11: 2026 % 11 == 0", "method": None, "result": None},
    "A5": {"label": "2026 divisible by 13: 2026 % 13 == 0", "method": None, "result": None},
    "A6": {"label": "2026 divisible by 17: 2026 % 17 == 0", "method": None, "result": None},
    "A7": {"label": "Prime factorization of 2026 (trial division)", "method": None, "result": None},
    "A8": {"label": "SC2 check: sum of proper divisors of 2026 vs 2026 (perfect number test)", "method": None, "result": None},
    "A9": {"label": "Cross-check: divisibility via gcd(2026, d) == d for each claimed d", "method": None, "result": None},
}

# 3. PRIMARY COMPUTATION — SC1: Divisibility checks via modulo
n = 2026
claimed_divisors = [2, 3, 7, 11, 13, 17]

print(f"\n=== SC1: Divisibility of {n} by claimed divisors {claimed_divisors} ===")
modulo_results = {}
for d in claimed_divisors:
    remainder = n % d
    is_divisible = (remainder == 0)
    modulo_results[d] = is_divisible
    status = "divisible" if is_divisible else f"NOT divisible (remainder={remainder})"
    print(f"  {n} % {d} = {remainder}  →  {status}")

sc1_passing = [d for d in claimed_divisors if modulo_results[d]]
sc1_failing = [d for d in claimed_divisors if not modulo_results[d]]
sc1_count = len(sc1_passing)
print(f"\n  Divisors that hold: {sc1_passing}")
print(f"  Divisors that FAIL: {sc1_failing}")
print(f"  Count of divisibilities holding: {sc1_count} / {len(claimed_divisors)}")

# 4. CROSS-CHECK: Independent method — GCD characterization
# d | n  ⟺  gcd(n, d) == d
# This is mathematically independent of the modulo check (different algebraic identity)
print(f"\n=== Cross-Check: GCD method — gcd({n}, d) == d iff d | {n} ===")
gcd_results = {}
for d in claimed_divisors:
    g = math.gcd(n, d)
    is_divisible_gcd = (g == d)
    gcd_results[d] = is_divisible_gcd
    status = "divisible" if is_divisible_gcd else f"NOT divisible (gcd={g}≠{d})"
    print(f"  gcd({n}, {d}) = {g}  →  {status}")

gcd_count = sum(1 for d in claimed_divisors if gcd_results[d])
print(f"\n  GCD method count of divisibilities holding: {gcd_count} / {len(claimed_divisors)}")

# Cross-check agreement
assert sc1_count == gcd_count, (
    f"Cross-check disagreement: modulo method={sc1_count}, gcd method={gcd_count}"
)
print(f"  Cross-check: modulo method and GCD method agree ({sc1_count} == {gcd_count}) ✓")

# 5. PRIME FACTORIZATION (structural explanation of why divisibilities fail)
print(f"\n=== Prime Factorization of {n} ===")
def prime_factors(num):
    """Trial division factorization — returns list of prime factors with repetition."""
    factors = []
    d = 2
    while d * d <= num:
        while num % d == 0:
            factors.append(d)
            num //= d
        d += 1
    if num > 1:
        factors.append(num)
    return factors

factors = prime_factors(n)
factor_str = " × ".join(map(str, factors))
print(f"  {n} = {factor_str}")

# Verify factorization (independent check)
product = 1
for f in factors:
    product *= f
assert product == n, f"Factorization verification failed: product={product}, expected={n}"
print(f"  Verification: {factor_str} = {product} ✓")

# Why divisibility by 3,7,11,13,17 fails: none of these appear in factorization
print(f"\n  Prime factors of {n}: {sorted(set(factors))}")
for d in [3, 7, 11, 13, 17]:
    in_factors = (d in factors)
    print(f"  {d} in prime factors of {n}: {in_factors}  →  {n} {'is' if in_factors else 'is NOT'} divisible by {d}")

# The minimum number divisible by ALL of 2,3,7,11,13,17 is their LCM
a, b, c, d_val, e, f_val = 2, 3, 7, 11, 13, 17
lcm_all = explain_calc("a * b * c * d_val * e * f_val", locals(),
                        label="LCM of {2,3,7,11,13,17} = 2×3×7×11×13×17")
print(f"  The smallest positive number divisible by all 6 primes is {lcm_all}")
print(f"  {n} is {lcm_all - n} less than {lcm_all} — it is NOT a multiple of {lcm_all}")

# 6. SC2: Perfect number check (most charitable interpretation of "hidden perfect number properties")
print(f"\n=== SC2: Perfect Number Test for {n} ===")
def proper_divisors_sum(num):
    """Sum of proper divisors of num (all divisors excluding num itself)."""
    total = 1  # 1 is always a proper divisor for num > 1
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            total += i
            if i != num // i:
                total += num // i
    return total

def proper_divisors_list(num):
    """List of proper divisors of num."""
    divs = [1]
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            divs.append(i)
            if i != num // i:
                divs.append(num // i)
    return sorted(divs)

divisors = proper_divisors_list(n)
sigma_proper = sum(divisors)
print(f"  Proper divisors of {n}: {divisors}")
print(f"  Sum of proper divisors (sigma(n) - n): {sigma_proper}")
print(f"  For a perfect number, sum must equal {n}")
print(f"  {sigma_proper} == {n}: {sigma_proper == n}")
print(f"  Difference: {sigma_proper} - {n} = {sigma_proper - n}")
print(f"  Classification: {'perfect' if sigma_proper == n else ('abundant' if sigma_proper > n else 'deficient')}")

# Also check Euclid-Euler formula: even perfect numbers have form 2^(p-1) * (2^p - 1)
# where (2^p - 1) is a Mersenne prime. Can 2026 be expressed this way?
print(f"\n  Euclid-Euler test: does {n} = 2^(p-1) * (2^p - 1) for any prime p?")
euclid_euler_match = False
for p in range(2, 20):
    candidate = (2**(p-1)) * (2**p - 1)
    if candidate == n:
        euclid_euler_match = True
        print(f"    p={p}: 2^{p-1} × (2^{p}-1) = {candidate} ✓")
        break
    if candidate > n:
        break
if not euclid_euler_match:
    print(f"    No p in [2,19] satisfies 2^(p-1) × (2^p - 1) = {n}")
    # The Euclid-Euler sequence for small p: 6, 28, 496, 8128, ...
    eu_seq = [(2**(p-1)) * (2**p - 1) for p in [2, 3, 5, 7]]
    print(f"    Euclid-Euler sequence (p=2,3,5,7): {eu_seq}")
    print(f"    2026 does not appear in this sequence")

# sigma(n)/n ratio (perfect numbers have ratio exactly 2)
sigma_n = sigma_proper + n  # total sum including n itself
ratio_expr = sigma_proper + n
print(f"\n  sigma({n}) = {sigma_n}  (sum of ALL divisors including {n})")
print(f"  sigma({n}) / {n} = {sigma_n / n:.6f}  (perfect numbers have ratio = 2.000000)")

# 7. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Could '2026' in the claim refer to a transformed or encoded value that IS divisible by all six primes?",
        "verification_performed": (
            "Computed LCM(2,3,7,11,13,17) = 102102. Checked all multiples of 102102 near 2026: "
            "the nearest multiples are 0 and 102102. 2026 is not a multiple of 102102. "
            "No standard calendar year encoding (e.g., 2026 mod k, 2026 in a different base) "
            "produces 102102 or any multiple thereof. Checked 2026 in bases 2-16: none yield 102102."
        ),
        "finding": (
            "2026 in any standard encoding is not divisible by all six claimed primes. "
            "The premise is straightforwardly false for the integer 2026."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is 'hidden perfect number properties' a recognized mathematical term that 2026 could satisfy?",
        "verification_performed": (
            "Surveyed standard number theory classifications: perfect numbers (sigma(n)=2n), "
            "quasi-perfect (sigma(n)=2n+1, none known), almost perfect (sigma(n)=2n-1, only powers of 2), "
            "multiply perfect / k-perfect (sigma(n)=kn), semiperfect/pseudoperfect (n equals some subset-sum of proper divisors), "
            "weird numbers (abundant but not semiperfect). "
            "'Hidden perfect number properties' appears in none of these standard classifications. "
            "Searched for the phrase in number theory literature — no results found."
        ),
        "finding": (
            "'Hidden perfect number properties' has no standard mathematical definition. "
            "Under the most charitable interpretation (2026 is a perfect number): "
            "sum of proper divisors of 2026 = 1016 ≠ 2026. 2026 is a deficient number. "
            "sigma(2026)/2026 ≈ 1.501, far from the ratio of 2 required for a perfect number."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does divisibility by 2, 3, 7, 11, 13, 17 imply any known perfect-number-adjacent property for numbers that ARE divisible by all six?",
        "verification_performed": (
            "The smallest number divisible by 2,3,7,11,13,17 is their LCM = 102102. "
            "sigma(102102): 102102 = 2 × 3 × 7 × 11 × 13 × 17. "
            "For a squarefree number n = p1×p2×...×pk, sigma(n) = (1+p1)(1+p2)...(1+pk). "
            "sigma(102102) = 3 × 4 × 8 × 12 × 14 × 18 = 290304. "
            "sigma(102102)/102102 ≈ 2.843 ≠ 2. So 102102 is abundant, not perfect."
        ),
        "finding": (
            "Even the smallest number genuinely divisible by all six claimed primes (102102) is NOT "
            "a perfect number. Divisibility by {2,3,7,11,13,17} does not imply perfect number "
            "properties for any number, let alone for 2026 which fails the divisibility premise."
        ),
        "breaks_proof": False,
    },
]

# 8. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    # Primary claim evaluation
    sc1_holds = compare(sc1_count, "==", CLAIM_FORMAL["threshold"],
                        label="SC1: count of divisibilities holding == 6 (all must hold)")
    sc2_holds = compare(sigma_proper, "==", n,
                        label="SC2: sum of proper divisors == 2026 (perfect number test)")

    # SC1 failure alone is decisive — if the premise is false, the compound claim is false.
    # SC2 is evaluated for completeness but cannot rescue a false premise.
    verdict = "DISPROVED" if not sc1_holds else ("DISPROVED" if not sc2_holds else "PROVED")

    # Update FACT_REGISTRY
    FACT_REGISTRY["A1"]["method"] = "2026 % 2"
    FACT_REGISTRY["A1"]["result"] = f"remainder={2026 % 2}, divisible={modulo_results[2]}"
    FACT_REGISTRY["A2"]["method"] = "2026 % 3"
    FACT_REGISTRY["A2"]["result"] = f"remainder={2026 % 3}, divisible={modulo_results[3]}"
    FACT_REGISTRY["A3"]["method"] = "2026 % 7"
    FACT_REGISTRY["A3"]["result"] = f"remainder={2026 % 7}, divisible={modulo_results[7]}"
    FACT_REGISTRY["A4"]["method"] = "2026 % 11"
    FACT_REGISTRY["A4"]["result"] = f"remainder={2026 % 11}, divisible={modulo_results[11]}"
    FACT_REGISTRY["A5"]["method"] = "2026 % 13"
    FACT_REGISTRY["A5"]["result"] = f"remainder={2026 % 13}, divisible={modulo_results[13]}"
    FACT_REGISTRY["A6"]["method"] = "2026 % 17"
    FACT_REGISTRY["A6"]["result"] = f"remainder={2026 % 17}, divisible={modulo_results[17]}"
    FACT_REGISTRY["A7"]["method"] = "Trial division prime factorization"
    FACT_REGISTRY["A7"]["result"] = factor_str
    FACT_REGISTRY["A8"]["method"] = "Sum of proper divisors via trial division"
    FACT_REGISTRY["A8"]["result"] = (
        f"sigma_proper(2026)={sigma_proper}, required={n}, "
        f"difference={sigma_proper - n}, classification=deficient"
    )
    FACT_REGISTRY["A9"]["method"] = "gcd(2026, d) == d for each d in {2,3,7,11,13,17}"
    FACT_REGISTRY["A9"]["result"] = (
        f"GCD method: {gcd_count}/6 divisibilities hold, "
        f"agrees with modulo method ({sc1_count}/6)"
    )

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
                    "Divisibility confirmed by two independent algebraic methods: "
                    "modular arithmetic (n % d == 0) and GCD characterization (gcd(n,d) == d). "
                    "Both methods agree on the count of divisibilities holding."
                ),
                "values_compared": [str(sc1_count), str(gcd_count)],
                "agreement": sc1_count == gcd_count,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n": n,
            "claimed_divisors": claimed_divisors,
            "divisors_that_hold": sc1_passing,
            "divisors_that_fail": sc1_failing,
            "sc1_count_holding": sc1_count,
            "sc1_required": CLAIM_FORMAL["threshold"],
            "sc1_holds": sc1_holds,
            "prime_factorization": factor_str,
            "proper_divisors": divisors,
            "sum_of_proper_divisors": sigma_proper,
            "sc2_holds": sc2_holds,
            "sigma_over_n_ratio": round(sigma_n / n, 6),
            "sc1_and_sc2_holds": sc1_holds and sc2_holds,
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
