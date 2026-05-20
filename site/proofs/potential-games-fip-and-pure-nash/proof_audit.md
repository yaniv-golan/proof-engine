# Audit: Generalized ordinal potentials imply FIP and a pure NE; exact-potential maximizers are pure Nash equilibria

- Generated: 2026-04-28
- Reader summary: [proof.md](proof.md)
- Proof script: [proof.py](proof.py)

## Claim Interpretation

**Natural-language claim.** "Let G be a finite strategic-form game. (A) If G admits a generalized ordinal potential P, then every better-response path is finite, G has the finite improvement property, and G admits a pure Nash equilibrium. (B) If G admits an exact potential P, then every global maximizer of P is a pure Nash equilibrium."

**Formal interpretation.** A deductive theorem (`claim_type: "theorem"`) universally quantified over the unbounded class of finite strategic-form games. Part (A) is a four-conclusion implication under the hypothesis of a generalized ordinal potential (GOP); Part (B) is a one-conclusion implication under the hypothesis of an exact potential. We adopt the standard definitions of GOP, exact potential, better-response path, FIP, and pure Nash equilibrium given in <!-- not-a-citation-start -->Monderer & Shapley (1996), "Potential Games," *Games and Economic Behavior* 14(1), 124–143<!-- not-a-citation-end -->.

**Attribution.** `CLAIM_FORMAL.attribution` is set to the <!-- not-a-citation-start -->Monderer & Shapley (1996)<!-- not-a-citation-end --> reference. Both Theorem (A) and Theorem (B) are theorems of that paper — Theorem (A) follows their Lemmas 2.3 + 2.5, and Theorem (B) is their Lemma 4.2 specialized. This artifact is a verifiable companion to the published result, not a substitute for citing it. The mathematical authority is the cited source; this artifact contributes (1) a structured re-exposition of the argument with the canonical proof-engine section list, and (2) implementation regression checks that confirm code-side detectors agree with the formal definitions on a sampled-and-constructive test suite.

**Operator choice.** `operator: "holds"`. The claim is boolean — it asserts that two implications hold for every finite strategic-form game in their respective hypothesis classes. Numeric thresholds do not apply.

**Formalization scope.** This is a 1:1 mapping. We do not weaken "every" to "some," do not narrow "finite" to a particular class (e.g., 2-player or symmetric), and do not weaken "pure Nash equilibrium" to a refinement. Part (A) lists three conclusions ("every better-response path is finite," "FIP," "pure NE exists") that are not independent — the first two are textbook-equivalent statements of the same property — and we discharge each.

*Source: proof.py JSON summary `claim_formal` and `claim_natural`.*

## Claim Specification

| Field | Value |
|---|---|
| subject | finite strategic-form games admitting either a generalized ordinal potential (Part A) or an exact potential (Part B) |
| property | Part A: every better-response path is finite, the finite improvement property holds, and a pure Nash equilibrium exists. Part B: every global maximizer of the exact potential is a pure NE. |
| operator | holds |
| claim_type | theorem |

*Source: proof.py JSON summary `claim_formal`.*

## Fact Registry

| ID | Type | Label | Key |
|---|---|---|---|
| A1 | computed | GOP-detector regression spot-check (Part A) | — |
| A2 | computed | FIP / pure-NE termination regression (Part A) and exact-implies-GOP closure (Corollary 1) | — |
| A3 | computed | Exact-potential maximizer is pure NE regression (Part B) | — |

