# Proof Narrative: Fewer than 20 percent of the positive integers from 1 to 1000 are prime.

## Verdict

**Verdict: PROVED**

The numbers don't lie: primes are rarer than you might think, and the math here leaves no room for doubt.

## What was claimed?

The claim is that if you look at every whole number from 1 to 1000, fewer than 1 in 5 of them will be prime — that is, divisible only by 1 and themselves. This might matter to anyone who's wondered how densely packed the primes are among ordinary counting numbers, or who's skeptical that primes "thin out" as numbers grow larger.

## What did we find?

There are exactly 168 prime numbers between 1 and 1000. They start at 2 and end at 997, and they are spread unevenly through the range — clustering a bit more at the low end and growing sparser as numbers get larger.

168 out of 1000 works out to 16.8%. That's comfortably below the 20% threshold. Even if you rounded generously, you'd still be well clear of the line.

To make sure this count was right, two completely independent methods were used. The first was the Sieve of Eratosthenes, a classical algorithm that works by crossing out multiples of each prime in sequence. The second was trial division, which tests each number individually by checking whether anything smaller than its square root divides it evenly. Both methods produced the exact same list of 168 primes — every single one matching.

That agreement matters. If there were a programming error that caused primes to be missed or double-counted, it would have to afflict both algorithms in exactly the same way — which is effectively impossible given how differently they work. As a further sanity check, 168 is also the well-established value that number theorists use for this count, written π(1000) = 168.

One potential quibble: does "fewer than 20 percent" mean strictly less than 20, or could it include exactly 20? The phrase "fewer than" is unambiguously strict. But even setting that aside, 168 is well below 200 — the count would have to be 32 primes higher before the claim could even be questioned under the most lenient reading.

## What should you keep in mind?

This result applies exactly to the range 1 through 1000 — no more, no less. The density of primes does continue to decrease as numbers get larger (a fact captured by the Prime Number Theorem), so the 16.8% figure is actually somewhat higher than you'd find for ranges like 1 to a million. In other words, this claim holds, but don't assume the same percentage applies at larger scales.

Also worth noting: 1 is not considered prime by modern convention, and 2 is the only even prime. These edge cases are handled correctly by both algorithms, but they're easy sources of off-by-one errors in informal reasoning about primes.

## How was this verified?

This claim was checked using two independent computational methods run against the same input range, then cross-validated against a known number-theoretic result. Full details are in [the structured proof report](proof.md) and [the full verification audit](proof_audit.md). To inspect or rerun the calculation yourself, see [re-run the proof yourself](proof.py).