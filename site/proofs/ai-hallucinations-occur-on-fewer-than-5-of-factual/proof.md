# Proof: AI hallucinations occur on fewer than 5% of factual questions

- **Generated:** 2026-03-29
- **Verdict:** DISPROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Key Findings

- OpenAI's o3 model hallucinated **33% of the time** on the PersonQA benchmark (B1) — nearly 7x the claimed ceiling of 5%.
- ChatGPT generates hallucinated content in approximately **19.5% of its responses** across general testing (B2) — nearly 4x the claimed ceiling.
- On the AA-Omniscience benchmark (6,000 factual questions across 42 topics), even the **best-performing model hallucinates 22%** of the time (B3).
- No major AI model achieves < 5% hallucination on open-ended factual question benchmarks. Sub-5% rates exist only on narrow grounded summarization tasks, not factual QA.

## Claim Interpretation

**Natural language:** "AI hallucinations occur on fewer than 5% of factual questions"

**Formal interpretation:** The claim asserts that AI language models, as a general class, hallucinate on fewer than 5% of factual questions. The claim is universal — it says "AI hallucinations" without qualifying a specific model or benchmark. To disprove it, we require at least 3 independent, verified sources documenting hallucination rates at or above 5% on factual question benchmarks. We focus on open-ended factual QA benchmarks (SimpleQA, PersonQA, AA-Omniscience) rather than grounded summarization tasks, which test a different capability.

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | IEEE ComSoc: OpenAI o3 hallucinated 33% on PersonQA | Yes |
| B2 | AllAboutAI: ChatGPT hallucinates in ~19.5% of responses | Yes |
| B3 | Artificial Analysis: best model 22% hallucination on AA-Omniscience | Yes |
| A1 | Verified source count meets disproof threshold | Computed: 3 independent sources confirmed (threshold: 3) |

*Source: proof.py JSON summary*

## Proof Logic

Three independent sources, each reporting on different AI models and benchmarks, consistently show hallucination rates far exceeding the claimed 5% ceiling:

1. **PersonQA benchmark (B1):** IEEE ComSoc reports that OpenAI's o3 — described as its most powerful system — hallucinated 33% of the time on PersonQA, a benchmark testing factual knowledge about people. This is 6.6x the claimed maximum rate.

2. **General response testing (B2):** AllAboutAI's independent testing found that ChatGPT generates hallucinated content in approximately 19.5% of its responses, nearly 4x the claimed ceiling.

3. **AA-Omniscience benchmark (B3):** Artificial Analysis tested models on 6,000 factual questions across 42 topics in 6 economically relevant domains. The best-performing model (Grok 4.20 Beta) still hallucinated 22% of the time. This benchmark was specifically designed to measure "knowledge reliability and hallucination."

All three sources were independently verified via live URL fetching, and their quotes confirmed on the source pages. The sources report on different models (o3, ChatGPT, Grok), different benchmarks (PersonQA, general testing, AA-Omniscience), and different organizations (OpenAI/IEEE, AllAboutAI, Artificial Analysis) — establishing genuine independence (Rule 6).

With 3 verified sources (A1), the disproof threshold of 3 is met.

## Counter-Evidence Search

**Could any model achieve < 5% on factual QA?** On Vectara's original summarization benchmark, some models achieve < 1% (Gemini-2.0-Flash at 0.7%). However, summarization measures factual consistency with provided text — not open-ended factual question answering. On Vectara's newer, harder dataset, most frontier models exceed 10%.

**Could the claim hold under specific conditions?** RAG-augmented systems can reduce hallucination rates, but the claim says "AI hallucinations" generically without specifying RAG or any augmentation technique. Base model performance on factual QA consistently exceeds 5%.

**Are benchmarks measuring hallucination correctly?** Benchmark methodology varies, but PersonQA, SimpleQA, and AA-Omniscience specifically test factual accuracy on verifiable questions — directly matching the claim's scope of "factual questions."

*Source: author analysis*

## Conclusion

**DISPROVED.** The claim that AI hallucinations occur on fewer than 5% of factual questions is contradicted by overwhelming evidence from multiple independent benchmarks. Three verified sources document hallucination rates of 19.5% to 33% on factual question benchmarks — rates 4x to 7x higher than the claimed ceiling. Even the best-performing model on the most comprehensive factual QA benchmark (AA-Omniscience, 6,000 questions) hallucinates 22% of the time. Sub-5% hallucination rates exist only on narrow grounded summarization tasks, not on open-ended factual question answering.

Note: All 3 citations come from unclassified (tier 2) sources. IEEE ComSoc is a professional engineering society; AllAboutAI and Artificial Analysis are established AI benchmarking platforms. See Source Credibility Assessment in the audit trail.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.1.0 on 2026-03-29.
