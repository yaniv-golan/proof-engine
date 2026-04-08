# Audit: US venture capital funding reached $332 billion in 2021 before declining by over 35% in 2022.

- **Generated:** 2026-04-08
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | US venture capital deal value |
| Property | 2021 annual total and 2022 year-over-year decline percentage |
| Operator | compound AND |
| SC1 threshold | >$300B (2021 US VC deal value ≈ $332B ± $15B) |
| SC2 threshold | >35% decline from 2021 to 2022 |
| Operator note | SC1: NVCA initial = $329.9B; PitchBook revised = $344.7B; claim's $332B falls between. SC2 is contested: CB Insights reports −37%, PitchBook reports −30.8%. Discrepancy reflects different fund universes and 2021 baselines. |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | B1 | NVCA press release: 2021 US VC = $329.9B |
| B2 | B2 | CB Insights: 2022 US VC = $198.4B (down 37% from 2021) |
| B3 | B3 | PitchBook-NVCA via Built In: 2022 US VC = $238.3B (down 30.8% from $344.7B) |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

No Type A facts — all facts in this proof are empirical (Type B).

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | NVCA press release: 2021 US VC = $329.9B | NVCA Press Release: U.S. VC Activity Soars to New Highs in 2021 | https://nvca.org/press_releases/u-s-venture-capital-soars-to-new-highs-in-2021/ | "a staggering $329.9 billion was invested across an estimated 17,054 deals, a record for deal count and roughly double 2020's previous deal value high" | verified | unicode_normalized | Tier 2 (unknown) |
| B2 | CB Insights: 2022 US VC = $198.4B (down 37% from 2021) | CB Insights: State of Venture 2022 Report | https://www.cbinsights.com/research/report/venture-trends-2022/ | "US venture funding hit $198.4B in 2022 — down 37% from 2021, but up 31% when compared to 2020" | verified | full_quote | Tier 2 (unknown) |
| B3 | PitchBook-NVCA via Built In: 2022 US VC = $238.3B (down 30.8% from $344.7B) | Built In: VC Funding Dropped in 2022 but Eclipsed Pre-2021 Totals (citing PitchBook-NVCA) | https://builtin.com/articles/tech-funding-2022-pitchbook-report | "About $238.3 billion was allocated in VC deals last year, according to PitchBook-NVCA Venture Monitor" | verified | unicode_normalized | Tier 2 (unknown) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — NVCA Press Release**
- Status: verified
- Method: unicode_normalized (full quote verified after Unicode normalization; coverage_pct: null — full match)
- Fetch mode: live

**B2 — CB Insights: State of Venture 2022 Report**
- Status: verified
- Method: full_quote (exact quote found verbatim; coverage_pct: null)
- Fetch mode: live

**B3 — Built In (citing PitchBook-NVCA)**
- Status: verified
- Method: unicode_normalized (full quote verified after Unicode normalization; coverage_pct: null — full match)
- Fetch mode: live

*Source: proof.py JSON summary*

---

## Computation Traces

```
[✓] B1: Full quote verified for B1 (after Unicode normalization) (source: tier 2/unknown)
[✓] B2: Full quote verified for B2 (source: tier 2/unknown)
[✓] B3: Full quote verified for B3 (after Unicode normalization) (source: tier 2/unknown)
  unknown: Parsed '329.9' -> 329.9
B1: 2021 US VC (NVCA initial): $329.9B
  unknown: Parsed '198.4' -> 198.4
  unknown: Parsed '37' -> 37.0 (source text: '37')
B2: 2022 US VC (CB Insights): $198.4B, decline: 37.0%
  unknown: Parsed '238.3' -> 238.3
  SC2 cross-check: PitchBook 2022 decline % from revised 2021 baseline: (vc_2021_pb_revised - vc_2022_pb) / vc_2021_pb_revised * 100 = (344.7 - 238.3) / 344.7 * 100 = 30.8674
  2022 US VC: CB Insights vs PitchBook (different methodologies): 198.4 vs 238.3, diff=39.900000000000006, relative=0.167436, tolerance=0.3 -> AGREE
  SC1: 2021 US VC > $300B (claim threshold): 329.9 > 300.0 = True
  SC2: 2022 decline >35% (CB Insights): 37.0 > 35.0 = True
  SC2: 2022 decline >35% (PitchBook): 30.867420945749924 > 35.0 = False
  Overall verdict holds (SC1 + SC2 + no breaks): 0 >= 1 = False
```

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

**2022 US VC totals: CB Insights vs PitchBook**

| Source | 2022 VC Total | 2021 Baseline | Computed Decline |
|--------|--------------|---------------|-----------------|
| CB Insights (B2) | $198.4B | ~$314B (implied) | 37.0% |
| PitchBook-NVCA (B3) | $238.3B | $344.7B (revised) | 30.9% |

Cross-check result: AGREE within 30% relative tolerance (actual relative diff = 16.7%). Sources agree directionally on the 2022 decline but disagree on magnitude.

