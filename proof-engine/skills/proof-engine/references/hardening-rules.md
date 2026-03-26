# Hardening Rules Reference

Read this before writing any proof code.

These seven rules close specific failure modes where LLM-generated proof code looks correct but is silently wrong. Each rule creates a verifiable link between the proof's internal representation and an external ground truth — so that when the LLM hallucinates, the error breaks visibly rather than hiding.

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

---

## Complete Proof Template

A well-formed proof script has this structure. The structural elements (FACT_REGISTRY, JSON summary block, required JSON fields) are the contract. Variable names and specific logic are illustrative — adapt them to the claim being proved.

```python
"""
Proof: [claim text]
Generated: [date]
"""
import json
import sys

# Path to proof-engine scripts directory (the directory containing SKILL.md).
# In Claude Code, replace with the resolved value of ${CLAUDE_SKILL_DIR}.
# In standalone use, set to the absolute path of the skills/proof-engine directory.
PROOF_ENGINE_ROOT = "..."  # ← LLM fills this with the actual path at proof-writing time
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

# --- STRUCTURAL IMPORTS (always needed) ---
from scripts.smart_extract import normalize_unicode, verify_extraction
from scripts.verify_citations import verify_all_citations
from scripts.computations import compare, explain_calc

# --- CLAIM-SPECIFIC IMPORTS (adapt to your proof) ---
# For date/age proofs:
from scripts.extract_values import parse_date_from_quote
from scripts.computations import compute_age, DAYS_PER_GREGORIAN_YEAR, days_to_years
# For empirical/numeric proofs:
#   from scripts.extract_values import parse_number_from_quote, parse_percentage_from_quote, parse_range_from_quote
# For pure-math proofs:
#   (no extract_values imports needed)

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "property": "...",
    "operator": ">",
    "operator_note": "...",
    "threshold": ...,
}

# For compound claims ("X AND Y", "X BECAUSE Y"), decompose into sub-claims:
# sub_claims = [
#     {
#         "id": "A",
#         "natural": "X is true",
#         "operator": ">",
#         "operator_note": "...",
#         "threshold": ...,
#     },
#     {
#         "id": "B",
#         "natural": "Y is true",
#         "operator": "==",
#         "operator_note": "...",
#         "threshold": ...,
#     },
# ]
# conjunction = "AND"  # or "OR", "BECAUSE", "IMPLIES"
# Overall verdict: PROVED only if all sub-claims proved (for AND).
# Include sub_claims and conjunction in the JSON summary.

# 2. FACT REGISTRY — maps report IDs to proof-script keys
# CONTRACT: Every proof must define this. It is the single source of truth
# for cross-document ID consistency between proof.md and proof_audit.md.
# B = empirical (Type B), A = computed (Type A). Each source is its own fact.
FACT_REGISTRY = {
    "B1": {"key": "source_a", "label": "...one-line description..."},
    "B2": {"key": "source_b", "label": "...one-line description..."},
    "A1": {"label": "...one-line description...", "method": None, "result": None},
    # A-type method and result are populated in __main__ after computation.
}

# 3. EMPIRICAL FACTS — quotes only, NO hand-typed values (Rule 1)
# Optional: include "snapshot" with pre-fetched page text for offline verification.
# If Python has no outbound HTTP access (e.g., ChatGPT), fetch each source page
# using your browsing capability and include the page text as the snapshot field.
empirical_facts = {
    "source_a": {
        "quote": "...", "url": "...", "source_name": "...",
        # "snapshot": "...full page text...",
        # "snapshot_fetched_at": "2026-03-26T10:00:00Z",
    },
    "source_b": {
        "quote": "...", "url": "...", "source_name": "...",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
# Fallback chain: live fetch → snapshot → Wayback (if opted in).
# verify_all_citations returns structured dicts with status/method/coverage_pct.
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. VALUE EXTRACTION — parsed from quotes (Rule 1)
# NOTE: parse functions and verify_extraction print match status inline.
val_a = parse_date_from_quote(empirical_facts["source_a"]["quote"], "source_a")
val_a_in_quote = verify_extraction(val_a, empirical_facts["source_a"]["quote"], "B1")
val_b = parse_date_from_quote(empirical_facts["source_b"]["quote"], "source_b")
val_b_in_quote = verify_extraction(val_b, empirical_facts["source_b"]["quote"], "B2")

# 6. CROSS-CHECK (Rule 6)
assert val_a == val_b, f"Sources disagree: {val_a} vs {val_b}"

# 7. SYSTEM TIME (Rule 3)
PROOF_GENERATION_DATE = date(...)
today = date.today()

# 8. COMPUTATION — use bundled functions (Rule 7)
# NOTE: explain_calc prints symbolic/substituted/result traces inline.
age = compute_age(val_a, today)
approx_years = explain_calc("(today - val_a).days / DAYS_PER_GREGORIAN_YEAR", locals())

# 9. CLAIM EVALUATION — use compare(), not eval() (Rule 7)
claim_holds = compare(age, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"])

# 10. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "...",  # web search for empirical, computation for pure math
        "finding": "...",
        "breaks_proof": False,
    },
]

# 11. VERDICT AND STRUCTURED OUTPUT
# CONTRACT: __main__ must end with a JSON summary block containing all
# structured fields that proof.md and proof_audit.md depend on.
# verify_citation now returns structured dicts — no message parsing needed.
if __name__ == "__main__":
    # --- Verdict logic (adapt to claim structure) ---
    # All five levels must be considered:
    #   PROVED, PROVED (with unverified citations), DISPROVED,
    #   PARTIALLY VERIFIED, UNDETERMINED
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    if claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds:
        verdict = "DISPROVED"
    # For complex proofs, also handle:
    # verdict = "PARTIALLY VERIFIED"  — some sub-claims proved, others not
    # verdict = "UNDETERMINED"        — insufficient evidence either way

    # --- Populate Type A method/result (after computation completes) ---
    FACT_REGISTRY["A1"]["method"] = "compute_age()"
    FACT_REGISTRY["A1"]["result"] = str(age)

    # --- Build citation details from structured results (no message parsing) ---
    citation_detail = {}
    for fact_id, info in FACT_REGISTRY.items():
        key = info.get("key")
        if key and key in citation_results:
            cr = citation_results[key]
            citation_detail[fact_id] = {
                "source_key": key,
                "source_name": empirical_facts[key].get("source_name", ""),
                "url": empirical_facts[key].get("url", ""),
                "quote": empirical_facts[key].get("quote", ""),
                "status": cr["status"],
                "method": cr["method"],
                "coverage_pct": cr["coverage_pct"],
                "fetch_mode": cr["fetch_mode"],
            }

    # --- Build extraction records ---
    extractions = {
        "B1": {
            "value": str(val_a),
            "value_in_quote": val_a_in_quote,
            "quote_snippet": empirical_facts["source_a"]["quote"][:80],
        },
        "B2": {
            "value": str(val_b),
            "value_in_quote": val_b_in_quote,
            "quote_snippet": empirical_facts["source_b"]["quote"][:80],
        },
    }

    # --- Build JSON summary ---
    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {"description": "...", "values_compared": [str(val_a), str(val_b)], "agreement": val_a == val_b}
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "age": age,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
```

