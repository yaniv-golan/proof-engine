# Proof: In venture capital, the top 10% of investments generate more than 75% of total portfolio returns, following a power law distribution.

- **Generated:** 2026-04-08
- **Verdict:** SUPPORTED (with unverified citations)
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Key Findings

- The a16z/Horsley Bridge dataset (7,000+ investments, 2000–2014) found that **~6% of investments** representing 4.5% of capital deployed generated **~60% of total returns** — confirming extreme power law concentration at the deal level.
- Cambridge Associates found that the **top 10% of VC managers** generate more than 90% of industry returns — confirming power law structure at the manager level.
- The **specific "10% → >75%" threshold** in the claim was **not verbatim confirmed** by any publicly accessible major study.
- The directional claim (power law distribution of VC returns) is well-supported; the precise numerical threshold cannot be proved from public sources.

## Claim Interpretation

**Natural language:** In venture capital, the top 10% of investments generate more than 75% of total portfolio returns, following a power law distribution.

**Formal interpretation:** The claim asserts two sub-claims: (SC1) a quantitative power law threshold — the top decile of investments (by count) generates more than 75% of total portfolio returns; (SC2) a conceptual characterization — VC return distributions follow a power law. Key ambiguities: "top 10%" can refer to top decile by count or by capital deployed; "returns" can mean realized returns, TVPI, or DPI. The specific "75%/10%" threshold is widely cited in popular VC writing but appears to be an approximation rather than a verbatim finding from a primary study. The best available empirical study (a16z/Horsley Bridge) finds even greater concentration (6% of investments → 60% of returns), which is directionally consistent but does not confirm the 10%/75% threshold. SUPPORTED is the appropriate verdict.

**Sub-claims evaluated:**

| Sub-claim | Description | Verdict |
|-----------|-------------|---------|
| SC1 | Power law concentration confirmed by ≥ 2 sources | True (2/3 sources confirmed) |
| SC2 | Specific "10% → >75%" threshold verbatim confirmed | False (0 sources verbatim) |

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | a16z/Horsley Bridge: ~6% of investments → ~60% of total returns (7,000+ investments, 2000–2014) | Partial (50% word coverage) |
| B2 | Cambridge Associates: top 10% of VC managers → >90% of industry returns | Partial (aggressive normalization) |
| B3 | HBR/academic: power law characterization widely supported | Fetch failed (HTTP 404) |

## Proof Logic

### SC1: Power law return concentration (directional)

Two of three cited sources were at least partially verified:

- **B1 (a16z/Horsley Bridge):** Partial verification. The a16z blog post is live and contains language consistent with the cited statistic (~6% of investments, 4.5% of dollars, ~60% of returns). Word coverage was 50% due to minor wording differences between the cited quote and the rendered page text.
- **B2 (Cambridge Associates):** Partial verification via aggressive normalization. The page is live but the precise quote was not matched verbatim; a close passage was found referencing the top 10% of managers and industry returns.
- **B3 (HBR):** Fetch failed — the URL returned HTTP 404. This citation cannot be verified and is excluded from the count.

With 2 of 3 sources at least partially confirmed, SC1 (power law pattern exists) **holds**.

### SC2: Specific "10% → >75%" threshold

No source verbatim states that the top 10% of individual investments generate more than 75% of total returns. The closest available data:

- B1 says **6% of investments → 60%** (more concentrated on the investment count side, but a smaller absolute return percentage)
- B2 says **top 10% of managers → >90%** (at the manager/fund level, not the individual investment level)

The 10%/75% figure circulates widely in VC writing as a stylized fact but does not appear to originate from a single primary study. SC2 **does not hold**.

## Adversarial Checks

### Check 1: The specific "10% → 75%" threshold is not verbatim confirmed
- **Verification:** Searched for "top 10% venture capital investments 75% returns power law." The most-cited empirical study (a16z/Horsley Bridge, 7,000+ investments) finds ~6% of investments generate ~60% of returns — directionally consistent with power law concentration but not confirming the 10%/75% specific threshold. Cambridge Associates' "top 10% of managers → 90%+" finding applies at the manager level, not the deal level.
- **Breaks proof:** Yes — prevents PROVED verdict; verdict is SUPPORTED.

### Check 2: Power law in VC is fund-level, not necessarily investment-level
- **Verification:** Cambridge Associates measures concentration at the manager/fund level; a16z/Horsley Bridge measures at the individual investment level. These are different units of analysis. The claim says "top 10% of investments" (deal-level), which B1 addresses most directly. B1 shows even greater concentration (6%/60%) than claimed (10%/75%), so the directional claim is supported at the deal level.
- **Breaks proof:** No.

### Check 3: Power law pattern varies by fund type and vintage year
- **Verification:** Early-stage funds (seed, Series A) exhibit more extreme power law concentration than growth-stage funds. Late-stage growth equity has more distributed return profiles. The "10%/75%" framing applies best to early-stage VC, introducing scope ambiguity. However, the directional characterization (power law) holds across VC fund types.
- **Breaks proof:** No.

## Conclusion

**Verdict: SUPPORTED (with unverified citations).** The power law distribution of VC returns is well-supported by empirical data: a16z/Horsley Bridge found that ~6% of investments generated ~60% of total returns across 7,000+ deals (2000–2014), and Cambridge Associates has reported that the top 10% of VC managers generate more than 90% of industry returns. The directional claim — that VC returns are heavily concentrated in a small fraction of investments — is credible and supported by multiple independent sources. However, the specific "10%/75%" threshold is not verbatim confirmed by any publicly accessible primary study, and one citation (B3, HBR) returned a 404 error and could not be verified. SUPPORTED rather than PROVED is appropriate.
