"""
Proof: Quantum entanglement enables the transmission of usable information
faster than the speed of light when the distant parties pre-agree on a
measurement basis.
Generated: 2026-03-28
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "Quantum entanglement enables the transmission of usable information "
    "faster than the speed of light when the distant parties pre-agree on "
    "a measurement basis."
)
CLAIM_FORMAL = {
    "subject": "quantum entanglement with pre-agreed measurement basis",
    "property": "number of independent authoritative sources confirming this is impossible",
    "operator": ">=",
    "operator_note": (
        "This is a DISPROOF. The claim asserts entanglement enables FTL information "
        "transfer with a pre-agreed measurement basis. The no-communication theorem "
        "in quantum mechanics proves this is impossible: local measurement statistics "
        "are independent of the distant party's measurement choice, so no information "
        "can be encoded or decoded superluminally regardless of any pre-agreed protocol. "
        "We disprove the claim by finding >= 3 independent authoritative sources that "
        "confirm entanglement cannot transmit usable information FTL. The threshold of 3 "
        "reflects broad scientific consensus from independent institutions."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "source_a",
        "label": "Wikipedia: No-communication theorem — theorem statement",
    },
    "B2": {
        "key": "source_b",
        "label": "Caltech Science Exchange — entanglement does not enable FTL communication",
    },
    "B3": {
        "key": "source_c",
        "label": "Wikipedia: Faster-than-light communication — scientific consensus",
    },
    "B4": {
        "key": "source_d",
        "label": "QSNP (EU Quantum Flagship) — debunking FTL entanglement myth",
    },
    "A1": {
        "label": "Verified source count meeting disproof threshold",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm it is false)
empirical_facts = {
    "source_a": {
        "quote": (
            "It asserts that during the measurement of an entangled quantum state, "
            "it is impossible for one observer to transmit information to another "
            "observer, regardless of their spatial separation."
        ),
        "url": "https://en.wikipedia.org/wiki/No-communication_theorem",
        "source_name": "Wikipedia — No-communication theorem",
    },
    "source_b": {
        "quote": (
            "Experiments have shown that this is not true, nor can quantum physics "
            "be used to send faster-than-light communications."
        ),
        "url": "https://scienceexchange.caltech.edu/topics/quantum-science-explained/entanglement",
        "source_name": "Caltech Science Exchange — Quantum Entanglement",
    },
    "source_c": {
        "quote": (
            "The current scientific consensus is that faster-than-light communication "
            "is not possible, and to date it has not been achieved in any experiment."
        ),
        "url": "https://en.wikipedia.org/wiki/Faster-than-light_communication",
        "source_name": "Wikipedia — Faster-than-light communication",
    },
    "source_d": {
        "quote": (
            "The catch is that we are not actually sending any information."
        ),
        "url": "https://qsnp.eu/debunking-quantum-myths-entanglement-allows-faster-than-light-communication/",
        "source_name": "QSNP (EU Quantum Flagship) — Debunking quantum myths",
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

# 6. CLAIM EVALUATION — MUST use compare(), never hardcode claim_holds
claim_holds = compare(
    n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
    label="verified source count vs disproof threshold"
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# For a disproof, adversarial checks search for sources that SUPPORT the claim
adversarial_checks = [
    {
        "question": (
            "Is there any credible peer-reviewed physics paper demonstrating "
            "FTL information transfer via entanglement with pre-agreed measurement bases?"
        ),
        "verification_performed": (
            "Searched for: 'pre-agreed measurement basis entanglement superluminal "
            "signaling loophole scheme'. Reviewed results from arXiv, Physics Forums, "
            "Stanford Encyclopedia of Philosophy, and Wikipedia."
        ),
        "finding": (
            "No credible peer-reviewed source demonstrates FTL information transfer "
            "via entanglement. Proposed schemes (e.g., Gao Shan 2003) have been "
            "refuted. The no-communication theorem is mathematically proven under "
            "standard quantum mechanics. All search results confirm the impossibility."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does pre-agreeing on a measurement basis create any loophole "
            "in the no-communication theorem?"
        ),
        "verification_performed": (
            "Searched for: 'quantum entanglement FTL information transfer pre-agreed "
            "measurement basis impossibility'. Reviewed Physics Forums discussions "
            "and the arXiv paper 2001.08867."
        ),
        "finding": (
            "Pre-agreeing on a measurement basis does not create a loophole. "
            "The no-communication theorem proves that Bob's local measurement "
            "statistics are completely independent of Alice's measurement choice, "
            "regardless of any prior agreement. Each party sees random 50/50 "
            "outcomes locally; correlations only emerge when results are compared "
            "via a classical (light-speed-limited) channel."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Has any experiment ever demonstrated superluminal information transfer "
            "using quantum entanglement?"
        ),
        "verification_performed": (
            "Searched for: 'quantum entanglement enables faster than light "
            "communication claim debunked physics'. Reviewed phys.org, Caltech, "
            "and QSNP articles."
        ),
        "finding": (
            "No experiment has ever demonstrated FTL information transfer. "
            "Wikipedia's Faster-than-light communication article states: "
            "'The current scientific consensus is that faster-than-light "
            "communication is not possible, and to date it has not been "
            "achieved in any experiment.'"
        ),
        "breaks_proof": False,
    },
]

# 8. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif claim_holds and not any_unverified:
        verdict = "DISPROVED" if is_disproof else "PROVED"
    elif claim_holds and any_unverified:
        verdict = ("DISPROVED (with unverified citations)" if is_disproof
                   else "PROVED (with unverified citations)")
    elif not claim_holds:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = str(n_confirmed)

    citation_detail = build_citation_detail(
        FACT_REGISTRY, citation_results, empirical_facts
    )

    # Extractions: for qualitative proofs, each B-type fact records citation status
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
                "description": "Multiple independent sources consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {
                    k: citation_results[k]["status"] for k in empirical_facts
                },
                "independence_note": (
                    "Sources are from 4 different institutions/publications: "
                    "Wikipedia (community encyclopedia citing physics literature), "
                    "Caltech (university research institution), "
                    "Wikipedia FTL article (separate article with distinct references), "
                    "QSNP/EU Quantum Flagship (European research consortium). "
                    "All trace to independent primary physics research and the "
                    "mathematically proven no-communication theorem."
                ),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirmed": n_confirmed,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
        },
        "generator": {
            "name": "proof-engine",
            "version": open(
                os.path.join(PROOF_ENGINE_ROOT, "VERSION")
            ).read().strip(),
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
