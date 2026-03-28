# Proof: The correlation between human brain volume and intelligence is r = 0.4

- Generated: 2026-03-27
- Verdict: **PARTIALLY VERIFIED**
- Audit trail: [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

---

## Key Findings

- **SC1 (unconditional overall estimate) — FAILS:** Two independent large-scale meta-analyses, Pietschnig et al. (2015) and Nave et al. (2022), both report r = 0.24 for the unconditional brain volume–IQ correlation. The deviation from 0.40 is 0.16, well outside the ±0.05 tolerance.
- **SC2 (conditional estimate: healthy adults, high-quality tests) — PASSES:** Wikipedia's Neuroscience and intelligence article (citing Gignac & Bates 2017, *Intelligence*) states r ≈ 0.40 when high-quality IQ tests are used in healthy adult samples.
- **The r = 0.4 figure is conditionally correct:** It holds under optimal measurement conditions, not as a general population-wide average.
- **Publication bias inflates, not deflates:** Both major meta-analyses found evidence that published studies overreport high correlations. The true unconditional r is likely ≤ 0.24, not 0.40.

---

## Claim Interpretation

**Natural language claim:** "The correlation between human brain volume and intelligence is r = 0.4"

**Formal interpretation:**

| Field | Value |
|-------|-------|
| Subject | Pearson r between total in-vivo brain volume (MRI) and intelligence (IQ/g-factor) |
| Property | Meta-analytic correlation coefficient |
| Threshold | 0.40 |
| Tolerance | ±0.05 (i.e., 0.35 ≤ r ≤ 0.45) |

**Operator rationale:** The claim specifies a single point value (r = 0.4). A tolerance of ±0.05 is applied, as meta-analytic estimates are reported to two decimal places and carry estimation uncertainty. This is a *generous* interpretation — a narrower tolerance (±0.02) would still fail SC1 and still pass SC2.

**Two sub-claims:**
- **SC1:** The unconditional overall meta-analytic estimate = 0.40 (±0.05)
- **SC2:** The conditional estimate for healthy adults using high-quality intelligence tests = 0.40 (±0.05)

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Pietschnig et al. (2015): overall r = .24, 88 studies, 8,000+ subjects | Yes (live) |
| B2 | Nave et al. (2022): overall r = 0.24, 86 studies, N = 26,000+ | Partial (50% fragment match; data value 0.24 confirmed live) |
| B3 | Wikipedia: r ≈ 0.4 for healthy adults using high-quality tests | Yes (live) |
| A1 | SC1-A deviation: \|0.24 − 0.40\| = 0.1600 | Computed |
| A2 | SC1-B deviation: \|0.24 − 0.40\| = 0.1600 | Computed |
| A3 | SC2 deviation: \|0.40 − 0.40\| = 0.0000 | Computed |
| A4 | Cross-check: Pietschnig 2015 r vs PMC 2022 r — both 0.24 | Computed (agreement) |

---

## Proof Logic

### SC1: Unconditional overall meta-analytic estimate

The two largest systematic meta-analyses both find the same result:

- **Pietschnig et al. (2015) (B1):** Based on 88 studies with over 8,000 subjects, the overall weighted correlation is r = .24 (R² = .06). This generalises across age groups, IQ domains, and sex. The authors note evidence of publication bias inflating earlier estimates.

- **Nave et al. (2022) (B2):** The largest meta-analysis to date (86 studies, N = 26,000+, 454 effect sizes). Most reasonable meta-analytic specifications yield r-values in the mid-0.20s. Their primary result is r = 0.24, with the extreme range being 0.10–0.37 depending on specification choices. Three-quarters of all reasonable specifications do not exceed r = 0.26.

Both sources independently converge on r = 0.24 (cross-check: |0.24 − 0.24| = 0.0 ≤ 0.01, A4). The deviation from the claimed 0.40 is 0.16 — more than three times the ±0.05 tolerance. **SC1 fails.**

### SC2: Conditional estimate (healthy adults, high-quality tests)

**Wikipedia (B3)**, summarising Gignac & Bates (2017, *Intelligence*), states: "In healthy adults, the correlation of total brain volume and IQ is approximately 0.4 when high-quality tests are used." The underlying paper found corrected correlations of .23 (fair quality tests), .32 (good quality), and .39 (excellent quality), concluding the association "is arguably best characterised as r ≈ .40." The deviation from 0.40 is 0.00. **SC2 passes.**

This conditional result is consistent with broader meta-analytic patterns: the Nave et al. (2022) analysis also notes "the strongest effects observed for more g-loaded tests and in healthy samples" (B2).

---

## Counter-Evidence Search

**Does any major unconditional meta-analysis report r = 0.40?**
No. Three principal meta-analyses were reviewed: McDaniel (2005) found r = 0.33 overall (37 samples, n = 1,530); Pietschnig et al. (2015) found r = .24 (88 studies, 8,000+ subjects); Nave et al. (2022) found r = 0.24 (86 studies, N = 26,000+). Gignac & Bates (2017) report r ≈ 0.40 only as a conditional estimate for excellent-quality tests, not as an unconditional overall average.

**Could publication bias be deflating estimates below 0.40?**
No — publication bias works in the opposite direction. Pietschnig et al. (2015) found that "strong and positive correlation coefficients have been reported frequently in the literature whilst small and non-significant associations appear to have been often omitted from reports." Nave et al. (2022) similarly found estimates were "somewhat inflated due to selective reporting." After publication bias correction, estimates remain around r = 0.24. The true unconditional r is likely at or *below* 0.24.

**Is the Wikipedia source for SC2 credible?**
Yes. The source (Gignac & Bates 2017) is published in *Intelligence*, a peer-reviewed Elsevier journal. Its finding that measurement quality moderates the brain–IQ correlation is consistent with the broad meta-analytic literature, and the direction of the effect (better tests → higher correlations) is theoretically well-motivated.

---

## Conclusion

**Verdict: PARTIALLY VERIFIED**

- **SC1 (unconditional r = 0.40): DISPROVED.** The best-established meta-analytic consensus, from two independent studies covering N > 26,000 subjects, places the unconditional correlation at r ≈ 0.24 — not 0.40. This is robust to publication bias corrections (which, if anything, push the true value lower).

- **SC2 (conditional r ≈ 0.40): PROVED.** When the analysis is restricted to healthy adult samples assessed with high-quality (g-loaded) intelligence tests, the correlation rises to approximately r = 0.40. This is supported by the peer-reviewed Gignac & Bates (2017) meta-analysis.

**Summary for practical use:** Citing "r = 0.4" without qualification overstates the general brain–IQ correlation. The unconditional average is approximately r = 0.24. The figure r ≈ 0.40 applies specifically under optimal conditions. Textbooks and popular science that cite r = 0.4 as a universal value are simplifying — the number is conditionally correct but misleading as a blanket statement.

Note: B2 (Nave et al. 2022, PMC) achieved only partial (fragment) citation verification. However, the key data value (r = 0.24) was independently confirmed live on the page, and B1 (Pietschnig 2015) provides full independent verification of the same r = 0.24 result.
