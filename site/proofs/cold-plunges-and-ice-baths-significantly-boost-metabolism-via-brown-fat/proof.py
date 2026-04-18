"""
Proof: Cold plunges and ice baths significantly boost metabolism via brown fat
activation and aid long-term fat loss.
Generated: 2026-03-31
"""
import json
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

from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "Cold plunges and ice baths significantly boost metabolism via brown fat "
    "activation and aid long-term fat loss."
)
CLAIM_FORMAL = {
    "subject": "Cold water immersion (cold plunges, ice baths)",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "activates brown adipose tissue (BAT) in humans",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC1 holds if at least 2 independent peer-reviewed sources confirm "
                "cold exposure activates brown adipose tissue (BAT) in humans. "
                "Threshold 2 chosen because human BAT activation by cold is a "
                "well-replicated PET/CT imaging finding; 2 independent publications "
                "are the minimum to rule out isolated or non-reproducible results."
            ),
        },
        {
            "id": "SC2",
            "property": "BAT activation increases resting metabolic rate/energy expenditure",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC2 holds if at least 2 independent peer-reviewed sources confirm "
                "BAT activation measurably increases resting metabolic rate or total "
                "energy expenditure. 'Significantly boosts metabolism' in the original "
                "claim is interpreted as a peer-reviewed-documented, directionally "
                "confirmed increase. The word 'significantly' implies a meaningful "
                "increase — reviewers note the whole-body effect may be modest "
                "(Carpentier et al. 2018: 'lower end of clinically relevant'), but the "
                "directional finding is well-supported. Threshold 2 for the same reason as SC1."
            ),
        },
        {
            "id": "SC3",
            "property": "aids long-term fat loss (sustained fat mass reduction) in humans",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC3 holds if at least 2 independent peer-reviewed sources confirm "
                "cold water immersion produces long-term fat mass reduction in humans. "
                "'Long-term' is interpreted as sustained reductions in fat mass or "
                "body weight over weeks to months in controlled human studies — not "
                "merely increased energy expenditure or acute fat mobilisation. "
                "Threshold 2 required; a single small study would be insufficient. "
                "This is the critical sub-claim most disputed in the literature. "
                "Counter-evidence: Scott & Fuller (IJMS 2023) state ICE 'does not "
                "consistently lower body weight or fat mass'; Marlatt & Ravussin "
                "(Curr Obes Rep 2017) state BAT contribution 'is unlikely to cause "
                "weight loss'; Scheele & Nielsen (Redox Biol 2017) state 'substantial "
                "reductions in body weight following BAT activation has not yet been "
                "shown in humans'."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "All three sub-claims must hold for the compound claim to be PROVED. "
        "The claim implies: cold plunges activate BAT (SC1) AND this boosts "
        "metabolism (SC2) AND this produces long-term fat loss (SC3). If any "
        "sub-claim fails, the verdict is PARTIALLY VERIFIED with explanation of "
        "which parts are supported and which are not."
    ),
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "sc1_source_a", "label": "SC1: Ouellet et al. (JCI 2012) — cold activates BAT oxidative metabolism"},
    "B2": {"key": "sc1_source_b", "label": "SC1: van der Lans et al. (JCI 2013) — cold acclimation increases BAT activity"},
    "B3": {"key": "sc1_source_c", "label": "SC1: Scott & Fuller (IJMS 2023) — ICE consistently increases BAT activity"},
    "B4": {"key": "sc2_source_a", "label": "SC2: Scheele & Nielsen (Redox Biol 2017) — BAT activation increases resting metabolic rate"},
    "B5": {"key": "sc2_source_b", "label": "SC2: Scheele & Wolfrum (Endocrine Rev 2020) — BAT activation increases metabolic rate"},
    "B6": {"key": "sc2_source_c", "label": "SC2: Carpentier et al. (Front Endocrinol 2018) — cold doubles/triples BAT oxidative capacity"},
    "B7": {"key": "sc3_source_a", "label": "SC3: Esperland et al. (Int J Circumpolar Health 2022) — CWI may reduce adipose tissue (hedged)"},
    "A1": {"label": "SC1 verified source count", "method": None, "result": None},
    "A2": {"label": "SC2 verified source count", "method": None, "result": None},
    "A3": {"label": "SC3 verified source count", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — grouped by sub-claim
# SC1: cold exposure activates BAT
# SC2: BAT activation increases metabolic rate
# SC3: cold plunges aid long-term fat loss (only one hedged supporting source found;
#       multiple sources actively contradict this sub-claim — see adversarial_checks)
empirical_facts = {
    "sc1_source_a": {
        "quote": (
            "we demonstrated cold-induced activation of oxidative metabolism in BAT, "
            "but not in adjoining skeletal muscles and subcutaneous adipose tissue. "
            "This activation was associated with an increase in total energy expenditure."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/22269323/",
        "source_name": "Ouellet et al., J Clin Invest 2012 (PubMed 22269323)",
    },
    "sc1_source_b": {
        "quote": (
            "we show that a 10-day cold acclimation protocol in humans increases BAT activity "
            "in parallel with an increase in nonshivering thermogenesis (NST)."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/23867626/",
        "source_name": "van der Lans et al., J Clin Invest 2013 (PubMed 23867626)",
    },
    "sc1_source_c": {
        "quote": (
            "ICE consistently increases the activity of brown adipose tissue (BAT) "
            "and transitions white adipose tissue to a phenotype more in line with BAT."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/38203217/",
        "source_name": "Scott & Fuller, Int J Mol Sci 2023 (PubMed 38203217)",
    },
    "sc2_source_a": {
        "quote": (
            "Activation of brown adipose tissue (BAT) in adult humans increase glucose "
            "and fatty acid clearance as well as resting metabolic rate, whereas a prolonged "
            "elevation of BAT activity improves insulin sensitivity."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/28431377/",
        "source_name": "Scheele & Nielsen, Redox Biol 2017 (PubMed 28431377)",
    },
    "sc2_source_b": {
        "quote": (
            "acute activation increases metabolic rate. Brown adipose tissue (BAT) recruitment "
            "occurs during cold acclimation and includes secretion of factors, known as batokines, "
            "which target several different cell types within BAT."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/31638161/",
        "source_name": "Scheele & Wolfrum, Endocrine Rev 2020 (PubMed 31638161)",
    },
    "sc2_source_c": {
        "quote": (
            "BAT thermogenesis is efficiently recruited upon repeated cold exposure, doubling to "
            "tripling its total oxidative capacity, with reciprocal reduction of muscle thermogenesis."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/30131768/",
        "source_name": "Carpentier et al., Front Endocrinol 2018 (PubMed 30131768)",
    },
    "sc3_source_a": {
        "quote": (
            "CWI seems to reduce and/or transform body adipose tissue, as well as reduce "
            "insulin resistance and improve insulin sensitivity."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/36137565/",
        "source_name": "Esperland et al., Int J Circumpolar Health 2022 (PubMed 36137565)",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
print("Verifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)
for key, result in citation_results.items():
    print(f"  {key}: {result.get('status')} ({result.get('method', 'n/a')})")

# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]
sc3_keys = [k for k in empirical_facts if k.startswith("sc3_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc3 = sum(1 for k in sc3_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

print(f"\n  SC1 confirmed: {n_sc1} / {len(sc1_keys)}")
print(f"  SC2 confirmed: {n_sc2} / {len(sc2_keys)}")
print(f"  SC3 confirmed: {n_sc3} / {len(sc3_keys)}")

# 6. PER-SUB-CLAIM EVALUATION
sc1_holds = compare(n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
                    label="SC1: cold exposure activates BAT")
sc2_holds = compare(n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
                    label="SC2: BAT activation increases metabolic rate")
sc3_holds = compare(n_sc3, ">=", CLAIM_FORMAL["sub_claims"][2]["threshold"],
                    label="SC3: cold exposure aids long-term fat loss")

# 7. COMPOUND EVALUATION
n_holding = sum([sc1_holds, sc2_holds, sc3_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# 8. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": (
            "Do peer-reviewed reviews conclude that cold exposure causes "
            "meaningful weight or fat loss in humans?"
        ),
        "verification_performed": (
            "Searched PubMed and Google Scholar for 'cold water immersion fat loss humans', "
            "'ice bath weight loss evidence', 'cold exposure fat mass reduction controlled trial'. "
            "Found Scott & Fuller (IJMS 2023): 'While ICE does not consistently lower body weight "
            "or fat mass, there does seem to be evidence for ICE as a positive modulator of the "
            "metabolic consequences of obesity.' Also found Marlatt & Ravussin (Curr Obes Rep 2017): "
            "'BAT contributes a small amount to overall energy metabolism which is unlikely to cause "
            "weight loss. There is no convincing evidence yet to indicate that BAT may be a viable "
            "pharmaceutical target for body weight loss.' And Scheele & Nielsen (Redox Biol 2017): "
            "'substantial reductions in body weight following BAT activation has not yet been shown "
            "in humans.'"
        ),
        "finding": (
            "Three independent peer-reviewed reviews explicitly state that cold-induced BAT "
            "activation does not consistently produce measurable fat or weight loss in humans. "
            "This directly contradicts SC3 and is the strongest counter-evidence found."
        ),
        "breaks_proof": False,  # SC3 already fails threshold; adversarial finding confirms verdict
    },
    {
        "question": (
            "Is the whole-body metabolic boost from BAT activation 'significant' "
            "in clinical or practical terms?"
        ),
        "verification_performed": (
            "Searched for 'brown fat energy expenditure magnitude humans', "
            "'BAT thermogenesis clinical relevance', 'brown adipose tissue weight loss humans'. "
            "Carpentier et al. (Front Endocrinol 2018) state BAT's contribution is 'at the lower "
            "end of what would be potentially clinically relevant if chronically sustained.' "
            "Marlatt & Ravussin (Curr Obes Rep 2017) state BAT is 'unlikely to cause weight loss.' "
            "No source found claiming the boost is large enough to drive fat loss on its own."
        ),
        "finding": (
            "The metabolic increase from BAT activation is directionally confirmed (SC2 holds) "
            "but reviewers consistently characterize the magnitude as modest — at the lower end "
            "of clinical relevance. The 'significantly' qualifier in the original claim is "
            "therefore overstated: the boost is real but not large enough to drive fat loss. "
            "This does not break SC2 (directional increase is documented) but reinforces the "
            "failure of SC3."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there evidence that cold water immersion protocols used in practice "
            "(brief plunges) differ from the prolonged cold-room exposures studied in labs?"
        ),
        "verification_performed": (
            "Searched for 'cold plunge vs cold room BAT activation', "
            "'ice bath brown fat activation protocol', "
            "'cold water immersion duration BAT'. "
            "Scott & Fuller (IJMS 2023) note: 'The majority of the current literature on ICE "
            "is based on rodent models where animals are housed in cold rooms, which does not "
            "reflect protocols likely to be implemented in humans such as cold water immersion.' "
            "Most human BAT studies use sustained cold-air exposure (16-18°C for hours), not "
            "brief cold-water immersion (minutes in ~10-15°C water)."
        ),
        "finding": (
            "The research base for BAT activation (SC1) and metabolic boost (SC2) uses "
            "sustained cold-air protocols that differ from typical cold plunge/ice bath practice. "
            "Human cold-water immersion is shorter and involves different thermal dynamics. "
            "Whether brief cold plunges achieve comparable BAT activation is not well established. "
            "This is an important ecological validity concern but does not definitively refute SC1 "
            "or SC2 since Scott & Fuller (2023) does include CWI-adjacent ICE protocols."
        ),
        "breaks_proof": False,
    },
]

# 9. VERDICT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        # Mixed: some sub-claims hold, others don't → PARTIALLY VERIFIED
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    else:
        # No sub-claims met threshold
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified sc1 citations) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1)
    FACT_REGISTRY["A2"]["method"] = f"count(verified sc2 citations) = {n_sc2}"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2)
    FACT_REGISTRY["A3"]["method"] = f"count(verified sc3 citations) = {n_sc3}"
    FACT_REGISTRY["A3"]["result"] = str(n_sc3)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: for qualitative proofs, record citation status per B-type fact
    extractions = {}
    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        cr = citation_results.get(ef_key, {})
        extractions[fid] = {
            "value": cr.get("status", "unknown"),
            "value_in_quote": cr.get("status") in COUNTABLE_STATUSES,
            "quote_snippet": empirical_facts[ef_key]["quote"][:80],
        }

    summary = {
        "fact_registry": {fid: dict(info) for fid, info in FACT_REGISTRY.items()},
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {
                "description": "SC1: independent sources consulted for cold → BAT activation",
                "n_sources_consulted": len(sc1_keys),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in sc1_keys},
                "independence_note": (
                    "Sources from three different publications: "
                    "J Clin Invest 2012, J Clin Invest 2013, Int J Mol Sci 2023 — "
                    "independently measured using PET/CT imaging and review methodology."
                ),
            },
            {
                "description": "SC2: independent sources consulted for BAT → metabolic rate",
                "n_sources_consulted": len(sc2_keys),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in sc2_keys},
                "independence_note": (
                    "Sources from three different publications: "
                    "Redox Biol 2017, Endocrine Rev 2020, Front Endocrinol 2018 — "
                    "independent review and experimental findings."
                ),
            },
            {
                "description": "SC3: sources consulted for cold → long-term fat loss",
                "n_sources_consulted": len(sc3_keys),
                "n_sources_verified": n_sc3,
                "sources": {k: citation_results[k]["status"] for k in sc3_keys},
                "independence_note": (
                    "Only one hedged supportive source found (Esperland 2022). "
                    "Multiple independent reviews explicitly contradict SC3 — see adversarial_checks."
                ),
            },
        ],
        "sub_claim_results": [
            {
                "id": "SC1",
                "n_confirming": n_sc1,
                "threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"],
                "holds": sc1_holds,
            },
            {
                "id": "SC2",
                "n_confirming": n_sc2,
                "threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"],
                "holds": sc2_holds,
            },
            {
                "id": "SC3",
                "n_confirming": n_sc3,
                "threshold": CLAIM_FORMAL["sub_claims"][2]["threshold"],
                "holds": sc3_holds,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_holding": n_holding,
            "n_total": n_total,
            "claim_holds": claim_holds,
            "sc1_holds": sc1_holds,
            "sc2_holds": sc2_holds,
            "sc3_holds": sc3_holds,
        },
        "generator": {
            "name": "proof-engine",
            "version": open(os.path.join(PROOF_ENGINE_ROOT, "VERSION")).read().strip(),
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
