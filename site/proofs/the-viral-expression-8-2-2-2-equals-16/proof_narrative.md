# Proof Narrative: The viral expression "8 ÷ 2(2+2)" equals 16

## Verdict

**Verdict: PROVED**

Under standard order-of-operations rules, `8 ÷ 2(2+2)` equals 16 — but the real story is why this simple-looking expression has sparked so much genuine controversy.

## What was claimed?

The claim is that the viral math expression `8 ÷ 2(2+2)` has a definitive answer of 16. You've probably seen this or something like it circulate on social media, with comment sections splitting evenly between people insisting the answer is 16 and others equally certain it's 1. The question matters because it touches on something most of us were taught in school — order of operations — and yet reasonable, mathematically literate people land on different answers.

## What did we find?

Working through the expression step by step using standard PEMDAS/BODMAS rules — the order-of-operations system taught in most schools and used by Python, scientific calculators, and the international standard ISO 80000-2 — the answer is 16. You handle the parentheses first: `(2+2) = 4`. That gives you `8 ÷ 2 × 4`. Since division and multiplication have equal precedence, you work left to right: `8 ÷ 2 = 4`, then `4 × 4 = 16`.

Two independent cross-checks confirm this. One uses algebraic rearrangement: since dividing by 2 is the same as multiplying by one-half, you can rewrite the expression as `8 × 4 ÷ 2 = 32 ÷ 2 = 16` — a completely different computation path, same answer. The second cross-check runs the equivalent expression through Python's arithmetic engine, which also returns 16.

Here's where it gets genuinely interesting: there is a competing convention, and it isn't wrong. In some academic fields — particularly physics and as codified in American Mathematical Society house style — when a number is written directly against a parenthesis without an explicit multiplication sign (called *juxtaposition*), that implied multiplication binds more tightly than an explicit division symbol. Under that reading, `2(2+2)` is treated as a single unit, and the expression becomes `8 ÷ [2 × 4] = 8 ÷ 8 = 1`.

Both conventions are in real use. The viral controversy exists because the expression is genuinely ambiguous — not because one side is making a mistake.

## What should you keep in mind?

This proof establishes that 16 is correct *under the standard left-to-right PEMDAS convention* — not that 16 is the only defensible answer. If you encounter this expression in an academic physics paper or a context following AMS style, the intended answer may well be 1. No major international standard mandates the implicit-multiplication-first interpretation, but that doesn't make it fringe: it reflects a real and widely-used practice in technical writing.

The deeper lesson is that the expression itself is poorly written. Both `(8 ÷ 2)(2+2)` and `8 ÷ (2(2+2))` are unambiguous and immediately clear. The viral version is a notation trap, not a math puzzle.

## How was this verified?

This claim was evaluated by computing the expression using multiple independent methods, cross-checking results, and explicitly testing the strongest counterargument — the alternative convention — to see whether it undermines the proof. You can read [the structured proof report](proof.md) for a full walkthrough of the logic, inspect [the full verification audit](proof_audit.md) for computation traces and adversarial checks, or [re-run the proof yourself](proof.py) to reproduce every result from scratch.