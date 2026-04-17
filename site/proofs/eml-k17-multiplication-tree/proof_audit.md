# Audit: A K=17 binary tree of eml operations evaluates to x * y

- **Generated:** 2026-04-16
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The claim defines eml(a, b) = exp(a) - ln(b) and asserts that a specific binary tree of 8 eml operations and 9 leaves (drawn from {1, x, y}) evaluates to x * y. The total token count K = 8 + 9 = 17. The claim text says "depth 17"; following the convention in arXiv:2603.21852, this denotes the RPN code length (total tree nodes), not the tree height. The actual tree height is 8.

The formal interpretation uses exact equality (==) with threshold True. The operator_note documents the full inside-out derivation through 8 layers, identifying the algebraic strategy: x * y = exp(ln(x) + ln(y)), achieved through the chain eml(1,x) = e - ln(x) → triple-nesting → subtraction of ln(y) → unwrap → final exp.

The key insight is that eml(1, x) = e - ln(x) directly provides the "e minus logarithm" form that the K=19 addition tree needed two steps to reach (eml(x,1) then eml(1,_) to get e - x). This, combined with using y as a bare leaf in the subtraction step (yielding -ln(y) instead of -y), makes the multiplication tree 2 nodes shorter than the addition tree.

The expression is undefined at x = 0 (ln(0) in M1), y = 0 (ln(0) in M5), and x = e^e (where e - ln(x) = 0). The singularity at x = e^e is removable — the limit from both sides equals e^e * y, verified by SymPy. The singularities at x = 0 and y = 0 are not removable (the expression diverges).

For the complex domain, the identity is interpreted as a formal algebraic identity where ln(exp(z)) = z. On the principal branch of the complex logarithm, the identity holds for all nonzero x, y (except x = e^e). The branch-cut analysis is more favorable than for K=19 addition: since Im(e - ln(xy)) = -arg(xy) and arg is always in (-pi, pi], the principal-branch condition |Im(z)| < pi is automatically satisfied.

**Formalization scope:** The formal interpretation is a faithful mapping of the natural-language claim. The token count K = 17 is explicitly verified. The "for all complex x and y" clause is interpreted in the formal algebraic setting, with the domain restrictions (x != 0, y != 0, x != e^e) documented. The expression was constructed analytically using algebraic identities from the previously verified eml proofs (triple-nesting, subtraction) and verified independently. The construction was performed without reference to the original paper's proof.

