# Audit: 641 divides 2^{32} + 1 exactly

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | 2^32 + 1 (the fifth Fermat number, F_5) |
| Property | (2^32 + 1) mod 641 |
| Operator | == |
| Threshold | 0 |
| Operator note | 'Divides exactly' means 641 is a factor of 2^32 + 1, i.e., (2^32 + 1) mod 641 == 0. This is equivalent to showing 2^32 + 1 = 641 * k for some positive integer k. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| A1 | — | Direct modular arithmetic: (2^32 + 1) mod 641 |
| A2 | — | Integer division cross-check: 2^32 + 1 == 641 * quotient |
| A3 | — | Algebraic decomposition via Euler's method |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Direct modular arithmetic: (2^32 + 1) mod 641 | Python exact integer arithmetic: (2**32 + 1) % 641 | 0 |
| A2 | Integer division cross-check: 2^32 + 1 == 641 * quotient | Integer division: divmod(2^32 + 1, 641) then verify 641 * quotient == 2^32 + 1 | quotient=6700417, remainder=0, 641*6700417=4294967297 |
| A3 | Algebraic decomposition via Euler's method | Euler's algebraic decomposition: 641 = 5^4 + 2^4 = 5*2^7 + 1, therefore 5^4 ≡ -2^4 and 5*2^7 ≡ -1 (mod 641), combining gives 2^32 ≡ -1 (mod 641) | 2^32 mod 641 = 640, so (2^32 + 1) mod 641 = 0 |

*Source: proof.py JSON summary*

## Computation Traces

```
2^32 + 1 = 4294967297
  A1: (2^32 + 1) mod 641: fermat_5 % 641 = 4294967297 % 641 = 0

Cross-check 1 (integer division):
  divmod(2^32 + 1, 641) = quotient=6700417, remainder=0
  A2: 641 * quotient: 641 * quotient = 641 * 6700417 = 4294967297
  A2: 641 * quotient == 2^32 + 1: 4294967297 == 4294967297 = True

Cross-check 2 (Euler's algebraic decomposition):
  A3a: 5^4 + 2^4: 5**4 + 2**4 = 5 ** 4 + 2 ** 4 = 641
  A3a: 5^4 + 2^4 == 641: 641 == 641 = True
  A3b: 5 * 2^7 + 1: 5 * 2**7 + 1 = 5 * 2 ** 7 + 1 = 641
  A3b: 5 * 2^7 + 1 == 641: 641 == 641 = True
  A3c: (5 * 2^7)^4 mod 641: pow(5 * 128, 4, 641) = 1
  A3d: 5^4 mod 641: pow(5, 4, 641) = 625
  A3e: -2^4 mod 641: (-pow(2, 4, 641)) % 641 = -pow(2, 4, 641) % 641 = 625
  A3: 5^4 ≡ -2^4 (mod 641): 625 == 625 = True
  A3f: 2^32 mod 641: pow(2, 32, 641) = 640
  A3: (2^32 + 1) mod 641 == 0 via Euler: 0 == 0 = True

Adversarial: trial division to verify 641 is smallest prime factor
  Smallest factor of 4294967297 found by trial division: 641
  Cofactor: 4294967297 / 641 = 6700417
  Cofactor 6700417 is prime: True
  Complete factorization: 4294967297 = 641 × 6700417
  VERDICT: (2^32 + 1) mod 641 == 0: 0 == 0 = True
```

*Source: proof.py inline output (execution trace)*

## Cross-Checks

| # | Description | Values Compared | Agreement |
|---|-------------|-----------------|-----------|
| 1 | Integer division: 641 * quotient reconstructs 2^32 + 1 | 4294967297 vs 4294967297 | Yes |
| 2 | Euler's algebraic decomposition confirms 2^32 ≡ -1 (mod 641) | 640 vs 640 | Yes |

All cross-checks use mathematically independent methods: (1) direct modular arithmetic, (2) integer division with reconstruction, and (3) Euler's algebraic identities. No shared intermediate computation.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

| # | Question | Verification Performed | Finding | Breaks Proof? |
|---|----------|----------------------|---------|---------------|
| 1 | Could the computation overflow or lose precision? | Python integers have arbitrary precision — no overflow is possible. 2^32 + 1 = 4294967297, well within exact integer range. The modular arithmetic uses Python's built-in integer mod, which is exact. | No precision issue. Python integers are arbitrary-precision. | No |
| 2 | Is 641 the smallest prime factor of 2^32 + 1? | Checked by trial division: no prime less than 641 divides 4294967297. The cofactor 4294967297 / 641 = 6700417, which is itself prime. Thus 4294967297 = 641 × 6700417 is the complete factorization. | 641 is indeed the smallest prime factor. Confirmed by trial division. | No |
| 3 | Does 'divides exactly' require that 641 is a prime factor, or just a factor? | The claim says '641 divides 2^{32} + 1 exactly', which in standard number theory means 641 \| (2^32 + 1), i.e., the remainder is zero. The claim does not require 641 to be prime (though it is). Our proof shows the remainder is 0, which is sufficient for the claim as stated. | The interpretation is correct. 'Divides exactly' means zero remainder. | No |

*Source: proof.py JSON summary*

## Hardening Checklist

| Rule | Status |
|------|--------|
| Rule 1: Every empirical value parsed from quote text | N/A — pure computation, no empirical facts |
| Rule 2: Every citation URL fetched and quote checked | N/A — pure computation, no empirical facts |
| Rule 3: System time used for date-dependent logic | Pass — `date.today()` used for generated_at |
| Rule 4: Claim interpretation explicit with operator rationale | Pass — CLAIM_FORMAL with operator_note present |
| Rule 5: Adversarial checks searched for counter-evidence | Pass — 3 adversarial checks documented |
| Rule 6: Cross-checks used independently sourced inputs | N/A — pure computation, no empirical facts. Three independent mathematical methods used. |
| Rule 7: Constants/formulas imported from computations.py | Pass — `compare()` and `explain_calc()` used; no hard-coded constants |
| validate_proof.py result | PASS — 14/14 checks passed, 0 issues, 0 warnings |

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
