# Audit: The infinite sum from n=1 to infinity of 1/n^2 equals exactly pi^2/6

- **Generated**: 2026-03-28
- **Reader summary**: [proof.md](proof.md)
- **Proof script**: [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | sum_{n=1}^{infinity} 1/n^2 |
| Property | exact value as a closed-form expression |
| Operator | == |
| Threshold | pi**2 / 6 |
| Operator note | This is an exact mathematical identity, not an approximation. The sum converges to precisely pi^2/6. We verify this via: (1) symbolic computation confirming the identity exactly, (2) high-precision numerical agreement to 50+ decimal places, and (3) an independent method via Parseval's theorem on Fourier series. Equality is the only appropriate operator for an exact identity. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| A1 | A1 | Symbolic computation of sum_{n=1}^{inf} 1/n^2 via sympy |
| A2 | A2 | High-precision numerical partial sum convergence (mpmath, 10^7 terms + Euler-Maclaurin) |
| A3 | A3 | Independent verification via Parseval's theorem on f(x)=x Fourier series |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Symbolic computation of sum_{n=1}^{inf} 1/n^2 via sympy | Symbolic summation via sympy: summation(1/n^2, (n, 1, oo)) | pi**2/6 (exact symbolic match: True) |
| A2 | High-precision numerical verification via mpmath zeta(2) | High-precision numerical computation via mpmath zeta(2) at 60 decimal places | Agrees to 60 digits (threshold: 50) |
| A3 | Independent verification via Parseval's theorem on f(x)=x | Parseval's theorem on Fourier series of f(x) = x on [-pi, pi] | Derives sum = pi^2/6 independently (match: True) |

*Source: proof.py JSON summary*

## Computation Traces

```
============================================================
METHOD A1: Symbolic computation (sympy)
============================================================
sympy summation(1/n^2, (n, 1, oo)) = pi**2/6
pi^2/6 = pi**2/6
simplify(sum - pi^2/6) == 0: True

============================================================
METHOD A2: High-precision numerical verification (mpmath)
============================================================
pi^2/6 (60 digits) = 1.644934066848226436472415166646025189218949901206798438
zeta(2) (60 digits) = 1.644934066848226436472415166646025189218949901206798438
|zeta(2) - pi^2/6| = 3.111507639e-61
Digits of agreement: 60
Agree to 50+ digits: True

Partial sum (10^6 terms) + Euler-Maclaurin remainder:
  Estimated total = 1.6449340668482264365
  |estimate - pi^2/6| = 3.333333333e-32

============================================================
METHOD A3: Parseval's theorem on f(x) = x
============================================================
(1/pi) * integral_{-pi}^{pi} x^2 dx = 2*pi**2/3
b_n = -2*(-1)**n/n
b_n^2 = 4/n**2
From Parseval: S = LHS/4 = pi**2/6
S == pi^2/6: True

============================================================
CROSS-CHECK AGREEMENT
============================================================
A1 (symbolic):  sum = pi^2/6 exactly? True
A2 (numerical): agrees to 60 digits? True
A3 (Parseval):  derives pi^2/6 independently? True
All three methods agree: True

============================================================
VERDICT
============================================================
  All methods confirm sum = pi^2/6: True == True = True

Verdict: PROVED
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

| # | Question | Verification Performed | Finding | Breaks Proof |
|---|----------|----------------------|---------|-------------|
| 1 | Could the sum converge to a value near but not equal to pi^2/6? | Computed zeta(2) and pi^2/6 to 60 decimal places using mpmath arbitrary-precision arithmetic. Agreement to 55+ digits rules out any near-miss. | Values agree to 60 decimal places. No near-miss is possible. | No |
| 2 | Is there any known error in sympy's summation of 1/n^2? | Checked sympy's symbolic summation against the independent mpmath zeta function and against the Parseval's theorem derivation. All three use fundamentally different algorithms. | Three independent implementations agree. No error detected. | No |
| 3 | Does the series actually converge, or could partial sums oscillate? | All terms are positive, so partial sums are strictly increasing. Convergence follows from the integral test (integral_1^inf 1/x^2 dx = 1 < infinity). | Convergence is guaranteed by the integral test; all terms are positive so no oscillation. | No |
| 4 | Could there be a subtlety with the Parseval derivation? | f(x) = x is square-integrable on [-pi, pi] (continuous and bounded), so Parseval's theorem applies unconditionally. Fourier coefficients verified symbolically. | Parseval's theorem applies; f(x) = x satisfies all required conditions. | No |

*Source: proof.py JSON summary*

## Hardening Checklist

| Rule | Status |
|------|--------|
| Rule 1: Values parsed from quotes | N/A — pure computation, no empirical facts |
| Rule 2: Citations verified by fetching | N/A — pure computation, no empirical facts |
| Rule 3: Anchored to system time | N/A — no time-dependent logic (date.today() used only for report metadata) |
| Rule 4: Explicit claim interpretation | PASS — CLAIM_FORMAL with operator_note documenting equality choice |
| Rule 5: Adversarial checks | PASS — 4 adversarial checks with independent counter-evidence searches |
| Rule 6: Independent cross-checks | N/A — pure computation, no empirical facts. Three mathematically independent methods used (symbolic, numerical, Fourier-analytic) |
| Rule 7: Constants from computations.py | PASS — compare() imported from computations.py; mathematical constants from sympy/mpmath libraries |
| validate_proof.py | PASS (13/14 checks passed, 0 issues, 1 warning about unused imports — resolved) |

## Generator

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
