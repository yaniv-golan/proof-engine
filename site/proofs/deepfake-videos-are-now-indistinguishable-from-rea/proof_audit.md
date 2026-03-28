# Audit: Deepfake videos are now indistinguishable from real footage to the average human eye.

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Deepfake video detection by average, untrained humans |
| Property | Number of independent peer-reviewed sources confirming performance at or near chance level (not reliably above 50% accuracy) for video deepfake detection |
| Operator | `>=` |
| Threshold | 3 |
| Proof direction | affirm |
| Operator note | "Indistinguishable" is interpreted as: average humans cannot reliably distinguish deepfake videos from real footage — meaning their detection accuracy is near chance (~50%) and not statistically significantly above chance in controlled studies. Threshold = 3 independent peer-reviewed sources confirming near-chance detection. Counter-evidence: studies showing above-chance video detection (63–67%) documented in adversarial checks. |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | meta_analysis_2024 | Systematic review & meta-analysis of 56 papers (86,155 participants): video detection CI crosses 50% — not significantly above chance |
| B2 | fooled_twice_2021 | Fooled Twice RCT (N=210): people cannot reliably detect deepfakes; only 5/16 videos detectable above chance |
| B3 | fooled_twice_sciencedirect | Fooled Twice (ScienceDirect full-text): 'seeing-is-believing' heuristic; training and incentives do not improve detection |
| A1 | — | Verified source count meeting near-chance confirmation threshold |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified source count meeting near-chance confirmation threshold | count(verified citations) = 1 | 1 confirmed source(s) of 3 required; adversarial check breaks proof (video detection above chance in multiple studies) |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Meta-analysis (56 papers, 86K participants): video CI crosses 50% | Diel et al. (2024), Computers in Human Behavior Reports, Elsevier | https://www.sciencedirect.com/science/article/pii/S2451958824001714 | "Overall deepfake detection rates (sensitivity) were not significantly above chance because 95% confidence intervals crossed 50%. Total deepfake detection accuracy was 55.54% (95% CI [48.87, 62.10], k = 67)." | fetch_failed | — | Tier 4 (academic) |
| B2 | Fooled Twice RCT: cannot reliably detect deepfakes | Köbis et al. (2021), iScience / PMC, N=210 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8602050/ | "people cannot reliably detect deepfakes and neither raising awareness nor introducing financial incentives improves their detection accuracy" | partial | aggressive_normalization | Tier 5 (government, NIH.gov) |
| B3 | Fooled Twice: "seeing is believing" heuristic, training fails | Köbis et al. (2021), iScience, Elsevier (ScienceDirect) | https://www.sciencedirect.com/science/article/pii/S2589004221013353 | "people can no longer reliably detect deepfakes. Some of the previously established strategies against misinformation do not hold for the detection of deepfakes" | fetch_failed | — | Tier 4 (academic) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — Diel et al. 2024 (meta-analysis)**
- Status: `fetch_failed`
- Method: N/A — HTTP 403 (paywalled ScienceDirect)
- Fetch mode: live
- Impact: B1 is the primary evidence supporting the claim. Its quote could not be machine-verified. However, the same statistics (55.54%, CI [48.87, 62.10]) are independently reported in multiple secondary sources including search engine snippets and academic aggregators, increasing confidence the quote is accurate. The adversarial break (not B1) drives the UNDETERMINED verdict.

*Source: proof.py JSON summary; impact analysis is author analysis*

**B2 — Köbis et al. 2021 (Fooled Twice, PMC)**
- Status: `partial`
- Method: aggressive_normalization (fragment match, 6 words)
- Fetch mode: live
- Coverage: Partial match — fragment "people cannot reliably detect deepfakes" found via aggressive normalization. The PMC page contains inline citation markers and HTML noise; the quote was verified via fragment. PMC is the government-hosted, open-access version of the peer-reviewed iScience paper.

*Source: proof.py JSON summary*

**B3 — Köbis et al. 2021 (Fooled Twice, ScienceDirect)**
- Status: `fetch_failed`
- Method: N/A — HTTP 403 (paywalled ScienceDirect)
- Fetch mode: live
- Impact: B3 is the ScienceDirect mirror of B2. Both cite the same underlying paper; B2 (PMC) partially verified the same research. B3's failure does not uniquely undermine the evidence, as B2 covers the same claims.

*Source: proof.py JSON summary; impact analysis is author analysis*

---

## Computation Traces

```
Confirmed sources: 1 / 3
verified source count vs threshold: 1 >= 3 = False
```

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

