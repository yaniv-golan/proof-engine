# Absence-of-Evidence Proof Template

> You are reading one template. See [proof-templates.md](proof-templates.md) for the full index and selection guidance.

For claims about the absence of published evidence (e.g., "There is no published evidence that X causes Y"). Uses `search_registry` to document database searches and their results.

**When to use:** The claim asserts that no credible evidence exists for a proposition. The proof documents systematic searches of authoritative databases.

**Key differences from other templates:**
- Uses `search_registry` instead of (or alongside) `empirical_facts`
- Type S facts (search) in FACT_REGISTRY with `S{N}` IDs
- `verify_search_registry()` checks search URL accessibility (not result counts)
- Verdict is always `SUPPORTED` (never `PROVED`) — reflects weaker trust boundary
- `result_count` is author-reported, not machine-verified
- Each search must include a clickable `search_url` for human reproduction
- Separate thresholds: `search_threshold` (null accessible searches) and `corroboration_threshold` (optional verified corroborating sources)

**Trust boundary:** `result_count` is an authored value — the tool cannot verify it. Mitigations: SUPPORTED verdict (not PROVED), reproducible search URLs, adversarial reproducibility checks, operator_note documenting the gap.

```python
"""
Proof: [claim text — e.g., "There is no published evidence that X causes Y"]
Generated: [date]
"""
import os
import sys
from urllib.parse import urlparse

_SKILL_EXCLUDED_DIRS = {".git", ".venv", "venv", ".tox", ".worktrees",
                        ".cache", ".idea", ".vscode", "node_modules",
                        "__pycache__", "site-packages", "dist", "build"}

def _is_valid_skill_root(p):
    return (os.path.isfile(os.path.join(p, "scripts", "verify_citations.py"))
            and os.path.isfile(os.path.join(p, "SKILL.md")))

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        for _cand in (
            os.path.join(_d, "proof-engine", "skills", "proof-engine"),
            os.path.join(_d, "skills", "proof-engine"),
        ):
            if _is_valid_skill_root(_cand):
                PROOF_ENGINE_ROOT = _cand
                break
        if PROOF_ENGINE_ROOT:
            break
        try:
            for _sib in os.listdir(_d):
                if _sib in _SKILL_EXCLUDED_DIRS:
                    continue
                _sib_path = os.path.join(_d, _sib)
                if not os.path.isdir(_sib_path):
                    continue
                for _cand in (
                    os.path.join(_sib_path, "skills", "proof-engine"),
                    os.path.join(_sib_path, "proof-engine", "skills", "proof-engine"),
                ):
                    if _is_valid_skill_root(_cand):
                        PROOF_ENGINE_ROOT = _cand
                        break
                if PROOF_ENGINE_ROOT:
                    break
                if _sib.startswith("."):
                    try:
                        for _sub in os.listdir(_sib_path):
                            if _sub in _SKILL_EXCLUDED_DIRS:
                                continue
                            _cand = os.path.join(_sib_path, _sub, "skills", "proof-engine")
                            if _is_valid_skill_root(_cand):
                                PROOF_ENGINE_ROOT = _cand
                                break
                    except OSError:
                        pass
                    if PROOF_ENGINE_ROOT:
                        break
        except OSError:
            pass
        if PROOF_ENGINE_ROOT:
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError(
            "PROOF_ENGINE_ROOT not set and skill dir not found via walk-up "
            f"or sibling search from {os.path.dirname(os.path.abspath(__file__))}. "
            "Set the env var explicitly: "
            "export PROOF_ENGINE_ROOT=/path/to/skills/proof-engine"
        )
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_search_registry, verify_all_citations, build_citation_detail
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "property": "absence of published evidence for ...",
    "operator": ">=",
    "operator_note": (
        "An absence-of-evidence proof searches authoritative databases and documents "
        "null results. 'SUPPORTED' means the search threshold was met and no counter-evidence "
        "was found, not that the phenomenon is impossible. A future study could change this verdict. "
        "result_count values are author-reported and reproducible via search_url links but not machine-verified."
    ),
    "search_threshold": 3,         # min unique databases with null results (result_count==0, accessible, deduped by domain)
    "corroboration_threshold": 0,  # min verified corroborating sources (0 = optional)
    "proof_direction": "absence",
}

# 2. FACT REGISTRY
# S{N} = search entries; B{N} = corroborating citation sources (optional); A1 = computed count
FACT_REGISTRY = {
    "S1": {"key": "search_a", "label": "PubMed: [query]"},
    "S2": {"key": "search_b", "label": "Cochrane Library: [query]"},
    "S3": {"key": "search_c", "label": "Embase: [query]"},
    # Optional corroborating sources:
    # "B1": {"key": "corroboration_a", "label": "..."},
    "A1": {"label": "Unique accessible databases with null results", "method": None, "result": None},
}

# 3. SEARCH REGISTRY — systematic database searches
# result_count == 0: null search (counts toward threshold)
# result_count > 0: reviewed search (does NOT count toward threshold; must have adversarial check)
search_registry = {
    "search_a": {
        "database": "PubMed",
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "search_url": "https://pubmed.ncbi.nlm.nih.gov/?term=%22X+cause+Y%22+OR+%22X+association+Y%22",
        "query_terms": ["X cause Y", "X association Y"],
        "date_range": "all years through [year]",
        "result_count": 0,
        "source_name": "NIH National Library of Medicine",
    },
    "search_b": {
        "database": "Cochrane Library",
        "url": "https://www.cochranelibrary.com/",
        "search_url": "https://www.cochranelibrary.com/search?searchBy=6&searchText=%22X+cause+Y%22",
        "query_terms": ["X cause Y"],
        "date_range": "all years",
        "result_count": 0,
        "source_name": "Cochrane Collaboration",
    },
    "search_c": {
        "database": "Embase",
        "url": "https://www.embase.com/",
        "search_url": "https://www.embase.com/search#q=%22X+cause+Y%22",
        "query_terms": ["X cause Y"],
        "date_range": "all years through [year]",
        "result_count": 2,
        "review_note": "2 results found; both study a different compound (not Y) — not relevant to the claim",
        "source_name": "Elsevier Embase",
    },
}

# 4. SEARCH REGISTRY VERIFICATION (checks search_url accessibility, not result counts)
search_results = verify_search_registry(search_registry)

# 5. COUNT UNIQUE DATABASES WITH NULL RESULTS FROM ACCESSIBLE URLS
# Dedup by URL domain — multiple queries to the same database count as one.
# Only "accessible" (HTTP 200) status counts; "known" (403) and "unreachable" don't.
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
n_reviewed = len(reviewed_databases - null_databases)  # only count if no null search on same db
print(f"  Unique databases with null results (accessible): {n_null_verified}")
print(f"  Unique databases with reviewed results only: {n_reviewed}")

# 6. OPTIONAL CORROBORATING SOURCES (authorities explicitly stating the absence)
# If present, these go through the normal verify_all_citations() path.
# Set empirical_facts = {} and skip verify_all_citations() if no corroborating sources.
empirical_facts = {
    # "corroboration_a": {
    #     "quote": "...", "url": "...", "source_name": "...",
    # },
}

COUNTABLE_STATUSES = ("verified", "partial")
if empirical_facts:
    # For all-snapshot proofs against blocked domains (PMC, Nature, etc.), see
    # scripts-api.md "Snapshot-only fast path" — pass skip_live_fetch=True,
    # oa_lookup=False to skip the slow live-fetch + OA-lookup attempts.
    citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)
    n_corroborating = sum(
        1 for key in empirical_facts
        if citation_results.get(key, {}).get("status") in COUNTABLE_STATUSES
    )
else:
    citation_results = {}
    n_corroborating = 0
print(f"  Verified corroborating sources: {n_corroborating}")

# 7. CLAIM EVALUATION — both thresholds must be met independently; wrap in compare() for validator
searches_met = compare(n_null_verified, ">=", CLAIM_FORMAL["search_threshold"],
                       label="null accessible searches vs threshold")
corroboration_met = compare(n_corroborating, ">=", CLAIM_FORMAL["corroboration_threshold"],
                            label="corroborating sources vs threshold")

# Wrap compound boolean in compare() so the validator sees a compare() call (not a bare boolean)
claim_holds = compare(int(searches_met and corroboration_met), ">=", 1,
                      label="both thresholds met")

# 8. ADVERSARIAL CHECKS (Rule 5)
# REQUIRED: at least one reproducibility check per search (preferably per database).
# REQUIRED: one adversarial check per reviewed search (result_count > 0), documenting why
#           the results don't constitute evidence for the claim. Set breaks_proof: True if
#           any result IS genuine evidence — this will set the verdict to UNDETERMINED.
adversarial_checks = [
    # Reproducibility checks — human verification of search_url and result counts
    {
        "question": "Can the PubMed search be reproduced and does it confirm 0 results?",
        "verification_performed": "Clicked search_url for PubMed, confirmed 0 results on [date]",
        "finding": "Search URL accessible; result page shows 0 items for the query",
        "breaks_proof": False,
    },
    {
        "question": "Can the Cochrane Library search be reproduced and does it confirm 0 results?",
        "verification_performed": "Clicked search_url for Cochrane Library, confirmed 0 results on [date]",
        "finding": "Search URL accessible; result page shows 0 items for the query",
        "breaks_proof": False,
    },
    # Reviewed-search adversarial check — REQUIRED for each search with result_count > 0
    {
        "question": "Could the 2 results from Embase constitute evidence for the claim?",
        "verification_performed": "Reviewed 2 results from Embase: [titles/summaries of results]",
        "finding": "Both results study a different compound (not Y); neither addresses the claim",
        "breaks_proof": False,
    },
    # Counter-evidence check
    {
        "question": "Is there any published evidence supporting the claim that X causes Y?",
        "verification_performed": "Searched for 'X causes Y' in Google Scholar and WHO publications",
        "finding": "No credible published evidence found supporting the claim",
        "breaks_proof": False,
    },
]

# 9. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    is_absence = CLAIM_FORMAL.get("proof_direction") == "absence"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    # any_unverified comes from optional empirical_facts only (not search_registry)
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
    elif not claim_holds:
        base_verdict = "UNDETERMINED"
    else:
        base_verdict = "UNDETERMINED"  # defensive fallback
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
        elif fid.startswith("B") and empirical_facts:
            ef_key = info["key"]
            ef = empirical_facts[ef_key]
            cr = citation_results.get(ef_key, {})
            builder.add_empirical_fact(
                fid,
                label=info["label"],
                source_name=ef["source_name"],
                source_url=ef["url"],
                source_quote=ef["quote"],
            )
            builder.set_verification(
                fid,
                status=cr.get("status", "unknown"),
                method=cr.get("method", "full_quote"),
                coverage_pct=cr.get("coverage_pct"),
                fetch_mode=cr.get("fetch_mode", "live"),
                credibility=cr.get("credibility", {}),
            )
            builder.set_extraction(
                fid,
                value=cr.get("status", "unknown"),
                value_in_quote=cr.get("status") in COUNTABLE_STATUSES,
                quote_snippet=ef["quote"][:80],
            )

    builder.add_computed_fact(
        "A1",
        label="Unique accessible databases with null results",
        method=f"unique accessible databases with null results = {n_null_verified}",
        result=n_null_verified,
        depends_on=[fid for fid in FACT_REGISTRY if fid.startswith("S")],
    )

    builder.add_cross_check(
        description="Systematic database searches for published evidence",
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
        independence_note="Searches span distinct databases with independent indexing",
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
        n_null_verified=n_null_verified,
        n_reviewed=n_reviewed,
        n_corroborating=n_corroborating,
        search_threshold=CLAIM_FORMAL["search_threshold"],
        corroboration_threshold=CLAIM_FORMAL["corroboration_threshold"],
        searches_met=searches_met,
        corroboration_met=corroboration_met,
        claim_holds=claim_holds,
    )
    builder.emit()
```

