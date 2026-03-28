# Audit: You must wait at least 30 minutes after eating before swimming or you will suffer dangerous cramps.

- **Generated**: 2026-03-28
- **Reader summary**: [proof.md](proof.md)
- **Proof script**: [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | swimming after eating |
| Property | whether swimming within 30 minutes of eating causes dangerous cramps |
| Operator | >= |
| Threshold | 3 |
| Proof direction | disprove |
| Operator note | This is a disproof. The claim asserts a causal link: eating + swimming within 30 min = dangerous cramps. 'Dangerous' implies cramps severe enough to cause drowning or serious injury. We seek >= 3 independent authoritative sources that reject this causal claim. The claim is a compound assertion: (1) swimming after eating causes cramps, AND (2) those cramps are dangerous. If either sub-claim is rejected by medical consensus, the overall claim is disproved. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | duke_health | Duke Health: myth that blood diversion causes dangerous cramps is unfounded |
| B2 | uams_health | UAMS Health: no medical evidence supports the myth |
| B3 | britannica | Britannica: science does not support the food-drowning link |
| B4 | ilsf | International Life Saving Federation: no evidence eating before swimming increases drowning risk |
| A1 | — | Verified source count meeting disproof threshold |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified source count meeting disproof threshold | count(verified citations) = 3 | 3 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Duke Health: myth unfounded | Duke Health (Duke University Health System) | [link](https://www.dukehealth.org/blog/myth-or-fact-should-you-wait-swim-after-eating) | "the blood going to your digestive tract after eating steals the blood needed to keep your arms and legs pumping during swimming is unfounded" | verified | full_quote | Tier 2 (unknown) |
| B2 | UAMS Health: no evidence | UAMS Health (University of Arkansas for Medical Sciences) | [link](https://uamshealth.com/medical-myths/do-you-have-to-wait-30-minutes-after-eating-before-swimming/) | "there is no medical evidence to support the myth" | verified | full_quote | Tier 2 (unknown) |
| B3 | Britannica: science doesn't support | Encyclopaedia Britannica | [link](https://www.britannica.com/story/is-it-really-dangerous-to-swim-after-eating) | "The chances of suffering a stomach cramp while swimming are remote, regardless of when the swimmer last ate" | verified | full_quote | Tier 3 (reference) |
| B4 | ILSF: no drowning risk | International Life Saving Federation (ILSF) | [link](https://www.ilsf.org/wp-content/uploads/2018/11/MPS-18-2014-Eating-before-Swimming.pdf) | "eating before swimming does not increase the risk of drowning" | not_found | — | Tier 2 (unknown) |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1 (duke_health)**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B2 (uams_health)**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B3 (britannica)**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4 (ilsf)**
- Status: not_found
- Fetch mode: wayback
- Impact: The ILSF position statement is a corroborating source. The disproof does not depend on B4 — the three verified sources (B1, B2, B3) independently meet the threshold of 3. The ILSF finding is well-known and cited by multiple other verified sources (author analysis).

*Source: proof.py JSON summary; impact analysis is author analysis*

## Computation Traces

```
  Confirmed sources: 3 / 4
  verified source count vs disproof threshold: 3 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Property | Value |
|----------|-------|
| Sources consulted | 4 |
| Sources verified | 3 |
| duke_health | verified |
| uams_health | verified |
| britannica | verified |
| ilsf | not_found |
| Independence note | Sources are from different institutions: Duke University Health System, University of Arkansas for Medical Sciences, Encyclopaedia Britannica, and the International Life Saving Federation. These represent independent medical, academic, and reference organizations. |

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**1. Is there any peer-reviewed study showing that eating before swimming causes dangerous cramps or drowning?**
- Verification performed: Searched for 'eating before swimming cramps dangerous evidence support' across medical databases and general web. Reviewed results from Duke Health, UAMS, Mayo Clinic, Red Cross, Britannica, ILSF, and multiple other medical sources.
- Finding: No peer-reviewed study was found that supports the claim. Multiple sources explicitly state that no documented case of drowning caused by swimming on a full stomach has ever been recorded in medical literature.
- Breaks proof: No

**2. Do any major medical or safety organizations recommend waiting 30 minutes after eating before swimming?**
- Verification performed: Searched for current recommendations from American Academy of Pediatrics, American Red Cross, International Life Saving Federation, and Mayo Clinic regarding eating and swimming.
- Finding: Neither the American Academy of Pediatrics nor the American Red Cross makes any specific recommendation about waiting after eating before swimming. The ILSF explicitly states the recommendation is unfounded. The 2011 Red Cross Scientific Advisory Council review found no evidence of danger.
- Breaks proof: No

**3. Could strenuous competitive swimming after a large meal pose some risk, even if recreational swimming does not?**
- Verification performed: Searched for 'competitive swimming eating cramps exercise intensity' to check if the claim has any validity for extreme exercise conditions.
- Finding: Some sources note mild discomfort (nausea, minor cramps) is possible during vigorous exercise after eating, but characterize this as inconvenient, not dangerous. No source describes exercise-associated cramps after eating as a drowning risk. The claim specifies 'dangerous cramps,' which is not supported even for strenuous swimming.
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | dukehealth.org | unknown | 2 | Unclassified domain — Duke University Health System, affiliated with Duke University School of Medicine. Authoritative medical source despite tier-2 automated classification. |
| B2 | uamshealth.com | unknown | 2 | Unclassified domain — University of Arkansas for Medical Sciences health system. Authoritative academic medical source. |
| B3 | britannica.com | reference | 3 | Established reference source (Encyclopaedia Britannica). |
| B4 | ilsf.org | unknown | 2 | Unclassified domain — International Life Saving Federation, the international authority on water safety. Citation could not be verified (PDF). |

Note: B1, B2, and B4 have tier 2 (unclassified) due to automated domain lookup limitations. Duke Health and UAMS Health are university medical system websites operated by accredited medical schools. ILSF is the recognized international authority on drowning prevention and water safety. All are authoritative sources for this medical claim despite their automated tier classification.

*Source: proof.py JSON summary; tier context is author analysis*

## Extraction Records

For this qualitative/consensus proof, extractions record citation verification status rather than numeric values:

| Fact ID | Value (status) | Countable | Quote snippet |
|---------|---------------|-----------|---------------|
| B1 | verified | Yes | "the blood going to your digestive tract after eating steals the blood needed to " |
| B2 | verified | Yes | "there is no medical evidence to support the myth" |
| B3 | verified | Yes | "The chances of suffering a stomach cramp while swimming are remote, regardless o" |
| B4 | not_found | No | "eating before swimming does not increase the risk of drowning" |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1**: N/A — qualitative consensus proof, no numeric extraction from quotes
- **Rule 2**: All 4 citation URLs fetched and quotes checked; 3 verified, 1 not found (PDF via Wayback)
- **Rule 3**: N/A — no time-dependent logic in this proof
- **Rule 4**: Claim interpretation explicit with operator rationale documenting disproof direction and threshold choice
- **Rule 5**: Three adversarial checks searched for independent counter-evidence supporting the claim; none found
- **Rule 6**: 4 independent sources from different institutions consulted; 3 verified
- **Rule 7**: N/A — qualitative consensus proof, no constants or formulas
- **validate_proof.py result**: PASS with warnings (1 warning: no else-fallback in verdict assignment — cosmetic only, all code paths covered by elif chain)

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
