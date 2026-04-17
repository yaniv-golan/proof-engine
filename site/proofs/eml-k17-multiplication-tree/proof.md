# Proof: A K=17 binary tree of eml operations evaluates to x * y

- **Generated:** 2026-04-16
- **Verdict:** PROVED
- **Original result:** A. Odrzywołek, "All elementary functions from a single binary operator," [arXiv:2603.21852](https://arxiv.org/abs/2603.21852) (2026). This proof provides independent computational verification.
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| A1 | Token count K = 17 (8 eml operations + 9 leaves) | Computed: 8 eml + 9 leaves = 17 |
| A2 | Step-by-step symbolic evaluation: M8 = x * y | Computed: all 5 critical residuals = 0 |
| A3 | Full expression minus x * y = 0 | Computed: residual = 0 |
| A4 | Removable singularity at x = e^e: limit equals e^e * y | Computed: limit from both sides = e^e * y |
| A5 | Numerical spot-check at 12 real-valued (x, y) pairs | Computed: max |diff| = 9.38e-15 |
| A6 | Numerical spot-check at 6 complex-valued (x, y) pairs | Computed: max |diff| = 6.47e-15 |
| A7 | Exhaustive search: no K <= 15 eml tree computes x * y | Computed: 1,980,526 distinct values at K=15, x*y not found |

## Proof Logic

The binary operator eml(a, b) = exp(a) - ln(b) is a single operation that, through nesting, can express all elementary functions. The claim is that the specific 17-token expression

```
eml(eml(1, eml(eml(eml(1, eml(eml(1, eml(1, x)), 1)), y), 1)), 1)
```

evaluates to x * y for all nonzero complex x and y.

The proof first verifies this expression contains exactly 8 eml operations and 9 leaves (from {1, x, y}), confirming K = 17 (A1).

The expression is unwound layer by layer through 8 intermediate sub-expressions. The algebraic strategy exploits a key insight: multiplication can be expressed as x * y = exp(ln(x) + ln(y)), and the eml operator provides a shortcut to the "e minus logarithm" form through eml(1, x) = e - ln(x). This saves steps compared to the K=19 addition tree, which needed two operations to reach e - x.

At each layer, SymPy's symbolic algebra engine evaluates the eml operation and simplifies. Five critical algebraic cancellation points are verified with exact zero residuals (A2):

1. **M1 = e - ln(x):** The innermost eml(1, x) directly produces e - ln(x), the starting point for the chain.
2. **M3 = exp(e)/(e - ln(x)):** The triple-nesting pattern (steps 1-4) produces exp(e)/(e - ln(x)), leading to M4 = ln(e - ln(x)).
3. **M5 = e - ln(xy):** Using eml(M4, y) = exp(ln(e - ln(x))) - ln(y) = (e - ln(x)) - ln(y) = e - ln(xy). Here y serves as a bare leaf, contributing -ln(y) directly — a variant of the subtraction identity that saves a step.
4. **M7 = ln(xy):** The unwrap pattern (steps 6-7) converts e - ln(xy) into ln(xy).
5. **M8 = x * y:** The final step exp(ln(xy)) = xy completes the multiplication.

SymPy confirms that simplify(M8 - x*y) = 0 exactly (A3).

The expression has a removable singularity at x = e^e (approximately 15.154), where M1 = e - ln(e^e) = 0 causes a division by zero in the next step. SymPy confirms that the limit from both sides equals e^e * y (A4). The expression is genuinely undefined at x = 0 and y = 0, where ln(0) diverges; these are not removable singularities.

As an independent cross-check, the full 8-layer chain was evaluated numerically at 18 test points. Twelve real-valued (x, y) pairs — including negative inputs, near-singularity values (x within 1e-12 of e^e), and extreme ratios — all agreed with x * y within machine epsilon, with the largest discrepancy being 9.38e-15 (A5). Six complex-valued pairs (including purely imaginary and both-negative inputs) likewise agreed, with maximum discrepancy 6.47e-15 (A6).

An exhaustive bottom-up search enumerated all distinct eml binary trees with leaves {1, x, y} through K = 15, totaling 1,980,526 distinct values. No expression at any K <= 15 evaluates to x * y (A7), confirming no shorter tree exists.

## What Could Challenge This Verdict?

**Negative real inputs:** When x or y is negative, the intermediate logarithms produce complex values with imaginary parts of +/-pi*i. These imaginary components cancel exactly across the chain, always returning a real result equal to x * y. Numerical tests at (-2, 3) and (-3, -5) confirm |diff| < 8e-15.

**Singularities:** The expression is undefined at x = 0, y = 0 (where ln diverges), and at x = e^e (where an intermediate hits zero). The singularity at x = e^e is removable — SymPy confirms the limit equals e^e * y from both sides. The singularities at x = 0 and y = 0 are not removable; these are genuine limitations where the eml tree cannot represent the value x * y = 0.

**Complex branch cuts:** On the principal branch, the critical cancellation ln(exp(z)) = z requires |Im(z)| < pi. For the expression's final cancellation, z = e - ln(xy), and Im(z) = -arg(xy) which is always in [-pi, pi). The identity therefore holds on the principal branch for all nonzero x, y (except x = e^e). In the formal algebraic framework, it holds without restriction.

**Minimality of K = 17:** An exhaustive search through K = 15 (1.98M distinct values, ~2.5 seconds) found no expression evaluating to x * y. K = 17 is the shortest known code length for multiplication.

**Numerical overflow:** The largest intermediate values occur at M3 and M6, bounded by the log-exp cancellation at M4 and M7. The symbolic proof is independent of floating-point arithmetic.

## Conclusion

**Verdict: PROVED.** The 17-token expression eml(eml(1, eml(eml(eml(1, eml(eml(1, eml(1, x)), 1)), y), 1)), 1) evaluates to x * y. This was verified symbolically by SymPy (exact zero residual) and numerically at 18 test points (12 real including negatives, 6 complex; maximum discrepancy 9.38e-15). The limit at the removable singularity x = e^e was verified to equal e^e * y from both sides. The expression uses exactly 8 eml operations and 9 leaves, confirming K = 17. An exhaustive search through K = 15 found no shorter expression for multiplication.

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-16.
