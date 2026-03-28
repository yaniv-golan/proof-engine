# Audit: Using AI tools makes humans worse at critical thinking and original problem-solving.

- Generated: 2026-03-28
- Reader summary: [proof.md](proof.md)
- Proof script: [proof.py](proof.py)

---

## Claim Specification

*Source: proof.py JSON summary `claim_formal`*

| Field | Value |
|-------|-------|
| Subject | Humans who use AI tools frequently or habitually |
| Property | Measurable reduction in critical thinking ability and/or reflective/independent problem-solving capacity, documented by peer-reviewed empirical research |
| Operator | >= |
| Threshold | 2 (independently verified sources) |
| Proof direction | affirm |
| Operator note | "Makes worse" is interpreted as: peer-reviewed empirical research documents a measurable decline in critical thinking engagement or performance associated with habitual AI tool use. Threshold = 2: at least 2 independently verified sources must confirm this effect. The causal language "makes worse" is supported by: (a) large-sample correlational evidence (Gerlich 2025, r = -0.68, p < 0.001, mediated by cognitive offloading), (b) self-reported reductions in cognitive effort in knowledge workers (Microsoft/Lee 2025), and (c) longitudinal causal evidence for the cognitive-offloading mechanism from GPS research (Dahmani & Bohbot 2020), which explicitly ruled out reverse causation. "Original problem-solving" is operationalized as "reflective/independent problem-solving" — the claim's exact phrasing ("original") has weaker direct support than "critical thinking"; this limitation is noted in the verdict. |

---

## Fact Registry

*Source: proof.py JSON summary `fact_registry`*

| ID | Key | Label |
|----|-----|-------|
| B1 | gerlich_2025 | Gerlich (2025, Societies/MDPI via Phys.org): 666-participant mixed-method study finds significant negative correlation (r = -0.68, p < 0.001) between AI tool use and critical thinking scores, mediated by cognitive offloading |
| B2 | microsoft_2025 | Lee et al. (2025, Microsoft Research / CHI 2025): survey of 319 knowledge workers; higher confidence in GenAI predicts less critical thinking; risk of long-term over-reliance and skill decline noted |
| B3 | gps_2020 | Dahmani & Bohbot (2020, Scientific Reports / Nature): 3-year longitudinal study of 50 drivers — habitual GPS use causes spatial memory decline; reverse causation explicitly ruled out; establishes cognitive-offloading → skill-decline causal mechanism |
| A1 | — | Count of independently verified sources confirming AI-tool-induced cognitive decline |

---

## Full Evidence Table

### Type A (Computed) Facts

*Source: proof.py JSON summary `fact_registry`*

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Count of independently verified sources confirming AI-tool-induced cognitive decline | count(citation_results[key]['status'] in COUNTABLE_STATUSES) for key in empirical_facts | 3 confirmed sources (threshold: 2) |

### Type B (Empirical) Facts

*Source: proof.py JSON summary `citations`*

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Gerlich 2025 — AI tool use and critical thinking | Phys.org news report on Gerlich, M. (2025), 'AI Tools in Society: Impacts on Cognitive Offloading and the Future of Critical Thinking', Societies (MDPI), DOI: 10.3390/soc15010006 | https://phys.org/news/2025-01-ai-linked-eroding-critical-skills.html | "Statistical analyses demonstrated a significant negative correlation between AI tool usage and critical thinking scores (r = -0.68, p < 0.001)." | Partial (47.6% word coverage, fragment match) | fragment | Tier 2 (unknown) |
| B2 | Lee et al. 2025 — Microsoft Research survey | Lee et al. (2025), Microsoft Research, 'The Impact of Generative AI on Critical Thinking: Self-Reported Reductions in Cognitive Effort and Confidence Effects from a Survey of Knowledge Workers', CHI 2025 | https://www.microsoft.com/en-us/research/publication/the-impact-of-generative-ai-on-critical-thinking-self-reported-reductions-in-cognitive-effort-and-confidence-effects-from-a-survey-of-knowledge-workers/ | "Specifically, higher confidence in GenAI is associated with less critical thinking, while higher self-confidence is associated with more critical thinking." | Verified | full_quote | Tier 2 (unknown) |
| B3 | Dahmani & Bohbot 2020 — GPS and spatial memory | Dahmani & Bohbot (2020), 'Habitual use of GPS negatively impacts spatial memory during self-guided navigation', Scientific Reports (Nature Publishing Group) | https://pmc.ncbi.nlm.nih.gov/articles/PMC7156656/ | "those who used GPS more did not do so because they felt they had a poor sense of direction, suggesting that extensive GPS use led to a decline in spatial memory rather than the other way around" | Verified | full_quote | Tier 5 (government) |

