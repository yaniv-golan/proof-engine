# Proof Narrative: The 100000th prime number is exactly 1299709.

## Verdict

**Verdict: PROVED**

The 100,000th prime number is exactly 1,299,709 — and this can be established with complete certainty through multiple independent computational methods that all agree.

## What was claimed?

Prime numbers are the building blocks of arithmetic: 2, 3, 5, 7, 11, and so on, each divisible only by 1 and itself. If you list them in order and count to the 100,000th one, what number do you land on? The claim is that it's precisely 1,299,709 — no rounding, no approximation, exact.

This kind of question comes up in number theory, cryptography, and mathematical curiosity. It's the sort of fact you might encounter in a textbook or an online list of primes, and it's worth knowing whether those sources actually get it right.

## What did we find?

A Sieve of Eratosthenes — the classical algorithm for generating primes — was run to find the 100,000th prime directly. It returned 1,299,709.

To make sure this wasn't just one algorithm getting lucky, an independent method counted how many primes exist up to 1,299,709. The answer: exactly 100,000. That means 1,299,709 is the 100,000th prime, not the 99,999th or the 100,001st.

To close the boundary completely, the same counting method was applied to 1,299,708 — the number just below. It found 99,999 primes. So there are 99,999 primes up to 1,299,708, and exactly 100,000 primes up to 1,299,709. The only way that's possible is if 1,299,709 itself is prime — and a third method, trial division, confirmed this independently by checking every possible factor up to its square root and finding none.

As an additional sanity check, the sieve was tested against known small values: the 1st prime is 2, the 10th is 29, the 100th is 541, the 1,000th is 7,919. All correct. This rules out any systematic counting error that might quietly shift the answer.

## What should you keep in mind?

Modern mathematics does not count 1 as a prime number, and this proof follows that convention. If someone were using an older convention that included 1, the 100,000th prime under that system would be different. The proof explicitly checks this and confirms the claim uses the standard modern convention.

There's also the question of indexing: does "the 100,000th prime" mean starting the count at zero or one? The proof uses 1-based indexing — p(1) = 2, p(2) = 3, and so on — which is the standard mathematical convention. The claim is consistent with this.

These edge cases were checked deliberately, not assumed away. Neither one undermines the result.

## How was this verified?

This proof was produced by running fully automated computations using three mathematically independent methods, with every step logged. You can read [the structured proof report](proof.md) for a summary of the evidence, examine [the full verification audit](proof_audit.md) for computation traces and adversarial checks, or [re-run the proof yourself](proof.py) to reproduce the result from scratch.