### Pure-Math Proof Template

For claims that are entirely mathematical (no empirical sources, no URLs, no citations), use this streamlined template. It omits all citation/extraction boilerplate and focuses on computation, cross-checks, and adversarial analysis.

```python
"""
Proof: [claim text]
Generated: [date]
"""
import json
import sys

PROOF_ENGINE_ROOT = "..."  # ← LLM fills with resolved ${CLAUDE_SKILL_DIR}
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.computations import compare, explain_calc

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "property": "...",
    "operator": "==",
    "operator_note": "...",
    "threshold": ...,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {"label": "...", "method": None, "result": None},
    "A2": {"label": "...", "method": None, "result": None},
}

# 3. COMPUTATION — primary method
# ... your computation logic here ...
# Use explain_calc() where it adds clarity (scalar expressions).
# For aggregations over lists, use descriptive print() statements instead.
primary_result = ...

# 4. CROSS-CHECKS — mathematically independent methods (Rule 6)
# Each cross-check must use a DIFFERENT algorithm, identity, or structural
# argument. See Rule 6 for what counts as "independent" in pure math.
crosscheck_result = ...  # different method, same expected answer
assert primary_result == crosscheck_result, (
    f"Cross-check failed: primary={primary_result}, crosscheck={crosscheck_result}"
)

# 5. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "...",  # computation or structural analysis
        "finding": "...",
        "breaks_proof": False,
    },
]

# 6. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    claim_holds = compare(primary_result, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"])

    verdict = "PROVED" if claim_holds else "DISPROVED"

    FACT_REGISTRY["A1"]["method"] = "..."
    FACT_REGISTRY["A1"]["result"] = str(primary_result)
    FACT_REGISTRY["A2"]["method"] = "..."
    FACT_REGISTRY["A2"]["result"] = str(crosscheck_result)

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "cross_checks": [
            {
                "description": "...",
                "values_compared": [str(primary_result), str(crosscheck_result)],
                "agreement": primary_result == crosscheck_result,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "primary_result": primary_result,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
```

