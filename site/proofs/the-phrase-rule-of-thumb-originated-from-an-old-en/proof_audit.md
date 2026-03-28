# Audit: The phrase "rule of thumb" originated from an old English law that allowed a man to beat his wife with a stick no thicker than his thumb.

- Generated: 2026-03-28
- Reader summary: [proof.md](proof.md)
- Proof script: [proof.py](proof.py)

## Claim Specification

Source: proof.py JSON summary `claim_formal`.

| Field | Value |
|-------|-------|
| Subject | The phrase "rule of thumb" |
| Property | etymological origin linked to a specific English law permitting wife-beating |
| Operator | >= |
| Threshold | 3 |
| Proof direction | disprove |
| Operator note | This is a compound claim: (1) an old English law existed permitting a man to beat his wife with a stick no thicker than his thumb, AND (2) this law is the origin of the phrase "rule of thumb." Both sub-claims must be true for the claim to hold. We attempt to disprove by finding >= 3 independent authoritative sources that reject these sub-claims. Sources must be from different institutions/publications. |

## Fact Registry

Source: proof.py JSON summary `fact_registry`.

| ID | Key | Label |
|----|-----|-------|
| B1 | wikipedia | Wikipedia: no such law ever existed |
| B2 | phrases_org | Phrases.org.uk: no printed records associate phrase with domestic violence until 1970s |
| B3 | uoregon | U. Oregon legal scholar: no truth in the legend |
| B4 | allthatsinteresting | All That's Interesting: no evidence Buller said anything of the sort |
| A1 | — | Verified source count rejecting the claim |

## Full Evidence Table

### Type A (Computed) Facts

Source: proof.py JSON summary `fact_registry` (A-type entries).

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified source count rejecting the claim | count(verified citations) = 4 | 4 |

### Type B (Empirical) Facts

Source: proof.py JSON summary `citations`.

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | No such law ever existed | Wikipedia — Rule of thumb | https://en.wikipedia.org/wiki/Rule_of_thumb | "A modern folk etymology holds that the phrase is derived from the maximum width of a stick allowed for wife-beating under English common law, but no such law ever existed." | verified | full_quote | Tier 3 (reference) |
| B2 | No printed records until 1970s | Phrases.org.uk — Rule of Thumb meaning and origin | https://phrases.org.uk/meanings/rule-of-thumb.html | "Despite the phrase being in common use since the 17th century and appearing many thousands of times in print, there are no printed records that associate it with domestic violence until the 1970s" | verified | full_quote | Tier 2 (unknown) |
| B3 | No truth in the legend | University of Oregon — Rule of Thumb essay | https://dynamic.uoregon.edu/jjf/essays/ruleofthumb.html | "there is probably no truth whatever in the legend that he was permitted to beat her with a stick no thicker than his thumb" | verified | full_quote | Tier 4 (academic) |
| B4 | No evidence Buller said it | All That's Interesting — Rule of Thumb Origin | https://allthatsinteresting.com/rule-of-thumb-origin | "There is no evidence that Buller actually said anything of the sort, but he was mocked in the press." | verified | full_quote | Tier 2 (unknown) |

## Citation Verification Details

Source: proof.py JSON summary `citations`.

