# Audit: A real number is rational if and only if its decimal expansion is eventually periodic

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Real numbers and their decimal expansions |
| Property | Biconditional equivalence between rationality and eventual periodicity |
| Operator | == |
| Threshold | True |
| Operator note | This is a biconditional (iff) claim with two directions: (1) rational => eventually periodic, and (2) eventually periodic => rational. Both must hold for the claim to be PROVED. "Eventually periodic" means there exist non-negative integers k (pre-period length) and p >= 1 (period length) such that for all n >= k, digit d(n) = d(n+p). A terminating decimal is eventually periodic with repeating 0s (or equivalently 9s). We verify computationally by testing both directions on a comprehensive set of cases. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| A1 | -- | Direction 1: Long division of p/q produces eventually periodic digits (pigeonhole on remainders) |
| A2 | -- | Direction 2: Every eventually periodic decimal converts to a fraction p/q |
| A3 | -- | Cross-check: Python Fraction confirms rational <-> periodic equivalence |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Long division of p/q produces eventually periodic digits | Long division tracking remainders; pigeonhole principle guarantees remainder repetition within q steps. Tested on 35 rationals (terminating, purely repeating, and mixed). | All 35 cases passed: expansion is eventually periodic and round-trips to original fraction |
| A2 | Every eventually periodic decimal converts to a fraction p/q | Algebraic conversion: multiply by 10^(k+p) and 10^k, subtract to eliminate repeating part, yielding ratio of integers. Tested on 14 periodic decimals. | All 14 cases converted to correct fractions and round-tripped |
| A3 | Cross-check: Python Fraction confirms rational <-> periodic equivalence | Exhaustive test of all p/q with 1 <= q <= 200, 0 <= p < q: long_division -> periodic_decimal_to_fraction must return original Fraction(p,q). Uses Python's Fraction for exact arithmetic. | 20,100 rationals tested, 0 failures |

*Source: proof.py JSON summary*

## Computation Traces

```
Period length for 1/7: len(period) = len([1, 4, 2, 8, 5, 7]) = 6
Pigeonhole upper bound (= denominator): q = 7
Algebraic: repeating block / (10^p - 1): 142857 / 999999 = 0.1429
Total rationals tested: tested = 20100
Failures found: failures = 0
Direction 1 (rational => periodic): True == True = True
Direction 2 (periodic => rational): True == True = True
Cross-check (exhaustive q<=200): True == True = True
Biconditional: both directions verified + cross-check: True == True = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

### Check 1: Does 0.(9) = 1 break the uniqueness of decimal expansions?

- **Verification performed:** Tested 0.(9) conversion: `periodic_decimal_to_fraction(True, 0, [], [9])` returns `Fraction(1, 1) = 1`. This is correct -- 0.999... = 1 is a well-known identity. Decimal representations are not unique, but the theorem holds: both 1.0(0) and 0.(9) are eventually periodic representations of the rational number 1.
- **Finding:** 0.(9) = 1 is handled correctly. Non-uniqueness does not affect the theorem.
- **Breaks proof:** No

### Check 2: Are there irrational numbers with "almost periodic" expansions?

- **Verification performed:** Considered sqrt(2) = 1.41421356..., the Champernowne constant, and Liouville's number. None are eventually periodic. The proof relies on algebraic structure (pigeonhole for long division, fraction reconstruction for periodic decimals), not on digit pattern detection in arbitrary real numbers.
- **Finding:** Almost-periodic irrationals do not affect the proof.
- **Breaks proof:** No

### Check 3: Does the proof handle edge cases (0, negatives, integers)?

- **Verification performed:** 0/1 = 0.0(0) terminates; -1/3 = -0.(3) with sign handled separately; 5/1 = 5.0(0) integer terminates; 100/4 = 25.0(0) integer from non-trivial fraction. All pass both directions.
- **Finding:** Edge cases handled correctly.
- **Breaks proof:** No

### Check 4: Could the pigeonhole argument fail for very large denominators?

- **Verification performed:** Pigeonhole guarantees repetition within q steps for denominator q. Tested q=97 (period 96, maximal for prime), q=127 (period 42), q=239. Exhaustive cross-check covers all q up to 200. The argument is valid for all positive q by the pigeonhole principle.
- **Finding:** Pigeonhole bound holds for all tested denominators.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A -- pure computation, no empirical facts
- **Rule 2:** N/A -- pure computation, no empirical facts
- **Rule 3:** `date.today()` used for generated_at timestamp
- **Rule 4:** CLAIM_FORMAL with operator_note explicitly documents biconditional interpretation and definition of "eventually periodic"
- **Rule 5:** Four adversarial checks covering edge cases (0.999...=1, almost-periodic irrationals, zero/negatives/integers, large denominators)
- **Rule 6:** N/A -- pure computation, no empirical facts. Cross-check uses exhaustive enumeration (mathematically independent from hand-picked test cases)
- **Rule 7:** `compare()` and `explain_calc()` imported from `scripts/computations.py`; no hard-coded constants
- **validate_proof.py result:** PASS (14/14 checks passed, 0 issues, 0 warnings)

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
