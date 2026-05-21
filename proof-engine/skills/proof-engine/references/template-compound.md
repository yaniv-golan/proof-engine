# Compound CLAIM_FORMAL Template

> You are reading one template. See [proof-templates.md](proof-templates.md) for the full index and selection guidance.

For claims with multiple sub-claims joined by AND. Each sub-claim gets its own confirmation list, source count, and `compare()` evaluation. The compound verdict aggregates sub-claim results.

**When to use:** The claim contains AND or implies multiple independently verifiable conditions. Examples: "Israel withdrew from Gaza AND Hamas won the 2006 election," "Brain weight is 2% of body weight AND uses 20% of oxygen."

**Not supported:** Negated sub-claims (X BUT NOT Y) require per-sub-claim `proof_direction`, which this template doesn't model. For claims with negated parts, decompose into separate proofs — one affirmative, one disproof — using the qualitative template's `proof_direction` field.

```python
"""
Proof: [compound claim text]
Generated: [date]
"""
import os
import sys

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

from scripts.verify_citations import verify_all_citations, build_citation_detail
# If any sub-claim uses absence-search evidence (Type S facts), also import:
# from scripts.verify_citations import verify_search_registry
# from urllib.parse import urlparse
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "sub_claims": [
        {"id": "SC1", "property": "...", "operator": ">=", "threshold": 3, "operator_note": "..."},
        {"id": "SC2", "property": "...", "operator": ">=", "threshold": 3, "operator_note": "..."},
        # For 3+ sub-claims, just keep adding entries — the rest of the template
        # loops over CLAIM_FORMAL["sub_claims"], no other code changes needed.
        # Example of a derived sub-claim (v1.43.0+): computed from SC1+SC2 with
        # no independent sources of its own. Validator skips the 2-source Rule 6
        # warning for these but requires at least one add_computed_fact(...) with
        # non-empty depends_on to prove derivation is wired.
        # {"id": "SC3", "property": "...", "derived": True,
        #  "operator_note": "Computed from SC1 ∧ SC2; no independent sources"},
    ],
    "compound_operator": "AND",  # only AND is supported; OR claims should be decomposed into separate proofs
    "operator_note": "All sub-claims must hold for the compound claim to be PROVED",
    # "subclaim_to_sources": {     # optional: add when using descriptive empirical_facts key names
    #     "SC1": ["source_key_a", "source_key_b"],  # list the empirical_facts keys for each sub-claim
    #     "SC2": ["source_key_c", "source_key_d"],
    # },
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "sc1_source_a", "label": "SC1 source A: ..."},
    "B2": {"key": "sc1_source_b", "label": "SC1 source B: ..."},
    "B3": {"key": "sc2_source_a", "label": "SC2 source A: ..."},
    "B4": {"key": "sc2_source_b", "label": "SC2 source B: ..."},
    "A1": {"label": "SC1 source count", "method": None, "result": None},
    "A2": {"label": "SC2 source count", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — grouped by sub-claim
empirical_facts = {
    "sc1_source_a": {"quote": "...", "url": "...", "source_name": "..."},
    "sc1_source_b": {"quote": "...", "url": "...", "source_name": "..."},
    "sc2_source_a": {"quote": "...", "url": "...", "source_name": "..."},
    "sc2_source_b": {"quote": "...", "url": "...", "source_name": "..."},
}

# 3b. SNAPSHOT FALLBACK — for sources that block automated fetches
# Two approaches depending on source access:
#
# PUBLIC sources that block bots (PMC, .gov with JS rendering):
#   Use inline "snapshot" — content is public, safe to commit.
#
# PAYWALLED sources (Nature, Springer, Elsevier, Wiley):
#   Use "snapshot_file" pointing to snapshots/ directory (.gitignored).
#   This keeps copyrighted content out of committed proof.py.
#   See environment-and-sources.md "Handling Paywalled Sources" for details.

_PROOF_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_snapshot(fname):
    fpath = os.path.join(_PROOF_DIR, fname)
    try:
        with open(fpath) as f:
            return f.read()
    except FileNotFoundError:
        return None

# Public source (PMC) — inline snapshot is fine:
#   "sc1_source_a": {
#       "quote": "...", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC...",
#       "source_name": "...",
#       "snapshot": _load_snapshot("pmc_source_a.html"),
#       "snapshot_source": "public:pre_fetched",
#   },
#
# Paywalled source — use snapshot_file (content stays in .gitignored snapshots/):
#   "sc1_source_b": {
#       "quote": "...", "url": "https://nature.com/articles/...",
#       "source_name": "...",
#       "snapshot_file": "snapshots/B2_snapshot.txt",
#       "snapshot_source": "paywalled:user_provided",
#   },

# 3c. OPTIONAL: SEARCH REGISTRY — Type S facts for absence-search sub-claims
# When a sub-claim's strongest evidence is an absence search ("no published
# evidence in PubMed/Cochrane/etc."), define a search_registry alongside
# empirical_facts. Each entry has the same shape as in template-absence.md
# (database, url, search_url, query_terms, date_range, result_count,
# source_name). Keys use the same SCn_ prefix as empirical_facts so the
# generalized loops in steps 5/6 pick them up automatically.
#
# IMPORTANT (Rule 6 caveat): A sub-claim backed only by S-facts is a
# 1-source sub-claim — the validator will warn. Pair each S-fact with at
# least one corroborating B-fact (an authority statement of the absence),
# OR mark the sub-claim derived: True if its conclusion is computed from
# other sub-claims' results.
#
# search_registry = {
#     "sc2_search_a": {
#         "database": "PubMed",
#         "url": "https://pubmed.ncbi.nlm.nih.gov/",
#         "search_url": "https://pubmed.ncbi.nlm.nih.gov/?term=...",
#         "query_terms": ["..."],
#         "date_range": "all years through [year]",
#         "result_count": 0,
#         "source_name": "NIH National Library of Medicine",
#     },
# }
# search_results = verify_search_registry(search_registry)

# 4. CITATION VERIFICATION (Rule 2)
# For all-snapshot proofs against blocked domains (PMC, Nature, etc.), see
# scripts-api.md "Snapshot-only fast path" — pass skip_live_fetch=True,
# oa_lookup=False to skip the slow live-fetch + OA-lookup attempts.
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
COUNTABLE_STATUSES = ("verified", "partial")
# sc_keys: {sc_id: [empirical_facts keys for this sub-claim]}
sc_keys = {sc["id"]: [k for k in empirical_facts if k.startswith(sc["id"].lower() + "_")]
           for sc in CLAIM_FORMAL["sub_claims"]}
# Optional: S-fact keys, if search_registry is defined.
# sc_search_keys = {sc["id"]: [k for k in search_registry if k.startswith(sc["id"].lower() + "_")]
#                   for sc in CLAIM_FORMAL["sub_claims"]}

# n_sc: {sc_id: number of verified+partial citations}. For derived sub-claims,
# the count is computed from other sub-claims' results — set it manually below.
# When pairing with S-facts, add their result_count==0 contributions:
#   n_sc[sc_id] += sum(1 for k in sc_search_keys[sc_id]
#                      if search_registry[k]["result_count"] == 0
#                      and search_results[k]["status"] == "accessible")
n_sc = {sc["id"]: sum(1 for k in sc_keys[sc["id"]]
                      if citation_results[k]["status"] in COUNTABLE_STATUSES)
        for sc in CLAIM_FORMAL["sub_claims"]}

# Example: derived sub-claim SC3 = SC1 ∧ SC2
# n_sc["SC3"] = int(n_sc["SC1"] >= CLAIM_FORMAL["sub_claims"][0]["threshold"]
#                   and n_sc["SC2"] >= CLAIM_FORMAL["sub_claims"][1]["threshold"])

# 6. PER-SUB-CLAIM EVALUATION — loop over sub_claims
sc_holds = {}
for sc in CLAIM_FORMAL["sub_claims"]:
    sc_holds[sc["id"]] = compare(
        n_sc[sc["id"]], sc.get("operator", ">="), sc["threshold"],
        label=f"{sc['id']}: {sc['property']}"
    )

# 7. COMPOUND EVALUATION
n_holding = sum(sc_holds.values())
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# 8. COI FLAGS — per sub-claim, defined before verdict
# Keyed by sub-claim id; add entries for SC3, SC4, ... as needed.
sc_coi_flags = {
    sc["id"]: [
        # Populate during proof writing. Empty list if no COI identified.
    ]
    for sc in CLAIM_FORMAL["sub_claims"]
}

# 9. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "Searched for ...",
        "finding": "...",  # If counter-evidence found AND breaks_proof=False: MUST include explicit rebuttal (Rule 5)
        "breaks_proof": False,  # If True, verdict forced to UNDETERMINED
    },
]

# 10. VERDICT — handles mixed results, proof direction, and unverified citations
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"

    # Per-sub-claim COI gate (Rule 6) — loop over sub_claims
    sc_coi_override = {}
    for sc in CLAIM_FORMAL["sub_claims"]:
        sc_id = sc["id"]
        # Derived sub-claims have no own sources → no COI to gate
        if sc.get("derived"):
            sc_coi_override[sc_id] = False
            continue
        confirmed = {k for k in sc_keys[sc_id]
                     if citation_results[k]["status"] in COUNTABLE_STATUSES}
        flags = sc_coi_flags[sc_id]
        favorable = {f["source_key"] for f in flags
                     if f["direction"] == "favorable_to_subject"
                     and f["source_key"] in confirmed}
        unfavorable = {f["source_key"] for f in flags
                       if f["direction"] == "unfavorable_to_subject"
                       and f["source_key"] in confirmed}
        majority = max(len(favorable), len(unfavorable)) if flags else 0
        sc_coi_override[sc_id] = (n_sc[sc_id] >= sc["threshold"]
                                  and majority > n_sc[sc_id] / 2)

    any_coi_override = any(sc_coi_override.values())

    # Contested qualifier override: SC1 holds + SC2 fails → DISPROVED
    # (assertion exists but the epistemic qualifier is not warranted).
    # INTRINSICALLY 2-SUB-CLAIM: this branch is gated by len(sub_claims) == 2
    # because the carve-out relies on "SC1 = factual assertion, SC2 = qualifier"
    # semantics that don't generalize. For 3+ sub-claims, restructure as
    # separate simple-AND sub-claims or use the absence template for
    # epistemic checks. Set is_contested_qualifier = False to skip the branch.
    is_contested_qualifier = "qualifier" in CLAIM_FORMAL.get("operator_note", "").lower()
    is_2sc_contested_qualifier = (
        is_contested_qualifier
        and len(CLAIM_FORMAL["sub_claims"]) == 2
    )

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif any_coi_override:
        base_verdict = "UNDETERMINED"
    elif is_2sc_contested_qualifier and sc_holds["SC1"] and not sc_holds["SC2"]:
        base_verdict = "DISPROVED"
    elif not claim_holds and n_holding > 0:
        base_verdict = "PARTIALLY VERIFIED"
    elif claim_holds:
        base_verdict = "DISPROVED" if is_disproof else "PROVED"
    elif not claim_holds and n_holding == 0:
        base_verdict = "UNDETERMINED"
    else:
        base_verdict = "UNDETERMINED"  # defensive fallback
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    # Map empirical_facts key → sub_claim id via prefix (sc1_*, sc2_*, ...)
    # Explicit loop with assertion catches mislabeling that the old
    # `"SC1" if … else "SC2"` ternary would silently swallow for SC3+.
    def _key_to_sub_claim(ef_key):
        for sc in CLAIM_FORMAL["sub_claims"]:
            if ef_key.startswith(sc["id"].lower() + "_"):
                return sc["id"]
        raise AssertionError(
            f"empirical_facts key {ef_key!r} has no SCn_ prefix — "
            "every empirical fact must be assigned to a sub-claim"
        )

    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        ef = empirical_facts[ef_key]
        cr = citation_results.get(ef_key, {})
        builder.add_empirical_fact(
            fid,
            label=info["label"],
            source_name=ef["source_name"],
            source_url=ef["url"],
            source_quote=ef["quote"],
            sub_claim=_key_to_sub_claim(ef_key),
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

    # Per-sub-claim Type A count fact + cross_check + sub_claim_result.
    # FACT_REGISTRY's "A1", "A2", ... entries are mapped 1:1 with sub_claims
    # in declaration order. Derived sub-claims still get a Type A fact; its
    # depends_on references the source sub-claims' B-facts (validator
    # enforces non-empty depends_on for derived sub-claims).
    for i, sc in enumerate(CLAIM_FORMAL["sub_claims"]):
        sc_id = sc["id"]
        a_id = f"A{i + 1}"
        sc_fact_ids = [fid for fid, info in FACT_REGISTRY.items()
                       if fid.startswith("B") and info["key"] in sc_keys[sc_id]]
        if sc.get("derived"):
            # For a derived sub-claim, populate depends_on with the source
            # sub-claims' fact IDs. Edit this loop to reference whichever
            # sub-claims this one is derived from.
            sc_fact_ids = [fid for fid in FACT_REGISTRY
                           if fid.startswith("B")]
        builder.add_computed_fact(
            a_id,
            label=f"{sc_id} source count",
            method=f"count(verified {sc_id.lower()} citations) = {n_sc[sc_id]}",
            result=n_sc[sc_id],
            depends_on=sc_fact_ids,
            sub_claim=sc_id,
        )

        builder.add_cross_check(
            description=f"{sc_id}: independent sources consulted",
            fact_ids=sc_fact_ids,
            n_sources_consulted=len(sc_keys[sc_id]),
            n_sources_verified=n_sc[sc_id],
            sources={k: citation_results[k]["status"] for k in sc_keys[sc_id]},
            independence_note="Sources from different publications",
            coi_flags=sc_coi_flags[sc_id],
            agreement=sc_holds[sc_id],
        )

        builder.add_sub_claim_result(
            id=sc_id, n_confirming=n_sc[sc_id],
            threshold=sc["threshold"], holds=sc_holds[sc_id],
        )

    # Optional: emit Type S facts for absence-search sub-claims.
    # Uncomment if search_registry is defined above. Same SCn_ prefix
    # convention as empirical_facts maps each entry to its sub-claim.
    # for sr_key, entry in search_registry.items():
    #     # SCn label is derived from key prefix
    #     sub_claim_id = None
    #     for sc in CLAIM_FORMAL["sub_claims"]:
    #         if sr_key.startswith(sc["id"].lower() + "_"):
    #             sub_claim_id = sc["id"]; break
    #     # S-fact IDs typically S1, S2, ... — pick the next free index per registry
    #     s_id = f"S{list(search_registry).index(sr_key) + 1}"
    #     builder.add_search_fact(
    #         s_id,
    #         label=f"{entry['database']}: {', '.join(entry['query_terms'])}",
    #         database=entry["database"],
    #         url=entry["url"],
    #         search_url=entry["search_url"],
    #         query_terms=entry["query_terms"],
    #         date_range=entry["date_range"],
    #         result_count=entry["result_count"],
    #         source_name=entry["source_name"],
    #         sub_claim=sub_claim_id,
    #     )

    for ac in adversarial_checks:
        builder.add_adversarial_check(
            question=ac["question"],
            verification_performed=ac["verification_performed"],
            finding=ac["finding"],
            breaks_proof=ac["breaks_proof"],
        )

    builder.set_verdict(base_verdict, any_unverified=any_unverified)
    builder.set_key_results(
        n_holding=n_holding,
        n_total=n_total,
        claim_holds=claim_holds,
    )
    builder.emit()
```

