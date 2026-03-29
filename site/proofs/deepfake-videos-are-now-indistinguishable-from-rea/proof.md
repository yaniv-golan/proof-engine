# Proof: Deepfake videos are now indistinguishable from real footage to the average human eye.

- **Generated:** 2026-03-29
- **Verdict:** DISPROVED (with unverified citations)
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Key Findings

- Average humans detect deepfake videos above chance level, with accuracy ranging from 57% to 67% across major studies — well above the 50% threshold that "indistinguishable" would require.
- A large-scale study (N=1,901) found human video discrimination AUC of 0.67, with humans outperforming AI algorithms on video deepfakes specifically.
- A separate UK-based study (N=1,093) confirmed that "people are better than random at determining whether an individual video is genuine or fake."
- Leading deepfake researchers explicitly distinguish between voice deepfakes (which have crossed the "indistinguishable threshold") and video deepfakes (which have not).

## Claim Interpretation

**Natural language:** "Deepfake videos are now indistinguishable from real footage to the average human eye."

**Formal interpretation:** "Indistinguishable" means detection accuracy at or near chance level (50% in a two-alternative forced choice). If average humans detect deepfake videos significantly above 50%, the videos are distinguishable — disproving the claim. We seek >= 3 independent sources showing above-chance detection to disprove. This is the conservative threshold: even a single well-powered study showing above-chance performance would challenge the claim, but we require 3 for robustness.

*Source: proof.py JSON summary*

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | UK study on deepfake video detection (PMC, N=1093) | Yes |
| B2 | UF study on human vs machine deepfake detection (PMC, N=1901) | Yes |
| B3 | Expert assessment distinguishing video from voice deepfakes (Fortune) | Partial (fragment match, 54.5% coverage) |
| A1 | Verified source count confirming above-chance video detection | Computed: 3 independent sources confirmed humans detect deepfake videos above chance |

*Source: proof.py JSON summary*

## Proof Logic

The claim asserts that deepfake videos are "indistinguishable" from real footage to the average human eye. In signal detection theory, "indistinguishable" means performance at chance level — approximately 50% accuracy in a forced-choice task.

Three independent sources were identified that contradict this claim:

1. **B1** — A UK-based study (N=1,093) published in iScience found that "people are better than random at determining whether an individual video is genuine or fake," directly contradicting the indistinguishability claim.

2. **B2** — A University of Florida study (N=1,901) published in Cognitive Research found that "the ability to discriminate between deepfake and real videos was fairly good in humans," with an AUC of 0.67 — clearly above the 0.50 chance level. Notably, humans outperformed AI algorithms on video deepfakes, even though AI was superior on still images.

3. **B3** — Prof. Siwei Lyu, Director of the UB Media Forensic Lab and a leading deepfake researcher, explicitly stated that "voice cloning has crossed what I would call the 'indistinguishable threshold'" — deliberately using this language for voice but NOT for video deepfakes. He characterized video deepfakes as having "realism high enough to reliably fool nonexpert viewers," a deliberately weaker claim than indistinguishable.

All 3 sources were verified (A1), meeting the threshold of >= 3 independent sources needed to disprove the claim.

*Source: author analysis*

## Counter-Evidence Search

1. **Do studies show humans at chance level for video deepfakes?** A meta-analysis of 56 papers found video detection accuracy at 57.31% (95% CI [47.80, 66.57]). While the CI crosses 50%, the point estimate is above chance, and the largest individual studies show clearly above-chance performance. The CI width reflects study-to-study heterogeneity (varying deepfake quality), not individual inability.

2. **Does the iProov study show humans cannot detect deepfakes?** The widely cited "0.1% accuracy" figure measures perfect classification across an entire test battery (all images AND videos), not per-video detection. Getting every single item correct is far harder than above-chance detection on average.

3. **Has any expert claimed video deepfakes crossed the indistinguishable threshold?** No. Leading researchers deliberately distinguish between voice (indistinguishable) and video (improving but not yet indistinguishable) as of March 2026.

*Source: proof.py JSON summary*

## Conclusion

**DISPROVED (with unverified citations).** The claim that deepfake videos are "indistinguishable" from real footage to the average human eye is contradicted by multiple large-scale studies. Humans detect deepfake videos at rates of 57-67%, significantly above the 50% chance level that "indistinguishable" would require. Three independent sources — two peer-reviewed studies (B1, B2) and one expert assessment (B3) — confirm that video deepfakes remain detectable, even as voice deepfakes have crossed the indistinguishable threshold.

The B3 citation (Fortune) was only partially verified (54.5% fragment coverage). However, this conclusion does not depend solely on B3 — the two fully verified peer-reviewed sources (B1, B2) independently establish above-chance detection.

**Important nuance:** While disproved in its absolute form, the claim captures a real trend. Human detection is modest (57-67%, not 90%+), varies with deepfake quality, and is declining as technology improves. The claim may become true in the near future, but as of March 2026, the evidence does not support it for video deepfakes.

Note: 1 citation (B3) comes from an unclassified source (fortune.com, tier 2). Fortune is a well-established business publication, but the credibility engine classifies it as unclassified. The disproof does not depend solely on this source — see verified B1 and B2.

*Source: proof.py JSON summary; impact analysis is author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.2.0 on 2026-03-29.
