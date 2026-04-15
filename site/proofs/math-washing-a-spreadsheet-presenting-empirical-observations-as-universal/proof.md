# Proof: Presenting empirical spreadsheet observations as universal theorems violates the hypothetico-deductive method as defined by mainstream philosophy of science.

- **Generated:** 2026-04-07
- **Verdict:** PROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

---

## Key Findings

- Three independently verified authoritative sources confirm that the hypothetico-deductive (HD) method requires steps that the practice of presenting empirical spreadsheet observations as universal theorems structurally omits.
- Popper's falsifiability criterion requires that scientific theories be testable in principle — presenting observations as universal theorems bypasses this requirement (B1 — verified).
- The Stanford Encyclopedia of Philosophy confirms that scientific method requires reasoning *beyond* observation — observation alone is insufficient (B2 — verified).
- The Catalog of Bias identifies presenting unplanned analyses as prespecified as a recognized methodological distortion (B3 — verified).

---

## Claim Interpretation

**Note: This claim was re-framed from the original.** The original claim was normative: "'Math washing' a spreadsheet (presenting empirical observations as universal theorems) is valid scientific practice." That claim could not be directly proved or disproved because "valid scientific practice" is a normative judgment. The re-framed claim is factual: it asks whether the practice violates the hypothetico-deductive method as defined by mainstream philosophy of science.

**Natural language:** Presenting empirical spreadsheet observations as universal theorems violates the hypothetico-deductive method as defined by mainstream philosophy of science.

**Formal interpretation:** The claim asserts a factual violation: the practice of presenting empirical spreadsheet observations as universal theorems omits steps that the hypothetico-deductive (HD) method requires. We count independent authoritative sources that define HD method requirements — falsifiability, reasoning beyond observation, pre-specified hypotheses — which this practice structurally omits. A threshold of 3 is used to require broad consensus across distinct philosophical and methodological traditions.

**Entailment note:** The cited sources define general requirements of the scientific method / HD method. None specifically names "spreadsheet observations presented as theorems." The entailment bridge is: (1) the HD method requires steps X, Y, Z; (2) presenting observations as universal theorems without hypothesis formation, falsifiability testing, or pre-specified analysis omits X, Y, Z; therefore (3) the practice violates the HD method. This inference is logically valid but requires the author-reasoning bridge documented here.

**Formalization scope:** "Universal theorem" is interpreted strictly — a claim of deductive necessity holding without exception, not a statistical regularity or empirical generalization. "Violates" means the practice omits one or more requirements that the HD method mandates. The proof does not address whether the practice might be valid under non-HD frameworks (e.g., pure inductivism); adversarial check 1 addresses this limitation.

*Source: proof.py JSON summary*

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Britannica: Popper's falsifiability criterion — scientific theories must be falsifiable in principle | Yes |
| B2 | Stanford Encyclopedia of Philosophy: scientific method requires reasoning beyond observation | Yes |
| B3 | Catalog of Bias: presenting unplanned analyses as prespecified is a recognized methodological distortion | Yes |
| A1 | Count of authoritative sources confirming HD method requirements that the practice omits | Computed: 3 sources confirmed — meets threshold of 3 independent authorities |

---

## Proof Logic

The proof establishes that presenting empirical spreadsheet observations as universal theorems violates the hypothetico-deductive method by showing that three independent authoritative sources each identify a distinct HD method requirement that this practice omits.

The `n_confirmed` value is **derived from citation verification results**, not hardcoded. Three sources are checked: each must be verified to count toward the threshold of 3.

1. **B1** — Encyclopaedia Britannica's article on Popper's criterion of falsifiability states that *"a theory is genuinely scientific only if it is possible in principle to establish that it is false."* Presenting empirical observations as universal theorems makes no provision for falsifiability — the observations are treated as self-evidently true rather than as claims that could in principle be shown false. This omits the falsifiability requirement of the HD method.

