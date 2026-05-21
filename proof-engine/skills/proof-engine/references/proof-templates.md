# Proof Templates

Read this at **Step 3** when writing proof code. Choose the template that matches your claim type, then read the specific template file.

## Template Selection

| Claim type | Template file | When to use |
|------------|--------------|-------------|
| Date/age | [template-date-age.md](template-date-age.md) | Claim about when something happened or how old it is |
| Numeric/table data | [template-numeric.md](template-numeric.md) | CPI, GDP, population — primary evidence from HTML tables |
| Qualitative consensus | [template-qualitative.md](template-qualitative.md) | "Sources agree X is true" — source count, not numeric comparison |
| Compound (X AND Y) | [template-compound.md](template-compound.md) | Multiple independently verifiable sub-claims; supports N≥2 sub-claims, derived sub-claims, and optional `search_registry` for absence-based sub-claims |
| Absence of evidence | [template-absence.md](template-absence.md) | "No published evidence that X causes Y" |
| Citation audit (Type R) | [template-citation-audit.md](template-citation-audit.md) | "Paper X by author Y in journal Z exists with claimed bibliographic metadata" — catches LLM-fabricated references via `verify_citation_record` |
| Pure math | [template-pure-math.md](template-pure-math.md) | Entirely mathematical, no empirical sources |
| Deductive theorem | [template-deductive-theorem.md](template-deductive-theorem.md) | Universally quantified theorem over an unbounded domain (e.g., "every finite game", "Let G be a finite ..."), proof is a deductive argument; declare `claim_type: 'theorem'` |

## Decision Flowchart

1. Is the claim a universally-quantified theorem over an unbounded domain (e.g., "every finite ...", "Let G be a finite ..."), where the proof is a deductive argument and computation can only sanity-check an implementation? → **Deductive theorem** (declare `claim_type: 'theorem'`)
2. Is the claim purely mathematical (no empirical sources)? → **Pure math**
3. Does the claim assert absence of evidence **and** no authoritative sources actively reject the claim? → **Absence**
   > Absence means the claim's *primary* answer is "no evidence exists." If authoritative sources actively debunk or reject the claim (i.e., positive rejection sources exist), skip to step 9 — those claims are better served by qualitative-disproof, which produces a DISPROVED verdict rather than the weaker SUPPORTED.
3.5. Does the claim assert that *specific* citations (X by author Y in journal Z, with DOI/PMID) exist with claimed bibliographic metadata? → **Citation audit (Type R)**
   > Use this when the operative question is "are these references real?" not "do their contents support a claim." Catches the LLM-fabricated-citation failure mode that quote-on-page verification misses.
4. Does the claim have multiple sub-claims (X AND Y, X BECAUSE Y)? → **Compound**
5. Does the claim use an epistemic qualifier ("verified," "confirmed," "proven")? → **Compound** (contested qualifier pattern)
6. Does the claim use causal language ("causes," "leads to")? → **Compound** (causal decomposition)
7. Is the primary evidence numeric data from tables? → **Numeric/table**
8. Is the claim about a date or age? → **Date/age**
9. Does the claim depend on expert/source agreement or rejection? → **Qualitative consensus**

## Key Structural Elements (All Templates)

Every template includes:
- `CLAIM_FORMAL` with `operator_note` (Rule 4)
- `FACT_REGISTRY` mapping report IDs to proof-script keys
- `compare()` for claim evaluation (Rule 7)
- `adversarial_checks` with `verification_performed` (Rule 5)
- JSON summary in `__main__` ending with `=== PROOF SUMMARY (JSON) ===`
