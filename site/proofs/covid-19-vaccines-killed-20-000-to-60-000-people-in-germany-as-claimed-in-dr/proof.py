"""
Proof: COVID-19 vaccines killed 20,000 to 60,000 people in Germany
(as claimed in Dr. Helmut Sterz's March 19, 2026 parliamentary testimony
and amplified by Elon Musk on April 12).
Generated: 2026-04-19
"""
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/sessions/relaxed-gracious-johnson/mnt/.remote-plugins/plugin_01XTFg5zCzEf8gfhTURAn7wR/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date
from scripts.verify_citations import verify_all_citations
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# ---
# 1. CLAIM INTERPRETATION (Rule 4)
# ---
CLAIM_NATURAL = (
    "COVID-19 vaccines killed 20,000 to 60,000 people in Germany "
    "(as claimed in Dr. Helmut Sterz's March 19, 2026 parliamentary testimony "
    "and amplified by Elon Musk on April 12)."
)

CLAIM_FORMAL = {
    "subject": "COVID-19 vaccine deaths in Germany",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "Dr. Helmut Sterz made the 20,000-60,000 death claim in German parliamentary testimony on March 19, 2026, and Elon Musk amplified it on April 12, 2026",
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC1 checks provenance — did Sterz make this claim and did Musk amplify it? "
                "This is a factual question about whether the events occurred, not whether the claim is true."
            ),
        },
        {
            "id": "SC2",
            "property": "The claim that COVID-19 vaccines killed 20,000-60,000 people in Germany is scientifically supported",
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC2 checks the epistemic qualifier — 'killed' asserts a causal relationship. "
                "For the compound claim to be PROVED, it must be the case that vaccines actually caused "
                "20,000-60,000 deaths. SC2 requires independent scientific sources confirming this causation. "
                "Sources rejecting the methodology or finding no causal link belong in adversarial_checks."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "The claim uses the contested qualifier 'killed' (causal language). "
        "SC1 checks provenance (the assertion was made and amplified as described). "
        "SC2 checks the epistemic qualifier (the causal claim is scientifically warranted). "
        "Both must hold for the compound claim to be PROVED. "
        "If SC1 holds but SC2 fails, the verdict is DISPROVED — the assertion exists but "
        "the causal claim is not scientifically supported."
    ),
}

# ---
# 2. FACT REGISTRY
# ---
FACT_REGISTRY = {
    "B1": {"key": "sc1_factcheck_org", "label": "SC1: FactCheck.org confirms Sterz testimony and Musk amplification"},
    "B2": {"key": "sc1_newsbytes", "label": "SC1: NewsBytes confirms Sterz Bundestag testimony on March 19, 2026"},
    "B3": {"key": "sc1_businesstoday", "label": "SC1: BusinessToday confirms Musk's April 12 comments"},
    # Note: SC2 has no empirical_facts entries because no independent scientific
    # sources confirm 20,000-60,000 vaccine deaths in Germany. This is expected
    # per the contested qualifier pattern — empty SC2 means the qualifier is unwarranted.
    "A1": {"label": "SC1 verified source count", "method": None, "result": None},
    "A2": {"label": "SC2 verified source count", "method": None, "result": None},
}