Key differences from the empirical template:
- No `empirical_facts`, `verify_all_citations`, `extract_values`, or `smart_extract` imports
- No `citations` or `extractions` keys in the JSON summary (omitted, not empty)
- Cross-checks use mathematically independent methods instead of independent sources
- Adversarial checks use `verification_performed` with computations, not web searches
- No `date.today()` unless the claim is time-dependent
- `explain_calc()` is optional — use it for scalar expressions where the symbolic/substituted/result trace adds clarity. For aggregations over lists (e.g., `sum(fib[1:101])`), use descriptive `print()` statements instead, since the AST walker can't introspect built-in calls over slices.

### Adapting for empirical consensus proofs

The template above uses date/age variables as examples. For proofs where the claim is "multiple authoritative sources agree on a quantitative finding" (e.g., climate attribution, economic statistics), adapt as follows:

- **Imports**: Use `parse_number_from_quote`, `parse_percentage_from_quote`, `parse_range_from_quote` instead of `parse_date_from_quote`. Drop `compute_age`, `DAYS_PER_GREGORIAN_YEAR`, `days_to_years`.
- **FACT_REGISTRY**: Typically 3+ B-type entries (one per authoritative source) and 1-2 A-type entries for derived computations (averages, ratios).
- **Snapshots**: For government and scientific sources that may block automated fetching, include `"snapshot"` with the pre-fetched page text. If Python has no outbound HTTP access, fetch each source page using your browsing capability and include it as the snapshot.
- **Extraction**: Values are often ranges ("1.0°C to 2.0°C") — use `parse_range_from_quote()`. Call `verify_extraction()` on each extracted value.
- **Cross-checks**: Compare independently extracted values across sources. Agreement within ranges is sufficient — exact equality is unlikely for empirical data.
- **Computation**: Derive summary statistics (midpoint of range, percentage attribution) using `explain_calc()`.
- **Verdict**: Empirical consensus proofs often land on PROVED (with unverified citations) because government and scientific websites frequently have formatting that prevents full quote verification.

### Adapting for qualitative consensus proofs

For claims where the evidence is "multiple authoritative sources agree that X is true/possible" — without a numeric threshold — adapt the template as follows:

- **Claim type**: The claim is qualitative ("does the scientific literature support X?"). The formal threshold is not a number but a consensus criterion: "N of M authoritative sources explicitly state X."
- **Imports**: You may not need `parse_number_from_quote` or other numeric extractors. The structural imports (`verify_extraction`, `verify_all_citations`, `compare`, `explain_calc`) are still needed.
- **Extraction**: Instead of parsing numbers, verify that a specific keyword or phrase appears in each source quote. Use `verify_extraction("keyword", quote, fact_id)` — it works for strings, not just numbers. For example: `verify_extraction("reactivates", empirical_facts["source_a"]["quote"], "B1")`.
- **FACT_REGISTRY**: B-type entries per source (one per authoritative reference). A-type entries for the logical conclusion (e.g., "A1: All 4 sources confirm reactivation is possible").
- **CLAIM_FORMAL**: The operator may be "==" with threshold as a boolean or count: `"operator": ">=", "threshold": 3, "operator_note": "at least 3 of 4 sources must explicitly confirm the finding"`.
- **Cross-checks**: Compare whether independently sourced quotes agree on the same qualitative finding. Agreement means the same concept is present, not necessarily the same wording.
- **Adversarial**: Search for sources that explicitly dispute or qualify the consensus. Look for review articles that note exceptions or controversy.
- **Verdict**: PROVED if all/most sources agree and no credible counter-evidence found. PARTIALLY VERIFIED if sources agree but with significant caveats. DISPROVED if authoritative sources explicitly contradict the claim.

### Citing structured/tabular data

For economic, statistical, or scientific claims, the key numeric values often live in HTML tables rather than prose text. The verifiable prose quote confirms the source authority, while the numbers come from a data table.

Use a `data_values` dict alongside the quote:

```python
empirical_facts = {
    "source_a_cpi": {
        "quote": "The CPI for USA is calculated and issued by: U.S. Bureau of Labor Statistics",
        "url": "https://www.rateinflation.com/consumer-price-index/usa-historical-cpi/",
        "source_name": "RateInflation.com (sourced from BLS)",
        # Table values stored separately — these are the extractable numbers
        "data_values": {"cpi_1913": "9.883", "cpi_2024": "313.689"},
    },
}
```

- The `quote` field verifies the source's authority via `verify_all_citations()`
- The `data_values` entries are parsed with `parse_number_from_quote(fact["data_values"]["cpi_1913"], r"([\d.]+)", "B1_cpi_1913")`
- The audit doc distinguishes "source authority verified via quote" from "numeric data extracted from table"
- Use `cross_check()` from computations.py to compare values across sources with tolerance
