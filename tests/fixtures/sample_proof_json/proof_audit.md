# Audit: A venture capital fund investing $50 million in 25 startups at equal sizes requires at least one 50x return and two 10x returns to achieve a 3x gross multiple.

- Generated: 2026-04-08
- Reader summary: [proof.md](proof.md)
- Proof script: [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | A VC fund with $50M invested equally across 25 startups |
| Property | whether 1×50x + 2×10x returns (others=0) achieves a 3x gross multiple |
| Operator | `==` |
| Threshold | 3.0 |
| Proof direction | disprove |
| Operator note | Interpreted as a sufficiency claim: the stated returns (1 company at 50x, 2 at 10x, 22 at 0x) are sufficient to achieve a 3x gross multiple. Per-company investment: $50M/25 = $2M. Required return for 3x gross: $50M × 3 = $150M. Actual return under claimed scenario: (1×50 + 2×10)×$2M = $140M. $140M < $150M, so the claim is false. The claim also fails as a necessity claim: 3x is reachable without any 50x return. |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Label |
|----|-------|
| A1 | Per-company investment: $50M / 25 companies = $2M each |
| A2 | Total return under claimed scenario: (1×50 + 2×10) × $2M = $140M |
| A3 | Gross multiple achieved: $140M / $50M = 2.8x |
| A4 | Cross-check via direct portfolio sum: 1×$100M + 2×$20M + 22×$0M = $140M |
| A5 | Claim evaluation: gross_multiple == 3.0 |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Per-company investment: $50M / 25 companies = $2M each | fund_size_m / n_companies | $2.0M |
| A2 | Total return under claimed scenario: (1×50 + 2×10) × $2M = $140M | (n_50x × multiple_50x + n_10x × multiple_10x) × per_company_m | $140.0M |
| A3 | Gross multiple achieved: $140M / $50M = 2.8x | total_return_m / fund_size_m | 2.8000x |
| A4 | Cross-check via direct portfolio sum: 1×$100M + 2×$20M + 22×$0M = $140M | sum([50x×$2M, 10x×$2M, 10x×$2M, 0x×$2M × 22]) | $140.0M → 2.8000x |
| A5 | Claim evaluation: gross_multiple == 3.0 | compare(2.8000, '==', 3.0) | False |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

N/A — pure-math proof, no empirical citations.

### Type S (Search) Facts

N/A — pure-math proof, no search registry entries.

---

## Computation Traces

```
============================================================
COMPUTATION
============================================================
  A1: per-company investment ($M): fund_size_m / n_companies = 50.0 / 25 = 2.0000
  -> $2.0M per company
  Required total return for 3x gross ($M): fund_size_m * required_multiple = 50.0 * 3.0 = 150.0000
  -> $150M needed
  Return from 50x winner ($M): n_50x * multiple_50x * per_company_m = 1 * 50.0 * 2.0 = 100.0000
  Return from 10x winners ($M): n_10x * multiple_10x * per_company_m = 2 * 10.0 * 2.0 = 40.0000
  A2: total return under claimed scenario ($M): winner_50x_return_m + winner_10x_return_m = 100.0 + 40.0 = 140.0000
  A3: gross multiple achieved: total_return_m / fund_size_m = 140.0 / 50.0 = 2.8000
  Shortfall from 3x target ($M): required_return_m - total_return_m = 150.0 - 140.0 = 10.0000
  -> The scenario falls $10M short of the $150M needed for 3x

============================================================
CROSS-CHECK
============================================================
  Portfolio breakdown: 25 companies
    Company 1 (50x): $100.0M
    Companies 2-3 (10x each): $20.0M, $20.0M
    Companies 4-25 (0x): $0.0M each
  A4: Sum of all company returns = $140.0M
  Cross-check gross multiple: $140.0M / $50M = 2.8000x
  Cross-check: 2.8000x == 2.8000x [AGREE]

============================================================
VERDICT DETERMINATION
============================================================
  A5: gross_multiple == 3.0: 2.8 == 3.0 = False

Verdict: DISPROVED
  Gross multiple achieved: 2.8000x
  Required (claimed): 3.0x
  Shortfall: $10.0M (0.2000x)
```

*Source: proof.py inline output (execution trace)*

---

## Adversarial Checks (Rule 5)

**Check 1 — Can a 3x gross multiple be achieved without any 50x return?**

- Question: Can a 3x gross multiple be achieved without any 50x return? If yes, the 'necessity' reading of the claim is also false.
- Verification performed: Computed two alternative portfolios: (a) 15 companies at 5x each: 15 × 5 × $2M = $150M → 3.0x gross. (b) 5 companies at 15x each: 5 × 15 × $2M = $150M → 3.0x gross. Both achieve exactly 3x without any 50x return.
- Finding: 3x gross is achievable without any 50x return. Example: 15 companies at 5.0x each yields 3.0x gross; 5 companies at 15.0x each yields 3.0x gross. The claim fails as a necessity condition as well as a sufficiency condition.
- Breaks proof: No

**Check 2 — What if the fund has fewer companies?**

- Question: What if the fund has fewer companies (e.g., 20 instead of 25), keeping the same 1×50x + 2×10x pattern? Does the gross multiple change?
- Verification performed: Computed: $50M / 20 companies = $2.5M each. Return: (1×50 + 2×10) × $2.5M = $175.0M. Gross multiple: $175.0M / $50M = 3.50x.
- Finding: With 20 equal-size investments, the same 1×50x + 2×10x pattern yields 3.50x gross — which exceeds 3x. This shows the number of companies matters critically: the minimum required per-company investment to reach 3x with 1×50x + 2×10x is $150M / 70 = $2.143M, which requires ≤23 companies in a $50M fund. The claim specifies 25 companies ($2M each), which is too many to hit 3x with this pattern.
- Breaks proof: No

**Check 3 — Does the definition of "gross multiple" matter?**

- Question: Does the claim hold if 'gross multiple' refers to a return ON INVESTED capital rather than total value returned (i.e., 2.8x TVPI vs. 3x MOIC interpretation)?
- Verification performed: Confirmed standard VC terminology: gross multiple = TVPI (total value to paid-in), which is total proceeds divided by total invested capital. MOIC (multiple on invested capital) is computed identically at the fund level. Both give 2.8x for this scenario.
- Finding: Both TVPI and MOIC yield 2.8x for this scenario. No alternative definition of 'gross multiple' changes the arithmetic. The claim is false under any standard VC accounting convention.
- Breaks proof: No

*Source: proof.py JSON summary*

---

## Hardening Checklist

| Rule | Status |
|------|--------|
| Rule 1: Every empirical value parsed from quote text, not hand-typed | N/A — pure computation, no empirical facts |
| Rule 2: Every citation URL fetched and quote checked | N/A — pure computation, no empirical facts |
| Rule 3: System time used for date-dependent logic | PASS — `date.today()` anchors `generated_at` |
| Rule 4: Claim interpretation explicit with operator rationale | PASS — `CLAIM_FORMAL` with `operator_note` states exact interpretation and arithmetic |
| Rule 5: Adversarial checks searched for independent counter-evidence | PASS — 3 adversarial checks; alternative portfolios computed; terminology verified |
| Rule 6: Cross-checks used independently sourced inputs | N/A — pure computation, no empirical facts; cross-check uses independent algebraic method |
| Rule 7: Constants and formulas imported from computations.py, not hand-coded | PASS — `compare()` and `explain_calc()` from `scripts.computations` |
| validate_proof.py result | PASS — 14/14 checks passed, 0 issues, 0 warnings |

*Source: author analysis*

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.10.0 on 2026-04-08.*
