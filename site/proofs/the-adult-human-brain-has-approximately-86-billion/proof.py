"""
Proof: The adult human brain has approximately 86 billion neurons and an average of
7,000 synapses per neuron, resulting in a total synaptic count exceeding 6 × 10^14.
Generated: 2026-03-27
"""
import json
from datetime import date
import re
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.smart_extract import normalize_unicode, verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare, explain_calc, cross_check

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "The adult human brain has approximately 86 billion neurons and an average of "
    "7,000 synapses per neuron, resulting in a total synaptic count exceeding 6 × 10^14."
)
CLAIM_FORMAL = {
    "subject": "Adult human brain",
    "sub_claims": {
        "SC1": "Neuron count ≈ 86 billion (within ±15% tolerance)",
        "SC2": "Average synapses per neuron ≈ 7,000, applied brain-wide across all neurons",
        "SC3": "Total synaptic count = SC1 × SC2 > 6 × 10^14",
    },
    "operator": ">",
    "operator_note": (
        "'Exceeding 6 × 10^14' means strictly greater than 6.0e14. "
        "The arithmetic (86e9 × 7000 = 6.02e14 > 6e14) is correct given the premises. "
        "However, the 7,000 synapses/neuron figure (SC2) originates from research on "
        "NEOCORTICAL neurons specifically (~20 billion neurons), not all 86 billion brain neurons. "
        "Applying it as a brain-wide average — including the ~69 billion cerebellar granule "
        "cells (which have only 4–5 synapses each) — inflates the estimated total by roughly "
        "3–5×. This makes SC2, as stated for all neurons, unsupported by primary literature. "
        "The compound claim is therefore only PARTIALLY VERIFIED."
    ),
    "threshold": 6e14,
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {
        "key": "source_neurons_a",
        "label": "Herculano-Houzel 2009 (Frontiers Hum Neurosci, PMC2776484): 86B neurons in adult brain",
    },
    "B2": {
        "key": "source_neurons_b",
        "label": "UCLA Brain Research Institute: ~86B neurons, ~100 trillion synapses whole-brain",
    },
    "B3": {
        "key": "source_synapses",
        "label": "BioNumbers BNID 112055 (Harvard/Drachman 2005): 7,000 synapses per neocortical neuron",
    },
    "A1": {
        "label": "SC3 arithmetic: 86e9 × 7,000 = 6.02e14",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "SC3 comparison: 6.02e14 > 6e14",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
# ---------------------------------------------------------------------------
empirical_facts = {
    "source_neurons_a": {
        "quote": (
            "the adult male human brain, at an average of 1.5 kg, has 86 billion neurons "
            "and 85 billion non-neuronal cells"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2776484/",
        "source_name": "Frontiers in Human Neuroscience, Herculano-Houzel 2009 (PubMed Central)",
    },
    "source_neurons_b": {
        "quote": (
            "The human brain contains approximately 86 billion neurons, each forming "
            "thousands of connections, resulting in an estimated 100 trillion synapses."
        ),
        "url": "https://bri.ucla.edu/brain-fact/billions-of-neurons-trillions-of-synapses/",
        "source_name": "UCLA Brain Research Institute, Brain Facts",
    },
    "source_synapses": {
        "quote": (
            "Within the liter and a half of human brain, stereologic studies estimate "
            "that there are approximately 20 billion neocortical neurons, with an average "
            "of 7,000 synaptic connections each"
        ),
        "url": "https://bionumbers.hms.harvard.edu/bionumber.aspx?s=n&v=3&id=112055",
        "source_name": "BioNumbers BNID 112055, Harvard Medical School (citing Drachman 2005, Neurology)",
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. VALUE EXTRACTION (Rule 1) — parse numbers from quote strings
# ---------------------------------------------------------------------------
def extract_billion_neurons(quote, fact_id):
    """Extract N-billion neuron count. Returns count as float (raw neurons, e.g. 86e9)."""
    norm = normalize_unicode(quote)
    match = re.search(r'(\d+)\s+billion\s+neurons', norm)
    if not match:
        raise ValueError(f"[{fact_id}] Could not find 'N billion neurons' in: {quote!r}")
    billions = int(match.group(1))
    verify_extraction(billions, quote, fact_id)
    return float(billions) * 1e9


def extract_synapses_per_neuron(quote, fact_id):
    """Extract synapses-per-neuron average from BioNumbers quote."""
    norm = normalize_unicode(quote)
    match = re.search(r'average of ([\d,]+) synaptic connections', norm)
    if not match:
        raise ValueError(f"[{fact_id}] Could not find synapse count in: {quote!r}")
    val_str = match.group(1).replace(",", "")
    value = float(val_str)
    verify_extraction(int(value), quote, fact_id)
    return value


neurons_a = extract_billion_neurons(empirical_facts["source_neurons_a"]["quote"], "B1")
neurons_b = extract_billion_neurons(empirical_facts["source_neurons_b"]["quote"], "B2")
synapses_per_neuron = extract_synapses_per_neuron(empirical_facts["source_synapses"]["quote"], "B3")

# ---------------------------------------------------------------------------
# 6. CROSS-CHECK (Rule 6): Two independent sources agree on neuron count
# ---------------------------------------------------------------------------
cross_check(
    neurons_a, neurons_b,
    tolerance=0.0,
    mode="absolute",
    label="SC1 neuron count: B1 (Herculano-Houzel) vs B2 (UCLA BRI)",
)

# ---------------------------------------------------------------------------
# 7. COMPUTATION (Rule 7): SC3 arithmetic
# ---------------------------------------------------------------------------
neurons = neurons_a  # primary source
total_synapses = explain_calc(
    "neurons * synapses_per_neuron",
    locals(),
    label="SC3: total synaptic count (86e9 neurons × 7,000 synapses/neuron)",
)
sc3_arithmetic = compare(
    total_synapses, ">", CLAIM_FORMAL["threshold"],
    label="SC3 arithmetic: total_synapses > 6e14",
)

# ---------------------------------------------------------------------------
# 8. SUB-CLAIM VERDICTS
# ---------------------------------------------------------------------------
# SC1: 86 billion neurons — supported by B1 and B2 independently
# Cross-check already passed; use compare() to make this auditable
sc1_holds = compare(neurons_a, ">=", 70e9, label="SC1: neurons_a >= 70e9 (well within ~86B range)")

# SC2: 7,000 synapses per neuron as a BRAIN-WIDE average — NOT supported
# The 7,000 figure (B3) is explicitly for NEOCORTICAL neurons (~20B of 86B total).
# The ~69 billion cerebellar granule cells have only 4–5 synapses each.
# Primary literature whole-brain totals: ~1×10^14 (UCLA BRI) to ~3×10^14, not 6×10^14.
# SC2 is assessed False based on adversarial evidence; no computed equivalent exists.
sc2_applies_to_all_neurons = False  # editorial verdict from adversarial check #2

# SC3: arithmetic holds IF SC1 and SC2 hold; fails because SC2 is false for all neurons
sc3_holds = sc1_holds and sc2_applies_to_all_neurons

# Compound claim holds only if all three sub-claims hold
claim_holds = sc1_holds and sc2_applies_to_all_neurons and sc3_holds

# ---------------------------------------------------------------------------
# 9. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": "Is the 86 billion neuron figure disputed?",
        "verification_performed": (
            "Searched for critiques of Herculano-Houzel's isotropic fractionator method. "
            "Found Goriely (Brain, 2024, PMC11884752) arguing confidence intervals "
            "span ~73–99 billion, not precisely 86 billion. A 2025 rebuttal (Brain, "
            "PMID 39913195) defends the ~86 billion estimate and recommends the phrasing "
            "'around 86 billion neurons'."
        ),
        "finding": (
            "86 billion is the best current estimate. The uncertainty (±8B per Azevedo 2009) "
            "does not undermine SC1. The claim says 'approximately 86 billion', which is accurate."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does the 7,000 synapses/neuron figure apply to ALL brain neurons?",
        "verification_performed": (
            "Read BioNumbers BNID 112055 (Harvard): explicitly says '~20 billion neocortical "
            "neurons, with an average of 7,000 synaptic connections each' — not all 86 billion. "
            "Primary source: Drachman 2005 (Neurology 64:2004), citing Pakkenberg et al. 2003 "
            "for neocortical data. The cerebellum alone contains ~69 billion granule cells with "
            "only 4–5 synapses each (confirmed in multiple neuroanatomy texts). If only neocortical "
            "neurons average 7,000: 20e9 × 7000 = 1.4e14, well below 6e14."
        ),
        "finding": (
            "BREAKS SC2 as stated for ALL neurons. "
            "The 7,000 figure applies to neocortical neurons only. Brain-wide average is far lower "
            "due to the ~69 billion cerebellar granule cells. The compound claim's SC2 premise is "
            "a conflation of neocortical average with whole-brain average."
        ),
        "breaks_proof": True,
    },
    {
        "question": "Do any primary sources report total brain synapses at or above 6×10^14?",
        "verification_performed": (
            "Searched PubMed, PMC, and educational sources for whole-brain synapse estimates. "
            "UCLA BRI (B2): ~100 trillion = 1×10^14. "
            "Pakkenberg et al. 2003 (PMID 12543266): ~0.15×10^15 = 1.5×10^14 (neocortex only). "
            "Tang et al. 2001 (PMID 11418939): ~1.64×10^14 (neocortex). "
            "PMC11423976: 'around 10^14 (100 trillion) synapses in the average adult human brain'. "
            "No primary peer-reviewed source found reporting 6×10^14 for the whole brain."
        ),
        "finding": (
            "No primary source corroborates 6×10^14 as the total synapse count. "
            "Primary literature consistently gives ~1–3×10^14. The 6×10^14 figure arises "
            "from applying the neocortical average (7,000) to all 86 billion neurons — a "
            "methodological error in the original claim."
        ),
        "breaks_proof": True,
    },
]

# ---------------------------------------------------------------------------
# 10. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    # SC1 is proved; SC2 is not supported brain-wide; SC3 arithmetic is correct given
    # the stated premises but those premises are invalid for SC2 applied to all neurons.
    if sc1_holds and not sc2_applies_to_all_neurons:
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = "explain_calc(neurons * synapses_per_neuron)"
    FACT_REGISTRY["A1"]["result"] = f"{total_synapses:.3e}"
    FACT_REGISTRY["A2"]["method"] = "compare(total_synapses, '>', 6e14)"
    FACT_REGISTRY["A2"]["result"] = str(sc3_arithmetic)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": f"{neurons_a:.3e}",
            "value_in_quote": True,
            "quote_snippet": empirical_facts["source_neurons_a"]["quote"][:80],
        },
        "B2": {
            "value": f"{neurons_b:.3e}",
            "value_in_quote": True,
            "quote_snippet": empirical_facts["source_neurons_b"]["quote"][:80],
        },
        "B3": {
            "value": str(synapses_per_neuron),
            "value_in_quote": True,
            "quote_snippet": empirical_facts["source_synapses"]["quote"][:80],
        },
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
                "description": "SC1 neuron count: B1 (Herculano-Houzel 86e9) vs B2 (UCLA BRI 86e9)",
                "values_compared": [str(neurons_a), str(neurons_b)],
                "agreement": neurons_a == neurons_b,
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_neurons": f"{neurons_a:.3e}",
            "sc2_synapses_per_neuron": synapses_per_neuron,
            "sc2_applies_to_all_neurons": sc2_applies_to_all_neurons,
            "sc3_arithmetic_total": f"{total_synapses:.3e}",
            "sc3_arithmetic_holds": sc3_arithmetic,
            "sc3_empirically_supported": False,
            "primary_literature_whole_brain_synapses": "~1e14 to ~3e14",
            "threshold": CLAIM_FORMAL["threshold"],
            "claim_holds": claim_holds,
        },
        "generator": {
            "name": "proof-engine",
            "version": "0.10.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
