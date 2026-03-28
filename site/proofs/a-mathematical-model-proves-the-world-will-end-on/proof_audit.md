# Audit: A mathematical model proves the world will end on a specific day in 2026.

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | The von Foerster et al. (1960) mathematical model (the only known candidate) |
| Property | Constitutes a scientifically credible proof that Earth / human civilization will effectively end on a specific day in 2026 |
| Operator | >= |
| Threshold | 2 |
| Proof direction | disprove |
| Operator note | The claim asserts a mathematical model "proves" world-end on a specific day in 2026. "Proves" is interpreted as: the model provides a scientifically valid, evidence-supported prediction. The only known candidate is von Foerster, Mora & Amiot (1960, Science), predicting population growth would reach a mathematical singularity on Friday, November 13, 2026. Disproof established if ≥2 independent sources confirm Earth's lifespan is billions of years and/or the model's assumptions are falsified. Threshold=2 (not 3) because counter-evidence is overwhelming and authoritative sources are limited. |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_future_earth | Wikipedia Future of Earth: Sun engulfs Earth in ~7.59 billion years |
| B2 | source_ladbible | LADbible: von Foerster model's exponential growth assumption falsified |
| B3 | source_livescience | Live Science: Earth habitable for another 1.75 billion years |
| A1 | *(computed)* | Verified disproof source count vs threshold |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified disproof source count vs threshold | count(verified disproof citations) = 3 | 3 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Wikipedia Future of Earth: Sun engulfs Earth in ~7.59 billion years | Wikipedia: Future of Earth (synthesizing peer-reviewed astrophysics) | https://en.wikipedia.org/wiki/Future_of_Earth | "These effects will counterbalance the impact of mass loss by the Sun, and the Sun will likely engulf Earth in about 7.59 billion years from now." | verified | full_quote | Tier 3 (reference) |
| B2 | LADbible: von Foerster model's exponential growth assumption falsified | LADbible: Chilling mathematical equation predicted world end date (Jan 2026) | https://www.ladbible.com/news/science/when-will-world-end-date-408044-20260109 | "With the exponential growth of the population halted, largely because women are choosing to have fewer children in some of the world's largest countries, a 2026 apocalypse is less likely." | verified | full_quote | Tier 2 (unknown) |
| B3 | Live Science: Earth habitable for another 1.75 billion years | Live Science: How Much Longer Can Earth Support Life? | https://www.livescience.com/39775-how-long-can-earth-support-life.html | "in another 1.75 billion years the planet will travel out of the solar system's habitable zone and into a hot zone that will scorch away its oceans" | verified | full_quote | Tier 3 (major_news) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — Wikipedia: Future of Earth**
- Status: verified
- Method: full_quote
- Coverage: N/A (full match)
- Fetch mode: live

**B2 — LADbible: von Foerster 2026 prediction**
- Status: verified
- Method: full_quote
- Coverage: N/A (full match)
- Fetch mode: live

**B3 — Live Science: Earth habitability**
- Status: verified
- Method: full_quote
- Coverage: N/A (full match)
- Fetch mode: live

*Source: proof.py JSON summary*

---

## Computation Traces

```
days from today until predicted Nov 13 2026 doomsday: (predicted_end_date - today).days = 230
verified disproof sources vs threshold: 3 >= 2 = True
Confirmed disproof sources: 3 / 3
```

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

| Description | Sources Consulted | Sources Verified | Agreement |
|-------------|-------------------|------------------|-----------|
| Three independent sources from different domains: astrophysics (B1, B3) and science journalism on demography (B2). B1 and B3 independently confirm Earth's lifespan in billions of years. B2 confirms the von Foerster model's assumptions were falsified. | 3 | 3 | All sources independently reach the same conclusion via different mechanisms |

**Independence note:** B1 (Wikipedia/astrophysics — stellar evolution models) and B3 (Live Science/habitability research — planetary science models) are independent measurements from different research domains. B2 (LADbible/demography — UN population projections) documents the demographic evidence independently. All three confirm the disproof through non-overlapping mechanisms.

*Source: proof.py JSON summary*

---

## Adversarial Checks (Rule 5)

