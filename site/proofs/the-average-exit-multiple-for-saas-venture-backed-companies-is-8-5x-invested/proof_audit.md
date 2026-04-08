# Audit: The average exit multiple for SaaS venture-backed companies is 8.5x invested capital, higher than for consumer internet companies.

- **Generated:** 2026-04-08
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Average exit multiple for SaaS venture-backed companies |
| Property | Multiple of invested capital (MOIC) at exit, compared to consumer internet |
| Operator | == AND > (compound) |
| Threshold | 2 independent confirming sources per sub-claim |
| Operator note | The claim asserts two things: (SC1) the average SaaS exit multiple is 8.5x invested capital (MOIC — not EV/Revenue), and (SC2) this exceeds the consumer internet average. MOIC measures (total exit value) / (total capital invested), the standard VC return metric. This is distinct from EV/Revenue multiples (valuation relative to annual revenue). Public SaaS M&A data typically reports EV/Revenue, not MOIC. MOIC data by sector requires access to proprietary VC fund databases (PitchBook, CB Insights premium, Carta). |

## Fact Registry

| Report ID | Label |
|-----------|-------|
| SC1 | SaaS average exit MOIC = 8.5x — no public source found; 8.5x EV/Revenue found but is a different metric |
| SC2 | SaaS MOIC > consumer internet MOIC — no public comparable data found |

## Sub-claim Evaluation Table

| Sub-claim | Description | Sources Required | Sources Confirmed | Holds |
|-----------|-------------|-----------------|-------------------|-------|
| SC1 | Average SaaS exit multiple is 8.5x invested capital (MOIC) | 2 | 0 | No |
| SC2 | SaaS exit multiple exceeds consumer internet exit multiple | 2 | 0 | No |

## Citation Verification Details

No Type B (empirical) citations were verified as confirming the MOIC claim. The following sources were searched and assessed:

### Aventis Advisors — SaaS M&A multiples (EV/Revenue)
- **Searched for:** "8.5x SaaS exit multiple invested capital"
- **Found:** 543 SaaS M&A deals (2015–2026); top-quartile EV/Revenue above 8.1x; median EV/Revenue 4.5x
- **Assessment:** Reports EV/Revenue, not MOIC. The 8.5x figure in this context refers to enterprise value as a multiple of annual revenue, not return on invested capital. Cannot confirm SC1.
- **Breaks proof:** Yes — metric mismatch

### SaaS Capital Annual Surveys (EV/NTM Revenue)
- **Searched for:** SaaS exit multiples by year
- **Found:** Median EV/NTM Revenue ranging 3.3x–6.4x depending on year surveyed
- **Assessment:** EV/Revenue metric. Does not address MOIC. Cannot confirm SC1.
- **Breaks proof:** Yes — metric mismatch

### PitchBook / CB Insights / Carta (MOIC databases)
- **Searched for:** Sector-level MOIC for VC-backed SaaS exits
- **Found:** All primary MOIC databases require paid subscriptions. No public-access data providing average MOIC for SaaS specifically.
- **Assessment:** Cannot confirm SC1 or SC2 from public data.
- **Breaks proof:** Yes — data not publicly available

### NVCA / Kauffman Foundation (aggregate VC returns)
- **Searched for:** Average MOIC by sector, SaaS vs. consumer internet
- **Found:** Aggregate VC return data published, but no sector-level MOIC breakdown
- **Assessment:** Cannot confirm SC1 or SC2.
- **Breaks proof:** Yes — sector breakdown not available

### Academic literature (Gompers, Kaplan, Metrick; SSRN; NBER)
- **Searched for:** VC exit multiples by sector, SaaS vs. consumer internet MOIC
- **Found:** General VC return literature; no study isolates SaaS vs. consumer internet MOIC with an 8.5x benchmark
- **Assessment:** SaaS as a distinct VC sector category has limited longitudinal academic coverage. No academic source confirms SC1 or SC2.
- **Breaks proof:** Yes — no confirming academic source found

## Adversarial Checks

### Check 1 — Is the 8.5x figure actually EV/Revenue rather than MOIC?
- **Question:** Does the "8.5x" figure that circulates in SaaS discussions refer to EV/Revenue (an M&A pricing metric) rather than MOIC (a VC return metric)?
- **Verification performed:** Searched for "8.5x SaaS" in financial literature. Found Aventis Advisors reporting top-quartile EV/Revenue above 8.1x (543 SaaS M&A deals, 2015–2026) and SaaS Capital reporting median EV/NTM Revenue of 3.3x–6.4x.
- **Finding:** The 8.5x figure almost certainly refers to EV/Revenue, not MOIC. These are fundamentally different metrics: EV/Revenue measures the acquisition price relative to annual revenue; MOIC measures the return on capital invested by a VC fund.
- **Breaks proof:** Yes

### Check 2 — Is MOIC data by sector publicly available from any source?
- **Question:** Does any public (non-paywalled) source report average MOIC for VC-backed SaaS exits?
- **Verification performed:** Searched PitchBook, CB Insights, Carta, NVCA, Kauffman Foundation, and academic databases.
- **Finding:** All primary MOIC databases require paid subscriptions. No public source provides average MOIC for SaaS specifically.
- **Breaks proof:** Yes

### Check 3 — Are there academic papers reporting SaaS vs. consumer internet MOIC?
- **Question:** Does peer-reviewed or preprint literature isolate SaaS vs. consumer internet MOIC?
- **Verification performed:** Searched SSRN, NBER, Google Scholar for VC exit multiples by sector.
- **Finding:** General VC return papers (Gompers, Kaplan, Metrick) do not isolate SaaS vs. consumer internet. The SaaS category is too recent for longitudinal academic MOIC analysis. No confirming academic source found.
- **Breaks proof:** Yes

## Hardening Checklist

- **Rule 1:** No numeric values were hand-typed from the claim. All values noted are sourced from identified literature.
- **Rule 2:** No citations were verified as confirming MOIC data; the search process identified metric mismatch as the core issue.
- **Rule 3:** Proof generated 2026-04-08 via `date.today()`.
- **Rule 4:** Claim interpretation explicitly distinguishes MOIC from EV/Revenue in `CLAIM_FORMAL`; operator rationale documented.
- **Rule 5:** 3 adversarial checks performed — metric identity (EV/Revenue vs. MOIC), public data availability, academic literature search. All three break the proof.
- **Rule 6:** Multiple data sources searched independently; no source found providing sector-level MOIC.
- **Rule 7:** No hard-coded constants; verdict based on source count comparison (`0 >= 2 = False`).

## Verdict Determination

Both SC1 and SC2 require a minimum of 2 independently confirmed public sources and received 0. The compound operator (AND) means both sub-claims must hold for the overall claim to be proved. With 0 confirmed sources for each sub-claim, the verdict is **UNDETERMINED** — not DISPROVED, because the absence of public data does not prove the claim false; it means the claim cannot be verified or falsified from publicly available evidence.
