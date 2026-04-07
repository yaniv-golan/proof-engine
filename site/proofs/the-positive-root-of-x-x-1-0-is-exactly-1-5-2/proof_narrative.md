# Proof Narrative: The positive root of x² - x - 1 = 0 is exactly (1 + √5)/2

## Verdict

**Verdict: PROVED**

This one is clean: the claim is exactly right, and the math confirms it two independent ways.

## What was claimed?

The equation x² - x - 1 = 0 has a specific positive solution, and the claim is that solution is precisely (1 + √5)/2 — the famous golden ratio, approximately 1.618. This comes up constantly in mathematics, art, and nature, so it's worth knowing whether the connection to this particular equation is genuinely exact or just an approximation.

## What did we find?

The golden ratio φ = (1 + √5)/2 satisfies x² - x - 1 = 0 exactly — not approximately, exactly. To see why, compute φ² directly: squaring (1 + √5)/2 gives (3 + √5)/2. Subtract φ and you get exactly 1. Subtract 1 more and you get 0. The irrational √5 terms cancel out perfectly, leaving integer arithmetic that resolves to zero without any rounding.

This was also confirmed the other way around: starting from the equation itself and applying the quadratic formula (x = (1 ± √5)/2), you get two roots. One is positive — (1 + √5)/2 ≈ 1.618 — and one is negative — (1 − √5)/2 ≈ −0.618. The positive root is φ, matching the claim exactly.

A natural question is whether there might be another positive root hiding somewhere. There isn't. A degree-2 polynomial has at most two roots total, and both roots here are fully accounted for: one positive, one negative. There's no room for a second positive root.

The proof also checked whether floating-point arithmetic might be creating a false impression of exactness. It doesn't — the symbolic computation uses only integer arithmetic on the rational and irrational parts separately, so the result is genuinely zero, not just very close to zero.

## What should you keep in mind?

This proof is about one specific equation: x² − x − 1 = 0. Slight variations — such as x² + x − 1 = 0 or x² − x + 1 = 0 — have different roots or no real roots at all. The golden ratio's connection to *this* equation is exact, but that doesn't extend automatically to other quadratics that look similar.

The numerical value φ ≈ 1.618 is an approximation. The claim, and the proof, are about the exact algebraic expression (1 + √5)/2. Those are not the same thing, and the proof is careful to keep them separate — the symbolic verification path never relies on decimal approximations.

## How was this verified?

This claim was verified using the proof-engine system, which checks mathematical claims through automated computation and adversarial testing. The full step-by-step derivation, including the symbolic arithmetic, is in [the structured proof report](proof.md). Every computation step and check is logged in [the full verification audit](proof_audit.md). You can reproduce the entire verification by running [re-run the proof yourself](proof.py).