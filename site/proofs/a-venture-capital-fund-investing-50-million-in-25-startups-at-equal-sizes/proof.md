# Proof: A venture capital fund investing $50 million in 25 startups at equal sizes requires at least one 50x return and two 10x returns to achieve a 3x gross multiple.

- Generated: 2026-04-08
- Verdict: **DISPROVED**
- Audit trail: [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

---

## Key Findings

- A $50M fund investing equally in 25 startups places **$2M per company**. The 1×50x + 2×10x scenario returns $100M + $40M = **$140M total** — which is only **2.8x gross**, not 3x.
- The scenario falls **$10M short** of the $150M required for a 3x gross multiple.
- The claim also fails as a necessity condition: 3x is achievable without any 50x return. For example, 15 companies at 5x each, or 5 companies at 15x each, each yield exactly 3.0x gross.
- The arithmetic holds under every standard VC definition of gross multiple (TVPI or MOIC). The verdict is DISPROVED by pure computation.

---

## Claim Interpretation

**Natural-language claim:** A venture capital fund investing $50 million in 25 startups at equal sizes requires at least one 50x return and two 10x returns to achieve a 3x gross multiple.

**Formal interpretation:** The claim is read as a sufficiency claim — that 1 company returning 50x, 2 companies returning 10x, and the remaining 22 returning 0x is sufficient to achieve a 3x gross multiple on a $50M equal-allocation fund.

The operator is `==`: the claimed scenario either yields 3.0x or it does not.

- Per-company investment: $50M / 25 = $2.0M
- Required total return for 3x gross: $50M × 3 = $150M
- Actual return under claimed scenario: (1×50 + 2×10) × $2M = $140M
- Since $140M < $150M, the claim is false.

The claim also fails as a necessity condition: 3x is reachable without any 50x return (see Counter-Evidence Search section).

**Formalization scope:** The natural-language claim uses "equal sizes," which the formal interpretation takes at face value as equal dollar allocations. The claim specifies exactly $50M across 25 companies — no ambiguity in the formalization. The formal interpretation is a faithful 1:1 mapping of the claim's arithmetic structure.

*Source: proof.py JSON summary*

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| A1 | Per-company investment: $50M / 25 companies = $2M each | Computed: $2.0M per company |
| A2 | Total return under claimed scenario: (1×50 + 2×10) × $2M = $140M | Computed: $140.0M total return |
| A3 | Gross multiple achieved: $140M / $50M = 2.8x | Computed: 2.8000x (vs. claimed 3.0x) |
| A4 | Cross-check via direct portfolio sum: 1×$100M + 2×$20M + 22×$0M = $140M | Computed: $140.0M → 2.8000x (independently agrees) |
| A5 | Claim evaluation: gross_multiple == 3.0 | Computed: False (2.8x ≠ 3.0x) |

*Source: proof.py JSON summary*

---

## Proof Logic

The fund invests $50M equally across 25 companies, placing **$2.0M per company** (A1).

Under the claimed scenario (1 company at 50x, 2 at 10x, 22 at 0x), the returns are:
- 1 winner at 50x: 50 × $2M = **$100M** 
- 2 winners at 10x: 2 × 10 × $2M = **$40M**
- 22 companies at 0x: **$0M**

Total return: $100M + $40M = **$140M** (A2).

Gross multiple: $140M / $50M = **2.8x** (A3). The required gross multiple for a 3x return is $50M × 3 = $150M. The scenario falls **$10M short** of this target.

The cross-check (A4) independently confirms this by explicitly summing all 25 company returns (one at $100M, two at $20M each, twenty-two at $0M) and divides by $50M, also yielding 2.8000x. Both methods agree exactly.

The claim evaluation (A5) compares 2.8000 == 3.0, which is False. Verdict: **DISPROVED**.

*Source: author analysis*

---

## Counter-Evidence Search

**Check 1 — Can 3x be achieved without any 50x return?**

Two alternative portfolios were computed: (a) 15 companies at 5x each, yielding 15 × 5 × $2M = $150M → 3.0x gross; (b) 5 companies at 15x each, yielding 5 × 15 × $2M = $150M → 3.0x gross. Both achieve the 3x threshold without any 50x return. The claim therefore also fails as a necessity condition — it is neither sufficient nor necessary.

**Check 2 — What if the fund had 20 companies instead of 25?**

With $50M / 20 companies = $2.5M each, the same 1×50x + 2×10x pattern returns (1×50 + 2×10) × $2.5M = $175M → 3.50x gross. This shows the number of portfolio companies is the critical variable: with 25 companies the per-company stake ($2M) is too small to reach 3x with this pattern. The pattern only clears 3x when the fund has ≤23 companies (per-company stake ≥ $2.143M).

**Check 3 — Does the definition of "gross multiple" matter?**

Both TVPI (total value to paid-in) and MOIC (multiple on invested capital) are computed identically at the fund level: total proceeds ÷ total invested capital. Both yield 2.8x for this scenario. No standard VC accounting convention changes the result.

None of the three checks found evidence that breaks or weakens the disproof.

*Source: proof.py JSON summary (adversarial_checks)*

---

## Conclusion

**Verdict: DISPROVED.**

The claimed scenario (1×50x + 2×10x returns, others zero, on a $50M equal-size fund with 25 investments) yields a gross multiple of **2.8x**, not 3x. The fund falls $10M short of the $150M required for 3x. This is a pure arithmetic result: 1×50 + 2×10 = 70 weighted units × $2M per unit = $140M < $150M.

Additionally, the claim fails as a necessity condition: multiple alternative portfolios achieve 3x without any 50x return.

This is a pure-math proof with no empirical citations. The verdict does not depend on any unverified sources.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.10.0 on 2026-04-08.*
