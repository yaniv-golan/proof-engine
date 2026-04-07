# Proof Narrative: The St. Petersburg paradox has a finite expected value that a rational person should be willing to pay.

## Verdict

**Verdict: DISPROVED**

The claim gets the math backwards: the expected monetary value of the St. Petersburg game is not finite — it's infinite, which is exactly why the paradox exists in the first place.

## What was claimed?

The St. Petersburg paradox describes a coin-flipping game where your winnings double each round, and you keep flipping until you get tails. The claim is that this game has a finite expected value — a specific dollar amount that a rational person could calculate and decide whether to pay as an entry fee.

People encounter this claim when trying to resolve the paradox. The intuition is appealing: surely there must be some number that captures what the game is "worth." If there were a finite expected value, you could simply compare it to the entry fee and decide whether to play.

## What did we find?

The expected monetary value of the St. Petersburg game is infinite, not finite. To see why, consider what each round contributes to the expected value. On flip 1, there's a 1-in-2 chance of winning $2, contributing exactly $1. On flip 2, there's a 1-in-4 chance of winning $4, also contributing exactly $1. On flip 3, a 1-in-8 chance of winning $8 — again exactly $1. This pattern holds for every flip without exception: each round contributes precisely $1 to the expected value. Adding infinitely many $1 contributions gives infinity, not a finite number. This was verified algebraically and confirmed computationally for the first 20 terms.

The divergence isn't subtle or approximate. After 10 rounds, the partial sum is exactly 10. After 20 rounds, exactly 20. The sum grows without bound — there is no ceiling.

This infinite expected value is precisely the paradox. If you take expected monetary value seriously as a decision rule, you should pay any finite entry fee to play — which strikes most people as absurd, since the game rarely pays out large sums in practice.

There is a genuine resolution to the paradox, but it doesn't involve a finite expected value. The 18th-century mathematician Daniel Bernoulli proposed that rational people maximize expected *utility*, not expected monetary value. Under logarithmic utility — where each doubling of wealth matters less than the last — the expected utility of the game is finite: approximately 1.386, which translates to a certainty equivalent of exactly $4. That's the most a rational, risk-averse agent should pay to play.

The claim conflates these two distinct concepts. The $4 figure is a certainty equivalent derived from expected utility theory, not an expected value. The expected value remains infinite.

## What should you keep in mind?

The $4 certainty equivalent is real and meaningful — but it depends on assuming logarithmic utility and zero initial wealth. Under different but still reasonable risk-averse preferences, you'd get a different finite number. The point is that any risk-averse utility model gives *some* finite willingness to pay; the exact amount varies.

Logarithmic utility is also not a complete fix for all related puzzles. A variant of the game with a different payoff structure can produce infinite expected utility even under log utility, showing that the deeper question of how to handle extreme tail risks in decision theory remains open.

The claim's failure is terminological as much as mathematical. "Expected value" has a precise technical meaning, and the St. Petersburg game's expected value is infinite by mathematical consensus — confirmed by both Wikipedia and the Stanford Encyclopedia of Philosophy. Saying the game has a "finite expected value" is simply incorrect, regardless of what framework you use to decide what to pay.

## How was this verified?

This claim was evaluated by decomposing it into two sub-claims — whether the expected monetary value is finite, and whether a rational willingness to pay exists — then testing each algebraically and computationally. You can read the full mathematical breakdown in [the structured proof report](proof.md), review every computation and citation check in [the full verification audit](proof_audit.md), or [re-run the proof yourself](proof.py).