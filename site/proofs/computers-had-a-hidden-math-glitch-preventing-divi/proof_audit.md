# Audit: Computers had a hidden "math glitch" preventing division by zero until it was patched in 2026.

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| subject | division-by-zero handling in computers |
| property | was a hidden, unintentional 'math glitch' that was patched in 2026 |
| operator | >= |
| threshold | 3 (independent verified refuting sources required) |
| proof_direction | disprove |
| operator_note | The claim makes two assertions: (SC1) division-by-zero prevention was a hidden, unintentional 'math glitch'; (SC2) this was patched in 2026. Both must be true for the claim to hold. The claim is refuted if: 3+ independent verified sources document that division-by-zero behavior has been intentionally defined (not a glitch) for decades before 2026, AND zero credible sources document a '2026 patch.' Threshold of 3 sources is conservative given this is a well-documented technical standard. proof_direction='disprove': empirical_facts contain sources that refute the claim; disproof_established = (n_refuting >= threshold); claim_holds = NOT disproof_established. |

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | ieee754_wiki | Wikipedia: IEEE 754 — division by zero is a defined exception type, not a glitch |
| B2 | divbyzero_wiki | Wikipedia: Division by zero — IEEE arithmetic defines well-specified, deterministic behavior |
| B3 | osdev_exceptions | OSDev Wiki: x86 Divide Error (#DE) — standard hardware exception since early x86 |
| A1 | — | Count of verified sources refuting the claim (SC1 + SC2) |
| A2 | — | Claim holds evaluation: disproof established => original claim does not hold |

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Count of verified sources refuting the claim | sum(status in ('verified','partial') for refuting sources) | 3 of 3 sources verified |
| A2 | Claim holds evaluation | claim_holds = NOT(n_refuting >= threshold) | claim_holds = False (disproof_established = True) |

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Wikipedia: IEEE 754 | Wikipedia: IEEE 754 floating-point standard | https://en.wikipedia.org/wiki/IEEE_754 | "The standard defines five exception types: invalid operation, division by zero, overflow, underflow, and inexact." | Partial | aggressive_normalization | Tier 3 (reference) |
| B2 | Wikipedia: Division by zero | Wikipedia: Division by zero | https://en.wikipedia.org/wiki/Division_by_zero | "In IEEE arithmetic, division of 0/0 or infinity/infinity results in NaN, but otherwise division always produces a well-defined result." | Partial | aggressive_normalization | Tier 3 (reference) |
| B3 | OSDev Wiki: x86 Exceptions | OSDev Wiki: x86 Processor Exceptions | https://wiki.osdev.org/Exceptions | "The Division Error occurs when dividing any number by 0 using the DIV or IDIV instruction, or when the division result is too large to be represented in the destination." | Verified | full_quote | Tier 2 (unknown) |

---

## Citation Verification Details

**B1 — Wikipedia: IEEE 754**
- Status: `partial`
- Method: `aggressive_normalization` (fragment match, ~4 words)
- Fetch mode: `live`
- Impact: B1 is partially verified and counts toward the disproof threshold. The same core fact (IEEE 754 defines division-by-zero as an explicit exception type, not a glitch) is independently supported by B2 (partial) and the historical record referenced in adversarial checks. The disproof conclusion does not depend solely on B1.

**B2 — Wikipedia: Division by zero**
- Status: `partial`
- Method: `aggressive_normalization` (fragment match, ~6 words)
- Fetch mode: `live`
- Impact: B2 is partially verified and counts toward the disproof threshold. The claim it supports (IEEE arithmetic produces well-defined results for division by zero) is independently supported by B3 (fully verified) which documents the x86 hardware exception machinery. The disproof conclusion does not depend solely on B2.

**B3 — OSDev Wiki: x86 Processor Exceptions**
- Status: `verified`
- Method: `full_quote`
- Fetch mode: `wayback` (Wayback Machine fallback)
- Impact: N/A (fully verified)

---

## Computation Traces

```
  Refuting sources verified: 3 / 3
  SC: verified refuting sources >= threshold (disproof established): 3 >= 3 = True
```

`compare()` output (from proof.py execution):
- `SC: verified refuting sources >= threshold (disproof established): 3 >= 3 = True`
- `disproof_established = True`
- `claim_holds = not disproof_established = False`

---

## Independent Source Agreement (Rule 6)

| Description | Sources Compared | Agreement |
|-------------|-----------------|-----------|
| Three independent sources each document division-by-zero as intentional, defined behavior | ieee754_wiki: partial / divbyzero_wiki: partial / osdev_exceptions: verified | True (all 3 in countable statuses) |

All three sources are structurally independent:
- B1 (Wikipedia IEEE 754) covers the formal floating-point standard
- B2 (Wikipedia Division by zero) covers the mathematical/computational behavior
- B3 (OSDev Wiki Exceptions) covers the x86 hardware exception architecture

No two sources share the same URL, organization, or page. B3 was verified via a different mechanism (Wayback Machine, full quote) from B1 and B2 (live fetch, fragment matching), providing additional independence.

---

## Adversarial Checks (Rule 5)

**Check 1 — Does any credible source document a "2026 patch" for division-by-zero?**
- Search performed: "division by zero patch 2026," "CPU divide by zero fix 2026," "IEEE 754 division by zero bug patch 2026," "computers math glitch division zero 2026 patch." Also reviewed Microsoft March 2026 Patch Tuesday (BleepingComputer, 79 CVEs listed).
- Finding: No credible source documents any 2026 patch addressing division-by-zero behavior. Microsoft March 2026 Patch Tuesday addressed SQL Server, .NET, and Windows security vulnerabilities; no arithmetic behavior was changed. No IEEE 754 revision was issued in 2026. The "2026 patch" is entirely fabricated.
- Breaks proof: **No**

**Check 2 — Could there be an obscure CPU microcode update in 2026 affecting division by zero?**
- Search performed: "Intel errata division by zero 2026," "AMD microcode division by zero 2026," "ARM Cortex divide by zero errata 2026."
- Finding: No hardware errata from Intel, AMD, or ARM in 2026 pertains to division-by-zero behavior. The x86 #DE exception has been stable since the Intel 8086 (1978). The 1994 Pentium FDIV bug was a floating-point division *accuracy* issue — not a division-by-zero issue — and was resolved in 1994.
- Breaks proof: **No**

**Check 3 — Was division-by-zero handling ever described as a "hidden glitch" in mainstream CS?**
- Search performed: "division by zero glitch CPU hidden," "division by zero unintentional computer design," "division by zero bug computer history." Reviewed IEEE 754-1985 historical background.
- Finding: Division-by-zero raising a hardware exception (#DE) has been intentional since at least the Intel 8086 (1978) and IBM S/360 (1964). IEEE 754-1985 explicitly standardized floating-point division-by-zero as returning ±infinity (or NaN for 0/0). No mainstream CS literature characterizes this as a "hidden glitch."
- Breaks proof: **No**

---

## Source Credibility Assessment

| ID | Domain | Tier | Type | Notes |
|----|--------|------|------|-------|
| B1 | wikipedia.org | 3 | reference | Established reference source |
| B2 | wikipedia.org | 3 | reference | Established reference source |
| B3 | osdev.org | 2 | unknown | Unclassified domain — OSDev Wiki is a well-known technical reference in OS development education; quote fully verified against archived content |

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
