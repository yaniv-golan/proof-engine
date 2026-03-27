# Hardening Rules Reference

These seven rules close specific failure modes where LLM-generated proof code looks correct but is silently wrong. Each rule creates a verifiable link between the proof's internal representation and an external ground truth — so that when the LLM hallucinates, the error breaks visibly rather than hiding.

For proof templates, see [proof-templates.md](${CLAUDE_SKILL_DIR}/references/proof-templates.md).

## Table of Contents
1. [Rule 1: Never Hand-Type Extracted Values](#rule-1-never-hand-type-extracted-values)
2. [Rule 2: Verify Citations By Fetching](#rule-2-verify-citations-by-fetching)
3. [Rule 3: Anchor to System Time](#rule-3-anchor-to-system-time)
4. [Rule 4: Explicit Claim Interpretation](#rule-4-explicit-claim-interpretation)
5. [Rule 5: Structurally Independent Adversarial Check](#rule-5-structurally-independent-adversarial-check)
6. [Rule 6: Cross-Checks Must Be Truly Independent](#rule-6-cross-checks-must-be-truly-independent)
7. [Rule 7: Never Hard-Code Constants or Formulas](#rule-7-never-hard-code-constants-or-formulas)

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

**Critical normalization details**: Real web pages contain two categories of mismatch that break naive string matching:

1. **HTML tags**: Government websites use inline markup (e.g., `<span class="tei-persname">Ben-Gurion</span>`). The script strips tags, removes spaces before punctuation, collapses whitespace, and lowercases — in that order.

2. **Unicode mismatches**: NOAA, NASA, and IPCC pages use en-dashes (– U+2013) where the LLM transcribes hyphens (-), curly quotes (' U+2019) where the LLM uses straight quotes ('), ring-above (˚ U+02DA) where degree signs (° U+00B0) are expected, and non-breaking spaces (U+00A0) where normal spaces are expected. The script applies `normalize_unicode()` from `smart_extract.py` before all other normalization.

When a quote still fails after automatic normalization, use `diagnose_mismatch()` to identify the specific character differences, then write a custom extraction function using the **two-phase extraction** pattern (see SKILL.md).

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

**How validate_proof.py catches it**: Looks for `date.today()` in the code. If only hardcoded `date()` is found in a time-dependent proof, flags it.

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

**Tactics for effective adversarial search:**
- Search for **alternative definitions** of key terms (e.g., "founding" = proclamation vs recognition vs UN admission)
- Search for **later or earlier milestone dates** that could shift the result past the threshold
- Search for **contested terminology** where the same word means different things in different sources
- Check if the **same institution uses inconsistent wording** across pages (e.g., NASA climate page vs NASA FAQ)
- Look for **source hierarchy conflicts** (primary source disagrees with secondary summary)
- Search for **edge cases where the operator choice matters** (claim is exactly at the threshold boundary)
- Search for **methodological disputes** (different measurement approaches yield different numbers)

**How validate_proof.py catches it**: Looks for "adversarial", "disproof", "counter-evidence" etc. in the code.

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
