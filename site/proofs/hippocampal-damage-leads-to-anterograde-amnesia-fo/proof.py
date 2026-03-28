"""
Proof: Hippocampal damage leads to anterograde amnesia for new episodic memories
       and does not impair skill learning or retrograde memories from early life.
Generated: 2026-03-27

Canonical evidence: Patient H.M. (Henry Molaison, 1926–2008), who underwent
bilateral medial temporal lobe resection in 1953, remains the most thoroughly
documented case of hippocampal amnesia in neuroscience literature.

Three sub-claims are evaluated independently:
  SC1: Hippocampal damage causes anterograde amnesia for new episodic memories.
  SC2: Hippocampal damage does NOT impair skill/procedural learning.
  SC3: Hippocampal damage does NOT impair retrograde memories from early life.

All three must be confirmed for the compound claim to be PROVED.
"""

import json
from datetime import date
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.smart_extract import verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "Hippocampal damage leads to anterograde amnesia for new episodic memories "
    "and does not impair skill learning or retrograde memories from early life."
)

CLAIM_FORMAL = {
    "subject": "Bilateral hippocampal damage (canonical case: patient H.M., Henry Molaison)",
    "property": (
        "Three jointly required sub-claims: "
        "(SC1) causes anterograde amnesia for new episodic memories; "
        "(SC2) does not impair procedural/skill learning; "
        "(SC3) does not impair retrograde memories from early life"
    ),
    "operator": ">=",
    "operator_note": (
        "The compound claim is interpreted as TRUE if all three sub-claims are each confirmed "
        "by at least 2 independent sources (threshold=2 per sub-claim). This threshold was chosen "
        "because neuroscience consensus claims require corroboration from more than one source, "
        "but the core findings from H.M. are well-replicated across many studies. "
        "SC1 is proved by sources documenting inability to encode new episodic/declarative memories. "
        "SC2 is proved by sources documenting preserved motor skill learning (e.g., mirror tracing). "
        "SC3 is proved by sources documenting intact autobiographical memories predating surgery. "
        "The overall compound claim fails if ANY sub-claim fails to meet its threshold, or if "
        "adversarial checks reveal credible disconfirming evidence against any sub-claim."
    ),
    "threshold": 2,
    "proof_direction": "affirm",
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {
        "key": "source_a",
        "label": "Squire LR (2009) The Legacy of Patient H.M. for Neuroscience, Neuron 61(1):6-9 (PMC2649674) — SC1",
    },
    "B2": {
        "key": "source_b",
        "label": "Wikipedia: Henry Molaison — anterograde amnesia and procedural memory — SC1, SC2",
    },
    "B3": {
        "key": "source_c",
        "label": "Simply Psychology: Patient H.M. Case Study — early life memories — SC3",
    },
    "B4": {
        "key": "source_d",
        "label": "BrainFacts.org: Patient Zero — What We Learned from H.M. — SC2",
    },
    "B5": {
        "key": "source_e",
        "label": "Wikipedia: Anterograde amnesia — H.M. childhood memories — SC3",
    },
    "A1": {
        "label": "SC1 confirming source count (anterograde amnesia for new episodic memories)",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "SC2 confirming source count (skill/procedural learning preserved)",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "SC3 confirming source count (early-life retrograde memories intact)",
        "method": None,
        "result": None,
    },
    "A4": {
        "label": "All three sub-claims meet threshold (compound claim holds)",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
# ---------------------------------------------------------------------------
empirical_facts = {
    # SC1: Anterograde amnesia for new episodic memories
    "source_a": {
        "quote": (
            "He forgot daily events nearly as fast as they occurred, "
            "apparently in the absence of any general intellectual loss."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2649674/",
        "source_name": "Squire LR (2009) The Legacy of Patient H.M. for Neuroscience, Neuron (PMC)",
    },
    # SC1 + SC2: Anterograde amnesia confirmed; procedural memory noted as intact
    "source_b": {
        "quote": (
            "Molaison developed severe anterograde amnesia: "
            "although his working memory and procedural memory were intact"
        ),
        "url": "https://en.wikipedia.org/wiki/Henry_Molaison",
        "source_name": "Wikipedia: Henry Molaison",
    },
    # SC3: Early-life retrograde memories intact
    "source_c": {
        "quote": (
            "he could still recall childhood memories, but he had difficulty "
            "remembering events that happened during the years immediately "
            "preceding the surgery"
        ),
        "url": "https://www.simplypsychology.org/henry-molaison-patient-hm.html",
        "source_name": "Simply Psychology: Patient H.M. Case Study",
    },
    # SC2: Skill/motor learning preserved
    "source_d": {
        "quote": (
            "he had retained the ability to form non-declarative memories, "
            "which took the form of improvement in motor skills."
        ),
        "url": "https://www.brainfacts.org/thinking-sensing-and-behaving/learning-and-memory/2013/patient-zero-what-we-learned-from-hm",
        "source_name": "BrainFacts.org: Patient Zero — What We Learned from H.M.",
    },
    # SC3: Early-life retrograde memories intact (independent second source)
    "source_e": {
        "quote": "He could remember anything from his childhood.",
        "url": "https://en.wikipedia.org/wiki/Anterograde_amnesia",
        "source_name": "Wikipedia: Anterograde amnesia",
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. KEYWORD EXTRACTION (Rule 1)
#    verify_extraction(keyword, quote_string, fact_id) → bool
#    Confirms keyword is present in the quote string (sanity check Rule 1).
#    Citation verification (Rule 2) separately confirms quote appears on page.
# ---------------------------------------------------------------------------

# --- SC1: Anterograde amnesia for new episodic memories ---
sc1_a = verify_extraction("forgot daily events", empirical_facts["source_a"]["quote"], "B1")
sc1_b = verify_extraction("anterograde amnesia", empirical_facts["source_b"]["quote"], "B2")

# --- SC2: Skill/procedural learning preserved ---
sc2_b = verify_extraction("procedural memory", empirical_facts["source_b"]["quote"], "B2")
sc2_d = verify_extraction("motor skills", empirical_facts["source_d"]["quote"], "B4")

# --- SC3: Early-life retrograde memories intact ---
sc3_c = verify_extraction("childhood memories", empirical_facts["source_c"]["quote"], "B3")
sc3_e = verify_extraction("childhood", empirical_facts["source_e"]["quote"], "B5")

# ---------------------------------------------------------------------------
# 6. SOURCE COUNTS PER SUB-CLAIM (Rule 6)
#    Each sub-claim uses independently sourced evidence.
# ---------------------------------------------------------------------------
confirmations_sc1 = [sc1_a, sc1_b]         # B1 (PMC), B2 (Wikipedia HM)
confirmations_sc2 = [sc2_b, sc2_d]         # B2 (Wikipedia HM), B4 (BrainFacts)
confirmations_sc3 = [sc3_c, sc3_e]         # B3 (Simply Psychology), B5 (Wikipedia AA)

n_sc1 = sum(1 for c in confirmations_sc1 if c)
n_sc2 = sum(1 for c in confirmations_sc2 if c)
n_sc3 = sum(1 for c in confirmations_sc3 if c)

# ---------------------------------------------------------------------------
# 7. CLAIM EVALUATION (Rule 7)
#    All three sub-claims must meet threshold independently.
# ---------------------------------------------------------------------------
sc1_holds = compare(n_sc1, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                    label="SC1 (anterograde amnesia): confirming sources")
sc2_holds = compare(n_sc2, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                    label="SC2 (skill learning preserved): confirming sources")
sc3_holds = compare(n_sc3, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                    label="SC3 (early-life memories intact): confirming sources")

all_sub_claims_count = sum(1 for h in [sc1_holds, sc2_holds, sc3_holds] if h)
claim_holds = compare(all_sub_claims_count, "==", 3,
                      label="Compound claim: all three sub-claims confirmed")

# ---------------------------------------------------------------------------
# 8. ADVERSARIAL CHECKS (Rule 5)
#    Searches for independent counter-evidence against each sub-claim.
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Does Multiple Trace Theory (Nadel & Moscovitch 1997) show the hippocampus "
            "IS required for early-life memories, contradicting SC3?"
        ),
        "verification_performed": (
            "Searched for 'multiple trace theory hippocampus remote memories early life'. "
            "Reviewed MTT arguments against standard consolidation theory."
        ),
        "finding": (
            "MTT argues the hippocampus is always engaged in rich episodic memory retrieval, "
            "even for remote memories. However, (1) H.M.'s preserved childhood memories are an "
            "empirical finding independent of theoretical interpretation; (2) even MTT proponents "
            "acknowledge that semantic (gist-level) memories become hippocampus-independent; "
            "(3) the temporal gradient of retrograde amnesia (older = better preserved) is "
            "well-documented regardless of which theory is correct. MTT represents theoretical "
            "disagreement, not empirical refutation of SC3."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does hippocampal damage impair certain types of skill or procedural learning, "
            "contradicting SC2?"
        ),
        "verification_performed": (
            "Searched for 'hippocampus procedural learning impaired skill', "
            "'hippocampus sequence learning SRTT', 'hippocampus motor skill'."
        ),
        "finding": (
            "Some studies show hippocampus involvement in probabilistic sequence learning "
            "(serial reaction time tasks with probabilistic elements) and spatial navigation "
            "learning. However, classic motor skill learning (mirror tracing, rotor pursuit, "
            "weight bias) is consistently preserved after hippocampal damage across multiple "
            "patients and studies. The claim's reference to 'skill learning' aligns with this "
            "classical finding, which is the domain Milner established in H.M. The sequence "
            "learning nuance does not break the proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could H.M.'s anterograde amnesia (SC1) be caused by amygdala or entorhinal "
            "cortex removal rather than hippocampal damage specifically?"
        ),
        "verification_performed": (
            "Searched for 'selective hippocampal damage anterograde amnesia amygdala "
            "entorhinal HM patient RB'. Reviewed subsequent amnesic patient cases."
        ),
        "finding": (
            "Subsequent research on patients with selective hippocampal damage confirmed the "
            "hippocampus-specific role: Patient R.B. (Zola-Morgan et al. 1986) had isolated "
            "CA1 damage and showed clear anterograde amnesia; patients with hippocampal atrophy "
            "show similar profiles. Amygdala damage contributes to emotional memory and fear "
            "conditioning but not the classic episodic anterograde amnesia. The hippocampus is "
            "the critical structure for SC1."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there evidence that remote spatial memories from early life are impaired "
            "after hippocampal damage, undermining SC3?"
        ),
        "verification_performed": (
            "Found paper: 'Impaired Remote Spatial Memory After Hippocampal Lesions Despite "
            "Extensive Training Beginning Early in Life' (PMC2754396). Reviewed its scope."
        ),
        "finding": (
            "This paper (and others) shows that hippocampal lesions impair remote SPATIAL "
            "memories even acquired early in life, which may contradict a broad reading of SC3. "
            "However, the claim specifically concerns 'retrograde memories from early life' in the "
            "context of H.M.'s autobiographical/episodic memories — the domain in which the "
            "classical finding holds. Spatial navigation memory may be a distinct case. Both the "
            "Wikipedia and Simply Psychology sources confirm H.M.'s childhood autobiographical "
            "memories were preserved. The spatial memory nuance refines but does not refute SC3 "
            "as stated for autobiographical early-life memories."
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
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

    # Populate A-type fact results
    FACT_REGISTRY["A1"]["method"] = f"sum(confirmations_sc1) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1)
    FACT_REGISTRY["A2"]["method"] = f"sum(confirmations_sc2) = {n_sc2}"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2)
    FACT_REGISTRY["A3"]["method"] = f"sum(confirmations_sc3) = {n_sc3}"
    FACT_REGISTRY["A3"]["result"] = str(n_sc3)
    FACT_REGISTRY["A4"]["method"] = "sc1_holds AND sc2_holds AND sc3_holds"
    FACT_REGISTRY["A4"]["result"] = str(claim_holds)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": "forgot daily events",
            "value_in_quote": sc1_a,
            "quote_snippet": empirical_facts["source_a"]["quote"][:80],
        },
        "B2_sc1": {
            "value": "anterograde amnesia",
            "value_in_quote": sc1_b,
            "quote_snippet": empirical_facts["source_b"]["quote"][:80],
        },
        "B2_sc2": {
            "value": "procedural memory",
            "value_in_quote": sc2_b,
            "quote_snippet": empirical_facts["source_b"]["quote"][:80],
        },
        "B3": {
            "value": "childhood memories",
            "value_in_quote": sc3_c,
            "quote_snippet": empirical_facts["source_c"]["quote"][:80],
        },
        "B4": {
            "value": "motor skills",
            "value_in_quote": sc2_d,
            "quote_snippet": empirical_facts["source_d"]["quote"][:80],
        },
        "B5": {
            "value": "childhood",
            "value_in_quote": sc3_e,
            "quote_snippet": empirical_facts["source_e"]["quote"][:80],
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
                "description": "SC1 independent sources (PMC Squire 2009 + Wikipedia HM)",
                "n_sources": len(confirmations_sc1),
                "n_confirming": n_sc1,
                "agreement": n_sc1 == len(confirmations_sc1),
            },
            {
                "description": "SC2 independent sources (Wikipedia HM + BrainFacts)",
                "n_sources": len(confirmations_sc2),
                "n_confirming": n_sc2,
                "agreement": n_sc2 == len(confirmations_sc2),
            },
            {
                "description": "SC3 independent sources (Simply Psychology + Wikipedia AA)",
                "n_sources": len(confirmations_sc3),
                "n_confirming": n_sc3,
                "agreement": n_sc3 == len(confirmations_sc3),
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_anterograde_amnesia_sources": n_sc1,
            "sc2_skill_learning_preserved_sources": n_sc2,
            "sc3_early_life_memories_intact_sources": n_sc3,
            "threshold_per_sub_claim": CLAIM_FORMAL["threshold"],
            "all_sub_claims_hold": claim_holds,
            "any_citation_unverified": any_unverified,
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
