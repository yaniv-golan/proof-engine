"""
Proof: AI-generated code has fewer security vulnerabilities than typical human-written code
Generated: 2026-03-29
Verdict: DISPROVED — Multiple independent studies consistently find AI-generated code
contains MORE security vulnerabilities than human-written code, not fewer.
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
CLAIM_NATURAL = "AI-generated code has fewer security vulnerabilities than typical human-written code"
CLAIM_FORMAL = {
    "subject": "AI-generated code (from major LLMs such as GPT-4, Claude, Copilot, DeepSeek)",
    "property": "security vulnerability rate compared to human-written code",
    "operator": ">=",
    "operator_note": (
        "To DISPROVE the claim, we need >= 3 independent, verified sources showing "
        "AI-generated code has EQUAL OR MORE vulnerabilities than human-written code. "
        "'Fewer' is interpreted as a strict inequality: if AI code has the same or more "
        "vulnerabilities, the claim is false. We use proof_direction='disprove' with "
        "threshold=3, meaning 3+ verified sources rejecting the claim suffices for DISPROVED."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "source_stanford", "label": "Stanford CCS 2023: AI assistant users wrote significantly less secure code"},
    "B2": {"key": "source_veracode", "label": "Veracode 2025: 45% of AI code contains OWASP vulnerabilities"},
    "B3": {"key": "source_coderabbit", "label": "CodeRabbit Dec 2025: AI PRs have 1.7x more issues, security up to 2.74x higher"},
    "B4": {"key": "source_register", "label": "The Register/Georgia Tech 2026: 74 CVEs from AI-authored code tracked"},
    "A1": {"label": "Verified source count rejecting the claim", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm AI code is NOT safer)
empirical_facts = {
    "source_stanford": {
        "source_name": "Perry et al., ACM CCS 2023 (Stanford University)",
        "url": "https://arxiv.org/html/2211.03622v3",
        "quote": (
            "Overall, we find that participants who had access to an AI assistant "
            "wrote significantly less secure code than those without access to an assistant."
        ),
    },
    "source_veracode": {
        "source_name": "Help Net Security / Veracode 2025 GenAI Code Security Report",
        "url": "https://www.helpnetsecurity.com/2025/08/07/create-ai-code-security-risks/",
        "quote": (
            "in 45 percent of all test cases, LLMs produced code containing "
            "vulnerabilities aligned with the OWASP Top 10"
        ),
    },
    "source_coderabbit": {
        "source_name": "CodeRabbit State of AI vs Human Code Generation Report (Dec 2025)",
        "url": "https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report",
        "quote": (
            "Security issues were up to 2.74x higher"
        ),
    },
    "source_register": {
        "source_name": "The Register / Georgia Tech SSLab (Mar 2026)",
        "url": "https://www.theregister.com/2026/03/26/ai_coding_assistant_not_more_secure/",
        "quote": (
            "Claude Code alone now appears in more than 4 percent of public commits on GitHub. "
            "If AI were truly responsible for only 74 out of 50,000 public vulnerabilities, "
            "that would imply AI-generated code is orders of magnitude safer than human-written code. "
            "We do not think that is credible."
        ),
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
print(f"  Confirmed sources rejecting the claim: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — MUST use compare()
claim_holds = compare(n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                      label="verified source count vs threshold")

# 7. ADVERSARIAL CHECKS (Rule 5)
# Search for evidence SUPPORTING the claim (that AI code is safer)
adversarial_checks = [
    {
        "question": "Are there any peer-reviewed studies showing AI-generated code has FEWER vulnerabilities than human code?",
        "verification_performed": (
            "Searched: 'AI generated code more secure than human code evidence study 2025 2026'. "
            "Reviewed top 10 results from Google. No study found that concludes AI-generated code "
            "is more secure overall. All results either show AI code has more vulnerabilities or "
            "discuss the security risks of AI-generated code."
        ),
        "finding": (
            "No peer-reviewed study found showing AI-generated code has fewer vulnerabilities. "
            "The Veracode Spring 2026 update title explicitly states: 'Despite Claims, AI Models "
            "Are Still Failing Security.' The Register's March 2026 article is titled: 'Using AI "
            "to code does not mean your code is more secure.'"
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could AI code be safer in specific narrow contexts even if worse overall?",
        "verification_performed": (
            "Searched for domain-specific studies where AI might outperform humans on security. "
            "Some sources note that AI models are improving at syntax correctness (50% to 95% "
            "since 2023), but Veracode found security pass rates have remained flat at 45-55% "
            "regardless of model generation. No narrow domain was identified where AI code is "
            "demonstrably safer."
        ),
        "finding": (
            "While AI coding accuracy has improved, security-specific performance has not. "
            "The claim is stated broadly ('AI-generated code'), not for a specific narrow domain, "
            "so the broad evidence applies."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Do the studies use outdated AI models that no longer reflect current capabilities?",
        "verification_performed": (
            "Checked recency of sources: Stanford study used Codex (2023), Veracode tested 100+ "
            "LLMs including current models (2025), CodeRabbit analyzed real-world GitHub PRs (Dec 2025), "
            "Georgia Tech tracked CVEs through March 2026. The most recent sources (2025-2026) test "
            "current-generation models and still find elevated vulnerability rates."
        ),
        "finding": (
            "Sources span 2023-2026, with the most recent using current models. "
            "The pattern of AI code having more vulnerabilities is consistent across model generations. "
            "This does not break the proof."
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
                "description": "Multiple independent sources consulted across different research methodologies",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from independent institutions using different methodologies: "
                    "(1) Stanford — controlled user study with 47 participants, "
                    "(2) Veracode — automated testing of 100+ LLMs across 80 tasks, "
                    "(3) CodeRabbit — analysis of 470 real-world GitHub PRs, "
                    "(4) Georgia Tech — CVE tracking across open-source ecosystem. "
                    "No two sources share methodology or data."
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
            "version": open(os.path.join(PROOF_ENGINE_ROOT, "VERSION")).read().strip(),
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print(f"\n  VERDICT: {verdict}")
    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
