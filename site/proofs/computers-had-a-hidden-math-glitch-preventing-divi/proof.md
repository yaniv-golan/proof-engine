# Proof: Computers had a hidden "math glitch" preventing division by zero until it was patched in 2026.

- **Generated:** 2026-03-28
- **Verdict:** DISPROVED (with unverified citations)
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

---

## Key Findings

- Division-by-zero behavior has been **intentionally defined** in computer hardware since at least the Intel 8086 (1978) and the IBM S/360 (1964) — it is not a "glitch" (B3).
- IEEE 754-1985 explicitly standardized floating-point division by zero as returning ±infinity (or NaN for 0/0), with an optional exception flag — 40 years before the claimed "2026 patch" (B1, B2).
- A thorough search of CPU errata databases, OS patch notes (including Microsoft March 2026 Patch Tuesday), and IEEE revision history found **zero credible sources** documenting a 2026 patch for division-by-zero behavior.
- All 3 independent sources refuting the claim were verified (1 fully, 2 by fragment matching). The disproof threshold of 3 was met.

---

## Claim Interpretation

**Natural language claim:** *Computers had a hidden "math glitch" preventing division by zero until it was patched in 2026.*

**Formal interpretation:** The claim asserts two sub-claims:
- **SC1:** Division-by-zero prevention was a hidden, unintentional "math glitch" (i.e., not deliberate design).
- **SC2:** This glitch was patched in 2026.

Both sub-claims must be true for the overall claim to hold.

**Operator note:** The claim is refuted if 3 or more independent, verified sources document that division-by-zero behavior has been intentionally defined for decades before 2026, AND zero credible sources document a "2026 patch." The threshold of 3 sources is conservative given this is a well-documented technical standard. The disproof logic: `disproof_established = (n_refuting >= 3)`; `claim_holds = NOT disproof_established`.

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Wikipedia: IEEE 754 — division by zero is a defined exception type, not a glitch | Partial (fragment match via aggressive normalization) |
| B2 | Wikipedia: Division by zero — IEEE arithmetic defines well-specified, deterministic behavior | Partial (fragment match via aggressive normalization) |
| B3 | OSDev Wiki: x86 Divide Error (#DE) — standard hardware exception since early x86 | Yes (full quote, via Wayback Machine) |
| A1 | Count of verified sources refuting the claim (SC1 + SC2) | Computed: 3 of 3 sources verified |
| A2 | Claim holds evaluation: disproof established => original claim does not hold | Computed: claim_holds = False (disproof_established = True) |

---

## Proof Logic

**SC1 — Division-by-zero is intentional design, not a hidden glitch:**

The IEEE 754 standard (ratified 1985) explicitly defines five exception types including "division by zero" (B1). This exception category means the CPU raises a defined signal when a program attempts to divide by zero — the result is fully specified (±infinity for floating-point, or a hardware trap for integers). This is deliberate architecture, not an accidental side effect.

The Wikipedia article on Division by Zero confirms: "in IEEE arithmetic, division of 0/0 or ∞/∞ results in NaN, but otherwise division always produces a well-defined result" (B2). The phrase "well-defined result" is the opposite of "hidden glitch."

The OSDev Wiki entry for x86 processor exceptions (B3) documents: "The Division Error occurs when dividing any number by 0 using the DIV or IDIV instruction, or when the division result is too large to be represented in the destination." This exception (#DE, vector 0) has been part of the x86 architecture since the Intel 8086 (1978). It is specified in Intel's official programmer's manual — it cannot be "hidden."

**SC2 — No 2026 patch exists:**

A systematic search of patch records, CPU errata, and standards revisions found no 2026 patch for division-by-zero behavior in any major CPU architecture, operating system, or IEEE 754 revision. Microsoft's March 2026 Patch Tuesday addressed 79 security vulnerabilities (SQL Server, .NET, Windows), none related to arithmetic behavior. No IEEE 754 revision was issued in 2026.

**Combined verdict:** Both sub-claims of the original claim are false. The claim is **DISPROVED**.

---

## Counter-Evidence Search

**Search 1 — "2026 patch" for division by zero:**
Searched for "division by zero patch 2026," "CPU divide by zero fix 2026," "IEEE 754 division by zero bug patch 2026," and "computers math glitch division zero 2026 patch." Also reviewed Microsoft March 2026 Patch Tuesday (BleepingComputer), which listed 79 CVEs — none related to arithmetic division-by-zero behavior. **Finding:** The "2026 patch" component of the claim is entirely fabricated. No such patch exists.

**Search 2 — Obscure CPU microcode errata in 2026:**
Searched for "Intel errata division by zero 2026," "AMD microcode division by zero 2026," "ARM Cortex divide by zero errata 2026." **Finding:** No hardware errata from Intel, AMD, or ARM in 2026 pertains to division-by-zero behavior. The x86 #DE exception has been stable since the Intel 8086 (1978). The 1994 Pentium FDIV bug was a floating-point division *accuracy* issue for specific operand pairs — not a division-by-zero issue — and was resolved in 1994.

**Search 3 — "Hidden glitch" framing in mainstream CS:**
Searched for "division by zero glitch CPU hidden," "division by zero unintentional computer design," "division by zero bug computer history." **Finding:** No mainstream computer science literature characterizes division-by-zero handling as a "hidden glitch." IBM S/360 (1964) and Intel 8086 (1978) already defined this as intentional trap behavior.

---

## Conclusion

**Verdict: DISPROVED (with unverified citations)**

The claim is false on both sub-claims:
- **SC1 (hidden glitch):** Division-by-zero behavior has been intentional, documented hardware and software design since at least 1964. IEEE 754 (1985) formally standardizes it as returning ±infinity or raising an exception flag.
- **SC2 (2026 patch):** No 2026 patch for division-by-zero behavior exists in any CPU architecture, operating system, or IEEE standard.

Two of three supporting citations (B1 and B2, both Wikipedia) received "partial" verification status due to Unicode normalization during quote matching. The third citation (B3, OSDev Wiki) was fully verified. The disproof conclusion does not depend solely on the partially-verified citations: B3 independently and fully confirms intentional exception design. B1 and B2 provide corroborating evidence about the IEEE 754 standard.

Note: 1 citation (B3) comes from an unclassified domain (osdev.org, Tier 2). OSDev Wiki is a well-known technical reference widely cited in operating-systems education; the quote itself was fully verified against archived page content.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
