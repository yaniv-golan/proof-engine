# Audit: Humans use only 10% of their brain at any one time.

- **Generated:** 2026-03-27
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| subject | human brain usage |
| property | Whether scientific consensus holds that only 10% of the brain is active at any given moment |
| operator | >= |
| operator_note | This proof proceeds by disproof: the claim is adjudicated FALSE if 3 or more independent authoritative sources explicitly characterize it as a myth, misconception, or scientifically unsupported belief. If the threshold is not met, the verdict is UNDETERMINED — failing to find enough rejection sources does not validate the claim. |
| threshold | 3 |
| proof_direction | disprove |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_mit | MIT McGovern Institute for Brain Research: labels the 10% claim a myth |
| B2 | source_britannica | Encyclopaedia Britannica: states entire brain is in use at all times |
| B3 | source_sciam | Scientific American: characterizes the 10-percent claim as a myth |
| A1 | — | Source count: independent authoritative sources rejecting the 10% claim |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Source count: independent authoritative sources rejecting the 10% claim | sum(confirmations) = 3 | 3 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | MIT McGovern Institute: labels claim a myth | MIT McGovern Institute for Brain Research | https://mcgovern.mit.edu/2024/01/26/do-we-use-only-10-percent-of-our-brain/ | "But the idea that we use 10 percent of our brain is 100 percent a myth." | verified | full_quote | Tier 4 (academic) |
| B2 | Britannica: entire brain in use | Encyclopaedia Britannica | https://www.britannica.com/story/do-we-really-use-only-10-percent-of-our-brain | "But the truth is that we use all of our brain all of the time." | verified | full_quote | Tier 3 (reference) |
| B3 | Scientific American: characterizes as myth | Scientific American | https://www.scientificamerican.com/article/do-we-really-use-only-10/ | "the 10-percent myth is one of those hopeful shibboleths that refuses to die" | verified | full_quote | Tier 2 (unknown) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — MIT McGovern Institute**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Coverage: N/A (full quote match)

**B2 — Encyclopaedia Britannica**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Coverage: N/A (full quote match)

**B3 — Scientific American**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Coverage: N/A (full quote match)

No citations were unverified; impact analysis is not required.

*Source: proof.py JSON summary*

---

## Computation Traces

Reproduced verbatim from proof.py execution:

```
  [✓] source_mit: Full quote verified for source_mit (source: tier 4/academic)
  [✓] source_britannica: Full quote verified for source_britannica (source: tier 3/reference)
  [✓] source_sciam: Full quote verified for source_sciam (source: tier 2/unknown)
  [✓] B1: extracted myth from quote
  [✓] B2: extracted all of our brain from quote
  [✓] B3: extracted myth from quote
  compare: 3 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

| Description | n_sources | n_confirming | Agreement |
|-------------|-----------|--------------|-----------|
| Independent source agreement on claim rejection | 3 | 3 | True |

All 3 sources independently reject the 10% claim using rejection language verified against live page content. Each source is independently published (different organizations: MIT, Britannica, Scientific American), providing independent corroboration.

*Source: proof.py JSON summary*

---

## Adversarial Checks (Rule 5)

**Check 1**
- Question: Does any peer-reviewed neuroscience study support that only 10% of the brain is active at any given moment?
- Verification performed: Searched: 'scientific evidence supporting 10 percent brain usage theory peer reviewed'. All results were debunking articles or consensus statements. No peer-reviewed study was found that supports the 10% claim.
- Finding: No peer-reviewed neuroscience study supports the 10% claim. fMRI and PET imaging studies consistently show substantially more than 10% of brain regions active at any given time. The claim has no empirical basis.
- Breaks proof: No

**Check 2**
- Question: Could 'sparse coding' — the fact that not all neurons fire simultaneously — give the 10% claim any scientific grounding?
- Verification performed: Searched: 'neuroscience sparse coding 10 percent neurons firing simultaneously'. Reviewed neuroscience discussions on neural efficiency and sparse representation.
- Finding: Sparse coding means individual neurons fire selectively, not that only 10% of brain REGIONS are active. fMRI BOLD signal shows that even simple tasks engage many distributed brain regions simultaneously. Sparse neuron firing is fundamentally different from 10% brain usage and does not rescue the claim.
- Breaks proof: No

**Check 3**
- Question: Could the qualifier 'at any one time' narrow the claim to something defensible — e.g., only a fraction of the brain fires in any single millisecond?
- Verification performed: Reviewed neuroscience literature on neural synchrony, BOLD signal interpretation, and metabolic baseline activity. Considered whether any temporal interpretation makes the claim valid.
- Finding: Even under the most favorable temporal interpretation the claim fails. The brain's metabolic baseline — consuming 20% of the body's energy despite being 2% of body mass — requires continuous activity across many regions at all times, including during sleep. There is no timescale at which only 10% of brain regions are active while the rest are truly idle.
- Breaks proof: No

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | mit.edu | academic | 4 | Academic domain (.edu) |
| B2 | britannica.com | reference | 3 | Established reference source |
| B3 | scientificamerican.com | unknown | 2 | Unclassified domain — verify source authority manually |

Tier scale: 5=government/intergovernmental, 4=academic/peer-reviewed, 3=major news or established reference, 2=unclassified, 1=flagged unreliable.

Note on B3: Scientific American (founded 1845) is a major science publication and is widely considered authoritative. Its tier-2 classification reflects the automated scorer's lack of a domain rule for scientificamerican.com, not any concern about the source's reliability. The disproof conclusion (B1, B2) is independently supported by tier-3 and tier-4 sources and does not depend solely on B3.

*Source: proof.py JSON summary*

---

## Extraction Records

| ID | Keyword Extracted | Found in Quote | Quote Snippet |
|----|-------------------|----------------|---------------|
| B1 | myth | True | "But the idea that we use 10 percent of our brain is 100 percent a myth." |
| B2 | all of our brain | True | "But the truth is that we use all of our brain all of the time." |
| B3 | myth | True | "the 10-percent myth is one of those hopeful shibboleths that refuses to die" |

Extraction method: `verify_extraction(keyword, quote, fact_id)` from `scripts/smart_extract.py`. Each keyword was verified to appear in the corresponding quote string. For disproof proofs, the keyword confirms the source is expressing rejection of the claim (not mere mention). All keywords ("myth", "all of our brain", "myth") are present only in quotes that treat the 10% claim as false.

*Source: proof.py JSON summary (extractions); extraction method is author analysis*

---

## Hardening Checklist

| Rule | Status | Notes |
|------|--------|-------|
| Rule 1: Every empirical value parsed from quote text, not hand-typed | PASS | `verify_extraction()` used for all 3 fact keywords |
| Rule 2: Every citation URL fetched and quote checked | PASS | `verify_all_citations()` with `wayback_fallback=True`; all 3 verified live |
| Rule 3: System time used for date-dependent logic | N/A | No date computations in this proof |
| Rule 4: Claim interpretation explicit with operator rationale | PASS | `CLAIM_FORMAL` with full `operator_note` including proof_direction rationale |
| Rule 5: Adversarial checks searched for independent counter-evidence | PASS | 3 adversarial checks; none found counter-evidence; `breaks_proof=False` for all |
| Rule 6: Cross-checks used independently sourced inputs | PASS | 3 independently published sources (MIT, Britannica, SciAm) with unanimous agreement |
| Rule 7: Constants and formulas imported from computations.py, not hand-coded | PASS | `compare()` used for claim evaluation; no hand-coded thresholds |
| validate_proof.py result | PASS (14/14 checks, 0 issues, 0 warnings) | Run: `python scripts/validate_proof.py proof.py` |
