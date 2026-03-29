# Audit: AI hallucinations occur on fewer than 5% of factual questions

- **Generated:** 2026-03-29
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | AI language models (as a general class) |
| Property | hallucination rate on factual question benchmarks |
| Operator | >= |
| Threshold | 3 (verified disproof sources needed) |
| Proof direction | disprove |
| Operator note | To DISPROVE the claim that hallucinations occur on fewer than 5% of factual questions, we need >= 3 independent, verified sources showing hallucination rates >= 5% on factual question benchmarks. The claim is universal ('AI hallucinations') without specifying a particular model, so any major AI model demonstrating >= 5% hallucination on factual questions constitutes a counterexample. We focus on open-ended factual QA benchmarks like SimpleQA, PersonQA, and AA-Omniscience. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_ieee | IEEE ComSoc: OpenAI o3 hallucinated 33% on PersonQA |
| B2 | source_allaboutai | AllAboutAI: ChatGPT hallucinates in ~19.5% of responses |
| B3 | source_aa | Artificial Analysis: best model 22% hallucination on AA-Omniscience |
| A1 | — | Verified source count meets disproof threshold |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified source count meets disproof threshold | count(verified citations) = 3 | 3 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | OpenAI o3 hallucinated 33% on PersonQA | IEEE Communications Society Technology Blog | [link](https://techblog.comsoc.org/2025/05/10/nyt-ai-is-getting-smarter-but-hallucinations-are-getting-worse/) | "The company found that o3 — its most powerful system — hallucinated 33% of the time when running its PersonQA benchmark test" | verified | full_quote | Tier 2 (unknown) |
| B2 | ChatGPT hallucinates in ~19.5% of responses | AllAboutAI LLM Hallucination Test | [link](https://www.allaboutai.com/resources/llm-hallucination/) | "ChatGPT generates hallucinated content in approximately 19.5% of its responses" | verified | full_quote | Tier 2 (unknown) |
| B3 | Best model 22% hallucination on AA-Omniscience | Artificial Analysis AA-Omniscience Benchmark | [link](https://artificialanalysis.ai/evaluations/omniscience) | "Grok 4.20 Beta 0309 (Reasoning)" + data_values: best_model_hallucination_rate=22%, benchmark_questions=6,000 | verified | full_quote | Tier 2 (unknown) |

*Source: proof.py JSON summary*

## Citation Verification Details

### B1 — IEEE ComSoc (source_ieee)
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B2 — AllAboutAI (source_allaboutai)
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B3 — Artificial Analysis (source_aa)
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Data values verification:** best_model_hallucination_rate ("22%") found on page [live]; benchmark_questions ("6,000") found on page [live]

*Source: proof.py JSON summary*

## Computation Traces

```
verified disproof sources vs threshold: 3 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Aspect | Details |
|--------|---------|
| Sources consulted | 3 |
| Sources verified | 3 |
| source_ieee | verified |
| source_allaboutai | verified |
| source_aa | verified |
| Independence note | Sources are from different publications (IEEE ComSoc, AllAboutAI, Artificial Analysis) reporting on different benchmarks and models (PersonQA, ChatGPT testing, AA-Omniscience). Each measures hallucination rates independently. |

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

### Check 1: Can any model achieve < 5% on factual QA?
- **Verification performed:** Searched for 'AI model lowest hallucination rate factual questions 2025 2026'. Found that on Vectara's ORIGINAL summarization benchmark, some models achieve < 1% (Gemini-2.0-Flash at 0.7%). However, this measures grounded summarization (factual consistency with provided text), NOT open-ended factual question answering. On the Vectara NEW dataset (harder, more realistic), most frontier models exceed 10%. On AA-Omniscience (6,000 factual questions), the best model has 22% hallucination.
- **Finding:** Low hallucination rates (< 5%) exist only on narrow grounded summarization tasks, not on open-ended factual question benchmarks.
- **Breaks proof:** No

### Check 2: Could the claim hold under specific conditions?
- **Verification performed:** Searched for 'best AI model factual accuracy 2026 lowest error rate'. Some models with RAG can reduce hallucination rates significantly, but the claim says 'AI hallucinations' generically.
- **Finding:** Even with the most charitable interpretation, open-ended factual QA hallucination rates exceed 5%. RAG-augmented systems may achieve lower rates, but the claim does not specify RAG.
- **Breaks proof:** No

### Check 3: Are benchmarks measuring hallucination correctly?
- **Verification performed:** Searched for 'AI hallucination benchmark methodology criticism'. Found that hallucination measurement varies by benchmark. PersonQA and SimpleQA specifically test factual accuracy on verifiable questions.
- **Finding:** Benchmark methodology criticism exists but does not undermine our sources. All cited benchmarks measure factual accuracy on verifiable questions.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | comsoc.org | unknown | 2 | IEEE Communications Society — professional engineering society. Unclassified by automated tool but a well-known professional organization. |
| B2 | allaboutai.com | unknown | 2 | Established AI benchmarking and review platform. Unclassified by automated tool. |
| B3 | artificialanalysis.ai | unknown | 2 | Independent AI benchmarking platform. Unclassified by automated tool. |

Note: All 3 citations come from unclassified (tier 2) sources. IEEE ComSoc (comsoc.org) is the Communications Society of IEEE, a major professional engineering body. AllAboutAI and Artificial Analysis are established AI benchmarking platforms with publicly reproducible methodologies. The disproof does not depend solely on any single source — all three independently confirm hallucination rates well above 5%.

*Source: proof.py JSON summary + author analysis*

## Extraction Records

For this qualitative consensus disproof, extractions record citation verification status rather than numeric values:

| Fact ID | Value | Countable | Quote Snippet |
|---------|-------|-----------|---------------|
| B1 | verified | Yes | "The company found that o3 — its most powerful system — hallucinated 33% of the t..." |
| B2 | verified | Yes | "ChatGPT generates hallucinated content in approximately 19.5% of its responses" |
| B3 | verified | Yes | "Grok 4.20 Beta 0309 (Reasoning)" |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A — qualitative consensus proof, no numeric extraction from quotes
- **Rule 2:** All 3 citation URLs fetched live, quotes verified via `verify_all_citations()`. Data values for B3 verified via `verify_data_values()`.
- **Rule 3:** `date.today()` used for generated_at timestamp
- **Rule 4:** CLAIM_FORMAL includes operator_note explaining disproof threshold and interpretation of "factual questions"
- **Rule 5:** Three adversarial checks searched for counter-evidence: sub-5% models, specific conditions, benchmark methodology
- **Rule 6:** Three independent sources from different organizations reporting on different benchmarks
- **Rule 7:** `compare()` from computations.py used for threshold evaluation
- **validate_proof.py:** PASS with warnings (1 warning: no else branch in verdict assignment — cosmetic only)

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.1.0 on 2026-03-29.
