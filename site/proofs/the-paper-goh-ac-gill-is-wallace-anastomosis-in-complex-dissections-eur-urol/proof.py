"""
Proof: The paper "Goh AC, Gill IS. Wallace anastomosis in complex dissections.
Eur Urol Focus. (2024) 11:80-8" does not exist.
Generated: 2026-05-21

This is an absence-of-evidence proof. It documents systematic searches of four
independent scholarly indexes (PubMed, Europe PMC, OpenAlex, Crossref) for any
record of a published journal article matching the disputed citation, and
records two independent lines of corroboration in the adversarial checks.
"""
import os
import sys
from urllib.parse import urlparse

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        if os.path.isdir(os.path.join(_d, "proof-engine", "skills", "proof-engine", "scripts")):
            PROOF_ENGINE_ROOT = os.path.join(_d, "proof-engine", "skills", "proof-engine")
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_search_registry, verify_all_citations
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "The paper 'Goh AC, Gill IS. Wallace anastomosis in complex dissections. "
    "Eur Urol Focus. (2024) 11:80–8' does not exist."
)
CLAIM_FORMAL = {
    "subject": (
        "the journal article cited as 'Goh AC, Gill IS. Wallace anastomosis in "
        "complex dissections. Eur Urol Focus. (2024) 11:80–8'"
    ),
    "property": (
        "absence of any indexed record of a published article matching this citation"
    ),
    "operator": ">=",
    "operator_note": (
        "Absence-of-evidence proof. 'Does not exist' is operationalised as: no "
        "published journal article matching the disputed citation -- this exact "
        "title, attributed to A.C. Goh and I.S. Gill, in the journal European "
        "Urology Focus -- can be located in any major scholarly index or in the "
        "journal's own catalogue. The verdict ceiling for an absence proof is "
        "SUPPORTED, never PROVED: comprehensive searching strongly supports "
        "non-existence but cannot logically exclude an unindexed record. "
        "result_count is the number of indexed records that MATCH the cited "
        "article; for relevance-ranked databases, unrelated ranked candidates "
        "returned by a fuzzy query are not matches and do not count toward it. "
        "result_count values are author-reported and reproducible via the "
        "search_url links but are not machine-verified. The exact citation "
        "string does occur once -- in the reference list of a single article "
        "(Frontiers in Oncology, 2025; DOI 10.3389/fonc.2025.1613772) -- but a "
        "reference-list entry is a claim that a paper exists, not the paper "
        "itself, and is the very artefact this claim concerns. Two independent "
        "lines of corroboration are documented in the adversarial checks: "
        "(1) the citation is internally inconsistent -- European Urology Focus "
        "volume 11 corresponds to 2025, not 2024; and (2) sibling references in "
        "that same reference list carry DOIs that resolve to unrelated papers, "
        "indicating a pattern of fabricated citations."
    ),
    "search_threshold": 3,          # min unique accessible databases with null results
    "corroboration_threshold": 0,   # corroborating citation sources optional
    "proof_direction": "absence",
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# S{N} = database searches; A1 = computed count of null-result databases
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "S1": {"key": "pubmed_title",      "label": "PubMed: exact-title phrase search"},
    "S2": {"key": "pubmed_author",     "label": "PubMed: Goh AC as author in European Urology Focus"},
    "S3": {"key": "europepmc_title",   "label": "Europe PMC: exact-title field search"},
    "S4": {"key": "europepmc_author",  "label": "Europe PMC: Goh AC as author in European Urology Focus"},
    "S5": {"key": "openalex",          "label": "OpenAlex: title search"},
    "S6": {"key": "crossref",          "label": "Crossref: exact-title match among indexed works"},
    "A1": {"label": "Unique accessible databases with null results", "method": None, "result": None},
}

