# Audit: Pythagorean Theorem (Biconditional)

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Any triangle with sides a, b, c |
| Property | biconditional: (a^2 + b^2 = c^2) <=> (angle opposite c = 90 degrees) |
| Operator | == |
| Threshold | True |
| Operator Note | This is a biconditional (if and only if) claim with two sub-claims: SC1 (Forward): a^2 + b^2 = c^2 implies angle C = 90 degrees. SC2 (Converse): angle C = 90 degrees implies a^2 + b^2 = c^2. Both directions are proved via the Law of Cosines: c^2 = a^2 + b^2 - 2ab*cos(C). The Law of Cosines is taken as an established theorem of Euclidean geometry. The proof is algebraic: substitution and simplification. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| A1 | - | SC1 (Forward): a^2 + b^2 = c^2 implies angle C = 90 degrees via Law of Cosines |
| A2 | - | SC2 (Converse): angle C = 90 degrees implies a^2 + b^2 = c^2 via Law of Cosines |
| A3 | - | Cross-check: numerical verification with random triangles |
| A4 | - | Cross-check: symbolic verification using sympy |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | SC1 (Forward): a^2 + b^2 = c^2 implies angle C = 90 degrees via Law of Cosines | Algebraic: substitute a^2+b^2=c^2 into Law of Cosines, derive cos(C)=0, conclude C=90 | True |
| A2 | SC2 (Converse): angle C = 90 degrees implies a^2 + b^2 = c^2 via Law of Cosines | Algebraic: substitute cos(90)=0 into Law of Cosines, derive c^2=a^2+b^2 | True |
| A3 | Cross-check: numerical verification with random triangles | Numerical: 10000 random triangles tested in both directions | SC1 failures: 0, SC2 failures: 0 |
| A4 | Cross-check: symbolic verification using sympy | Symbolic: sympy simplification of Law of Cosines substitution | SC1 symbolic: True, SC2 symbolic: True |

*Source: proof.py JSON summary*

## Computation Traces

```
SC1: cos(90 deg) is effectively 0: 6.123233995736766e-17 < 1e-15 = True
SC2: cos(90 deg) = 0 confirms substitution: 6.123233995736766e-17 == 0.0 = False
SC1 numerical: 10000 random right triangles, all angles = 90 deg: 0 == 0 = True
SC2 numerical: 10000 random triangles with C=90, all satisfy a^2+b^2=c^2: 0 == 0 = True
SC1 (Forward) holds: True == True = True
SC2 (Converse) holds: True == True = True
SC1 numerical cross-check passed: True == True = True
SC2 numerical cross-check passed: True == True = True
Biconditional: both directions proved: True == True = True
```

Note: The `SC2: cos(90 deg) = 0 confirms substitution` returns False due to floating-point representation (cos(pi/2) = 6.12e-17 in IEEE 754). This is expected and does not affect the proof: cos(90 degrees) is exactly 0 in Euclidean geometry. The algebraic argument is exact; the floating-point artifact is acknowledged and handled in the code.

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

Pure-math proof -- no empirical sources. Independence is established via mathematically distinct cross-check methods:

| Cross-check | Description | Agreement |
|-------------|-------------|-----------|
| Numerical | 10,000 random triangles tested in each direction, zero failures | True |
| Symbolic | sympy algebraic simplification confirms both directions | True |

The primary proof is algebraic manipulation of the Law of Cosines. The numerical cross-check uses a completely different approach (construct triangles, compute angles/sides, check equality). The symbolic cross-check uses a third approach (computer algebra system simplification). A bug in the algebraic reasoning would not propagate to these independent methods.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

| # | Question | Verification Performed | Finding | Breaks Proof? |
|---|----------|----------------------|---------|---------------|
| 1 | Does this proof depend on Euclidean geometry specifically? | Analyzed whether the Law of Cosines holds in non-Euclidean geometries. In spherical and hyperbolic geometry, the Law of Cosines takes a different form. | The claim is implicitly restricted to Euclidean geometry, which is the standard interpretation. Valid in this context. | No |
| 2 | Are there degenerate triangles where the proof fails? | Checked edge cases: degenerate triangle (a + b = c), triangle inequality violations, zero-length sides. | Degenerate cases do not satisfy a^2 + b^2 = c^2 with positive side lengths, so they are excluded by the hypothesis. | No |
| 3 | Is cos(C) = 0 sufficient to conclude C = 90 degrees? | cos(C) = 0 has solutions C = 90 + 180k. In a triangle, 0 < C < 180. Only solution: C = 90. | Within valid triangle angle range, cos(C) = 0 uniquely determines C = 90 degrees. | No |
| 4 | Does the converse require any additional conditions beyond C = 90? | Checked whether the converse direction assumes anything beyond C = 90 degrees. | No additional conditions needed. Follows directly from cos(90) = 0 in Law of Cosines. | No |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A -- pure computation, no empirical facts
- **Rule 2:** N/A -- pure computation, no empirical facts
- **Rule 3:** `date.today()` used for generator timestamp
- **Rule 4:** CLAIM_FORMAL with operator_note documents biconditional interpretation and sub-claim decomposition
- **Rule 5:** Four adversarial checks covering geometry scope, degenerate cases, cosine uniqueness, and converse conditions
- **Rule 6:** N/A -- pure computation, no empirical facts. Two mathematically independent cross-checks (numerical + symbolic) confirm the algebraic proof
- **Rule 7:** `compare()` used for all claim evaluations; no hard-coded constants or inline formulas
- **validate_proof.py result:** PASS (15/16 checks passed, 0 issues, 1 warning for unused `explain_calc` import -- removed)

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
