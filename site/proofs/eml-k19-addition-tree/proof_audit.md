# Audit: A K=19 binary tree of eml operations evaluates to x + y

- **Generated:** 2026-04-16
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The claim defines eml(a, b) = exp(a) - ln(b) and asserts that a specific binary tree of 9 eml operations and 10 leaves (drawn from {1, x, y}) evaluates to x + y. The total token count K = 9 + 10 = 19. The user's original claim referred to "depth 19"; in the paper's framework (arXiv:2603.21852), K denotes the RPN code length (total tree nodes), not the tree height. The actual tree height is 9.

The formal interpretation uses exact equality (==) with threshold True. The operator_note documents the full inside-out derivation through 9 layers, identifying two known eml sub-patterns: the triple-nesting identity (steps 3-5, which computes ln of a sub-expression) and the subtraction identity eml(ln(a), exp(b)) = a - b (step 7).

The expression has a removable singularity at x = e (where E2 = e - x = 0). The identity holds for all real x != e and at x = e in the limit sense, verified by SymPy's limit function from both sides.

For the complex domain, the identity is interpreted as a formal algebraic identity where ln(exp(z)) = z (the paper's framework). On the principal branch of the complex logarithm, the identity holds when |Im(x + y)| < pi. Beyond that boundary, the error is exactly 2*k*pi*i for integer k.

**Formalization scope:** The formal interpretation is a faithful mapping of the natural-language claim. The token count K = 19 is explicitly verified. The "for all complex x and y" clause is interpreted in the formal algebraic setting, with the principal-branch limitation documented. The expression was constructed analytically (not extracted from the referenced paper) and verified independently. The removable singularity at x = e is documented and verified via limit analysis.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Binary operator eml(a, b) = exp(a) - ln(b) |
| Property | eml(1, eml(eml(eml(1, eml(eml(1, eml(1, eml(x, 1))), 1)), eml(y, 1)), 1)) = x + y for all real x, y (x != e) |
| Operator | == |
| Threshold | True |
| Operator Note | The claim asserts that a specific K=19 binary tree of eml operations evaluates to x + y. K denotes the total number of tree nodes (9 internal eml nodes + 10 leaves = 19). Working inside out through 9 layers: (1) E1 = eml(x, 1) = exp(x). (2) E2 = eml(1, E1) = e - x. (3) E3 = eml(1, E2) = e - ln(e-x). (4) E4 = eml(E3, 1) = exp(e)/(e-x). (5) E5 = eml(1, E4) = ln(e-x). Steps 3-5 are the triple-nesting identity applied to (e-x). (6) E6 = eml(y, 1) = exp(y). (7) E7 = eml(E5, E6) = (e-x) - y = e - x - y. This is the eml-subtraction identity eml(ln(a), exp(b)) = a - b. (8) E8 = eml(E7, 1) = exp(e - x - y). (9) E9 = eml(1, E8) = e - ln(exp(e-x-y)) = e - (e-x-y) = x + y. The expression is undefined at x = e (where E2 = 0 causes log(0) in E3); this is a removable singularity — the limit from both sides equals e + y = x + y, verified by SymPy. For complex x, y: the identity holds as a formal algebraic identity where ln(exp(z)) = z (i.e., on the Riemann surface of log). On the principal branch, it holds when |Im(x+y)| < pi; beyond that, the error is exactly 2*k*pi*i for integer k. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | Token count K = 19 (9 eml operations + 10 leaves) | -- |
| A2 | Step-by-step symbolic evaluation: E9 = x + y | -- |
| A3 | Full expression minus (x + y) = 0 | -- |
| A4 | Removable singularity at x = e: limit equals e + y | -- |
| A5 | Numerical spot-check at 10 real-valued (x, y) pairs | -- |
| A6 | Numerical spot-check at 5 complex-valued (x, y) pairs | -- |
| A7 | Exhaustive search: no K <= 15 eml tree computes x + y | -- |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Token count K = 19 (9 eml operations + 10 leaves) | Programmatic parsing of the expression string to count eml operation nodes and leaf nodes (1, x, y) | Confirmed: 9 eml + 10 leaves = K = 19 |
| A2 | Step-by-step symbolic evaluation: E9 = x + y | SymPy symbolic evaluation through 9 layers: build each sub-expression E1..E9 with simplification at each step, verify residuals at 5 critical algebraic cancellation points (E1=exp(x), E2=e-x, E4=exp(e)/(e-x), E7=e-x-y, E9=x+y) all equal zero | Confirmed: all 5 critical residuals = 0, E9 = x + y |
| A3 | Full expression minus (x + y) = 0 | SymPy simplify(E9 - (x + y)) for real symbols x, y; verify residual equals 0 | Confirmed: residual = 0 |
| A4 | Removable singularity at x = e: limit equals e + y | SymPy limit(E9, x, e) from left, right, and both sides; verify all three equal e + y | Confirmed: limit from left = y + E, from right = y + E, both = e + y |
| A5 | Numerical spot-check at 10 real-valued (x, y) pairs | Numerical evaluation of the full 9-layer chain at 10 real-valued (x, y) pairs spanning [-100, 100], including x = 0, x > e, x near the singularity at e (within 1e-12); verify |result - (x+y)| < 1e-6 | Confirmed: max |diff| = 1.26e-14 |
| A6 | Numerical spot-check at 5 complex-valued (x, y) pairs | Numerical evaluation of the full 9-layer chain at 5 complex-valued (x, y) pairs with |Im(x+y)| < pi (principal-branch domain); verify |result - (x+y)| < 1e-10 | Confirmed: max |diff| = 1.34e-15 |
| A7 | Exhaustive search: no K <= 15 eml tree computes x + y | Embedded exhaustive bottom-up search: enumerate all distinct eml binary trees with leaves {1, x, y} at each odd K from 1 to 15 using numerical fingerprinting at a generic complex test point; check if x+y appears | Confirmed: 1,980,526 distinct values at K=15, x+y not found at any K <= 15 |

*Source: proof.py JSON summary*

## Computation Traces

```
  Token count: 9 eml operations + 10 leaves = K = 19
  A1: K = 19: 19 == 19 = True
  Step-by-step evaluation:
    E1=eml(x,1) = exp(x)
    E2=eml(1,E1) = E - x
    E3=eml(1,E2) = E - log(E - x)
    E4=eml(E3,1) = -exp(E)/(x - E)
    E5=eml(1,E4) = -log(-1/(x - E))
    E6=eml(y,1) = exp(y)
    E7=eml(E5,E6) = -x - y + E
    E8=eml(E7,1) = exp(-x - y + E)
    E9=eml(1,E8) = x + y
  A2a: E1 = exp(x): 0 == 0 = True
  A2b: E2 = e - x: 0 == 0 = True
  A2c: E4 = exp(e)/(e-x): 0 == 0 = True
  A2d: E7 = e - x - y: 0 == 0 = True
  A2e: E9 = x + y: 0 == 0 = True
  A3: E9 - (x+y) = 0: 0 == 0 = True
  Limit as x -> e-: y + E
  Limit as x -> e+: y + E
  Limit as x -> e:  y + E
  A4: limit(E9, x->e) = e + y from both sides: True == True = True
  Numerical (real):
    x=                   2, y=           3  |diff|=0.00e+00
    x=                  -5, y=           8  |diff|=4.44e-16
    x=                 100, y=         -99  |diff|=1.26e-14
    x=               0.001, y=       0.002  |diff|=5.58e-16
    x=                 2.5, y=     3.14159  |diff|=0.00e+00
    x=                -100, y=       100.5  |diff|=4.00e-15
    x=                   0, y=           0  |diff|=0.00e+00
    x=      2.718280828459, y=           0  |diff|=0.00e+00
    x=      2.718282828459, y=           0  |diff|=1.22e-22
    x=      2.718281828458, y=     2.71828  |diff|=0.00e+00
  A5: all real spot-checks agree within 1e-6: True == True = True
  Numerical (complex, |Im(x+y)| < pi):
    x=    (1+0.5j), y=    (2-0.3j)  |Im|=0.2  |diff|=1.67e-16
    x=    (0.5+1j), y=   (-1.5+2j)  |Im|=3.0  |diff|=0.00e+00
    x=   (-3+0.7j), y=    (4-0.7j)  |Im|=0.0  |diff|=1.34e-15
    x=          1j, y=     (-0-1j)  |Im|=0.0  |diff|=4.58e-16
    x=      (2+3j), y=   (-1-0.1j)  |Im|=2.9  |diff|=0.00e+00
  A6: all complex spot-checks agree within 1e-10: True == True = True
  Exhaustive search K=1..15:
    K= 1:          3 distinct values
    K= 3:          9 distinct values
    K= 5:         54 distinct values
    K= 7:        380 distinct values
    K= 9:      2,971 distinct values
    K=11:     24,836 distinct values
    K=13:    217,969 distinct values
    K=15:  1,980,526 distinct values
    Search time: 3.13s
    x+y found at K <= 15: None
  A7: no K <= 15 tree computes x+y: True == True = True
  All facts verified (symbolic + numerical + search): True == True = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

### Check 1: Does the identity hold for real x > e?

- **Question:** Does the identity hold for real x > e, where the intermediate value e - x is negative?
- **Verification performed:** For x > e (e.g., x = 100), E2 = e - x < 0. Then E3 = e - log(e-x) involves log of a negative real, producing a complex intermediate with imaginary part -pi*i. Tracing: E3 = (e - ln|e-x|) - pi*i, E4 = exp(E3) = -(exp(e)/|e-x|) (negative real), E5 = e - log(E4) = ln|e-x| - pi*i. Then E7 = exp(E5) - log(exp(y)) = -(e-x) - y = e-x-y (real). The +/-pi*i terms cancel exactly. Numerical tests at x=100/y=-99 and x=e+1e-6/y=0 confirm |diff| < 2e-14.
- **Finding:** The identity holds for all real x != e (including x > e). Intermediate complex values with +/-pi*i cancel perfectly.
- **Breaks proof:** No

### Check 2: Is x = e a genuine exception or a removable singularity?

- **Question:** Is x = e a genuine exception or a removable singularity?
- **Verification performed:** At x = e, E2 = 0, and E3 = eml(1, 0) = e - log(0) is undefined (log(0) = -infinity). SymPy's limit() function confirms: lim_{x->e-} E9 = e + y, lim_{x->e+} E9 = e + y, and the two-sided limit = e + y. Since both one-sided limits exist and equal x + y = e + y, this is a removable singularity. Numerical evaluation at x = e - 1e-12 gives |diff| < 1e-6, confirming the expression approaches the correct value.
- **Finding:** x = e is a removable singularity. The expression is undefined at that single point but its limit from both sides equals e + y. The identity holds for all real x except this isolated point.
- **Breaks proof:** No

### Check 3: Complex branch cut analysis

- **Question:** Does the identity hold for arbitrary complex x, y on the principal branch of log?
- **Verification performed:** E9 = e - log(exp(e - x - y)). On the principal branch, log(exp(z)) = z iff Im(z) in (-pi, pi]. Since Im(e - x - y) = -Im(x + y), the identity holds when |Im(x + y)| < pi. Verification: x=0.5+i, y=-1.5+2i gives Im(x+y)=3 < pi and |diff|=0. x=1+2i, y=1+2i gives Im(x+y)=4 > pi and |diff|=2*pi (branch-cut error of exactly 2*pi*i). In the paper's formal algebraic framework, ln(exp(z)) = z is an axiom (equivalently, working on the Riemann surface), and the identity holds for all complex x, y.
- **Finding:** On the principal branch: holds when |Im(x+y)| < pi. As a formal algebraic identity: holds for all complex x, y. The branch-cut error is always exactly 2*k*pi*i.
- **Breaks proof:** No

### Check 4: Minimality of K = 19

- **Question:** Is K = 19 the minimum code length for addition?
- **Verification performed:** An embedded exhaustive search (A7) enumerated all distinct eml trees through K=15 (1,980,526 distinct values at K=15) and found no expression evaluating to x+y. A separate external search extended through K=17 (18,470,098 distinct values, 572 seconds) with the same result: closest match at K=17 was |diff|=2.0e-3, not a match. No expression at K <= 17 computes x+y. This is consistent with the result in arXiv:2603.21852 that K=19 is minimal for addition.
- **Finding:** Exhaustive search through K=15 (embedded, reproducible) and K=17 (external) found no eml tree computing x+y. K=19 is confirmed minimal.
- **Breaks proof:** No

### Check 5: Numerical overflow risk

- **Question:** Could numerical overflow cause false agreement?
- **Verification performed:** The largest intermediate value in the chain is E4 or E8. E4 = exp(e)/(e-x): for x near e, this diverges (the singularity), but E5 = log(E4) brings it back down. E8 = exp(e-x-y): for x=-100, y=100.5, E8 = exp(e-0.5) ~ 9.19. The log-exp cancellation in E5=ln(e-x) undoes the exponential growth from E4, keeping the chain bounded. The symbolic proof does not depend on floating-point.
- **Finding:** No overflow risk. The log-exp cancellation at E5 bounds intermediate values. The proof rests on exact symbolic algebra.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A -- pure computation, no empirical facts
- **Rule 2:** N/A -- pure computation, no empirical facts
- **Rule 3:** N/A -- proof is not time-sensitive; date.today() used only in generator metadata
- **Rule 4:** CLAIM_FORMAL with operator_note present; documents the full 9-layer inside-out derivation, domain restrictions, removable singularity at x = e, and complex branch-cut behavior
- **Rule 5:** 5 adversarial checks: large-x behavior with +/-pi*i cancellation, singularity analysis with limit verification, complex branch cut boundary, minimality cross-reference with embedded search, numerical overflow risk
- **Rule 6:** N/A -- pure computation, no empirical facts. Cross-checks use mathematically independent methods (numerical evaluation via cmath vs. symbolic algebra via SymPy; exhaustive search vs. analytical construction)
- **Rule 7:** All computations via SymPy (symbolic) and cmath (numerical); no hard-coded constants
- **validate_proof.py result:** PASS -- 16/16 checks passed, 0 issues, 0 warnings

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-16.
