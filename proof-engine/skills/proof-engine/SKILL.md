---
name: proof-engine
description: >
  Create formal, verifiable proofs of claims by decomposing them into chains of
  individually verifiable facts connected by executable Python logic. Use this skill
  whenever someone asks to prove, verify, fact-check, or rigorously establish
  whether a claim is true or false — mathematical, empirical, or mixed. Trigger
  phrases include "is it really true that", "can you prove", "verify this",
  "I don't believe that", "show me the logic", "check this claim", "is this
  correct", "prove it", "fact-check this", or requests for rigorous argument.
  This skill produces machine-verifiable reasoning — every step is either
  computable or cited. Even for seemingly simple claims, use this skill if the
  user wants rigor. Do NOT use for persuasive essays, opinion pieces, philosophical
  arguments, creative writing, or questions with no verifiable answer.
metadata:
  author: Yaniv Golan
  version: 1.0.0
---

# Proof Engine

LLMs have two weaknesses that make them unreliable for factual claims: they hallucinate facts and they make reasoning errors. This skill overcomes both by offloading all verification to **code** and **citations**. The LLM never asserts a fact on its own authority. Every fact is either computed by Python code anyone can re-run (Type A) or backed by a specific source, URL, and exact quote (Type B).

The skill produces three outputs: a re-runnable `proof.py` script, a reader-facing `proof.md` summary, and a `proof_audit.md` with full verification details.

## Before Writing Any Proof Code

Read [Hardening Rules Reference](${CLAUDE_SKILL_DIR}/references/hardening-rules.md) — it contains the 7 rules with bad/good code examples for each. These rules close specific failure modes where proof code *looks* correct but is silently wrong.

## Bundled Scripts

Import these instead of re-implementing verification logic. They are tested and deterministic.

| Script | Purpose | Key functions |
|--------|---------|---------------|
| `${CLAUDE_SKILL_DIR}/scripts/extract_values.py` | Parse values FROM quote strings (Rule 1) | `parse_date_from_quote()`, `parse_number_from_quote()`, `parse_percentage_from_quote()`, `parse_range_from_quote()` |
| `${CLAUDE_SKILL_DIR}/scripts/smart_extract.py` | Unicode normalization + LLM-assisted extraction utilities | `normalize_unicode()`, `verify_extraction()`, `diagnose_mismatch()`, `ExtractionRecord` |
| `${CLAUDE_SKILL_DIR}/scripts/verify_citations.py` | Fetch URLs, verify quotes (live, snapshot, Wayback, PDF) (Rule 2) | `verify_citation()`, `verify_all_citations()` |
| `${CLAUDE_SKILL_DIR}/scripts/computations.py` | Verified constants, formulas, and self-documenting output (Rule 7) | `compute_age()`, `compare()`, `explain_calc()`, `cross_check()`, `compute_percentage_change()`, `DAYS_PER_GREGORIAN_YEAR` |
| `${CLAUDE_SKILL_DIR}/scripts/source_credibility.py` | Assess domain credibility from URL (offline, bundled data). **Note:** `verify_all_citations()` runs credibility assessment automatically — do NOT call `assess_all()` separately in proof scripts. Use `assess_credibility(url)` only for standalone CLI use. | `assess_credibility(url)`, `assess_all(empirical_facts)` |
| `${CLAUDE_SKILL_DIR}/scripts/validate_proof.py` | Static analysis for rule compliance (pre-flight) | `ProofValidator(filepath).validate()` |

To import these from a proof script, set `PROOF_ENGINE_ROOT` to the skill's install directory (the directory containing this SKILL.md and the `scripts/` subdirectory). In Claude Code, use the resolved value of `${CLAUDE_SKILL_DIR}`:
```python
import sys
PROOF_ENGINE_ROOT = "${CLAUDE_SKILL_DIR}"  # ← replaced with actual path at proof-writing time
sys.path.insert(0, PROOF_ENGINE_ROOT)
```

## Environment Requirements