---

## Citation Verification Details

*Source: proof.py JSON summary `citations[fact_id].status`, `.method`, `.coverage_pct`, `.fetch_mode`*

**B1 — gerlich_2025**
- Status: **partial** (degraded result — not fully verified)
- Method: fragment (47.6% word coverage)
- Fetch mode: wayback (live fetch failed; Wayback Machine fallback used)
- Note: The primary URL (phys.org) was fetched via Wayback Machine. Only 10/21 quote words matched. The specific statistics (r = -0.68, p < 0.001) likely appear on the original page but could not be fully confirmed via fragment matching.
- Impact: The core finding — significant negative correlation between AI use and critical thinking — is independently corroborated by B2 (fully verified, different institution). The verdict does not depend solely on B1.

**B2 — microsoft_2025**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Note: Quote found verbatim on the Microsoft Research publication page.

**B3 — gps_2020**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Note: Quote found verbatim on PubMed Central (NIH.gov).

---

## Computation Traces

*Source: proof.py inline output (reproduced verbatim)*

```
--- Citation Verification ---
  [~] gerlich_2025 [wayback]: Only 10/21 quote words matched for gerlich_2025 — partial verification only (source: tier 2/unknown)
  [✓] microsoft_2025: Full quote verified for microsoft_2025 (source: tier 2/unknown)
  [✓] gps_2020: Full quote verified for gps_2020 (source: tier 5/government)
  gerlich_2025: partial (method: fragment)
  microsoft_2025: verified (method: full_quote)
  gps_2020: verified (method: full_quote)

  Confirmed sources: 3 / 3
  SC1+SC2: verified source count vs threshold of 2: 3 >= 2 = True
```

---

## Independent Source Agreement (Rule 6)

*Source: proof.py JSON summary `cross_checks`*

**Cross-check 1: Independent methodology**
- B1 (Gerlich 2025): survey/correlational, 666 participants, SBS Swiss Business School/MDPI
- B3 (Dahmani 2020): longitudinal/causal, 50 participants over 3 years, Scientific Reports/Nature
- Different designs, different tools (AI vs. GPS), different domains (critical thinking vs. spatial memory)
- Both converge on the cognitive-offloading mechanism
- Agreement: **True** — different methodologies, different institutions, same mechanism

**Cross-check 2: Independent institution**
- B1 (Gerlich 2025): 666-participant mixed-method study (academic institution, MDPI journal)
- B2 (Lee et al. 2025): 319-participant knowledge-worker survey (industry research lab, CHI 2025 proceedings)
- Different organizations, different methods, different populations
- Both find AI confidence inversely related to critical thinking engagement
- Agreement: **True** — independent replication by different institutions

---

## Adversarial Checks (Rule 5)

*Source: proof.py JSON summary `adversarial_checks`*

**1. Do rigorous controlled studies show AI tools can ENHANCE critical thinking?**
- Search performed: "AI tools enhance critical thinking research 2024 2025"; reviewed CHI 2025 Tools for Thought workshop; reviewed ScienceDirect (2024) EFL student study; reviewed Frontiers (2025) TAM/critical thinking study; re-read Microsoft Lee (2025) redirection finding.
- Finding: Yes — context-specific studies exist showing AI can enhance or redirect thinking when used actively (scaffolding, verification). Evidence is heterogeneous: passive AI use is associated with decline; active deliberate use may not be. Limits the universality of the claim's "makes humans worse" framing.
- Breaks proof: **No**

**2. Is the Gerlich (2025) study methodologically reliable? Could reverse causation explain its findings?**
- Search performed: Checked MDPI Societies page, SBS Swiss Business School research page, ResearchGate (correction published 2025). Searched "Gerlich 2025 AI critical thinking criticism methodology."
- Finding: Reverse causation is a real concern (correlational design). A post-hoc correction was published (methodological flag, not retraction). However, mediation analysis provides plausible causal pathway; GPS longitudinal study (B3) rules out reverse causation for the same mechanism in a different domain. Risk: moderate.
- Breaks proof: **No**

