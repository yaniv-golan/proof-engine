# Audit: Daily low-dose aspirin reduces the risk of recurrent non-fatal myocardial infarction in patients with prior cardiovascular disease, per the Antithrombotic Trialists' Collaboration meta-analysis

- **Generated:** 2026-05-20
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The natural-language claim is: "Daily low-dose aspirin reduces the risk of recurrent non-fatal myocardial infarction in patients with prior cardiovascular disease, per the Antithrombotic Trialists' Collaboration meta-analysis."

The claim uses causal language ("reduces the risk"). Under the Proof Engine's causal rule, a causal claim must be decomposed into an association sub-claim and a causation sub-claim; the `operator_note` may not redefine the claim as merely associational to avoid this. The formal interpretation is therefore a compound (AND) claim with two sub-claims:

- **SC1 (association):** The Antithrombotic Trialists' (ATT) Collaboration meta-analysis found daily low-dose aspirin associated with a reduction in non-fatal myocardial infarction (MI) among patients with prior cardiovascular disease (CVD). Operator: count of verified ATT-source quotations `>=` 2.
- **SC2 (causation):** The ATT meta-analysis pools randomized controlled trials (RCTs), so the observed reduction has a causal — not merely correlational — basis. Operator: count of verified ATT-source quotations `>=` 2.

Both sub-claims must hold for a PROVED verdict.

The source-count threshold is **2** rather than the default **3**. This reduction is justified under the Proof Engine's threshold-2 conditions: (1) *domain scarcity* — the claim explicitly restricts the evidence base to one named source program, the ATT Collaboration meta-analysis, and the ATT Collaboration produced exactly two landmark meta-analyses bearing on this question (the 2002 *BMJ* collaborative overview and the 2009 *Lancet* individual-participant-data meta-analysis); (2) *source quality* — both are peer-reviewed in top-tier journals and each pools large randomized-trial datasets (≈135,000 and ≈17,000 patients respectively), well above any per-domain minimum; (3) *no majority conflict of interest* — the ATT Collaboration is an independent academic consortium funded by the UK Medical Research Council, British Heart Foundation, Cancer Research UK, and the EC Biomed Programme, with no aspirin-manufacturer funding; (4) the rationale is documented in `CLAIM_FORMAL.operator_note`.

**Formalization scope.** The formal interpretation operationalizes three natural-language terms, each documented in `operator_note`:

- *"Patients with prior cardiovascular disease"* is interpreted as the secondary-prevention / high-risk population the ATT analyses studied (acute or previous occlusive vascular disease).
- *"Recurrent non-fatal myocardial infarction"* is interpreted as non-fatal MI events occurring within that established-disease population. The ATT analyses include an explicit "previous myocardial infarction" patient category in which any subsequent non-fatal MI is unambiguously recurrent; for the broader prior-CVD population the proof treats non-fatal MI as a recurrent vascular event because the population already has established disease.
- *"Low-dose aspirin"* is interpreted as the 75–150 mg/day range the 2002 ATT overview found "at least as effective as higher daily doses."

These are operationalizations of an otherwise faithful mapping; no element of the natural-language claim is excluded. The phrase "per the Antithrombotic Trialists' Collaboration meta-analysis" is treated as an attribution constraint and is satisfied by evaluating the claim directly against the ATT Collaboration's own publications.

*Source: proof.py JSON summary `claim_formal` and `claim_natural`.*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Daily low-dose aspirin and recurrent non-fatal MI in patients with prior CVD, as assessed by the ATT Collaboration meta-analyses |
| Compound operator | AND (both sub-claims must hold) |
| SC1 | Association: low-dose aspirin associated with reduced non-fatal MI in prior-CVD patients — operator `>=`, threshold 2 |
| SC2 | Causation: ATT meta-analysis pools randomized controlled trials — operator `>=`, threshold 2 |
| Time-sensitive | No |
| Proof direction | Affirmative (prove) |

*Source: proof.py JSON summary `claim_formal`.*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | sc1_att2002_mi | SC1 — ATT 2002 BMJ: non-fatal MI reduced by one third in high-risk patients |
| B2 | sc1_att2002_dose | SC1 — ATT 2002 BMJ: low-dose aspirin (75–150 mg) at least as effective as higher doses |
| B3 | sc1_att2009 | SC1 — ATT 2009 Lancet: aspirin reduces serious vascular events in secondary-prevention trials |
| B4 | sc2_att2002 | SC2 — ATT 2002 BMJ: inclusion restricted to randomised trials |
| B5 | sc2_att2009 | SC2 — ATT 2009 Lancet: meta-analysis of individual participant data from randomised trials |
| A1 | — | SC1 verified source count |
| A2 | — | SC2 verified source count |