### Adaptation notes

**When NOT to use this template:** If every search in your `search_registry` returned results (all `result_count > 0`), this template is the wrong choice. Use the Qualitative Consensus template instead to argue that the results don't support the claim. The absence template is for proving a gap in the literature, not for critiquing existing literature.

**`review_note` is required for reviewed searches.** Any search with `result_count > 0` MUST include a `review_note` field explaining why those results don't constitute evidence for the claim (e.g., "3 results found but all study a different population"). A bare `result_count: 5` with no explanation is not acceptable.

**Deduplication is by domain, not by registry key.** If you run two queries against PubMed (different `query_terms`), they are two entries in `search_registry` but count as ONE database in `n_null_verified`. The validator counts unique `urlparse(entry["url"]).netloc` values — design your `search_registry` accordingly.

**`corroboration_threshold: 0` means corroborating sources are optional but verified if present.** Set it to a positive integer (e.g., 1) only if the claim requires at least one external authority explicitly stating the absence. When set to 0, adding corroborating sources to `empirical_facts` still runs `verify_all_citations()` on them and populates `any_unverified`, potentially upgrading the verdict to `SUPPORTED (with unverified citations)`.

**Adversarial reproducibility checks are required, not optional.** At least one entry in `adversarial_checks` must document "Clicked search_url, confirmed N results on [date]" for each database. This is the audit trail that partially compensates for the unverifiable `result_count` — a human reviewer clicked the link and saw what the author claimed.
