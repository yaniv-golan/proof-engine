# Proof Narrative: The Goldbach conjecture holds for every even integer greater than 2.

## Verdict

**Verdict: UNDETERMINED**

One of mathematics' oldest unsolved problems remains exactly that — unsolved. Computation can build evidence, but it cannot close an infinite question.

## What was claimed?

The Goldbach conjecture, first proposed in 1742, asserts that every even number greater than 2 can be written as the sum of two prime numbers. For example, 4 = 2 + 2, 6 = 3 + 3, 28 = 5 + 23. It sounds simple enough to state in a single sentence, yet no one has ever proved — or disproved — that it holds for every even number without exception. People encounter this claim in popular mathematics, puzzle books, and viral posts, often presented as if it were either obvious or secretly settled.

## What did we find?

We checked every even integer from 4 up to one million — that's 499,999 numbers — and found zero counterexamples. Every single one could be expressed as the sum of two primes. This was done using two completely independent computational methods: one that tests primality on demand for each candidate pair, and one that pre-generates all primes up to a million and uses fast set lookups. Both methods produced identical results, which rules out a bug in either approach causing a false confirmation.

This is not a small feat of computation. A counterexample would be genuinely newsworthy, and none has ever been found. The broader mathematical community has pushed verification far beyond our one-million bound: as of 2013, Oliveira e Silva had confirmed the conjecture holds up to 4 × 10¹⁸ — four quintillion — and the Gridbach project has extended this further still.

We also searched for any reported counterexample or accepted proof, and found neither. Several non-peer-reviewed papers have claimed proofs in recent years, but none has been accepted by mainstream mathematics. As of early 2026, the conjecture is listed as an open problem by every major mathematical reference.

The fundamental issue is not the quality of computation but the nature of the claim. No finite check, however large, can verify a statement about infinitely many numbers. Even if someone verified every even integer up to a googol, there could still be a counterexample beyond that point. That gap between "verified for all cases checked" and "true for all cases that exist" is precisely what makes this UNDETERMINED rather than SUPPORTED or PROVED.

## What should you keep in mind?

The UNDETERMINED verdict reflects the structure of the problem, not a weakness in the evidence. In fact, the computational evidence is unusually strong — hundreds of years of searching, billions of cases checked, no counterexample ever found. But mathematical proof requires certainty over an infinite domain, and computation alone cannot provide that.

It is also worth noting that the absence of a counterexample is not the same as the conjecture being "almost certainly true" in a way that should satisfy a skeptic. History contains examples of conjectures that held for enormous ranges before finally failing. Mathematicians take this possibility seriously, even for Goldbach.

Finally, the claimed proofs circulating in non-peer-reviewed venues should not be taken as evidence that the problem is close to being settled. The mathematical community has clear standards for what counts as a proof, and none of these have met them.

## How was this verified?

This investigation ran two independent computational checks across all 499,999 even integers in the range [4, 1,000,000], and conducted adversarial searches for counterexamples and accepted proofs in the mathematical literature. Full details of the evidence and logic are in [the structured proof report](proof.md), the complete step-by-step methodology is documented in [the full verification audit](proof_audit.md), and you can [re-run the proof yourself](proof.py).