# ---------------------------------------------------------------------------
# 3. SEARCH REGISTRY -- systematic database searches (all returned 0 matches)
# result_count == 0 marks a null search that counts toward the threshold.
# Searches run 2026-05-21. Counts reproducible via the search_url links.
# ---------------------------------------------------------------------------
search_registry = {
    "pubmed_title": {
        "database": "PubMed",
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "search_url": "https://pubmed.ncbi.nlm.nih.gov/?term=%22Wallace+anastomosis+in+complex+dissections%22",
        "query_terms": ['"Wallace anastomosis in complex dissections" (exact title phrase)'],
        "date_range": "all years indexed by PubMed; searched 2026-05-21",
        "result_count": 0,
        "source_name": "NIH National Library of Medicine -- PubMed",
    },
    "pubmed_author": {
        "database": "PubMed",
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "search_url": "https://pubmed.ncbi.nlm.nih.gov/?term=Goh+AC%5BAuthor%5D+AND+%22European+Urology+Focus%22%5BJournal%5D",
        "query_terms": ['Goh AC[Author] AND "European Urology Focus"[Journal]'],
        "date_range": "all years indexed by PubMed; searched 2026-05-21",
        "result_count": 0,
        "source_name": "NIH National Library of Medicine -- PubMed",
    },
    "europepmc_title": {
        "database": "Europe PMC",
        "url": "https://europepmc.org/",
        "search_url": "https://europepmc.org/search?query=TITLE%3A%22Wallace%20anastomosis%20in%20complex%20dissections%22",
        "query_terms": ['TITLE:"Wallace anastomosis in complex dissections"'],
        "date_range": "all years indexed by Europe PMC; searched 2026-05-21",
        "result_count": 0,
        "source_name": "EMBL-EBI -- Europe PMC",
    },
    "europepmc_author": {
        "database": "Europe PMC",
        "url": "https://europepmc.org/",
        "search_url": "https://europepmc.org/search?query=AUTH%3A%22Goh%20AC%22%20AND%20JOURNAL%3A%22European%20Urology%20Focus%22",
        "query_terms": ['AUTH:"Goh AC" AND JOURNAL:"European Urology Focus"'],
        "date_range": "all years indexed by Europe PMC; searched 2026-05-21",
        "result_count": 0,
        "source_name": "EMBL-EBI -- Europe PMC",
    },
    "openalex": {
        "database": "OpenAlex",
        "url": "https://openalex.org/",
        "search_url": "https://api.openalex.org/works?filter=title.search:Wallace%20anastomosis%20in%20complex%20dissections",
        "query_terms": ["title.search:Wallace anastomosis in complex dissections"],
        "date_range": "all years indexed by OpenAlex (~250M works); searched 2026-05-21",
        "result_count": 0,
        "source_name": "OurResearch -- OpenAlex",
    },
    "crossref": {
        "database": "Crossref",
        "url": "https://www.crossref.org/",
        "search_url": "https://api.crossref.org/works?query.title=Wallace+anastomosis+in+complex+dissections&rows=20",
        "query_terms": [
            "query.title=Wallace anastomosis in complex dissections "
            "(exact-title matches among Crossref-registered works)"
        ],
        "date_range": "all years of Crossref DOI registrations; searched 2026-05-21",
        "result_count": 0,
        "source_name": "Crossref -- DOI registration agency",
    },
}

# ---------------------------------------------------------------------------
# 4. SEARCH REGISTRY VERIFICATION (checks search_url accessibility)
# ---------------------------------------------------------------------------
search_results = verify_search_registry(search_registry)

# ---------------------------------------------------------------------------
# 5. COUNT UNIQUE DATABASES WITH NULL RESULTS FROM ACCESSIBLE URLS
# Dedup by URL domain -- multiple queries to one database count once.
# ---------------------------------------------------------------------------
null_databases = set()
reviewed_databases = set()
for key, entry in search_registry.items():
    domain = urlparse(entry["url"]).netloc
    if search_results[key]["status"] != "accessible":
        continue
    if entry["result_count"] == 0:
        null_databases.add(domain)
    else:
        reviewed_databases.add(domain)
