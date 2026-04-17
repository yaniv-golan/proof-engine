"""
Proof: Presenting empirical spreadsheet observations as universal theorems violates
       the hypothetico-deductive method as defined by mainstream philosophy of science.
Generated: 2026-04-07

Proof direction: PROVE — three independent authoritative sources confirm the
hypothetico-deductive method requires steps (falsifiability, reasoning beyond
observation, pre-specified hypotheses) that this practice omits.
"""
import json
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "Presenting empirical spreadsheet observations as universal theorems violates "
    "the hypothetico-deductive method as defined by mainstream philosophy of science."
)
CLAIM_FORMAL = {
    "subject": "Presenting empirical spreadsheet observations as universal theorems",
    "property": (
        "violates the hypothetico-deductive method as defined by mainstream "
        "philosophy of science"
    ),
    "operator": ">=",
    "operator_note": (
        "The claim asserts a factual violation: the practice of presenting empirical "
        "spreadsheet observations as universal theorems omits steps that the "
        "hypothetico-deductive (HD) method requires. We count independent authoritative "
        "sources that define HD method requirements (falsifiability, reasoning beyond "
        "observation, pre-specified hypotheses) which this practice structurally omits. "
        "A threshold of 3 is used to require broad consensus across distinct philosophical "
        "and methodological traditions. "
        "Entailment note: the cited sources define general requirements of the scientific "
        "method / HD method. None specifically names 'spreadsheet observations presented "
        "as theorems.' The entailment bridge is: (1) the HD method requires steps X, Y, Z; "
        "(2) presenting observations as universal theorems without hypothesis formation, "
        "falsifiability testing, or pre-specified analysis omits X, Y, Z; therefore "
        "(3) the practice violates the HD method. This inference is logically valid but "
        "requires the author-reasoning bridge documented here. "
        "Formalization scope: 'universal theorem' is interpreted strictly — a claim of "
        "deductive necessity holding without exception, not a statistical regularity or "
        "empirical generalization. 'Violates' means the practice omits one or more "
        "requirements that the HD method mandates. The proof does not address whether "
        "the practice might be valid under non-HD frameworks (e.g., pure inductivism); "
        "adversarial check 1 addresses this limitation."
    ),
    "threshold": 3,
    "proof_direction": "prove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_britannica_popper",
        "label": (
            "Britannica: Popper's falsifiability criterion — scientific theories "
            "must be falsifiable in principle"
        ),
    },
    "B2": {
        "key": "source_sep_scientific_method",
        "label": (
            "Stanford Encyclopedia of Philosophy: scientific method requires "
            "reasoning beyond observation"
        ),
    },
    "B3": {
        "key": "source_catalog_of_bias",
        "label": (
            "Catalog of Bias: presenting unplanned analyses as prespecified "
            "is a recognized methodological distortion"
        ),
    },
    "A1": {
        "label": (
            "Count of authoritative sources confirming HD method requirements "
            "that the practice omits"
        ),
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS
# Sources that define HD method requirements the practice omits.
empirical_facts = {
    "source_britannica_popper": {
        "quote": (
            "a theory is genuinely scientific only if it is possible in principle to establish "
            "that it is false."
        ),
        "url": "https://www.britannica.com/topic/criterion-of-falsifiability",
        "source_name": "Encyclopaedia Britannica — criterion of falsifiability",
    },
    "source_sep_scientific_method": {
        "quote": (
            "In addition to careful observation, then, scientific method requires a logic as a "
            "system of reasoning for properly arranging, but also inferring beyond, what is known "
            "by observation."
        ),
        "url": "https://plato.stanford.edu/entries/scientific-method/",
        "source_name": "Stanford Encyclopedia of Philosophy — scientific method",
    },
    "source_catalog_of_bias": {
        "quote": (
            "A distortion that arises from presenting the results of unplanned statistical tests "
            "as if they were a fully prespecified course of analyses."
        ),
        "url": "https://catalogofbias.org/biases/data-dredging-bias/",
        "source_name": "Catalog of Bias — data-dredging bias",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CROSS-CHECK (Rule 6)
b1_confirmed = citation_results.get("source_britannica_popper", {}).get("status") in COUNTABLE_STATUSES
b2_confirmed = citation_results.get("source_sep_scientific_method", {}).get("status") in COUNTABLE_STATUSES
b3_confirmed = citation_results.get("source_catalog_of_bias", {}).get("status") in COUNTABLE_STATUSES
cross_check_agreement = b1_confirmed and b2_confirmed and b3_confirmed

# 7. CLAIM EVALUATION — MUST use compare(), never hardcode claim_holds (Rule 7)
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified source count vs proof threshold",
)

# 8. SYSTEM TIME (Rule 3)
PROOF_GENERATION_DATE = date(2026, 4, 7)
today = date.today()
if today == PROOF_GENERATION_DATE:
    date_note = "System date matches proof generation date."
else:
    date_note = f"Proof generated on {PROOF_GENERATION_DATE}; running on {today}."

# 9. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": (
            "Is there a scientific tradition that validates presenting inductive "
            "generalizations from data as universal laws without further testing?"
        ),
        "verification_performed": (
            "Searched 'defense inductive reasoning empirical observations sufficient "
            "universal scientific laws' and 'Bacon inductivism valid science pattern "
            "observation'. Found inductivism (Bacon's model) as a candidate defense."
        ),
        "finding": (
            "Even Bacon's inductivism — the strongest defense of inductive science — "
            "requires systematic collection, replication, and elimination of observer "
            "bias before generalizing. Naive inductivism has been largely discredited "
            "in philosophy of science (Popper, 1934; Hempel, 1965). More importantly, "
            "no form of inductivism endorses presenting patterns as universal 'theorems' "
            "(a term implying deductive necessity) rather than empirical generalizations. "
            "This check does not break the proof but limits the verdict's scope: "
            "the proof establishes violation of the HD method specifically, not all "
            "possible philosophies of science."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does Exploratory Data Analysis (EDA) validate presenting spreadsheet "
            "patterns as scientific findings?"
        ),
        "verification_performed": (
            "Searched 'Tukey exploratory data analysis purpose hypothesis generation "
            "not confirmation'. Reviewed EDA methodology documentation."
        ),
        "finding": (
            "EDA (Tukey 1977) is an explicitly hypothesis-generating practice, not "
            "hypothesis-confirming. Tukey's framework is designed to produce candidate "
            "hypotheses for subsequent testing, not to generate universal theorems. "
            "This supports the proof: the EDA literature itself distinguishes "
            "pattern-finding from universal claims."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could 'math washing' be valid in limited empirical domains like actuarial "
            "science, empirical economics, or physics phenomenology?"
        ),
        "verification_performed": (
            "Searched 'stylized facts empirical economics vs universal law', "
            "'actuarial science empirical observation universal theorem'. Reviewed "
            "terminology used in empirical economic methodology."
        ),
        "finding": (
            "Empirical economics explicitly distinguishes between 'stylized facts' "
            "(regularities observed in data) and 'economic laws' or theorems. "
            "Kaldor (1961) introduced 'stylized facts' precisely because observed "
            "patterns in data do NOT constitute universal theorems without theoretical "
            "grounding. Even in phenomenological physics, empirical regularities "
            "(e.g., Kepler's laws) were only elevated to scientific law status after "
            "being derived from deeper theoretical principles (Newton's mechanics). "
            "No domain endorses presenting data patterns as universal theorems directly."
        ),
        "breaks_proof": False,
    },
]

# 10. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = (
        f"{n_confirmed} sources confirmed (threshold: {CLAIM_FORMAL['threshold']})"
    )

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

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
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {
                "description": (
                    "Three independent authoritative sources from distinct traditions "
                    "(encyclopedic philosophy, academic philosophy reference, medical/scientific "
                    "methodology catalog) each confirm a different HD method requirement that "
                    "the practice omits: falsifiability (B1), reasoning beyond observation (B2), "
                    "pre-specified hypotheses (B3)."
                ),
                "values_compared": [
                    citation_results.get("source_britannica_popper", {}).get("status", "unknown"),
                    citation_results.get("source_sep_scientific_method", {}).get("status", "unknown"),
                    citation_results.get("source_catalog_of_bias", {}).get("status", "unknown"),
                ],
                "agreement": cross_check_agreement,
                "coi_flags": [],
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirmed": n_confirmed,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
            "proof_direction": "prove",
            "any_unverified_citations": any_unverified,
            "date_note": date_note,
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
