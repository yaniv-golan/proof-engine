# Audit: The average person swallows eight spiders per year while sleeping.

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | the average person |
| Property | number of spiders swallowed per year while sleeping |
| Operator | >= |
| Threshold | 3 (verified sources confirming claim is false) |
| Proof direction | disprove |
| Operator note | The claim asserts a specific rate of 8 spiders/year. To disprove it, we seek authoritative sources confirming the claim is a myth with no scientific basis. Using the qualitative consensus disproof template: if >= 3 independent authoritative sources confirm the claim is false, verdict is DISPROVED. Threshold of 3 chosen because this is a widely-addressed myth with many authoritative sources available. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | scientific_american | Scientific American: spider-swallowing myth debunked |
| B2 | burke_museum | Burke Museum (arachnology dept): no formal record of spider ingestion |
| B3 | britannica | Britannica: we swallow no spiders at all |
| B4 | sleep_foundation | Sleep Foundation: no proof spiders crawl into mouths |
| A1 | — | Verified source count meets disproof threshold |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified source count meets disproof threshold | count(verified citations) = 4 | 4 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Scientific American: spider-swallowing myth debunked | Scientific American | [link](https://www.scientificamerican.com/article/fact-or-fiction-people-swallow-8-spiders-a-year-while-they-sleep1/) | "The myth flies in the face of both spider and human biology, which makes it highly unlikely that a spider would ever end up in your mouth." | verified | full_quote | Tier 3 (major_news) |
| B2 | Burke Museum (arachnology dept): no formal record of spider ingestion | Burke Museum — Arachnology & Entomology | [link](https://www.burkemuseum.org/collections-and-research/biology/arachnology-and-entomology/spider-myths/myth-you-swallow-spiders) | "For a sleeping person to swallow even one live spider would involve so many highly unlikely circumstances that for practical purposes we can rule out the possibility." | verified | full_quote | Tier 2 (unknown) |
| B3 | Britannica: we swallow no spiders at all | Encyclopaedia Britannica | [link](https://www.britannica.com/story/do-we-really-swallow-spiders-in-our-sleep) | "The reality, however, is quite different: we swallow no spiders at all." | verified | full_quote | Tier 3 (reference) |
| B4 | Sleep Foundation: no proof spiders crawl into mouths | Sleep Foundation | [link](https://www.sleepfoundation.org/sleep-faqs/how-many-spiders-do-you-eat-in-your-sleep) | "There is no proof that spiders crawl into people's mouths while they are sleeping." | verified | full_quote | Tier 2 (unknown) |

*Source: proof.py JSON summary*

## Citation Verification Details

### B1 — Scientific American
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B2 — Burke Museum
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B3 — Britannica
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B4 — Sleep Foundation
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

*Source: proof.py JSON summary*

## Computation Traces

```
verified source count vs disproof threshold: 4 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Check | Sources Consulted | Sources Verified | Agreement |
|-------|-------------------|------------------|-----------|
| Multiple independent sources consulted | 4 | 4 | All sources independently reject the claim |

**Independence note:** Sources are from different institutions: Scientific American (science journalism), Burke Museum (academic museum / arachnology), Encyclopaedia Britannica (reference encyclopedia), and Sleep Foundation (health/sleep nonprofit). Each independently debunks the claim.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

### Check 1: Is there any scientific study that confirms people swallow spiders in their sleep?
- **Verification performed:** Searched for: 'swallow spiders sleep scientific study evidence confirmed'. Reviewed results from Scientific American, Burke Museum, Britannica, Sleep Foundation, HowStuffWorks, Discover Magazine, and ScienceDirect. Also found a ScienceDirect paper titled 'Believing that Humans Swallow Spiders in Their Sleep: False Beliefs as Side Effects of the Processes that Support Accurate Knowledge' — which studies the myth's persistence, not its truth.
- **Finding:** No scientific study, medical record, or sleep research study has ever documented a case of a person swallowing a spider while sleeping. Every source found unanimously debunks the claim.
- **Breaks proof:** No

### Check 2: Could the claim have a legitimate scientific origin that was later misrepresented?
- **Verification performed:** Searched for the origin of the claim. Multiple sources (Snopes, Britannica, Scientific American) trace it to a 1993 PC Professional magazine column by Lisa Holst, who deliberately included it as an example of ridiculous 'facts' that people would uncritically believe. However, Snopes later noted that the Lisa Holst origin story itself may be apocryphal — the magazine article has never been independently located.
- **Finding:** Regardless of whether the Lisa Holst origin is real, no legitimate scientific study has ever supported the claim. The origin is either a deliberate fabrication to illustrate gullibility, or an untraceable piece of folklore. Neither constitutes scientific evidence.
- **Breaks proof:** No

### Check 3: Is it biologically plausible that spiders would enter a sleeping person's mouth?
- **Verification performed:** Reviewed entomological explanations from Scientific American and Burke Museum. Rod Crawford (Burke Museum arachnologist) and other experts explain that spiders are sensitive to vibrations from breathing, heartbeat, and snoring; sleeping humans are warm, moist, and create air currents — all things spiders avoid. Spiders have no biological incentive to enter a mouth.
- **Finding:** Spider biology and behavior make it extremely unlikely a spider would approach a sleeping human's mouth. Vibrations, warmth, moisture, and air currents all deter spiders. Experts consider it practically impossible.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | scientificamerican.com | major_news | 3 | Major news organization |
| B2 | burkemuseum.org | unknown | 2 | Unclassified domain — verify source authority manually |
| B3 | britannica.com | reference | 3 | Established reference source |
| B4 | sleepfoundation.org | unknown | 2 | Unclassified domain — verify source authority manually |

**Note on tier 2 sources:** Burke Museum (B2) is the University of Washington's natural history museum; its spider myths page is authored by Rod Crawford, a professional arachnologist. Sleep Foundation (B4) is a well-known health nonprofit with medically reviewed content. Both are authoritative in their domains despite being unclassified by the automated credibility engine. The disproof does not depend solely on these sources — Scientific American (B1) and Britannica (B3), both tier 3, independently confirm the claim is false.

*Source: proof.py JSON summary; tier 2 impact note is author analysis*

## Extraction Records

For this qualitative consensus disproof, extractions record citation verification status per source rather than numeric values.

| Fact ID | Value (status) | Countable | Quote Snippet |
|---------|----------------|-----------|---------------|
| B1 | verified | Yes | "The myth flies in the face of both spider and human biology, which makes it high..." |
| B2 | verified | Yes | "For a sleeping person to swallow even one live spider would involve so many high..." |
| B3 | verified | Yes | "The reality, however, is quite different: we swallow no spiders at all." |
| B4 | verified | Yes | "There is no proof that spiders crawl into people's mouths while they are sleepin..." |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A — qualitative consensus proof, no numeric value extraction
- **Rule 2:** All 4 citation URLs fetched and quotes verified (all full_quote matches)
- **Rule 3:** N/A — no date-dependent logic
- **Rule 4:** CLAIM_FORMAL includes operator_note explaining disproof threshold and interpretation
- **Rule 5:** Three adversarial checks performed: searched for supporting scientific evidence, investigated claim origin, and assessed biological plausibility. No counter-evidence found.
- **Rule 6:** Four independent sources from different institutions (science journalism, academic museum, reference encyclopedia, health nonprofit)
- **Rule 7:** N/A — qualitative proof, no constants or formulas
- **validate_proof.py result:** PASS with warnings (14/15 checks passed, 0 issues, 1 warning about missing else branch in verdict assignment)

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