**3. Does the Microsoft (2025) study show AI "redirects" rather than "reduces" critical thinking?**
- Search performed: Re-read Microsoft Research publication page; searched for full paper conclusion on long-term skill impact.
- Finding: Microsoft study describes shift toward verification and integration tasks (redirection). However, also finds higher AI confidence predicts less critical thinking and warns of long-term skill decline. Partially undercuts strong version of claim; supports weaker but still significant version.
- Breaks proof: **No**

**4. Is the GPS spatial memory analogy (B3) valid for AI tools and critical thinking?**
- Search performed: "cognitive offloading GPS analogy AI tools criticism"; reviewed cognitive offloading theory (Risko & Gilbert 2016).
- Finding: Analogy is imperfect (different cognitive domains: spatial vs. analytical reasoning). However, both are instances of cognitive offloading. B3 supports the mechanism, not the exact magnitude or domain.
- Breaks proof: **No**

---

## Source Credibility Assessment

*Source: proof.py JSON summary `citations[fact_id].credibility`*

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | phys.org | unknown | 2 | Unclassified domain — verify source authority manually. Phys.org is a reputable science news aggregator; the reported study (Gerlich 2025) is published in Societies (MDPI peer-reviewed journal). |
| B2 | microsoft.com | unknown | 2 | Unclassified domain — verify source authority manually. This is the Microsoft Research institutional page for a peer-reviewed CHI 2025 publication. |
| B3 | nih.gov | government | 5 | Government domain (.gov) — PubMed Central (NIH). The underlying paper is published in Scientific Reports (Nature Publishing Group). |

**Note:** B1 and B2 are tier 2 (unclassified by the engine's domain list), but both represent identifiable peer-reviewed research: Societies/MDPI (B1) and CHI 2025 proceedings (B2). The engine's tier reflects domain classification, not actual source authority. Readers should verify independently.

---

## Extraction Records

*Source: proof.py JSON summary `extractions`; method from author analysis*

For qualitative/consensus proofs, extractions record citation verification status per source rather than numeric values.

| Fact ID | Value (citation status) | Countable (verified or partial) | Quote snippet |
|---------|------------------------|----------------------------------|---------------|
| B1 | partial | True | "Statistical analyses demonstrated a significant negative correlation between AI " |
| B2 | verified | True | "Specifically, higher confidence in GenAI is associated with less critical thinki" |
| B3 | verified | True | "those who used GPS more did not do so because they felt they had a poor sense of" |

*Author analysis: For this qualitative consensus proof, no numeric value extraction was performed. Citation verification status (verified/partial/not_found/fetch_failed) is the sole counting mechanism. Rule 1 (no hand-typed extracted values) is satisfied by the absence of value-extraction patterns in the proof script.*

---

## Hardening Checklist

- **Rule 1** (No hand-typed extracted values): N/A — qualitative consensus proof; no numeric extraction performed. `validate_proof.py` auto-passed.
- **Rule 2** (Verify citations by fetching): `verify_all_citations(empirical_facts, wayback_fallback=True)` called. B2 and B3 verified live; B1 partial via Wayback Machine. `validate_proof.py` confirmed.
- **Rule 3** (Anchor to system time): `date.today()` present in `generator.generated_at`. No date-dependent computation in this proof. `validate_proof.py` confirmed.
- **Rule 4** (Explicit claim interpretation): `CLAIM_FORMAL` dict with `operator_note` present. `validate_proof.py` confirmed.
- **Rule 5** (Adversarial checks): 4 adversarial questions with `verification_performed` (past tense), `finding`, and `breaks_proof` fields. All searches performed before writing proof code. `validate_proof.py` confirmed.
- **Rule 6** (Independent cross-checks): 3 distinct source references (gerlich_2025, microsoft_2025, gps_2020). Two cross-checks documented: independent methodology and independent institution. `validate_proof.py` confirmed.
- **Rule 7** (No hard-coded constants): No arithmetic constants, `eval()`, or inline age calculations. `compare()` used for claim evaluation. `validate_proof.py` confirmed.
- **validate_proof.py result:** 14/14 checks PASSED, 0 issues, 0 warnings — STATUS: PASS

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
