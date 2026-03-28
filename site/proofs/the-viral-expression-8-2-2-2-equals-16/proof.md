# Proof: The viral expression "8 ÷ 2(2+2)" equals 16

- **Generated:** 2026-03-28
- **Verdict:** PROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

---

## Key Findings

- Under standard PEMDAS/BODMAS (left-to-right equal precedence for × and ÷), `8 ÷ 2(2+2)` evaluates to **16**.
- Step-by-step: parentheses first → `8 ÷ 2 × 4`; then left-to-right → `(8÷2)×4 = 4×4 = 16`.
- Two independent cross-checks (algebraic rearrangement and Python built-in evaluation) both confirm **16**.
- The alternative implicit-multiplication-first convention gives **1**, not 16 — the expression is genuinely ambiguous, and the answer depends on which convention you apply.

---

## Claim Interpretation

**Natural language:** The viral expression "8 ÷ 2(2+2)" equals 16.

**Formal interpretation:**

| Field | Value |
|---|---|
| Subject | 8 ÷ 2(2+2) |
| Property | Arithmetic value under standard PEMDAS/BODMAS |
| Operator | == |
| Threshold | 16 |

**Convention note:** The expression `8 ÷ 2(2+2)` is famously ambiguous because of the notation `2(2+2)` (a coefficient written directly against a parenthesis, called *juxtaposition*). Two conventions exist:

1. **Standard PEMDAS/BODMAS (this proof's convention):** Multiplication and division have equal precedence and are evaluated left-to-right. `2(2+2)` means `× (2+2)`, so the expression parses as `(8 ÷ 2) × (2+2) = 4 × 4 = 16`.

2. **Implicit-multiplication-first convention:** Juxtaposition binds more tightly than explicit division. The expression parses as `8 ÷ [2 × (2+2)] = 8 ÷ 8 = 1`.

This proof adopts convention (1) — the standard left-to-right rule used by Python, most scientific calculators, and ISO 80000-2. Convention (2) is documented in the Counter-Evidence section.

---

## Evidence Summary

| ID | Fact | Verified |
|---|---|---|
| A1 | Left-to-right PEMDAS evaluation of 8 ÷ 2(2+2): (8÷2)×(2+2) | Computed: 16.0 |
| A2 | Algebraic rearrangement cross-check using commutativity: 8×(2+2)÷2 | Computed: 16.0 |
| A3 | Alternative convention (implicit multiplication higher precedence): 8÷[2×(2+2)] | Computed: 1.0 (adversarial reference) |

---

## Proof Logic

**Step 1 — Parentheses (P in PEMDAS):**
Evaluate the grouped sub-expression first: `(2+2) = 4`.
The expression reduces to `8 ÷ 2 × 4`.

**Step 2 — Left-to-right (equal precedence for ÷ and ×):**
The leftmost operation is performed first: `8 ÷ 2 = 4` (A1, step 2a).
Then the remaining multiplication: `4 × 4 = 16` (A1, step 2b).

**Cross-check via algebraic rearrangement (A2):**
Since `÷ b` is equivalent to `× (1/b)`, multiplication is commutative, so:
`8 ÷ 2 × (2+2) = 8 × (2+2) ÷ 2 = 32 ÷ 2 = 16`.
This uses a completely different computation order and confirms the same result.

**Cross-check via Python evaluation:**
Python evaluates `8 / 2 * (2 + 2)` as `16.0` using CPython's left-to-right IEEE 754 semantics — identical to the primary method, independently executed.

All three methods agree: **16** (A1, A2, Python check).

---

## Counter-Evidence Search

**Alternative convention (implicit multiplication higher precedence):**
Under the convention where juxtaposition binds more tightly than explicit division, the expression `8 ÷ 2(2+2)` parses as `8 ÷ [2 × (2+2)] = 8 ÷ 8 = 1`. This convention is used by the American Mathematical Society (AMS) house style and is common in academic physics writing where `a/bc` means `a/(bc)`. Wolfram Alpha returns 16 by default for this expression but acknowledges the ambiguity exists. This alternative does *not* break the proof — the proof explicitly states it applies the standard PEMDAS left-to-right convention.

**ISO 80000-2 standard check:**
ISO 80000-2:2019 (Mathematical signs and symbols) specifies left-to-right evaluation for sequences of × and ÷ without parentheses: `a × b ÷ c = (a × b) ÷ c`. The standard also explicitly recommends using parentheses to avoid ambiguity in expressions involving juxtaposition. No major international standard mandates the implicit-multiplication-first convention for this form.

**Floating-point precision:**
All operands (8, 2, 2, 2) are exactly representable as IEEE 754 doubles. All intermediate values are exact: `8/2 = 4.0`, `2+2 = 4`, `4.0 × 4 = 16.0`. No rounding error occurs; `16.0 == 16` is mathematically exact.

---

## Conclusion

**Verdict: PROVED** under the standard PEMDAS/BODMAS left-to-right convention.

`8 ÷ 2(2+2) = (8 ÷ 2) × (2+2) = 4 × 4 = 16`.

Two independent computational cross-checks confirm this result. No floating-point errors are possible. No authoritative standard mandates the alternative interpretation.

**Important caveat:** The expression is genuinely ambiguous in mathematical notation. The answer is 1 under the implicit-multiplication-first convention, which is also in real use. The viral controversy stems from this real ambiguity — this proof proves the answer *given the stated convention*, not that the answer is unambiguously 16 in all contexts. The well-formed version of the expression that is unambiguous is either `(8 ÷ 2)(2+2)` or `8 ÷ (2(2+2))`.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
