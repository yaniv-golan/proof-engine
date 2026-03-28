#!/usr/bin/env python3
"""
Proof Engine — Open Problem: Goldbach Conjecture
Claim: The Goldbach conjecture holds for every even integer greater than 2.

This is an OPEN PROBLEM. Computational verification up to a finite bound
provides evidence but cannot prove the universal claim.
Verdict is always UNDETERMINED.
"""

import sys
import json
from datetime import date
from sympy import isprime, primerange

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.computations import compare, explain_calc

# ============================================================
# 1. CLAIM
# ============================================================

CLAIM_NATURAL = "The Goldbach conjecture holds for every even integer greater than 2."

CLAIM_FORMAL = {
    "subject": "Goldbach conjecture",
    "property": "counterexamples in range [4, 10^6]",
    "operator": "==",
    "threshold": 0,
    "claim_type": "open_problem",
    "operator_note": (
        "The Goldbach conjecture asserts that every even integer > 2 is the sum "
        "of two primes. This is an unresolved conjecture — no proof or disproof "
        "exists as of 2026. Computational verification up to a finite bound "
        "provides evidence but cannot prove the claim for all even integers. "
        "The literature records verification up to 4 x 10^18 (Oliveira e Silva, 2013). "
        "Our script verifies up to 10^6 with two independent methods. "
        "Verdict is always UNDETERMINED regardless of computational outcome."
    ),
}

VERIFICATION_BOUND = 10**6

# ============================================================
# 2. FACT REGISTRY
# ============================================================

FACT_REGISTRY = {
    "A1": {
        "label": "Primary check: counterexamples in [4, 10^6] via trial division",
        "type": "A",
        "key": "primary_check",
        "method": "",
        "result": "",
    },
    "A2": {
        "label": "Cross-check: counterexamples in [4, 10^6] via prime-pair sieve",
        "type": "A",
        "key": "cross_check",
        "method": "",
        "result": "",
    },
}

# ============================================================
# 3. PRIMARY COMPUTATION (Method 1: Trial Division)
# ============================================================