*Source: proof.py JSON summary `fact_registry`.*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | SC1 verified source count | count(verified sc1 citations) | 3 |
| A2 | SC2 verified source count | count(verified sc2 citations) | 2 |

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote (truncated) | Status | Method | Credibility |
|----|------|--------|-----|-------------------|--------|--------|-------------|
| B1 | Non-fatal MI reduced by one third in high-risk patients | ATT Collaboration, BMJ 2002;324:71–86 (PMC64503) | https://pmc.ncbi.nlm.nih.gov/articles/PMC64503/ | Overall, among these high risk patients, allocation to antiplatelet therapy reduced the combined outcome… | verified | full_quote | Government |
| B2 | Low-dose aspirin 75–150 mg at least as effective as higher doses | ATT Collaboration, BMJ 2002;324:71–86 (PMC64503) | https://pmc.ncbi.nlm.nih.gov/articles/PMC64503/ | Aspirin was the most widely studied antiplatelet drug, with doses of 75-150 mg daily at least as effective… | verified | full_quote | Government |
| B3 | Aspirin reduces serious vascular events in secondary prevention | ATT Collaboration, Lancet 2009;373:1849–60 (PMID 19482214) | https://pubmed.ncbi.nlm.nih.gov/19482214/ | In the secondary prevention trials, aspirin allocation yielded a greater absolute reduction in serious… | verified | full_quote | Government |
| B4 | Inclusion restricted to randomised trials | ATT Collaboration, BMJ 2002;324:71–86 (PMC64503) | https://pmc.ncbi.nlm.nih.gov/articles/PMC64503/ | Randomised trials of an antiplatelet regimen versus control or of one antiplatelet regimen versus another… | verified | full_quote | Government |
| B5 | Meta-analysis of individual participant data from randomised trials | ATT Collaboration, Lancet 2009;373:1849–60 (PMID 19482214) | https://pubmed.ncbi.nlm.nih.gov/19482214/ | collaborative meta-analysis of individual participant data from randomised trials | verified | full_quote | Government |

*Source: proof.py JSON summary `citations` and `fact_registry`.*

## Citation Verification Details

**B1 — ATT 2002 BMJ, non-fatal MI reduction**
- Status: verified
- Method: full_quote (exact verbatim substring match; coverage_pct not applicable)
- Fetch mode: live
- Verbatim status: verbatim quote (declared default)

**B2 — ATT 2002 BMJ, low-dose equivalence**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Verbatim status: verbatim quote

