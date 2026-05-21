# Audit: The paper "Goh AC, Gill IS. Wallace anastomosis in complex dissections. Eur Urol Focus. (2024) 11:80–8" does not exist.

**Generated:** 2026-05-21
**Reader summary:** [proof.md](proof.md)
**Proof script:** [proof.py](proof.py)

## Claim Interpretation

The natural-language claim is: *"The paper 'Goh AC, Gill IS. Wallace anastomosis in complex dissections. Eur Urol Focus. (2024) 11:80–8' does not exist."*

The subject is a single journal article, fully specified by a citation containing a title ("Wallace anastomosis in complex dissections"), two authors (A.C. Goh and I.S. Gill), a journal (*European Urology Focus*, abbreviated "Eur Urol Focus"), a publication year (2024), a volume (11), and a page range (80–88, written "80–8").

This is an absence-of-evidence proof. Non-existence cannot be established with deductive certainty — no finite search can logically exclude an unindexed record — so the claim is operationalised as: *no published journal article matching the disputed citation can be located in any major scholarly index or in the journal's own catalogue.* The operator is `>=`: the number of independent scholarly indexes returning zero matching records must reach or exceed a threshold of 3.

**Formalization scope.** The formalization narrows "does not exist" to "is not discoverable in the major scholarly indexing infrastructure (PubMed, Europe PMC, OpenAlex, Crossref) or in the publisher's DOI registry." This is a faithful operationalization for a 2024/2025 article in an Elsevier journal — every such article is registered with Crossref and indexed by these services — but it is a proxy, not a logical equivalence. The verdict ceiling is therefore SUPPORTED, not PROVED. "result_count" is defined as the number of indexed records that *match* the cited article; relevance-ranked databases return unrelated near-match candidates even for non-existent titles, and those candidates are not matches. result_count values are author-reported and reproducible via the search_url links, but the tool verifies only that each search URL is reachable, not the count itself.

*Source: proof.py JSON summary (`claim_natural`, `claim_formal`)*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | The journal article cited as "Goh AC, Gill IS. Wallace anastomosis in complex dissections. Eur Urol Focus. (2024) 11:80–8" |
| Property | Absence of any indexed record of a published article matching this citation |
| Operator | `>=` (unique accessible databases with null results vs. threshold) |
| Search threshold | 3 |
| Corroboration threshold | 0 (corroborating citation sources optional) |
| Proof direction | absence |

*Source: proof.py JSON summary (`claim_formal`)*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| S1 | pubmed_title | PubMed: exact-title phrase search |
| S2 | pubmed_author | PubMed: Goh AC as author in European Urology Focus |
| S3 | europepmc_title | Europe PMC: exact-title field search |
| S4 | europepmc_author | Europe PMC: Goh AC as author in European Urology Focus |
| S5 | openalex | OpenAlex: title search |
| S6 | crossref | Crossref: exact-title match among indexed works |
| A1 | — | Unique accessible databases with null results |

*Source: proof.py JSON summary (`evidence`)*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Unique accessible databases with null results | Count of unique accessible database domains with result_count == 0 | 4 |

### Type B (Empirical) Facts

None. This proof contains no Type B citation facts. Non-existence is established by the Type S search facts below; the two corroboration lines (the volume/year contradiction and the fabricated-DOI pattern) are documented and verified in the Adversarial Checks section rather than as citation-verified facts.

### Type S (Search) Facts

| ID | Database | Search URL | Query Terms | Date Range | Result Count | Status | Credibility |
|----|----------|-----------|-------------|-----------|--------------|--------|-------------|
| S1 | PubMed | https://pubmed.ncbi.nlm.nih.gov/?term=%22Wallace+anastomosis+in+complex+dissections%22 | "Wallace anastomosis in complex dissections" (exact title phrase) | All years indexed; searched 2026-05-21 | 0 | accessible | Government |
| S2 | PubMed | https://pubmed.ncbi.nlm.nih.gov/?term=Goh+AC%5BAuthor%5D+AND+%22European+Urology+Focus%22%5BJournal%5D | Goh AC[Author] AND "European Urology Focus"[Journal] | All years indexed; searched 2026-05-21 | 0 | accessible | Government |
| S3 | Europe PMC | https://europepmc.org/search?query=TITLE%3A%22Wallace%20anastomosis%20in%20complex%20dissections%22 | TITLE:"Wallace anastomosis in complex dissections" | All years indexed; searched 2026-05-21 | 0 | accessible | Unclassified |
| S4 | Europe PMC | https://europepmc.org/search?query=AUTH%3A%22Goh%20AC%22%20AND%20JOURNAL%3A%22European%20Urology%20Focus%22 | AUTH:"Goh AC" AND JOURNAL:"European Urology Focus" | All years indexed; searched 2026-05-21 | 0 | accessible | Unclassified |
| S5 | OpenAlex | https://api.openalex.org/works?filter=title.search:Wallace%20anastomosis%20in%20complex%20dissections | title.search:Wallace anastomosis in complex dissections | All years indexed (~250M works); searched 2026-05-21 | 0 | accessible | Unclassified |
| S6 | Crossref | https://api.crossref.org/works?query.title=Wallace+anastomosis+in+complex+dissections&rows=20 | query.title=Wallace anastomosis in complex dissections (exact-title matches among registered works) | All years of Crossref registrations; searched 2026-05-21 | 0 | accessible | Academic |

