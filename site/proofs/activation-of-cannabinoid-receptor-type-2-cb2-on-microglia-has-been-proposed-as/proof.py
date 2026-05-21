"""
Proof: "Activation of cannabinoid receptor type 2 (CB2) on microglia has been
proposed as a mechanism for modulating neuroinflammatory pain states, including
chronic widespread pain syndromes such as fibromyalgia where central
sensitization and microglial activation have been implicated
(Cabral & Griffin-Thomas, 2009; Stella, 2010; Chen et al., 2023)."

Compound empirical claim about the scientific literature. Decomposed into three
sub-claims joined by AND:
  SC1 - the CB2/microglia mechanism for neuroinflammatory pain has been proposed;
  SC2 - central sensitization and microglial activation are implicated in
        fibromyalgia;
  SC3 - the three references the claim names all resolve to real, identifiable
        publications.

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

# PubMed Central (pmc.ncbi.nlm.nih.gov) blocks / truncates automated HTTP
# fetches non-deterministically: an identical request returns the full article
# on one run and a ~21 KB stub on the next. To make this proof fully
# deterministic and offline-reproducible, live fetching is disabled so that
# verification runs against the committed snapshots/ copies (captured
# 2026-05-20 with a browser user-agent). Monkeypatching `requests` on the
# verify module is a documented, supported pattern (see SKILL.md).
import scripts.verify_citations as _vc
_vc.requests = None

from scripts.verify_citations import verify_all_citations          # noqa: E402
from scripts.computations import compare, apply_verdict_qualifier  # noqa: E402
from scripts.proof_summary import ProofSummaryBuilder              # noqa: E402

_PROOF_DIR = os.path.dirname(os.path.abspath(__file__))


def _snap(name):
    """Absolute path to a committed source snapshot."""
    return os.path.join(_PROOF_DIR, "snapshots", name)


# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "Activation of cannabinoid receptor type 2 (CB2) on microglia has been "
    "proposed as a mechanism for modulating neuroinflammatory pain states, "
    "including chronic widespread pain syndromes such as fibromyalgia where "
    "central sensitization and microglial activation have been implicated "
    "(Cabral & Griffin-Thomas, 2009; Stella, 2010; Chen et al., 2023)."
)

CLAIM_FORMAL = {
    "subject": (
        "the peer-reviewed literature on CB2-receptor activation on microglia, "
        "neuroinflammatory pain, and fibromyalgia, plus the three references "
        "the claim cites"
    ),
    "claim_type": "compound_empirical",
    "proof_direction": "affirm",
    "is_time_sensitive": False,
    "sub_claims": [
        {
            "id": "SC1",
            "property": (
                "independently published peer-reviewed sources that propose or "
                "articulate CB2-receptor activation on microglia as a mechanism "
                "for modulating neuroinflammatory pain"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "Counts independently published peer-reviewed sources that "
                "articulate the CB2-on-microglia / neuroinflammatory-pain "
                "mechanism. Threshold 3 is the standard consensus floor. The "
                "claim's phrase 'including ... fibromyalgia' is read as naming "
                "fibromyalgia as an INSTANCE of a neuroinflammatory pain state "
                "(a reading justified by SC2); SC1 therefore does NOT require a "
                "study that specifically proposed CB2-on-microglia agonism as a "
                "fibromyalgia therapy. The claim's verb 'has been proposed' is "
                "hedged, hypothesis-level language: the proof verifies that the "
                "mechanism has been proposed, NOT that it is a clinically "
                "proven fibromyalgia treatment."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "independently published peer-reviewed sources implicating "
                "central sensitization and microglial activation in fibromyalgia"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "Counts independently published peer-reviewed sources "
                "implicating central sensitization and/or microglial activation "
                "in fibromyalgia. Threshold 3 is the standard consensus floor. "
                "The two phenomena are evaluated together because the claim "
                "conjoins them; the supporting set collectively covers both - "
                "microglial / glial activation (Findeisen et al. review; "
                "Albrecht et al. PET study) and central sensitization "
                "(Jurado-Priego et al. review, which names fibromyalgia "
                "explicitly). The verb 'have been implicated' is hedged."
            ),
        },
        {
            "id": "SC3",
            "property": (
                "references named in the claim that resolve to a real, "
                "identifiable publication on the attributed topic"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "Citation-integrity check - NOT a consensus count. The claim "
                "explicitly cites three references; threshold 3 means all three "
                "must resolve to a real, identifiable publication. Empirical "
                "facts sc3_cabral and sc3_stella confirm two of them "
                "(Cabral & Griffin-Thomas, 2009; Stella, 2010). There is NO "
                "empirical fact for the third reference, 'Chen et al., 2023', "
                "because systematic PubMed searches (adversarial check AC3) "
                "found no publication matching that citation on this topic. "
                "The absence of a third empirical fact is itself the evidence "
                "that SC3 fails: n_sc3 = 2 < 3."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "The claim is taken as a complete unit - the sentence AND its "
        "parenthetical citation list - and decomposed into three sub-claims "
        "joined by AND. SC1 and SC2 test the two scientific propositions; SC3 "
        "tests the integrity of the three references the claim names. All "
        "three sub-claims must hold for the claim to be fully PROVED. The "
        "claim's verbs ('has been proposed', 'have been implicated') are "
        "deliberately hedged, hypothesis-level language; this proof verifies "
        "exactly that hedged form and does not test clinical efficacy."
    ),
}

# Reference inventory the claim asserts. SC3 tests whether each resolves.
# This is documentation only; the SC3 verdict is computed from citation
# verification results below, not from this table.
CITED_REFERENCES = [
    "Cabral & Griffin-Thomas, 2009  -> resolves (Expert Rev Mol Med 11:e3; PMC2768535)",
    "Stella, 2010                   -> resolves (Glia 58(9):1017-1030; PMC2919281)",
    "Chen et al., 2023              -> NOT identified (see adversarial check AC3)",
]

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {"key": "sc1_cabral",   "label": "SC1: Cabral & Griffin-Thomas (2009) - CB2 localized to microglia"},
    "B2": {"key": "sc1_stella",   "label": "SC1: Stella (2010) - CB2 on microglia; activation regulates microglial function"},
    "B3": {"key": "sc1_xu",       "label": "SC1: Xu et al. (2023) - CB2 on activated microglia in spinal pain circuitry"},
    "B4": {"key": "sc2_brainsci", "label": "SC2: Findeisen et al. (2025) - maladaptive microglial activation in fibromyalgia"},
    "B5": {"key": "sc2_albrecht", "label": "SC2: Albrecht et al. (2019) - PET evidence of brain glial activation in fibromyalgia"},
    "B6": {"key": "sc2_jurado",   "label": "SC2: Jurado-Priego et al. (2024) - central sensitization as a process in fibromyalgia"},
    "B7": {"key": "sc3_cabral",   "label": "SC3: cited reference 1 - Cabral & Griffin-Thomas (2009) resolves to a real publication"},
    "B8": {"key": "sc3_stella",   "label": "SC3: cited reference 2 - Stella (2010) resolves to a real publication"},
    "A1": {"label": "SC1 verified-source count", "method": None, "result": None},
    "A2": {"label": "SC2 verified-source count", "method": None, "result": None},
    "A3": {"label": "SC3 resolved-citation count", "method": None, "result": None},
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS - grouped by sub-claim (Rule 2)
#    Quotes are verbatim substrings of the committed snapshots/ copies.
# ---------------------------------------------------------------------------
empirical_facts = {
    # --- SC1: CB2-on-microglia mechanism for neuroinflammatory pain ---
    "sc1_cabral": {
        "quote": "This expression of CB2 has been localized primarily to microglia, the resident macrophages of the CNS.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2768535/",
        "source_name": "Cabral GA & Griffin-Thomas L (2009), 'Emerging role of the cannabinoid receptor CB2 in immune regulation: therapeutic prospects for neuroinflammation', Expert Reviews in Molecular Medicine 11:e3 (PubMed Central PMC2768535)",
        "snapshot_file": _snap("cabral2009.html"),
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": "2026-05-20",
    },
    "sc1_stella": {
        "quote": "These receptors are expressed by microglia, astrocytes and astrocytomas, and their activation regulates these cells’ differentiation, functions and viability.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2919281/",
        "source_name": "Stella N (2010), 'Cannabinoid and cannabinoid-like receptors in microglia, astrocytes, and astrocytomas', Glia 58(9):1017-1030 (PubMed Central PMC2919281)",
        "snapshot_file": _snap("stella2010.html"),
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": "2026-05-20",
    },
    "sc1_xu": {
        "quote": "Accumulating evidence has demonstrated that the expression of CB2 receptors is significantly increased in activated microglia in the spinal cord",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9917135/",
        "source_name": "Xu K, Wu Y, Tian Z, et al. (2023), 'Microglial Cannabinoid CB2 Receptors in Pain Modulation', International Journal of Molecular Sciences 24(3):2348 (PubMed Central PMC9917135)",
        "snapshot_file": _snap("xu2023.html"),
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": "2026-05-20",
    },
    # --- SC2: central sensitization & microglial activation in fibromyalgia ---
    "sc2_brainsci": {
        "quote": "There is a growing focus on processes occurring in the dorsal root ganglia and the role of maladaptive microglial cell activation.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11852494/",
        "source_name": "Findeisen K, Guymer E, Littlejohn G (2025), 'Neuroinflammatory and Immunological Aspects of Fibromyalgia', Brain Sciences 15(2):206 (PubMed Central PMC11852494)",
        "snapshot_file": _snap("fm_brainsci2025.html"),
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": "2026-05-20",
    },
    "sc2_albrecht": {
        "quote": "While mounting evidence suggests a role for neuroinflammation, no study has directly provided evidence of brain glial activation in FM.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6541932/",
        "source_name": "Albrecht DS, Forsberg A, Sandstrom A, et al. (2019), 'Brain glial activation in fibromyalgia - A multi-site positron emission tomography investigation', Brain, Behavior, and Immunity 75:72-83 (PubMed Central PMC6541932)",
        "snapshot_file": _snap("albrecht2019.html"),
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": "2026-05-20",
    },
    "sc2_jurado": {
        "quote": "three underlying processes in fibromyalgia have been investigated. These include central sensitization, associated with an increase in the release of both excitatory and inhibitory neurotransmitters",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11275111/",
        "source_name": "Jurado-Priego LN, Cueto-Urena C, Ramirez-Exposito MJ, Martinez-Martos JM (2024), 'Fibromyalgia: A Review of the Pathophysiological Mechanisms and Multidisciplinary Treatment Approaches', Biomedicines 12(7):1543 (PubMed Central PMC11275111)",
        "snapshot_file": _snap("jurado2024.html"),
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": "2026-05-20",
    },
    # --- SC3: do the cited references resolve to real publications? ---
    "sc3_cabral": {
        "quote": "Expert Rev Mol Med. 2009 Jan 20;11:e3. doi: 10.1017/S1462399409000957",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2768535/",
        "source_name": "PubMed Central bibliographic record for Cabral & Griffin-Thomas (2009), PMC2768535",
        "snapshot_file": _snap("cabral2009.html"),
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": "2026-05-20",
    },
    "sc3_stella": {
        "quote": "Glia. 2010 Jul;58(9):1017-1030. doi: 10.1002/glia.20983",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2919281/",
        "source_name": "PubMed Central bibliographic record for Stella (2010), PMC2919281",
        "snapshot_file": _snap("stella2010.html"),
        "snapshot_source": "public:pre_fetched",
        "snapshot_fetched_at": "2026-05-20",
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=False)

# ---------------------------------------------------------------------------
# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]
sc3_keys = [k for k in empirical_facts if k.startswith("sc3_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc3 = sum(1 for k in sc3_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

# ---------------------------------------------------------------------------
# 6. PER-SUB-CLAIM EVALUATION (Rule 7 - compare(), no hardcoded booleans)
# ---------------------------------------------------------------------------
sc1_holds = compare(n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
                    label="SC1 (CB2/microglia mechanism proposed)")
sc2_holds = compare(n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
                    label="SC2 (central sensitization & microglial activation in fibromyalgia)")
sc3_holds = compare(n_sc3, ">=", CLAIM_FORMAL["sub_claims"][2]["threshold"],
                    label="SC3 (all three cited references resolve)")

# ---------------------------------------------------------------------------
# 7. COMPOUND EVALUATION
# ---------------------------------------------------------------------------
sub_claim_outcomes = [sc1_holds, sc2_holds, sc3_holds]
n_holding = sum(sub_claim_outcomes)
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound (all sub-claims hold)")

# ---------------------------------------------------------------------------
# 8. CONFLICT-OF-INTEREST FLAGS (Rule 6) - per sub-claim
#    The claim concerns the scientific literature, not a commercial entity;
#    every source is an independent academic publication. No COI identified.
# ---------------------------------------------------------------------------
sc1_coi_flags = []
sc2_coi_flags = []
sc3_coi_flags = []

# ---------------------------------------------------------------------------
# 9. ADVERSARIAL CHECKS (Rule 5) - documentation of Step-2 counter-research
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Is the CB2-on-microglia mechanism for neuroinflammatory pain a "
            "genuine, proposed research mechanism - or is it fringe / disputed?"
        ),
        "verification_performed": (
            "Searched PubMed and the web for reviews and primary literature on "
            "CB2 receptors, microglia and pain ('CB2 microglia pain "
            "modulation', 'cannabinoid CB2 neuroinflammation', 'cannabinoid "
            "fibromyalgia efficacy'). Cross-checked whether cannabinoids are "
            "an established fibromyalgia treatment."
        ),
        "finding": (
            "The CB2-on-microglia mechanism for modulating neuroinflammatory "
            "pain is a well-established research hypothesis, articulated "
            "across many independent peer-reviewed reviews from 2009 to 2023 - "
            "not a fringe claim. Counter-point: clinical efficacy of "
            "cannabinoids in fibromyalgia SPECIFICALLY remains inconsistent "
            "and unproven. This does not break SC1, because the claim asserts "
            "only that the mechanism 'has been proposed' (hypothesis-level "
            "language), not that it is a clinically proven treatment; the "
            "hedged wording is accurate. The unproven-efficacy point is "
            "recorded so the claim is not over-read."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is microglial activation in fibromyalgia disputed - e.g. is the "
            "Albrecht et al. (2019) glial-activation PET finding contradicted?"
        ),
        "verification_performed": (
            "Searched for replication and criticism of glial-activation "
            "findings in fibromyalgia ('fibromyalgia microglia PET "
            "criticism', 'fibromyalgia neuroinflammation replication', "
            "'TSPO PET limitations')."
        ),
        "finding": (
            "TSPO-PET evidence of glial activation in fibromyalgia has "
            "acknowledged limitations (the TSPO tracer is not microglia-"
            "specific; sample sizes are modest), and it remains an area of "
            "active research. But the broader implication - that "
            "neuroinflammation / microglial activation and central "
            "sensitization are involved in fibromyalgia - is supported by "
            "converging evidence (PET imaging, CSF cytokines, multiple "
            "narrative reviews). No authoritative source rejects the "
            "implication. The claim's verb 'have been implicated' is "
            "appropriately hedged, so the TSPO caveats do not break SC2."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the cited reference 'Chen et al., 2023' correspond to a "
            "real, identifiable publication supporting the attributed content?"
        ),
        "verification_performed": (
            "Systematic PubMed searches via NCBI E-utilities and the PubMed "
            "web interface: (1) Chen[au] AND 2023[dp] AND (CB2 OR cannabinoid) "
            "AND microglia AND pain -> 1 hit, Chen L et al., 'Assessing "
            "Cannabidiol as a Therapeutic Agent for Preventing and "
            "Alleviating Alzheimer's Disease Neurodegeneration', Cells 2023 "
            "(off-topic: cannabidiol / Alzheimer's, not CB2 / microglia / "
            "pain). (2) Chen[au] AND 2023[dp] AND cannabinoid AND microglia "
            "-> 7 hits, no Chen-first-author paper on CB2 / microglia / pain. "
            "(3) Chen[au] AND 2023[dp] AND fibromyalgia -> 25 hits, none a "
            "Chen-first-author cannabinoid / CB2 / microglia paper. "
            "(4) Chen[au] AND 2023[dp] AND CB2 AND pain -> 1 hit, first "
            "author Nan, not Chen. Web searches likewise surfaced the only "
            "on-topic 2023 review, 'Microglial Cannabinoid CB2 Receptors in "
            "Pain Modulation' (first author Xu, not Chen), and 'Spinal "
            "cannabinoid receptor 2 activation alleviates neuropathic pain "
            "by regulating microglia' (first author Zhou, not Chen). "
            "PubMed query URLs: "
            "https://pubmed.ncbi.nlm.nih.gov/?term=Chen%5Bau%5D+AND+2023%5Bdp%5D+AND+cannabinoid+AND+microglia ; "
            "https://pubmed.ncbi.nlm.nih.gov/?term=Chen%5Bau%5D+AND+2023%5Bdp%5D+AND+fibromyalgia"
        ),
        "finding": (
            "No publication matching 'Chen et al., 2023' on CB2 / microglia / "
            "neuroinflammatory pain or fibromyalgia could be identified. The "
            "two genuinely on-topic 2023 papers have first authors Xu and "
            "Zhou, not Chen. This is the evidence underlying SC3's failure: "
            "one of the three references named in the claim is unverifiable, "
            "a pattern consistent with a misattributed or fabricated "
            "(hallucinated) citation. It does NOT break the proof and is not "
            "forced to UNDETERMINED, because SC1 and SC2 are independently "
            "established and SC3's failure is already captured by the "
            "compound verdict. breaks_proof is therefore False."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the claim require a source that specifically proposed "
            "CB2-on-microglia modulation as a fibromyalgia treatment?"
        ),
        "verification_performed": (
            "Re-read the claim's grammar and searched for CB2 / microglia "
            "proposals targeting fibromyalgia specifically ('CB2 receptor "
            "microglia fibromyalgia', 'endocannabinoid system fibromyalgia')."
        ),
        "finding": (
            "Under the natural reading, 'including chronic widespread pain "
            "syndromes such as fibromyalgia' names fibromyalgia as an "
            "INSTANCE of the neuroinflammatory pain states for which the "
            "mechanism is proposed - a reading bridged by SC2, which "
            "establishes that fibromyalgia is characterized by central "
            "sensitization and microglial activation. The claim does not "
            "assert that a specific study tested CB2-on-microglia agonism in "
            "fibromyalgia patients, and this proof does not rely on one. A "
            "stricter reading (a dedicated fibromyalgia-specific CB2/microglia "
            "proposal) would be only weakly supported; that scope limitation "
            "is disclosed here and in proof.md. It does not change the "
            "verdict, which already reports SC3's failure."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 10. VERDICT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    any_unverified = any(cr["status"] != "verified" for cr in citation_results.values())
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif claim_holds:
        base_verdict = "DISPROVED" if is_disproof else "PROVED"
    elif n_holding > 0:
        base_verdict = "PARTIALLY VERIFIED"
    else:
        base_verdict = "UNDETERMINED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)

    # ----- Human-readable trace -----
    print("=" * 72)
    print("PROOF: CB2-on-microglia / neuroinflammatory pain / fibromyalgia claim")
    print("=" * 72)
    print("\nCLAIM:\n  " + CLAIM_NATURAL)
    print("\nCITED-REFERENCE INVENTORY (SC3):")
    for r in CITED_REFERENCES:
        print("  - " + r)
    print("\nCITATION VERIFICATION:")
    for k, cr in citation_results.items():
        print(f"  {k:14s} {cr['status']:10s} (mode={cr.get('fetch_mode')})")
    print("\nSUB-CLAIM RESULTS:")
    print(f"  SC1  verified sources = {n_sc1}/3  -> holds={sc1_holds}")
    print(f"  SC2  verified sources = {n_sc2}/3  -> holds={sc2_holds}")
    print(f"  SC3  resolved citations = {n_sc3}/3 -> holds={sc3_holds}")
    print(f"\n  Sub-claims holding: {n_holding}/{n_total}")
    print(f"  Compound (all hold): {claim_holds}")
    print(f"  Any citation unverified: {any_unverified}")
    print(f"\nVERDICT: {verdict}")
    print("=" * 72)

    # ----- Structured proof summary -----
    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    def _sub_of(ef_key):
        if ef_key in sc1_keys:
            return "SC1"
        if ef_key in sc2_keys:
            return "SC2"
        return "SC3"

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
            sub_claim=_sub_of(ef_key),
        )
        builder.set_verification(
            fid,
            status=cr.get("status", "unknown"),
            method=cr.get("method", "full_quote") or "full_quote",
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

    sc1_fact_ids = [fid for fid, info in FACT_REGISTRY.items()
                    if fid.startswith("B") and info["key"] in sc1_keys]
    sc2_fact_ids = [fid for fid, info in FACT_REGISTRY.items()
                    if fid.startswith("B") and info["key"] in sc2_keys]
    sc3_fact_ids = [fid for fid, info in FACT_REGISTRY.items()
                    if fid.startswith("B") and info["key"] in sc3_keys]

    builder.add_computed_fact(
        "A1", label="SC1 verified-source count",
        method=f"count(verified SC1 citations) = {n_sc1}",
        result=n_sc1, depends_on=sc1_fact_ids, sub_claim="SC1",
    )
    builder.add_computed_fact(
        "A2", label="SC2 verified-source count",
        method=f"count(verified SC2 citations) = {n_sc2}",
        result=n_sc2, depends_on=sc2_fact_ids, sub_claim="SC2",
    )
    builder.add_computed_fact(
        "A3", label="SC3 resolved-citation count",
        method=(f"count(cited references resolving to a real publication) "
                f"= {n_sc3}; the claim names 3 references, so n_sc3 < 3 "
                f"means at least one citation is unverifiable"),
        result=n_sc3, depends_on=sc3_fact_ids, sub_claim="SC3",
    )

    builder.add_cross_check(
        description="SC1: independent peer-reviewed sources for the CB2/microglia mechanism",
        fact_ids=sc1_fact_ids,
        n_sources_consulted=len(sc1_keys),
        n_sources_verified=n_sc1,
        sources={k: citation_results[k]["status"] for k in sc1_keys},
        independence_note=("Three separate publications, distinct author groups, "
                           "spanning 2009-2023; no shared authorship and no COI "
                           "with a commercial subject."),
        coi_flags=sc1_coi_flags,
        agreement=sc1_holds,
    )
    builder.add_cross_check(
        description="SC2: independent peer-reviewed sources for fibromyalgia neuro-immune features",
        fact_ids=sc2_fact_ids,
        n_sources_consulted=len(sc2_keys),
        n_sources_verified=n_sc2,
        sources={k: citation_results[k]["status"] for k in sc2_keys},
        independence_note=("A 2025 narrative review, a 2019 multi-site PET primary "
                           "study, and a 2024 pathophysiology review - distinct "
                           "author groups; collectively cover microglial activation "
                           "and central sensitization."),
        coi_flags=sc2_coi_flags,
        agreement=sc2_holds,
    )
    builder.add_cross_check(
        description="SC3: do the three references named in the claim resolve to real publications?",
        fact_ids=sc3_fact_ids,
        n_sources_consulted=3,
        n_sources_verified=n_sc3,
        sources={k: citation_results[k]["status"] for k in sc3_keys},
        independence_note=("Two of the three named references resolve and verify "
                           "(Cabral & Griffin-Thomas 2009; Stella 2010). The third, "
                           "'Chen et al., 2023', was searched systematically in "
                           "PubMed and could not be identified - see adversarial "
                           "check AC3. n_sc3 = 2 < 3."),
        coi_flags=sc3_coi_flags,
        agreement=sc3_holds,
    )

    builder.add_sub_claim_result(
        id="SC1", n_confirming=n_sc1,
        threshold=CLAIM_FORMAL["sub_claims"][0]["threshold"], holds=sc1_holds,
    )
    builder.add_sub_claim_result(
        id="SC2", n_confirming=n_sc2,
        threshold=CLAIM_FORMAL["sub_claims"][1]["threshold"], holds=sc2_holds,
    )
    builder.add_sub_claim_result(
        id="SC3", n_confirming=n_sc3,
        threshold=CLAIM_FORMAL["sub_claims"][2]["threshold"], holds=sc3_holds,
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
        sc1_holds=sc1_holds,
        sc2_holds=sc2_holds,
        sc3_holds=sc3_holds,
        unidentified_citation="Chen et al., 2023",
    )
    builder.set_extra("verdict_note", (
        "PARTIALLY VERIFIED: the two scientific propositions (SC1, SC2) are "
        "verified and well-supported; the citation-integrity sub-claim (SC3) "
        "fails because one of the three references the claim names, "
        "'Chen et al., 2023', could not be identified as a real publication."
    ))
    builder.emit()
