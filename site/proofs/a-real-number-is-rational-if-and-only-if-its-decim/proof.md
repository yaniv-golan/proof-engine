# Proof: A real number is rational if and only if its decimal expansion is eventually periodic

- **Generated:** 2026-03-28
- **Verdict:** PROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Key Findings

- **Direction 1 (Rational => Periodic):** Long division of p/q tracks at most q distinct remainders; by the pigeonhole principle, a remainder must repeat within q steps, forcing the decimal digits to cycle. Verified on 35 hand-picked rationals covering terminating, purely repeating, and mixed cases.
- **Direction 2 (Periodic => Rational):** Any eventually periodic decimal 0.d_1...d_k(r_1...r_p) can be converted to a fraction by multiplying by 10^(k+p) and 10^k and subtracting, yielding a ratio of integers. Verified on 14 periodic decimals including the edge case 0.(9) = 1.
- **Exhaustive cross-check:** All 20,100 rationals p/q with 1 <= q <= 200 and 0 <= p < q were round-tripped (rational -> periodic expansion -> rational) with zero failures, using Python's `Fraction` for exact arithmetic.
- **No adversarial counter-evidence found:** Edge cases (0, negatives, integers, 0.999...) all handled correctly; the pigeonhole argument is watertight for all positive denominators.

## Claim Interpretation

**Natural language:** "A real number is rational if and only if its decimal expansion is eventually periodic."

**Formal interpretation:** This is a biconditional claim requiring two directions:
1. Every rational number p/q (q != 0) has a decimal expansion that is eventually periodic.
2. Every real number with an eventually periodic decimal expansion is rational.

"Eventually periodic" means there exist non-negative integers k (pre-period length) and p >= 1 (period length) such that for all n >= k, digit d(n) = d(n+p). Terminating decimals are eventually periodic with repeating 0s. The operator is equality (both directions must hold).

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| A1 | Long division of p/q produces eventually periodic digits (pigeonhole on remainders) | Computed: All 35 test cases passed -- expansion is eventually periodic and round-trips to original fraction |
| A2 | Every eventually periodic decimal converts to a fraction p/q | Computed: All 14 test cases converted to correct fractions and round-tripped |
| A3 | Exhaustive cross-check via Python Fraction for all q <= 200 | Computed: 20,100 rationals tested, 0 failures |

## Proof Logic

### Direction 1: Rational => Eventually Periodic

Given a rational number p/q with q > 0, perform long division of p by q. At each step, the remainder r satisfies 0 <= r < q, giving exactly q possible remainder values. By the **pigeonhole principle**, within at most q steps, some remainder must recur. Once a remainder repeats, the subsequent digits repeat identically, producing a periodic cycle (A1).

For example, 1/7 produces remainders [1, 3, 2, 6, 4, 5, 1, ...] -- remainder 1 recurs at position 6, giving period (142857) of length 6, which satisfies the pigeonhole bound 6 <= 7 (A1).

Terminating decimals (e.g., 1/4 = 0.25) reach remainder 0, after which all subsequent digits are 0 -- this is eventually periodic with period (0).

### Direction 2: Eventually Periodic => Rational

Given a decimal 0.d_1...d_k(r_1...r_p) with pre-period of length k and period of length p, let x be its value. Then:

- 10^(k+p) * x has the repeating block aligned one full cycle later
- 10^k * x has the repeating block starting immediately

Subtracting: (10^(k+p) - 10^k) * x = (integer formed by all k+p digits) - (integer formed by k pre-period digits)

This gives x = (integer difference) / (10^(k+p) - 10^k), a ratio of integers, hence rational (A2).

For example, 0.(142857): here k=0, p=6, so x = 142857 / (10^6 - 1) = 142857/999999 = 1/7.

### Exhaustive Verification

Both directions were verified exhaustively for all 20,100 rationals p/q with 1 <= q <= 200 and 0 <= p < q. Each rational was converted to its periodic expansion via long division, then converted back to a fraction, confirming exact equality with the original. Zero failures (A3).

## Counter-Evidence Search

- **0.(9) = 1 edge case:** The identity 0.999... = 1 is correctly handled. Non-uniqueness of decimal representations does not affect the theorem -- both 1.0(0) and 0.(9) are eventually periodic.
- **Almost-periodic irrationals:** Numbers like sqrt(2) or the Champernowne constant have non-repeating digits. The proof does not rely on digit-pattern detection -- it relies on the algebraic structure of long division (pigeonhole) and fraction reconstruction.
- **Edge cases (0, negatives, integers):** All handled correctly. Sign is factored out; integers have trivially periodic expansions.
- **Large denominators:** The pigeonhole argument holds for all q. Tested up to q=239 in hand-picked cases and exhaustively up to q=200.

## Conclusion

**PROVED.** A real number is rational if and only if its decimal expansion is eventually periodic. Both directions of the biconditional were verified:

1. **Rational => periodic** follows from the pigeonhole principle applied to long division remainders (at most q possible values force a cycle within q steps).
2. **Periodic => rational** follows from algebraic manipulation: multiplying and subtracting eliminates the repeating part, expressing the number as a ratio of integers.

The exhaustive cross-check over 20,100 rationals with zero failures provides strong computational confirmation. All edge cases (terminating decimals, 0.999... = 1, negatives, zero, integers) are handled correctly.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
