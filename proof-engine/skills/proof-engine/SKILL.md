---
name: proof-engine
description: >
  Create formal, verifiable proofs of claims with machine-checkable reasoning.
  Use when asked to prove, verify, fact-check, or rigorously establish whether
  a claim is true or false — mathematical, empirical, or mixed. Trigger phrases:
  "is it really true", "can you prove", "verify this", "fact-check this",
  "prove it", "show me the logic". Do NOT use for opinions, essays, or
  questions with no verifiable answer.
metadata:
  author: Yaniv Golan
  version: "1.1.0"
  license: MIT
compatibility: >
  Requires Python 3 and requests library. Optional: pdfplumber (PDF citations),
  sympy (symbolic math). Outbound HTTP needed for Type B (empirical) proofs.
  Works on Claude Code, ChatGPT, Cursor, and other AI coding environments.
---

# Proof Engine

LLMs hallucinate facts and make reasoning errors. This skill overcomes both by offloading all verification to **code** and **citations**. Every fact is either computed by Python code anyone can re-run (Type A) or backed by a specific source, URL, and exact quote (Type B).

Produces three outputs: a re-runnable `proof.py` script, a reader-facing `proof.md`, and a `proof_audit.md` with full verification details.

## Gotchas

These are the highest-value lessons from field testing. Read before writing any proof code.

- **Don't inline verification logic**: Import the bundled scripts. Rewriting `normalize_text()` inline risks garbling the HTML-stripping logic.
- **Don't use `int()` truncation as a cross-check**: `int(days / 365.2425) == calendar_years` is not independent — both are functions of the same input.
- **Don't restate the proof as an adversarial check**: "70 years after 1948 is 2018, and 2026 > 2018" catches nothing. Search for counter-evidence.
- **Handle Unicode in citations**: Real web pages use en-dashes, curly quotes, ring-above vs degree, non-breaking spaces. `verify_citations.py` handles this automatically.
- **WebFetch paraphrases quotes** — Quotes from WebFetch may be silently altered. You cannot pre-verify them (WebFetch is the intermediary). Instead: (1) write the quote as-is, (2) run `verify_all_citations`, (3) if a quote returns `partial` or `not_found`, re-fetch the page asking for the exact sentence around a distinctive keyword, (4) update the quote and re-verify. For qualitative proofs where exact quotes matter less, prefer shorter distinctive phrases that are less likely to be paraphrased. A `partial` result with `coverage_pct >= 50` is acceptable if other fully-verified sources independently confirm the same point — the engine's own threshold for `verified` via fragment matching is `coverage >= 0.8` (80%), so anything below that returns `partial`.
- **`explain_calc()` vs `compute_*()`**: Use named functions (`compute_percentage_change()`, `compute_age()`) when they match your computation — they self-document. Use `explain_calc()` for ad-hoc expressions. Don't wrap a `compute_*()` call in `explain_calc()`.
- **Don't call `verify_extraction()` on data_values**: It's circular. Instead, call `verify_data_values(url, data_values, fact_id)` to confirm each value string appears on the source page, then cross-check across sources (Rule 6).
- **Never create pseudo-quote fields for table data**: Don't store table cell values in fields like `cpi_1913_quote: "9.883"`. If the source evidence is a table cell or numeric grid, store it under `data_values` and verify with `verify_data_values()`. The validator will reject pseudo-quote fields containing bare numeric or date literals that are parsed as evidence.
- **Handle `verify_data_values()` failures**: If `verify_data_values()` returns `found: false` for a source (common with JS-rendered pages), do not use that source's `data_values` as the primary computation input. Use a verified source as primary, and note the unverified source's data as corroborating only. If both sources fail verification, search for a third source with static HTML. A cross-check between two unverified `data_values` sources is circular — it compares your authored strings against each other.
- **Index base mismatches**: Economic data from different aggregators may use different base periods. If `cross_check()` flags a large disagreement, check whether sources use different scaling. Document the base period in source_name.
- **Dynamic/JS-rendered sites**: Many aggregators (officialdata.org, in2013dollars.com, inflationdata.com) render page chrome via JavaScript. Live fetch gets raw HTML — data tables may be static but page titles, headings, and navigation are often JS-rendered. Quote verification on page titles commonly fails even when data is correct. Use `verify_data_values()` as the primary verification for table data; treat quote verification as a bonus, not a requirement.
- **`cross_check()` mode and tolerance**: Use `mode="absolute"` for computed results that should match closely. Use `mode="relative"` for source-to-source comparisons. Tolerance heuristics for government statistics: expect 1-5% variation across aggregators due to rounding, month selection (annual avg vs December), and base-period differences. If sources disagree by more than 5%, investigate: find a third source, check if they use different base periods or date ranges, and document the discrepancy in adversarial checks. Don't silently ignore large disagreements — they may indicate one source is wrong.
- **Quote selection for qualitative claims**: Pick quotes that directly state the claim's core assertion, not tangential mentions. A source that says "the brain is remarkable" does not support "adult neurogenesis occurs." The quote must be specific enough that citation verification confirms the source actually addresses the claim.
- **Academic HTML degrades citation matches**: PMC and journal pages embed inline reference markers (`[1]`, superscripts) that inject noise after HTML stripping. If a real verbatim quote gets `partial` status, check whether the source is academic HTML before suspecting the quote itself. Use `snapshot` to capture clean text if needed.
- **Don't conflate source count with evidence strength**: 5 news articles citing the same study count as 1 independent source, not 5. For qualitative consensus proofs, check whether sources trace to independent primary research. Document the independence rationale in the cross-checks section.
- **Absence claims need search documentation**: For "no evidence exists" claims, use the Absence-of-Evidence template. Document what was searched (databases, query terms, date ranges), not just what was found. The `search_registry` structure makes this machine-checkable.

