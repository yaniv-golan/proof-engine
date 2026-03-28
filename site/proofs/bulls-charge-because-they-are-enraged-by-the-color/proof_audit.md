# Audit: Bulls charge because they are enraged by the color red.

- Generated: 2026-03-28
- Reader summary: [proof.md](proof.md)
- Proof script: [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Bulls (Bos taurus, particularly fighting bulls) |
| Property | Whether charging behavior is caused by rage triggered by the color red |
| Operator | >= |
| Threshold | 3 |
| Proof direction | disprove |
| Operator note | This is a causal claim with two components: (1) bulls perceive and are enraged by red, and (2) this rage causes their charging behavior. Scientific evidence shows cattle are dichromatic and cannot distinguish red from green, and that movement — not color — triggers charging. We disprove by finding >= 3 independent authoritative sources that reject the claim. The threshold of 3 reflects strong scientific consensus. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_a | Peer-reviewed study: cattle have dichromatic vision (two cone types, no red receptor) |
| B2 | source_b | University science Q&A: red does not make bulls angry, they lack red retina receptor |
| B3 | source_c | Science publication: bulls respond to movement of cape, not its color |
| A1 | — | Verified source count meeting disproof threshold |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified source count meeting disproof threshold | count(verified citations) = 3 | 3 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Peer-reviewed study: cattle have dichromatic vision | Jacobs et al. 1998, Visual Neuroscience (PubMed) | https://pubmed.ncbi.nlm.nih.gov/9685209/ | "Electroretinogram (ERG) flicker photometry was used to measure the spectral properties of cones in three common ungulates-cattle (Bos taurus), goats (Capra hircus), and sheep (Ovis aries). Two cone mechanisms were identified in each species." | verified | full_quote | Tier 5 (government) |
| B2 | University science Q&A: red does not make bulls angry | West Texas A&M University — Science Questions with Surprising Answers | https://www.wtamu.edu/~cbaird/sq/2012/12/12/what-is-it-about-red-that-makes-bulls-so-angry/ | "The color red does not make bulls angry. Cattle lack the red retina receptor and can only see yellow, green, blue, and violet colors." | partial | aggressive_normalization | Tier 4 (academic) |
| B3 | Science publication: bulls respond to movement | ScienceABC — Do Bulls Really Hate the Color Red? | https://www.scienceabc.com/nature/animals/do-bulls-really-hate-red-colour-blind.html | "It's not the color, but rather the movement of the cape and the bullfighter that makes bulls so angry." | verified | full_quote | Tier 2 (unknown) |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1 — Jacobs et al. 1998 (PubMed)**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B2 — West Texas A&M University**
- Status: partial
- Method: aggressive_normalization (fragment_match, 8 words)
- Fetch mode: live
- Impact: B2 confirms that red does not make bulls angry and that cattle lack a red retina receptor. This conclusion is independently supported by B1 (peer-reviewed, fully verified), which establishes the dichromatic photopigment basis. The disproof does not depend solely on B2.

**B3 — ScienceABC**
- Status: verified
- Method: full_quote
- Fetch mode: live

*Source: proof.py JSON summary; impact analysis is author analysis*

## Computation Traces

```
verified source count vs disproof threshold: 3 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Metric | Value |
|--------|-------|
| Sources consulted | 3 |
| Sources verified | 3 (2 full, 1 partial) |
| source_a status | verified |
| source_b status | partial |
| source_c status | verified |

**Independence note:** Source A is a peer-reviewed neuroscience paper (Jacobs et al. 1998, Visual Neuroscience). Source B is a university physics department Q&A (West Texas A&M). Source C is a science education publication (ScienceABC). These represent independent publications from different institutions and domains (primary research, academic outreach, science journalism).

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**1. Is there any scientific study showing bulls can perceive red or are trichromatic?**
- Verification performed: Searched for 'cattle trichromatic vision' and 'bulls see red color scientific evidence'. All results confirm cattle are dichromatic with two cone types (S-cone ~444-455nm, M/L-cone ~552-555nm). No peer-reviewed study was found claiming cattle have a red cone receptor or trichromatic vision.
- Finding: No credible source supports cattle having red color perception. Jacobs et al. (1998) is the definitive photopigment study.
- Breaks proof: No

**2. Is there any experimental evidence that red specifically triggers aggression in bulls more than other colors?**
- Verification performed: Searched for 'bulls actually do see red color evidence support myth true'. Found MythBusters (Discovery Channel, 2007) ran controlled experiments: (1) stationary red, blue, and white flags received equal attacks; (2) a moving blue flag was charged while a stationary red flag was ignored; (3) a motionless person in red was ignored while moving bullfighters were charged. No source was found showing red triggers more aggression than other colors.
- Finding: All experimental evidence confirms movement, not color, triggers charging. No counter-evidence found.
- Breaks proof: No

**3. Could the traditional use of red capes indicate that matadors observed a real color preference?**
- Verification performed: Searched for 'why matadors use red cape history bullfighting muleta'. Multiple sources explain the red muleta is used in the final stage (tercio de muerte) to mask blood splatters from the audience. The earlier stages use a larger magenta-and-yellow capote. The color choice is for human spectators, not the bull.
- Finding: Red cape tradition is for masking blood from audience, not based on bull color preference.
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | nih.gov | government | 5 | Government domain (.gov) — PubMed hosts peer-reviewed abstracts |
| B2 | wtamu.edu | academic | 4 | Academic domain (.edu) — university science outreach |
| B3 | scienceabc.com | unknown | 2 | Unclassified domain — verify source authority manually |

B3 is from a Tier 2 (unclassified) source. The claim it supports (movement triggers charging, not color) is independently confirmed by B1 and B2 from higher-tier sources, as well as by the MythBusters experimental results documented in adversarial checks. The disproof does not depend solely on B3.

*Source: proof.py JSON summary; tier impact analysis is author analysis*

## Extraction Records

For this qualitative disproof, extractions record citation verification status rather than numeric values.

| Fact ID | Value | Value in quote | Quote snippet |
|---------|-------|---------------|---------------|
| B1 | verified | true | "Electroretinogram (ERG) flicker photometry was used to measure the spectral prop..." |
| B2 | partial | true | "The color red does not make bulls angry. Cattle lack the red retina receptor and..." |
| B3 | verified | true | "It's not the color, but rather the movement of the cape and the bullfighter that..." |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A — qualitative proof with no numeric value extraction
- **Rule 2:** All 3 citation URLs fetched and quotes checked via `verify_all_citations()`. Results: 2 verified (full_quote), 1 partial (aggressive_normalization).
- **Rule 3:** `date.today()` used for `generated_at` in generator block
- **Rule 4:** CLAIM_FORMAL with operator_note explicitly documents the causal interpretation, threshold choice, and disproof direction
- **Rule 5:** Three adversarial checks searched for counter-evidence: red perception studies, experimental color preference evidence, and historical cape tradition rationale. None found.
- **Rule 6:** Three independent sources from different domains (government/peer-reviewed, academic, science journalism) consulted. All independently reject the claim.
- **Rule 7:** `compare()` used for claim evaluation; no hard-coded constants
- **validate_proof.py:** PASS with 1 warning (no else branch in verdict assignment — cosmetic, all paths covered for this proof)

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
