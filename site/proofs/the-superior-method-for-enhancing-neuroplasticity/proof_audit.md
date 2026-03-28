# Audit: The superior method for enhancing neuroplasticity in adults is neurofeedback training compared to exercise or sleep optimization.

- **Generated:** 2026-03-27
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Neurofeedback training |
| Property | Scientific evidence quality for neuroplasticity enhancement in adults, compared to aerobic exercise and sleep optimization |
| Operator | >= |
| Operator note | The claim asserts neurofeedback is THE SUPERIOR method — meaning it outperforms BOTH exercise AND sleep optimization for neuroplasticity. Disproof requires showing at least one of those alternatives has stronger or more reliably demonstrated neuroplasticity effects than neurofeedback. 'Superior' is interpreted as having larger effect sizes, better replication, and clearer mechanistic evidence across independent meta-analyses and systematic reviews. Neuroplasticity is operationalized as changes in BDNF levels, hippocampal volume, gray matter density, or functional neural modulation. |
| Threshold | 3 (minimum confirming sources) |
| Proof direction | disprove |

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_a | Szuhany et al. 2014 meta-analysis — exercise and BDNF effect sizes (J Psychiatric Research) |
| B2 | source_b | Cardoso et al. 2024 systematic review — aerobic exercise and neuroplasticity (Int J Exercise Science) |
| B3 | source_c | Marzbani et al. 2016 comprehensive review — neurofeedback efficacy limitations (Basic Clin Neurosci) |
| B4 | source_d | Orndorff-Plunkett et al. 2017 — neurofeedback versus sham controls (Brain Sciences) |
| A1 | (computed) | Count of independent sources rejecting neurofeedback-as-superior claim |

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Count of independent sources rejecting neurofeedback-as-superior claim | sum(confirmations) = 4 | 4 |

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Exercise BDNF effect size meta-analysis | Szuhany et al. 2014, Journal of Psychiatric Research (PMC4314337) | https://pmc.ncbi.nlm.nih.gov/articles/PMC4314337/ | "Results demonstrated a moderate effect size for increases in BDNF following a single session of exercise" | verified | full_quote | Tier 5 (government) |
| B2 | Aerobic exercise neuroplasticity systematic review | Cardoso et al. 2024, Int J Exercise Science (PMC11385284) | https://pmc.ncbi.nlm.nih.gov/articles/PMC11385284/ | "moderate to high intensity aerobic exercise (AE), increases the level of peripheral BDNF" | verified | full_quote | Tier 5 (government) |
| B3 | Neurofeedback efficacy review | Marzbani et al. 2016, Basic and Clinical Neuroscience (PMC4892319) | https://pmc.ncbi.nlm.nih.gov/articles/PMC4892319/ | "current research does not support conclusive results about its efficacy" | verified | full_quote | Tier 5 (government) |
| B4 | Neurofeedback vs. sham review | Orndorff-Plunkett et al. 2017, Brain Sciences (PMC5575615) | https://pmc.ncbi.nlm.nih.gov/articles/PMC5575615/ | "recent accumulating evidence seems to refute the clinical superiority of feedback training over sham treatment" | verified | full_quote | Tier 5 (government) |

---

## Citation Verification Details

**B1 — Szuhany et al. 2014**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Impact: N/A (verified)

**B2 — Cardoso et al. 2024**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Impact: N/A (verified)

**B3 — Marzbani et al. 2016**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Impact: N/A (verified)

**B4 — Orndorff-Plunkett et al. 2017**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Impact: N/A (verified)

---

## Computation Traces

```
[✓] source_a: Full quote verified for source_a (source: tier 5/government)
[✓] source_b: Full quote verified for source_b (source: tier 5/government)
[✓] source_c: Full quote verified for source_c (source: tier 5/government)
[✓] source_d: Full quote verified for source_d (source: tier 5/government)
[✓] B1: extracted effect size from quote
[✓] B2: extracted BDNF from quote
[✓] B3: extracted not support from quote
[✓] B4: extracted refute from quote
SC1: sources confirming rejection of neurofeedback-as-superior claim: 4 >= 3 = True
```

---

## Independent Source Agreement (Rule 6)

| Description | N Sources | N Confirming | Agreement |
|-------------|-----------|--------------|-----------|
| Independent source agreement: exercise superiority confirmed by B1+B2; neurofeedback insufficiency confirmed by B3+B4 | 4 | 4 | Yes |

**Note:** B1 (Szuhany 2014) and B2 (Cardoso 2024) are independent research groups using independent datasets — different authors, different participant pools, different measurement timepoints. B3 (Marzbani 2016) and B4 (Orndorff-Plunkett 2017) are independent review articles from different author groups reviewing overlapping but not identical literature. All four converge on the same conclusion.

---

## Adversarial Checks (Rule 5)

