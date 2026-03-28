# Audit: The claim that Israel maintains an illegal occupation of the entire West Bank is contradicted by the Oslo Accords designating Area C as remaining under full Israeli civil and security administration pending final-status negotiations.

- **Generated:** 2026-03-27
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

*Source: proof.py JSON summary*

| Field | Value |
|-------|-------|
| Subject | Oslo Accords / Area C designation |
| Compound operator | AND (all sub-claims must hold) |
| SC1 property | Oslo II (1995) designates Area C under full Israeli civil and security administration pending final-status negotiations |
| SC1 operator | >= 2 sources confirming |
| SC1 operator note | Factual claim about treaty content; non-controversial |
| SC2a property | Oslo shows the West Bank is NOT entirely under Israeli civil control (Areas A and B have Palestinian civil administration) |
| SC2a operator | >= 2 sources confirming |
| SC2a operator note | Non-controversial; established by the treaty text |
| SC2b property | The Oslo designation contradicts the "illegal" characterization under international law |
| SC2b operator | >= 2 sources confirming |
| SC2b operator note | FAILS: ICJ 2024 Advisory Opinion explicitly found occupation unlawful and stated Oslo cannot detract from Israel's international law obligations. Fourth Geneva Convention Art. 47 bars bilateral agreements from derogating IHL protections. |
| Overall operator note | SC1 and SC2a hold; SC2b fails → PARTIALLY VERIFIED |

---

## Fact Registry

*Source: proof.py JSON summary*

| ID | Key | Label |
|----|-----|-------|
| B1 | wiki_oslo_ii_areas | Wikipedia: Oslo II Accord — Area C "full Israeli civil and security control" |
| B2 | area_c_wiki | Wikipedia: Area C — Oslo II definition "gradually transferred to Palestinian jurisdiction" |
| B3 | wiki_area_a | Wikipedia: Oslo II Accord — Area A "full civil and security control by the Palestinian Authority" |
| B4 | wiki_area_b | Wikipedia: Oslo II Accord — Area B "Palestinian civil control and joint Israeli-Palestinian security control" |
| A1 | (computed) | SC1 confirmed: n_sources_sc1 >= 2 |
| A2 | (computed) | SC2a confirmed: n_sources_sc2a >= 2 |
| A3 | (computed) | SC2b fails: ICJ 2024 finds occupation unlawful regardless of Oslo |

---

## Full Evidence Table

### Type A (Computed) Facts

*Source: proof.py JSON summary*

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | SC1 confirmed | sum(sc1_confirmations) = 2 | 2 / 2 sources confirm SC1 (Area C under Israeli control) |
| A2 | SC2a confirmed | sum(sc2a_confirmations) = 2 | 2 / 2 sources confirm SC2a (Areas A, B under Palestinian civil control) |
| A3 | SC2b fails | adversarial_check: ICJ 2024 Advisory Opinion | SC2b fails: ICJ found occupation unlawful; Oslo cannot detract from international law obligations |

### Type B (Empirical) Facts

*Source: proof.py JSON summary*

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Area C under Israeli control | Wikipedia: West Bank areas in Oslo II Accord | https://en.wikipedia.org/wiki/West_Bank_areas_in_the_Oslo_II_Accord | "Area C (full Israeli civil and security control): initially, circa 72–74% (first phase, 1995)" | verified | full_quote | Tier 3 (reference) |
| B2 | Area C Oslo II definition | Wikipedia: Area C (West Bank) | https://en.wikipedia.org/wiki/Area_C_(West_Bank) | "areas of the West Bank outside Areas A and B, which, except for the issues that will be negotiated in the permanent status negotiations, will be gradually transferred to Palestinian jurisdiction in accordance with this Agreement" | verified | full_quote | Tier 3 (reference) |
| B3 | Area A under Palestinian control | Wikipedia: West Bank areas in Oslo II Accord | https://en.wikipedia.org/wiki/West_Bank_areas_in_the_Oslo_II_Accord | "full civil and security control by the Palestinian Authority" | verified | full_quote | Tier 3 (reference) |
| B4 | Area B under Palestinian civil control | Wikipedia: West Bank areas in Oslo II Accord | https://en.wikipedia.org/wiki/West_Bank_areas_in_the_Oslo_II_Accord | "Palestinian civil control and joint Israeli-Palestinian security control" | verified | full_quote | Tier 3 (reference) |

