# Proof Narrative: A real number is rational if and only if its decimal expansion is eventually periodic.

## Verdict

**Verdict: PROVED**

This is one of the foundational results of real analysis, and the verification confirms it completely: every fraction produces a repeating decimal, and every repeating decimal comes from a fraction — no exceptions.

## What was claimed?

The claim is that there is a perfect two-way correspondence between rational numbers (fractions like 1/3 or 7/12) and decimals that eventually fall into a repeating cycle. A decimal like 0.333... repeats forever; 0.08333... has a short non-repeating prefix before settling into repetition; even 0.25 counts, because it's really 0.25000... with an endlessly repeating zero. The claim says this "eventually repeating" pattern is exactly what separates rational numbers from irrationals like π or √2, whose digits never settle into any cycle.

Anyone who has done long division by hand has glimpsed why this should be true — the remainders only have so many possible values. But the claim goes both directions, and the "other way" deserves equal scrutiny.

## What did we find?

The first direction — that every fraction eventually repeats — was verified by watching long division in action. When you divide p by q, each step produces a remainder between 0 and q−1. Since there are only q possible remainders, you cannot go more than q steps before seeing a remainder you've already seen. The moment a remainder repeats, the digits repeat, and you have a cycle. This was tested on 35 fractions: terminating decimals, purely repeating decimals, and mixed cases where a non-repeating prefix precedes the cycle. Every single one behaved exactly as the pigeonhole argument predicts.

The second direction — that every eventually repeating decimal equals a fraction — was verified algebraically. If a decimal has a repeating block starting at position k with period length p, you can multiply the number by 10^(k+p) and by 10^k separately, then subtract. The repeating tails cancel, leaving a ratio of two whole numbers. That ratio is the fraction. Fourteen carefully chosen periodic decimals, including the famous 0.999... = 1, all converted correctly to their expected fractions.

The most compelling confirmation came from an exhaustive sweep: every reduced fraction p/q with denominator up to 200 was converted to its periodic decimal expansion and then converted back. All 20,100 fractions came back exactly right, with zero failures. Python's exact-arithmetic library served as an independent check throughout.

Four potential weak points were also tested. The identity 0.999... = 1 is a well-known oddity — it produces two different decimal representations for the same number — but both representations are eventually periodic, and the algebra handles it correctly. Numbers like √2 have digits that look nearly random and never form a cycle, but the proof never tries to detect cycles in arbitrary digit strings; it relies on the algebraic structure of fractions, which is immune to that confusion. Zero, negative fractions, and whole numbers were all tested and handled correctly. And the pigeonhole argument holds for any denominator, no matter how large, because it is a consequence of pure counting.

## What should you keep in mind?

The verification is computational, not a formal mathematical proof from axioms. It provides very strong evidence — 20,100 cases exhaustively confirmed — but it tests a finite sample of the infinite set of all rationals, and it tests specific implementations of the two conversion algorithms. The mathematical argument (pigeonhole for direction one; algebraic cancellation for direction two) is watertight and well-known, and the computation confirms it, but the two should not be confused.

The theorem applies to decimal expansions specifically. In other number bases (binary, hexadecimal), the same result holds with the appropriate base substituted — but the specific fractions that terminate versus repeat will differ.

Decimal representations are not unique: 0.999... and 1.000... represent the same number. The theorem is unaffected by this, but it means "the decimal expansion" is slightly loose language — any eventually periodic representation of a number suffices to confirm it is rational.

## How was this verified?

A proof script computed both directions of the biconditional, performed an exhaustive round-trip test over 20,100 rationals, and searched for counter-examples across four adversarial scenarios. The full reasoning and evidence are in [the structured proof report](proof.md), every methodological step and adversarial check is documented in [the full verification audit](proof_audit.md), and you can [re-run the proof yourself](proof.py) to reproduce all results independently.