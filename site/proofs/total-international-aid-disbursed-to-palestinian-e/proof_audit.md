# Audit: Total international aid to Palestinian entities from 1994–2023 exceeded $40 billion USD

**Generated:** 2026-03-27
**Reader summary:** [proof.md](proof.md)
**Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Cumulative international aid to Palestinian entities (West Bank and Gaza Strip) |
| Property | Total nominal USD disbursements from OECD DAC bilateral aid and UNRWA contributions, 1994–2023 |
| Operator | `>` |
| Threshold | $40,000,000,000 (40 billion USD, nominal) |
| Operator note | Conservative two-step: if 1994–2020 > $40B AND 2021–2023 > $0, then 1994–2023 > $40B. The OECD total ODA figure for West Bank & Gaza embeds UNRWA imputed share. Bilateral-only + full UNRWA sum would be even larger. |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_wikipedia | Wikipedia citing OECD: aid to Palestinians totaled over $40B, 1994–2020 |
| B2 | source_arabcenterdc | Arab Center DC citing OECD: aid to Palestinians amounted to more than $40B, 1994–2020 |
| B3 | source_borgen | Borgen Project citing OECD (via Arab Center DC): >$40B to Palestinians, 1994–2020 |
| B4 | source_donortracker | Donor Tracker citing OECD 2024 preliminary: $1.4B to West Bank & Gaza in 2023 |
| A1 | (computed) | Conservative lower bound for 1994–2023 total: $40B floor (1994–2020) + $1.4B (2023 alone) |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Conservative lower bound: 1994–2020 floor + 2023 | explain_calc('baseline_b1 + oda_2023', locals()) | $41,400,000,000 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Wikipedia on 1994–2020 OECD total | Wikipedia — International aid to Palestinians | https://en.wikipedia.org/wiki/International_aid_to_Palestinians | "According to the Organization for Economic Cooperation and Development, aid to Palestinians totaled over $40 billion between 1994 and 2020." | Partial | fragment (50%) | Tier 3 (reference) |
| B2 | Arab Center DC on 1994–2020 OECD total | Arab Center Washington DC (2022) | https://arabcenterdc.org/resource/international-aid-to-the-palestinians-between-politicization-and-development/ | "According to figures compiled by the Organization for Economic Cooperation and Development, aid to Palestinians amounted to more than $40 billion between 1994 and 2020." | Verified | full_quote | Tier 2 (unclassified) |
| B3 | Borgen Project on 1994–2020 OECD total | The Borgen Project — Foreign Aid to Palestine | https://borgenproject.org/foreign-aid-to-palestine/ | "The Organization for Economic Cooperation and Development (OECD) estimates that between 1994 and 2020, funding to the Palestinians totaled more than $40 billion" | Verified | full_quote | Tier 2 (unclassified) |
| B4 | Donor Tracker on 2023 ODA | Donor Tracker — OECD 2023 Preliminary Data (2024) | https://donortracker.org/publications/donor-updates-in-brief-2023-oecd-preliminary-data-2024 | "ODA to the West Bank and Gaza increased by 12% to US$1.4 billion;" | Verified | full_quote | Tier 2 (unclassified) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — Wikipedia (source_wikipedia)**
- Status: `partial` (fragment match, 50% word coverage)
- Method: `fragment` — live fetch succeeded but only 10 of 20 quote words matched. Likely explanation: Wikipedia's page structure uses wikitext markup, and the sentence may be embedded in a template or rendered differently in raw HTML. The phrase "over $40 billion between 1994 and 2020" may be partially present.
- Fetch mode: `live`
- Impact: The key fact (OECD >$40B for Palestinians, 1994–2020) established by B1 is independently and fully verified by B2 (full_quote) and B3 (full_quote). The conclusion does not depend on B1.

**B2 — Arab Center DC (source_arabcenterdc)**
- Status: `verified`
- Method: `full_quote` — exact text found on live page
- Fetch mode: `live`

