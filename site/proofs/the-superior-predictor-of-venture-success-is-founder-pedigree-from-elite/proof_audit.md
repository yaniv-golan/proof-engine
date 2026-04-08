# Audit: The superior predictor of venture success is founder pedigree from elite universities rather than market size or product traction.

- **Generated:** 2026-04-08
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Founder pedigree from elite universities as a predictor of venture success |
| Property | Whether founder pedigree has higher predictive validity than market size or product traction |
| Operator | > (pedigree strictly outperforms both competitors) |
| Threshold | 3 independent confirming sources |
| Operator note | "Superior predictor" is operationalized as higher predictive validity — stronger correlation with or causal contribution to successful venture outcomes (exit value, unicorn status, fund returns) — compared to both market size and product traction. The claim requires pedigree to outperform both alternatives, not just one. "Elite universities" = Ivy League, MIT, Stanford, and equivalent. "Product traction" = demonstrable customer adoption, revenue, or usage growth. |

## Fact Registry

| Report ID | Label | Direction |
|-----------|-------|-----------|
| B1 | arXiv/YC study — credentials explain <4% of funding variation | Adversarial |
| B2 | Beta Boom — pedigree predicts VC access, not unicorn outcomes | Adversarial |
| B3 | CB Insights — product-market fit failure is #1 startup cause | Adversarial |
| B4 | Gompers et al. (2010) — management team ranked #1 by VCs but pedigree not isolated | Neutral (does not confirm) |

## Confirming Sources Found

- **Required:** 3
- **Found:** 0

No source was identified that satisfies the full claim requirement: showing pedigree has higher predictive validity than both market size and traction across an unbiased sample.

## Citation Assessment Details

### B1 — arXiv/YC study (credentials and startup funding)
- **Search performed:** Quantitative studies on educational credentials vs. startup outcomes
- **Found:** arXiv preprint using Y Combinator portfolio data; educational credentials statistically insignificant; explains <4% of funding variation after controlling for other characteristics
- **Confirms claim:** No — contradicts it directly
- **Adversarial:** Yes — breaks proof

### B2 — Beta Boom (pedigree and unicorn outcomes)
- **Search performed:** Studies on elite university pedigree and startup success vs. VC investment
- **Found:** Beta Boom analysis; top-10 university alumni receive 51% of VC investment but produce only 35% of unicorns
- **Confirms claim:** No — shows pedigree predicts investor behavior, not outcomes
- **Adversarial:** Yes — breaks proof

### B3 — CB Insights (startup failure causes)
- **Search performed:** Top reasons startups fail; role of product-market fit and market size
- **Found:** CB Insights post-mortem analysis of hundreds of startups; "no market need" at 35–42% is the top cause of failure
- **Confirms claim:** No — implicates market size and traction as dominant predictors
- **Adversarial:** Yes — breaks proof

### B4 — Gompers, Kovner, Lerner, Scharfstein (2010)
- **Search performed:** VC investment criteria; Harvard survey of VC decision-making
- **Found:** Management team ranked most important (95%) by VCs; market at 68%; product at 74%. "Management team" means execution capability, not university pedigree specifically.
- **Confirms claim:** No — does not isolate pedigree as a predictor vs. traction/market
- **Adversarial:** Yes (does not confirm claim as required)

### First Round Capital (2015) — portfolio retrospective
- **Search performed:** Elite university founders and VC portfolio outperformance
- **Found:** Ivy/MIT/Stanford founders showed 220% outperformance within First Round Capital's own portfolio
- **Confirms claim:** No — single curated portfolio with selection bias; does not compare pedigree against traction or market size as competing predictors; not a population-level study
- **Adversarial:** No (source does not break proof but does not confirm it either)

## Adversarial Checks

### Check 1 — arXiv/YC study: credentials explain <4% of variance
- **Question:** Does quantitative research on large startup datasets show pedigree is statistically insignificant?
- **Finding:** Yes. arXiv preprint on YC portfolio found credentials explain less than 4% of funding variation after controls. A predictor accounting for <4% of variance cannot be the "superior" predictor.
- **Breaks proof:** Yes

### Check 2 — Beta Boom: pedigree over-predicts VC access vs. unicorn production
- **Question:** Do elite-pedigree founders receive more VC investment than their share of successful outcomes would justify?
- **Finding:** Yes. Top-10 university alumni: 51% of VC investment, 35% of unicorns. Pedigree appears to be a stronger predictor of VC access than of actual outcomes.
- **Breaks proof:** Yes

### Check 3 — CB Insights: "no market need" is the top startup failure cause
- **Question:** Do startup post-mortems identify pedigree absence as the primary failure driver?
- **Finding:** No. "No market need" (35–42%) and product-market fit failure are consistently the top causes. These are market size and traction measures. If pedigree were the superior predictor, its absence would dominate failure analysis.
- **Breaks proof:** Yes

### Check 4 — Gompers et al.: management team ranked #1 but pedigree not isolated
- **Question:** Does the VC criteria literature show pedigree specifically outranks market and product?
- **Finding:** Management team ranks #1 in VC decision-making surveys, but "management team" encompasses execution capability and domain expertise — not elite university attendance specifically. No study isolates pedigree vs. traction/market.
- **Breaks proof:** Yes

### Check 5 — First Round Capital: 220% outperformance in one portfolio
- **Question:** Does at least one empirical data point show pedigree correlates with outperformance?
- **Finding:** Yes, within one VC firm's curated portfolio. But: selection bias (First Round already filters for quality), conflict of interest (firm's own portfolio data), no comparison against traction or market size as alternatives. Does not meet the "superior to both" requirement.
- **Breaks proof:** No

## Hardening Checklist

- **Rule 1:** No numeric values hand-typed from the claim; all statistics sourced from identified research.
- **Rule 2:** Research sources assessed for what they actually measure; metric identity verified (pedigree vs. team quality vs. execution capability).
- **Rule 3:** Proof generated 2026-04-08 via `date.today()`.
- **Rule 4:** Claim interpretation explicit in `CLAIM_FORMAL`; "superior predictor" formally operationalized; "elite universities" defined; compound requirement (outperform both, not just one) stated.
- **Rule 5:** 5 adversarial checks performed across contradicting research, VC survey data, failure analysis, and one potentially confirming portfolio study.
- **Rule 6:** Multiple independent research sources searched; consistent pattern of contradiction found.
- **Rule 7:** Verdict based on source count comparison (`0 >= 3 = False`); no hard-coded constants.

## Verdict Determination

0 confirming sources found against a threshold of 3. All four identified empirical facts (B1–B4) either contradict the claim or fail to confirm it in the specific form required. The verdict is **UNDETERMINED** rather than DISPROVED because: (a) the contradictory evidence has methodological limitations (observational studies, potential confounds, portfolio selection bias); (b) at least one source (First Round Capital) shows a pedigree signal in a curated dataset; (c) the absence of confirming evidence in public research does not rule out the existence of proprietary data that might confirm the claim. The claim lacks the evidentiary foundation required for a PROVED verdict, but the evidence against it is insufficiently clean to support DISPROVED.
