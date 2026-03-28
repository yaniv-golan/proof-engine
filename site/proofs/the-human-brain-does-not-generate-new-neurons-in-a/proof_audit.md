# Audit: The human brain does not generate new neurons in adulthood.

- **Generated:** 2026-03-27
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| subject | The human brain |
| property | generates new neurons in adulthood (adult hippocampal neurogenesis, AHN) |
| operator | >= |
| threshold | 3 |
| proof\_direction | disprove |
| operator\_note | The claim asserts that adult neurogenesis does NOT occur (zero occurrence). We DISPROVE it by counting independent peer-reviewed sources that directly confirm adult neurogenesis in humans. proof\_direction='disprove': n\_confirming counts sources REJECTING the claim (i.e., confirming AHN exists). If n\_confirming >= 3 (threshold), claim\_holds=True means the disproof succeeds => verdict=DISPROVED. The threshold of 3 independent sources was chosen as a conservative minimum for scientific consensus. |

*Source: proof.py JSON summary*

---

## Fact Registry

| Fact ID | Key | Label |
|---------|-----|-------|
| B1 | moreno\_jimenez\_2019 | Moreno-Jiménez et al. 2019, Nature Medicine — primary research article: identified thousands of immature neurons in the dentate gyrus of healthy humans up to the 9th decade |
| B2 | kempermann\_2018 | Kempermann et al. 2018, Cell Stem Cell — 18-author consensus review: no reason to abandon the idea that adult-generated neurons contribute across the human life span |
| B3 | llorens\_martin\_2021 | Llorens-Martín et al. 2021, Journal of Neuroscience — primary research article: demonstrates AHN is a robust phenomenon in the human hippocampus during physiological and pathologic aging |
| A1 | — | Count of independent sources confirming adult neurogenesis in humans (rejecting the claim) |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Count of independent sources confirming adult neurogenesis in humans | sum(confirmations) = 3 | 3 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Moreno-Jiménez et al. 2019 — thousands of immature neurons in adult human hippocampus | Moreno-Jiménez et al. 2019, Nature Medicine (PubMed abstract) | https://pubmed.ncbi.nlm.nih.gov/30911133/ | "we identified thousands of immature neurons in the DG of neurologically healthy human subjects up to the ninth decade of life" | verified | full\_quote | Tier 5 (government) |
| B2 | Kempermann et al. 2018 — 18-author consensus review | Kempermann et al. 2018, Cell Stem Cell (PMC) | https://pmc.ncbi.nlm.nih.gov/articles/PMC6035081/ | "there is currently no reason to abandon the idea that adult-generated neurons make important functional contributions to neural plasticity and cognition across the human life span" | verified | full\_quote | Tier 5 (government) |
| B3 | Llorens-Martín et al. 2021 — AHN confirmed as robust phenomenon in human hippocampus | Llorens-Martín et al. 2021, Journal of Neuroscience (PMC) | https://pmc.ncbi.nlm.nih.gov/articles/PMC8018741/ | "adult neurogenesis is a robust phenomenon that occurs in the human hippocampus during physiological and pathologic aging" | verified | full\_quote | Tier 5 (government) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — Moreno-Jiménez et al. 2019 (PubMed)**
- Status: verified
- Method: full\_quote
- Fetch mode: live
- coverage\_pct: null (full\_quote match — no fragmentation needed)

**B2 — Kempermann et al. 2018 (PMC)**
- Status: verified
- Method: full\_quote
- Fetch mode: live
- coverage\_pct: null (full\_quote match)

**B3 — Llorens-Martín et al. 2021 (PMC)**
- Status: verified
- Method: full\_quote
- Fetch mode: live
- coverage\_pct: null (full\_quote match)

All three citations were fetched live and verified by full quote match. No Wayback Machine fallback was needed.

*Source: proof.py JSON summary*

---

## Computation Traces

