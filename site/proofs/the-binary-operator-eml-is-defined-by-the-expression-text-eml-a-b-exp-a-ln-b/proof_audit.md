# Audit: \(\text{eml}(1, 1) = e\)

- **Generated:** 2026-04-16
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The claim defines a binary operator eml(a, b) = exp(a) - ln(b) and asserts that evaluating it at (1, 1) yields the mathematical constant e. This is a specific-point evaluation: eml(1, 1) = exp(1) - ln(1). Since exp(1) = e by definition and ln(1) = 0, the result is e - 0 = e.

The formal interpretation uses exact equality (==) with threshold True. The operator_note documents the complete reasoning chain: substitution, evaluation of exp(1) and ln(1), and the conclusion that the result is an exact algebraic identity.

**Formalization scope:** The formal interpretation is a faithful 1:1 mapping of the natural-language claim. The operator eml is fully defined in the claim, the input values are explicit (a = 1, b = 1), and the expected output (e) is unambiguous. The only interpretive choice is using the principal branch of the complex logarithm, which is the standard convention and produces the unique value ln(1) = 0.

**Attribution:** This result was originally established in A. Odrzywołek, "All elementary functions from a single binary operator," arXiv:2603.21852 (2026). The proof presented here provides independent computational verification using symbolic algebra (SymPy) and numerical methods, and was developed without reference to the original proof.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Binary operator eml(a, b) = exp(a) - ln(b) |
| Property | eml(1, 1) = e |
| Operator | == |
| Threshold | True |
| Operator Note | Substituting a = 1, b = 1: eml(1, 1) = exp(1) - ln(1). exp(1) = e by definition of the exponential function. ln(1) = 0 (principal branch of the complex logarithm: Log(1) = ln\|1\| + i*Arg(1) = 0 + 0 = 0). Therefore eml(1, 1) = e - 0 = e. This is an exact algebraic identity, not a numerical approximation. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | exp(1) = e (symbolic verification) | — |
| A2 | ln(1) = 0 (symbolic verification) | — |
| A3 | eml(1, 1) - e = 0 (symbolic simplification) | — |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | exp(1) = e (symbolic verification) | SymPy symbolic evaluation: simplify(exp(1) - E); verify equals 0 | Confirmed: exp(1) = e |
| A2 | ln(1) = 0 (symbolic verification) | SymPy symbolic evaluation of ln(1); verify equals 0 | Confirmed: ln(1) = 0 |
| A3 | eml(1, 1) - e = 0 (symbolic simplification) | SymPy symbolic simplification of exp(1) - ln(1) - E; verify result is 0 | Confirmed: residual = 0 |

*Source: proof.py JSON summary*

## Computation Traces

```
  A1: exp(1) - e = 0: 0 == 0 = True
  A2: ln(1) = 0: 0 == 0 = True
  A3: simplify(eml(1,1) - e) = 0: 0 == 0 = True
  Numerical: eml(1,1) = 2.718281828459045
  Numerical: e        = 2.718281828459045
  |eml(1,1) - e|      = 0.00e+00
  Numerical cross-check: |eml(1,1) - e| < 1e-15: True == True = True
  All facts verified (symbolic + numerical): True == True = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

### Check 1: Is exp(1) exactly e?

- **Question:** Is exp(1) exactly e, or just an approximation?
- **Verification performed:** The exponential function exp is defined such that exp(1) = e by definition. In SymPy, exp(1) returns the symbolic constant E (Euler's number), not a floating-point approximation. The identity exp(1) = e is definitional, not computed.
- **Finding:** exp(1) = e is exact and definitional. No approximation is involved.
- **Breaks proof:** No

### Check 2: Does ln(1) = 0 hold for the complex logarithm?

- **Question:** Does ln(1) = 0 hold for the complex logarithm?
- **Verification performed:** The principal branch of the complex logarithm is defined as Log(z) = ln|z| + i*Arg(z) where Arg is the principal argument in (-pi, pi]. For z = 1: |1| = 1, Arg(1) = 0, so Log(1) = ln(1) + i*0 = 0. This holds regardless of branch cut conventions since z = 1 is on the positive real axis.
- **Finding:** ln(1) = 0 holds universally for the principal branch of the complex logarithm. No branch ambiguity at z = 1.
- **Breaks proof:** No

### Check 3: Could SymPy's simplify() miss a nonzero result?

- **Question:** Could SymPy's simplify() fail to reduce a nonzero expression to zero?
- **Verification performed:** For the expression exp(1) - ln(1) - E, SymPy evaluates exp(1) to E and ln(1) to 0 before simplify() is even called. The expression becomes E - 0 - E = 0, which is trivial constant arithmetic. There is no symbolic variable or complex cancellation involved. Additionally, the numerical cross-check confirms the result independently.
- **Finding:** The simplification is trivial constant folding (E - 0 - E = 0). No risk of simplify() missing a cancellation.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A — pure computation, no empirical facts
- **Rule 2:** N/A — pure computation, no empirical facts
- **Rule 3:** N/A — proof is not time-sensitive; date.today() used only in generator metadata
- **Rule 4:** CLAIM_FORMAL with operator_note present; documents the substitution, evaluation, and principal branch convention
- **Rule 5:** 3 adversarial checks: definitional exactness of exp(1), complex logarithm branch at z = 1, simplification reliability
- **Rule 6:** N/A — pure computation, no empirical facts. Cross-check uses mathematically independent method (numerical evaluation via cmath/math vs. symbolic algebra via SymPy)
- **Rule 7:** All computations via SymPy (symbolic) and cmath/math (numerical); no hard-coded constants
- **validate_proof.py result:** PASS — 16/16 checks passed, 0 issues, 0 warnings

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-16.