Full Type B (empirical) verification requires **outbound HTTP access** from Python to fetch citation URLs. Without it, `verify_all_citations()` falls back through a chain: live fetch → embedded snapshot → Wayback Machine (if opted in).

**Workaround for sandboxed environments (ChatGPT, cloud containers):** During Step 2 (Gather Facts), fetch each source page using your browsing capability and include the page text as the `snapshot` field in `empirical_facts`. The proof script will verify quotes against these snapshots instead of live-fetching. The audit doc will show `fetch_mode: "snapshot"`.

**Verification fallback chain:**
1. **Live fetch** — try to fetch the URL directly. If successful, verify against live page.
2. **Snapshot** — if live fetch fails and a `snapshot` field is present, verify against the pre-fetched text. This is deterministic and user-provided.
3. **Wayback Machine** — if live and snapshot both fail and `wayback_fallback=True`, try the Wayback Machine archive. This is opt-in to avoid silently changing existing proof behavior.

**Fetch result statuses** (in the structured return dict):
- `verified` — quote found (full match or >=80% fragment coverage)
- `partial` — only a fragment matched (degraded verification)
- `not_found` — page fetched but quote not there (wrong quote or URL)
- `fetch_failed` — could not obtain page text by any method

**PDF citations:** When a URL returns a PDF, `verify_citation()` extracts text using `pdfplumber` or `PyPDF2` (optional dependencies). Install with `pip install pdfplumber` for PDF support.

Type A (pure math) proofs have no network requirements — they run entirely offline.

## Handling Paywalled Sources

Many scientific papers and reports are behind paywalls. When a key source returns 403 or requires authentication:

1. **Try the abstract URL** — PubMed (pubmed.ncbi.nlm.nih.gov), DOI resolver (doi.org), or Google Scholar often have abstracts with key findings. Cite the abstract URL instead.
2. **Check for open-access versions** — many papers have preprints on arXiv, bioRxiv, medRxiv, or the author's institutional page.
3. **Cite the abstract quote** — if the abstract contains the key finding, that's a valid citation. Note "cited from abstract; full text behind paywall" in the audit doc.
4. **Find alternative sources** — if the claim is well-established, there are usually multiple sources. Prefer open-access ones.
5. **Last resort** — if the paywalled source is essential and no alternative exists, cite it with whatever quote is publicly visible and mark as "Not verified (paywall)" in the audit doc. This does not invalidate the proof if other verified sources support the same finding.

**Government statistics sites (.gov):** BLS, FRED, Federal Reserve, Census, and similar .gov sites systematically return 403 to automated fetching. This is the norm, not the exception. For government statistics:
- Use the **snapshot workflow as the primary path** — fetch via browser during Step 2, embed as `snapshot` in `empirical_facts`
- Use reliable aggregators as citation URLs: rateinflation.com, inflationdata.com (for CPI); measuringworth.com (for historical data)
- Note in the audit doc that aggregator sources republish data from the primary authority (e.g., "sourced from BLS via rateinflation.com")

## Core Concepts

**Type A facts (Pure)**: Established entirely by code. The computation IS the verification. Use for math, logic, and derivations. Tools: `sympy` for symbolic math, plain Python for arithmetic.

**Type B facts (Empirical)**: Established by citation. Each MUST have: source name, working URL, exact quote. The citation IS the verification. Reputable sources only (peer-reviewed, government, established references).

**Every proof has three parts**: (1) Fact Registry — numbered facts tagged Type A or B, (2) Proof Logic — a self-contained Python script, (3) Verdict — one of the five levels below.

## The 7 Hardening Rules

| Rule | Closes failure mode | Enforced by |
|------|-------------------|-------------|
| 1. Never hand-type values | LLM misreads dates/numbers from quotes | `${CLAUDE_SKILL_DIR}/scripts/extract_values.py` |
| 2. Verify citations by fetching | Fabricated quotes/URLs | `${CLAUDE_SKILL_DIR}/scripts/verify_citations.py` |
| 3. Anchor to system time | LLM wrong about today's date | `date.today()` |
| 4. Explicit claim interpretation | Silent ambiguity in operators/terms | `CLAIM_FORMAL` dict with `operator_note` |
| 5. Independent adversarial check | Confirmation bias | Counter-evidence web searches |
| 6. Independent cross-checks | Shared-variable bugs in verification | Multiple sources parsed separately |
| 7. Never hard-code constants/formulas | LLM misremembers 365.25 vs 365.2425, eval() bugs | `${CLAUDE_SKILL_DIR}/scripts/computations.py` |

