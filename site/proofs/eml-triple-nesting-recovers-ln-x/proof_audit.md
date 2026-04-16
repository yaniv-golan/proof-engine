# Audit: \(\text{eml}(1, \text{eml}(\text{eml}(1, x), 1)) = \ln(x)\) for all real \(x > 0\)

- **Generated:** 2026-04-16
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The claim defines eml(a, b) = exp(a) - ln(b) and asserts that for every real x > 0, the triple nesting eml(1, eml(eml(1, x), 1)) equals ln(x). This is a symbolic identity involving three nested applications of the same operator at specific argument patterns.

The formal interpretation uses exact equality (==) with threshold True. The operator_note documents the full inside-out derivation: (1) eml(1, x) = e - ln(x), (2) eml(e - ln(x), 1) = exp(e)/x, (3) eml(1, exp(e)/x) = e - ln(exp(e)/x) = ln(x). The domain restriction x > 0 ensures all logarithms are real-valued and ln(exp(y)) = y holds without branch ambiguity.

**Formalization scope:** The formal interpretation is a faithful 1:1 mapping of the natural-language claim. The operator eml is fully defined, the nesting structure is explicit, and the domain x > 0 is stated in the claim. The only interpretive choice is confirming that ln denotes the real natural logarithm (equivalently, the principal branch restricted to positive reals), which the claim specifies.

**Attribution:** This result was originally established in R. Cheng, "The elementary function arithmetic," arXiv:2603.21852 (2026). The proof presented here provides independent computational verification using symbolic algebra (SymPy) and numerical methods, and was developed without reference to the original proof.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Binary operator eml(a, b) = exp(a) - ln(b) |
| Property | eml(1, eml(eml(1, x), 1)) = ln(x) for all real x > 0 |
| Operator | == |
| Threshold | True |
| Operator Note | The claim asserts a symbolic identity for the triple nesting of eml. Working inside out: (1) eml(1, x) = exp(1) - ln(x) = e - ln(x). (2) eml(eml(1, x), 1) = exp(e - ln(x)) - ln(1) = exp(e)/x. (3) eml(1, exp(e)/x) = exp(1) - ln(exp(e)/x) = e - (e - ln(x)) = ln(x). The domain restriction x > 0 ensures ln(x) is real-valued. The proof verifies symbolically that the nested expression minus ln(x) simplifies to 0 for symbolic positive x. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | eml(1, x) = e - ln(x) (inner evaluation) | — |
| A2 | eml(eml(1, x), 1) = exp(e)/x (middle evaluation) | — |
| A3 | eml(1, eml(eml(1, x), 1)) - ln(x) = 0 (full identity) | — |
| A4 | Numerical spot-check at 6 positive real points | — |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | eml(1, x) = e - ln(x) (inner evaluation) | SymPy symbolic evaluation of eml(1, x) = exp(1) - ln(x) for positive symbol x; verify simplify(result - (E - ln(x))) = 0 | Confirmed: eml(1, x) = e - ln(x) |
| A2 | eml(eml(1, x), 1) = exp(e)/x (middle evaluation) | SymPy symbolic evaluation of eml(eml(1, x), 1) for positive symbol x; verify simplify(result - exp(E)/x) = 0 | Confirmed: eml(eml(1, x), 1) = exp(e)/x |
| A3 | eml(1, eml(eml(1, x), 1)) - ln(x) = 0 (full identity) | SymPy symbolic evaluation of eml(1, eml(eml(1, x), 1)) for positive symbol x; verify simplify(result - ln(x)) = 0 | Confirmed: full nested expression = ln(x), residual = 0 |
| A4 | Numerical spot-check at 6 positive real points | Numerical evaluation of eml(1, eml(eml(1, x), 1)) - ln(x) at x = 0.01, 0.5, 1, 2, e, 100 using Python math; verify all < 1e-10 | Confirmed: max |diff| = 8.88e-16 |

*Source: proof.py JSON summary*

## Computation Traces

