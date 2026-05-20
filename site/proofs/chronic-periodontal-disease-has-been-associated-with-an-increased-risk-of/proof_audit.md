# Proof Audit: Periodontal Disease and ASCVD

**Generated:** 2026-05-20
**Verdict:** PROVED
**Confirmed sources:** 4 of 4 (threshold ≥ 3)
**Re-runnable artifact:** `proof.py` (executed against the `proof-citations` PyPI package, Python 3.11)

This document covers the full verification details and machine-checkable provenance of the proof. The reader-facing summary is in `proof.md`; the plain-language narrative is in `proof_narrative.md`; the structured machine-readable summary is in `proof.json`.

## 1. Claim and Formalization

**Natural-language claim.** "Chronic periodontal disease has been associated with an increased risk of atherosclerotic cardiovascular disease in adults, with consensus reviews pointing to systemic inflammation as a biologically plausible mediating mechanism (Tonetti & Van Dyke, 2013; Sanz et al., 2020; Cullinan & Ford, 2013)."

**Formalization.**

- **subject:** Chronic periodontal disease and atherosclerotic cardiovascular disease (ASCVD).
- **property:** Consensus reviews in periodontology and cardiology report (a) a statistically meaningful association between periodontitis and incident ASCVD in adults that is independent of established cardiovascular risk factors, and (b) systemic inflammation as a biologically plausible mediating mechanism for this association.
- **operator:** ≥
- **threshold:** 3 independent consensus reviews or scientific statements.
- **proof_direction:** affirm.

**Operator note.** The claim is read as **associational, not causal**. The phrasing "has been associated with" and "biologically plausible mediating mechanism" is deliberately weaker than "causes" or "established mechanism." A causal claim would require a separate, stricter proof and would currently not reach PROVED on the existing evidence (Mendelian-randomization studies do not demonstrate genetic causality; the AHA 2012 statement explicitly rejects causation).

**Attribution correction.** The user's citation "Cullinan & Ford, 2013" does not correspond to any indexed publication. The 2013 Periodontology 2000 review is by Cullinan MP and Seymour GJ (10.1111/prd.12007). Ford is co-author on the 2009 Australian Dental Journal review by Cullinan, Ford and Seymour. This is treated as a benign mis-citation — same year, same scope, substitute paper makes the same assertion — and is documented as Adversarial Check #2 below.

## 2. Fact Registry

