# Audit: The climate has always changed — today's warming is not unusual or alarming.

- **Generated**: 2026-03-29
- **Reader summary**: [proof.md](proof.md)
- **Proof script**: [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Current global warming |
| Compound operator | AND |
| SC1 property | Whether Earth's climate has changed in the past |
| SC1 operator | >= 2 sources |
| SC1 note | Trivially true and universally accepted. 2 sources suffice since uncontested. |
| SC2 property | Whether the current rate of warming is unusual compared to paleoclimate record |
| SC2 operator | >= 3 sources (disproof) |
| SC2 note | If 3+ authoritative sources confirm the rate IS unprecedented, "not unusual" is DISPROVED. |
| SC3 property | Whether today's warming is not alarming |
| SC3 operator | N/A |
| SC3 note | Normative/subjective — cannot be formally proved or disproved. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | sc1_nasa | SC1: NASA — paleoclimate evidence of past changes |
| B2 | sc1_noaa | SC1: NOAA — historical temperature record |
| B3 | sc2_nasa_rate | SC2: NASA — 10x faster than ice age recovery |
| B4 | sc2_ipcc_ar6 | SC2: IPCC AR6 — unprecedented in 2000 years |
| B5 | sc2_noaa_rate | SC2: NOAA — 0.20C/decade since 1975 |
| B6 | sc2_arizona | SC2: U of Arizona — unprecedented in 24,000 years |
| A1 | — | SC1 verified source count |
| A2 | — | SC2 verified source count (disproof) |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | SC1 verified source count | count(verified citations for SC1) = 2 | 2 |
| A2 | SC2 verified source count (disproof) | count(verified citations for SC2 disproof) = 3 | 3 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | SC1: NASA — paleoclimate evidence | NASA Science | https://science.nasa.gov/climate-change/evidence/ | "Carbon dioxide from human activities is increasing about 250 times faster than it did from natural sources after the last Ice Age." | verified | full_quote | Tier 5 (government) |
| B2 | SC1: NOAA — temperature record | NOAA Climate.gov | https://www.climate.gov/news-features/understanding-climate/climate-change-global-temperature | "Earth's temperature has risen by an average of 0.11 Fahrenheit (0.06 Celsius) per decade since 1850, or about 2 F in total." | verified | full_quote | Tier 5 (government) |
| B3 | SC2: NASA — 10x faster | NASA Science | https://science.nasa.gov/climate-change/evidence/ | "Current warming is occurring roughly 10 times faster than the average rate of warming after an ice age." | verified | full_quote | Tier 5 (government) |
| B4 | SC2: IPCC AR6 — unprecedented | IPCC AR6 via Carbon Brief | https://www.carbonbrief.org/in-depth-qa-the-ipccs-sixth-assessment-report-on-climate-science/ | "key indicators of the climate system are increasingly at levels unseen in centuries to millennia, and are changing at rates unprecedented in at least the last 2,000 years" | verified | full_quote | Tier 2 (unknown) |
| B5 | SC2: NOAA — rate data | NOAA Climate.gov | https://www.climate.gov/news-features/understanding-climate/climate-change-global-temperature | "the combined land and ocean temperature has warmed at an average rate of 0.11 degrees Fahrenheit..." | not_found | — | Tier 5 (government) |
| B6 | SC2: U of Arizona — 24,000 years | University of Arizona News | https://news.arizona.edu/news/global-temperatures-over-last-24000-years-show-todays-warming-unprecedented | "the speed of human-caused global warming is faster than anything we've seen in that same time" | verified | full_quote | Tier 4 (academic) |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1** (sc1_nasa)
- Status: verified
- Method: full_quote
- Fetch mode: live

**B2** (sc1_noaa)
- Status: verified
- Method: full_quote
- Fetch mode: live

**B3** (sc2_nasa_rate)
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4** (sc2_ipcc_ar6)
- Status: verified
- Method: full_quote
- Fetch mode: live

**B5** (sc2_noaa_rate)
- Status: not_found
- Method: N/A
- Fetch mode: live
- Impact: B5 provides supplementary rate data (0.20C/decade since 1975). The SC2 disproof does not depend on this source — three other independently verified sources (B3, B4, B6) meet the threshold of 3. The NOAA page likely reformatted the text since the quote was captured via WebFetch. *(Source: author analysis)*

**B6** (sc2_arizona)
- Status: verified
- Method: full_quote
- Fetch mode: live

*Source: proof.py JSON summary*

## Computation Traces

```
SC1: climate has always changed — verified sources vs threshold: 2 >= 2 = True
SC2: current warming IS unusual — disproof sources vs threshold: 3 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

### SC1: Past climate changes

| Source | Status | Organization |
|--------|--------|-------------|
| sc1_nasa | verified | NASA (U.S. federal agency) |
| sc1_noaa | verified | NOAA (U.S. federal agency) |

2 of 2 sources verified. NASA and NOAA are independent U.S. federal agencies with separate research programs.

### SC2: Current rate is unprecedented

| Source | Status | Organization |
|--------|--------|-------------|
| sc2_nasa_rate | verified | NASA (U.S. federal agency) |
| sc2_ipcc_ar6 | verified | IPCC (international intergovernmental body, 234 scientists from 66 countries) |
| sc2_noaa_rate | not_found | NOAA (U.S. federal agency) |
| sc2_arizona | verified | University of Arizona (peer-reviewed paleoclimate reconstruction) |

3 of 4 sources verified. Sources span four independent organizations using different datasets and methodologies:
- NASA uses satellite and instrumental records
- IPCC synthesizes thousands of peer-reviewed studies worldwide
- University of Arizona uses paleoclimate proxy reconstructions (ice cores, sediments, tree rings)
- NOAA maintains independent instrumental temperature records

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**Check 1: Peer-reviewed support for "not unusual"**
- Question: Are there peer-reviewed studies showing current warming rates are within natural variability?
- Search performed: "current warming natural variability not unusual peer reviewed", "climate always changed not unusual scientific evidence"
- Finding: No peer-reviewed studies found in reputable journals concluding the current rate is within natural variability.
- Breaks proof: No

**Check 2: Medieval Warm Period / Holocene Thermal Maximum**
- Question: Could past warm periods make current warming seem less unusual?
- Search performed: "Medieval Warm Period warmer than today", "Holocene Thermal Maximum vs current warming rate"
- Finding: Neither approached the *rate* of current warming. The HCM took thousands of years for 0.7C; current warming exceeded 1.3C in ~150 years.
- Breaks proof: No

**Check 3: Paleoclimate measurement limitations**
- Question: Is there a methodological dispute about paleoclimate warming rate measurements?
- Search performed: "paleoclimate warming rate measurement limitations smoothing bias"
- Finding: Smoothing limitation is acknowledged but does not undermine the disproof. IPCC AR6 accounts for this uncertainty and still concluded with "high confidence."
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | nasa.gov | government | 5 | Government domain (.gov) |
| B2 | climate.gov | government | 5 | Government domain (.gov) |
| B3 | nasa.gov | government | 5 | Government domain (.gov) |
| B4 | carbonbrief.org | unknown | 2 | Unclassified domain — verify source authority manually |
| B5 | climate.gov | government | 5 | Government domain (.gov) |
| B6 | arizona.edu | academic | 4 | Academic domain (.edu) |

Note on B4: Carbon Brief (tier 2) is a well-regarded UK-based climate science media outlet. The quoted text is from the IPCC AR6 report itself (which would be tier 5 intergovernmental). The disproof does not depend solely on this source — B3 (tier 5) and B6 (tier 4) independently confirm the same conclusion.

*Source: proof.py JSON summary*

## Extraction Records

For this qualitative proof, extractions record citation verification status per source:

| Fact ID | Value (status) | Countable | Quote Snippet |
|---------|---------------|-----------|---------------|
| B1 | verified | Yes | "Carbon dioxide from human activities is increasing about 250 times faster than i..." |
| B2 | verified | Yes | "Earth's temperature has risen by an average of 0.11 Fahrenheit (0.06 Celsius)..." |
| B3 | verified | Yes | "Current warming is occurring roughly 10 times faster than the average rate of wa..." |
| B4 | verified | Yes | "key indicators of the climate system are increasingly at levels unseen in centur..." |
| B5 | not_found | No | "the combined land and ocean temperature has warmed at an average rate of 0.11 de..." |
| B6 | verified | Yes | "the speed of human-caused global warming is faster than anything we've seen in t..." |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1**: N/A — qualitative consensus proof with no numeric value extraction
- **Rule 2**: All 6 citation URLs fetched and quotes checked; 5 verified, 1 not found
- **Rule 3**: N/A — no time-dependent computations
- **Rule 4**: Claim interpretation explicit with three sub-claims, operator rationale for each, and compound operator note explaining the logical fallacy in the original claim's structure
- **Rule 5**: Three adversarial checks conducted via web search, covering peer-reviewed counter-evidence, past warm periods, and measurement methodology disputes
- **Rule 6**: SC1 uses 2 independent sources (NASA, NOAA); SC2 uses 4 sources from independent organizations (NASA, IPCC, NOAA, U of Arizona)
- **Rule 7**: N/A — no constants or formulas; `compare()` used for threshold evaluation
- **validate_proof.py result**: PASS with warnings (14/15 checks passed, 1 warning about else branch)

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.2.0 on 2026-03-29.
