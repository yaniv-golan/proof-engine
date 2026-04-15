# Proof Narrative: Automation Nash Equilibrium vs Cooperative Optimum

## Verdict

**Verdict: PROVED**

The mathematics checks out: firms acting in self-interest systematically over-automate compared to what would be collectively optimal, and the gap is exactly quantifiable.

## What was claimed?

Imagine a sector where several identical firms each decide how much of their workforce to replace with automation. Automation saves on labor costs, but there is a catch: displaced workers spend less, shrinking the very demand that all firms depend on. The claim lays out a precise mathematical model of this tension and asserts three specific formulas: one for how much firms automate when each acts independently (the Nash equilibrium), one for the collectively optimal automation level (the cooperative optimum), and a formula for the gap between them that is always strictly positive.

This matters because it formalizes a real economic intuition -- that individual firms ignore part of the social cost of automation, leading to more automation than is collectively efficient.

## What did we find?

We verified all three formulas using two independent methods.

First, symbolic algebra. Using SymPy, we set up each firm's profit function exactly as specified in the model, took derivatives, and solved the first-order conditions. For the Nash equilibrium, differentiating an individual firm's profit with respect to its automation rate and solving yields the claimed formula. A striking detail emerged: each firm's optimal rate does not depend on what other firms do -- it is a dominant strategy. The demand externality enters diluted by 1/N (the firm's market share), so each firm sees only a fraction of the demand destruction it causes.

For the cooperative optimum, maximizing total industry profit yields a different formula where the full demand externality appears undiluted. The difference between the two formulas simplifies to the claimed gap expression. In both cases, the algebraic residual was exactly zero -- not approximately zero, but symbolically zero.

Second, we verified the formulas numerically at concrete parameter values (five firms, specific wage and cost levels). The first-order conditions evaluated to exactly zero at the claimed equilibrium rates, and the gap computed by direct subtraction matched the formula precisely.

We also confirmed that the second-order conditions hold: both the individual and joint profit functions are strictly concave, meaning the first-order conditions do identify maxima, not minima.

## What should you keep in mind?

The formulas are interior solutions -- they assume the optimal automation rates fall between 0 and 1. For extreme parameter values (very low cost savings or very high friction), the unconstrained optimum could fall outside this range, and the actual solution would be a corner. The algebra is correct regardless; the practical applicability depends on parameter magnitudes.

The model assumes symmetric firms, equal market shares, linear demand, and quadratic friction costs. Real-world automation decisions involve richer dynamics (strategic interaction over time, heterogeneous firms, adjustment costs). The proof establishes the mathematical claim within the stated model, not a universal economic law.

The gap being positive is an algebraic certainty given the model's parameter restrictions (positive cost saving, positive demand feedback, at least two firms), not an empirical finding that could be overturned by data.

## How was this verified?

This claim was verified using the proof-engine framework, which requires every mathematical step to be executed by code rather than asserted by the AI. The symbolic derivations were performed by SymPy and independently cross-checked numerically. For the full formal breakdown, see [the structured proof report](proof.md). For verification details including computation traces and adversarial checks, see [the full verification audit](proof_audit.md). To reproduce the proof yourself, [re-run the proof script](proof.py) with Python and SymPy installed.