**Key design points:**
- `PARTIALLY VERIFIED` is checked BEFORE the `claim_holds` branches — mixed results short-circuit the verdict.
- For **contested qualifier** claims: `is_contested_qualifier` auto-detects from `operator_note` and inserts a `sc1_holds and not sc2_holds → DISPROVED` branch before `PARTIALLY VERIFIED`. This ensures "assertion exists but qualifier is unwarranted" produces DISPROVED, not PARTIALLY VERIFIED. Standard compound claims are unaffected.
- `UNDETERMINED` when no sub-claims meet threshold — for source-counting proofs, insufficient evidence is not disproof.
- Per-sub-claim `compare()` calls use labels, so the computation trace is self-documenting.
- `any_unverified` modifies PROVED → PROVED (with unverified citations). For PARTIALLY VERIFIED and UNDETERMINED, citation status is documented in proof.md's Conclusion section rather than changing the verdict label — those verdicts already signal incompleteness.
- `sub_claim_results` in the JSON summary gives downstream tooling per-SC detail.
- Only `AND` compounds are supported. For OR claims ("X or Y is true"), decompose into separate proofs — an OR compound where either sub-claim suffices is just two independent proofs.

**Adapting for numeric compound claims:** Replace the citation-counting step with `parse_number_from_quote()` / `verify_data_values()` per the Numeric/Table template. The compound evaluation (steps 6-7) stays the same — only the per-sub-claim counting (step 5) changes.

