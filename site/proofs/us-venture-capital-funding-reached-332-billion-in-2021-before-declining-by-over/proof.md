# Proof: US venture capital funding reached $332 billion in 2021 before declining by over 35% in 2022.

- **Generated:** 2026-04-08
- **Verdict:** PARTIALLY VERIFIED
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

---

## Key Findings

- The NVCA/PitchBook Q4 2021 Venture Monitor reported $329.9B in US VC deal value for 2021 — within $2.1B (0.6%) of the claimed $332B, confirmed as approximately correct (B1).
- CB Insights reported 2022 US VC at $198.4B, a 37% decline from 2021 — confirming the >35% threshold (B2).
- PitchBook-NVCA reported 2022 US VC at $238.3B, a 30.8% decline from a revised 2021 baseline of $344.7B — below the 35% threshold and directly contradicting sub-claim 2 (B3).
- Sources agree on the direction of the decline but disagree on magnitude: whether it exceeded 35% depends on methodology and which 2021 baseline is used.

---

## Claim Interpretation

The natural-language claim asserts two things: (1) US venture capital funding totaled $332 billion in 2021, and (2) it declined by more than 35% in 2022.

**Formal interpretation:** The claim is treated as a compound AND of two sub-claims:

- **SC1:** 2021 US VC deal value ≥ ~$332B (operationalized as >$300B, given source variation)
- **SC2:** 2022 US VC deal value declined by >35% year-over-year from 2021

The **operator** is compound AND: both sub-claims must hold for PROVED.

**Operator rationale:** The claim's phrasing ("reached $332 billion ... before declining by over 35%") requires both the 2021 figure and the 2022 decline magnitude to be approximately correct.

**Formalization scope:** The natural-language claim cites a specific figure ($332B) that no single major source publishes exactly. The formal interpretation accepts NVCA's $329.9B initial estimate and PitchBook's $344.7B revised estimate as the bracketing range; $332B is treated as approximately correct if it falls within this range. For SC2, the >35% threshold is applied literally. The claim does not specify which data provider's methodology governs — this ambiguity is the core reason for the PARTIALLY VERIFIED verdict.

*Source: proof.py JSON summary*

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | NVCA press release: 2021 US VC = $329.9B | Yes |
| B2 | CB Insights: 2022 US VC = $198.4B (down 37% from 2021) | Yes |
| B3 | PitchBook-NVCA via Built In: 2022 US VC = $238.3B (down 30.8% from $344.7B) | Yes |

Note: "Verified: Yes" means the quote was found on the source page. It does not mean the quote entails the claim's conclusion. See Proof Logic below for the reasoning chain.

Note: All three citations are from unclassified (Tier 2) domains. See Source Credibility Assessment in the audit trail.

*Source: proof.py JSON summary*

---

## Proof Logic

**Sub-claim 1 (2021 US VC ≈ $332B):**

The NVCA press release reported "a staggering $329.9 billion was invested across an estimated 17,054 deals" in 2021 (B1). This is $2.1B below the claimed $332B — a 0.6% discrepancy. PitchBook later revised its 2021 estimate upward to $344.7B (cited in B3's context). The claimed $332B falls between these two estimates, likely reflecting a different aggregation methodology (possibly KPMG Venture Pulse Q4 2021). No single major source publishes exactly $332B, but the figure is within the range of credible estimates. SC1 holds: 2021 US VC clearly exceeded $300B.

**Sub-claim 2 (2022 US VC declined >35%):**

Two independent sources report 2022 US VC totals with divergent conclusions:

- CB Insights reports $198.4B in 2022, explicitly stating "down 37% from 2021" (B2). This confirms SC2.
- PitchBook-NVCA reports $238.3B in 2022 (B3). Using PitchBook's revised 2021 baseline of $344.7B, the computed decline is (344.7 − 238.3) / 344.7 × 100 = 30.9% — below the 35% threshold. SC2 is not confirmed by PitchBook.

The cross-check of the two 2022 figures ($198.4B vs $238.3B) shows a 16.7% relative difference, within the 30% relative tolerance, confirming these are measuring the same phenomenon with different scope (CB Insights uses a narrower fund universe; PitchBook includes more fund types and uses a higher revised 2021 baseline).

**Overall:** SC1 holds. SC2 is confirmed by one source (CB Insights) and contradicted by the most authoritative VC data provider (PitchBook-NVCA). The verdict is PARTIALLY VERIFIED.

*Source: author analysis*

---

## Counter-Evidence Search

**1. PitchBook-NVCA reports only 30.8% decline (< 35% threshold)**

PitchBook-NVCA Q4 2022 Venture Monitor reports 2022 US VC at $238.3B, down 30.8% from the revised 2021 figure of $344.7B. This is below the claim's >35% threshold and directly contradicts SC2. PitchBook is the most authoritative VC data source for the US market. The discrepancy with CB Insights (−37% using $198.4B) reflects: (1) different fund universes included, (2) different treatment of corporate VC and CVC arms, (3) PitchBook's revised 2021 baseline of $344.7B vs CB Insights' lower baseline. **This breaks SC2.**

**2. $332B claim vs $329.9B actual (NVCA) — minor discrepancy**

The NVCA press release cites $329.9B for 2021 (initial estimate). PitchBook later revised this to $344.7B. The claim's $332B is between these two figures, suggesting it may reflect KPMG's Venture Pulse Q4 2021 or an intermediate estimate. No single major source publishes exactly $332B, but the figure is within the range of credible estimates. **Does not break the proof.**

**3. Global vs US figures — scope alignment**

The NVCA/PitchBook figures are for US-only venture capital. CB Insights also reports global figures (e.g., $415B global VC in 2021) which are higher. The claim uses "US venture capital funding," consistent with the NVCA/PitchBook scope. No scoping inconsistency in the sources used. **Does not break the proof.**

*Source: proof.py JSON summary*

---

## Conclusion

**Verdict: PARTIALLY VERIFIED**

SC1 holds: 2021 US VC reached approximately $332B (NVCA's $329.9B initial estimate, within 0.6% of the claimed figure, confirmed by B1). SC2 is contested: CB Insights confirms a 37% decline (B2), exceeding the >35% threshold, but PitchBook-NVCA — the most authoritative source — reports only 30.8% using a revised 2021 baseline (B3). The discrepancy arises from different fund universes and baseline methodologies, not a factual error by either provider.

All three citations come from unclassified (Tier 2) domains (nvca.org, cbinsights.com, builtin.com). The NVCA and CB Insights figures are authoritative industry sources despite their unclassified tier designation; the builtin.com article directly cites the PitchBook-NVCA Venture Monitor. The PARTIALLY VERIFIED verdict does not depend on these credibility limitations — the central issue is source disagreement on the decline percentage, not source quality.

Note: 3 citation(s) come from unclassified or low-credibility sources. See Source Credibility Assessment in the audit trail.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.10.0 on 2026-04-08.*