def goldbach_trial_division(bound):
    """For each even n in [4, bound], check if n = p + (n-p) where both are prime.
    Uses sympy.isprime for primality testing on each candidate."""
    counterexamples = []
    for n in range(4, bound + 1, 2):
        found_pair = False
        for p in range(2, n // 2 + 1):
            if isprime(p) and isprime(n - p):
                found_pair = True
                break
        if not found_pair:
            counterexamples.append(n)
    return counterexamples

# ============================================================
# 4. CROSS-CHECK (Method 2: Prime Sieve + Pair Check)
# ============================================================

def goldbach_prime_sieve(bound):
    """Generate all primes up to bound via sympy.primerange (sieve of Eratosthenes),
    then for each even n check if any prime p <= n/2 has (n-p) also in the prime set.
    Structurally independent: uses a pre-built set instead of per-candidate isprime()."""
    prime_list = sorted(primerange(2, bound))  # sorted list for ordered iteration
    prime_set = set(prime_list)                 # set for O(1) membership lookup
    counterexamples = []
    for n in range(4, bound + 1, 2):
        found_pair = False
        for p in prime_list:
            if p > n // 2:
                break
            if (n - p) in prime_set:
                found_pair = True
                break
        if not found_pair:
            counterexamples.append(n)
    return counterexamples

# ============================================================
# 5. ADVERSARIAL CHECKS (Rule 5)
# ============================================================

adversarial_checks = [
    {
        "question": "Has any counterexample to Goldbach's conjecture ever been found?",
        "verification_performed": (
            "Searched: 'Goldbach conjecture counterexample found disproved'. "
            "Reviewed Wikipedia, Physics Forums, Medium articles, and LessWrong. "
            "No counterexample has ever been reported."
        ),
        "finding": "No counterexample exists in the literature or computational records.",
        "breaks_proof": False,
    },
    {
        "question": "Has the Goldbach conjecture been formally proved or disproved?",
        "verification_performed": (
            "Searched: 'Goldbach conjecture proof solved 2024 2025 2026'. "
            "Found several claimed proofs in non-peer-reviewed venues (SSRN, SCIRP, "
            "preprints.org, ScienceOpen) but none accepted by the mainstream "
            "mathematical community. The conjecture remains open as of March 2026."
        ),
        "finding": (
            "No universally accepted proof or disproof exists. "
            "The conjecture is listed as an open problem by all major references."
        ),
        "breaks_proof": False,
    },
    {
        "question": "What is the current computational verification bound?",
        "verification_performed": (
            "Searched: 'Goldbach conjecture verified computational bound 2026'. "
            "Oliveira e Silva verified up to 4 x 10^18 (2013). "
            "The Gridbach project (2025) extended this further. "
            "A March 2025 preprint reports empirical verification beyond 4 quintillion."
        ),
        "finding": (
            "Verified computationally up to at least 4 x 10^18. Our 10^6 bound is "
            "far below the literature record but uses two independent methods."
        ),
        "breaks_proof": False,
    },
]

# ============================================================
# 6. MAIN
# ============================================================

if __name__ == "__main__":
    print(f"Claim (natural): {CLAIM_NATURAL}")
    print(f"Claim (formal): counterexamples in [4, {VERIFICATION_BOUND}] == 0")
    print(f"Claim type: open_problem")
    print()

    # --- Primary computation ---
    print("=" * 60)
    print("PRIMARY CHECK: Trial division method")
    print("=" * 60)
    counterexamples_primary = goldbach_trial_division(VERIFICATION_BOUND)
    n_primary = len(counterexamples_primary)
    print(f"Checked all even integers in [4, {VERIFICATION_BOUND}]")
    n_even = explain_calc(
        "(VERIFICATION_BOUND - 4) // 2 + 1",
        {"VERIFICATION_BOUND": VERIFICATION_BOUND},
        label="even integers checked",
    )
    print(f"Counterexamples found (trial division): {n_primary}")
    print()

    # --- Cross-check computation ---
    print("=" * 60)
    print("CROSS-CHECK: Prime sieve method")
    print("=" * 60)
    counterexamples_sieve = goldbach_prime_sieve(VERIFICATION_BOUND)
    n_sieve = len(counterexamples_sieve)
    print(f"Checked all even integers in [4, {VERIFICATION_BOUND}]")
    print(f"Counterexamples found (prime sieve): {n_sieve}")
    print()

    # --- Cross-check agreement ---
    print("=" * 60)
    print("CROSS-CHECK AGREEMENT")
    print("=" * 60)
    methods_agree = compare(n_primary, "==", n_sieve,
                            label="trial division vs prime sieve counterexample count")
    print()

    # --- Adversarial checks ---
    print("=" * 60)
    print("ADVERSARIAL CHECKS")
    print("=" * 60)
    for i, ac in enumerate(adversarial_checks, 1):
        print(f"\nAdversarial check {i}: {ac['question']}")
        print(f"  Verification: {ac['verification_performed']}")
        print(f"  Finding: {ac['finding']}")
        print(f"  Breaks proof: {ac['breaks_proof']}")
    print()

    # --- Verdict ---
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    n_counterexamples = n_primary
    no_counterexamples = compare(n_counterexamples, "==", 0,
                                  label=f"no counterexamples in [4, {VERIFICATION_BOUND}]")

    # Both branches produce UNDETERMINED — open problems cannot be resolved
    # by finite computation. The conditional documents *why*.
    if no_counterexamples:
        verdict = "UNDETERMINED"  # verified up to bound, but finite check != proof
        verdict_reason = (
            f"No counterexamples found up to {VERIFICATION_BOUND} by two independent "
            "methods. However, this is a universal conjecture over infinitely many "
            "even integers. Computational verification of a finite range cannot "
            "constitute a proof. The Goldbach conjecture remains an open problem."
        )
    else:
        verdict = "DISPROVED"  # a genuine counterexample would disprove the conjecture
        verdict_reason = (
            f"Counterexample(s) found: {counterexamples_primary}. "
            "The Goldbach conjecture is disproved."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Reason: {verdict_reason}")

    # --- Update FACT_REGISTRY ---
    FACT_REGISTRY["A1"]["method"] = "goldbach_trial_division() — isprime() per candidate"
    FACT_REGISTRY["A1"]["result"] = f"{n_primary} counterexamples in [4, {VERIFICATION_BOUND}]"
    FACT_REGISTRY["A2"]["method"] = "goldbach_prime_sieve() — primerange sieve + set lookup"
    FACT_REGISTRY["A2"]["result"] = f"{n_sieve} counterexamples in [4, {VERIFICATION_BOUND}]"

    # --- JSON Summary ---
    summary = {
        "claim_natural": CLAIM_NATURAL,
        "claim_formal": CLAIM_FORMAL,
        "fact_registry": FACT_REGISTRY,
        "citations": {},
        "extractions": {},
        "cross_checks": [
            {
                "description": "Trial division vs prime sieve methods",
                "value_a": n_primary,
                "value_b": n_sieve,
                "agree": methods_agree,
                "independence": (
                    "Mathematically independent: Method 1 uses per-number isprime() calls; "
                    "Method 2 pre-generates a prime set via sieve and uses set membership. "
                    "Different algorithms, different data structures."
                ),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "key_results": {
            "verified_up_to": VERIFICATION_BOUND,
            "counterexamples_found": n_counterexamples,
            "methods_agree": methods_agree,
            "literature_bound": "4 x 10^18 (Oliveira e Silva, 2013)",
        },
        "generator": {
            "name": "proof-engine",
            "version": "0.10.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": str(date.today()),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
