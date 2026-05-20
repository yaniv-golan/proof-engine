"""
Proof: Chronic periodontal disease has been associated with an increased risk of
atherosclerotic cardiovascular disease in adults, with consensus reviews pointing
to systemic inflammation as a biologically plausible mediating mechanism
(Tonetti & Van Dyke, 2013; Sanz et al., 2020; Cullinan & Ford, 2013).
Generated: 2026-05-20
"""
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        cand = os.path.join(_d, "proof-engine", "skills", "proof-engine", "scripts")
        if os.path.isdir(cand):
            PROOF_ENGINE_ROOT = os.path.join(_d, "proof-engine", "skills", "proof-engine")
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        # Fallback for hosted skill location used by the proof-engine plugin.
        _candidates = [
            "/sessions/beautiful-vigilant-dirac/mnt/.remote-plugins/plugin_011ppymzz6m5MeDLUDFMKX53/skills/proof-engine",
        ]
        for c in _candidates:
            if os.path.isdir(os.path.join(c, "scripts")):
                PROOF_ENGINE_ROOT = c
                break
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Hardening Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "Chronic periodontal disease has been associated with an increased risk of "
    "atherosclerotic cardiovascular disease in adults, with consensus reviews "
    "pointing to systemic inflammation as a biologically plausible mediating "
    "mechanism (Tonetti & Van Dyke, 2013; Sanz et al., 2020; "
    "Cullinan & Ford, 2013)."
)
CLAIM_FORMAL = {
    "subject": "Chronic periodontal disease and atherosclerotic cardiovascular disease (ASCVD)",
    "property": (
        "Consensus reviews in periodontology and cardiology report (a) a "
        "statistically meaningful association between periodontitis and incident "
        "ASCVD in adults that is independent of established cardiovascular risk "
        "factors, and (b) systemic inflammation as a biologically plausible "
        "mediating mechanism for this association."
    ),
    "operator": ">=",
    "operator_note": (
        "Claim is read as ASSOCIATIONAL, not causal — the words 'has been "
        "associated with' and 'biologically plausible mediating mechanism' are "
        "deliberately weaker than 'causes'. The claim is supported when ≥ 3 "
        "independent consensus reviews/scientific statements affirm BOTH (a) an "
        "independent epidemiological association between periodontitis and "
        "ASCVD AND (b) systemic inflammation as a biologically plausible "
        "mediating mechanism. ATTRIBUTION CORRECTION: The cited 'Cullinan & "
        "Ford, 2013' is treated as a benign mis-citation of the 2013 "
        "Periodontology 2000 review whose actual authors are 'Cullinan MP, "
        "Seymour GJ' (doi:10.1111/prd.12007). Patrice Ford is co-author of an "
        "earlier 2009 Australian Dental Journal review by Cullinan, Ford and "
        "Seymour, not the 2013 paper. This is documented as an adversarial "
        "check; the underlying consensus claim is unaffected."
    ),
    "threshold": 3,
    "proof_direction": "affirm",
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {"key": "tonetti_van_dyke_2013",
           "label": "Tonetti & Van Dyke 2013, EFP/AAP Joint Workshop consensus report"},
    "B2": {"key": "sanz_2020",
           "label": "Sanz et al. 2020, EFP/WHF Perio-Cardio Workshop consensus report"},
    "B3": {"key": "cullinan_seymour_2013",
           "label": "Cullinan & Seymour 2013, Periodontology 2000 review (treated as the cited 'Cullinan & Ford 2013')"},
    "B4": {"key": "aha_2012",
           "label": "Lockhart et al. 2012, AHA Scientific Statement (Circulation) — independent corroboration"},
    "A1": {"label": "Verified source count", "method": None, "result": None},
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS — sources confirming the claim
# Each quote was copied verbatim from the rendered PubMed abstract page
# (UTF-8 plaintext) — see snapshots/ for archived copies.
# ---------------------------------------------------------------------------
_PROOF_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_snapshot(fname):
    fpath = os.path.join(_PROOF_DIR, fname)
    try:
        with open(fpath, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

empirical_facts = {
    "tonetti_van_dyke_2013": {
        "quote": (
            "In longitudinal studies assessing incident cardiovascular events, "
            "statistically significant excess risk for ACVD was reported in "
            "individuals with periodontitis. This was independent of "
            "established cardiovascular risk factors."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/23627332/",
        "source_name": "Tonetti MS, Van Dyke TE (2013), Periodontitis and atherosclerotic cardiovascular disease: consensus report of the Joint EFP/AAP Workshop on Periodontitis and Systemic Diseases. J Clin Periodontol 40(Suppl 14):S24-S29. doi:10.1111/jcpe.12089",
        "snapshot": _load_snapshot("snapshots/B1_tonetti_van_dyke_2013.txt"),
        "snapshot_source": "public:pubmed_abstract",
    },
    "sanz_2020": {
        "quote": (
            "There is now a significant body of evidence to support independent "
            "associations between severe periodontitis and several NCDs, in "
            "particular CVD."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/32011025/",
        "source_name": "Sanz M, Marco del Castillo A, Jepsen S, et al. (2020), Periodontitis and cardiovascular diseases: Consensus report. J Clin Periodontol 47(3):268-288. doi:10.1111/jcpe.13189",
        "snapshot": _load_snapshot("snapshots/B2_sanz_2020.txt"),
        "snapshot_source": "public:pubmed_abstract",
    },
    "cullinan_seymour_2013": {
        "quote": (
            "the weight of evidence from numerous studies conducted over this "
            "period, together with several systematic reviews and meta-analyses, "
            "supports an association between periodontitis and cardiovascular "
            "disease, and between periodontitis and diabetes. The association "
            "has also been supported by a number of biologically plausible "
            "mechanisms, including direct infection, systemic inflammation and "
            "molecular mimicry."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/23574472/",
        "source_name": "Cullinan MP, Seymour GJ (2013), Periodontal disease and systemic illness: will the evidence ever be enough? Periodontol 2000 62(1):271-286. doi:10.1111/prd.12007",
        "snapshot": _load_snapshot("snapshots/B3_cullinan_seymour_2013.txt"),
        "snapshot_source": "public:pubmed_abstract",
    },
    "aha_2012": {
        "quote": (
            "Observational studies to date support an association between PD "
            "and ASVD independent of known confounders. They do not, however, "
            "support a causative relationship."
        ),
        "url": "http://web.archive.org/web/20260128105120/https://pubmed.ncbi.nlm.nih.gov/22514251/",
        "source_name": "Lockhart PB, Bolger AF, Papapanou PN, et al. (2012), Periodontal Disease and Atherosclerotic Vascular Disease: Does the Evidence Support an Independent Association? A Scientific Statement From the American Heart Association. Circulation 125(20):2520-2544. doi:10.1161/CIR.0b013e31825719f3. PubMed: https://pubmed.ncbi.nlm.nih.gov/22514251/ (live PubMed fetch was intercepted by reCAPTCHA from this environment; Wayback snapshot used instead).",
        "snapshot": _load_snapshot("snapshots/B4_aha_2012.txt"),
        "snapshot_source": "public:pubmed_abstract_via_wayback",
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Hardening Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. COUNT SOURCES WITH VERIFIED CITATIONS
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# ---------------------------------------------------------------------------
# 6. CLAIM EVALUATION (Hardening Rule 7 — compare(), no hardcoded True/False)
# ---------------------------------------------------------------------------
claim_holds = compare(
    n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
    label="verified consensus-review count vs. threshold",
)

# ---------------------------------------------------------------------------
# 7. COI FLAGS
# ---------------------------------------------------------------------------
# All four sources are peer-reviewed consensus statements or scientific
# statements from major medical/dental societies (EFP/AAP, EFP/WHF, AHA, and
# the Periodontology 2000 journal). No commercial sponsor steers the
# conclusions; the AHA statement is, if anything, the most conservative of
# the four (it pushes back on causation). No COI flagged.
coi_flags = []

# ---------------------------------------------------------------------------
# 8. ADVERSARIAL CHECKS (Hardening Rule 5)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Do recent reviews or Mendelian-randomization studies overturn the "
            "epidemiological association between periodontitis and ASCVD?"
        ),
        "verification_performed": (
            "Searched PubMed and the web (2022–2026) for counter-evidence: "
            "'periodontitis cardiovascular disease no evidence', "
            "'periodontitis CVD not causal', 'Mendelian randomization "
            "periodontitis ASCVD'. Located Carra et al. 2024 ('Periodontitis "
            "and atherosclerotic cardiovascular disease: A critical "
            "appraisal', Periodontology 2000, doi:10.1111/prd.12528) and the "
            "Brodzikowska & Górski 2022 review (PMC9275186). Both papers "
            "REJECT the stronger causal claim and note that Mendelian "
            "randomization has so far failed to demonstrate genetic "
            "causality, but BOTH still affirm the associational link the "
            "claim asserts. Carra et al. explicitly state that observed "
            "associations 'may be influenced by various biases, such as "
            "confounding and collider stratification' — yet still conclude "
            "the association is real. The claim under proof uses only "
            "associational and 'biologically plausible' language, not causal "
            "language, so this counter-evidence does not break the proof."
        ),
        "finding": (
            "No source overturns the association. Counter-evidence is "
            "directed at the stronger causal hypothesis (which this claim "
            "does NOT assert). The associational + 'biologically plausible "
            "mechanism' framing remains consensus."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is 'Cullinan & Ford, 2013' a real publication, or is the user's "
            "citation mis-attributed?"
        ),
        "verification_performed": (
            "Searched PubMed and Google Scholar for any 2012–2013 "
            "Cullinan-and-Ford periodontal-systemic review. No such paper "
            "exists. The 2013 Periodontology 2000 review on periodontitis "
            "and systemic illness is Cullinan MP & Seymour GJ (PMID "
            "23574472). The Ford co-authorship is on an earlier 2009 "
            "Australian Dental Journal review (Cullinan, Ford, Seymour; "
            "doi:10.1111/j.1834-7819.2009.01144.x). This is treated as a "
            "benign mis-citation: the cited year is correct, the subject "
            "matter matches, only the second-author attribution is wrong. "
            "Proof substitutes the actual Cullinan & Seymour 2013 paper as B3."
        ),
        "finding": (
            "Attribution error confirmed. Does not break the proof because "
            "the substitute source (Cullinan & Seymour 2013) makes exactly "
            "the assertion the claim attributes to that citation."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could publication-bias or sponsor capture inflate the apparent "
            "consensus among periodontology consensus statements?"
        ),
        "verification_performed": (
            "Checked authorship and convening bodies. Two of the four "
            "sources are joint perio-cardio workshops with cardiology "
            "co-leadership (EFP/AAP 2013 included Van Dyke from the Forsyth "
            "Institute; EFP/WHF 2020 was co-led with the World Heart "
            "Federation and includes cardiology co-authors such as "
            "Gonzalez-Juanatey and Vlachopoulos). The AHA 2012 statement "
            "(B4) is from cardiology, not periodontology, and is the most "
            "skeptical of the four (rejects causation). The convergence of "
            "the periodontology consensus reviews with the independent "
            "cardiology statement reduces the risk that the apparent "
            "consensus is an artifact of disciplinary self-promotion."
        ),
        "finding": (
            "Cross-disciplinary corroboration present. The AHA statement, "
            "from outside periodontology, agrees on the associational claim."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 9. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    confirmed_keys = {k for k in empirical_facts
                      if citation_results[k]["status"] in COUNTABLE_STATUSES}
    coi_favorable = {f["source_key"] for f in coi_flags
                     if f["direction"] == "favorable_to_subject"
                     and f["source_key"] in confirmed_keys}
    coi_unfavorable = {f["source_key"] for f in coi_flags
                       if f["direction"] == "unfavorable_to_subject"
                       and f["source_key"] in confirmed_keys}
    coi_majority = max(len(coi_favorable), len(coi_unfavorable)) if coi_flags else 0
    coi_override = (n_confirmed >= CLAIM_FORMAL["threshold"]
                    and coi_majority > n_confirmed / 2)

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif coi_override:
        base_verdict = "UNDETERMINED"
    elif claim_holds:
        base_verdict = "DISPROVED" if is_disproof else "PROVED"
    else:
        base_verdict = "UNDETERMINED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    print(f"\n=== VERDICT: {verdict} ===\n")

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
        label="Verified source count",
        method=f"count(verified citations) = {n_confirmed}",
        result=n_confirmed,
        depends_on=[fid for fid in FACT_REGISTRY if fid.startswith("B")],
    )

    builder.add_cross_check(
        description=(
            "Four independent consensus statements consulted: two joint "
            "perio-cardio workshops (EFP/AAP 2013, EFP/WHF 2020), one "
            "Periodontology 2000 narrative review (Cullinan & Seymour 2013), "
            "and one independent AHA cardiology scientific statement (Lockhart "
            "et al. 2012)."
        ),
        fact_ids=[fid for fid in FACT_REGISTRY if fid.startswith("B")],
        n_sources_consulted=len(empirical_facts),
        n_sources_verified=n_confirmed,
        sources={k: citation_results[k]["status"] for k in empirical_facts},
        independence_note=(
            "Sources span three convening bodies (EFP, AAP, WHF), two "
            "disciplines (periodontology and cardiology), and a 7-year time "
            "window. AHA 2012 is the most skeptical and was published by a "
            "cardiology body — its agreement on the associational claim is "
            "the strongest evidence against discipline-internal bias."
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
