# Audit: The adult human brain has approximately 86 billion neurons and an average of 7,000 synapses per neuron, resulting in a total synaptic count exceeding 6 × 10^14

- **Generated:** 2026-03-27
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Adult human brain |
| SC1 | Neuron count ≈ 86 billion (within ±15% tolerance) |
| SC2 | Average synapses per neuron ≈ 7,000, applied brain-wide across all neurons |
| SC3 | Total synaptic count = SC1 × SC2 > 6 × 10¹⁴ |
| Operator | > |
| Threshold | 6.0 × 10¹⁴ |
| Operator note | "Exceeding 6 × 10¹⁴" means strictly > 6.0e14. Arithmetic (86e9 × 7000 = 6.02e14) is correct given premises. SC2 as stated for all neurons is unsupported; 7,000 is the neocortical figure only. |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_neurons_a | Herculano-Houzel 2009 (Frontiers Hum Neurosci, PMC2776484): 86B neurons in adult brain |
| B2 | source_neurons_b | UCLA Brain Research Institute: ~86B neurons, ~100 trillion synapses whole-brain |
| B3 | source_synapses | BioNumbers BNID 112055 (Harvard/Drachman 2005): 7,000 synapses per neocortical neuron |
| A1 | — | SC3 arithmetic: 86e9 × 7,000 = 6.02e14 |
| A2 | — | SC3 comparison: 6.02e14 > 6e14 |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | SC3 arithmetic: 86e9 × 7,000 = 6.02e14 | `explain_calc(neurons * synapses_per_neuron)` | 6.020e+14 |
| A2 | SC3 comparison: 6.02e14 > 6e14 | `compare(total_synapses, '>', 6e14)` | True |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | 86B neurons in adult brain | Frontiers in Human Neuroscience, Herculano-Houzel 2009 (PubMed Central) | https://pmc.ncbi.nlm.nih.gov/articles/PMC2776484/ | "the adult male human brain, at an average of 1.5 kg, has 86 billion neurons and 85 billion non-neuronal cells" | verified | full_quote | Tier 5 (government) |
| B2 | ~86B neurons, ~100T synapses | UCLA Brain Research Institute, Brain Facts | https://bri.ucla.edu/brain-fact/billions-of-neurons-trillions-of-synapses/ | "The human brain contains approximately 86 billion neurons, each forming thousands of connections, resulting in an estimated 100 trillion synapses." | verified | full_quote | Tier 4 (academic) |
| B3 | 7,000 synapses per neocortical neuron | BioNumbers BNID 112055, Harvard Medical School (citing Drachman 2005, Neurology) | https://bionumbers.hms.harvard.edu/bionumber.aspx?s=n&v=3&id=112055 | "Within the liter and a half of human brain, stereologic studies estimate that there are approximately 20 billion neocortical neurons, with an average of 7,000 synaptic connections each" | verified | full_quote | Tier 4 (academic) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — Frontiers in Human Neuroscience (PMC2776484)**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: full match (no fragment)

**B2 — UCLA Brain Research Institute**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: full match

**B3 — BioNumbers BNID 112055 (Harvard)**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: full match

*Source: proof.py JSON summary*

---

## Computation Traces

```
SC3: total synaptic count (86e9 neurons × 7,000 synapses/neuron): neurons * synapses_per_neuron = 86000000000.0 * 7000.0 = 6.02e+14
SC3 arithmetic: total_synapses > 6e14: 602000000000000.0 > 600000000000000.0 = True
SC1: neurons_a >= 70e9 (well within ~86B range): 86000000000.0 >= 70000000000.0 = True
SC1 neuron count: B1 (Herculano-Houzel) vs B2 (UCLA BRI): 86000000000.0 vs 86000000000.0, diff=0.0, tolerance=0.0 -> AGREE
```

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

| Cross-check | Source A | Source B | Values | Agreement |
|-------------|----------|----------|--------|-----------|
| SC1 neuron count | B1: Herculano-Houzel 2009 (86e9) | B2: UCLA BRI (86e9) | 86,000,000,000 vs 86,000,000,000 | ✓ Exact agreement |

Note: The neuron count cross-check is independent (different organizations, different publication types: peer-reviewed journal vs university fact page). The synapse average (B3) has no second independent source giving the same brain-wide figure; B3 is the sole citation for SC2.

*Source: proof.py JSON summary*

---

## Adversarial Checks (Rule 5)

**1. Is the 86 billion neuron figure disputed?**
- Verification performed: Searched for critiques of Herculano-Houzel's isotropic fractionator method. Found Goriely (Brain, 2024, PMC11884752) arguing confidence intervals span ~73–99 billion, not precisely 86 billion. A 2025 rebuttal (Brain, PMID 39913195) defends the ~86 billion estimate and recommends the phrasing 'around 86 billion neurons'.
- Finding: 86 billion is the best current estimate. The uncertainty (±8B per Azevedo 2009) does not undermine SC1. The claim says 'approximately 86 billion', which is accurate.
- **Breaks proof: No**