# ---
# 3. EMPIRICAL FACTS — grouped by sub-claim
# ---
empirical_facts = {
    # SC1: Provenance — the claim was made and amplified
    "sc1_factcheck_org": {
        "quote": "baselessly claimed that the Pfizer/BioNTech vaccine killed 60,000 people in Germany",
        "url": "https://www.factcheck.org/2026/04/elon-musk-amplifies-baseless-claim-about-covid-19-vaccine/",
        "source_name": "FactCheck.org",
    },
    "sc1_newsbytes": {
        "quote": "before Germany's Bundestag's Corona Enquete Commission on March 19, 2026",
        "url": "https://www.newsbytesapp.com/news/world/fact-check-did-60-000-die-in-germany-from-covid-vaccine/story",
        "source_name": "NewsBytes",
        "verbatim": False,  # Summarized from article; exact phrasing may differ
    },
    "sc1_businesstoday": {
        "quote": "my second vaccine shot almost sent me to the hospital. Felt like I was dying",
        "url": "https://www.businesstoday.in/latest/trends/story/covid-19-vaccine-scrutiny-back-in-focus-after-elon-musks-comments-heres-what-he-said-525275-2026-04-12",
        "source_name": "BusinessToday India",
    },
    # SC2: Scientific support for the causal claim
    # No independent scientific sources confirm 20,000-60,000 vaccine deaths in Germany.
    # The methodology (multiplying passive surveillance reports by an underreporting factor)
    # is rejected by pharmacovigilance experts. Sources rejecting the claim are in adversarial_checks.
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
# 6. PER-SUB-CLAIM EVALUATION
# ---
sc1_holds = compare(
    n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
    label="SC1: Provenance — Sterz made the claim and Musk amplified it",
)
sc2_holds = compare(
    n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
    label="SC2: Scientific support — vaccines killed 20k-60k in Germany",
)

# ---
# 7. COMPOUND EVALUATION
# ---
n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# ---
# 8. COI FLAGS
# ---
sc1_coi_flags = []  # Provenance: COI does not invalidate "assertion was made"
sc2_coi_flags = []  # No SC2 sources exist

# ---
# 9. ADVERSARIAL CHECKS (Rule 5)
# ---
adversarial_checks = [
    {
        "question": "Does Sterz's methodology — multiplying PEI death reports by an underreporting factor of 30 — have any scientific basis?",
        "verification_performed": (
            "Searched FactCheck.org, VAERS FAQ (vaers.hhs.gov), Science Feedback, and NewsGuard Reality Check. "
            "Dr. Mahmoud Zureik (Versailles epidemiologist) stated: 'It is not valid to presume the 2000 reported "
            "deaths were caused by vaccines, much less to presume that there were 30x this number.' "
            "Jeffrey Morris noted that 'applying a fixed underreporting factor is not only unsupported but also "
            "ignores the possibility of reporting inflation.' "
            "The VAERS FAQ states: 'VAERS reports alone cannot be used to determine if a vaccine caused or "
            "contributed to an adverse event or illness.' "
            "An arXiv paper (2202.04204) specifically analyzed the absurdity of death estimates based on VAERS "
            "underreporting factors."
        ),
        "finding": (
            "No credible pharmacovigilance authority endorses multiplying passive surveillance death "
            "reports by a fixed underreporting factor to estimate causal deaths. The methodology conflates "
            "temporal association with causation and misapplies underreporting factors designed for non-serious "
            "events to deaths (which are more thoroughly reported). Multiple independent experts reject it."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Did the Paul Ehrlich Institute itself attribute 20,000-60,000 deaths to COVID vaccines?",
        "verification_performed": (
            "Checked PEI's official pharmacovigilance report (March 2025, covering data through Dec 2024). "
            "PEI received 2,133 reports of deaths following Pfizer/BioNTech vaccination. Of these, PEI assessed "
            "only 28 as having a 'possible or probable' causal relationship. NewsGuard reported the figure as 74 "
            "deaths across all COVID vaccines where causality was 'possible or probable.' "
            "PEI explicitly states: 'spontaneous reports are not suitable for determining if the reported adverse "
            "reaction was caused by vaccination.'"
        ),
        "finding": (
            "PEI's own assessment found 28 deaths possibly/probably related to Pfizer vaccination specifically "
            "(74 across all COVID vaccines) — orders of magnitude below the 20,000-60,000 claimed. "
            "The official regulator's causal assessment directly contradicts the claimed figure."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Do large-scale epidemiological studies find that COVID vaccines increased mortality?",
        "verification_performed": (
            "Searched for peer-reviewed studies on COVID vaccine mortality. A French study of 28 million adults "
            "(cited by FactCheck.org) found vaccinated people were less likely to die. The Lancet published data "
            "showing high vaccination rates correlated with lower mortality in Western Europe. "
            "Science Feedback analyzed and debunked a claim that vaccines killed 17 million people globally, "
            "noting the analysis was 'highly flawed' and 'doesn't account for COVID-19 mortality surges.'"
        ),
        "finding": (
            "Large epidemiological studies consistently find COVID vaccines reduced mortality rather than "
            "increasing it. No peer-reviewed study supports the 20,000-60,000 death figure for Germany."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is there any credible evidence supporting the claim that might make SC2 hold?",
        "verification_performed": (
            "Searched for studies supporting vaccine-caused excess mortality in Germany. Found one ecological "
            "study noting a correlation between vaccination rates and excess mortality in Germany's third "
            "pandemic year. However, Science Feedback noted this was an ecological correlation that 'provides "
            "moderate-strength evidence of an unexpected, statistically robust association' WITHOUT establishing "
            "causality. The study does not claim 20,000-60,000 deaths and explicitly states it cannot determine "
            "causation. No peer-reviewed source supports the specific 20,000-60,000 figure."
        ),
        "finding": (
            "The strongest evidence in the direction of the claim is an ecological correlation study that "
            "explicitly disclaims causal inference and does not support the specific death count. This does not "
            "meet the threshold for SC2. The adversarial search confirms no credible source supports the claim."
        ),
        "breaks_proof": False,
    },
]

# ---
# 10. VERDICT
# ---
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    # Per-sub-claim COI gate (Rule 6)
    sc1_coi_override = False  # Provenance: COI does not invalidate "assertion was made"

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

    # Contested qualifier: "killed" is the qualifier being tested
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
    print(f"SC1 (provenance): {n_sc1} verified sources, holds={sc1_holds}")
    print(f"SC2 (scientific support): {n_sc2} verified sources, holds={sc2_holds}")
    print(f"Compound: {n_holding}/{n_total} sub-claims hold")
    print(f"Contested qualifier detected: {is_contested_qualifier}")
    print(f"Any unverified citations: {any_unverified}")
    print()

    # --- Build JSON summary ---
    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        if ef_key not in empirical_facts:
            continue  # B4 is a placeholder for empty SC2
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
        description="SC1: independent sources on provenance of Sterz testimony and Musk amplification",
        fact_ids=sc1_fact_ids,
        n_sources_consulted=len(sc1_keys),
        n_sources_verified=n_sc1,
        sources={k: citation_results[k]["status"] for k in sc1_keys},
        independence_note="FactCheck.org (Annenberg), NewsBytes, BusinessToday — independent publications",
        coi_flags=sc1_coi_flags,
        agreement=sc1_holds,
    )
    builder.add_cross_check(
        description="SC2: independent scientific sources confirming 20k-60k vaccine deaths in Germany",
        fact_ids=sc2_fact_ids,
        n_sources_consulted=len(sc2_keys),
        n_sources_verified=n_sc2,
        sources={k: citation_results[k]["status"] for k in sc2_keys},
        independence_note="No independent scientific sources confirm the claim",
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
    )
    builder.emit()
