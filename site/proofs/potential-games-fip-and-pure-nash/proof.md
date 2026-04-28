# Proof: Generalized ordinal potentials imply FIP and a pure NE; exact-potential maximizers are pure Nash equilibria

- Generated: 2026-04-28
- Verdict: **PROVED**
- Audit trail: [proof_audit.md](proof_audit.md), [proof.py](proof.py)

## Theorem statement

Let \(G = (N, (S_i)_{i \in N}, (u_i)_{i \in N})\) be a finite strategic-form game with player set \(N\), finite strategy sets \(S_i\), and payoff functions \(u_i : S \to \mathbb{R}\) where \(S = \prod_i S_i\). For \(s \in S\) and a unilateral deviation by player \(i\) to \(s'_i \in S_i \setminus \{s_i\}\), write \((s'_i, s_{-i})\) for the resulting profile.

A function \(P : S \to \mathbb{R}\) is a **generalized ordinal potential** for \(G\) iff for every player \(i\), every profile \(s\), and every \(s'_i \in S_i\):
\[
u_i(s'_i, s_{-i}) > u_i(s) \implies P(s'_i, s_{-i}) > P(s).
\]
\(P\) is an **exact potential** iff for every \(i, s, s'_i\):
\[
u_i(s'_i, s_{-i}) - u_i(s) = P(s'_i, s_{-i}) - P(s).
\]
A **better-response path** is a (possibly infinite) sequence \(s^{(0)}, s^{(1)}, \dots\) of profiles such that each step \(s^{(k)} \to s^{(k+1)}\) is a unilateral deviation by some player \(i_k\) with \(u_{i_k}(s^{(k+1)}) > u_{i_k}(s^{(k)})\). The **finite improvement property (FIP)** says every such path terminates after finitely many steps. A profile \(s^*\) is a **pure Nash equilibrium** iff no unilateral deviation strictly increases the deviator's payoff.

**Theorem (A).** If \(G\) admits a generalized ordinal potential, then every better-response path is finite, \(G\) has the FIP, and \(G\) admits at least one pure Nash equilibrium.

**Theorem (B).** If \(G\) admits an exact potential \(P\), then every global maximizer of \(P\) is a pure Nash equilibrium of \(G\).

## Proof

**Part (A).** Let \(P\) be a generalized ordinal potential for \(G\) and let \(s^{(0)}, s^{(1)}, \dots\) be any better-response path.

1. Each step \(s^{(k)} \to s^{(k+1)}\) is by definition a unilateral deviation by some player \(i_k\) with \(u_{i_k}(s^{(k+1)}) > u_{i_k}(s^{(k)})\).
2. By the GOP property applied to player \(i_k\) at profile \(s^{(k)}\), this strict payoff increase forces \(P(s^{(k+1)}) > P(s^{(k)})\). Hence \(P\) is **strictly increasing** along the path.
3. A strictly increasing sequence on the finite set \(P(S)\) cannot revisit any value; in particular it cannot revisit any profile. The path therefore visits each profile at most once, and \(|S| < \infty\) bounds its length by \(|S| - 1\).
4. So every better-response path is finite. Equivalently, \(G\) has the FIP.
5. Pick any starting profile \(s^{(0)}\) and run a maximal better-response path. By step 4 it must terminate at some profile \(s^*\). Termination means no improving unilateral deviation exists at \(s^*\); equivalently, \(s^*\) is a pure Nash equilibrium.
6. Hence \(G\) admits at least one pure Nash equilibrium. ∎

**Part (B).** Let \(P\) be an exact potential for \(G\) and let \(s^* \in S\) be a global maximizer of \(P\).

1. Fix any player \(i\) and any deviation \(s'_i \in S_i\). By definition of global maximizer, \(P(s'_i, s^*_{-i}) \le P(s^*)\).
2. By exactness, \(u_i(s'_i, s^*_{-i}) - u_i(s^*) = P(s'_i, s^*_{-i}) - P(s^*) \le 0\).
3. So no deviation by \(i\) strictly increases \(u_i\). Since \(i\) was arbitrary, \(s^*\) is a pure Nash equilibrium. ∎

The argument is purely deductive. See [proof_audit.md](proof_audit.md) under *Implementation regression checks* for the spot-checks confirming the GOP-detector, exact-potential detector, better-response simulator, and pure-NE detector implemented in [proof.py](proof.py) match the formal definitions used above.

## Corollaries

**Corollary 1.** *Every finite exact-potential game has a pure Nash equilibrium.*

*Sketch.* An exact potential is in particular a generalized ordinal potential (exactness implies GOP because matching differences match signs). Apply Theorem (A). Alternatively, take any global maximizer of the exact potential — it exists because \(S\) is finite and \(P\) is real-valued — and apply Theorem (B).

**Corollary 2.** *Every better-response path in a finite generalized-ordinal-potential game terminates after at most \(|S| - 1\) steps.*

*Sketch.* By step 3 of Part (A), \(P\) is strictly increasing along any better-response path, so no profile repeats; with \(|S|\) profiles available, the path's length is bounded by \(|S| - 1\).

**Corollary 3.** *In a finite exact-potential game, the set of global maximizers of \(P\) is a non-empty subset of the pure Nash equilibria.*

*Sketch.* Non-emptiness follows from finiteness of \(S\). Inclusion in the pure-NE set is exactly Theorem (B), which holds for every (not just one) global maximizer.

**Corollary 4.** *If \(G\) admits a generalized ordinal potential and the GOP is strict (different profiles get different \(P\) values), then \(G\) has a unique pure Nash equilibrium reachable from every starting profile via better-response dynamics.*

*Sketch.* By Part (A) every better-response path terminates. A strictly-valued GOP means the unique global maximum of \(P\) on \(S\) attracts every path: the path's \(P\)-value is strictly increasing and bounded above by \(\max_{s} P(s)\), so the path terminates exactly at the unique \(\arg\max\), which must be a pure NE.

## Scope

This proof does NOT establish:

- **The converse direction.** Whether FIP implies the existence of a generalized ordinal potential is the content of <!-- not-a-citation-start -->Monderer & Shapley (1996)<!-- not-a-citation-end --> Theorem 3.2 and is not addressed here.
- **Mixed-strategy equilibria.** Existence and characterization of mixed Nash equilibria (<!-- not-a-citation-start -->Nash 1950<!-- not-a-citation-end -->) are independent results not used in the deductive argument.
- **Infinite or continuous strategy spaces.** Step 3 of Part (A) uses finiteness of \(S\) essentially; for infinite \(S\) one needs additional structure (compactness, well-ordering, or topology-aware "weak" potentials) and the conclusion can fail.
- **Convergence rates.** The bound \(|S| - 1\) on path length is worst-case and uniform; sharper bounds depending on game structure are not derived.
- **Broader learning dynamics.** Best-response, fictitious play, no-regret learning, and other dynamics may converge under FIP but require their own analyses.
- **Computational complexity.** Computing a pure NE in an exact-potential game is PLS-complete in general; the existence proof here gives no efficient algorithm.

## Relation to prior work

Both theorems are due to <!-- not-a-citation-start -->Monderer & Shapley (1996), "Potential Games," *Games and Economic Behavior* 14(1), 124–143<!-- not-a-citation-end -->. Specifically:

- **Theorem (A)** is the forward direction of <!-- not-a-citation-start -->*Monderer & Shapley (1996)*<!-- not-a-citation-end -->, **Lemma 2.3** (FIP under generalized ordinal potential) combined with their **Lemma 2.5** (FIP implies existence of pure NE).
- **Theorem (B)** is <!-- not-a-citation-start -->*Monderer & Shapley (1996)*<!-- not-a-citation-end -->, **Lemma 4.2** specialized to global maximizers.

Rosenthal's earlier construction of an exact potential for finite congestion games <!-- not-a-citation-start -->Rosenthal (1973), "A Class of Games Possessing Pure-Strategy Nash Equilibria," *International Journal of Game Theory* 2(1), 65–67<!-- not-a-citation-end --> provides a canonical class of games to which both theorems apply.

The converse — FIP if and only if a generalized ordinal potential exists — is also in <!-- not-a-citation-start -->Monderer & Shapley (1996)<!-- not-a-citation-end -->, Theorem 3.2, and is not addressed here.

## What could challenge this verdict?

Four classes of objection were investigated; details and rebuttals appear in [proof_audit.md](proof_audit.md) under *Adversarial Checks*.

1. *Implicit reliance on finiteness.* Resolved: finiteness of the strategy space is the first hypothesis of the theorem, and step 3 of Part (A) uses it openly to bound path length by \(|S| - 1\).
2. *Equivalence of "every better-response path is finite" and FIP.* Resolved: these phrasings name the same property in <!-- not-a-citation-start -->Monderer & Shapley (1996), "Potential Games," *Games and Economic Behavior* 14(1), 124–143<!-- not-a-citation-end -->; both are stated to mirror the natural-language claim.
3. *Tie-breaking subtleties for global maximizers in Part (B).* Resolved: the argument uses only \(P(s'_i, s^*_{-i}) \le P(s^*)\); uniqueness of the maximizer is not required, and ties between maximizers all qualify as pure NE.
4. *Match between our formalization of GOP and the standard textbook definition.* Resolved: our definition (sign-of-payoff-change matched by sign-of-\(P\)-change for every unilateral deviation) coincides with the standard one; the proof uses only the one-directional implication "improving deviation strictly raises \(P\)," which is the load-bearing half.

## Conclusion

**PROVED.** Both Theorem (A) and Theorem (B) are established by the deductive argument above. The implementation regression checks in [proof_audit.md](proof_audit.md) confirm that the GOP-detector, exact-potential detector, better-response simulator, and pure-NE detector implemented in [proof.py](proof.py) agree with the formal definitions used in the argument; sampling cannot establish either theorem and is not framed as primary evidence.

The result is the foundational lemma underlying the theory of potential games <!-- not-a-citation-start -->Monderer & Shapley (1996), "Potential Games," *Games and Economic Behavior* 14(1), 124–143<!-- not-a-citation-end --> and applies in particular to every finite congestion game in the sense of <!-- not-a-citation-start -->Rosenthal (1973), "A Class of Games Possessing Pure-Strategy Nash Equilibria," *International Journal of Game Theory* 2(1), 65–67<!-- not-a-citation-end -->.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.33.2 on 2026-04-28.