## Reference Files

Read these on demand, not all upfront.

| File | Read when |
|------|-----------|
| [hardening-rules.md](${CLAUDE_SKILL_DIR}/references/hardening-rules.md) | **Step 3** — the 7 rules with bad/good examples |
| [proof-templates.md](${CLAUDE_SKILL_DIR}/references/proof-templates.md) | **Step 3** — choose a template: date/age, numeric/table, or pure-math |
| [output-specs.md](${CLAUDE_SKILL_DIR}/references/output-specs.md) | **Step 5** — proof.md and proof_audit.md structure |
| [self-critique-checklist.md](${CLAUDE_SKILL_DIR}/references/self-critique-checklist.md) | **Step 6** — before presenting results |
| [advanced-patterns.md](${CLAUDE_SKILL_DIR}/references/advanced-patterns.md) | When encountering complex quotes or table-sourced data |
| [environment-and-sources.md](${CLAUDE_SKILL_DIR}/references/environment-and-sources.md) | When facing fetch failures, paywalls, or .gov 403s |

## Bundled Scripts

Import these instead of re-implementing verification logic.

| Script | Purpose | Key functions |
|--------|---------|---------------|
| `scripts/extract_values.py` | Parse values FROM quote strings (Rule 1) | `parse_date_from_quote()`, `parse_number_from_quote()`, `parse_percentage_from_quote()` |
| `scripts/smart_extract.py` | Unicode normalization + extraction utilities | `normalize_unicode()`, `verify_extraction()`, `diagnose_mismatch()` |
| `scripts/verify_citations.py` | Fetch URLs, verify quotes (Rule 2) | `verify_citation()`, `verify_all_citations()`, `build_citation_detail()`, `verify_data_values()` |
| `scripts/computations.py` | Verified constants, formulas, self-documenting output (Rule 7) | `compute_age()`, `compare()`, `explain_calc()`, `cross_check()`, `compute_percentage_change()` |
| `scripts/source_credibility.py` | Domain credibility from URL (offline). Called automatically by `verify_all_citations()`. | `assess_credibility(url)` |
| `scripts/validate_proof.py` | Static analysis for rule compliance | `ProofValidator(filepath).validate()` |

**Key function signatures:**

```python
# computations.py
cross_check(value_a, value_b, tolerance=0.01, mode="absolute", label=None) -> bool
#   mode="absolute": |a - b| <= tolerance
#   mode="relative": |a - b| / max(|a|, |b|) <= tolerance
compute_percentage_change(old_value, new_value, label=None, mode="increase") -> float
#   mode="increase": (new - old) / old * 100
#   mode="decline": (1 - old / new) * 100
explain_calc(expr_str, scope, label=None) -> object
#   Prints symbolic -> substituted -> result. RETURNS the computed value.
compare(value, op_str, threshold, label=None) -> bool
#   Prints "{label}: {value} {op_str} {threshold} = {result}". Label defaults to "compare".

# verify_citations.py
build_citation_detail(fact_registry, citation_results, empirical_facts) -> dict
verify_data_values(url, data_values, fact_id, timeout=15, snapshot=None) -> dict
#   Fetches page and confirms each value string appears. Returns {key: {found, value, fetch_mode}}
```

