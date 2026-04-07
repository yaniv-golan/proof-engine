# Proof Narrative: Current AI systems in 2026 have near-zero hallucinations and human-level reasoning across most domains.

## Verdict

**Verdict: DISPROVED**

The claim that today's AI systems hallucinate at near-zero rates and reason at human level across most domains is not supported by evidence — on both counts, the gap between the claim and reality is large.

## What was claimed?

The claim asserts two things about AI in 2026: that it rarely makes things up (near-zero hallucinations), and that it can reason as well as a human across most fields of knowledge. This kind of claim circulates widely in tech coverage and marketing, and it matters because people make real decisions — in medicine, law, education, and business — based on how much they trust AI outputs.

## What did we find?

Starting with hallucinations: as of 2026, AI systems still fabricate information at rates that are far from negligible. The Vectara Hallucination Leaderboard, which systematically measures how often AI models generate false information, found that Gemini-3-pro has a 13.6% hallucination rate — and that major frontier models including Claude Sonnet 4.5, GPT-5, GPT-OSS-120B, Grok-4, and DeepSeek-R1 all exceed 10%. That is not a rounding error around zero; it is one false statement in roughly every ten outputs.

Duke University Libraries reported in January 2026 that students continue to encounter hallucinations firsthand — plausible-sounding but factually wrong AI-generated content — as an ongoing, documented problem. OpenAI's own SimpleQA benchmark, designed specifically to test whether models know the limits of their knowledge, was published with the explicit expectation that it would remain relevant "for the next few generations of frontier models." The company building the leading AI systems does not expect the hallucination problem to be solved soon.

The reasoning picture is equally stark. ARC-AGI-3, launched in March 2026, offers a $2 million prize to any AI that can match the performance of untrained humans on novel abstract reasoning tasks. Every frontier model tested scored below 1%: the best result was 0.37%, against a human baseline of 100%. This is not a close miss — it is a 270-fold gap.

The ARC Prize 2025 competition, using the slightly less demanding ARC-AGI-2 benchmark, showed the best commercial AI reaching 37.6% — still less than half the human baseline. And on Humanity's Last Exam, a 2,500-question test spanning more than 100 academic disciplines, the leading models at the time of release scored between 2.7% and 8%. By early 2026, the best models had climbed to 34–38%, but expert humans score around 90%.

It is worth noting that AI does score at or above average human performance on some older benchmarks like MMLU and GSM8K. But those benchmarks are now considered saturated and likely contaminated by training data — models that score 97% on GSM8K score substantially lower on novel variants of the same problems, suggesting partial memorization rather than genuine reasoning.

## What should you keep in mind?

The picture is genuinely mixed, and nuance matters here. AI does perform impressively on some narrow tasks — certain coding problems, structured math questions, standardized test formats. The "near-zero" hallucination claim is not entirely invented: some models achieve sub-1% error rates on specific document-summarization tasks under ideal conditions. But those are best-case, task-specific results, not a general property.

The reasoning benchmarks that show large gaps — ARC-AGI-3, Humanity's Last Exam — are specifically designed to resist memorization and test novel problem-solving. It is possible that future models will perform better. The field is moving quickly. What the evidence establishes is that as of 2026, neither claim holds as a general description of current AI capability.

## How was this verified?

This verdict was reached by checking six independently sourced citations — three on hallucination rates, three on reasoning benchmarks — against a predefined threshold for what would constitute disproof. All six citations were verified live against their source pages. You can read the full evidence and reasoning in [the structured proof report](proof.md), examine the step-by-step verification log in [the full verification audit](proof_audit.md), or [re-run the proof yourself](proof.py).