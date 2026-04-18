# Audit: Discrete-Time Rescaling via \(R_m = A_m - \log(1 - U_m p_{\tau_m})\)

**Generated:** 2026-04-19
**Reader summary:** [proof.md](proof.md)
**Proof script:** [proof.py](proof.py)

## Claim Interpretation

The natural-language claim asserts that for a correctly specified discrete-time Bernoulli spike train with conditional probabilities \(p_k\), the rescaled interspike intervals \(R_m = A_m - \log(1 - U_m \cdot p_{\tau_m})\) are i.i.d. Exp(1), where \(A_m\) is the cumulative hazard over non-spike bins and \(U_m \sim \text{Uniform}(0,1)\) independently. The claim has two components: marginal Exp(1) distribution and mutual independence.

The formal interpretation proves both components via the randomized probability integral transform (PIT) theorem applied to the discrete CDF of \(\tau_m\) conditional on \(\mathcal{F}_{\tau_{m-1}}\). Independence follows by the tower property. The proof is universal — tested with constant and time-varying \(p_k\).

**Formalization scope:** The formalization is a faithful 1:1 mapping of the natural-language claim. The PIT argument applies to all \(p_k \in (0,1)\) without restriction.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Randomized discrete-time rescaling \(R_m = A_m - \log(1 - U_m p_{\tau_m})\) |
| Property | \(R_m \sim \text{Exp}(1)\) and \(R_m\) are i.i.d. |
| Operator | == |
| Threshold | Exp(1) |
| Operator note | Two-part claim: (1) marginal Exp(1) via PIT theorem, (2) independence via tower property. Verified analytically and by Monte Carlo with constant and time-varying \(p_k\). |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | Analytical PIT verification (constant p) | — |
| A2 | Monte Carlo KS test (constant p = 0.3) | — |
| A3 | Monte Carlo KS test (constant p = 0.5) | — |
| A4 | Monte Carlo KS test (time-varying p_k) | — |
| A5 | Independence test via serial correlation | — |
| A6 | Analytical CDF derivation matches PIT | — |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Analytical PIT verification | Computed P(Z <= z) analytically for z in [0.1, 0.25, 0.5, 0.75, 0.9, 0.99] using constant p=0.3. Summed over geometric distribution support. | Max error = 1.11e-16. PIT exact: True |
| A2 | Monte Carlo KS (p=0.3) | 100,000 samples, KS test against Exp(1) | KS stat = 0.003145 <= 0.004301. Not rejected. |
| A3 | Monte Carlo KS (p=0.5) | 100,000 samples, KS test against Exp(1) | KS stat = 0.002705 <= 0.004301. Not rejected. |
| A4 | Monte Carlo KS (varying p) | 100,000 samples with p_k = 0.1 + 0.08*sin(2*pi*k/50) | KS stat = 0.002624 <= 0.004301. Not rejected. |
| A5 | Independence test | Lag-1 and lag-2 autocorrelation of Z_m for 100,000 samples | Lag-1 = -0.0034, lag-2 = 0.0035; threshold 0.0062. Not rejected. |
| A6 | Formula equivalence | Compared Z_claim = 1-exp(-R_m) with Z_PIT for 6 (n,U) pairs | Max error = 0.00e+00. Formulas identical. |

*Source: proof.py JSON summary*

## Computation Traces

```
A1: PIT exact to machine precision: 1.1102230246251565e-16 < 1e-10 = True
A2: KS passes for p=0.3: 0.0031454481134972068 <= 0.0043006976178289955 = True
A3: KS passes for p=0.5: 0.0027050350162163284 <= 0.0043006976178289955 = True
A4: KS passes for time-varying p: 0.002623598639104885 <= 0.0043006976178289955 = True
A5: lag-1 autocorrelation within threshold: 0.003417833292193835 < 0.006198064213930023 = True
A6: formula matches PIT to machine precision: 0.0 < 1e-14 = True
All 6 verification checks pass: 6 == 6 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Method Agreement (Rule 6)

Three mathematically independent approaches confirm R_m ~ Exp(1):

1. **Analytical PIT computation (A1, A6):** Direct computation of the CDF shows P(Z <= z) = z to machine precision. This is a closed-form algebraic argument — no randomness involved.

2. **Monte Carlo simulation with KS test (A2, A3, A4):** Empirical sampling with a statistical hypothesis test. The simulation generates spike trains de novo and applies the transformation, testing the distributional claim via a completely different pathway. Three model specifications (constant p = 0.3, constant p = 0.5, and sinusoidal p_k) all pass.

3. **Moment cross-checks:** E[R_m] and Var[R_m] independently computed from Monte Carlo samples match the theoretical Exp(1) moments (mean 1.0, variance 1.0) within sampling error. This catches any systematic bias that might be missed by the KS test.

The analytical and Monte Carlo methods share no computational pathway. The analytical result is exact algebra; the Monte Carlo result is a statistical test on random samples.

*Source: proof.py JSON summary (cross_checks); independence analysis is author analysis*

## Adversarial Checks (Rule 5)

**Check 1: Does the previous disproof apply?**
Investigation: Algebraically compared this formula (\(-\log(1 - Up)\)) with the previously disproved one (\(U \cdot (-\log(1-p))\)). The key difference is \((1-Up)\) vs \((1-p)^U\) — distinct by Jensen's inequality.
Finding: The two formulas are algebraically distinct. The disproof does not transfer.
Breaks proof: No.

**Check 2: PIT under filtration-adapted p_k?**
Investigation: Verified the PIT applies conditionally on \(\mathcal{F}_{\tau_{m-1}}\), which yields a fixed CDF. The time-varying Monte Carlo test (A4) confirms computationally.
Finding: The conditional PIT argument is valid for arbitrary adapted sequences.
Breaks proof: No.

**Check 3: Is the independence claim valid?**
Investigation: Proved via tower property that \(Z_m | \mathcal{F}_{\tau_{m-1}} \sim U(0,1)\) (constant conditional distribution) implies unconditional independence by induction. The autocorrelation test (A5) confirms.
Finding: Independence follows from the tower property.
Breaks proof: No.

**Check 4: Boundary cases?**
Investigation: Checked formula behavior as \(p \to 0\) (continuous-time limit) and \(p \to 1\) (near-certain spike). Both are mathematically sound.
Finding: Formula is well-defined and correct for all \(p \in (0,1)\).
Breaks proof: No.

*Source: proof.py JSON summary (adversarial_checks)*

## Quality Checks

- Rule 1: N/A — pure computation, no empirical facts
- Rule 2: N/A — pure computation, no empirical facts
- Rule 3: No time-sensitive operations
- Rule 4: CLAIM_FORMAL with detailed operator_note decomposing the claim into marginal distribution and independence components
- Rule 5: Four adversarial checks covering: relationship to previous disproof, conditional PIT validity, independence argument, and boundary behavior
- Rule 6: N/A — pure computation, no empirical facts. Three mathematically independent methods (analytical PIT, Monte Carlo KS, moment cross-checks) confirm the result.
- Rule 7: compare() and cross_check() from computations.py used for all comparisons
- validate_proof.py result: PASS — 15/16 checks passed, 0 issues, 1 warning (style suggestion about claim_holds)

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.23.0 on 2026-04-19.
