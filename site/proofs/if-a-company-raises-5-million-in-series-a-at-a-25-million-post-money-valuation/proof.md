# Claim Verification: "If a company raises $5 million in Series A at a $25 million post-money valuation and exits at $500 million seven years later, the annualized return to the Series A investor exceeds 40% before dilution." — PROVED

## Claim

> If a company raises $5 million in Series A at a $25 million post-money valuation and exits at $500 million seven years later, the annualized return to the Series A investor exceeds 40% before dilution.

## Key Findings

- Series A ownership: **20%** ($5M / $25M post-money)
- Exit proceeds (no dilution): **$100M** (20% × $500M)
- MOIC: **20×**
- CAGR (sympy exact): **53.41%** — exceeds the 40% threshold by 13.4 percentage points
- Cross-check: scipy numerical IRR agrees to within 1.8 × 10⁻¹³

## Verdict

**PROVED**

The computed annualized return (CAGR) under the stated scenario is **53.41%**, which strictly exceeds the claimed 40% threshold. The result is confirmed by two independent computational methods (sympy symbolic solver and scipy numerical solver) agreeing to within 10⁻¹³.

## Claim Interpretation

**Subject:** Annualized return (CAGR) to a Series A investor who invests $5M at a $25M post-money valuation, holds for 7 years, and exits at a $500M company valuation.

**Formal specification:** CAGR > 0.40 (40%)

**Formalization scope:** The claim specifies "before dilution" — this proof models a scenario with no intermediate financing rounds. The investor retains the full 20% ownership stake (= $5M / $25M) from investment through exit. If typical dilution of ~20% per subsequent round is modeled over 7 years (3 rounds), CAGR falls to approximately 39.5% — below the 40% threshold. The "before dilution" qualifier is therefore load-bearing.

**CAGR** is defined as MOIC^(1/years) − 1, which equals IRR for a two-cashflow investment (initial outlay, single exit).

## Evidence Summary

All facts are Type A (computed):

| ID | Description | Value |
|----|-------------|-------|
| A1 | Series A ownership stake | 20.00% |
| A2 | Exit proceeds (20% × $500M, no dilution) | $100,000,000 |
| A3 | MOIC (multiple on invested capital) | 20.00× |
| A4 | CAGR via sympy exact symbolic solve | **53.4127%** |

## Proof Logic

| Method | CAGR | Agreement |
|--------|------|-----------|
| sympy exact symbolic solve | 53.4127% | — |
| scipy brentq NPV=0 numerical solve | 53.4127% | Δ = 1.8 × 10⁻¹³ ✓ |

## Adversarial Checks

1. **Post-money vs pre-money interpretation** — "Post-money valuation" is unambiguous in VC practice: it is the valuation after the investment closes. Pre-money = $20M, ownership = $5M/$25M = 20%. No alternative reading exists.

2. **Effect of dilution** — Removing the "before dilution" caveat and modeling 3 subsequent rounds at 20% dilution each reduces CAGR to ≈39.5%, just below 40%. The qualifier is material.

3. **CAGR vs IRR equivalence** — For a two-cashflow scenario (one investment, one exit), CAGR and IRR are identical. No accounting convention would change the result.

## Conclusion

The claim is **PROVED**. Under the stated no-dilution scenario:
- Ownership: 20%
- Exit proceeds: $100M
- MOIC: 20×
- CAGR: **53.41%** (> 40% threshold by 13.4 percentage points)
