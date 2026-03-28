# Proof: The theoretical vacuum energy density from QFT exceeds the observed cosmological-constant value by more than 10^120 orders of magnitude

- **Generated**: 2026-03-28
- **Verdict**: DISPROVED (with unverified citations)
- **Audit trail**: [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Key Findings

- The QFT vacuum energy density (Planck cutoff) is ~2.93 x 10^111 J/m^3; the observed value is ~5.36 x 10^-10 J/m^3 — a ratio of ~5.5 x 10^120, or **~121 orders of magnitude**.
- The claim states the discrepancy is "more than 10^120 orders of magnitude," which literally means the ratio exceeds 10^(10^120). Since 121 << 10^120, the claim is **false**.
- The correct statement is that the discrepancy is "about 120 orders of magnitude" (a *ratio* of ~10^120), not "10^120 orders of magnitude."
- Even the maximum literature estimate (~122 orders of magnitude, Planck cutoff) falls vastly short of 10^120 orders of magnitude. Modern Lorentz-invariant methods reduce the discrepancy to ~55-60 orders.

## Claim Interpretation

**Natural language**: "The theoretical vacuum energy density from quantum field theory exceeds the observed cosmological-constant value inferred from Type Ia supernovae by more than 10^120 orders of magnitude."

**Formal interpretation**: In standard mathematical usage, "N orders of magnitude" denotes a ratio of 10^N. The claim asserts the number of orders of magnitude in the ratio (theoretical / observed vacuum energy density) exceeds 10^120. This would require a ratio greater than 10^(10^120).

This is almost certainly a conflation of two different expressions: "120 orders of magnitude" (the standard description of the cosmological constant problem) and "a factor of 10^120." We evaluate the claim as literally stated.

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Observed vacuum energy density from Planck satellite (Wikipedia, Cosmological constant problem) | Yes |
| B2 | Observed dark energy density (Wikipedia, Dark energy) | Partial (aggressive normalization — Unicode superscripts in source) |
| B3 | Observed vacuum energy in GeV^4 units (CosmoVerse) | Yes |
| A1 | QFT vacuum energy density with Planck cutoff | Computed: 2.93 x 10^111 J/m^3 |
| A2 | Ratio of theoretical to observed vacuum energy density | Computed: 5.48 x 10^120 |
| A3 | Number of orders of magnitude in the discrepancy | Computed: 120.74 |
| A4 | Cross-check: ratio computed in GeV^4 units | Computed: 121.15 orders of magnitude |

## Proof Logic

The proof proceeds in three stages:

**1. Compute the theoretical QFT vacuum energy density (A1).** Using CODATA fundamental constants, we compute the Planck mass M_P = sqrt(hbar c / G) and derive the zero-point energy density of a scalar quantum field with a Planck-scale ultraviolet cutoff: rho_QFT = M_P^4 / (16 pi^2). Converting from natural units (GeV^4) to SI (J/m^3) yields rho_QFT ~ 2.93 x 10^111 J/m^3.

**2. Establish the observed vacuum energy density (B1, B2, B3).** The observed dark energy density, inferred from Type Ia supernovae distance measurements and confirmed by Planck satellite CMB observations, is rho_obs ~ 5.36 x 10^-10 J/m^3 (equivalently, ~10^-47 GeV^4). Multiple independent sources confirm this value (B1, B2 — independently sourced).

**3. Compute the ratio and evaluate the claim (A2, A3).** The ratio rho_QFT / rho_obs ~ 5.5 x 10^120, giving ~120.7 orders of magnitude. A cross-check in GeV^4 units (A4) gives 121.1 orders of magnitude — consistent within 0.3%. The claim requires this number to exceed 10^120. Since 120.7 << 10^120 (by about 118 orders of magnitude), the claim is disproved.

## Counter-Evidence Search

1. **Is "10^120 orders of magnitude" standard in physics?** Searched physics literature and textbooks. The standard phrasing is "120 orders of magnitude" or "a factor of 10^120." No reputable source uses "10^120 orders of magnitude."

2. **Could any regularization scheme produce a larger discrepancy?** The maximum in the literature is ~122 orders of magnitude (Planck cutoff). Modern Lorentz-invariant calculations give only ~55-60 orders. No known method produces a discrepancy approaching 10^120 orders of magnitude.

3. **Could the observed value be smaller than cited?** The observed value (~5.36 x 10^-10 J/m^3) is well-established across multiple sources. Even if it were exactly zero, the ratio would be undefined (infinite), not 10^(10^120).

## Conclusion

**DISPROVED (with unverified citations).** The theoretical vacuum energy density from QFT (with Planck-scale cutoff) exceeds the observed cosmological constant by approximately **121 orders of magnitude** — a ratio of roughly 10^121. This is the famous "cosmological constant problem," often described as "the worst prediction in physics."

However, the claim states the discrepancy is "more than 10^120 orders of magnitude," which would require a ratio exceeding 10^(10^120). The actual ~121 orders of magnitude falls short of 10^120 orders of magnitude by a factor too vast to meaningfully express. The claim appears to conflate "a factor of 10^120" with "10^120 orders of magnitude."

The correct formulation is: the discrepancy is **about 120 orders of magnitude** (or equivalently, the ratio is about 10^120).

One citation (B2, Wikipedia Dark energy) was verified only via aggressive normalization due to Unicode superscripts in the source HTML. The disproof does not depend on B2 — it follows from the Type A computation (A1-A3) and the independently verified B1 and B3 sources.

Note: 1 citation comes from an unclassified source (B3, CosmoVerse). See Source Credibility Assessment in the audit trail.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
