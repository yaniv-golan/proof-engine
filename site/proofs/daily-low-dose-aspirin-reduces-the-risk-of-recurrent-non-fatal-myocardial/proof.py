"""
Proof: "Daily low-dose aspirin reduces the risk of recurrent non-fatal
myocardial infarction in patients with prior cardiovascular disease, per the
Antithrombotic Trialists' Collaboration meta-analysis."

Claim type: compound / causal. The claim uses causal language ("reduces the
risk"), so per the Proof Engine causal rule it is decomposed into an
association sub-claim (SC1) and a causation sub-claim (SC2).

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
        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "Daily low-dose aspirin reduces the risk of recurrent non-fatal myocardial "
    "infarction in patients with prior cardiovascular disease, per the "
    "Antithrombotic Trialists' Collaboration meta-analysis."
)

CLAIM_FORMAL = {
    "subject": (
        "Daily low-dose aspirin and recurrent non-fatal myocardial infarction in "
        "patients with prior cardiovascular disease, as assessed by the "
        "Antithrombotic Trialists' (ATT) Collaboration meta-analyses"
    ),
    "is_time_sensitive": False,
    "sub_claims": [
        {
            "id": "SC1",
            "property": (
                "The ATT Collaboration meta-analysis found daily low-dose aspirin "
                "associated with a reduction in non-fatal myocardial infarction "
                "among patients with prior cardiovascular disease"
            ),
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC1 (association) holds when at least 2 verified quotations from "
                "the ATT meta-analysis publications report that low-dose aspirin / "
                "antiplatelet therapy is associated with a reduction in non-fatal "
                "myocardial infarction (or the coronary-event composite that "
                "includes non-fatal MI) among patients with prior cardiovascular "
                "disease."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "The ATT Collaboration meta-analysis pools randomized controlled "
                "trials, giving the observed reduction a causal (not merely "
                "associational) basis"
            ),
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC2 (causation) holds when at least 2 verified quotations "
                "establish that the ATT meta-analysis pools randomized controlled "
                "trials. Random allocation removes confounding, so a reduction "
                "observed consistently across pooled RCTs supports a causal "
                "interpretation -- this meets the Proof Engine's gold-standard "
                "criterion for SC-causation (RCTs / controlled experiments)."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "The claim uses causal language ('reduces the risk'), so it is decomposed "
        "into an association sub-claim (SC1) and a causation sub-claim (SC2); both "
        "must hold for a PROVED verdict (compound_operator AND). The claim is "
        "explicitly attributed to 'the Antithrombotic Trialists' Collaboration "
        "meta-analysis', so the proof evaluates it against the ATT Collaboration's "
        "own publications: the 2002 BMJ collaborative overview of antiplatelet "
        "therapy in high-risk patients and the 2009 Lancet individual-participant-"
        "data meta-analysis of aspirin in primary and secondary prevention. "
        "'Patients with prior cardiovascular disease' is interpreted as the "
        "secondary-prevention / high-risk population the ATT analyses studied "
        "(acute or previous occlusive vascular disease). 'Recurrent non-fatal "
        "myocardial infarction' is interpreted as non-fatal MI events occurring "
        "within that established-disease population; the ATT analyses include an "
        "explicit 'previous myocardial infarction' patient category in which any "
        "subsequent non-fatal MI is unambiguously recurrent. 'Low-dose aspirin' is "
        "interpreted as the 75-150 mg/day range the ATT 2002 analysis found 'at "
        "least as effective as higher daily doses'. Source-count thresholds are "
        "set to 2 (not the default 3): by construction the claim restricts the "
        "evidence base to one named source program (the ATT Collaboration "
        "meta-analysis), which produced exactly two landmark meta-analyses on this "
        "question -- both peer-reviewed in top-tier journals (BMJ, Lancet), each "
        "pooling large randomized-trial datasets, and funded by public/charitable "
        "bodies (UK Medical Research Council, British Heart Foundation, Cancer "
        "Research UK, EC Biomed) with no aspirin-manufacturer funding. No conflict "
        "of interest favoring the claim was identified."
    ),
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY  (report IDs -> proof-script keys)
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {"key": "sc1_att2002_mi",
           "label": "SC1 - ATT 2002 BMJ: non-fatal MI reduced by one third in high-risk patients"},
    "B2": {"key": "sc1_att2002_dose",
           "label": "SC1 - ATT 2002 BMJ: low-dose aspirin (75-150 mg) at least as effective as higher doses"},
    "B3": {"key": "sc1_att2009",
           "label": "SC1 - ATT 2009 Lancet: aspirin reduces serious vascular events in secondary-prevention trials"},
    "B4": {"key": "sc2_att2002",
           "label": "SC2 - ATT 2002 BMJ: inclusion restricted to randomised trials"},
    "B5": {"key": "sc2_att2009",
           "label": "SC2 - ATT 2009 Lancet: meta-analysis of individual participant data from randomised trials"},
    "A1": {"label": "SC1 verified source count", "method": None, "result": None},
    "A2": {"label": "SC2 verified source count", "method": None, "result": None},
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS  (grouped by sub-claim via the sc1_ / sc2_ key prefix)
# ---------------------------------------------------------------------------
_PMC_2002 = "https://pmc.ncbi.nlm.nih.gov/articles/PMC64503/"
_PUBMED_2009 = "https://pubmed.ncbi.nlm.nih.gov/19482214/"

_SRC_2002 = ("Antithrombotic Trialists' Collaboration. Collaborative meta-analysis of "
             "randomised trials of antiplatelet therapy for prevention of death, "
             "myocardial infarction, and stroke in high risk patients. BMJ "
             "2002;324:71-86 (full text via PubMed Central, PMC64503).")
_SRC_2009 = ("Antithrombotic Trialists' (ATT) Collaboration. Aspirin in the primary and "
             "secondary prevention of vascular disease: collaborative meta-analysis of "
             "individual participant data from randomised trials. Lancet "
             "2009;373:1849-60 (abstract via PubMed, PMID 19482214).")

# Snapshot fallback (Rule 2). PubMed Central and PubMed periodically block or
# throttle automated fetches, so each citation carries an offline snapshot of
# the page captured on 2026-05-20. The verifier uses the fallback chain
# live -> snapshot -> Wayback, so a transient live-fetch failure cannot change
# the verdict. The snapshots are public-domain government pages, stored as
# separate files to keep this script readable.
_PROOF_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_snapshot(fname):
    fpath = os.path.join(_PROOF_DIR, fname)
    try:
        with open(fpath, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


_SNAPSHOT_2002 = _load_snapshot("snapshots/pmc64503.html")
_SNAPSHOT_2009 = _load_snapshot("snapshots/pubmed19482214.html")
_SNAPSHOT_DATE = "2026-05-20"

empirical_facts = {
    # ---- SC1: association (aspirin reduces non-fatal MI in prior-CVD patients) ----
    "sc1_att2002_mi": {
        "quote": (
            "Overall, among these high risk patients, allocation to antiplatelet "
            "therapy reduced the combined outcome of any serious vascular event by "
            "about one quarter; non-fatal myocardial infarction was reduced by one "
            "third, non-fatal stroke by one quarter, and vascular mortality by one "
            "sixth"
        ),
        "url": _PMC_2002,
        "source_name": _SRC_2002,
        "snapshot": _SNAPSHOT_2002,
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": _SNAPSHOT_DATE,
    },
    "sc1_att2002_dose": {
        "quote": (
            "Aspirin was the most widely studied antiplatelet drug, with doses of "
            "75-150 mg daily at least as effective as higher daily doses."
        ),
        "url": _PMC_2002,
        "source_name": _SRC_2002,
        "snapshot": _SNAPSHOT_2002,
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": _SNAPSHOT_DATE,
    },
    "sc1_att2009": {
        "quote": (
            "In the secondary prevention trials, aspirin allocation yielded a "
            "greater absolute reduction in serious vascular events"
        ),
        "url": _PUBMED_2009,
        "source_name": _SRC_2009,
        "snapshot": _SNAPSHOT_2009,
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": _SNAPSHOT_DATE,
    },
    # ---- SC2: causation (the meta-analysis pools randomised controlled trials) ----
    "sc2_att2002": {
        "quote": (
            "Randomised trials of an antiplatelet regimen versus control or of one "
            "antiplatelet regimen versus another in high risk patients"
        ),
        "url": _PMC_2002,
        "source_name": _SRC_2002,
        "snapshot": _SNAPSHOT_2002,
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": _SNAPSHOT_DATE,
    },
    "sc2_att2009": {
        "quote": (
            "collaborative meta-analysis of individual participant data from "
            "randomised trials"
        ),
        "url": _PUBMED_2009,
        "source_name": _SRC_2009,
        "snapshot": _SNAPSHOT_2009,
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": _SNAPSHOT_DATE,
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

# ---------------------------------------------------------------------------
# 6. PER-SUB-CLAIM EVALUATION (Rule 7 - compare(), no eval())
# ---------------------------------------------------------------------------
sc1_holds = compare(n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
                    label="SC1 (association): verified ATT sources")
sc2_holds = compare(n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
                    label="SC2 (causation): verified ATT sources")

# ---------------------------------------------------------------------------
# 7. COMPOUND EVALUATION
# ---------------------------------------------------------------------------
n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# ---------------------------------------------------------------------------
# 8. COI FLAGS (Rule 6) - per sub-claim
# ---------------------------------------------------------------------------
# The ATT Collaboration is an independent academic consortium funded by the UK
# Medical Research Council, British Heart Foundation, Cancer Research UK and the
# EC Biomed Programme -- no aspirin-manufacturer funding. Its 2009 Lancet paper
# concluded that aspirin is "of uncertain net value" in primary prevention,
# demonstrating willingness to report null/negative findings. No conflict of
# interest favoring the claim was identified for either sub-claim.
sc1_coi_flags = []
sc2_coi_flags = []

# ---------------------------------------------------------------------------
# 9. ADVERSARIAL CHECKS (Rule 5) - counter-evidence searched during research
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": ("Does the ATT meta-analysis actually report a reduction in "
                     "non-fatal myocardial infarction, or is the attribution wrong?"),
        "verification_performed": (
            "Fetched and read the ATT 2002 BMJ meta-analysis (PMC64503) and the "
            "ATT 2009 Lancet meta-analysis abstract (PubMed 19482214); searched for "
            "the verbatim findings on non-fatal MI and secondary prevention."
        ),
        "finding": (
            "The attribution is accurate. The 2002 BMJ ATT meta-analysis explicitly "
            "states that, among high-risk patients, 'non-fatal myocardial infarction "
            "was reduced by one third'. The 2009 Lancet ATT meta-analysis reports "
            "that in secondary-prevention trials aspirin reduced serious vascular "
            "events and coronary events. No mismatch between the claim and the named "
            "source was found."
        ),
        "breaks_proof": False,
    },
    {
        "question": ("Does the bleeding harm of aspirin negate or contradict the "
                     "reduction in non-fatal MI?"),
        "verification_performed": (
            "Searched for counter-evidence on aspirin's bleeding harms and net "
            "benefit in secondary prevention (gastrointestinal / extracranial "
            "bleeding meta-analyses)."
        ),
        "finding": (
            "Aspirin does increase major extracranial and gastrointestinal bleeding "
            "-- a well-documented, separate harm. This does not contradict the "
            "claim, which concerns the non-fatal-MI outcome specifically, not net "
            "clinical benefit. The ATT 2002 paper itself reports that in the "
            "high-risk categories 'the absolute benefits substantially outweighed "
            "the absolute risks of major extracranial bleeding'. Bleeding is a "
            "treatment trade-off, not evidence against the MI-reduction finding, so "
            "it does not break the proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": ("Is the secondary-prevention benefit of aspirin contradicted by "
                     "more recent evidence from the modern statin / revascularization "
                     "era?"),
        "verification_performed": (
            "Searched 2020-2025 reviews and meta-analyses that question aspirin in "
            "secondary prevention, including recent commentary and a 2025 systematic "
            "review/meta-analysis of aspirin for secondary prevention of MI."
        ),
        "finding": (
            "Recent commentary debates whether aspirin's marginal benefit is as "
            "large in the modern treatment era and notes P2Y12 inhibitors as "
            "alternatives. However, a 2025 systematic review/meta-analysis still "
            "found aspirin reduced recurrent events by roughly a fifth in secondary "
            "prevention, and no source claims the ATT finding of reduced non-fatal "
            "MI was wrong or reversed. The direction of effect is confirmed by "
            "modern evidence; only the magnitude and its role relative to newer "
            "therapies are debated. This does not break a proof scoped to the ATT "
            "meta-analysis finding."
        ),
        "breaks_proof": False,
    },
    {
        "question": ("Does 'low-dose' aspirin specifically -- not antiplatelet "
                     "therapy in general -- carry the non-fatal MI reduction?"),
        "verification_performed": (
            "Checked the ATT 2002 BMJ dose analysis and the scope of the 2009 "
            "Lancet meta-analysis."
        ),
        "finding": (
            "Supported. The ATT 2002 meta-analysis found 'doses of 75-150 mg daily "
            "at least as effective as higher daily doses' and identified aspirin as "
            "'the most widely studied antiplatelet drug'; the 2009 ATT meta-analysis "
            "is explicitly an analysis of 'low-dose aspirin'. The 2002 paper notes "
            "the effects of doses below 75 mg are 'less certain', but standard "
            "low-dose aspirin (75-150 mg) is squarely within the supported range, "
            "so this does not break the proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": ("Could 'recurrent' non-fatal MI be unsupported because the ATT "
                     "meta-analysis pooled mixed prior-CVD populations rather than "
                     "only prior-MI patients?"),
        "verification_performed": (
            "Reviewed the ATT meta-analysis patient categories in the 2002 BMJ and "
            "2009 Lancet reports."
        ),
        "finding": (
            "The ATT meta-analysis explicitly includes a 'previous myocardial "
            "infarction' patient category among its high-risk groups (six "
            "secondary-prevention prior-MI trials in the 2009 analysis), in which a "
            "subsequent non-fatal MI is by definition recurrent. The proof "
            "interprets 'recurrent non-fatal MI in patients with prior CVD' as "
            "non-fatal MI events within the established-CVD secondary-prevention "
            "population the ATT analysed -- an interpretation documented in the "
            "operator_note that does not overstate the source -- so this does not "
            "break the proof."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 10. VERDICT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"

    # Per-sub-claim COI gate (Rule 6)
    sc1_confirmed_keys = {k for k in sc1_keys
                          if citation_results[k]["status"] in COUNTABLE_STATUSES}
    sc1_coi_favorable = {f["source_key"] for f in sc1_coi_flags
                         if f["direction"] == "favorable_to_subject"
                         and f["source_key"] in sc1_confirmed_keys}
    sc1_coi_unfavorable = {f["source_key"] for f in sc1_coi_flags
                           if f["direction"] == "unfavorable_to_subject"
                           and f["source_key"] in sc1_confirmed_keys}
    sc1_coi_majority = max(len(sc1_coi_favorable), len(sc1_coi_unfavorable)) if sc1_coi_flags else 0
    sc1_threshold = CLAIM_FORMAL["sub_claims"][0]["threshold"]
    sc1_coi_override = n_sc1 >= sc1_threshold and sc1_coi_majority > n_sc1 / 2

    sc2_confirmed_keys = {k for k in sc2_keys
                          if citation_results[k]["status"] in COUNTABLE_STATUSES}
    sc2_coi_favorable = {f["source_key"] for f in sc2_coi_flags
                         if f["direction"] == "favorable_to_subject"
                         and f["source_key"] in sc2_confirmed_keys}
    sc2_coi_unfavorable = {f["source_key"] for f in sc2_coi_flags
                           if f["direction"] == "unfavorable_to_subject"
                           and f["source_key"] in sc2_confirmed_keys}
    sc2_coi_majority = max(len(sc2_coi_favorable), len(sc2_coi_unfavorable)) if sc2_coi_flags else 0
    sc2_threshold = CLAIM_FORMAL["sub_claims"][1]["threshold"]
    sc2_coi_override = n_sc2 >= sc2_threshold and sc2_coi_majority > n_sc2 / 2

    any_coi_override = sc1_coi_override or sc2_coi_override

    # This is a causal-decomposition compound claim, not a contested-qualifier
    # claim, so the contested-qualifier branch must not fire.
    is_contested_qualifier = "qualifier" in CLAIM_FORMAL.get("operator_note", "").lower()

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif any_coi_override:
        base_verdict = "UNDETERMINED"
    elif is_contested_qualifier and sc1_holds and not sc2_holds:
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

    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        ef = empirical_facts[ef_key]
        cr = citation_results.get(ef_key, {})
        sub_claim = "SC1" if ef_key in sc1_keys else "SC2"
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
            fetch_mode=cr.get("fetch_mode", "live"),
            credibility=cr.get("credibility", {}),
        )
        builder.set_extraction(
            fid,
            value=cr.get("status", "unknown"),
            value_in_quote=cr.get("status") in COUNTABLE_STATUSES,
            quote_snippet=ef["quote"][:80],
        )

    sc1_fact_ids = [fid for fid, info in FACT_REGISTRY.items()
                    if fid.startswith("B") and info["key"] in sc1_keys]
    sc2_fact_ids = [fid for fid, info in FACT_REGISTRY.items()
                    if fid.startswith("B") and info["key"] in sc2_keys]

    builder.add_computed_fact(
        "A1",
        label="SC1 verified source count",
        method=f"count(verified sc1 citations) = {n_sc1}",
        result=n_sc1,
        depends_on=sc1_fact_ids,
        sub_claim="SC1",
    )
    builder.add_computed_fact(
        "A2",
        label="SC2 verified source count",
        method=f"count(verified sc2 citations) = {n_sc2}",
        result=n_sc2,
        depends_on=sc2_fact_ids,
        sub_claim="SC2",
    )

    builder.add_cross_check(
        description="SC1: independent ATT meta-analysis publications consulted",
        fact_ids=sc1_fact_ids,
        n_sources_consulted=len(sc1_keys),
        n_sources_verified=n_sc1,
        sources={k: citation_results[k]["status"] for k in sc1_keys},
        independence_note=(
            "SC1 draws on two distinct ATT meta-analyses published seven years "
            "apart in different journals (BMJ 2002, Lancet 2009) using different "
            "methods (tabular data vs individual participant data) and overlapping "
            "but non-identical trial sets. B1 and B2 are two distinct findings "
            "(the non-fatal-MI reduction and the low-dose equivalence) from the "
            "2002 BMJ paper; B3 is from the independent 2009 Lancet meta-analysis."
        ),
        coi_flags=sc1_coi_flags,
        agreement=sc1_holds,
    )
    builder.add_cross_check(
        description="SC2: independent ATT meta-analysis publications consulted",
        fact_ids=sc2_fact_ids,
        n_sources_consulted=len(sc2_keys),
        n_sources_verified=n_sc2,
        sources={k: citation_results[k]["status"] for k in sc2_keys},
        independence_note=(
            "SC2 is confirmed by both ATT publications independently: the 2002 BMJ "
            "paper restricts inclusion to 'Randomised trials', and the 2009 Lancet "
            "paper is a 'collaborative meta-analysis of individual participant data "
            "from randomised trials'. Two separate publications each document the "
            "randomized-controlled-trial basis."
        ),
        coi_flags=sc2_coi_flags,
        agreement=sc2_holds,
    )

    builder.add_sub_claim_result(
        id="SC1", n_confirming=n_sc1,
        threshold=CLAIM_FORMAL["sub_claims"][0]["threshold"], holds=sc1_holds,
    )
    builder.add_sub_claim_result(
        id="SC2", n_confirming=n_sc2,
        threshold=CLAIM_FORMAL["sub_claims"][1]["threshold"], holds=sc2_holds,
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
        sc1_verified_sources=n_sc1,
        sc2_verified_sources=n_sc2,
    )

    print("=" * 70)
    print("PROOF: Daily low-dose aspirin and recurrent non-fatal MI (ATT)")
    print("=" * 70)
    print(f"SC1 (association) verified ATT sources: {n_sc1} "
          f"(threshold {CLAIM_FORMAL['sub_claims'][0]['threshold']}) -> holds={sc1_holds}")
    print(f"SC2 (causation)   verified ATT sources: {n_sc2} "
          f"(threshold {CLAIM_FORMAL['sub_claims'][1]['threshold']}) -> holds={sc2_holds}")
    print(f"Sub-claims holding: {n_holding}/{n_total}")
    print(f"Adversarial checks that break the proof: "
          f"{sum(1 for ac in adversarial_checks if ac['breaks_proof'])}")
    print(f"\nVERDICT: {verdict}")
    print("=" * 70)

    builder.emit()
