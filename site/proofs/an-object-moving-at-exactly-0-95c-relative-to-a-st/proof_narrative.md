# Proof Narrative: An object moving at exactly 0.95c relative to a stationary observer experiences a Lorentz factor γ greater than 3.2.

## Verdict

**Verdict: PROVED**

The math checks out — and then some. Three independent methods all confirm the same result, with one of them requiring no approximation whatsoever.

## What was claimed?

Special relativity predicts that objects moving at high speeds experience time dilation, length contraction, and increased relativistic mass. The severity of these effects is captured by a single number called the Lorentz factor, denoted γ. The claim here is that an object traveling at 95% of the speed of light has a Lorentz factor greater than 3.2 — meaning relativistic effects are amplified by more than a factor of 3.2 relative to a stationary observer. This kind of threshold claim matters when people are checking whether a given speed pushes an object firmly into the "highly relativistic" regime.

## What did we find?

The Lorentz factor has a precise mathematical definition: γ = 1 divided by the square root of (1 minus the square of the speed ratio). With a speed ratio of exactly 0.95, the arithmetic is fully determined — there is no measurement uncertainty, no sampling, no modeling assumption. This is pure mathematics applied to a fixed input.

The primary calculation gives γ ≈ 3.2026. That is above 3.2 by about 0.0026 — a small margin, but the question is whether it is unambiguous.

To check, the same calculation was run a second time using 50-digit decimal arithmetic, a method with far more precision than standard floating-point. The result matched to every displayed digit.

The most rigorous check went further and bypassed square roots entirely. By expressing 0.95 as the fraction 19/20, the squared speed ratio becomes exactly 361/400, and therefore γ² equals exactly 400/39. The threshold 3.2 squared equals exactly 256/25. Comparing 400/39 against 256/25 using exact rational arithmetic — no approximation of any kind — confirms that γ² is strictly greater than (3.2)². Therefore γ is strictly greater than 3.2. This result is not an approximation; it is exact.

All three methods agree to more than ten decimal places. There is no conflict, no ambiguity, and no rounding issue that could overturn the conclusion.

## What should you keep in mind?

The margin above the threshold is real but modest — roughly 0.0026. Had the threshold been set at 3.203, the claim would be false. The claim is precisely true as stated, but it is not true by a large buffer.

The Lorentz factor computation assumes the speed is given as an exact value. In any physical experiment, measuring a speed to be exactly 0.95c is impossible — there will always be measurement uncertainty. This proof applies to the idealized mathematical case, not to any real moving object whose speed is only approximately known.

Nothing in this result should be taken to imply that the object "experiences" relativistic effects in a subjective sense — from the object's own reference frame, nothing unusual is happening. The Lorentz factor describes how things look from the stationary observer's perspective.

## How was this verified?

This claim was evaluated using the proof-engine verification framework, which applies a formal claim specification, computes results via multiple independent methods, and runs adversarial checks designed to find scenarios that could overturn the verdict. You can read [the structured proof report](proof.md) for a step-by-step breakdown of the logic, review [the full verification audit](proof_audit.md) for method details and adversarial analysis, or [re-run the proof yourself](proof.py) to reproduce every result from scratch.