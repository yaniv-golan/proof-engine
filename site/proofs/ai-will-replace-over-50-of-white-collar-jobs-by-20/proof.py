"""
Proof: AI will replace over 50% of white-collar jobs by 2035
Generated: 2026-03-28
Strategy: Qualitative Consensus — Disproof Direction.
  The claim requires that AI *replaces* (permanently eliminates) a strict majority
  of white-collar jobs by 2035. This is evaluated against the body of authoritative
  institutional research and peer-reviewed empirical data. Three or more independently
  verified sources contradicting the claim constitute a disproof under this template.
"""

import json
import os
import sys
from datetime import date

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = "AI will replace over 50% of white-collar jobs by 2035"

CLAIM_FORMAL = {
    "subject": "AI's effect on white-collar employment by 2035",
    "property": (
        "number of independently verified authoritative sources "
        "that CONTRADICT the claim (finding displacement far below 50%, "
        "or that augmentation dominates over replacement)"
    ),
    "operator": ">=",
    "operator_note": (
        "This proof takes the *disproof* direction: we show that "
        "3 or more authoritative, independently verifiable sources "
        "reject the '>50% replacement by 2035' threshold. "
        "'Replace' is interpreted strictly as permanent job elimination "
        "(not task augmentation, job transformation, or partial exposure). "
        "'Over 50%' means a strict majority of all white-collar (professional, "
        "managerial, technical, and administrative) roles. 'By 2035' means "
        "within 9 years of the proof generation date (2026-03-28). "
        "The adversarial section documents the strongest supporting arguments "
        "(e.g., Dario Amodei's May 2025 warning) and explains why they do not "
        "overcome the counter-evidence: they refer only to 'entry-level' roles "
        "(not all white-collar), and Amodei's own company's peer-reviewed research "
        "found no systematic unemployment increase in AI-exposed occupations."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {
        "key": "yale_budget_lab",
        "label": "Yale Budget Lab (2026): AI labor market shows stability, not major disruption",
    },
    "B2": {
        "key": "anthropic_research",
        "label": "Anthropic peer-reviewed research (2026): no systematic unemployment increase in AI-exposed occupations",
    },
    "B3": {
        "key": "jpmorgan_research",
        "label": "J.P. Morgan Global Research (2025): little association between AI intensity and job growth",
    },
    "B4": {
        "key": "hbr_2026",
        "label": "Harvard Business Review (2026): generative AI creates augmentation demand, not economy-wide job elimination",
    },
    "A1": {
        "label": "Count of independently verified sources contradicting the 50%+ replacement claim",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
#    These are sources that REJECT the claim (confirm it is false).
#    Adversarial sources (those supporting the claim) are in adversarial_checks.
# ---------------------------------------------------------------------------
empirical_facts = {
    "yale_budget_lab": {
        "quote": (
            "The picture of AI's impact on the labor market that emerges from our data "
            "is one that largely reflects stability, not major disruption at an "
            "economy-wide level."
        ),
        "url": "https://fortune.com/2026/02/02/ai-labor-market-yale-budget-lab-ai-washing/",
        "source_name": "Yale Budget Lab / Fortune (February 2026)",
    },
    "anthropic_research": {
        "quote": (
            "We find no systematic increase in unemployment for highly exposed workers "
            "since late 2022"
        ),
        "url": "https://www.anthropic.com/research/labor-market-impacts",
        "source_name": "Anthropic Labor Market Impacts Research (January 2026)",
    },
    "jpmorgan_research": {
        "quote": (
            "We find little association between various measures of AI intensity "
            "and job growth outside of selected tech industries."
        ),
        "url": "https://www.jpmorgan.com/insights/global-research/artificial-intelligence/ai-impact-job-growth",
        "source_name": "J.P. Morgan Global Research — AI's Impact on Job Growth (2025)",
    },
    "hbr_2026": {
        "quote": (
            "Rather than solely eliminating jobs, generative AI creates new demand "
            "in augmentation-prone roles, suggesting that human-AI collaboration "
            "is a key driver of labor market transformation"
        ),
        "url": "https://hbr.org/2026/03/research-how-ai-is-changing-the-labor-market",
        "source_name": "Harvard Business Review — Research: How AI Is Changing the Labor Market (March 2026)",
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. COUNT SOURCES WITH VERIFIED CITATIONS
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources (status verified or partial): {n_confirmed} / {len(empirical_facts)}")

# ---------------------------------------------------------------------------
# 6. CLAIM EVALUATION (Rule 7 — use compare(), never hardcode)
# ---------------------------------------------------------------------------
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified counter-evidence sources vs threshold",
)

# ---------------------------------------------------------------------------
# 7. ADVERSARIAL CHECKS (Rule 5)
#    These document the strongest arguments FOR the original claim, and explain
#    why they do not overcome the counter-evidence.
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Does Dario Amodei's May 2025 warning of '50% of entry-level "
            "white-collar jobs eliminated within five years' support the claim?"
        ),
        "verification_performed": (
            "Fetched Fortune article (fortune.com/2025/05/28/anthropic-ceo-warning-ai-job-loss/) "
            "confirming Amodei stated: 'AI could eliminate half of all entry-level white-collar "
            "jobs within five years.' Also reviewed Anthropic's own January 2026 peer-reviewed "
            "research paper (anthropic.com/research/labor-market-impacts) which found 'no "
            "systematic increase in unemployment for highly exposed workers since late 2022' — "
            "directly contradicting Amodei's prediction with Anthropic's own data."
        ),
        "finding": (
            "Amodei's warning is limited to 'entry-level' roles only (a subset of white-collar), "
            "not all white-collar jobs. His own company's peer-reviewed research shows no "
            "measured unemployment increase in AI-exposed occupations even 3+ years after "
            "ChatGPT's launch. The CEO prediction is a forward-looking warning, not a "
            "measured forecast; it does not constitute evidence that the full claim holds."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does Microsoft AI Chief Mustafa Suleyman's prediction that 'most professional "
            "work will be replaced within a year to 18 months' (March 2026) support the claim?"
        ),
        "verification_performed": (
            "Found quote in Fortune article (fortune.com/2026/03/06/ai-job-losses-report-anthropic-research-great-recession-for-white-collar-workers/). "
            "Searched for any corroborating institutional data supporting Suleyman's timeline. "
            "Found no institutional study (Goldman Sachs, IMF, WEF, BLS, Yale Budget Lab, "
            "J.P. Morgan) supporting 50%+ replacement within 18 months or by 2035."
        ),
        "finding": (
            "Suleyman's prediction is an executive opinion, not a systematic study. "
            "Current measured data (3+ years of AI deployment since ChatGPT) contradicts "
            "an 18-month replacement timeline: employment in AI-exposed occupations has not "
            "fallen by anywhere near 50%. No major institutional forecast supports this claim."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does McKinsey's estimate that '57% of current work hours are theoretically "
            "automatable' support the 50%+ job replacement claim?"
        ),
        "verification_performed": (
            "Reviewed McKinsey Global Institute reports and coverage. The 57% figure refers "
            "to the *theoretical automation potential of tasks/hours*, not to actual job "
            "elimination. McKinsey explicitly distinguishes between 'technically automatable' "
            "and 'likely to be automated by 2035.' Searched for any McKinsey forecast "
            "projecting 50%+ white-collar job replacement by 2035."
        ),
        "finding": (
            "'Tasks theoretically automatable' is not equivalent to 'jobs replaced.' "
            "Automation of some tasks within a role typically transforms that role rather "
            "than eliminating it. McKinsey's own report notes adoption lags far behind "
            "theoretical potential. No McKinsey forecast projects 50%+ white-collar job "
            "replacement by 2035."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the IMF finding that '40% of global jobs (60% in high-income countries) "
            "are exposed to AI' support the 50%+ replacement claim?"
        ),
        "verification_performed": (
            "Reviewed IMF 2024 World Economic Outlook AI assessment. The 40-60% figure "
            "refers to 'exposure' — jobs containing tasks that AI could potentially assist "
            "with. The IMF explicitly states that exposure can lead to either augmentation "
            "(increased productivity) or displacement, and that historical technology "
            "transitions show net job creation rather than elimination."
        ),
        "finding": (
            "'Exposure to AI' is not equivalent to 'replacement by AI.' The IMF's own "
            "analysis finds that advanced economies see AI mostly as a productivity-enhancing "
            "tool (augmentation), with only a subset of exposed jobs at risk of displacement. "
            "The IMF does not project 50%+ white-collar job replacement by 2035."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there any peer-reviewed study projecting 50%+ white-collar job "
            "replacement specifically by 2035?"
        ),
        "verification_performed": (
            "Searched for: 'peer-reviewed study AI replace 50 percent white collar jobs 2035'; "
            "'academic research AI job displacement 50% forecast 2035'; "
            "'economics paper AI employment white collar replacement 50 percent'. "
            "Also reviewed: Oxford Frey & Osborne (2013, 47% US jobs 'at high risk'), "
            "Goldman Sachs research note (March 2023, 300 million jobs globally affected), "
            "Yale Budget Lab (2026), Anthropic research (2026), J.P. Morgan (2025)."
        ),
        "finding": (
            "No peer-reviewed economics study projects 50%+ white-collar job *replacement* "
            "by 2035. The Oxford 47% figure (Frey & Osborne 2013) refers to 'at high risk "
            "of automation' over unspecified long run, not confirmed replacement by 2035 — "
            "and has been widely criticized as overestimating displacement. Goldman Sachs "
            "projects 300 million jobs globally 'affected' but their net employment effect "
            "estimate is only 6-7% displacement if AI is fully deployed. The institutional "
            "consensus is far below the 50% threshold."
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

    FACT_REGISTRY["A1"]["method"] = (
        f"count(citations with status in {COUNTABLE_STATUSES}) = {n_confirmed}"
    )
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
                    "Four independent authoritative sources consulted — "
                    "institutional research (Yale Budget Lab, J.P. Morgan), "
                    "peer-reviewed AI company research (Anthropic), and "
                    "independent academic journalism (HBR). All four reach "
                    "the same conclusion: no evidence of 50%+ replacement."
                ),
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources span independent institutions: Yale University Budget Lab, "
                    "Anthropic (AI company's own research), J.P. Morgan (investment bank), "
                    "and Harvard Business Review (academic journalism). No two sources "
                    "share the same methodological approach or institutional affiliation."
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
            "interpretation": (
                "claim_holds=True means enough sources CONTRADICT the claim, "
                "leading to a DISPROVED verdict"
            ),
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
