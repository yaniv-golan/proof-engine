# Proof: A K=19 binary tree of eml operations evaluates to x + y

- **Generated:** 2026-04-16
- **Verdict:** PROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| A1 | Token count K = 19 (9 eml operations + 10 leaves) | Computed: 9 eml + 10 leaves = 19 |
| A2 | Step-by-step symbolic evaluation: E9 = x + y | Computed: all 5 critical residuals = 0 |
| A3 | Full expression minus (x + y) = 0 | Computed: residual = 0 |
| A4 | Removable singularity at x = e: limit equals e + y | Computed: limit from both sides = e + y |
| A5 | Numerical spot-check at 10 real-valued (x, y) pairs | Computed: max |diff| = 1.26e-14 |
| A6 | Numerical spot-check at 5 complex-valued (x, y) pairs | Computed: max |diff| = 1.34e-15 |
| A7 | Exhaustive search: no K <= 15 eml tree computes x + y | Computed: 1,980,526 distinct values at K=15, x+y not found |

## Proof Logic

The binary operator eml(a, b) = exp(a) - ln(b) is a single operation that, through nesting, can express all elementary functions. The claim is that the specific 19-token expression

```
eml(1, eml(eml(eml(1, eml(eml(1, eml(1, eml(x, 1))), 1)), eml(y, 1)), 1))
```

evaluates to x + y for all real x and y.

The proof first verifies this expression contains exactly 9 eml operations and 10 leaves (from {1, x, y}), confirming K = 19 (A1).

The expression is unwound layer by layer through 9 intermediate sub-expressions. At each layer, SymPy's symbolic algebra engine evaluates the eml operation and simplifies. Five critical algebraic cancellation points are verified with exact zero residuals (A2):

1. **E1 = exp(x):** The innermost eml(x, 1) evaluates to exp(x) - ln(1) = exp(x).
2. **E2 = e - x:** Wrapping gives eml(1, exp(x)) = e - ln(exp(x)) = e - x.
3. **E4 = exp(e)/(e-x):** The triple-nesting pattern (steps 3-5) produces exp(e)/(e-x), which is then unwrapped to yield E5 = ln(e-x). This is the triple-nesting identity applied to the sub-expression (e - x).
4. **E7 = e - x - y:** The subtraction identity eml(ln(a), exp(b)) = a - b gives (e-x) - y.
5. **E9 = x + y:** The final two steps reverse the chain: E8 = exp(e - x - y) and E9 = e - ln(exp(e - x - y)) = x + y.

SymPy confirms that simplify(E9 - (x + y)) = 0 exactly (A3).

The expression has a removable singularity at x = e, where the intermediate E2 = e - x = 0 causes a division by zero through log(0) in the next step. SymPy's limit function confirms that the limit from both sides equals e + y = x + y (A4), so the identity holds in the limit sense at this isolated point.

As an independent cross-check, the full 9-layer chain was evaluated numerically at 15 test points. Ten real-valued (x, y) pairs spanning the range [-100, 100] — including three points near the singularity at x = e (within 1e-12) — all agreed with x + y within machine epsilon, with the largest discrepancy being 1.26e-14 (A5). Five complex-valued pairs (within the principal-branch domain |Im(x+y)| < pi) likewise agreed, with maximum discrepancy 1.34e-15 (A6).

As a second independent method, an exhaustive bottom-up search enumerated all distinct eml binary trees with leaves {1, x, y} through K = 15, totaling 1,980,526 distinct values. No expression at any K <= 15 evaluates to x + y (A7). A separate external search extended this through K = 17 (18,470,098 distinct values) with the same result, confirming K = 19 is the minimum code length for addition.

## What Could Challenge This Verdict?

**Large real x (x > e):** When x exceeds e, the intermediate value E2 = e - x is negative, causing subsequent logarithms to produce complex intermediate values with imaginary parts of +/-pi*i. These imaginary components cancel exactly across the chain, as confirmed by the numerical test at x = 100, y = -99 (|diff| < 2e-14) and at x = e + 1e-6 (|diff| < 1e-22).

**Singularity at x = e:** The expression is undefined at exactly x = e, where E2 = 0 and the subsequent log(0) diverges. SymPy confirms this is a removable singularity: the limit from both sides equals e + y. Numerical tests at x = e - 1e-12 confirm the expression approaches the correct value. The identity holds for all real x except this isolated point, where it holds in the limit sense.

**Complex branch cuts:** On the principal branch of the complex logarithm, log(exp(z)) = z holds only when |Im(z)| <= pi. The identity holds numerically for all complex x, y satisfying |Im(x + y)| < pi. For larger imaginary parts, the error is always an exact multiple of 2*pi*i. In the paper's formal algebraic framework (where ln and exp are true inverses), the identity holds without restriction.

**Minimality of K = 19:** An embedded exhaustive search through K = 15 (1.98M distinct values, ~3 seconds) and a separate external search through K = 17 (18.5M distinct values) found no expression evaluating to x + y. This is consistent with the published result (arXiv:2603.21852) that K = 19 is the minimum code length for addition.

**Numerical overflow:** The largest intermediate values occur at E4 (near the singularity) and E8. The log-exp cancellation at E5 bounds intermediate growth. The symbolic proof is independent of floating-point arithmetic.

## Conclusion

**Verdict: PROVED.** The 19-token expression eml(1, eml(eml(eml(1, eml(eml(1, eml(1, eml(x, 1))), 1)), eml(y, 1)), 1)) evaluates to x + y. This was verified symbolically by SymPy (exact zero residual for real x, y) and numerically at 15 test points (10 real including near-singularity, 5 complex; maximum discrepancy 1.26e-14). The limit at the removable singularity x = e was verified to equal e + y from both sides. The expression uses exactly 9 eml operations and 10 leaves, confirming K = 19. An exhaustive search through K = 15 (embedded, reproducible in ~3 seconds) and K = 17 (external) found no shorter expression for addition.

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-16.
