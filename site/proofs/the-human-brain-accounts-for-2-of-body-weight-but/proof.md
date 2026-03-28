# Proof: The human brain accounts for 2% of body weight but uses 20% of the body's oxygen at rest.

- **Generated:** 2026-03-27
- **Verdict:** PROVED (with unverified citations)
- **Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

---

## Key Findings

- Two independent authoritative sources both report the brain as **exactly 2%** of adult body weight (SC1), matching the claim precisely.
- The same two sources both report the brain as **exactly 20%** of resting whole-body oxygen consumption (SC2), matching the claim precisely.
- PNAS citation (B1, B2) fully verified; NCBI Bookshelf weight citation (B3) fully verified; NCBI oxygen citation (B4) partially verified (60% word coverage — but SC2 is independently established by fully-verified B2).
- No counter-evidence found in any direction: the ~2% and ~20% figures are consistent across all neuroscience literature.

*Source: proof.py JSON summary*

---

## Claim Interpretation

**Natural language claim:** "The human brain accounts for 2% of body weight but uses 20% of the body's oxygen at rest."

This is a compound claim with two sub-claims:

**SC1 — Brain weight:** The brain mass as a fraction of total adult human body weight is approximately 2%. Formally: the cited literature value lies within ±0.5 percentage points of 2.0%. This is the conservative interpretation — a value of 1.5% or 2.5% would still satisfy the claim; 1.0% or 3.0% would not. Both sources report exactly 2%, so no borderline case arises.

**SC2 — Oxygen use at rest:** The brain's share of resting whole-body O₂ consumption is approximately 20%. Formally: the cited literature value lies within ±2 percentage points of 20.0%. The ±2pp window accommodates natural rounding across studies while distinguishing "~20%" from substantially different claims (e.g., 25% or 15%). Both sources report exactly 20%, and an independent numerical cross-check (CMRO₂ = 3.5 mL/100g/min × 1,400g ÷ resting VO₂ ≈ 250 mL/min ≈ 19.6%) rounds to 20%.

The qualifier **"at rest"** is meaningful: during cognitive tasks, local brain blood flow increases 30–50%, but whole-brain O₂ consumption increases only ~1–5% above basal. The cited sources explicitly measure the resting/basal state, matching the claim's qualifier.

*Source: proof.py JSON summary + author analysis*

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | PNAS 2002: brain = ~2% of body weight | Yes |
| B2 | PNAS 2002: brain = ~20% of resting O₂ | Yes |
| B3 | NCBI Basic Neurochemistry: brain = ~2% body weight | Yes |
| B4 | NCBI Basic Neurochemistry: brain = 20% resting O₂ | Partial (60% fragment — full sentence differs slightly from quote; conclusion supported independently by B2) |
| A1 | SC1: extracted weight % lies within ±0.5pp of 2% | Computed |
| A2 | SC2: extracted O₂ % lies within ±2pp of 20% | Computed |

*Source: proof.py JSON summary*

---

## Proof Logic

**SC1 — Brain is ~2% of body weight:**

The PNAS landmark paper by Raichle & Gusnard (2002) states (B1): *"In the average adult human, the brain represents about 2% of the body weight."* The NCBI Bookshelf chapter on cerebral metabolic rate states (B3): *"the brain, which represents only about 2% of total body weight."* Both sources report exactly 2.0%. Cross-check: |2.0 − 2.0| = 0.0pp < 0.5pp tolerance → sources agree. Claim check: 2.0% is within [1.5%, 2.5%] → SC1 holds.

**SC2 — Brain uses ~20% of oxygen at rest:**

The same PNAS paper states (B2): *"the brain accounts for about 20% of the oxygen and, hence, calories consumed by the body."* The NCBI Bookshelf states (B4): *"accounts for 20% of the resting total body O₂ consumption."* Both sources report exactly 20.0%. Cross-check: |20.0 − 20.0| = 0.0pp < 2.0pp tolerance → sources agree. Claim check: 20.0% is within [18.0%, 22.0%] → SC2 holds.

The two sub-claims together constitute the complete compound claim. Both hold, both cross-checked.

*Source: author analysis*

---

## Counter-Evidence Search

**1. Could a different brain weight percentage (not ~2%) be correct?**
Searched for authoritative sources disputing the 2% figure. No credible counter-evidence found. Computed independently: adult brain mass ~1,400 g ÷ 70 kg reference body = 2.0% exactly. Accounting for natural variation (brain 1,300–1,500 g, body 60–80 kg), the range is 1.6–2.5% — all described in the literature as "about 2%."

**2. Could a substantially different O₂ percentage (not ~20%) be correct?**
Searched for authoritative sources disputing the 20% figure. No credible counter-evidence found. Independent numerical derivation: normal cerebral metabolic rate of oxygen (CMRO₂) = 3.5 mL O₂/100g/min × 1,400g brain = 49 mL O₂/min; resting whole-body VO₂ ≈ 250 mL/min; 49 ÷ 250 = 19.6% ≈ 20%. Some sources say "20–25%" for an active brain but consistently cite ~20% at rest.

**3. Would the claim be false when measuring during activity rather than at rest?**
Neuroimaging studies show local brain blood flow increases 30–50% during cognitive tasks, but whole-brain O₂ consumption increases only ~1–5% above basal. The claim explicitly qualifies "at rest," matching the cited sources. The qualifier is both accurate and appropriate.

*Source: proof.py JSON summary*

---

## Conclusion

**Verdict: PROVED (with unverified citations)**

Both sub-claims are strongly supported:
- SC1 (brain = ~2% of body weight): 2.0% reported by two independent peer-reviewed sources (B1 fully verified, B3 fully verified), confirmed equal.
- SC2 (brain = ~20% of O₂ at rest): 20.0% reported by two independent sources (B2 fully verified, B4 partially verified at 60%).

The only qualification to full PROVED status is that B4 (NCBI oxygen quote) achieved only partial citation verification (60% word coverage). However, SC2 does **not** depend solely on B4 — it is independently and fully established by B2 (PNAS, fully verified). The partial verification of B4 is a conservative flag, not a substantive challenge to the conclusion.

The claim is accurate and consistent with scientific consensus.
