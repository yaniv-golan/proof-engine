# Audit: An object moving at exactly 0.95c experiences a Lorentz factor greater than 3.2

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Lorentz factor γ for an object at v = 0.95c |
| Property | γ = 1 / sqrt(1 - β²) where β = v/c = 0.95 |
| Operator | > |
| Threshold | 3.2 |
| Operator note | "greater than 3.2" interpreted as strict inequality (>). If γ were exactly 3.2, the claim would be FALSE. The Lorentz factor is a standard definition from special relativity with no empirical ambiguity. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| A1 | — | Primary computation of γ via direct formula |
| A2 | — | Cross-check via high-precision decimal arithmetic |
| A3 | — | Cross-check via algebraic simplification γ² = 1/(1-β²) |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Primary computation of γ via direct formula | Direct float computation: γ = 1/√(1 - 0.95²) | 3.2025630761 |
| A2 | Cross-check via high-precision decimal arithmetic | 50-digit Decimal arithmetic | 3.2025630761 |
| A3 | Cross-check via algebraic simplification γ² = 1/(1-β²) | Exact rational: γ² = 400/39, verify γ² > (3.2)² = 256/25 | γ² = 400/39 ≈ 10.2564102564, γ ≈ 3.2025630761 |

*Source: proof.py JSON summary*

## Computation Traces

```
  β²: beta ** 2 = 0.95 ** 2 = 0.9025
  1 - β²: 1 - beta_squared = 1 - 0.9025 = 0.0975
  γ (primary, float): 1 / sqrt(one_minus_beta_sq) = 1 / sqrt(0.09750000000000003) = 3.2026

Cross-check 1 (Decimal, 50-digit precision): γ = 3.2025630761017426696650733953537407492681846040983
  Primary (float) vs Decimal arithmetic: 3.202563076101742 vs 3.2025630761017427, diff=8.881784197001252e-16, tolerance=1e-10 -> AGREE

Cross-check 2 (exact rational): γ² = 400/39 = 10.2564102564
  threshold² = 256/25 = 10.2400000000
  γ² > threshold²: True
  Primary (float) vs Rational arithmetic: 3.202563076101742 vs 3.2025630761017427, diff=8.881784197001252e-16, tolerance=1e-10 -> AGREE

  γ > 3.2: 3.202563076101742 > 3.2 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

This is a pure-math proof with no empirical sources. Independence is achieved through **mathematically distinct computation methods**:

| Cross-check | Values Compared | Agreement |
|-------------|----------------|-----------|
| Float vs 50-digit Decimal arithmetic | 3.2025630761 vs 3.2025630761 | Yes |
| Float vs exact rational (Fraction) arithmetic | 3.2025630761 vs 3.2025630761 | Yes |
| Exact rational squared comparison: γ² = 400/39 > 256/25 = (3.2)² | 400/39 vs 256/25 | Yes (400/39 > 256/25) |

The three methods are structurally independent:
- **A1 (float):** Uses IEEE 754 double-precision `math.sqrt()`.
- **A2 (Decimal):** Uses Python's `decimal` module with 50-digit precision and its own `sqrt()` implementation.
- **A3 (rational):** Uses Python's `fractions.Fraction` for exact rational arithmetic — no square root, no floating-point. The comparison γ > 3.2 is reduced to γ² > 3.2² using exact fractions, bypassing sqrt entirely.

A bug in any one method (e.g., incorrect sqrt implementation, floating-point edge case) would not propagate to the others.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

| # | Question | Verification Performed | Finding | Breaks Proof? |
|---|----------|----------------------|---------|---------------|
| 1 | Is there any alternative definition of the Lorentz factor that would yield a different value? | Reviewed standard physics references. The Lorentz factor γ = 1/√(1-v²/c²) is the universal definition in special relativity. There is no competing definition. The reciprocal 1/γ is sometimes used but is clearly distinct. | No alternative definition exists that would change the computed value. | No |
| 2 | Could floating-point representation of 0.95 introduce enough error to change the comparison? | Computed γ via three independent methods: IEEE 754 float, 50-digit Decimal, and exact rational (Fraction) arithmetic. All agree to >10 decimal places. The exact rational computation confirms γ² = 400/39 > 256/25 = 3.2² with no floating-point involved. | Floating-point representation cannot affect the verdict; exact rational arithmetic confirms γ > 3.2. | No |
| 3 | Is the margin above 3.2 so small that rounding could flip the result? | γ ≈ 3.2026 and threshold is 3.2. The margin is ~0.0026, well above any floating-point uncertainty. Exact rational proof shows γ² = 400/39 ≈ 10.2564 vs 3.2² = 10.24, margin ~0.0164 in squared domain. | The margin is small but unambiguous — confirmed by exact arithmetic. | No |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A — pure computation, no empirical facts.
- **Rule 2:** N/A — pure computation, no empirical facts.
- **Rule 3:** `date.today()` used in generator block for output dating.
- **Rule 4:** `CLAIM_FORMAL` with `operator_note` explicitly documents strict inequality interpretation and notes the consequence if γ were exactly 3.2.
- **Rule 5:** Three adversarial checks: alternative definitions, floating-point error risk, margin analysis. None break the proof.
- **Rule 6:** N/A — pure computation, no empirical facts. Three mathematically independent methods used as cross-checks (float, Decimal, exact rational).
- **Rule 7:** `compare()` and `explain_calc()` imported from `scripts/computations.py`. `cross_check()` used for method agreement. No hard-coded constants or inline formulas.
- **validate_proof.py result:** PASS (14/14 checks passed, 0 issues, 0 warnings)

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
