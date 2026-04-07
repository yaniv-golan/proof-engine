# Proof Narrative: The viral expression "8 ÷ 2(2+2)" equals 1

## Verdict

**Verdict: DISPROVED**

The claim that this expression equals 1 is false under the standard mathematical convention used by calculators, programming languages, and modern curricula — the answer is 16.

## What was claimed?

The expression "8 ÷ 2(2+2)" went viral because people keep getting different answers — and both camps are convinced the other side failed basic math. The specific claim being evaluated here is that the correct answer is 1. If true, it would mean that most calculators and the convention taught in schools are wrong.

## What did we find?

Two well-established conventions exist for interpreting this expression, and they produce different answers. Under the dominant modern standard — the one implemented by Python, Wolfram Alpha, Texas Instruments calculators, Desmos, and the US Common Core curriculum — division and multiplication have equal precedence and are evaluated left to right. Applying that rule: resolve the parentheses first to get 4, then work left to right: 8 ÷ 2 = 4, then 4 × 4 = 16.

The answer of 1 comes from a different convention, where writing a number directly next to parentheses — as in "2(2+2)" — creates a tighter bond than explicit division. Under that reading, "2(2+2)" is treated as a single unit equal to 8, and the full expression becomes 8 ÷ 8 = 1. This convention does appear in some academic physics and mathematics writing, and Wikipedia documents it explicitly.

Two independent methods were used to verify the result under the standard convention. A manual step-by-step calculation and a Python evaluation of the equivalent expression both returned 16.0 exactly. No authoritative standards body — not ISO, ANSI, or NIST — mandates the juxtaposition-priority rule for general arithmetic. It is a legitimate but minority convention.

The expression itself is a deliberate trap. It was written without the parentheses that would make the intent unambiguous. Mathematical style guides from APA and AMS both recommend explicit parentheses precisely to avoid this kind of dispute. The "war" that erupts every time this goes viral isn't about anyone making arithmetic mistakes — it's about two groups applying different, incompatible conventions to the same poorly written expression.

## What should you keep in mind?

The juxtaposition-priority convention is not simply wrong. It is used in serious academic contexts, including some physics journals. If you learned math in an environment that treated implied multiplication as higher priority, you weren't taught incorrectly for that context. The problem is the expression itself, not the people arguing about it.

What this proof does not settle is which convention is "better" — that's a style question, not a mathematical one. It establishes only that under the convention implemented by the overwhelming majority of modern computational tools, the answer is 16, and the claim of 1 is therefore false by that standard. A clearly written version of either intended calculation would use parentheses: (8÷2)×(2+2) = 16, or 8÷(2×(2+2)) = 1.

## How was this verified?

This claim was evaluated by computing the expression under both competing conventions, independently verifying the dominant-convention result using Python's runtime evaluator, and checking whether any major standards body mandates the minority convention. Full details are in [the structured proof report](proof.md) and [the full verification audit](proof_audit.md), and you can [re-run the proof yourself](proof.py).