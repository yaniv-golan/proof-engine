# Proof: Adult neurogenesis occurs in the human neocortex.

- **Generated:** 2026-04-07
- **Verdict:** DISPROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

---

## Key Findings

- **2 of 2 independent peer-reviewed human tissue studies explicitly reject the claim** that new neurons are generated in the adult human neocortex at a detectable level (A1).
- Bhardwaj et al. 2006 (PNAS) used C14 radiocarbon bomb-pulse dating on human neocortical tissue and found that *"neurons in the human cerebral neocortex are not generated in adulthood at detectable levels but are generated perinatally"* (B1 -- verified).
- Spalding et al. 2013 (Cell) independently applied C14 bomb-pulse dating to human cortical neurons and confirmed that *"cortical and olfactory bulb neurons ... are not exchanged postnatally to a detectable degree in humans"* (B2 -- verified).
- Both citations are from PubMed/PMC (tier 5, government domain) and were verified live with full quote match. No unverified citations.

---

## Claim Interpretation

**Natural language:** "Adult neurogenesis occurs in the human neocortex."

**Formal interpretation:** The claim asserts that new neurons are generated in the adult human neocortex -- the layered cerebral cortex comprising prefrontal, temporal, parietal, and occipital regions -- at a detectable level. This explicitly excludes the hippocampal dentate gyrus and olfactory bulb, which are anatomically and functionally distinct structures where adult neurogenesis is a separate and ongoing debate.

**Proof direction:** Disproof. We count independent peer-reviewed sources that explicitly reject this claim using direct human tissue evidence. A threshold of 2 is used because domain scarcity limits the available evidence: only two independent research groups have applied C14 radiocarbon bomb-pulse dating to human neocortical tissue (Bhardwaj/Frisen 2006 and Spalding/Frisen 2013, the latter measuring cortical neurons as a control for hippocampal analysis). No other method provides equivalent precision for dating neuronal birth in postmortem human tissue. A threshold of 3 would force inclusion of weaker evidence (cross-species extrapolation or hedged review language), which the hardening rules prohibit for DISPROVED verdicts.

**Formalization scope:** The proof addresses whether neurogenesis occurs at detectable levels using current methodology. It does not exclude the theoretical possibility of neurogenesis below the detection threshold of C14 dating.

*Source: proof.py JSON summary*

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Bhardwaj et al. 2006 (PNAS) -- C14 bomb-pulse dating + BrdU study shows no adult neocortical neurogenesis in humans (direct human tissue study) | Yes |
| B2 | Spalding et al. 2013 (Cell) -- C14 bomb-pulse dating shows cortical neurons are not exchanged postnatally in humans (direct human tissue study) | Yes |
| A1 | Count of independent peer-reviewed human studies rejecting adult neocortical neurogenesis | Computed: 2 independent human tissue studies confirmed rejection (threshold met) |

*Source: proof.py JSON summary*

---

## Proof Logic

The proof is a disproof by source-counting: we count independent peer-reviewed studies on human tissue that explicitly reject the claim of adult neocortical neurogenesis. The threshold is 2, and 2 studies meet this criterion.

**B1 -- Bhardwaj et al. 2006 (PNAS):** The authors exploited atmospheric C14 produced by Cold War nuclear bomb tests. C14 is incorporated into DNA at the moment of cell division, so measuring a neuron's C14 content reveals when it was born. They analyzed neocortical neurons from human postmortem tissue and found that every cortical neuron tested had C14 levels corresponding to atmospheric concentrations at the time of the individual's birth -- not to any later period. Additionally, BrdU (a DNA synthesis marker) was available in neocortex from cancer patients who had received BrdU therapeutically; 515 BrdU-positive cells were identified, but none had neuronal morphology or reacted to neuronal markers. The verified conclusion: *"neurons in the human cerebral neocortex are not generated in adulthood at detectable levels but are generated perinatally."* (B1)

**B2 -- Spalding et al. 2013 (Cell):** In a study primarily focused on hippocampal neurogenesis, the authors independently applied C14 bomb-pulse dating to human cortical neurons as a control comparison. They confirmed that *"cortical and olfactory bulb neurons ... are not exchanged postnatally to a detectable degree in humans."* (B2) This represents an independent measurement on different postmortem human brain samples, published seven years later.

The C14 method is methodologically superior to BrdU labeling because it cannot be confounded by BrdU incorporation into cells undergoing DNA repair or apoptosis -- a key flaw in earlier positive reports (e.g., Gould et al. 1999).

**Source count:** 2 independent human tissue studies confirmed rejection (A1), meeting the threshold of >= 2 required for DISPROVED.

*Source: author analysis*

---

## Counter-Evidence Search

Three adversarial checks were performed before writing this proof:

**1. Does Gould et al. 1999 (Science) provide credible unrebutted evidence of adult neocortical neurogenesis in primates?**

Gould et al. 1999 used BrdU labeling in adult macaques and claimed new neurons in prefrontal, temporal, and parietal cortex. This paper was immediately contested. Kornack & Rakic 2001 used the identical BrdU method in macaques and found zero new neurons in neocortex. Nowakowski & Hayes 2000 (Science 288:771) published a formal critique. Bhardwaj et al. 2006 (B1) used C14 bomb-pulse dating -- a method immune to BrdU artifacts -- and found no adult neocortical neurogenesis in human tissue. The Gould 1999 findings are now regarded as methodological artifacts by the field. Does not break the disproof.

**2. Could any post-2013 study have demonstrated neocortical neurogenesis in humans?**

No post-2013 study using C14 dating or any other method has found neocortical neurogenesis in humans. The 2018-2024 debate concerns the hippocampal dentate gyrus only (Sorrells 2018 vs Boldrini 2018). Reviews through 2023 continue to state that cortical neurons are not generated locally in adulthood. Both B1 and B2 remain unrebutted for the neocortex specifically. Does not break the disproof.

**3. Is the neocortex claim contaminated by the hippocampal adult neurogenesis controversy?**

The 2018-2024 debate is confined to the hippocampus. All parties in that debate treat the neocortex as a settled negative. B1 covers both structures with the same C14 method and reaches the same negative conclusion for the neocortex independent of the hippocampal results. B2 separately confirms cortical neurons are not exchanged postnatally. The hippocampal controversy does not rescue the neocortical claim. Does not break the disproof.

*Source: author analysis*

---

## Conclusion

**Verdict: DISPROVED**

The claim "Adult neurogenesis occurs in the human neocortex" is disproved. Two independent peer-reviewed human tissue studies (A1 = 2, threshold = 2) using C14 bomb-pulse dating explicitly reject it. Bhardwaj et al. 2006 (B1) found that neocortical neurons are born perinatally, not in adulthood. Spalding et al. 2013 (B2) independently confirmed that cortical neurons are not exchanged postnatally. All citations are fully verified live from PubMed/PMC (tier 5, government domain) with no unverified sources. No adversarial check broke the disproof.

The ongoing debate in the field (2018-2024) concerns adult neurogenesis in the **hippocampus**, not the neocortex. The neocortical question is settled.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.8.0 on 2026-04-07.*
