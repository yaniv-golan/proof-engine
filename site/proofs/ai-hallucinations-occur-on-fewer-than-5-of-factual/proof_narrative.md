# Proof Narrative: AI hallucinations occur on fewer than 5% of factual questions

## Verdict

**Verdict: DISPROVED**

The data is unambiguous: AI models don't hallucinate occasionally — they do it routinely, at rates that dwarf the 5% ceiling this claim proposes.

## What was claimed?

The claim is that when you ask an AI a factual question, it will make something up less than 5% of the time. This is the kind of assurance that would matter if you were relying on AI for research, fact-checking, medical information, or anything where accuracy is important. If true, AI hallucination would be a rare edge case. As it turns out, it isn't.

## What did we find?

Three independent benchmarks, run by different organizations on different AI models, tell the same story: hallucination rates are not in the low single digits. They are measured in the tens of percent.

OpenAI's o3 — at the time of testing, described as the company's most powerful model — hallucinated 33% of the time on the PersonQA benchmark, which tests factual knowledge about people. That's one wrong answer in every three questions. Not a rounding error; not an edge case.

ChatGPT, tested independently by AllAboutAI across a broad range of queries, generated hallucinated content in approximately 19.5% of responses. Nearly one in five answers contained fabricated information.

Artificial Analysis took a different approach with their AA-Omniscience benchmark: 6,000 factual questions spanning 42 topics across six economically relevant domains. This is one of the most comprehensive factual QA benchmarks available. The best-performing model they tested still hallucinated 22% of the time.

These three sources are genuinely independent — different publishers, different models, different benchmark designs. They don't confirm each other because they copied each other; they converge because the underlying phenomenon is real and consistent.

One important clarification came out of the research: there is a category of AI task where sub-5% error rates do appear. When AI is asked to summarize a document it has in front of it — checking consistency with provided text — some models achieve under 1% error. But that is a fundamentally different task from answering open-ended factual questions from memory. The claim says "factual questions," which is the harder, more relevant case. There, every tested model falls far short of the 5% threshold.

## What should you keep in mind?

Hallucination rates vary considerably between models, benchmarks, and question types. A model that hallucinates 33% on one benchmark might perform differently on another. The rates cited here reflect specific testing conditions, and the field moves quickly — newer models may perform differently.

Systems augmented with retrieval tools (sometimes called RAG) can reduce hallucination substantially by grounding answers in retrieved documents rather than relying solely on the model's memory. The claim doesn't specify such systems, and base model rates are what the evidence addresses.

The sources used here are credible but not peer-reviewed academic journals. IEEE's Communications Society is a major professional engineering body; Artificial Analysis and AllAboutAI are established benchmarking platforms with publicly reproducible methods. None of the three sources disagrees with the others on the core picture.

What's perhaps most striking: even the *best* model on the most comprehensive benchmark still hallucinated more than one time in five. The 5% ceiling isn't close to being achieved under real-world factual QA conditions.

## How was this verified?

This narrative summarizes a structured proof that collected and independently verified three sources, each documenting hallucination rates well above 5% across different models and benchmarks. Full details of the evidence, source credibility assessments, and adversarial checks are in [the structured proof report](proof.md) and [the full verification audit](proof_audit.md). To inspect the methodology or reproduce the results, you can [re-run the proof yourself](proof.py).