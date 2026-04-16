# Audit: \(\text{eml}(a, b) = \exp(a) - \ln(b)\) satisfies \(\text{eml}(x, 1) = \exp(x)\)

- **Generated:** 2026-04-16
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The claim defines a binary operator eml(a, b) = exp(a) - ln(b) and asserts that for every complex number x, eml(x, 1) = exp(x). This is a pure algebraic identity: substituting b = 1 gives exp(x) - ln(1), and since ln(1) = 0, the result is exp(x).

The formal interpretation uses exact equality (==) with threshold True. The operator_note documents the reasoning chain: ln(1) = 0 in the principal branch, substitution, and simplification. The proof verifies this symbolically via SymPy and numerically at representative complex points.

**Formalization scope:** The formal interpretation is a faithful 1:1 mapping of the natural-language claim. The operator eml is fully defined in the claim, the domain is all complex numbers, and the identity to verify is explicit. The only interpretive choice is using the principal branch of the complex logarithm, which is the standard convention and produces the unique value ln(1) = 0.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Binary operator eml(a, b) = exp(a) - ln(b) |
| Property | eml(x, 1) = exp(x) for all complex x |
| Operator | == |
| Threshold | True |
| Operator Note | The claim follows from ln(1) = 0, which holds in the principal branch of the complex logarithm. Substituting b = 1: eml(x, 1) = exp(x) - ln(1) = exp(x) - 0 = exp(x). This is an algebraic identity, not a limit or approximation. The proof verifies symbolically that exp(x) - ln(1) - exp(x) simplifies to 0 for symbolic x. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | ln(1) = 0 (symbolic verification) | — |
| A2 | eml(x, 1) - exp(x) = 0 (symbolic simplification) | — |
| A3 | Numerical spot-check at 5 complex points | — |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | ln(1) = 0 (symbolic verification) | SymPy symbolic evaluation of ln(1); verify equals 0 | Confirmed: ln(1) = 0 |
| A2 | eml(x, 1) - exp(x) = 0 (symbolic simplification) | SymPy symbolic simplification of exp(x) - ln(1) - exp(x); verify result is identically 0 for symbolic x | Confirmed: residual = 0 |
| A3 | Numerical spot-check at 5 complex points | Numerical evaluation of |eml(x,1) - exp(x)| at x = 0, 1, -3, i*pi, 2+3i using Python cmath; verify all < 1e-15 | Confirmed: max residual = 0.00e+00 |

*Source: proof.py JSON summary*

## Computation Traces

```
  A1: ln(1) = 0: 0 == 0 = True
  A2: simplify(eml(x,1) - exp(x)) = 0: 0 == 0 = True
  x =            0  |eml(x,1) - exp(x)| = 0.00e+00
  x =            1  |eml(x,1) - exp(x)| = 0.00e+00
  x =           -3  |eml(x,1) - exp(x)| = 0.00e+00
  x = 3.141592653589793j  |eml(x,1) - exp(x)| = 0.00e+00
  x =       (2+3j)  |eml(x,1) - exp(x)| = 0.00e+00
  A3: numerical spot-checks at 5 complex points all < 1e-15: True == True = True
  All facts verified (symbolic + numerical): True == True = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

### Check 1: Does ln(1) = 0 hold for the complex logarithm?

- **Question:** Does ln(1) = 0 hold for the complex logarithm?
- **Verification performed:** The principal branch of the complex logarithm is defined as Log(z) = ln|z| + i*Arg(z) where Arg is the principal argument in (-pi, pi]. For z = 1: |1| = 1, Arg(1) = 0, so Log(1) = ln(1) + i*0 = 0. This holds regardless of branch cut conventions since z = 1 is on the positive real axis.
- **Finding:** ln(1) = 0 holds universally for the principal branch of the complex logarithm. No branch ambiguity at z = 1.
- **Breaks proof:** No

### Check 2: Is the operator well-defined for all complex x?

- **Question:** Is the operator well-defined for all complex x?
- **Verification performed:** eml(x, 1) = exp(x) - ln(1). The exponential function exp(x) is entire (defined for all complex x). ln(1) = 0 is a constant. The subtraction of a constant from an entire function is entire. The only concern would be if b = 0 (since ln(0) is undefined), but the claim fixes b = 1.
- **Finding:** eml(x, 1) is well-defined for every complex x. The operator eml(a, b) has a singularity at b = 0, but the claim only evaluates at b = 1.
- **Breaks proof:** No

### Check 3: Could numerical precision mask a nonzero residual?

- **Question:** Could numerical precision mask a nonzero residual?
- **Verification performed:** The symbolic computation uses SymPy's exact symbolic engine, not floating-point arithmetic. simplify(exp(x) - ln(1) - exp(x)) returns exactly 0, not an approximation. The numerical cross-check is supplementary — the proof rests on the symbolic result.
- **Finding:** The symbolic residual is exactly 0 — no numerical precision issue can affect it. Numerical cross-checks confirm agreement to machine epsilon.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A — pure computation, no empirical facts
- **Rule 2:** N/A — pure computation, no empirical facts
- **Rule 3:** N/A — proof is not time-sensitive; date.today() used only in generator metadata
- **Rule 4:** CLAIM_FORMAL with operator_note present; documents the ln(1) = 0 reduction and principal branch convention
- **Rule 5:** 3 adversarial checks: complex logarithm branch, well-definedness, numerical precision
- **Rule 6:** N/A — pure computation, no empirical facts. Cross-check uses mathematically independent method (numerical evaluation vs. symbolic algebra)
- **Rule 7:** All computations via SymPy (symbolic) and cmath (numerical); no hard-coded constants
- **validate_proof.py result:** PASS — 16/16 checks passed, 0 issues, 0 warnings

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-16.
