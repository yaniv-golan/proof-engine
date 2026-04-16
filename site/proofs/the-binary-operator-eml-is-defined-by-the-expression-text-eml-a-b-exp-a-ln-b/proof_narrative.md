# Proof Narrative: \(\text{eml}(1, 1) = e\)

## Verdict

**Verdict: PROVED**

Plug in the numbers, and out comes one of the most famous constants in mathematics.

## What Was Claimed?

A binary operator called "eml" takes two numbers and returns the exponential of the first minus the natural logarithm of the second. The claim is that when both inputs are set to 1, the result is exactly e — Euler's number, approximately 2.71828. It is the kind of claim that looks like it should be easy to verify, and it is — but even easy claims deserve rigorous checking.

## What Did We Find?

The proof breaks into two elementary facts. First, the exponential of 1 is e. This is not a computation — it is the definition of the exponential function. The function exp is defined as the unique function satisfying exp(0) = 1 and being its own derivative; evaluating it at 1 gives the constant e. The computer algebra system SymPy confirms this: exp(1) minus its symbolic constant E equals exactly zero.

Second, the natural logarithm of 1 is zero. Since the logarithm answers "what power of e gives this number?", and e raised to the zero power is 1, we get ln(1) = 0. This holds in the complex plane as well — the principal branch of the complex logarithm evaluates to zero at the point z = 1, safely away from any branch cut.

Putting it together: eml(1, 1) = exp(1) - ln(1) = e - 0 = e. SymPy confirms the residual exp(1) - ln(1) - e is exactly zero. As a cross-check, numerical evaluation in Python gives eml(1, 1) = 2.718281828459045, matching the built-in value of e to all 15 displayed decimal places, with zero absolute difference.

## What Should You Keep In Mind?

This result is specific to the inputs (1, 1). The operator eml(a, b) is not defined when b = 0, since ln(0) is undefined. For other input values, the result will generally not equal e or any other recognizable constant.

The identity is an algebraic certainty — it follows from definitions and cannot be overturned by new evidence or different computational methods. It is as definitive as mathematical results get.

## How Was This Verified?

This claim was verified using the proof-engine framework, which requires every step to be executed by code rather than asserted by the AI. The symbolic verification was performed by SymPy and independently confirmed by numerical evaluation. The result being verified was originally established in R. Cheng, "The elementary function arithmetic" (arXiv:2603.21852, 2026); this proof was developed independently using different methods. For the full formal breakdown, see [the structured proof report](proof.md). For verification details including computation traces and adversarial checks, see [the full verification audit](proof_audit.md). To reproduce the proof yourself, [re-run the proof script](proof.py).