```
  A1: eml(1, x) - (e - ln(x)) = 0: 0 == 0 = True
  A2: eml(eml(1, x), 1) - exp(e)/x = 0: 0 == 0 = True
  A3: eml(1, eml(eml(1, x), 1)) - ln(x) = 0: 0 == 0 = True
  x =     0.01  nested =   -4.605170185988092  ln(x) =   -4.605170185988091  |diff| = 8.88e-16
  x =      0.5  nested =   -0.693147180559945  ln(x) =   -0.693147180559945  |diff| = 1.11e-16
  x =      1.0  nested =    0.000000000000000  ln(x) =    0.000000000000000  |diff| = 0.00e+00
  x =      2.0  nested =    0.693147180559945  ln(x) =    0.693147180559945  |diff| = 1.11e-16
  x = 2.718281828459045  nested =    1.000000000000000  ln(x) =    1.000000000000000  |diff| = 0.00e+00
  x =    100.0  nested =    4.605170185988092  ln(x) =    4.605170185988092  |diff| = 0.00e+00
  A4: all numerical spot-checks agree within 1e-10: True == True = True
  All facts verified (symbolic + numerical): True == True = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

### Check 1: Does the identity hold at x -> 0+?

- **Question:** Does the identity hold at the boundary x -> 0+?
- **Verification performed:** As x -> 0+, ln(x) -> -infinity. The inner expression eml(1, x) = e - ln(x) -> +infinity. Then eml(eml(1, x), 1) = exp(e - ln(x)) -> +infinity. Then eml(1, eml(...)) = e - ln(exp(e - ln(x))) = e - (e - ln(x)) = ln(x) -> -infinity. The algebraic identity holds for all x > 0 regardless of how large or small x is; the intermediate values may be extreme, but the cancellations are exact. The numerical test at x = 0.01 confirms this.
- **Finding:** The identity holds even as x -> 0+. The intermediate expressions diverge, but the final cancellation is algebraically exact.
- **Breaks proof:** No

### Check 2: Does the identity hold at x -> +infinity?

- **Question:** Does the identity hold at x -> +infinity?
- **Verification performed:** As x -> +infinity, ln(x) -> +infinity. eml(1, x) = e - ln(x) -> -infinity. eml(eml(1, x), 1) = exp(e - ln(x)) -> 0+. eml(1, exp(e - ln(x))) = e - ln(exp(e - ln(x))) = e - (e - ln(x)) = ln(x). Again the algebraic cancellation is exact. The numerical test at x = 100 confirms the identity holds for large x.
- **Finding:** The identity holds as x -> +infinity. Despite intermediate expressions approaching 0 or -infinity, the cancellation is exact.
- **Breaks proof:** No

### Check 3: Is ln(exp(y)) = y always valid for x > 0?

- **Question:** Is ln(exp(e - ln(x))) = e - ln(x) always valid for x > 0?
- **Verification performed:** For real y, ln(exp(y)) = y holds for all real y (the natural logarithm and exponential are inverse functions on the reals). Here y = e - ln(x), which is real for any x > 0. So ln(exp(e - ln(x))) = e - ln(x) without restriction. This step would fail for complex x where branch cuts matter, but the claim restricts to real x > 0.
- **Finding:** ln(exp(y)) = y holds for all real y. Since the claim restricts to x > 0 (making e - ln(x) real), no branch cut issue arises.
- **Breaks proof:** No

### Check 4: Could numerical overflow cause false agreement?

- **Question:** Could numerical overflow in exp(e - ln(x)) cause false agreement?
- **Verification performed:** For small x (e.g., x = 0.01), e - ln(x) ≈ 7.323, so exp(7.323) ≈ 1512 — well within float64 range. For very small x (e.g., x = 1e-300), e - ln(x) ≈ 694, and exp(694) ≈ 1e301 — still representable. Overflow would require x < exp(-exp(709)) which is below the smallest positive float. The symbolic proof does not depend on floating-point at all; the numerical cross-check is supplementary.
- **Finding:** No overflow risk for representable positive floats. The proof rests on exact symbolic algebra, not numerics.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A — pure computation, no empirical facts
- **Rule 2:** N/A — pure computation, no empirical facts
- **Rule 3:** N/A — proof is not time-sensitive; date.today() used only in generator metadata
- **Rule 4:** CLAIM_FORMAL with operator_note present; documents the full inside-out derivation and domain restriction
- **Rule 5:** 4 adversarial checks: boundary behavior at x -> 0+ and x -> +infinity, ln(exp(y)) = y validity, numerical overflow risk
- **Rule 6:** N/A — pure computation, no empirical facts. Cross-check uses mathematically independent method (numerical evaluation via Python math vs. symbolic algebra via SymPy)
- **Rule 7:** All computations via SymPy (symbolic) and math (numerical); no hard-coded constants
- **validate_proof.py result:** PASS — 16/16 checks passed, 0 issues, 0 warnings

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-16.
