# Proof Narrative: A venture capital fund investing $50 million in 25 startups at equal sizes requires at least one 50x return and two 10x returns to achieve a 3x gross multiple.

## Verdict

**Verdict: DISPROVED**

The math does not work: the scenario described in the claim returns only 2.8x, falling $10 million short of the 3x gross multiple it claims to achieve.

## What was claimed?

The claim states that a VC fund with $50 million invested equally across 25 startups needs at least one company to return 50 times its investment and two more to return 10 times their investment in order to achieve a 3x gross return for the whole fund. This kind of rule of thumb is common in venture capital education — the idea being that a fund needs one spectacular winner plus a few solid ones to return well. The question is whether the specific numbers actually add up.

## What did we find?

The arithmetic is straightforward. A $50 million fund split equally across 25 companies puts $2 million into each company.

Under the claimed scenario, the 50x winner returns 50 × $2M = $100 million. The two 10x companies each return $20 million, for a combined $40 million. Everyone else returns nothing. Total proceeds: $140 million.

A 3x gross multiple on a $50 million fund requires $150 million in total proceeds. The described portfolio produces only $140 million — a $10 million shortfall, or 0.2x below the claimed threshold.

Two independent methods confirmed this. The algebraic formula (1×50 + 2×10) × $2M gives $140M. Explicitly listing all 25 companies — one at $100M, two at $20M each, twenty-two at $0 — and summing them also gives $140M. Both methods agree exactly.

The counter-evidence checks made the picture even clearer. Not only does the described scenario fail to reach 3x, but 3x is achievable through many other routes that involve no 50x return at all: 15 companies each returning 5x yields $150 million (exactly 3x), and 5 companies each returning 15x does the same. The claim fails both as a sufficiency statement (the described scenario is not sufficient) and as a necessity statement (a 50x return is not necessary).

One adversarial check explored what happens if the fund has 20 companies instead of 25. With $2.5 million per company, the same 1×50x + 2×10x pattern returns $175 million — 3.5x gross. This highlights that the number of portfolio companies is the key variable: with 25 companies the per-company stake is too small to reach 3x with this particular return pattern.

## What should you keep in mind?

This proof addresses the arithmetic of the specific scenario as stated. It does not evaluate whether a 50x return is desirable, likely, or important to a fund's strategy — only whether the described combination of returns is mathematically sufficient for 3x. Real fund math also involves fees, carry, recycling, and partial exits, none of which are captured here. The proof assumes a simplified model: equal allocation, binary outcomes (full multiple or zero), and gross returns only.

The claim may have originated from a slightly different fund structure — for example, a smaller number of companies or different allocation sizes — where the numbers do work out. The 3x threshold is also sensitive to portfolio size: the same return pattern works for funds with ≤23 equal-size investments.

## How was this verified?

This is a pure mathematical proof with no external data sources — only arithmetic applied to the numbers stated in the claim. The proof script uses the proof-engine's `compare()` and `explain_calc()` functions from `scripts/computations.py` to perform and document each calculation, and includes a cross-check using an independent summation method. All steps are re-runnable.

Full details are available in [the structured proof report](proof.md), [the full verification audit](proof_audit.md), and you can [re-run the proof yourself](proof.py).
