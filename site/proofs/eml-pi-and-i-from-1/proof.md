# Proof: Finite eml expressions from the constant 1 evaluate to π and to i

- **Generated:** 2026-04-16
- **Verdict:** PROVED
- **Original result:** A. Odrzywołek, "All elementary functions from a single binary operator," [arXiv:2603.21852](https://arxiv.org/abs/2603.21852) (2026). This proof provides independent computational verification.
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| A1 | Token count of the π-expression: K = 137 | Computed: recursive tree-walk confirms K_pi = 137 |
| A2 | Token count of the i-expression: K = 91 | Computed: recursive tree-walk confirms K_i = 91 |
| A3 | Symbolic: Z = eml(1, eml(1, eml(eml(eml(1,1),1),1))) has Im(Z) = -π | Computed: SymPy simplify(Im(Z) - (-π)) = 0 exactly |
| A4 | Numerical: π-expression matches math.pi | Computed: \|π-expr − π\| = 3.52e-15 |
| A5 | Numerical: i-expression matches 1j | Computed: \|i-expr − i\| = 1.30e-15 |
| A6 | Numerical cross-check: (i-expression)² = -1 | Computed: \|i² + 1\| = 2.59e-15 |
| A7 | Every leaf in both expressions is the constant 1 | Computed: recursive all-leaves-are-1 check = True for both |

## Proof Logic

The binary operator eml(a, b) = exp(a) - ln(b) is a single operation that combines exponentials and logarithms. The claim is that π and i — the two most iconic transcendental constants in mathematics — can each be expressed as a finite eml tree whose leaves are nothing but the constant 1.

The proof exhibits explicit expressions and verifies them in three independent ways: a symbolic proof that the pivot sub-expression has imaginary part exactly −π, numerical evaluation that agrees with math.pi and 1j to machine precision, and a structural check that every leaf is the constant 1 (no variables, no other constants).

The construction proceeds in nine stages, each step grounded in previously verified eml identities (the K=3 exponential tree, K=11 subtraction tree, K=11 triple-nesting log tree, K=19 addition tree, K=17 multiplication tree):

1. **E = eml(1,1) = e** (K=3). The starting block: the eml of two 1s is e.
2. **EXP_E = eml(E, 1) = exp(e)** (K=5). Bare `eml(x,1)` is the exponential tree.
3. **EXP_EXP_E = exp(exp(e))** (K=7). Another exp layer.
4. **NEG = eml(1, EXP_EXP_E) = e − exp(e)** (K=9). The first real-negative value: about −12.44.
5. **Z = eml(1, NEG) = e − ln(e − exp(e))** (K=11). This is the pivot. The argument of the outer logarithm is a negative real, so the principal-branch log emits +iπ as its imaginary part, which the outer subtraction flips to −iπ. SymPy confirms Im(Z) = −π **exactly** (A3).
6. **A = eml(1, eml(E, EXP_E)) = e − ln(exp(e) − e)** (K=11). The real part of Z.
7. **NIPI = SUB(Z, A) = −iπ** (K=31). The K=11 subtraction identity isolates the pure imaginary part by subtracting Re(Z) from Z.
8. **NEG_ONE = exp(NIPI) = −1** (K=33), then **IPI = log_tree(−1) = +iπ** (K=39). The triple-nesting log identity recovers the positive imaginary branch.
9. **TWO = ADD(1,1) = 2** (K=19); **HALF = exp(−ln(2)) = 1/2** (K=35); **IPI_HALF = MULT(IPI, HALF) = iπ/2** (K=89); **I_EXPR = exp(iπ/2) = i** (K=91); **PI_EXPR = MULT(I_EXPR, NIPI) = i · (−iπ) = π** (K=137).

The π-expression has 137 tokens and the i-expression has 91 tokens (A1, A2). Every leaf in both trees is the constant 1 (A7) — no variables, no other constants.

Numerical verification uses `cmath.exp` and `cmath.log` recursively through each tree. The π-expression evaluates to 3.141592653589… matching math.pi to 3.52e-15 (A4). The i-expression evaluates to ≈0 + 1j matching 1j to 1.30e-15 (A5). Squaring the i-expression gives approximately −1, matching with residual 2.59e-15 (A6). Fourteen intermediate stage values were also cross-checked against their analytic counterparts; every one agrees to better than 4e-15.

## What Could Challenge This Verdict?

**Branch-cut conventions:** The construction rests on the principal-branch convention log(−r) = ln(r) + iπ for real r > 0. Both Python `cmath` and SymPy agree with this convention, and it is the standard choice in complex analysis. The assignment of arg = +π (rather than −π) to the negative real axis is canonical and unambiguous on the principal branch.

**Reuse of ADD and MULT trees:** The K=19 addition tree and K=17 multiplication tree were proved separately (see eml-k19-addition-tree and eml-k17-multiplication-tree) to hold for all complex inputs subject to the principal-branch conditions. We invoke ADD only with x = y = 1 (trivially safe) and MULT twice — with inputs (iπ, 1/2) and (i, −iπ). For MULT(IPI, HALF), xy = iπ/2 with |Im(e − ln(xy))| = π/2 < π. For MULT(I_EXPR, NIPI), xy = π (real positive), so Im(e − ln(xy)) = 0. Both are strictly inside the safe zone.

**Subtraction branch consistency:** SUB(Z, A) = exp(ln(Z)) − ln(exp(A)). Here Z has argument in (−π/2, 0) and A is real positive, so both cancellations happen strictly inside |Im| < π/2. The numerical residual |NIPI − (−iπ)| < 1e-15 confirms branch consistency.

**Minimality:** The claim is existence, not minimality. K = 137 for π and K = 91 for i are upper bounds; exhaustive search for shorter trees was not performed here. (The K=17 multiplication proof does perform such a search for x·y; an analogous exhaustive search for π or i would be a separate investigation.)

**Numerical overflow:** The largest intermediate value in the chain is EXP_EXP_E ≈ 3.8 × 10⁶, well inside double-precision range. Smallest non-zero is HALF = 0.5. No overflow risk.

## Conclusion

**Verdict: PROVED.** Explicit finite eml-from-1 expressions for π (K = 137) and for i (K = 91) were constructed in nine stages using previously verified eml identities, and verified by symbolic simplification (the pivot sub-expression Z has Im(Z) = −π exactly), by direct numerical evaluation matching math.pi and 1j to better than 4e-15, and by the independent cross-check that (i-expression)² matches −1 to 2.59e-15. Every leaf in both expressions is the constant 1.

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-16.
