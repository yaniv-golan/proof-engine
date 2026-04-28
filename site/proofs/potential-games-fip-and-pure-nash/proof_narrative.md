# Proof Narrative: Generalized ordinal potentials imply FIP and a pure NE; exact-potential maximizers are pure Nash equilibria

## Verdict

**Verdict: PROVED, after Monderer & Shapley (1996)**

Both halves of this two-part theorem are theorems of <!-- not-a-citation-start -->Monderer & Shapley (1996), "Potential Games," *Games and Economic Behavior* 14(1), 124–143<!-- not-a-citation-end --> — Theorem (A) follows their Lemmas 2.3 + 2.5, and Theorem (B) is their Lemma 4.2 specialized. This artifact does not establish the result independently; it is a verifiable companion that re-presents the cited argument and regression-tests the implementation. A paper using these results should cite the primary source above.

## What Was Claimed?

The claim concerns *strategic games* — situations in which several decision-makers each pick an action and each one's payoff depends on what everybody chose. The claim has two parts.

Part (A) starts from a structural condition called a *generalized ordinal potential*: a single bookkeeping function over the joint outcomes such that whenever any player can switch to a strictly better personal payoff, the bookkeeping value goes up. Whenever a game admits such a function, the claim says three things follow at once: any sequence of one-player-at-a-time improvements must eventually stop; the game has the so-called "finite improvement property"; and there is at least one outcome from which nobody wants to deviate — a pure Nash equilibrium.

Part (B) strengthens the bookkeeping. If the bookkeeping function tracks payoff changes *exactly* — every personal payoff change equals the corresponding bookkeeping change — then any outcome where the bookkeeping is at its highest is automatically an equilibrium. Ties at the top all qualify.

This matters because pure equilibria are notoriously hard to guarantee in arbitrary games. The potential-function machinery provides one of the cleanest sufficient conditions for the easier, more interpretable pure case, and it covers a large practical class including congestion games on roads, networks, and resource pools.

## What Did We Find?

The argument for Part (A) is a one-paragraph induction on path length. Whenever a player switches to a strictly better personal payoff, the potential function strictly increases. Strictly increasing means it cannot revisit a value, so it cannot revisit an outcome. With only finitely many outcomes available, the sequence has to stop. Wherever it stops, by definition no player has a strictly profitable switch — exactly the meaning of pure Nash equilibrium. The three conclusions of Part (A) all fall out of this single observation.

The argument for Part (B) is even shorter. At an outcome where the bookkeeping is at its highest, no neighboring outcome can have higher bookkeeping by definition. With *exact* bookkeeping, any single-player switch would change a personal payoff by exactly the same amount the bookkeeping changes — so no switch can strictly increase a payoff. That is the definition of equilibrium, and the argument never needed uniqueness, so ties don't break it.

We also examined four ways the argument could quietly go wrong. The reliance on finiteness is explicit, not hidden. The two phrasings "every better-response path is finite" and "the finite improvement property" name the same property, so the redundancy in the original claim is harmless. The Part (B) argument never assumed a unique maximum. Our formalization of the potential conditions matches the standard textbook one.

The companion script implements the relevant detectors and runs them on a hand-built example for each part, then on hundreds of random small games as a code-health check. Everything came back consistent. None of that establishes the theorem (sampling cannot prove a "for all" statement), but it confirms the supporting code does not silently disagree with the formal definitions used in the argument.

## What Should You Keep In Mind?

The result is a *sufficient* condition: when a potential exists, equilibria exist. It says nothing about games that lack a potential, and nothing about *finding* an equilibrium efficiently — that question (the complexity of computing a pure equilibrium even when one is known to exist) is a separate, well-known harder problem.

Both halves require finiteness. Infinite or continuous strategy spaces — common in models with prices or quantities — need additional assumptions and the conclusion can fail without them. The result also does not address mixed equilibria, learning dynamics other than naive better-response, or convergence rates beyond the worst-case bound that path length is at most the number of outcomes minus one.

Finally, the result is foundational, not novel. It is the forward direction of an "if and only if" theorem in the canonical 1996 reference; the converse (FIP implies a generalized ordinal potential exists) is in the same paper but is not addressed here.

## How Was This Verified?

The proof is a deductive argument written out as numbered steps; it stands on its own without computation. A re-runnable Python script implements the detectors and a better-response simulator, runs them on a constructive example and a random-sample sweep as a code-health check, and emits a structured proof summary. See [the structured proof report](proof.md), [the full verification audit](proof_audit.md), or [re-run the proof yourself](proof.py).

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.33.2 on 2026-04-28.
