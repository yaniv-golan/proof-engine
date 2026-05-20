"""
Proof: Topaz et al. (2026) analyzed 2.5 million biomedical papers in PubMed
Central from January 2023 through February 2026 and identified 4,046 references
pointing to studies that do not exist, distributed across 2,810 papers.

Generated: 2026-05-20
"""
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        if os.path.isdir(os.path.join(_d, "proof-engine", "skills", "proof-engine", "scripts")):
            PROOF_ENGINE_ROOT = os.path.join(_d, "proof-engine", "skills", "proof-engine")
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        # Fall back to local proof-citations package if skill scripts unavailable.
        PROOF_ENGINE_ROOT = None
if PROOF_ENGINE_ROOT:
    sys.path.insert(0, PROOF_ENGINE_ROOT)
    from scripts.verify_citations import verify_all_citations  # noqa: E402
    from scripts.computations import compare, apply_verdict_qualifier  # noqa: E402
    from scripts.proof_summary import ProofSummaryBuilder  # noqa: E402
else:
    # Use proof-citations package directly (skill scripts are thin shims over it).
    from proof_citations.verify import verify_all_citations  # type: ignore
    from proof_citations.computations import compare, apply_verdict_qualifier  # type: ignore
    from proof_citations.proof_summary import ProofSummaryBuilder  # type: ignore


# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "Topaz et al. (2026) analyzed 2.5 million biomedical papers in PubMed "
    "Central from January 2023 through February 2026 and identified 4,046 "
    "references pointing to studies that do not exist, distributed across "
    "2,810 papers."
)

CLAIM_FORMAL = {
    "subject": "Topaz, Roguin, Gupta, Zhang, Peltonen — 'Fabricated citations: "
               "an audit across 2.5 million biomedical papers', Lancet 2026; "
               "407: 1779-81 (correspondence)",
    "purpose": "fact_verification",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "Corpus size ≈ 2.5 million biomedical papers in PubMed Central",
            "operator": "==",
            "threshold": True,
            "operator_note": (
                "Paper reports 2,471,758 papers scanned from PMC Open Access "
                "subset; this rounds to '2.5 million' as used in the paper's "
                "own title and the claim."
            ),
        },
        {
            "id": "SC2",
            "property": "Time window: January 2023 through February 2026",
            "operator": "==",
            "threshold": True,
            "operator_note": (
                "Paper specifies exactly Jan 1, 2023 to Feb 18, 2026. The "
                "claim's month-resolution phrasing 'January 2023 through "
                "February 2026' is a faithful summary of this interval."
            ),
        },
        {
            "id": "SC3",
            "property": "Number of fabricated references identified = 4,046",
            "operator": "==",
            "threshold": True,
            "operator_note": (
                "Paper's text says '4046 fabricated references'. The paper's "
                "supplementary appendix uses the more cautious term 'suspected "
                "fabricated references' and reports pipeline precision of 91% "
                "— see adversarial checks. The claim describes them as "
                "'references pointing to studies that do not exist', which "
                "matches the paper's own definition: 'references whose "
                "claimed titles correspond to no existing publication'."
            ),
        },
        {
            "id": "SC4",
            "property": "Number of distinct papers containing fabricated refs = 2,810",
            "operator": "==",
            "threshold": True,
            "operator_note": (
                "Paper states '4046 fabricated references across 2810 papers' "
                "and later 'Of the 2810 affected papers, 98·4% had received "
                "no publisher action'."
            ),
        },
    ],
    "compound_operator": "AND",
    "proof_direction": "affirm",
    "operator_note": (
        "All four sub-claims must hold for the compound claim to be PROVED. "
        "Each sub-claim is verified against verbatim text from the Topaz et "
        "al. 2026 correspondence article in The Lancet (the primary and only "
        "authoritative source for what that paper reports)."
    ),
    "subclaim_to_sources": {
        "SC1": ["sc1_corpus_size"],
        "SC2": ["sc2_date_range"],
        "SC3": ["sc3_fab_count"],
        "SC4": ["sc4_affected_papers"],
    },
}


# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "sc1_corpus_size",       "label": "SC1: corpus size from Topaz et al. 2026 methods"},
    "B2": {"key": "sc2_date_range",        "label": "SC2: date range from Topaz et al. 2026 methods"},
    "B3": {"key": "sc3_fab_count",         "label": "SC3: 4046 fabricated references (Topaz et al. 2026 results)"},
    "B4": {"key": "sc4_affected_papers",   "label": "SC4: 2810 affected papers (Topaz et al. 2026 limitations)"},
    "A1": {"label": "SC1 verified-source count", "method": None, "result": None},
    "A2": {"label": "SC2 verified-source count", "method": None, "result": None},
    "A3": {"label": "SC3 verified-source count", "method": None, "result": None},
    "A4": {"label": "SC4 verified-source count", "method": None, "result": None},
}


# 3. EMPIRICAL FACTS
# Source: the Topaz et al. 2026 Lancet correspondence (PIIS0140-6736(26)00603-3).
# The article is uploaded as a PDF; we rely on a verbatim text snapshot of the
# PDF (extracted with pypdf) as the citation-verification surface. The live URL
# on thelancet.com requires institutional access for the full text.

_PROOF_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_snapshot(fname):
    fpath = os.path.join(_PROOF_DIR, fname)
    try:
        with open(fpath) as f:
            return f.read()
    except FileNotFoundError:
        return None


_PAPER_SNAPSHOT = _load_snapshot("snapshots/topaz_paper.txt")
_PAPER_URL = (
    "https://www.thelancet.com/journals/lancet/article/"
    "PIIS0140-6736(26)00603-3/fulltext"
)
_SOURCE_NAME = (
    "Topaz M, Roguin N, Gupta P, Zhang Z, Peltonen L-M. Fabricated citations: "
    "an audit across 2·5 million biomedical papers. Lancet 2026; 407: 1779-81."
)

empirical_facts = {
    # SC1 — corpus size. Quote is the methods sentence reporting the corpus.
    "sc1_corpus_size": {
        "quote": (
            "We developed an automated reference verification system scanning "
            "PubMed Central's Open Access subset from Jan 1, 2023, to Feb 18, "
            "2026: 2 471 758 papers and 125 615 773 structured references."
        ),
        "url": _PAPER_URL,
        "source_name": _SOURCE_NAME,
        "snapshot": _PAPER_SNAPSHOT,
        "snapshot_source": "user_uploaded_pdf:pypdf_extract",
    },
    # SC2 — date range. Same methods sentence (Jan 1, 2023 to Feb 18, 2026).
    "sc2_date_range": {
        "quote": (
            "scanning PubMed Central's Open Access subset from Jan 1, 2023, "
            "to Feb 18, 2026"
        ),
        "url": _PAPER_URL,
        "source_name": _SOURCE_NAME,
        "snapshot": _PAPER_SNAPSHOT,
        "snapshot_source": "user_uploaded_pdf:pypdf_extract",
    },
    # SC3 — 4046 fabricated references. Results sentence.
    "sc3_fab_count": {
        "quote": (
            "Among 97·1 million verified references, we identified 4046 "
            "fabricated references across 2810 papers"
        ),
        "url": _PAPER_URL,
        "source_name": _SOURCE_NAME,
        "snapshot": _PAPER_SNAPSHOT,
        "snapshot_source": "user_uploaded_pdf:pypdf_extract",
    },
    # SC4 — 2810 affected papers. Limitations sentence that re-states the
    # affected-paper count gives independent textual confirmation within the
    # same article.
    "sc4_affected_papers": {
        "quote": (
            "Of the 2810 affected papers, 98·4% had received no publisher "
            "action at the time of our audit"
        ),
        "url": _PAPER_URL,
        "source_name": _SOURCE_NAME,
        "snapshot": _PAPER_SNAPSHOT,
        "snapshot_source": "user_uploaded_pdf:pypdf_extract",
    },
}


# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=False)