---

## Citation Verification Details

*Source: proof.py JSON summary*

**B1 — wiki_oslo_ii_areas**
- Status: verified
- Method: full_quote
- Fetch mode: live
- Note: Initial quote used en-dash and tilde ("~72–74%"); page text uses "circa 72–74%". Quote was corrected to match page text before verification passed.

**B2 — area_c_wiki**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B3 — wiki_area_a**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4 — wiki_area_b**
- Status: verified
- Method: full_quote
- Fetch mode: live

---

## Computation Traces

*Source: proof.py inline output (execution trace)*

```
[✓] wiki_oslo_ii_areas: Full quote verified (source: tier 3/reference)
[✓] area_c_wiki: Full quote verified (source: tier 3/reference)
[✓] wiki_area_a: Full quote verified (source: tier 3/reference)
[✓] wiki_area_b: Full quote verified (source: tier 3/reference)
[✓] B1: extracted "Israeli civil and security control" from quote
[✓] B2: extracted "permanent status negotiations" from quote
[✓] B3: extracted "Palestinian Authority" from quote
[✓] B4: extracted "Palestinian civil control" from quote
compare: 2 >= 2 = True    [SC1 holds]
compare: 2 >= 2 = True    [SC2a holds]
compare: 0 >= 2 = False   [SC2b fails]
compare: 2 == 3 = False   [compound claim does not fully hold]
```

Note: No numeric computation traces — this is a qualitative/source-counting proof. `compare()` calls serve as the primary computational audit.

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

*Source: proof.py JSON summary*

| Cross-check | Sources | Confirming | Agreement |
|-------------|---------|------------|-----------|
| SC1: Area C under Israeli control | 2 | 2 | Yes |
| SC2a: Areas A, B under Palestinian civil control | 2 | 2 | Yes |
| SC2b: Oslo contradicts "illegal" characterization | 1 (adversarial) | 0 | No — ICJ 2024 directly contradicts |

**Independence note:** B1 and B3/B4 are drawn from the same Wikipedia article (two different sections confirming different sub-claims). B2 is from the Area C Wikipedia article (independent page). For a higher-assurance proof, primary treaty text (via UN UNISPAL) and the actual ICJ opinion PDF would be preferred. The Wikipedia sources are authoritative summaries of non-controversial, well-documented treaty content — the Oslo II zone designations are not disputed facts.

*Source: proof.py JSON summary*

---

## Adversarial Checks (Rule 5)

*Source: proof.py JSON summary*

**Check 1:** Does the Oslo II Accord's designation of Area C contradict international legal characterizations of the occupation as illegal?
- Performed: Fetched ICJ Advisory Opinion summary (icj-cij.org/node/204176, July 19 2024). Searched for legal scholarship on Oslo Accords and occupation law. Reviewed Opinio Juris (2020), Indiana University Law Review, Max Planck Institute analysis.
- Finding: The ICJ 2024 Advisory Opinion found: (1) Israel's continued presence in the Occupied Palestinian Territory is unlawful; (2) the Oslo Accords do not permit Israel to annex OPT or maintain a permanent presence; (3) such agreements cannot detract from Israel's international law obligations. Fourth Geneva Convention Article 47 bars bilateral derogation of IHL. SC2b fails.
- Breaks proof: No (affects only SC2b, which was already categorized as failing)

**Check 2:** Does Israel's consent argument (Palestinians agreed via Oslo, so no occupation) have legal merit?
- Performed: Searched "Israel Oslo Accords estoppel no occupation argument international law." Reviewed JCFA article on Palestinian compliance with Oslo Accords. Reviewed Opinio Juris analysis.
- Finding: Israel's consent/estoppel argument is a minority legal position rejected by the ICJ (2004 and 2024) and mainstream IHL scholarship. Art. 47 GC IV was drafted to prevent exactly this kind of waiver-by-agreement.
- Breaks proof: No

