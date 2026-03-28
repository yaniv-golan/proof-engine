"""
Proof: Computers had a hidden "math glitch" preventing division by zero until it was patched in 2026.
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
CLAIM_NATURAL = 'Computers had a hidden "math glitch" preventing division by zero until it was patched in 2026.'

CLAIM_FORMAL = {
    "subject": "division-by-zero handling in computers",
    "property": "was a hidden, unintentional 'math glitch' that was patched in 2026",
    "operator": ">=",
    "operator_note": (
        "The claim makes two assertions: "
        "(SC1) division-by-zero prevention was a hidden, unintentional 'math glitch'; "
        "(SC2) this was patched in 2026. "
        "Both must be true for the claim to hold. "
        "The claim is refuted if: 3+ independent verified sources document that division-by-zero "
        "behavior has been intentionally defined (not a glitch) for decades before 2026, "
        "AND zero credible sources document a '2026 patch' for division-by-zero. "
        "Threshold of 3 sources is conservative given this is a well-documented technical standard. "
        "proof_direction='disprove': empirical_facts contain sources that refute the claim; "
        "disproof_established = (n_refuting >= threshold); claim_holds = NOT disproof_established."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "ieee754_wiki", "label": "Wikipedia: IEEE 754 — division by zero is a defined exception type, not a glitch"},
    "B2": {"key": "divbyzero_wiki", "label": "Wikipedia: Division by zero — IEEE arithmetic defines well-specified, deterministic behavior"},
    "B3": {"key": "osdev_exceptions", "label": "OSDev Wiki: x86 Divide Error (#DE) — standard hardware exception since early x86"},
    "A1": {"label": "Count of verified sources refuting the claim (SC1 + SC2)", "method": None, "result": None},
    "A2": {"label": "Claim holds evaluation: disproof established => original claim does not hold", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REFUTE the claim (confirm it is false)
# These establish: (a) division-by-zero behavior is intentional design, not a glitch,
# and (b) this was standardized decades before 2026.
empirical_facts = {
    "ieee754_wiki": {
        "quote": "The standard defines five exception types: invalid operation, division by zero, overflow, underflow, and inexact.",
        "url": "https://en.wikipedia.org/wiki/IEEE_754",
        "source_name": "Wikipedia: IEEE 754 floating-point standard",
    },
    "divbyzero_wiki": {
        "quote": "In IEEE arithmetic, division of 0/0 or infinity/infinity results in NaN, but otherwise division always produces a well-defined result.",
        "url": "https://en.wikipedia.org/wiki/Division_by_zero",
        "source_name": "Wikipedia: Division by zero",
    },
    "osdev_exceptions": {
        "quote": "The Division Error occurs when dividing any number by 0 using the DIV or IDIV instruction, or when the division result is too large to be represented in the destination.",
        "url": "https://wiki.osdev.org/Exceptions",
        "source_name": "OSDev Wiki: x86 Processor Exceptions",
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT VERIFIED REFUTING SOURCES
COUNTABLE_STATUSES = ("verified", "partial")
n_refuting = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Refuting sources verified: {n_refuting} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION (Rule 7 — use compare(), never hardcode)
# Disproof established when 3+ independent sources confirm division-by-zero is intentional design
disproof_established = compare(
    n_refuting, ">=", CLAIM_FORMAL["threshold"],
    label="SC: verified refuting sources >= threshold (disproof established)"
)
# The original claim holds only if the disproof is NOT established
claim_holds = not disproof_established

# 7. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Does any credible source document a '2026 patch' for division-by-zero in CPUs or IEEE 754?",
        "verification_performed": (
            "Searched the web for 'division by zero patch 2026', 'CPU divide by zero fix 2026', "
            "'IEEE 754 division by zero bug patch 2026', 'computers math glitch division zero 2026 patch'. "
            "Also reviewed Microsoft March 2026 Patch Tuesday (BleepingComputer) which listed 79 CVEs — "
            "none related to arithmetic division-by-zero behavior."
        ),
        "finding": (
            "No credible source documents any 2026 patch addressing division-by-zero behavior. "
            "Microsoft's March 2026 Patch Tuesday addressed SQL Server, .NET, and Windows security vulnerabilities; "
            "no arithmetic behavior was changed. No IEEE 754 revision was issued in 2026. "
            "The '2026 patch' component of the claim is entirely fabricated."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could there be an obscure CPU microcode update in 2026 affecting division by zero?",
        "verification_performed": (
            "Searched for 'Intel errata division by zero 2026', 'AMD microcode division by zero 2026', "
            "'ARM Cortex divide by zero errata 2026'. Reviewed processor errata reports from major vendors."
        ),
        "finding": (
            "No hardware errata from Intel, AMD, or ARM in 2026 pertains to division-by-zero behavior. "
            "The x86 #DE (divide error) exception has been stable since the Intel 8086 (1978). "
            "The 1994 Intel Pentium FDIV bug was a floating-point division *accuracy* bug for specific operand "
            "pairs — not a division-by-zero issue — and was resolved in 1994, not 2026."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Was division-by-zero handling ever described as a 'hidden glitch' in mainstream computer science?",
        "verification_performed": (
            "Searched for 'division by zero glitch CPU hidden', 'division by zero unintentional computer design', "
            "'division by zero bug computer history'. Reviewed IEEE 754-1985 historical background."
        ),
        "finding": (
            "Division-by-zero raising a hardware exception (#DE) has been intentional since at least the "
            "Intel 8086 (1978) and IBM S/360 (1964). IEEE 754-1985 explicitly standardized floating-point "
            "division-by-zero as returning ±infinity (or NaN for 0/0), with an optional exception flag. "
            "No mainstream CS literature characterizes this as a 'hidden glitch'."
        ),
        "breaks_proof": False,
    },
]

# 8. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    if not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    elif claim_holds and not any_unverified:
        verdict = "UNDETERMINED"  # unexpected: refutation threshold not met
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = "sum(status in ('verified','partial') for refuting sources)"
    FACT_REGISTRY["A1"]["result"] = f"{n_refuting} of {len(empirical_facts)} sources verified"
    FACT_REGISTRY["A2"]["method"] = "claim_holds = NOT(n_refuting >= threshold)"
    FACT_REGISTRY["A2"]["result"] = f"claim_holds = {claim_holds} (disproof_established = {disproof_established})"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": {},
        "cross_checks": [
            {
                "description": "Three independent sources (Wikipedia IEEE 754, Wikipedia Division by zero, OSDev Wiki) each document division-by-zero as intentional, defined behavior",
                "values_compared": [
                    f"ieee754_wiki: {citation_results['ieee754_wiki']['status']}",
                    f"divbyzero_wiki: {citation_results['divbyzero_wiki']['status']}",
                    f"osdev_exceptions: {citation_results['osdev_exceptions']['status']}",
                ],
                "agreement": all(
                    citation_results[k]["status"] in COUNTABLE_STATUSES
                    for k in ["ieee754_wiki", "divbyzero_wiki", "osdev_exceptions"]
                ),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_refuting_sources_verified": n_refuting,
            "disproof_threshold": CLAIM_FORMAL["threshold"],
            "disproof_established": disproof_established,
            "claim_holds": claim_holds,
            "sc1_division_by_zero_intentional": "IEEE 754 (1985) and x86 #DE exception (1978) document intentional, defined behavior",
            "sc2_no_2026_patch": "Web search confirms no 2026 patch for division-by-zero in any CPU, OS, or standard",
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