**Sub-claims with no possible supporting sources:** Keep the sub-claim in `CLAIM_FORMAL["sub_claims"]` with its full structure — do not remove it from `n_total`. Set its `n_confirming` to 0 via an empty confirmations list (not a hardcoded literal). The compound verdict will naturally produce `PARTIALLY VERIFIED` (some hold, some don't) or `UNDETERMINED` (none hold). Removing a failing sub-claim from the denominator would change the claim's meaning and could turn a failing proof into a passing one. Document the sub-claim's failure and the evidence for it (e.g., adversarial findings) in the proof's adversarial_checks section.

### Adaptation: Contested Qualifier Claims

When a claim bundles a factual assertion with an epistemic qualifier ("verified," "confirmed," "proven," "established," "debunked"), decompose into:

- **SC1 (provenance):** Do the underlying assertions exist and originate from an identifiable source? SC1 means "the assertion exists and can be traced to an identifiable source" — NOT "the assertion is true."
- **SC2 (epistemic):** Has the assertion been independently verified/confirmed/etc. as claimed? SC2 is a meta-claim requiring different sources than SC1: independent audits, judicial findings, investigative bodies — entities that *evaluated* the evidence, not just reported it.

**Empty SC2 is expected.** For many contested qualifier claims, no sources exist that *confirm* independent verification — the qualifier simply hasn't been warranted. In this case, `sc_keys["SC2"]` is empty and `n_sc["SC2"] = 0`, which causes SC2 to fail naturally. This is the normal pattern, not an error. Sources that *reject* the qualifier (e.g., an independent review finding "claims not substantiated") belong in `adversarial_checks`, not in SC2's `empirical_facts` — they are counter-evidence, not confirming sources.

**COI gate and provenance (SC1).** COI does not undermine provenance sources — a biased or interested party can still confirm that an allegation was made. For SC1 (provenance), bypass the COI gate:

```python
# After the COI gate loop, override the SC1 entry:
sc_coi_override["SC1"] = False  # Provenance: COI does not invalidate "allegation was made"
```

**Contested-qualifier requires exactly 2 sub-claims.** The carve-out (`sc_holds["SC1"] and not sc_holds["SC2"] → DISPROVED`) is gated by `len(CLAIM_FORMAL["sub_claims"]) == 2`. For 3+ sub-claims, restructure as separate simple-AND sub-claims or use the absence template for epistemic checks.

COI is especially critical for SC2 — apply Rule 6 COI check rigorously.

**Verdict mapping** follows the compound template's existing logic:

| SC1 | SC2 | Verdict |
|-----|-----|---------|
| holds | holds | PROVED (assertion exists and qualifier is warranted) |
| holds | fails | DISPROVED (assertion exists but qualifier is false) |
| fails | fails | UNDETERMINED (insufficient evidence either way) |

Note: SC1-fails/SC2-holds is not a realistic state for this pattern — if the assertion's provenance can't be established (SC1 fails), there's nothing for SC2 to verify. The compound template's standard `n_holding > 0` → PARTIALLY VERIFIED branch handles this edge case if it ever arises, but no special logic is needed.

If SC1 fails because sources actively deny the assertion was ever made (not just absence of evidence), document this in `adversarial_checks` with `breaks_proof: True`. The `any_breaks` check at the top of the verdict block will force UNDETERMINED, and the proof.md Conclusion section should explain that the assertion's provenance itself is disputed.

**Example CLAIM_FORMAL:**

```python
CLAIM_FORMAL = {
    "subject": "...",
    "sub_claims": [
        {"id": "SC1", "property": "assertion originates from identifiable source",
         "operator": ">=", "threshold": 2,
         "operator_note": "SC1 checks provenance — does the assertion exist?"},
        {"id": "SC2", "property": "assertion independently verified as claimed",
         "operator": ">=", "threshold": 3,
         "operator_note": "SC2 checks the epistemic qualifier — was it independently verified?"},
    ],
    "compound_operator": "AND",
    "operator_note": (
        "The claim uses the qualifier '[qualifier]'. SC1 checks provenance "
        "(the assertion exists), SC2 checks the qualifier (independently verified). "
        "Both must hold for the claim to be PROVED."
    ),
}
```
