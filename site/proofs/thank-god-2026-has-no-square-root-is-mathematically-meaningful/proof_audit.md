# Audit: "Thank God 2026 has no square root" is mathematically meaningful

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | 2026 |
| Property | Count of positive integers n such that n² = 2026 (equivalently: is 2026 a perfect square?) |
| Operator | == |
| Threshold | 0 |
| Operator note | The phrase "has no square root" is interpreted as "is not a perfect square" — no positive integer n satisfies n² = 2026. "Mathematically meaningful" means the assertion is precise and true. The claim would be FALSE if any n ∈ ℤ⁺ existed with n²=2026. Context: 2025 = 45² is a perfect square, grounding the "relief". Real-valued √2026 ≈ 45.011 exists but that is not the meaningful assertion in this context. |

---

## Fact Registry

| ID | Label | Type |
|----|-------|------|
| A1 | isqrt(2026)² ≠ 2026 (primary: no integer square root) | Pure computation |
| A2 | Prime factorisation of 2026 has odd-exponent prime factors (cross-check) | Pure computation |
| A3 | 45² = 2025 (predecessor year is a perfect square — context) | Pure computation |
| A4 | √2026 is irrational (consequence of A1/A2) | Pure computation |

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | isqrt(2026)² ≠ 2026 (primary: no integer square root) | math.isqrt(2026) = 45; verified 45² = 2025 ≠ 2026 and 46² = 2116 ≠ 2026 | True |
| A2 | Prime factorisation of 2026 has odd-exponent prime factors (cross-check) | Prime factorisation: 2026 = 2¹ × 1013¹; both exponents are odd → not a perfect square | True |
| A3 | 45² = 2025 (predecessor year is a perfect square — context) | math.isqrt(2025) = 45; verified 45² = 2025 | True |
| A4 | √2026 is irrational | Valuation argument: v₂(2026) = 1 (odd); if √2026 = p/q then 2·v₂(p) = 1 + 2·v₂(q) — even = odd, contradiction | True |

*(No Type B or Type S facts — this is a pure-math proof.)*

---

## Computation Traces

Verbatim output from `python proof.py`:

```
=== PRIMARY: integer square root check ===
math.isqrt(2026) = 45
  floor_sq = isqrt(2026)²: isqrt_n * isqrt_n = 45 * 45 = 2025
  ceil_sq  = (isqrt(2026)+1)²: (isqrt_n + 1) * (isqrt_n + 1) = (45 + 1) * (45 + 1) = 2116
  A1a: 45² ≠ 2026: 2025 != 2026 = True
  A1b: 46² ≠ 2026: 2116 != 2026 = True
  A1: both 45² ≠ 2026 AND 46² ≠ 2026 → no integer square root: 1 == 1 = True

=== CROSS-CHECK: prime factorisation ===
Prime factorisation of 2026: 2^1 × 1013^1
Factorisation product verified: 2026 = 2026 ✓
Primes with odd exponents: [(2, 1), (1013, 1)]
  A2: at least one prime with odd exponent → not a perfect square: 2 >= 1 = True
Cross-check A1 vs A2: AGREE ✓

=== CONTEXT: 2025 is a perfect square ===
  A3: isqrt(2025)²: isqrt_2025 * isqrt_2025 = 45 * 45 = 2025
  A3: 2025 is a perfect square: 2025 == 2025 = True
isqrt(2025) = 45, so 2025 = 45²  → perfect square: True

=== IRRATIONALITY of √2026 ===
v₂(2026) = 1  (exponent of 2 in prime factorisation of 2026)
  A4: v₂(2026) is odd → √2026 irrational: 1 == 1 = True
A4 (√2026 irrational): True  [if √2026 = p/q then 2·v₂(p) = 1 + 2·v₂(q), but LHS is even and RHS is odd — contradiction]

=== ADVERSARIAL: exhaustive n² = 2026 search ===
  Exhaustive search: no n with n²=2026: 0 == 0 = True

=== ADVERSARIAL: primality of 1013 ===
  1013 has no divisors in [2, floor(√1013)]: 0 == 0 = True
1013 is prime: True
  Primary claim: 2026 is not a perfect square: 0 == 0 = True
```

---

## Cross-Check: Independent Method Agreement (Rule 6)

| Description | Method A | Method B | Agreement |
|-------------|----------|----------|-----------|
| 2026 is not a perfect square | A1: isqrt floor/ceil check (45²=2025 ≠ 2026, 46²=2116 ≠ 2026) | A2: prime factorisation parity (2026=2¹×1013¹, odd exponents) | ✓ Both: True |

The two methods are mathematically independent: A1 uses integer square root arithmetic; A2 uses the Fundamental Theorem of Arithmetic and exponent parity. Neither shares intermediate computations with the other. A bug in either method would produce a visible disagreement.

---

## Adversarial Checks (Rule 5)

| # | Question | Verification Performed | Finding | Breaks Proof? |
|---|----------|----------------------|---------|---------------|
| 1 | Does 2026 have an integer square root that was overlooked? | Computed math.isqrt(2026) = 45; verified 45² = 2025 and 46² = 2116. Exhaustive search over all n ∈ [1, 2026] — zero counterexamples. | No integer n satisfies n² = 2026. Nearest perfect squares: 45² = 2025 and 46² = 2116. | No |
| 2 | Could 'no square root' mean something other than 'not a perfect square'? | Three interpretations evaluated: (1) no real root — FALSE; (2) no rational root — TRUE; (3) no integer root — TRUE. The "year context" framing aligns with interpretation (3). | Claim is true under both meaningful interpretations (2) and (3). Only interpretation (1) fails, but is linguistically inconsistent with the "Thank God" framing. | No |
| 3 | Is 2026 a perfect power of some other kind? | 2026 = 2 × 1013 (semiprimes, all exponents = 1). A perfect k-th power requires all exponents divisible by k. For k ≥ 2, no exponent of 1 is divisible by k. | Not a perfect square, cube, or any higher power. The claim is not undermined by other power relationships. | No |
| 4 | Is 1013 actually prime? | Trial division by all integers from 2 to ⌊√1013⌋ = 31. Zero divisors found. | 1013 is prime. Factorisation 2026 = 2 × 1013 is correct. | No |

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
