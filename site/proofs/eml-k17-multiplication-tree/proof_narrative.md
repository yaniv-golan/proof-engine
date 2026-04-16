# Proof Narrative: A K=17 binary tree of eml operations evaluates to x * y

## Verdict

**Verdict: PROVED**

Eight operations. Nine leaves. Multiplication emerges from an operator that knows only exponentials and logarithms.

## What Was Claimed?

The binary operator eml is defined by the expression eml(a, b) = exp(a) - ln(b). There exists a finite binary tree consisting solely of eml operations, whose 9 leaves are drawn from the set {1, x, y}, such that the tree evaluates exactly to x times y. The tree has K = 17 tokens (8 eml operations and 9 leaves), and the identity holds for all complex x and y in the algebraic setting where ln composed with exp is the identity.

This is a remarkable claim. Multiplication is one of the most fundamental arithmetic operations, yet expressing it through an operator that combines exponentials and logarithms seems to require threading values through layers of explosive growth and slow compression. The claim says this can be done with only 17 tokens -- two fewer than the 19 needed for addition.

## What Did We Find?

The proof exhibits the explicit 17-token expression and verifies it layer by layer.

The construction rests on a single algebraic insight: x times y equals exp(ln(x) + ln(y)). The challenge is computing ln(x) + ln(y) using eml. Here the operator reveals a surprising shortcut. The expression eml(1, x) directly produces e minus ln(x) -- the exact "e minus logarithm" form that the addition tree needed two steps to reach. This head start, combined with using y as a bare leaf in the subtraction step (which contributes minus ln(y) instead of minus y), makes multiplication two tokens shorter than addition.

The chain unfolds in eight layers. The first step gives e minus ln(x). The next three apply the triple-nesting identity to produce ln(e minus ln(x)). The fifth step combines this with y to get e minus ln(xy) -- exploiting the logarithmic identity ln(x) + ln(y) = ln(xy). Two more steps unwrap this to recover ln(xy). The final step exponentiates: exp(ln(xy)) equals xy.

Every one of the eight layers was evaluated symbolically by SymPy, which confirmed that five critical algebraic cancellation points produce exact zero residuals. The final expression minus x times y simplifies to exactly zero. As an independent cross-check, the chain was evaluated numerically at eighteen test points -- twelve with real values (including negative inputs and values within one trillionth of a singularity) and six with complex values -- all matching x times y to within machine epsilon.

An embedded exhaustive search of all eml binary trees through K equals 15 (nearly two million distinct expressions, completed in about two and a half seconds) found nothing that computes multiplication, confirming that no shorter expression exists.

## What Should You Keep In Mind?

Unlike the addition tree, the multiplication expression cannot handle zero. When x or y is zero, the very first step requires the logarithm of zero, which is undefined, and the expression diverges. Multiplication by zero is well-defined in arithmetic, but the eml tree cannot represent it. This is a genuine limitation, not a removable singularity.

There is one removable singularity: at x equals e raised to the e power (approximately 15.154), an intermediate value hits zero. SymPy confirmed that the limit from both sides equals the correct product, and numerical tests extremely close to this point converge properly.

For negative real inputs, the intermediate computations pass through complex numbers -- logarithms of negative reals introduce imaginary parts of plus or minus pi times i. As with the addition tree, these imaginary terms cancel exactly, always returning the correct real product. This was verified numerically for several negative-input pairs.

On the principal branch of the complex logarithm, the identity holds for all nonzero x and y. The branch-cut analysis is actually more favorable than for the addition tree: the imaginary part of the critical intermediate is always bounded by pi, so no restriction on the inputs is needed beyond excluding zero.

## How Was This Verified?

This claim was verified using the proof-engine framework, which requires every step to be executed by code rather than asserted by the AI. The symbolic derivation was performed by SymPy and independently cross-checked with numerical evaluation at eighteen points, including negative and complex inputs. An embedded exhaustive search provides a reproducible minimality check. The result being verified was originally established in R. Cheng, "The elementary function arithmetic" (arXiv:2603.21852, 2026); this proof was developed independently using different methods. For the full formal breakdown, see [the structured proof report](proof.md). For verification details including computation traces and adversarial checks, see [the full verification audit](proof_audit.md). To reproduce the proof yourself, [re-run the proof script](proof.py).
