# Audit: Napoleon Bonaparte stood shorter than the average Frenchman of his era.

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Napoleon Bonaparte's height |
| Property | comparison of Napoleon's height to average French male height of his era (late 18th/early 19th century) |
| Operator | `<` |
| Operator note | "stood shorter than" is interpreted as strictly less than: Napoleon's height < average French male height. Napoleon lived 1769-1821; "his era" is interpreted as the late 18th to early 19th century. Heights are compared in centimeters. If Napoleon's height is equal to or greater than the average, the claim is DISPROVED. |
| Threshold | average French male height (~164-165 cm) |
| Measurement note | Napoleon's height was recorded in pre-metric French units (pieds and pouces). The French pouce (inch) was 2.71 cm vs the English inch at 2.54 cm. His recorded "5 pieds 2 pouces" translates to approximately 168-170 cm in modern units, not the 157 cm that a naive English conversion would yield. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | britannica_height | Britannica: Napoleon's height at death (~1.68m) and average French male height in 1820 (~1.65m) |
| B2 | history_com | History.com: Napoleon's height ~1.67m, above average for early 1800s French men |
| B3 | napoleon_series | Napoleon Series: Average French male height 1800-1820 was 164.1 cm |
| B4 | britannica_story | Britannica: Napoleon average or taller, most Frenchmen 5'2"-5'6" |
| A1 | — | Comparison: Napoleon's height vs average French male height |
| A2 | — | Cross-check: Napoleon's height vs average using second source pair |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Comparison: Napoleon's height vs average French male height | compare(napoleon_conservative, '<', avg_french_generous) | Napoleon (1.67m) vs avg French (1.65m): claim_holds=False |
| A2 | Cross-check: Napoleon's height vs average using second source pair | cross_check() on independent sources | Napoleon heights agree (1.68m vs 1.67m), avg heights agree (1.65m vs 1.641m) |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Napoleon's height and avg French height | Encyclopaedia Britannica | https://www.britannica.com/question/Was-Napoleon-short | "At the time of his death in 1821, Napoleon measured about 5 feet 7 inches (roughly 1.68 meters) tall." | partial | fragment (47.4% coverage) | Tier 3 (reference) |
| B2 | Napoleon's height ~1.67m | History.com (A&E Networks) | https://www.history.com/articles/napoleon-complex-short | "Three French sources...said that Napoleon's height was just over 5 pieds 2 pouces..." | partial | aggressive_normalization | Tier 2 (unknown) |
| B3 | Average French male height 164.1 cm | The Napoleon Series | https://www.napoleon-series.org/research/abstract/population/vital/c_heights1.html | "France 1800 - 1820 164.1" | verified | full_quote | Tier 2 (unknown) |
| B4 | Most Frenchmen 5'2"-5'6" | Encyclopaedia Britannica | https://www.britannica.com/story/was-napoleon-short | "most Frenchmen stood between 5'2\" and 5'6\" (1.58 and 1.68 meters) tall" | verified | full_quote | Tier 3 (reference) |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1 — Encyclopaedia Britannica (Napoleon's height):**
- Status: partial
- Method: fragment (coverage_pct: 47.4%)
- Fetch mode: live
- Impact: The data values (1.68m Napoleon, 1.65m average) were independently confirmed on the live page via `verify_data_values()`. The partial quote match is due to WebFetch paraphrasing. The conclusion does not depend solely on this citation — B2 independently confirms Napoleon's height, and B3 independently confirms the French average.

**B2 — History.com (Napoleon's height):**
- Status: partial
- Method: aggressive_normalization
- Fetch mode: live
- Impact: The data value (1.67m) was confirmed on the live page via `verify_data_values()`. The partial quote match is due to the long quote with special characters. B1 independently corroborates Napoleon's height at 1.68m.

**B3 — The Napoleon Series (average French height):**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4 — Encyclopaedia Britannica (French height range):**
- Status: verified
- Method: full_quote
- Fetch mode: live

*Source: proof.py JSON summary; impact analysis is author analysis*

## Computation Traces

```
Average French height (B3) in meters: avg_french_b3_cm / 100 = 164.1 / 100 = 1.6410

--- Cross-checks ---
Napoleon height cross-check (B1 vs B2): 1.68 vs 1.67, diff=0.010000000000000009, tolerance=0.02 -> AGREE
Average French height cross-check (B1 vs B3): 1.65 vs 1.641, diff=0.008999999999999897, tolerance=0.02 -> AGREE

--- Claim evaluation ---
Conservative Napoleon height (lower of two sources): min(napoleon_height_b1, napoleon_height_b2) = min(1.68, 1.67) = 1.6700
Generous average French height (higher of two sources): max(avg_french_b1, avg_french_b3) = max(1.65, 1.641) = 1.6500
Napoleon minus average French male (cm): (napoleon_conservative - avg_french_generous) * 100 = (1.67 - 1.65) * 100 = 2.0000
Napoleon height < average French male height: 1.67 < 1.65 = False
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Cross-check | Values Compared | Agreement | Tolerance |
|-------------|-----------------|-----------|-----------|
| Napoleon height: Britannica vs History.com | 1.68 vs 1.67 | Yes | 0.02m absolute |
| Average French male height: Britannica vs Napoleon Series | 1.65 vs 1.641 | Yes | 0.02m absolute |

Both Napoleon's height and the average French male height are corroborated by independent sources that agree within tolerance. The sources are independently published (Encyclopaedia Britannica, History.com/A&E Networks, and The Napoleon Series are separate editorial organizations).

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**Check 1: Are there credible sources claiming Napoleon was below average?**
- Verification performed: Searched for "Napoleon shorter than average evidence sources claiming Napoleon was genuinely short." Reviewed results from History.com, Britannica, National Geographic, Washington Post, and Wikipedia.
- Finding: No credible source claims Napoleon was below average height. The myth is universally attributed to unit conversion confusion and British propaganda cartoons by James Gillray.
- Breaks proof: No

**Check 2: Could the French measurement conversion be wrong?**
- Verification performed: Checked multiple sources on the French pouce (2.71 cm) vs English inch (2.54 cm) conversion. This is well-established in metrology.
- Finding: The conversion is consistent across all scholarly sources. No credible dispute exists.
- Breaks proof: No

**Check 3: Could the average French male height have been higher than 164-165 cm?**
- Verification performed: Consulted Napoleon Series anthropometric data and Britannica. Academic anthropometric studies by Komlos confirm the 164-165 cm range.
- Finding: No source suggests the average exceeded 166 cm. Even at the generous upper bound of 165 cm, Napoleon (167-170 cm) was still taller.
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | britannica.com | reference | 3 | Established reference source |
| B2 | history.com | unknown | 2 | Unclassified domain — History.com is published by A&E Networks, a well-known media company; editorially credible for historical claims |
| B3 | napoleon-series.org | unknown | 2 | Unclassified domain — The Napoleon Series is a respected research site compiling peer-reviewed anthropometric data; editorially credible |
| B4 | britannica.com | reference | 3 | Established reference source |

Two sources have tier 2 (unclassified). Neither is the sole basis for the disproof — both are corroborated by tier 3 Britannica sources. The disproof holds even using only the tier 3 sources: B4 confirms French men ranged 1.58-1.68m, and B1 confirms Napoleon at ~1.68m.

*Source: proof.py JSON summary; tier interpretation is author analysis*

## Extraction Records

| Fact ID | Extracted Value | Value in Quote | Quote Snippet |
|---------|----------------|----------------|---------------|
| B1_napoleon_height | 1.68 | Yes | data_values['napoleon_height_m'] |
| B1_avg_french | 1.65 | Yes | data_values['avg_french_height_m'] |
| B2_napoleon_height | 1.67 | Yes | data_values['napoleon_height_m'] |
| B3_avg_french_cm | 164.1 | Yes | data_values['avg_french_height_cm'] |

All values were extracted from `data_values` strings using `parse_number_from_quote()` and verified on their respective source pages via `verify_data_values()`. All returned `found: true` with `fetch_mode: live`.

*Source: proof.py JSON summary; extraction method narrative is author analysis*

## Hardening Checklist

- **Rule 1:** Every empirical value parsed from data_values strings via `parse_number_from_quote()`, not hand-typed
- **Rule 2:** Every citation URL fetched and quote checked via `verify_all_citations()`; data values confirmed via `verify_data_values()`
- **Rule 3:** N/A — this proof is not time-dependent (historical heights are fixed)
- **Rule 4:** Claim interpretation explicit with operator rationale in `CLAIM_FORMAL` with `operator_note` and `measurement_note`
- **Rule 5:** Three adversarial checks searched for independent counter-evidence; none found
- **Rule 6:** Cross-checks used independently sourced inputs — Napoleon's height from 2 sources (Britannica, History.com), average French height from 2 sources (Britannica, Napoleon Series)
- **Rule 7:** All computations via `compare()`, `explain_calc()`, and `cross_check()` from computations.py
- **validate_proof.py result:** PASS with warnings (unused imports removed after initial validation)

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
