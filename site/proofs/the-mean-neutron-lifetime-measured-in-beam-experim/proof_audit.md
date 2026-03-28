# Audit: The mean neutron lifetime measured in beam experiments is more than 1 second shorter than the lifetime obtained from ultracold-neutron bottle experiments

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | neutron lifetime discrepancy between beam and bottle experiments |
| Property | difference defined as (beam lifetime) minus (bottle lifetime) |
| Operator | < |
| Threshold | -1.0 |
| Unit | seconds |
| Operator note | The claim asserts beam < bottle by more than 1 second. Formally: (beam_lifetime - bottle_lifetime) < -1.0. If the difference is positive (beam > bottle) or within [-1, 0], the claim is FALSE. We use the world-average values reported in the physics literature for each method. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | doe_source | U.S. DOE: beam lifetime 887.7 +/- 2.2 s, bottle lifetime 878.5 +/- 0.8 s |
| B2 | quanta_source | Quanta Magazine: beam ~14 min 48 s, bottle ~14 min 39 s, gap ~9 s |
| A1 | — | Computed difference (beam - bottle) from DOE values |
| A2 | — | Computed difference (beam - bottle) from Quanta values |
| A3 | — | Claim evaluation: is (beam - bottle) < -1.0? |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Computed difference (beam - bottle) from DOE values | explain_calc('beam_lifetime - bottle_lifetime') | 9.200000000000045 s |
| A2 | Computed difference (beam - bottle) from Quanta values | Quanta Magazine reported gap | 9.0 s (beam > bottle) |
| A3 | Claim evaluation: is (beam - bottle) < -1.0? | compare(difference, '<', -1.0) | False |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | DOE beam & bottle values | U.S. Department of Energy, Office of Science | [energy.gov](https://www.energy.gov/science/articles/mystery-neutron-lifetime) | "One method measures it as 887.7 seconds, plus or minus 2.2 seconds." | verified | full_quote | Tier 5 (government) |
| B1 (bottle) | DOE bottle value | U.S. Department of Energy, Office of Science | [energy.gov](https://www.energy.gov/science/articles/mystery-neutron-lifetime) | "Another method measures it as 878.5 seconds, plus or minus 0.8 second." | verified | full_quote | Tier 5 (government) |
| B2 | Quanta gap report | Quanta Magazine | [quantamagazine.org](https://www.quantamagazine.org/neutron-lifetime-puzzle-deepens-but-no-dark-matter-seen-20180213/) | "The gap between the world-average bottle and beam measurements has only grown slightly — to nine seconds" | verified | full_quote | Tier 2 (unclassified) |

*Source: proof.py JSON summary*

## Citation Verification Details

### B1 (doe_source — beam value)
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B1 (doe_source_bottle — bottle value)
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B2 (quanta_source — gap report)
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

*Source: proof.py JSON summary*

## Computation Traces

```
B1_beam: Parsed '887.7' -> 887.7
B1_bottle: Parsed '878.5' -> 878.5
[✓] B1_beam: extracted 887.7 from quote
[✓] B1_bottle: extracted 878.5 from quote
A1: beam minus bottle (DOE): beam_lifetime - bottle_lifetime = 887.7 - 878.5 = 9.2000
A2: Quanta reports gap of 9.0 s (beam > bottle)
DOE difference vs Quanta gap: 9.200000000000045 vs 9.0, diff=0.20000000000004547, tolerance=0.5 -> AGREE
A3: Is (beam - bottle) < -1.0?: 9.200000000000045 < -1.0 = False
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Cross-check | Values compared | Agreement |
|-------------|-----------------|-----------|
| DOE computed difference vs Quanta reported gap | 9.2 s vs 9.0 s | Yes (within 0.5 s tolerance) |

The DOE source (tier 5/government) provides explicit numerical values for both beam (887.7 s) and bottle (878.5 s) lifetimes, yielding a computed difference of +9.2 s. Quanta Magazine independently reports the gap as "nine seconds" with beam being longer. These agree within 0.2 s. Both sources are independently published — the DOE article references the experimental physics community's consensus; Quanta Magazine is an independent science journalism outlet.

*Source: proof.py JSON summary + author analysis*

## Adversarial Checks (Rule 5)

### Check 1: Alternative definitions of "beam experiment"
- **Question:** Could the claim be using a non-standard definition where 'beam' refers to a different measurement technique?
- **Verification performed:** Searched web for 'neutron lifetime beam experiment definition method'. All sources consistently define beam experiments as measuring decay products (protons) from cold neutron beams, yielding ~887-888 s. Bottle experiments trap ultracold neutrons and count survivors, yielding ~878-879 s. No alternative definition found.
- **Finding:** The two methods are universally defined consistently across all sources. Beam always gives the longer lifetime.
- **Breaks proof:** No

### Check 2: Any beam result below bottle average
- **Question:** Is there any recent measurement where a beam experiment produced a shorter lifetime than the bottle average?
- **Verification performed:** Searched web for 'neutron lifetime beam experiment new result 2024 2025'. Checked PDG 2024 data. The most recent beam measurement is YUE 2013 at 887.7 +/- 1.2 s. No beam experiment has ever produced a result below the bottle average of ~878 s. The BL2 experiment at NIST is ongoing but has not published a result contradicting this.
- **Finding:** No beam experiment result is shorter than the bottle average. The discrepancy has persisted since the 2000s with beam consistently higher.
- **Breaks proof:** No

### Check 3: Alternative reading of "shorter"
- **Question:** Could 'shorter' in the claim refer to something other than the numerical value (e.g., measurement duration)?
- **Verification performed:** Linguistic analysis of the claim. 'The mean neutron lifetime measured in beam experiments is more than 1 second shorter' unambiguously refers to the numerical value of the measured lifetime.
- **Finding:** The claim clearly refers to the measured lifetime value, not the experiment duration. No alternative reading is plausible.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | energy.gov | government | 5 | Government domain (.gov) |
| B2 | quantamagazine.org | unknown | 2 | Unclassified domain — verify source authority manually |

Quanta Magazine (tier 2) is a well-regarded science journalism publication funded by the Simons Foundation, known for accurate science reporting. However, the disproof does not depend solely on it — the U.S. DOE source (tier 5) alone establishes both the beam and bottle values.

*Source: proof.py JSON summary + author analysis*

## Extraction Records

| Fact ID | Extracted Value | Value in Quote | Quote Snippet |
|---------|-----------------|----------------|---------------|
| B1_beam | 887.7 | Yes | One method measures it as 887.7 seconds, plus or minus 2.2 seconds. |
| B1_bottle | 878.5 | Yes | Another method measures it as 878.5 seconds, plus or minus 0.8 second. |
| B2_gap | 9.0 | Yes | The gap between the world-average bottle and beam measurements has only grown sl... |

Extraction method: `parse_number_from_quote()` with regex `r"([\d.]+)\s+seconds"` for numerical values. The Quanta gap was extracted by word-to-number mapping of "nine" to 9. All extracted values confirmed present in their source quotes via `verify_extraction()`.

*Source: proof.py JSON summary + author analysis*

## Hardening Checklist

- **Rule 1:** Every empirical value parsed from quote text using `parse_number_from_quote()`, not hand-typed
- **Rule 2:** Every citation URL fetched live and quote verified — all 3 citations returned `verified` with `full_quote` method
- **Rule 3:** Not applicable (no date-dependent computation), but `date.today()` used for generation date
- **Rule 4:** Claim interpretation explicit with `CLAIM_FORMAL` dict including `operator_note` explaining the `<` operator and -1.0 threshold
- **Rule 5:** Three adversarial checks performed: alternative definitions, recent contradicting results, and alternative readings of "shorter"
- **Rule 6:** Two independent sources (DOE tier 5, Quanta tier 2) provide agreeing values for the beam-bottle gap (9.2 s vs 9 s)
- **Rule 7:** Computation uses `explain_calc()` and `compare()` from bundled `computations.py`; `cross_check()` for source agreement
- **validate_proof.py result:** PASS with warnings (1 unused import removed after initial validation)

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
