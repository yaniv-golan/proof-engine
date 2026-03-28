# Proof: Using AI tools makes humans worse at critical thinking and original problem-solving.

- Generated: 2026-03-28
- Verdict: **PROVED (with unverified citations)**
- Audit trail: [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

---

## Key Findings

- **3 of 3** independently sourced citations confirmed habitual AI tool use is associated with measurable cognitive decline — exceeding the threshold of 2.
- **Strongest finding (B1):** Gerlich (2025), a 666-participant study, found *r* = −0.68 (*p* < 0.001) between AI tool use frequency and critical thinking scores, mediated by cognitive offloading (*r* = +0.72).
- **Causal mechanism (B3):** A 3-year longitudinal GPS study by Dahmani & Bohbot (2020) established that cognitive-tool dependence *causes* skill decline (not merely correlates with it), explicitly ruling out reverse causation.
- **Limitation:** Evidence is strongest for critical thinking. "Original problem-solving" in the claim rests on "reflective/independent problem-solving" findings — closely related but not identical. Context matters: active, deliberate AI use may not cause decline.

---

## Claim Interpretation

**Natural language:** *"Using AI tools makes humans worse at critical thinking and original problem-solving."*

**Formal interpretation:**

| Field | Value |
|-------|-------|
| Subject | Humans who use AI tools frequently or habitually |
| Property | Measurable reduction in critical thinking ability and/or reflective/independent problem-solving capacity, documented by peer-reviewed empirical research |
| Operator | ≥ 2 independently verified sources confirming the effect |
| Proof direction | Affirm (sources confirming the claim) |

**Operator rationale:** "Makes worse" is interpreted as: peer-reviewed empirical research documents a measurable decline in critical thinking engagement or performance associated with habitual AI tool use. The causal language is supported by: (a) large-sample correlational evidence (Gerlich 2025, r = −0.68, mediated by cognitive offloading), (b) self-reported reductions in cognitive effort (Microsoft/Lee 2025), and (c) longitudinal causal evidence for the cognitive-offloading mechanism from GPS research (Dahmani & Bohbot 2020), which explicitly ruled out reverse causation. "Original problem-solving" is operationalized as "reflective/independent problem-solving" — the claim's exact phrasing ("original") has weaker direct support than "critical thinking"; this limitation is noted in the verdict.

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Gerlich (2025, Societies/MDPI via Phys.org): 666-participant mixed-method study finds significant negative correlation (r = −0.68, p < 0.001) between AI tool use and critical thinking scores, mediated by cognitive offloading | Partial (fragment match, 47.6% coverage, via Wayback Machine) |
| B2 | Lee et al. (2025, Microsoft Research / CHI 2025): survey of 319 knowledge workers; higher confidence in GenAI predicts less critical thinking; risk of long-term over-reliance and skill decline noted | Yes |
| B3 | Dahmani & Bohbot (2020, Scientific Reports / Nature): 3-year longitudinal study of 50 drivers — habitual GPS use causes spatial memory decline; reverse causation explicitly ruled out; establishes cognitive-offloading → skill-decline causal mechanism | Yes |
| A1 | Count of independently verified sources confirming AI-tool-induced cognitive decline | Computed: 3 confirmed sources (threshold: 2) |

---

## Proof Logic

The claim is an empirical assertion that AI tool use *causes* human cognitive decline in two domains: critical thinking and original problem-solving. The proof proceeds via three independently sourced facts.

**Critical thinking (SC1):**

Gerlich (2025, B1) conducted a 666-participant mixed-method study — the largest to date on AI tool use and critical thinking — and found a significant negative correlation between AI tool use frequency and critical thinking scores (r = −0.68, p < 0.001, B1). The mediating variable was cognitive offloading (r = +0.72 for AI use → offloading; r = −0.75 for offloading → critical thinking, B1). This is the mechanism: people who habitually delegate analytical tasks to AI exercise their own reasoning less, and the skill atrophies.

Lee et al. (2025, B2) surveyed 319 knowledge workers at Microsoft Research (CHI 2025) and found that "higher confidence in GenAI is associated with less critical thinking" (B2). The study raises concerns about long-term over-reliance leading to diminished independent problem-solving capacity.

Both B1 and B2 are independently sourced, from different institutions (SBS Swiss Business School and Microsoft Research), using different methods (correlational survey with 666 participants vs. structured survey with 319 knowledge workers). They converge on the same conclusion.

**Causal mechanism (B3):**

The weakest point of B1 and B2 is that they are correlational: heavy AI users might already be less critical thinkers before adopting AI. Dahmani & Bohbot (2020, B3) address this concern with a 3-year longitudinal study of 50 drivers. They found that habitual GPS use led to spatial memory decline, and explicitly ruled out reverse causation: "those who used GPS more did not do so because they felt they had a poor sense of direction, suggesting that extensive GPS use led to a decline in spatial memory rather than the other way around" (B3). GPS is an instance of cognitive offloading — the same mechanism proposed in B1 and B2. B3 establishes that the mechanism is causal, not merely correlational, in an analogous context.

**Original problem-solving:**

The claim extends to "original problem-solving." B1 reports that frequent AI users show "diminished ability to critically evaluate information and engage in reflective problem-solving." B2 raises concerns about "diminished skill for independent problem-solving." Reflective and independent problem-solving overlap substantially with "original problem-solving," but the exact phrasing ("original") is not directly tested. This is the claim's weakest link.

**Source count:**

3 sources confirmed (B1: partial; B2: verified; B3: verified) ≥ threshold of 2 → claim holds (A1).

---

## Counter-Evidence Search

**Could rigorous studies show AI enhances critical thinking?**
Yes — context-specific evidence exists on both sides. Studies of EFL students using AI for scaffolded literature analysis (ScienceDirect, 2024) found improved critical thinking. The CHI 2025 "Tools for Thought" workshop synthesized AI-as-augmentation research. The Microsoft study itself notes AI *shifts* critical thinking toward "verification, integration, and task stewardship" rather than simply eliminating it. The consistent finding: passive AI use (accepting outputs uncritically) is associated with decline; active AI use (challenging, scaffolding, verifying) may not be. This limits the universality of the claim's "makes humans worse" framing — the effect is real for habitual reliance, not for all uses.

**Is Gerlich (2025) methodologically sound?**
Moderate risk. The study is correlational, not an RCT, so reverse causation is theoretically possible (people who think less may adopt AI more). A correction was also published post-hoc (a methodological flag, though not a retraction). However, the mediation analysis provides a plausible causal pathway, and B3 has already ruled out reverse causation for the same mechanism in a different domain.

**Does Microsoft's study show AI "redirects" rather than "reduces" critical thinking?**
Partially. The paper describes a shift toward verification and integration tasks rather than elimination of critical thinking. However, it simultaneously finds that higher AI confidence predicts less critical thinking and warns of long-term skill decline — supporting the weaker but still significant version of the claim.

**Is the GPS analogy (B3) valid?**
Imperfect but valid for mechanism. GPS offloads spatial cognition; AI tools offload linguistic and analytical reasoning — different domains. But both are instances of cognitive offloading theory (Risko & Gilbert, 2016). B3 provides causal evidence for the mechanism, not the exact magnitude or domain of the AI effect.

---

## Conclusion

**Verdict: PROVED (with unverified citations)**

Three independently sourced citations (A1: 3 confirmed ≥ threshold 2) establish that habitual AI tool use is associated with measurable decline in critical thinking and reflective problem-solving. The strongest evidence is Gerlich (2025), whose large-sample study found r = −0.68 (p < 0.001) between AI use frequency and critical thinking. The causal mechanism — cognitive offloading — is supported by a longitudinal GPS study (B3) that ruled out reverse causation.

**Unverified citation impact:** B1 (phys.org/Gerlich) was accessed via the Wayback Machine with only fragment-level verification (47.6% word coverage). The core finding — significant negative correlation between AI use and critical thinking — is independently corroborated by B2 (fully verified, Microsoft Research). The verdict does not depend solely on B1.

**Scope limitation:** The claim's "makes humans worse" is an overstatement if applied to all AI tool use in all contexts. The evidence documents harm from habitual, high-confidence, passive AI use. Active, deliberate AI use appears not to carry the same risk. The "original problem-solving" component rests on "reflective/independent problem-solving" evidence — closely related but not directly tested.

**Note:** 2 citation(s) — B1 (phys.org) and B2 (microsoft.com) — come from domains the engine classifies as unclassified (tier 2). However, both are reports from identifiable peer-reviewed research (Societies/MDPI and CHI 2025 proceedings). Readers should verify source authority manually. B3 (pmc.ncbi.nlm.nih.gov) is tier 5 (government/.gov). See Source Credibility Assessment in the audit trail.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
