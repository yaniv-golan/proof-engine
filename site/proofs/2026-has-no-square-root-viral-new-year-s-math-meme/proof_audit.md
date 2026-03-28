# Audit: 2026 has no square root

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| subject | 2026 |
| property | existence of an integer n such that n² = 2026 |
| operator | == |
| threshold | False |
| operator_note | The claim is interpreted as: there is no integer n ≥ 0 satisfying n² = 2026 (equivalently, 2026 is not a perfect square). In ℝ or ℂ, 2026 trivially has square roots (√2026 ≈ 45.011…), so the real/complex interpretation makes the claim false. The viral meme's mathematical punch-line — that 2025 = 45² is a perfect square and 2026 is not — only makes sense under the integer interpretation, which is therefore the formal claim. Proof succeeds when both independent methods agree: no integer n satisfies n² = 2026. |

---

## Fact Registry

| ID | Label | Type |
|----|-------|------|
| A1 | Floor-sqrt bound check: no integer squares to 2026 | Computed |
| A2 | Quadratic-residue mod-16 check: 2026 mod 16 is not a perfect-square residue | Computed |
| A3 | Context: 2025 = 45² confirming the adjacent perfect square | Computed |

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Floor-sqrt bound check: no integer squares to 2026 | math.isqrt() floor-sqrt bound check | 45² = 2025 ≠ 2026, 46² = 2116 ≠ 2026 → no integer square root |
| A2 | Quadratic-residue mod-16 check: 2026 mod 16 is not a perfect-square residue | Quadratic residues mod 16 | 2026 mod 16 = 10; QR₁₆ = {0,1,4,9}; 10 ∉ QR₁₆ → not a perfect square |
| A3 | Context: 2025 = 45² confirming the adjacent perfect square | math.isqrt() perfect-square confirmation | 45² = 2025 → 2025 IS a perfect square (adjacent year) |

*No Type B (empirical) facts — pure-math proof.*

---

## Computation Traces

Verbatim output from `python proof.py`:

```
  A1: floor_root² (lower bound): floor_root ** 2 = 45 ** 2 = 2025
  A1: (floor_root+1)² (upper bound): (floor_root + 1) ** 2 = (45 + 1) ** 2 = 2116

A1: math.isqrt(2026) = 45
A1: 45² = 2025  (must equal 2026 for a perfect square)
A1: 46² = 2116  (next perfect square)
A1: 2025 < 2026 < 2116  →  no integer square root exists
  A1: is_perfect_square (primary): False == False = True

A2: Quadratic residues mod 16 = [0, 1, 4, 9]
  A2: 2026 mod 16: n % 16 = 2026 % 16 = 10
A2: 2026 mod 16 = 10  (quadratic residues mod 16: [0, 1, 4, 9])
A2: 10 ∈ QR_16? False  →  is_perfect_square = False
  A2: is_perfect_square (mod-16 cross-check): False == False = True

✓ Both independent methods agree: 2026 is NOT a perfect square.

A3: math.isqrt(2025) = 45
A3: 45² = 2025  →  2025 IS a perfect square: True
  A3: 2025 is a perfect square (context): True == True = True
  Verdict: primary and cross-check agree on is_perfect_square: False == False = True
  Verdict: 2026 is not a perfect square: False == False = True
```

---

## Adversarial Checks (Rule 5)

| # | Question | Search/Verification Performed | Finding | Breaks Proof? |
|---|----------|-------------------------------|---------|---------------|
| 1 | Does 2026 have a real or complex square root? Could that vindicate the claim? | Computed math.sqrt(2026) ≈ 45.011109… and noted that every positive real has exactly two real square roots (±). In ℂ every number has square roots. The meme's mathematical joke depends on 2025 being special as a perfect square year; the intended meaning is unambiguously the integer/perfect-square sense. | √2026 ≈ 45.011… exists in ℝ but is irrational. The real/complex interpretations make the claim FALSE; only the integer interpretation makes it TRUE and mathematically interesting. The formal claim is correctly scoped to integers. | No |
| 2 | Are there any integers near 2026 that are perfect squares, confirming 2026 is genuinely between two? | Computed 45² = 2025 and 46² = 2116. Checked that 2025 < 2026 < 2116 with no integer between 45 and 46, confirming no gap is missed. | 44² = 1936, 45² = 2025, 46² = 2116, 47² = 2209. 2026 falls strictly between consecutive perfect squares 2025 and 2116. Fully consistent with the primary proof — no counterexample. | No |
| 3 | Could a modular-arithmetic error give a false 'not a perfect square' result? | Verified the set PERFECT_SQUARE_RESIDUES_MOD16 by enumerating all k in 0..15 and computing k² mod 16. Result: {0,1,4,9}. Confirmed 2026 mod 16 = 10 by direct subtraction: 2026 − 126×16 = 2026 − 2016 = 10. Checked that 10 ∉ {0,1,4,9} by inspection. | The residue set {0,1,4,9} and 2026 mod 16 = 10 are both straightforward to verify by hand. No error — the modular argument is sound. | No |
| 4 | Is math.isqrt() reliable for four-digit numbers? | math.isqrt() is specified in PEP 578 / Python 3.8+ and computes the exact integer square root (no floating-point rounding). For n = 2026, cross-checked: floor(√2026) = floor(45.011…) = 45. Since 45² = 2025 and 46² = 2116, and math.isqrt(2026) = 45, the result is correct. | math.isqrt() is exact for all non-negative integers (arbitrary precision). No floating-point risk. Result for 2026 verified by manual bounding. | No |

---

## Cross-Check Independence Note

Methods A1 and A2 are **structurally independent**:

- **A1** computes `math.isqrt(2026)` and squares the result — this uses integer square root arithmetic.
- **A2** computes `2026 % 16` and checks membership in the set of quadratic residues mod 16 — this uses only modular reduction, with no square root operations.

The two methods share no intermediate values. A bug in A1's floor-sqrt logic would not affect A2's modular check, and vice versa. Their agreement on `is_perfect_square = False` is a genuine independent confirmation.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
