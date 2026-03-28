# Audit: 2026 being divisible by 2, 3, 7, 11, 13, 17 proves it has "hidden perfect number properties."

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | 2026 |
| Property | SC1: number of claimed divisors {2,3,7,11,13,17} that actually divide 2026 == 6; SC2: 2026 has "hidden perfect number properties" (sum of proper divisors equals 2026) |
| Operator | == |
| Threshold | 6 (SC1: all 6 claimed divisors must hold) |
| Operator Note | Compound claim requires both SC1 and SC2. SC1 is checked via modular arithmetic (n % d == 0) and GCD characterization (gcd(n,d) == d). "Hidden perfect number properties" is not a standard term — interpreted as: 2026 is a perfect number (σ_proper(n) == n). If SC1 is false, the compound claim is disproved regardless of SC2. |

---

## Fact Registry

| ID | Label | Type |
|----|-------|------|
| A1 | 2026 divisible by 2: 2026 % 2 == 0 | Type A (computed) |
| A2 | 2026 divisible by 3: 2026 % 3 == 0 | Type A (computed) |
| A3 | 2026 divisible by 7: 2026 % 7 == 0 | Type A (computed) |
| A4 | 2026 divisible by 11: 2026 % 11 == 0 | Type A (computed) |
| A5 | 2026 divisible by 13: 2026 % 13 == 0 | Type A (computed) |
| A6 | 2026 divisible by 17: 2026 % 17 == 0 | Type A (computed) |
| A7 | Prime factorization of 2026 (trial division) | Type A (computed) |
| A8 | SC2 check: sum of proper divisors of 2026 vs 2026 (perfect number test) | Type A (computed) |
| A9 | Cross-check: divisibility via gcd(2026, d) == d for each claimed d | Type A (computed) |

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | 2026 divisible by 2 | 2026 % 2 | remainder=0, divisible=True |
| A2 | 2026 divisible by 3 | 2026 % 3 | remainder=1, divisible=False |
| A3 | 2026 divisible by 7 | 2026 % 7 | remainder=3, divisible=False |
| A4 | 2026 divisible by 11 | 2026 % 11 | remainder=2, divisible=False |
| A5 | 2026 divisible by 13 | 2026 % 13 | remainder=11, divisible=False |
| A6 | 2026 divisible by 17 | 2026 % 17 | remainder=3, divisible=False |
| A7 | Prime factorization of 2026 | Trial division prime factorization | 2 × 1013 |
| A8 | SC2: perfect number test | Sum of proper divisors via trial division | sigma_proper(2026)=1016, required=2026, difference=−1010, classification=deficient |
| A9 | Cross-check: GCD method | gcd(2026, d) == d for each d in {2,3,7,11,13,17} | GCD method: 1/6 divisibilities hold, agrees with modulo method (1/6) |

*(No Type B empirical facts — pure-math proof.)*

---

## Computation Traces

```
=== SC1: Divisibility of 2026 by claimed divisors [2, 3, 7, 11, 13, 17] ===
  2026 % 2 = 0  →  divisible
  2026 % 3 = 1  →  NOT divisible (remainder=1)
  2026 % 7 = 3  →  NOT divisible (remainder=3)
  2026 % 11 = 2  →  NOT divisible (remainder=2)
  2026 % 13 = 11  →  NOT divisible (remainder=11)
  2026 % 17 = 3  →  NOT divisible (remainder=3)

  Divisors that hold: [2]
  Divisors that FAIL: [3, 7, 11, 13, 17]
  Count of divisibilities holding: 1 / 6

=== Cross-Check: GCD method — gcd(2026, d) == d iff d | 2026 ===
  gcd(2026, 2) = 2  →  divisible
  gcd(2026, 3) = 1  →  NOT divisible (gcd=1≠3)
  gcd(2026, 7) = 1  →  NOT divisible (gcd=1≠7)
  gcd(2026, 11) = 1  →  NOT divisible (gcd=1≠11)
  gcd(2026, 13) = 1  →  NOT divisible (gcd=1≠13)
  gcd(2026, 17) = 1  →  NOT divisible (gcd=1≠17)

  GCD method count of divisibilities holding: 1 / 6
  Cross-check: modulo method and GCD method agree (1 == 1) ✓

=== Prime Factorization of 2026 ===
  2026 = 2 × 1013
  Verification: 2 × 1013 = 2026 ✓

  Prime factors of 2026: [2, 1013]
  3 in prime factors of 2026: False  →  2026 is NOT divisible by 3
  7 in prime factors of 2026: False  →  2026 is NOT divisible by 7
  11 in prime factors of 2026: False  →  2026 is NOT divisible by 11
  13 in prime factors of 2026: False  →  2026 is NOT divisible by 13
  17 in prime factors of 2026: False  →  2026 is NOT divisible by 17
  LCM of {2,3,7,11,13,17} = 2×3×7×11×13×17: a * b * c * d_val * e * f_val = 2 * 3 * 7 * 11 * 13 * 17 = 102102
  The smallest positive number divisible by all 6 primes is 102102
  2026 is 100076 less than 102102 — it is NOT a multiple of 102102

=== SC2: Perfect Number Test for 2026 ===
  Proper divisors of 2026: [1, 2, 1013]
  Sum of proper divisors (sigma(n) - n): 1016
  For a perfect number, sum must equal 2026
  1016 == 2026: False
  Difference: 1016 - 2026 = -1010
  Classification: deficient

  Euclid-Euler test: does 2026 = 2^(p-1) * (2^p - 1) for any prime p?
    No p in [2,19] satisfies 2^(p-1) × (2^p - 1) = 2026
    Euclid-Euler sequence (p=2,3,5,7): [6, 28, 496, 8128]
    2026 does not appear in this sequence

  sigma(2026) = 3042  (sum of ALL divisors including 2026)
  sigma(2026) / 2026 = 1.501481  (perfect numbers have ratio = 2.000000)
  SC1: count of divisibilities holding == 6 (all must hold): 1 == 6 = False
  SC2: sum of proper divisors == 2026 (perfect number test): 1016 == 2026 = False
```

