# Proof: <!-- not-a-citation-start -->Topaz et al. (2026)<!-- not-a-citation-end --> analyzed 2.5 million biomedical papers in PubMed Central from January 2023 through February 2026 and identified 4,046 references pointing to studies that do not exist, distributed across 2,810 papers.

- **Generated:** 2026-05-20
- **Verdict:** PROVED
- **Audit trail:** see [proof_audit.md](proof_audit.md); re-run [proof.py](proof.py)

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | SC1: corpus size from Topaz et al. 2026 methods | Yes |
| B2 | SC2: date range from Topaz et al. 2026 methods | Yes |
| B3 | SC3: 4046 fabricated references (Topaz et al. 2026 results) | Yes |
| B4 | SC4: 2810 affected papers (Topaz et al. 2026 limitations) | Yes |
| A1 | SC1 verified-source count | Computed: 1 quote verified in source paper |
| A2 | SC2 verified-source count | Computed: 1 quote verified in source paper |
| A3 | SC3 verified-source count | Computed: 1 quote verified in source paper |
| A4 | SC4 verified-source count | Computed: 1 quote verified in source paper |

All four citations resolve against the Topaz et al. 2026 PDF snapshot at tier-4 academic credibility (thelancet.com).

## Proof Logic

The claim is a four-part compound assertion about what a single, named source — the Topaz et al. 2026 correspondence in *The Lancet* — reports. Because the claim is about what the paper says (not about the ground-truth fabrication rate in PubMed Central), the appropriate evidence is verbatim text from that paper.

**SC1 — Corpus size (≈2.5 million papers in PubMed Central).** The paper's methods sentence (B1) states the system scanned "2 471 758 papers and 125 615 773 structured references" from PubMed Central's Open Access subset. The paper's own title rounds this to "2·5 million biomedical papers," matching the claim's "2.5 million" figure.

**SC2 — Time window (January 2023 through February 2026).** The same methods sentence (B2) specifies "Jan 1, 2023, to Feb 18, 2026." The claim's month-resolution phrasing "January 2023 through February 2026" is a faithful summary of this interval; both endpoints fall within the named months, with the early-2026 quarter explicitly flagged in the paper as an incomplete (7-week) period.

**SC3 — 4,046 fabricated references.** The paper's results sentence (B3) states verbatim: "Among 97·1 million verified references, we identified 4046 fabricated references across 2810 papers." The paper defines "fabricated references" as "references whose claimed titles correspond to no existing publication" — semantically equivalent to the claim's "references pointing to studies that do not exist."

**SC4 — 2,810 affected papers.** The same results sentence (B3) covers this count, and the paper's limitations section provides an independent in-paper restatement (B4): "Of the 2810 affected papers, 98·4% had received no publisher action at the time of our audit." Two distinct sentences in the same article report the same figure, providing internal corroboration.

Each verbatim quote was located in a pypdf-extracted text snapshot of the uploaded source PDF and confirmed with the proof-engine's citation verifier. All four sub-claim evaluations return `True`, so the compound `claim_holds` = `n_holding == n_total` = `4 == 4` = `True`.

*Source: author analysis*

## What could challenge this verdict?

Four adversarial questions were investigated; none break the proof.

The paper's headline term is "fabricated references," but the supplementary appendix uses the more cautious "suspected fabricated references" and reports a pipeline precision of 91% (Fleiss' κ = 0.71, from a 500-entry masked validation by three independent reviewers). Strictly, this means the *true* number of references-to-nothing is approximately 4046 × 0.91 ≈ 3,682 — not exactly 4,046. The claim under verification, however, is about what the paper *reports*, and the paper reports 4,046 as the headline figure without precision adjustment.

The paper was published as *Lancet* correspondence on May 9, 2026; today's date is May 20, 2026. Eleven days post-publication leaves essentially no window for a formal retraction or correction to appear, and none is attached to the uploaded PDF.

The claim phrases the date range as "January 2023 through February 2026," while the paper specifies "Jan 1, 2023, to Feb 18, 2026." The month-level phrasing is a common and accurate way to summarize an interval ending Feb 18 — it does not imply analysis through Feb 28.

The "2.5 million" figure matches the paper's own headline rounding of 2,471,758 (which is 2.47M, rounding to 2.5M at two significant figures).

*Source: proof.py JSON summary — `adversarial_checks`*

## Conclusion

**Verdict: PROVED.** All four sub-claims are confirmed by verbatim text in the Topaz et al. 2026 *Lancet* correspondence:
- Corpus: 2,471,758 PubMed Central papers (rounded to 2.5M by the paper itself in its title)
- Window: Jan 1, 2023 to Feb 18, 2026 (faithfully summarized as "January 2023 through February 2026")
- Fabricated references: 4,046
- Affected papers: 2,810

All four citations are fully verified against the source PDF snapshot. No unverified citations, no COI override, no adversarial check breaks the proof.

One contextual caveat that does not affect the verdict: the paper's own supplementary appendix uses "suspected fabricated references" and reports 91% pipeline precision. A reader citing the 4,046 figure should understand this is the pipeline's classification, not a ground-truth count of confirmed fabrications; the true count is approximately 9% lower. This does not change what the paper reports.

*Source: proof.py JSON summary — `verdict`, `key_results`*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) on 2026-05-20.
