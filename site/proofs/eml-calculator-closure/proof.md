# Proof: Every calculator-level elementary function is an eml-tree over {1, x, y}

- **Generated:** 2026-04-17
- **Verdict:** PROVED
- **Original result:** R. Cheng, [arXiv:2603.21852](https://arxiv.org/abs/2603.21852) (2026). This proof provides independent computational verification.
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| A1 | eml-trees exist for every listed primitive | Computed: 16 primitive trees constructed (13 functions + pi, e, i) |
| A2 | Every primitive matches its analytic value numerically | Computed: 50 checks across primitives + constants, max \|diff\| = 1.23e-14 |
| A3 | Composition witness: sin(sqrt(x) + cos(x)) matches math.sin(sqrt(x)+cos(x)) | Computed: K = 1367; max \|diff\| at 3 test points = 1.49e-15 |
| A4 | Inverse-trio witness: sin(arcsin(a)) = cos(arccos(a)) = tan(arctan(a)) = a | Computed: all three round-trips at a = 0.5; max \|diff\| = 1.96e-15 |
| A5 | Every constructed tree has leaves in {1, x, y} only | Computed: recursive leaf-set check on all 16 trees |
| A6 | Building-block integrity: ADD(1,1) = 2, MULT(1,1) = 1 at K = 19, K = 17 | Computed: matches published K=19 and K=17 proofs byte-for-byte |

## Proof Logic

The claim is a universal-closure statement: every elementary function that appears on a standard scientific calculator — the four arithmetic operations, exponentiation, square root, log base 10, the trig trio sin/cos/tan and their inverses, plus the constants \(\pi\), \(e\), \(i\) — can be realised as a finite binary tree of the operator \(\mathrm{eml}(a, b) = e^a - \ln b\) whose leaves are the constant \(1\) and the input variables \(x, y\).

The proof is by explicit construction. It reuses five previously verified eml identities (each the subject of a separate site proof):

1. **EXP(x) = eml(x, 1)** [K=3 per variable]. Trivial: \(e^x - \ln 1 = e^x\).
2. **LN(p) = eml(1, eml(eml(1, p), 1))** [K=7 per variable]. The triple-nesting log identity.
3. **SUB(p, q) = eml(LN(p), EXP(q)) = p − q** [K=11].
4. **ADD tree** [K=19] — gives \(x + y\) for all complex \(x, y\) in the principal-branch safe zone.
5. **MULT tree** [K=17] — gives \(x \cdot y\); has a documented removable singularity at \(xy = 0\).

The constants \(\pi\) (K=137), \(e\) (K=3) and \(i\) (K=91) are imported verbatim from the published eml-pi-and-i-from-1 proof.

The derived calculator functions are then built by standard elementary-function identities applied to the five building blocks:

- **DIV**(x, y) = MULT(x, EXP(−LN(y)))
- **POW**(x, y) = EXP(MULT(y, LN(x)))
- **SQRT**(x) = EXP(MULT(1/2, LN(x)))
- **LOG10**(x) = DIV(LN(x), LN(10)), where 10 is built via five additions of the tree for 2
- **SIN**(x) = DIV(SUB(EXP(i·x), EXP(−i·x)), MULT(2, i))
- **COS**(x) = DIV(ADD(EXP(i·x), EXP(−i·x)), 2)
- **TAN**(x) = DIV(SIN(x), COS(x))
- **ARCTAN**(x) = MULT(i/2, LN(DIV(ADD(i, x), SUB(i, x))))
- **ARCSIN**(x) = MULT(−i, LN(ADD(i·x, SQRT(SUB(1, x²)))))
- **ARCCOS**(x) = SUB(\(\pi\)/2, ARCSIN(x))

Negation \(-t\) is expressed as MULT(−1, t) rather than SUB(0, t) because SUB(0, t) would require \(\ln(0)\), which is undefined.

The script constructs all sixteen trees, verifies their leaf sets lie in \(\{1, x, y\}\), evaluates them numerically at multiple interior test points of each natural domain, and reports the maximum \(|\text{diff}|\) versus the standard `math.*` reference values. Across 50 numerical checks the worst disagreement is 1.23 × 10⁻¹⁴ (A2). The composition witness \(\sin(\sqrt{x} + \cos x)\) (K = 1367, built by leaf substitution into the sin tree) and the inverse-trio witnesses \(\sin(\arcsin a)\), \(\cos(\arccos a)\), \(\tan(\arctan a)\) at \(a = 0.5\) all match to better than 2 × 10⁻¹⁵ (A3, A4). Every tree has leaves in \(\{1, x, y\}\) (A5).

## What Could Challenge This Verdict?

**Composition vs direct verification.** Composition closure is a structural property: leaf substitution of an eml-tree into another eml-tree produces an eml-tree. No new correctness obligation is incurred. The single composition witness \(\sin(\sqrt{x} + \cos x)\) is corroborative, not constitutive; its role is to guard against an implementation bug in the substitution code.

**Removable singularities at 0.** Many derived trees inherit the K=17 MULT tree's removable singularity at \(xy = 0\). For example, \(\sqrt{1}\), \(\sin(0)\), \(\log_{10}(1)\) all evaluate to trees that contain \(\ln(0)\). The true function values at those points (1, 0, 0) are finite — matching what a scientific calculator displays — so the construction agrees with the standard function on the natural domain by continuous extension. All numerical verification uses interior test points that avoid these removable zeros.

**Branch-cut traversal in inverse trig.** The arctan and arcsin constructions use complex logarithms. On the principal branch (which is what `cmath.log` implements and what every standard library uses), these formulas produce the real-valued inverse-trig branch on the relevant domain. Verified at multiple points: \(\arctan(1) = \pi/4\), \(\arcsin(0.5) = \pi/6\), etc., all to < 3 × 10⁻¹⁵.

**Completeness of the primitive list.** A standard scientific calculator exposes arithmetic, exp/ln/log10/log2, trig and inverse trig, sqrt and powers, hyperbolic functions, and the constants \(\pi\), \(e\). Every one of these is a finite composition of \(\{\text{EXP}, \text{LN}, \text{ARITHMETIC}, i, \pi\}\) — all of which are realised here. Non-elementary keys (factorial, modular arithmetic, statistical aggregates, random-number generation) are outside the elementary-function scope of the claim.

**Minimality.** No minimality is claimed. Reported K values (17 for MULT up to 2683 for the \(\tan(\arctan x)\) closure witness) are finite upper bounds. Shorter trees may exist for any of the derived functions; exhaustive search was performed only for MULT (in its own site proof).

## Conclusion

**Verdict: PROVED.** Sixteen explicit eml-trees — one for each listed calculator primitive and constant — were constructed from five previously verified building blocks and matched their analytic values at 50 interior test points with maximum disagreement 1.23 × 10⁻¹⁴. Composition closure was confirmed by an explicit compound witness (\(\sin(\sqrt{x} + \cos x)\), K = 1367, max |diff| = 1.49 × 10⁻¹⁵) and inverse closure by the three round-trip identities \(\sin(\arcsin(0.5)) = \cos(\arccos(0.5)) = \tan(\arctan(0.5)) = 0.5\) (max |diff| = 1.96 × 10⁻¹⁵). The listed primitives plus composition exhaust the elementary-function content of a standard scientific calculator.

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.18.0 on 2026-04-17.
