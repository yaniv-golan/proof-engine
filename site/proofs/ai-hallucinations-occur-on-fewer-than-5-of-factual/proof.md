# Proof: AI hallucinations occur on fewer than 5% of factual questions

- **Generated:** 2026-03-28
- **Verdict:** DISPROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

---

## Key Findings

- **GPT-4o hallucinates on 45.15% of factual questions** it attempts to answer on PreciseWikiQA — a standard short-fact benchmark — according to a 2025 ACL paper (B1, fully verified).
- **ChatGPT 3.5 hallucinates 69% of the time and Llama 2 hallucinates 88% of the time** when asked verifiable factual questions about federal court cases, per a Stanford/Princeton/NYU study (B2, fully verified).
- **LLaMA 2 and DeepSeek show 20–25% hallucination rates** on factual Q&A benchmarks, per a 2025 PMC survey (B3, fully verified).
- All three sources are from independent institutions, different benchmark designs, and separate domains. All three quotes verified live against their published URLs.

---

## Claim Interpretation

**Natural language claim:** "AI hallucinations occur on fewer than 5% of factual questions"

**Formal interpretation:**

| Field | Value |
|-------|-------|
| Subject | AI language models (mainstream LLMs: GPT-4/4o, Claude, Llama, etc.) |
| Property | Hallucination rate on factual question-answering benchmarks |
| Operator | `<` |
| Threshold | 5.0% |
| Direction | Disproof |

**Operator note:** The claim uses "AI" without qualification, which must be read as a universal statement about mainstream language models. The 5% threshold means fewer than 5 hallucinated answers per 100 factual questions. As a universal claim, a single well-documented counterexample — any mainstream AI system showing ≥5% hallucination on a standard factual Q&A benchmark — is sufficient to disprove it. This proof presents three independent such counterexamples.

Note: Summarization-task hallucination rates (e.g., the Vectara leaderboard) are excluded from this analysis because they measure a different phenomenon — whether a model introduces facts not present in a source document being summarized. That is fundamentally different from recalling factual knowledge in response to a direct question.

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|---------|
| B1 | HalluLens ACL 2025: GPT-4o hallucination rate on PreciseWikiQA factual Q&A | Yes |
| B2 | Large Legal Fictions (arxiv 2401.01301): LLM hallucination rate on legal factual questions | Yes |
| B3 | PMC survey (2025): LLaMA 2 and DeepSeek hallucination rates on factual Q&A | Yes |
| A1 | Count of independent sources confirming hallucination rates ≥5% | Computed: 3 confirmed sources (need ≥3) |

---

## Proof Logic

To disprove the claim that AI hallucinations occur on fewer than 5% of factual questions, the proof establishes three independent, verified counterexamples showing mainstream AI models with hallucination rates far exceeding 5%.

**Counterexample 1 — General factual Q&A (B1):** The HalluLens paper (ACL 2025) benchmarks leading AI models on PreciseWikiQA, described as designed to "assess the level of extrinsic hallucination in LLMs when responding to short, fact-based queries." GPT-4o — the top-performing model in the benchmark — achieves a 45.15% hallucination rate on questions it attempts to answer, with an overall correct-answer rate of 52.59% across all questions. Even the best-performing model in this benchmark hallucinates on nearly half of its attempted factual answers.

**Counterexample 2 — Legal domain factual Q&A (B2):** A study by researchers at Stanford, Princeton, and NYU tested three major language models (ChatGPT 3.5, Google's PaLM 2, and Meta's Llama 2) on 15,000 randomly sampled federal court cases. When asked "direct, verifiable question[s] about a randomly selected federal court case," these models hallucinated between 69% (ChatGPT 3.5) and 88% (Llama 2) of the time (B2). This is factual Q&A about a specific, verifiable real-world domain — the definition of the claim's scope.

**Counterexample 3 — Open-source models (B3):** A 2025 PMC-published survey of hallucinations in large language models documents that "LLaMA 2 and DeepSeek exhibited significantly higher factual hallucination rates around 20%–25%" on standard factual accuracy benchmarks (B3). This is approximately 4–5× the 5% threshold claimed.

Each counterexample alone suffices to disprove the universal claim. Together, they demonstrate the claim is false across general knowledge, legal, and open-source model domains.

---

## Counter-Evidence Search

Three adversarial questions were investigated before finalizing the verdict:

**1. Does GPT-4 specifically achieve <5% hallucination under some conditions?**

Yes — one study (PMC12518350) reports GPT-4 maintaining a hallucination rate below 5% under chain-of-thought prompting conditions on a specific benchmark. However, this does not rescue the universal claim for two reasons: (a) it applies only to GPT-4 under specific prompted conditions, not to "AI" broadly; (b) HalluLens shows GPT-4o at 45.15% on a different factual benchmark. The claim would need to be true for AI models generally; the existence of one model under one condition approaching 5% does not make a universal claim true.

**2. Does the Vectara summarization leaderboard show rates below 5%?**

Yes — the top-performing models on the Vectara leaderboard achieve 1.8%–3.3% hallucination on document summarization tasks. But the Vectara leaderboard measures whether a model *introduces facts not in the source document* when summarizing — a different and much easier task than recalling factual knowledge from training data. On actual factual Q&A benchmarks (SimpleQA, PreciseWikiQA, legal case queries), rates are far higher across all tested models.

**3. Could a narrow definition of "hallucination" make the <5% claim true?**

No — all three cited studies use standard, conservative definitions (incorrect factual answers, hallucinated case citations and holdings, factual accuracy benchmarks). No credible narrow definition reduces any of the cited rates below 5%.

None of the adversarial checks found evidence that breaks or qualifies the disproof.

---

## Conclusion

**Verdict: DISPROVED**

Three independent, fully verified academic sources document mainstream AI hallucination rates between 20% and 88% on factual question benchmarks — 4× to 17× above the claimed 5% threshold. All three citations were verified live against their published URLs with full quote matches. The claim is false as a universal statement about AI language models. A more accurate characterization is that hallucination rates vary widely by model, domain, and prompting strategy — ranging from roughly 20% for well-optimized models on general knowledge Q&A to over 80% for less capable models on specialized legal or scientific questions.

Note: No citations in this proof come from unclassified or low-credibility sources. B1 and B2 are both Tier 4 (arxiv.org academic), and B3 is Tier 5 (nih.gov government).

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
