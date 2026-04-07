# Proof Narrative: 641 divides 2^{32} + 1 exactly.

## Verdict

**Verdict: PROVED**

641 divides 2^32 + 1 without a remainder — and this result was confirmed three independent ways, including by a classical argument that dates back to Euler.

## What was claimed?

The claim is that 641 divides the number 2^32 + 1 exactly, meaning no remainder is left over. That number — 2^32 + 1, which equals 4,294,967,297 — is historically significant. Fermat conjectured in the 1600s that all numbers of this form (1 plus a power-of-two exponent that is itself a power of two) are prime. This claim is a direct test of whether Fermat was wrong about the fifth such number.

## What did we find?

The most direct check: compute 4,294,967,297 divided by 641 and look at the remainder. The remainder is zero. That alone is sufficient to confirm the claim.

To make sure the result wasn't a fluke of how the arithmetic was done, a second method reconstructed the original number from scratch. Dividing 4,294,967,297 by 641 gives a quotient of 6,700,417 with nothing left over. Multiplying back — 641 times 6,700,417 — returns exactly 4,294,967,297. The numbers agree to the last digit.

A third approach follows Euler's own 18th-century proof. The number 641 can be written two different ways: as 5^4 + 2^4, and as 5 × 2^7 + 1. These two representations can be combined through a short chain of modular arithmetic to show that 2^32 must be congruent to −1 modulo 641 — which is just another way of saying that adding 1 makes it divisible by 641. This approach uses no division at all, yet reaches the same conclusion.

All three methods agree. The complete factorization of 4,294,967,297 is 641 × 6,700,417. Both of those factors are prime, so this is as far as the number breaks down.

## What should you keep in mind?

The arithmetic here is exact — there's no rounding, no estimation. Python's integers can be arbitrarily large, so computing with a 10-digit number introduces no precision risk.

The claim doesn't require 641 to be prime (though it is). "Divides exactly" just means remainder zero, and that's what was tested.

This result disproves Fermat's conjecture for F_5, but it says nothing about the other Fermat numbers. Some are prime; many others are composite. The pattern Fermat hoped for doesn't hold in general, and this specific number is the most famous counterexample.

One thing worth appreciating: the fact that 641 has the dual representations 5^4 + 2^4 and 5 × 2^7 + 1 isn't a coincidence used in hindsight — Euler deliberately sought a number with both properties, knowing that structure would force divisibility. It's a rare case where a proof from three centuries ago can be re-run as working code and confirmed digit-by-digit.

## How was this verified?

This result was produced using the proof-engine framework, which runs automated computation, cross-checks results using independent methods, and tests adversarial scenarios before returning a verdict. The full reasoning is in [the structured proof report](proof.md), every computation step is logged in [the full verification audit](proof_audit.md), and you can [re-run the proof yourself](proof.py).