# Audit: Concavity of the Poisson Spike-Train Log-Likelihood

**Generated:** 2026-04-18
**Reader summary:** [proof.md](proof.md)
**Proof script:** [proof.py](proof.py)

## Claim Interpretation

The natural-language claim asserts that for an inhomogeneous Poisson process spike-train model with intensity \(\lambda_t = f(\eta_t)\), where \(\eta_t = x_t^\top \beta + h_t^\top \gamma + b\) is affine in \(\theta = (\beta, \gamma, b)\), the log-likelihood is concave in \(\theta\) provided \(f\) is positive, convex, and log-concave. The claim further asserts that this concavity implies every local maximum is global, that maximum-likelihood fitting is a convex optimization problem, and that MAP inference under any log-concave prior is also convex.

The formal interpretation treats this as a theorem verification: the claim is TRUE if and only if the concavity of the log-likelihood follows from the stated hypotheses via standard convex analysis composition rules. The operator `==` with threshold `True` captures this binary determination.

**Formalization scope:** The formal interpretation is a faithful 1:1 mapping of the natural-language claim. No aspects are narrowed, excluded, or operationalized by proxy. The proof verifies the mathematical reasoning chain and provides numerical confirmation on a concrete example (\(f = \exp\)).

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Poisson spike-train log-likelihood with link function f |
| Property | concavity of log-likelihood in θ when f is positive, convex, and log-concave |
| Operator | == |
| Threshold | True |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| A1 | — | Composition: concave(affine) is concave |
| A2 | — | Convex(affine) is convex ⇒ −f(affine) concave |
| A3 | — | Non-negative scalar times concave is concave |
| A4 | — | Log-likelihood is sum of concave terms ⇒ concave |
| A5 | — | Numerical Hessian eigenvalues all ≤ 0 (f = exp) |
| A6 | — | MAP multi-start optimization converges to unique optimum |
| A7 | — | ML multi-start optimization converges to unique optimum |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Composition: concave(affine) is concave | Convex analysis composition rule applied to log f and affine η_t(θ) | True |
| A2 | Convex(affine) is convex ⇒ −f(affine) concave | Convex analysis composition rule applied to f and affine η_t(θ) | True |
| A3 | Non-negative scalar times concave is concave | Scaling rule: n_t ≥ 0 preserves concavity of log f(η_t) | True |
| A4 | Log-likelihood is sum of concave terms ⇒ concave | Summation of concave terms from A1-A3 over time bins | True |
| A5 | Numerical Hessian eigenvalues all ≤ 0 (f = exp) | Finite-difference Hessian at 5 random points; max eigenvalue −6.71e-02 | True |
| A6 | MAP multi-start optimization converges to unique optimum | 10 random starts with Gaussian prior; spread 1.17e-10 | True |
| A7 | ML multi-start optimization converges to unique optimum | 10 random starts; log-likelihood spread 2.80e-06 | True |

*Source: proof.py JSON summary*

## Computation Traces

```
A7: Multi-start spread < 1e-4 (unique optimum): 2.7970402555453157e-06 < 0.0001 = True
A6: MAP multi-start spread < 1e-4 (unique optimum): 1.1740697303253e-10 < 0.0001 = True
Analytical Hessian max eigenvalue (should be <= 0): max_analytical_eig = -0.041917791557041076 = -0.0419
All sub-claims hold: True == True = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

**Check 1: Are the conditions vacuous?**
- Question: Is "positive, convex, and log-concave" a vacuous set of conditions? Do common link functions actually satisfy all three simultaneously?
- Verification performed: Checked exp(x): positive (exp(x) > 0), convex (exp″ = exp > 0), log-concave (log(exp(x)) = x is concave/linear). Also checked f(x) = x for x > 0: positive, convex, log f = log x is concave. Softplus log(1 + exp(x)): positive, convex, and log-concave.
- Finding: The conditions are not vacuous. The exponential, identity-on-positive-reals, and softplus functions all satisfy positivity, convexity, and log-concavity.
- Breaks proof: No

**Check 2: Unbounded parameter spaces**
- Question: Could the proof break for non-compact or unbounded parameter spaces? The claim assumes convex parameter space — does concavity still guarantee a unique global maximum exists?
- Verification performed: Concavity guarantees that every local maximum is global, but does not guarantee existence of a maximum (the supremum might not be attained). The claim as stated says "every local maximum is global" and "ML fitting is a convex optimization problem" — both are true by concavity alone. Existence is a separate (unstated) concern.
- Finding: The claim is about concavity and the local=global property, not existence. Existence of the MLE may require additional conditions but is not part of the stated claim.
- Breaks proof: No

**Check 3: Does local=global require strict concavity?**
- Question: Is the claim that "every local maximum is global" actually a theorem for concave functions, or does it require strict concavity?
- Verification performed: Standard result in convex analysis: if f is concave and x* is a local maximum, then for any y and small t > 0, f(x* + t(y − x*)) ≤ f(x*). By concavity, f(x* + t(y − x*)) ≥ tf(y) + (1 − t)f(x*), so tf(y) + (1 − t)f(x*) ≤ f(x*), giving f(y) ≤ f(x*). This holds for any y, so x* is a global maximum.
- Finding: Confirmed: every local maximum of a concave function is global. This does NOT require strict concavity.
- Breaks proof: No

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A — pure computation, no empirical facts.
- **Rule 2:** N/A — pure computation, no empirical facts.
- **Rule 3:** No time-sensitive operations detected.
- **Rule 4:** CLAIM_FORMAL with operator_note found. Operator choice (== True) documented with rationale.
- **Rule 5:** Three adversarial checks performed, investigating non-vacuousness of hypotheses, unbounded parameter spaces, and the local=global theorem for concave functions.
- **Rule 6:** N/A — pure computation, no empirical facts. Cross-checks use mathematically independent methods: analytical Hessian vs. numerical finite-difference Hessian, and Hessian eigenvalue analysis vs. multi-start optimization convergence.
- **Rule 7:** Constants and formulas computed via `explain_calc()` and `compare()` from computations.py.
- **validate_proof.py result:** PASS — 16/16 checks passed, 0 issues, 0 warnings

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.23.0 on 2026-04-18.
