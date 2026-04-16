# Proof Narrative: \(\text{eml}(a, b) = \exp(a) - \ln(b)\) satisfies \(\text{eml}(x, 1) = \exp(x)\)

## Verdict

**Verdict: PROVED**

The identity holds exactly — not approximately, not in a limit, but as a straightforward algebraic fact.

## What Was Claimed?

Someone defined a new two-input operator called "eml" that takes two numbers and returns the exponential of the first minus the natural logarithm of the second: eml(a, b) = exp(a) - ln(b). The claim is that when the second input is fixed at 1, this operator simply returns the exponential of the first input. In other words, eml(x, 1) = exp(x) for every complex number x.

This is the kind of identity that looks obvious once you see the trick — but the trick needs to be verified rigorously, especially when the claim extends to all complex numbers, where the logarithm has branch cuts and other subtleties.

## What Did We Find?

The entire proof hinges on one fact: the natural logarithm of 1 is zero. When you plug b = 1 into the operator definition, you get eml(x, 1) = exp(x) - ln(1) = exp(x) - 0 = exp(x). That is the complete argument.

We verified this in two independent ways. First, using symbolic algebra (SymPy), we confirmed that ln(1) evaluates to exactly 0, and that the expression exp(x) - ln(1) - exp(x) simplifies to exactly 0 for a symbolic variable x. This is not a numerical approximation — the computer algebra system proves the identity holds in closed form.

Second, as a cross-check, we evaluated the operator numerically at five representative complex numbers: zero, a positive real number, a negative real number, a purely imaginary number (iπ), and a general complex number (2 + 3i). At every point, the difference between eml(x, 1) and exp(x) was exactly zero — not merely small, but identically zero to machine precision.

We also investigated whether the complex logarithm could introduce any surprises. The logarithm has branch cuts in the complex plane, but the point z = 1 sits safely on the positive real axis, far from any branch cut. Every standard branch of the complex logarithm gives ln(1) = 0.

## What Should You Keep In Mind?

The identity is specific to b = 1. The operator eml(a, b) is not defined at b = 0 (since ln(0) is undefined), and for other values of b it does not simplify to exp(a). The proof says nothing about the operator's behavior at other values of its second argument.

The result is an algebraic certainty within the standard mathematical framework — it cannot be overturned by new data or different parameter choices. It is as definitive as proofs get.

## How Was This Verified?

This claim was verified using the proof-engine framework, which requires every step to be executed by code rather than asserted by the AI. The symbolic derivation was performed by SymPy and independently cross-checked with numerical evaluation. The result being verified was originally established in R. Cheng, "The elementary function arithmetic" (arXiv:2603.21852, 2026); this proof was developed independently using different methods. For the full formal breakdown, see [the structured proof report](proof.md). For verification details including computation traces and adversarial checks, see [the full verification audit](proof_audit.md). To reproduce the proof yourself, [re-run the proof script](proof.py).
