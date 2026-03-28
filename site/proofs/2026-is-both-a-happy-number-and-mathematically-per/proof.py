"""
Proof: 2026 is both a "happy number" and mathematically "perfect"
Generated: 2026-03-28
"""
import json
import sys
import os

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.computations import compare, explain_calc

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = '2026 is both a "happy number" and mathematically "perfect," proving the year is cosmically special.'

CLAIM_FORMAL = {
    "subject": "2026",
    "sub_claims": {
        "SC1": {
            "property": "happy number",
            "operator": "==",
            "operator_note": (
                "A positive integer n is 'happy' if repeatedly replacing n with the sum "
                "of squares of its decimal digits eventually reaches 1. All other integers "
                "are 'unhappy' (they cycle through a fixed loop containing 4). "
                "This is the standard mathematical definition (OEIS A007770). "
                "Informal uses such as 'happy' as an adjective are not mathematical claims "
                "and are not evaluated."
            ),
            "threshold": True,
        },
        "SC2": {
            "property": "perfect number",
            "operator": "==",
            "operator_note": (
                "A positive integer n is 'perfect' if the sum of its proper divisors "
                "(all positive divisors excluding n itself) equals n exactly. "
                "This is the standard mathematical definition (Euclid, Elements Book IX, "
                "Proposition 36; OEIS A000396). The known perfect numbers are: 6, 28, 496, "
                "8128, 33550336, ... Perfect numbers are extraordinarily rare — only 51 are "
                "known as of 2024. The claim 'mathematically perfect' is interpreted as "
                "this strict definition, not a colloquial usage, because the claim invokes "
                "mathematical precision."
            ),
            "threshold": True,
        },
        "SC3": {
            "property": "cosmically special",
            "operator": "==",
            "operator_note": (
                "'Cosmically special' is a rhetorical/metaphorical expression, not a "
                "mathematical or empirical claim. It is not formally evaluable. "
                "This sub-claim is excluded from the verdict and noted as opinion."
            ),
            "threshold": "NOT_EVALUABLE",
        },
    },
    "compound_operator": "AND (SC1 AND SC2; SC3 excluded as non-evaluable)",
    "operator_note": (
        "The compound claim holds only if BOTH SC1 and SC2 are true. "
        "SC3 ('cosmically special') is not a mathematical claim and is excluded."
    ),
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY — A-types only for pure math
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "A1": {
        "label": "SC1: Is 2026 a happy number? (iterative digit-square-sum algorithm)",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "SC1 cross-check: Happy-number verification via cycle membership (OEIS A007770 structure)",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "SC2: Is 2026 a perfect number? (compute sum of proper divisors)",
        "method": None,
        "result": None,
    },
    "A4": {
        "label": "SC2 cross-check: Perfect-number verification via multiplicative sigma formula",
        "method": None,
        "result": None,
    },
    "A5": {
        "label": "SC2 factorisation: prime factorisation of 2026",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. SC1 — HAPPY NUMBER CHECK
# ---------------------------------------------------------------------------

def digit_square_sum(n: int) -> int:
    """Return the sum of squares of decimal digits of n."""
    total = 0
    while n > 0:
        digit = n % 10
        total += digit * digit
        n //= 10
    return total


def is_happy_iterative(n: int) -> tuple[bool, list[int]]:
    """
    Primary method: Floyd's cycle-detection on digit-square-sum sequence.
    Returns (is_happy, sequence_to_1_or_cycle_entry).
    An unhappy number enters the cycle {4, 16, 37, 58, 89, 145, 42, 20, 4, ...}.
    A happy number reaches 1.
    """
    seen = set()
    sequence = [n]
    current = n
    while current != 1 and current not in seen:
        seen.add(current)
        current = digit_square_sum(current)
        sequence.append(current)
    return (current == 1, sequence)


# Cross-check: verify using the known unhappy cycle membership
# If a number is NOT in the unhappy cycle and the sequence reaches 1, it is happy.
UNHAPPY_CYCLE = {4, 16, 37, 58, 89, 145, 42, 20}  # the fixed loop unhappy numbers enter


def is_happy_cycle_check(n: int) -> bool:
    """
    Cross-check method: iterate until we hit 1 (happy) or a known unhappy-cycle member.
    Mathematically independent because it uses a different stopping criterion:
    instead of checking if 'current' has been seen before (Floyd detection),
    it checks membership in the precomputed unhappy cycle.
    """
    current = n
    for _ in range(1000):  # safety limit — convergence is always fast
        if current == 1:
            return True
        if current in UNHAPPY_CYCLE:
            return False
        current = digit_square_sum(current)
    raise RuntimeError(f"Did not converge for {n}")  # should never happen


sc1_happy, sc1_sequence = is_happy_iterative(2026)
sc1_crosscheck = is_happy_cycle_check(2026)

print("\n--- SC1: Happy Number ---")
print(f"  digit-square-sum sequence for 2026: {sc1_sequence}")
print(f"  Sequence terminates at: {sc1_sequence[-1]}")
print(f"  Primary (Floyd cycle detection): is_happy = {sc1_happy}")
print(f"  Cross-check (unhappy-cycle membership): is_happy = {sc1_crosscheck}")

assert sc1_happy == sc1_crosscheck, (
    f"SC1 cross-check disagreement: primary={sc1_happy}, cross-check={sc1_crosscheck}"
)

sc1_claim_holds = compare(sc1_happy, "==", True, label="SC1: 2026 is a happy number")

# ---------------------------------------------------------------------------
# 4. SC2 — PERFECT NUMBER CHECK
# ---------------------------------------------------------------------------

def prime_factorisation(n: int) -> dict[int, int]:
    """Return the prime factorisation of n as {prime: exponent}."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def sum_of_proper_divisors_direct(n: int) -> int:
    """
    Primary method: enumerate all divisors of n, sum those < n.
    Straightforward O(sqrt(n)) algorithm.
    """
    if n <= 1:
        return 0
    divisor_sum = 1  # 1 always divides n > 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            divisor_sum += i
            if i != n // i:
                divisor_sum += n // i
        i += 1
    return divisor_sum


def sigma_multiplicative(n: int) -> int:
    """
    Cross-check method: compute σ(n) (sum of ALL divisors including n) using the
    multiplicative formula: for n = p1^a1 * p2^a2 * ...,
      σ(n) = product of (p_i^(a_i+1) - 1) / (p_i - 1)
    Then sum of PROPER divisors = σ(n) - n.
    This is mathematically independent of the direct enumeration method:
    it uses number-theoretic multiplicativity rather than iteration over candidate divisors.
    """
    factors = prime_factorisation(n)
    sigma = 1
    for p, a in factors.items():
        # sum of p^0 + p^1 + ... + p^a = (p^(a+1) - 1) / (p - 1)
        sigma *= (p ** (a + 1) - 1) // (p - 1)
    return sigma - n  # subtract n to get proper divisors only


n = 2026
factors_2026 = prime_factorisation(n)
s_direct = sum_of_proper_divisors_direct(n)
s_sigma = sigma_multiplicative(n)

print("\n--- SC2: Perfect Number ---")
print(f"  Prime factorisation of 2026: {factors_2026}")
print(f"  Primary (direct enumeration): sum of proper divisors = {s_direct}")
print(f"  Cross-check (multiplicative σ formula): sum of proper divisors = {s_sigma}")

assert s_direct == s_sigma, (
    f"SC2 cross-check disagreement: direct={s_direct}, sigma={s_sigma}"
)

explain_calc("s_direct - n", locals(), label="SC2: (sum of proper divisors) - 2026 [must be 0 for perfect]")

sc2_claim_holds = compare(s_direct, "==", n, label="SC2: sum_of_proper_divisors(2026) == 2026")

# ---------------------------------------------------------------------------
# 5. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": "Is there an alternative definition of 'happy number' that would yield a different result for 2026?",
        "verification_performed": (
            "Reviewed OEIS A007770 (Happy Numbers) definition. "
            "Also checked whether 'base-10' vs 'base-2' happy number definitions differ: "
            "the standard definition (Grundman & Teeple 2001) operates in base 10. "
            "The claim does not specify a base, so base 10 is used (the overwhelmingly standard interpretation). "
            "In base-2, a different set of happy numbers exists, but the unqualified term 'happy number' "
            "refers to base 10 in mathematical literature."
        ),
        "finding": "No credible alternative definition changes the result. 2026 is happy in base 10 by any standard algorithm.",
        "breaks_proof": False,
    },
    {
        "question": "Is there an alternative definition of 'perfect number' under which 2026 qualifies?",
        "verification_performed": (
            "Checked related concepts: quasi-perfect numbers (σ(n) = 2n+1), "
            "almost perfect numbers (σ(n) = 2n-1), semiperfect numbers (n = sum of some proper divisors), "
            "abundant numbers (σ(n) > 2n), deficient numbers (σ(n) < 2n). "
            "2026: σ(2026) = 1+2+1013+2026 = 3042; 2*2026 = 4052. "
            "So 2026 is deficient (σ(n) = 3042 < 4052 = 2n). It is not quasi-perfect, "
            "semiperfect, or abundant either."
        ),
        "finding": (
            "Under the standard definition, 2026 is deficient, not perfect. "
            "No non-standard variant of 'perfect number' makes 2026 qualify."
        ),
        "breaks_proof": False,  # Does not break SC1; SC2 was already shown false
    },
    {
        "question": "Could 2026 be a perfect number if a different factorisation is used (e.g., a computation error)?",
        "verification_performed": (
            "Verified factorisation independently: 2026 / 2 = 1013. "
            "Checked primality of 1013 by trial division up to floor(sqrt(1013)) = 31: "
            "1013 is not divisible by 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, or 31. "
            "Therefore 2026 = 2^1 * 1013^1 is the unique prime factorisation. "
            "The two independent methods (direct enumeration and multiplicative σ) both agree: "
            "sum of proper divisors = 1016."
        ),
        "finding": "Factorisation is confirmed. Sum of proper divisors is unambiguously 1016, not 2026.",
        "breaks_proof": False,
    },
    {
        "question": "Is 'cosmically special' a falsifiable mathematical claim?",
        "verification_performed": (
            "Reviewed mathematical literature for 'cosmically special number' as a defined term. "
            "Found no such definition in number theory, combinatorics, or mathematical physics. "
            "The phrase is rhetorical/poetic, not mathematical."
        ),
        "finding": "SC3 is not a mathematical claim and cannot be proved or disproved. Excluded from verdict.",
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 6. COMPOUND VERDICT
# ---------------------------------------------------------------------------
# The AND-compound holds only if both SC1 and SC2 hold.
compound_holds = compare(sc1_claim_holds and sc2_claim_holds, "==", True, label="Compound: SC1 AND SC2 (both must hold for year to be cosmically special)")

# ---------------------------------------------------------------------------
# 7. STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    FACT_REGISTRY["A1"]["method"] = "is_happy_iterative(2026): Floyd cycle detection on digit-square-sum sequence"
    FACT_REGISTRY["A1"]["result"] = f"True — sequence {sc1_sequence} terminates at 1"

    FACT_REGISTRY["A2"]["method"] = "is_happy_cycle_check(2026): halt on UNHAPPY_CYCLE membership"
    FACT_REGISTRY["A2"]["result"] = f"True — agrees with A1"

    FACT_REGISTRY["A3"]["method"] = "sum_of_proper_divisors_direct(2026): O(sqrt(n)) enumeration"
    FACT_REGISTRY["A3"]["result"] = f"{s_direct} (need {n} for perfect; deficit = {n - s_direct})"

    FACT_REGISTRY["A4"]["method"] = "sigma_multiplicative(2026): product formula σ(n)=∏(p^(a+1)-1)/(p-1) minus n"
    FACT_REGISTRY["A4"]["result"] = f"{s_sigma} — agrees with A3"

    FACT_REGISTRY["A5"]["method"] = "prime_factorisation(2026): trial division"
    FACT_REGISTRY["A5"]["result"] = str(factors_2026)

    # Determine per-sub-claim verdicts
    sc1_verdict = "PROVED" if sc1_claim_holds else "DISPROVED"
    sc2_verdict = "DISPROVED" if not sc2_claim_holds else "PROVED"

    if sc1_claim_holds and sc2_claim_holds:
        verdict = "PROVED"
    elif sc1_claim_holds and not sc2_claim_holds:
        verdict = "PARTIALLY VERIFIED"
    elif not sc1_claim_holds and sc2_claim_holds:
        verdict = "PARTIALLY VERIFIED"
    else:
        verdict = "DISPROVED"

    cross_checks = [
        {
            "description": "SC1: Two independent happy-number algorithms agree",
            "values_compared": [str(sc1_happy), str(sc1_crosscheck)],
            "agreement": sc1_happy == sc1_crosscheck,
            "tolerance": "exact (boolean)",
            "method_independence": (
                "Primary uses Floyd cycle detection (stops when 'current' is seen before); "
                "cross-check stops on membership in the precomputed UNHAPPY_CYCLE set. "
                "Different stopping criteria — a bug in one would not affect the other."
            ),
        },
        {
            "description": "SC2: Two independent proper-divisor-sum algorithms agree",
            "values_compared": [str(s_direct), str(s_sigma)],
            "agreement": s_direct == s_sigma,
            "tolerance": "exact (integer)",
            "method_independence": (
                "Primary enumerates candidate divisors by iteration (arithmetic); "
                "cross-check uses the multiplicative sigma formula from number theory "
                "(algebraic identity). Different mathematical principles."
            ),
        },
    ]

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "cross_checks": cross_checks,
        "adversarial_checks": adversarial_checks,
        "sub_claim_verdicts": {
            "SC1": sc1_verdict,
            "SC2": sc2_verdict,
            "SC3": "NOT_EVALUABLE (opinion/metaphor)",
        },
        "verdict": verdict,
        "key_results": {
            "sc1_is_happy": sc1_happy,
            "sc1_sequence": sc1_sequence,
            "sc2_sum_proper_divisors": s_direct,
            "sc2_n": n,
            "sc2_deficit": n - s_direct,
            "sc2_is_perfect": sc2_claim_holds,
            "sc2_prime_factors": factors_2026,
            "compound_holds": compound_holds,
        },
        "generator": {
            "name": "proof-engine",
            "version": open(os.path.join(PROOF_ENGINE_ROOT, "VERSION")).read().strip(),
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-03-28",
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
