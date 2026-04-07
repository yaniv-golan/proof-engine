# Proof Narrative: The Schwarzschild radius of the Sun calculated via rs = 2GM/c² with 2022 CODATA values for G, solar mass, and c lies strictly between 2.95 km and 2.96 km.

## Verdict

**Verdict: PROVED**

The Sun's Schwarzschild radius — the size it would need to be compressed to in order to become a black hole — comes out to 2.953 km, firmly inside the claimed range.

## What was claimed?

If you could somehow squeeze all of the Sun's mass into a sphere smaller than about 3 kilometers across, it would collapse into a black hole. The specific claim here is that when you compute this critical radius using the standard formula and the best available physical constants, the result falls strictly between 2.95 km and 2.96 km — not approximately, but precisely within that narrow 10-meter window.

This matters because the Schwarzschild radius is a foundational result in general relativity, and pinning it down to a specific numerical range requires using authoritative values for the gravitational constant, the speed of light, and the Sun's mass.

## What did we find?

The calculation centers on the formula rs = 2GM/c², where G is Newton's gravitational constant, M is the Sun's mass, and c is the speed of light. Using the 2022 CODATA recommended values from NIST — the international reference standard for physical constants — and the IAU 2015 nominal solar mass parameter, the result is 2.953250 km.

That single number settles the claim: 2.953250 is greater than 2.95 and less than 2.96, so both strict inequalities hold.

One subtle detail is worth noting. CODATA doesn't actually publish a standalone solar mass value. Instead, astronomers work with the gravitational parameter GM☉ — the product of G and the solar mass — which is measured far more precisely than either quantity alone. Using this combined value directly, G cancels out of the formula entirely, and the result is unchanged: 2.953250 km.

Two independent calculation paths were run: one decomposing the gravitational parameter into G and M separately, then recombining; the other using the gravitational parameter directly. Both returned identical results to ten significant figures. A third calculation using an independently published value from Wikipedia's solar mass article — a slightly more precise figure — agreed to within 50 nanometers of the primary result.

## What should you keep in mind?

The 10-meter window between 2.95 and 2.96 km is narrow, but the computed value of 2.9533 km sits comfortably near the middle, about 3 meters above the lower bound and 7 meters below the upper bound. The uncertainty in G, the least precisely known of the constants, can only shift the result by about 0.06 meters — a factor of 50 too small to threaten the claim.

Different time coordinate conventions used in astronomy (TCB, TDB, TCG) produce slightly different versions of the solar gravitational parameter. The differences appear only in the eighth significant digit, shifting the Schwarzschild radius by less than a millimeter. This has no effect on the result.

Popular sources like Wikipedia and NASA round the Sun's Schwarzschild radius to "approximately 3 km." That rounding is correct but hides the precision the claim is asserting. No authoritative source places the value outside the range 2.9–3.0 km, and all precise computations agree near 2.953 km.

## How was this verified?

This was verified by fetching the relevant physical constants live from NIST and IAU sources, running two independent calculations, and cross-checking against a third independently published value. See [the structured proof report](proof.md) for the full evidence summary and proof logic, [the full verification audit](proof_audit.md) for source credibility, extraction records, and adversarial checks, or [re-run the proof yourself](proof.py) to reproduce the computation from scratch.