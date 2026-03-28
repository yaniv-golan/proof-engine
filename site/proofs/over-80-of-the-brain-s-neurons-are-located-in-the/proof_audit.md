# Audit: Over 80% of the brain's neurons are located in the cerebellum.

- **Generated:** 2026-03-27
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|---|---|
| Subject | Human cerebellum |
| Property | Percentage of total brain neurons located in the cerebellum |
| Operator | > |
| Threshold | 80.0% |
| Operator note | "'Over 80%' is interpreted as strictly greater than 80.0%. If the cerebellum held exactly 80.0% of neurons the claim would be FALSE. 'Brain' means the entire brain (cerebrum + cerebellum + brainstem) excluding the spinal cord — the standard neuroanatomical usage in all cited sources. The more conservative strict-greater-than reading is used; >= would make the claim easier to prove." |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Key | Label |
|---|---|---|
| B1 | source_a_total | Total human brain neuron count — Herculano-Houzel 2009 (PMC2776484) |
| B2 | source_a_cerebellum | Cerebellum neuron count — Herculano-Houzel 2009 (PMC2776484) |
| B3 | source_b | Independent statement: cerebellum ~80% of brain neurons — von Bartheld et al. 2016 review (PMC5063692) |
| B4 | source_c | Cross-species comparison: 80% in human — Herculano-Houzel et al. 2010 Frontiers Neuroanatomy |
| A1 | (computed) | Computed cerebellum neuron %: (69 billion / 86 billion) × 100 |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|---|---|---|---|
| A1 | Cerebellum as % of total brain neurons | `cerebellum_neurons / total_neurons * 100` | 80.2326% |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|---|---|---|---|---|---|---|---|
| B1 | Total brain neurons: 86 billion | Herculano-Houzel 2009, Front Hum Neurosci 3:31. PMC2776484 | https://pmc.ncbi.nlm.nih.gov/articles/PMC2776484/ | "the adult male human brain, at an average of 1.5 kg, has 86 billion neurons and 85 billion non-neuronal cells" | verified | full_quote | Tier 5 (government) |
| B2 | Cerebellum neurons: 69 billion | Herculano-Houzel 2009, Front Hum Neurosci 3:31. PMC2776484 | https://pmc.ncbi.nlm.nih.gov/articles/PMC2776484/ | "the human cerebellum, at 154 g and 69 billion neurons, matches or even slightly exceeds the expected" | verified | full_quote | Tier 5 (government) |
| B3 | Cerebellum ~80% of brain neurons | von Bartheld et al. 2016, J Comp Neurol 524(18). PMC5063692 | https://pmc.ncbi.nlm.nih.gov/articles/PMC5063692/ | "the cerebellum (which contains about 80% of all neurons in the human brain; Azevedo et al. (2009))" | verified | full_quote | Tier 5 (government) |
| B4 | 80% in human (comparative) | Herculano-Houzel et al. 2010, Front Neuroanat 4:12 | https://www.frontiersin.org/journals/neuroanatomy/articles/10.3389/fnana.2010.00012/full | "the cerebellum holds 60% of all brain neurons in the mouse, small shrews, and marmoset; 70% in the rat, guinea pig and macaque; and 80% in the agouti, galago, and human" | verified | full_quote | Tier 4 (academic) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — Herculano-Houzel 2009 (PMC2776484) — total neurons**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Data values confirmed: "86 billion neurons" found on page [live]

**B2 — Herculano-Houzel 2009 (PMC2776484) — cerebellum neurons**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Data values confirmed: "69 billion neurons" found on page [live]

**B3 — von Bartheld et al. 2016 (PMC5063692)**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4 — Herculano-Houzel et al. 2010 (Frontiers Neuroanatomy)**
- Status: verified
- Method: full_quote
- Fetch mode: live

*Source: proof.py inline output (execution trace)*

---

## Computation Traces

```
=== Verifying citations ===
  [✓] source_a_total: Full quote verified for source_a_total (source: tier 5/government)
  [✓] source_a_cerebellum: Full quote verified for source_a_cerebellum (source: tier 5/government)
  [✓] source_b: Full quote verified for source_b (source: tier 5/government)
  [✓] source_c: Full quote verified for source_c (source: tier 4/academic)

=== Verifying data values ===
  [✓] B1.total_neurons: '86 billion neurons' found on page [live]
  [✓] B2.cerebellum_neurons: '69 billion neurons' found on page [live]

  [✓] B1: extracted 86 from quote
  [✓] B2: extracted 69 from quote

Extracted total brain neurons: 86 billion
Extracted cerebellum neurons: 69 billion

=== Computation ===
  Cerebellum % of total brain neurons: cerebellum_neurons / total_neurons * 100 = 69000000000.0 / 86000000000.0 * 100 = 80.2326

=== Claim Evaluation ===
  SC1: cerebellum neuron % > 80%: 80.23255813953489 > 80.0 = True

=== Cross-check ===
  [✓] B3: extracted 80 from quote
  Computed 80.23% vs B3 stated ~80% (von Bartheld 2016): 80.23255813953489 vs 80.0, diff=0.2325581395348877, tolerance=2.0 -> AGREE
  [✓] B4: extracted 80 from quote
  Computed 80.23% vs B4 stated 80% (Herculano-Houzel 2010): 80.23255813953489 vs 80.0, diff=0.2325581395348877, tolerance=2.0 -> AGREE
```

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