**Check 1**
- Question: Is there any meta-analysis or systematic review showing neurofeedback produces neuroplasticity effects (BDNF increase, hippocampal volume, gray matter change) larger than aerobic exercise in healthy adults?
- Verification performed: Searched PubMed, Google Scholar, and PMC for: "neurofeedback neuroplasticity BDNF meta-analysis", "neurofeedback hippocampal volume", "neurofeedback superior exercise neuroplasticity". Also reviewed Galang et al. 2025 (PMC12426165) — the largest recent neurofeedback meta-analysis (SMD=0.32 for neural modulation, functional only, not structural neuroplasticity).
- Finding: No meta-analysis or systematic review was found claiming neurofeedback produces neuroplasticity effects exceeding those of aerobic exercise. The best pro-neurofeedback finding (Galang et al. 2025, SMD=0.32) measures functional neural modulation during sessions only — not structural neuroplasticity (BDNF, hippocampal volume, gray matter). Exercise meta-analyses report Hedges' g = 0.46–0.58 for BDNF and documented hippocampal volume changes in RCTs. Neurofeedback's structural neuroplasticity evidence is absent.
- Breaks proof: No

**Check 2**
- Question: Could "neuroplasticity" in the claim refer only to EEG-measured functional plasticity (alpha/theta brainwave modulation), where neurofeedback might excel?
- Verification performed: Reviewed neuroscience literature definitions of neuroplasticity. Searched for "neuroplasticity definition EEG neurofeedback" and "neuroplasticity BDNF hippocampus gold standard". Reviewed Galang et al. 2025 functional vs. structural distinction.
- Finding: Standard neuroscience definitions of neuroplasticity encompass structural and functional changes: synaptic density, gray matter volume, hippocampal neurogenesis, BDNF-mediated changes. A narrow redefinition limited to EEG brainwave modulation would exclude the primary measures used in the neuroplasticity enhancement literature and is not the standard scientific meaning. Even under this generous interpretation, neurofeedback's functional modulation effects (SMD=0.32) are contested and not established above sham; does not break proof.
- Breaks proof: No

**Check 3**
- Question: Is there any RCT showing neurofeedback produces superior neuroplasticity outcomes compared to an active exercise control?
- Verification performed: Searched PubMed for "neurofeedback exercise RCT neuroplasticity comparison", "neurofeedback versus aerobic exercise brain". Checked Thibault et al. 2017 (Brain, Oxford) commentary on sham-controlled trials.
- Finding: No RCT comparing neurofeedback head-to-head against exercise for neuroplasticity was found. Thibault et al. 2017 notes that as of 2017, very few randomized double-blind sham-controlled neurofeedback trials exist, and those that do show genuine and sham neurofeedback produce comparable improvements, suggesting placebo plays a central role. The absence of head-to-head evidence means the claim of neurofeedback's superiority cannot be supported; does not break disproof.
- Breaks proof: No

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | nih.gov | government | 5 | NIH PubMed Central — peer-reviewed article repository |
| B2 | nih.gov | government | 5 | NIH PubMed Central — peer-reviewed article repository |
| B3 | nih.gov | government | 5 | NIH PubMed Central — peer-reviewed article repository |
| B4 | nih.gov | government | 5 | NIH PubMed Central — peer-reviewed article repository |

All sources are Tier 5 (government domain, NIH PubMed Central), hosting peer-reviewed journal articles. No low-credibility sources were used.

---

## Extraction Records

| Fact ID | Keyword | Found in Quote | Quote Snippet |
|---------|---------|----------------|---------------|
| B1 | "effect size" | Yes | "Results demonstrated a moderate effect size for increases in BDNF following a si..." |
| B2 | "BDNF" | Yes | "moderate to high intensity aerobic exercise (AE), increases the level of periphe..." |
| B3 | "not support" | Yes | "current research does not support conclusive results about its efficacy" |
| B4 | "refute" | Yes | "recent accumulating evidence seems to refute the clinical superiority of feedbac..." |

**Extraction method:** `verify_extraction()` from `scripts/smart_extract.py` — performs case-insensitive substring match with Unicode normalization. Each keyword confirms the source's position relative to the claim (exercise produces quantified neuroplasticity effects; neurofeedback lacks sufficient/superior evidence).

**Author analysis:** For the disproof direction, keywords were chosen to confirm each source's rejection stance: B1/B2 keywords confirm documented exercise neuroplasticity effects (refuting neurofeedback's exclusivity); B3/B4 keywords confirm the source directly states neurofeedback evidence is insufficient or refuted.

---

## Hardening Checklist

- **Rule 1:** Every empirical value parsed from quote text via `verify_extraction()` — no hand-typed values
- **Rule 2:** Every citation URL fetched live; all 4 quotes verified full_quote against live page text
- **Rule 3:** No date-dependent logic (this is a literature consensus proof, not a time-dependent claim)
- **Rule 4:** `CLAIM_FORMAL` with `operator_note` explicitly documents the interpretation of "superior" and the disproof threshold
- **Rule 5:** Three adversarial checks performed searching for counter-evidence (pro-neurofeedback meta-analyses, narrow definitions, head-to-head RCTs) — none found to break the disproof
- **Rule 6:** Four independent sources from two independent research pairs (B1/B2 for exercise; B3/B4 for neurofeedback); all agree
- **Rule 7:** No hard-coded constants or formulas; `compare()` from `scripts/computations.py` used for claim evaluation