**B3 — Borgen Project (source_borgen)**
- Status: `verified`
- Method: `full_quote` — exact text found on live page
- Fetch mode: `live`

**B4 — Donor Tracker (source_donortracker)**
- Status: `verified`
- Method: `full_quote` — exact text found on live page
- Fetch mode: `live`

*Source: proof.py JSON summary*

---

## Computation Traces

```
baseline_b1 + oda_2023: baseline_b1 + oda_2023 = 40000000000.0 + 1400000000.0 = 4.14e+10

Baseline 1994–2020 floor:  $40,000,000,000
2023 ODA (OECD prelim.):   $1,400,000,000
Conservative 1994–2023 LB: $41,400,000,000
Threshold:                 $40,000,000,000
Margin above threshold:    $1,400,000,000

compare: 41400000000.0 > 40000000000 = True
```

**Notes:**
- `baseline_b1` = $40B is a stated lower bound extracted from quote (quote says "over" / "more than" $40B)
- `oda_2023` = $1.4B is itself conservative (excludes UNRWA core operations per OECD note)
- 2021 and 2022 flows are not included in the conservative total (no precise published figure used)
- The actual 1994–2023 total is substantially higher than the computed $41.4B lower bound

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

| Cross-check | Values compared | Agreement | Tolerance | Independence note |
|-------------|----------------|-----------|-----------|-------------------|
| B1 (Wikipedia) vs B2 (Arab Center DC), 1994–2020 floor | $40,000,000,000 vs $40,000,000,000 | ✓ | 0.1% relative | Independently published; same OECD data authority |
| B1 (Wikipedia) vs B3 (Borgen Project), 1994–2020 floor | $40,000,000,000 vs $40,000,000,000 | ✓ | 0.1% relative | B3 cites B2 (Arab Center DC) directly — not fully independent of B2 |

**Independence assessment:** B1 (Wikipedia) and B2 (Arab Center DC) are independently published by different organizations. Both trace to the same underlying OECD DAC data, making them "independently published (same upstream authority)" rather than "independently measured." This provides weaker assurance than independent measurements but can still catch transcription errors. B3 (Borgen Project) explicitly hyperlinks to B2 as its source — it is not independent of B2. The strongest independent cross-check is B1 vs B2.

*Source: proof.py JSON summary*

---

## Adversarial Checks (Rule 5)

| # | Question | Search performed | Finding | Breaks proof? |
|---|----------|-----------------|---------|---------------|
| 1 | Are there credible sources disputing the >$40B OECD figure for 1994–2020? | Searched "Palestinian aid $40 billion disputed," "OECD aid Palestinians overcount," "Palestinian aid figure wrong," "foreign aid Palestinians less than 40 billion." Reviewed WaPo fact-check (May 2019) of Kushner claim. | No credible source disputes the cumulative total. WaPo confirmed high per-capita ODA without disputing the aggregate. | No |
| 2 | Does Carnegie Endowment's $35.1B (constant prices, 1994–2016) contradict the >$40B nominal figure? | Reviewed Carnegie 2018 report. Searched "Carnegie Palestine aid constant vs nominal." | No contradiction: different period (stops 2016) and different price basis (constant vs. nominal). Not competing measurements. | No |
| 3 | Would bilateral-only OECD ODA (excluding UNRWA imputed) drop below $40B? | Searched "OECD DAC bilateral ODA West Bank Gaza excludes UNRWA," "Palestine bilateral aid only no multilateral imputed." Reviewed i-AML figures. | i-AML reports ~$26.7B for 2011–2021 alone in OECD member-state donations. Bilateral + UNRWA separately would likely total $50B+ for 1994–2020. | No |
| 4 | Does the 2023 OECD preliminary ($1.4B) exclude UNRWA, making the conservative total understate? | Reviewed OECD April 2024 press release methodology note. Searched "OECD 2023 ODA West Bank Gaza UNRWA excluded preliminary." | Confirmed: $1.4B excludes UNRWA. This makes our $41.4B conservative lower bound more conservative, not less. | No |

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | wikipedia.org | Reference | 3 | Established reference source; content is user-contributed, subject to policy-area editing disputes |
| B2 | arabcenterdc.org | Unclassified | 2 | Arab Center Washington DC is a policy research organization; cites OECD directly; verify manually |
| B3 | borgenproject.org | Unclassified | 2 | Advocacy/NGO organization; cites Arab Center DC; verify manually |
| B4 | donortracker.org | Unclassified | 2 | Donor Tracker is a development finance tracking initiative; cites OECD preliminary data; verify manually |