*Source: proof.py JSON summary (`evidence`, S-type) cross-referenced with `search_registry`*

## Citation Verification Details

No Type B citations are present in this proof, so there are no `verify_all_citations()` results to report. Citation verification (Rule 2) is satisfied here by `verify_search_registry()`, which confirmed that all six search URLs are reachable (HTTP 200, status "accessible"). The corroborating findings — the volume/year contradiction and the resolved sibling DOIs — were verified directly against the Crossref API and are documented verbatim in the Adversarial Checks section; they are recorded as prose adversarial evidence, not as machine-verified citations.

## Computation Traces

```
  null accessible databases vs threshold: 4 >= 3 = True
  corroborating sources vs threshold: 0 >= 0 = True
  both thresholds met: 1 >= 1 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

The proof relies on four independent scholarly indexes, deduplicated by URL domain: `pubmed.ncbi.nlm.nih.gov`, `europepmc.org`, `openalex.org` and `www.crossref.org`. Six searches were issued across these four domains; all six returned zero matching records and all six search URLs were accessible. After domain deduplication, 4 unique databases returned null results — exceeding the threshold of 3.

These indexes have independent ingestion pipelines: PubMed is curated by the NIH National Library of Medicine; Europe PMC is operated by EMBL-EBI and aggregates PubMed, PubMed Central, preprint servers, Agricola and patents; OpenAlex is built by the non-profit OurResearch from Crossref, PubMed and other feeds; Crossref is the DOI registration agency through which Elsevier (the publisher of *European Urology Focus*) registers every article. A genuine 2024 or 2025 article in this journal would necessarily appear in Crossref (via DOI registration) and, in the normal course, in PubMed and the aggregators. Agreement across all four is therefore meaningful rather than circular.

**Conflict-of-interest assessment.** No conflict of interest applies. The four indexes are general-purpose bibliographic infrastructure with no organizational, funding, competitive, or advocacy relationship to the disputed citation, its named authors, or the journal. `coi_flags`: none.

*Source: proof.py JSON summary (`cross_checks`); COI assessment is author analysis*

## Adversarial Checks (Rule 5)

Ten adversarial checks were performed. None broke the proof (`breaks_proof: false` for all).

1. **PubMed reproducibility** — Queried the PubMed E-utilities API and public search page on 2026-05-21. `esearch` for the exact title returned count=0; `esearch` for `Goh AC[Author] AND "European Urology Focus"[Journal]` returned count=0 ("No items found"). Finding: PubMed accessible; both queries return 0 records.
2. **Europe PMC reproducibility** — Queried the Europe PMC REST API on 2026-05-21. `TITLE:"Wallace anastomosis in complex dissections"` returned hitCount=0; `AUTH:"Goh AC" AND JOURNAL:"European Urology Focus"` returned hitCount=0. Finding: Europe PMC accessible; both queries return 0 across an exceptionally broad corpus.
3. **OpenAlex reproducibility** — Queried the OpenAlex API on 2026-05-21. `filter=title.search:...` returned meta.count=0 across ~250M works. Finding: OpenAlex accessible; 0 works match.
4. **Crossref reproducibility** — Queried the Crossref REST API on 2026-05-21. A title query and a journal-scoped scan of *European Urology Focus* (ISSN 2405-4569) found 0 works with the exact title and none so titled by A.C. Goh; the disputed citation has no DOI. Finding: Crossref accessible; 0 records match.
5. **Fuzzy-candidate review** — Reviewed the relevance-ranked candidates returned by the Crossref and OpenAlex fuzzy queries and by web/Scholar search. Finding: every candidate is a different, real publication on ureteroileal anastomosis (e.g. "Wallace method of ureteroileal anastomosis", *Urology* 1975); none is the disputed title and none is by Goh and Gill. Ranked near-matches for a non-existent title are not counter-evidence.
6. **Any-evidence check** — Searched for every occurrence of the exact title string. Finding: it occurs once, in the reference list of *Frontiers in Oncology* 2025 (DOI 10.3389/fonc.2025.1613772), as an entry with no DOI. A reference-list entry asserts a paper exists; it is not the paper and is the artefact the claim concerns. No indexed article, DOI, or catalogue entry corresponds to it. This confirms the citation has no referent rather than breaking the proof.
7. **Fabrication-pattern check** — Examined sibling references in that same reference list and resolved their DOIs via Crossref. Finding: 10.1007/s00423-021-02413-4 resolves to a 2021 *Langenbeck's Archives of Surgery* paper (cited as "<!-- not-a-citation-start -->Urol Oncol (2024)<!-- not-a-citation-end --> 42:15–24"); 10.1111/bju.12121 resolves to a 2013 *BJU International* paper (cited as "J <!-- not-a-citation-start -->Urol (2024)<!-- not-a-citation-end --> 211:45–55"); 10.1016/j.ucl.2005.02.001 resolves to a 2005 *Urologic Clinics of North America* paper (cited as "<!-- not-a-citation-start -->Eur Urol Focus (2024)<!-- not-a-citation-end --> 10:50–8"). The disputed reference has no DOI. This pattern is consistent with AI-hallucinated citations and corroborates non-existence.
8. **Volume/year consistency check** — Cross-referenced *European Urology Focus* volume numbering via Crossref: the journal began at volume 1 in 2015; 2024 articles carry volume 10, 2025 articles carry volume 11. Finding: the disputed citation pairs "(2024)" with "volume 11"; volume 11 corresponds to 2025. No real article can satisfy both coordinates — the citation is internally inconsistent.
9. **Real-authors check** — A.C. Goh and I.S. Gill are real, co-publishing urologic surgeons. Searched their joint record on PubMed. Finding: the only Goh-AC + Gill-IS + "Wallace" record is PMID 25016136, "Robotic intracorporeal orthotopic neobladder during radical cystectomy in 132 patients", *J Urol* 2014;192:1734–40 — a different paper. No paper titled "Wallace anastomosis in complex dissections" by these authors exists in any index.

(The PubMed reproducibility entry covers both PubMed queries S1 and S2, so the ten checks above are reported as nine consolidated entries in `proof.json`.)

*Source: proof.py JSON summary (`adversarial_checks`)*

## Source Credibility Assessment

| Fact ID | Domain | Type | Note |
|---------|--------|------|------|
| S1, S2 | pubmed.ncbi.nlm.nih.gov | Government | NIH National Library of Medicine; tier 5 (.gov) |
| S3, S4 | europepmc.org | Unclassified | EMBL-EBI scholarly aggregator; tier 2 only because the domain is not in the checker's reference list — a well-established, authoritative index |
| S5 | openalex.org | Unclassified | OurResearch (non-profit) open scholarly index; tier 2 for the same reason — a well-established, authoritative index |
| S6 | www.crossref.org | Academic | Crossref, the DOI registration agency; tier 4 |

The two "Unclassified" entries reflect a gap in the automated checker's domain list, not a genuine credibility concern. Europe PMC and OpenAlex are standard scholarly infrastructure; the verdict does not depend on either of them alone — PubMed (Government) and Crossref (Academic) independently meet the threshold of 3 only in combination with one of them, and all four agree.

*Source: proof.py JSON summary (`evidence` S-type credibility)*

## Source Data

| Fact ID | Extracted value | Found | Quote snippet |
|---------|-----------------|-------|---------------|
| S1 | accessible | Yes | result_count=0 |
| S2 | accessible | Yes | result_count=0 |
| S3 | accessible | Yes | result_count=0 |
| S4 | accessible | Yes | result_count=0 |
| S5 | accessible | Yes | result_count=0 |
| S6 | accessible | Yes | result_count=0 |

For Type S facts the "extracted value" is the search URL's accessibility status returned by `verify_search_registry()`. "Found = Yes" means the search URL responded successfully (HTTP 200), so the search is reproducible by a human reviewer. It does not mean the zero result count was machine-verified — the result count is author-reported and was established by querying the PubMed E-utilities, Europe PMC REST, OpenAlex and Crossref APIs directly on 2026-05-21.

*Source: proof.py JSON summary (`evidence` extractions); extraction-method narrative is author analysis*

## Quality Checks

- **Rule 1 (no hand-typed values):** N/A — no values are parsed from quote text; the proof has no Type B extractions.
- **Rule 2 (verify citations):** PASS — `verify_search_registry()` imported and called; all six search URLs fetched and confirmed accessible.
- **Rule 3 (system time):** N/A — no time-sensitive computation; the search date (2026-05-21) is recorded as text, not used in executable date logic.
- **Rule 4 (explicit claim interpretation):** PASS — `CLAIM_FORMAL` includes a detailed `operator_note` defining the absence operationalization, the result_count semantics, and the SUPPORTED ceiling.
- **Rule 5 (adversarial checks):** PASS — 9 adversarial-check entries covering reproducibility for all four databases plus five independent counter-evidence investigations.
- **Rule 6 (independent cross-checks):** PASS — 4 unique database domains with independent ingestion pipelines.
- **Rule 7 (no hard-coded constants):** PASS — no constants or formulas hand-coded; `compare()` used for all evaluations.
- **validate_proof.py result:** PASS — 17/17 checks passed, 0 issues, 0 warnings.

## Generator

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.34.1 on 2026-05-21.
