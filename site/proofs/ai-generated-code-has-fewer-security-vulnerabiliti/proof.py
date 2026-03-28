"""
Proof: AI-generated code has fewer security vulnerabilities than typical human-written code
Generated: 2026-03-28

Strategy: DISPROOF via Qualitative Consensus.
Three independent peer-reviewed studies (IEEE S&P 2022, ACM CCS 2023, IEEE ISSRE 2025)
find that AI-generated / AI-assisted code has MORE or EQUAL vulnerabilities compared to
human-written code — directly contradicting the claim.
proof_direction = 'disprove': empirical_facts contain sources that REJECT the claim.
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = "AI-generated code has fewer security vulnerabilities than typical human-written code"

CLAIM_FORMAL = {
    "subject": "AI-generated code",
    "property": "security vulnerability rate relative to typical human-written code",
    "operator": ">=",
    "operator_note": (
        "The claim asserts AI code has FEWER vulnerabilities than human code. "
        "We disprove this using proof_direction='disprove': we collect at least 3 independent "
        "peer-reviewed studies whose findings REJECT the claim (showing AI code has MORE or EQUAL "
        "vulnerabilities). The operator '>=' counts verified sources against threshold=3. "
        "A source counts if its quote was found on the page (status verified or partial). "
        "'Fewer' is interpreted strictly: the claim is false if credible independent research "
        "consistently finds AI code is not safer. We use the conservative threshold of 3 "
        "independent studies from different research groups and venues."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {
        "key": "pearce_2022",
        "label": (
            "Pearce et al. 2022 (IEEE S&P): Copilot generated ~40% vulnerable programs "
            "across 89 security-sensitive scenarios"
        ),
    },
    "B2": {
        "key": "perry_2023",
        "label": (
            "Perry et al. 2023 (ACM CCS): AI-assisted participants wrote significantly "
            "less secure code than unassisted participants"
        ),
    },
    "B3": {
        "key": "cotroneo_2025",
        "label": (
            "Cotroneo et al. 2025 (IEEE ISSRE): Large-scale study (500k+ samples) finds "
            "AI-generated code contains more high-risk security vulnerabilities than human code"
        ),
    },
    "A1": {
        "label": "Count of independently verified sources rejecting the claim",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
# Sources that REJECT the claim (confirm AI code is NOT fewer-vulnerability than human code).
# Adversarial sources (those that support the claim) go in adversarial_checks only.
# ---------------------------------------------------------------------------
empirical_facts = {
    "pearce_2022": {
        "quote": (
            "In total, we produce 89 different scenarios for Copilot to complete, "
            "producing 1,689 programs. Of these, we found approximately 40% to be vulnerable."
        ),
        "url": "https://arxiv.org/abs/2108.09293",
        "source_name": (
            "Pearce et al. 2022, 'Asleep at the Keyboard? Assessing the Security of "
            "GitHub Copilot's Code Contributions', IEEE Symposium on Security and Privacy 2022"
        ),
    },
    "perry_2023": {
        "quote": (
            "participants who had access to an AI assistant wrote significantly less secure "
            "code than those without access to an assistant"
        ),
        "url": "https://arxiv.org/html/2211.03622v3",
        "source_name": (
            "Perry et al. 2023, 'Do Users Write More Insecure Code with AI Assistants?', "
            "ACM CCS 2023"
        ),
    },
    "cotroneo_2025": {
        "quote": (
            "AI-generated code also contains more high-risk security vulnerabilities"
        ),
        "url": "https://arxiv.org/abs/2508.21634",
        "source_name": (
            "Cotroneo et al. 2025, 'Human-Written vs. AI-Generated Code: A Large-Scale "
            "Study of Defects, Vulnerabilities, and Complexity', IEEE ISSRE 2025"
        ),
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. COUNT SOURCES WITH VERIFIED CITATIONS
# A source counts if its quote was found on the page (verified or partial).
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# ---------------------------------------------------------------------------
# 6. CLAIM EVALUATION (Rule 7 — use compare(), never hardcode)
# ---------------------------------------------------------------------------
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified source count vs threshold",
)

# ---------------------------------------------------------------------------
# 7. ADVERSARIAL CHECKS (Rule 5)
# These document searches for evidence that SUPPORTS the original claim
# (i.e., evidence that AI code IS more secure). Performed before writing this proof.
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Does any peer-reviewed study find AI-generated code has FEWER security "
            "vulnerabilities than human-written code, contradicting this disproof?"
        ),
        "verification_performed": (
            "Searched 'AI generated code fewer security vulnerabilities than human peer-reviewed', "
            "'Copilot code more secure than human developer', and reviewed Sandoval et al. 2023 "
            "(USENIX Security) 'Lost at C: A User Study on the Security Implications of LLM Code "
            "Assistants'. Sandoval et al. found that AI-assisted C programmers produced critical "
            "security bugs at a rate no greater than ~10% more than controls in a narrow "
            "low-level C pointer/array task. Some metrics showed the assisted group had fewer bugs."
        ),
        "finding": (
            "Sandoval et al. 2023 found limited/neutral security impact in one narrow scenario "
            "(low-level C). This does NOT show AI code has categorically fewer vulnerabilities — "
            "it shows one specific task where the difference was small. No study was found claiming "
            "AI-generated code is generally more secure than human-written code across broad domains. "
            "The Sandoval finding does not break the disproof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do Perry et al. and Pearce et al. study different things (AI-assisted humans vs. "
            "pure AI-generated code), making the comparison inconsistent?"
        ),
        "verification_performed": (
            "Reviewed the scope of all three sources. Pearce et al. generates code directly from "
            "GitHub Copilot (100% AI-generated). Cotroneo et al. generates code from ChatGPT, "
            "DeepSeek-Coder, and Qwen-Coder without human editing (100% AI-generated). "
            "Perry et al. studies human developers who USE an AI assistant — they write the final "
            "code but with AI suggestions. The claim uses the broad phrase 'AI-generated code', "
            "which in practice encompasses both scenarios."
        ),
        "finding": (
            "Two of three sources (B1 Pearce, B3 Cotroneo) study purely AI-generated code. "
            "B2 Perry et al. studies AI-assisted coding — still directly relevant to the claim "
            "as stated, since developers widely use AI assistants to generate code. "
            "The mixed scope does not undermine the disproof: even in the broader AI-assisted "
            "interpretation of the claim, the evidence shows more vulnerabilities, not fewer."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Are Pearce et al.'s results biased by cherry-picked security-sensitive prompts "
            "not representative of typical code generation?"
        ),
        "verification_performed": (
            "Reviewed methodology: Pearce et al. explicitly targeted CWE Top-25 vulnerability "
            "scenarios, which could inflate vulnerability rates. However, Cotroneo et al. 2025 "
            "used over 500,000 general-purpose Python and Java code samples — not adversarially "
            "selected for security sensitivity — and still found AI code had more high-risk "
            "security vulnerabilities. Searched for 'Copilot code representative sample security' "
            "to check for rebuttal papers; found none contradicting the general trend."
        ),
        "finding": (
            "Pearce et al.'s focused-prompt methodology is a legitimate limitation for that "
            "study alone. However, Cotroneo et al.'s large-scale general study independently "
            "confirms the finding on 500k+ samples without security-focused prompting. "
            "The convergence of findings across different methodologies (targeted security "
            "prompts vs. general-purpose coding) strengthens the disproof."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 8. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
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
        verdict = (
            "DISPROVED (with unverified citations)"
            if is_disproof
            else "PROVED (with unverified citations)"
        )
    elif not claim_holds:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = str(n_confirmed)

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
                    "Three independent studies from different research groups and venues "
                    "consulted, all finding AI code is NOT more secure than human code"
                ),
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources from three different research groups: "
                    "(1) NYU — Pearce et al. 2022, IEEE S&P; "
                    "(2) Stanford/UCSD/UIUC — Perry et al. 2023, ACM CCS; "
                    "(3) University of Naples — Cotroneo et al. 2025, IEEE ISSRE. "
                    "Different methodologies: security-targeted prompts (B1), "
                    "user study with diverse tasks (B2), large-scale general sampling (B3). "
                    "Time span 2022-2025 covers multiple generations of AI coding tools."
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
            "proof_direction": "disprove",
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
