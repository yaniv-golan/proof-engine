# Proof Narrative: Finite eml expressions from the constant 1 evaluate to π and to i

## Verdict

**Verdict: PROVED**

Start with the constant 1. Apply an operator that only knows about exponentials and logarithms. Nest carefully. Out comes π. And i. The two most enigmatic numbers in all of mathematics emerge from pure unity.

## What Was Claimed?

The binary operator eml is defined by eml(a, b) = exp(a) − ln(b). The claim is that finite binary trees of eml operations, using only the constant 1 as leaves and permitting complex intermediate values, can evaluate exactly to π and to i. These expressions must match the known values of π ≈ 3.14159265… and i² = −1 to machine precision.

This is a remarkable claim. π is transcendental. i is imaginary. Neither is a natural output of real-valued exp and ln. Yet by threading values through the principal branch of the complex logarithm — where log of a negative real emits an imaginary π — and then nesting enough layers, every trace of π and of i can be coaxed from nothing but 1s and the eml operator.

## What Did We Find?

The proof exhibits two explicit expressions — one for π with 137 tokens, one for i with 91 tokens — and verifies them three independent ways.

The construction proceeds in nine stages. First, e = eml(1, 1). Two more exp layers produce exp(exp(e)) ≈ 3.8 million. A single outer eml subtracts this from 1: NEG = e − exp(e) ≈ −12.44 — the first real-negative value. Applying one more eml produces Z = e − ln(e − exp(e)), and the principal-branch log of the negative real injects exactly +iπ into the imaginary part, which the outer subtraction flips to −π. SymPy confirms symbolically that Im(Z) equals −π exactly.

Once Z carries −iπ as its imaginary part, the rest is a dance of previously verified eml identities. The K=11 subtraction tree isolates −iπ from Z. Exponentiating gives −1; the triple-nesting log identity recovers +iπ. The K=19 addition tree produces 2, and exp of the negated log gives 1/2. The K=17 multiplication tree combines iπ and 1/2 into iπ/2, whose exponential is i. Multiplying i by −iπ gives π. Each building block was proved separately in other site proofs; this proof is the composition.

The π-expression matches math.pi to 3.52 × 10⁻¹⁵. The i-expression matches 1j to 1.30 × 10⁻¹⁵. Squaring the i-expression matches −1 with residual 2.59 × 10⁻¹⁵. Fourteen intermediate stage values were cross-checked against analytic counterparts; every one agrees to better than 4 × 10⁻¹⁵. A structural check confirms that every single leaf in both trees is the constant 1 — no x, no y, no hidden constants.

## What Should You Keep In Mind?

The construction is an existence proof, not a minimality proof. K = 137 for π and K = 91 for i are upper bounds. Whether shorter eml-from-1 expressions exist for either constant is an open question that would require an exhaustive search larger than the one performed for multiplication.

The proof rests on the principal-branch convention log(−r) = ln(r) + iπ for real r > 0. This is the canonical choice in complex analysis and is what both Python's cmath and SymPy implement. A different branch convention (e.g., placing the cut elsewhere) would require a different chain — the imaginary unit enters the computation precisely at the two steps that cross the negative real axis.

The reused identities (ADD, MULT, SUB) carry their own principal-branch obligations: they need |Im| < π at their internal cancellation points. Every invocation in this proof was checked — SUB(Z, A) operates strictly inside |Im| < π/2; the first MULT operates at |Im| = π/2; the second MULT operates at Im = 0. All safely inside the fan.

The largest intermediate value in the chain is exp(exp(e)) ≈ 3.8 × 10⁶, well within double precision. No overflow or underflow risk.

## How Was This Verified?

This claim was verified using the proof-engine framework, which requires every step to be executed by code rather than asserted by the AI. The symbolic pivot — Im(Z) = −π exactly — was established by SymPy's as_real_imag() on the eleven-token sub-expression. The full chain was evaluated numerically via recursive cmath.exp and cmath.log, and cross-checked by squaring the i-expression. Fourteen intermediates were independently checked. Token counts and the all-leaves-are-1 property were verified by tree-walks. The result being verified was originally established in A. Odrzywołek, "All elementary functions from a single binary operator" (arXiv:2603.21852, 2026); this proof was developed independently by composing previously verified eml identities. For the full formal breakdown, see [the structured proof report](proof.md). For verification details, see [the audit](proof_audit.md). To reproduce, [re-run the proof script](proof.py).
