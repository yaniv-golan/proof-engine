# Proof: The human brain does not generate new neurons in adulthood.

- **Generated:** 2026-03-27
- **Verdict:** DISPROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

---

## Key Findings

- **3 of 3** independent peer-reviewed sources directly confirm that the human brain generates new neurons in adulthood — meeting the threshold of ≥ 3 required to disprove the claim.
- Moreno-Jiménez et al. 2019 (*Nature Medicine*) identified **thousands of immature neurons** in the dentate gyrus of neurologically healthy humans up to the 9th decade of life (B1, verified).
- Kempermann et al. 2018 (*Cell Stem Cell*, 18 co-authors) concluded there is **"no reason to abandon the idea that adult-generated neurons make important functional contributions to neural plasticity and cognition across the human life span"** (B2, verified).
- Llorens-Martín et al. 2021 (*Journal of Neuroscience*) concluded that **"adult neurogenesis is a robust phenomenon that occurs in the human hippocampus"** and persists until the 10th decade of life (B3, verified).
- All three citations were verified by live fetch against the source pages (tier 5 / government domain, nih.gov).

---

## Claim Interpretation

**Natural language claim:** "The human brain does not generate new neurons in adulthood."

**Subject:** The human brain
**Property:** Generates new neurons in adulthood (adult hippocampal neurogenesis, AHN)

**Formal interpretation:** The claim asserts that adult hippocampal neurogenesis (AHN) does not occur (zero occurrence). To disprove it, we count independent peer-reviewed sources that directly confirm AHN in humans. If n\_confirming ≥ 3 (threshold), the disproof succeeds.

**Operator note:** This is a disproof proof (`proof_direction = "disprove"`). `claim_holds = True` means the disproof holds — i.e., the claim is FALSE. The threshold of 3 independent sources was chosen as a conservative minimum for scientific consensus. Requiring only 1 source would risk being overturned by a single replication failure; 3 is a well-established minimum for scientific credibility across independent studies.

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Moreno-Jiménez et al. 2019, *Nature Medicine* — thousands of immature neurons identified in human dentate gyrus up to the 9th decade | Yes |
| B2 | Kempermann et al. 2018, *Cell Stem Cell* — 18-author consensus review; no reason to abandon adult-generated neurons across the life span | Yes |
| B3 | Llorens-Martín et al. 2021, *Journal of Neuroscience* — AHN is a robust phenomenon in the human hippocampus during physiological and pathologic aging | Yes |
| A1 | Count of independent sources confirming adult neurogenesis in humans (n\_confirming) | Computed: 3 |

*Source: proof.py JSON summary*

---

## Proof Logic

The claim rests on the old neuroscience dogma that the adult mammalian brain is post-mitotic — that no new neurons are generated after development. This dogma began to break down in the 1990s.

**Three independent lines of evidence disprove the claim:**

**B1 — Moreno-Jiménez et al. 2019 (Nature Medicine).** Using human brain samples obtained under tightly controlled postmortem delay (PMD < 4 hours) combined with state-of-the-art tissue processing, the authors "identified thousands of immature neurons in the DG of neurologically healthy human subjects up to the ninth decade of life." The subjects ranged in age from 43 to 87 years — spanning the full breadth of conventional adulthood. This is the strongest primary-evidence source, because the methodology directly addresses the main contested variable in the field (tissue fixation quality).

**B2 — Kempermann et al. 2018 (Cell Stem Cell).** This 18-author consensus review was published specifically in response to conflicting reports (including Sorrells 2018, discussed below). The authors surveyed the full state of the field and concluded: "there is currently no reason to abandon the idea that adult-generated neurons make important functional contributions to neural plasticity and cognition across the human life span." The breadth of authorship (18 leading researchers across multiple institutions) gives this source exceptional weight as a scientific consensus statement.

**B3 — Llorens-Martín et al. 2021 (Journal of Neuroscience).** This primary research article presents direct immunohistochemical evidence and states: "adult neurogenesis is a robust phenomenon that occurs in the human hippocampus during physiological and pathologic aging." The study also documents that AHN persists until the 10th decade of human life and is impaired in Alzheimer's disease, establishing clinical relevance.

All three sources are independently authored, use different methodologies, and converge on the same conclusion: the human brain does generate new neurons in adulthood. Source count: n\_confirming = 3 ≥ 3 (threshold) → claim\_holds = True → **DISPROVED**.

---

## Counter-Evidence Search

**1. Is there credible evidence that adult neurogenesis does NOT occur?**

Yes — Sorrells et al. 2018 (*Nature* 555:377–381) is the most prominent counter-evidence. Using 17 post-mortem controls (age 18–77) and 12 surgical resections from epilepsy patients, the authors concluded that "neurogenesis in the dentate gyrus does not continue, or is extremely rare, in adult humans."

However, the field has traced this negative result to a methodological artifact: postmortem delay (PMD). Doublecortin (DCX), the primary immunohistochemical marker for immature neurons, degrades rapidly after death. The Sorrells samples had PMDs of up to 48 hours. Boldrini et al. 2018 (*Cell Stem Cell*), published the same month, found persistent neurogenesis using PMDs ≤ 26 hours. Moreno-Jiménez et al. 2019 used PMDs < 4 hours and found thousands of immature neurons. The 18-author Kempermann et al. 2018 review explicitly addressed the Sorrells controversy and concluded adult neurogenesis persists. The Sorrells finding does not break the disproof.

**2. Is adult neurogenesis confirmed only in rodents, not humans specifically?**

No. Multiple human-specific studies using independent methodologies confirm AHN in humans: Eriksson et al. 1998 (*Nature Medicine*) used BrdU incorporation in post-mortem cancer patients; Spalding et al. 2013 (*Cell*) used radiocarbon (14C) retrospective birthdating — an approach entirely independent of immunohistochemical markers. These human-specific findings rule out a species-specificity exclusion.

**3. Could "adulthood" be interpreted to exclude the ages studied?**

No. Moreno-Jiménez 2019 confirmed neurogenesis in subjects aged 43–87; Llorens-Martín 2021 documents persistence "until the 10th decade of human life." Under any conventional definition of adulthood (post-18, post-25, or otherwise), neurogenesis persists well into the range studied.

---

## Conclusion

**Verdict: DISPROVED**

The claim "The human brain does not generate new neurons in adulthood" is **disproved** by three independent peer-reviewed sources (B1, B2, B3), all fully verified by live page fetch. Adult hippocampal neurogenesis (AHN) — the generation of new neurons in the dentate gyrus of the hippocampus — has been confirmed in neurologically healthy adult humans using immunohistochemistry with controlled postmortem delay, BrdU labeling, and radiocarbon birthdating. The phenomenon persists from middle age into the 9th–10th decades of life.

The strongest counter-evidence (Sorrells 2018) is credibly explained as a tissue fixation artifact, and is explicitly rejected by the 18-author consensus review (B2). No citation in this proof is from a low-credibility source (all are tier 5 / government domain via PubMed Central and PubMed).