**Check 3:** Does "entire West Bank" terminology accurately describe the occupation claim?
- Performed: Searched for UN, PA, and scholarly usage of "entire West Bank occupation." Reviewed Al Jazeera, Anera, UN sources on Areas A, B, C.
- Finding: Critics use "Occupied Palestinian Territory" (not "entire West Bank under Israeli civil control"). The "entire" qualifier is somewhat of a straw man — SC2a holds for the letter of the claim but critics' actual position is more nuanced (effective control via borders/movement even in Areas A/B).
- Breaks proof: No

**Check 4:** Can the Area C designation legitimize Israeli control, undermining the "illegal" label?
- Performed: Reviewed Oslo as lex specialis vs. lex generalis. Fetched Opinio Juris (2020). Searched for academic articles on Oslo II and Fourth Geneva Convention.
- Finding: Oslo is not lex specialis overriding GC IV. Bilateral consent cannot waive occupation law. PLO agreement to interim arrangements does not transform the legal character of the occupation. SC2b fails.
- Breaks proof: No

*Source: proof.py JSON summary*

---

## Source Credibility Assessment

*Source: proof.py JSON summary*

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | wikipedia.org | reference | 3 | Established reference source |
| B2 | wikipedia.org | reference | 3 | Established reference source |
| B3 | wikipedia.org | reference | 3 | Established reference source |
| B4 | wikipedia.org | reference | 3 | Established reference source |

**Note:** All four citations are Tier 3 (Wikipedia). For claims about non-controversial treaty content (the Oslo II zone designations are matters of public record), this is adequate. For the SC2b legal analysis, the ICJ Advisory Opinion (Tier 5 — intergovernmental) was consulted as an adversarial source but not cited as an empirical fact (per template: adversarial sources go in `adversarial_checks`, not `empirical_facts`). A production-grade proof should cite the ICJ opinion and the Oslo II treaty text directly from UN UNISPAL as Tier 5 sources.

*Source: proof.py JSON summary*

---

## Extraction Records

*Source: proof.py JSON summary + author analysis*

| Fact ID | Extracted Value | Found in Quote | Quote Snippet |
|---------|----------------|----------------|---------------|
| B1 | "Israeli civil and security control" confirmed | Yes | "Area C (full Israeli civil and security control): initially, circa 72–74% (first phase" |
| B2 | "permanent status negotiations" confirmed | Yes | "areas of the West Bank outside Areas A and B, which, except for the issues that " |
| B3 | "Palestinian Authority" confirmed | Yes | "full civil and security control by the Palestinian Authority" |
| B4 | "Palestinian civil control" confirmed | Yes | "Palestinian civil control and joint Israeli-Palestinian security control" |

**Extraction method:** `verify_extraction()` from `scripts/smart_extract.py` — performs Unicode normalization and case-insensitive substring matching. All four keywords were found in their respective quotes on first pass.

**Normalization note (B1):** The initial quote used `~72–74%` (tilde + en-dash). The live page text uses `circa 72–74%`. Quote was corrected to match the live page text before verification. Unicode en-dash (U+2013) was preserved correctly.

*Source: proof.py JSON summary + author analysis*

---

## Hardening Checklist

| Rule | Check | Status |
|------|-------|--------|
| Rule 1 | Every empirical value parsed from quote text, not hand-typed | PASS — `verify_extraction()` used for all keyword checks |
| Rule 2 | Every citation URL fetched and quote checked | PASS — `verify_all_citations()` called; all 4 citations verified live |
| Rule 3 | System time used for date-dependent logic | N/A — no date-dependent computations in this proof |
| Rule 4 | Claim interpretation explicit with operator rationale | PASS — compound `CLAIM_FORMAL` with `operator_note` on each sub-claim |
| Rule 5 | Adversarial checks searched for independent counter-evidence | PASS — 4 adversarial checks covering ICJ opinion, consent argument, terminology, lex specialis |
| Rule 6 | Cross-checks used independently sourced inputs | PASS — B2 (Area C Wiki) independent of B1 (Oslo II areas Wiki); B3/B4 from same article, different sections |
| Rule 7 | Constants and formulas imported from computations.py, not hand-coded | PASS — `compare()` used for all evaluations; no hand-coded constants |
| validate_proof.py | Static analysis result | PASS — 17/17 checks passed, 0 issues, 0 warnings |
