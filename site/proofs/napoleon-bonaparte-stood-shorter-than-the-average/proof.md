# Proof: Napoleon Bonaparte stood shorter than the average Frenchman of his era.

- **Generated:** 2026-03-28
- **Verdict:** DISPROVED (with unverified citations)
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Key Findings

- Napoleon's height was approximately **1.67-1.68 meters** (5'6"-5'7") based on multiple independent sources, after correcting for the difference between French and English measurement units.
- The average French male height in Napoleon's era (1800-1820) was approximately **1.641-1.65 meters** (5'4"-5'5").
- Even using the most conservative estimate for Napoleon (1.67m) and the most generous estimate for the average (1.65m), Napoleon was approximately **2 cm taller** than the average Frenchman.
- The widespread belief that Napoleon was short originated from confusion between French and English inches and British propaganda cartoons, not from his actual stature.

## Claim Interpretation

The claim "Napoleon Bonaparte stood shorter than the average Frenchman of his era" is interpreted as: Napoleon's height was strictly less than the average height of French men during his lifetime (1769-1821). Napoleon's height was recorded in pre-metric French units (pieds and pouces), where the French pouce (inch) was 2.71 cm compared to the English inch at 2.54 cm. His recorded "5 pieds 2 pouces" translates to approximately 168 cm in modern units, not the 157 cm a naive English conversion would yield. If Napoleon's height equals or exceeds the French average, the claim is disproved.

*Source: proof.py JSON summary*

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Britannica: Napoleon's height at death (~1.68m) and average French male height in 1820 (~1.65m) | Partial (fragment match, 47.4% coverage; data values confirmed on page) |
| B2 | History.com: Napoleon's height ~1.67m, above average for early 1800s French men | Partial (aggressive normalization; data values confirmed on page) |
| B3 | Napoleon Series: Average French male height 1800-1820 was 164.1 cm | Yes |
| B4 | Britannica: Napoleon average or taller, most Frenchmen 5'2"-5'6" | Yes |
| A1 | Comparison: Napoleon's height vs average French male height | Computed: Napoleon (1.67m) > avg French (1.65m) — claim is false |
| A2 | Cross-check: Napoleon's height vs average using second source pair | Computed: Both Napoleon heights (1.68m vs 1.67m) and average heights (1.65m vs 1.641m) agree across independent sources |

*Source: proof.py JSON summary*

## Proof Logic

Napoleon's height is established by two independent sources:
- **Encyclopaedia Britannica (B1)** reports Napoleon measured about 1.68 meters at the time of his death in 1821.
- **History.com (B2)** reports that three French contemporaries (his valet Constant, General Gourgaud, and physician Antommarchi) recorded Napoleon at just over "5 pieds 2 pouces," which converts to approximately 1.67 meters.

These two values agree within 1 cm (cross-check A2 confirms agreement within 0.02m tolerance).

The average French male height is established by two independent sources:
- **Encyclopaedia Britannica (B1)** states the average French man in 1820 was about 1.65 meters.
- **The Napoleon Series (B3)** provides anthropometric data showing French males in 1800-1820 averaged 164.1 cm.

These two values also agree within 1 cm.

Using the most conservative approach — Napoleon's lowest reported height (1.67m from B2) versus the highest reported average (1.65m from B1) — Napoleon was still **2 cm taller** than the average Frenchman (A1). The claim that Napoleon was shorter is therefore false.

Additionally, Britannica (B4) confirms that "most Frenchmen stood between 5'2" and 5'6" (1.58 and 1.68 meters)," placing Napoleon at or above the upper end of this range.

*Source: author analysis*

## Counter-Evidence Search

Three adversarial searches were conducted:

1. **Were there credible sources claiming Napoleon was below average?** Searched across History.com, Britannica, National Geographic, Washington Post, and Wikipedia. No credible source claims Napoleon was below average height. The myth is universally attributed to unit conversion confusion and British propaganda.

2. **Could the measurement conversion be wrong?** The French pouce (2.71 cm) vs English inch (2.54 cm) conversion is well-established across all scholarly sources. No credible dispute exists.

3. **Could the average French height have been higher?** No source suggests the average exceeded 166 cm. Multiple independent anthropometric studies confirm the 164-165 cm range.

*Source: proof.py JSON summary*

## Conclusion

**DISPROVED (with unverified citations).** Napoleon Bonaparte was approximately 1.67-1.68 meters tall, which was 2-4 cm *taller* than the average Frenchman of his era (~1.641-1.65 meters). The claim that Napoleon stood shorter than the average Frenchman is a well-documented myth originating from confusion between French and English measurement units and propagated by British wartime caricatures.

Two citations (B1 Britannica, B2 History.com) received partial verification status due to quote-matching limitations, but the underlying data values (1.68m, 1.67m, 1.65m) were all independently confirmed on the live pages. The disproof does not depend on any unverified claim — the fully verified sources (B3, B4) independently establish the average French height and Napoleon's position relative to it.

Note: 2 citation(s) come from unclassified or low-credibility-tier sources (B2 History.com tier 2, B3 Napoleon Series tier 2). History.com is a well-known history publication by A&E Networks; The Napoleon Series is a respected Napoleonic history research site. Both are editorially credible for this claim.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