*Source: proof.py JSON summary `evidence`.*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|---|---|---|---|
| A1 | GOP-detector regression spot-check (Part A) | Implementation regression spot-check: 600 sampled random 2-player games plus a hand-constructed 2x2 GOP-only game, used to spot-check that the GOP-detector agrees with the formal definition. | True |
| A2 | FIP / pure-NE termination regression (Part A) and exact-implies-GOP closure (Corollary 1) | Implementation regression sanity check: 600 sampled random 2-player games plus the constructive coordination game (distinct from A1's GOP-only example), used to confirm better-response paths terminate as the deductive argument requires; also asserts the GOP-detector accepts the constructed exact potential, closing Corollary 1's "exact-implies-GOP" sketch. | True |
| A3 | Exact-potential maximizer is pure NE regression (Part B) | Implementation regression spot-check: 600 sampled random common-payoff 2-player games plus a constructive coordination game, used to spot-check that every global maximizer of the exact potential is a pure NE. | True |

*Source: proof.py JSON summary `evidence`.*

## Implementation Regression Checks

The deductive argument in [proof.md](proof.md) `## Proof` carries the verdict for both Theorem (A) and Theorem (B). The regression checks here spot-check the *code* in [proof.py](proof.py) that decides whether a given finite instance satisfies the formal hypotheses (GOP, exact potential, FIP, pure NE). Sampling cannot establish a "for all" claim; it can only catch implementation drift between detector code and formal definition.

**Constructive examples (deterministic).** Two 2x2 games are constructed in [proof.py](proof.py): a coordination game with an exact potential (Part B), and a GOP-but-not-exact game with asymmetric payoffs (Part A). For each, the corresponding detector (`has_exact_potential`, `has_generalized_ordinal_potential`) accepts the supplied potential, and `better_response_paths_terminate` reports termination from every starting profile. Every global maximizer of the exact potential in the coordination game is a pure NE.

**Random-sample sweep.** 600 random 2-player games (sampled via `random.Random` seed 20260428, integer payoffs uniform on \([-10, 10]\)) were used to exercise the GOP-detector and the better-response simulator. For each sampled game, a heuristic candidate GOP (sum of payoffs at each profile) was tested; when accepted by the detector, the better-response simulator was checked for termination. **0 disagreements** were observed across the sweep — every accepted candidate was truly a GOP under repeated detector application, and every better-response simulation terminated at a pure NE within \(|S| - 1\) steps.

**Exact-potential maximizer sweep.** 600 random common-payoff 2-player games (seed 20260429, integer payoffs uniform on \([-5, 5]\); both players share the same payoff function, which makes the common payoff an exact potential) were used to spot-check Part (B). For each sample, every global maximizer of the constructed exact potential was confirmed to be a pure NE. **0 disagreements** observed.

These regression checks have no bearing on the verdict beyond signaling implementation health. A regression failure would prompt human investigation of the code, not a re-evaluation of the theorem.

*Source: proof.py inline output (execution trace) and `evidence[A1..A3].method`.*

## Computation Traces

```
  theorem established by deductive argument: True
```

*Source: proof.py inline output (execution trace).*

## Adversarial Checks (Rule 5)

**Question 1.** Does the deductive argument silently rely on finiteness in a way the statement does not make explicit?

- *Verification performed.* Re-read the argument: termination of better-response paths uses strict monotonicity of \(P\) along edges plus finiteness of the profile set (no profile repeats; the strategy space is finite, hence paths cannot extend beyond \(|S|\) profiles). Both finiteness assumptions are explicit hypotheses of the theorem.
- *Finding.* The reliance on finiteness is explicit: "finite strategic-form game" is the first hypothesis. The argument fails for infinite strategy spaces (Part A's termination would require an additional well-ordering or compactness assumption).
- *Breaks proof.* No.

**Question 2.** Is "better-response path is finite" equivalent to FIP, or is there an asymmetry the proof glosses over?

- *Verification performed.* Cross-check the standard definition: FIP = every better-response improvement path terminates after finitely many steps. The two phrasings are textbook-equivalent in <!-- not-a-citation-start -->Monderer & Shapley (1996)<!-- not-a-citation-end -->; we keep both in the theorem statement to mirror the natural-language claim.
- *Finding.* No asymmetry. "Every better-response path is finite" and "FIP" name the same property; including both in the conclusion is a redundancy of phrasing, not of substance.
- *Breaks proof.* No.

**Question 3.** Could a global maximizer of an exact potential fail to be a pure NE because of a tie-breaking subtlety?

- *Verification performed.* Re-verified the Part B argument: at a global maximizer \(s^*\), no neighbor \(s'\) satisfies \(P(s') > P(s^*)\) by definition of maximizer; exactness gives \(u_i(s') - u_i(s^*) = P(s') - P(s^*) \le 0\) for every deviation by player \(i\). The argument uses \(\ge / \le\) at the max; it does not require uniqueness of the maximizer.
- *Finding.* No subtlety. Multiple global maximizers all qualify as pure NE, including ties — the regression sweep over the full argmax set confirms this for each sampled game.
- *Breaks proof.* No.

**Question 4.** Does the formalization of "generalized ordinal potential" match the standard textbook definition?

- *Verification performed.* Cross-checked our definition (sign of \(u_i\) payoff change matches sign of \(P\) change for every unilateral deviation) against <!-- not-a-citation-start -->Monderer & Shapley (1996)<!-- not-a-citation-end -->, Definition 2.4. The one-directional implication used in the proof — strictly improving deviations strictly raise \(P\) — is sufficient for termination and is what we encode in the detector.
- *Finding.* Definitions agree. The detector implements the same condition the deductive argument uses; the regression spot-checks below are consistent with this formalization.
- *Breaks proof.* No.

*Source: proof.py JSON summary `adversarial_checks`.*

## Quality Checks

- Rule 1: N/A — pure deductive proof, no empirical facts to extract values from.
- Rule 2: N/A — pure deductive proof, no citations to verify by HTTP fetch (prior-work attributions in proof.md are wrapped in non-citation HTML comments per Rule 9, since this proof has no empirical claims that require verification).
- Rule 3: N/A — claim is not time-sensitive; `is_time_sensitive` not declared, no `date.today()` used.
- Rule 4: PASS — `CLAIM_FORMAL.operator_note` documents the deductive structure and disclaims sampling as load-bearing.
- Rule 5: PASS — four adversarial checks targeting hidden finiteness assumptions, redundancy of FIP phrasing, tie-breaking at maximizers, and definition match against the standard reference.
- Rule 6: N/A — pure deductive proof, no empirical sources.
- Rule 7: PASS — `prove_holds` and `apply_verdict_qualifier` imported from `scripts.computations`; no inline formulas or eval().
- Rule 8: N/A — affirmative proof, no rejection threshold.
- Rule 9: PASS — prior-work attributions are wrapped in non-citation HTML comments to suppress the citation linter for prose-only mentions; no bare hand-typed author/year strings.
- Rule 10: PASS — `claim_type: "theorem"` declared; sampling tokens in `add_computed_fact` `method` strings are within ~80 characters of regression-role wording ("Implementation regression spot-check," "Implementation regression sanity check"); no sampling counts in proof.md body prose.
- validate_proof.py result: **PASS** — 17/17 checks passed, 0 issues, 0 warnings.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.33.2 on 2026-04-28.
