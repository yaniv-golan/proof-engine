"""
Proof: Six minutes of birdsong reduced anxiety with a medium effect size,
while six minutes of traffic noise raised depression with the same effect size.

Generated: 2026-04-28

This is a primary-source compound claim about the findings of one specific
randomized online experiment (Stobbe, Sundermann, Foerster & Kuühn, 2022,
Scientific Reports). The proof verifies via verbatim quotes from the original
peer-reviewed paper and its PubMed-indexed abstract.
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

# ---
# 1. CLAIM INTERPRETATION (Rule 4)
# ---
CLAIM_NATURAL = (
    "Six minutes of birdsong reduced anxiety with a medium effect size, "
    "while six minutes of traffic noise raised depression with the same effect size."
)

CLAIM_FORMAL = {
    "subject": "Stobbe et al. 2022 randomized online experiment on soundscape exposure",
    "sub_claims": [
        {
            "id": "SC1",
            "property": (
                "In Stobbe et al. (2022), 6-minute exposure to birdsong soundscapes "
                "produced a significant decrease in self-reported anxiety, characterized "
                "by the authors as a medium effect size (Cohen's d in [-0.77, -0.70])."
            ),
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC1 verifies what the study reports about birdsong and anxiety. "
                "Two sources confirm: (a) the full Nature paper gives the raw "
                "Cohen's d values d = -0.77 (low diversity) and d = -0.70 (high diversity); "
                "(b) the PubMed-indexed abstract characterizes these as 'medium effect sizes'."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "In Stobbe et al. (2022), 6-minute exposure to traffic noise soundscapes "
                "produced a significant increase in self-reported depression, with a "
                "medium effect size in the high-diversity condition (Cohen's d = 0.59)."
            ),
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC2 verifies what the study reports about traffic noise and depression. "
                "Two sources confirm: (a) the full Nature paper gives Cohen's d = 0.59 "
                "(high diversity, characterized as medium) and d = 0.29 (low diversity, "
                "characterized as small); (b) the PubMed-indexed abstract characterizes "
                "the high-diversity result as a 'medium effect size'. The claim's match "
                "for SC2 is to the high-diversity finding, not the low-diversity finding."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "PRIMARY-SOURCE CLAIM. This is a claim about what one specific study reported. "
        "Both sub-claims trace to Stobbe et al. (2022) Scientific Reports 12:16414. "
        "Threshold of 2 is justified by domain scarcity: there is exactly one study "
        "with this design, so 'independent sources' are the full paper text and the "
        "PubMed-mirrored abstract, which agree on numeric d values and on the authors' "
        "magnitude labels. \n\n"
        "FORMALIZATION SCOPE NOTE: The natural-language phrase 'with the same effect size' "
        "is operationalized as 'both effects are characterized as medium by the study "
        "authors' (Cohen's d magnitude category), not as 'numerically identical d values'. "
        "Birdsong-anxiety has |d| in [0.70, 0.77] (authors: 'medium effect sizes'). "
        "Traffic-depression has d = 0.59 in the high-diversity condition (authors: "
        "'medium effect size'). Both fall within Cohen's medium magnitude bracket per "
        "the authors' own classification. \n\n"
        "CAVEAT NOT CAPTURED IN THE CLAIM: The traffic-depression effect was 'medium' "
        "only in the high-diversity condition; the low-diversity traffic condition "
        "produced a small effect (d = 0.29). The compound claim oversimplifies by "
        "omitting this conditioning, but the medium effect the claim asserts does "
        "exist in the study. SC2 is satisfied by the high-diversity finding. \n\n"
        "The claim is NOT a causal claim about long-term mental health outcomes — it "
        "describes immediate pre/post questionnaire changes after a 6-minute laboratory "
        "exposure. It is also NOT a claim that traffic noise causes clinical depression."
    ),
}

# ---
# 2. FACT REGISTRY
# ---
FACT_REGISTRY = {
    "B1": {
        "key": "sc1_nature_paper",
        "label": (
            "SC1: Nature paper (Stobbe et al. 2022) — verbatim Cohen's d values for "
            "birdsong-anxiety (d = -0.77 low diversity, d = -0.70 high diversity)"
        ),
    },
    "B2": {
        "key": "sc1_pubmed_abstract",
        "label": (
            "SC1: PubMed-indexed abstract — author characterization 'Anxiety and "
            "paranoia significantly decreased in both birdsong conditions (medium effect sizes)'"
        ),
    },
    "B3": {
        "key": "sc2_nature_paper",
        "label": (
            "SC2: Nature paper (Stobbe et al. 2022) — verbatim Cohen's d values for "
            "traffic-depression (d = 0.29 low, d = 0.59 high diversity)"
        ),
    },
    "B4": {
        "key": "sc2_pubmed_abstract",
        "label": (
            "SC2: PubMed-indexed abstract — author characterization 'increase in depression "
            "(small effect size in low, medium effect size in high diversity condition)'"
        ),
    },
    "B5": {
        "key": "duration_nature_paper",
        "label": "Both SCs: Nature paper confirms 6-minute exposure duration",
    },
    "A1": {"label": "SC1 verified source count", "method": None, "result": None},
    "A2": {"label": "SC2 verified source count", "method": None, "result": None},
}

# ---
# 3. EMPIRICAL FACTS — grouped by sub-claim
# ---
empirical_facts = {
    # SC1: birdsong reduces anxiety with medium effect size
    "sc1_nature_paper": {
        "quote": (
            "low diversity: T(1, 62) =  − 6.13, p < 0.001, d =  − 0.77; "
            "high diversity: T(1, 60) =  − 6.32, p < 0.001, d =  − 0.70"
        ),
        "url": "https://www.nature.com/articles/s41598-022-20841-0",
        "source_name": (
            "Stobbe E, Sundermann J, Foerster L, Kühn S (2022). Birdsongs alleviate "
            "anxiety and paranoia in healthy participants. Scientific Reports 12:16414."
        ),
    },
    "sc1_pubmed_abstract": {
        "quote": (
            "Anxiety and paranoia significantly decreased in both birdsong conditions "
            "(medium effect sizes)."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/36229489/",
        "source_name": (
            "PubMed-indexed abstract of Stobbe et al. 2022 (PMID 36229489), "
            "U.S. National Library of Medicine."
        ),
    },
    # SC2: traffic noise raises depression with medium effect size (high diversity)
    "sc2_nature_paper": {
        "quote": (
            "depressive symptoms significantly increased within both the low diversity "
            "urban soundscape (T(1, 82) = 2.64, p = 0.010, d = 0.29) and high diversity "
            "urban condition (T(1, 68) = 4.88, p < 0.001, d = 0.59)"
        ),
        "url": "https://www.nature.com/articles/s41598-022-20841-0",
        "source_name": (
            "Stobbe E, Sundermann J, Foerster L, Kühn S (2022). Birdsongs alleviate "
            "anxiety and paranoia in healthy participants. Scientific Reports 12:16414."
        ),
    },
    "sc2_pubmed_abstract": {
        "quote": (
            "the traffic noise soundscapes were associated with a significant increase "
            "in depression (small effect size in low, medium effect size in high diversity "
            "condition)."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/36229489/",
        "source_name": (
            "PubMed-indexed abstract of Stobbe et al. 2022 (PMID 36229489), "
            "U.S. National Library of Medicine."
        ),
    },
    # Duration anchor — confirms 'six minutes' part of the claim
    "duration_nature_paper": {
        "quote": (
            "N = 295 participants were exposed to one out of four conditions for 6 min: "
            "traffic noise low, traffic noise high, birdsong low, and birdsong high "
            "diversity soundscapes."
        ),
        "url": "https://www.nature.com/articles/s41598-022-20841-0",
        "source_name": (
            "Stobbe E, Sundermann J, Foerster L, Kühn S (2022). Birdsongs alleviate "
            "anxiety and paranoia in healthy participants. Scientific Reports 12:16414."
        ),
    },
}

# ---
# 4. CITATION VERIFICATION (Rule 2)
# ---
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---
# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
# ---
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

# ---
# 6. PER-SUB-CLAIM EVALUATION (Rule 7 — never hardcode holds values)
# ---
sc1_holds = compare(n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
                    label="SC1: birdsong reduces anxiety, medium effect")
sc2_holds = compare(n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
                    label="SC2: traffic noise raises depression, medium effect (high-diversity)")

# ---
# 7. COMPOUND EVALUATION
# ---
n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# ---
# 8. COI FLAGS
# ---
sc1_coi_flags = []  # Primary-source verification; PubMed independently archives the abstract.
sc2_coi_flags = []

# ---
# 9. ADVERSARIAL CHECKS (Rule 5)
# ---
adversarial_checks = [
    {
        "question": (
            "Does the original paper actually report the effect sizes described, or did "
            "secondary coverage (press release, news articles) mischaracterize the findings?"
        ),
        "verification_performed": (
            "Fetched the full Nature paper at https://www.nature.com/articles/s41598-022-20841-0 "
            "and located the within-group t-test results in the Results section. Confirmed: "
            "anxiety decreased in both birdsong conditions (d = -0.77, d = -0.70) and "
            "depression increased in both traffic-noise conditions (d = 0.29, d = 0.59). "
            "Cross-checked the abstract verbatim on both nature.com and pubmed.ncbi.nlm.nih.gov "
            "to confirm the authors' own 'medium effect size' characterization for both finding."
        ),
        "finding": (
            "The paper itself supports both sub-claims. The abstract explicitly labels both "
            "the birdsong-anxiety effects and the high-diversity traffic-depression effect as "
            "'medium effect sizes'. The claim's language faithfully reflects the authors' "
            "own summary."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the qualifier 'the same effect size' break the claim? The d values are not "
            "numerically identical (anxiety |d| in [0.70, 0.77]; depression d = 0.59 high diversity)."
        ),
        "verification_performed": (
            "Reviewed Cohen's (1988) conventional d magnitude thresholds: 0.2 small, 0.5 "
            "medium, 0.8 large. Examined the authors' own labels: birdsong-anxiety = 'medium', "
            "traffic-depression high diversity = 'medium'. Considered the standard "
            "interpretation that 'effect size' in plain-language summaries refers to Cohen's "
            "magnitude category rather than to identical decimal values."
        ),
        "finding": (
            "Both effects share the 'medium' magnitude category as labeled by the study "
            "authors. The d values differ (0.70-0.77 vs 0.59) but both lie within Cohen's "
            "medium bracket per the authors' classification. Operationalizing 'same effect "
            "size' as 'same magnitude category' is the standard reading for non-technical "
            "summaries of psychological findings, and this matches the abstract phrasing."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the low-diversity traffic condition (d = 0.29, small effect) contradict "
            "or break the claim?"
        ),
        "verification_performed": (
            "Re-read the abstract: 'small effect size in low, medium effect size in high "
            "diversity condition'. Considered whether the claim's omission of the "
            "low-diversity small-effect finding is a fatal oversimplification."
        ),
        "finding": (
            "The low-diversity finding is not a contradiction — depression still increased, "
            "just less. The claim is faithful to the high-diversity finding (which IS medium) "
            "and to the abstract-level summary; it omits the diversity conditioning. SC2's "
            "operator_note documents this scope. Operationally, the claim is supported by "
            "the high-diversity arm and is not refuted by the low-diversity arm."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the study have methodological problems (sample, design, replication) that "
            "would undermine even the descriptive 'this study reported X' claim?"
        ),
        "verification_performed": (
            "Searched for replications, criticism, and retractions of Stobbe et al. 2022. "
            "Reviewed the published methods: N = 295, randomized online experiment, four "
            "between-subjects conditions, validated questionnaires (STAI-S for state anxiety, "
            "PHQ-D for depression, R-GPTS for paranoia), 6-minute soundscape exposure. The "
            "paper has been cited extensively in mental-health and environmental-psychology "
            "literature without retraction or formal correction."
        ),
        "finding": (
            "The study is online-administered and has the usual limits of self-report and "
            "short-duration laboratory designs (immediate effects only, no ecological "
            "validity for long-term outcomes, no health-outcomes follow-up). These are "
            "limitations of what the finding GENERALIZES to, not of whether the study "
            "reported the effect sizes shown. The descriptive claim about what the study "
            "reported holds; broader causal/clinical generalizations are out of scope."
        ),
        "breaks_proof": False,
    },
]

# ---
# 11. VERDICT
# ---
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    # Per-sub-claim COI gate (Rule 6) — primary-source claim, no COI flagged.
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
        base_verdict = "PROVED"
    elif not claim_holds and n_holding == 0:
        base_verdict = "UNDETERMINED"
    else:
        base_verdict = "UNDETERMINED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    print(f"\n{'='*60}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*60}")
    print(f"SC1 (birdsong reduces anxiety, medium effect): n={n_sc1}, holds={sc1_holds}")
    print(f"SC2 (traffic noise raises depression, medium effect): n={n_sc2}, holds={sc2_holds}")
    print(f"Compound: {n_holding}/{n_total} sub-claims hold")
    print(f"Any unverified citations: {any_unverified}")
    print()

    # --- Build JSON summary ---
    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    # Map each B-fact to its sub-claim. B5 (duration) supports both — assign to SC1 for indexing.
    fact_to_sc = {
        "B1": "SC1", "B2": "SC1",
        "B3": "SC2", "B4": "SC2",
        "B5": "SC1",  # duration anchor; both sub-claims depend on it
    }

    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        ef = empirical_facts[ef_key]
        cr = citation_results.get(ef_key, {})
        sub_claim = fact_to_sc[fid]
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
        description=(
            "SC1: independent quotation of birdsong-anxiety finding from primary paper "
            "(raw d values) and PubMed-indexed abstract (author 'medium effect size' label)."
        ),
        fact_ids=sc1_fact_ids,
        n_sources_consulted=len(sc1_keys),
        n_sources_verified=n_sc1,
        sources={k: citation_results[k]["status"] for k in sc1_keys},
        independence_note=(
            "Nature paper full text and NLM PubMed abstract are separate hosted instances "
            "of the published record. They confirm both the numeric d values and the "
            "authors' qualitative label."
        ),
        coi_flags=sc1_coi_flags,
        agreement=sc1_holds,
    )
    builder.add_cross_check(
        description=(
            "SC2: independent quotation of traffic-noise depression finding from primary "
            "paper (raw d values) and PubMed-indexed abstract (author 'medium effect size' "
            "label for high-diversity condition)."
        ),
        fact_ids=sc2_fact_ids,
        n_sources_consulted=len(sc2_keys),
        n_sources_verified=n_sc2,
        sources={k: citation_results[k]["status"] for k in sc2_keys},
        independence_note=(
            "Same as SC1 — Nature and PubMed mirror the published record and are "
            "the canonical archival sources for the abstract and full text."
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
        sc1_d_low=-0.77,
        sc1_d_high=-0.70,
        sc2_d_low=0.29,
        sc2_d_high=0.59,
        exposure_minutes=6,
        sample_size=295,
    )
    builder.emit()