| ID | Type | Source key | Label |
|---|---|---|---|
| B1 | empirical | `tonetti_van_dyke_2013` | Tonetti & Van Dyke 2013, EFP/AAP Joint Workshop consensus report |
| B2 | empirical | `sanz_2020` | Sanz et al. 2020, EFP/WHF Perio-Cardio Workshop consensus report |
| B3 | empirical | `cullinan_seymour_2013` | Cullinan & Seymour 2013, Periodontology 2000 review (substitute for the user's "Cullinan & Ford 2013") |
| B4 | empirical | `aha_2012` | Lockhart et al. 2012, AHA Scientific Statement (Circulation) — independent cardiology corroboration |
| A1 | computed | — | Verified source count |

## 3. Citation Verification Details

All quotes were verified character-for-character against the rendered text of the cited page using the `proof-citations` PyPI package (`verify_all_citations(..., wayback_fallback=True)`). Snapshots of each page are saved under `snapshots/` so the proof is self-contained for future re-verification.

| ID | URL | Status | Method | Fetch mode | Credibility | Impact |
|---|---|---|---|---|---|---|
| B1 | pubmed.ncbi.nlm.nih.gov/23627332/ | verified | full_quote | live | tier 5 (.gov) | counts toward threshold |
| B2 | pubmed.ncbi.nlm.nih.gov/32011025/ | verified | full_quote | live | tier 5 (.gov) | counts toward threshold |
| B3 | pubmed.ncbi.nlm.nih.gov/23574472/ | verified | full_quote | live | tier 5 (.gov) | counts toward threshold |
| B4 | Wayback snapshot of pubmed.ncbi.nlm.nih.gov/22514251/ (archived 2026-01-28) | verified | full_quote | live | tier 2 (Wayback, `no_https`) | counts toward threshold |

**B4 verification note.** The live PubMed URL for the AHA 2012 statement returned a reCAPTCHA challenge page from this verification environment, causing the inline live fetch to retrieve content that did not contain the quote. The Wayback Machine archive of the same PubMed page (captured 2026-01-28) contains the abstract verbatim and was used as the canonical verification URL. The original PubMed URL is preserved in the source citation string for human reference. This is a Hardening-Rule-2 fallback (see `references/environment-and-sources.md` in the skill).

## 4. Cross-Check

Four independent consensus statements consulted, spanning:

- **Convening bodies:** European Federation of Periodontology (EFP), American Academy of Periodontology (AAP), World Heart Federation (WHF), American Heart Association (AHA).
- **Disciplines:** periodontology (B1, B2, B3) and cardiology (B4).
- **Time window:** 2012 (B4) through 2020 (B2) — 8-year span.
- **Authorship:** B1 and B2 share Tonetti as a co-author; B3 and B4 have non-overlapping author teams; B4's authorship is entirely independent of the periodontology consensus reviews.

**Independence rationale.** The AHA 2012 statement (B4) is the strongest individual cross-check. It is convened by a cardiology body, written largely by cardiologists, and is the most skeptical of the four sources — it explicitly **rejects** causation and yet still affirms the associational claim. Its agreement reduces the risk that the apparent consensus is an artifact of periodontology-internal self-promotion or sponsor capture.

## 5. Adversarial Checks (Hardening Rule 5)

### AC1 — Mendelian-randomization counter-evidence

**Question.** Do recent reviews or Mendelian-randomization (MR) studies overturn the epidemiological association between periodontitis and ASCVD?

**Verification performed.** Searched PubMed and the web (2022–2026) for counter-evidence using terms including "periodontitis cardiovascular disease no evidence", "periodontitis CVD not causal", "Mendelian randomization periodontitis ASCVD." Located:

- Carra MC et al. 2024, "Periodontitis and atherosclerotic cardiovascular disease: A critical appraisal." *Periodontology 2000*. 10.1111/prd.12528 — explicitly notes "the positive associations observed in epidemiological studies between periodontitis and ASCVD may also be influenced by various biases, such as confounding and collider stratification," yet still concludes the **association** is real.
- Brodzikowska A, Górski B. 2022, "Is There a Causal Link Between Periodontitis and Cardiovascular Disease? A Concise Review of Recent Findings." PMC9275186 — concludes Mendelian-randomization studies have so far failed to demonstrate genetic causality.

**Finding.** Counter-evidence is directed at the stronger **causal** claim. None of it overturns the **associational** claim that the proof under audit actually asserts. The "biologically plausible" framing in the claim is also consistent with this critical-appraisal literature — none of the critical reviews argue that systemic inflammation is *implausible* as a mediating mechanism; they argue that current evidence does not yet meet the causal-inference bar.

**Breaks proof?** No.

### AC2 — Mis-attributed citation ("Cullinan & Ford, 2013")

**Question.** Is "Cullinan & Ford, 2013" a real publication, or is the user's citation mis-attributed?

**Verification performed.** Searched PubMed and Google Scholar for any 2012–2013 Cullinan-and-Ford periodontal-systemic review. No such paper exists. The 2013 Periodontology 2000 review is Cullinan MP & Seymour GJ (PMID 23574472). The Ford co-authorship is on the 2009 Australian Dental Journal review by Cullinan, Ford and Seymour (10.1111/j.1834-7819.2009.01144.x).

**Finding.** Attribution error confirmed. Treated as benign mis-citation — same year, same scope, substitute paper (Cullinan & Seymour 2013) makes the same assertion. Documented transparently in `CLAIM_FORMAL.operator_note` and in B3's source label.

**Breaks proof?** No.

### AC3 — Discipline-internal bias and sponsor capture

**Question.** Could publication bias or sponsor capture inflate the apparent consensus among periodontology consensus statements?

**Verification performed.** Checked authorship and convening bodies. B1 and B2 are joint perio-cardio workshops with cardiology co-leadership (B1 included Van Dyke from the Forsyth Institute; B2 was co-led with the World Heart Federation and includes cardiology co-authors such as Gonzalez-Juanatey and Vlachopoulos). B4 (AHA 2012) is convened by a cardiology body, not periodontology.

**Finding.** Cross-disciplinary corroboration is present. The most skeptical of the four sources (B4) is the one farthest from periodontology interests.

**Breaks proof?** No.

## 6. COI Flags

No conflict-of-interest flag raised. All four sources are peer-reviewed consensus statements or scientific statements from major medical and dental societies. None has a commercial sponsor steering the conclusions, and the cardiology-convened source (B4) is the most conservative, not the most enthusiastic.

## 7. Verdict Derivation

```
n_confirmed = 4   (B1, B2, B3, B4 all verified)
threshold   = 3
operator    = ">="
claim_holds = compare(4, ">=", 3) = True
any_unverified = False
any_breaks     = False (no adversarial check sets breaks_proof = True)
coi_override   = False (no COI flags)
proof_direction = "affirm"
=> base_verdict = "PROVED"
=> verdict      = apply_verdict_qualifier("PROVED", any_unverified=False) = "PROVED"
```

## 8. Verdict

**PROVED.** All four independent consensus reviews and scientific statements consulted affirm both the associational and the mechanism-plausibility components of the claim. The threshold (≥ 3 independent verified sources) is exceeded (4/4). Counter-evidence located by adversarial search targets only the stronger causal claim, which the proof under audit explicitly does not assert.

## 9. Re-verification Instructions

```bash
# Requires Python 3.11+
python -m venv .venv && source .venv/bin/activate
pip install proof-citations
python proof.py
```

Expected output:

```
  [✓] tonetti_van_dyke_2013: Full quote verified ... tier 5/government
  [✓] sanz_2020: Full quote verified ... tier 5/government
  [✓] cullinan_seymour_2013: Full quote verified ... tier 5/government
  [✓] aha_2012: Full quote verified ... tier 2/unknown [no_https]
  Confirmed sources: 4 / 4
  verified consensus-review count vs. threshold: 4 >= 3 = True

=== VERDICT: PROVED ===
```

PubMed occasionally serves reCAPTCHA challenges to automated fetchers. If B1, B2, or B3 returns `not_found`, wait 15–30 seconds and re-run; the snapshots under `snapshots/` are not currently auto-used because live fetch succeeds with a non-empty (challenge) page. The Wayback URL for B4 is stable.
