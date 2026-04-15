# Audit: Presenting empirical spreadsheet observations as universal theorems violates the hypothetico-deductive method as defined by mainstream philosophy of science.

- **Generated:** 2026-04-07
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| subject | Presenting empirical spreadsheet observations as universal theorems |
| property | violates the hypothetico-deductive method as defined by mainstream philosophy of science |
| operator | >= |
| threshold | 3 |
| proof_direction | prove |
| operator_note | The claim asserts a factual violation: the practice of presenting empirical spreadsheet observations as universal theorems omits steps that the hypothetico-deductive (HD) method requires. We count independent authoritative sources that define HD method requirements (falsifiability, reasoning beyond observation, pre-specified hypotheses) which this practice structurally omits. A threshold of 3 is used to require broad consensus across distinct philosophical and methodological traditions. Entailment note: the cited sources define general requirements of the scientific method / HD method. None specifically names 'spreadsheet observations presented as theorems.' The entailment bridge is: (1) the HD method requires steps X, Y, Z; (2) presenting observations as universal theorems without hypothesis formation, falsifiability testing, or pre-specified analysis omits X, Y, Z; therefore (3) the practice violates the HD method. This inference is logically valid but requires the author-reasoning bridge documented here. Formalization scope: 'universal theorem' is interpreted strictly — a claim of deductive necessity holding without exception, not a statistical regularity or empirical generalization. 'Violates' means the practice omits one or more requirements that the HD method mandates. The proof does not address whether the practice might be valid under non-HD frameworks (e.g., pure inductivism); adversarial check 1 addresses this limitation. |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_britannica_popper | Britannica: Popper's falsifiability criterion — scientific theories must be falsifiable in principle |
| B2 | source_sep_scientific_method | Stanford Encyclopedia of Philosophy: scientific method requires reasoning beyond observation |
| B3 | source_catalog_of_bias | Catalog of Bias: presenting unplanned analyses as prespecified is a recognized methodological distortion |
| A1 | *(computed)* | Count of authoritative sources confirming HD method requirements that the practice omits |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Count of authoritative sources confirming HD method requirements that the practice omits | count(verified citations) = 3 | 3 sources confirmed (threshold: 3) |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Britannica: Popper's falsifiability criterion — scientific theories must be falsifiable in principle | Encyclopaedia Britannica — criterion of falsifiability | https://www.britannica.com/topic/criterion-of-falsifiability | "a theory is genuinely scientific only if it is possible in principle to establish that it is false." | verified | full_quote | Tier 3 (reference) |
| B2 | Stanford Encyclopedia of Philosophy: scientific method requires reasoning beyond observation | Stanford Encyclopedia of Philosophy — scientific method | https://plato.stanford.edu/entries/scientific-method/ | "In addition to careful observation, then, scientific method requires a logic as a system of reasoning for properly arranging, but also inferring beyond, what is known by observation." | verified | full_quote | Tier 4 (academic) |
| B3 | Catalog of Bias: presenting unplanned analyses as prespecified is a recognized methodological distortion | Catalog of Bias — data-dredging bias | https://catalogofbias.org/biases/data-dredging-bias/ | "A distortion that arises from presenting the results of unplanned statistical tests as if they were a fully prespecified course of analyses." | verified | full_quote | Tier 2 (unknown) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — Encyclopaedia Britannica: criterion of falsifiability**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: 100% (full quote match)
- Impact: Establishes Popper's falsifiability criterion as a requirement of the HD method. The practice of presenting empirical observations as universal theorems omits falsifiability testing.

**B2 — Stanford Encyclopedia of Philosophy: scientific method**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: 100% (full quote match)
- Impact: Establishes that scientific method requires reasoning beyond observation. The practice of presenting empirical observations as theorems treats observation as sufficient, omitting the required inferential step.

**B3 — Catalog of Bias: data-dredging bias**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: 100% (full quote match)
- Impact: Identifies the specific methodological distortion of presenting unplanned analyses as prespecified — the pattern that "math washing" follows.

All three citations were fully verified. No "with unverified citations" qualifier applies.

*Source: proof.py JSON summary; impact analysis is author analysis*

---

## Computation Traces

```
Verifying citations...
  [✓] source_britannica_popper: Full quote verified (source: tier 3/reference)
  [✓] source_sep_scientific_method: Full quote verified (source: tier 4/academic)
  [✓] source_catalog_of_bias: Full quote verified (source: tier 2/unknown)
  Confirmed sources: 3 / 3
  n_confirmed = 3
  compare(3, '>=', 3) = True => claim_holds = True
  Proof direction: prove — claim is PROVED
```

*Source: proof.py inline output (execution trace)*

---

## Extraction Records

| Fact ID | Extracted Value | Value in Quote | Quote Snippet |
|---------|----------------|----------------|---------------|
| B1 | verified | Yes | a theory is genuinely scientific only if it is possible in principle to establis |
| B2 | verified | Yes | In addition to careful observation, then, scientific method requires a logic as  |
| B3 | verified | Yes | A distortion that arises from presenting the results of unplanned statistical te |

For this qualitative/consensus proof, the `extractions` field records citation verification status per source rather than numeric values. "Value in Quote" indicates whether the citation was countable (verified or partial).

*Source: proof.py JSON summary; extraction method note is author analysis*

---

## Independent Source Agreement (Rule 6)

| Cross-check | Values Compared | Agreement |
|-------------|-----------------|-----------|
| Three independent authoritative sources from distinct traditions (encyclopedic philosophy, academic philosophy reference, medical/scientific methodology catalog) each confirm a different HD method requirement that the practice omits: falsifiability (B1), reasoning beyond observation (B2), pre-specified hypotheses (B3). | B1: verified, B2: verified, B3: verified | True |

