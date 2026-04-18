# Audit: InfoNCE Loss Lower Bound on Mutual Information

- **Generated:** 2026-04-18
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The natural-language claim asserts three properties of the InfoNCE contrastive loss:

1. \(\log N - L_N(s)\) is a lower bound on mutual information \(I(X;Y)\) for any measurable scoring function \(s(x,y)\).
2. The Bayes-optimal score is the pointwise mutual information \(s^*(x,y) = \log \frac{p(y|x)}{p(y)} + c(x)\) where \(c(x)\) is arbitrary.
3. The resulting lower bound tightens as \(N\) increases.

The formal interpretation treats these as three conjunctive sub-claims that must all hold for the overall claim to be proved. The operator is "==" with threshold True (all three hold).

**Operator rationale:** Equality (all sub-claims must hold) is the correct operator since the claim asserts all three properties jointly, connected by "Then...The Bayes-optimal score is...the resulting...bound tightens."

**Formalization scope:** The natural-language claim is universal ("for any measurable scoring function"). The formal verification operationalizes this via numerical Monte Carlo on two distribution families (bivariate Gaussian and asymmetric discrete), testing the optimal PMI score and a suboptimal linear score. This is a faithful numerical verification of the claim on specific distributions, not a universal analytical proof. The operator_note documents this explicitly and notes that the analytical argument is well-established in the literature (Oord et al. 2018, Poole et al. 2019).

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | InfoNCE contrastive loss and mutual information |
| Property | Three sub-claims all hold simultaneously |
| Operator | == |
| Threshold | True |
| Time-sensitive | No |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | SC1: Lower bound holds for Gaussian (multiple rho, N) | -- |
| A2 | SC2: Optimal score outperforms suboptimal on Gaussian | -- |
| A3 | SC3: Bound tightens with increasing N on Gaussian | -- |
| A4 | Cross-check: SC1 holds on discrete distribution | -- |
| A5 | Cross-check: SC2 holds on discrete distribution | -- |
| A6 | Cross-check: SC3 holds on discrete distribution | -- |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | SC1: Lower bound holds for Gaussian | Monte Carlo (100k samples) over rho in {0.3, 0.6, 0.8, 0.95} and N in {2,4,8,16,32,64,128,256} | All 32 tests passed |
| A2 | SC2: Optimal score outperforms suboptimal on Gaussian | Monte Carlo comparison of optimal PMI score vs linear score x*y | Optimal score beats suboptimal in all 6 tests |
| A3 | SC3: Bound tightens with increasing N on Gaussian | Monte Carlo: verify bound increases monotonically with N for rho in {0.5, 0.8, 0.95} | Bound tightens in all tested cases |
| A4 | Cross-check: SC1 holds on discrete distribution | Monte Carlo on 3x3 discrete joint | SC1 holds on discrete |
| A5 | Cross-check: SC2 holds on discrete distribution | Optimal vs linear score on discrete, N=32 | Optimal wins by 0.3129 |
| A6 | Cross-check: SC3 holds on discrete distribution | Monotonicity check on discrete distribution | Tightens on discrete |

*Source: proof.py JSON summary*

## Computation Traces

```
SC1 discrete: zero violations: 0 == 0 = True
SC3 discrete: zero violations: 0 == 0 = True
SC1: lower bound holds (Gaussian): True == True = True
SC2: optimal score is PMI (Gaussian): True == True = True
SC3: bound tightens with N (Gaussian): True == True = True
SC1 cross-check (discrete): True == True = True
SC2 cross-check (discrete): True == True = True
SC3 cross-check (discrete): True == True = True
All sub-claims and cross-checks hold: True == True = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

Each sub-claim was verified on two mathematically independent distribution families:

| Cross-check | Fact IDs | Values | Agreement |
|------------|----------|--------|-----------|
| SC1 on Gaussian vs discrete | A1, A4 | True, True | Yes |
| SC2 on Gaussian vs discrete | A2, A5 | True, True | Yes |
| SC3 on Gaussian vs discrete | A3, A6 | True, True | Yes |

The two distribution families (continuous bivariate Gaussian and discrete 3x3 joint) are mathematically independent: they share no parameters, no common structure, and exercise different code paths in the scoring functions. Agreement across both families provides meaningful cross-validation.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**Q1: Does the bound break for extreme correlations (rho -> 1)?**

*Verification:* Tested rho=0.95 (I(X;Y)=1.516 nats). For N=256, bound=1.49 which is below I(X;Y). For N=512, bound=1.50. The bound is loose when I(X;Y) >> log N but never exceeds I(X;Y).

*Finding:* No violation found. The bound saturates near log N when I(X;Y) > log N (the known log N ceiling per McAllester & Stratos 2020), but this is a tightness limitation, not a bound violation. **Does not break proof.**

**Q2: Can a non-PMI score achieve lower InfoNCE loss than the PMI score?**

*Verification:* Compared optimal PMI score against suboptimal linear score x*y across 6 parameter combinations. Also searched literature for counterexamples to the optimality of the PMI score in InfoNCE.

*Finding:* The PMI score always achieves lower or equal loss. The optimality is well-established: it follows from the fact that the optimal N-way classifier is the Bayes classifier, and its log-likelihood ratio reduces to PMI + c(x). No counterexample exists in the literature. **Does not break proof.**

**Q3: Does the bound ever decrease (get looser) as N increases?**

*Verification:* Tested monotonicity for 3 correlation values across N=2 to N=512. Searched for "InfoNCE bound non-monotonic N" -- no results found.

*Finding:* The bound monotonically increases with N in all tests. This is consistent with the analytical result: the KL divergence between the posterior over i* and the uniform distribution decreases as N grows. **Does not break proof.**

**Q4: Is the claim misleading because the bound saturates at log N?**

<!-- not-a-citation-start -->
*Verification:* Searched "InfoNCE log N saturation criticism." McAllester & Stratos (2020) and Poole et al. (2019) document that the bound cannot exceed log N. The claim says the bound "tightens as N increases," which is true -- it approaches I(X;Y) from below.
<!-- not-a-citation-end -->

*Finding:* The claim is not misleading. "Tightens" means the gap I(X;Y) - bound decreases, which is true. The claim does not assert the bound reaches I(X;Y) for finite N. The log N saturation is a rate limitation, not a contradiction of the tightening property. **Does not break proof.**

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A -- pure computation, no empirical facts
- **Rule 2:** N/A -- pure computation, no empirical facts
- **Rule 3:** N/A -- no time-sensitive operations
- **Rule 4:** CLAIM_FORMAL with operator_note found, documenting interpretation of "lower bound," "Bayes-optimal," and "tightens"
- **Rule 5:** 4 adversarial checks performed, including extreme correlation testing, optimality counterexample search, monotonicity verification, and semantic analysis of "tightens"
- **Rule 6:** N/A -- pure computation, no empirical facts. Cross-checks use mathematically independent distribution families (Gaussian vs discrete)
- **Rule 7:** No hard-coded constants; all computations use numpy and standard library math
- **validate_proof.py result:** PASS -- 19/19 checks passed, 0 warnings

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.23.0 on 2026-04-18.
