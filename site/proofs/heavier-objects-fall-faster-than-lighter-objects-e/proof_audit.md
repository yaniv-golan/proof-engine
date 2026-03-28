# Audit: Heavier objects fall faster than lighter objects even in a perfect vacuum

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Objects of different mass in a perfect vacuum (no air resistance) |
| Property | Whether heavier objects have greater gravitational acceleration than lighter objects |
| Operator | >= |
| Threshold | 3 |
| Proof direction | disprove |
| Operator note | The claim asserts that heavier objects fall faster, meaning their acceleration due to gravity would be greater than that of lighter objects. We interpret 'fall faster' as 'have greater free-fall acceleration.' In Newtonian mechanics, F = mg and a = F/m = g, so acceleration is independent of mass. The claim requires a_heavy > a_light, but physics shows a_heavy == a_light == g. This is a disproof: we seek >= 3 authoritative sources confirming that all objects fall at the same rate in a vacuum regardless of mass. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| A1 | — | Newtonian derivation: acceleration = g, independent of mass |
| B1 | source_a | NASA Glenn: all objects free fall with same acceleration |
| B2 | source_b | NASA Science: Apollo 15 hammer-feather drop |
| B3 | source_c | Wikipedia: Weak Equivalence Principle |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Newtonian derivation: acceleration = g, independent of mass | Symbolic algebra (sympy): a = F/m = mg/m = g for any mass m | a1 == a2 == g (acceleration independent of mass) |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | NASA Glenn: all objects free fall with same acceleration | NASA Glenn Research Center | https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/free-fall-without-air-resistance/ | "So all objects, regardless of size or shape or weight, free fall with the same acceleration." | verified | full_quote | Tier 5 (government) |
| B2 | NASA Science: Apollo 15 hammer-feather drop | NASA Science | https://science.nasa.gov/resource/the-apollo-15-hammer-feather-drop/ | "Because they were essentially in a vacuum, there was no air resistance and the feather fell at the same rate as the hammer" | verified | full_quote | Tier 5 (government) |
| B3 | Wikipedia: Weak Equivalence Principle | Wikipedia: Equivalence Principle | https://en.wikipedia.org/wiki/Equivalence_principle | "in a gravitational field the acceleration of a test particle is independent of its properties, including its rest mass" | verified | full_quote | Tier 3 (reference) |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1 — NASA Glenn Research Center**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B2 — NASA Science**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B3 — Wikipedia: Equivalence Principle**
- Status: verified
- Method: full_quote
- Fetch mode: live

*Source: proof.py JSON summary*

## Computation Traces

```
=== TYPE A: Newtonian Derivation ===
  Object 1 (mass m1): F = m1*g, acceleration a1 = m1*g / m1 = g
  Object 2 (mass m2): F = m2*g, acceleration a2 = m2*g / m2 = g
  a1 == a2 == g: True
  Conclusion: acceleration is independent of mass; all objects fall at rate g.
  verified source count vs threshold: 3 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

Mathematical derivation (Type A) independently confirms empirical sources (Type B).

- **Math result:** a = g for all masses (sympy symbolic simplification)
- **Sources consulted:** 3
- **Sources verified:** 3
- **Source statuses:** source_a: verified, source_b: verified, source_c: verified
- **Independence note:** Type A derivation uses only Newton's laws (no external sources). Type B sources are from independent institutions: NASA Glenn Research Center, NASA Science (Apollo 15 mission data), and Wikipedia (summarizing Einstein's equivalence principle). The mathematical proof and empirical evidence are fully independent lines of reasoning.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**Q: Is there any credible scientific evidence that heavier objects fall faster in a vacuum?**
- Verification performed: Searched 'heavier objects fall faster vacuum gravitational attraction evidence'. All results (Physics Forums, NASA, University of Illinois, UCSB ScienceLine, Britannica) unanimously confirm objects fall at the same rate in a vacuum.
- Finding: No credible scientific source supports the claim. The only nuance found is the two-body problem: a heavier object attracts the Earth slightly more (reducing the distance faster), but this effect is negligible (~10^-25 for everyday objects) and does not contradict the equivalence principle. All standard physics references state that in a uniform gravitational field, acceleration is independent of mass.
- Breaks proof: No

**Q: Did Aristotle's theory (heavier objects fall faster) have any experimental support?**
- Verification performed: Searched 'Aristotle heavier objects fall faster disproved Galileo'. Aristotle's claim was based on everyday observation with air resistance, not vacuum conditions. Galileo's experiments (c. 1590) and the Apollo 15 demonstration (1971) definitively disproved it in vacuum conditions.
- Finding: Aristotle's theory was based on observations in air (where drag affects lighter objects more) and was never validated for vacuum conditions. It has been thoroughly disproved by experiment.
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | nasa.gov | government | 5 | Government domain (.gov) |
| B2 | nasa.gov | government | 5 | Government domain (.gov) |
| B3 | wikipedia.org | reference | 3 | Established reference source |

*Source: proof.py JSON summary*

## Extraction Records

| Fact ID | Value | Value in Quote | Quote Snippet |
|---------|-------|----------------|---------------|
| B1 | verified | Yes | "So all objects, regardless of size or shape or weight, free fall with the same a..." |
| B2 | verified | Yes | "Because they were essentially in a vacuum, there was no air resistance and the f..." |
| B3 | verified | Yes | "in a gravitational field the acceleration of a test particle is independent of i..." |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A — qualitative disproof with no numeric extraction
- **Rule 2:** All 3 citation URLs fetched and quotes verified (all full_quote matches)
- **Rule 3:** `date.today()` used in generator block
- **Rule 4:** CLAIM_FORMAL explicit with operator_note explaining interpretation of "fall faster" as "greater acceleration" and rationale for disproof direction
- **Rule 5:** Two adversarial checks searched for evidence supporting the claim; none found
- **Rule 6:** Three independent sources (NASA Glenn, NASA Science/Apollo 15, Wikipedia/Equivalence Principle) plus independent Type A mathematical derivation
- **Rule 7:** N/A — no constants or formulas requiring computations.py (sympy used for symbolic algebra)
- **validate_proof.py result:** PASS (15/15 checks passed, 0 issues, 0 warnings)

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
