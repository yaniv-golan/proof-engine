# Audit: Lightning never strikes the same place twice.

- **Generated**: 2026-03-28
- **Reader summary**: [proof.md](proof.md)
- **Proof script**: [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Lightning |
| Property | whether lightning can strike the same location more than once |
| Operator | >= |
| Threshold | 3 |
| Proof direction | disprove |
| Operator note | The claim asserts lightning NEVER strikes the same place twice — an absolute universal negative. To DISPROVE this, we need authoritative sources confirming that lightning DOES strike the same place repeatedly. A threshold of 3 independent authoritative sources confirming repeated strikes is used. The claim is disproved if >= 3 sources confirm it is false. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | nws_myths | NWS Lightning Myths page: lightning often strikes same place repeatedly |
| B2 | nssl_faq | NOAA NSSL FAQ: lightning does hit the same spot more than once |
| B3 | nasa_spinoff | NASA Spinoff: lightning often strikes the same place twice |
| B4 | britannica | Britannica: lightning can and will strike the same place twice |
| A1 | — | Verified source count confirming claim is false |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified source count confirming claim is false | count(verified citations) = 4 | 4 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | NWS Lightning Myths page | National Weather Service (NWS) | https://www.weather.gov/safety/lightning-myths | "Lightning often strikes the same place repeatedly, especially if it's a tall, pointy, isolated object. The Empire State Building is hit an average of 23 times a year" | partial | aggressive_normalization | Tier 5 (government) |
| B2 | NOAA NSSL FAQ | NOAA National Severe Storms Laboratory (NSSL) | https://www.nssl.noaa.gov/education/svrwx101/lightning/faq/ | "Lightning does hit the same spot (or almost the same spot) more than once, contrary to folk wisdom" | verified | full_quote | Tier 5 (government) |
| B3 | NASA Spinoff | NASA Spinoff | https://spinoff.nasa.gov/Spinoff2005/ps_3.html | "Contrary to popular misconception, lightning often strikes the same place twice" | verified | full_quote | Tier 5 (government) |
| B4 | Britannica | Encyclopaedia Britannica | https://www.britannica.com/story/can-lightning-strike-the-same-place-twice | "lightning can and will strike the same place twice, whether it be during the same storm or even centuries later" | verified | full_quote | Tier 3 (reference) |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1 (NWS Lightning Myths)**
- Status: partial
- Method: aggressive_normalization (fragment_match, 8 words)
- Fetch mode: live
- Impact: The NWS source was verified via aggressive normalization rather than full quote match, likely due to HTML rendering on the .gov page. This does not affect the disproof — the three remaining sources (B2, B3, B4) are independently fully verified and exceed the threshold of 3 on their own.

*Source: proof.py JSON summary; impact is author analysis*

**B2 (NOAA NSSL FAQ)**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B3 (NASA Spinoff)**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4 (Britannica)**
- Status: verified
- Method: full_quote
- Fetch mode: live

*Source: proof.py JSON summary*

## Computation Traces

```
  Confirmed sources: 4 / 4
  verified source count vs threshold: 4 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Source | Institution | Status | Independent? |
|--------|-------------|--------|--------------|
| B1 (NWS) | National Weather Service | partial | Yes (NOAA entity, separate editorial from NSSL) |
| B2 (NSSL) | NOAA National Severe Storms Laboratory | verified | Yes (NOAA entity, separate editorial from NWS) |
| B3 (NASA) | NASA | verified | Yes (fully independent federal agency) |
| B4 (Britannica) | Encyclopaedia Britannica | verified | Yes (independent private encyclopedia) |

All four sources consulted. Four confirmed (3 verified + 1 partial). Sources span 3 fully independent organizations (NOAA, NASA, Britannica); NWS and NSSL are both NOAA entities but have separate missions and publication pipelines.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**Check 1: Is there any scientific evidence supporting the claim?**
- Verification performed: Searched for "lightning never strikes same place twice any truth defense of saying". Reviewed results from Britannica, NWS, NOAA, Merriam-Webster, and multiple science education sites.
- Finding: No scientific source supports the literal claim. Every authoritative meteorological source explicitly identifies it as a myth. The phrase is recognized only as a metaphorical/idiomatic expression (Merriam-Webster defines it as meaning "an unusual event is not likely to happen again to the same person or in the same place").
- Breaks proof: No

**Check 2: Could the claim be interpreted more charitably?**
- Verification performed: Analyzed whether lightning could be said to never strike the exact same molecular coordinates. Reviewed NSSL FAQ on lightning strike precision.
- Finding: Even under the most charitable interpretation, the claim fails. The NSSL notes lightning hits "the same spot (or almost the same spot)" repeatedly. Lightning channels are meters wide, and the same structures are struck thousands of times over their lifetimes.
- Breaks proof: No

**Check 3: Are the sources independently authored?**
- Verification performed: Checked provenance of each source: NWS (federal weather safety page), NSSL (federal severe storms research lab), NASA (space technology spinoff article), Britannica (independent encyclopedia). Each is authored by a different organization with independent editorial processes.
- Finding: All four sources are from different institutions with independent editorial authority. NWS and NSSL are both NOAA entities but have separate missions and publication pipelines. NASA and Britannica are fully independent.
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | weather.gov | government | 5 | Government domain (.gov) |
| B2 | noaa.gov | government | 5 | Government domain (.gov) |
| B3 | nasa.gov | government | 5 | Government domain (.gov) |
| B4 | britannica.com | reference | 3 | Established reference source |

All sources are tier 3 or above. Three of four are tier 5 government sources.

*Source: proof.py JSON summary*

## Extraction Records

For this qualitative consensus proof, extractions record citation verification status per source rather than numeric values.

| Fact ID | Value (verification status) | Countable | Quote Snippet |
|---------|----------------------------|-----------|---------------|
| B1 | partial | Yes | "Lightning often strikes the same place repeatedly, especially if it's a tall, po..." |
| B2 | verified | Yes | "Lightning does hit the same spot (or almost the same spot) more than once, contr..." |
| B3 | verified | Yes | "Contrary to popular misconception, lightning often strikes the same place twice" |
| B4 | verified | Yes | "lightning can and will strike the same place twice, whether it be during the sam..." |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1**: N/A — qualitative consensus proof, no numeric extraction from quotes
- **Rule 2**: All 4 citation URLs fetched and quotes checked; 3 fully verified, 1 partial (aggressive normalization)
- **Rule 3**: `date.today()` used for generation date
- **Rule 4**: CLAIM_FORMAL includes operator_note explaining the universal negative interpretation and threshold choice
- **Rule 5**: Three adversarial checks performed: searched for supporting evidence, tested charitable interpretations, verified source independence
- **Rule 6**: Four sources from 4 different institutions (NWS, NSSL, NASA, Britannica) with independent editorial authority
- **Rule 7**: N/A — no numeric constants or formulas; `compare()` used for threshold evaluation
- **validate_proof.py result**: PASS with warnings (14/15 checks passed, 0 issues, 1 warning about else branch in verdict — safe since claim_holds is always a bool)

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
