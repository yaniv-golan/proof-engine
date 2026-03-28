# Audit: The Great Wall of China is the only man-made object visible from space with the naked eye

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | The Great Wall of China |
| Property | number of independent authoritative sources confirming the claim is false |
| Operator | >= |
| Threshold | 3 |
| Proof direction | disprove |
| Operator note | This is a compound claim: (SC1) the Great Wall is visible from space with the naked eye, AND (SC2) it is the ONLY man-made object so visible. For disproof, we need authoritative sources confirming EITHER sub-claim is false. In fact, both sub-claims are false. 'Space' is interpreted as low Earth orbit (~200-400 km altitude, e.g. ISS), the most favorable interpretation for the claim. Threshold of 3 sources required for disproof. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | nasa_great_wall | NASA official statement: wall not visible without high-powered lenses |
| B2 | sci_am_astronaut | Scientific American: astronaut Jeffrey Hoffman confirms wall not visible |
| B3 | britannica_wall | Britannica: Great Wall not visible with naked eye from space |
| B4 | wikipedia_structures | Wikipedia: highways, dams, and cities visible from space without magnification |
| A1 | — | Verified source count for disproof |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified source count for disproof | count(verified citations) = 4 | 4 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | NASA official statement | NASA | [nasa.gov](https://www.nasa.gov/image-article/great-wall/) | "Despite myths to the contrary, the wall isn't visible from the moon, and is difficult or impossible to see from Earth orbit without the high-powered lenses used for this photo." | partial | aggressive_normalization | Tier 5 (government) |
| B2 | Astronaut Jeffrey Hoffman | Scientific American | [scientificamerican.com](https://www.scientificamerican.com/article/is-chinas-great-wall-visible-from-space/) | "I have spent a lot of time looking at the Earth from space, including numerous flights over China, and I never saw the wall" | verified | full_quote | Tier 3 (major_news) |
| B3 | Great Wall not visible | Encyclopaedia Britannica | [britannica.com](https://www.britannica.com/question/Can-you-see-the-Great-Wall-of-China-from-space) | "You typically can't see the Great Wall of China from space" | verified | full_quote | Tier 3 (reference) |
| B4 | Other structures visible | Wikipedia | [wikipedia.org](https://en.wikipedia.org/wiki/Artificial_structures_visible_from_space) | "Artificial structures visible from space without magnification include highways, dams, and cities" | verified | full_quote | Tier 3 (reference) |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1 (NASA):**
- Status: partial
- Method: aggressive_normalization (fragment_match, 6 words)
- Fetch mode: live
- Impact: The NASA source was verified via fragment matching rather than full quote. However, the disproof does not depend solely on this source — 3 other fully verified sources independently confirm both sub-claims are false.

*Source: proof.py JSON summary; impact is author analysis*

**B2 (Scientific American):**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B3 (Britannica):**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4 (Wikipedia):**
- Status: verified
- Method: full_quote
- Fetch mode: live

*Source: proof.py JSON summary*

## Computation Traces

```
  Confirmed sources: 4 / 4
  verified source count vs threshold for disproof: 4 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Metric | Value |
|--------|-------|
| Sources consulted | 4 |
| Sources verified | 4 (3 full, 1 partial) |
| Independence note | Sources are from different institutions: NASA (government space agency), Scientific American (science journalism), Encyclopaedia Britannica (reference), and Wikipedia (encyclopedic summary of multiple sources). Each represents an independent editorial decision to publish the same conclusion. |

Source verification statuses:
- nasa_great_wall: partial
- sci_am_astronaut: verified
- britannica_wall: verified
- wikipedia_structures: verified

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**1. Are there credible sources that say the Great Wall IS visible from space with the naked eye?**
- Verification performed: Searched for 'Great Wall of China visible from space confirmed' and 'astronauts who saw Great Wall from space'. Found that astronauts Eugene Cernan and Ed Lu reported seeing the wall under specific lighting conditions (low sun angle creating shadows), but these observations are disputed and may involve camera-assisted viewing. NASA's official position remains that it is not visible with the naked eye.
- Finding: A small number of astronauts claim to have seen the wall under very specific lighting conditions, but these reports are disputed. China's first astronaut Yang Liwei could not see it, and Canadian astronaut Chris Hadfield explicitly stated it is not visible. NASA's official page states it is 'difficult or impossible to see from Earth orbit without high-powered lenses.' The scientific consensus is clearly against visibility.
- Breaks proof: No

**2. Is there any basis for the claim that no OTHER man-made objects are visible from space?**
- Verification performed: Searched for 'only man-made structure visible from space' and reviewed multiple sources. Every credible source lists numerous structures visible from low Earth orbit including highways, cities at night, dams, greenhouses in Almeria Spain, airports, and the Bingham Canyon Mine.
- Finding: No credible source supports the claim that the Great Wall is the only visible structure. Multiple man-made structures are routinely visible from space, making this sub-claim completely false.
- Breaks proof: No

**3. Does the definition of 'space' matter — could the claim be true at some altitude?**
- Verification performed: Reviewed definitions of 'space' (Karman line at 100km, ISS at ~400km, Moon at ~384,000km). At no altitude is the Great Wall the only visible structure. At ISS altitude, many structures are visible. At lunar distance, NO man-made structures are visible at all, including the wall.
- Finding: At any reasonable definition of 'space', the claim fails. At low orbit: many structures are visible, the wall generally is not. At lunar distance: nothing man-made is visible.
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | nasa.gov | government | 5 | Government domain (.gov) |
| B2 | scientificamerican.com | major_news | 3 | Major news organization |
| B3 | britannica.com | reference | 3 | Established reference source |
| B4 | wikipedia.org | reference | 3 | Established reference source |

*Source: proof.py JSON summary*

## Extraction Records

For this qualitative consensus proof, extractions record citation verification status per source:

| Fact ID | Value (status) | Countable | Quote Snippet |
|---------|---------------|-----------|---------------|
| B1 | partial | Yes | "Despite myths to the contrary, the wall isn't visible from the moon, and is diff..." |
| B2 | verified | Yes | "I have spent a lot of time looking at the Earth from space, including numerous f..." |
| B3 | verified | Yes | "You typically can't see the Great Wall of China from space" |
| B4 | verified | Yes | "Artificial structures visible from space without magnification include highways,..." |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A — qualitative consensus proof, no numeric value extraction
- **Rule 2:** Every citation URL fetched and quote checked via `verify_all_citations()`
- **Rule 3:** System time used via `date.today()` for generation date
- **Rule 4:** Claim interpretation explicit with operator rationale in `operator_note`; compound claim decomposed into SC1 and SC2
- **Rule 5:** Three adversarial checks searched for counter-evidence: astronaut sightings, alternative definitions of "space", and support for the "only" claim
- **Rule 6:** 4 independent sources from different institutions (NASA, Scientific American, Britannica, Wikipedia)
- **Rule 7:** `compare()` used for claim evaluation; no hard-coded constants
- **validate_proof.py result:** PASS with warnings (1 warning: no else branch in verdict assignment — cosmetic)

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