**Check 1: Was the von Foerster paper peer-reviewed? Could the model still be considered valid?**
- Question: Was the von Foerster 1960 paper peer-reviewed and published in a credible journal? Could the model still be considered scientifically valid?
- Search performed: Searched "von Foerster 1960 Science paper doomsday equation". Confirmed: von Foerster, Mora & Amiot published "Doomsday: Friday, 13 November, A.D. 2026" in *Science* (Vol. 132, pp. 1291-1295, 4 Nov 1960). Paper was explicitly presented as a conditional extrapolation under extreme assumptions (unlimited food, no nuclear war, ever-accelerating growth).
- Finding: Paper is peer-reviewed, but doomsday conclusion was always conditional. By 2026 the core assumption — super-exponential population acceleration — is observably false. UN projects population peaking at 10.3 billion and declining. A model whose assumptions are falsified does not "prove" its conclusion.
- Breaks proof: No

**Check 2: Are there other mathematical models predicting world end in 2026?**
- Question: Are there other mathematical models (besides von Foerster) predicting world end in 2026?
- Search performed: Searched "mathematical model predicts world end 2026 scientific peer reviewed". Found: (1) Messiah Foundation International — fringe religious group, asteroid impact claim, no mathematical model; (2) various numerology-based claims with no scientific basis.
- Finding: Von Foerster (1960) is the only peer-reviewed mathematical model cited in connection with a specific 2026 doomsday date. The claim rises or falls with von Foerster — and that model's assumptions have been falsified.
- Breaks proof: No

**Check 3: Could "world will end" mean civilizational collapse? Would this rescue the claim?**
- Question: Could "world will end" refer only to civilizational collapse rather than physical Earth destruction?
- Search performed: Analyzed whether the von Foerster model's singularity could constitute a validated civilizational collapse mechanism. Considered UN population projections and the model's mechanism.
- Finding: Even the charitable reading fails. The model predicted a mathematical singularity in a population equation — a feature of the equation, not a validated physical mechanism. With population growth slowed and the UN projecting a stable peak, the model's mechanism is not operational. A model whose driving assumption is falsified does not prove any version of world-end.
- Breaks proof: No

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | wikipedia.org | reference | 3 | Established reference source |
| B2 | ladbible.com | unknown | 2 | Unclassified domain — verify source authority manually |
| B3 | livescience.com | major_news | 3 | Major news organization |

**Note on B2 (Tier 2):** LADbible is classified as "unknown" (unclassified domain, Tier 2). However, the disproof does not depend solely on B2. The astrophysics sources B1 and B3 (both Tier 3) independently establish that Earth's lifespan is measured in billions of years — sufficient on their own to meet the threshold of 2 verified sources. B2 provides corroborating evidence that the von Foerster model's demographic assumptions were falsified, but the verdict stands without it.

*Source: proof.py JSON summary*

---

## Extraction Records

For qualitative/consensus proofs, extraction records capture citation verification status per source rather than extracted numeric values.

| Fact ID | Value (Verification Status) | Countable toward threshold? | Quote Snippet (first 80 chars) |
|---------|----------------------------|----------------------------|-------------------------------|
| B1 | verified | Yes | "These effects will counterbalance the impact of mass loss by the Sun, and the Su" |
| B2 | verified | Yes | "With the exponential growth of the population halted, largely because women are " |
| B3 | verified | Yes | "in another 1.75 billion years the planet will travel out of the solar system's h" |

*Source: proof.py JSON summary*

---

## Hardening Checklist

| Rule | Status | Notes |
|------|--------|-------|
| Rule 1: Every empirical value parsed from quote text, not hand-typed | N/A | Qualitative proof — no numeric extraction from quotes |
| Rule 2: Every citation URL fetched and quote checked | PASS | All 3 citations verified as `full_quote` via live fetch |
| Rule 3: System time used for date-dependent logic | PASS | `date.today()` used; system date (2026-03-28) matched proof generation date |
| Rule 4: Claim interpretation explicit with operator rationale | PASS | `CLAIM_FORMAL` with `operator_note` present; threshold and `proof_direction` documented |
| Rule 5: Adversarial checks searched for independent counter-evidence | PASS | 3 adversarial checks covering model credibility, alternative models, and charitable interpretations |
| Rule 6: Cross-checks used independently sourced inputs | PASS | B1 (astrophysics/stellar evolution) and B3 (planetary habitability) are independent research domains; B2 provides independent demographic evidence |
| Rule 7: Constants and formulas imported from computations.py, not hand-coded | PASS | `compare()` and `explain_calc()` from `scripts/computations.py`; no hand-coded constants |
| validate_proof.py result | PASS (14/15, 1 warning) | Warning: missing fallback else branch in verdict assignment — fixed before execution |

*Source: proof.py inline output (execution trace) and author analysis*

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
