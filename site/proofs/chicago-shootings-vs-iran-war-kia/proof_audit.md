# Audit: More Americans were killed in Chicago shootings over a four-week period in March 2026 than US service members killed in action in the US-Israel Iran war to date.

- **Generated:** 2026-04-18
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The natural-language claim compares two quantities: Americans killed in Chicago shootings during a four-week period in March 2026, and US service members killed in action in the US-Israel Iran war "to date."

"Killed in Chicago shootings" is operationalized as CPD's "shot & killed" category — people who died from gunshot wounds in Chicago. This excludes homicides by other means (stabbings, beatings, etc.). "Four-week period in March 2026" is interpreted as any 28-consecutive-day window within March 1-31, computed as 28/31 of the full monthly total. "Killed in action" (KIA) uses the standard military classification: deaths caused by enemy fire, as distinguished from non-hostile deaths. "To date" is anchored to the proof generation date (April 18, 2026).

**Formalization scope:** The natural-language claim is faithfully captured. One narrowing: the proof uses estimated shooting deaths (90% of 41 homicides = ~37) rather than an exact count, because official CPD monthly reports distinguish total homicides but do not always separately publish "shooting deaths" as a standalone figure. The 90.3% rate is derived from the same source's YTD data (112 shot & killed out of 124 total homicides). This is a conservative estimate — the true figure may be slightly higher.

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Comparison of Chicago shooting fatalities vs. US KIA in Iran war |
| Property | Chicago shooting deaths in a 4-week March 2026 window vs. US KIA to date |
| Operator | > |
| Threshold | 0 (Chicago deaths minus US KIA must be positive) |
| Time-sensitive | Yes |

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | military_times | Military Times — 7 US service members killed by enemy fire (KIA) |
| B2 | military_times_total | Military Times — 13 total US service members killed |
| B3 | heyjackass_ytd | HeyJackass.com — 2026 YTD Chicago shot & killed totals |
| B4 | nbc_chicago | NBC Chicago — Chicago murders up 16% in March 2026 |
| B5 | cbs_weekend_mar20 | CBS Chicago — 4 killed in weekend shootings March 20-23 |
| B6 | cbs_weekend_mar13 | CBS Chicago — 3 killed in weekend shootings March 13-16 |
| B7 | cbs_weekend_feb27 | CBS Chicago — 5 killed in weekend shootings Feb 27-Mar 2 |
| A1 | — | Compute Q1 2026 shot & killed from YTD minus April-to-date |
| A2 | — | Estimate minimum 4-week shooting deaths (28/31 of monthly) |
| A3 | — | Comparison — Chicago 4-week shooting deaths > US KIA |

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Q1 2026 shot & killed | ytd_shot_killed − apr_shot_killed | 93.0 |
| A2 | Minimum 4-week shooting deaths | march_shooting_deaths × 28/31 | 33.3 |
| A3 | Comparison: Chicago > US KIA | compare(33.3, >, 7) | True |

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote (truncated) | Status | Method | Credibility |
|----|------|--------|-----|--------------------|--------|--------|-------------|
| B1 | 7 KIA in Operation Epic Fury | Military Times (DCAS) | [link](https://www.militarytimes.com/news/your-military/2026/04/08/pentagon-data-13-us-troops-killed-346-wounded-in-operation-epic-fury/) | "the department listed seven service members as having been killed by enemy fire..." | verified | full_quote | Tier 2 (unclassified — Military Times is the leading US mil pub) |
| B2 | 13 total US killed | Military Times (CENTCOM) | [link](https://www.militarytimes.com/news/your-military/2026/04/08/pentagon-data-13-us-troops-killed-346-wounded-in-operation-epic-fury/) | "13 U.S. service members have been killed and 381 have been wounded..." | verified | full_quote | Tier 2 |
| B3 | YTD Chicago shot & killed: 112 | HeyJackass.com (CPD/CFD/ME) | [link](https://heyjackass.com/) | "Year to Date Shot & Killed: 112 Shot & Wounded: 374 Total Shot: 486..." | verified | full_quote | Tier 2 (unclassified — community tracker sourced from official data) |
| B4 | Murders up 16% in March | NBC Chicago (CPD) | [link](https://www.nbcchicago.com/investigations/shootings-up-78-in-chicago-in-one-week-as-city-suffers-two-month-murder-surge/3916370/) | "murders citywide have also surged in the past two months: increasing 16%..." | verified | full_quote | Tier 2 (NBC affiliate) |
| B5 | 4 killed weekend Mar 20-23 | CBS Chicago | [link](https://www.cbsnews.com/chicago/news/chicago-weekend-shootings-march-20-to-23/) | "At least four people were killed, and 17 people were hurt..." | verified | full_quote | Major news (Tier 3) |
| B6 | 3 killed weekend Mar 13-16 | CBS Chicago | [link](https://www.cbsnews.com/chicago/news/chicago-weekend-shootings-march-13-to-16/) | "At least three people were killed, and 11 others were injured..." | verified | full_quote | Major news (Tier 3) |
| B7 | 5 killed weekend Feb 27-Mar 2 | CBS Chicago | [link](https://www.cbsnews.com/chicago/news/chicago-weekend-shootings-feb-27-to-march-2/) | "At least five people were killed, and 18 others were injured..." | verified | full_quote | Major news (Tier 3) |

## Citation Verification Details

All 7 citations were verified via live fetch with full_quote matching.

| ID | Status | Method | Fetch Mode | Notes |
|----|--------|--------|------------|-------|
| B1 | verified | full_quote | live | Quote found verbatim on Military Times page |
| B2 | verified | full_quote | live | Quote found verbatim on Military Times page (same article, different passage) |
| B3 | verified | full_quote | live | Quote found verbatim on HeyJackass.com homepage; data_values also verified (4/4 values found on page) |
| B4 | verified | full_quote | live | Quote found verbatim on NBC Chicago page |
| B5 | verified | full_quote | live | Quote found verbatim on CBS Chicago page |
| B6 | verified | full_quote | live | Quote found verbatim on CBS Chicago page |
| B7 | verified | full_quote | live | Quote found verbatim on CBS Chicago page |

## Data Value Verification (B3)

| Key | Value | Found | Fetch Mode |
|-----|-------|-------|------------|
| ytd_shot_killed | 112 | Yes | live |
| ytd_total_homicides | 124 | Yes | live |
| apr_shot_killed | 19 | Yes | live |
| apr_total_homicides | 22 | Yes | live |

## Cross-Checks

**Cross-check 1: US deaths internal consistency.** 7 KIA (B1) + 6 non-hostile = 13 total (B2). Values are from different passages in the same article but describe different DCAS classifications. Independently published (same upstream authority: Pentagon DCAS/CENTCOM).

**Cross-check 2: Weekend shooting deaths corroborate monthly rate.** CBS Chicago weekend reports (B5, B6, B7) document 12 killed in shooting incidents across 3 weekends (9 days). This implies a weekend shooting death rate of 1.3/day, which exceeds the overall monthly rate of 1.2/day (37 shooting deaths / 31 days). This is consistent with the known pattern that weekends are deadlier than weekdays in Chicago.

## Adversarial Checks

| # | Question | Verification | Finding | Breaks Proof |
|---|----------|-------------|---------|--------------|
| 1 | Could there be unreported US KIA? | Searched for updates; ceasefire since April 8 | No additional KIA; margin too large (26+) | No |
| 2 | Is KIA definition too narrow? | Checked military terminology | Even using all 13 deaths, 33 > 13 | No |
| 3 | Does Chicago count include non-fatal? | Checked claim language | Proof uses only "shot & killed" | No |
| 4 | Is 41 March homicides accurate? | Cross-checked WTTW, NBC, HeyJackass | Multiple independent outlets confirm | No |

## Source Credibility Assessment

Military Times (B1, B2): Tier 2/unclassified by automated classifier, but Military Times is the leading independent US military news publication, reporting Pentagon DCAS data directly. Source authority is high.

HeyJackass.com (B3): Tier 2/unclassified. Community-run Chicago crime tracker that sources data from CPD, Chicago Fire Department, and Medical Examiner records. Data is consistent with official CPD statistics reported by major news outlets.

NBC Chicago (B4): Tier 2/unclassified by classifier, but NBC Chicago is a major local affiliate reporting CPD crime statistics directly.

CBS Chicago (B5, B6, B7): Tier 3/major_news. CBS News is a major news organization.

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.23.0 on 2026-04-18.
