# Proof Narrative: The theoretical vacuum energy density from quantum field theory exceeds the observed cosmological-constant value inferred from Type Ia supernovae by more than 10^120 orders of magnitude.

## Verdict

**Verdict: DISPROVED (with unverified citations)**

The claim gets the famous cosmological constant problem exactly backwards — not in spirit, but in the precise mathematical language it uses. The discrepancy it describes is real; the number used to quantify it is off by an almost unimaginable margin.

## What was claimed?

The claim asserts that the vacuum energy density predicted by quantum field theory is larger than what we actually observe in the universe — specifically, by "more than 10^120 orders of magnitude." This touches on one of the most celebrated puzzles in theoretical physics: why does empty space appear to weigh so little compared to what quantum theory predicts? The claim is the kind of striking factoid that circulates in popular science, and the underlying mismatch is very real and very dramatic. The question is whether the number attached to it is correct.

## What did we find?

Quantum field theory, when pushed to its natural limits at the Planck scale, predicts a vacuum energy density of roughly 2.93 × 10^111 joules per cubic meter. The observed value, inferred from Type Ia supernovae distances and confirmed by the Planck satellite's measurements of the cosmic microwave background, is roughly 5.36 × 10^-10 joules per cubic meter. Those two numbers could hardly be further apart.

Dividing the theoretical prediction by the observed value gives a ratio of about 5.5 × 10^120 — or, equivalently, a discrepancy of approximately 121 orders of magnitude. This was confirmed independently by repeating the calculation in different units (GeV^4 instead of SI), which gave 121.1 orders of magnitude — a difference of less than half a percent.

Here is where the claim goes wrong. "About 121 orders of magnitude" means the ratio is roughly 10^121. But the claim says the discrepancy is "more than 10^120 orders of magnitude." In standard mathematical usage, "N orders of magnitude" means a ratio of 10^N. So "10^120 orders of magnitude" would mean a ratio of 10^(10^120) — a number so astronomically large it has no physical meaning whatsoever.

The actual discrepancy of ~121 orders of magnitude is vastly smaller than 10^120 orders of magnitude — by about 118 orders of magnitude. No alternative calculation changes this conclusion. Using Lorentz-invariant regularization methods actually reduces the discrepancy to roughly 55–60 orders of magnitude. No known approach in the physics literature produces a discrepancy anywhere near 10^120 orders of magnitude.

The claim almost certainly intends to say that the ratio between the two densities is about 10^120 — which is accurate. The error is conflating "a ratio of 10^120" with "10^120 orders of magnitude." These are two very different things.

## What should you keep in mind?

The underlying cosmological constant problem is real, well-documented, and widely considered one of the deepest unsolved problems in physics. It is often called "the worst prediction in physics." But the precise magnitude of the discrepancy depends on which regularization scheme is used: the Planck-cutoff calculation gives ~120–122 orders of magnitude, while modern Lorentz-invariant approaches reduce it to ~55–60. The claim's phrasing — "10^120 orders of magnitude" rather than "120 orders of magnitude" — is a common error in popular science writing. One of the three supporting sources (CosmoVerse, a European research network) could not be fully classified by domain credibility, and one Wikipedia source was only partially verified due to Unicode formatting in the source HTML. Neither gap affects the conclusion, which follows from direct computation and is corroborated across multiple independent sources.

## How was this verified?

The observed vacuum energy density was drawn from multiple independent sources, while the theoretical prediction was computed directly from fundamental physical constants using the standard Planck-cutoff formula, then cross-checked in two different unit systems. Full details of every source, computation step, and adversarial check are available in [the structured proof report](proof.md) and [the full verification audit](proof_audit.md). To reproduce the calculation yourself, see [re-run the proof yourself](proof.py).