```
  [✓] moreno_jimenez_2019: Full quote verified for moreno_jimenez_2019 (source: tier 5/government)
  [✓] kempermann_2018: Full quote verified for kempermann_2018 (source: tier 5/government)
  [✓] llorens_martin_2021: Full quote verified for llorens_martin_2021 (source: tier 5/government)
  [✓] B1: extracted immature neurons from quote
  [✓] B2: extracted adult-generated neurons from quote
  [✓] B3: extracted adult neurogenesis from quote
  compare: 3 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

| Description | n\_sources | n\_confirming | Agreement |
|-------------|-----------|--------------|-----------|
| All three sources confirm adult neurogenesis in humans | 3 | 3 | True |

The three sources are independently authored research groups across different institutions:
- B1: Moreno-Jiménez group (Spain) — primary immunohistochemical data, controlled PMD
- B2: International consortium of 18 neuroscientists across multiple countries — consensus review
- B3: Llorens-Martín group (Spain) — primary immunohistochemical data, aging focus

All three converge on the same conclusion using different angles of evidence. No shared-variable dependency exists between them.

*Source: proof.py JSON summary*

---

## Adversarial Checks (Rule 5)

**Check 1: Is there credible peer-reviewed evidence that adult human neurogenesis does NOT occur?**
- Verification performed: Searched 'Sorrells 2018 adult neurogenesis humans no evidence'. Found: Sorrells et al. 2018 (Nature 555:377-381) concluded 'neurogenesis in the dentate gyrus does not continue, or is extremely rare, in adult humans' based on 17 post-mortem controls (18-77 years) and 12 epilepsy surgical resections. This is the strongest counter-evidence in the literature.
- Finding: The Sorrells 2018 finding is attributed by the field to a methodological artifact: postmortem delay (PMD). DCX (doublecortin), the key marker for immature neurons, degrades rapidly after death. Sorrells samples had PMDs up to 48 hours; Boldrini et al. 2018 (Cell Stem Cell) used PMDs ≤26 hours and found persistent neurogenesis. Moreno-Jiménez et al. 2019 used tightly controlled PMDs (<4 hours) and found thousands of immature neurons per mm². The 18-author Kempermann et al. 2018 consensus review explicitly addressed the Sorrells controversy and concluded adult neurogenesis persists.
- **breaks\_proof: False**

**Check 2: Is adult neurogenesis confirmed only in rodents, not specifically in humans?**
- Verification performed: Searched 'adult neurogenesis absent humans but present rodents species-specific'. Reviewed: Eriksson et al. 1998 (Nature Medicine) — first human study using BrdU incorporation in post-mortem cancer patients, confirmed new neurons in adult human dentate gyrus. Spalding et al. 2013 (Cell) — used radiocarbon (14C) retrospective birthdating, confirmed new neurons in adult human hippocampus independently of any immunohistochemical markers.
- Finding: Human-specific studies using three independent methodologies — BrdU labeling (Eriksson 1998), 14C retrospective birthdating (Spalding 2013), and controlled-PMD immunohistochemistry (Moreno-Jiménez 2019, Llorens-Martín 2021) — all confirm adult neurogenesis in humans. No species-specific exclusion argument is credible.
- **breaks\_proof: False**

**Check 3: Could 'adulthood' exclude the ages studied?**
- Verification performed: Searched 'adult neurogenesis human age range decline decades'. Reviewed Moreno-Jiménez 2019 subject ages: 43–87 years. Reviewed Llorens-Martín 2021 which states persistence 'until the 10th decade of human life'. Boldrini et al. 2018 (Cell Stem Cell) found neurogenesis in subjects up to age 79.
- Finding: Neurogenesis is confirmed in subjects aged 43–87 (Moreno-Jiménez 2019) and up to the 10th decade (Llorens-Martín 2021). Even under any reasonable definition of 'adulthood' (post-18, post-25, etc.), neurogenesis persists. This adversarial challenge fails.
- **breaks\_proof: False**

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | nih.gov | government | 5 | PubMed abstract of peer-reviewed Nature Medicine paper (PMID 30911133) |
| B2 | nih.gov | government | 5 | PubMed Central full text of peer-reviewed Cell Stem Cell article (PMC6035081) |
| B3 | nih.gov | government | 5 | PubMed Central full text of peer-reviewed Journal of Neuroscience article (PMC8018741) |

All sources are tier 5 (government domain). The underlying journals — *Nature Medicine*, *Cell Stem Cell*, and *Journal of Neuroscience* — are peer-reviewed publications with high impact factors in the neuroscience field.

*Source: proof.py JSON summary*

---

## Extraction Records

| Fact ID | Extracted Value | Found in Quote | Quote Snippet |
|---------|----------------|----------------|---------------|
| B1 | "immature neurons" (keyword confirmed) | True | "we identified thousands of immature neurons in the DG of neurologically healthy " |
| B2 | "adult-generated neurons" (keyword confirmed) | True | "there is currently no reason to abandon the idea that adult-generated neurons ma" |
| B3 | "adult neurogenesis" (keyword confirmed) | True | "adult neurogenesis is a robust phenomenon that occurs in the human hippocampus d" |

**Extraction method:** `verify_extraction(keyword, quote, fact_id)` from `scripts/smart_extract.py`. Checks that the keyword substring appears in the quote string using Unicode-normalized matching. No custom regex was needed — all keywords are simple ASCII substrings present verbatim in the quotes.

*Source: proof.py JSON summary; extraction method — author analysis*

---

## Hardening Checklist

| Rule | Description | Status |
|------|-------------|--------|
| Rule 1 | Every empirical value parsed from quote text, not hand-typed | PASS — `verify_extraction()` used for all three B-facts; no hand-typed values |
| Rule 2 | Every citation URL fetched and quote checked | PASS — `verify_all_citations()` called; all three verified by live fetch, full\_quote method |
| Rule 3 | System time used for date-dependent logic | N/A — no date computations in this proof |
| Rule 4 | Claim interpretation explicit with operator rationale | PASS — `CLAIM_FORMAL` with `operator_note` and `proof_direction` present |
| Rule 5 | Adversarial checks searched for independent counter-evidence | PASS — three adversarial checks, including the primary counter-study (Sorrells 2018) |
| Rule 6 | Cross-checks used independently sourced inputs | PASS — three independent research groups, different methodologies |
| Rule 7 | Constants and formulas imported from computations.py, not hand-coded | PASS — `compare()` from `scripts/computations.py`; no inline formulas |
| validate\_proof.py | Static analysis result | PASS (13/14 checks, 1 warning resolved before run — missing else branch added) |

*Source: author analysis*
