# Proof Narrative: Every calculator-level elementary function is an eml-tree

## Verdict

**Verdict: PROVED**

Pick any key on your scientific calculator. Plus, minus, times, divide. Square root. Log. Sin, cos, tan, and their inverses. The constant π. The constant e. The imaginary i. Every one of them is secretly a finite tree of a single alien operator, eml(a, b) = exp(a) − ln(b), applied only to the constant 1 and the variables you type in.

## What Was Claimed?

The claim is that every elementary function on a standard scientific calculator — arithmetic, exponentiation, roots, log base 10, the trig trio sin/cos/tan and their inverses, plus the constants π, e, i — can be realised as a finite eml-tree whose leaves are drawn from {1, x, y}. Compositions and inverses are included. The construction must agree with the standard mathematical definition at every interior point of the function's natural domain.

This is a universal-closure statement. Each individual calculator key must be an explicit eml-tree, and the class must be closed under composition (substituting one function into another) and inversion (for each sin there is an arcsin, etc.). If even one key resists the construction, the claim fails.

## What Did We Find?

The proof exhibits sixteen explicit eml-trees — one for each listed function plus the three constants — built from five previously verified building blocks. Token counts range from K = 3 (for e) to K = 2683 (for the tan-of-arctan round-trip). Every leaf of every tree is either 1, x, or y. Every tree agrees numerically with its standard-library counterpart to better than 1.23 × 10⁻¹⁴ across 50 interior test points.

The building blocks are EXP(x) = eml(x, 1), LN via a K=7 triple nesting, SUB via K=11, and the K=19 ADD and K=17 MULT trees. The constants π, e and i are imported from the site's π-and-i-from-1 proof. Everything else is built by standard identities: division is x × exp(−ln y); the square root is x raised to the one-half power; log10 is ln(x) divided by ln(10); sin and cos use the complex exponential identities; tan is sin over cos; arctan, arcsin and arccos use the classical logarithmic formulas.

Composition closure is structural. Substituting a subtree into a leaf produces another eml-tree. As a witness the proof builds sin(sqrt(x) + cos(x)) — K = 1367 — and matches math.sin(math.sqrt(x) + math.cos(x)) at three interior points to within 1.49 × 10⁻¹⁵. Inverse closure is witnessed by three forward-inverse round-trips: sin(arcsin(0.5)), cos(arccos(0.5)), tan(arctan(0.5)) — all evaluate to 0.5 within 2 × 10⁻¹⁵. A subtle formula error in either direction would make this cross-check fail; it did not.

## What Should You Keep In Mind?

The reported K values are upper bounds from specific constructions. Whether a shorter tree exists for any given derived function is an open question. Only MULT (K = 17) was proved minimal in its own site proof.

The K=17 multiplication tree has a documented removable singularity at xy = 0. Every derived function that composes MULT inherits this: sqrt(1), sin(0), log10(1), and similar boundary zeros evaluate to trees with a ln(0) inside. The function's true value at those points (1, 0, 0) is finite — exactly what a scientific calculator displays — so closure to the boundary follows by continuity. Numerical verification uses interior test points that avoid these removable zeros. The inverse trig constructions traverse branch cuts of the complex logarithm; on the principal branch they produce the real-valued inverse branches on the natural domain.

Negation is implemented as MULT(−1, t) rather than SUB(0, t) because SUB(0, t) would require ln(0). This inherits the same t = 0 exclusion as MULT itself. Non-elementary keys — factorial, modular arithmetic, random-number generation, statistical aggregates — are outside the elementary-function scope of the claim.

## How Was This Verified?

This claim was verified using the proof-engine framework, which requires every step to be executed by code rather than asserted. The script constructs all sixteen primitive trees and two closure witnesses programmatically, parsing the K=19 ADD and K=17 MULT tree strings verbatim from their published site proofs, then recursively evaluates each tree with cmath.exp and cmath.log (principal branch) at multiple interior test points of the function's natural domain. Results are compared against Python's math module. Every leaf in every tree is confirmed to lie in {1, x, y} by a recursive walk. The result being verified was originally established in A. Odrzywołek, "All elementary functions from a single binary operator" (arXiv:2603.21852, 2026); this proof was developed independently by composing previously verified eml identities. For the full formal breakdown, see [the structured proof report](proof.md). For verification details, see [the audit](proof_audit.md). To reproduce, [re-run the proof script](proof.py).
