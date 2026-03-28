# Audit: The 100000th prime number is exactly 1299709

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | the 100000th prime number |
| Property | value of the 100000th prime in the sequence of primes (2, 3, 5, 7, 11, ...) |
| Operator | == |
| Operator note | 'exactly' means strict equality. The 100000th prime must be precisely 1299709. Primes are indexed starting at p(1)=2, p(2)=3, etc. -- the standard convention. |
| Threshold | 1299709 |

*Source: proof.py JSON summary*

## Fact Registry

| Report ID | Proof-script key | Label |
|-----------|-----------------|-------|
| A1 | A1 | 100000th prime via Sieve of Eratosthenes |
| A2 | A2 | Prime-counting function pi(1299709) equals 100000 |
| A3 | A3 | 1299709 is prime (trial division) |
| A4 | A4 | pi(1299708) equals 99999 (confirms no prime between) |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | 100000th prime via Sieve of Eratosthenes | Sieve of Eratosthenes up to upper bound, extract 100000th prime | 1299709 |
| A2 | Prime-counting function pi(1299709) equals 100000 | Independent sieve counting all primes <= 1299709 | 100000 |
| A3 | 1299709 is prime (trial division) | Trial division testing all factors up to sqrt(1299709) | True |
| A4 | pi(1299708) equals 99999 (confirms no prime between) | Independent sieve counting all primes <= 1299708 | 99999 |

*Source: proof.py JSON summary*

## Computation Traces

```
============================================================
PRIMARY METHOD: Sieve of Eratosthenes
============================================================
The 100000th prime (via sieve) = 1299709

============================================================
CROSS-CHECK 1: Prime-counting function π(1299709)
============================================================
π(1299709) = 100000

============================================================
CROSS-CHECK 2: Primality of 1299709 via trial division
============================================================
is_prime(1299709) = True

============================================================
CROSS-CHECK 3: π(1299708) — confirming boundary
============================================================
π(1299708) = 99999

============================================================
CROSS-CHECK ASSERTIONS
============================================================
Sieve result matches claim: 1299709 == 1299709 → True
π(1299709) == 100000: 100000 == 100000 → True
1299709 is prime: True
π(1299708) == 99999: 99999 == 99999 → True

============================================================
ADVERSARIAL: Small-case verification
============================================================
  p(1) = 2 (expected 2) ✓
  p(10) = 29 (expected 29) ✓
  p(100) = 541 (expected 541) ✓
  p(1000) = 7919 (expected 7919) ✓
  100000th prime check: 1299709 == 1299709 = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

| # | Question | Verification Performed | Finding | Breaks Proof? |
|---|----------|----------------------|---------|---------------|
| 1 | Could the indexing convention differ (0-based vs 1-based)? | Checked standard mathematical convention: p(1)=2, p(2)=3, p(3)=5, ... The claim uses 'the 100000th prime' which in standard notation is p(100000). Verified sieve starts counting at p(1)=2. | Sieve uses 1-based indexing (first prime counted is 2). Matches claim convention. | No |
| 2 | Is 1 sometimes counted as a prime, shifting the index? | Historically, 1 was sometimes considered prime, but modern convention (post-1800s) excludes 1. The sieve starts from 2. If 1 were included, p(100000) would be p(99999) in modern convention. Verified that the claim uses modern convention. | Modern convention excludes 1 as prime. Both sieve and claim use this convention. | No |
| 3 | Could there be an off-by-one error in the sieve or counting? | Verified sieve against known small primes: p(1)=2, p(10)=29, p(100)=541, p(1000)=7919. Additionally, the independent pi(x) counting function provides a structural cross-check: pi(1299709)=100000 and pi(1299708)=99999 together confirm 1299709 is the exact 100000th prime. | Small-case verification and pi(x) boundary check rule out off-by-one errors. | No |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A -- pure computation, no empirical facts
- **Rule 2:** N/A -- pure computation, no empirical facts
- **Rule 3:** `date.today()` used in generator block for proof generation date
- **Rule 4:** `CLAIM_FORMAL` with `operator_note` explicitly documents "exactly" as `==` and explains 1-based prime indexing convention
- **Rule 5:** Three adversarial checks performed: indexing convention, historical treatment of 1, off-by-one errors. Small-case verification executed in code.
- **Rule 6:** N/A -- pure computation, no empirical facts. Cross-checks use mathematically independent methods: (1) sieve extraction vs. prime counting function, (2) trial division as independent primality test, (3) boundary verification via pi(n-1).
- **Rule 7:** `compare()` imported from `scripts/computations.py` for verdict evaluation. No hard-coded constants or formulas needed for this proof.
- **validate_proof.py result:** PASS (14/14 checks passed, 0 issues, 0 warnings)

*Source: author analysis*

## Generator

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
