# Proof Narrative: AI progress in capabilities has largely plateaued since late 2024

## Verdict

**Verdict: DISPROVED**

The data tell a striking story: not only has AI progress not plateaued since late 2024, it has actually accelerated. The rate of capability improvement nearly doubled.

## What was claimed?

The claim is that AI models stopped getting meaningfully better sometime around late 2024 — that the rapid advances of prior years had run out of steam. This matters because it shapes decisions about whether to invest in AI, whether to rely on current tools, and whether the hype around AI progress is grounded in reality.

## What did we find?

The most direct evidence comes from Epoch AI, a nonprofit research organization that tracks AI model capabilities across 149 models and dozens of benchmarks. Their analysis found that the rate of progress on their composite capability index — which aggregates results from 42 different tests — grew nearly twice as fast after April 2024 as it did in the two years before. Specifically, improvement accelerated from roughly 8 points per year to roughly 15 points per year. That's not a plateau; that's an acceleration.

This finding holds up when you look at specific capability domains rather than composite scores. On SWE-bench Verified — a benchmark built from 500 real-world software engineering tasks pulled from actual GitHub repositories — top model scores reached 80.9% by late 2025 and continued rising. A year earlier, no model came close to that level.

The math domain shows an even more dramatic shift. FrontierMath, a benchmark of genuinely difficult mathematical problems, saw AI scores go from below 2% in November 2024 to nearly 48% by March 2026. That's more than a twentyfold improvement in sixteen months.

We also looked hard for evidence on the other side. The most prominent plateau argument comes from critics who point out that while benchmarks improve, practical usefulness hasn't kept pace. Notably, even Gary Marcus — a prominent AI skeptic — conceded that "2025 models perform better on benchmarks" while arguing that usefulness hasn't improved as much. That distinction matters: the claim under review is about capabilities, which benchmarks directly measure. Another commonly cited plateau argument, from Bill Gates, was made in 2023 — before the period in question.

## What should you keep in mind?

Benchmark progress and practical value are not the same thing. It's entirely possible for models to score higher on capability tests while users find the day-to-day improvement less dramatic. This proof addresses the capability question, not the usefulness question.

There's also the benchmark saturation issue: older tests like MMLU now score above 90%, so they can't show further progress even if it exists. The evidence here deliberately uses newer, harder benchmarks designed to resist saturation — but that choice itself reflects an active debate in the field about how to measure AI progress fairly.

The sources used here are credible but not universally authoritative. Epoch AI is widely cited in AI research and policy circles, but their benchmarking methodology involves choices that others might make differently. The composite index aggregates 42 tests, and which tests get included affects the result.

Finally, the partial verification of one source (the Epoch AI methodology page) means that piece of the picture rests on a fragment match rather than a confirmed full quote. That said, the core conclusion doesn't depend on it — three independently verified sources already meet the standard for disproof.

## How was this verified?

This narrative presents findings from a structured proof that checked multiple independent sources against a defined evidentiary threshold. You can read [the structured proof report](proof.md) for the full evidence table and logic, inspect [the full verification audit](proof_audit.md) for citation verification details and adversarial checks, or [re-run the proof yourself](proof.py) to reproduce the results from scratch.