See [Hardening Rules Reference](${CLAUDE_SKILL_DIR}/references/hardening-rules.md) for detailed examples of each.

## Workflow

### Step 1: Analyze the Claim
Classify the claim: mathematical (Type A only), empirical (Type B only), or mixed. Identify ambiguous terms. Determine what would constitute proof AND disproof. If the claim has multiple parts (X AND Y, X BECAUSE Y), decompose into sub-claims — each gets its own entry in `sub_claims` with its own operator and threshold. Write a brief proof strategy and share it with the user before proceeding.

If the claim is an opinion, value judgment, or has no verifiable answer (e.g., "Python is the best language"), do NOT attempt a proof. Explain why, and offer to prove a related factual claim instead.

Before proceeding, assess whether a formal proof adds value. Consider these guiding questions:
- Does the claim have a crisp true/false threshold?
- Can the evidence be decomposed into a finite set of extractable facts?
- Are there canonical, publicly accessible sources?
- Is there a clear disproof condition (what would make it false)?
- Is the ambiguity surface manageable (few contested definitions)?
- Is this a scientific/literature consensus claim? If so, the standard is "multiple authoritative sources agree" rather than a single numeric threshold — see "Adapting for qualitative consensus proofs" in hardening-rules.md.

If fewer than 3 are true, consider whether a simpler factual summary would serve the user better than a full proof. If the user explicitly wants rigor, proceed anyway but note the limitations in the proof strategy.

### Step 2: Gather Facts (Both Directions)
Search for sources that SUPPORT the claim. Then search for sources that CONTRADICT it (adversarial — Rule 5). For empirical facts, find at least two independent sources (Rule 6). For math claims, identify the right tool (sympy, plain Python) and plan at least two mathematically independent approaches for cross-checking (Rule 6 — see "Interpreting independent for pure-math proofs" in hardening-rules.md).

When fetching source pages during research, save the page text for each citation. Include it as the `snapshot` field in `empirical_facts` so the proof is reproducible offline. This is especially important in sandboxed environments where Python cannot fetch URLs directly.

### Step 3: Write the Proof Code
Read [references/hardening-rules.md](${CLAUDE_SKILL_DIR}/references/hardening-rules.md) first. Start from the template at the bottom of that file. Import and use the bundled scripts. The proof script must be self-contained: `python proof.py` produces the full output.

Required structural elements in every proof script:
- `CLAIM_FORMAL` dict with `operator_note` (Rule 4). For compound claims, a `sub_claims` list with per-sub-claim evaluation and a `conjunction` type (AND/OR/BECAUSE/IMPLIES)
- For empirical proofs: `empirical_facts` dict with quotes but NO hand-typed values (Rule 1); imports from bundled scripts for verification (Rules 1, 2)
- For pure-math proofs: no `empirical_facts`, no citation/extraction imports. Use the **pure-math template** from hardening-rules.md
- `date.today()` for time-dependent proofs (Rule 3)
- `compare()` from `${CLAUDE_SKILL_DIR}/scripts/computations.py` — never hand-code formulas or well-known constants (Rule 7). Use `explain_calc()` for self-documenting output on scalar expressions; for aggregations over lists, use descriptive `print()` statements instead
- Adversarial checks section with `verification_performed` field (Rule 5) — web searches for empirical proofs, computations/structural analysis for pure math
- Cross-checks from independent sources (empirical) or mathematically independent methods (pure math) (Rule 6)
- `FACT_REGISTRY` dict mapping report IDs (B1, A1) to proof-script keys and labels
- JSON summary block in `__main__` with all structured fields (see hardening-rules.md template)
- `if __name__ == "__main__"` block with structured output ending in `=== PROOF SUMMARY (JSON) ===`

