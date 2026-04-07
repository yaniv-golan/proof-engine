# Proof Narrative: For any triangle with sides a, b, c where a^2 + b^2 = c^2, the angle opposite c is exactly 90 degrees, AND the converse also holds.

## Verdict

**Verdict: PROVED**

The Pythagorean theorem — one of the most famous results in all of mathematics — holds up completely under rigorous verification, in both directions.

## What was claimed?

The claim is that the Pythagorean relationship between a triangle's sides and its angles works both ways. Most people know the forward version: if a triangle has a right angle, then the square of the longest side equals the sum of the squares of the other two. But the claim goes further — if the sides of *any* triangle happen to satisfy that equation, then the triangle must have a right angle. No exceptions.

This matters because it means the equation a² + b² = c² is not just a consequence of having a right angle — it's a perfect test for one. Carpenters, surveyors, and anyone laying out a right angle in the physical world relies on this equivalence constantly.

## What did we find?

Both directions were proved using the Law of Cosines, a well-established theorem of Euclidean geometry that relates the sides of any triangle to one of its angles. The key insight is that when you substitute a² + b² = c² into this formula, the algebra forces the cosine of the opposite angle to equal zero. And within the valid range of interior angles for a triangle — anything strictly between 0 and 180 degrees — zero cosine means exactly one thing: a 90-degree angle. The forward direction is settled.

The converse is even more direct. If the angle is 90 degrees, then its cosine is zero, and the cosine term in the Law of Cosines simply drops out, leaving c² = a² + b². One substitution, and the result follows immediately.

To confirm these algebraic arguments weren't hiding any errors, two independent checks were run. First, 10,000 randomly generated triangles were tested in each direction — every single one behaved as predicted, with zero failures. Second, a computer algebra system independently simplified the same substitutions symbolically and confirmed both directions as true. Three completely different methods — algebra, numerical testing, and symbolic computation — all agree.

One subtle point worth noting: when computed numerically, cos(90°) isn't exactly zero due to how computers represent floating-point numbers — it comes out as roughly 6 × 10⁻¹⁷. This tiny artifact is a quirk of computer arithmetic, not a flaw in the mathematics. The algebraic proof is exact.

## What should you keep in mind?

This proof holds in Euclidean geometry — the flat geometry of everyday experience. In curved geometries (like the surface of a sphere or the geometry underlying general relativity), the Law of Cosines takes a different form, and the Pythagorean relationship no longer holds in general. The claim doesn't assert anything about those settings, and the proof is valid for its intended context.

The proof also implicitly requires a genuine triangle: sides must have positive length and satisfy the triangle inequality. A degenerate "triangle" where three points lie on a line doesn't qualify, and such cases don't satisfy a² + b² = c² anyway, so they don't create any counterexamples.

## How was this verified?

This claim was verified by decomposing it into two sub-claims, proving each algebraically via the Law of Cosines, and confirming both with independent numerical and symbolic cross-checks. Full details of the reasoning and evidence are in [the structured proof report](proof.md) and the step-by-step computation log is in [the full verification audit](proof_audit.md). To inspect or rerun the verification yourself, see [re-run the proof yourself](proof.py).