| Description | Values Compared | Agreement | Note |
|-------------|----------------|-----------|------|
| B1 (meta-analysis 2024) vs B2/B3 (Fooled Twice 2021) — independently conducted by different research groups | "Meta-analysis: 55.54% overall, video CI crosses 50%" / "Fooled Twice: 57.6% overall, only 5/16 videos detectable above chance" | True (consistent direction) | B2 and B3 are PMC and ScienceDirect versions of the same paper — shared upstream data. B1 is independent of B2/B3. Consistent direction (near-chance) but different methodologies. |

*Source: proof.py JSON summary*

---

## Adversarial Checks (Rule 5)

**Check 1: Do studies show humans detect VIDEO deepfakes reliably above chance (~50%)?**
- Verification performed: Searched PMC and PNAS for studies measuring human video deepfake detection accuracy. Found: (1) Groh et al. 2022 (PNAS, N=15,016): 66% accuracy for video deepfakes — well above chance; (2) Köbis et al. 2025 "Is this real?" (PMC12779810): 63% accuracy, AUC=0.67 for videos, described as "fairly good" discrimination; (3) University of Florida study (Feb 2026): humans correctly identified real and fake videos about two-thirds of the time, outperforming AI algorithms.
- Finding: Multiple studies — including a large PNAS study (N=15,016) and a 2025 PMC study — show human video deepfake detection at 63–67%, which IS above chance. This directly contradicts the claim that videos are "indistinguishable." The meta-analysis (B1) shows video CI [47.80, 66.57] crossing 50%, but individual studies with dedicated video stimuli consistently show above-chance performance. This is genuine counter-evidence that breaks the strong form of the claim.
- **Breaks proof: YES**

**Check 2: Is the claim specifically about state-of-the-art (2024–2026) deepfakes?**
- Verification performed: Searched for studies specifically testing newest-generation deepfakes (Sora, HeyGen, Face Swap v2) vs older FaceForensics++ dataset. Found the iProov (2024) commercial study claiming only 0.1% can detect, but with opaque methodology from a company selling detection tools. No peer-reviewed academic study specifically testing 2025–2026 generation deepfakes found.
- Finding: Academic evidence covers mostly 2018–2023 deepfake generations. The "now" qualifier suggests the most current deepfakes may be harder to detect, but no peer-reviewed data confirms this. Evidence gap, not direct counter-evidence.
- **Breaks proof: NO**

**Check 3: Could meta-analysis aggregate bias explain why CI crosses 50%?**
- Verification performed: Examined meta-analysis methodology — 56 heterogeneous studies with different deepfake types, quality levels, and designs. Wide CI reflects high between-study variability (heterogeneity). CI crossing 50% does not mean all studies found at-chance performance.
- Finding: CI crossing 50% reflects high heterogeneity, not consensus of chance-level detection. Individual well-controlled video studies consistently show above-chance detection (63–67%). Meta-analysis is inconclusive, not supportive.
- **Breaks proof: NO**

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | sciencedirect.com | academic | 4 | Known academic/scholarly publisher (Elsevier) |
| B2 | nih.gov | government | 5 | Government domain (.gov) — NIH/PMC open access archive |
| B3 | sciencedirect.com | academic | 4 | Known academic/scholarly publisher (Elsevier) |

No citations from tier ≤ 2 sources.

*Source: proof.py JSON summary*

---

## Extraction Records

For qualitative proofs, extraction records reflect citation verification status per B-type fact.

| Fact ID | Value (citation status) | Countable? | Quote Snippet |
|---------|------------------------|-----------|---------------|
| B1 | fetch_failed | No | "Overall deepfake detection rates (sensitivity) were not significantly above chan" |
| B2 | partial | Yes | "people cannot reliably detect deepfakes and neither raising awareness nor introd" |
| B3 | fetch_failed | No | "people can no longer reliably detect deepfakes. Some of the previously establish" |

*Source: proof.py JSON summary*

---

## Hardening Checklist

- **Rule 1:** N/A — qualitative proof; no numeric values extracted from quotes
- **Rule 2:** ✓ Citation verification code present (`verify_all_citations`); B2 partially verified; B1 and B3 fetch_failed (paywalled)
- **Rule 3:** ✓ `date.today()` used for generation date (no time-dependent comparisons in this proof)
- **Rule 4:** ✓ `CLAIM_FORMAL` dict with `operator_note` explicitly stating "indistinguishable = near-chance = not significantly above chance"
- **Rule 5:** ✓ Three adversarial checks; first check found genuine counter-evidence (63–67% above-chance detection in video studies) and is marked `breaks_proof: True`
- **Rule 6:** ✓ B1 (meta-analysis) and B2/B3 (Fooled Twice) are from independent research groups; B2/B3 are the same paper but B1 is independent of both
- **Rule 7:** N/A — no hard-coded constants or formulas; `compare()` from computations.py used
- **validate_proof.py result:** PASS with 1 warning (missing else-branch, subsequently fixed); 14/15 checks passed

*Source: author analysis*

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