### Step 4: Validate Before Executing
Run `python ${CLAUDE_SKILL_DIR}/scripts/validate_proof.py proof_file.py` and fix any issues before proceeding. Note: validate_proof.py checks structural compliance with the hardening rules (imports, FACT_REGISTRY, JSON summary, etc.), not epistemic quality. Reasoning quality is assessed in the Step 6 self-critique checklist.

### Step 5: Execute and Report

Run the proof script, capture its output. The script produces two output streams:
1. **Inline output** — human-readable traces from bundled scripts (verify_citations, verify_extraction, explain_calc) that appear during execution
2. **JSON summary block** — a structured `=== PROOF SUMMARY (JSON) ===` block at the end containing all fields needed for report generation

Write three output files:

- **`proof.py`**: the proof script itself (re-runnable, with FACT_REGISTRY and JSON summary in `__main__`)
- **`proof.md`**: reader-facing summary (structure below)
- **`proof_audit.md`**: full verification details (structure below)

Use the JSON summary for populating structured sections (tables, fact IDs, verification statuses). Use the inline output for detailed traces (computation steps, citation verification messages).

#### proof.md structure

The reader-facing report. A reader who never opens proof_audit.md should fully understand the verdict and its justification.

Title line: `# Proof: [claim text]`

Header block:
- Generated: [date]
- Verdict: [VERDICT]
- Audit trail: link to proof_audit.md and proof.py

Section "Key Findings": 3-4 bullet points with the decisive numbers that justify the verdict. This is the executive summary — a reader who stops here should understand the result. Source: JSON summary `verdict` and `key_results`.

Section "Claim Interpretation": CLAIM_FORMAL in prose. State the natural-language claim, the formal interpretation, the operator choice with rationale. Expand acronyms on first use (e.g., "greenhouse gases (GHGs)"). Source: JSON summary `claim_formal` and `claim_natural`.

Section "Evidence Summary": Table with columns ID, Fact, Verified. IDs and labels from JSON summary `fact_registry`.
- Type A facts: Verified = "Computed"
- Type B facts: Verified = "Yes", "No", or "Partial" with brief reason for No/Partial (e.g., "No (URL returned 403)"). Derive from JSON summary `citations[fact_id].status`.
- Each source is its own fact row — no aggregation

Section "Proof Logic": Narrative explanation of the reasoning chain. Every key number must reference its fact ID inline, e.g., "Human activities account for ~95.5% of observed warming (B1, B3)." When multiple facts establish the same claim, note the redundancy: "Israel was founded on May 14, 1948 (B1, B2 — independently sourced)." Sub-claims get their own sub-sections if the proof has multiple parts. Source: author analysis.

Section "Counter-Evidence Search": Results of adversarial checks — what counter-evidence was searched for and what was found. Use plain language, not "Rule 5". Source: JSON summary `adversarial_checks`.

Section "Conclusion": Restate verdict with the key numbers. Verdict-specific:
- PROVED/DISPROVED: If any citations are not fully verified, state which conclusions depend on them and whether those conclusions are independently supported by verified sources.
- PROVED (with unverified citations): Same as PROVED, but explicitly list the unverified citations and their impact.
- PARTIALLY VERIFIED: List which sub-claims were proved and which remain unverifiable, with reasons.
- UNDETERMINED: State what specific evidence would be needed to resolve the claim.
- If any cited source has credibility tier ≤ 2 (unclassified or flagged), add a note: "Note: [N] citation(s) come from unclassified or low-credibility sources. See Source Credibility Assessment in the audit trail."
Source: JSON summary `verdict`, `key_results`, `citations[].credibility`; impact analysis is author analysis.

#### proof_audit.md structure

The verification-focused report. Contains everything a verifier needs to check the proof's machinery without running proof.py. For proofs with more than 10 citations, group evidence and citation details by sub-claim rather than listing all citations linearly.

Title line: `# Audit: [claim text]`

