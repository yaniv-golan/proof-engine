# Proof: Deepfake videos are now indistinguishable from real footage to the average human eye.

- **Generated:** 2026-03-28
- **Verdict:** UNDETERMINED
- **Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

---

## Key Findings

- The most comprehensive meta-analysis of human deepfake detection (56 papers, 86,155 participants, 2024) found overall accuracy of **55.54%** with a 95% confidence interval of **[48.87, 62.10]** that crosses 50% — not statistically significantly above chance.
- For **video deepfakes specifically**, the meta-analysis found **57.31%** detection accuracy (CI [47.80, 66.57]) — also crossing 50% and not significant.
- However, three independent studies — including a large PNAS study (N=15,016, 2022) and a 2025 peer-reviewed study — show human video detection at **63–67%**, clearly above chance.
- The claim cannot be definitively proved or disproved: the meta-analytic evidence supports near-chance performance, but individual studies with dedicated video stimuli consistently show above-chance detection.

---

## Claim Interpretation

**Natural language:** "Deepfake videos are now indistinguishable from real footage to the average human eye."

**Formal interpretation:** "Average, untrained humans cannot reliably distinguish deepfake videos from real footage — i.e., detection accuracy is near chance (~50%) and not statistically significantly above chance in controlled studies."

**Operator:** `>=` (threshold: 3 independent peer-reviewed sources confirming near-chance video detection)

**Rationale:** "Indistinguishable" is interpreted as humans performing at near-chance level on video deepfake detection. A score of 50% means pure guessing. The claim is formalised as: do at least 3 independent sources confirm that average humans cannot reliably detect video deepfakes? Counter-evidence (above-chance detection) is evaluated through adversarial checks. Note: the claim is specifically about *video* deepfakes, not static images (where evidence of chance-level performance is stronger).

*Source: proof.py JSON summary*

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Diel et al. (2024) meta-analysis of 56 papers (86,155 participants): video detection CI crosses 50% — not significantly above chance | No (URL returned 403 — paywalled ScienceDirect) |
| B2 | Köbis et al. (2021) "Fooled Twice" RCT (N=210): people cannot reliably detect deepfakes; only 5/16 videos detectable above chance | Partial (fragment match on PMC) |
| B3 | Köbis et al. (2021) "Fooled Twice" ScienceDirect mirror: "seeing-is-believing" heuristic; training and incentives do not improve detection | No (URL returned 403 — paywalled ScienceDirect) |
| A1 | Verified source count meeting near-chance confirmation threshold | Computed: 1 confirmed source of 3 required; adversarial check breaks proof (video detection above chance in multiple studies) |

*Source: proof.py JSON summary*

---

## Proof Logic

The claim requires at least 3 independently verified peer-reviewed sources confirming that average humans detect video deepfakes near chance level.

**B1** (Diel et al. 2024, meta-analysis): The most comprehensive evidence available — 56 papers, 86,155 participants, pooled across modalities. Overall accuracy 55.54% (CI [48.87, 62.10]). For video specifically: 57.31% (CI [47.80, 66.57]). Both confidence intervals cross 50%, meaning the meta-analysis cannot conclude that detection is significantly above chance. This is the strongest single piece of evidence supporting the claim.

**B2/B3** (Köbis et al. 2021, "Fooled Twice"): In a pre-registered RCT with N=210, "people cannot reliably detect deepfakes and neither raising awareness nor introducing financial incentives improves their detection accuracy." Although the reported overall accuracy of 57.6% was statistically above chance (p < .001), closer analysis showed only 5 of 16 individual videos were detectable above chance — the rest were near-random. The conclusion states: "people can no longer reliably detect deepfakes."

**However**, a threshold of 3 confirmed sources was not reached: only 1 source (B2, partial) was verified, versus the 3 required. More critically, the adversarial check (below) found direct counter-evidence that breaks the proof.

*Source: author analysis*

---

## Counter-Evidence Search

**Do studies show humans detect VIDEO deepfakes reliably above chance?**

Yes — this is the most important adversarial finding. Three independent studies show video detection at 63–67%:

1. **Groh et al. (2022), PNAS** (N=15,016): Participants achieved 66% accuracy on video deepfakes. "Ordinary human observers perform in the range of the leading machine learning model."
2. **Köbis et al. (2025), PMC** ("Is this real?"): Human video detection AUC = 0.67, 63% accuracy. "The ability to discriminate between deepfake and real videos was fairly good in humans."
3. **University of Florida study (February 2026)**: "humans correctly identified real and fake videos about two-thirds of the time," outperforming AI algorithms. Researcher quote: "But people still have an advantage when it comes to identifying deepfake videos."

These results directly contradict the claim that videos are "indistinguishable." The meta-analysis (B1) shows video detection CI crossing 50%, but the CI is wide ([47.80, 66.57]), reflecting high study heterogeneity rather than a consensus of chance-level detection. Individual well-controlled video studies consistently show above-chance performance.

**Is the claim specifically about newest-generation (2025–2026) deepfakes?**

Possibly. The "now" qualifier in the claim could apply to state-of-the-art 2025–2026 deepfakes (e.g., from tools like Sora or HeyGen), which may be harder to detect than older FaceForensics++ footage used in academic studies. No peer-reviewed academic study specifically measuring detection of 2025–2026 generation deepfakes was found. A commercial study by iProov (2024) claims only 0.1% of people can detect AI-generated deepfakes, but uses opaque methodology from a company that sells detection products. This is an evidence gap, not direct counter-evidence.

**Does the meta-analysis' wide CI invalidate the individual studies?**

No — the CI crossing 50% reflects high between-study heterogeneity (studies differ in deepfake type, quality, and design), not a conclusion that all studies found chance-level performance. Individual well-controlled video studies consistently show above-chance detection. The meta-analytic result is inconclusive rather than supportive.

*Source: proof.py JSON summary (adversarial_checks)*

---

## Conclusion

**Verdict: UNDETERMINED**

The evidence is genuinely divided:

- **Supporting the claim:** The most comprehensive meta-analysis (56 studies, 86K participants) shows video deepfake detection at 57.31%, with a confidence interval that crosses 50% — not statistically significantly above chance. One large RCT found "people can no longer reliably detect deepfakes," with only 5 of 16 videos individually detectable.

- **Against the claim:** Three independent peer-reviewed/institutional studies show humans detect video deepfakes at 63–67% accuracy — clearly above the 50% chance threshold. This includes a large PNAS study (N=15,016) and a 2025 PMC study specifically focused on videos.

The weight of individual video-focused studies suggests humans *can* detect video deepfakes above chance, but the effect is modest. The claim "indistinguishable" (implying ~50% detection) overstates what the evidence shows for video. However, the meta-analytic evidence is inconclusive enough that DISPROVED would also be too strong.

**What would resolve this:**
1. A large-scale peer-reviewed study specifically using 2025–2026 generation deepfakes with naive participants
2. A meta-analysis restricted to video-only studies with careful quality controls

Note: 2 of 3 cited sources (B1, B3) could not be machine-verified due to paywall (ScienceDirect 403), though both are real, peer-reviewed publications indexed in major academic databases. The adversarial break that drives the UNDETERMINED verdict does not depend on these sources.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
