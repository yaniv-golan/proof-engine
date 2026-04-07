# Proof Narrative: There are no positive integer solutions to the equation x^4 + y^4 = z^4.

## Verdict

**Verdict: UNDETERMINED**

This is one of the most famous results in mathematics — yet our engine cannot fully verify it. Here's what we found, and why that gap matters.

## What was claimed?

The claim is that no matter what positive whole numbers you pick for x, y, and z, you will never find a combination where x⁴ + y⁴ equals z⁴. If you double every number, raise it to the fourth power, and try to make two of them add up to a third — it simply cannot be done. This is a special case of Fermat's Last Theorem, a problem that stumped mathematicians for over 350 years and became one of the most celebrated puzzles in the history of mathematics.

## What did we find?

We began with a brute-force sweep: checking every combination of x and y up to 1,000 — over half a million pairs — and computing whether x⁴ + y⁴ ever lands on a perfect fourth power. It never did. Not once.

To make sure this wasn't a fluke of our algorithm, we ran a second search using a completely different approach. Instead of building up from x and y, we started from every possible z up to 1,000 and asked: does z⁴ minus x⁴ ever equal a fourth power? Again, zero solutions.

We then turned to pure mathematics. Using modular arithmetic — essentially checking how fourth powers behave when divided by 16 — we found an independent structural reason why certain classes of solutions are impossible. Specifically, if both x and y were odd numbers, the remainder pattern that results is one that no fourth power can match. This rules out an entire family of candidate solutions without any computation.

These three independent lines of inquiry all point to the same answer: no solutions exist up to 1,000, and the mathematical structure of the problem constrains where solutions could even hide.

The deeper story is well-known: Fermat himself proved this result around 1637 using a technique called infinite descent. The idea is elegant — if a solution existed, you could always construct a strictly smaller solution, which would let you construct an even smaller one, and so on forever. Since you cannot have an infinite descending chain of positive integers, no solution can exist. Euler later gave an independent proof, and in 1995 Andrew Wiles' famous proof of Fermat's Last Theorem for all exponents made this a corollary of an even larger result.

## What should you keep in mind?

The UNDETERMINED verdict is not a sign of doubt about the mathematics — it reflects a limitation of this verification engine. Fermat's infinite descent argument is a logical chain of reasoning, not a calculation a computer can run and check off. Our engine can verify computations; it cannot certify the logical steps of a proof by contradiction spanning infinite cases. The verdict honestly reflects that boundary.

Worth noting: the claim is specifically about positive integers. If you allow real numbers, solutions are easy to find — for example, x = y = 1 gives z = 2^(1/4), roughly 1.189. The integer constraint is what makes the problem hard and the result nontrivial.

It is also worth noting that while our computational search covered numbers up to 1,000, independent projects have verified no solutions exist up to at least 10¹⁸. The theoretical proof covers all integers; the computation corroborates it at scale.

## How was this verified?

This claim was evaluated using a combination of exhaustive computational search, an algorithmically independent cross-check, and modular arithmetic analysis, all conducted by the proof-engine framework. You can read [the structured proof report](proof.md) for a full summary of the evidence and logic, examine [the full verification audit](proof_audit.md) for step-by-step computation traces and adversarial checks, or [re-run the proof yourself](proof.py) to reproduce every result independently.