**Attribution:** This result was originally established in A. Odrzywołek, "All elementary functions from a single binary operator," arXiv:2603.21852 (2026). The proof presented here provides independent computational verification using symbolic algebra (SymPy), numerical methods, and exhaustive search, and was developed without reference to the original proof.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Binary operator eml(a, b) = exp(a) - ln(b) |
| Property | eml(eml(1, eml(eml(eml(1, eml(eml(1, eml(1, x)), 1)), y), 1)), 1) = x * y for all complex x, y (x != 0, y != 0, x != e^e) |
| Operator | == |
| Threshold | True |
| Operator Note | The claim asserts that a specific K=17 binary tree of eml operations evaluates to x * y. K denotes the total number of tree nodes (8 internal eml nodes + 9 leaves = 17). The claim text says 'depth 17'; following the convention in arXiv:2603.21852, this denotes the RPN code length (total tree nodes), not the tree height. The actual tree height is 8. Working inside out through 8 layers: (1) M1 = eml(1, x) = e - ln(x). (2) M2 = eml(1, M1) = e - ln(e - ln(x)). (3) M3 = eml(M2, 1) = exp(e)/(e - ln(x)). (4) M4 = eml(1, M3) = ln(e - ln(x)). Steps 1-4 apply the triple-nesting identity to (e - ln(x)), yielding ln(e - ln(x)). The key observation is that eml(1, x) = e - ln(x) directly provides the 'e minus logarithm' form, saving one step compared to the K=19 addition tree where two steps were needed (eml(x,1) then eml(1,_)) to get e - x. (5) M5 = eml(M4, y) = exp(ln(e - ln(x))) - ln(y) = (e - ln(x)) - ln(y) = e - ln(x) - ln(y) = e - ln(xy). This uses a variant of the subtraction identity: eml(ln(a), y) = a - ln(y) where y is used as a bare leaf, not wrapped in exp(). This saves another step compared to the addition tree. (6) M6 = eml(M5, 1) = exp(e - ln(xy)) = exp(e)/(xy). (7) M7 = eml(1, M6) = e - ln(exp(e)/(xy)) = e - (e - ln(xy)) = ln(xy). (8) M8 = eml(M7, 1) = exp(ln(xy)) = xy. The expression is undefined at x = 0 (ln(0) in M1), y = 0 (ln(0) in M5), and x = e^e (where e - ln(x) = 0 causes ln(0) in M2). The singularity at x = e^e is removable: the limit from both sides equals e^e * y, verified by SymPy. For complex x, y: the identity holds as a formal algebraic identity where ln(exp(z)) = z (i.e., on the Riemann surface of log). On the principal branch, it holds for all x, y with x != 0, y != 0. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | Token count K = 17 (8 eml operations + 9 leaves) | -- |
| A2 | Step-by-step symbolic evaluation: M8 = x * y | -- |
| A3 | Full expression minus x * y = 0 | -- |
| A4 | Removable singularity at x = e^e: limit equals e^e * y | -- |
| A5 | Numerical spot-check at 12 real-valued (x, y) pairs | -- |
| A6 | Numerical spot-check at 6 complex-valued (x, y) pairs | -- |
| A7 | Exhaustive search: no K <= 15 eml tree computes x * y | -- |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Token count K = 17 (8 eml operations + 9 leaves) | Programmatic parsing of the expression string to count eml operation nodes and leaf nodes (1, x, y) | Confirmed: 8 eml + 9 leaves = K = 17 |
| A2 | Step-by-step symbolic evaluation: M8 = x * y | SymPy symbolic evaluation through 8 layers: build each sub-expression M1..M8 with simplification at each step, verify residuals at 5 critical algebraic cancellation points (M1=e-ln(x), M3=exp(e)/(e-ln(x)), M5=e-ln(xy), M7=ln(xy), M8=x*y) all equal zero | Confirmed: all 5 critical residuals = 0, M8 = x * y |
| A3 | Full expression minus x * y = 0 | SymPy simplify(M8 - x*y) for positive real symbols x, y; verify residual equals 0 | Confirmed: residual = 0 |
| A4 | Removable singularity at x = e^e: limit equals e^e * y | SymPy limit(M8, x, exp(e)) from left, right, and both sides; verify all three equal exp(e) * y | Confirmed: limit from left = y*exp(E), from right = y*exp(E), both = e^e * y |
| A5 | Numerical spot-check at 12 real-valued (x, y) pairs | Numerical evaluation of the full 8-layer chain at 12 real-valued (x, y) pairs including positive, negative, near-zero, near-singularity (x near e^e within 1e-12); verify |result - x*y| < 1e-6 | Confirmed: max |diff| = 9.38e-15 |
| A6 | Numerical spot-check at 6 complex-valued (x, y) pairs | Numerical evaluation of the full 8-layer chain at 6 complex-valued (x, y) pairs including purely imaginary and negative real inputs; verify |result - x*y| < 1e-10 | Confirmed: max |diff| = 6.47e-15 |
| A7 | Exhaustive search: no K <= 15 eml tree computes x * y | Embedded exhaustive bottom-up search: enumerate all distinct eml binary trees with leaves {1, x, y} at each odd K from 1 to 15 using numerical fingerprinting at a generic complex test point; check if x*y appears | Confirmed: 1,980,526 distinct values at K=15, x*y not found at any K <= 15 |

*Source: proof.py JSON summary*

## Computation Traces

