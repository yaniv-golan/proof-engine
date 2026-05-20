# Audit: <!-- not-a-citation-start -->Topaz et al. (2026)<!-- not-a-citation-end --> analyzed 2.5 million biomedical papers in PubMed Central from January 2023 through February 2026 and identified 4,046 references pointing to studies that do not exist, distributed across 2,810 papers.

- **Generated:** 2026-05-20
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The natural-language claim asserts four specific facts about a single named source: the Topaz et al. 2026 correspondence in *The Lancet* titled "Fabricated citations: an audit across 2·5 million biomedical papers" (vol 407, pp 1779-1781, published May 9, 2026). The claim's logical structure is `Source S reports facts F1 ∧ F2 ∧ F3 ∧ F4`, where:

- F1: corpus = ~2.5 million biomedical papers in PubMed Central
- F2: window = January 2023 through February 2026
- F3: fabricated references identified = 4,046
- F4: distinct papers affected = 2,810

The compound operator is AND — all four must hold. The proof_direction is "affirm" (this is not a disproof). The formal interpretation is a faithful 1:1 mapping of the natural-language claim with one explicit operationalization: "studies that do not exist" is interpreted as the paper's own definition, "references whose claimed titles correspond to no existing publication." The claim's "2.5 million" is interpreted as the paper's own headline rounding of 2,471,758 (the exact figure reported in methods).

**Formalization scope:** The claim is verified against what the paper *reports*, not against the ground-truth fabrication rate in PubMed Central. The paper's own supplementary appendix uses the more cautious term "suspected fabricated references" and reports 91% pipeline precision. This is documented in the operator_note for SC3 and in the adversarial checks.

*Source: proof.py JSON summary — `claim_natural`, `claim_formal`*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Topaz, Roguin, Gupta, Zhang, Peltonen — *Lancet* 2026; 407: 1779-81 |
| Purpose | fact_verification |
| Compound operator | AND |
| Proof direction | affirm |
| SC1 property | Corpus size ≈ 2.5 million biomedical papers in PubMed Central |
| SC2 property | Time window: January 2023 through February 2026 |
| SC3 property | Number of fabricated references identified = 4,046 |
| SC4 property | Number of distinct papers containing fabricated refs = 2,810 |
| Threshold per SC | 1 verified in-source quote |

*Source: proof.py JSON summary — `claim_formal`*

## Fact Registry

| ID | Type | Key | Label |
|----|------|-----|-------|
| B1 | empirical | sc1_corpus_size | SC1: corpus size from Topaz et al. 2026 methods |
| B2 | empirical | sc2_date_range | SC2: date range from Topaz et al. 2026 methods |
| B3 | empirical | sc3_fab_count | SC3: 4046 fabricated references (Topaz et al. 2026 results) |
| B4 | empirical | sc4_affected_papers | SC4: 2810 affected papers (Topaz et al. 2026 limitations) |
| A1 | computed | — | SC1 verified-source count |
| A2 | computed | — | SC2 verified-source count |
| A3 | computed | — | SC3 verified-source count |
| A4 | computed | — | SC4 verified-source count |

*Source: proof.py JSON summary — `evidence`*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | SC1 verified-source count | count(verified sc1 citations) | 1 |
| A2 | SC2 verified-source count | count(verified sc2 citations) | 1 |
| A3 | SC3 verified-source count | count(verified sc3 citations) | 1 |
| A4 | SC4 verified-source count | count(verified sc4 citations) | 1 |

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote (truncated) | Status | Method | Credibility |
|----|------|--------|-----|-------------------|--------|--------|-------------|
| B1 | SC1 corpus size | Topaz et al. 2026, Lancet 407:1779-81 | [thelancet.com](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00603-3/fulltext) | We developed an automated reference verification system scanning PubMed Central&rsquo;s O… | verified | full_quote | Academic |
| B2 | SC2 date range | Topaz et al. 2026, Lancet 407:1779-81 | [thelancet.com](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00603-3/fulltext) | scanning PubMed Central&rsquo;s Open Access subset from Jan 1, 2023, to Feb 18, 2026 | verified | full_quote | Academic |
| B3 | SC3 fab count | Topaz et al. 2026, Lancet 407:1779-81 | [thelancet.com](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00603-3/fulltext) | Among 97·1 million verified references, we identified 4046 fabricated references across 2810 papers | verified | full_quote | Academic |
| B4 | SC4 affected papers | Topaz et al. 2026, Lancet 407:1779-81 | [thelancet.com](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00603-3/fulltext) | Of the 2810 affected papers, 98·4% had received no publisher action at the time of our audit | verified | full_quote | Academic |

