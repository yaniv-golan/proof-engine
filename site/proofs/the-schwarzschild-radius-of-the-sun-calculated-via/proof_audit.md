# Audit: The Schwarzschild radius of the Sun lies strictly between 2.95 km and 2.96 km

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Schwarzschild radius of the Sun |
| Property | rs = 2GM/c² in kilometres |
| Operator | compound: > AND < |
| Threshold (lower) | 2.95 |
| Threshold (upper) | 2.96 |
| Operator note | "strictly between" means rs > 2.95 AND rs < 2.96 (both strict). CODATA does not publish solar mass; IAU 2015 Resolution B3 nominal GM☉^N is used instead, with M☉ derived as GM☉^N / G. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | nist_G | Newtonian gravitational constant G (2022 CODATA) |
| B2 | nist_c | Speed of light c (2022 CODATA, exact) |
| B3 | iau_GM_sun | Nominal solar mass parameter GM☉^N (IAU 2015 Resolution B3) |
| B4 | wiki_solar_mass | Solar mass cross-check (Wikipedia) |
| A1 | — | rs via separate G and M (primary) |
| A2 | — | rs via GM☉ directly (cross-check) |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | rs via separate G and M (primary) | rs = 2 * G * (GM☉/G) / c² (G and M separate) | 2.953250 km |
| A2 | rs via GM☉ directly (cross-check) | rs = 2 * GM☉ / c² (direct, G cancels) | 2.953250 km |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Newtonian gravitational constant G | NIST 2022 CODATA | [nist.gov](https://physics.nist.gov/cgi-bin/cuu/Value?bg) | "Newtonian constant of gravitation" | verified | full_quote | Tier 5 (government) |
| B2 | Speed of light c | NIST 2022 CODATA | [nist.gov](https://physics.nist.gov/cgi-bin/cuu/Value?c) | "speed of light in vacuum" | verified | full_quote | Tier 5 (government) |
| B3 | Nominal solar mass parameter GM☉^N | IAU 2015 Resolution B3 | [arxiv.org](https://ar5iv.labs.arxiv.org/html/1510.07674) | "nominal solar mass parameter" | verified | full_quote | Tier 4 (academic) |
| B4 | Solar mass cross-check | Wikipedia — Solar mass | [wikipedia.org](https://en.wikipedia.org/wiki/Solar_mass) | "1.32712442099" | partial | aggressive_normalization | Tier 3 (reference) |

*Source: proof.py JSON summary*

## Citation Verification Details

### B1: Newtonian gravitational constant G
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B2: Speed of light c
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B3: Nominal solar mass parameter GM☉^N
- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live

### B4: Solar mass cross-check (Wikipedia)
- **Status:** partial
- **Method:** aggressive_normalization (alphanumeric_only)
- **Fetch mode:** live
- **Impact:** B4 is used only as a cross-check source. The primary computation relies on B1, B2, and B3 (all fully verified). The partial status of B4 does not affect the conclusion. *Source: author analysis*

*Source: proof.py JSON summary*

## Computation Traces

```
Solar mass M☉ = GM☉^N / G: GM_sun_iau / G = 1.3271244e+20 / 6.6743e-11 = 1.99e+30
  M☉ = 1.988410e+30 kg
rs = 2GM/c² (primary, metres): 2 * G * M_sun / (c ** 2) = 2 * 6.6743e-11 * 1.988409870698051e+30 / 299792458.0 ** 2 = 2953.2501
rs in kilometres (primary): rs_primary_m / 1000 = 2953.2500761002498 / 1000 = 2.9533
rs = 2(GM☉)/c² (direct, metres): 2 * GM_sun_iau / (c ** 2) = 2 * 1.3271244e+20 / 299792458.0 ** 2 = 2953.2501
rs in kilometres (cross-check): rs_crosscheck_m / 1000 = 2953.2500761002498 / 1000 = 2.9533
rs primary vs direct (km): 2.95325007610025 vs 2.95325007610025, diff=0.0, tolerance=1e-10 -> AGREE
rs using Wikipedia GM☉ (metres): 2 * GM_sun_wiki / (c ** 2) = 2 * 1.32712442099e+20 / 299792458.0 ** 2 = 2953.2501
rs using Wikipedia GM☉ (km): rs_wiki_m / 1000 = 2953.250122809299 / 1000 = 2.9533
rs IAU vs Wikipedia (km): 2.95325007610025 vs 2.953250122809299, diff=4.670904907300155e-08, tolerance=1e-05 -> AGREE
rs > 2.95 km: 2.95325007610025 > 2.95 = True
rs < 2.96 km: 2.95325007610025 < 2.96 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Cross-check | Values | Agreement | Tolerance |
|-------------|--------|-----------|-----------|
| GM☉ IAU nominal vs Wikipedia TCG | 1.3271244e+20 vs 1.32712442099e+20 | AGREE | 1e-5 relative |
| rs primary (G×M) vs direct (GM☉/c²) | 2.9532500761 vs 2.9532500761 | AGREE | 1e-10 km absolute |
| rs IAU nominal GM☉ vs Wikipedia GM☉ | 2.953250 vs 2.953250 | AGREE | 1e-5 km absolute |

Note: The primary computation decomposes GM☉ into G and M (M = GM☉/G), then recombines as 2GM/c². The cross-check uses GM☉ directly. In exact arithmetic these are identical; in floating point they agree to machine precision (diff = 0). The Wikipedia cross-check uses an independently published GM☉ value with more significant digits, providing a genuinely independent data source. Both upstream GM☉ values (IAU nominal and measured TCG) are independently published — same upstream measurement tradition but different compilation and rounding.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

### 1. Could uncertainty in G shift rs outside [2.95, 2.96] km?
- **Verification performed:** Computed rs using G ± uncertainty (6.67430 ± 0.00015 × 10⁻¹¹). Since rs = 2(GM☉)/c² and G cancels when using the GM☉ product, G's uncertainty does not affect the result. Even computing via G×M separately, the relative uncertainty in G (2.2 × 10⁻⁵) shifts rs by only ~0.00006 km, well within the 0.01 km band.
- **Finding:** G uncertainty cannot move rs outside [2.95, 2.96].
- **Breaks proof:** No

### 2. Does the choice of time coordinate (TCB vs TDB) for GM☉ matter?
- **Verification performed:** Searched for TCB vs TDB solar mass parameter values. TCG: 1.32712442099 × 10²⁰, TDB: 1.32712440041 × 10²⁰. IAU nominal: 1.3271244 × 10²⁰. Difference is in the 8th digit, yielding ~10⁻⁸ relative change in rs — negligible.
- **Finding:** Time coordinate choice shifts rs by < 10⁻⁵ km. No impact.
- **Breaks proof:** No

### 3. Do any authoritative sources cite a Schwarzschild radius outside [2.95, 2.96] km?
- **Verification performed:** Searched web: 'Schwarzschild radius Sun km value'. Wikipedia cites 'approximately 3.0 km' and '2.95 × 10³ m'. NASA SpaceMath cites ~3 km. No source gives a value outside the range [2.9, 3.0] km, and all precise computations give ~2.953 km.
- **Finding:** No authoritative source contradicts the [2.95, 2.96] range.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | nist.gov | government | 5 | Government domain (.gov) |
| B2 | nist.gov | government | 5 | Government domain (.gov) |
| B3 | arxiv.org | academic | 4 | Known academic/scholarly publisher |
| B4 | wikipedia.org | reference | 3 | Established reference source |

All sources are tier 3 or above. No flags.

*Source: proof.py JSON summary*

## Extraction Records

| Fact ID | Extracted Value | Source String | Value in Quote |
|---------|----------------|---------------|----------------|
| B1_G | 6.6743e-11 | 6.674 30 x 10^-11 | Yes |
| B2_c | 299792458.0 | 299 792 458 | Yes |
| B3_GM_sun | 1.3271244e+20 | 1.3271244 x 10^20 | Yes |
| B4_GM_sun_tcg | 1.32712442099e+20 | 1.32712442099 x 10^20 | Yes |

Extraction method: Values parsed from `data_values` strings which are formatted as they appear on the source pages. Space-separated digit groups (NIST convention) are joined before parsing to float. Exponents are applied programmatically. *Source: author analysis*

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** Values extracted from data_values strings, not hand-typed
- **Rule 2:** All 4 citations fetched live; 3 verified (full_quote), 1 partial (aggressive_normalization)
- **Rule 3:** N/A — no date-dependent logic in this proof
- **Rule 4:** CLAIM_FORMAL with operator_note documents the compound operator choice and source substitution for solar mass
- **Rule 5:** Three adversarial checks searched for independent counter-evidence (G uncertainty, time coordinate, external sources)
- **Rule 6:** Four independent sources (2 NIST, 1 IAU/arXiv, 1 Wikipedia); two independent computation paths (G×M vs GM☉ direct)
- **Rule 7:** All computations use `explain_calc()`, `compare()`, and `cross_check()` from computations.py
- **validate_proof.py result:** PASS with 1 warning (compound `claim_holds` uses `and` of two `compare()` calls — appropriate for two-sided bound)

*Source: author analysis*

## Generator

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
