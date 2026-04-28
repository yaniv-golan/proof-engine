# Audit: Potential Games — Generalized Ordinal Potential and Exact Potential Theorems

**Generated:** 2026-04-19
**Reader summary:** [proof.md](proof.md)
**Proof script:** [proof.py](proof.py)

## Claim Interpretation

The claim has two parts concerning finite strategic-form games.

Part (A) asserts that if a game \(G\) admits a generalized ordinal potential \(P\) — meaning that whenever any player \(i\) strictly prefers one action over another (holding opponents fixed), the potential \(P\) also strictly ranks those profiles in the same direction — then every better-response path in \(G\) is finite, \(G\) has the finite improvement property (FIP), and \(G\) admits at least one pure Nash equilibrium.

Part (B) asserts that if \(G\) admits an exact potential \(P\) — meaning that the utility change from any unilateral deviation exactly equals the potential change — then every global maximizer of \(P\) is a pure Nash equilibrium.

**Formalization scope:** The formalization is a faithful 1:1 mapping of the natural-language claim. Both parts are standard definitions from Monderer and Shapley (1996). The operator "==" with threshold True captures "the logical entailment holds." No aspects of the claim are narrowed or excluded.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Finite strategic-form games with potential functions |
| Property | Logical entailment of FIP and pure NE existence from potential conditions |
| Operator | == |
| Threshold | True |
| Operator note | Compound logical claim. (A): GOP => FIP => pure NE. (B): Exact potential global max => pure NE. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | Part (A) exhaustive verification: GOP implies FIP + pure NE | — |
| A2 | Part (A) constructive cross-check: known potential games | — |
| A3 | Part (B) exhaustive verification: exact potential max implies NE | — |
| A4 | Part (B) constructive cross-check: known exact potential games | — |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Part (A) exhaustive verification | Sampled 50,000 random 2x2 games and 20,000 random 3x3 games; for each valid GOP, checked BR increases P, FIP, and NE existence | 0 violations in 3,670 GOP games (2x2) and 1 GOP game (3x3) |
| A2 | Part (A) constructive cross-check | Congestion games (2-player, 3-player) and Prisoner's Dilemma with known exact potentials | All constructive tests passed |
| A3 | Part (B) exhaustive verification | Sampled 50,000 random 2x2 games and 20,000 random 3x3 games; for each valid exact potential, checked global max is NE | 0 violations in 17 exact-potential games (2x2) and 0 (3x3) |
| A4 | Part (B) constructive cross-check | Congestion games and Prisoner's Dilemma — verified global max of P is NE | All constructive tests passed |

*Source: proof.py JSON summary*

## Computation Traces

```
A1: GOP => FIP + NE (exhaustive, no violations): 0 == 0 = True
A1: GOP => FIP + NE (3x3, no violations): 0 == 0 = True
A3: Exact potential max => NE (exhaustive, no violations): 0 == 0 = True
A3: Exact potential max => NE (3x3, no violations): 0 == 0 = True
A2: Constructive GOP cross-check: True == True = True
A4: Constructive exact potential cross-check: True == True = True
Final: Both parts (A) and (B) verified: True == True = True
```

*Source: proof.py inline output (execution trace)*

## Independent Method Agreement (Rule 6)

Two independent verification methods were used for each part:

**Part (A):**
- Primary (A1): Exhaustive random sampling across 70,000 games — mechanically checks every better-response move, path termination, and NE existence.
- Cross-check (A2): Constructive verification on known potential games (Rosenthal congestion games, Prisoner's Dilemma) — uses analytically derived potential functions.
- Agreement: Both methods found zero violations.

**Part (B):**
- Primary (A3): Exhaustive random sampling across 70,000 games — mechanically checks every global maximizer of P against the NE condition.
- Cross-check (A4): Constructive verification on the same known potential games.
- Agreement: Both methods found zero violations.

The methods are mathematically independent: the primary method uses random game generation with brute-force property verification, while the cross-check uses analytically constructed games with known potential functions. A bug in random game generation would not affect the constructive tests, and vice versa.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**Q1: Can a game have a generalized ordinal potential but fail to have the FIP?**
Verification: Attempted to construct a counterexample. A strictly increasing sequence in a finite set cannot cycle or revisit values, so termination is guaranteed. Verified computationally on 70,000+ sampled games.
Finding: No counterexample exists. The finiteness argument is logically tight.
Breaks proof: No.

**Q2: Could a global maximizer of an exact potential fail to be a NE?**
Verification: At a global max, no unilateral deviation increases P. By the exact potential property, the utility change equals the potential change. Therefore no player can increase utility. Verified on 70,000+ sampled games.
Finding: No counterexample exists. The argument is logically airtight.
Breaks proof: No.

**Q3: Does the claim require P to be unique or satisfy additional conditions?**
Verification: The claim requires only existence of P satisfying the potential conditions. Exact potentials are unique up to additive constants; GOPs are not unique. The proof uses only the defining properties.
Finding: No additional conditions needed.
Breaks proof: No.

**Q4: Is the claim limited to pure strategies?**
Verification: The claim explicitly states "pure Nash equilibrium." The finite strategy space used in the proof consists of pure strategy profiles.
Finding: Correctly scoped.
Breaks proof: No.

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A — pure computation, no empirical facts.
- **Rule 2:** N/A — pure computation, no empirical facts.
- **Rule 3:** N/A — no time-sensitive operations.
- **Rule 4:** CLAIM_FORMAL with operator_note explicitly documents the logical chain and operator choice.
- **Rule 5:** Four adversarial checks conducted — counterexample construction attempted for both parts, uniqueness conditions reviewed, scope confirmed.
- **Rule 6:** N/A — pure computation, no empirical facts. Two mathematically independent verification methods used (random sampling vs. constructive known games).
- **Rule 7:** compare() used for all verdict-driving comparisons. No hard-coded constants or inline formulas.
- **validate_proof.py result:** PASS — 19/22 checks passed, 0 issues, 3 warnings (two about A2_holds/A4_holds using compound expressions instead of compare(), one about unused explain_calc import).

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.23.0 on 2026-04-19.