**Import pattern:**
```python
import sys
PROOF_ENGINE_ROOT = "${CLAUDE_SKILL_DIR}"  # replaced with actual path at proof-writing time
sys.path.insert(0, PROOF_ENGINE_ROOT)
```

## Environment

Full Type B verification requires **outbound HTTP** from Python. Fallback chain: live fetch -> snapshot -> Wayback Machine (opt-in). Type A proofs run entirely offline.

For environment-specific details (Claude Code, ChatGPT, sandboxed), paywalled sources, and .gov workarounds, see [environment-and-sources.md](${CLAUDE_SKILL_DIR}/references/environment-and-sources.md).

## Core Concepts

**Type A facts (Pure)**: Established entirely by code. The computation IS the verification.

**Type B facts (Empirical)**: Established by citation. Each MUST have: source name, working URL, exact quote. Reputable sources only.

**Type S facts (Search)**: For absence-of-evidence proofs. Each database search is documented with a clickable `search_url`. The tool confirms the URL is accessible but cannot verify the result count — that's author-reported and reproducible by a human reviewer. This weaker trust boundary is reflected in the SUPPORTED verdict (never PROVED).

**Every proof has three parts**: (1) Fact Registry — numbered facts tagged Type A, B, or S, (2) Proof Logic — a self-contained Python script, (3) Verdict — one of the levels below.

## The 7 Hardening Rules

| Rule | Closes failure mode | Enforced by |
|------|-------------------|-------------|
| 1. Never hand-type values | LLM misreads dates/numbers from quotes | `scripts/extract_values.py` |
| 2. Verify citations by fetching | Fabricated quotes/URLs | `scripts/verify_citations.py` |
| 3. Anchor to system time | LLM wrong about today's date | `date.today()` |
| 4. Explicit claim interpretation | Silent ambiguity | `CLAIM_FORMAL` dict with `operator_note` |
| 5. Independent adversarial check | Confirmation bias | Counter-evidence web searches |
| 6. Independent cross-checks | Shared-variable bugs | Multiple sources parsed separately |
| 7. Never hard-code constants/formulas | LLM misremembers values | `scripts/computations.py` |

See [hardening-rules.md](${CLAUDE_SKILL_DIR}/references/hardening-rules.md) for detailed examples of each.

## Workflow

### Step 1: Analyze the Claim
Classify: mathematical (Type A), empirical (Type B), or mixed. Identify ambiguous terms. Determine what constitutes proof AND disproof. For compound claims (X AND Y, X BECAUSE Y), decompose into sub-claims. Write a brief proof strategy and share with the user before proceeding.

If the claim is an opinion or has no verifiable answer, do NOT attempt a proof. Offer a related factual claim instead.

Guiding questions:
- Crisp true/false threshold? Extractable facts? Canonical sources? Clear disproof condition?
- If fewer than 3 are true, consider a simpler factual summary instead.
- For consensus claims, see the Qualitative Consensus Proof Template in [proof-templates.md](${CLAUDE_SKILL_DIR}/references/proof-templates.md).

### Step 2: Gather Facts (Both Directions)
Search for sources that SUPPORT the claim, then sources that CONTRADICT it (adversarial — Rule 5). Find at least two independent sources (Rule 6). For math claims, plan two independent computation approaches.

**Adversarial work happens once, here.** The `adversarial_checks` list in proof code records what you found — it's documentation of Step 2 research, not code that runs searches at proof execution time. Use past tense in `verification_performed` (e.g., "Searched for counter-evidence...") to make this clear.

**Adversarial sources belong in `adversarial_checks`, not `empirical_facts`.** Sources that argue *against* your proof's conclusion should be documented in the `adversarial_checks` list's `verification_performed` field. Only sources that *support* the proof's conclusion belong in `empirical_facts`. This prevents adversarial citation failures from degrading the verdict via `any_unverified`.

If a source is likely to return 403 on automated fetch (common for .gov, .edu, and some aggregators), pre-fetch the page text using any available tool and include it as the `snapshot` field in `empirical_facts`. The proof script will verify against the snapshot instead of live-fetching. See [environment-and-sources.md](${CLAUDE_SKILL_DIR}/references/environment-and-sources.md) for details.

