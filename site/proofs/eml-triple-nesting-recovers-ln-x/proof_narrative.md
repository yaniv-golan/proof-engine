# Proof Narrative: Triple nesting of eml recovers ln(x)

## Verdict

**Verdict: PROVED**

Three layers of an unfamiliar operator, and what comes out the other side is one of the most fundamental functions in mathematics.

## What Was Claimed?

Someone defined an operator called "eml" that takes two numbers and returns the exponential of the first minus the logarithm of the second. The claim is that if you nest this operator three times in a specific pattern — eml(1, eml(eml(1, x), 1)) — the result is simply ln(x), the natural logarithm, for every positive real number x.

This is surprising on its face. The operator involves exponentials, which grow explosively, and logarithms, which grow slowly. Nesting three calls should compound these effects. Yet the claim says the result collapses to a single, clean logarithm.

## What Did We Find?

The proof unwinds the nesting one layer at a time, verifying each step with a computer algebra system.

The innermost call, eml(1, x), evaluates to e minus ln(x) — straightforward substitution using the definition of the operator and the fact that exp(1) equals the mathematical constant e.

The middle call feeds this result into eml as the first argument, with 1 as the second. This gives exp(e - ln(x)) minus ln(1). Since ln(1) is zero, the result is exp(e - ln(x)), which simplifies to exp(e) divided by x using standard exponent rules.

The outer call then takes 1 as the first argument and the middle result as the second. This gives e minus ln(exp(e)/x). The logarithm of a quotient splits into a difference: ln(exp(e)) minus ln(x). Since ln(exp(e)) equals e — the logarithm and exponential cancel — the expression becomes e minus (e minus ln(x)), which is simply ln(x).

Every one of these steps was confirmed by SymPy's symbolic algebra engine, which verified that the full nested expression minus ln(x) simplifies to exactly zero for a general positive symbol x. As an independent cross-check, the identity was evaluated numerically at six representative values spanning four orders of magnitude — from x = 0.01 to x = 100 — and matched ln(x) to within machine epsilon at every point.

## What Should You Keep In Mind?

The identity requires x to be a positive real number. This ensures every logarithm in the chain is real-valued, and guarantees that ln(exp(y)) = y holds without branch-cut ambiguity. For complex x, additional care would be needed.

The intermediate expressions can be extreme — for small x, the middle step produces very large numbers, while for large x it produces values near zero. But the algebraic cancellations are exact regardless. This is a structural property of the operator, not a numerical coincidence.

The result reveals that the eml operator, despite involving both exponentials and logarithms, can invert itself through nesting. The logarithm emerges not from any single step but from precise cancellation across all three layers.

## How Was This Verified?

This claim was verified using the proof-engine framework, which requires every step to be executed by code rather than asserted by the AI. The symbolic derivation was performed by SymPy and independently cross-checked with numerical evaluation at six points. The result being verified was originally established in A. Odrzywołek, "All elementary functions from a single binary operator" (arXiv:2603.21852, 2026); this proof was developed independently using different methods. For the full formal breakdown, see [the structured proof report](proof.md). For verification details including computation traces and adversarial checks, see [the full verification audit](proof_audit.md). To reproduce the proof yourself, [re-run the proof script](proof.py).
