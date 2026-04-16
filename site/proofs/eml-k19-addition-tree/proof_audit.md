# Audit: A K=19 binary tree of eml operations evaluates to x + y

- **Generated:** 2026-04-16
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The claim defines eml(a, b) = exp(a) - ln(b) and asserts that a specific binary tree of 9 eml operations and 10 leaves (drawn from {1, x, y}) evaluates to x + y. The total token count K = 9 + 10 = 19. The user's original claim referred to "depth 19"; in the paper's framework (arXiv:2603.21852), K denotes the RPN code length (total tree nodes), not the tree height. The actual tree height is 9.

The formal interpretation uses exact equality (==) with threshold True. The operator_note documents the full inside-out derivation through 9 layers, identifying two known eml sub-patterns: the triple-nesting identity (steps 3-5, which computes ln of a sub-expression) and the subtraction identity eml(ln(a), exp(b)) = a - b (step 7).

For the complex domain, the identity is interpreted as a formal algebraic identity where ln(exp(z)) = z (the paper's framework). On the principal branch of the complex logarithm, the identity holds when |Im(x + y)| < pi.

The expression has a removable singularity at x = e (where E2 = e - x = 0). The identity holds for all real x != e and at x = e in the limit sense.

**Formalization scope:** The formal interpretation is a faithful mapping of the natural-language claim. The token count K = 19 is explicitly verified. The "for all complex x and y" clause is interpreted in the formal algebraic setting, with the principal-branch limitation documented. The expression was constructed analytically (not extracted from the referenced paper) and verified independently.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Binary operator eml(a, b) = exp(a) - ln(b) |
| Property | eml(1, eml(eml(eml(1, eml(eml(1, eml(1, eml(x, 1))), 1)), eml(y, 1)), 1)) = x + y |
| Operator | == |
| Threshold | True |
| Operator Note | The claim asserts that a specific K=19 binary tree of eml operations evaluates to x + y. K denotes the total number of tree nodes (9 internal eml nodes + 10 leaves = 19). Working inside out through 9 layers: (1) E1 = eml(x, 1) = exp(x). (2) E2 = eml(1, E1) = e - x. (3) E3 = eml(1, E2) = e - ln(e-x). (4) E4 = eml(E3, 1) = exp(e)/(e-x). (5) E5 = eml(1, E4) = ln(e-x). Steps 3-5 are the triple-nesting identity applied to (e-x). (6) E6 = eml(y, 1) = exp(y). (7) E7 = eml(E5, E6) = (e-x) - y = e - x - y. This is the eml-subtraction identity eml(ln(a), exp(b)) = a - b. (8) E8 = eml(E7, 1) = exp(e - x - y). (9) E9 = eml(1, E8) = e - ln(exp(e-x-y)) = e - (e-x-y) = x + y. The identity holds exactly for all real x, y. For complex x, y, it holds as a formal algebraic identity where ln(exp(z)) = z; on the principal branch of log, it holds when |Im(x+y)| < pi. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | Token count K = 19 (9 eml operations + 10 leaves) | -- |
| A2 | Step-by-step symbolic evaluation: E9 = x + y | -- |
| A3 | Full expression minus (x + y) = 0 | -- |
| A4 | Numerical spot-check at 8 real-valued (x, y) pairs | -- |
| A5 | Numerical spot-check at 4 complex-valued (x, y) pairs | -- |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Token count K = 19 | Programmatic parsing of the expression string to count eml operation nodes and leaf nodes (1, x, y) | Confirmed: 9 eml + 10 leaves = K = 19 |
| A2 | Step-by-step symbolic evaluation: E9 = x + y | SymPy symbolic evaluation through 9 layers: build each sub-expression E1..E9, simplify, verify residuals at 5 critical algebraic cancellation points (E1=exp(x), E2=e-x, E4=exp(e)/(e-x), E7=e-x-y, E9=x+y) | Confirmed: all 5 critical residuals = 0, E9 = x + y |
| A3 | Full expression minus (x + y) = 0 | SymPy simplify(E9 - (x + y)) for real symbols x, y; verify residual = 0 | Confirmed: residual = 0 |
| A4 | Numerical spot-check at 8 real-valued (x, y) pairs | Numerical evaluation of the full 9-layer chain at 8 real-valued (x, y) pairs spanning extremes: x,y in [-100, 100]; verify |result - (x+y)| < 1e-10 | Confirmed: max |diff| = 1.26e-14 |
| A5 | Numerical spot-check at 4 complex-valued (x, y) pairs | Numerical evaluation of the full 9-layer chain at 4 complex-valued (x, y) pairs with |Im(x+y)| < pi; verify |result - (x+y)| < 1e-10 | Confirmed: max |diff| = 1.34e-15 |

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
  x =       2.0, y =       3.0  result=    5.00000000000000  expected=    5.00000000000000  |diff|=0.00e+00
  x =      -5.0, y =       8.0  result=    3.00000000000000  expected=    3.00000000000000  |diff|=4.44e-16
  x =     100.0, y =     -99.0  result=    1.00000000000000  expected=    1.00000000000000  |diff|=1.26e-14
  x =     0.001, y =     0.002  result=    0.00300000000000  expected=    0.00300000000000  |diff|=5.58e-16
  x =       2.5, y = 3.14159..  result=    5.64159265358979  expected=    5.64159265358979  |diff|=0.00e+00
  x =    -100.0, y =     100.5  result=    0.50000000000000  expected=    0.50000000000000  |diff|=4.00e-15
  x =       0.0, y =       0.0  result=    0.00000000000000  expected=    0.00000000000000  |diff|=0.00e+00
  x = 2.7172818, y =       0.0  result=    2.71728182845905  expected=    2.71728182845905  |diff|=0.00e+00
  A4: all real spot-checks agree within 1e-10: True == True = True
  x =    (1+0.5j), y =    (2-0.3j)  |diff|=1.67e-16
  x =    (0.5+1j), y =   (-1.5+2j)  |diff|=0.00e+00
  x =   (-3+0.7j), y =    (4-0.7j)  |diff|=1.34e-15
  x =          1j, y =     (-0-1j)   |diff|=4.58e-16
  A5: all complex spot-checks agree within 1e-10: True == True = True
  All facts verified (symbolic + numerical): True == True = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

### Check 1: Does the identity hold for real x > e?

- **Question:** Does the identity hold for real x > e, where the intermediate value e - x is negative?
- **Verification performed:** For x > e (e.g., x = 100), the intermediate E2 = e - x < 0. This means E3 = e - log(e-x) involves log of a negative number, giving a complex intermediate with imaginary part +/-pi*i. Tracing through: E3 = e - (ln|e-x| + pi*i), E4 = exp(E3) = -exp(e)/|e-x| (negative real), E5 = e - log(E4) = e - (ln|E4| + pi*i) = ln|e-x| - pi*i. Then exp(E5) = |e-x| * exp(-pi*i) = -(e-x), and E7 = -(e-x) - log(exp(y)) = -(e-x) - y = e - x - y (real). The +/-pi*i terms cancel exactly across the chain. Numerical test at x = 100, y = -99 confirms: |diff| < 2e-14.
- **Finding:** The identity holds for all real x (including x > e). Intermediate complex values with +/-pi*i cancel perfectly.
- **Breaks proof:** No

### Check 2: Complex branch cut analysis

- **Question:** Does the identity hold for arbitrary complex x, y on the principal branch of log?
- **Verification performed:** The final step is E9 = e - log(exp(e - x - y)). On the principal branch, log(exp(z)) = z only when |Im(z)| <= pi. Since Im(e - x - y) = -Im(x + y), the identity holds when |Im(x + y)| < pi. Numerical tests confirm: x = 0.5+i, y = -1.5+2i gives Im(x+y) = 3 < pi and |diff| = 0; x = 1+2i, y = 1+2i gives Im(x+y) = 4 > pi and |diff| = 2*pi (branch-cut error). In the paper's formal algebraic framework, ln(exp(z)) = z is an axiom (equivalently, working on the Riemann surface of log), and the identity holds for all complex x, y. The principal-branch limitation is a property of numerical evaluation, not of the algebraic identity.
- **Finding:** On the principal branch, the identity holds when |Im(x+y)| < pi. As a formal algebraic identity (the paper's framework), it holds for all complex x, y.
- **Breaks proof:** No

### Check 3: Minimality of K = 19

- **Question:** Is K = 19 the minimum code length for addition?
- **Verification performed:** An exhaustive bottom-up search of all eml binary trees with leaves {1, x, y} was performed up to K = 17. At each odd K from 1 to 17, all distinct eml-tree values were enumerated using numerical fingerprinting at a generic complex test point. Results: K=15 had 1,980,501 distinct values (closest to x+y: |diff|=8.1e-3); K=17 had 18,470,098 distinct values (closest: |diff|=2.0e-3). No expression at K <= 17 evaluates to x + y. This is consistent with the published result (arXiv:2603.21852) that K = 19 is the minimal code length for addition using eml.
- **Finding:** Exhaustive search through K=17 found no eml tree computing x+y, consistent with K=19 being minimal.
- **Breaks proof:** No

### Check 4: Numerical overflow risk

- **Question:** Could numerical overflow cause false agreement?
- **Verification performed:** The largest intermediate value occurs at E8 = exp(e - x - y). For the real test with x = -100, y = 100.5, E8 = exp(e + 100 - 100.5) = exp(e - 0.5) ~ exp(2.218) ~ 9.19 -- well within float64 range. The intermediate chain keeps values bounded because the log-exp cancellation in E5 = ln(e-x) undoes the exp in E4. The symbolic proof does not depend on floating-point at all.
- **Finding:** No overflow risk for representable floats. The proof rests on exact symbolic algebra.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A -- pure computation, no empirical facts
- **Rule 2:** N/A -- pure computation, no empirical facts
- **Rule 3:** N/A -- proof is not time-sensitive; date.today() used only in generator metadata
- **Rule 4:** CLAIM_FORMAL with operator_note present; documents the full 9-layer inside-out derivation, domain restrictions, and the removable singularity at x = e
- **Rule 5:** 4 adversarial checks: large-x behavior with +/-pi*i cancellation, complex branch cut boundary, minimality cross-reference, numerical overflow risk
- **Rule 6:** N/A -- pure computation, no empirical facts. Cross-check uses mathematically independent method (numerical evaluation via cmath vs. symbolic algebra via SymPy)
- **Rule 7:** All computations via SymPy (symbolic) and cmath (numerical); no hard-coded constants
- **validate_proof.py result:** PASS -- 16/16 checks passed, 0 issues, 0 warnings

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-16.
