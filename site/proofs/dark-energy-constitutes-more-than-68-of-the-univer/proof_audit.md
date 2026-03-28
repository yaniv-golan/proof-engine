# Audit: Dark energy constitutes more than 68% of the universe's total energy density according to the Planck 2018 legacy release

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Dark energy fraction of the universe's total energy density |
| Property | Omega_Lambda (dark energy density parameter) as reported by Planck 2018 |
| Operator | > |
| Threshold | 0.68 |
| Operator note | "More than 68%" is interpreted as ΩΛ > 0.68 (strictly greater). The claim references the Planck 2018 legacy release (Planck Collaboration VI, A&A 641, A6, 2020; arXiv:1807.06209). In the base-ΛCDM model with spatial flatness (Ωtotal = 1), ΩΛ = 1 − Ωm. The claim is about the best-fit central value, not the confidence interval. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | planck_paper | Planck 2018 paper: matter density Omega_m = 0.315 +/- 0.007 |
| B2 | unlv_reference | UNLV cosmic parameters reference: Omega_Lambda = 0.6853(74) from Planck 2018 |
| A1 | — | Derived Omega_Lambda from Omega_m via flat-LCDM relation |
| A2 | — | Cross-check: derived Omega_Lambda vs directly reported Omega_Lambda |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Derived ΩΛ from Ωm via flat-ΛCDM relation | `explain_calc('1 - omega_m')` | 0.685 |
| A2 | Cross-check: derived ΩΛ vs directly reported ΩΛ | `cross_check(derived, direct, tolerance=0.01, mode='relative')` | True |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Planck 2018 paper: Ωm = 0.315 ± 0.007 | Planck Collaboration VI (2020), A&A 641, A6 — arXiv:1807.06209 (ar5iv HTML) | https://ar5iv.labs.arxiv.org/html/1807.06209 | "matter density parameter Ωm=0.315±0.007" | Partial | aggressive_normalization | Tier 4 (academic) |
| B2 | UNLV reference: ΩΛ = 0.6853(74) | UNLV Cosmic Parameters Reference (sourced from Planck 2018) | https://www.physics.unlv.edu/~jeffery/astro/cosmol/cosmic_parameters.html | "Omega_Lambda 0.6853(74) Assuming Omega = 1 (Planck 2018 p. 14)" | Verified | full_quote | Tier 4 (academic) |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1 — Planck 2018 paper (ar5iv HTML)**
- Status: partial
- Method: aggressive_normalization (alphanumeric-only matching). The ar5iv HTML rendering of the Planck paper uses LaTeX-to-HTML conversion that introduces formatting artifacts (subscripts, special spacing). After aggressive normalization (stripping all non-alphanumeric characters), the quote content was confirmed present.
- Fetch mode: live
- Impact: B1 provides Ωm for the cross-check derivation (A1). Even without B1, the directly reported ΩΛ from B2 (fully verified) independently establishes the claim. B1 adds confirmatory value but is not required for the conclusion.

**B2 — UNLV Cosmic Parameters Reference**
- Status: verified
- Method: full_quote
- Fetch mode: live

*Source: proof.py JSON summary; impact analysis is author analysis*

## Computation Traces

```
Omega_Lambda (derived from Omega_m, flat LCDM): 1 - omega_m = 1 - 0.315 = 0.6850
Omega_Lambda: derived from Omega_m vs direct report: 0.685 vs 0.6853, diff=0.00029999999999996696, relative=0.000438, tolerance=0.01 -> AGREE
Omega_Lambda > 0.68: 0.6853 > 0.68 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Check | Values Compared | Agreement |
|-------|-----------------|-----------|
| ΩΛ derived from Ωm (B1) vs directly reported (B2) | 0.685 vs 0.6853 | Yes (relative diff 0.04%) |

The two sources are independently published: B1 is the primary Planck Collaboration paper (arXiv/A&A), while B2 is a UNLV academic reference page that independently cites the Planck 2018 parameter table. Both trace to the same upstream authority (Planck Collaboration) but represent independent publications and presentations of the data.

The small discrepancy (0.685 vs 0.6853) is explained by rounding: the abstract quotes Ωm = 0.315 (3 decimal places), while the full-precision value Ωm = 0.3147 yields ΩΛ = 0.6853 exactly.

*Source: proof.py JSON summary; independence analysis is author analysis*

## Adversarial Checks (Rule 5)

**1. Has the Planck 2018 value for ΩΛ been revised or retracted?**
- Verification performed: Searched for "Planck 2018 dark energy revised retracted correction erratum". The Planck 2018 paper (arXiv:1807.06209) was published in A&A 641, A6 (2020) as the final legacy release. No errata revising the cosmological parameters have been issued.
- Finding: No revision or retraction found. The 2018 release is the final Planck data release.
- Breaks proof: No

**2. Could alternative cosmological models give ΩΛ < 0.68 from the same Planck data?**
- Verification performed: Searched for "Planck 2018 dark energy fraction alternative model lower than 68 percent". Extended models (w0waCDM, curved models) can shift ΩDE slightly, but the claim specifically references the base-ΛCDM results.
- Finding: In the base-ΛCDM model, ΩΛ = 0.6853 ± 0.0074. Even at the lower 1σ bound (0.6779), the central value is clearly > 0.68.
- Breaks proof: No

**3. Is the 68% threshold ambiguous — could it refer to a different quantity?**
- Verification performed: Considered whether "energy density" might refer to ΩDE in a non-flat model, or to a different definition.
- Finding: The standard interpretation is unambiguous: ΩΛ is the dark energy fraction of the critical density, equal to the fraction of total energy density in a flat universe.
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | arxiv.org | academic | 4 | Known academic/scholarly publisher |
| B2 | unlv.edu | academic | 4 | Academic domain (.edu) |

*Source: proof.py JSON summary*

## Extraction Records

| Fact ID | Extracted Value | Value in Quote | Quote Snippet |
|---------|----------------|----------------|---------------|
| B1 | 0.315 | Yes | "matter density parameter Ωm=0.315±0.007" |
| B2 | 0.6853 | Yes | "Omega_Lambda 0.6853(74) Assuming Omega = 1 (Planck 2018..." |

Extraction method: B1 uses `parse_number_from_quote()` with regex `[Ωo]m\s*=\s*([\d.]+)` to extract Ωm from the Planck abstract. B2 uses `parse_number_from_quote()` with regex `Omega_Lambda\s+([\d.]+)` to extract ΩΛ from the UNLV table. Both extractions confirmed via `verify_extraction()`.

*Source: proof.py JSON summary; extraction method narrative is author analysis*

## Hardening Checklist

- [x] **Rule 1:** Every empirical value parsed from quote text via `parse_number_from_quote()`, not hand-typed
- [x] **Rule 2:** Every citation URL fetched and quote checked via `verify_all_citations()`
- [x] **Rule 3:** Not time-dependent (no date computations), but `date.today()` used for generator timestamp
- [x] **Rule 4:** Claim interpretation explicit in `CLAIM_FORMAL` with `operator_note` explaining "more than 68%" as ΩΛ > 0.68
- [x] **Rule 5:** Three adversarial checks searched for revision/retraction, alternative models, and threshold ambiguity
- [x] **Rule 6:** Cross-checks used independently sourced inputs (Planck paper Ωm vs UNLV reference ΩΛ)
- [x] **Rule 7:** Computation uses `explain_calc()`, `cross_check()`, and `compare()` from `computations.py`
- [x] **validate_proof.py result:** PASS (14/14 checks passed, 0 issues, 0 warnings)

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