*Source: proof.py JSON summary — `evidence`*

## Citation Verification Details

All four citations resolve to the same source URL (the *Lancet* article PIIS0140-6736(26)00603-3) and are verified against a pypdf-extracted text snapshot of the user-uploaded PDF.

- **B1 — SC1 corpus size:** Status `verified` · Method `full_quote` · Fetch mode `snapshot` (snapshot_source: `user_uploaded_pdf:pypdf_extract`). Verbatim status: verbatim.
- **B2 — SC2 date range:** Status `verified` · Method `full_quote` · Fetch mode `snapshot`. Verbatim status: verbatim.
- **B3 — SC3 fab count:** Status `verified` · Method `full_quote` · Fetch mode `live` (the verifier was able to confirm this quote without snapshot fallback — likely because the substring is short and stable enough to match against the Lancet page text). Verbatim status: verbatim.
- **B4 — SC4 affected papers:** Status `verified` · Method `full_quote` · Fetch mode `snapshot`. Verbatim status: verbatim.

No citations are in `not_found`, `partial`, or `fetch_failed` state. No citation recovery loop was needed.

*Source: proof.py JSON summary — `evidence[].verification`*

## Computation Traces

```
[✓] sc1_corpus_size [snapshot]: Full quote verified for sc1_corpus_size (source: tier 4/academic)
[✓] sc2_date_range [snapshot]: Full quote verified for sc2_date_range (source: tier 4/academic)
[✓] sc3_fab_count: Full quote verified for sc3_fab_count (source: tier 4/academic)
[✓] sc4_affected_papers [snapshot]: Full quote verified for sc4_affected_papers (source: tier 4/academic)
SC1: corpus size ≈ 2.5M papers in PMC: 1 >= 1 = True
SC2: date range Jan 2023 - Feb 2026: 1 >= 1 = True
SC3: 4046 fabricated references: 1 >= 1 = True
SC4: 2810 affected papers: 1 >= 1 = True
compound: all sub-claims hold: 4 == 4 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

This proof has an intrinsic single-source structure: the claim is about what the Topaz et al. 2026 paper itself reports. There is no second authoritative source for "what the paper says" other than the paper. The proof therefore declares a single in-source quote per sub-claim and accepts that the validator's "≥2 sources per SC" guidance does not apply to this kind of claim.

For SC4 (2,810 affected papers), the paper itself provides a measure of internal corroboration: the same count appears in two distinct sentences (the results sentence "4046 fabricated references across 2810 papers" and the limitations sentence "Of the 2810 affected papers, 98·4% had received no publisher action"). B3 and B4 are extracted from these two sentences respectively.

**COI assessment:** No COI flags are recorded. The single source (Topaz et al.) is the paper *being characterized* by the claim — this is by design of the claim, not a conflict of interest. The proof does not evaluate whether Topaz et al.'s reported counts reflect ground-truth fabrications in PubMed Central; that is a separate empirical claim outside the scope of this proof.

*Source: proof.py JSON summary — `cross_checks`*

## Adversarial Checks (Rule 5)

| # | Question | Verification performed | Finding | Breaks proof? |
|---|----------|------------------------|---------|---------------|
| 1 | Does the paper itself use weaker language than "studies that do not exist" for these 4,046 references? | Searched the supplementary appendix for the exact language. Main paper: "fabricated references." Appendix: "suspected fabricated references," with 91% pipeline precision (Fleiss' κ = 0.71). | The claim's "references pointing to studies that do not exist" tracks the paper's own definition. The true count of references-to-nothing is approximately 4,046 × 0.91 ≈ 3,682, but the claim is about what the paper reports (4,046), not the ground-truth count. | No |
| 2 | Are there any retractions, corrections, or rebuttals that would change the headline numbers? | Paper published May 9, 2026; today is May 20, 2026. Eleven days post-publication; no formal correction notice attached. | None known. Headline figures appear unchanged. | No |
| 3 | Could "January 2023 through February 2026" overstate the actual interval? | Compared claim against the paper's exact interval (Jan 1, 2023 to Feb 18, 2026). | The claim's month-level phrasing is consistent with the paper. No overstatement. | No |
| 4 | Is "2.5 million" a fair rounding of 2,471,758? | 2,471,758 rounds to 2.5M at 2 sig figs. The paper itself uses "2·5 million" in its title. | Match is exact to the paper's own rounding. | No |

*Source: proof.py JSON summary — `adversarial_checks`*

## Source Credibility Assessment

| Fact ID | Domain | Type | Note |
|---------|--------|------|------|
| B1 | thelancet.com | Academic | Tier 4 — known academic/scholarly publisher |
| B2 | thelancet.com | Academic | Tier 4 — known academic/scholarly publisher |
| B3 | thelancet.com | Academic | Tier 4 — known academic/scholarly publisher |
| B4 | thelancet.com | Academic | Tier 4 — known academic/scholarly publisher |

All four citations resolve to the same source — *The Lancet*, a tier-4 academic publisher. No flagged or unclassified sources.

*Source: proof.py JSON summary — `evidence[].verification.credibility`*

## Source Data

| Fact ID | Extracted value | Found in quote | Quote snippet |
|---------|-----------------|----------------|---------------|
| B1 | verified | true | We developed an automated reference verification system scanning PubMed Central's O |
| B2 | verified | true | scanning PubMed Central's Open Access subset from Jan 1, 2023, to Feb 18, 2026 |
| B3 | verified | true | Among 97·1 million verified references, we identified 4046 fabricated references a |
| B4 | verified | true | Of the 2810 affected papers, 98·4% had received no publisher action at the time of |

Extraction method: full-quote presence check against snapshot. No value parsing was needed — the claim is a presence/match of named figures inside named quotes, not a derived numeric computation.

*Source: proof.py JSON summary — `evidence[].extraction`; method narrative: author analysis*

## Quality Checks

- **Rule 1 — No hand-typed extracted values:** PASS. Sub-claim outcomes derive from `verify_all_citations()` output, not hand-typed.
- **Rule 2 — Citation verification:** PASS. All four citations fetched/snapshot-verified via the `proof_citations` package.
- **Rule 3 — System time:** N/A. Proof is not time-sensitive.
- **Rule 4 — Claim interpretation:** PASS. CLAIM_FORMAL contains operator_note for each sub-claim and an aggregate operator_note.
- **Rule 5 — Adversarial checks:** PASS. Four counter-evidence questions investigated; findings documented.
- **Rule 6 — Cross-checks:** Single-source by design. The proof structure is correct for "what does the paper report" claims; the validator's per-SC source-count warning is acknowledged and explained above.
- **Rule 7 — No hard-coded constants/formulas:** PASS. Uses `compare()` and `apply_verdict_qualifier()` from the proof-engine computations module.
- **validate_proof.py result:** PASS with warnings — 23/27 checks passed, 0 issues, 4 warnings (all four warnings are the per-SC single-source notes addressed above).

## Generator

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) on 2026-05-20.