**Independence rationale:** B1 is Encyclopaedia Britannica's article on Popper's falsifiability criterion (encyclopedic reference). B2 is the Stanford Encyclopedia of Philosophy's article on scientific method (academic reference, peer-reviewed). B3 is the Catalog of Bias's entry on data-dredging (maintained by the Centre for Evidence-Based Medicine at the University of Oxford). These are three independently authored and maintained sources from distinct intellectual traditions. Each addresses a different failure mode: falsifiability (B1), reasoning beyond observation (B2), pre-specified hypotheses (B3).

**COI assessment:** No conflict of interest flags identified. None of the three sources has a financial, institutional, or ideological stake in the specific question of "math washing" or spreadsheet-based claims.

*Source: proof.py JSON summary; independence rationale and COI assessment are author analysis*

---

## Adversarial Checks (Rule 5)

**Check 1: Is there a scientific tradition that validates presenting inductive generalizations from data as universal laws without further testing?**
- Question: Is there a scientific tradition that validates presenting inductive generalizations from data as universal laws without further testing?
- Verification performed: Searched 'defense inductive reasoning empirical observations sufficient universal scientific laws' and 'Bacon inductivism valid science pattern observation'. Found inductivism (Bacon's model) as a candidate defense.
- Finding: Even Bacon's inductivism — the strongest defense of inductive science — requires systematic collection, replication, and elimination of observer bias before generalizing. Naive inductivism has been largely discredited in philosophy of science (Popper, 1934; Hempel, 1965). More importantly, no form of inductivism endorses presenting patterns as universal 'theorems' (a term implying deductive necessity) rather than empirical generalizations. This check does not break the proof but limits the verdict's scope: the proof establishes violation of the HD method specifically, not all possible philosophies of science.
- Breaks proof: No

**Check 2: Does Exploratory Data Analysis (EDA) validate presenting spreadsheet patterns as scientific findings?**
- Question: Does Exploratory Data Analysis (EDA) validate presenting spreadsheet patterns as scientific findings?
- Verification performed: Searched 'Tukey exploratory data analysis purpose hypothesis generation not confirmation'. Reviewed EDA methodology documentation.
- Finding: EDA (Tukey 1977) is an explicitly hypothesis-generating practice, not hypothesis-confirming. Tukey's framework is designed to produce candidate hypotheses for subsequent testing, not to generate universal theorems. This supports the proof: the EDA literature itself distinguishes pattern-finding from universal claims.
- Breaks proof: No

**Check 3: Could 'math washing' be valid in limited empirical domains like actuarial science, empirical economics, or physics phenomenology?**
- Question: Could 'math washing' be valid in limited empirical domains like actuarial science, empirical economics, or physics phenomenology?
- Verification performed: Searched 'stylized facts empirical economics vs universal law', 'actuarial science empirical observation universal theorem'. Reviewed terminology used in empirical economic methodology.
- Finding: Empirical economics explicitly distinguishes between 'stylized facts' (regularities observed in data) and 'economic laws' or theorems. Kaldor (1961) introduced 'stylized facts' precisely because observed patterns in data do NOT constitute universal theorems without theoretical grounding. Even in phenomenological physics, empirical regularities (e.g., Kepler's laws) were only elevated to scientific law status after being derived from deeper theoretical principles (Newton's mechanics). No domain endorses presenting data patterns as universal theorems directly.
- Breaks proof: No

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | britannica.com | reference | 3 | Established reference source |
| B2 | stanford.edu | academic | 4 | Academic domain (.edu) |
| B3 | catalogofbias.org | unknown | 2 | Unclassified domain — verify source authority manually |

**Note on B3 (Tier 2):** catalogofbias.org is the online home of the Catalog of Bias project, affiliated with the University of Oxford's Centre for Evidence-Based Medicine (CEBM). The domain is unclassified by the automated credibility system, but the project is an established academic resource in evidence-based medicine. The conclusion does not depend solely on B3 — B1 (Tier 3) and B2 (Tier 4) independently support the proof.

*Source: proof.py JSON summary; tier-2 note is author analysis*

---

## Hardening Checklist

| Rule | Status | Notes |
|------|--------|-------|
| Rule 1: Every empirical value parsed from quote text, not hand-typed | N/A — qualitative proof; no numeric values extracted from quotes | Proof is based on citation verification status, not numeric extraction |
| Rule 2: Every citation URL fetched and quote checked | PASS | All 3 citations verified via live fetch (B1: full_quote, B2: full_quote, B3: full_quote) |
| Rule 3: System time used for date-dependent logic | N/A — no time-dependent computation | Proof generates date via `date.today()` for the generator block only |
| Rule 4: Claim interpretation explicit with operator rationale | PASS | CLAIM_FORMAL includes operator_note explaining entailment bridge, formalization scope, threshold rationale, and proof direction |
| Rule 5: Adversarial checks searched for independent counter-evidence | PASS | Three adversarial checks covering inductivism defense, EDA methodology, and domain-specific practices |
| Rule 6: Cross-checks used independently sourced inputs | PASS | Three independently authored and maintained sources from distinct intellectual traditions, all verified; COI assessment performed |
| Rule 7: Constants and formulas imported from computations.py, not hand-coded | PASS | `compare()` imported from `scripts/computations.py`; no hard-coded constants |

*Source: author analysis based on proof.py structure and execution results*

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.8.0 on 2026-04-07.*
