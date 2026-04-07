# Proof Narrative: The integer 1 is a prime number.

## Verdict

**Verdict: DISPROVED**

The integer 1 is not a prime number — and this isn't a close call. It fails the definition of primality on two separate counts, confirmed by three independent methods.

## What was claimed?

The claim is that 1 is a prime number, the same kind of number as 2, 3, 5, 7, or 11. This comes up surprisingly often: people remember that primes are numbers "only divisible by 1 and themselves," and 1 fits that description in a loose reading. It seems like it should qualify. Many people are surprised to learn it doesn't.

## What did we find?

A prime number, by the standard definition used in all of modern mathematics, must satisfy two conditions: it must be greater than 1, and it must have exactly two distinct positive divisors — 1 and itself. The integer 1 fails both.

First, 1 is not greater than 1. That one is straightforward. The definition is explicit: primes must be strictly greater than 1.

Second, 1 has only one positive divisor: itself. A prime like 7 has two divisors — 1 and 7. The number 1 only has one divisor (1), so it doesn't have the two distinct divisors that primality requires. The phrase "divisible by 1 and itself" only means something distinct for a prime because those are *two different numbers*. For 1, they're the same number.

Three independent methods were used to confirm this. Exhaustive enumeration of divisors, a standard trial division algorithm, and the Python mathematical library SymPy all return the same answer: 1 is not prime.

## What should you keep in mind?

The result here is unambiguous by modern standards, but the history is genuinely interesting. For centuries, many prominent mathematicians — including Goldbach and Euler — did consider 1 to be prime. The modern convention excluding 1 was not always obvious or universal.

The reason 1 is excluded today isn't arbitrary. If 1 were prime, the Fundamental Theorem of Arithmetic — which says every integer greater than 1 has a *unique* prime factorization — would break down. The number 6 could be factored as 2 × 3, or as 1 × 2 × 3, or as 1 × 1 × 2 × 3, and so on infinitely. Unique factorization is a cornerstone of number theory, and preserving it is the mathematical reason the definition was standardized to exclude 1.

Every major modern authority agrees on this: ISO 80000-2, the international standard for mathematical notation, requires primes to be greater than 1. So do all major textbooks and computational references.

## How was this verified?

This claim was evaluated by applying the formal definition of primality directly to the integer 1, enumerating its divisors computationally and checking each definitional criterion, then cross-checking with two independent algorithms. See [the structured proof report](proof.md) for the full evidence summary and reasoning, [the full verification audit](proof_audit.md) for computation traces and adversarial checks, or [re-run the proof yourself](proof.py) to reproduce every result.