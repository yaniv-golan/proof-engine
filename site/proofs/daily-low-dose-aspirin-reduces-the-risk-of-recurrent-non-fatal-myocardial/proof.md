# Proof: Daily low-dose aspirin reduces the risk of recurrent non-fatal myocardial infarction in patients with prior cardiovascular disease, per the Antithrombotic Trialists' Collaboration meta-analysis

- **Generated:** 2026-05-20
- **Verdict:** PROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) (verification detail) · [proof.py](proof.py) (re-runnable script)

The claim uses causal language ("reduces the risk"), so it was decomposed into two sub-claims that must both hold: SC1 — daily low-dose aspirin is *associated* with reduced non-fatal myocardial infarction in patients with prior cardiovascular disease; SC2 — that reduction is *causal*, because the Antithrombotic Trialists' (ATT) Collaboration meta-analysis pools randomized controlled trials. Both sub-claims were evaluated against the ATT Collaboration's own publications, the source the claim explicitly names.

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | ATT 2002 BMJ overview: among high-risk patients, non-fatal myocardial infarction was reduced by about one third | Yes |
| B2 | ATT 2002 BMJ overview: low-dose aspirin (75–150 mg daily) at least as effective as higher daily doses | Yes |
| B3 | ATT 2009 Lancet meta-analysis: in secondary-prevention trials, aspirin produced a greater absolute reduction in serious vascular events | Yes |
| B4 | ATT 2002 BMJ overview: inclusion restricted to randomised trials of an antiplatelet regimen versus control | Yes |
| B5 | ATT 2009 Lancet meta-analysis: a collaborative meta-analysis of individual participant data from randomised trials | Yes |
| A1 | SC1 (association) verified ATT source count | Computed: 3 ATT sources verified (threshold: 2) |
| A2 | SC2 (causation) verified ATT source count | Computed: 2 ATT sources verified (threshold: 2) |

All five empirical citations were fetched live and verified verbatim against government-hosted pages (PubMed Central and PubMed, both nih.gov, credibility tier 5/5).

## Proof Logic

The claim attributes a causal effect ("reduces the risk") to a specific named evidence source ("the Antithrombotic Trialists' Collaboration meta-analysis"). The proof therefore did two things: confirmed that the named source reports the effect, and confirmed that the source's design supports a causal — not merely correlational — reading.

### SC1 — Association: low-dose aspirin and reduced non-fatal MI in prior-CVD patients

The ATT Collaboration's 2002 *BMJ* collaborative overview pooled 287 randomized trials covering roughly 135,000 high-risk patients — defined as patients with acute or previous occlusive vascular disease, i.e. the secondary-prevention population. Among those patients, "non-fatal myocardial infarction was reduced by one third" under antiplatelet therapy (B1). Because the claim specifies *low-dose* aspirin, the proof also confirmed that the same overview found aspirin "the most widely studied antiplatelet drug, with doses of 75-150 mg daily at least as effective as higher daily doses" (B2) — so the one-third reduction applies to standard low-dose aspirin, not only to higher doses or to other antiplatelet agents.

The ATT Collaboration's later 2009 *Lancet* meta-analysis, which pooled individual participant data from 16 secondary-prevention trials (about 17,000 patients with prior vascular disease, including six trials of patients with previous myocardial infarction), independently confirmed the direction: "in the secondary prevention trials, aspirin allocation yielded a greater absolute reduction in serious vascular events" (B3), a category the paper defines as myocardial infarction, stroke, or vascular death. SC1 required at least 2 verified ATT sources and obtained 3 (A1), so SC1 holds.

### SC2 — Causation: the reduction rests on randomized controlled trials

