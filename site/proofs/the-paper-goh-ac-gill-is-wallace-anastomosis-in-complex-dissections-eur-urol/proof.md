# Proof: The paper "Goh AC, Gill IS. Wallace anastomosis in complex dissections. Eur Urol Focus. (2024) 11:80–8" does not exist.

**Generated:** 2026-05-21
**Verdict:** SUPPORTED
**Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| S1 | PubMed — exact-title phrase search for "Wallace anastomosis in complex dissections" | Accessible (0 results) |
| S2 | PubMed — Goh AC as author in *European Urology Focus* | Accessible (0 results) |
| S3 | Europe PMC — exact-title field search | Accessible (0 results) |
| S4 | Europe PMC — Goh AC as author in *European Urology Focus* | Accessible (0 results) |
| S5 | OpenAlex — title search across ~250M works | Accessible (0 results) |
| S6 | Crossref — exact-title match among registered works | Accessible (0 results) |
| A1 | Unique accessible databases returning zero matching records | Computed: 4 independent indexes, 0 results each |

Note: Europe PMC and OpenAlex are scored "tier 2 (unclassified)" by the automated credibility checker only because their domains are not in its built-in reference list. Both are well-established scholarly indexes — Europe PMC is operated by EMBL-EBI, OpenAlex by the non-profit OurResearch. See Source Credibility Assessment in the audit trail.

## Proof Logic

The claim asserts that a specific journal article does not exist. The article is identified by the full citation "Goh AC, Gill IS. Wallace anastomosis in complex dissections. Eur Urol Focus. (2024) 11:80–8" — a title, two authors, a journal, a year, a volume, and a page range. An absence-of-evidence proof cannot demonstrate non-existence with logical certainty, so the claim is operationalised as: no published article matching this citation can be located in any major scholarly index or in the journal's own catalogue.

Four independent scholarly indexes were searched on 2026-05-21. PubMed, the NIH National Library of Medicine database, returned zero records for the exact title phrase (S1) and zero records for any article by A.C. Goh in *European Urology Focus* (S2). Europe PMC, the EMBL-EBI aggregator that spans PubMed, PubMed Central, preprint servers, Agricola and patents, returned zero records for the exact title (S3) and zero for the author-and-journal query (S4). OpenAlex, which indexes roughly 250 million works ingested from Crossref, PubMed and many other sources, returned zero works for the title (S5). Crossref, the DOI registration agency through which the journal's publisher (Elsevier) registers every article, holds no work with that exact title and no such article in *European Urology Focus* (S6). The disputed citation also carries no DOI. Counting unique database domains, four independent indexes each returned zero matching records (A1), which meets the proof's threshold of three.

Three further lines of investigation were pursued to test whether the paper might exist despite the null searches. First, the exact citation string does appear in exactly one place on the open web: the reference list of a 2025 *Frontiers in Oncology* article (DOI 10.3389/fonc.2025.1613772). But a reference-list entry is a *claim* that a paper exists — it is not the paper, and it is precisely the artefact this proof's claim concerns. Second, the citation is internally inconsistent: *European Urology Focus* began at volume 1 in 2015 and runs one volume per year, so its volume 11 corresponds to 2025, while 2024 corresponds to volume 10. The disputed citation pairs "(2024)" with "volume 11", a combination no real article in this journal can satisfy. Third, the sibling references surrounding the disputed entry in that same *Frontiers* reference list carry DOIs that resolve to entirely unrelated papers (see below), revealing a pattern of fabricated citations. Together these confirm that the searches' null results reflect a genuine absence, not a poorly-indexed real paper.

*Source: author analysis*

## What could challenge this verdict?

Ten adversarial checks were performed; none broke the proof.

The reproducibility checks confirmed that all four databases were reachable on 2026-05-21 and that every query returned zero matching records, reproducible by anyone via the search URLs in the audit trail.

The strongest apparent counter-evidence is that the citation string does occur once — in the reference list of the 2025 *Frontiers in Oncology* article. This was examined directly. A reference-list entry is an assertion that a paper exists; it is not itself a publication record, and the claim under proof is exactly that this asserted paper has no real referent. No indexed article, registered DOI, or journal-catalogue entry corresponds to it.

A check of that reference list's other entries found a clear pattern of fabricated citations: three sibling references carry DOIs that resolve to completely different papers — 10.1007/s00423-021-02413-4 points to a 2021 paper in *Langenbeck's Archives of Surgery* (cited as "<!-- not-a-citation-start -->Urol Oncol (2024)<!-- not-a-citation-end --> 42:15–24"); 10.1111/bju.12121 points to a 2013 paper in *BJU International* (cited as "J <!-- not-a-citation-start -->Urol (2024)<!-- not-a-citation-end --> 211:45–55"); 10.1016/j.ucl.2005.02.001 points to a 2005 paper in *Urologic Clinics of North America* (cited as "<!-- not-a-citation-start -->Eur Urol Focus (2024)<!-- not-a-citation-end --> 10:50–8"). The disputed reference has no DOI at all. This pattern is consistent with AI-hallucinated citations.

A check of whether a real paper by these authors might exist under different citation coordinates found that A.C. Goh and I.S. Gill are real, co-publishing urologic surgeons, but their only joint "Wallace"-related record in PubMed is a different 2014 paper (PMID 25016136, *Journal of Urology*). The disputed citation recombines real authors, a real journal and a real surgical technique into a reference whose target does not exist.

*Source: proof.py JSON summary (`adversarial_checks`)*

## Conclusion

**Verdict: SUPPORTED.** The absence threshold was met: four independent scholarly indexes — PubMed, Europe PMC, OpenAlex and Crossref — were searched on 2026-05-21, and each returned zero records matching the disputed citation, against a required threshold of three. All four search databases were accessible; none was blocked or unreachable. The result is reproducible by any reader via the search URLs listed in the audit trail, though the zero result counts are author-reported rather than machine-verified — this is the inherent trust boundary of an absence proof, reflected in the SUPPORTED (rather than PROVED) verdict.

Two independent lines of corroboration strengthen the verdict beyond the searches alone: the citation is internally inconsistent (volume 11 of *European Urology Focus* is 2025, not 2024), and it originates from a reference list demonstrably containing fabricated citations. The cited paper "Goh AC, Gill IS. Wallace anastomosis in complex dissections. Eur Urol Focus. (2024) 11:80–8" does not exist; it is a fabricated citation, most consistent with an AI-hallucinated reference.

This verdict could in principle change if the article were a genuine publication absent from all four major indexes and from its own publisher's DOI registry — an essentially negligible possibility for a purported 2024/2025 article in an Elsevier journal, but one an absence proof cannot logically exclude.

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.34.1 on 2026-05-21.