# 5. PER-SUB-CLAIM VERIFICATION COUNTS
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = ["sc1_corpus_size"]
sc2_keys = ["sc2_date_range"]
sc3_keys = ["sc3_fab_count"]
sc4_keys = ["sc4_affected_papers"]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc3 = sum(1 for k in sc3_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc4 = sum(1 for k in sc4_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)


# 6. PER-SUB-CLAIM EVALUATION
sc1_holds = compare(n_sc1, ">=", 1, label="SC1: corpus size ≈ 2.5M papers in PMC")
sc2_holds = compare(n_sc2, ">=", 1, label="SC2: date range Jan 2023 - Feb 2026")
sc3_holds = compare(n_sc3, ">=", 1, label="SC3: 4046 fabricated references")
sc4_holds = compare(n_sc4, ">=", 1, label="SC4: 2810 affected papers")


# 7. COMPOUND EVALUATION
n_holding = sum([sc1_holds, sc2_holds, sc3_holds, sc4_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")


# 8. COI FLAGS (per sub-claim)
# All four sub-claims share a single source: the Topaz paper itself. Since the
# CLAIM under verification is "what does the Topaz paper REPORT," self-reporting
# by the paper IS the appropriate evidence — this is by design of the claim,
# not a COI on the proof. (A COI gate is for the proof's reasoning; we are not
# evaluating ground-truth fabrication counts, only whether the paper states
# those counts.)
sc1_coi_flags = []
sc2_coi_flags = []
sc3_coi_flags = []
sc4_coi_flags = []


# 9. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Does the paper itself use weaker language than 'studies "
                    "that do not exist' for these 4,046 references?",
        "verification_performed": (
            "Searched the supplementary appendix (uploaded mmc1.pdf) for the "
            "exact language used to describe the 4,046 entries. The main "
            "Lancet correspondence uses 'fabricated references' (defined as "
            "'references whose claimed titles correspond to no existing "
            "publication'). The supplementary appendix consistently uses "
            "'suspected fabricated references' and reports pipeline precision "
            "of 91% (Fleiss' kappa = 0.71) on a 500-entry masked validation. "
            "This means roughly 9% of the 4,046 entries may be false positives."
        ),
        "finding": (
            "The user's phrasing 'references pointing to studies that do not "
            "exist' tracks the paper's own definition and headline term. "
            "However, the rigorous statement is that the pipeline FLAGGED "
            "4,046 entries as suspected fabrications with 91% precision, so "
            "the true number of references-to-nothing is approximately "
            "4046 * 0.91 ≈ 3682, not exactly 4,046. The claim under "
            "verification is about what the paper REPORTS, and the paper "
            "reports the figure 4,046 explicitly. No precision adjustment is "
            "applied to the headline number in the paper's own text."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Are there any independent retractions, corrections, or "
                    "rebuttals of the Topaz et al. 2026 finding that would "
                    "change the headline numbers?",
        "verification_performed": (
            "The paper was published as a Lancet correspondence on May 9, "
            "2026 (vol 407, pp 1779-1781); today's date is May 20, 2026. "
            "Eleven days post-publication leaves essentially no time for a "
            "formal retraction or correction to appear. No such notice is "
            "attached to the uploaded PDF. The user-supplied PDF and "
            "supplement are the canonical source for what the paper reports."
        ),
        "finding": (
            "No retractions, corrections, or errata are known for the source "
            "paper at the time of this proof. The headline figures (2.5M / "
            "Jan 2023 - Feb 2026 / 4,046 / 2,810) appear unchanged."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the date phrasing 'January 2023 through February "
                    "2026' overstate the actual interval?",
        "verification_performed": (
            "Compared the claim's interval ('January 2023 through February "
            "2026') against the paper's exact interval ('Jan 1, 2023, to "
            "Feb 18, 2026'). The claim describes both bounds at month "
            "resolution; the paper specifies day-of-month bounds within "
            "those months. The paper also notes the early-2026 quarter is "
            "incomplete (Jan 1 - Feb 18 represents the first 7 weeks of "
            "2026)."
        ),
        "finding": (
            "The claim's month-level phrasing is consistent with the paper. "
            "It does not imply analysis through Feb 28, 2026; saying 'through "
            "February 2026' to describe a period ending Feb 18, 2026 is a "
            "common and accurate summary. No overstatement."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is the corpus-size figure '2.5 million' a fair "
                    "rounding of the paper's actual 2,471,758?",
        "verification_performed": (
            "2,471,758 rounded to one significant figure beyond 'millions' "
            "gives 2.5 million (since 2.47 rounds up to 2.5 at 2 sig figs). "
            "The paper itself uses '2·5 million' in its title and in the "
            "supplementary appendix subtitle. The user's claim adopts the "
            "paper's own rounding."
        ),
        "finding": (
            "'2.5 million' is the paper's own headline rounding. Match is "
            "exact."
        ),
        "breaks_proof": False,
    },
]


# 10. VERDICT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"

    # COI gates — none active for this proof; all sub-claims confirmed by the
    # paper itself, which is the correct evidence for "what the paper reports."
    any_coi_override = False

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif any_coi_override:
        base_verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        base_verdict = "PARTIALLY VERIFIED"
    elif claim_holds:
        base_verdict = "DISPROVED" if is_disproof else "PROVED"
    elif not claim_holds and n_holding == 0:
        base_verdict = "UNDETERMINED"
    else:
        base_verdict = "UNDETERMINED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    sc_keys_map = {"SC1": sc1_keys, "SC2": sc2_keys, "SC3": sc3_keys, "SC4": sc4_keys}

    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        ef = empirical_facts[ef_key]
        cr = citation_results.get(ef_key, {})
        sub_claim = None
        for sc, keys in sc_keys_map.items():
            if ef_key in keys:
                sub_claim = sc
                break
        builder.add_empirical_fact(
            fid,
            label=info["label"],
            source_name=ef["source_name"],
            source_url=ef["url"],
            source_quote=ef["quote"],
            sub_claim=sub_claim,
        )
        builder.set_verification(
            fid,
            status=cr.get("status", "unknown"),
            method=cr.get("method", "full_quote"),
            coverage_pct=cr.get("coverage_pct"),
            fetch_mode=cr.get("fetch_mode", "snapshot"),
            credibility=cr.get("credibility", {}),
        )
        builder.set_extraction(
            fid,
            value=cr.get("status", "unknown"),
            value_in_quote=cr.get("status") in COUNTABLE_STATUSES,
            quote_snippet=ef["quote"][:80],
        )

    fact_ids_by_sc = {
        sc: [fid for fid, info in FACT_REGISTRY.items()
             if fid.startswith("B") and info["key"] in keys]
        for sc, keys in sc_keys_map.items()
    }

    n_by_sc = {"SC1": n_sc1, "SC2": n_sc2, "SC3": n_sc3, "SC4": n_sc4}
    holds_by_sc = {"SC1": sc1_holds, "SC2": sc2_holds, "SC3": sc3_holds, "SC4": sc4_holds}

    for i, sc in enumerate(["SC1", "SC2", "SC3", "SC4"], start=1):
        builder.add_computed_fact(
            f"A{i}",
            label=f"{sc} verified-source count",
            method=f"count(verified {sc.lower()} citations) = {n_by_sc[sc]}",
            result=n_by_sc[sc],
            depends_on=fact_ids_by_sc[sc],
            sub_claim=sc,
        )
        builder.add_cross_check(
            description=f"{sc}: in-source quote verification",
            fact_ids=fact_ids_by_sc[sc],
            n_sources_consulted=len(sc_keys_map[sc]),
            n_sources_verified=n_by_sc[sc],
            sources={k: citation_results[k]["status"] for k in sc_keys_map[sc]},
            independence_note=(
                "Single authoritative source (Topaz et al. 2026) — claim is "
                "about what that paper reports."
            ),
            coi_flags=[],
            agreement=holds_by_sc[sc],
        )
        builder.add_sub_claim_result(
            id=sc,
            n_confirming=n_by_sc[sc],
            threshold=1,
            holds=holds_by_sc[sc],
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
        n_holding=n_holding,
        n_total=n_total,
        claim_holds=claim_holds,
    )
    builder.emit()