```
  Token count: 8 eml operations + 9 leaves = K = 17
  A1: K = 17: 17 == 17 = True
  Step-by-step evaluation:
    M1=eml(1,x) = E - log(x)
    M2=eml(1,M1) = E - log(E - log(x))
    M3=eml(M2,1) = exp(E)/(E - log(x))
    M4=eml(1,M3) = -log(-1/(log(x) - E))
    M5=eml(M4,y) = E - log(x*y)
    M6=eml(M5,1) = exp(E)/(x*y)
    M7=eml(1,M6) = log(x*y)
    M8=eml(M7,1) = x*y
  A2a: M1 = e - ln(x): 0 == 0 = True
  A2b: M3 = exp(e)/(e - ln(x)): 0 == 0 = True
  A2c: M5 = e - ln(xy): 0 == 0 = True
  A2d: M7 = ln(xy): 0 == 0 = True
  A2e: M8 = x*y: 0 == 0 = True
  A3: M8 - x*y = 0: 0 == 0 = True
  Limit as x -> e^e-: y*exp(E)
  Limit as x -> e^e+: y*exp(E)
  Limit as x -> e^e:  y*exp(E)
  A4: limit(M8, x->e^e) = e^e * y from both sides: True == True = True
  Numerical (real):
    x=                   2, y=           3  |diff|=8.88e-16
    x=                 0.5, y=           4  |diff|=6.66e-16
    x=                  -2, y=           3  |diff|=4.32e-15
    x=                  -3, y=          -5  |diff|=8.00e-15
    x=                 100, y=        0.01  |diff|=1.35e-15
    x=                -100, y=         0.5  |diff|=9.38e-15
    x=                   1, y=           1  |diff|=0.00e+00
    x=      2.718281828459, y=     3.14159  |diff|=0.00e+00
    x=     15.154261241479, y=           2  |diff|=3.55e-15
    x=     15.154263241479, y=           2  |diff|=3.55e-15
    x=     15.154262241478, y=           1  |diff|=0.00e+00
    x=               0.001, y=        1000  |diff|=4.44e-16
  A5: all real spot-checks agree within 1e-6: True == True = True
  Numerical (complex):
    x=    (1+0.5j), y=    (2-0.3j)  |diff|=8.95e-16
    x=    (0.5+1j), y=   (-1.5+2j)  |diff|=1.79e-15
    x=   (-3+0.7j), y=    (4-0.7j)  |diff|=6.47e-15
    x=          1j, y=     (-0-1j)  |diff|=9.93e-16
    x=      (2+3j), y=   (-1-0.1j)  |diff|=4.44e-16
    x=     (-1+0j), y=     (-1+0j)  |diff|=5.07e-16
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
    Search time: 2.45s
    x*y found at K <= 15: None
  A7: no K <= 15 tree computes x*y: True == True = True
  All facts verified (symbolic + numerical + search): True == True = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

### Check 1: Does the identity hold for negative real x and y?

- **Question:** Does the identity hold for negative real x and y?
- **Verification performed:** For negative real x (e.g., x = -2), ln(x) = ln|x| + pi*i. Then M1 = e - ln|x| - pi*i (complex intermediate). Tracing through the chain: the imaginary components from ln(negative) at steps M1 and M5 interact through exp and log operations. The +-pi*i terms cancel exactly across the chain, returning a real result. Numerical tests confirm: (-2)*3 gives |diff| < 5e-15, (-3)*(-5) gives |diff| < 8e-15.
- **Finding:** The identity holds for all real nonzero x and y, including negatives. Intermediate complex values with +-pi*i cancel exactly.
- **Breaks proof:** No

### Check 2: What singularities does the expression have?

- **Question:** What singularities does the expression have, and are they removable?
- **Verification performed:** Three singularity classes: (1) x = 0: M1 = eml(1, 0) = e - ln(0) is undefined. The limit as x -> 0 diverges (M1 -> +infinity), so this is NOT removable. However, x*y = 0 at x = 0, and multiplication by zero is well-defined, so this is a genuine limitation of the eml expression. (2) y = 0: M5 = eml(M4, 0) = exp(M4) - ln(0) is undefined. Same analysis: not removable. (3) x = e^e (approx 15.154): M1 = e - ln(e^e) = 0, and M2 = eml(1, 0) involves ln(0). SymPy limit confirms: lim_{x->e^e} M8 = e^e * y from both sides. This IS a removable singularity, analogous to x = e in the K=19 addition tree. Numerical tests within 1e-12 of e^e confirm convergence.
- **Finding:** x = 0 and y = 0 are genuine singularities (not removable). x = e^e is a removable singularity. The identity holds for all real x not in {0, e^e} and y != 0.
- **Breaks proof:** No

### Check 3: Complex branch cut analysis

- **Question:** Does the identity hold for arbitrary complex x, y on the principal branch of log?
- **Verification performed:** The critical cancellation is M7 = e - ln(exp(e - ln(xy))). On the principal branch, ln(exp(z)) = z when |Im(z)| < pi. Here z = e - ln(xy) = (e - ln|xy|) - i*arg(xy). Since arg(xy) is in (-pi, pi], we have |Im(z)| <= pi, and the cancellation holds for all nonzero x, y. The earlier cancellation exp(ln(e-ln(x))) at M5 requires e-ln(x) != 0, which fails only at x = e^e. Numerical tests at 6 complex points (including (-1)*(-1)=1, purely imaginary inputs) all agree within 1e-15. In the formal algebraic framework, ln(exp(z)) = z is an axiom and the identity holds for all nonzero complex x, y.
- **Finding:** On the principal branch: holds for all nonzero x, y (except x = e^e). As a formal algebraic identity: holds for all nonzero complex x, y.
- **Breaks proof:** No

### Check 4: Minimality of K = 17

- **Question:** Is K = 17 the minimum code length for multiplication?
- **Verification performed:** An embedded exhaustive search (A7) enumerated all distinct eml trees through K=15 and found no expression evaluating to x*y. The search space at K=15 contains approximately 2 million distinct values. No expression at K <= 15 computes x*y. Note: the search covers K=1 through K=15 (all odd K); K=17 is the next possible level. Whether K=17 is strictly minimal (i.e., no other K=17 tree also computes x*y) is not determined, but the search confirms no shorter tree exists.
- **Finding:** Exhaustive search through K=15 found no eml tree computing x*y. K=17 is the shortest known code length for multiplication.
- **Breaks proof:** No

### Check 5: Numerical overflow risk

- **Question:** Could numerical overflow cause false agreement?
- **Verification performed:** The largest intermediate value is M6 = exp(e - ln(xy)). For |xy| << 1 (e.g., x=0.001, y=0.001), M6 = exp(e+6.9) which is large but finite (~15000). For |xy| >> 1, M6 = exp(e - ln(xy)) becomes small. The symbolic proof does not depend on floating-point. The log-exp cancellation at M7 (= ln(xy)) bounds intermediate values. Numerical tests at extremes (x=100/y=0.01, x=-100/y=0.5) confirm |diff| < 1e-14.
- **Finding:** No overflow risk for representable floats. The proof rests on exact symbolic algebra.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A -- pure computation, no empirical facts
- **Rule 2:** N/A -- pure computation, no empirical facts
- **Rule 3:** N/A -- proof is not time-sensitive; date.today() used only in generator metadata
- **Rule 4:** CLAIM_FORMAL with operator_note present; documents the full 8-layer inside-out derivation, domain restrictions (x != 0, y != 0, x != e^e), removable singularity, and complex branch-cut behavior
- **Rule 5:** 5 adversarial checks: negative-input behavior with +-pi*i cancellation, singularity analysis with removability classification, complex branch cut analysis, minimality cross-reference with embedded search, numerical overflow risk
- **Rule 6:** N/A -- pure computation, no empirical facts. Cross-checks use mathematically independent methods (numerical evaluation via cmath vs. symbolic algebra via SymPy; exhaustive search vs. analytical construction)
- **Rule 7:** All computations via SymPy (symbolic) and cmath (numerical); no hard-coded constants
- **validate_proof.py result:** PASS -- 16/16 checks passed, 0 issues, 0 warnings

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-16.