2. **B2** — The Stanford Encyclopedia of Philosophy's article on scientific method states that *"scientific method requires a logic as a system of reasoning for properly arranging, but also inferring beyond, what is known by observation."* Presenting spreadsheet observations as theorems treats observation as sufficient, omitting the requirement for reasoning beyond observation — hypothesis formation, deductive prediction, and testing.

3. **B3** — The Catalog of Bias defines data-dredging as *"a distortion that arises from presenting the results of unplanned statistical tests as if they were a fully prespecified course of analyses."* Presenting spreadsheet observations as universal theorems follows exactly this pattern: unplanned pattern-finding is presented as if it were a prespecified, hypothesis-driven result.

**Logical chain:**
(1) Three independently verified sources each identify a distinct HD method requirement that the practice omits → (2) `compare(n_confirmed=3, ">=", 3)` → True → (3) The claim holds: the practice violates the HD method as defined by mainstream philosophy of science.

*Source: author analysis*

---

## Counter-Evidence Search

Three adversarial checks were performed before writing this proof:

**1. Is there a scientific tradition that validates presenting inductive generalizations from data as universal laws without further testing?**
Searched for defenses of inductivism and found Bacon's inductivism as the strongest candidate. Even Bacon's model requires systematic collection, replication, and elimination of observer bias before generalizing. Naive inductivism has been largely discredited in philosophy of science (Popper 1934, Hempel 1965). More importantly, no form of inductivism endorses presenting patterns as universal "theorems" (a term implying deductive necessity) rather than empirical generalizations. This check does not break the proof but limits the verdict's scope: the proof establishes violation of the HD method specifically, not all possible philosophies of science.

**2. Does Exploratory Data Analysis (EDA) validate presenting spreadsheet patterns as scientific findings?**
Reviewed EDA methodology documentation and found that EDA (Tukey 1977) is an explicitly hypothesis-generating practice, not hypothesis-confirming. Tukey's framework produces candidate hypotheses for subsequent testing, not universal theorems. The EDA literature itself distinguishes pattern-finding from universal claims.

**3. Could "math washing" be valid in limited empirical domains like actuarial science, empirical economics, or physics phenomenology?**
Searched for domain-specific practices. Empirical economics explicitly distinguishes between "stylized facts" (regularities observed in data) and economic laws or theorems. Kaldor (1961) introduced "stylized facts" precisely because observed patterns do not constitute universal theorems without theoretical grounding. Even in phenomenological physics, empirical regularities (e.g., Kepler's laws) were only elevated to scientific law status after being derived from deeper theoretical principles (Newton's mechanics). No domain endorses presenting data patterns as universal theorems directly.

None of these checks produce counter-evidence that breaks the proof.

*Source: proof.py JSON summary*

---

## Conclusion

**Verdict: PROVED**

Three independently verified authoritative sources — from encyclopedic philosophy (B1), academic philosophy (B2), and scientific methodology (B3) — each confirm a distinct requirement of the hypothetico-deductive method that the practice of presenting empirical spreadsheet observations as universal theorems structurally omits: falsifiability, reasoning beyond observation, and pre-specified hypotheses. All three citations were verified by live fetch with full quote match (3/3, threshold >= 3).

Note: One citation (B3, catalogofbias.org) comes from an unclassified domain (credibility tier 2). See Source Credibility Assessment in the [audit trail](proof_audit.md). The Catalog of Bias is maintained by the Centre for Evidence-Based Medicine at the University of Oxford, but its domain is not classified in the credibility database. The proof's conclusion does not depend solely on B3 — the two higher-tier sources (B1 tier 3, B2 tier 4) independently establish the violation.

Note: The cited sources state general principles of the HD method, not specifically naming "spreadsheet observations presented as theorems." The proof relies on an author-reasoning bridge connecting these general principles to the specific practice. This entailment gap is documented in the Claim Interpretation section.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.8.0 on 2026-04-07.*
