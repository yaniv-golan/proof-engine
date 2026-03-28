"""
Proof: Heavier objects fall faster than lighter objects even in a perfect vacuum.
Generated: 2026-03-28
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

# --- STRUCTURAL IMPORTS ---
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare
from sympy import symbols, simplify

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "Heavier objects fall faster than lighter objects even in a perfect vacuum."
CLAIM_FORMAL = {
    "subject": "Objects of different mass in a perfect vacuum (no air resistance)",
    "property": "Whether heavier objects have greater gravitational acceleration than lighter objects",
    "operator": ">=",
    "operator_note": (
        "The claim asserts that heavier objects fall faster, meaning their acceleration "
        "due to gravity would be greater than that of lighter objects. We interpret 'fall faster' "
        "as 'have greater free-fall acceleration.' In Newtonian mechanics, F = mg and a = F/m = g, "
        "so acceleration is independent of mass. The claim requires a_heavy > a_light, but physics "
        "shows a_heavy == a_light == g. This is a disproof: we seek >= 3 authoritative sources "
        "confirming that all objects fall at the same rate in a vacuum regardless of mass."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "A1": {"label": "Newtonian derivation: acceleration = g, independent of mass", "method": None, "result": None},
    "B1": {"key": "source_a", "label": "NASA Glenn: all objects free fall with same acceleration"},
    "B2": {"key": "source_b", "label": "NASA Science: Apollo 15 hammer-feather drop"},
    "B3": {"key": "source_c", "label": "Wikipedia: Weak Equivalence Principle"},
}

# 3. TYPE A FACT: Mathematical derivation from Newton's Second Law
# F_gravity = m * g (gravitational force)
# F = m * a (Newton's Second Law)
# Therefore: m * a = m * g => a = g (mass cancels)
m1, m2, g_sym = symbols('m1 m2 g', positive=True)

# For object 1 (heavy): F1 = m1 * g, a1 = F1 / m1
a1 = simplify((m1 * g_sym) / m1)

# For object 2 (light): F2 = m2 * g, a2 = F2 / m2
a2 = simplify((m2 * g_sym) / m2)

# Both reduce to g — acceleration is independent of mass
print("=== TYPE A: Newtonian Derivation ===")
print(f"  Object 1 (mass m1): F = m1*g, acceleration a1 = m1*g / m1 = {a1}")
print(f"  Object 2 (mass m2): F = m2*g, acceleration a2 = m2*g / m2 = {a2}")
print(f"  a1 == a2 == g: {a1 == a2 == g_sym}")
print(f"  Conclusion: acceleration is independent of mass; all objects fall at rate g.")

masses_cancel = a1 == a2 == g_sym
assert masses_cancel, "Mathematical derivation failed: accelerations should equal g"

# 4. EMPIRICAL FACTS — sources that REJECT the claim (confirm it's false)
empirical_facts = {
    "source_a": {
        "quote": "So all objects, regardless of size or shape or weight, free fall with the same acceleration.",
        "url": "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/free-fall-without-air-resistance/",
        "source_name": "NASA Glenn Research Center",
    },
    "source_b": {
        "quote": "Because they were essentially in a vacuum, there was no air resistance and the feather fell at the same rate as the hammer",
        "url": "https://science.nasa.gov/resource/the-apollo-15-hammer-feather-drop/",
        "source_name": "NASA Science",
    },
    "source_c": {
        "quote": "in a gravitational field the acceleration of a test particle is independent of its properties, including its rest mass",
        "url": "https://en.wikipedia.org/wiki/Equivalence_principle",
        "source_name": "Wikipedia: Equivalence Principle",
    },
}

# 5. CITATION VERIFICATION (Rule 2)
print("\n=== CITATION VERIFICATION ===")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 6. COUNT SOURCES WITH VERIFIED CITATIONS
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 7. CLAIM EVALUATION — enough sources confirm the claim is FALSE
claim_holds = compare(n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                      label="verified source count vs threshold")

# 8. ADVERSARIAL CHECKS (Rule 5) — search for sources SUPPORTING the claim
adversarial_checks = [
    {
        "question": "Is there any credible scientific evidence that heavier objects fall faster in a vacuum?",
        "verification_performed": (
            "Searched 'heavier objects fall faster vacuum gravitational attraction evidence'. "
            "All results (Physics Forums, NASA, University of Illinois, UCSB ScienceLine, "
            "Britannica) unanimously confirm objects fall at the same rate in a vacuum."
        ),
        "finding": (
            "No credible scientific source supports the claim. The only nuance found is the "
            "two-body problem: a heavier object attracts the Earth slightly more (reducing the "
            "distance faster), but this effect is negligible (~10^-25 for everyday objects) and "
            "does not contradict the equivalence principle. All standard physics references state "
            "that in a uniform gravitational field, acceleration is independent of mass."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Did Aristotle's theory (heavier objects fall faster) have any experimental support?",
        "verification_performed": (
            "Searched 'Aristotle heavier objects fall faster disproved Galileo'. "
            "Aristotle's claim was based on everyday observation with air resistance, not "
            "vacuum conditions. Galileo's experiments (c. 1590) and the Apollo 15 demonstration "
            "(1971) definitively disproved it in vacuum conditions."
        ),
        "finding": (
            "Aristotle's theory was based on observations in air (where drag affects lighter "
            "objects more) and was never validated for vacuum conditions. It has been thoroughly "
            "disproved by experiment."
        ),
        "breaks_proof": False,
    },
]

# 9. VERDICT AND STRUCTURED OUTPUT
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
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = "Symbolic algebra (sympy): a = F/m = mg/m = g for any mass m"
    FACT_REGISTRY["A1"]["result"] = "a1 == a2 == g (acceleration independent of mass)"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

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
                "description": "Mathematical derivation (Type A) independently confirms empirical sources (Type B)",
                "math_result": "a = g for all masses (sympy symbolic simplification)",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Type A derivation uses only Newton's laws (no external sources). "
                    "Type B sources are from independent institutions: NASA Glenn Research Center, "
                    "NASA Science (Apollo 15 mission data), and Wikipedia (summarizing Einstein's "
                    "equivalence principle). The mathematical proof and empirical evidence are "
                    "fully independent lines of reasoning."
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
            "math_derivation": "a = g (mass cancels in F=ma=mg)",
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