n_null_verified = len(null_databases)
n_reviewed = len(reviewed_databases - null_databases)
print(f"  Unique databases with null results (accessible): {n_null_verified}")
print(f"  Unique databases with reviewed results only: {n_reviewed}")

# ---------------------------------------------------------------------------
# 6. CORROBORATING SOURCES -- none (corroboration_threshold is 0).
# The two corroboration lines (volume/year contradiction; fabricated-DOI
# pattern) are documented as adversarial checks, not citation-verified facts.
# ---------------------------------------------------------------------------
empirical_facts = {}

COUNTABLE_STATUSES = ("verified", "partial")
if empirical_facts:
    citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)
    n_corroborating = sum(
        1 for key in empirical_facts
        if citation_results.get(key, {}).get("status") in COUNTABLE_STATUSES
    )
else:
    citation_results = {}
    n_corroborating = 0
print(f"  Verified corroborating sources: {n_corroborating}")

# ---------------------------------------------------------------------------
# 7. CLAIM EVALUATION -- both thresholds must be met independently
# ---------------------------------------------------------------------------
searches_met = compare(n_null_verified, ">=", CLAIM_FORMAL["search_threshold"],
                       label="null accessible databases vs threshold")
corroboration_met = compare(n_corroborating, ">=", CLAIM_FORMAL["corroboration_threshold"],
                            label="corroborating sources vs threshold")
claim_holds = compare(int(searches_met and corroboration_met), ">=", 1,
                      label="both thresholds met")

