# Proof Narrative: A K=19 binary tree of eml operations evaluates to x + y

## Verdict

**Verdict: PROVED**

Nine operations. Ten leaves. That is all it takes for one unfamiliar operator to replicate addition itself.

## What Was Claimed?

The binary operator eml is defined by the expression eml(a, b) = exp(a) - ln(b). The claim is that there exists a finite binary tree consisting solely of eml operations, whose 10 leaves are drawn from the set {1, x, y}, such that the tree evaluates exactly to x + y. The tree has K = 19 tokens (9 eml operations and 10 leaves), and the identity holds for all real x and y -- and formally for all complex x, y in the algebraic setting where ln composed with exp is the identity.

This is a startling claim. Addition is the most basic arithmetic operation, yet expressing it through an operator built from exponentials and logarithms requires considerable machinery. The expression must thread through layers of rapidly growing exponentials and slowly growing logarithms, and somehow produce a simple sum at the end.

## What Did We Find?

The proof exhibits the explicit 19-token expression and verifies it layer by layer.

The construction follows a clear algebraic strategy. The key insight is that x + y equals e minus (e minus x minus y), so the chain needs to compute (e minus x minus y) and then subtract it from e. The innermost layers compute exp(x), then e minus x. The next three layers apply the triple-nesting identity (previously proved for the eml operator) to produce the natural logarithm of (e minus x). This is then combined with exp(y) through the eml subtraction pattern, yielding e minus x minus y. The final two layers wrap this in exp and then reverse it: e minus the logarithm of exp(e minus x minus y) collapses to x plus y.

Every one of the nine layers was evaluated symbolically by SymPy, which confirmed that five critical algebraic cancellation points produce exact zero residuals. The final expression minus (x plus y) simplifies to exactly zero. As an independent cross-check, the entire nine-layer chain was evaluated numerically at fifteen test points -- ten with real values spanning four orders of magnitude (including three points extremely close to a singularity) and five with complex values -- all matching x plus y to within machine epsilon.

An embedded exhaustive search of all eml binary trees through K equals 15 (nearly two million distinct expressions, completed in about three seconds) found nothing that computes addition. A separate external search extended through K equals 17 (over eighteen million expressions) with the same result, confirming that no shorter expression exists.

## What Should You Keep In Mind?

The expression has a removable singularity at x equals e, where an intermediate value hits zero and a logarithm becomes undefined. SymPy confirmed that the limit from both sides equals e plus y, and numerical tests within one trillionth of the singularity confirmed the expression approaches the correct value. The identity holds everywhere except this single isolated point, where it holds in the limit sense.

When x exceeds e, the intermediate computations pass through complex numbers -- logarithms of negative reals introduce imaginary components of plus or minus pi times i. Remarkably, these imaginary terms cancel exactly across the chain, always returning a real result. This was verified both algebraically and numerically.

For complex inputs, the expression works perfectly when the imaginary part of x plus y stays below pi in absolute value. Beyond that boundary, the principal branch of the complex logarithm introduces errors that are always exact multiples of two pi i. In the formal algebraic framework used by the original paper -- where logarithm and exponential are treated as true inverses -- the identity holds without restriction.

## How Was This Verified?

This claim was verified using the proof-engine framework, which requires every step to be executed by code rather than asserted by the AI. The symbolic derivation was performed by SymPy and independently cross-checked with numerical evaluation at fifteen points, including near-singularity and complex inputs. An embedded exhaustive search provides a reproducible minimality check. For the full formal breakdown, see [the structured proof report](proof.md). For verification details including computation traces and adversarial checks, see [the full verification audit](proof_audit.md). To reproduce the proof yourself, [re-run the proof script](proof.py).