Header block:
- Generated: [date]
- Reader summary: link to proof.md
- Proof script: link to proof.py

Section "Claim Specification": CLAIM_FORMAL fields. Source: proof.py JSON summary `claim_formal`.

Section "Fact Registry": FACT_REGISTRY showing ID-to-key mapping. Source: proof.py JSON summary `fact_registry`.

Section "Full Evidence Table": Two sub-sections:

- "Type A (Computed) Facts" — table with columns: ID, Fact, Method, Result. All fields from JSON summary `fact_registry` entries where `method` and `result` are present. Source: proof.py JSON summary.
- "Type B (Empirical) Facts" — table with columns: ID, Fact, Source, URL, Quote, Status, Method, Credibility. One row per source. Source: proof.py JSON summary `citations` (which has normalized `status` and `method` fields — not free-form messages). The Credibility column shows "Tier N (type)" from `citations[fact_id].credibility`. For pure-math proofs, omit.

Section "Citation Verification Details": For each Type B citation, four fields — all from structured JSON fields, not parsed from prose:
- Status: verified / partial / not_found / fetch_failed. Source: JSON summary `citations[fact_id].status`.
- Method (only if verified or partial): full_quote / unicode_normalized / fragment / aggressive_normalization. Source: JSON summary `citations[fact_id].method` and `.coverage_pct`. Note: `coverage_pct` is null for full_quote and unicode_normalized methods — only populated for fragment matches. Partial (fragment match) is a degraded result — present it distinctly from full verification.
- Fetch mode: live / snapshot / wayback. Source: JSON summary `citations[fact_id].fetch_mode`. Indicates how the page was obtained.
- Impact (only if NOT verified): Which conclusions in proof.md depend on this citation, and whether they have independent support. Source: author analysis (label as such).
For pure-math proofs, omit this section.

Section "Computation Traces": The explain_calc() output showing symbolic expression, substituted values, and result for each computation step. Source: proof.py inline output (execution trace). This is the mechanical audit of all calculations — reproduce the explain_calc lines verbatim.

Section "Independent Source Agreement (Rule 6)": Cross-check details — which values were independently sourced, whether they agree, source-to-source comparisons. Source: proof.py JSON summary `cross_checks`. For pure-math proofs, omit.

Section "Adversarial Checks (Rule 5)": Full records with questions, searches performed, findings, and whether each breaks the proof. Source: proof.py JSON summary `adversarial_checks`.

Section "Source Credibility Assessment": Table with columns: Fact ID, Domain, Type, Tier, Note. Source: JSON summary `citations[fact_id].credibility`. If any source has tier ≤ 1 (flagged unreliable or satire), add a note explaining why it was cited and whether the claim depends solely on it. Tier scale: 5=government/intergovernmental, 4=academic/peer-reviewed, 3=major news or established reference, 2=unclassified, 1=flagged unreliable. For pure-math proofs, omit.

Section "Extraction Records": For each extracted value — fact ID, extracted value, whether value was found in quote. Source: JSON summary `extractions[fact_id]` (value, value_in_quote, quote_snippet). Plus: extraction method and normalization narrative. Source: author analysis (label as such). For pure-math proofs, omit.

Section "Hardening Checklist":
- Rule 1: Every empirical value parsed from quote text, not hand-typed
- Rule 2: Every citation URL fetched and quote checked
- Rule 3: System time used for date-dependent logic
- Rule 4: Claim interpretation explicit with operator rationale
- Rule 5: Adversarial checks searched for independent counter-evidence
- Rule 6: Cross-checks used independently sourced inputs
- Rule 7: Constants and formulas imported from computations.py, not hand-coded
- validate_proof.py result: [PASS/FAIL with details]

For pure-math proofs, mark Rules 1, 2, and 6 as "N/A — pure computation, no empirical facts."

#### Consistency rules

