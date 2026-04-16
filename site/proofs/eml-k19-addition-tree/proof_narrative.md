# Proof Narrative: A K=19 binary tree of eml operations evaluates to x + y

## Verdict

**Verdict: PROVED**

Nine operations. Ten leaves. That is all it takes for one unfamiliar operator to replicate addition itself.

## What Was Claimed?

Someone defined a binary operator called "eml" that takes two numbers and returns the exponential of the first minus the logarithm of the second. The claim is that there exists a specific arrangement of nine nested eml calls, with leaves drawn only from the constant 1 and two variables x and y, that computes x + y for every real x and y. The entire expression has exactly 19 tokens (nodes and leaves combined).

This is a startling claim. Addition is the most basic arithmetic operation, yet expressing it through an operator built from exponentials and logarithms seems to require considerable machinery. The expression must thread through layers of rapidly growing exponentials and slowly growing logarithms, and somehow produce a simple sum at the end.

## What Did We Find?

The proof exhibits the explicit K=19 expression and verifies it layer by layer.

The construction follows a clear algebraic strategy. The innermost layers compute exp(x), then e minus x. The next three layers apply the triple-nesting identity (previously proved for the eml operator) to produce the natural logarithm of (e minus x). This is then combined with exp(y) through the eml subtraction pattern, yielding e minus x minus y. The final two layers wrap this in exp and then reverse it: e minus the logarithm of exp(e minus x minus y) collapses to x plus y.

Every one of the nine layers was evaluated symbolically by SymPy, which confirmed that five critical algebraic cancellation points produce exact zero residuals. The final expression minus (x plus y) simplifies to exactly zero. As an independent cross-check, the entire nine-layer chain was evaluated numerically at twelve test points — eight with real values spanning four orders of magnitude and four with complex values — all matching x plus y to within machine epsilon.

An exhaustive search of all eml binary trees through K=17 (over eighteen million distinct expressions) found nothing that computes addition, confirming that no shorter expression exists.

## What Should You Keep In Mind?

The expression has a removable singularity at x equals e, where an intermediate value hits zero and a logarithm becomes undefined. The limit at this point is correct (e plus y), and every other real input works without issue.

When x exceeds e, the intermediate computations pass through complex numbers — logarithms of negative reals introduce imaginary components of plus or minus pi times i. Remarkably, these imaginary terms cancel exactly across the chain, always returning a real result. This was verified both algebraically and numerically.

For complex inputs, the expression works perfectly when the imaginary part of x plus y stays below pi in absolute value. Beyond that boundary, the principal branch of the complex logarithm introduces errors that are always exact multiples of two pi i. In the formal algebraic framework used by the original paper — where logarithm and exponential are treated as true inverses — the identity holds without restriction.

## How Was This Verified?

This claim was verified using the proof-engine framework, which requires every step to be executed by code rather than asserted by the AI. The symbolic derivation was performed by SymPy and independently cross-checked with numerical evaluation at twelve points, including both real and complex inputs. For the full formal breakdown, see [the structured proof report](proof.md). For verification details including computation traces and adversarial checks, see [the full verification audit](proof_audit.md). To reproduce the proof yourself, [re-run the proof script](proof.py).