**2. Does the 7,000 synapses/neuron figure apply to ALL brain neurons?**
- Verification performed: Read BioNumbers BNID 112055 (Harvard): explicitly says '~20 billion neocortical neurons, with an average of 7,000 synaptic connections each' — not all 86 billion. Primary source: Drachman 2005 (Neurology 64:2004), citing Pakkenberg et al. 2003 for neocortical data. The cerebellum alone contains ~69 billion granule cells with only 4–5 synapses each. If only neocortical neurons average 7,000: 20e9 × 7000 = 1.4e14, well below 6e14.
- Finding: BREAKS SC2 as stated for ALL neurons. The 7,000 figure applies to neocortical neurons only. Brain-wide average is far lower due to the ~69 billion cerebellar granule cells. The compound claim's SC2 premise is a conflation of neocortical average with whole-brain average.
- **Breaks proof: Yes → SC2 and SC3 are unsupported**

**3. Do any primary sources report total brain synapses at or above 6×10¹⁴?**
- Verification performed: Searched PubMed, PMC, and educational sources for whole-brain synapse estimates. UCLA BRI (B2): ~100 trillion = 1×10¹⁴. Pakkenberg et al. 2003 (PMID 12543266): ~0.15×10¹⁵ = 1.5×10¹⁴ (neocortex only). Tang et al. 2001 (PMID 11418939): ~1.64×10¹⁴ (neocortex). PMC11423976: 'around 10¹⁴ (100 trillion) synapses in the average adult human brain'. No primary peer-reviewed source found reporting 6×10¹⁴ for the whole brain.
- Finding: No primary source corroborates 6×10¹⁴ as the total synapse count. Primary literature consistently gives ~1–3×10¹⁴. The 6×10¹⁴ figure arises from applying the neocortical average (7,000) to all 86 billion neurons — a methodological error in the original claim.
- **Breaks proof: Yes → SC3 is empirically unsupported**

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | nih.gov | government | 5 | PubMed Central — NIH-hosted peer-reviewed full text |
| B2 | ucla.edu | academic | 4 | UCLA Brain Research Institute fact page |
| B3 | harvard.edu | academic | 4 | BioNumbers, Harvard Medical School; cites Drachman 2005 (Neurology) |

All sources are Tier 4–5. No low-credibility sources used.

*Source: proof.py JSON summary*

---

## Extraction Records

| Fact ID | Extracted Value | Value in Quote | Extraction Method |
|---------|----------------|----------------|-------------------|
| B1 | 8.600e+10 (86 billion) | ✓ | `extract_billion_neurons()`: regex `(\d+)\s+billion\s+neurons` on normalized text |
| B2 | 8.600e+10 (86 billion) | ✓ | `extract_billion_neurons()`: same function, independently applied |
| B3 | 7000.0 | ✓ | `extract_synapses_per_neuron()`: regex `average of ([\d,]+) synaptic connections` |

Quote snippets:
- B1: `"the adult male human brain, at an average of 1.5 kg, has 86 billion neurons and..."`
- B2: `"The human brain contains approximately 86 billion neurons, each forming thousand..."`
- B3: `"Within the liter and a half of human brain, stereologic studies estimate that th..."`

*Source: proof.py JSON summary; extraction method is author analysis*

---

## Hardening Checklist

| Rule | Status | Notes |
|------|--------|-------|
| Rule 1: Every empirical value parsed from quote text, not hand-typed | ✓ PASS | `extract_billion_neurons()` and `extract_synapses_per_neuron()` use regex + `verify_extraction()` |
| Rule 2: Every citation URL fetched and quote checked | ✓ PASS | All 3 citations verified live via `verify_all_citations()` |
| Rule 3: System time used for date-dependent logic | N/A | No date-dependent calculations |
| Rule 4: Claim interpretation explicit with operator rationale | ✓ PASS | `CLAIM_FORMAL` with `operator_note` documenting the SC2 scope issue |
| Rule 5: Adversarial checks searched for independent counter-evidence | ✓ PASS | 3 checks; 2 break the proof (SC2 scope, SC3 empirical support) |
| Rule 6: Cross-checks used independently sourced inputs | ✓ PASS | SC1 neuron count cross-checked from B1 (PMC) and B2 (UCLA), exact agreement |
| Rule 7: Constants and formulas imported from computations.py, not hand-coded | ✓ PASS | `compare()`, `explain_calc()`, `cross_check()` used throughout |
| validate_proof.py result | PASS with warnings | 14/16 checks passed, 0 issues, 2 warnings (compound boolean assignments for sc3_holds and claim_holds — no compare() equivalent for logical conjunction) |