An association alone would not establish that aspirin *reduces* risk rather than merely co-occurring with lower risk. The ATT meta-analyses settle this by design: they pool only randomized controlled trials. The 2002 *BMJ* overview restricted inclusion to "Randomised trials of an antiplatelet regimen versus control or of one antiplatelet regimen versus another in high risk patients" (B4), and required that comparisons be unconfounded. The 2009 *Lancet* paper is, by its own title, "a collaborative meta-analysis of individual participant data from randomised trials" (B5). Random allocation removes systematic confounding, so a reduction observed consistently across pooled randomized trials supports a causal interpretation — this is the gold-standard evidence class for causal inference. SC2 required at least 2 verified ATT sources and obtained 2 (A2), so SC2 holds.

### Compound result

Both sub-claims hold (2 of 2). Under the AND operator, the compound causal claim is established: the ATT Collaboration meta-analysis reports that daily low-dose aspirin reduces the risk of recurrent non-fatal myocardial infarction in patients with prior cardiovascular disease.

## What could challenge this verdict?

Five independent counter-evidence checks were run during research; none broke the proof.

*Is the attribution accurate?* The claim names a specific source, so the first check was whether the ATT meta-analysis actually reports this. Both ATT papers were fetched and read directly: the 2002 *BMJ* overview states the one-third non-fatal-MI reduction explicitly, and the 2009 *Lancet* paper confirms reduced serious vascular and coronary events in secondary prevention. The attribution is accurate.

*Does aspirin's bleeding harm contradict the finding?* Aspirin increases major gastrointestinal and extracranial bleeding — a real, separate harm. But the claim concerns the non-fatal-MI outcome specifically, not net clinical benefit. The 2002 ATT overview itself reports that in high-risk categories "the absolute benefits substantially outweighed the absolute risks of major extracranial bleeding." Bleeding is a treatment trade-off, not evidence against the MI-reduction finding.

*Has more recent evidence overturned the finding?* Recent (2020–2025) commentary debates whether aspirin's *marginal* benefit is as large in the modern era of statins and revascularization, and notes newer P2Y12 inhibitors as alternatives. But a 2025 systematic review and meta-analysis still found aspirin reduced recurrent events by roughly a fifth in secondary prevention. No source claims the ATT finding was wrong or reversed; only its magnitude and role relative to newer drugs are debated.

*Does "low-dose" specifically carry the effect?* The 2002 ATT overview found 75–150 mg daily at least as effective as higher doses, and the 2009 ATT meta-analysis is explicitly an analysis of low-dose aspirin. The 2002 paper notes effects of doses *below* 75 mg are "less certain," but standard low-dose aspirin (75–150 mg) sits squarely within the supported range.

*Is "recurrent" MI supported?* The ATT meta-analysis includes an explicit "previous myocardial infarction" patient category — six prior-MI secondary-prevention trials in the 2009 analysis — in which any subsequent non-fatal MI is by definition recurrent. The proof interprets "recurrent non-fatal MI in patients with prior cardiovascular disease" as non-fatal MI events within the established-disease population the ATT analyzed; this interpretation is documented and does not overstate the source.

## Conclusion

**Verdict: PROVED.** Both sub-claims of the decomposed causal claim hold. SC1 (association) was confirmed by 3 verified quotations from the ATT Collaboration's 2002 *BMJ* and 2009 *Lancet* meta-analyses against a threshold of 2 (A1); SC2 (causation) was confirmed by 2 verified quotations establishing that those meta-analyses pool randomized controlled trials, against a threshold of 2 (A2). All five citations were verified verbatim from live government-hosted pages, so no verdict qualifier applies. No adversarial check broke the proof; the bleeding-harm and modern-era objections concern net benefit and effect magnitude, not the existence or direction of the non-fatal-MI reduction that the named source — the Antithrombotic Trialists' Collaboration meta-analysis — reports.

The verdict is scoped to what the claim asserts: that this specific reduction is found in the ATT meta-analysis. It is not a statement that aspirin is the optimal therapy for every secondary-prevention patient today, nor that its benefits outweigh its bleeding risks in every case — those are separate clinical questions outside the claim.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.34.1 on 2026-05-20.
