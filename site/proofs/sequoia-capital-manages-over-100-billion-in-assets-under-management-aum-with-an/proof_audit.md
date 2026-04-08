# Proof Audit Trail: Sequoia Capital AUM and Fund Multiples

**Generated:** 2026-04-08
**Proof Engine:** 1.10.0
**Verdict:** PARTIALLY VERIFIED (with unverified citations)

---

## Citation Verification

### B1 — Wikipedia: Sequoia Capital — AUM figure for US/Europe entity (2024)

| Field | Value |
|-------|-------|
| Fact ID | B1 |
| Source | Wikipedia: Sequoia Capital — AUM figure for US/Europe entity (2024) |
| URL | https://en.wikipedia.org/wiki/Sequoia_Capital |
| Quote used | "AUM US$ 56.3 billion (2024)" |
| Verification status | **verified** |
| Method | unicode_normalized (full quote match after Unicode normalization) |
| Coverage % | N/A |
| Fetch mode | live |
| Credibility tier | Tier 3 (established reference source — Wikipedia) |
| Fetch issue | None |

**Note:** Quote was fully verified after Unicode normalization (the dollar sign and spacing may differ in rendered vs. raw Wikipedia text). The $56.3B figure is sourced from Sequoia Capital's Wikipedia infobox and reflects the US/Europe entity only.

---

### B2 — Wikipedia: HongShan — formerly Sequoia China, now independent entity

| Field | Value |
|-------|-------|
| Fact ID | B2 |
| Source | Wikipedia: HongShan — formerly Sequoia China, now independent entity |
| URL | https://en.wikipedia.org/wiki/HongShan |
| Quote used | "Assets under management US$56 billion" |
| Verification status | **not_found** |
| Method | N/A |
| Coverage % | N/A |
| Fetch mode | live |
| Credibility tier | Tier 3 (established reference source — Wikipedia) |
| Fetch issue | Quote not matched on page — Wikipedia infobox text may use different phrasing |

**Note:** The Wikipedia article for HongShan was fetched successfully but the exact quote "Assets under management US$56 billion" was not matched. The Wikipedia infobox may present this figure in a different format (e.g., different punctuation, wording, or currency notation). The $56B figure is commonly cited for HongShan in press coverage; manual verification of the current Wikipedia text is recommended.

---

### B3 — Wikipedia: Peak XV Partners — formerly Sequoia India/Southeast Asia

| Field | Value |
|-------|-------|
| Fact ID | B3 |
| Source | Wikipedia: Peak XV Partners — formerly Sequoia India/Southeast Asia |
| URL | https://en.wikipedia.org/wiki/Peak_XV_Partners |
| Quote used | "Assets under management US$9 billion" |
| Verification status | **fetch_failed** |
| Method | N/A |
| Coverage % | N/A |
| Fetch mode | live |
| Credibility tier | Tier 3 (established reference source — Wikipedia) |
| Fetch issue | HTTP 404 — page may have been renamed or moved on Wikipedia |

**Note:** The Peak XV Partners Wikipedia page returned HTTP 404 at time of verification. The page may have been renamed (e.g., to "Peak XV" without "Partners"), deleted, or the URL may have changed. Manual verification required. The $9B figure for Peak XV AUM is cited in press coverage; the exact current Wikipedia value should be confirmed.

---

## Adversarial Check Log

### AC-1: The US/Europe Sequoia entity alone has only $56.3B AUM (< $100B)

- **Finding:** Wikipedia confirms the US/Europe Sequoia Capital entity has $56.3B AUM (2024), which is less than the $100B threshold. The $100B threshold is crossed only when combining all three post-split successor entities.
- **Computation:** $56.3B (US/Europe) + $56B (HongShan) + $9B (Peak XV) = $121.3B combined.
- **Impact:** SC1 depends on interpretation. The "Sequoia Capital" brand post-2021 primarily refers to the US/Europe entity ($56.3B). Whether the claim intends the pre-split organization or all successor entities is ambiguous — and material.
- **Breaks proof:** Yes

### AC-2: Average net fund multiple > 4x is not publicly documented

- **Finding:** No public source provides a verified average net MOIC across all Sequoia funds. VC fund return data is not publicly disclosed unless reported in LP meeting presentations. Cambridge Associates and Preqin track this data but require paid subscriptions.
- **Impact:** SC2 cannot be verified from public sources. The claim asserts ">4x net average" without any citable evidence.
- **Breaks proof:** Yes

### AC-3: Sequoia has both top-performing funds and below-average ones

- **Finding:** Any calculation of "average fund multiple" must include all funds, including newer and underperforming vintages. The Cambridge Associates benchmark for top-quartile VC funds (1985-2015 vintages) is typically 2-3x net TVPI. A "4x net average" would require Sequoia to consistently perform at ~2x the top-quartile benchmark.
- **Impact:** Even granting Sequoia's exceptional historical performance, the "average" claim across their full fund history remains unverified and is a higher bar than often assumed.
- **Breaks proof:** Yes

---

## Computed Values (from proof.py)

| Variable | Value | Source |
|----------|-------|--------|
| aum_us_europe_B | $56.3B | B1 (Wikipedia, verified) |
| aum_hongshan_B | $56.0B | B2 (Wikipedia, not_found) |
| aum_peak_xv_B | $9.0B | B3 (Wikipedia, fetch_failed) |
| aum_combined_B | $121.3B | Computed: 56.3 + 56.0 + 9.0 |
| SC1 (US/Europe only) | False | 56.3 > 100 = False |
| SC1 (combined) | True | 121.3 > 100 = True |
| SC2 (public data) | False | 0 sources >= 1 required |

---

## Verification Summary

| Fact | Status | Notes |
|------|--------|-------|
| B1 | verified | Full match after Unicode normalization |
| B2 | not_found | Fetched but quote not matched; manual check needed |
| B3 | fetch_failed | HTTP 404; page may have moved |
| AC-1 (AUM entity ambiguity) | Confirmed | SC1 holds only with combined entities |
| AC-2 (no public MOIC data) | Confirmed | SC2 unverifiable from public sources |
| AC-3 (average vs. best fund) | Confirmed | Raises bar for SC2 further |

**Overall verdict: PARTIALLY VERIFIED (with unverified citations)**

SC1 is supportable only under a broad interpretation (all three successor entities combined = $121.3B). The US/Europe entity alone ($56.3B) does not meet the threshold. SC2 has no public supporting evidence. B2 and B3 could not be fully verified by automated fetch.
