# Hardening Rules Reference

These ten rules close specific failure modes where LLM-generated proof code looks correct but is silently wrong. Each rule creates a verifiable link between the proof's internal representation and an external ground truth — so that when the LLM hallucinates, the error breaks visibly rather than hiding.

For proof templates, see [proof-templates.md](${CLAUDE_SKILL_DIR}/references/proof-templates.md).

## Table of Contents
1. [Rule 1: Never Hand-Type Extracted Values](#rule-1-never-hand-type-extracted-values)
2. [Rule 2: Verify Citations By Fetching](#rule-2-verify-citations-by-fetching)
3. [Rule 3: Anchor to System Time](#rule-3-anchor-to-system-time)
4. [Rule 4: Explicit Claim Interpretation](#rule-4-explicit-claim-interpretation)
5. [Rule 5: Structurally Independent Adversarial Check](#rule-5-structurally-independent-adversarial-check)
6. [Rule 6: Cross-Checks Must Be Truly Independent](#rule-6-cross-checks-must-be-truly-independent)
7. [Rule 7: Never Hard-Code Constants or Formulas](#rule-7-never-hard-code-constants-or-formulas)
8. [Rule 8: Evidence Relevance for Rejection Verdicts](#rule-8-evidence-relevance-for-rejection-verdicts)
9. [Rule 9: Prose References Are Mechanically Resolvable](#rule-9--prose-references-are-mechanically-resolvable)
10. [Rule 10: Quantifier–Domain Match](#rule-10-quantifier-domain-match)

---

## Rule Applicability by Proof Type

The validator checks all 9 rules for every proof. Some rules auto-pass when
the proof doesn't contain the patterns they target. This table shows typical
validator behavior — the "Auto-pass when" column describes the heuristic.

| Rule | Date/Age | Numeric/Table | Qualitative | Absence | Pure Math | Auto-pass when |
|------|----------|---------------|-------------|---------|-----------|----------------|
| 1    | Checked  | Checked       | Auto-pass   | Auto-pass | Auto-pass | No value-extraction patterns found |
| 2    | Checked  | Checked       | Checked     | Checked*  | Auto-pass | No `empirical_facts`, `search_registry`, or URLs |
| 3    | Checked  | Checked       | Auto-pass   | Auto-pass | Auto-pass | No time-dependent keywords (`today`, `age`, etc.) |
| 4    | Checked  | Checked       | Checked     | Checked   | Checked   | Never auto-passes |
| 5    | Checked  | Checked       | Checked     | Checked   | Checked   | Never auto-passes |
| 6    | Checked  | Checked       | Checked     | Checked*  | Auto-pass | No `empirical_facts` or `search_registry` keys |
| 7    | Checked  | Checked       | Auto-pass   | Auto-pass | Checked   | No `365.2*`/`eval()`/inline-age patterns |
| 8    | Auto-pass | Auto-pass  | Checked (disproof) | Auto-pass | Auto-pass | No `proof_direction: "disprove"` found, or no empirical_facts quotes found |

*For absence proofs, Rule 2 checks `verify_search_registry` import (plus
 `verify_all_citations` if corroborating `empirical_facts` are present);
 Rule 6 counts unique databases in `search_registry` by URL domain.

**Note on Pure Math Rule 6:** The validator auto-passes when no empirical sources
are present. It does not inspect whether cross-checks use mathematically
independent methods — that's a proof-writing discipline enforced by the template
and self-critique checklist, not by static analysis.

---

## Rule 1: Never Hand-Type Extracted Values

**Failure mode**: An LLM reads a quote like "On May 14, 1948, David Ben-Gurion proclaimed..." and then, in a separate line of code, types `date(1948, 5, 15)`. The quote says the 14th; the code says the 15th. Nothing connects them — the quote sits in a string, the date sits in a constructor, and the proof runs without complaint. This happens because LLMs frequently make small transcription errors with numbers, dates, and quantities.

**Bad — value disconnected from quote:**
```python
fact = {
    "quote": "population reached 13,988,129 in 2023",
    "value": 13988129  # LLM typed this separately — could be wrong
}
```

**Good — value derived from quote text:**
```python
from scripts.extract_values import parse_number_from_quote
fact = {"quote": "population reached 13,988,129 in 2023"}
fact["value"] = int(parse_number_from_quote(fact["quote"], r'reached ([\d,]+)', "fact_1"))
```

**Bad — date disconnected from quote:**
```python
empirical_facts = {
    "source_a": {
        "quote": "On May 14, 1948, David Ben-Gurion proclaimed...",
        "extracted_date": date(1948, 5, 14),  # hand-typed — could easily be wrong
    }
}
```

**Good — date parsed from quote:**
```python
from scripts.extract_values import parse_date_from_quote
founding_date = parse_date_from_quote(empirical_facts["source_a"]["quote"], "source_a")
```

**When simple parsing fails — two-phase extraction:**

Real-world quotes contain Unicode quirks (en-dashes, curly quotes, degree symbols) that break simple regex. When `parse_number_from_quote()` fails, write a custom extraction function using `smart_extract.py` utilities:

```python
from scripts.smart_extract import normalize_unicode, verify_extraction

def extract_ghg_warming_low(quote):
    '''Extract GHG low-end warming from NOAA page.
    The page uses en-dashes (–) and ° symbols — normalize before extracting.'''
    normalized = normalize_unicode(quote)
    match = re.search(r'warming of ([\d.]+)', normalized)
    value = float(match.group(1))
    verify_extraction(value, quote, "ghg_warming_low")
    return value

ghg_low = extract_ghg_warming_low(empirical_facts["source_b"]["quote"])
```

This function is IN the proof script — auditable, re-runnable, no LLM needed at re-run time. Use `diagnose_mismatch()` to identify the specific character differences before writing the extractor.

**How validate_proof.py catches it**: Looks for `date()` literals and `"value": N` patterns near fact definitions. Flags them as potential hand-typed values.

---

## Rule 2: Verify Citations By Fetching

**Failure mode**: LLMs hallucinate citations. They generate plausible-sounding quotes, attribute them to real institutions, and provide URLs that look right. The human sees "Source: U.S. National Archives" with a `.gov` URL and trusts it. But the quote might be fabricated, or the URL might not contain that text.

**Bad — citation trusted without verification:**
```python
empirical_facts = {
    "source_a": {
        "quote": "On May 14, 1948, David Ben-Gurion proclaimed...",
        "url": "https://history.state.gov/milestones/1945-1952/creation-israel",
        "source_name": "U.S. Department of State",
    }
}
# Just use the quote as-is, never check if it's real
```

**Good — citation verified by fetching:**
```python
from scripts.verify_citations import verify_all_citations

citation_results = verify_all_citations(empirical_facts)
unverified = [k for k, v in citation_results.items() if v["status"] != "verified"]
```

**Critical normalization details**: Real web pages contain several categories of mismatch that break naive string matching:

1. **HTML tags**: Government websites use inline markup (e.g., `<span class="tei-persname">Ben-Gurion</span>`). The script strips tags without injecting spaces, removes spaces before punctuation, collapses whitespace, and lowercases — in that order.

2. **Unicode mismatches**: NOAA, NASA, and IPCC pages use en-dashes (– U+2013) where the LLM transcribes hyphens (-), curly quotes (' U+2019) where the LLM uses straight quotes ('), ring-above (˚ U+02DA) where degree signs (° U+00B0) are expected, and non-breaking spaces (U+00A0) where normal spaces are expected. The script applies `normalize_unicode()` from `smart_extract.py` before all other normalization.

3. **Invisible Unicode characters**: Pages embed zero-width spaces (U+200B), zero-width non-joiners/joiners (U+200C/U+200D), word joiners (U+2060), BiDi marks (U+200E/U+200F), soft hyphens (U+00AD), and variation selectors (U+FE00–U+FE0F). These are invisible but break string matching. The script strips all of them during normalization.

4. **Superscripts and subscripts**: `<sup>` and `<sub>` tags are handled context-dependently. In running prose (footnote markers like "study¹"), they are stripped. In mathematical/scientific contexts (exponents like "10²" or "m²"), they are preserved as numeric characters.

5. **MathML markup**: Scientific pages embed `<math>` tags with LaTeX in the `alttext` attribute. The script extracts `alttext` and converts LaTeX notation (fractions, Greek letters, operators) to readable text via `latex_text.py`.

The script uses **two-pass matching**: first exact match on the fully cleaned text, then substring search as fallback.

When a quote still fails after automatic normalization, use `diagnose_mismatch()` to identify the specific character differences, then write a custom extraction function using the **two-phase extraction** pattern (see SKILL.md).

**Verbatim quoting requirement:** The `quote` field must be a character-for-character substring of the source page text. A subtler variant of the hallucination problem: the LLM recalls the *gist* of what a source says and writes a plausible-sounding quote that captures the meaning but uses completely different wording. The URL is real, the source is real, but the quote is fabricated. This passes human review but fails machine verification because the exact words don't appear on the page.

Common violations:
- **Paraphrasing**: "Sixteen participants" when the page says "16 study participants"
- **Splicing**: Stitching the start of one sentence to the end of another, skipping the middle
- **Synthesizing**: Combining facts from different paragraphs into one "quote"
- **Cleaning up**: Removing parenthetical insertions like "(Gold)" that appear in the original

**Bad — quote written from memory (paraphrased):**
```python
empirical_facts = {
    "source_a": {
        # LLM recalled the gist but used different words
        "quote": "Addition of a single irrelevant clause provokes catastrophic accuracy drops",
        "url": "https://arxiv.org/html/2410.05229v1",
        "source_name": "Mirzadeh et al., GSM-Symbolic (ICLR 2025)",
    }
}
# verify_all_citations() returns not_found — the page uses different wording
```

**Good — quote copied from fetched page:**
```python
import requests
resp = requests.get("https://arxiv.org/html/2410.05229v1")
# Search resp.text for the relevant passage, then copy verbatim:
empirical_facts = {
    "source_a": {
        "quote": (
            "We add seemingly relevant but ultimately inconsequential statements "
            "to GSM-Symbolic templates. Since these statements carry no operational "
            "significance, we refer to them as No-Op"
        ),
        "url": "https://arxiv.org/html/2410.05229v1",
        "source_name": "Mirzadeh et al., GSM-Symbolic (ICLR 2025)",
    }
}
```

If the exact text is too long or unwieldy, use a shorter exact substring that still captures the key finding. A 20-word verbatim quote that verifies is better than a 50-word paraphrase that doesn't.

**Pre-verification workflow:** After writing `empirical_facts`, run `verify_all_citations()` immediately. If any citation returns `partial` or `not_found`, use `closest_passage` from the result to locate the actual wording on the page, then copy the visible rendered text. Fix the quote before proceeding.

**Verdict impact**: If any citation can't be verified, the proof verdict downgrades to "PROVED (with unverified citations)".

**How validate_proof.py catches it**: Looks for imports of `verify_citations` / `verify_all_citations`, or presence of `requests.get`.

---

## Rule 3: Anchor to System Time

**Failure mode**: LLMs are often wrong about the current date. The system prompt might say "today is March 25, 2026" but the LLM might internalize it as 2025 or get the month wrong. If the proof hardcodes a wrong date, the entire time-dependent computation is silently incorrect.

**Bad — hardcoded date only:**
```python
today = date(2026, 3, 25)  # What if the LLM got this wrong?
age = today.year - founding_date.year
```

**Good — anchored to system clock:**
```python
from datetime import date

PROOF_GENERATION_DATE = date(2026, 3, 25)  # For reproducibility
actual = date.today()

if actual == PROOF_GENERATION_DATE:
    today = PROOF_GENERATION_DATE
    date_note = "System date matches proof generation date"
else:
    today = actual
    date_note = f"Proof generated for {PROOF_GENERATION_DATE}, running on {actual}"
```

If run on the generation date, this confirms the LLM was right. If run later, the system clock takes over. If the LLM got the date wrong, the mismatch is visible.

**How validate_proof.py catches it**: Checks `CLAIM_FORMAL["is_time_sensitive"]` declaration against actual `date.today()` usage. Declaring `is_time_sensitive: True` without `date.today()` is an issue; using `date.today()` without the declaration is a warning. When neither condition applies, a hard-coded `date(YYYY, ...)` without `date.today()` is flagged as an issue (e.g. the common `PROOF_GENERATION_DATE = date(YYYY, M, D)` pattern used alongside `date.today()` is fine).

---

## Rule 4: Explicit Claim Interpretation

**Failure mode**: Natural language claims are ambiguous. "Over 70 years old" could mean `> 70` or `>= 70`. "Founded" could mean proclaimed, recognized, or admitted to the UN. An LLM silently picks whichever interpretation makes the proof succeed. If the claim is borderline, the wrong choice flips the verdict.

**Bad — implicit interpretation:**
```python
# "over 70" — is that > 70 or >= 70?
age = compute_age(founding_date, today)
if age >= 70:  # Why >= and not >? No documentation.
    verdict = "PROVED"
```

**Good — explicit interpretation with rationale:**
```python
CLAIM_NATURAL = "The State of Israel is over 70 years old"
CLAIM_FORMAL = {
    "subject": "State of Israel",
    "property": "age in completed calendar years since founding",
    "operator": ">",
    "operator_note": (
        "'over 70' is interpreted as strictly greater than 70. "
        "If Israel were exactly 70 years and 0 days old, this claim would be FALSE. "
        "This is the more conservative interpretation — using >= would make it easier to prove."
    ),
    "threshold": 70,
    "founding_event": (
        "Proclamation of the Declaration of Independence on 14 May 1948. "
        "Alternative founding events (US recognition same day, UN admission 11 May 1949) "
        "are noted but the proclamation date is the standard reference."
    ),
}
```

The `operator_note` is critical — it forces the LLM to articulate WHY it chose one operator over another, making the decision auditable.

**Epistemic qualifiers:** If the claim contains words like "verified," "confirmed," "proven," "established," "debunked," or "disproven," these assert a specific evidentiary status — not just the underlying fact. Decompose using the Contested Qualifier pattern in the compound template (`template-compound.md`). The `operator_note` must identify the qualifier and explain why it creates a distinct sub-claim (SC1 for provenance, SC2 for the qualifier's warrant).

**How validate_proof.py catches it**: Looks for `CLAIM_FORMAL` dict and checks for `operator_note`.

---

## Rule 5: Structurally Independent Adversarial Check

**Failure mode**: LLMs exhibit confirmation bias. When asked to prove a claim, they seek supporting evidence. The "adversarial check" in many LLM-generated proofs is theater — it recomputes the same values a different way, which catches nothing.

**Bad — adversarial check that's just the proof restated:**
```python
# "Adversarial check": 70 years after 1948 is 2018. Today (2026) > 2018. Claim holds.
# This uses the SAME date (1948) and SAME logic. If 1948 is wrong, this is also wrong.
adversarial_age = 2026 - 1948  # not independent at all
```

**Good — adversarial checks that search for independent counter-evidence:**
```python
adversarial_checks = [
    {
        "question": "Was there ever a gap or dissolution of Israel's statehood since 1948?",
        "verification_performed": "web search: 'Israel statehood continuity gap dissolution'",
        "finding": "No credible source documents any interruption of sovereignty.",
        "breaks_proof": False,
    },
    {
        "question": "Is there a credible alternative founding date that would make Israel younger than 70?",
        "verification_performed": "web search: 'Israel founding date dispute alternative'",
        "finding": "Even UN admission (May 1949) yields 76+ years. No date brings age below 70.",
        "breaks_proof": False,
    },
    {
        "question": "Could 'over 70' linguistically require 71+?",
        "verification_performed": "linguistic analysis",
        "finding": "Even under the strictest reading (71+), 77 > 71.",
        "breaks_proof": False,
    },
]
```

The `verification_performed` field describes what was done to investigate the question. For empirical proofs this is typically a web search; for pure-math proofs it is a computation or structural analysis. (The legacy field name `search_performed` is also accepted.)

These are structurally independent: they don't re-derive the founding date or recompute the age. They search for entirely different facts that, if found, would invalidate the proof's assumptions. Perform these via actual web searches BEFORE writing the proof code.

**Search against your emerging conclusion, not just against the claim.** "Counter-evidence" means evidence that contradicts *your current verdict direction*. If your proof is converging on PROVED, search for reasons the claim is false. If converging on UNDETERMINED or DISPROVED, search for evidence that *supports* the claim — that's the real adversarial check when your finding is negative. The goal is to stress-test whichever conclusion you're about to reach.

**Tactics for effective adversarial search:**
- Search for **alternative definitions** of key terms (e.g., "founding" = proclamation vs recognition vs UN admission)
- Search for **later or earlier milestone dates** that could shift the result past the threshold
- Search for **contested terminology** where the same word means different things in different sources
- Check if the **same institution uses inconsistent wording** across pages (e.g., NASA climate page vs NASA FAQ)
- Look for **source hierarchy conflicts** (primary source disagrees with secondary summary)
- Search for **edge cases where the operator choice matters** (claim is exactly at the threshold boundary)
- Search for **methodological disputes** (different measurement approaches yield different numbers)
- Distinguish **"not found verbatim" from "inconsistent with sources"** — Public sources frequently round figures. A precise number not appearing verbatim is not counter-evidence if it falls within the range sources report. Before flagging a figure as fabricated or unlocatable, check whether it's consistent with reported ranges. The correct framing is "precise figure not independently sourced" — not "appears fabricated." Reserve "fabricated" for figures that contradict or fall outside reported ranges.

**`breaks_proof` must be justified when counter-evidence is found.** For each adversarial check:
- If `breaks_proof: True` — the verdict is forced to UNDETERMINED. No further justification needed.
- If `breaks_proof: False` AND the check found counter-evidence (not just a reproducibility confirmation or null result) — the `finding` field must contain an explicit rebuttal: *why* the counter-evidence does not invalidate the conclusion. "Does not break the proof" or "the proof still holds" is insufficient.
- This rebuttal requirement does NOT apply to reproducibility checks, null-result checks, or edge-case checks where no counter-evidence was discovered.
- **Red flag**: If the `finding` text contains "no significant difference," "does not confirm," "contradicts," "insufficient evidence," or "RCTs show no effect" — and `breaks_proof` is False — the rebuttal must explain why this specific contradiction does not apply. If you cannot write a specific rebuttal, set `breaks_proof: True`.
- **Red flag**: If a `finding` says a number "appears to be fabricated" or "does not appear in any source" — verify whether the number is *inconsistent* with sources or merely *more precise* than sources. Rounding differences are not fabrication.

**How validate_proof.py catches it**: Uses AST to verify `adversarial_checks` is defined as a non-empty list. An empty `adversarial_checks = []` is an issue (vocabulary match alone is not sufficient). The absence of any `adversarial_checks` variable is also an issue. Non-list forms (e.g. `adversarial_checks = build_checks()`) cannot be AST-counted and are passed with a note that entry count could not be verified.

---

## Rule 6: Cross-Checks Must Be Truly Independent

**Failure mode**: A "cross-check" computes the same value two ways — both reading from the same `founding_date` variable. If `founding_date` is wrong, BOTH computations are wrong, and the assertion passes because they're consistently wrong.

**Bad — shared-variable "cross-check":**
```python
# Both methods read founding_date — not independent
age1 = today.year - founding_date.year
age2 = (today - founding_date).days / 365.2425
assert int(age2) == age1  # passes even if founding_date is wrong
```

**Good — truly independent cross-check from separate sources:**
```python
from scripts.extract_values import parse_date_from_quote

# Source A: U.S. State Department (different organization, different page)
date_a = parse_date_from_quote(empirical_facts["source_a"]["quote"], "source_a")

# Source B: U.S. National Archives (independent source)
date_b = parse_date_from_quote(empirical_facts["source_b"]["quote"], "source_b")

# Cross-check: independently parsed values must agree
assert date_a == date_b, f"Sources disagree: source_a={date_a}, source_b={date_b}"

# Compute age from EACH source independently
age_a = compute_age(date_a, today)
age_b = compute_age(date_b, today)
assert age_a == age_b, f"Ages disagree: source_a→{age_a}, source_b→{age_b}"
```

Now if one source has a different date, the assertion catches it. The cross-check has truly independent inputs.

**Interpreting "independent" for government statistics:** For data published by a single authority (BLS for CPI, Census for population), truly independent *measurements* don't exist — all sources trace back to the same authority. In this context, "independent" means independent *publication and presentation*: two different websites that republish BLS data can catch transcription errors, display bugs, or rounding differences between them. This provides weaker assurance than independent measurements but still has value. Note the distinction in the audit doc: "independently published (same upstream authority)" vs "independently measured."

**Interpreting "independent" for pure-math proofs:** Multiple external sources don't apply. Instead, independence means **mathematically distinct approaches** — different algorithms, identities, or structural arguments that don't share intermediate computations with the primary method. Examples of genuinely independent cross-checks:

- Primary: direct summation → Cross-check: closed-form identity (e.g., sum of Fibonacci numbers = F(n+2) − 1)
- Primary: brute-force enumeration → Cross-check: algebraic proof or generating function
- Primary: numerical computation → Cross-check: modular/structural analysis (e.g., Pisano periodicity)
- Primary: symbolic algebra → Cross-check: numerical spot-check at specific values

Re-computing the same formula with different variable names, a different loop structure, or a trivially equivalent expression is **NOT** an independent cross-check. The test: if a bug in the primary method's mathematical reasoning would also affect the cross-check, they are not independent.

**Independence from the claim's subject (Conflict of Interest):**

Sources must be independent not only of each other, but of the entity or claim being evaluated. COI types to check (drawn from IFCN/Cochrane/ICMJE frameworks):

- **Organizational** — source is part of the same org, parent org, or subsidiary as the claim subject
- **Funding dependency** — source receives material funding from the claim subject (or vice versa)
- **Institutional co-benefit** — source's mission or reputation benefits from a particular verdict
- **Competitive antagonism** — source is a direct competitor with incentive to discredit (inverse COI)
- **Revolving door** — key personnel moved between source and claim subject recently
- **Advocacy/ideological** — source exists to advance a position on the topic being evaluated

A COI does not disqualify a source — it reduces the independence credit. Document identified COIs in the `coi_flags` field of the relevant `cross_checks` entry (see output-specs.md).

**Majority COI override (source-counting proofs only):** For proofs where the verdict depends on how many independent sources confirm a finding (qualitative consensus, compound with source-counting sub-claims): if more than half of the confirmed sources have COI in the same `direction` (`favorable_to_subject` or `unfavorable_to_subject`), the verdict is forced to UNDETERMINED. Count unique source keys, not flag entries — a source with multiple COI types still counts as one source. This does NOT apply to date/age, numeric, or pure-math proofs where `threshold` represents a claim value rather than a source count. The COI majority check only applies when the verified source count meets or exceeds the sub-claim's threshold — below that, the source-count check already degrades the verdict, and applying COI to a reduced set produces misleading results.

For compound proofs, the COI check runs per sub-claim, not globally.

**How validate_proof.py catches it**: Counts distinct source references (`source_a`, `source_b`, etc.). Warns if only one source is found for an empirical proof.

---

## Rule 7: Never Hard-Code Constants or Formulas

**Failure mode**: LLMs reconstruct well-known constants and formulas from memory — and sometimes get them wrong. An LLM might type `365.25` (Julian year) instead of `365.2425` (Gregorian year), use `eval()` for comparisons (unsafe and easy to mis-format), or write an inline age calculation with a subtle off-by-one error. These aren't values extracted from citations (Rule 1 handles those) — they're formulas and constants the LLM "knows" but might misremember.

The deeper issue: Python's dynamic nature means these errors produce valid code that runs without errors. `days / 365.25` is perfectly valid Python — it's just using the wrong divisor. The proof runs, produces a number, and nobody notices it's slightly off.

**Bad — hard-coded constant and inline formula:**
```python
approx_years = total_days / 365.2425  # LLM typed from memory — could be wrong
age = today.year - founding_date.year  # inline logic — might miss birthday adjustment
if (today.month, today.day) < (founding_date.month, founding_date.day):
    age -= 1
claim_holds = eval(f"{age} > {threshold}")  # eval is unsafe and error-prone
```

**Good — verified constants and tested functions from bundled script:**
```python
from scripts.computations import compute_age, compare, DAYS_PER_GREGORIAN_YEAR, days_to_years

age = compute_age(founding_date, today)  # tested implementation with birthday adjustment
approx_years = days_to_years(total_days)  # uses verified DAYS_PER_GREGORIAN_YEAR
claim_holds = compare(age, ">", 70)  # type-safe, no eval()
```

The bundled `scripts/computations.py` provides:
- `DAYS_PER_GREGORIAN_YEAR` = 365.2425 (with derivation in docstring)
- `compute_age(birth_date, reference_date)` → int (completed calendar years, handles birthday edge case)
- `compare(value, operator_string, threshold)` → bool (replaces eval(), type-safe)
- `days_to_years(days, calendar="gregorian")` → float
- `compute_elapsed_days(start, end)` → int

Each constant includes its mathematical derivation in the docstring, so the proof is auditable.

**Self-documenting output with `explain_calc()`:**

There's a subtler version of this problem: the code computes correctly, but the LLM writes a print() statement that describes the formula *differently* from what the code actually does. The description and the implementation are disconnected — same structural problem as Rule 1.

`explain_calc()` uses Python's `ast` module to introspect the actual expression at runtime. The code describes itself:

```python
from scripts.computations import explain_calc, DAYS_PER_GREGORIAN_YEAR

# Bad — LLM writes description separately from computation:
approx_years = total_days / DAYS_PER_GREGORIAN_YEAR
print(f"Approximate age (365.2425 days/year): {approx_years:.2f}")  # description could be wrong

# Good — AST walker generates description from the actual code:
approx_years = explain_calc("total_days / DAYS_PER_GREGORIAN_YEAR", locals())
# output: total_days / DAYS_PER_GREGORIAN_YEAR = 28439 / 365.2425 = 77.8633
```

The three-column output (symbolic → substituted → result) makes every step auditable. Use `explain_calc()` for any computation whose output the human needs to verify.

**How validate_proof.py catches it**: Flags hard-coded `365.24*` or `365.25` literals, `eval()` calls, and inline year-subtraction age calculations when `compute_age` is not imported.

---

## Rule 8: Evidence Relevance for Rejection Verdicts

**Failure mode**: A proof reaches DISPROVED by counting sources that don't directly study the claim's subject. Example: a macaque study counts as evidence against a human-neurogenesis claim; a review that "questions" findings counts equally with one that "finds no evidence."

**Subject-match requirement:** For claims about a specific species, organ, population, or domain, at least 2 of 3 rejection sources in the threshold set must directly study that specific subject. A source studying a different species, population, or domain may corroborate but does not count toward the rejection threshold.

**Hedged-language downgrade:** A source that "questions," "challenges," or "casts doubt on" a finding provides weaker evidence than one that "rejects," "finds no evidence for," or "refutes." If any source in the rejection threshold set uses hedged language, the verdict must be SUPPORTED (against) rather than DISPROVED, unless the hedged source is replaced by a direct-rejection source that meets the subject-match requirement.

**How to apply:**
1. For each rejection source, note whether it directly studies the claim's subject
2. For each rejection source, classify its language as "direct rejection" or "hedged challenge"
3. If fewer than 2 of 3 sources pass the subject-match test, downgrade to SUPPORTED (against)
4. If any threshold source uses hedged language and no replacement is available, downgrade to SUPPORTED (against)

Document the subject-match and language classification in the `adversarial_checks` finding field.

**Structural enforcement via `rejection_statement`:** Add a `rejection_statement` field to each `empirical_facts` entry in disproof proofs, containing the verbatim phrase from the quote that constitutes the rejection. This makes the evidentiary link between source and claim explicit and auditable without semantic analysis. `validate_proof.py` warns when the field is absent and raises an issue when it is present but not a verbatim substring of the quote.

---

## Rule 9 — Prose references are mechanically resolvable

**Closes:** hand-typed author/title strings in narrative prose (the
Cheng-vs-Odrzywołek class), and the artifact-gap where build-time template
rendering would leave unresolved tokens in the archived file.

**Enforced by:** `tools/lib/reference_resolver.py` + `tools/lib/prose_reference_scan.py` + `cite-expand` pre-publish gate.

**Two mechanisms exist; one works in practice.** The skill ships:

1. **`<!-- not-a-citation-start -->...<!-- not-a-citation-end -->`** — HTML-comment escape hatch. **This is the working idiom for new proofs.** Wrap the entire bibliographic mention; do NOT include `doi:` inside the wrapper (the linter pattern-matches it even inside the comment).
2. **`{{cite:<type>:<value>}}`** — structured marker resolved at publish time by `cite-expand`. **Deprecated for new proofs pending toolchain fix.** As of the 2026-04-28 end-to-end test, `cite-expand` could not resolve DOI metadata even after `resolve-deps --refresh`, and `verify-prose` still flagged `doi:` inside the resolved output. Existing published proofs that use `{{cite:...}}` are not being rewritten — this is a forward-going recommendation only.

**Bad (hand-typed, unwrapped):**
```markdown
R. Cheng, "The elementary function arithmetic" (arXiv:2603.21852)
```

**Good (HTML-comment wrapper, no DOI in prose):**
```markdown
<!-- not-a-citation-start -->A. Odrzywołek (2026), "All elementary functions from a single binary operator," arXiv preprint<!-- not-a-citation-end -->
```

If you need the DOI/arXiv ID for machine consumption, put it in `proof.json` metadata or `meta.yaml`, not in proof.md prose.

**Deprecated (do not use for new proofs):**
```markdown
{{cite:arxiv:2603.21852}}
```

**Authoring workflow (HTML-comment form):**
```
proof-site.py verify-prose --artifacts-dir <dir>
proof-site.py publish <dir>
```

The `resolve-deps` and `cite-expand` steps are only needed for proofs that still rely on `{{cite:...}}` markers.

**Escape hatch** (rare — use only for historical prose, never for actual citations):
```markdown
<!-- not-a-citation-start --> Einstein (1905) famously... <!-- not-a-citation-end -->
```

The escape hatch suppresses only `DANGLING_SHORT_PATTERN` (bare author-year). Author + quoted title must always carry an identifier — there is no escape hatch for that form.

**What the linter actually flags vs. what is allowed:**

The `verify-prose` linter pattern-matches a narrow shape: capitalized name(s), optional `&`, then a parenthesized 4-digit year. The regex is roughly `\b[A-Z][a-z]+\s*(?:&\s*[A-Z][a-z]+)?\s*\((?:19|20)\d{2}\)`. Things outside that shape pass through silently.

| Form | Status | Example |
|------|--------|---------|
| Parenthetical author-year | **Flagged** | `Monderer & Shapley (1996) showed ...` |
| Author et al. + year | **Flagged** | `Smith et al. (2010) proved ...` |
| Cross-reference to sibling artifact | Allowed | `See proof_audit.md, Implementation regression checks, for ...` |
| Section / heading name in prose | Allowed | `... discussed in the Scope section.` |
| Code identifier or file path | Allowed | `tools/lib/proof_loader.py` |
| Prose with no parenthetical year | Allowed | `Rosenthal's potential function ...` |

**Working idiom for new proofs.** Wrap the entire bibliographic mention in the HTML-comment escape hatch and keep DOIs out of the prose:

```markdown
<!-- not-a-citation-start -->Monderer & Shapley (1996), "Potential Games," *Games and Economic Behavior* 14(1), 124–143<!-- not-a-citation-end -->
```

The DOI (if needed for machine consumption) belongs in `proof.json` metadata or `meta.yaml`, not in proof.md. The `verify-prose` linter pattern-matches the literal `doi:` prefix even inside `<!-- not-a-citation-* -->` blocks and will reject the line.

---

## Rule 10: Quantifier–Domain Match

**Failure mode**: An LLM is given a universally-quantified claim over an unbounded domain ("every finite group of prime order is cyclic", "every finite exact-potential game has a pure NE", "Let G be a finite ... then ..."). The deductive argument is the only thing that can establish such a claim — sampling 10,000 instances proves nothing about the (n+1)th. But sampling code is easy to write and produces a clean number, while a deductive argument is harder. The LLM ends up filing a "PROVED" verdict whose visible evidence is "0 violations across 3,670 sampled games," reading to a reviewer as a demo, not a theorem. Worse, in the artifact text the sampling counts get more visual prominence than the argument, and the verdict is silently downgraded from a real theorem to a sampling result that happens to use the word "PROVED."

**Rule**: If the claim is universally quantified over an unbounded domain (declared via `CLAIM_FORMAL.claim_type: "theorem"`, or detected by claim phrasing such as *"every finite"*, *"for all"*, *"Let G be a finite ..."*), then sampling cannot be the load-bearing evidence for the verdict. The proof must include either:

- (a) a **deductive argument** written as numbered steps in proof.md's `## Proof` section, or
- (b) a **coverage proof** showing exhaustive enumeration over the (necessarily finite) domain.

Sampling-based facts must be labeled as **regression checks** in their `method` text (use phrases such as *"Implementation regression"*, *"regression"*, *"sanity check"*, *"spot-check"* within ~80 characters of any sampling token like *"sampled"*, *"random"*, *"Monte Carlo"*) and must live in **proof_audit.md**, in an `## Implementation regression checks` section — not in proof.md.

For the canonical theorem-proof shape (section list, builder usage, role-disclosing `method` examples), see [template-deductive-theorem.md](template-deductive-theorem.md).

**Bad — theorem proof with sampling counts as primary evidence in proof.md:**

```markdown
<!-- proof.md -->
## Evidence Summary
We verified the claim on **3,670 random 2x2 GOP games**. **0 violations**
were found. The proof script (`proof.py`) re-runs this verification.

## Proof Logic
The implementation samples N games, builds the better-response graph, and
counts cycles. Across 3,670 samples we observed no cycles, confirming the
claim that every finite GOP game has a pure NE.
```

```python
# proof.py — method text reads as primary evidence
builder.add_computed_fact(
    "A1",
    label="GOP games verified",
    method=f"Sampled {N_SAMPLES} random 2x2 games and confirmed each has a pure NE.",
    result=0,
)
```

This proves nothing about a "for all" claim — the (3,671)th game is unaddressed. The Rule 10 check warns because the `method` string contains *"sampled"* / *"random"* without nearby regression-role wording.

**Good — same proof reorganized: deductive argument primary, regression-labeled sampling moved to proof_audit.md:**

```markdown
<!-- proof.md -->
## Theorem statement
**Theorem.** Let G be a finite strategic-form game with the finite
improvement property (FIP). Then G has at least one pure Nash equilibrium.

## Proof
1. By FIP, every better-response path in G terminates.
2. A maximal better-response path ends at a profile where no player has a
   profitable unilateral deviation.
3. Such a profile is, by definition, a pure Nash equilibrium.
4. Hence G has at least one pure NE. ∎

## Corollaries
**Corollary 1.** Every finite exact-potential game has a pure NE. *(Sketch:
exact-potential games satisfy FIP; apply the theorem.)*
...

## Conclusion
**PROVED.** The argument is purely deductive; see proof_audit.md for the
implementation regression checks confirming our GOP-detector matches the
formal definition.
```

```markdown
<!-- proof_audit.md -->
## Implementation regression checks
We sampled 3,670 finite 2-player games to spot-check that our
GOP-detector implementation agrees with the formal definition (no cycles
in the better-response graph). Across the sample: 0 disagreements.
This regression-checks the *code*, not the theorem — sampling cannot
prove a 'for all' claim.
```

```python
# proof.py — method text discloses the regression role
builder.add_computed_fact(
    "A1",
    label="GOP-detector regression spot-check",
    method=(
        f"Implementation regression: sampled {N_SAMPLES} games to "
        f"spot-check the GOP-detector against the formal definition."
    ),
    result=0,
)
```

The deductive argument carries the verdict; the sampling is honestly framed as a regression check on the code; and the `method` string includes *"Implementation regression"* and *"spot-check"* within ~80 characters of *"sampled"*, so the Rule 10 check is satisfied.

**How validate_proof.py catches it**: When `CLAIM_FORMAL.claim_type == "theorem"`, the validator scans `add_computed_fact()` call args and `FACT_REGISTRY` dict literals for `method`/`label` strings (including f-string literal parts) containing sampling tokens (*"sampled"*, *"random"*, *"Monte Carlo"*). For each match, it requires regression-role wording (*"regression"*, *"implementation regression"*, *"sanity check"*, *"spot-check"*) within ~80 characters; otherwise it warns that the sampling fact reads as primary evidence. Independently, when the claim text or `CLAIM_FORMAL` looks universally quantified (*"every finite"*, *"all finite-strategy"*, *"for any finite"*, *"Let [Var] be a finite [domain]"*) but `claim_type != "theorem"`, the validator suggests declaring `claim_type: "theorem"`. Section-presence enforcement (the `## Proof` / `## Corollaries` / `## Scope` / `## Relation to prior work` requirements) lives in `tools/lib/proof_loader.py` at site-build time, not in `validate_proof.py`.