**Conflict of Interest flags:** No COI identified. CB Insights and PitchBook are independent commercial data providers. NVCA is a trade association with an interest in reporting VC activity accurately for its members; no directional COI on reporting declines.

*Source: proof.py JSON summary*

---

## Adversarial Checks (Rule 5)

**Check 1: PitchBook-NVCA reports only 30.8% decline (< 35% threshold)**

- Question: Does the most authoritative VC data source confirm the >35% decline?
- Search performed: PitchBook-NVCA Q4 2022 Venture Monitor data (via Built In article citing the report directly, B3)
- Finding: PitchBook-NVCA reports $238.3B for 2022, down 30.8% from the revised 2021 figure of $344.7B. This falls below the >35% threshold. The discrepancy with CB Insights reflects: (1) different fund universes, (2) different treatment of corporate VC and CVC arms, (3) PitchBook's higher revised 2021 baseline.
- Breaks proof: **Yes** — SC2 is contested by PitchBook, the most authoritative source.

**Check 2: $332B claim vs $329.9B actual (NVCA) — minor discrepancy**

- Question: Does any source actually report $332B for 2021?
- Search performed: Reviewed NVCA press release ($329.9B initial), PitchBook revised ($344.7B), KPMG Venture Pulse as possible intermediate source.
- Finding: No single major source publishes exactly $332B. The figure falls between two credible estimates. Likely reflects KPMG or a third aggregator's methodology.
- Breaks proof: **No** — $332B is approximately correct within source variation.

**Check 3: Global vs US figures — scope alignment**

- Question: Are the sources measuring US-only VC or global VC?
- Search performed: Checked CB Insights global vs US figures ($415B global VC in 2021 vs $329.9B US-only).
- Finding: All three sources used (B1, B2, B3) report US-only figures, consistent with the claim's scope.
- Breaks proof: **No** — no scoping inconsistency.

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | nvca.org | unknown | 2 | Unclassified domain — verify source authority manually. NVCA (National Venture Capital Association) is the primary US VC trade association; authoritative despite unclassified tier. |
| B2 | cbinsights.com | unknown | 2 | Unclassified domain — verify source authority manually. CB Insights is a major VC/startup intelligence platform widely cited by press and industry. |
| B3 | builtin.com | unknown | 2 | Unclassified domain — verify source authority manually. Built In is a tech industry publication; this article directly cites the PitchBook-NVCA Venture Monitor. |

No Tier 1 (flagged unreliable) sources. All three sources are Tier 2 (unclassified) due to automatic domain classification, not due to any quality concern. The NVCA and PitchBook-NVCA figures are primary data from the leading US VC industry body.

*Source: proof.py JSON summary*

---

## Extraction Records

| Fact ID | Extracted Value | Value in Quote? | Quote Snippet |
|---------|----------------|-----------------|---------------|
| B1 | $329.9B | Yes | "a staggering $329.9 billion was invested across an estimated 17,054 deals" |
| B2 (2022 total) | $198.4B | Yes | "US venture funding hit $198.4B in 2022 — down 37% from 2021" |
| B2 (decline %) | 37.0% | Yes | "down 37% from 2021" |
| B3 | $238.3B | Yes | "About $238.3 billion was allocated in VC deals last year" |

All values parsed from quote text using `parse_number_from_quote()` with explicit regex patterns — not hand-typed (Rule 1). The PitchBook 2021 revised baseline of $344.7B is the only value not extracted from a quote; it is cited in the claim interpretation context as a known public figure and used only in the explain_calc() cross-check computation.

*Source: proof.py JSON summary*

---

## Hardening Checklist

| Rule | Status | Notes |
|------|--------|-------|
| Rule 1: No hand-typed empirical values | PASS | All values parsed via `parse_number_from_quote()` with explicit regex patterns. Exception: PitchBook revised 2021 baseline ($344.7B) used only in cross-check calculation. |
| Rule 2: Citations fetched and verified | PASS | All three citations verified live (B1: unicode_normalized, B2: full_quote, B3: unicode_normalized). |
| Rule 3: System time anchored | N/A | No date-dependent logic in this proof. |
| Rule 4: Explicit claim interpretation | PASS | CLAIM_FORMAL defines both SC1 and SC2 with explicit thresholds and operator rationale. |
| Rule 5: Adversarial checks | PASS | Three adversarial checks performed; one (PitchBook contradiction) breaks SC2. |
| Rule 6: Independent cross-checks | PASS | CB Insights and PitchBook independently measured 2022 US VC; results cross-checked within 30% relative tolerance (actual: 16.7%). COI assessment performed — no COI identified. |
| Rule 7: No hard-coded constants | PASS | `compare()`, `cross_check()`, and `explain_calc()` imported from `computations.py`. |
| validate_proof.py | Not run inline — run separately via `python proof-engine/skills/proof-engine/scripts/validate_proof.py docs/examples/us-vc-funding-2021-2022/proof.py` |

*Source: author analysis*

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.10.0 on 2026-04-08.*