- Every fact ID in proof.md must appear in the JSON summary's `fact_registry` and in proof_audit.md's evidence table
- Verification statuses in proof.md must be derivable from JSON summary `citations[].status` (normalized field, not parsed from message)
- The verdict and key numbers must be identical across proof.md, proof_audit.md, and the JSON summary
- All Type A facts in proof_audit.md must have method/result from JSON summary `fact_registry` entries
- All extraction records in proof_audit.md must have value/value_in_quote from JSON summary `extractions`
- Sections labeled "Source: proof.py JSON summary" or "Source: proof.py inline output" must be traceable to actual proof.py output
- Sections labeled "Source: author analysis" must be clearly marked as such in proof_audit.md

### Step 6: Self-Critique Checklist

Before presenting results, verify:

Hardening rules (verify each in proof_audit.md):
- [ ] All 7 hardening rules checked in proof_audit.md hardening checklist
- [ ] validate_proof.py passes

Proof script contract:
- [ ] proof.py includes FACT_REGISTRY with IDs for all facts
- [ ] proof.py `__main__` emits `=== PROOF SUMMARY (JSON) ===` block
- [ ] JSON summary contains required keys: fact_registry (with method/result for A-types), claim_formal, adversarial_checks, verdict, key_results
- [ ] For empirical proofs: JSON summary also contains citations (with normalized status/method/coverage_pct/credibility), extractions (with value/value_in_quote/quote_snippet), cross_checks
- [ ] For pure-math proofs: omit citations and extractions keys entirely (do not include as empty dicts). cross_checks should contain computationally independent verification methods (see Rule 6 in hardening-rules.md for what "independent" means in a pure-math context). Use the pure-math template from hardening-rules.md.
- [ ] FACT_REGISTRY keys in JSON match IDs used in both report documents

Document consistency:
- [ ] proof.md has executive summary with key numbers directly under verdict
- [ ] Every fact ID in proof.md appears in JSON summary fact_registry and proof_audit.md evidence table
- [ ] proof.md verification statuses derivable from JSON summary `citations[].status` (not from message strings)
- [ ] proof.md conclusion addresses unverified/partially verified citations with impact analysis (if any)
- [ ] proof_audit.md sections labeled with provenance (proof.py JSON summary / proof.py inline output / author analysis)
- [ ] proof_audit.md includes Computation Traces reproduced from explain_calc inline output
- [ ] proof_audit.md presents "Partially verified" citations distinctly from "Verified"
- [ ] proof_audit.md includes Source Credibility Assessment table (for empirical proofs)
- [ ] proof.md conclusion notes low-credibility sources if any cited source has tier ≤ 2
- [ ] All three files are consistent with each other

## Verdicts

| Verdict | Meaning |
|---------|---------|
| **PROVED** | All facts verified, logic valid, conclusion follows |
| **PROVED (with unverified citations)** | Logic valid but some citation URLs couldn't be fetched |
| **DISPROVED** | Verified counterexample or contradiction found |
| **PARTIALLY VERIFIED** | Some sub-claims proved, others unverifiable |
| **UNDETERMINED** | Insufficient evidence either way |

## Edge Cases

**Vague claims** ("X is big"): Ask the user to specify a threshold, or state your interpretation in CLAIM_FORMAL and proceed.

**Opinions** ("X is the best"): Do not attempt a proof. Explain that "best" has no objective definition without criteria. Offer factual alternatives.

**Future knowledge** ("X will happen"): Mark as UNDETERMINED. Future events can't be verified.

**Trivially true/false** ("1 + 1 = 2"): Still produce a proof — it'll be short. The structure matters.

## Limitations

**Practical ceiling**: strong for crisp, auditable, bounded claims; weak for open-ended, normative, predictive, or research-grade claims. The key limit is not hard vs easy, but **formalizable vs fuzzy** — a claim works if it decomposes into a finite set of extractable facts and a clear rule for what counts as proof or disproof.

**Proof vs disproof asymmetry**: Disproof is often easier — a single counterexample or source contradiction suffices. Proof is harder when it needs exhaustive coverage, universal quantification, or strong source completeness.

**The engine struggles when proof or disproof needs**:
- Deep original mathematics beyond computation or sympy's symbolic capabilities
- Broad causal inference from messy evidence
- Competing definitions or legal/historical interpretation with no canonical standard
- Large literature synthesis where the answer depends on weighing many partially conflicting sources

