# Proof Audit Trail: VC Startup Failure Rates

**Generated:** 2026-04-08
**Proof Engine:** 1.10.0
**Verdict:** PARTIALLY VERIFIED (with unverified citations)

---

## Citation Verification

### B1 — Harvard Business School News: The Venture Capital Secret (Shikhar Ghosh)

| Field | Value |
|-------|-------|
| Fact ID | B1 |
| Source | Harvard Business School News: The Venture Capital Secret (Shikhar Ghosh) |
| URL | https://www.hbs.edu/news/Pages/item.aspx?num=487 |
| Quote used | "as many as 75 percent of venture-backed companies never return cash to investors" |
| Verification status | **fetch_failed** |
| Method | N/A |
| Coverage % | N/A |
| Fetch mode | live |
| Credibility tier | Tier 4 (academic domain — .edu) |
| Fetch issue | HTTP 403 Forbidden — server blocked automated fetch |

**Note:** The HBS page returns HTTP 403 for automated requests. The quote is well-attested in secondary sources (Inc. Magazine B2, multiple news outlets) and traces to Shikhar Ghosh's research on 2,000+ VC-backed companies. Manual verification is required to confirm the exact quote on the source page.

---

### B2 — Inc. Magazine: Report — 3 Out of 4 Venture-Backed Start-Ups Fail

| Field | Value |
|-------|-------|
| Fact ID | B2 |
| Source | Inc. Magazine: Report — 3 Out of 4 Venture-Backed Start-Ups Fail |
| URL | https://www.inc.com/john-mcdermott/report-3-out-of-4-venture-backed-start-ups-fail.html |
| Quote used | "as many as 75 percent of venture-backed U.S. companies never return cash to investors" |
| Verification status | **fetch_failed** |
| Method | N/A |
| Coverage % | N/A |
| Fetch mode | live |
| Credibility tier | Tier 2 (unclassified domain — verify source authority manually) |
| Fetch issue | HTTP 403 Forbidden — server blocked automated fetch |

**Note:** Inc.com returns HTTP 403 for automated requests. This article was a news report on the Ghosh/Harvard research and corroborates B1. Manual verification required.

---

### B3 — LLC.org: Startup Failure Rate Statistics (citing BLS data)

| Field | Value |
|-------|-------|
| Fact ID | B3 |
| Source | LLC.org: Startup Failure Rate Statistics (citing BLS data) |
| URL | https://www.llc.org/startup-failure-rate-statistics/ |
| Quote used | "Small businesses have a 70 percent failure rate within 10 years of opening" |
| Verification status | **partial** |
| Method | aggressive_normalization (fragment_match, 4 words) |
| Coverage % | N/A |
| Fetch mode | live |
| Credibility tier | Tier 2 (unclassified domain — verify source authority manually) |
| Closest match hint | "to small businesses, where 70 percent fail within 10 years of opening. More..." (53% similarity) |

**Note:** The quote was partially matched via aggressive normalization with 53% similarity. The page appears to contain a variant wording of the same statistic ("70 percent fail within 10 years of opening" vs. "70 percent failure rate within 10 years of opening"). Manual verification is recommended. Note also that LLC.org is a commercial site — the statistic ultimately originates from BLS Business Employment Dynamics data and applies to ALL small businesses, not specifically VC-backed startups.

---

## Adversarial Check Log

### AC-1: Population mismatch — 70% is for all businesses, not VC-backed

- **Finding:** The 70% figure cited in the claim is the BLS Business Employment Dynamics rate for all small businesses within 10 years. It is NOT a VC-backed-specific figure.
- **Impact:** The claim's core assertion (70% VC-backed failure rate) is based on the wrong population. Ghosh/Harvard's research on 2,000+ VC-backed companies finds 75% never return capital — a different number AND a different definition of failure.
- **Conclusion:** SC1 fails. The cited figure (70%) applies to all businesses; the best VC-specific data (75%) contradicts the claimed number.
- **Breaks proof:** Yes

### AC-2: The '90% of startups fail' baseline is disputed

- **Finding:** Multiple fact-checks identify the 90% figure as a myth or misquotation without traceable origin in BLS or comparable government data. BLS data implies ~65% of businesses fail within 10 years (50% survive 5 years, ~35% survive 10 years).
- **Impact:** If the 90% baseline is false, then the comparative claim ("lower than 90%") is evaluated against an incorrect baseline.
- **Conclusion:** SC2 (that the 90% figure is "commonly cited") is technically true — it IS widely cited — but the figure itself appears to be incorrect. The comparative framing of the claim is undermined.
- **Breaks proof:** Yes

### AC-3: Inconsistent definition of 'failure' across sources

- **Finding:** BLS defines failure as business closure (entity ceases to exist). Ghosh/Harvard defines failure as never returning invested capital to investors. These produce materially different rates for the same set of companies.
- **Impact:** A VC-backed acquisition at a loss to investors is a "failure" under the Ghosh definition but may not be a "failure" under the BLS definition if the acquirer continues operating the business.
- **Conclusion:** The claim does not specify which definition of "failure" it uses. Mixing definitions makes the claim imprecise and difficult to verify or falsify.
- **Breaks proof:** Yes

---

## Verification Summary

| Fact | Status | Breaks Proof |
|------|--------|--------------|
| B1 | fetch_failed (HTTP 403) | — |
| B2 | fetch_failed (HTTP 403) | — |
| B3 | partial (53% similarity match) | — |
| AC-1 (population mismatch) | Confirmed | Yes |
| AC-2 (90% baseline disputed) | Confirmed | Yes |
| AC-3 (definition inconsistency) | Confirmed | Yes |

**Overall verdict: PARTIALLY VERIFIED (with unverified citations)**

All three adversarial checks identify material flaws. B1 and B2 could not be fetched automatically (HTTP 403). B3 was partially matched. SC1 fails because the 70% figure is misapplied to VC-backed startups. SC2 holds in the narrow sense that the 90% figure is indeed commonly cited in popular discourse.
