# Audit: Napoleon Bonaparte stood shorter than the average Frenchman of his era.

- **Generated:** 2026-04-16
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The natural-language claim asserts that Napoleon Bonaparte's height was less than the average height of French men during his lifetime (1769-1821). The formal interpretation operationalizes this as a strict inequality: Napoleon's height in centimeters < average French male height in centimeters for the late 18th/early 19th century.

The key interpretive decision is the unit conversion: Napoleon's height was recorded as "5 pieds 2 pouces" in pre-metric French units. The French pouce was 2.71 cm vs the English inch at 2.54 cm, so "5'2" in French units converts to approximately 167-170 cm — not the 157 cm that a naive English conversion yields.

**Formalization scope:** The natural-language claim maps faithfully to the formal interpretation. "Stood shorter" is operationalized as strict less-than; "his era" is interpreted as the late 18th to early 19th century, matching Napoleon's adult life. No aspects are narrowed or excluded.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Napoleon Bonaparte's height |
| Property | comparison of Napoleon's height to average French male height of his era |
| Operator | < (strictly less than) |
| Operator note | "stood shorter than" interpreted as strict inequality; if equal or greater, claim is DISPROVED |
| Threshold | 3 (minimum verified sources for disproof) |
| Proof direction | disprove |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key / Type | Label |
|----|-----------|-------|
| B1 | britannica | Britannica: Napoleon's height 5'6"-5'7" (1.68-1.7 m) |
| B2 | howstuffworks | HowStuffWorks: Napoleon 169 cm in modern units |
| B3 | history_com | History.com: Napoleon ~1.67 m, above average for early 1800s |
| B4 | britannica_avg | Britannica: most Frenchmen stood 5'2"-5'6" (1.58-1.68 m) |
| A1 | Computed | Napoleon's height from Britannica (conservative, lower bound) |
| A2 | Computed | Average French male height upper bound from Britannica |
| A3 | Computed | Height comparison: Napoleon vs average Frenchman |
| A4 | Computed | Verified source count confirming Napoleon was not shorter |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Napoleon's height (conservative, lower bound) | parse_number_from_quote(B1, lower bound) | 1.68 m |
| A2 | Average French male height upper bound | parse_number_from_quote(B4, upper bound of range) | 1.68 m |
| A3 | Height comparison: Napoleon vs average Frenchman | compare(1.68, '<', 1.68) | False — Napoleon (1.68 m) was NOT shorter than average (1.68 m) |
| A4 | Verified source count | count(verified citations) = 4 | 4 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Napoleon's height estimate | Encyclopaedia Britannica | [link](https://www.britannica.com/story/was-napoleon-short) | "Sources consequently estimate that Napoleon was probably closer to 5'6" or 5'7" (1.68 or 1.7 meters) than to 5'2"." | Verified | full_quote | Reference |
| B2 | Napoleon 169 cm in modern units | HowStuffWorks | [link](https://history.howstuffworks.com/history-vs-myth/napoleon-short.htm) | "At the time of his death, he measured 5 feet, 2 inches, in French units, the equivalent of about 5 feet, 6 inches, (169 centimeters)" | Verified | full_quote | Unclassified |
| B3 | Napoleon ~1.67 m, above average | History.com (A&E Networks) | [link](https://www.history.com/articles/napoleon-complex-short) | "Applying the French measurements of the time, that equals around 1.67 meters, or just under 5'6", which is a little above average for a French man in the early 1800s" | Verified | full_quote | Unclassified |
| B4 | Average French male height range | Encyclopaedia Britannica | [link](https://www.britannica.com/story/was-napoleon-short) | "it was typical in the 19th century, when most Frenchmen stood between 5'2" and 5'6" (1.58 and 1.68 meters) tall" | Verified | full_quote | Reference |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1 (Britannica — Napoleon's height):**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B2 (HowStuffWorks — Napoleon 169 cm):**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B3 (History.com — Napoleon 1.67 m):**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4 (Britannica — average French height):**
- Status: verified
- Method: full_quote
- Fetch mode: live

All 4 citations fully verified via live fetch. No unverified citations.

*Source: proof.py JSON summary*

## Computation Traces

```
Average French height midpoint: (avg_french_lower_m + avg_french_upper_m) / 2 = (1.58 + 1.68) / 2 = 1.6300
Height difference (conservative Napoleon - generous average, cm): (napoleon_conservative - avg_generous) * 100 = (1.68 - 1.68) * 100 = 0.0000
Difference: Britannica Napoleon vs midpoint average (cm): (napoleon_height_m - avg_french_midpoint_m) * 100 = (1.68 - 1.63) * 100 = 5.0000
Difference: HowStuffWorks Napoleon vs midpoint average (cm): (napoleon_height_hsw_m - avg_french_midpoint_m) * 100 = (1.69 - 1.63) * 100 = 6.0000
Difference: History.com Napoleon vs midpoint average (cm): (napoleon_height_hist_m - avg_french_midpoint_m) * 100 = (1.67 - 1.63) * 100 = 4.0000
Claim test: Napoleon height < average French height (conservative): 1.68 < 1.68 = False
Claim test: Napoleon (History.com lowest) < average French (midpoint): 1.67 < 1.63 = False
Source count vs threshold for disproof: 4 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

**Napoleon's height across three independent publishers:**

| Source | Napoleon's Height | Publisher |
|--------|------------------|-----------|
| Britannica (B1) | 1.68 m | Encyclopaedia Britannica |
| HowStuffWorks (B2) | 1.69 m | InfoSpace Holdings |
| History.com (B3) | 1.67 m | A&E Networks |

Cross-check results (relative tolerance 3%):
- Britannica vs HowStuffWorks: 0.59% difference — AGREE
- Britannica vs History.com: 0.60% difference — AGREE
- HowStuffWorks vs History.com: 1.18% difference — AGREE

All three sources agree within a 2 cm range. Sources are from different publishers with no organizational relationship.

**Average French height corroboration:**
Britannica's range (1.58-1.68 m) is consistent with academic anthropometric estimates from military conscription records (Komlos et al.: 162-165 cm). These represent independently published data (same underlying historical records, different publication channels).

**COI assessment:** No conflicts of interest identified. All sources are general-purpose reference or educational publishers with no stake in Napoleon's height.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**1. Is there any credible historical source that measured Napoleon as genuinely short for his era?**
- Verification: Searched for "Napoleon actually short evidence historical measurement"
- Finding: The short myth originates entirely from the French/English inch confusion and British propaganda cartoons by James Gillray. No modern historical source supports the claim that Napoleon was shorter than average.
- Breaks proof: No

**2. Could "his era" refer to a time period when average French height was much taller?**
- Verification: Searched for "average height French men 1770 1800 1820 anthropometric history". Consulted Komlos et al. on French anthropometric history.
- Finding: Anthropometric data consistently places average French male height at 162-165 cm for Napoleon's era. Even the most generous estimate (165 cm) is below Napoleon's measured 167-170 cm.
- Breaks proof: No

**3. Did Napoleon's height change significantly over his lifetime?**
- Verification: Searched for "Napoleon height young man military academy"
- Finding: The nickname "le petit caporal" was a term of endearment, not a height description. No source provides measurements significantly different from 167-170 cm. His Imperial Guard were selected for height (minimum 5'10"), creating an optical illusion.
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Note |
|---------|--------|------|------|
| B1 | britannica.com | Reference | Established reference source |
| B2 | howstuffworks.com | Unclassified | Popular science explainer; article cites National Gallery of Victoria |
| B3 | history.com | Unclassified | A&E Networks history channel; cites primary French sources |
| B4 | britannica.com | Reference | Established reference source |

Note: B2 and B3 are classified as "Unclassified" by the automated credibility checker but are established popular media outlets (HowStuffWorks owned by InfoSpace/System1, History.com by A&E Networks). Both cite primary historical sources and their height figures agree with Britannica's reference data.

*Source: proof.py JSON summary*

## Source Data

| Fact ID | Extracted Value | Value in Quote | Quote Snippet |
|---------|----------------|----------------|---------------|
| B1 | 1.68 m (conservative lower bound) | Yes | "Sources consequently estimate that Napoleon was probably closer to 5'6" or 5'7"..." |
| B2 | 169.0 cm = 1.69 m | Yes | "At the time of his death, he measured 5 feet, 2 inches, in French units, the equ..." |
| B3 | 1.67 m | Yes | "Applying the French measurements of the time, that equals around 1.67 meters, or..." |
| B4 | 1.58-1.68 m range | Yes | "it was typical in the 19th century, when most Frenchmen stood between 5'2" and 5..." |

All values extracted from quotes using `parse_number_from_quote()` — no hand-typed values.

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** All empirical values parsed from quote text using `parse_number_from_quote()` — not hand-typed
- **Rule 2:** All 4 citation URLs fetched and quotes verified (all `verified` via full_quote match)
- **Rule 3:** `date.today()` used for generation date
- **Rule 4:** CLAIM_FORMAL with explicit operator_note documenting unit conversion and threshold interpretation
- **Rule 5:** 3 adversarial checks searched for independent counter-evidence (none found)
- **Rule 6:** 3 independent publishers cross-checked for Napoleon's height; average height corroborated by academic data
- **Rule 7:** All computations use `explain_calc()`, `compare()`, and `cross_check()` from bundled scripts
- **validate_proof.py result:** PASS (16/17 checks passed, 0 issues, 1 warning about verify_extraction — expected for parse_number_from_quote usage)

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.15.0 on 2026-04-16.
