# Proof Narrative: Let G be a finite strategic-form game. (A) If G admits a generalized ordinal potential P, then every better-response path is finite, G has the finite improvement property, and G admits a pure Nash equilibrium. (B) If G admits an exact potential P, then every global maximizer of P is a pure Nash equilibrium.

## Verdict

**Verdict: PROVED**

Both parts of this theorem are classical results, established by Monderer and Shapley in their landmark 1996 paper on potential games — and the deductive argument holds up under scrutiny without qualification.

## What Was Claimed?

The claim asks about a family of games where players repeatedly choose strategies trying to improve their own outcomes. In some games there exists a single "potential" function — a score assigned to each combination of strategies — that tracks, at least in direction, whether any one player's situation is improving. The claim asserts two things: first, that in games with this kind of potential function (called a generalized ordinal potential), the process of players sequentially making moves that help themselves must eventually stop, and when it does, the game has reached a stable outcome where nobody wants to move. Second, that if the potential function tracks payoff differences exactly (an exact potential), then the strategy combinations that maximize the potential score are themselves stable outcomes — no one has any reason to deviate.

This matters because stability — a "Nash equilibrium" — is the central solution concept in game theory. Many games are complex enough that proving one must exist is non-trivial. Potential games give a constructive route to that guarantee.

## What Did We Find?

The key insight in Part A is elegantly simple. Imagine following a sequence of moves where each player, when it is their turn, chooses a strategy that strictly increases their payoff. If a potential function exists that rises whenever any player's payoff rises, then this function is strictly increasing at every step. A strictly increasing sequence on a finite set cannot revisit the same value — and therefore cannot revisit the same game state. Since the number of possible game states is finite, the sequence must eventually end. When it ends, no player can make a profitable move, which is precisely the definition of a Nash equilibrium.

In Part B, the argument is even more direct. At a strategy combination that globally maximizes the potential, there is no state with a higher potential score. For an exact potential, the change in any player's payoff from switching strategies equals the change in the potential exactly. Since the potential cannot increase from a global maximum, no player's payoff can strictly increase by switching either. That makes every global maximizer a Nash equilibrium by definition.

Both proofs trace directly back to Monderer and Shapley (1996), specifically their Lemmas 2.3 and 2.5 for Part A and their Lemma 4.2 for Part B. The argument in the structured proof report is a re-exposition of their published reasoning, not an independent derivation. The computational checks — sweeping over 600 randomly sampled games in each case — confirmed that the code implementations of the detectors and simulators behave consistently with the formal definitions. No discrepancies were found.

## What Should You Keep In Mind?

These theorems apply only to games with a **finite** number of strategies. The termination argument in Part A relies essentially on finiteness — in a game with infinitely many possible strategies, better-response paths could go on forever even with a potential function, unless additional mathematical structure is present. The proofs say nothing about mixed-strategy equilibria, convergence rates, or how to find a Nash equilibrium efficiently (computing one is computationally hard in general). The theorems also say nothing about the converse: a game can have pure Nash equilibria without having any potential function. The computational sweeps over sampled games are sanity checks on the code, not evidence for the theorems themselves — theorems about all finite games cannot be confirmed by sampling.

## How Was This Verified?

This result was verified by re-examining the published deductive proof from Monderer and Shapley (1996) and confirming that every step holds under the stated hypotheses, alongside implementation regression checks that tested the code-side detectors against both constructive examples and random game samples. The full logical argument is in [the structured proof report](proof.md), the complete log of all checks is in [the full verification audit](proof_audit.md), and you can inspect or re-execute all computations by reading [re-run the proof yourself](proof.py).