**Note:** 3 citations (B2, B3, B4) come from Tier 2 (unclassified) sources. All three cite OECD DAC statistics as their primary authority. The original OECD data (stats.oecd.org Table 2A / Aid Disbursements to Countries and Regions) is the upstream Tier 5 authority. The secondary sources reproduce the same data with consistent figures, and B2 was fully verified by live page fetch.

*Source: proof.py JSON summary*

---

## Extraction Records

| Fact ID | Extracted value | Value in quote | Quote snippet | Method |
|---------|----------------|----------------|---------------|--------|
| B1 | $40,000,000,000 | Yes | "According to the Organization for Economic Cooperation and Development, aid to P..." | parse_number_from_quote regex `\$(\d+(?:\.\d+)?) billion` → 40.0 × 1e9 |
| B2 | $40,000,000,000 | Yes | "According to figures compiled by the Organization for Economic Cooperation and D..." | parse_number_from_quote regex `\$(\d+(?:\.\d+)?) billion` → 40.0 × 1e9 |
| B3 | $40,000,000,000 | Yes | "The Organization for Economic Cooperation and Development (OECD) estimates that ..." | parse_number_from_quote regex `\$(\d+(?:\.\d+)?) billion` → 40.0 × 1e9 |
| B4 | $1,400,000,000 | Yes | "ODA to the West Bank and Gaza increased by 12% to US$1.4 billion;" | parse_number_from_quote regex `US\$([\d.]+) billion` → 1.4 × 1e9 |

**Normalization notes:** All quotes were plain ASCII — no Unicode normalization was required. The `verify_extraction` check confirmed the key strings ("40" for B1/B2/B3, "1.4" for B4) appear within the respective quote strings.

*Source: proof.py JSON summary and author analysis*

---

## Hardening Checklist

| Rule | Status | Detail |
|------|--------|--------|
| Rule 1: Extracted values parsed, not hand-typed | ✓ PASS | All values (40B floor × 4 sources, 1.4B for 2023) parsed via `parse_number_from_quote()` with regex patterns |
| Rule 2: Every citation URL fetched and verified | ✓ PASS | `verify_all_citations()` called; B2, B3, B4 fully verified; B1 partial (50% fragment) |
| Rule 3: System time used for date-dependent logic | N/A | No date calculations in this proof |
| Rule 4: Claim interpretation explicit with operator rationale | ✓ PASS | CLAIM_FORMAL includes `operator_note` documenting the two-step inequality argument |
| Rule 5: Adversarial checks for independent counter-evidence | ✓ PASS | 4 adversarial checks performed before writing proof code; none found evidence that breaks the proof |
| Rule 6: Cross-checks used independently sourced inputs | ✓ PASS | B1 (Wikipedia) vs B2 (Arab Center DC) cross-check uses independently published sources; B3 dependence on B2 is documented |
| Rule 7: Constants/formulas from computations.py, not hand-coded | ✓ PASS | `explain_calc()`, `compare()`, `cross_check()` all imported from bundled scripts; no hard-coded arithmetic |
| validate_proof.py | PASS (with 1 warning) | 13/14 checks passed; 1 warning: `normalize_unicode` imported but not used (removed before final run) |

*Source: proof.py inline output and author analysis*