**B3 — ATT 2009 Lancet, secondary-prevention reduction**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Verbatim status: verbatim quote (copied from the PubMed abstract page; the verified substring stops before the journal's middle-dot decimal and `<`-encoded p-values to avoid Unicode/entity ambiguity)

**B4 — ATT 2002 BMJ, randomised-trial inclusion criteria**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Verbatim status: verbatim quote

**B5 — ATT 2009 Lancet, individual participant data from randomised trials**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Verbatim status: verbatim quote (substring of the article title as printed on the PubMed page)

All five citations verified on the recorded execution (fetch mode `live` for each). No citation is unverified, so no conclusion in proof.md depends on unverified evidence.

**Snapshot fallback.** PubMed Central is a known bot-throttling domain, and during verification one transient live-fetch failure was observed on a single PMC citation. To make the verdict robust against such intermittent blocks, each citation carries a bundled offline snapshot of its source page, captured 2026-05-20 (`snapshots/pmc64503.html` for the 2002 BMJ paper, `snapshots/pubmed19482214.html` for the 2009 Lancet abstract). The verifier uses the fallback chain live → snapshot → Wayback; a separate test forcing every live fetch to fail confirmed all five citations still verify verbatim against the snapshots (status `verified`, fetch mode `snapshot`). The verdict therefore does not depend on live network conditions at re-run time.

*Source: proof.py JSON summary `citations`; snapshot-fallback test is author analysis.*

## Computation Traces

```
  SC1 (association): verified ATT sources: 3 >= 2 = True
  SC2 (causation): verified ATT sources: 2 >= 2 = True
  compound: all sub-claims hold: 2 == 2 = True
```

*Source: proof.py inline output (execution trace).*

## Independent Source Agreement (Rule 6)

**SC1 cross-check** — 3 sources consulted, 3 verified, agreement: holds. SC1 draws on two distinct ATT meta-analyses published seven years apart in different journals (*BMJ* 2002, *Lancet* 2009) using different methods (tabular data versus individual participant data) and overlapping but non-identical trial sets. B1 and B2 are two distinct findings from the 2002 *BMJ* paper (the non-fatal-MI reduction and the low-dose equivalence); B3 is from the independent 2009 *Lancet* meta-analysis.

**SC2 cross-check** — 2 sources consulted, 2 verified, agreement: holds. SC2 is confirmed by both ATT publications independently: the 2002 *BMJ* paper restricts inclusion to randomised trials, and the 2009 *Lancet* paper is a meta-analysis of individual participant data from randomised trials. Two separate publications each document the randomized-controlled-trial basis.

**Conflict-of-interest assessment (`coi_flags`).** Both sub-claims carry an explicit `coi_flags` field, each an empty list. The ATT Collaboration is an independent academic consortium; its funders (UK Medical Research Council, British Heart Foundation, Cancer Research UK, EC Biomed Programme) include no aspirin manufacturer, so there is no funding-dependency COI. The collaboration's 2009 *Lancet* paper concluded that aspirin is "of uncertain net value" in primary prevention — evidence that it reports null and negative findings and is not biased toward a pro-aspirin verdict. One independence limitation is noted transparently rather than as a COI: the claim names the ATT meta-analysis as its source, so all primary evidence necessarily comes from ATT publications; the proof mitigates this by using two distinct ATT meta-analyses and by cross-referencing the broader independent literature in the adversarial checks below. No majority COI exists; the COI override does not fire.

*Source: proof.py JSON summary `cross_checks`.*

## Adversarial Checks (Rule 5)

Five counter-evidence checks were performed during research (Step 2). None breaks the proof.

**1. Is the attribution to the ATT meta-analysis accurate?**
Verification performed: Fetched and read the ATT 2002 *BMJ* meta-analysis (PMC64503) and the ATT 2009 *Lancet* meta-analysis abstract (PubMed 19482214); searched for the verbatim findings on non-fatal MI and secondary prevention.
Finding: The attribution is accurate. The 2002 *BMJ* paper explicitly states that, among high-risk patients, non-fatal MI "was reduced by one third"; the 2009 *Lancet* paper reports reduced serious vascular and coronary events in secondary-prevention trials. No mismatch between the claim and the named source was found.
Breaks proof: No.

**2. Does aspirin's bleeding harm contradict the reduction in non-fatal MI?**
Verification performed: Searched for counter-evidence on aspirin's bleeding harms and net benefit in secondary prevention (gastrointestinal / extracranial bleeding meta-analyses).
Finding: Aspirin does increase major extracranial and gastrointestinal bleeding — a well-documented, separate harm. This does not contradict the claim, which concerns the non-fatal-MI outcome specifically, not net clinical benefit. The 2002 ATT paper itself reports that in the high-risk categories "the absolute benefits substantially outweighed the absolute risks of major extracranial bleeding." Bleeding is a treatment trade-off, not evidence against the MI-reduction finding.
Breaks proof: No.

**3. Is the secondary-prevention benefit contradicted by more recent evidence?**
Verification performed: Searched 2020–2025 reviews and meta-analyses questioning aspirin in secondary prevention, including recent commentary and a 2025 systematic review/meta-analysis of aspirin for secondary prevention of MI.
Finding: Recent commentary debates whether aspirin's marginal benefit is as large in the modern statin/revascularization era and notes P2Y12 inhibitors as alternatives. However, a 2025 systematic review/meta-analysis still found aspirin reduced recurrent events by roughly a fifth in secondary prevention, and no source claims the ATT finding of reduced non-fatal MI was wrong or reversed. The direction of effect is confirmed by modern evidence; only the magnitude and role relative to newer therapies are debated. This does not break a proof scoped to the ATT meta-analysis finding.
Breaks proof: No.

**4. Does "low-dose" aspirin specifically carry the non-fatal MI reduction?**
Verification performed: Checked the ATT 2002 *BMJ* dose analysis and the scope of the 2009 *Lancet* meta-analysis.
Finding: Supported. The 2002 ATT meta-analysis found doses of 75–150 mg daily "at least as effective as higher daily doses" and identified aspirin as "the most widely studied antiplatelet drug"; the 2009 ATT meta-analysis is explicitly an analysis of low-dose aspirin. The 2002 paper notes the effects of doses below 75 mg are "less certain," but standard low-dose aspirin (75–150 mg) is squarely within the supported range.
Breaks proof: No.

**5. Could "recurrent" non-fatal MI be unsupported because the meta-analysis pooled mixed prior-CVD populations?**
Verification performed: Reviewed the ATT meta-analysis patient categories in the 2002 *BMJ* and 2009 *Lancet* reports.
Finding: The ATT meta-analysis explicitly includes a "previous myocardial infarction" patient category among its high-risk groups (six secondary-prevention prior-MI trials in the 2009 analysis), in which a subsequent non-fatal MI is by definition recurrent. The proof interprets "recurrent non-fatal MI in patients with prior CVD" as non-fatal MI events within the established-CVD secondary-prevention population the ATT analyzed — an interpretation documented in the operator_note that does not overstate the source.
Breaks proof: No.

*Source: proof.py JSON summary `adversarial_checks`.*

## Source Credibility Assessment

| Fact ID | Domain | Type | Note |
|---------|--------|------|------|
| B1 | nih.gov | Government | PubMed Central, full text of the 2002 BMJ paper; credibility tier 5/5 |
| B2 | nih.gov | Government | PubMed Central, full text of the 2002 BMJ paper; credibility tier 5/5 |
| B3 | nih.gov | Government | PubMed abstract index, 2009 Lancet paper; credibility tier 5/5 |
| B4 | nih.gov | Government | PubMed Central, full text of the 2002 BMJ paper; credibility tier 5/5 |
| B5 | nih.gov | Government | PubMed abstract index, 2009 Lancet paper; credibility tier 5/5 |

All sources are government-hosted (U.S. National Institutes of Health) reproductions of peer-reviewed articles. No source is flagged unreliable; no source falls at credibility tier 2 or below.

*Source: proof.py JSON summary `citations[].credibility`.*

## Source Data

This is a qualitative/source-counting proof — no numeric values are parsed from quotes. The `extractions` field records citation verification status per source instead of extracted values.

| Fact ID | Verification status | Counted toward sub-claim | Quote snippet |
|---------|--------------------|--------------------------|---------------|
| B1 | verified | Yes (SC1) | Overall, among these high risk patients, allocation to antiplatelet… |
| B2 | verified | Yes (SC1) | Aspirin was the most widely studied antiplatelet drug, with doses of 75-150 mg… |
| B3 | verified | Yes (SC1) | In the secondary prevention trials, aspirin allocation yielded a greater… |
| B4 | verified | Yes (SC2) | Randomised trials of an antiplatelet regimen versus control or of one… |
| B5 | verified | Yes (SC2) | collaborative meta-analysis of individual participant data from randomised trials |

Extraction method (author analysis): No value extraction was performed. Each fact is established by verbatim citation presence; `verify_all_citations()` confirmed each quote is an exact substring of the fetched source page after HTML stripping and Unicode normalization. SC1 and SC2 source counts (A1, A2) were computed by counting facts whose verification status is `verified` or `partial`.

*Source: proof.py JSON summary `extractions`; extraction-method narrative is author analysis.*

## Quality Checks

- **Rule 1 (no hand-typed values):** N/A — qualitative source-counting proof; no numeric values parsed from quotes. Validator: no value-extraction patterns detected.
- **Rule 2 (citations verified by fetching):** Pass — all five citations fetched live and verified verbatim via `verify_all_citations()`; each also carries a bundled offline snapshot as a verified fallback.
- **Rule 3 (anchor to system time):** N/A — claim is not time-sensitive (`is_time_sensitive: False`); no date-dependent logic.
- **Rule 4 (explicit claim interpretation):** Pass — `CLAIM_FORMAL` with `operator_note` documents the causal decomposition, the term operationalizations, and the threshold-2 rationale.
- **Rule 5 (independent adversarial check):** Pass — five counter-evidence checks, performed via web search and direct source reading; none breaks the proof.
- **Rule 6 (independent cross-checks):** Pass — two distinct ATT meta-analyses (different journals, methods, trial sets); `coi_flags` assessed (empty, no aspirin-manufacturer funding).
- **Rule 7 (no hard-coded constants/formulas):** Pass — `compare()` and `apply_verdict_qualifier()` imported from `computations.py`; no `eval()` or hard-coded constants.
- **validate_proof.py result:** PASS — 21/21 checks passed, 0 issues, 0 warnings.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.34.1 on 2026-05-20.