# ---------------------------------------------------------------------------
# 8. ADVERSARIAL CHECKS (Rule 5) -- documents Step 2 research performed on
#    2026-05-21. Past tense: these record investigation, not run-time searches.
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": "Can the PubMed searches be reproduced and do they confirm 0 results?",
        "verification_performed": (
            "Queried the PubMed E-utilities API and the public PubMed search page on "
            "2026-05-21. esearch term='\"Wallace anastomosis in complex dissections\"' "
            "returned count=0. esearch term='Goh AC[Author] AND \"European Urology "
            "Focus\"[Journal]' returned count=0 with the message 'No items found'."
        ),
        "finding": (
            "PubMed accessible; both queries return 0 records. No article with this "
            "title is indexed, and A.C. Goh has no article indexed in European "
            "Urology Focus."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Can the Europe PMC searches be reproduced and do they confirm 0 results?",
        "verification_performed": (
            "Queried the Europe PMC REST API on 2026-05-21. "
            "query='TITLE:\"Wallace anastomosis in complex dissections\"' returned "
            "hitCount=0. query='AUTH:\"Goh AC\" AND JOURNAL:\"European Urology Focus\"' "
            "returned hitCount=0."
        ),
        "finding": (
            "Europe PMC accessible; both queries return 0 records. Europe PMC "
            "aggregates PubMed, PubMed Central, preprint servers, Agricola and "
            "patents, so a 0 hitCount spans an exceptionally broad corpus."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Can the OpenAlex search be reproduced and does it confirm 0 results?",
        "verification_performed": (
            "Queried the OpenAlex API on 2026-05-21. "
            "filter=title.search:Wallace anastomosis in complex dissections returned "
            "meta.count=0 across the ~250-million-work OpenAlex index."
        ),
        "finding": (
            "OpenAlex accessible; 0 works match the title. OpenAlex ingests Crossref, "
            "PubMed, and many other sources, so this is a wide independent index."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Can the Crossref search be reproduced and does it confirm 0 results?",
        "verification_performed": (
            "Queried the Crossref REST API on 2026-05-21. A query.title search and a "
            "journal-scoped scan of European Urology Focus (ISSN 2405-4569) were both "
            "examined; 0 indexed works carry the exact title 'Wallace anastomosis in "
            "complex dissections', and no European Urology Focus work has that title "
            "or lists A.C. Goh as an author of an article so titled. The disputed "
            "citation also has no DOI."
        ),
        "finding": (
            "Crossref accessible; 0 records match the cited article. Crossref is the "
            "DOI registration agency for Elsevier (the publisher of European Urology "
            "Focus), so a real article would carry a registered DOI here."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could the relevance-ranked candidates returned by fuzzy title queries "
            "actually be the disputed paper under a different wording?"
        ),
        "verification_performed": (
            "Reviewed the ranked candidate lists returned by the Crossref and OpenAlex "
            "fuzzy title queries and by Google Scholar / web search for the title."
        ),
        "finding": (
            "Every ranked candidate is a different, real publication on ureteroileal "
            "anastomosis (e.g. 'Wallace method of ureteroileal anastomosis', Urology "
            "1975; 'Evaluation of Ureterointestinal Anastomosis: Wallace vs Bricker'). "
            "None is titled 'Wallace anastomosis in complex dissections' and none is "
            "authored by Goh and Gill. Fuzzy databases return ranked near-matches even "
            "for non-existent titles, so these candidates are not counter-evidence."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is there ANY published evidence that the cited paper exists?",
        "verification_performed": (
            "Searched for every occurrence of the exact title string across web "
            "search, Google Scholar, and the four scholarly indexes."
        ),
        "finding": (
            "The exact citation string occurs in exactly one place: the reference "
            "list of the article 'Comparative analysis of ureteroileal anastomotic "
            "stricture rates: Bricker versus Wallace techniques...' (Frontiers in "
            "Oncology, 2025, DOI 10.3389/fonc.2025.1613772), as reference entry "
            "'Goh AC, Gill IS. Wallace anastomosis in complex dissections. Eur Urol "
            "Focus. (2024) 11:80-8' with NO DOI. A reference-list entry is a claim "
            "that a paper exists; it is not the paper, and is precisely the artefact "
            "this proof's claim concerns. No indexed article, registered DOI, or "
            "journal-catalogue entry corresponds to it. This does not break the "
            "proof -- it confirms the disputed citation has no referent."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the citation's sole point of origin show signs that the reference "
            "is fabricated rather than a real-but-poorly-indexed paper?"
        ),
        "verification_performed": (
            "Examined the sibling references in the same Frontiers in Oncology "
            "reference list and resolved their DOIs via the Crossref API on 2026-05-21."
        ),
        "finding": (
            "The reference list shows a clear pattern of fabricated citations. Three "
            "sibling references carry DOIs that resolve to entirely unrelated papers: "
            "10.1007/s00423-021-02413-4 (cited as 'Kouba ES et al. Urol Oncol (2024) "
            "42:15-24') actually resolves to a 2021 paper in Langenbeck's Archives of "
            "Surgery; 10.1111/bju.12121 (cited as 'Goh AC, Gill IS, Desai MM. J Urol "
            "(2024) 211:45-55') actually resolves to a 2013 paper in BJU "
            "International; 10.1016/j.ucl.2005.02.001 (cited as 'Goh AC, Gill IS. Eur "
            "Urol Focus (2024) 10:50-8') actually resolves to a 2005 paper in "
            "Urologic Clinics of North America. The disputed reference itself has no "
            "DOI at all. This pattern is consistent with AI-hallucinated citations "
            "and corroborates that the disputed paper does not exist."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is the disputed citation internally consistent on volume and year?",
        "verification_performed": (
            "Cross-referenced European Urology Focus volume numbering via the Crossref "
            "API on 2026-05-21: the journal began at volume 1 in 2015; articles "
            "published in 2024 carry volume 10; articles published in 2025 carry "
            "volume 11."
        ),
        "finding": (
            "The disputed citation pairs '(2024)' with 'volume 11'. European Urology "
            "Focus volume 11 corresponds to publication year 2025, and 2024 "
            "corresponds to volume 10. No real article in this journal can satisfy "
            "both coordinates simultaneously -- the citation is internally "
            "inconsistent. This is independent corroboration that the citation does "
            "not describe a real paper; it does not break the proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could a real paper by these authors on this topic exist under different "
            "citation coordinates, making the claim too strong?"
        ),
        "verification_performed": (
            "A.C. Goh and I.S. Gill are real urologic surgeons who have co-published. "
            "Searched their joint publication record on PubMed on 2026-05-21 "
            "('Goh AC[Author] AND Gill IS[Author] AND Wallace')."
        ),
        "finding": (
            "The only Goh-AC + Gill-IS record involving 'Wallace' in PubMed is PMID "
            "25016136, 'Robotic intracorporeal orthotopic neobladder during radical "
            "cystectomy in 132 patients', J Urol 2014;192:1734-40 -- a different "
            "paper with a different title in a different journal and year. No paper "
            "titled 'Wallace anastomosis in complex dissections' by these authors "
            "exists in any index. The disputed citation recombines real authors, a "
            "real journal, and a real surgical technique into a reference whose "
            "target does not exist."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 9. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    is_absence = CLAIM_FORMAL.get("proof_direction") == "absence"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif claim_holds:
        if is_absence:
            base_verdict = "SUPPORTED"
        elif CLAIM_FORMAL.get("proof_direction") == "disprove":
            base_verdict = "DISPROVED"
        else:
            base_verdict = "PROVED"
    else:
        base_verdict = "UNDETERMINED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    for fid, info in FACT_REGISTRY.items():
        if fid.startswith("S"):
            sr_key = info["key"]
            entry = search_registry[sr_key]
            sr = search_results.get(sr_key, {})
            builder.add_search_fact(
                fid,
                label=info["label"],
                database=entry["database"],
                url=entry["url"],
                search_url=entry["search_url"],
                query_terms=", ".join(entry["query_terms"]),
                date_range=entry["date_range"],
                result_count=entry["result_count"],
                source_name=entry["source_name"],
            )
            builder.set_extraction(
                fid,
                value=sr.get("status", "unknown"),
                value_in_quote=sr.get("status") == "accessible",
                quote_snippet=f"result_count={entry['result_count']}",
            )

    builder.add_computed_fact(
        "A1",
        label="Unique accessible databases with null results",
        method=f"count of unique accessible databases with result_count == 0 = {n_null_verified}",
        result=n_null_verified,
        depends_on=[fid for fid in FACT_REGISTRY if fid.startswith("S")],
    )

    builder.add_cross_check(
        description=(
            "Systematic searches of four independent scholarly indexes for any "
            "record of the disputed article"
        ),
        fact_ids=[fid for fid in FACT_REGISTRY if fid.startswith("S")],
        n_databases_searched=len(search_registry),
        n_null_verified=n_null_verified,
        n_reviewed=n_reviewed,
        databases={
            key: {
                "database": entry["database"],
                "result_count": entry["result_count"],
                "status": search_results[key]["status"],
            }
            for key, entry in search_registry.items()
        },
        independence_note=(
            "PubMed (NLM), Europe PMC (EMBL-EBI), OpenAlex (OurResearch) and "
            "Crossref (DOI registration agency) maintain separate indexes with "
            "independent ingestion pipelines; all four would index a genuine 2024 "
            "or 2025 European Urology Focus article."
        ),
        agreement=claim_holds,
    )

    for ac in adversarial_checks:
        builder.add_adversarial_check(
            question=ac["question"],
            verification_performed=ac["verification_performed"],
            finding=ac["finding"],
            breaks_proof=ac["breaks_proof"],
        )

    builder.set_verdict(base_verdict, any_unverified=any_unverified)
    builder.set_key_results(
        n_databases_searched=len(search_registry),
        n_null_verified=n_null_verified,
        n_reviewed=n_reviewed,
        n_corroborating=n_corroborating,
        search_threshold=CLAIM_FORMAL["search_threshold"],
        corroboration_threshold=CLAIM_FORMAL["corroboration_threshold"],
        searches_met=searches_met,
        corroboration_met=corroboration_met,
        claim_holds=claim_holds,
    )

    print()
    print(f"VERDICT: {verdict}")
    print()
    builder.emit()
