# Proof Audit: Series A IRR (No Dilution)

**Claim:** If a company raises $5 million in Series A at a $25 million post-money valuation and exits at $500 million seven years later, the annualized return to the Series A investor exceeds 40% before dilution.

**Verdict:** PROVED

**Generated:** 2026-04-08

---

## Verification Environment

- Python with sympy and scipy.optimize
- Proof engine scripts: `proof-engine/skills/proof-engine/scripts/`
- Validator: 13/13 checks passed

---

## Computation Trace (verbatim proof output)

```
  A1: Series A ownership stake: INVESTED / POST_MONEY = 5000000 / 25000000 = 0.2000
  A2: Exit proceeds (no dilution): ownership * EXIT_VALUE = 0.2 * 500000000 = 1.00e+08
  A3: MOIC (multiple on invested capital): exit_proceeds / INVESTED = 100000000.0 / 5000000 = 20.0000
A4: CAGR (sympy exact symbolic): 0.53412740 = 53.412740%
A4-xcheck: CAGR (scipy brentq NPV=0): 0.53412740 = 53.412740%
  A4 cross-check: sympy vs scipy CAGR agreement: 0.534127404634391 vs 0.5341274046342092, diff=1.8185453143360064e-13, tolerance=1e-08 -> AGREE
  CAGR > 40% threshold: 0.534127404634391 > 0.4 = True
```

---

## Rule Compliance

| Rule | Status | Notes |
|------|--------|-------|
| Rule 1: No hand-typed values | ✓ | All values defined as named constants |
| Rule 2: Citation verification | N/A | Pure math proof, no empirical sources |
| Rule 3: Time anchoring | N/A | Claim is time-independent |
| Rule 4: CLAIM_FORMAL | ✓ | operator_note documents all assumptions |
| Rule 5: Adversarial check | ✓ | 3 adversarial checks, none break proof |
| Rule 6: Independent cross-check | ✓ | sympy vs scipy agree to 10⁻¹³ |
| Rule 7: No hard-coded formulas | ✓ | Uses explain_calc(), compare() |

---

## Adversarial Check Details

**Check 1: Post-money interpretation**
- Conclusion: Unambiguous in VC practice. No alternative reading exists.
- Breaks proof: No

**Check 2: Effect of dilution**
- Modeled: 3 rounds × 20% dilution → ownership 10.24% → $51.2M exit proceeds → CAGR ≈ 39.5%
- Conclusion: "Before dilution" qualifier is load-bearing. Claim explicitly scopes to no-dilution scenario.
- Breaks proof: No

**Check 3: CAGR vs IRR**
- Conclusion: For two-cashflow investments, CAGR = IRR. No measurement convention changes the result.
- Breaks proof: No

---

## Cross-Check Summary

| Method | Value | Δ from primary |
|--------|-------|----------------|
| sympy exact symbolic | 53.4127% | — |
| scipy brentq NPV=0 | 53.4127% | 1.82 × 10⁻¹¹ pp |

Tolerance: 1 × 10⁻⁸ → **AGREE**
