# Audit: Humans use only 10% of their brain at any one time

- **Generated:** 2026-04-15
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The natural-language claim asserts that humans use only 10% of their brain at any one time. This is interpreted as a neuroscientific claim about the proportion of brain tissue that is functionally active at any given moment.

"Use" is operationalized as neuronal activity detectable by functional brain imaging (functional magnetic resonance imaging, positron emission tomography) or inferred from lesion studies. The claim is disproved when three or more authoritative, independent neuroscience sources reject it with evidence that substantially more than 10% of the brain is active at any given time.

**Formalization scope:** The natural-language claim maps directly to the formal interpretation. The only narrowing is the operationalization of "use" as detectable neuronal activity, which is the standard neuroscientific interpretation of brain usage. The formal spec does not address metaphorical readings (e.g., "untapped potential"), which are noted in the adversarial checks.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Human brain |
| Property | proportion of brain actively used at any given time |
| Operator | >= |
| Threshold | 3 (rejection sources needed) |
| Proof direction | disprove |
| Operator note | The claim asserts that only 10% of the brain is in use at any one time. This is disproved when >= 3 authoritative neuroscience sources reject the claim, providing evidence that substantially more than 10% of the brain is active at any given time. 'Use' is interpreted as neuronal activity detectable by functional brain imaging (fMRI, PET scans) or inferred from lesion studies. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | scientific_american | Scientific American — neurologist Barry Gordon rejects the 10% myth |
| B2 | mit_mcgovern | MIT McGovern Institute — the 10% claim is '100 percent a myth' |
| B3 | uw_neuroscience | University of Washington Neuroscience — no scientific evidence for 10% claim |
| A1 | — | Verified rejection source count |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified rejection source count | count(verified rejection citations) = 3 | 3 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Scientific American — neurologist Barry Gordon rejects the 10% myth | Scientific American (Barry Gordon, Johns Hopkins) | [link](https://www.scientificamerican.com/article/do-people-only-use-10-percent-of-their-brains/) | the &ldquo;10 percent myth&rdquo; is so wrong it is almost laughable, says neurologist Barry Go... | verified | full_quote | Major news |
| B2 | MIT McGovern Institute — the 10% claim is '100 percent a myth' | MIT McGovern Institute for Brain Research | [link](https://mcgovern.mit.edu/2024/01/26/do-we-use-only-10-percent-of-our-brain/) | the idea that we use 10 percent of our brain is 100 percent a myth | verified | full_quote | Academic |
| B3 | University of Washington Neuroscience — no scientific evidence for 10% claim | Neuroscience For Kids, University of Washington (Eric Chudler) | [link](http://faculty.washington.edu/chudler/tenper.html) | There is no scientific evidence to suggest that we use only 10% of our brains | verified | full_quote | Academic |

*Source: proof.py JSON summary*

## Citation Verification Details

### B1 — Scientific American

- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Rejection statement:** the "10 percent myth" is so wrong it is almost laughable
- **Verbatim status:** verbatim (default)

### B2 — MIT McGovern Institute

- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Rejection statement:** the idea that we use 10 percent of our brain is 100 percent a myth
- **Verbatim status:** verbatim (default)

### B3 — University of Washington Neuroscience

- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Rejection statement:** no scientific evidence to suggest that we use only 10%
- **Verbatim status:** verbatim (default)

*Source: proof.py JSON summary*

## Computation Traces

```
  verified rejection source count vs threshold: 3 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

Three independent sources were consulted, and all three were successfully verified:

| Source key | Verification status |
|------------|-------------------|
| scientific_american | verified |
| mit_mcgovern | verified |
| uw_neuroscience | verified |

**Independence note:** Sources are from different institutions: Scientific American (quoting Johns Hopkins neurologist), MIT McGovern Institute, and University of Washington. No organizational, funding, or ideological overlap.

**COI assessment:** No conflicts of interest identified. All three sources are independent academic or science journalism institutions with no stake in the outcome of this claim.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

### Check 1: Any peer-reviewed support for the 10% claim?

- **Question:** Is there any peer-reviewed neuroscience study that supports the claim that only 10% of the brain is active at any given time?
- **Verification performed:** Searched for: '10 percent brain myth credible support evidence true', '10% brain use scientific evidence peer-reviewed'. Reviewed results from Scientific American, Psychology Today, Wikipedia, Association for Psychological Science, MIT McGovern Institute, Medical News Today, and University of Washington.
- **Finding:** No peer-reviewed neuroscience study was found supporting the 10% claim. Every neuroscience source consulted explicitly labels it a myth. Brain imaging studies (fMRI, PET) consistently show activity throughout the entire brain, even during sleep.
- **Breaks proof:** No

### Check 2: Neuron-to-glia ratio interpretation

- **Question:** Could the 10% figure refer to the ratio of neurons to glial cells, making the claim technically true under a different interpretation?
- **Verification performed:** Searched for: 'neurons 10 percent brain cells glial ratio'. Reviewed neuroscience sources on neuron-to-glia ratios.
- **Finding:** While roughly 10% of brain cells are neurons (the rest being glial cells), the claim says 'use only 10% of their brain,' which refers to brain regions being active, not cell-type ratios. Furthermore, glial cells are also functionally active — they support neuronal function, maintain homeostasis, and participate in signaling. The neuron/glia ratio does not support the claim as stated.
- **Breaks proof:** No

### Check 3: William James's 1907 statement

- **Question:** Could William James's original 1907 statement be interpreted as literal neuroscience supporting the 10% claim?
- **Verification performed:** Searched for: 'William James 1907 energies of men 10 percent origin'. Reviewed MIT McGovern and Wikipedia articles on the myth's origins.
- **Finding:** William James wrote in 'The Energies of Men' (1907) that 'we are making use of only a small part of our possible mental and physical resources.' He was speaking metaphorically about human potential, not making a neuroscientific claim about brain activity percentages. He never stated 10%, and his work predates functional brain imaging by decades.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Note |
|---------|--------|------|------|
| B1 | scientificamerican.com | Major news | Major news organization |
| B2 | mit.edu | Academic | Academic domain (.edu) |
| B3 | washington.edu | Academic | Academic domain (.edu) |

*Source: proof.py JSON summary*

## Source Data

For this qualitative consensus/disproof proof, the `extractions` field records citation verification status per source rather than numeric extracted values.

| Fact ID | Value | Value in quote | Quote snippet |
|---------|-------|----------------|---------------|
| B1 | verified | Yes | the "10 percent myth" is so wrong it is almost laughable, says neurologist Barry |
| B2 | verified | Yes | the idea that we use 10 percent of our brain is 100 percent a myth |
| B3 | verified | Yes | There is no scientific evidence to suggest that we use only 10% of our brains |

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A — qualitative proof, no numeric value extraction needed
- **Rule 2:** All 3 citation URLs fetched; all quotes verified (full_quote match, live fetch)
- **Rule 3:** N/A — proof is not time-sensitive
- **Rule 4:** CLAIM_FORMAL includes operator_note explaining interpretation of "use" and disproof threshold
- **Rule 5:** 3 adversarial checks performed — searched for peer-reviewed support, alternative interpretations (neuron/glia ratio), and historical origin (William James). None broke the proof.
- **Rule 6:** 3 independent sources from different institutions (Scientific American/Johns Hopkins, MIT, University of Washington). No COI identified.
- **Rule 7:** N/A — qualitative proof, no constants or formulas
- **validate_proof.py result:** PASS — 21/21 checks passed, 0 issues, 0 warnings

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.16.0 on 2026-04-15.
