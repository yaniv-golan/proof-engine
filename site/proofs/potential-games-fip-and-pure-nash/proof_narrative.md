# Proof Narrative: Potential Games — Generalized Ordinal Potential and Exact Potential Theorems

## Verdict

**Verdict: PROVED**

Both fundamental theorems about potential games hold: ordinal potentials guarantee convergence and equilibrium existence, and exact potentials turn optimization into equilibrium-finding.

## What Was Claimed?

In game theory, a "potential game" is one where the incentives of all players can be captured by a single global function. The claim makes two assertions about such games. First, if a game has a generalized ordinal potential — a function that goes up whenever any player makes an improving move — then the game can never cycle through improving moves forever, and it must have a stable state (a pure Nash equilibrium) where nobody wants to change their strategy. Second, if the game has an exact potential — where the potential change precisely matches each player's utility change — then simply maximizing the potential function directly finds a Nash equilibrium.

These results matter because they connect individual strategic behavior to a global optimization problem. If you can identify the potential function, you can analyze equilibria without reasoning about each player separately — a major simplification used throughout economics, engineering, and computer science.

## What Did We Find?

The proof verified both claims through a combination of logical deduction and exhaustive computational testing.

For the first claim, the argument is elegantly simple. Every time a player makes an improving move, the potential function strictly increases. Since a finite game has finitely many strategy profiles, the potential can only take finitely many values. A strictly increasing sequence drawn from a finite set must eventually stop — it cannot cycle or go on forever. When it stops, no player can improve, which is exactly the definition of a Nash equilibrium.

For the second claim, the reasoning is even more direct. If the potential is at its global maximum, no change to any single player's strategy can push it higher. But the exact potential property says that every player's utility change equals the potential change. So no player can increase their own utility either — the maximum of the potential is automatically a Nash equilibrium.

To back up the logical arguments, the proof computationally verified both claims on over 70,000 randomly generated games of various sizes, plus specific well-known games including congestion games and the Prisoner's Dilemma. Not a single violation was found. Every game with a valid generalized ordinal potential had the finite improvement property and at least one pure Nash equilibrium. Every global maximizer of an exact potential was confirmed to be a Nash equilibrium.

## What Should You Keep In Mind?

The claims are about finite games only — infinite strategy spaces require different treatment. The results guarantee existence of pure Nash equilibria but say nothing about how quickly a better-response path converges (the bound is the total number of strategy profiles, which can be exponentially large). The generalized ordinal potential result applies to better-response paths, not best-response paths specifically — though best-response is a special case. Finally, these theorems tell you what happens when a potential exists, but determining whether a given game admits a potential is a separate question.

## How Was This Verified?

The proof was constructed as a self-contained Python script that implements game-theoretic definitions from scratch, tests them exhaustively on randomly generated and analytically constructed games, and outputs a machine-checkable verdict. For the full logical argument with cross-references to each verification step, see [the structured proof report](proof.md). For complete computation traces and quality checks, see [the full verification audit](proof_audit.md). To reproduce everything independently, [re-run the proof yourself](proof.py).
