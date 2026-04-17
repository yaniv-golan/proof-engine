"""
Proof: Humans use only 10% of their brain at any one time.
Generated: 2026-04-15
Direction: DISPROVE — authoritative neuroscience sources reject this claim
"""
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# ---
# 1. Claim Interpretation (Rule 4)
# ---
CLAIM_NATURAL = "Humans use only 10% of their brain at any one time."
CLAIM_FORMAL = {
    "subject": "Human brain",
    "property": "proportion of brain actively used at any given time",
    "operator": ">=",
    "operator_note": (
        "The claim asserts that only 10% of the brain is in use at any one time. "
        "This is disproved when >= 3 authoritative neuroscience sources reject the claim, "
        "providing evidence that substantially more than 10% of the brain is active at any "
        "given time. 'Use' is interpreted as neuronal activity detectable by functional "
        "brain imaging (fMRI, PET scans) or inferred from lesion studies."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# ---
# 2. Fact Registry
# ---
FACT_REGISTRY = {
    "B1": {"key": "scientific_american", "label": "Scientific American — neurologist Barry Gordon rejects the 10% myth"},
    "B2": {"key": "mit_mcgovern", "label": "MIT McGovern Institute — the 10% claim is '100 percent a myth'"},
    "B3": {"key": "uw_neuroscience", "label": "University of Washington Neuroscience — no scientific evidence for 10% claim"},
    "A1": {"label": "Verified rejection source count", "method": None, "result": None},
}

# ---
# 3. Empirical Facts — sources that REJECT the claim (confirm it is false)
# ---
empirical_facts = {
    "scientific_american": {
        "source_name": "Scientific American (Barry Gordon, Johns Hopkins)",
        "url": "https://www.scientificamerican.com/article/do-people-only-use-10-percent-of-their-brains/",
        "quote": (
            'the "10 percent myth" is so wrong it is almost laughable, '
            "says neurologist Barry Gordon at Johns Hopkins School of Medicine in Baltimore"
        ),
        "rejection_statement": 'the "10 percent myth" is so wrong it is almost laughable',
    },
    "mit_mcgovern": {
        "source_name": "MIT McGovern Institute for Brain Research",
        "url": "https://mcgovern.mit.edu/2024/01/26/do-we-use-only-10-percent-of-our-brain/",
        "quote": (
            "the idea that we use 10 percent of our brain is 100 percent a myth"
        ),
        "rejection_statement": "the idea that we use 10 percent of our brain is 100 percent a myth",
    },
    "uw_neuroscience": {
        "source_name": "Neuroscience For Kids, University of Washington (Eric Chudler)",
        "url": "http://faculty.washington.edu/chudler/tenper.html",
        "quote": (
            "There is no scientific evidence to suggest that we use only 10% of our brains"
        ),
        "rejection_statement": "no scientific evidence to suggest that we use only 10%",
    },
}

# ---
# 4. Citation Verification (Rule 2)
# ---
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---
# 5. Count Sources with Verified Citations
# ---
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed rejection sources: {n_confirmed} / {len(empirical_facts)}")

# ---
# 6. Claim Evaluation — MUST use compare(), never hardcode claim_holds
# ---
claim_holds = compare(n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                      label="verified rejection source count vs threshold")

# ---
# 7. COI Flags (Rule 6)
# ---
coi_flags = []  # No COI identified — all sources are independent academic/science institutions

# ---
# 8. Adversarial Checks (Rule 5) — for disproof, search for evidence SUPPORTING the claim
# ---
adversarial_checks = [
    {
        "question": "Is there any peer-reviewed neuroscience study that supports the claim that only 10% of the brain is active at any given time?",
        "verification_performed": (
            "Searched for: '10 percent brain myth credible support evidence true', "
            "'10% brain use scientific evidence peer-reviewed'. "
            "Reviewed results from Scientific American, Psychology Today, Wikipedia, "
            "Association for Psychological Science, MIT McGovern Institute, "
            "Medical News Today, and University of Washington."
        ),
        "finding": (
            "No peer-reviewed neuroscience study was found supporting the 10% claim. "
            "Every neuroscience source consulted explicitly labels it a myth. "
            "Brain imaging studies (fMRI, PET) consistently show activity throughout "
            "the entire brain, even during sleep."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the 10% figure refer to the ratio of neurons to glial cells, making the claim technically true under a different interpretation?",
        "verification_performed": (
            "Searched for: 'neurons 10 percent brain cells glial ratio'. "
            "Reviewed neuroscience sources on neuron-to-glia ratios."
        ),
        "finding": (
            "While roughly 10% of brain cells are neurons (the rest being glial cells), "
            "the claim says 'use only 10% of their brain,' which refers to brain regions "
            "being active, not cell-type ratios. Furthermore, glial cells are also functionally "
            "active — they support neuronal function, maintain homeostasis, and participate in "
            "signaling. The neuron/glia ratio does not support the claim as stated."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could William James's original 1907 statement be interpreted as literal neuroscience supporting the 10% claim?",
        "verification_performed": (
            "Searched for: 'William James 1907 energies of men 10 percent origin'. "
            "Reviewed MIT McGovern and Wikipedia articles on the myth's origins."
        ),
        "finding": (
            "William James wrote in 'The Energies of Men' (1907) that 'we are making use "
            "of only a small part of our possible mental and physical resources.' He was "
            "speaking metaphorically about human potential, not making a neuroscientific "
            "claim about brain activity percentages. He never stated 10%, and his work "
            "predates functional brain imaging by decades."
        ),
        "breaks_proof": False,
    },
]

# ---
# 9. Verdict and Structured Output
# ---
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    # COI GATE (Rule 6)
    confirmed_keys = {k for k in empirical_facts
                      if citation_results[k]["status"] in COUNTABLE_STATUSES}
    coi_favorable = {f["source_key"] for f in coi_flags
                     if f["direction"] == "favorable_to_subject"
                     and f["source_key"] in confirmed_keys}
    coi_unfavorable = {f["source_key"] for f in coi_flags
                       if f["direction"] == "unfavorable_to_subject"
                       and f["source_key"] in confirmed_keys}
    coi_majority = max(len(coi_favorable), len(coi_unfavorable)) if coi_flags else 0
    coi_override = n_confirmed >= CLAIM_FORMAL["threshold"] and coi_majority > n_confirmed / 2

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif coi_override:
        base_verdict = "UNDETERMINED"
    elif claim_holds:
        base_verdict = "DISPROVED" if is_disproof else "PROVED"
    else:
        base_verdict = "UNDETERMINED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

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
        label="Verified rejection source count",
        method=f"count(verified rejection citations) = {n_confirmed}",
        result=n_confirmed,
        depends_on=[fid for fid in FACT_REGISTRY if fid.startswith("B")],
    )

    builder.add_cross_check(
        description="Multiple independent sources consulted",
        fact_ids=[fid for fid in FACT_REGISTRY if fid.startswith("B")],
        n_sources_consulted=len(empirical_facts),
        n_sources_verified=n_confirmed,
        sources={k: citation_results[k]["status"] for k in empirical_facts},
        independence_note=(
            "Sources are from different institutions: Scientific American (quoting "
            "Johns Hopkins neurologist), MIT McGovern Institute, and University of "
            "Washington. No organizational, funding, or ideological overlap."
        ),
        coi_flags=coi_flags,
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
        n_confirmed=n_confirmed,
        threshold=CLAIM_FORMAL["threshold"],
        operator=CLAIM_FORMAL["operator"],
        claim_holds=claim_holds,
    )
    builder.emit()