**B1 (Wikipedia):**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B2 (Phrases.org.uk):**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B3 (University of Oregon):**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4 (All That's Interesting):**
- Status: verified
- Method: full_quote
- Fetch mode: live

## Computation Traces

Source: proof.py inline output (execution trace).

```
  Confirmed sources: 4 / 4
  verified source count vs threshold: 4 >= 3 = True
```

## Independent Source Agreement (Rule 6)

Source: proof.py JSON summary `cross_checks`.

| Metric | Value |
|--------|-------|
| Sources consulted | 4 |
| Sources verified | 4 |
| wikipedia | verified |
| phrases_org | verified |
| uoregon | verified |
| allthatsinteresting | verified |

**Independence note:** Sources are from different institutions: Wikimedia Foundation (Wikipedia), Gary Martin's Phrases.org.uk, University of Oregon academic essay, All That's Interesting. While they cite overlapping primary research, they are independently published and maintained.

## Adversarial Checks (Rule 5)

Source: proof.py JSON summary `adversarial_checks`.

**1. Was there ever an actual English law specifying a thumb-width stick for wife-beating?**
- Verification performed: Searched for 'rule of thumb wife beating law evidence historical support Buller ruling'. Reviewed Wikipedia, Phrases.org.uk, University of Oregon essay, and allthatsinteresting.com. Also reviewed the Sir Francis Buller / Judge Thumb incident of 1782.
- Finding: No such law was ever codified in English common law. Sir Francis Buller was rumored in 1782 to have stated a husband could beat his wife with a stick no wider than his thumb, but there is no record he actually made this ruling. He was satirized as 'Judge Thumb.' Some 19th-century American courts referenced a supposed common-law doctrine, but legal scholars (including Henry Ansgar Kelly) confirm no such law existed.
- Breaks proof: No

**2. Could the phrase have originated from the wife-beating association even without a formal law?**
- Verification performed: Searched for earliest documented uses of 'rule of thumb' and when the wife-beating association first appeared. Checked multiple etymology sources.
- Finding: The phrase first appeared in print in 1658/1685 (James Durham's sermons), referring to rough practical measurement. The first recorded link between the phrase and wife-beating appeared only in 1976, in a report by women's-rights advocate Del Martin. The phrase predates the false association by roughly 300 years, ruling out this etymology.
- Breaks proof: No

**3. Are the three disproof sources truly independent?**
- Verification performed: Checked source independence: Wikipedia cites multiple scholarly references; Phrases.org.uk is an independent etymology reference site; University of Oregon essay is an academic source citing legal historian Henry Ansgar Kelly's research.
- Finding: Sources are from different institutions (Wikimedia Foundation, Gary Martin's Phrases.org.uk, University of Oregon). While they cite overlapping primary research (e.g., Kelly's work), they are independently published and maintained.
- Breaks proof: No

## Source Credibility Assessment

Source: proof.py JSON summary `citations[].credibility`.

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | wikipedia.org | reference | 3 | Established reference source |
| B2 | org.uk | unknown | 2 | Unclassified domain — verify source authority manually |
| B3 | uoregon.edu | academic | 4 | Academic domain (.edu) |
| B4 | allthatsinteresting.com | unknown | 2 | Unclassified domain — verify source authority manually |

Note: B2 (Phrases.org.uk) and B4 (All That's Interesting) are tier 2 (unclassified). Phrases.org.uk is a well-known etymology reference maintained by Gary Martin since 1996. All That's Interesting is a popular history publication. Their claims are independently corroborated by tier 3 (Wikipedia) and tier 4 (University of Oregon) sources, so the verdict does not depend solely on these lower-tier sources.

## Extraction Records

Source: proof.py JSON summary `extractions`; method narrative is author analysis.

For this qualitative/consensus proof, extractions record citation verification status per source rather than numeric values.

| Fact ID | Value (status) | Countable | Quote Snippet |
|---------|---------------|-----------|---------------|
| B1 | verified | Yes | "A modern folk etymology holds that the phrase is derived from the maximum width " |
| B2 | verified | Yes | "Despite the phrase being in common use since the 17th century and appearing many" |
| B3 | verified | Yes | "there is probably no truth whatever in the legend that he was permitted to beat " |
| B4 | verified | Yes | "There is no evidence that Buller actually said anything of the sort, but he was " |

## Hardening Checklist

- Rule 1: N/A — qualitative proof, no numeric values extracted from quotes
- Rule 2: All 4 citation URLs fetched and quotes verified via `verify_all_citations()`
- Rule 3: `date.today()` used for generated_at date
- Rule 4: CLAIM_FORMAL includes explicit operator_note explaining compound claim structure and disproof direction
- Rule 5: Three adversarial checks performed: searched for supporting evidence (Buller ruling, informal etymology, source independence)
- Rule 6: 4 independently published sources from different institutions consulted and verified
- Rule 7: `compare()` used for claim evaluation; no hard-coded constants
- validate_proof.py result: PASS with warnings (1 warning: no fallback else branch in verdict assignment — cosmetic only, all paths covered for this proof)

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
