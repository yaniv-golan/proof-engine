# Audit: Venture capital funds vintage 2012-2016 have a median net IRR of 16.8% according to Cambridge Associates but 18.2% according to Preqin.

- **Generated:** 2026-04-08
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Median net IRR of US venture capital funds with vintage years 2012-2016 |
| Property | Median net Internal Rate of Return as reported by two specific benchmarking firms |
| Operator | == (equality — two specific figures from two named sources) |
| Thresholds | SC1: 16.8% (Cambridge Associates); SC2: 18.2% (Preqin) |
| Compound operator | AND — both sub-claims must hold for the claim to be verified |
| Operator note | "Net IRR" = after management fees and carried interest. "Vintage year" = year of first investment. Both Cambridge Associates and Preqin are subscription-only; full benchmark tables are not publicly accessible. Verification requires either a paid subscription, a public press release reproducing the figures, or an academic paper attributing these figures to the named sources. |

## Fact Registry

| ID | Label |
|----|-------|
| SC1 | Cambridge Associates: median net IRR for VC vintage 2012-2016 = 16.8% — no public source found |
| SC2 | Preqin: median net IRR for VC vintage 2012-2016 = 18.2% — no public source found |

## Citation Verification Details

### SC1 — Cambridge Associates: median net IRR, VC vintage 2012-2016 = 16.8%

- **Data source:** Cambridge Associates US VC benchmark database (subscription-only)
- **Expected value:** 16.8% median net IRR for VC vintage year cohort 2012-2016
- **Verification status:** Not verified — no public source found
- **Search scope:**
  - cambridgeassociates.com/research/ — benchmark landing page confirms existence of VC benchmarks but requires subscription
  - Cambridge Associates Q3 2025 public summary PDF — contains only aggregate 5/10/20-year horizon returns; no per-vintage-year median net IRR table
  - SSRN and NBER searches for Cambridge Associates VC benchmark data — no match
  - Financial news outlets (Bloomberg, Reuters, WSJ, FT) searches for "Cambridge Associates venture 16.8 IRR" — no match
  - Over 30 URL attempts total across CA's domain and secondary sources
- **Result:** The specific figure 16.8% for VC vintage 2012-2016 cannot be confirmed from any publicly accessible source.

### SC2 — Preqin: median net IRR, VC vintage 2012-2016 = 18.2%

- **Data source:** Preqin fund performance database (subscription-only)
- **Expected value:** 18.2% median net IRR for VC vintage year cohort 2012-2016
- **Verification status:** Not verified — no public source found
- **Search scope:**
  - preqin.com/benchmarks — requires login; full benchmark tables behind paywall
  - Preqin Global Alternatives Report (annual public PDFs) — cites aggregate venture return quartiles, not specific vintage-year median figures
  - Google search: "Preqin venture 2012 2016 IRR 18.2" — no match
  - Academic databases (SSRN, NBER, Google Scholar) for "Preqin venture median IRR vintage 2012" — no match
  - Financial news outlets search for "Preqin venture 18.2 IRR" — no match
- **Result:** The specific figure 18.2% for VC vintage 2012-2016 cannot be confirmed from any publicly accessible source.

## Adversarial Search Queries

1. **"Cambridge Associates venture IRR 16.8 vintage 2012 2016"** — to find any public reproduction of the CA figure. No results.

2. **"Preqin venture IRR 18.2 vintage 2012 2016"** — to find any public reproduction of the Preqin figure. No results.

3. **"16.8 18.2 Cambridge Preqin venture IRR"** — to find any secondary source citing both figures together. No results.

4. **"Cambridge Associates VC benchmark 2012 2016 median"** — broad search for any public CA vintage-year median data. Only subscription product pages found.

5. **"Preqin global alternatives report venture IRR 2012 2016"** — to find aggregate data that might contain per-vintage figures. Annual reports cite aggregate quartiles only.

## Methodology Notes

**Cambridge Associates methodology:** CA uses a cash-on-cash timing approach and builds its benchmark from a proprietary fund universe (voluntarily reporting funds). The benchmark includes net-of-fee IRR data supplied by fund managers. Per-vintage-year tables are a standard feature of the paid subscription product.

**Preqin methodology:** Preqin sources fund performance data from multiple channels including LP filings, fund manager disclosures, and freedom-of-information requests to public pension funds. Preqin uses its own timing convention for vintage year assignment. The fund universe and vintage year boundaries differ from Cambridge Associates, which accounts for the plausible 1.4 percentage-point gap between the two figures (16.8% vs 18.2%).

**Why the figures may be correct but unverifiable:** Both CA and Preqin provide their benchmark data as a paid subscription service. Data consumers typically download proprietary reports; these are not publicly posted. Academics sometimes reproduce summary statistics from these databases in papers, but the specific vintage 2012-2016 cohort median net IRR does not appear to have been reproduced in any accessible academic or press publication.

## Sub-claim Logic

```
sc1_holds = compare(n_sc1_confirmed, ">=", 1)
  → compare(0, ">=", 1) = False

sc2_holds = compare(n_sc2_confirmed, ">=", 1)
  → compare(0, ">=", 1) = False

any_breaks = True (all three adversarial checks break proof)

Verdict logic:
  if sc1_holds and sc2_holds and not any_breaks → PROVED
  elif sc1_holds or sc2_holds → PARTIALLY VERIFIED
  else → UNDETERMINED  ← this branch taken

  VERDICT = "UNDETERMINED"
```

## Hardening Checklist

- **Rule 1:** No numeric values were extracted — the proof could not obtain publicly accessible quote text containing the figures to parse. `parse_number_from_quote()` was not called because no verifiable quote was available.
- **Rule 2:** Citation verification was attempted for both SC1 and SC2. Both returned no match across extensive URL search. The sources are behind subscription paywalls.
- **Rule 3:** Proof generated with date anchored to system time (2026-04-08).
- **Rule 4:** Claim interpretation explicit in `CLAIM_FORMAL` dict. Disambiguation of "net IRR," "vintage year," and the compound AND logic of the two sub-claims is documented.
- **Rule 5:** Three adversarial checks performed — CA data availability, Preqin data availability, and secondary source triangulation. All three break the proof.
- **Rule 6:** No cross-check possible — neither primary source is publicly accessible. The 1.4 pp gap between CA (16.8%) and Preqin (18.2%) is noted as plausible given documented methodology differences.
- **Rule 7:** All comparisons via `compare()` from `computations.py`.