**Technical limitations**:
- Citations are snapshots in time — web pages change
- URL fetching can fail due to network issues, paywalls, or bot protection
- Citation verification confirms quote presence on the page, not semantic entailment — a real quote may not actually support the claim. The adversarial cross-check (Rule 5) mitigates this but does not eliminate it
- Evidence behind images, videos, PDFs, or dynamic pages cannot be cited
- sympy has limits on certain symbolic computations
- This is rigorous verification, not peer review — it catches LLM errors but doesn't replace domain expertise

## Two-Phase Extraction (for complex quotes)

When `parse_number_from_quote()` or simple regex fails on real-world text (Unicode mismatches, special characters, unusual formatting), use the **two-phase extraction** pattern:

**Phase 1 (proof-writing time, LLM available):** Write a custom extraction function tailored to the specific quote. This function is literal Python code in the proof script — fully visible and auditable. It includes the quote it operates on, a normalization step for the specific Unicode quirks found, the extraction logic, and an assertion via `verify_extraction()`.

**Phase 2 (re-run time, no LLM needed):** The custom function runs as normal Python. It's self-contained. Anyone can read the code and see exactly how the value was extracted.

```python
from scripts.smart_extract import normalize_unicode, verify_extraction

def extract_ghg_warming_low(quote):
    '''Extract GHG low-end warming from NOAA page.
    The page uses en-dashes and ° symbols — normalize before extracting.'''
    normalized = normalize_unicode(quote)
    match = re.search(r'warming of ([\d.]+)', normalized)
    value = float(match.group(1))
    verify_extraction(value, quote, "ghg_warming_low")
    return value
```

Use `diagnose_mismatch(page_text, quote)` to understand WHY a quote fails verification, then write the custom extractor to handle those specific differences.

## Table-Sourced Numeric Data

For claims backed by HTML tables (CPI values, GDP figures, population data), the numeric values aren't in prose text that can be quoted. Use the `data_values` pattern:

```python
empirical_facts = {
    "source_a_cpi": {
        # Prose quote verifies source authority
        "quote": "The CPI for USA is calculated and issued by: U.S. Bureau of Labor Statistics",
        "url": "https://www.rateinflation.com/consumer-price-index/usa-historical-cpi/",
        "source_name": "RateInflation.com (sourced from BLS)",
        # Table values stored as strings — parsed via parse_number_from_quote()
        "data_values": {"cpi_1913": "9.883", "cpi_2024": "313.689"},
    },
}
```

- The `quote` field verifies the source's authority via `verify_all_citations()`
- Parse table values with `parse_number_from_quote(fact["data_values"]["cpi_1913"], r"([\d.]+)", "B1_cpi_1913")`
- Use `cross_check()` to compare values across independent sources
- The audit doc should distinguish "source authority verified via quote" from "numeric data extracted from table"

See hardening-rules.md "Citing structured/tabular data" for the full pattern.

## Gotchas

- **Don't inline verification logic**: Import the bundled scripts. Rewriting `normalize_text()` inline risks garbling the HTML-stripping logic.
- **Don't use `int()` truncation as a cross-check**: `int(days / 365.2425) == calendar_years` is not independent — both are functions of the same input.
- **Don't restate the proof as an adversarial check**: "70 years after 1948 is 2018, and 2026 > 2018" catches nothing. Search for counter-evidence.
- **Handle HTML in citations**: Government websites often use inline `<span>` tags. The bundled script handles this — but only if you use it.
- **Handle Unicode in citations**: Real web pages use en-dashes (–), curly quotes ('), ring-above (˚) vs degree (°), non-breaking spaces, etc. `verify_citations.py` automatically applies `normalize_unicode()` from `smart_extract.py`. For custom extraction, import and use `normalize_unicode()` explicitly.
- **Don't write print() descriptions of formulas**: Use `explain_calc("expr", locals())` instead. It AST-walks the expression and prints what the code actually does, not what you think it does. This closes the gap between computation and description.
