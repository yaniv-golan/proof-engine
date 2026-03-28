# Audit: 0.999... (with 9s repeating forever) is strictly less than 1.

- **Generated**: 2026-03-28
- **Reader summary**: [proof.md](proof.md)
- **Proof script**: [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | 0.999... (the repeating decimal 0.9 recurring) |
| Property | value compared to 1 |
| Operator | < (strict less than) |
| Threshold | 1 |
| Operator note | The claim asserts strict inequality: 0.999... < 1. In standard real analysis, 0.999... denotes the limit of the sequence 0.9, 0.99, 0.999, ... which equals exactly 1. This proof will show 0.999... = 1, thereby disproving the strict inequality. We work in the standard real number system (not hyperreals or surreals). |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| A1 | -- | Algebraic proof: if x = 0.999... then x = 1 |
| A2 | -- | Geometric series proof: sum of 9/10^k for k=1..inf equals 1 |
| A3 | -- | Fraction proof: 1/3 = 0.333..., so 3 * (1/3) = 0.999... = 1 |
| A4 | -- | Numerical convergence: partial sums approach 1 with zero gap |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Algebraic proof: if x = 0.999... then x = 1 | Algebraic: x = 0.999..., 10x - x = 9, x = 1 (verified via Fraction(9,9)) | 1.0 |
| A2 | Geometric series proof: sum of 9/10^k for k=1..inf equals 1 | Geometric series: a/(1-r) = (9/10)/(9/10) = 1 (verified via Fraction arithmetic) | 1.0 |
| A3 | Fraction proof: 1/3 = 0.333..., so 3 * (1/3) = 0.999... = 1 | Fraction identity: 3 * (1/3) = 3/3 = 1 (verified via Fraction arithmetic) | 1.0 |
| A4 | Numerical convergence: partial sums approach 1 with zero gap | Numerical convergence: partial sums 1 - 10^(-n) -> 1 as n -> inf | True (converges to 1) |

*Source: proof.py JSON summary*

## Computation Traces

```
  A1: algebraic result equals 1: 1.0 == 1.0 = True
  A2: geometric series equals 1: 1.0 == 1.0 = True
  A3: 3 * (1/3) equals 1: 1.0 == 1.0 = True
  A4: limit of partial sums equals 1: 1 == 1 = True
  value of 0.999...: Fraction(9, 9) = 1
  claim: 0.999... < 1: 1.0 < 1 = False
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

### Check 1: Is there a number system where 0.999... != 1?

- **Verification performed**: Investigated alternative number systems: hyperreals, surreals, and p-adic numbers. In hyperreals, one can define a number 0.999...;...999 with a specific hypernatural number of 9s that differs from 1 by an infinitesimal. However, '0.999...' with genuinely infinitely many 9s (i.e., one 9 for every natural number) equals 1 even in the hyperreals. The standard notation '0.999...' always denotes the real number 1.
- **Finding**: In no standard or extended number system does the notation '0.999... (repeating forever)' denote a value less than 1. The claim specifically says 'with 9s repeating forever,' which maps to the standard real-number interpretation.
- **Breaks proof**: No

### Check 2: Could there be a flaw in the algebraic proof (multiplying infinite decimals)?

- **Verification performed**: Examined whether multiplying an infinite repeating decimal by 10 is rigorous. The operation is justified because 0.999... is defined as the limit of the sequence S_n = sum_{k=1}^{n} 9*10^{-k}. Multiplying by 10: 10*S_n = 9 + S_n - 9*10^{-n}. Taking limits: 10*L = 9 + L - 0, so 9L = 9, L = 1. The algebra is rigorous when interpreted as operations on limits.
- **Finding**: The algebraic manipulation is fully rigorous when grounded in the epsilon-delta definition of limits. No flaw found.
- **Breaks proof**: No

### Check 3: Does the geometric series formula apply here (is |r| < 1)?

- **Verification performed**: The geometric series sum a/(1-r) requires |r| < 1. Here r = 1/10, so |r| = 0.1 < 1. The formula applies unconditionally.
- **Finding**: The convergence condition is satisfied. Formula is valid.
- **Breaks proof**: No

### Check 4: Is there peer-reviewed mathematical literature disputing 0.999... = 1?

- **Verification performed**: Searched for mathematical papers disputing 0.999... = 1 in standard real analysis. Found extensive pedagogical literature discussing why students resist this equality (Tall & Schwarzenberger 1978, Dubinsky et al. 2005), but no peer-reviewed paper disputes the result within standard mathematics.
- **Finding**: No credible mathematical source disputes that 0.999... = 1 in the real numbers. The equality is a theorem, not a conjecture.
- **Breaks proof**: No

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1**: N/A -- pure computation, no empirical facts.
- **Rule 2**: N/A -- pure computation, no empirical facts.
- **Rule 3**: `date.today()` used for `generated_at` timestamp. No time-dependent computation.
- **Rule 4**: CLAIM_FORMAL includes operator_note explaining "<" interpretation and the choice of standard real number system.
- **Rule 5**: Four adversarial checks investigated alternative number systems, algebraic rigor, convergence conditions, and mathematical literature. None break the proof.
- **Rule 6**: N/A -- pure computation, no empirical facts. Four mathematically independent methods used as cross-checks (algebraic, geometric series, fraction identity, numerical convergence). These are genuinely independent: they rely on different mathematical identities and share no intermediate computations.
- **Rule 7**: All computations use Python's `Fraction` (exact rational arithmetic) and `Decimal` (arbitrary precision). Constants derived from `Fraction` constructors, not hard-coded. `compare()` and `explain_calc()` from `scripts/computations.py` used for claim evaluation.
- **validate_proof.py result**: PASS (14/14 checks passed, 0 issues, 0 warnings)

*Source: author analysis*

## Generator

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