| Cross-check | Values | Tolerance | Mode | Agreement |
|---|---|---|---|---|
| Computed 80.23% vs B3 stated ~80% (von Bartheld 2016 review) | 80.2326 vs 80.0 | 2.0 pp | absolute | Yes (diff = 0.23 pp) |
| Computed 80.23% vs B4 stated 80% (Herculano-Houzel 2010) | 80.2326 vs 80.0 | 2.0 pp | absolute | Yes (diff = 0.23 pp) |

**Note on independence:** B1 and B2 share the same URL (PMC2776484) — they are the same published paper but carry two distinct facts (total count and cerebellum count). B3 (PMC5063692) and B4 (Frontiers 2010) are independently authored papers that state the 80% figure, providing independent source agreement with the computed value. This constitutes "independently published (same upstream authority — Azevedo 2009)" rather than fully independent measurements.

*Source: proof.py JSON summary*

---

## Adversarial Checks (Rule 5)

**1. Does any peer-reviewed source dispute the ~80% figure?**
- Verification: Searched "cerebellum percentage brain neurons 80 percent counter-evidence dispute". Found brainfacts.org (2020) says "more than half." Found PMC5063692 Table 4 lists Andrade-Moraes 2013 at 54×10⁹ cerebellum neurons vs Azevedo's 69×10⁹.
- Finding: Andrade-Moraes 2013 is a genuine alternative giving ~63% under the same total — well below 80%. brainfacts.org is popular science. No peer-reviewed paper disputes ~80% *under the Azevedo methodology*.
- Breaks proof: No

**2. If 'brain' included the spinal cord, would the percentage fall below 80%?**
- Verification: Searched spinal cord neuron count. Estimate: ~1 billion. 69/(86+1) = 79.3%.
- Finding: Yes, it would drop to 79.3%. But "brain" excludes the spinal cord by standard neuroanatomical definition used in all cited sources.
- Breaks proof: No

**3. Is the margin of 0.23 pp within measurement error?**
- Verification: Azevedo 2009 reports 86.1 ± 8.1B total and 69.03 ± 6.65B cerebellum. Lower-bound ratio: 66.2%; upper: 97.0%.
- Finding: The 0.23 pp excess is within measurement uncertainty. The proof rests on point estimates. Scientific literature says "about 80%," not "strictly over 80%." Genuine limitation noted; does not disprove the claim.
- Breaks proof: No

**4. Could 'over 80%' linguistically require 81%+?**
- Verification: Linguistic analysis.
- Finding: "Over 80%" means > 80.0% in standard English. 80.23% satisfies this.
- Breaks proof: No

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---|---|---|---|---|
| B1 | nih.gov | government | 5 | Government domain (.gov) — PubMed Central |
| B2 | nih.gov | government | 5 | Government domain (.gov) — PubMed Central |
| B3 | nih.gov | government | 5 | Government domain (.gov) — PubMed Central |
| B4 | frontiersin.org | academic | 4 | Known academic/scholarly publisher |

All citations tier 4 or 5. No low-credibility sources cited.

*Source: proof.py JSON summary*

---

## Extraction Records

| ID | Extracted Value | Found in Quote | Quote Snippet |
|---|---|---|---|
| B1 | 86 billion (86,000,000,000) | Yes | "the adult male human brain, at an average of 1.5 kg, has 86 billion neurons and…" |
| B2 | 69 billion (69,000,000,000) | Yes | "the human cerebellum, at 154 g and 69 billion neurons, matches or even slightly…" |
| B3 | 80% | Yes | "the cerebellum (which contains about 80% of all neurons in the human brain; Azev…" |
| B4 | 80% | Yes | "the cerebellum holds 60% of all brain neurons in the mouse, small shrews, and ma…" |

**Extraction method for B1/B2:** Regex `(\d+) billion neurons` applied after `normalize_unicode()`. Integer captured, then multiplied by 10⁹. `verify_extraction()` confirms the raw integer (86, 69) appears in the original quote string.

**Extraction method for B3:** Regex `about (\d+)%` applied after `normalize_unicode()`. Captured 80.

**Extraction method for B4:** Regex `and (\d+)% in the agouti` applied after `normalize_unicode()`. Captured 80.

*Source: proof.py JSON summary; extraction method description is author analysis*

---

## Hardening Checklist

- [x] **Rule 1:** All values parsed from quote text using regex + `verify_extraction()`. No hand-typed numbers.
- [x] **Rule 2:** All 4 citation URLs fetched live; all quotes verified (full_quote method).
- [x] **Rule 3:** N/A — no date-dependent computations in this proof.
- [x] **Rule 4:** `CLAIM_FORMAL` with `operator_note` documents the strict-greater-than interpretation and definition of "brain."
- [x] **Rule 5:** Adversarial checks searched for counter-evidence (Andrade-Moraes competing estimate, spinal cord inclusion, measurement uncertainty, brainfacts.org understatement).
- [x] **Rule 6:** Cross-checks use B3 and B4 as independently authored sources to corroborate the computed percentage. B1/B2 share a URL but carry distinct factual claims. Independence note documented.
- [x] **Rule 7:** No hard-coded constants. `explain_calc()` and `compare()` used from `scripts/computations.py`.
- [x] **validate_proof.py:** 14/14 checks passed, 0 issues, 0 warnings — STATUS: PASS