---

## Independent Cross-Check (Rule 6)

| Description | Value A (Modulo) | Value B (GCD) | Agreement |
|-------------|-----------------|---------------|-----------|
| Count of divisibilities holding | 1 | 1 | True |

**Method independence:** The modulo method tests `n % d == 0` directly. The GCD method uses the algebraic identity `d | n ⟺ gcd(n, d) = d`, which is a structurally different characterization (Euclidean algorithm vs. remainder computation). Both methods yield the same count (1/6), confirming the result is not an artifact of any single method.

---

## Adversarial Checks (Rule 5)

**Check 1: Could '2026' refer to a transformed value?**
- Question: Could '2026' in the claim refer to a transformed or encoded value that IS divisible by all six primes?
- Verification performed: Computed LCM(2,3,7,11,13,17) = 102102. Checked all multiples of 102102 near 2026: the nearest multiples are 0 and 102102. 2026 is not a multiple of 102102. No standard calendar year encoding (e.g., 2026 mod k, 2026 in a different base) produces 102102 or any multiple thereof. Checked 2026 in bases 2–16: none yield 102102.
- Finding: 2026 in any standard encoding is not divisible by all six claimed primes. The premise is straightforwardly false for the integer 2026.
- Breaks proof: No

**Check 2: Is "hidden perfect number properties" a recognized term?**
- Question: Is 'hidden perfect number properties' a recognized mathematical term that 2026 could satisfy?
- Verification performed: Surveyed standard number theory classifications: perfect numbers (sigma(n)=2n), quasi-perfect (sigma(n)=2n+1, none known), almost perfect (sigma(n)=2n−1, only powers of 2), multiply perfect/k-perfect (sigma(n)=kn), semiperfect/pseudoperfect (n equals some subset-sum of proper divisors), weird numbers (abundant but not semiperfect). "Hidden perfect number properties" appears in none of these standard classifications. Searched for the phrase in number theory literature — no results found.
- Finding: 'Hidden perfect number properties' has no standard mathematical definition. Under the most charitable interpretation (2026 is a perfect number): sum of proper divisors of 2026 = 1016 ≠ 2026. 2026 is a deficient number. sigma(2026)/2026 ≈ 1.501, far from the ratio of 2 required for a perfect number.
- Breaks proof: No

**Check 3: Does divisibility by {2,3,7,11,13,17} imply perfect-number-adjacent properties?**
- Question: Does divisibility by 2, 3, 7, 11, 13, 17 imply any known perfect-number-adjacent property for numbers that ARE divisible by all six?
- Verification performed: The smallest number divisible by 2,3,7,11,13,17 is their LCM = 102102. For squarefree n = p₁×…×p_k, sigma(n) = (1+p₁)(1+p₂)…(1+p_k). sigma(102102) = 3×4×8×12×14×18 = 290304. sigma(102102)/102102 ≈ 2.843 ≠ 2. So 102102 is abundant, not perfect.
- Finding: Even the smallest number genuinely divisible by all six claimed primes (102102) is NOT a perfect number. Divisibility by {2,3,7,11,13,17} does not imply perfect number properties for any number, let alone for 2026 which fails the divisibility premise.
- Breaks proof: No

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
