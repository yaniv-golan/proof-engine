# Audit: AI hallucinations occur on fewer than 5% of factual questions

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | AI language models (mainstream LLMs) |
| Property | Hallucination rate on factual question-answering benchmarks |
| Operator | `<` |
| Threshold | 5.0% |
| Proof direction | disprove |
| Operator note | Universal claim — "AI" without qualification. Any mainstream LLM with ≥5% hallucination rate on a standard factual Q&A benchmark disproves it. Summarization-task rates (Vectara) excluded as they measure a different phenomenon. |

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | hallulens | HalluLens ACL 2025: GPT-4o hallucination rate on PreciseWikiQA factual Q&A |
| B2 | legal_fictions | Large Legal Fictions (arxiv 2401.01301): LLM hallucination rate on legal factual questions |
| B3 | pmc_survey | PMC survey (2025): LLaMA 2 and DeepSeek hallucination rates on factual Q&A |
| A1 | *(computed)* | Count of independent sources confirming hallucination rates ≥5% |

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Count of independent sources confirming hallucination rates ≥5% | count(citations with status in ('verified', 'partial')) | 3 confirmed sources (need ≥3) |

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | GPT-4o hallucination rate on PreciseWikiQA | HalluLens: LLM Hallucination Benchmark (ACL 2025, arxiv 2504.17550) | https://arxiv.org/html/2504.17550v1 | "GPT-4o, with a 45.15% hallucination rate when not refusing, maintains a much lower false refusal rate and achieves the highest correct answer scores (52.59%), indicating a trade-off between precision and recall." | verified | full_quote | Tier 4 (academic) |
| B2 | LLM hallucination rate on legal factual questions | Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models (arxiv 2401.01301) | https://arxiv.org/html/2401.01301v1 | "legal hallucinations are alarmingly prevalent, occurring between 69% of the time with ChatGPT 3.5 and 88% with Llama 2" | verified | full_quote | Tier 4 (academic) |
| B3 | LLaMA 2 and DeepSeek hallucination rates | PMC: Survey and analysis of hallucinations in large language models (2025, PMC12518350) | https://pmc.ncbi.nlm.nih.gov/articles/PMC12518350/ | "LLaMA 2 and DeepSeek exhibited significantly higher factual hallucination rates around 20%–25%" | verified | full_quote | Tier 5 (government) |

---

## Citation Verification Details

### B1 — HalluLens (arxiv 2504.17550)

- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Coverage:** N/A (full quote match)

### B2 — Large Legal Fictions (arxiv 2401.01301)

- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Coverage:** N/A (full quote match)

### B3 — PMC Survey (PMC12518350)

- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Coverage:** N/A (full quote match)

---

## Computation Traces

```
confirmed disproof sources vs threshold of 3: 3 >= 5.0 = False
confirmed disproof sources (need ≥3 to establish disproof): 3 >= 3 = True
```

*Note: The first compare() call (3 >= 5.0) uses the claim's numeric threshold (5%) applied to source count — it is superseded by the second call which correctly uses the disproof source threshold of 3. The second call drives the verdict.*

---

## Independent Source Agreement (Rule 6)

| Description | Sources consulted | Sources verified | Agreement |
|-------------|-------------------|-----------------|-----------|
| Three independent research groups, separate benchmarks, separate domains | 3 | 3 | All verified |

**Independence note:**
- B1: AI/NLP researchers (HalluLens, ACL 2025) — general factual Q&A benchmark
- B2: Legal AI researchers (Stanford/Princeton/NYU, arxiv 2401.01301) — legal domain Q&A
- B3: PMC survey authors (2025) — open-source model evaluation

Different institutions, different benchmark designs, different domains. Each independently confirms hallucination rates far above 5%.

---

## Adversarial Checks (Rule 5)

### Check 1: Does GPT-4 achieve <5% hallucination on some benchmarks?

- **Question:** Does GPT-4 specifically achieve hallucination rates below 5% on any factual benchmark, potentially making the claim true for the best models?
- **Search performed:** Searched for GPT-4 hallucination rate studies. Found PMC12518350 which reports "GPT-4 achieved near-perfect factual accuracy, maintaining a hallucination rate below 5%" in one study. However: (1) this is under chain-of-thought prompting conditions; (2) it applies to GPT-4 specifically, not "AI" in general; (3) HalluLens (ACL 2025) shows GPT-4o at 45.15% on PreciseWikiQA — a different benchmark.
- **Finding:** GPT-4 may approach <5% under optimal conditions on some benchmarks. This does not save the universal claim: LLaMA 2, DeepSeek, ChatGPT 3.5, GPT-4o on other benchmarks, and all models on legal/medical domain questions all show rates far above 5%. The claim as stated is false for "AI" broadly.
- **Breaks proof:** No

### Check 2: Vectara summarization leaderboard shows some models below 5%

- **Question:** Does the Vectara summarization leaderboard show models below 5%, suggesting the claim could be true for some AI systems?
- **Search performed:** Reviewed Vectara hallucination leaderboard (github.com/vectara/hallucination-leaderboard). Top-performing models show 1.8%–3.3% hallucination on document summarization tasks. However, the Vectara leaderboard measures whether a model introduces facts not present in a source document when summarizing — NOT factual Q&A hallucination.
- **Finding:** Summarization-fidelity rates (Vectara) are not comparable to factual Q&A hallucination rates. On actual factual question benchmarks (SimpleQA, PreciseWikiQA, legal/medical domain tests), rates are far above 5% across all tested models.
- **Breaks proof:** No

### Check 3: Narrow definition of "hallucination"

- **Question:** Could "hallucination" be defined narrowly enough (e.g., only fabricated citations, not factual errors) to make the <5% claim true?
- **Search performed:** Reviewed definitions across the three cited papers. HalluLens defines hallucination as "incorrect answers when the model does not refuse to answer" on fact-based queries. The legal study counts hallucinated case citations and holdings. The PMC survey uses standard factual accuracy benchmarks. All three use well-established, conservative definitions.
- **Finding:** Narrow definitions do not rescue the claim. All studies use standard, conservative hallucination definitions, and rates remain far above 5% under any reasonable definition.
- **Breaks proof:** No

---

## Source Credibility Assessment

| ID | Domain | Tier | Type | Notes |
|----|--------|------|------|-------|
| B1 | arxiv.org | 4 | Academic | Known academic/scholarly publisher |
| B2 | arxiv.org | 4 | Academic | Known academic/scholarly publisher |
| B3 | nih.gov | 5 | Government | Government domain (.gov) |

All sources are Tier 4 or higher. No low-credibility sources were used.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
