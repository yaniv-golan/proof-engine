"""
Proof: AI hallucinations occur on fewer than 5% of factual questions
Generated: 2026-03-28

Verdict approach: DISPROOF — three independent published studies each document
hallucination rates far exceeding 5% for mainstream AI models on factual question
benchmarks. The claim is universal ("AI"), so a single well-documented counterexample
suffices; three independent ones constitute overwhelming disproof.
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = "AI hallucinations occur on fewer than 5% of factual questions"

CLAIM_FORMAL = {
    "subject": "AI language models (mainstream LLMs)",
    "property": "hallucination rate on factual question-answering benchmarks",
    "operator": "<",
    "operator_note": (
        "The claim uses 'AI' without qualification — interpreted as mainstream large "
        "language models (GPT-4/4o, Claude, Llama, etc.). 'Factual questions' maps to "
        "published factual Q&A benchmarks (PreciseWikiQA, legal case queries, domain "
        "Q&A studies). The threshold 5% means <5 hallucinated answers per 100 factual "
        "questions. As a universal claim, a single well-documented counterexample "
        "showing any mainstream AI ≥5% on a standard factual Q&A benchmark disproves it. "
        "This proof uses three independent counterexamples. "
        "Note: summarization-task hallucination rates (Vectara leaderboard) are excluded "
        "as they measure a different phenomenon (introducing facts not in the source "
        "document), which is distinct from recalling factual knowledge under questioning."
    ),
    "threshold": 5.0,
    "proof_direction": "disprove",
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {
        "key": "hallulens",
        "label": "HalluLens ACL 2025: GPT-4o hallucination rate on PreciseWikiQA factual Q&A",
    },
    "B2": {
        "key": "legal_fictions",
        "label": "Large Legal Fictions (arxiv 2401.01301): LLM hallucination rate on legal factual questions",
    },
    "B3": {
        "key": "pmc_survey",
        "label": "PMC survey (2025): LLaMA 2 and DeepSeek hallucination rates on factual Q&A",
    },
    "A1": {
        "label": "Count of independent sources confirming hallucination rates ≥5%",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS — sources that CONFIRM the claim is FALSE
#    (i.e., show hallucination rates ≥5% for mainstream AI on factual questions)
# ---------------------------------------------------------------------------
empirical_facts = {
    "hallulens": {
        "quote": (
            "GPT-4o, with a 45.15% hallucination rate when not refusing, maintains "
            "a much lower false refusal rate and achieves the highest correct answer "
            "scores (52.59%), indicating a trade-off between precision and recall."
        ),
        "url": "https://arxiv.org/html/2504.17550v1",
        "source_name": "HalluLens: LLM Hallucination Benchmark (ACL 2025, arxiv 2504.17550)",
    },
    "legal_fictions": {
        "quote": (
            "legal hallucinations are alarmingly prevalent, occurring between 69% of the "
            "time with ChatGPT 3.5 and 88% with Llama 2"
        ),
        "url": "https://arxiv.org/html/2401.01301v1",
        "source_name": "Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models (arxiv 2401.01301)",
    },
    "pmc_survey": {
        "quote": (
            "LLaMA 2 and DeepSeek exhibited significantly higher factual hallucination "
            "rates around 20%\u201325%"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12518350/",
        "source_name": "PMC: Survey and analysis of hallucinations in large language models (2025, PMC12518350)",
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
print("Verifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)
for key, result in citation_results.items():
    print(f"  {key}: {result['status']}")

# ---------------------------------------------------------------------------
# 5. COUNT SOURCES WITH VERIFIED CITATIONS (disproof mode)
#    A source counts if its quote was found on the page (verified or partial).
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources (showing hallucination ≥5%): {n_confirmed} / {len(empirical_facts)}")

# ---------------------------------------------------------------------------
# 6. CLAIM EVALUATION — MUST use compare(), not hardcoded bool
#    In disproof mode: claim_holds means "we have enough evidence to disprove"
# ---------------------------------------------------------------------------
claim_holds = compare(
    n_confirmed,
    ">=",
    CLAIM_FORMAL["threshold"],
    label="confirmed disproof sources vs threshold of 3",
)
# Reinterpret for disproof: threshold is the minimum number of confirming sources
DISPROOF_SOURCE_THRESHOLD = 3
claim_holds = compare(
    n_confirmed,
    ">=",
    DISPROOF_SOURCE_THRESHOLD,
    label="confirmed disproof sources (need ≥3 to establish disproof)",
)

# ---------------------------------------------------------------------------
# 7. ADVERSARIAL CHECKS (Rule 5) — searching for evidence SUPPORTING the claim
#    (i.e., evidence that hallucination rates ARE below 5%)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Does GPT-4 specifically achieve hallucination rates below 5% on any "
            "factual benchmark, potentially making the claim true for the best models?"
        ),
        "verification_performed": (
            "Searched for GPT-4 hallucination rate studies. Found PMC12518350 which "
            "reports 'GPT-4 achieved near-perfect factual accuracy, maintaining a "
            "hallucination rate below 5%' in one study. However: (1) this is under "
            "chain-of-thought prompting conditions; (2) it applies to GPT-4 specifically, "
            "not 'AI' in general; (3) HalluLens (ACL 2025) shows GPT-4o at 45.15% on "
            "PreciseWikiQA — a different benchmark. The claim uses 'AI' universally, and "
            "GPT-4 below 5% on one specific prompted benchmark does not rescue a universal "
            "claim when dozens of other models and benchmarks show far higher rates."
        ),
        "finding": (
            "GPT-4 may approach <5% under optimal conditions on some benchmarks. This "
            "does not save the universal claim: LLaMA 2, DeepSeek, ChatGPT 3.5, GPT-4o "
            "on other benchmarks, and all models on legal/medical domain questions all "
            "show rates far above 5%. The claim as stated is false for 'AI' broadly."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does the Vectara summarization leaderboard show models below 5%, suggesting "
            "the claim could be true for some AI systems?"
        ),
        "verification_performed": (
            "Reviewed Vectara hallucination leaderboard (github.com/vectara/hallucination-leaderboard). "
            "Top-performing models show 1.8%–3.3% hallucination on document summarization tasks. "
            "However, the Vectara leaderboard measures a different task: whether a model introduces "
            "facts not present in a source document when summarizing. This is NOT factual Q&A "
            "hallucination. Factual Q&A requires models to recall knowledge from training data — "
            "a fundamentally harder task where rates are consistently much higher."
        ),
        "finding": (
            "Summarization-fidelity rates (Vectara) are not comparable to factual Q&A hallucination "
            "rates. On actual factual question benchmarks (SimpleQA, PreciseWikiQA, legal/medical "
            "domain tests), rates are far above 5% across all tested models."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could 'hallucination' be defined narrowly enough (e.g., only fabricated citations, "
            "not factual errors) to make the <5% claim true?"
        ),
        "verification_performed": (
            "Reviewed definitions across the three cited papers. HalluLens defines hallucination "
            "as 'incorrect answers when the model does not refuse to answer' on fact-based queries. "
            "The legal study counts hallucinated case citations and holdings. The PMC survey uses "
            "standard factual accuracy benchmarks. All three use well-established, conservative "
            "definitions. There is no credible narrow definition that reduces these measured rates "
            "below 5%."
        ),
        "finding": (
            "Narrow definitions do not rescue the claim. All studies use standard, conservative "
            "hallucination definitions, and rates remain far above 5% under any reasonable definition."
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

    FACT_REGISTRY["A1"]["method"] = f"count(citations with status in {COUNTABLE_STATUSES})"
    FACT_REGISTRY["A1"]["result"] = f"{n_confirmed} confirmed sources (need ≥{DISPROOF_SOURCE_THRESHOLD})"

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
                "description": "Three independent research groups, separate benchmarks, separate domains",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "B1: AI/NLP researchers (HalluLens, ACL 2025). "
                    "B2: Legal AI researchers (Stanford/Princeton/NYU, arxiv 2401.01301). "
                    "B3: PMC survey authors (2025). "
                    "Different institutions, different benchmark designs, different domains."
                ),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirmed_disproof_sources": n_confirmed,
            "disproof_threshold": DISPROOF_SOURCE_THRESHOLD,
            "claim_holds": claim_holds,
            "hallucination_rates_found": {
                "GPT-4o on PreciseWikiQA (HalluLens ACL 2025)": "45.15%",
                "ChatGPT 3.5 on legal case questions (Legal Fictions 2024)": "69%",
                "Llama 2 on legal case questions (Legal Fictions 2024)": "88%",
                "LLaMA 2 / DeepSeek on factual Q&A (PMC survey 2025)": "~20-25%",
            },
        },
        "generator": {
            "name": "proof-engine",
            "version": open(os.path.join(PROOF_ENGINE_ROOT, "VERSION")).read().strip(),
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": __import__("datetime").date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
