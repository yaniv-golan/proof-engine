# Proof: The average exit multiple for SaaS venture-backed companies is 8.5x invested capital, higher than for consumer internet companies.

- **Generated:** 2026-04-08
- **Verdict:** UNDETERMINED
- **Audit trail:** [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

## Key Findings

- The claim specifies a **MOIC (multiple of invested capital)** of 8.5x for SaaS exits — but no public source provides average MOIC by sector for VC-backed companies.
- The figure "8.5x" in publicly available SaaS M&A literature refers to **EV/Revenue** (enterprise value as a multiple of annual revenue), a fundamentally different metric. Aventis Advisors reports top-quartile EV/Revenue above 8.1x across 543 SaaS M&A deals (2015–2026); median is 4.5x.
- MOIC data by sector requires access to proprietary VC fund databases (PitchBook, CB Insights premium, Carta). No public source was found providing average MOIC specifically for SaaS vs. consumer internet.
- Without public sector-level MOIC data, neither sub-claim (SC1: SaaS MOIC = 8.5x; SC2: SaaS MOIC > consumer internet MOIC) can be confirmed or disproved.

## Claim Interpretation

**Natural language:** The average exit multiple for SaaS venture-backed companies is 8.5x invested capital, higher than for consumer internet companies.

**Formal interpretation:** The claim asserts two things: (SC1) the average SaaS exit multiple is 8.5x invested capital — specifically MOIC (multiple on invested capital), the standard VC return metric measuring (total exit value) / (total capital invested) — and (SC2) this MOIC exceeds the average for consumer internet companies. MOIC is distinct from EV/Revenue multiples (valuation relative to annual revenue), which are used in M&A pricing. Public SaaS M&A data typically reports EV/Revenue, not MOIC. MOIC data by sector requires access to proprietary VC fund databases.

**Operator:** `==` AND `>` (compound: both sub-claims must hold). Threshold: 2 independent confirming sources per sub-claim.

## Evidence Summary

| ID | Fact | Status |
|----|------|--------|
| SC1 | SaaS average exit MOIC = 8.5x — no public source found; 8.5x EV/Revenue found but is a different metric | Not confirmed |
| SC2 | SaaS MOIC > consumer internet MOIC — no public comparable data found | Not confirmed |

No Type B (empirical) citations could be verified as confirming the MOIC claim. Public sources confirm EV/Revenue data for SaaS only.

## Proof Logic

### SC1 — SaaS average exit MOIC = 8.5x

- **Required confirming sources:** 2
- **Confirmed:** 0
- **Holds:** No

Public sources reporting "8.5x" in the context of SaaS exits describe EV/Revenue multiples, not MOIC. Aventis Advisors (543 deals, 2015–2026) reports top-quartile EV/Revenue at 8.1x and median at 4.5x. SaaS Capital annual surveys report median EV/NTM Revenue of 3.3x–6.4x depending on year. None of these are MOIC figures. No source provides average SaaS exit MOIC = 8.5x.

### SC2 — SaaS exit MOIC exceeds consumer internet exit MOIC

- **Required confirming sources:** 2
- **Confirmed:** 0
- **Holds:** No

No public source provides a sector-level breakdown of average VC exit MOIC for SaaS vs. consumer internet. The NVCA and Kauffman Foundation publish aggregate VC return data but not sector-specific MOIC. Academic literature (Gompers, Kaplan, Metrick) covers VC returns generally without isolating SaaS vs. consumer internet.

## Adversarial Checks

### Check 1 — Is the 8.5x figure actually EV/Revenue rather than MOIC?

**Finding:** Searched for "8.5x SaaS" in financial literature. Aventis Advisors (543 SaaS M&A deals, 2015–2026) reports top-quartile EV/Revenue above 8.1x and median EV/Revenue at 4.5x. SaaS Capital annual private SaaS surveys report EV/NTM Revenue medians ranging 3.3x–6.4x depending on year. The 8.5x figure, if it exists, almost certainly refers to EV/Revenue (enterprise value as a multiple of annual revenue), not MOIC (exit value as a multiple of capital invested). These are fundamentally different metrics and not interchangeable.

**Breaks proof:** Yes — the metric in the claim (MOIC) and the metric reported publicly (EV/Revenue) are different quantities. A claim about MOIC cannot be confirmed by EV/Revenue data.

### Check 2 — Is MOIC data by sector publicly available from any source?

**Finding:** Searched PitchBook, CB Insights, Carta, NVCA, and academic databases for sector-level MOIC data on VC-backed exits. All primary MOIC databases require paid subscriptions. The Kauffman Foundation and NVCA publish aggregate VC return data but not sector breakdowns by MOIC. No public source provides average MOIC for SaaS specifically.

**Breaks proof:** Yes — without publicly verifiable MOIC data, neither sub-claim can be confirmed.

### Check 3 — Are there academic papers reporting SaaS vs. consumer internet MOIC?

**Finding:** Searched SSRN, NBER, and Google Scholar for VC exit multiples by sector. Found papers on VC returns generally (Gompers, Kaplan, Metrick) but none that isolate SaaS vs. consumer internet MOIC with an 8.5x benchmark. The SaaS category as a distinct VC sector is relatively recent (pre-2015 mainstream adoption is limited), and longitudinal MOIC data by sector is sparse even in academic literature.

**Breaks proof:** Yes — no academic source confirms the 8.5x MOIC claim for SaaS.

## Conclusion

**Verdict: UNDETERMINED.**

The specific metric in the claim — MOIC, multiple of invested capital — is not publicly available broken down by sector. What public sources do provide for SaaS is EV/Revenue data, which is a fundamentally different metric measuring valuation relative to revenue, not returns relative to invested capital. A figure of approximately 8.5x does appear in SaaS M&A literature but describes top-quartile EV/Revenue, not average MOIC. No public source provides a SaaS vs. consumer internet MOIC comparison. The claim cannot be confirmed or disproved from publicly available data.
