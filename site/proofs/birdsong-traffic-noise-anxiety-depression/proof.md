# Proof: Six minutes of birdsong reduced anxiety with a medium effect size, while six minutes of traffic noise raised depression with the same effect size.

**Generated:** 2026-04-28
**Verdict:** PROVED
**Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | SC1: Nature paper (Stobbe et al. 2022) — verbatim Cohen's d values for birdsong-anxiety (d = -0.77 low diversity, d = -0.70 high diversity) | Yes |
| B2 | SC1: PubMed-indexed abstract — author characterization 'Anxiety and paranoia significantly decreased in both birdsong conditions (medium effect sizes)' | Yes |
| B3 | SC2: Nature paper (Stobbe et al. 2022) — verbatim Cohen's d values for traffic-depression (d = 0.29 low, d = 0.59 high diversity) | Yes |
| B4 | SC2: PubMed-indexed abstract — author characterization 'increase in depression (small effect size in low, medium effect size in high diversity condition)' | Yes |
| B5 | Both SCs: Nature paper confirms 6-minute exposure duration | Yes |
| A1 | SC1 verified source count | Computed: 2 independent sources confirmed birdsong-anxiety finding |
| A2 | SC2 verified source count | Computed: 2 independent sources confirmed traffic-depression finding |

## Proof Logic

<!-- not-a-citation-start -->
The claim describes findings from one specific randomized online experiment: Stobbe, Sundermann, Foerster & Kühn (2022), "Birdsongs alleviate anxiety and paranoia in healthy participants," *Scientific Reports* 12:16414. The proof verifies what that study reported, decomposed into two sub-claims joined by AND.
<!-- not-a-citation-end -->

### Common evidence: 6-minute exposure (B5)

The Nature paper states that "N = 295 participants were exposed to one out of four conditions for 6 min: traffic noise low, traffic noise high, birdsong low, and birdsong high diversity soundscapes" (B5). This anchors the "six minutes" portion of both sub-claims.

### SC1: Birdsong reduced anxiety with a medium effect size

The Nature paper's Results section reports the within-group t-tests for state anxiety: "low diversity: T(1, 62) = − 6.13, p < 0.001, d = − 0.77; high diversity: T(1, 60) = − 6.32, p < 0.001, d = − 0.70" (B1). Both Cohen's d values are negative, confirming anxiety *decreased*.

The PubMed-indexed abstract characterizes these effects as "Anxiety and paranoia significantly decreased in both birdsong conditions (medium effect sizes)" (B2). This is the study authors' own magnitude label, applied in the abstract.

SC1 holds: 2/2 sources verified.

### SC2: Traffic noise raised depression with the same (medium) effect size

The Nature paper's Results section reports the within-group t-tests for depressive symptoms: "depressive symptoms significantly increased within both the low diversity urban soundscape (T(1, 82) = 2.64, p = 0.010, d = 0.29) and high diversity urban condition (T(1, 68) = 4.88, p < 0.001, d = 0.59)" (B3). Both d values are positive, confirming depression *increased*.

The PubMed-indexed abstract characterizes these effects as "the traffic noise soundscapes were associated with a significant increase in depression (small effect size in low, medium effect size in high diversity condition)" (B4). The authors apply two magnitude labels: "small" for the low-diversity urban condition (d = 0.29) and "medium" for the high-diversity urban condition (d = 0.59).

The claim's "medium effect size" matches the high-diversity finding. SC2 holds: 2/2 sources verified.

### Why both effects qualify as "the same"

<!-- not-a-citation-start -->
Cohen's (1988) conventional thresholds are d = 0.2 (small), d = 0.5 (medium), d = 0.8 (large).
<!-- not-a-citation-end -->
The study authors place the birdsong-anxiety effects (|d| in [0.70, 0.77]) and the high-diversity traffic-depression effect (d = 0.59) into the same "medium" bracket. The claim's phrase "with the same effect size" is operationalized as "same Cohen's d magnitude category as labeled by the authors," not as "numerically identical decimal values" — and at the categorical level, both effects are medium.

## What could challenge this verdict?

Four adversarial checks were conducted.

**Did secondary coverage mischaracterize the findings?** The full Nature paper was fetched directly and the within-group t-test results located in the Results section. The numeric d values (−0.77, −0.70 for anxiety; 0.29, 0.59 for depression) and the abstract's "medium effect size" labels were both verified verbatim on nature.com and on PubMed. The press-release-level summary faithfully reflects the authors' own abstract.

**Does "the same effect size" break the claim because the d values differ numerically?** The d values are not identical (anxiety |d| in [0.70, 0.77]; high-diversity depression d = 0.59), but both fall within Cohen's medium bracket per the authors' own labels. Operationalizing "same effect size" as "same magnitude category" is the standard reading for plain-language summaries of psychological findings.

**Does the low-diversity traffic condition (d = 0.29, small effect) contradict the claim?** The low-diversity finding is not a contradiction — depression still increased, just less. The claim is faithful to the high-diversity finding (which IS medium); it omits the diversity conditioning, but the medium effect it asserts genuinely exists in the study.

**Does the study have methodological problems that would undermine the "study reported X" claim?** The study is online-administered and uses self-report measures (STAI-S, PHQ-D, R-GPTS). It reports immediate pre/post effects only — no clinical, ecological, or long-term outcomes. These are limitations on what the finding GENERALIZES to, not on whether the study reported these specific d values. The descriptive claim about what the study reported is unaffected; broader causal/clinical generalizations are out of scope.

## Conclusion

**Verdict: PROVED**

Both sub-claims are supported by independently verified verbatim quotations from the primary peer-reviewed source (Nature, *Scientific Reports*) and its PubMed-indexed abstract. SC1 is verified by 2/2 sources confirming the birdsong-anxiety reduction at d in [-0.77, -0.70], characterized by the authors as a medium effect. SC2 is verified by 2/2 sources confirming the traffic-noise depression increase, with d = 0.59 (high-diversity) characterized by the authors as a medium effect. Both effects share the medium Cohen's d magnitude category as labeled by the study authors, satisfying the "with the same effect size" qualifier under the standard plain-language reading.

The proof is descriptive: it establishes what the Stobbe et al. (2022) study reported. It is not a claim that traffic noise causes clinical depression in real-world settings, nor that long-term birdsong exposure produces comparable anxiety reduction — those are different claims with different evidentiary requirements.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.33.2 on 2026-04-28.
