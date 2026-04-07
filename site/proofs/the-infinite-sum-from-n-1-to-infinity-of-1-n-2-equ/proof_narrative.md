# Proof Narrative: The infinite sum from n=1 to infinity of 1/n^2 equals exactly pi^2/6

## Verdict

**Verdict: PROVED**

One of the most celebrated results in mathematics holds up under rigorous computational scrutiny: the sum of the reciprocals of all perfect squares equals exactly π²/6.

## What was claimed?

If you add up 1/1 + 1/4 + 1/9 + 1/16 + 1/25 — the reciprocals of every perfect square, forever — the total doesn't grow without bound. It settles on a precise value. The claim is that this value is *exactly* π²/6, roughly 1.6449. Not approximately, not coincidentally close — exactly equal, in the same way that 2 + 2 is exactly 4.

This result, known as the Basel problem, surprises many people: why should squaring integers and summing their reciprocals have anything to do with π, a number that comes from circles? That unexpected connection is part of what makes this identity famous.

## What did we find?

Three completely independent methods all arrived at the same answer: π²/6.

The first approach used symbolic algebra software to evaluate the sum in closed form. The computation returned π²/6 exactly — not a decimal approximation, but the symbolic expression itself. The difference between the computed result and π²/6 simplifies to zero.

The second approach bypassed symbolic reasoning entirely and worked numerically. Using arbitrary-precision arithmetic, both the infinite sum (computed via the Riemann zeta function at 2) and π²/6 were calculated to 60 decimal places independently. They agreed to every single one of those 60 digits. This rules out the possibility that the values are merely close neighbors rather than identical — any difference would have shown up within the first few digits.

The third approach came from a completely different branch of mathematics: Fourier analysis. Consider the simple function f(x) = x on the interval from −π to π. Parseval's theorem relates the energy of this function to its Fourier coefficients. Working through the math, the left side of the equation evaluates to 2π²/3, and the Fourier coefficients contribute exactly 4 times the sum we care about. Solving gives the sum = π²/6. This derivation doesn't use the first two methods at all — it arrives at the same result through an entirely different door.

The three methods use fundamentally different algorithms: symbolic Bernoulli number evaluation, arbitrary-precision Euler-Maclaurin summation, and Fourier analysis. The probability that all three would agree by coincidence or share the same bug is negligible.

## What should you keep in mind?

This is a pure mathematical identity, so the usual caveats about data quality or source reliability don't apply. What matters here is whether the verification methods themselves are trustworthy.

The 60-digit numerical agreement is strong evidence but technically not a proof of exact equality on its own — it rules out any near-miss but can't exclude differences smaller than 10⁻⁶⁰. That's where the symbolic computation and the Parseval derivation do the heavy lifting: they establish exact equality through formal mathematical reasoning, not just numerical closeness.

The Parseval approach requires that f(x) = x be square-integrable on [−π, π], which it is (the function is continuous and bounded on that interval). No edge cases were found that would undermine the derivation.

One thing worth noting: the series converges because all its terms are positive, so partial sums only increase. Convergence itself follows from a standard calculus test. There is no ambiguity about whether the sum "exists" — it does, and it equals π²/6.

## How was this verified?

This identity was checked using three mathematically independent computational methods — symbolic algebra, arbitrary-precision numerics, and Fourier analysis — run as a single automated proof script. Full details are in [the structured proof report](proof.md) and [the full verification audit](proof_audit.md). To inspect or rerun the computation yourself, see [re-run the proof yourself](proof.py).