### Step 3: Write the Proof Code
Read [hardening-rules.md](${CLAUDE_SKILL_DIR}/references/hardening-rules.md) for the 7 rules. Then read [proof-templates.md](${CLAUDE_SKILL_DIR}/references/proof-templates.md) and choose the template that matches your claim type (date/age, numeric/table, qualitative consensus, or pure-math). The proof script must be self-contained: `python proof.py` produces the full output.

Required elements:
- `CLAIM_FORMAL` dict with `operator_note` (Rule 4)
- `empirical_facts` dict (empirical proofs) or pure-math template (math proofs)
- `compare()` for claim evaluation, `explain_calc()` for computation traces (Rule 7)
- Adversarial checks with `verification_performed` field (Rule 5)
- Cross-checks from independent sources/methods (Rule 6)
- `FACT_REGISTRY` mapping report IDs to proof-script keys
- JSON summary block in `__main__` ending with `=== PROOF SUMMARY (JSON) ===`

### Step 4: Validate
Run `python ${CLAUDE_SKILL_DIR}/scripts/validate_proof.py proof_file.py` and fix issues.

### Step 5: Execute and Report
Run the proof script. Write three files: proof.py, proof.md, proof_audit.md.

For detailed output specifications, see [output-specs.md](${CLAUDE_SKILL_DIR}/references/output-specs.md).

### Step 6: Self-Critique
Before presenting results, run through the checklist in [self-critique-checklist.md](${CLAUDE_SKILL_DIR}/references/self-critique-checklist.md).

## Verdicts

| Verdict | Meaning |
|---------|---------|
| **PROVED** | All facts verified, logic valid, conclusion follows |
| **PROVED (with unverified citations)** | Logic valid but some citation URLs couldn't be fetched |
| **SUPPORTED** | Absence-of-evidence threshold met, no counter-evidence found |
| **SUPPORTED (with unverified citations)** | Absence threshold met but corroborating citations couldn't be fetched |
| **DISPROVED** | Verified counterexample or contradiction found |
| **DISPROVED (with unverified citations)** | Counterexample found but some citations couldn't be fetched |
| **PARTIALLY VERIFIED** | Some sub-claims met threshold, others did not — Conclusion states whether each failing SC lacked evidence or was contradicted |
| **UNDETERMINED** | Insufficient evidence either way |

**Threshold guidance for source-counting proofs:** The default `threshold: 3` means 3 independently verified sources must confirm the claim. Use `threshold: 2` only when the domain has few authoritative sources (e.g., a single landmark study replicated once). Always document the threshold choice in `operator_note`. Never set `threshold: 1` — a single source is not consensus.

## Limitations

Strong for crisp, auditable, bounded claims; weak for open-ended, normative, or predictive claims. The key limit is **formalizable vs fuzzy** — a claim works if it decomposes into extractable facts and a clear rule for proof/disproof.

Disproof is often easier (single counterexample suffices). The engine struggles with: deep original mathematics beyond sympy, broad causal inference, competing definitions, and large literature synthesis. Citation verification confirms quote presence, not semantic entailment — the adversarial check (Rule 5) mitigates this.

## Edge Cases

**Fictitious source attributions:** If a claim attributes data to a specific source that doesn't contain that data (e.g., "according to the 1947 British census" when no such census exists), treat it as a compound claim: (SC1) the numeric value is correct, (SC2) the stated source contains it. Prove SC1 from the actual source, and note the attribution error in `operator_note` and adversarial checks. The verdict reflects both sub-claims.

**Partial-period data:** If a claim covers a time range but the best sources only cover part of it (e.g., claim says 1994-2023, sources cover 1994-2020), document the gap in `operator_note`. For **cumulative nonnegative totals** (e.g., total aid disbursed, cumulative emissions), if the partial-period sum already exceeds the claim's threshold, prove it with a logical extension: "If S₂₀ > T and the quantity is monotonically nondecreasing (cumulative total cannot shrink), then S₂₃ ≥ S₂₀ > T." State the monotonicity assumption explicitly using `explain_calc()`. This shortcut does NOT apply to averages, rates, percentages, or rolling metrics — for those, the missing-period values could decrease the aggregate, and you must either find full-period sources or return `UNDETERMINED` with an explanation of what data is missing.

**Source doesn't contain claimed constant:** If a claim says "per [Source]" but that source doesn't publish the specific constant (e.g., "CODATA values for solar mass" when CODATA doesn't list solar mass), document the substitution in `operator_note`: which source you actually used, why it's authoritative, and how it relates to the claimed source.
