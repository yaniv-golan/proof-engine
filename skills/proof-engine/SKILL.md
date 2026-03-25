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

The skill produces two outputs: a re-runnable `.py` proof script and a readable `.md` summary.

## Before Writing Any Proof Code

Read [Hardening Rules Reference](${CLAUDE_SKILL_DIR}/references/hardening-rules.md) — it contains the 7 rules with bad/good code examples for each. These rules close specific failure modes where proof code *looks* correct but is silently wrong.

## Bundled Scripts

Import these instead of re-implementing verification logic. They are tested and deterministic.

| Script | Purpose | Key functions |
|--------|---------|---------------|
| `${CLAUDE_SKILL_DIR}/scripts/extract_values.py` | Parse values FROM quote strings (Rule 1) | `parse_date_from_quote()`, `parse_number_from_quote()`, `parse_percentage_from_quote()` |
| `${CLAUDE_SKILL_DIR}/scripts/smart_extract.py` | Unicode normalization + LLM-assisted extraction utilities | `normalize_unicode()`, `verify_extraction()`, `diagnose_mismatch()`, `ExtractionRecord` |
| `${CLAUDE_SKILL_DIR}/scripts/verify_citations.py` | Fetch URLs, verify quotes exist on page (Rule 2) | `verify_citation()`, `verify_all_citations()` |
| `${CLAUDE_SKILL_DIR}/scripts/computations.py` | Verified constants, formulas, and self-documenting output (Rule 7) | `compute_age()`, `compare()`, `explain_calc()`, `DAYS_PER_GREGORIAN_YEAR` |
| `${CLAUDE_SKILL_DIR}/scripts/validate_proof.py` | Static analysis for rule compliance (pre-flight) | `ProofValidator(filepath).validate()` |

To import these from a proof script, add the proof-engine root to the path:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## Core Concepts

**Type A facts (Pure)**: Established entirely by code. The computation IS the verification. Use for math, logic, and derivations. Tools: `sympy` for symbolic math, plain Python for arithmetic.

**Type B facts (Empirical)**: Established by citation. Each MUST have: source name, working URL, exact quote. The citation IS the verification. Reputable sources only (peer-reviewed, government, established references).

**Every proof has three parts**: (1) Fact Registry — numbered facts tagged Type A or B, (2) Proof Logic — a self-contained Python script, (3) Verdict — one of the five levels below.

## The 6 Hardening Rules

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
Classify the claim: mathematical (Type A only), empirical (Type B only), or mixed. Identify ambiguous terms. Determine what would constitute proof AND disproof. Write a brief proof strategy and share it with the user before proceeding.

If the claim is an opinion, value judgment, or has no verifiable answer (e.g., "Python is the best language"), do NOT attempt a proof. Explain why, and offer to prove a related factual claim instead.

### Step 2: Gather Facts (Both Directions)
Search for sources that SUPPORT the claim. Then search for sources that CONTRADICT it (adversarial — Rule 5). For empirical facts, find at least two independent sources (Rule 6). For math claims, identify the right tool (sympy, plain Python).

### Step 3: Write the Proof Code
Read [references/hardening-rules.md](${CLAUDE_SKILL_DIR}/references/hardening-rules.md) first. Start from the template at the bottom of that file. Import and use the bundled scripts. The proof script must be self-contained: `python proof.py` produces the full output.

Required structural elements in every proof script:
- `CLAIM_FORMAL` dict with `operator_note` (Rule 4)
- `empirical_facts` dict with quotes but NO hand-typed values (Rule 1)
- Imports from bundled scripts for verification (Rules 1, 2)
- `date.today()` for time-dependent proofs (Rule 3)
- `compute_age()`, `compare()`, `explain_calc()`, and constants from `${CLAUDE_SKILL_DIR}/scripts/computations.py` — never hand-code formulas or well-known constants, and use `explain_calc()` for self-documenting output (Rule 7)
- Adversarial checks section (Rule 5)
- Cross-checks from independent sources (Rule 6)
- `if __name__ == "__main__"` block printing everything including verdict

### Step 4: Validate Before Executing
Run `python ${CLAUDE_SKILL_DIR}/scripts/validate_proof.py proof_file.py` and fix any issues before proceeding.

### Step 5: Execute and Report
Run the proof script, capture output. Write both outputs:
- **`.py` file**: the proof script itself (re-runnable)
- **`.md` file**: readable summary with claim interpretation, fact registry, verification status, adversarial results, verdict, and hardening checklist

### Step 6: Self-Critique Checklist
Before presenting results, verify:
- [ ] Every empirical value parsed from quote text, not hand-typed (Rule 1)
- [ ] Every citation URL fetched and quote checked (Rule 2)
- [ ] System time used for date-dependent logic (Rule 3)
- [ ] Claim interpretation explicit with operator rationale (Rule 4)
- [ ] Adversarial checks searched for independent counter-evidence (Rule 5)
- [ ] Cross-checks used independently sourced inputs (Rule 6)
- [ ] Constants and formulas imported from computations.py, not hand-coded (Rule 7)
- [ ] validate_proof.py passes

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

## Gotchas

- **Don't inline verification logic**: Import the bundled scripts. Rewriting `normalize_text()` inline risks garbling the HTML-stripping logic.
- **Don't use `int()` truncation as a cross-check**: `int(days / 365.2425) == calendar_years` is not independent — both are functions of the same input.
- **Don't restate the proof as an adversarial check**: "70 years after 1948 is 2018, and 2026 > 2018" catches nothing. Search for counter-evidence.
- **Handle HTML in citations**: Government websites often use inline `<span>` tags. The bundled script handles this — but only if you use it.
- **Handle Unicode in citations**: Real web pages use en-dashes (–), curly quotes ('), ring-above (˚) vs degree (°), non-breaking spaces, etc. `verify_citations.py` automatically applies `normalize_unicode()` from `smart_extract.py`. For custom extraction, import and use `normalize_unicode()` explicitly.
- **Don't write print() descriptions of formulas**: Use `explain_calc("expr", locals())` instead. It AST-walks the expression and prints what the code actually does, not what you think it does. This closes the gap between computation and description.
